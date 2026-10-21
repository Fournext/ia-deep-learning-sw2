"""Configuración global de fixtures y utilidades de prueba para Pytest (Modo Stateless)."""

from collections.abc import AsyncGenerator
from typing import Any

import cv2
import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP asíncrono configurado para invocar la API en memoria."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Genera una imagen sintética en memoria codificada como JPEG."""
    img = np.full((480, 640, 3), 200, dtype=np.uint8)
    # Dibujar figura humana esquemática
    cv2.circle(img, (320, 100), 30, (50, 50, 50), -1)  # Cabeza
    cv2.line(img, (320, 130), (320, 300), (50, 50, 50), 10)  # Tronco
    cv2.line(img, (320, 160), (220, 220), (50, 50, 50), 8)  # Brazo izq
    cv2.line(img, (320, 160), (420, 220), (50, 50, 50), 8)  # Brazo der
    cv2.line(img, (320, 300), (260, 440), (50, 50, 50), 8)  # Pierna izq
    cv2.line(img, (320, 300), (380, 440), (50, 50, 50), 8)  # Pierna der
    _, encoded = cv2.imencode(".jpg", img)
    return encoded.tobytes()


@pytest.fixture
def sample_video_path(tmp_path: Any) -> str:
    """Crea un archivo de video AVI sintético de 25 fotogramas para pruebas."""
    video_file = str(tmp_path / "test_exercise.avi")
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(video_file, fourcc, 10.0, (320, 240))
    for i in range(25):
        frame = np.full((240, 320, 3), 220, dtype=np.uint8)
        # Movimiento oscilatorio de flexión
        y_knee = int(140 + 30 * np.sin(i / 3.0))
        cv2.circle(frame, (160, 50), 15, (50, 50, 50), -1)
        cv2.line(frame, (160, 65), (160, 130), (50, 50, 50), 5)
        cv2.line(frame, (160, 130), (140, y_knee), (50, 50, 50), 5)
        cv2.line(frame, (140, y_knee), (140, 210), (50, 50, 50), 5)
        out.write(frame)
    out.release()
    return video_file
