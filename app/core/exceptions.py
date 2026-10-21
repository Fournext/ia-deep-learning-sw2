"""Definición de excepciones de dominio para el microservicio de IA.

Cada excepción modela un error semántico del negocio sin acoplamiento a HTTP.
"""


class GymAIError(Exception):
    """Excepción base para todos los errores del microservicio."""

    def __init__(self, message: str) -> None:
        """Inicializa la excepción con un mensaje descriptivo."""
        super().__init__(message)
        self.message = message


class EntityNotFoundError(GymAIError):
    """Lanzada cuando una entidad solicitada no existe."""

    def __init__(self, entity_name: str, identifier: str) -> None:
        """Inicializa con el nombre de la entidad y su identificador."""
        super().__init__(f"{entity_name} con identificador {identifier} no fue encontrada.")
        self.entity_name = entity_name
        self.identifier = identifier


class EvaluationNotFoundError(EntityNotFoundError):
    """Lanzada cuando una evaluación no existe."""

    def __init__(self, evaluation_id: str) -> None:
        """Inicializa con el ID de la evaluación."""
        super().__init__("Evaluación", evaluation_id)


class WorkoutPlanNotFoundError(EntityNotFoundError):
    """Lanzada cuando una rutina de entrenamiento no existe."""

    def __init__(self, plan_id: str) -> None:
        """Inicializa con el ID de la rutina."""
        super().__init__("Plan de entrenamiento", plan_id)


class RecommendationNotFoundError(EntityNotFoundError):
    """Lanzada cuando una recomendación no existe."""

    def __init__(self, recommendation_id: str) -> None:
        """Inicializa con el ID de la recomendación."""
        super().__init__("Recomendación", recommendation_id)


class ImageQualityLowError(GymAIError):
    """Lanzada cuando una imagen no cuenta con suficiente resolución o puntos anatómicos visibles."""

    def __init__(self, reason: str, confidence: float) -> None:
        """Inicializa con el motivo de baja calidad y la confianza obtenida."""
        super().__init__(
            f"Calidad de imagen insuficiente para evaluación postural: {reason} (Confianza: {confidence:.2f})"
        )
        self.reason = reason
        self.confidence = confidence


class VideoProcessingError(GymAIError):
    """Lanzada cuando ocurre un error al decodificar o analizar un video."""

    def __init__(self, reason: str) -> None:
        """Inicializa con la causa del error en el video."""
        super().__init__(f"Error en procesamiento de video de ejercicio: {reason}")
        self.reason = reason


class BiomechanicalCalculationError(GymAIError):
    """Lanzada ante datos geométricos anómalos o división por cero en vectores articulares."""

    def __init__(self, details: str) -> None:
        """Inicializa con el detalle del fallo biomecánico."""
        super().__init__(f"Fallo en cálculo biomecánico: {details}")
        self.details = details


class ExerciseIncompatibleError(GymAIError):
    """Lanzada cuando un ejercicio viola una restricción física severa del cliente."""

    def __init__(self, exercise_name: str, restriction: str) -> None:
        """Inicializa con el nombre del ejercicio y la restricción violada."""
        super().__init__(
            f"El ejercicio '{exercise_name}' es incompatible con la restricción '{restriction}'."
        )
        self.exercise_name = exercise_name
        self.restriction = restriction


class RoutineApprovalPendingError(GymAIError):
    """Lanzada al intentar asignar o activar una rutina que no ha sido aprobada por el entrenador."""

    def __init__(self, plan_id: str) -> None:
        """Inicializa con el ID del plan pendiente."""
        super().__init__(
            f"El plan de entrenamiento {plan_id} requiere aprobación obligatoria por un entrenador antes de su uso."
        )
        self.plan_id = plan_id


class InvalidFileTypeError(GymAIError):
    """Lanzada cuando se sube un formato de archivo no permitido."""

    def __init__(self, filename: str, allowed: str) -> None:
        """Inicializa con el nombre del archivo y los formatos permitidos."""
        super().__init__(
            f"Archivo '{filename}' no válido. Formatos soportados: {allowed}."
        )
        self.filename = filename
        self.allowed = allowed
