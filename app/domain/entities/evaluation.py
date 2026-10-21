"""Entidad de dominio para la Evaluación Física del Cliente."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class FitnessLevel(str, Enum):
    """Nivel de condición física del cliente."""

    PRINCIPIANTE = "PRINCIPIANTE"
    INTERMEDIO = "INTERMEDIO"
    AVANZADO = "AVANZADO"


class FitnessGoal(str, Enum):
    """Objetivo principal de entrenamiento."""

    HIPERTROFIA = "HIPERTROFIA"
    PERDIDA_GRASA = "PERDIDA_GRASA"
    FUERZA = "FUERZA"
    RESISTENCIA = "RESISTENCIA"
    SALUD_GENERAL = "SALUD_GENERAL"


class EvaluationStatus(str, Enum):
    """Estado del ciclo de vida de la evaluación."""

    BORRADOR = "BORRADOR"
    PROCESANDO = "PROCESANDO"
    COMPLETADA = "COMPLETADA"
    ERROR = "ERROR"


@dataclass
class Evaluation:
    """Entidad pura de dominio que representa una evaluación física integral."""

    id: uuid.UUID
    client_id: uuid.UUID
    age: int
    weight_kg: float
    height_cm: float
    fitness_level: FitnessLevel
    fitness_goal: FitnessGoal
    available_days_per_week: int
    session_duration_minutes: int
    available_equipment: list[str] = field(default_factory=list)
    physical_restrictions: list[str] = field(default_factory=list)
    status: EvaluationStatus = EvaluationStatus.BORRADOR
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_bmi(self) -> float:
        """Calcula el índice de masa corporal (IMC) orientativo.

        Returns:
            Valor flotante del IMC redondeado a 2 decimales.
        """
        height_m = self.height_cm / 100.0
        if height_m <= 0:
            return 0.0
        return round(self.weight_kg / (height_m**2), 2)

    def get_bmi_category(self) -> str:
        """Determina la clasificación orientativa de peso según OMS."""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "Bajo peso"
        if bmi < 25.0:
            return "Normopeso"
        if bmi < 30.0:
            return "Sobrepeso"
        return "Obesidad"
