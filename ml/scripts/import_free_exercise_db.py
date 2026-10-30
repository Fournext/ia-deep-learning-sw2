"""Script de migración y enriquecimiento del catálogo de ejercicios.

Integra los ejercicios de 'free-exercise-db' dentro del catálogo canónico
del microservicio, normalizando taxonomía biomecánica, patrones motores y dificultad
conforme a los estándares de Clean Architecture y la entidad Exercise.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def normalize_muscle(primary_muscles: list[str]) -> tuple[str, str]:
    """Mapea la lista de músculos primarios a (body_part, muscle_type).

    Args:
        primary_muscles: Lista de strings con los músculos primarios en inglés.

    Returns:
        Tupla con (body_part, muscle_type).
    """
    if not primary_muscles:
        return "other", "full_body"

    m = primary_muscles[0].lower().strip()
    mapping: dict[str, tuple[str, str]] = {
        "abdominals": ("abs", "abs"),
        "chest": ("chest", "chest"),
        "biceps": ("arms", "biceps"),
        "triceps": ("arms", "triceps"),
        "forearms": ("forearms", "forearms"),
        "quadriceps": ("legs", "quadriceps"),
        "hamstrings": ("legs", "hamstrings"),
        "calves": ("legs", "calves"),
        "glutes": ("legs", "glutes"),
        "adductors": ("legs", "adductors"),
        "abductors": ("legs", "abductors"),
        "lats": ("back", "upper"),
        "middle back": ("back", "upper"),
        "traps": ("back", "upper"),
        "lower back": ("back", "lower"),
        "shoulders": ("shoulders", "shoulders"),
        "neck": ("shoulders", "neck"),
    }
    return mapping.get(m, ("other", m))


def normalize_pattern(name: str, force: str | None, body_part: str, muscle_type: str) -> str:
    """Determina el patrón motor biomecánico.

    Args:
        name: Nombre del ejercicio.
        force: Dirección de la fuerza (pull, push, static).
        body_part: Zona del cuerpo principal.
        muscle_type: Subgrupo muscular.

    Returns:
        Patrón motor: push, pull, squat, hinge, core u other.
    """
    name_l = name.lower()
    if body_part == "abs":
        return "core"

    # Sentadilla o variantes dominantes de rodilla
    if any(k in name_l for k in ["squat", "lunge", "leg press", "step-up", "step up"]):
        return "squat"

    # Bisagra de cadera
    if any(k in name_l for k in ["deadlift", "hip thrust", "good morning", "hyperextension"]) or (
        muscle_type in ("hamstrings", "lower") and force == "pull"
    ):
        return "hinge"

    if force == "push":
        return "push"
    if force == "pull":
        return "pull"

    if muscle_type in ("chest", "shoulders", "triceps"):
        return "push"
    if muscle_type in ("biceps", "upper"):
        return "pull"

    return "other"


def normalize_equipment(equipment: str | None) -> str:
    """Normaliza el equipamiento a la taxonomía estándar del sistema.

    Args:
        equipment: Equipamiento en formato original de free-exercise-db.

    Returns:
        Equipamiento normalizado.
    """
    if not equipment:
        return "other"
    eq = equipment.lower().strip()
    mapping = {
        "body only": "bodyweight",
        "dumbbell": "dumbbells",
        "barbell": "barbell",
        "cable": "cable",
        "machine": "machine",
        "kettlebells": "kettlebells",
        "bands": "bands",
        "exercise ball": "other",
        "foam roll": "other",
        "e-z curl bar": "barbell",
        "medicine ball": "other",
        "other": "other",
    }
    return mapping.get(eq, "other")


def normalize_difficulty(level: str | None) -> str:
    """Normaliza el nivel de dificultad a beginner, intermediate o advanced.

    Args:
        level: Nivel en free-exercise-db (beginner, intermediate, expert).

    Returns:
        Dificultad normalizada.
    """
    if not level:
        return "intermediate"
    l_clean = level.lower().strip()
    if l_clean == "expert":
        return "advanced"
    if l_clean in ("beginner", "intermediate", "advanced"):
        return l_clean
    return "intermediate"


def normalize_movement_type(mechanic: str | None, pattern: str, equipment: str) -> str:
    """Determina si el movimiento es compuesto o de aislamiento.

    Args:
        mechanic: compound o isolation si existe.
        pattern: Patrón motor inferido.
        equipment: Equipamiento necesario.

    Returns:
        'compound' o 'isolation'.
    """
    if mechanic in ("compound", "isolation"):
        return mechanic
    if pattern in ("squat", "hinge") or (pattern in ("push", "pull") and equipment in ("barbell", "bodyweight")):
        return "compound"
    return "isolation"


def process_dataset(
    canonical_csv_path: Path,
    free_db_json_path: Path,
    output_csv_path: Path,
    output_json_extended_path: Path,
) -> int:
    """Combina el dataset canónico con free-exercise-db sin duplicados.

    Args:
        canonical_csv_path: Ruta al CSV canónico existente.
        free_db_json_path: Ruta al JSON exercises.json de free-exercise-db.
        output_csv_path: Ruta de salida para el CSV unificado.
        output_json_extended_path: Ruta de salida con metadatos extendidos (instrucciones, fotos).

    Returns:
        Total de ejercicios en el catálogo consolidado.
    """
    existing_exercises: list[dict[str, Any]] = []
    known_names: set[str] = set()

    # 1. Cargar ejercicios canónicos existentes para preservar IDs 0..51
    if canonical_csv_path.exists():
        with open(canonical_csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_exercises.append(dict(row))
                known_names.add(row["exercise_name"].lower().strip())

    next_id = len(existing_exercises)

    # 2. Leer free-exercise-db
    with open(free_db_json_path, encoding="utf-8") as f:
        free_db_data: list[dict[str, Any]] = json.load(f)

    extended_records: list[dict[str, Any]] = []

    for raw in free_db_data:
        raw_name = raw.get("name", "").strip()
        norm_name = raw_name.lower()
        if not norm_name or norm_name in known_names:
            continue

        known_names.add(norm_name)
        body_part, muscle_type = normalize_muscle(raw.get("primaryMuscles", []))
        force = raw.get("force")
        pattern = normalize_pattern(raw_name, force, body_part, muscle_type)
        equipment = normalize_equipment(raw.get("equipment"))
        difficulty = normalize_difficulty(raw.get("level"))
        mov_type = normalize_movement_type(raw.get("mechanic"), pattern, equipment)

        # Parámetros estándar basados en dificultad
        if difficulty == "beginner":
            sets_min, sets_max = 3.0, 3.0
            reps_min, reps_max = 10, 15
            est_duration = 8.0
        elif difficulty == "advanced":
            sets_min, sets_max = 4.0, 5.0
            reps_min, reps_max = 6, 10
            est_duration = 9.0
        else:  # intermediate
            sets_min, sets_max = 3.0, 4.0
            reps_min, reps_max = 8, 12
            est_duration = 7.5

        ex_record: dict[str, Any] = {
            "exercise_id": next_id,
            "exercise_name": norm_name,
            "body_part": body_part,
            "muscle_type": muscle_type,
            "equipment": equipment,
            "movement_type": mov_type,
            "movement_pattern": pattern,
            "difficulty": difficulty,
            "sets_min": sets_min,
            "sets_max": sets_max,
            "reps_min": reps_min,
            "reps_max": reps_max,
            "est_duration_min": est_duration,
        }
        existing_exercises.append(ex_record)

        # Guardar registro extendido con instrucciones e imágenes
        extended_records.append({
            **ex_record,
            "instructions": raw.get("instructions", []),
            "images": raw.get("images", []),
            "category": raw.get("category", "strength"),
            "secondary_muscles": raw.get("secondaryMuscles", []),
        })
        next_id += 1

    # 3. Guardar CSV consolidado
    fieldnames = [
        "exercise_id",
        "exercise_name",
        "body_part",
        "muscle_type",
        "equipment",
        "movement_type",
        "movement_pattern",
        "difficulty",
        "sets_min",
        "sets_max",
        "reps_min",
        "reps_max",
        "est_duration_min",
    ]
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in existing_exercises:
            writer.writerow({k: r[k] for k in fieldnames})

    # 4. Guardar JSON extendido
    with open(output_json_extended_path, "w", encoding="utf-8") as f:
        json.dump(extended_records, f, indent=2, ensure_ascii=False)

    return len(existing_exercises)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[2]
    canonical_csv = base_dir / "ml" / "datasets" / "exercises_clean.csv"
    free_db_json = Path(r"C:\Users\sebas\Desktop\SW2\2do Parcial\EJERCICIOS\free-exercise-db\dist\exercises.json")
    out_csv = base_dir / "ml" / "datasets" / "exercises_clean.csv"
    out_json = base_dir / "ml" / "datasets" / "exercises_extended.json"

    total = process_dataset(canonical_csv, free_db_json, out_csv, out_json)
    print(f"Dataset consolidado exitosamente con {total} ejercicios.")
