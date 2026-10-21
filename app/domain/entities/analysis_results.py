"""Entidades de dominio para resultados de análisis visual (fotos y videos)."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ImageViewType(str, Enum):
    """Perspectiva visual de la fotografía corporal."""

    FRONTAL = "FRONTAL"
    LATERAL = "LATERAL"
    POSTERIOR = "POSTERIOR"


class ExerciseVideoType(str, Enum):
    """Tipo de ejercicio evaluado mediante video."""

    SQUAT = "SQUAT"
    PUSHUP = "PUSHUP"


@dataclass
class ImageAnalysisResult:
    """Resultado del análisis geométrico de una fotografía estática."""

    id: uuid.UUID
    evaluation_id: uuid.UUID
    view_type: ImageViewType
    file_path: str
    confidence_score: float
    has_quality_issues: bool
    detected_landmarks: dict[str, Any]
    calculated_angles: dict[str, float]
    posture_metrics: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VideoAnalysisResult:
    """Resultado del análisis dinámico y conteo de repeticiones de video."""

    id: uuid.UUID
    evaluation_id: uuid.UUID
    exercise_type: ExerciseVideoType
    file_path: str
    completed_reps: int
    average_depth_angle: float
    execution_score: float
    rep_details: list[dict[str, Any]] = field(default_factory=list)
    execution_errors: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
