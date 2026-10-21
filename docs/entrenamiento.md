# Documentación de Entrenamiento y Evaluación de Modelos

Este documento detalla el ciclo de vida de los datos, procedimientos de entrenamiento y evaluación empírica de los modelos utilizados en el microservicio.

---

## 1. Datasets Empleados

1. **Dataset de Ejercicios Canónicos (`exercises_clean.csv`):**
   - 51 ejercicios estandarizados con variables de grupo muscular primario, secundario, tipo de movimiento (compuesto o aislado), patrón motor (empuje, tracción, dominante de rodilla, dominante de cadera, core) y equipamiento necesario.
2. **Dataset de Estimación Postural y Ángulos:**
   - Vector de características extraído de secuencias de landmarks normalizados por altura de torso.
3. **Dataset de Interacciones y Validación NCF:**
   - Matriz de interacción usuario-ejercicio con partición fija 80% train / 20% test mediante semilla pseudoaleatoria reproducible (`seed=42`).

---

## 2. Métricas de Rendimiento y Evaluación de Modelos

Para el módulo de recomendación, la evaluación compara rigurosamente los modelos en tareas de Top-K ranking:

| Métrica | Content-Based | SVD (Collaborative) | Neural CF (GMF+MLP) |
| :--- | :---: | :---: | :---: |
| **Precision@5** | 0.1071 | 0.0810 | **0.1099** |
| **Recall@5** | 0.2795 | 0.2067 | **0.2925** |
| **NDCG@5** | 0.2029 | 0.1511 | **0.2103** |
| **Hit Rate@5** | **0.4744** | 0.3591 | 0.4701 |
| **Precision@10**| 0.0937 | 0.0741 | **0.0953** |
| **Recall@10** | 0.4857 | 0.3818 | **0.5025** |
| **NDCG@10** | 0.2828 | 0.2184 | **0.2917** |
| **Hit Rate@10**| 0.7138 | 0.5963 | **0.7214** |

> **Nota Crítica sobre Datos Sintéticos:**
> El benchmark experimental de FitRec evidencia que NCF obtiene las mejores métricas de ranking sobre las 15,000 interacciones generadas; sin embargo, al tratarse de un dataset sintético, en producción se prioriza el recomendador Content-Based como fallback primario para clientes sin interacciones reales registradas en el ERP.

---

## 3. Procedimiento de Reentrenamiento y Gobernanza

- **Aislamiento en Producción:** Ningún endpoint del microservicio realiza reentrenamiento dinámico en el ciclo de solicitud HTTP (`request-response`).
- **Pipeline Desacoplado:** Los scripts de reentrenamiento residen en `ml/training/` y generan artefactos versionados con hashes SHA-256 en `ml/registry/`.
- **Reproducibilidad:** Todos los scripts fijan semillas deterministas (`torch.manual_seed(42)`, `numpy.random.seed(42)`).
