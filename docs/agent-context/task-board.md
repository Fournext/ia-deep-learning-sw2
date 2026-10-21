# Tablero de Tareas y Asignaciones (Task Board)

Este tablero refleja el estado actual de las tareas de diseño, configuración e implementación del microservicio. Es administrado exclusivamente por `system-architect`.

---

## Leyenda de Estados
- `BACKLOG`: Tarea especificada pero no iniciada.
- `IN_PROGRESS`: Agente asignado trabajando activamente.
- `READY_FOR_REVIEW`: Código implementado con tests; pendiente de QA y Auditoría.
- `AUDIT_REJECTED`: Observaciones encontradas por QA o Auditor Técnico; devuelta al agente.
- `COMPLETED`: Aprobada formalmente con evidencias de pruebas y dictamen de auditoría.

---

## 1. Fase 1: Configuración de Equipo Multiagente e Investigación

| ID | Tarea | Agente Asignado | Estado | Dependencias | Criterios de Aceptación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-SETUP-01` | Definición de agentes en `.agents/agents/` | `system-architect` | `COMPLETED` | Ninguna | 7 archivos markdown con YAML frontmatter y roles detallados. |
| `TASK-SETUP-02` | Definición de reglas y estándares compartidos | `system-architect` | `COMPLETED` | `TASK-SETUP-01` | `AGENTS.md` y `.agents/rules/*.md` con SOLID, Clean Arch y guías. |
| `TASK-SETUP-03` | Creación del sistema de gestión de contexto | `system-architect` | `COMPLETED` | `TASK-SETUP-02` | 7 archivos en `docs/agent-context/` inicializados y coherentes. |
| `TASK-SETUP-04` | Clonación e integración de repositorios de referencia | `system-architect` | `COMPLETED` | `TASK-SETUP-03` | FitVisionAI, FitRec y AI-Personal-Trainer analizados en `docs/integracion_repositorios.md`. |

---

## 2. Fase 2: Desarrollo del Microservicio

| ID | Tarea | Agente Asignado | Estado | Criterios de Aceptación |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-DEV-01` | Setup de infraestructura base, Docker y CI/CD | `devsecops-mlops-engineer` | `COMPLETED` | Dockerfile multi-stage, `compose.yaml` con PostgreSQL 16 y `.env.example`. |
| `TASK-DEV-02` | Estructura Clean Architecture, FastAPI y PostgreSQL | `fastapi-backend-engineer` | `COMPLETED` | Capas de Dominio, Aplicación, Infraestructura y Presentación desacopladas. |
| `TASK-DEV-03` | Pipeline de extracción de landmarks y ángulos (MediaPipe) | `deep-learning-engineer` | `COMPLETED` | `MediaPipePoseDetector` con BlazePose 33 puntos, cálculo de pendientes y simetría bilateral. |
| `TASK-DEV-04` | Motor de recomendación híbrido y reglas de seguridad | `recommendation-engineer` | `COMPLETED` | Restricciones contraindicadas + Content-Based + PyTorch NCF con fallback. |
| `TASK-DEV-05` | Integración de endpoints REST y flujo Human-in-the-Loop | `fastapi-backend-engineer` | `COMPLETED` | Endpoints versionados (`/api/v1`), OpenAPI y flujo de aprobación por entrenador. |
| `TASK-DEV-06` | Suite de pruebas automatizadas y cobertura >= 85% | `qa-testing-engineer` | `COMPLETED` | 35 pruebas en pytest aprobadas con 85% de cobertura real. |
| `TASK-DEV-07` | Auditoría técnica independiente y certificación final | `technical-auditor` | `COMPLETED` | Verificado con `mypy --strict` (0 errores) y `ruff check` (All checks passed!). |

---

## 3. Fase 3: Transición a Inferencia Stateless (Cero Persistencia en BD)

| ID | Tarea | Agente Asignado | Estado | Criterios de Aceptación |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-STATELESS-01` | Repositorios en memoria y carga directa de dataset de ejercicios | `fastapi-backend-engineer` | `COMPLETED` | Repositorios en memoria implementados desacoplados de PostgreSQL, dataset cargado desde CSV. |
| `TASK-STATELESS-02` | Pipeline visual 100% en memoria con limpieza inmediata de temporales | `deep-learning-engineer` | `COMPLETED` | No guardar fotos en disco, procesar video con buffer efímero autodestruible en `finally`. |
| `TASK-STATELESS-03` | Endpoint unificado de análisis e inferencia `POST /api/v1/evaluations/analyze-and-recommend` | `fastapi-backend-engineer` | `COMPLETED` | Endpoint que recibe perfil + fotos/video y devuelve análisis + recomendación directa. |
| `TASK-STATELESS-04` | Desacoplamiento de PostgreSQL en ciclo de vida y Compose | `devsecops-mlops-engineer` | `COMPLETED` | `main.py` y `compose.yaml` optimizados para correr sin dependencia obligatoria de DB. |
| `TASK-STATELESS-05` | Pruebas unitarias/integración del flujo stateless y cobertura >= 85% | `qa-testing-engineer` | `COMPLETED` | 38 pruebas aprobadas (100% éxito) con 85% de cobertura total verificada. |
| `TASK-STATELESS-06` | Auditoría técnica independiente de cero persistencia | `technical-auditor` | `COMPLETED` | Inspección estricta de ausencia de escrituras a BD/disco, `mypy --strict` (0 errores) y `ruff` (All checks passed!). |
