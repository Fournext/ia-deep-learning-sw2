"""Pruebas unitarias para el calculador de ángulos biomecánicos."""

from app.infrastructure.cv.angle_calculator import AngleCalculator


def test_angle_perpendicular_vectors() -> None:
    """Verifica que dos vectores ortogonales formen exactamente un ángulo de 90°."""
    point_a = (0.0, 1.0)
    point_b = (0.0, 0.0)
    point_c = (1.0, 0.0)

    angle = AngleCalculator.calculate_angle_2d(point_a, point_b, point_c)
    assert abs(angle - 90.0) < 1e-2


def test_angle_straight_line() -> None:
    """Verifica que tres puntos alineados en sentido opuesto formen 180°."""
    point_a = (-1.0, 0.0)
    point_b = (0.0, 0.0)
    point_c = (1.0, 0.0)

    angle = AngleCalculator.calculate_angle_2d(point_a, point_b, point_c)
    assert abs(angle - 180.0) < 1e-2


def test_angle_colinear_same_direction() -> None:
    """Verifica que dos vectores en la misma dirección formen 0°."""
    point_a = (1.0, 1.0)
    point_b = (0.0, 0.0)
    point_c = (2.0, 2.0)

    angle = AngleCalculator.calculate_angle_2d(point_a, point_b, point_c)
    assert abs(angle - 0.0) < 1e-2


def test_angle_zero_norm_protection() -> None:
    """Verifica que puntos coincidentes no produzcan división por cero ni excepciones."""
    point_a = (0.0, 0.0)
    point_b = (0.0, 0.0)
    point_c = (1.0, 1.0)

    angle = AngleCalculator.calculate_angle_2d(point_a, point_b, point_c)
    assert angle == 180.0


def test_slope_degrees_horizontal() -> None:
    """Verifica que una línea perfectamente horizontal tenga pendiente 0°."""
    p_left = (0.2, 0.5)
    p_right = (0.8, 0.5)

    slope = AngleCalculator.calculate_slope_degrees(p_left, p_right)
    assert slope == 0.0


def test_slope_degrees_vertical() -> None:
    """Verifica que una línea vertical tenga pendiente de 90°."""
    p_top = (0.5, 0.2)
    p_bottom = (0.5, 0.8)

    slope = AngleCalculator.calculate_slope_degrees(p_top, p_bottom)
    assert slope == 90.0


def test_horizontal_symmetry_perfect() -> None:
    """Verifica que valores idénticos tengan un ratio de simetría de 1.0."""
    ratio = AngleCalculator.calculate_horizontal_symmetry(95.0, 95.0)
    assert ratio == 1.0


def test_horizontal_symmetry_asymmetric() -> None:
    """Verifica el cálculo del ratio de simetría cuando hay disparidad bilateral."""
    ratio = AngleCalculator.calculate_horizontal_symmetry(80.0, 100.0)
    assert ratio == 0.8
