"""Endpoints para generación de recomendaciones de ejercicios y rutinas (Stateless).

Permite al backend del ERP solicitar una propuesta de rutina y ranking de ejercicios
proporcionando únicamente los datos del perfil y objetivos del cliente en formato JSON.
"""

import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.schemas.recommendations import (
    RecommendationGenerateRequest,
    StatelessRecommendationResponse,
)
from app.infrastructure.cv.cv_adapter import MediaPipeCVEngine
from app.infrastructure.ml.hybrid_recommender import HybridRecommendationEngine
from app.infrastructure.repositories.in_memory_repositories import default_exercise_repo
from app.modules.stateless_pipeline.service import StatelessPipelineService

router = APIRouter()

_cv_engine_instance = MediaPipeCVEngine()
_rec_engine_instance = HybridRecommendationEngine()


def get_stateless_service() -> StatelessPipelineService:
    """Inyector de dependencias para StatelessPipelineService."""
    return StatelessPipelineService(
        cv_engine=_cv_engine_instance,
        rec_engine=_rec_engine_instance,
        exercise_repo=default_exercise_repo,
    )


@router.post(
    "/recommendations/generate",
    response_model=StatelessRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar recomendación de rutina semanal por IA (Stateless JSON)",
    description=(
        "Recibe el perfil del cliente, objetivos, nivel, disponibilidad, restricciones y equipamiento "
        "en un payload JSON estándar, procesa el algoritmo híbrido de recomendación (Random Forest + Red Neuronal) "
        "y retorna la estructura de la rutina semanal para que el backend del ERP la guarde en su base de datos."
    ),
)
async def generate_stateless_recommendations(
    request: RecommendationGenerateRequest,
    service: StatelessPipelineService = Depends(get_stateless_service),
) -> StatelessRecommendationResponse:
    """Genera la rutina y ranking de ejercicios en memoria."""
    client_uuid = request.client_id or uuid.uuid4()

    pipeline_result = await service.execute(
        client_id=client_uuid,
        age=request.age,
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        fitness_level=request.fitness_level,
        fitness_goal=request.fitness_goal,
        available_days_per_week=request.available_days_per_week,
        session_duration_minutes=request.session_duration_minutes,
        available_equipment=request.available_equipment,
        physical_restrictions=request.physical_restrictions + request.posture_findings,
    )

    return StatelessRecommendationResponse(
        client_id=pipeline_result.client_id,
        bmi=pipeline_result.bmi,
        bmi_category=pipeline_result.bmi_category,
        recommendation_engine=pipeline_result.recommendation_engine,
        recommended_exercises=pipeline_result.recommended_exercises[: request.top_k],
        workout_plan=pipeline_result.workout_plan,
        persisted_to_database=False,
    )
