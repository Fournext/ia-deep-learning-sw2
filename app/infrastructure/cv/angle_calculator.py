"""Módulo para cálculos trigonométricos y biomecánicos articulares."""

import math

import numpy as np


class AngleCalculator:
    """Calculador de ángulos articulares y métricas de alineación corporal."""

    @staticmethod
    def calculate_angle_2d(
        point_a: tuple[float, float],
        point_b: tuple[float, float],
        point_c: tuple[float, float],
    ) -> float:
        """Calcula el ángulo en grados formado por tres puntos en el plano 2D con vértice en B.

        Args:
            point_a: Coordenadas (x, y) del primer punto.
            point_b: Coordenadas (x, y) del punto vértice (articulación central).
            point_c: Coordenadas (x, y) del tercer punto.

        Returns:
            Ángulo en grados en el rango [0.0, 180.0].
        """
        ba = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]], dtype=np.float64)
        bc = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]], dtype=np.float64)

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba < 1e-6 or norm_bc < 1e-6:
            return 180.0

        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        angle = np.degrees(np.arccos(cosine_angle))
        return float(round(angle, 2))

    @staticmethod
    def calculate_slope_degrees(
        point_left: tuple[float, float], point_right: tuple[float, float]
    ) -> float:
        """Calcula la inclinación en grados de un segmento bilateral respecto a la horizontal.

        Útil para evaluar inclinación de hombros (acromion) o caderas (cresta ilíaca).

        Args:
            point_left: Coordenadas (x, y) del punto izquierdo.
            point_right: Coordenadas (x, y) del punto derecho.

        Returns:
            Inclinación absoluta en grados.
        """
        dx = point_right[0] - point_left[0]
        dy = point_right[1] - point_left[1]

        if abs(dx) < 1e-6:
            return 90.0

        angle_rad = math.atan2(abs(dy), abs(dx))
        return float(round(math.degrees(angle_rad), 2))

    @staticmethod
    def calculate_horizontal_symmetry(
        left_val: float, right_val: float
    ) -> float:
        """Calcula el ratio de simetría bilateral entre dos magnitudes (0.0 a 1.0).

        Args:
            left_val: Magnitud o ángulo del lado izquierdo.
            right_val: Magnitud o ángulo del lado derecho.

        Returns:
            Ratio normalizado (1.0 = perfecta simetría).
        """
        if left_val <= 0 or right_val <= 0:
            return 1.0
        return float(round(min(left_val, right_val) / max(left_val, right_val), 3))
