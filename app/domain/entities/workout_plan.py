"""Entidades de dominio para Planes de Entrenamiento y Recomendaciones."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PlanStatus(str, Enum):
    """Estado del flujo de aprobación humana para rutinas de entrenamiento."""

    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADA = "APROBADA"
    MODIFICADA = "MODIFICADA"
    RECHAZADA = "RECHAZADA"


@dataclass
class Recommendation:
    """Resultado del motor de recomendación híbrido."""

    id: uuid.UUID
    evaluation_id: uuid.UUID
    client_id: uuid.UUID
    recommendation_engine: str
    recommended_exercise_ids: list[str]
    scoring_breakdown: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkoutPlanExercise:
    """Ejercicio programado dentro de un día de entrenamiento."""

    id: uuid.UUID
    workout_plan_day_id: uuid.UUID
    exercise_id: uuid.UUID
    exercise_name: str
    order_index: int
    target_sets: int
    target_reps: str
    rest_seconds: int
    intensity_rpe: str
    notes: str | None = None


@dataclass
class WorkoutPlanDay:
    """Día individual programado en la rutina semanal."""

    id: uuid.UUID
    workout_plan_id: uuid.UUID
    day_number: int
    day_label: str
    exercises: list[WorkoutPlanExercise] = field(default_factory=list)


@dataclass
class WorkoutPlan:
    """Plan de entrenamiento estructurado sujeto a revisión del entrenador."""

    id: uuid.UUID
    recommendation_id: uuid.UUID
    client_id: uuid.UUID
    program_name: str
    status: PlanStatus = PlanStatus.PENDIENTE_APROBACION
    trainer_id: uuid.UUID | None = None
    trainer_notes: str | None = None
    approved_at: datetime | None = None
    days: list[WorkoutPlanDay] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_approved(self) -> bool:
        """Determina si la rutina ha sido autorizada formalmente por el entrenador."""
        return self.status in (PlanStatus.APROBADA, PlanStatus.MODIFICADA)
