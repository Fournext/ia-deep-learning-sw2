# Visión General del Proyecto: Microservicio de IA para ERP de Gimnasio

## 1. Propósito del Sistema
El microservicio de Inteligencia Artificial tiene como objetivo potenciar el ERP del gimnasio mediante dos capacidades clave:
1. **Análisis Biomecánico Visual:** Analizar fotografías estáticas y videos de clientes durante la ejecución de ejercicios para extraer puntos articulares (landmarks), calcular ángulos anatómicos, rangos de movimiento (ROM) y clasificar patrones de movimiento o desviaciones posturales notables.
2. **Recomendación Inteligente de Rutinas:** Cruzar las características posturales observadas, los objetivos del cliente (hipertrofia, resistencia, rehabilitación, pérdida de grasa), nivel de experiencia física y restricciones/lesiones, generando propuestas de entrenamiento personalizadas y seguras.
3. **Flujo Human-in-the-Loop:** La rutina generada se mantiene en estado `PENDING_APPROVAL` hasta que un entrenador profesional humano la revisa, ajusta y aprueba en el ERP.

---

## 2. Stack Tecnológico Seleccionado
- **Lenguaje:** Python 3.11+
- **Framework Web:** FastAPI (asíncrono, OpenAPI nativo)
- **Persistencia:** PostgreSQL 16 con SQLAlchemy 2.x (async) y Alembic
- **Validación de Datos:** Pydantic v2
- **Computer Vision & Pose Estimation:** MediaPipe (Pose Solution), OpenCV, NumPy
- **Deep Learning / Modelos:** PyTorch / ONNX Runtime (para inferencia optimizada)
- **Modelos de Referencia:** FitVisionAI (análisis de movimiento) y FitRec (recomendación secuencial)
- **Infraestructura:** Docker (multi-stage) y Docker Compose
- **Calidad y Seguridad:** Pytest, pytest-cov, Ruff, mypy (--strict), Bandit, pip-audit

---

## 3. Arquitectura de Alto Nivel (Clean Architecture)

```
+--------------------------------------------------------------------------+
|                            PRESENTATION LAYER                            |
|       FastAPI Endpoints (Routers), OpenAPI Docs, Middlewares, Auth       |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                            APPLICATION LAYER                             |
|       Application Services, Use Cases, DTOs (Pydantic v2), Events        |
+--------------------------------------------------------------------------+
                    /                                \
                   v                                  v
+------------------------------------+   +---------------------------------+
|            DOMAIN LAYER            |   |       INFRASTRUCTURE LAYER      |
|  Pure Entities, Value Objects,     |   |  SQLAlchemy Repositories,       |
|  Domain Exceptions, Interfaces/    |<--|  MediaPipe / CV Pipelines,      |
|  Protocols, Core Business Logic    |   |  FitVision / FitRec Adapters,   |
+------------------------------------+   |  PostgreSQL Engine, Alembic     |
                                         +---------------------------------+
```

---

## 4. Agentes Especializados Responsables

| Agente | Alcance Técnico |
| :--- | :--- |
| `system-architect` | Orquestación, contratos, límites modulares y gobernanza |
| `deep-learning-engineer` | MediaPipe, OpenCV, cálculos cinemáticos y adaptación de FitVisionAI |
| `recommendation-engineer` | Algoritmos de recomendación híbridos, cold-start y adaptación de FitRec |
| `fastapi-backend-engineer` | Endpoints REST, Pydantic, SQLAlchemy 2.x, Alembic y Auth |
| `qa-testing-engineer` | Pytest, cobertura >=85%, tests de integración y contratos |
| `devsecops-mlops-engineer` | Docker, Compose, CI/CD, Linters, Seguridad y MLOps |
| `technical-auditor` | Auditoría independiente, cumplimiento SOLID, anti-mocking |
