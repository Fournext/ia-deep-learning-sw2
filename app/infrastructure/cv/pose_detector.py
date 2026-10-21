"""Módulo de detección de postura y extracción de puntos anatómicos con MediaPipe Pose Tasks."""

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
from app.core.exceptions import ImageQualityLowError, InvalidFileTypeError
from app.domain.entities.analysis_results import ImageViewType
from app.infrastructure.cv.angle_calculator import AngleCalculator


class MediaPipePoseDetector:
    """Detector de pose basado en la API moderna de MediaPipe Tasks (PoseLandmarker)."""

    LANDMARK_NAMES = [
        "nose",
        "left_eye_inner",
        "left_eye",
        "left_eye_outer",
        "right_eye_inner",
        "right_eye",
        "right_eye_outer",
        "left_ear",
        "right_ear",
        "mouth_left",
        "mouth_right",
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_wrist",
        "right_wrist",
        "left_pinky",
        "right_pinky",
        "left_index",
        "right_index",
        "left_thumb",
        "right_thumb",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_heel",
        "right_heel",
        "left_foot_index",
        "right_foot_index",
    ]

    def __init__(self, model_path: str | None = None) -> None:
        """Inicializa el detector con el modelo de landmarks."""
        self._model_path = model_path or settings.POSE_MODEL_PATH
        self._calc = AngleCalculator()

    def _get_landmarker(self, running_mode: RunningMode = RunningMode.IMAGE) -> PoseLandmarker:
        """Crea una instancia de PoseLandmarker en el modo deseado."""
        if not os.path.exists(self._model_path):
            raise ImageQualityLowError(
                f"Archivo de modelo de pose no encontrado en {self._model_path}", 0.0
            )

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self._model_path),
            running_mode=running_mode,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            num_poses=1,
        )
        return PoseLandmarker.create_from_options(options)

    def extract_landmarks_from_image(
        self, image_bytes: bytes, view_type: ImageViewType
    ) -> dict[str, Any]:
        """Procesa una imagen estática y extrae landmarks, ángulos y métricas de alineación."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise InvalidFileTypeError("imagen", "JPEG, PNG, WEBP")

        h, w, _ = img.shape
        if h < 200 or w < 200:
            raise ImageQualityLowError("Resolución de imagen excesivamente reducida", 0.1)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        landmarker = self._get_landmarker(RunningMode.IMAGE)
        try:
            results = landmarker.detect(mp_image)
        finally:
            landmarker.close()

        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            raise ImageQualityLowError(
                "No se detectó un cuerpo humano completo visible en la toma", 0.0
            )

        first_pose = results.pose_landmarks[0]
        landmarks: dict[str, dict[str, float]] = {}
        visibilities: list[float] = []

        for idx, lm in enumerate(first_pose):
            if idx >= len(self.LANDMARK_NAMES):
                break
            name = self.LANDMARK_NAMES[idx]
            vis = getattr(lm, "visibility", 1.0)
            if vis is None or vis < 0:
                vis = 1.0
            landmarks[name] = {
                "x": round(float(lm.x), 4),
                "y": round(float(lm.y), 4),
                "z": round(float(lm.z), 4),
                "visibility": round(float(vis), 3),
            }
            visibilities.append(float(vis))

        avg_confidence = round(float(np.mean(visibilities)), 3) if visibilities else 0.0
        if avg_confidence < settings.MIN_LANDMARK_VISIBILITY_CONFIDENCE:
            raise ImageQualityLowError(
                f"Confianza promedio de visibilidad insuficiente ({avg_confidence} < {settings.MIN_LANDMARK_VISIBILITY_CONFIDENCE})",
                avg_confidence,
            )

        angles: dict[str, float] = {}

        # Extremidades superiores
        l_sh = (landmarks["left_shoulder"]["x"], landmarks["left_shoulder"]["y"])
        l_el = (landmarks["left_elbow"]["x"], landmarks["left_elbow"]["y"])
        l_wr = (landmarks["left_wrist"]["x"], landmarks["left_wrist"]["y"])
        angles["left_elbow_angle"] = self._calc.calculate_angle_2d(l_sh, l_el, l_wr)

        r_sh = (landmarks["right_shoulder"]["x"], landmarks["right_shoulder"]["y"])
        r_el = (landmarks["right_elbow"]["x"], landmarks["right_elbow"]["y"])
        r_wr = (landmarks["right_wrist"]["x"], landmarks["right_wrist"]["y"])
        angles["right_elbow_angle"] = self._calc.calculate_angle_2d(r_sh, r_el, r_wr)

        # Extremidades inferiores
        l_hip = (landmarks["left_hip"]["x"], landmarks["left_hip"]["y"])
        l_knee = (landmarks["left_knee"]["x"], landmarks["left_knee"]["y"])
        l_ank = (landmarks["left_ankle"]["x"], landmarks["left_ankle"]["y"])
        angles["left_knee_angle"] = self._calc.calculate_angle_2d(l_hip, l_knee, l_ank)

        r_hip = (landmarks["right_hip"]["x"], landmarks["right_hip"]["y"])
        r_knee = (landmarks["right_knee"]["x"], landmarks["right_knee"]["y"])
        r_ank = (landmarks["right_ankle"]["x"], landmarks["right_ankle"]["y"])
        angles["right_knee_angle"] = self._calc.calculate_angle_2d(r_hip, r_knee, r_ank)

        # Ángulo tronco / cadera
        angles["left_hip_angle"] = self._calc.calculate_angle_2d(l_sh, l_hip, l_knee)
        angles["right_hip_angle"] = self._calc.calculate_angle_2d(r_sh, r_hip, r_knee)

        # Inclinaciones bilaterales y simetría
        shoulder_slope = self._calc.calculate_slope_degrees(l_sh, r_sh)
        hip_slope = self._calc.calculate_slope_degrees(l_hip, r_hip)
        knee_slope = self._calc.calculate_slope_degrees(l_knee, r_knee)
        knee_symmetry = self._calc.calculate_horizontal_symmetry(
            angles["left_knee_angle"], angles["right_knee_angle"]
        )

        observations: list[str] = []
        if shoulder_slope > 4.5:
            observations.append(
                f"Ligera asimetría observable en línea de hombros (desviación: {shoulder_slope}°)"
            )
        else:
            observations.append("Alineación de hombros simétrica dentro de márgenes normales")

        if hip_slope > 4.5:
            observations.append(
                f"Ligera inclinación observable en línea de caderas (desviación: {hip_slope}°)"
            )

        posture_metrics: dict[str, Any] = {
            "shoulder_slope_degrees": shoulder_slope,
            "hip_slope_degrees": hip_slope,
            "knee_slope_degrees": knee_slope,
            "knee_symmetry_ratio": knee_symmetry,
            "observations": observations,
        }

        return {
            "confidence_score": avg_confidence,
            "has_quality_issues": False,
            "detected_landmarks": landmarks,
            "calculated_angles": angles,
            "posture_metrics": posture_metrics,
        }
