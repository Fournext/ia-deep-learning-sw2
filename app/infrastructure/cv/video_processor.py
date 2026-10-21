"""Procesador biomecánico de video para análisis de sentadillas y flexiones con MediaPipe Tasks."""

import os
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    PoseLandmarker,
    PoseLandmarkerOptions,
    RunningMode,
)

from app.core.config import settings
from app.core.exceptions import VideoProcessingError
from app.domain.entities.analysis_results import ExerciseVideoType
from app.infrastructure.cv.angle_calculator import AngleCalculator


class VideoExerciseAnalyzer:
    """Analizador de movimiento y contador de repeticiones para videos de ejercicios."""

    def __init__(self, model_path: str | None = None) -> None:
        """Inicializa el analizador con el modelo de pose."""
        self._model_path = model_path or settings.POSE_MODEL_PATH
        self._calc = AngleCalculator()

    def _get_landmarker(self) -> PoseLandmarker:
        """Crea instancia de PoseLandmarker en modo VIDEO."""
        if not os.path.exists(self._model_path):
            raise VideoProcessingError(f"Modelo de pose no encontrado en {self._model_path}")

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self._model_path),
            running_mode=RunningMode.VIDEO,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            num_poses=1,
        )
        return PoseLandmarker.create_from_options(options)

    def analyze_video(
        self, video_path: str, exercise_type: ExerciseVideoType
    ) -> dict[str, Any]:
        """Procesa el video frame a frame para contar repeticiones y evaluar forma."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoProcessingError(f"No se pudo abrir el archivo de video en '{video_path}'")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames < 10:
            cap.release()
            raise VideoProcessingError(
                "El video es demasiado corto para análisis de movimiento (mínimo 10 fotogramas)"
            )

        rep_counter = 0
        state = "UP"
        min_angle_in_rep = 180.0
        depth_angles: list[float] = []
        execution_errors: list[str] = []
        rep_details: list[dict[str, Any]] = []

        valid_frames_count = 0
        landmarker = self._get_landmarker()

        try:
            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_idx += 1
                timestamp_ms = int((frame_idx / fps) * 1000)

                # Submuestreo para agilidad en CPU
                if fps > 25 and frame_idx % 2 != 0:
                    continue

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                results = landmarker.detect_for_video(mp_image, timestamp_ms)

                if not results.pose_landmarks or len(results.pose_landmarks) == 0:
                    continue

                valid_frames_count += 1
                landmarks = results.pose_landmarks[0]

                if exercise_type == ExerciseVideoType.SQUAT:
                    # Cadera, rodilla y tobillo izquierdos (23, 25, 27)
                    l_hip = (landmarks[23].x, landmarks[23].y)
                    l_knee = (landmarks[25].x, landmarks[25].y)
                    l_ank = (landmarks[27].x, landmarks[27].y)
                    knee_angle = self._calc.calculate_angle_2d(l_hip, l_knee, l_ank)

                    if knee_angle < min_angle_in_rep:
                        min_angle_in_rep = knee_angle

                    if state == "UP" and knee_angle < 120.0:
                        state = "DOWN"
                    elif state == "DOWN" and knee_angle > 155.0:
                        rep_counter += 1
                        depth_angles.append(min_angle_in_rep)
                        is_good_depth = min_angle_in_rep <= 100.0
                        if not is_good_depth:
                            execution_errors.append(
                                f"Repetición {rep_counter}: Profundidad insuficiente ({min_angle_in_rep}° > 100°)"
                            )

                        rep_details.append({
                            "rep_number": rep_counter,
                            "min_depth_angle": min_angle_in_rep,
                            "completed": True,
                            "proper_depth": is_good_depth,
                        })
                        state = "UP"
                        min_angle_in_rep = 180.0

                elif exercise_type == ExerciseVideoType.PUSHUP:
                    # Hombro, codo y muñeca izquierdos (11, 13, 15)
                    l_sh = (landmarks[11].x, landmarks[11].y)
                    l_el = (landmarks[13].x, landmarks[13].y)
                    l_wr = (landmarks[15].x, landmarks[15].y)
                    elbow_angle = self._calc.calculate_angle_2d(l_sh, l_el, l_wr)

                    if elbow_angle < min_angle_in_rep:
                        min_angle_in_rep = elbow_angle

                    if state == "UP" and elbow_angle < 110.0:
                        state = "DOWN"
                    elif state == "DOWN" and elbow_angle > 150.0:
                        rep_counter += 1
                        depth_angles.append(min_angle_in_rep)
                        is_good_depth = min_angle_in_rep <= 95.0
                        if not is_good_depth:
                            execution_errors.append(
                                f"Repetición {rep_counter}: Descenso incompleto ({min_angle_in_rep}° > 95°)"
                            )

                        rep_details.append({
                            "rep_number": rep_counter,
                            "min_depth_angle": min_angle_in_rep,
                            "completed": True,
                            "proper_depth": is_good_depth,
                        })
                        state = "UP"
                        min_angle_in_rep = 180.0

        finally:
            cap.release()
            landmarker.close()

        if valid_frames_count < 5:
            raise VideoProcessingError(
                "No fue posible detectar suficientes puntos articulares en el video para validar el movimiento"
            )

        avg_depth = float(round(np.mean(depth_angles), 2)) if depth_angles else 0.0
        execution_score = round(max(0.0, 100.0 - (len(execution_errors) * 15.0)), 1) if rep_counter > 0 else 0.0

        return {
            "completed_reps": rep_counter,
            "average_depth_angle": avg_depth,
            "execution_score": execution_score,
            "rep_details": rep_details,
            "execution_errors": list(set(execution_errors)),
        }
