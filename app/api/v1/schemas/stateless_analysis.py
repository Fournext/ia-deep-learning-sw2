"""Esquemas Pydantic v2 para el endpoint de análisis corporal y recomendación stateless."""

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PostureAnalysisItem(BaseModel):
    """Resultados de análisis postural para una imagen individual."""

    model_config = ConfigDict(from_attributes=True)

    view_type: str = Field(..., description="Vista anatómica (FRONTAL, LATERAL, POSTERIOR)")
    confidence_score: float = Field(..., description="Índice de confianza de MediaPipe Pose [0.0 - 1.0]")
    has_quality_issues: bool = Field(..., description="Indica si la imagen tuvo baja visibilidad o problemas")
    calculated_angles: dict[str, float] = Field(default_factory=dict, description="Ángulos anatómicos calculados")
    observations: list[str] = Field(default_factory=list, description="Observaciones biomecánicas detectadas")
    shoulder_slope_degrees: float = Field(default=0.0, description="Inclinación biacromial en grados")
    hip_slope_degrees: float = Field(default=0.0, description="Inclinación de crestas ilíacas en grados")


class VideoAnalysisItem(BaseModel):
    """Resultados de análisis técnico y conteo en video."""

    model_config = ConfigDict(from_attributes=True)

    exercise_type: str = Field(..., description="Ejercicio evaluado (SQUAT o PUSHUP)")
    completed_reps: int = Field(..., description="Repeticiones válidas completadas")
    average_depth_angle: float = Field(..., description="Profundidad articular media alcanzada")
    execution_score: float = Field(..., description="Puntuación técnica global de ejecución [0.0 - 1.0]")
    execution_errors: list[str] = Field(default_factory=list, description="Desviaciones o errores observados")


class RecommendedExerciseDetail(BaseModel):
    """Detalle de un ejercicio recomendado por el motor de IA."""

    model_config = ConfigDict(from_attributes=True)

    exercise_id: uuid.UUID
    exercise_name: str
    body_part: str
    muscle_type: str
    equipment: str
    difficulty: str
    score: float


class WorkoutDayDetail(BaseModel):
    """Estructura de una sesión de entrenamiento diaria."""

    model_config = ConfigDict(from_attributes=True)

    day_number: int
    day_label: str
    exercises: list[dict[str, Any]]


class WorkoutPlanDetail(BaseModel):
    """Propuesta de plan de entrenamiento estructurado."""

    model_config = ConfigDict(from_attributes=True)

    program_name: str
    status: str = Field(default="PENDIENTE_APROBACION", description="Estado inicial inmutable")
    trainer_review_notice: str = Field(
        default=(
            "Propuesta preliminar generada por IA. No entra en vigor para el cliente "
            "hasta ser revisada, ajustada y aprobada formalmente por un entrenador del ERP."
        )
    )
    justification: str
    days: list[WorkoutDayDetail]


class StatelessAnalysisResponse(BaseModel):
    """Respuesta unificada del análisis corporal y recomendación en memoria (Stateless)."""

    model_config = ConfigDict(from_attributes=True)

    client_id: uuid.UUID
    bmi: float = Field(..., description="Índice de masa corporal calculado")
    bmi_category: str = Field(..., description="Categoría de peso según OMS")
    fitness_level: str
    fitness_goal: str
    posture_findings: list[str] = Field(
        default_factory=list, description="Hallazgos visuales integrados de fotos y videos"
    )
    photo_analyses: list[PostureAnalysisItem] = Field(
        default_factory=list, description="Desglose del análisis por cada fotografía cargada"
    )
    video_analysis: VideoAnalysisItem | None = Field(
        default=None, description="Desglose del análisis de video si fue suministrado"
    )
    recommendation_engine: str = Field(..., description="Nombre del pipeline de recomendación ejecutado")
    recommended_exercises: list[RecommendedExerciseDetail] = Field(
        default_factory=list, description="Ranking de ejercicios seleccionados"
    )
    workout_plan: WorkoutPlanDetail = Field(
        ..., description="Rutina personalizada estructurada lista para revisión del entrenador"
    )
    persisted_to_database: bool = Field(
        default=False,
        description="Garantía de que ningún dato biométrico ni personal fue almacenado en base de datos",
    )
