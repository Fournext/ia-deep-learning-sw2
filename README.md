# Microservicio de Inteligencia Artificial — ERP Gimnasio

Microservicio de Inteligencia Artificial y Visión por Computadora diseñado para integrarse con el sistema ERP de un gimnasio. Permite analizar fotografías y videos de clientes, extraer características corporales y patrones de movimiento, y generar recomendaciones de rutinas de entrenamiento personalizadas bajo un flujo estricto de **aprobación humana por parte del entrenador (*Human-in-the-Loop*)**.

---

## 1. Principios Éticos y Límites de Operación (No Negociables)

- **No Diagnóstico Médico:** El sistema nunca diagnostica patologías, lesiones ni afecciones de columna.
- **No Estimación Ficticia de Composición Corporal:** No se calculan porcentajes de grasa ni masa muscular a partir de simples fotografías 2D.
- **Human-in-the-Loop Obligatorio:** Ninguna rutina generada por la IA entra en vigor para el cliente sin la revisión, ajuste y aprobación formal del entrenador acreditado en el ERP (Estado inicial inmutable: `PENDIENTE_APROBACION`).

---

## 2. Tecnologías Empleadas

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.12 + FastAPI |
| **Validación de Entradas** | Pydantic v2 + Pydantic Settings |
| **Visión Artificial** | OpenCV + MediaPipe Pose (Tasks API) |
| **Deep Learning** | PyTorch (Neural Collaborative Filtering: GMF + MLP) |
| **Recomendador** | Motor Híbrido: Filtrado por Restricciones $\rightarrow$ Content-Based $\rightarrow$ Neural CF |
| **Base de Datos** | PostgreSQL 16 / SQLite en memoria (Tests) |
| **ORM y Migraciones** | SQLAlchemy 2.0 (Async) + Alembic |
| **Testing y Cobertura** | Pytest + pytest-cov + pytest-asyncio (Cobertura alcanzada: **85%**) |
| **Análisis Estático** | Ruff (0 errores) + Mypy estricto (`mypy --strict`, 0 errores) |
| **Contenedores** | Dockerfile multi-stage + Docker Compose |

---

## 3. Repositorios de Referencia Analizados

El sistema integra y adapta de forma modular componentes analizados en `references/`:
1. **FitVisionAI (`Niyatiiii06/FitVisionAI`):** Extracción de ángulos articulares y lógica de máquina de estados para clasificación de fases y conteo de sentadillas y flexiones.
2. **FitRec (`Khaledel123/fitness-recommender`):** Dataset de 51 ejercicios canónicos (`exercises_clean.csv`) y arquitectura Neural CF adaptada a PyTorch desacoplada de interfaces web.
3. **AI-Personal-Trainer (`thaochu05/AI-Personal-Trainer`):** Heurísticas de umbrales biomecánicos y validación de alineación de perspectiva de cámara.

*Documentación completa en [docs/integracion_repositorios.md](docs/integracion_repositorios.md).*

---

## 4. Arquitectura de Software

El microservicio está estructurado estrictamente bajo **Clean Architecture**:

```text
app/
├── core/                # Configuración central, logging estructurado y excepciones de dominio
├── domain/              # Núcleo puro de negocio sin acoplamiento a frameworks
│   ├── entities/        # Entidades puras (Evaluation, Exercise, WorkoutPlan, etc.)
│   └── interfaces/      # Protocolos de repositorios y motores de IA (DIP)
├── infrastructure/      # Adaptadores concretos
│   ├── cv/              # MediaPipe Pose y procesador de video
│   ├── ml/              # PyTorch Neural CF y recomendador híbrido
│   ├── database/        # Sesión async SQLAlchemy y base declarativa
│   ├── models/          # Modelos relacionales ORM
│   └── repositories/    # Implementaciones de repositorios
├── modules/             # Casos de uso de la aplicación
│   ├── evaluations/     # Gestión y comparación de evaluaciones
│   ├── image_analysis/  # Extracción de simetría y alineación
│   ├── video_analysis/  # Conteo de repeticiones y análisis biomecánico
│   ├── recommendations/ # Generación de recomendaciones
│   ├── workout_plans/   # Creación y aprobación por entrenador
│   └── progress_tracking/# Registro de sesiones y RPE
└── api/v1/              # Routers REST FastAPI y esquemas Pydantic v2
```

---

## 5. Puesta en Marcha

### Opción A: Con Docker Compose (Recomendado para Producción)

```bash
# 1. Clonar el repositorio y configurar variables de entorno
cp .env.example .env

# 2. Levantar la API y PostgreSQL en segundo plano
docker compose up -d --build

# 3. Comprobar que los contenedores están saludables
docker compose ps
```

- **API REST:** `http://localhost:8000/api/v1`
- **Documentación Swagger UI:** `http://localhost:8000/docs`
- **Health check de liveness:** `http://localhost:8000/health/live`
- **Health check de readiness:** `http://localhost:8000/health/ready`

---

### Opción B: Ejecución Local en Entorno Virtual

```bash
# 1. Crear y activar entorno virtual con Python 3.12
py -3.12 -m venv .venv
.\.venv\Scripts\activate

# 2. Instalar dependencias
pip install -e ".[dev]"

# 3. Descargar el modelo de MediaPipe Pose
python -c "import urllib.request, os; os.makedirs('models', exist_ok=True); urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task', 'models/pose_landmarker_lite.task')"

# 4. Iniciar el servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

---

## 6. Pruebas Automatizadas y Calidad

Para ejecutar la suite de pruebas unitarias, de integración y reporte de cobertura:

```bash
# Ejecutar Pytest con reporte de cobertura
pytest --cov=app --cov-report=term-missing tests/

# Verificación estricta de tipos estáticos
mypy app/

# Auditoría de formato y calidad de código
ruff check app/ tests/
```

### Resultados Empíricos Certificados:
- **35 pruebas ejecutadas / 35 aprobadas (100% éxito)**.
- **85% de cobertura de código alcanzada**.
- **0 errores en `mypy --strict` (66 archivos analizados)**.
- **0 errores en `ruff check` (All checks passed!)**.

---

## 7. Documentación Técnica Detallada

Consulte la carpeta `docs/` para documentación en profundidad:

1. [docs/arquitectura.md](docs/arquitectura.md): Arquitectura general y diagrama modular Mermaid.
2. [docs/integracion_repositorios.md](docs/integracion_repositorios.md): Análisis exhaustivo de los repositorios de referencia.
3. [docs/flujo_funcional.md](docs/flujo_funcional.md): Diagrama de secuencia del cliente y entrenador.
4. [docs/modelos_ia.md](docs/modelos_ia.md): Modelos MediaPipe Pose y PyTorch NCF.
5. [docs/entrenamiento.md](docs/entrenamiento.md): Datasets, reproducibilidad y métricas Top-K.
6. [docs/api.md](docs/api.md): Especificación de endpoints y ejemplos JSON.
7. [docs/base_datos.md](docs/base_datos.md): Diagrama entidad-relación y tablas PostgreSQL.
8. [docs/pruebas.md](docs/pruebas.md): Evidencias reales de terminal y reporte de cobertura.
9. [docs/despliegue.md](docs/despliegue.md): Guía de instalación y variables `.env`.
10. [docs/limitaciones.md](docs/limitaciones.md): Registro de limitaciones y consideraciones operativas.
