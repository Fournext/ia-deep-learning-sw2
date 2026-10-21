"""Entidad de dominio para Ejercicios de Entrenamiento."""

import uuid
from dataclasses import dataclass
from enum import Enum


class MovementType(str, Enum):
    """Tipo de movimiento muscular."""

    COMPOUND = "compound"
    ISOLATION = "isolation"


class MovementPattern(str, Enum):
    """Patrón motor biomecánico principal."""

    PUSH = "push"
    PULL = "pull"
    SQUAT = "squat"
    HINGE = "hinge"
    CORE = "core"
    OTHER = "other"


@dataclass
class Exercise:
    """Entidad pura de dominio que representa un ejercicio del catálogo."""

    id: uuid.UUID
    exercise_id_num: int
    name: str
    body_part: str
    muscle_type: str
    equipment: str
    movement_type: MovementType
    movement_pattern: MovementPattern
    difficulty: str
    sets_min: float
    sets_max: float
    reps_min: int
    reps_max: int
    est_duration_min: float
