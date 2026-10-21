"""Endpoint unificado de análisis corporal y recomendación stateless (sin guardar en BD)."""

import json
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.v1.schemas.stateless_analysis import StatelessAnalysisResponse
from app.domain.entities.analysis_results import ExerciseVideoType
from app.domain.entities.evaluation import FitnessGoal, FitnessLevel
from app.infrastructure.cv.cv_adapter import MediaPipeCVEngine
from app.infrastructure.ml.hybrid_recommender import HybridRecommendationEngine
from app.infrastructure.repositories.in_memory_repositories import default_exercise_repo
from app.modules.stateless_pipeline.service import StatelessPipelineService

router = APIRouter()

_cv_engine = MediaPipeCVEngine()
_rec_engine = HybridRecommendationEngine()


def get_stateless_service() -> StatelessPipelineService:
    """Inyector de dependencias para el servicio stateless."""
    return StatelessPipelineService(
        cv_engine=_cv_engine,
        rec_engine=_rec_engine,
        exercise_repo=default_exercise_repo,
    )


@router.post(
    "/pipeline/analyze-and-recommend",
    response_model=StatelessAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Análisis corporal completo y recomendación sin persistencia en BD (Stateless)",
    description=(
        "Recibe el perfil físico, restricciones, fotografías (frontal, lateral, posterior) "
        "y/o video del cliente, ejecuta el pipeline completo de visión y recomendación con IA "
        "y devuelve el resultado directamente. No guarda nada en base de datos ni retiene archivos en disco."
    ),
)
@router.post(
    "/evaluations/analyze-and-recommend",
    response_model=StatelessAnalysisResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=True,
    summary="Alias de compatibilidad: Análisis corporal y recomendación",
)
@router.post(
    "/analyze-and-recommend",
    response_model=StatelessAnalysisResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def analyze_and_recommend(
    client_id: uuid.UUID | None = Form(None, description="ID del cliente en el ERP (opcional)"),
    age: int = Form(..., ge=14, le=90, description="Edad del cliente"),
    weight_kg: float = Form(..., ge=30.0, le=300.0, description="Peso corporal en kg"),
    height_cm: float = Form(..., ge=100.0, le=250.0, description="Estatura en centímetros"),
    fitness_level: FitnessLevel = Form(..., description="Nivel de condición física"),
    fitness_goal: FitnessGoal = Form(..., description="Objetivo principal"),
    available_days_per_week: int = Form(..., ge=1, le=7, description="Días disponibles para entrenar"),
    session_duration_minutes: int = Form(..., ge=15, le=180, description="Minutos disponibles por sesión"),
    available_equipment: str = Form(
        "[]", description="Lista JSON de equipamiento (ej. ['dumbbells', 'machine'])"
    ),
    physical_restrictions: str = Form(
        "[]", description="Lista JSON de lesiones o restricciones (ej. ['rodilla', 'hombro'])"
    ),
    photo_frontal: UploadFile | None = File(None, description="Fotografía vista frontal"),
    photo_lateral: UploadFile | None = File(None, description="Fotografía vista lateral"),
    photo_posterior: UploadFile | None = File(None, description="Fotografía vista posterior"),
    video_exercise: UploadFile | None = File(None, description="Video de sentadilla o flexiones"),
    video_exercise_type: ExerciseVideoType | None = Form(None, description="Tipo de ejercicio del video"),
    service: StatelessPipelineService = Depends(get_stateless_service),
) -> StatelessAnalysisResponse:
    """Ejecuta el pipeline stateless en memoria."""
    # Parsear listas JSON
    equipment_list: list[str] = []
    if available_equipment:
        try:
            parsed = json.loads(available_equipment)
            if isinstance(parsed, list):
                equipment_list = [str(x) for x in parsed]
        except json.JSONDecodeError:
            equipment_list = [x.strip() for x in available_equipment.split(",") if x.strip()]

    restrictions_list: list[str] = []
    if physical_restrictions:
        try:
            parsed = json.loads(physical_restrictions)
            if isinstance(parsed, list):
                restrictions_list = [str(x) for x in parsed]
        except json.JSONDecodeError:
            restrictions_list = [x.strip() for x in physical_restrictions.split(",") if x.strip()]

    # Leer bytes de imágenes si se adjuntaron
    frontal_bytes = await photo_frontal.read() if photo_frontal else None
    lateral_bytes = await photo_lateral.read() if photo_lateral else None
    posterior_bytes = await photo_posterior.read() if photo_posterior else None
    vid_bytes = await video_exercise.read() if video_exercise else None

    effective_client_id = client_id or uuid.uuid4()

    return await service.execute(
        client_id=effective_client_id,
        age=age,
        weight_kg=weight_kg,
        height_cm=height_cm,
        fitness_level=fitness_level,
        fitness_goal=fitness_goal,
        available_days_per_week=available_days_per_week,
        session_duration_minutes=session_duration_minutes,
        available_equipment=equipment_list,
        physical_restrictions=restrictions_list,
        photo_frontal_bytes=frontal_bytes,
        photo_lateral_bytes=lateral_bytes,
        photo_posterior_bytes=posterior_bytes,
        video_bytes=vid_bytes,
        video_exercise_type=video_exercise_type,
    )
