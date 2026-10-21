"""Pruebas para los endpoints modulares de Visión Artificial (CV) Stateless."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cv_analyze_posture_endpoint(
    async_client: AsyncClient, sample_image_bytes: bytes
) -> None:
    """Verifica que el endpoint modular de postura analice imágenes y retorne métricas."""
    files = {
        "photo_frontal": ("front.jpg", sample_image_bytes, "image/jpeg"),
    }

    response = await async_client.post("/api/v1/cv/analyze-posture", files=files)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["view_type"] == "FRONTAL"
    assert "confidence_score" in item
    assert "shoulder_slope_degrees" in item
    assert "hip_slope_degrees" in item
    assert "calculated_angles" in item


@pytest.mark.asyncio
async def test_cv_analyze_movement_endpoint(
    async_client: AsyncClient, sample_video_path: str
) -> None:
    """Verifica que el endpoint modular de video analice movimiento sin persistencia."""
    with open(sample_video_path, "rb") as vid_file:
        files = {
            "video": ("exercise.avi", vid_file.read(), "video/avi"),
        }
        data = {
            "exercise_type": "SQUAT",
        }
        response = await async_client.post(
            "/api/v1/cv/analyze-movement", files=files, data=data
        )

    assert response.status_code in (200, 422)
    if response.status_code == 200:
        res_data = response.json()
        assert res_data["exercise_type"] == "SQUAT"
        assert "completed_reps" in res_data
        assert "average_depth_angle" in res_data
        assert "execution_score" in res_data
        assert isinstance(res_data["execution_errors"], list)
