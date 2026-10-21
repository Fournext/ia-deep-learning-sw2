"""Implementaciones en memoria de los repositorios de dominio (Stateless / In-Memory).

Permite el funcionamiento autónomo del microservicio sin persistir datos en
bases de datos externas (PostgreSQL/SQLite), cumpliendo la regla de no guardar
datos personales ni biométricos de clientes en persistencia permanente.
"""

import csv
import uuid
from pathlib import Path

from app.domain.entities.analysis_results import ImageAnalysisResult, VideoAnalysisResult
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.exercise import Exercise, MovementPattern, MovementType
from app.domain.entities.progress import WorkoutProgress
from app.domain.entities.workout_plan import Recommendation, WorkoutPlan


class InMemoryExerciseRepository:
    """Repositorio en memoria para el catálogo canónico de ejercicios."""

    def __init__(self, dataset_path: str | Path | None = None) -> None:
        """Carga los ejercicios desde ml/datasets/exercises_clean.csv en memoria."""
        self._exercises: dict[uuid.UUID, Exercise] = {}
        self._by_num: dict[int, Exercise] = {}

        if dataset_path is None:
            # Ruta relativa al proyecto
            dataset_path = Path(__file__).resolve().parents[3] / "ml" / "datasets" / "exercises_clean.csv"

        self._load_from_csv(Path(dataset_path))

    def _load_from_csv(self, path: Path) -> None:
        """Parsea el archivo CSV canónico y genera entidades Exercise."""
        if not path.exists():
            return

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ex_num = int(row["exercise_id"])
                # Generar UUID determinista basado en el número de ejercicio
                ex_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"exercise-{ex_num}")
                ex = Exercise(
                    id=ex_id,
                    exercise_id_num=ex_num,
                    name=row["exercise_name"],
                    body_part=row["body_part"],
                    muscle_type=row["muscle_type"],
                    equipment=row["equipment"],
                    movement_type=MovementType(row.get("movement_type", "compound")),
                    movement_pattern=MovementPattern(row.get("movement_pattern", "other")),
                    difficulty=row.get("difficulty", "intermediate"),
                    sets_min=float(row["sets_min"]) if row.get("sets_min") else 3.0,
                    sets_max=float(row["sets_max"]) if row.get("sets_max") else 4.0,
                    reps_min=int(row["reps_min"]) if row.get("reps_min") else 8,
                    reps_max=int(row["reps_max"]) if row.get("reps_max") else 12,
                    est_duration_min=float(row["est_duration_min"]) if row.get("est_duration_min") else 7.5,
                )
                self._exercises[ex_id] = ex
                self._by_num[ex_num] = ex

    async def get_by_id(self, exercise_id: uuid.UUID) -> Exercise | None:
        """Busca un ejercicio por su UUID."""
        return self._exercises.get(exercise_id)

    async def list_all(self) -> list[Exercise]:
        """Obtiene la lista completa de ejercicios del catálogo."""
        return list(self._exercises.values())

    async def get_by_exercise_num(self, num: int) -> Exercise | None:
        """Busca un ejercicio por su índice numérico canónico."""
        return self._by_num.get(num)


class InMemoryEvaluationRepository:
    """Repositorio en memoria volátil para evaluaciones físicas temporales."""

    def __init__(self) -> None:
        """Inicializa almacenamiento en memoria."""
        self._evaluations: dict[uuid.UUID, Evaluation] = {}

    async def save(self, evaluation: Evaluation) -> Evaluation:
        """Almacena temporalmente una evaluación en memoria."""
        self._evaluations[evaluation.id] = evaluation
        return evaluation

    async def get_by_id(self, evaluation_id: uuid.UUID) -> Evaluation | None:
        """Recupera la evaluación desde la memoria volátil."""
        return self._evaluations.get(evaluation_id)

    async def list_by_client_id(
        self, client_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[Evaluation]:
        """Filtra evaluaciones por cliente en memoria."""
        matched = [e for e in self._evaluations.values() if e.client_id == client_id]
        return matched[offset : offset + limit]


class InMemoryAnalysisRepository:
    """Repositorio en memoria para resultados de visión por computadora."""

    def __init__(self) -> None:
        """Inicializa almacenamiento volátil en memoria."""
        self._image_results: dict[uuid.UUID, list[ImageAnalysisResult]] = {}
        self._video_results: dict[uuid.UUID, list[VideoAnalysisResult]] = {}

    async def save_image_result(self, result: ImageAnalysisResult) -> ImageAnalysisResult:
        """Almacena temporalmente el resultado de imagen en memoria."""
        if result.evaluation_id not in self._image_results:
            self._image_results[result.evaluation_id] = []
        self._image_results[result.evaluation_id].append(result)
        return result

    async def get_image_results_by_evaluation(
        self, evaluation_id: uuid.UUID
    ) -> list[ImageAnalysisResult]:
        """Recupera los análisis de imagen de una evaluación."""
        return self._image_results.get(evaluation_id, [])

    async def save_video_result(self, result: VideoAnalysisResult) -> VideoAnalysisResult:
        """Almacena temporalmente el resultado de video en memoria."""
        if result.evaluation_id not in self._video_results:
            self._video_results[result.evaluation_id] = []
        self._video_results[result.evaluation_id].append(result)
        return result

    async def get_video_results_by_evaluation(
        self, evaluation_id: uuid.UUID
    ) -> list[VideoAnalysisResult]:
        """Recupera los análisis de video de una evaluación."""
        return self._video_results.get(evaluation_id, [])


class InMemoryWorkoutPlanRepository:
    """Repositorio en memoria para recomendaciones y planes de entrenamiento."""

    def __init__(self) -> None:
        """Inicializa almacenamiento en memoria."""
        self._recommendations: dict[uuid.UUID, Recommendation] = {}
        self._plans: dict[uuid.UUID, WorkoutPlan] = {}

    async def save_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Almacena una recomendación en memoria."""
        self._recommendations[recommendation.id] = recommendation
        return recommendation

    async def get_recommendation_by_id(
        self, recommendation_id: uuid.UUID
    ) -> Recommendation | None:
        """Recupera una recomendación por ID."""
        return self._recommendations.get(recommendation_id)

    async def save_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        """Almacena o actualiza un plan en memoria."""
        self._plans[plan.id] = plan
        return plan

    async def get_plan_by_id(self, plan_id: uuid.UUID) -> WorkoutPlan | None:
        """Recupera un plan por ID."""
        return self._plans.get(plan_id)


class InMemoryProgressRepository:
    """Repositorio en memoria para progreso de rutinas."""

    def __init__(self) -> None:
        """Inicializa almacenamiento en memoria."""
        self._progress: dict[uuid.UUID, list[WorkoutProgress]] = {}

    async def save_progress(self, progress: WorkoutProgress) -> WorkoutProgress:
        """Almacena un registro de avance en memoria."""
        if progress.workout_plan_id not in self._progress:
            self._progress[progress.workout_plan_id] = []
        self._progress[progress.workout_plan_id].append(progress)
        return progress

    async def list_by_plan(self, plan_id: uuid.UUID) -> list[WorkoutProgress]:
        """Obtiene el historial de progreso de un plan."""
        return self._progress.get(plan_id, [])


# Singletons en memoria para inyección de dependencias
default_exercise_repo = InMemoryExerciseRepository()
default_evaluation_repo = InMemoryEvaluationRepository()
default_analysis_repo = InMemoryAnalysisRepository()
default_workout_plan_repo = InMemoryWorkoutPlanRepository()
default_progress_repo = InMemoryProgressRepository()
