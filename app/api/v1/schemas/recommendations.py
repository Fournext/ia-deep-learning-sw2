"""Esquemas Pydantic v2 para recomendaciones de ejercicios."""

import uuid

from pydantic import BaseModel, Field

from app.api.v1.schemas.stateless_analysis import RecommendedExerciseDetail, WorkoutPlanDetail
from app.domain.entities.evaluation import FitnessGoal, FitnessLevel


class RecommendationGenerateRequest(BaseModel):
    """Solicitud para generar recomendaciones en modo stateless sin base de datos."""

    client_id: uuid.UUID | None = Field(None, description="Identificador único del cliente en el ERP")
    age: int = Field(..., ge=14, le=90, description="Edad del cliente")
    weight_kg: float = Field(..., ge=30.0, le=300.0, description="Peso corporal en kilogramos")
    height_cm: float = Field(..., ge=100.0, le=250.0, description="Estatura en centímetros")
    fitness_level: FitnessLevel = Field(..., description="Nivel de condición física")
    fitness_goal: FitnessGoal = Field(..., description="Objetivo principal")
    available_days_per_week: int = Field(..., ge=1, le=7, description="Días disponibles para entrenar por semana")
    session_duration_minutes: int = Field(..., ge=15, le=180, description="Minutos disponibles por sesión")
    available_equipment: list[str] = Field(default_factory=list, description="Lista de equipamiento disponible")
    physical_restrictions: list[str] = Field(default_factory=list, description="Restricciones o lesiones médicas")
    posture_findings: list[str] = Field(default_factory=list, description="Hallazgos visuales o asimetrías detectadas")
    top_k: int = Field(default=10, ge=3, le=25, description="Cantidad de ejercicios a recomendar")


class StatelessRecommendationResponse(BaseModel):
    """Respuesta con ejercicios recomendados y propuesta de rutina semanal estructurada."""

    client_id: uuid.UUID
    bmi: float
    bmi_category: str
    recommendation_engine: str
    recommended_exercises: list[RecommendedExerciseDetail]
    workout_plan: WorkoutPlanDetail
    persisted_to_database: bool = False
