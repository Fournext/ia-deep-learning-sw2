# Registro de Decisiones de Arquitectura (ADR)

Este documento registra las decisiones arquitectónicas estructurales tomadas para el microservicio de IA.

---

## ADR-001: Adopción de Clean Architecture y Separación Estricta de Capas
- **Fecha:** 2026-10-19
- **Estado:** Aceptado
- **Contexto:** El microservicio involucra cómputo matemático intensivo (CV/DL), reglas de recomendación, lógica de negocio y persistencia en base de datos. Mezclar dependencias de frameworks con modelos de ML generaría deuda técnica y acoplamiento severo.
- **Decisión:** Implementar Clean Architecture. El dominio (entidades puras e interfaces) estará totalmente libre de dependencias de terceros (como FastAPI, SQLAlchemy o OpenCV). Toda interacción con bases de datos o librerías de visión se implementará mediante adaptadores en la capa de infraestructura.
- **Consecuencias:**
  * Facilita pruebas unitarias sin dependencias externas complejas.
  * Mayor disciplina en la inyección de dependencias.

---

## ADR-002: Inferencia Desacoplada y Asíncrona para Video y Fotografías
- **Fecha:** 2026-10-19
- **Estado:** Aceptado
- **Contexto:** El procesamiento de video y la extracción de landmarks con MediaPipe son operaciones que consumen alta CPU/GPU y pueden tardar varios segundos, bloqueando el event loop de FastAPI si se ejecutan síncronamente en la petición HTTP.
- **Decisión:** La ingesta de archivos multimedia responderá inmediatamente con `HTTP 202 Accepted` y un identificador de tarea (`task_id`). La inferencia se ejecutará en hilos separados (`asyncio.to_thread`) o trabajadores en background, actualizando el estado del análisis en la base de datos para consulta mediante polling o webhook.
- **Consecuencias:**
  * La API mantiene alta disponibilidad y tiempos de respuesta de milisegundos en el router principal.
  * Requiere un mecanismo de control de estado de tareas (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).

---

## ADR-003: Recomendador Híbrido en Dos Etapas con Filtro Inmutable de Seguridad
- **Fecha:** 2026-10-19
- **Estado:** Aceptado
- **Contexto:** Recomendar rutinas con ejercicios lesivos para un usuario con limitaciones articulares o desbalances posturales severos representa un riesgo físico inaceptable. Ningún modelo probabilístico (como filtrado colaborativo puro) garantiza al 100% la exclusión de contraindicaciones.
- **Decisión:** Implementar un sistema en dos etapas:
  1. *Etapa de Recuperación y Reglas Duras:* Filtrado determinista basado en restricciones médicas/físicas y equipo disponible (Hard Exclusions).
  2. *Etapa de Ranking:* Scoring mediante modelo de similitud/contenido ponderado con características visuales observadas.
  3. *Aprobación:* El resultado final se etiqueta siempre como `PENDING_TRAINER_APPROVAL`.
- **Consecuencias:**
  * Cero riesgo de recomendar ejercicios contraindicados por errores del modelo latente.
  * La responsabilidad final de prescripción se mantiene en el entrenador humano.

---

## ADR-004: Adopción de SQLAlchemy 2.0 y Pydantic v2
- **Fecha:** 2026-10-19
- **Estado:** Aceptado
- **Contexto:** Se requiere interoperabilidad moderna, máxima velocidad de serialización en Python y tipado estricto.
- **Decisión:** Usar SQLAlchemy 2.x con `Mapped[...]`, `mapped_column()` y sesiones asíncronas con `asyncpg`. Usar Pydantic v2 con validadores estrictos y serialización en Rust.
- **Consecuencias:**
  * Código 100% tipado compatible con `mypy --strict`.
  * Mayor rendimiento en parseo de payloads.
