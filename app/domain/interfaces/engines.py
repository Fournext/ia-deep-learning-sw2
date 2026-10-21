"""Protocolos para los motores de Visión Artificial y Recomendación."""

from typing import Any, Protocol

from app.domain.entities.analysis_results import ExerciseVideoType, ImageViewType
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.exercise import Exercise


class ICVEngine(Protocol):
    """Protocolo del motor de visión por computadora."""

    def analyze_posture_image(
        self, image_bytes: bytes, view_type: ImageViewType
    ) -> dict[str, Any]:
        """Procesa una imagen y retorna landmarks, ángulos articulares y simetría.

        Args:
            image_bytes: Contenido binario del archivo de imagen.
            view_type: Vista anatómica (FRONTAL, LATERAL, POSTERIOR).

        Returns:
            Diccionario estructurado con métricas de postura y factor de confianza.
        """
        ...

    def analyze_exercise_video(
        self, video_path: str, exercise_type: ExerciseVideoType
    ) -> dict[str, Any]:
        """Procesa un archivo de video temporal y cuenta repeticiones y fases.

        Args:
            video_path: Ruta al archivo local de video temporal.
            exercise_type: Tipo de ejercicio (SQUAT o PUSHUP).

        Returns:
            Diccionario con repeticiones completadas, errores y ángulos medios.
        """
        ...


class IRecommendationEngine(Protocol):
    """Protocolo del motor híbrido de recomendación."""

    def recommend(
        self,
        evaluation: Evaluation,
        available_exercises: list[Exercise],
        posture_findings: list[str],
        top_k: int = 10,
    ) -> dict[str, Any]:
        """Genera recomendaciones priorizadas de ejercicios.

        Args:
            evaluation: Perfil físico y objetivos del cliente.
            available_exercises: Catálogo de ejercicios disponibles.
            posture_findings: Observaciones biomecánicas detectadas por visión.
            top_k: Cantidad de ejercicios a sugerir.

        Returns:
            Diccionario con IDs de ejercicios, motor utilizado y desglose de score.
        """
        ...
