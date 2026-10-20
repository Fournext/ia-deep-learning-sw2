# Registro de Problemas Conocidos y Limitaciones Técnicas (Known Issues)

Este documento centraliza los impedimentos, riesgos identificados y limitaciones de la plataforma para conocimiento compartido de todos los agentes.

---

## 1. Limitaciones de la Versión Actual de Google Antigravity

### ISSUE-001: Ausencia de Herramienta Nativa `invoke_subagent` en la Sesión Activa
- **Descripción:** En la sesión interactiva actual de Google Antigravity, el catálogo de herramientas expuesto al asistente incluye utilidades de manipulación de archivos (`write_to_file`, `replace_file_content`), ejecución de comandos de terminal (`run_command`, `manage_task`), búsqueda web (`search_web`) y subagente de navegador (`browser_subagent`), pero **no expone una herramienta directa llamada `invoke_subagent` o `define_subagent`**.
- **Impacto:** Las definiciones de subagentes en `.agents/agents/*.md` son reconocidas e indexadas por el motor de Antigravity (a nivel de IDE, CLI y selección en chat UI), pero no pueden ser instanciadas programáticamente mediante una llamada de herramienta automática dentro de esta conversación.
- **Mitigación Oficial:**
  1. Los archivos se configuran rigurosamente con la sintaxis oficial (`name`, `description`, `mainAgent`, `subagent`, `tools`).
  2. En el Antigravity IDE o Antigravity 2.0 Desktop, el usuario o el agente orquestador puede invocar los subagentes seleccionándolos en el dropdown de agentes o utilizando la CLI `agy --agent <nombre-agente>`.
  3. Durante la orquestación en chat, el agente orquestador emite las instrucciones con el contexto exacto y asume la personalidad/rol correspondiente de acuerdo con los handoffs estandarizados sin simular herramientas inexistentes.

---

## 2. Riesgos Técnicos del Microservicio de IA (Para Fase 2)

### ISSUE-002: Inferencia de MediaPipe y Dependencias C++ en Contenedores Slim
- **Descripción:** Las librerías de OpenCV (`opencv-python` vs `opencv-python-headless`) y MediaPipe requieren bibliotecas compartidas del sistema operativo (`libgl1-mesa-glx`, `libglib2.0-0`). En imágenes Docker `python:3.11-slim`, estas librerías deben instalarse explícitamente en el `Dockerfile`.
- **Mitigación:** `devsecops-mlops-engineer` debe utilizar `opencv-python-headless` e instalar las dependencias de sistema requeridas en la etapa de construcción.

### ISSUE-003: Cold-Start en Recomendaciones
- **Descripción:** Nuevos usuarios que no tienen registros previos de entrenamiento en el ERP no pueden beneficiarse de filtrado colaborativo puro.
- **Mitigación:** `recommendation-engineer` diseñará un árbol de decisión heurístico basado en arquetipos iniciales y objetivos declarados hasta que el usuario acumule al menos 5 sesiones de entrenamiento evaluadas.
