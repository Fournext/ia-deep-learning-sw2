# Modelos de Inteligencia Artificial y Visión por Computadora

Este documento detalla los modelos, algoritmos, entradas, salidas y restricciones éticas de los componentes de IA del microservicio.

---

## 1. Estimación de Pose y Biomecánica (MediaPipe Pose)

### 1.1 Modelo Base
- **Algoritmo:** MediaPipe Pose (BlazePose GHUM 3D).
- **Entradas:** Imagen estática (RGB, resolución mínima sugerida 640x480) o secuencia de video (24-60 FPS).
- **Salidas:** 33 puntos de referencia tridimensionales normalizados $(x, y, z)$ y un coeficiente de visibilidad/presencia $[0.0, 1.0]$.

### 1.2 Cálculos Biomecánicos Derivados
- **Ángulo Articular 2D/3D:**
  $$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right)$$
  Donde $\vec{u}$ y $\vec{v}$ son los vectores formados por la articulación central y sus dos articulaciones adyacentes (ej. Rodilla con Cadera y Tobillo).
- **Inclinación de Segmentos (Slope):**
  Calculado para la línea bi-acromial (hombros) y la línea bi-ilíaca (caderas) respecto a la horizontal.

---

## 2. Clasificación de Fases y Conteo en Videos (Sentadillas y Flexiones)

### 2.1 Enfoque Híbrido: Red Neuronal + Máquina de Estados
- **Pipeline:**
  1. Extracción de coordenadas clave en cada fotograma.
  2. Suavizado temporal de ángulos articulares con ventana móvil.
  3. Clasificación de fase (`START`, `INFLECTION/BOTTOM`, `COMPLETION`).
  4. Transición de estados finitos que valida que la repetición completó el rango de movimiento mínimo requerido (ROM) antes de incrementar el contador.

### 2.2 Fallback Biomecánico Determinista
Si la inferencia neuronal reporta baja confianza o no se cuenta con aceleración de hardware, el sistema conmuta automáticamente a umbrales biomecánicos validados:
- Sentadilla: Flexión de rodilla $< 100^\circ$ para repetición profunda válida.
- Flexión: Ángulo de codo $< 90^\circ$ en fase excéntrica.

---

## 3. Motor de Recomendación: Neural Collaborative Filtering (NCF) + Content-Based

### 3.1 Arquitectura Neural CF (GMF + MLP)
- **Generalized Matrix Factorization (GMF):** Producto punto de embeddings latentes de usuarios y ejercicios.
- **Multi-Layer Perceptron (MLP):** Concatenación de embeddings pasando por capas densas no lineales con activación ReLU y Dropout.
- **Capa de Fusión:** Concatena la salida de GMF y MLP hacia una neurona sigmoide final que estima la probabilidad de afinidad:
  $$\hat{y}_{u,i} = \sigma\left(h^T \left[\phi^{GMF} \,\|\, \phi^{MLP}\right]\right)$$

### 3.2 Estrategia para Usuarios Nuevos (Cold Start)
Para clientes del ERP sin interacciones históricas, se activa el recomendador **Content-Based Filtering**:
- Pondera matriz de características de ejercicios: dificultad vs. experiencia, equipamiento disponible vs. inventario del cliente, grupo muscular vs. objetivo.
- Garantiza que la primera rutina se genere en $< 150 \text{ ms}$ sin depender de datos de entrenamiento sintéticos.

---

## 4. Limitaciones Éticas y Médicas No Negociables

1. **No diagnóstico médico:** Prohibido catalogar escoliosis, lordosis clínica, roturas de menisco o tendinitis mediante cámara web o fotos.
2. **No cálculo inventado de grasa corporal:** Prohibido emitir porcentajes de grasa o masa muscular con fotos 2D; esto requiere bioimpedancia o plicometría en el gimnasio físico.
3. **Calidad de imagen insuficiente:** Si la visibilidad promedio de los landmarks cae por debajo de 0.65, el sistema reporta `CALIDAD_INSUFICIENTE` y no emite veredicto.
