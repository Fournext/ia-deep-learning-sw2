"""Adaptador de infraestructura que implementa la interfaz ICVEngine."""

from typing import Any

from app.domain.entities.analysis_results import ExerciseVideoType, ImageViewType
from app.domain.interfaces.engines import ICVEngine
from app.infrastructure.cv.pose_detector import MediaPipePoseDetector
from app.infrastructure.cv.video_processor import VideoExerciseAnalyzer


class MediaPipeCVEngine(ICVEngine):
    """Implementación de la interfaz ICVEngine utilizando MediaPipe Pose."""

    def __init__(self) -> None:
        """Inicializa los detectores de imagen y video."""
        self._pose_detector = MediaPipePoseDetector()
        self._video_analyzer = VideoExerciseAnalyzer()

    def analyze_posture_image(
        self, image_bytes: bytes, view_type: ImageViewType
    ) -> dict[str, Any]:
        """Procesa una imagen y retorna los datos biomecánicos observables."""
        return self._pose_detector.extract_landmarks_from_image(image_bytes, view_type)

    def analyze_exercise_video(
        self, video_path: str, exercise_type: ExerciseVideoType
    ) -> dict[str, Any]:
        """Procesa un archivo de video y retorna conteo de repeticiones y errores."""
        return self._video_analyzer.analyze_video(video_path, exercise_type)
