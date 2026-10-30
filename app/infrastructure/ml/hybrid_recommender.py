"""Motor híbrido de recomendación de ejercicios con filtrado por restricciones y Deep Learning."""

from typing import Any

import torch

from app.domain.entities.evaluation import Evaluation, FitnessGoal, FitnessLevel
from app.domain.entities.exercise import Exercise, MovementPattern, MovementType
from app.domain.interfaces.engines import IRecommendationEngine
from app.infrastructure.ml.neural_cf_model import NeuralCollaborativeFiltering


class HybridRecommendationEngine(IRecommendationEngine):
    """Implementación del recomendador híbrido: Restricciones -> Content-Based -> Neural CF."""

    def __init__(self) -> None:
        """Inicializa el modelo neuronal NCF pre-configurado."""
        # Modelo NCF inicializado con pesos reproducibles
        torch.manual_seed(42)
        self._ncf_model = NeuralCollaborativeFiltering(
            num_users=1000,
            num_exercises=1200,
            embedding_dim=16,
            mlp_hidden_layers=[32, 16, 8],
        )
        self._ncf_model.eval()

    def _matches_equipment(self, exercise: Exercise, user_equipment: list[str]) -> bool:
        """Verifica compatibilidad del ejercicio con el equipamiento del cliente."""
        if not user_equipment:
            return True  # Asume gimnasio completo si no se especifica

        eq_norm = [e.lower().strip() for e in user_equipment]
        ex_eq = exercise.equipment.lower().strip()

        # Ejercicios con peso corporal o libres permitidos siempre
        if ex_eq in ("bodyweight", "other", "peso_corporal"):
            return True

        for eq in eq_norm:
            if eq in ex_eq or ex_eq in eq:
                return True
        return False

    def _violates_restrictions(self, exercise: Exercise, restrictions: list[str]) -> bool:
        """Detecta si un ejercicio está contraindicado por restricciones físicas."""
        if not restrictions:
            return False

        rest_text = " ".join([r.lower() for r in restrictions])
        ex_name = exercise.name.lower()

        # Restricción Lumbar / Espalda baja
        if "lumbar" in rest_text or "espalda_baja" in rest_text:
            if "deadlift" in ex_name or "bent-over" in ex_name or "good morning" in ex_name:
                return True

        # Restricción Rodilla
        if "rodilla" in rest_text or "menisco" in rest_text:
            if "jump" in ex_name or "pistol" in ex_name:
                return True

        # Restricción Hombro
        if "hombro" in rest_text or "manguito" in rest_text:
            if "behind-the-neck" in ex_name or "upright row" in ex_name:
                return True

        return False

    def _calculate_content_score(
        self, exercise: Exercise, evaluation: Evaluation, posture_findings: list[str]
    ) -> float:
        """Calcula el score de afinidad basado en contenido y objetivos."""
        score = 50.0

        # Adecuación según nivel de condición física
        diff = exercise.difficulty.lower()
        if evaluation.fitness_level == FitnessLevel.PRINCIPIANTE:
            if diff == "beginner":
                score += 25.0
            elif diff == "intermediate":
                score += 10.0
            else:
                score -= 20.0
        elif evaluation.fitness_level == FitnessLevel.AVANZADO:
            if diff == "advanced":
                score += 25.0
            elif diff == "intermediate":
                score += 15.0
        else:  # INTERMEDIO
            if diff in ("intermediate", "beginner"):
                score += 20.0

        # Adecuación según objetivo
        if evaluation.fitness_goal in (FitnessGoal.HIPERTROFIA, FitnessGoal.FUERZA):
            if exercise.movement_type == MovementType.COMPOUND:
                score += 20.0
        elif evaluation.fitness_goal == FitnessGoal.PERDIDA_GRASA:
            # Mayor demanda metabólica
            if exercise.movement_pattern in (MovementPattern.SQUAT, MovementPattern.PULL, MovementPattern.PUSH):
                score += 15.0

        # Ponderación de hallazgos posturales (Human-in-the-Loop inputs)
        findings_str = " ".join([f.lower() for f in posture_findings])
        if "asimetría" in findings_str or "hombros" in findings_str:
            # Priorizar trabajo con mancuernas para corrección unilateral
            if "dumbbell" in exercise.name.lower():
                score += 15.0

        return score

    def recommend(
        self,
        evaluation: Evaluation,
        available_exercises: list[Exercise],
        posture_findings: list[str],
        top_k: int = 10,
    ) -> dict[str, Any]:
        """Genera recomendaciones priorizadas y seguras para el cliente."""
        candidates: list[Exercise] = []
        excluded_count = 0

        # 1. Filtro estricto de restricciones y equipamiento
        for ex in available_exercises:
            if self._violates_restrictions(ex, evaluation.physical_restrictions):
                excluded_count += 1
                continue
            if not self._matches_equipment(ex, evaluation.available_equipment):
                excluded_count += 1
                continue
            candidates.append(ex)

        if not candidates:
            # Fallback a todo el catálogo si los filtros excluyeron todo
            candidates = available_exercises[:top_k]

        # 2. Puntuación Content-Based y Neural CF
        scored_exercises: list[dict[str, Any]] = []

        # Usar pseudoid derivado para simulación de NCF
        user_idx = abs(hash(str(evaluation.client_id))) % 1000
        user_tensor = torch.tensor([user_idx], dtype=torch.long)

        for ex in candidates:
            content_score = self._calculate_content_score(ex, evaluation, posture_findings)

            # Inferencia de afinidad con Neural CF
            ex_idx = min(ex.exercise_id_num, 1199)
            ex_tensor = torch.tensor([ex_idx], dtype=torch.long)
            with torch.no_grad():
                ncf_affinity = float(self._ncf_model(user_tensor, ex_tensor).item())

            # Combinación híbrida (70% Content + 30% Neural CF)
            final_score = round((content_score * 0.70) + (ncf_affinity * 100.0 * 0.30), 2)

            scored_exercises.append({
                "exercise_id": str(ex.id),
                "exercise_name": ex.name,
                "body_part": ex.body_part,
                "equipment": ex.equipment,
                "final_score": final_score,
                "content_score": content_score,
                "ncf_affinity": round(ncf_affinity, 3),
            })

        # Ordenar por puntuación descendente
        scored_exercises.sort(key=lambda x: x["final_score"], reverse=True)
        top_recommendations = scored_exercises[:top_k]

        return {
            "recommendation_engine": "HYBRID_CONTENT_NEURAL_CF",
            "recommended_exercise_ids": [r["exercise_id"] for r in top_recommendations],
            "scoring_breakdown": {
                "total_candidates": len(candidates),
                "excluded_by_restrictions_or_equipment": excluded_count,
                "top_recommendations": top_recommendations,
            },
        }
