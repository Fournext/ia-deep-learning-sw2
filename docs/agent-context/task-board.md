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

## 1. Fase 1: Configuración de Equipo Multiagente (Etapa Actual)

| ID | Tarea | Agente Asignado | Estado | Dependencias | Criterios de Aceptación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TASK-SETUP-01` | Definición de agentes en `.agents/agents/` | `system-architect` | `COMPLETED` | Ninguna | 7 archivos markdown con YAML frontmatter y roles detallados. |
| `TASK-SETUP-02` | Definición de reglas y estándares compartidos | `system-architect` | `COMPLETED` | `TASK-SETUP-01` | `AGENTS.md` y `.agents/rules/*.md` con SOLID, Clean Arch y guías. |
| `TASK-SETUP-03` | Creación del sistema de gestión de contexto | `system-architect` | `COMPLETED` | `TASK-SETUP-02` | 7 archivos en `docs/agent-context/` inicializados y coherentes. |
| `TASK-SETUP-04` | Validación de descubrimiento e integración | `system-architect` | `IN_PROGRESS` | `TASK-SETUP-03` | Comprobación de archivos, sintaxis frontmatter y herramientas oficiales. |

---

## 2. Fase 2: Desarrollo del Microservicio (Fase Futura - Bloqueada hasta aprobación)

| ID | Tarea | Agente Asignado | Estado | Dependencias |
| :--- | :--- | :--- | :--- | :--- |
| `TASK-DEV-01` | Setup de infraestructura base, Docker y CI/CD | `devsecops-mlops-engineer` | `BACKLOG` | Aprobación Fase 1 |
| `TASK-DEV-02` | Estructura Clean Architecture, FastAPI y PostgreSQL | `fastapi-backend-engineer` | `BACKLOG` | `TASK-DEV-01` |
| `TASK-DEV-03` | Pipeline de extracción de landmarks y ángulos (MediaPipe) | `deep-learning-engineer` | `BACKLOG` | `TASK-DEV-02` |
| `TASK-DEV-04` | Motor de recomendación híbrido y reglas de seguridad | `recommendation-engineer` | `BACKLOG` | `TASK-DEV-02` |
| `TASK-DEV-05` | Integración de endpoints REST y procesamiento asíncrono | `fastapi-backend-engineer` | `BACKLOG` | `TASK-DEV-03`, `TASK-DEV-04` |
| `TASK-DEV-06` | Suite de pruebas automatizadas y cobertura >= 85% | `qa-testing-engineer` | `BACKLOG` | `TASK-DEV-05` |
| `TASK-DEV-07` | Auditoría técnica independiente y certificación final | `technical-auditor` | `BACKLOG` | `TASK-DEV-06` |
