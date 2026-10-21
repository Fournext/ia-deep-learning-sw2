# Documento de Integración y Análisis de Repositorios de Referencia

Este documento consolida la investigación técnica, revisión de licencias, auditoría de modelos preentrenados y análisis de componentes reutilizables de los repositorios clonados en `references/`.

---

## 1. Resumen Ejecutivo de Repositorios

| Repositorio | Licencia | Enfoque Principal | Modelos Disponibles | Nivel de Reutilización |
| :--- | :--- | :--- | :--- | :--- |
| **FitVisionAI** (`Niyatiiii06/FitVisionAI`) | MIT | Visión artificial, MediaPipe Pose, clasificación de fases y conteo de repeticiones (Pushup y Squat). | Redes neuronales ANN Keras (`pushup_ann.keras`, `squat_ann.keras`) con scalers y label encoders. | **Alto (Adaptado):** Extracción de ángulos, cálculo biomecánico y lógica de máquina de estados. |
| **FitRec** (`Khaledel123/fitness-recommender`) | MIT / Open Source | Recomendador multi-enfoque (Content-Based, SVD, Neural Collaborative Filtering). | Modelos en notebooks, datasets limpios (`exercises_clean.csv`, 1000 perfiles, 15000 interacciones sintéticas). | **Alto (Adaptado):** Dataset canónico de ejercicios, modelo NCF en PyTorch y motor híbrido Content-Based. |
| **AI-Personal-Trainer** (`thaochu05/AI-Personal-Trainer`) | MIT / Open Source | Evaluación de postura con MediaPipe, heurística de ángulos y transiciones de estados (Squats, Curls, Lunges). | Heurísticas basadas en umbrales biomecánicos (`thresholds.py`). | **Medio (Referencia):** Detección de ángulo de desvío de cámara (*camera offset*) y reglas geométricas. |

---

## 2. Análisis Detallado por Repositorio

### 2.1 FitVisionAI

- **Arquitectura Original:** Aplicación monolítica en Streamlit con scripts sueltos (`app.py`, `train_model.py`, `src/`).
- **Puntos Fuertes:**
  - Implementación sólida de MediaPipe Pose (33 landmarks).
  - Cálculo de ángulos articulares clave: codo, hombro, cadera, rodilla, tobillo.
  - Modelos entrenados presentes en `models/`:
    - `pushup_ann.keras` + `pushup_scaler.pkl` + `pushup_label_encoder.pkl`
    - `squat_ann.keras` + `squat_scaler.pkl` + `squat_label_encoder.pkl`
  - Máquina de estados para conteo de repeticiones (`UP` -> `DOWN` -> `UP`).
- **Limitaciones Identificadas:**
  - Acoplamiento directo con Streamlit y OpenCV GUI (`cv2.imshow`).
  - No apto directamente para peticiones HTTP ni procesamiento asíncrono sin refactorización.
  - Dependencias de Keras/TensorFlow que pueden entrar en conflicto con PyTorch y Python 3.12+.
- **Estrategia de Adaptación:**
  - Extraer la lógica pura de cálculo de ángulos e inferencia a la capa de dominio/infraestructura desacoplada de frameworks web.
  - Implementar tanto el predictor neuronal como el fallback determinista basado en umbrales biomecánicos (evita fallos de inferencia si las dependencias de Keras fallan en CPU o entornos restringidos).

### 2.2 FitRec (Fitness Recommender)

- **Arquitectura Original:** Colección de Jupyter Notebooks (`01_eda` a `05_neural_cf`) y una app demostrativa en Streamlit.
- **Puntos Fuertes:**
  - Dataset enriquecido de ejercicios (`exercises_clean.csv`) con categorías funcionales: grupo muscular, equipamiento, tipo de movimiento (push/pull/squat/hinge/core) y dificultad.
  - Comparativa rigurosa entre Content-Based, SVD y Neural Collaborative Filtering (NCF).
  - Métricas de ranking documentadas (Precision@K, Recall@K, NDCG@K).
- **Limitaciones Identificadas:**
  - Las 15,000 interacciones provienen de reglas sintéticas generadas probabilísticamente; no representan datos clínicos de clientes de gimnasio.
  - El modelo NCF requiere historial de usuario, por lo que sufre el problema de *Cold Start* ante usuarios nuevos del ERP.
  - No contempla inputs de evaluaciones visuales ni restricciones médicas.
- **Estrategia de Adaptación:**
  - Implementar arquitectura de recomendación en cascada (*Cascading Hybrid Recommender*):
    1. **Filtro de seguridad y restricciones:** Excluye ejercicios incompatibles con limitaciones declaradas por el cliente.
    2. **Filtro de concordancia visual:** Si el análisis de postura revela asimetrías o déficits de movilidad (ej. profundidad insuficiente en sentadillas), prioriza ejercicios correctivos o de menor impacto.
    3. **Content-Based Filtering:** Para clientes nuevos (*Cold Start*) basándose en objetivos, equipamiento y experiencia.
    4. **Neural CF (PyTorch):** Red GMF + MLP desacoplada para clientes con historial de interacción.

### 2.3 AI-Personal-Trainer

- **Arquitectura Original:** Aplicación Streamlit orientada a ejercicios con pesas y calistenia.
- **Puntos Fuertes:**
  - Validación de perspectiva de cámara mediante ángulo entre nariz y hombros (*view angle offset*), alertando cuando la persona no está alineada con el plano sagital/frontal.
  - Umbrales empíricos para ejercicios adicionales (Lunges, Bicep Curls).
- **Limitaciones Identificadas:**
  - Generación de planes basada en prompts simulados sin persistencia en base de datos.
  - Código con scripts redundantes y dependencias no versionadas.
- **Estrategia de Adaptación:**
  - Reutilizar la lógica de verificación de calidad del encuadre y ángulo de perspectiva para el Módulo B (Análisis de Fotografías).

---

## 3. Matriz de Componentes: Reutilizados, Adaptados y Nuevos

| Componente | Origen | Estado | Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Cálculo de ángulos articulares 2D/3D** | FitVisionAI (`angle_calculator.py`) | Adaptado | Extraído a `app/modules/pose_estimation/` con tipado estricto `numpy` y sin dependencias UI. |
| **Clasificación de fases (Squat / Pushup)** | FitVisionAI (`models/`) | Adaptado + Fallback | Conversión/adaptación de inferencia y adición de fallback geométrico determinista para máxima robustez. |
| **Dataset de 51 ejercicios canónicos** | FitRec (`exercises_clean.csv`) | Reutilizado | Base de conocimiento para la tabla `exercises` de PostgreSQL con migraciones Alembic. |
| **Arquitectura Neural CF (GMF + MLP)** | FitRec (`05_neural_cf.ipynb`) | Adaptado | Implementada en PyTorch nativo dentro de `app/modules/recommendations/` para inferencia eficiente en CPU/GPU. |
| **Validador de perspectiva y asimetría** | AI-Personal-Trainer (`utils.py`) | Adaptado | Integrado al procesador de fotografías estáticas (vista frontal/lateral/posterior). |
| **API REST FastAPI con Clean Architecture** | Ninguno | **Nuevo desde cero** | Arquitectura modular con routers v1, servicios desacoplados, Pydantic v2 y repositorios SQLAlchemy 2.0. |
| **Flujo de Human-in-the-Loop y Workflow de Aprobación** | Ninguno | **Nuevo desde cero** | Entidad de rutinas con estados `PENDIENTE_APROBACION`, `APROBADA`, `MODIFICADA`, garantizando supervisión médica/de entrenador. |
| **Persistencia Asíncrona con PostgreSQL y Alembic** | Ninguno | **Nuevo desde cero** | Modelos relacionales con UUIDs, tipos enum tipados y transacciones seguras. |

---

## 4. Dictamen de Compatibilidad del Entorno

- **Versión de Python elegida:** Python 3.12 (verificada en entorno `.venv`). Ofrece compatibilidad óptima con MediaPipe, OpenCV, PyTorch 2.x, Pydantic v2 y FastAPI.
- **Inferencia en Producción:** Se descarta el uso de TensorFlow monolítico pesado en la API en favor de PyTorch ligero y MediaPipe nativo, garantizando arranque rápido y bajo consumo de memoria en contenedores Docker CPU.
