"""Pruebas unitarias para StatelessPipelineService y la lógica de inferencia directa."""

import uuid

import pytest

from app.domain.entities.analysis_results import ImageViewType
from app.domain.entities.evaluation import FitnessGoal, FitnessLevel
from app.infrastructure.cv.cv_adapter import MediaPipeCVEngine
from app.infrastructure.ml.hybrid_recommender import HybridRecommendationEngine
from app.infrastructure.repositories.in_memory_repositories import default_exercise_repo
from app.modules.stateless_pipeline.service import StatelessPipelineService


@pytest.fixture
def stateless_service() -> StatelessPipelineService:
    """Instancia del servicio stateless con componentes reales en memoria."""
    return StatelessPipelineService(
        cv_engine=MediaPipeCVEngine(),
        rec_engine=HybridRecommendationEngine(),
        exercise_repo=default_exercise_repo,
    )


@pytest.mark.asyncio
async def test_stateless_service_basic_execution(stateless_service: StatelessPipelineService) -> None:
    """Verifica el cálculo de IMC, filtrado de ejercicios y días de entrenamiento."""
    client_id = uuid.uuid4()
    result = await stateless_service.execute(
        client_id=client_id,
        age=25,
        weight_kg=70.0,
        height_cm=175.0,
        fitness_level=FitnessLevel.PRINCIPIANTE,
        fitness_goal=FitnessGoal.PERDIDA_GRASA,
        available_days_per_week=3,
        session_duration_minutes=45,
        available_equipment=["dumbbells"],
        physical_restrictions=[],
    )

    assert result.client_id == client_id
    assert 22.0 < result.bmi < 24.0
    assert result.bmi_category == "Normopeso"
    assert result.persisted_to_database is False
    assert len(result.workout_plan.days) == 3
    assert result.workout_plan.status == "PENDIENTE_APROBACION"
    assert len(result.recommended_exercises) > 0


@pytest.mark.asyncio
async def test_stateless_service_with_restrictions(stateless_service: StatelessPipelineService) -> None:
    """Verifica que las restricciones de hombro y rodilla se integren en la justificación."""
    client_id = uuid.uuid4()
    result = await stateless_service.execute(
        client_id=client_id,
        age=40,
        weight_kg=95.0,
        height_cm=180.0,
        fitness_level=FitnessLevel.AVANZADO,
        fitness_goal=FitnessGoal.FUERZA,
        available_days_per_week=5,
        session_duration_minutes=60,
        available_equipment=["dumbbells", "barbell", "cable"],
        physical_restrictions=["hombro", "lumbar"],
    )

    assert result.bmi_category in ["Sobrepeso", "Obesidad Grado I"]
    assert "hombro" in result.workout_plan.justification
    assert "lumbar" in result.workout_plan.justification
    assert len(result.workout_plan.days) == 5


@pytest.mark.asyncio
async def test_stateless_service_with_synthetic_photo(
    stateless_service: StatelessPipelineService, sample_image_bytes: bytes
) -> None:
    """Verifica que al procesar una foto sintética se capture la calidad sin romper la ejecución."""
    client_id = uuid.uuid4()
    result = await stateless_service.execute(
        client_id=client_id,
        age=28,
        weight_kg=75.0,
        height_cm=178.0,
        fitness_level=FitnessLevel.INTERMEDIO,
        fitness_goal=FitnessGoal.HIPERTROFIA,
        available_days_per_week=4,
        session_duration_minutes=60,
        available_equipment=["dumbbells", "machine"],
        physical_restrictions=[],
        photo_frontal_bytes=sample_image_bytes,
    )

    assert len(result.photo_analyses) == 1
    photo = result.photo_analyses[0]
    assert photo.view_type == ImageViewType.FRONTAL.value
    assert result.persisted_to_database is False


@pytest.mark.asyncio
async def test_exercise_repo_queries() -> None:
    """Verifica consultas por número de ejercicio e ID en el catálogo canónico en memoria."""
    ex_list = await default_exercise_repo.list_all()
    assert len(ex_list) > 0

    first_ex = ex_list[0]
    by_num = await default_exercise_repo.get_by_exercise_num(first_ex.exercise_id_num)
    assert by_num is not None
    assert by_num.name == first_ex.name

    by_id = await default_exercise_repo.get_by_id(first_ex.id)
    assert by_id is not None
    assert by_id.exercise_id_num == first_ex.exercise_id_num

    assert await default_exercise_repo.get_by_exercise_num(999999) is None
    assert await default_exercise_repo.get_by_id(uuid.uuid4()) is None
