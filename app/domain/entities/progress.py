"""Entidad de dominio para el registro de avance y retroalimentación de entrenamiento."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkoutProgress:
    """Registro de una serie o sesión ejecutada por el cliente con valoración de esfuerzo."""

    id: uuid.UUID
    workout_plan_id: uuid.UUID
    client_id: uuid.UUID
    exercise_id: uuid.UUID
    sets_completed: int
    reps_completed: int
    weight_lifted_kg: float
    perceived_effort_rpe: int  # Escala 1 al 10 (RPE)
    client_comments: str | None = None
    trainer_feedback: str | None = None
    logged_at: datetime = field(default_factory=datetime.utcnow)
