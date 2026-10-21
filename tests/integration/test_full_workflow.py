"""Prueba de integración end-to-end del microservicio de IA en modo Stateless (Sin Base de Datos)."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_stateless_integration_workflow(
    async_client: AsyncClient, sample_image_bytes: bytes, sample_video_path: str
) -> None:
    """Ejecuta el flujo completo de integración para consumo por el backend del ERP.

    1. Comprobación de salud y preparación del microservicio.
    2. Análisis modular de postura fotográfica (MediaPipe).
    3. Análisis modular de técnica y conteo en video (MediaPipe + Biomecánica).
    4. Generación modular de recomendaciones de entrenamiento (IA Híbrida).
    5. Invocación al pipeline integral unificado (análisis corporal + recomendación directa).
    """
    # Paso 1: Health y Readiness
    health_resp = await async_client.get("/health/ready")
    assert health_resp.status_code == 200
    assert health_resp.json()["persistence"] == "none_stateless"

    # Paso 2: Análisis modular de fotografía postural
    files_img = {"photo_frontal": ("front.jpg", sample_image_bytes, "image/jpeg")}
    img_resp = await async_client.post("/api/v1/cv/analyze-posture", files=files_img)
    assert img_resp.status_code == 200
    img_data = img_resp.json()
    assert isinstance(img_data, list)
    assert len(img_data) == 1
    assert img_data[0]["view_type"] == "FRONTAL"

    # Paso 3: Análisis modular de video
    with open(sample_video_path, "rb") as vf:
        video_bytes = vf.read()

    files_vid = {"video": ("squat.avi", video_bytes, "video/avi")}
    vid_data = {"exercise_type": "SQUAT"}
    vid_resp = await async_client.post(
        "/api/v1/cv/analyze-movement", files=files_vid, data=vid_data
    )
    assert vid_resp.status_code in (200, 422)

    # Paso 4: Generación modular de recomendaciones (JSON puro)
    client_id = str(uuid.uuid4())
    rec_payload = {
        "client_id": client_id,
        "age": 29,
        "weight_kg": 76.0,
        "height_cm": 178.0,
        "fitness_level": "INTERMEDIO",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": 4,
        "session_duration_minutes": 60,
        "available_equipment": ["dumbbells", "barbell"],
        "physical_restrictions": ["hombro"],
        "posture_findings": ["asimetria_leve"],
        "top_k": 8,
    }
    rec_resp = await async_client.post("/api/v1/recommendations/generate", json=rec_payload)
    assert rec_resp.status_code == 200
    rec_result = rec_resp.json()
    assert rec_result["client_id"] == client_id
    assert len(rec_result["recommended_exercises"]) > 0
    assert rec_result["workout_plan"]["status"] == "PENDIENTE_APROBACION"
    assert len(rec_result["workout_plan"]["days"]) == 4

    # Paso 5: Invocación al pipeline integral unificado
    form_data = {
        "client_id": client_id,
        "age": "29",
        "weight_kg": "76.0",
        "height_cm": "178.0",
        "fitness_level": "INTERMEDIO",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": "4",
        "session_duration_minutes": "60",
        "available_equipment": '["dumbbells", "barbell"]',
        "physical_restrictions": '["hombro"]',
    }
    pipeline_files = {
        "photo_frontal": ("front.jpg", sample_image_bytes, "image/jpeg"),
    }
    pipeline_resp = await async_client.post(
        "/api/v1/pipeline/analyze-and-recommend",
        data=form_data,
        files=pipeline_files,
    )
    assert pipeline_resp.status_code == 200
    pipeline_result = pipeline_resp.json()
    assert pipeline_result["client_id"] == client_id
    assert pipeline_result["persisted_to_database"] is False
    assert len(pipeline_result["photo_analyses"]) == 1
    assert len(pipeline_result["recommended_exercises"]) > 0
    assert len(pipeline_result["workout_plan"]["days"]) == 4
