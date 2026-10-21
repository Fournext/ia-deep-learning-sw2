"""Punto de entrada principal de la aplicación FastAPI del Microservicio de IA (Modo Stateless)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api_router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.core.config import settings
from app.core.exceptions import (
    EntityNotFoundError,
    GymAIError,
    ImageQualityLowError,
    InvalidFileTypeError,
    RoutineApprovalPendingError,
    VideoProcessingError,
)
from app.core.logging import logger, setup_logging
from app.infrastructure.repositories.in_memory_repositories import default_exercise_repo


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación en modo Stateless (Sin persistencia en BD)."""
    setup_logging()
    logger.info("Iniciando %s v%s en MODO STATELESS...", settings.PROJECT_NAME, settings.VERSION)

    # Cargar y verificar catálogo canónico en memoria
    exercises = await default_exercise_repo.list_all()
    logger.info("Catálogo canónico en memoria: %d ejercicios cargados.", len(exercises))

    yield

    logger.info("Cerrando recursos del microservicio...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Microservicio de Inteligencia Artificial para ERP de Gimnasio (Modo Stateless). "
        "Proporciona análisis postural por visión artificial con MediaPipe, "
        "conteo biomecánico de repeticiones y recomendación personalizada "
        "de rutinas con flujo de aprobación humana (Human-in-the-Loop). "
        "Opera 100% en memoria sin persistir datos en base de datos ni retener archivos en disco."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuración de CORS restrictiva
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Enrutadores
app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_STR)


# Manejadores de Excepciones de Dominio Centralizados
@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    """Mapea entidad no encontrada a HTTP 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "error_type": "EntityNotFoundError"},
    )


@app.exception_handler(ImageQualityLowError)
async def image_quality_handler(request: Request, exc: ImageQualityLowError) -> JSONResponse:
    """Mapea calidad de imagen deficiente a HTTP 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "reason": exc.reason,
            "confidence": exc.confidence,
            "error_type": "ImageQualityLowError",
        },
    )


@app.exception_handler(VideoProcessingError)
async def video_processing_handler(request: Request, exc: VideoProcessingError) -> JSONResponse:
    """Mapea fallo de video a HTTP 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message, "error_type": "VideoProcessingError"},
    )


@app.exception_handler(RoutineApprovalPendingError)
async def approval_pending_handler(request: Request, exc: RoutineApprovalPendingError) -> JSONResponse:
    """Mapea intento de usar rutina no aprobada a HTTP 403 Forbidden."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message, "error_type": "RoutineApprovalPendingError"},
    )


@app.exception_handler(InvalidFileTypeError)
async def invalid_file_handler(request: Request, exc: InvalidFileTypeError) -> JSONResponse:
    """Mapea archivo inválido a HTTP 400 Bad Request."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "error_type": "InvalidFileTypeError"},
    )


@app.exception_handler(GymAIError)
async def generic_gym_ai_handler(request: Request, exc: GymAIError) -> JSONResponse:
    """Mapea error genérico de dominio a HTTP 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "error_type": "GymAIError"},
    )
