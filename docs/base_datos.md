# Documento de Datos, Entidades y Modo Stateless

> [!IMPORTANT]
> **Modo Operativo del Microservicio: Stateless (Cero Persistencia en BD - ADR-005)**  
> Conforme al requerimiento del ERP de Gimnasio, este microservicio opera como **motor puro de inferencia y cómputo biomecánico en memoria**. No persiste datos personales, biométricos ni rutinas en bases de datos externas ni retiene archivos en disco. El ERP es el único custodio y repositorio persistente de los datos de clientes.  
> Los esquemas relacionales descritos abajo corresponden a la estructura de dominio y a los repositorios desacoplados mediante DIP.

---

## 1. Diagrama Entidad-Relación (Mermaid)

```mermaid
erDiagram
    EVALUATIONS ||--o{ EVALUATION_IMAGES : contains
    EVALUATIONS ||--o{ EVALUATION_VIDEOS : contains
    EVALUATIONS ||--o{ RECOMMENDATIONS : produces
    RECOMMENDATIONS ||--o{ WORKOUT_PLANS : generates
    WORKOUT_PLANS ||--o{ WORKOUT_PLAN_DAYS : defines
    WORKOUT_PLAN_DAYS ||--o{ WORKOUT_PLAN_EXERCISES : schedules
    EXERCISES ||--o{ WORKOUT_PLAN_EXERCISES : referenced_by
    WORKOUT_PLANS ||--o{ WORKOUT_PROGRESS : tracks

    EVALUATIONS {
        uuid id PK
        uuid client_id "FK del cliente en ERP"
        integer age
        float weight_kg
        float height_cm
        string fitness_level
        string fitness_goal
        integer available_days_per_week
        integer session_duration_minutes
        jsonb available_equipment
        jsonb physical_restrictions
        string status
        timestamp created_at
        timestamp updated_at
    }

    EVALUATION_IMAGES {
        uuid id PK
        uuid evaluation_id FK
        string view_type "FRONTAL, LATERAL, POSTERIOR"
        string file_path
        jsonb detected_landmarks
        jsonb calculated_angles
        jsonb posture_metrics
        float confidence_score
        boolean has_quality_issues
        timestamp created_at
    }

    EVALUATION_VIDEOS {
        uuid id PK
        uuid evaluation_id FK
        string exercise_type "SQUAT, PUSHUP"
        string file_path
        integer completed_reps
        float average_depth_angle
        jsonb rep_details
        jsonb execution_errors
        float execution_score
        timestamp created_at
    }

    EXERCISES {
        uuid id PK
        string name
        string target_muscle
        string body_part
        string equipment
        string movement_type "COMPOUND, ISOLATION"
        string movement_pattern "PUSH, PULL, SQUAT, HINGE, CORE"
        string difficulty_level
        text instructions
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid evaluation_id FK
        uuid client_id
        string recommendation_engine "HYBRID_NCF, CONTENT_BASED"
        jsonb recommended_exercise_ids
        jsonb scoring_breakdown
        timestamp created_at
    }

    WORKOUT_PLANS {
        uuid id PK
        uuid recommendation_id FK
        uuid client_id
        uuid trainer_id "Opcional hasta ser aprobado"
        string program_name
        string status "PENDIENTE_APROBACION, APROBADA, MODIFICADA, RECHAZADA"
        text trainer_notes
        timestamp approved_at
        timestamp created_at
    }

    WORKOUT_PLAN_DAYS {
        uuid id PK
        uuid workout_plan_id FK
        integer day_number
        string day_label "Ej: Lunes - Pierna y Core"
    }

    WORKOUT_PLAN_EXERCISES {
        uuid id PK
        uuid workout_plan_day_id FK
        uuid exercise_id FK
        integer order_index
        integer target_sets
        string target_reps
        integer rest_seconds
        string intensity_rpe
        text notes
    }

    WORKOUT_PROGRESS {
        uuid id PK
        uuid workout_plan_id FK
        uuid client_id
        uuid exercise_id FK
        integer sets_completed
        integer reps_completed
        float weight_lifted_kg
        integer perceived_effort_rpe "1 a 10"
        text client_comments
        timestamp logged_at
    }
```

---

## 2. Índices y Reglas de Integridad

1. **Evaluations:**
   - Índice sobre `client_id` para acelerar consultas históricas del ERP: `CREATE INDEX idx_evaluations_client ON evaluations(client_id);`
   - Índice sobre `created_at` para ordenar evoluciones temporales.

2. **Workout Plans:**
   - Índice sobre `(client_id, status)` para consultar rápidamente la rutina vigente y planes pendientes de revisión por entrenadores.

3. **Exercises:**
   - Búsqueda por `body_part`, `target_muscle`, `equipment` y `difficulty_level`.
   - Carga inicial provista por el dataset enriquecido canónico `exercises_clean.csv`.
