"""Pruebas para el endpoint modular de recomendaciones de entrenamiento stateless."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_recommendations_generate_endpoint(async_client: AsyncClient) -> None:
    """Verifica que el endpoint genere rutinas en base a un payload JSON sin base de datos."""
    client_id = str(uuid.uuid4())
    payload = {
        "client_id": client_id,
        "age": 30,
        "weight_kg": 78.0,
        "height_cm": 180.0,
        "fitness_level": "INTERMEDIO",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": 4,
        "session_duration_minutes": 60,
        "available_equipment": ["dumbbells", "barbell"],
        "physical_restrictions": ["rodilla"],
        "posture_findings": ["ligera_asimetria_hombros"],
        "top_k": 8,
    }

    response = await async_client.post("/api/v1/recommendations/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["client_id"] == client_id
    assert data["bmi"] > 20.0
    assert data["persisted_to_database"] is False
    assert len(data["recommended_exercises"]) <= 8
    assert len(data["recommended_exercises"]) > 0
    assert data["workout_plan"]["status"] == "PENDIENTE_APROBACION"
    assert len(data["workout_plan"]["days"]) == 4


@pytest.mark.asyncio
async def test_recommendations_generate_validation_error(async_client: AsyncClient) -> None:
    """Verifica el rechazo con 422 ante días de entrenamiento inválidos."""
    payload = {
        "age": 30,
        "weight_kg": 78.0,
        "height_cm": 180.0,
        "fitness_level": "INTERMEDIO",
        "fitness_goal": "HIPERTROFIA",
        "available_days_per_week": 10,  # Máximo 7
        "session_duration_minutes": 60,
    }

    response = await async_client.post("/api/v1/recommendations/generate", json=payload)
    assert response.status_code == 422
