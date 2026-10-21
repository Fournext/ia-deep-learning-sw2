"""Pruebas unitarias para el motor de recomendación híbrido."""

import uuid

from app.domain.entities.evaluation import Evaluation, FitnessGoal, FitnessLevel
from app.domain.entities.exercise import Exercise, MovementPattern, MovementType
from app.infrastructure.ml.hybrid_recommender import HybridRecommendationEngine


def create_sample_exercises() -> list[Exercise]:
    """Genera lista de ejercicios sintéticos con distintas características para pruebas."""
    return [
        Exercise(
            id=uuid.uuid4(),
            exercise_id_num=1,
            name="Barbell Deadlift",
            body_part="back",
            muscle_type="lower back",
            equipment="barbell",
            movement_type=MovementType.COMPOUND,
            movement_pattern=MovementPattern.HINGE,
            difficulty="advanced",
            sets_min=3.0,
            sets_max=4.0,
            reps_min=6,
            reps_max=8,
            est_duration_min=8.0,
        ),
        Exercise(
            id=uuid.uuid4(),
            exercise_id_num=2,
            name="Dumbbell Bicep Curl",
            body_part="arms",
            muscle_type="biceps",
            equipment="dumbbells",
            movement_type=MovementType.ISOLATION,
            movement_pattern=MovementPattern.PULL,
            difficulty="beginner",
            sets_min=3.0,
            sets_max=4.0,
            reps_min=10,
            reps_max=15,
            est_duration_min=6.0,
        ),
        Exercise(
            id=uuid.uuid4(),
            exercise_id_num=3,
            name="Bodyweight Squat",
            body_part="legs",
            muscle_type="quads",
            equipment="bodyweight",
            movement_type=MovementType.COMPOUND,
            movement_pattern=MovementPattern.SQUAT,
            difficulty="beginner",
            sets_min=3.0,
            sets_max=4.0,
            reps_min=12,
            reps_max=20,
            est_duration_min=5.0,
        ),
        Exercise(
            id=uuid.uuid4(),
            exercise_id_num=4,
            name="Pistol Squat",
            body_part="legs",
            muscle_type="quads",
            equipment="bodyweight",
            movement_type=MovementType.COMPOUND,
            movement_pattern=MovementPattern.SQUAT,
            difficulty="advanced",
            sets_min=3.0,
            sets_max=4.0,
            reps_min=5,
            reps_max=8,
            est_duration_min=7.0,
        ),
    ]


def test_recommender_filters_lumbar_restrictions() -> None:
    """Verifica que el recomendador excluya el peso muerto si el cliente tiene dolor lumbar."""
    engine = HybridRecommendationEngine()
    exercises = create_sample_exercises()

    evaluation = Evaluation(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        age=30,
        weight_kg=75.0,
        height_cm=178.0,
        fitness_level=FitnessLevel.INTERMEDIO,
        fitness_goal=FitnessGoal.HIPERTROFIA,
        available_days_per_week=3,
        session_duration_minutes=60,
        available_equipment=["barbell", "dumbbells", "bodyweight"],
        physical_restrictions=["molestia_lumbar_severa"],
    )

    result = engine.recommend(evaluation, exercises, posture_findings=[], top_k=5)
    rec_ids = result["recommended_exercise_ids"]

    deadlift_id = str(exercises[0].id)
    assert deadlift_id not in rec_ids
    assert result["scoring_breakdown"]["excluded_by_restrictions_or_equipment"] >= 1


def test_recommender_filters_knee_restrictions() -> None:
    """Verifica que el recomendador excluya ejercicios de impacto o flexión extrema (pistol squat) ante molestia de rodilla."""
    engine = HybridRecommendationEngine()
    exercises = create_sample_exercises()

    evaluation = Evaluation(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        age=28,
        weight_kg=70.0,
        height_cm=170.0,
        fitness_level=FitnessLevel.AVANZADO,
        fitness_goal=FitnessGoal.FUERZA,
        available_days_per_week=4,
        session_duration_minutes=60,
        available_equipment=["bodyweight", "dumbbells"],
        physical_restrictions=["lesion_rodilla_menisco"],
    )

    result = engine.recommend(evaluation, exercises, posture_findings=[], top_k=5)
    rec_ids = result["recommended_exercise_ids"]

    pistol_id = str(exercises[3].id)
    assert pistol_id not in rec_ids


def test_recommender_equipment_filtering() -> None:
    """Verifica que si el cliente solo tiene mancuernas, no se recomienden ejercicios con barra."""
    engine = HybridRecommendationEngine()
    exercises = create_sample_exercises()

    evaluation = Evaluation(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        age=22,
        weight_kg=65.0,
        height_cm=172.0,
        fitness_level=FitnessLevel.PRINCIPIANTE,
        fitness_goal=FitnessGoal.SALUD_GENERAL,
        available_days_per_week=3,
        session_duration_minutes=45,
        available_equipment=["dumbbells"],
        physical_restrictions=[],
    )

    result = engine.recommend(evaluation, exercises, posture_findings=[], top_k=5)
    rec_ids = result["recommended_exercise_ids"]

    deadlift_id = str(exercises[0].id)
    assert deadlift_id not in rec_ids
    # Curl con mancuernas sí debe estar incluido
    curl_id = str(exercises[1].id)
    assert curl_id in rec_ids
