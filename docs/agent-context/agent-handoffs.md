# Protocolo y Registro de Transferencias entre Agentes (Agent Handoffs)

Este documento contiene el estándar de entrega formal que debe cumplir cada agente al completar una tarea, así como la plantilla oficial para el traspaso de información (*Handoff*) entre roles.

---

## 1. Plantilla Oficial de Entrega de Tarea (Task Handoff Standard)

Cada vez que un subagente finaliza una tarea y la presenta a `system-architect`, debe estructurar su reporte siguiendo este formato:

```markdown
# REPORTE DE ENTREGA DE TAREA: [ID-DE-LA-TAREA] - [TÍTULO CORTO]

## 1. Metadatos de la Tarea
- **Identificador:** [Ej. TASK-DEV-03]
- **Descripción:** [Resumen de 1-2 párrafos del trabajo encomendado y alcance completado]
- **Agente Responsable:** [deep-learning-engineer / recommendation-engineer / etc.]
- **Fecha de Entrega:** [YYYY-MM-DD]
- **Estado Propuesto:** [READY_FOR_REVIEW]

## 2. Archivos Creados o Modificados
- `[ruta/al/archivo_1.py]`: [Propósito del archivo y componentes agregados]
- `[ruta/al/archivo_2.py]`: [Propósito del archivo y componentes agregados]
- `[tests/test_archivo_1.py]`: [Pruebas asociadas]

## 3. Decisiones Técnicas y Justificación
- **Patrones de Diseño Aplicados:** [Ej. Factory, Strategy, Repository]
- **Decisiones Relevantes:** [Explicar por qué se eligió cierta estructura o parámetro técnico]
- **Cumplimiento de Contratos:** [Confirmar adherencia a docs/agent-context/module-contracts.md]

## 4. Pruebas Ejecutadas y Evidencias Verificables
- **Comando de Test:** `pytest tests/unit/test_pose_analysis.py -v --cov=src/cv`
- **Resultado:** `12 passed, 0 failed in 0.45s`
- **Cobertura Obtenida:** `89%`
- **Logs de Terminal Relevantes:**
  ```text
  [Pegar output literal del comando de prueba o benchmark]
  ```

## 5. Hallazgos, Corner-Cases y Problemas Detectados
- [Detallar comportamientos anómalos encontrados durante las pruebas y cómo fueron resueltos]
- [Limitaciones conocidas que deban ser consideradas por otros agentes]

## 6. Dependencias Pendientes o Próximos Pasos
- [Indicar si se requiere trabajo adicional de backend, base de datos o revisión especial]

## 7. Solicitud de Revisión Externa
- [ ] Solicitar validación a `qa-testing-engineer`
- [ ] Solicitar auditoría a `technical-auditor`
```

---

## 2. Registro Histórico de Handoffs

### Handoff #001: Configuración Inicial del Ecosistema Multiagente
- **Identificador:** `TASK-SETUP-01` a `TASK-SETUP-04`
- **Agente Responsable:** `system-architect`
- **Fecha:** 2026-10-19
- **Resumen:** Creación y configuración completa de los 7 agentes especializados, reglas globales y modulares en `.agents/rules/` y `AGENTS.md`, y el repositorio de contexto compartido en `docs/agent-context/`.
- **Estado:** `READY_FOR_REVIEW` (Validado localmente).
