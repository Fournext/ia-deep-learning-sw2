# Registro de Limitaciones Técnicas y Consideraciones Operativas

Este documento registra con total transparencia las limitaciones técnicas, supuestos de diseño y mitigaciones implementadas en el microservicio.

---

## 1. Limitaciones de Visión por Computadora (MediaPipe Pose)

1. **Oclusiones y Ropa Holgada:**
   - La precisión en la detección de puntos anatómicos disminuye significativamente si el usuario viste ropa muy holgada o si alguna articulación queda oculta detrás de equipamiento o fuera del plano de cámara.
   - *Mitigación:* Se implementa un filtro de umbral de visibilidad (`visibility >= 0.65`). Si no se alcanza, la imagen se rechaza con un error semántico explicativo (`ImageQualityLowError`).

2. **Ángulo de Captura y Perspectiva:**
   - Un ángulo de cámara diagonal o en contrapicado distorsiona los cálculos trigonométricos de pendientes en hombros y caderas.
   - *Mitigación:* Se valida la concordancia de orientación y se alertan desvíos mayores a $15^\circ$ respecto a la horizontal.

3. **Restricción Ética y Médica:**
   - No se diagnostica escoliosis, patologías de columna ni se emiten datos de composición corporal (grasa corporal o masa muscular) con fotos 2D. El análisis se limita estrictamente a métricas geométricas observables.

---

## 2. Limitaciones de los Modelos de Recomendación

1. **Datos Sintéticos de FitRec:**
   - El dataset original de 15,000 interacciones de FitRec es de naturaleza sintética generada por reglas probabilísticas. Por tanto, no debe considerarse como una prueba de eficacia clínica.
   - *Mitigación:* Se implementa una arquitectura híbrida donde el filtrado de seguridad y el recomendador Content-Based tienen prioridad garantizada, mientras que el modelo NCF proporciona ponderación latente cuando hay suficiente volumen de interacción real.

2. **Problema de Cold Start:**
   - Para clientes nuevos sin evaluaciones previas ni historial de ejercicios, el modelo NCF no cuenta con embeddings entrenados.
   - *Mitigación:* Fallback automático e instantáneo a Content-Based Filtering usando las características de los ejercicios, objetivos declarados y restricciones.

---

## 3. Limitaciones de Procesamiento de Video

1. **Procesamiento Asíncrono de Videos:**
   - El procesamiento cuadro a cuadro de videos de alta resolución (1080p o superior) es costoso en CPU.
   - *Mitigación:* Los videos se procesan redimensionados a 640x480 con submuestreo de frames para garantizar tiempos de respuesta rápidos y evitar saturación del servidor.

2. **Ejercicios Soportados Inicialmente:**
   - La clasificación de fases y conteo automatizado está validada empíricamente para **Sentadillas** (*Squats*) y **Flexiones de Brazos** (*Push-ups*). La arquitectura es extensible mediante interfaces para admitir nuevos ejercicios posteriormente.
