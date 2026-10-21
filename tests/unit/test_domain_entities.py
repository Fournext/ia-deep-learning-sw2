"""Pruebas unitarias para las entidades de dominio y reglas de negocio puras."""

import uuid

from app.domain.entities.evaluation import Evaluation, FitnessGoal, FitnessLevel
from app.domain.entities.exercise import Exercise, MovementPattern, MovementType
from app.domain.entities.workout_plan import PlanStatus, WorkoutPlan


def test_evaluation_bmi_calculation() -> None:
    """Verifica el cálculo del Índice de Masa Corporal (IMC)."""
    ev = Evaluation(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        age=25,
        weight_kg=70.0,
        height_cm=175.0,  # 1.75m -> 70 / (1.75^2) = 22.86
        fitness_level=FitnessLevel.INTERMEDIO,
        fitness_goal=FitnessGoal.HIPERTROFIA,
        available_days_per_week=4,
        session_duration_minutes=60,
    )
    assert ev.calculate_bmi() == 22.86


def test_evaluation_bmi_invalid_height() -> None:
    """Verifica que una altura inválida retorne 0.0 sin lanzar excepción."""
    ev = Evaluation(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        age=25,
        weight_kg=70.0,
        height_cm=0.0,
        fitness_level=FitnessLevel.PRINCIPIANTE,
        fitness_goal=FitnessGoal.SALUD_GENERAL,
        available_days_per_week=3,
        session_duration_minutes=45,
    )
    assert ev.calculate_bmi() == 0.0


def test_workout_plan_approval_states() -> None:
    """Verifica las reglas de estado de aprobación humana para rutinas."""
    plan = WorkoutPlan(
        id=uuid.uuid4(),
        recommendation_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        program_name="Rutina Prueba",
        status=PlanStatus.PENDIENTE_APROBACION,
    )
    assert not plan.is_approved()

    plan.status = PlanStatus.APROBADA
    assert plan.is_approved()

    plan.status = PlanStatus.MODIFICADA
    assert plan.is_approved()

    plan.status = PlanStatus.RECHAZADA
    assert not plan.is_approved()


def test_exercise_entity_properties() -> None:
    """Verifica la inicialización de la entidad Exercise."""
    ex = Exercise(
        id=uuid.uuid4(),
        exercise_id_num=1,
        name="Press Banca",
        body_part="chest",
        muscle_type="chest",
        equipment="barbell",
        movement_type=MovementType.COMPOUND,
        movement_pattern=MovementPattern.PUSH,
        difficulty="intermediate",
        sets_min=3.0,
        sets_max=4.0,
        reps_min=8,
        reps_max=12,
        est_duration_min=7.5,
    )
    assert ex.movement_type == MovementType.COMPOUND
    assert ex.movement_pattern == MovementPattern.PUSH
    assert ex.difficulty == "intermediate"
