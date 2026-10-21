"""Interfaces de repositorios para inversión de dependencias (DIP)."""

import uuid
from typing import Protocol

from app.domain.entities.analysis_results import ImageAnalysisResult, VideoAnalysisResult
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.exercise import Exercise
from app.domain.entities.progress import WorkoutProgress
from app.domain.entities.workout_plan import Recommendation, WorkoutPlan


class IEvaluationRepository(Protocol):
    """Protocolo del repositorio de evaluaciones físicas."""

    async def save(self, evaluation: Evaluation) -> Evaluation:
        """Persiste o actualiza una evaluación."""
        ...

    async def get_by_id(self, evaluation_id: uuid.UUID) -> Evaluation | None:
        """Recupera una evaluación por su UUID."""
        ...

    async def list_by_client_id(
        self, client_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[Evaluation]:
        """Lista evaluaciones históricas de un cliente."""
        ...


class IExerciseRepository(Protocol):
    """Protocolo del repositorio de ejercicios."""

    async def get_by_id(self, exercise_id: uuid.UUID) -> Exercise | None:
        """Busca un ejercicio por su UUID."""
        ...

    async def list_all(self) -> list[Exercise]:
        """Obtiene la lista completa de ejercicios del catálogo."""
        ...

    async def get_by_exercise_num(self, num: int) -> Exercise | None:
        """Busca un ejercicio por su índice numérico canónico."""
        ...


class IAnalysisRepository(Protocol):
    """Protocolo para almacenar resultados de visión artificial."""

    async def save_image_result(self, result: ImageAnalysisResult) -> ImageAnalysisResult:
        """Persiste el análisis de una imagen."""
        ...

    async def get_image_results_by_evaluation(
        self, evaluation_id: uuid.UUID
    ) -> list[ImageAnalysisResult]:
        """Recupera todas las fotos analizadas de una evaluación."""
        ...

    async def save_video_result(self, result: VideoAnalysisResult) -> VideoAnalysisResult:
        """Persiste el análisis de un video."""
        ...

    async def get_video_results_by_evaluation(
        self, evaluation_id: uuid.UUID
    ) -> list[VideoAnalysisResult]:
        """Recupera los videos procesados de una evaluación."""
        ...


class IWorkoutPlanRepository(Protocol):
    """Protocolo para persistencia de recomendaciones y planes."""

    async def save_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Persiste una propuesta de recomendación."""
        ...

    async def get_recommendation_by_id(
        self, recommendation_id: uuid.UUID
    ) -> Recommendation | None:
        """Recupera una recomendación por su ID."""
        ...

    async def save_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        """Persiste o actualiza un plan de entrenamiento."""
        ...

    async def get_plan_by_id(self, plan_id: uuid.UUID) -> WorkoutPlan | None:
        """Recupera un plan estructurado por su ID."""
        ...


class IProgressRepository(Protocol):
    """Protocolo para registrar y consultar avance del cliente."""

    async def save_progress(self, progress: WorkoutProgress) -> WorkoutProgress:
        """Guarda un registro de avance de entrenamiento."""
        ...

    async def list_by_plan(self, plan_id: uuid.UUID) -> list[WorkoutProgress]:
        """Lista el historial de avance de una rutina específica."""
        ...
