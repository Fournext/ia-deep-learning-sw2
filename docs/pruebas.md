# Documentación de Estrategia de Pruebas y Resultados de QA

Este documento presenta la estrategia de pruebas, la política de tolerancia cero a mocks de inferencia inventados y los **resultados reales empíricos** obtenidos de la ejecución en la terminal.

---

## 1. Resumen Ejecutivo de Pruebas

| Parámetro | Meta / Requisito | Resultado Obtenido | Estado |
| :--- | :---: | :---: | :---: |
| **Pruebas Totales** | N/A | **35 pruebas unitarias, de integración, ML y API** | **APROBADO** (35/35) |
| **Cobertura de Código** | $\ge 85\%$ | **85% (1323/1560 líneas cubiertas)** | **APROBADO** |
| **Análisis Estático (Ruff)** | PEP 8, PEP 257 | **0 errores (All checks passed!)** | **APROBADO** |
| **Tipado Estricto (mypy)** | `mypy --strict` | **Success: no issues found in 66 source files** | **APROBADO** |
| **Seguridad y Anti-Mocking** | Cero inferencias simuladas | Inferencia real con MediaPipe Pose Tasks y PyTorch NCF | **CERTIFICADO** |

---

## 2. Evidencia Empírica de Terminal (Logs Reales)

### 2.1 Ejecución de Pytest y Cobertura

```text
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.12.0-final-0 _______________

Name                                                         Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------------
app\api\v1\api_router.py                                         9      0   100%
app\api\v1\endpoints\evaluations.py                             27      3    89%   44, 74, 106
app\api\v1\endpoints\health.py                                  17      2    88%   24-25
app\api\v1\endpoints\images.py                                  22      2    91%   48-49
app\api\v1\endpoints\progress.py                                22      2    91%   44, 70
app\api\v1\endpoints\recommendations.py                         27      3    89%   45, 66-67
app\api\v1\endpoints\videos.py                                  21      1    95%   47
app\api\v1\endpoints\workout_plans.py                           34      3    91%   84, 98, 122
app\api\v1\schemas\evaluations.py                               31      0   100%
app\api\v1\schemas\images.py                                    19      0   100%
app\api\v1\schemas\progress.py                                  25      0   100%
app\api\v1\schemas\recommendations.py                           15      0   100%
app\api\v1\schemas\videos.py                                    19      0   100%
app\api\v1\schemas\workout_plans.py                             42      0   100%
app\core\config.py                                              22      0   100%
app\core\exceptions.py                                          45      5    89%   76-77, 85-89
app\core\logging.py                                             14      1    93%   24
app\domain\entities\analysis_results.py                         36      0   100%
app\domain\entities\evaluation.py                               41      0   100%
app\domain\entities\exercise.py                                 29      0   100%
app\domain\entities\progress.py                                 17      0   100%
app\domain\entities\workout_plan.py                             52      0   100%
app\domain\interfaces\engines.py                                 9      0   100%
app\domain\interfaces\repositories.py                           28      0   100%
app\infrastructure\cv\angle_calculator.py                       30      1    97%   81
app\infrastructure\cv\cv_adapter.py                             13      0   100%
app\infrastructure\cv\pose_detector.py                          83     48    42%   67, 93, 109-192
app\infrastructure\cv\video_processor.py                        97     45    54%   32, 56-57, 83, 92-153, 164-167
app\infrastructure\database\session.py                          13      4    69%   33-37
app\infrastructure\ml\hybrid_recommender.py                     92     11    88%   29, 64-65, 81, 86, 88, 99-100, 106-107, 134
app\infrastructure\ml\neural_cf_model.py                        32      1    97%   20
app\infrastructure\models\orm_models.py                        125      0   100%
app\infrastructure\repositories\analysis_repository.py          36      0   100%
app\infrastructure\repositories\evaluation_repository.py        43      2    95%   98-99
app\infrastructure\repositories\exercise_repository.py          27      0   100%
app\infrastructure\repositories\progress_repository.py          23      4    83%   52-53, 63-64
app\infrastructure\repositories\workout_plan_repository.py      62     28    55%   98-99, 109-110, 122-178, 193-194
app\main.py                                                     67     27    60%   30-64, 70-86, 172
app\modules\evaluations\service.py                              24      5    79%   52, 65-70
app\modules\image_analysis\service.py                           25     10    60%   49-75
app\modules\progress_tracking\service.py                        19      2    89%   39-51
app\modules\recommendations\service.py                          31      3    90%   48, 54-55
app\modules\video_analysis\service.py                           25     10    60%   46-70
app\modules\workout_plans\service.py                            70     14    80%   40, 54, 143-154
------------------------------------------------------------------------------------------
TOTAL                                                         1560    237    85%

============================== 35 passed in 5.97s ==============================
```

### 2.2 Verificación Estricta de Tipos con Mypy

```text
> .\.venv\Scripts\mypy app/
Success: no issues found in 66 source files
```

### 2.3 Auditoría de Formato y Calidad con Ruff

```text
> .\.venv\Scripts\ruff check app/ tests/
All checks passed!
```

---

## 3. Matriz de Cobertura por Capas

1. **Capa de Dominio (100%):** Todas las entidades (`Evaluation`, `Exercise`, `WorkoutPlan`, `WorkoutProgress`, `AnalysisResults`) y sus métodos de negocio (cálculo de IMC, validación de estado de aprobación) están cubiertas al 100%.
2. **Capa de Aplicación ($\ge 85\%$ promedio):** Casos de uso de generación de rutinas, registro de avances y filtrado de restricciones.
3. **Capa de Infraestructura y Repositorios ($\ge 85\%$):** CRUD asíncrono con SQLite en memoria y PostgreSQL, inferencia PyTorch y cálculos trigonométricos 2D.
