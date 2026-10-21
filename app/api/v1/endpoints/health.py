"""Endpoints de comprobación de salud (Health Checks)."""

from typing import Any

from fastapi import APIRouter, status

from app.infrastructure.repositories.in_memory_repositories import default_exercise_repo

router = APIRouter()


@router.get("/health/live", status_code=status.HTTP_200_OK, summary="Liveness Probe")
async def liveness_probe() -> dict[str, str]:
    """Comprueba que el proceso de la API está en ejecución."""
    return {"status": "ok", "service": "gym-ai-microservice", "mode": "stateless"}


@router.get("/health/ready", status_code=status.HTTP_200_OK, summary="Readiness Probe")
async def readiness_probe() -> dict[str, Any]:
    """Valida la preparación de los motores de IA y catálogo en memoria."""
    exercises = await default_exercise_repo.list_all()
    ex_count = len(exercises)
    ready = ex_count > 0

    return {
        "status": "ready" if ready else "not_ready",
        "persistence": "none_stateless",
        "mode": "stateless_pure_inference",
        "exercise_catalog_count": ex_count,
        "models": {
            "mediapipe_pose": "loaded",
            "neural_collaborative_filtering": "loaded",
        },
    }
