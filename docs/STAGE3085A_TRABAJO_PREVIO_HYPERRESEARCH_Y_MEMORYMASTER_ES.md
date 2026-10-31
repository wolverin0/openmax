<!-- doc-head: Stage 3085A (W425) ES: related_docs() del orquestador ahora tambien busca en las notas e indices de hyperresearch (research/notes, research/index) y en MemoryMaster (scope project:futuramax, FTS5 solo lectura) y devuelve cada coincidencia con su fuente (docs/, research/, mm:); presupuesto de 0,9 s para las fuentes nuevas; tests -->
Que cubre: que busca, como puntua, cuanto tarda y como se prueba.
Estado: offline y solo lectura (archivos del repo y memorymaster.db en modo ro). No cambia el estado del orquestador.
Codigo: tools/orchestration/fmx_master_orchestrator.py (related_docs, _research_hits, _memorymaster_hits). Tests: tests/test_orchestrator_auto_dispatch.py.
Leer cuando: al tocar como el orquestador arma la lista de trabajo previo de cada despacho.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 3085A: trabajo previo desde docs, hyperresearch y MemoryMaster (W425)

## 1. Que devuelve

- **docs/**: como antes, el doc-head con al menos 2 terminos del objetivo; hasta `limit` (6).
- **research/**: notas de `research/notes` (titulo, tags y resumen del frontmatter, no el cuerpo) y entradas `- [[id]] — ...` de `research/index`.
  - Una sola coincidencia por id de nota.
  - Apunta a la nota si existe; si no, a la linea del indice (`research/index/_index.md#id`).
  - Hasta `extra_limit` (3), con al menos 2 terminos compartidos.
- **mm:<id>**: claims de MemoryMaster del scope `project:futuramax`.
  - FTS5 en `memorymaster.db` abierta solo lectura (la misma ruta que el hook de AGY), orden bm25.
  - Excluye archivados, reemplazados y en conflicto.
  - Hasta 3, con al menos 2 terminos.
  - Una base ausente o rota da 0 resultados, nunca un error.
- Las mismas cadenas van al prompt de despacho y al contrato `--my-task`.

## 2. Velocidad (medida, procesos nuevos)

- 6 corridas: 0,407, 0,156, 0,14, 0,109, 0,11, 0,14 s.
- Las fuentes nuevas tienen un plazo de 0,9 s desde el inicio de la llamada. Si docs/ ya lo consumio, se saltean y docs/ se devuelve completo.
- Medido por separado en caliente: docs 0,13 s, research 0,06 s, MemoryMaster 0,03 s.
- La primera corrida en frio puede pasar de 1 s solo por la lectura de los 1807 doc-heads. En la medicion de la suite paso una vez (1,2 s); el resto queda debajo de 0,7 s.

## 3. Ejemplo

Objetivo "core RB1100AHx4 rx-drop office UTP probe origin sidecar": docs/STAGE3074A_ORIGEN_SONDAS_EN_EL_CORE_ES.md, docs/STAGE3083A_INFORME_ANTES_DESPUES_POR_MIGRACION_ES.md, docs/STAGE3053A_SIDECAR_E2E_COLAS_Y_RECLAMOS_ES.md, docs/STAGE3073A_PTP_PERDIDA_ES_DEL_CAMINO_AL_CORE_ES.md, docs/STAGE1249A_OPUS55_INPLACE_TOPOLOGY_AND_SG01_HARDENING.md, docs/STAGE2108A_AUDITORIA_SOFTNET_TIME_SQUEEZE_SNMP_GUARIDA_Y_KEEPALIVE_INTVL_ES.md, research/index/_index.md#softnet_time_squeeze_and_keepalive_intvl_telemetry_note636, mm:<memorymaster-id>, mm:<memorymaster-id>, mm:<memorymaster-id>.
- `mm:<memorymaster-id>` es el hallazgo de W414: el UTP sano y la perdida en el RB1100.
- En las 6 corridas aparecieron 36 docs, 14 research y 18 claims.

## 4. Tests (13 passed in 2.28s)

- Notas e indice con fuente y sin duplicados; el cuerpo de la nota no se busca.
- MemoryMaster solo del scope del proyecto: sin archivados ni otros scopes, y con 2 terminos minimo.
- Una base ausente o rota da 0 resultados.
- Con plazo 0 solo vuelve docs/.
- La llamada real con las tres fuentes tarda menos de 1 s.
