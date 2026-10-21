"""Servicio para el pipeline de análisis corporal y recomendación 100% en memoria (Stateless).

Ejecuta el flujo completo de Computer Vision (MediaPipe) y Deep Learning
(Recomendador Híbrido + NCF) directamente sobre los datos en memoria,
garantizando cero persistencia de datos personales o biométricos en bases de datos o disco.
"""

import os
import tempfile
import uuid
from typing import Any

from app.api.v1.schemas.stateless_analysis import (
    PostureAnalysisItem,
    RecommendedExerciseDetail,
    StatelessAnalysisResponse,
    VideoAnalysisItem,
    WorkoutDayDetail,
    WorkoutPlanDetail,
)
from app.core.exceptions import ImageQualityLowError
from app.domain.entities.analysis_results import ExerciseVideoType, ImageViewType
from app.domain.entities.evaluation import Evaluation, EvaluationStatus, FitnessGoal, FitnessLevel
from app.domain.entities.exercise import Exercise
from app.domain.interfaces.engines import ICVEngine, IRecommendationEngine
from app.domain.interfaces.repositories import IExerciseRepository


class StatelessPipelineService:
    """Pipeline unificado de análisis biomecánico e inferencia sin persistencia en BD."""

    def __init__(
        self,
        cv_engine: ICVEngine,
        rec_engine: IRecommendationEngine,
        exercise_repo: IExerciseRepository,
    ) -> None:
        """Inicializa los motores y el repositorio de ejercicios en memoria."""
        self._cv_engine = cv_engine
        self._rec_engine = rec_engine
        self._exercise_repo = exercise_repo

    async def execute(
        self,
        client_id: uuid.UUID,
        age: int,
        weight_kg: float,
        height_cm: float,
        fitness_level: FitnessLevel,
        fitness_goal: FitnessGoal,
        available_days_per_week: int,
        session_duration_minutes: int,
        available_equipment: list[str],
        physical_restrictions: list[str],
        photo_frontal_bytes: bytes | None = None,
        photo_lateral_bytes: bytes | None = None,
        photo_posterior_bytes: bytes | None = None,
        video_bytes: bytes | None = None,
        video_exercise_type: ExerciseVideoType | None = None,
    ) -> StatelessAnalysisResponse:
        """Ejecuta el análisis y recomendación completos sin tocar base de datos ni retener archivos.

        Returns:
            StatelessAnalysisResponse con métricas posturales y propuesta de entrenamiento.
        """
        # 1. Crear evaluación de dominio efímera en memoria
        evaluation = Evaluation(
            id=uuid.uuid4(),
            client_id=client_id,
            age=age,
            weight_kg=weight_kg,
            height_cm=height_cm,
            fitness_level=fitness_level,
            fitness_goal=fitness_goal,
            available_days_per_week=available_days_per_week,
            session_duration_minutes=session_duration_minutes,
            available_equipment=available_equipment,
            physical_restrictions=physical_restrictions,
            status=EvaluationStatus.COMPLETADA,
        )

        bmi = evaluation.calculate_bmi()
        bmi_cat = evaluation.get_bmi_category()

        # 2. Análisis de Fotografías en Memoria con MediaPipe Pose
        photo_analyses: list[PostureAnalysisItem] = []
        posture_findings: list[str] = []

        photos_to_process = [
            (ImageViewType.FRONTAL, photo_frontal_bytes),
            (ImageViewType.LATERAL, photo_lateral_bytes),
            (ImageViewType.POSTERIOR, photo_posterior_bytes),
        ]

        for view_type, p_bytes in photos_to_process:
            if not p_bytes or len(p_bytes) == 0:
                continue

            try:
                cv_res = self._cv_engine.analyze_posture_image(p_bytes, view_type)
                metrics = cv_res.get("posture_metrics", {})
                obs = metrics.get("observations", [])
                posture_findings.extend(obs)

                photo_analyses.append(
                    PostureAnalysisItem(
                        view_type=view_type.value,
                        confidence_score=cv_res.get("confidence_score", 0.0),
                        has_quality_issues=cv_res.get("has_quality_issues", False),
                        calculated_angles=cv_res.get("calculated_angles", {}),
                        observations=obs,
                        shoulder_slope_degrees=metrics.get("shoulder_slope_degrees", 0.0),
                        hip_slope_degrees=metrics.get("hip_slope_degrees", 0.0),
                    )
                )
            except ImageQualityLowError as eq:
                photo_analyses.append(
                    PostureAnalysisItem(
                        view_type=view_type.value,
                        confidence_score=eq.confidence,
                        has_quality_issues=True,
                        calculated_angles={},
                        observations=[f"Calidad insuficiente: {eq.reason}"],
                        shoulder_slope_degrees=0.0,
                        hip_slope_degrees=0.0,
                    )
                )

        # 3. Análisis de Video Efímero (Auto-limpieza inmediata)
        video_analysis_item: VideoAnalysisItem | None = None
        if video_bytes and len(video_bytes) > 0 and video_exercise_type is not None:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
            try:
                with os.fdopen(tmp_fd, "wb") as f:
                    f.write(video_bytes)

                vid_res = self._cv_engine.analyze_exercise_video(tmp_path, video_exercise_type)
                errors = vid_res.get("execution_errors", [])
                posture_findings.extend(errors)

                video_analysis_item = VideoAnalysisItem(
                    exercise_type=video_exercise_type.value,
                    completed_reps=vid_res.get("completed_reps", 0),
                    average_depth_angle=vid_res.get("average_depth_angle", 0.0),
                    execution_score=vid_res.get("execution_score", 0.0),
                    execution_errors=errors,
                )
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

        # 4. Motor de Recomendación Híbrido (Restricciones -> Contenido -> PyTorch NCF)
        all_exercises = await self._exercise_repo.list_all()
        rec_output = self._rec_engine.recommend(
            evaluation=evaluation,
            available_exercises=all_exercises,
            posture_findings=posture_findings,
            top_k=8,
        )

        breakdown_data = rec_output.get("scoring_breakdown", {})
        top_recs = (
            breakdown_data.get("top_recommendations", [])
            if isinstance(breakdown_data, dict)
            else []
        )

        # Mapear ejercicios recomendados a modelos de detalle
        recommended_details: list[RecommendedExerciseDetail] = []
        rec_map: dict[uuid.UUID, Exercise] = {e.id: e for e in all_exercises}

        for item in top_recs:
            ex_id_val = item["exercise_id"]
            if isinstance(ex_id_val, str):
                ex_id_val = uuid.UUID(ex_id_val)
            ex_obj = rec_map.get(ex_id_val)
            if ex_obj:
                recommended_details.append(
                    RecommendedExerciseDetail(
                        exercise_id=ex_obj.id,
                        exercise_name=ex_obj.name,
                        body_part=ex_obj.body_part,
                        muscle_type=ex_obj.muscle_type,
                        equipment=ex_obj.equipment,
                        difficulty=ex_obj.difficulty,
                        score=float(item.get("final_score", 0.8)),
                    )
                )

        # 5. Generar Plan de Entrenamiento Estructurado
        days_count = max(1, min(7, available_days_per_week))
        workout_days: list[WorkoutDayDetail] = []
        exercises_per_day = max(2, len(recommended_details) // days_count)

        for d_num in range(1, days_count + 1):
            start_idx = (d_num - 1) * exercises_per_day
            end_idx = start_idx + exercises_per_day
            day_exs = recommended_details[start_idx:end_idx] or recommended_details[:exercises_per_day]

            exercises_payload: list[dict[str, Any]] = [
                {
                    "exercise_id": str(dex.exercise_id),
                    "exercise_name": dex.exercise_name,
                    "target_sets": 3,
                    "target_reps": 10 if fitness_goal != FitnessGoal.FUERZA else 6,
                    "rest_seconds": 60 if fitness_goal == FitnessGoal.RESISTENCIA else 90,
                    "intensity_rpe": 7.5,
                    "notes": f"Enfocar en ejecución biomecánicamente controlada para {dex.body_part}.",
                }
                for dex in day_exs
            ]

            workout_days.append(
                WorkoutDayDetail(
                    day_number=d_num,
                    day_label=f"Día {d_num} - {fitness_goal.value.capitalize()}",
                    exercises=exercises_payload,
                )
            )

        # Justificación técnica combinando hallazgos visuales y objetivos
        justification_parts = [
            f"Rutina orientada a {fitness_goal.value} para nivel {fitness_level.value} con {days_count} días por semana.",
        ]
        if physical_restrictions:
            justification_parts.append(
                f"Se aplicaron filtros de exclusión dura para proteger: {', '.join(physical_restrictions)}."
            )
        if posture_findings:
            justification_parts.append(
                f"Se consideraron los siguientes hallazgos visuales y de movimiento: {'; '.join(set(posture_findings))}."
            )
        else:
            justification_parts.append("Postura y alineación evaluadas dentro de rangos normales de simetría.")

        workout_plan = WorkoutPlanDetail(
            program_name=f"Plan Personalizado {fitness_goal.value.capitalize()} (Stateless)",
            status="PENDIENTE_APROBACION",
            trainer_review_notice=(
                "Propuesta preliminar generada por IA. No entra en vigor para el cliente "
                "hasta ser revisada, ajustada y aprobada formalmente por un entrenador del ERP."
            ),
            justification=" ".join(justification_parts),
            days=workout_days,
        )

        return StatelessAnalysisResponse(
            client_id=client_id,
            bmi=bmi,
            bmi_category=bmi_cat,
            fitness_level=fitness_level.value,
            fitness_goal=fitness_goal.value,
            posture_findings=list(set(posture_findings)),
            photo_analyses=photo_analyses,
            video_analysis=video_analysis_item,
            recommendation_engine=rec_output["recommendation_engine"],
            recommended_exercises=recommended_details,
            workout_plan=workout_plan,
            persisted_to_database=False,
        )
