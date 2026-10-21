"""Pruebas para el endpoint de análisis corporal y recomendación stateless (sin guardar en BD)."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stateless_analysis_profile_only(async_client: AsyncClient) -> None:
    """Valida la ejecución del pipeline con datos de perfil sin fotos ni base de datos."""
    client_id = str(uuid.uuid4())
    form_data = {
        "client_id": client_id,
        "age": "28",
        "weight_kg": "75.0",
        "height_cm": "178.0",
        "fitness_level": "INTERMEDIO",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": "4",
        "session_duration_minutes": "60",
        "available_equipment": '["dumbbells", "machine"]',
        "physical_restrictions": '["hombro"]',
    }

    response = await async_client.post(
        "/api/v1/evaluations/analyze-and-recommend",
        data=form_data,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["client_id"] == client_id
    assert data["bmi"] > 20.0
    assert data["bmi_category"] in ["Normopeso", "Sobrepeso"]
    assert data["fitness_level"] == "INTERMEDIO"
    assert data["fitness_goal"] == "HIPERTROFIA"
    assert data["persisted_to_database"] is False
    assert len(data["recommended_exercises"]) > 0
    assert data["workout_plan"]["status"] == "PENDIENTE_APROBACION"
    assert "hombro" in data["workout_plan"]["justification"]
    assert len(data["workout_plan"]["days"]) == 4


@pytest.mark.asyncio
async def test_stateless_analysis_with_photo(
    async_client: AsyncClient, sample_image_bytes: bytes
) -> None:
    """Valida que una fotografía cargada sea analizada en memoria y reflejada en la recomendación."""
    client_id = str(uuid.uuid4())
    form_data = {
        "client_id": client_id,
        "age": "32",
        "weight_kg": "80.0",
        "height_cm": "175.0",
        "fitness_level": "PRINCIPIANTE",
        "fitness_goal": "PERDIDA_GRASA",
        "available_days_per_week": "3",
        "session_duration_minutes": "45",
        "available_equipment": '["dumbbells"]',
        "physical_restrictions": "[]",
    }
    files = {
        "photo_frontal": ("front.jpg", sample_image_bytes, "image/jpeg"),
    }

    response = await async_client.post(
        "/api/v1/evaluations/analyze-and-recommend",
        data=form_data,
        files=files,
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["photo_analyses"]) == 1
    photo = data["photo_analyses"][0]
    assert photo["view_type"] == "FRONTAL"
    assert "confidence_score" in photo
    assert data["persisted_to_database"] is False
    assert len(data["workout_plan"]["days"]) == 3


@pytest.mark.asyncio
async def test_stateless_analysis_invalid_inputs(async_client: AsyncClient) -> None:
    """Valida que valores fuera de rango anatómico sean rechazados con HTTP 422."""
    form_data = {
        "age": "5",  # Menor a 14 años
        "weight_kg": "70.0",
        "height_cm": "175.0",
        "fitness_level": "PRINCIPIANTE",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": "3",
        "session_duration_minutes": "60",
    }
    response = await async_client.post(
        "/api/v1/evaluations/analyze-and-recommend",
        data=form_data,
    )
    assert response.status_code == 422
