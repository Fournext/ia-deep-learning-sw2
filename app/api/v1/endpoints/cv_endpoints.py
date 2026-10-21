"""Endpoints modulares de Visión por Computadora (Computer Vision) Stateless.

Permite al backend del ERP enviar fotografías o videos de forma independiente
para obtener métricas articulares, simetría y conteo biomecánico sin persistencia.
"""

import os
import tempfile
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.v1.schemas.stateless_analysis import PostureAnalysisItem, VideoAnalysisItem
from app.core.exceptions import ImageQualityLowError
from app.domain.entities.analysis_results import ExerciseVideoType, ImageViewType
from app.infrastructure.cv.cv_adapter import MediaPipeCVEngine

router = APIRouter()
_cv_engine = MediaPipeCVEngine()


@router.post(
    "/cv/analyze-posture",
    response_model=list[PostureAnalysisItem],
    status_code=status.HTTP_200_OK,
    summary="Análisis postural modular de fotografías (MediaPipe Pose)",
    description=(
        "Recibe hasta 3 fotografías (frontal, lateral, posterior), extrae landmarks articulares "
        "con MediaPipe, calcula pendientes biacromiales, inclinación de crestas ilíacas y simetría, "
        "retornando las métricas inmediatamente sin almacenar archivos en disco ni BD."
    ),
)
async def analyze_posture_photos(
    photo_frontal: UploadFile | None = File(None, description="Fotografía plano frontal"),
    photo_lateral: UploadFile | None = File(None, description="Fotografía plano lateral"),
    photo_posterior: UploadFile | None = File(None, description="Fotografía plano posterior"),
) -> list[PostureAnalysisItem]:
    """Analiza las imágenes proporcionadas y retorna las métricas posturales."""
    results: list[PostureAnalysisItem] = []

    photos: list[tuple[ImageViewType, UploadFile | None]] = [
        (ImageViewType.FRONTAL, photo_frontal),
        (ImageViewType.LATERAL, photo_lateral),
        (ImageViewType.POSTERIOR, photo_posterior),
    ]

    for view_type, upload in photos:
        if upload is None:
            continue
        p_bytes = await upload.read()
        if not p_bytes:
            continue

        try:
            cv_res: dict[str, Any] = _cv_engine.analyze_posture_image(p_bytes, view_type)
            metrics: dict[str, Any] = cv_res.get("posture_metrics", {})
            raw_obs: list[Any] = metrics.get("observations", [])
            observations: list[str] = [str(o) for o in raw_obs]
            angles_raw: dict[str, Any] = cv_res.get("calculated_angles", {})
            calculated_angles: dict[str, float] = {
                str(k): round(float(v), 2) for k, v in angles_raw.items()
            }

            results.append(
                PostureAnalysisItem(
                    view_type=view_type.value,
                    confidence_score=round(float(cv_res.get("confidence_score", 0.0)), 3),
                    has_quality_issues=bool(cv_res.get("has_quality_issues", False)),
                    calculated_angles=calculated_angles,
                    observations=observations,
                    shoulder_slope_degrees=round(float(metrics.get("shoulder_slope_degrees", 0.0)), 2),
                    hip_slope_degrees=round(float(metrics.get("hip_slope_degrees", 0.0)), 2),
                )
            )
        except ImageQualityLowError as e:
            results.append(
                PostureAnalysisItem(
                    view_type=view_type.value,
                    confidence_score=e.confidence,
                    has_quality_issues=True,
                    calculated_angles={},
                    observations=[f"Calidad deficiente: {e.reason}"],
                    shoulder_slope_degrees=0.0,
                    hip_slope_degrees=0.0,
                )
            )

    return results


@router.post(
    "/cv/analyze-movement",
    response_model=VideoAnalysisItem,
    status_code=status.HTTP_200_OK,
    summary="Análisis biomecánico y conteo de repeticiones en video",
    description=(
        "Procesa un video de sentadilla o flexiones (push-ups), rastrea la trayectoria articular "
        "en cada fotograma, cuenta repeticiones completadas y detecta errores de profundidad o postura."
    ),
)
async def analyze_movement_video(
    video: UploadFile = File(..., description="Archivo de video (MP4, MOV, AVI)"),
    exercise_type: ExerciseVideoType = Form(..., description="Tipo de ejercicio: SQUAT o PUSHUP"),
) -> VideoAnalysisItem:
    """Procesa el video y retorna el reporte biomecánico."""
    vid_bytes = await video.read()

    # Procesamiento en archivo temporal efímero con eliminación garantizada
    suffix = ".mp4" if (video.filename and video.filename.endswith(".mp4")) else ".avi"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_vid:
        tmp_vid.write(vid_bytes)
        tmp_path = tmp_vid.name

    try:
        video_res: dict[str, Any] = _cv_engine.analyze_exercise_video(tmp_path, exercise_type)
        raw_errors: list[Any] = video_res.get("execution_errors", [])
        execution_errors: list[str] = [str(err) for err in raw_errors]

        return VideoAnalysisItem(
            exercise_type=exercise_type.value,
            completed_reps=int(video_res.get("completed_reps", 0)),
            average_depth_angle=round(float(video_res.get("average_depth_angle", 0.0)), 2),
            execution_score=round(float(video_res.get("execution_score", 0.0)), 3),
            execution_errors=execution_errors,
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
