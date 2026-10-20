# Estándares de Codificación y Calidad de Software

Este conjunto de reglas aplica a cualquier archivo de código Python desarrollado en el microservicio.

## 1. Guía de Estilo y Formato
- **Formateador y Linter:** Ruff es la herramienta estándar para comprobación estática y formateo.
- **Longitud de línea:** Máximo 100 caracteres.
- **Imports:** Ordenados alfabéticamente y agrupados (estándar, terceros, locales) mediante `isort` (integrado en Ruff).
- **Idioma:** Nombres de variables, funciones y clases en inglés técnico (ej. `calculate_knee_angle`, `generate_routine_candidates`). Documentación y docstrings en español claro y profesional.

## 2. Tipado Estricto (Type Annotations)
- Ninguna función pública o método puede omitir anotaciones de tipo en sus parámetros y valor de retorno.
- Usar tipos modernos de Python 3.10+ (`int | None`, `list[str]`, `dict[str, Any]`).
- Todo el código debe superar la verificación de `mypy --strict`.

## 3. Pruebas Automatizadas
- Cada nuevo módulo debe nacer acompañado de su archivo correspondiente en `tests/`.
- Meta ineludible: 85% de cobertura sobre la capa de aplicación y dominio.
- Los tests deben tener aserciones deterministas sobre casos de éxito, casos de error y casos límite (corner cases).
