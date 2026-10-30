"""Pruebas unitarias para la integración del dataset ampliado y funciones de normalización."""

import json
from pathlib import Path

import pytest

from app.domain.entities.exercise import Exercise, MovementPattern, MovementType
from app.infrastructure.repositories.in_memory_repositories import InMemoryExerciseRepository
from ml.scripts.import_free_exercise_db import (
    normalize_difficulty,
    normalize_equipment,
    normalize_movement_type,
    normalize_muscle,
    normalize_pattern,
)


def test_normalization_functions() -> None:
    """Valida que las funciones de normalización taxonómica operen correctamente."""
    # Músculos
    assert normalize_muscle(["abdominals"]) == ("abs", "abs")
    assert normalize_muscle(["quadriceps"]) == ("legs", "quadriceps")
    assert normalize_muscle(["lats"]) == ("back", "upper")
    assert normalize_muscle([]) == ("other", "full_body")

    # Patrones motores
    assert normalize_pattern("Goblet Squat", "push", "legs", "quadriceps") == "squat"
    assert normalize_pattern("Romanian Deadlift", "pull", "legs", "hamstrings") == "hinge"
    assert normalize_pattern("Crunch", None, "abs", "abs") == "core"
    assert normalize_pattern("Bench Press", "push", "chest", "chest") == "push"
    assert normalize_pattern("Lat Pulldown", "pull", "back", "upper") == "pull"
    assert normalize_pattern("Wrist Extension", "other", "forearms", "forearms") == "other"

    # Equipamiento
    assert normalize_equipment("body only") == "bodyweight"
    assert normalize_equipment("dumbbell") == "dumbbells"
    assert normalize_equipment("barbell") == "barbell"
    assert normalize_equipment(None) == "other"

    # Dificultad
    assert normalize_difficulty("expert") == "advanced"
    assert normalize_difficulty("beginner") == "beginner"
    assert normalize_difficulty(None) == "intermediate"

    # Tipo de movimiento
    assert normalize_movement_type("compound", "push", "barbell") == "compound"
    assert normalize_movement_type("isolation", "push", "dumbbells") == "isolation"
    assert normalize_movement_type(None, "squat", "barbell") == "compound"
    assert normalize_movement_type(None, "other", "dumbbells") == "isolation"


@pytest.mark.asyncio
async def test_dataset_integrity_and_repository_loading() -> None:
    """Verifica que el catálogo ampliado cargue correctamente en InMemoryExerciseRepository."""
    repo = InMemoryExerciseRepository()
    exercises = await repo.list_all()

    assert len(exercises) >= 900

    # Validar que todos los registros cumplan con las invariantes de dominio
    seen_ids = set()
    for ex in exercises:
        assert isinstance(ex, Exercise)
        assert ex.exercise_id_num >= 0
        assert ex.id not in seen_ids
        seen_ids.add(ex.id)
        assert len(ex.name) > 0
        assert isinstance(ex.movement_type, MovementType)
        assert isinstance(ex.movement_pattern, MovementPattern)
        assert ex.sets_min > 0
        assert ex.sets_max >= ex.sets_min
        assert ex.reps_min > 0
        assert ex.reps_max >= ex.reps_min
        assert ex.est_duration_min > 0


def test_extended_json_metadata_exists() -> None:
    """Verifica la existencia y formato del JSON extendido con instrucciones e imágenes."""
    extended_path = Path(__file__).resolve().parents[2] / "ml" / "datasets" / "exercises_extended.json"
    assert extended_path.exists()

    with open(extended_path, encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 800
    first = data[0]
    assert "instructions" in first
    assert "images" in first
    assert "category" in first


def test_process_dataset_synthetic(tmp_path: Path) -> None:
    """Verifica el flujo completo de combinación y procesamiento de datasets."""
    from ml.scripts.import_free_exercise_db import process_dataset

    # Crear CSV canónico dummy
    can_csv = tmp_path / "can.csv"
    can_csv.write_text(
        "exercise_id,exercise_name,body_part,muscle_type,equipment,movement_type,movement_pattern,difficulty,sets_min,sets_max,reps_min,reps_max,est_duration_min\n"
        "0,pull-ups,back,upper,pull-up bar,compound,pull,intermediate,3.0,4.0,8,12,7.4\n",
        encoding="utf-8",
    )

    # Crear JSON free-db dummy con 1 duplicado y 2 nuevos
    free_json = tmp_path / "free.json"
    dummy_free_data = [
        {
            "name": "Pull-ups",  # Duplicado (no debe agregarse)
            "force": "pull",
            "level": "intermediate",
            "mechanic": "compound",
            "equipment": "body only",
            "primaryMuscles": ["lats"],
        },
        {
            "name": "New Advanced Exercise",
            "force": "push",
            "level": "expert",
            "mechanic": "isolation",
            "equipment": "dumbbell",
            "primaryMuscles": ["chest"],
            "instructions": ["Step 1"],
            "images": ["img1.jpg"],
        },
        {
            "name": "New Beginner Exercise",
            "force": None,
            "level": "beginner",
            "mechanic": None,
            "equipment": None,
            "primaryMuscles": [],
        },
    ]
    free_json.write_text(json.dumps(dummy_free_data), encoding="utf-8")

    out_csv = tmp_path / "out.csv"
    out_json = tmp_path / "out.json"

    total = process_dataset(can_csv, free_json, out_csv, out_json)
    assert total == 3  # 1 original + 2 nuevos (1 ignorado por duplicado)
    assert out_csv.exists()
    assert out_json.exists()

