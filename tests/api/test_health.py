"""Pruebas para endpoints de health check y manejadores de excepciones."""

import pytest
from httpx import AsyncClient
from starlette.requests import Request

from app.core.exceptions import (
    EntityNotFoundError,
    GymAIError,
    ImageQualityLowError,
    InvalidFileTypeError,
    RoutineApprovalPendingError,
    VideoProcessingError,
)
from app.main import (
    approval_pending_handler,
    entity_not_found_handler,
    generic_gym_ai_handler,
    image_quality_handler,
    invalid_file_handler,
    video_processing_handler,
)


@pytest.mark.asyncio
async def test_health_live(async_client: AsyncClient) -> None:
    """Verifica que la sonda de liveness responda status 200."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_ready(async_client: AsyncClient) -> None:
    """Verifica que la sonda de readiness valide los modelos en memoria."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["persistence"] == "none_stateless"
    assert data["mode"] == "stateless_pure_inference"
    assert "models" in data


@pytest.mark.asyncio
async def test_exception_handlers() -> None:
    """Verifica el comportamiento de los manejadores de excepciones centralizados."""
    dummy_req = Request({"type": "http", "method": "GET", "path": "/"})

    res_404 = await entity_not_found_handler(dummy_req, EntityNotFoundError("Item", "123"))
    assert res_404.status_code == 404

    res_422_img = await image_quality_handler(dummy_req, ImageQualityLowError("Baja luz", 0.2))
    assert res_422_img.status_code == 422

    res_422_vid = await video_processing_handler(dummy_req, VideoProcessingError("Frame corrupto"))
    assert res_422_vid.status_code == 422

    res_403 = await approval_pending_handler(dummy_req, RoutineApprovalPendingError("p-1"))
    assert res_403.status_code == 403

    res_400_file = await invalid_file_handler(dummy_req, InvalidFileTypeError("test.exe", [".jpg"]))
    assert res_400_file.status_code == 400

    res_400_gen = await generic_gym_ai_handler(dummy_req, GymAIError("Error general"))
    assert res_400_gen.status_code == 400


@pytest.mark.asyncio
async def test_app_lifespan() -> None:
    """Verifica el ciclo de vida del lifespan de FastAPI."""
    from app.main import app, lifespan

    async with lifespan(app):
        pass

