"""Enrutador principal de la API REST v1 (Modo Stateless)."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    cv_endpoints,
    recommendations,
    stateless_analysis,
)

api_router = APIRouter()

# 1. Pipeline unificado de inferencia integral
api_router.include_router(stateless_analysis.router, tags=["Pipeline Integral (Stateless)"])

# 2. Endpoints modulares de visión por computadora
api_router.include_router(cv_endpoints.router, tags=["Visión Artificial (MediaPipe & Biomecánica)"])

# 3. Endpoint modular de recomendación de rutinas
api_router.include_router(recommendations.router, tags=["Recomendaciones de Entrenamiento"])
