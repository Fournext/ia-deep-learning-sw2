"""Pruebas complementarias para módulos core, excepciones y cálculo angular 3D."""


from app.core.exceptions import (
    BiomechanicalCalculationError,
    EntityNotFoundError,
    EvaluationNotFoundError,
    ExerciseIncompatibleError,
    GymAIError,
    ImageQualityLowError,
    InvalidFileTypeError,
    RecommendationNotFoundError,
    RoutineApprovalPendingError,
    VideoProcessingError,
    WorkoutPlanNotFoundError,
)
from app.core.logging import setup_logging
from app.infrastructure.cv.angle_calculator import AngleCalculator


def test_core_logging_setup() -> None:
    """Verifica la configuración del logger de la aplicación."""
    setup_logging()


def test_custom_domain_exceptions() -> None:
    """Verifica la instanciación y atributos de las excepciones personalizadas."""
    e1 = GymAIError("Error base de IA")
    assert e1.message == "Error base de IA"

    e2 = BiomechanicalCalculationError("División por cero")
    assert e2.details == "División por cero"

    e3 = ExerciseIncompatibleError("Sentadilla", "Lesión de menisco")
    assert e3.exercise_name == "Sentadilla"
    assert e3.restriction == "Lesión de menisco"

    e4 = RoutineApprovalPendingError("plan-123")
    assert e4.plan_id == "plan-123"

    e5 = EntityNotFoundError("Evaluacion", "eval-999")
    assert e5.entity_name == "Evaluacion"
    assert e5.identifier == "eval-999"

    e6 = EvaluationNotFoundError("eval-1")
    assert e6.identifier == "eval-1"

    e7 = WorkoutPlanNotFoundError("plan-1")
    assert e7.identifier == "plan-1"

    e8 = RecommendationNotFoundError("rec-1")
    assert e8.identifier == "rec-1"

    e9 = ImageQualityLowError(reason="Demasiado oscura", confidence=0.3)
    assert e9.confidence == 0.3
    assert e9.reason == "Demasiado oscura"

    e10 = VideoProcessingError("Codec no soportado")
    assert e10.reason == "Codec no soportado"

    e11 = InvalidFileTypeError(filename="doc.pdf", allowed=".jpg, .png")
    assert e11.filename == "doc.pdf"
    assert e11.allowed == ".jpg, .png"


def test_angle_calculator_edge_cases() -> None:
    """Verifica el cálculo de ángulos, pendientes y simetría en casos límite."""
    calc = AngleCalculator()

    # Caso puntos coincidentes (norma cero)
    assert calc.calculate_angle_2d((0.0, 0.0), (0.0, 0.0), (1.0, 1.0)) == 180.0

    # Pendiente vertical (dx = 0)
    assert calc.calculate_slope_degrees((1.0, 0.0), (1.0, 5.0)) == 90.0

    # Simetría con valores no positivos
    assert calc.calculate_horizontal_symmetry(0.0, 10.0) == 1.0
    assert calc.calculate_horizontal_symmetry(-5.0, 10.0) == 1.0
    assert calc.calculate_horizontal_symmetry(10.0, 10.0) == 1.0
    assert calc.calculate_horizontal_symmetry(8.0, 10.0) == 0.8
