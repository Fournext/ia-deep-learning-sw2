# Contratos e Interfaces entre Módulos

Este documento define formalmente los contratos de datos (Data Transfer Objects y Protocolos) entre los diferentes subsistemas. Todos los agentes deben implementar sus componentes adhiriéndose a estos esquemas.

---

## 1. Contrato del Módulo de Visión por Computadora (CV Pipeline)

### Entrada: `PoseAnalysisInput`
```python
from pydantic import BaseModel, Field

class PoseAnalysisInput(BaseModel):
    media_path: str = Field(..., description="Ruta local segura del archivo temporal de imagen o video")
    media_type: str = Field(..., description="'IMAGE' o 'VIDEO'")
    client_id: str = Field(..., description="UUID del cliente analizado")
    exercise_hint: str | None = Field(None, description="Pista del ejercicio evaluado (ej. 'squat', 'deadlift', 'posture_static')")
```

### Salida: `BiomechanicalAnalysisResult`
```python
from pydantic import BaseModel, Field

class JointAngle(BaseModel):
    joint_name: str = Field(..., description="Nombre de la articulación (ej. 'left_knee', 'right_hip', 'trunk_inclination')")
    min_angle: float = Field(..., description="Ángulo mínimo observado en grados")
    max_angle: float = Field(..., description="Ángulo máximo observado en grados")
    avg_angle: float = Field(..., description="Ángulo promedio en grados")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza de detección")

class BiomechanicalAnalysisResult(BaseModel):
    analysis_id: str
    client_id: str
    is_valid_detection: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    joint_angles: list[JointAngle]
    postural_observations: list[str] = Field(default_factory=list, description="Observaciones geométricas descriptivas")
    movement_classification: str | None = Field(None, description="Etiqueta clasificada (ej. 'squat_depth_adequate', 'knee_valgus_observed')")
    low_confidence_warning: bool = False
    error_message: str | None = None
```

---

## 2. Contrato del Motor de Recomendación (Recommendation Engine)

### Entrada: `RecommendationRequest`
```python
from pydantic import BaseModel, Field

class ClientProfile(BaseModel):
    client_id: str
    fitness_goal: str = Field(..., description="'HYPERTROPHY', 'STRENGTH', 'WEIGHT_LOSS', 'ENDURANCE', 'REHAB'")
    experience_level: str = Field(..., description="'BEGINNER', 'INTERMEDIATE', 'ADVANCED'")
    days_per_week: int = Field(..., ge=1, le=7)
    available_equipment: list[str] = Field(..., description="Lista de equipos disponibles (ej. ['BARBELL', 'DUMBBELL', 'CABLES'])")
    health_restrictions: list[str] = Field(default_factory=list, description="Limitaciones médicas o articulares reportadas")

class RecommendationRequest(BaseModel):
    client_profile: ClientProfile
    biomechanical_data: BiomechanicalAnalysisResult | None = None
    historical_feedback: list[dict] = Field(default_factory=list)
```

### Salida: `RoutineProposal`
```python
from pydantic import BaseModel, Field
from datetime import datetime

class ExerciseItem(BaseModel):
    exercise_id: str
    exercise_name: str
    target_muscle_group: str
    movement_pattern: str
    recommended_sets: int
    recommended_reps: str
    rest_seconds: int
    contraindication_flags: list[str] = Field(default_factory=list)
    relevance_score: float

class RoutineProposal(BaseModel):
    routine_id: str
    client_id: str
    created_at: datetime
    status: str = Field(default="PENDING_TRAINER_APPROVAL", description="Estado obligatorio: PENDING_TRAINER_APPROVAL, APPROVED, REJECTED")
    trainer_id: str | None = None
    exercises: list[ExerciseItem]
    justification_summary: str
    is_cold_start: bool
```

---

## 3. Protocolo de Persistencia (Repository Interfaces)

```python
from typing import Protocol

class AnalysisRepositoryProtocol(Protocol):
    async def save_analysis(self, result: BiomechanicalAnalysisResult) -> str:
        ...
    async def get_by_client_id(self, client_id: str) -> list[BiomechanicalAnalysisResult]:
        ...

class RoutineRepositoryProtocol(Protocol):
    async def save_proposal(self, proposal: RoutineProposal) -> str:
        ...
    async def approve_routine(self, routine_id: str, trainer_id: str, notes: str | None) -> bool:
        ...
```
