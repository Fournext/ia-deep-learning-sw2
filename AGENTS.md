# REGLAS GENERALES DEL SISTEMA MULTIAGENTE — ERP GIMNASIO IA

Este documento rige el comportamiento, los estándares técnicos y los límites de operación de todos los agentes que intervienen en el desarrollo del microservicio de Inteligencia Artificial para el ERP de Gimnasio.

---

## 1. PRINCIPIOS DE INGENIERÍA DE SOFTWARE OBLIGATORIOS

1. **Clean Architecture:**
   - La arquitectura debe respetar estrictamente la regla de dependencias: las dependencias del código fuente solo pueden apuntar hacia adentro (hacia el Dominio).
   - El Dominio no debe conocer frameworks, librerías de persistencia (SQLAlchemy) ni librerías de visión por computadora (OpenCV/MediaPipe).
   - La Infraestructura implementa las interfaces definidas en el Dominio o Aplicación.

2. **Principios SOLID:**
   - **SRP (Single Responsibility Principle):** Cada módulo o clase debe tener una única responsabilidad bien definida.
   - **OCP (Open/Closed Principle):** Las entidades deben estar abiertas para la extensión pero cerradas para la modificación directa.
   - **LSP (Liskov Substitution Principle):** Las implementaciones derivadas deben poder sustituir a sus abstracciones sin alterar el comportamiento esperado.
   - **ISP (Interface Segregation Principle):** Interfaces pequeñas y específicas en lugar de interfaces generales sobrecargadas.
   - **DIP (Dependency Inversion Principle):** Depender de abstracciones (protocolos/interfaces), no de concreciones.

3. **DRY (Don't Repeat Yourself) & KISS (Keep It Simple, Stupid):**
   - Centralizar la lógica común en servicios y utilidades reutilizables.
   - Evitar sobreingeniería o patrones complejos innecesarios antes de que exista justificación real.

4. **Modularidad Estricta:**
   - Cada componente (CV, Recomendador, Backend, MLOps) debe diseñarse de modo que pueda desarrollarse, probarse y desplegarse independientemente.

---

## 2. ESTÁNDARES DE CODIFICACIÓN EN PYTHON

1. **PEP 8 y PEP 257:**
   - Formato de código automatizado conforme a Ruff.
   - Todas las clases, métodos públicos y funciones deben incluir docstrings claros (estilo Google) en español, explicando argumentos, retornos y excepciones arrojadas.

2. **Type Hints Estrictos:**
   - El 100% del código nuevo debe incluir anotaciones de tipo completas.
   - El proyecto debe pasar la verificación estricta de tipos con `mypy --strict`.

3. **Validación de Entradas:**
   - Toda entrada externa (solicitudes HTTP, cargas de archivos, variables de entorno) debe validarse estrictamente con esquemas Pydantic v2 antes de tocar la lógica de negocio.

4. **Manejo Explícito de Excepciones:**
   - Prohibido el uso de bloques `except Exception: pass`.
   - Definir excepciones de dominio específicas (ej. `LandmarksNotFoundError`, `InvalidBiomechanicalAngleError`, `ExerciseIncompatibleError`, `RoutineApprovalPendingError`).
   - Los errores de la API deben retornar códigos HTTP semánticos y esquemas de error estandarizados.

---

## 3. ESTÁNDARES DE MACHINE LEARNING Y COMPUTER VISION

1. **Separación de Entrenamiento e Inferencia:**
   - Los pipelines de inferencia para producción deben estar completamente aislados de scripts de entrenamiento, notebooks de exploración o descargas dinámicas masivas de datasets.

2. **Reproducibilidad:**
   - Todo pipeline, modelo o semilla pseudoaleatoria debe ser configurable y determinista cuando corresponda (`seed` fijada para evaluación).

3. **Dependencias Justificadas:**
   - Ninguna librería pesada debe añadirse sin justificación arquitectónica explícita y aprobación previa del `system-architect`.

4. **Límites Éticos y Médicos (No Negociable):**
   - **No diagnósticos médicos:** El sistema nunca diagnosticará patologías o lesiones.
   - **No estimación corporal inventada:** Prohibido calcular porcentajes de grasa o datos de composición corporal con meras fotografías 2D.
   - **Human-in-the-Loop:** Toda recomendación de ejercicios es una propuesta preliminar que requiere aprobación obligatoria del entrenador humano.

---

## 4. POLÍTICAS DE ENTREGA Y EVIDENCIAS (TOLERANCIA CERO AL CÓDIGO SIMULADO)

1. **Prohibición de Inventar Resultados:**
   - Queda estrictamente prohibido simular salidas de inferencia, inventar métricas de validación (`accuracy = 0.98`) o declarar tareas como finalizadas sin pruebas ejecutadas.
2. **Definición de "Done":**
   - Una tarea solo se considera completada cuando:
     * El código está implementado y tipado.
     * Cuenta con pruebas automatizadas en Pytest con aserciones reales.
     * La cobertura de pruebas unitarias cumple la meta del 85%.
     * Ha sido revisada y aprobada por `qa-testing-engineer` y `technical-auditor`.
     * Se adjuntan los logs reales de terminal que evidencian el éxito.
