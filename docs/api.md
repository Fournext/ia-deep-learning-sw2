# Documentación de la API REST — Endpoints Stateless y Guía de Integración

El microservicio expone una API REST bajo el prefijo `/api/v1` documentada automáticamente con especificación OpenAPI 3.0 (disponible en `/docs`).

> [!IMPORTANT]
> **Modo Operativo: 100% Stateless (Sin Base de Datos)**
> El microservicio opera como un motor puro de inferencia y cómputo analítico en memoria. No persiste entidades, evaluaciones ni imágenes. El **backend principal del ERP** recibe las respuestas JSON y es el único encargado de almacenarlas en su propia base de datos.

---

## 1. Resumen de Endpoints Disponibles

| Método | Endpoint | Tipo | Descripción |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/pipeline/analyze-and-recommend` | **Integral** | Pipeline completo: Recibe perfil, restricciones y fotos/video. Retorna métricas posturales + rutina semanal en una sola llamada. |
| `POST` | `/api/v1/cv/analyze-posture` | **Modular CV** | Recibe de 1 a 3 fotografías (frontal, lateral, posterior). Retorna landmarks, ángulos y simetrías articulares. |
| `POST` | `/api/v1/cv/analyze-movement` | **Modular CV** | Recibe video de sentadilla o flexiones. Retorna conteo de repeticiones, cadencia y advertencias de técnica. |
| `POST` | `/api/v1/recommendations/generate` | **Modular ML** | Recibe perfil del cliente y restricciones en JSON. Retorna ranking de ejercicios y estructura semanal de la rutina. |
| `GET` | `/health/live` | **Sonda** | Comprueba que el proceso de la API está en ejecución. |
| `GET` | `/health/ready` | **Sonda** | Valida que los modelos de IA y catálogo en memoria estén cargados y listos. |

---

## 2. Especificación Detallada de Endpoints

### 2.1 Pipeline Integral: Análisis Corporal y Recomendación
`POST /api/v1/pipeline/analyze-and-recommend`  
*(Alias compatible: `POST /api/v1/evaluations/analyze-and-recommend`)*

**Entrada:** `multipart/form-data`
- `client_id` (UUID, opcional): Identificador del cliente en el ERP.
- `age` (int): Edad (14 - 90).
- `weight_kg` (float): Peso corporal (30.0 - 300.0).
- `height_cm` (float): Estatura en cm (100.0 - 250.0).
- `fitness_level` (string): `PRINCIPIANTE`, `INTERMEDIO`, `AVANZADO`.
- `fitness_goal` (string): `PERDIDA_GRASA`, `HIPERTROFIA`, `FUERZA`, `RESISTENCIA`, `SALUD_GENERAL`.
- `available_days_per_week` (int): Días disponibles (1 - 7).
- `session_duration_minutes` (int): Duración en minutos (15 - 180).
- `available_equipment` (string JSON): Ej. `["dumbbells", "barbell", "machine"]`.
- `physical_restrictions` (string JSON): Ej. `["hombro", "lumbar"]`.
- `photo_frontal` (File, opcional): Imagen frontal (JPEG/PNG).
- `photo_lateral` (File, opcional): Imagen lateral (JPEG/PNG).
- `photo_posterior` (File, opcional): Imagen posterior (JPEG/PNG).
- `video_exercise` (File, opcional): Video de ejercicio (MP4/AVI).
- `video_exercise_type` (string, opcional): `SQUAT` o `PUSHUP`.

**Respuesta Exitosa (200 OK):**
```json
{
  "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "bmi": 23.83,
  "bmi_category": "Normopeso",
  "fitness_level": "INTERMEDIO",
  "fitness_goal": "HIPERTROFIA",
  "posture_findings": [
    "Hombro derecho 1.5° más elevado que el izquierdo (asimetría leve)."
  ],
  "photo_analyses": [
    {
      "view_type": "FRONTAL",
      "confidence_score": 0.94,
      "has_quality_issues": false,
      "calculated_angles": { "elbow_left": 165.2, "knee_left": 178.5 },
      "observations": ["Hombro derecho elevado."],
      "shoulder_slope_degrees": 1.5,
      "hip_slope_degrees": 0.4
    }
  ],
  "video_analysis": null,
  "recommendation_engine": "Hybrid (Content-Based + PyTorch NCF)",
  "recommended_exercises": [
    {
      "exercise_id": "c1f72b9a-4e2a-5b9e-9d21-f1234567890a",
      "exercise_name": "Press de Banca con Mancuernas",
      "body_part": "Pecho",
      "muscle_type": "Pectoral Mayor",
      "equipment": "dumbbells",
      "difficulty": "intermediate",
      "score": 0.92
    }
  ],
  "workout_plan": {
    "program_name": "Rutina Hipertrofia 4 Días - Personalizada",
    "status": "PENDIENTE_APROBACION",
    "trainer_review_notice": "Propuesta preliminar generada por IA. No entra en vigor para el cliente hasta ser revisada, ajustada y aprobada formalmente por un entrenador del ERP.",
    "justification": "Plan enfocado en hipertrofia respetando disponibilidad de 4 días y excluyendo sobrecarga articular en hombro.",
    "days": [
      {
        "day_number": 1,
        "day_label": "Día 1: Torso / Empuje",
        "exercises": [
          {
            "exercise_id": "c1f72b9a-4e2a-5b9e-9d21-f1234567890a",
            "exercise_name": "Press de Banca con Mancuernas",
            "sets": 4,
            "reps": "8-12",
            "rest_seconds": 90,
            "target_rpe": 8
          }
        ]
      }
    ]
  },
  "persisted_to_database": false
}
```

---

### 2.2 Análisis Postural Modular (Fotografías)
`POST /api/v1/cv/analyze-posture`

**Entrada:** `multipart/form-data` con hasta 3 imágenes: `photo_frontal`, `photo_lateral`, `photo_posterior`.  
**Salida (200 OK):** Lista de `PostureAnalysisItem` con ángulos articulares, pendientes e inclinaciones.

---

### 2.3 Análisis de Movimiento Modular (Video)
`POST /api/v1/cv/analyze-movement`

**Entrada:** `multipart/form-data`
- `video`: Archivo de video.
- `exercise_type`: `SQUAT` o `PUSHUP`.

**Salida (200 OK):**
```json
{
  "exercise_type": "SQUAT",
  "completed_reps": 8,
  "average_depth_angle": 88.5,
  "execution_score": 85.0,
  "execution_errors": [
    "Repetición 3: Profundidad insuficiente (105° > 100°)"
  ]
}
```

---

### 2.4 Generación Modular de Recomendaciones
`POST /api/v1/recommendations/generate`

**Entrada:** `application/json`
```json
{
  "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "age": 28,
  "weight_kg": 75.5,
  "height_cm": 178.0,
  "fitness_level": "INTERMEDIO",
  "fitness_goal": "HIPERTROFIA",
  "available_days_per_week": 4,
  "session_duration_minutes": 60,
  "available_equipment": ["dumbbells", "barbell", "machine"],
  "physical_restrictions": ["hombro"],
  "posture_findings": ["asimetria_leve"],
  "top_k": 10
}
```

**Salida (200 OK):** `StatelessRecommendationResponse` con los ejercicios ordenados por puntaje y la estructura diaria de la rutina semanal.
