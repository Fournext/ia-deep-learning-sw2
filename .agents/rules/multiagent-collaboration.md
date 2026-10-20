# Protocolo de Colaboración Multiagente y Orquestación

Este documento norma la interacción entre el agente orquestador (`system-architect`) y los agentes especialistas.

## 1. Cadena de Mando y Flujo de Trabajo
1. El usuario interactúa únicamente con el agente principal `system-architect`.
2. `system-architect` analiza el alcance, actualiza `docs/agent-context/task-board.md` y descompone el trabajo en tareas unitarias.
3. Cada tarea se delega a un subagente específico indicándole:
   - Identificador de la tarea (ej. `TASK-001`).
   - Criterios de aceptación objetivos.
   - Archivos y contratos relevantes de `docs/agent-context/`.
4. El subagente ejecuta el trabajo de forma autónoma y devuelve un entregable estructurado según el Estándar de Entrega.
5. `system-architect` solicita la evaluación cruzada a `qa-testing-engineer` (tests y cobertura) y `technical-auditor` (arquitectura, seguridad y anti-mocking).
6. Si existen observaciones, se abre un ciclo de corrección con el agente responsable.
7. Una vez aprobado por QA y Auditor, `system-architect` actualiza `docs/agent-context/implementation-status.md` y presenta los resultados con evidencia empírica al usuario.

## 2. Aislamiento y Trabajo Paralelo
- Cuando dos subagentes requieran trabajar en módulos independientes en paralelo, se utilizarán ramas o Git worktrees aislados para evitar conflictos de archivos.
- Las dependencias entre tareas deben declararse explícitamente en el tablero de tareas antes de iniciar la ejecución.
