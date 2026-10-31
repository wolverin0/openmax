<!-- doc-head: Wave 113 (1716A-1718A) sintesis ES: nota #623 une Waves 109 (WMI/regdomain/channel-bounds RE estatico), 110 (plan colo 5GHz NO ejecutable + blueprint Panel3 + auditoria Panel1 en vivo read-only) y 112 (RE XC PtP/LTU pm_dbg + reconciliacion de knobs); feed del Command Center :8787 a 1536A..1721A; scholar INCONCLUSIVO por rate-limit (no es negativo); SIN campeon nuevo; una fila readonly_audit honesta en results.tsv -->
# Reporte ejecutivo - Nota #623: WMI/regdomain, colo 5GHz, Panel3 y XC/LTU

**Wave 113 - Etapas 1716A-1718A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron las Waves 109, 110 y 112, mas la auditoria en vivo read-only del post-heal de Panel1
(stage1674A), en la nota evergreen #623. El feed del Command Center :8787 se amplio a la banda
1536A..1721A. El titular honesto: estas waves son ingenieria inversa, reconciliacion estatica y PLANES
por etapas, mas una auditoria en vivo de solo lectura. **No hay campeon de trafico nuevo.**

## Etapa 1716A - sintesis (nota #623)

**Wave 109 (RE estatico):** stage1692A (CONFIRMED_STATIC_BINARY) desensamblado de opcodes WMI y
regdomain de ath10k (61 exports de ath10k_core; el valor 6035 MHz NO aparece como u16 en la imagen de
firmware). stage1693A (CONFIRMED_STATIC_DATA) reconciliacion WMI 4addr + limites de canal sobre 571
knobs estaticos.

**Wave 110 (2 planes estaticos + 1 auditoria en vivo read-only):** stage1698A (CONFIRMED_STATIC_PLAN)
retune de 5 GHz paso-0 del PtP-Colo + plan paso-1, **NO ejecutable** (3 pasos bloqueados, hybrid_ready
false, 0 ejecutables). stage1699A (CONFIRMED_STATIC_PLAN) blueprint de migracion por etapas de Panel3
(6 CPEs). stage1674A (LIVE_HARDWARE_READ_ONLY_PRODUCTION) auditoria de telemetria del post-heal de
Panel1 (3 CPEs cpe_41/cpe_223/cpe_80) + auditoria de Panel3: solo lectura, 0 escrituras de config, sin
A/B, por lo tanto sin objetivo de perdida medido.

**Wave 112 (RE estatico):** stage1710A (CONFIRMED_STATIC_BINARY) RE de XC PtP xmit + LTU pm_dbg en 5
modulos (atpc 7 / noack 6 / pm_dbg 1 hits). stage1711A (CONFIRMED_STATIC_DATA) reconciliacion de knobs
XC/LTU binario-a-vivo (mapeo estatico, pendiente de confirmacion en vivo).

**recall-first:** 5 de 6 consultas con aciertos (regdomain canal 4, limites de canal 4addr 20, colo
5GHz 1, migracion Panel3 5, knob XC/LTU 20; opcode WMI regdomain 0). La sintesis se ingreso como nota
#623 (evergreen); el vault paso a 623 notas. Recibo
`artifacts/autoresearch/stage1716a_hyperresearch_wmi_colo_panel3_xc_ltu_note623_receipt.json`.

## Etapa 1716A - scholar (chequeo unico suave, INCONCLUSIVO honesto)

Se hizo UN chequeo suave de un principio atomico de dominio regulatorio, con 4 s de espacio para evitar
el rate-limit de Wave 108. El sondeo de liveness del motor funciono (P=0.96, source=live), pero el unico
scholar_verify_claim devolvio FETCH_FAILED (ReadTimeout): la ruta de verify sigue rate-limited. Por eso
la pata scholar queda INCONCLUSIVA (fetch degradado), NO un negativo; la sintesis se apoya en el recall
y en los recibos propios de RE/datos/plan.

## Etapa 1717A - banda del feed a 1536A..1721A

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero con la banda ampliada; los 7
recibos aparecen con su propia clase de evidencia (binario/datos/plan estatico + uno live read-only). Se
agrego UNA fila honesta a results.tsv para la auditoria en vivo de Panel1: commit
`s1674a_panel1_postheal_ro`, dominio D4_GUARIDA_84_OTA, status `readonly_audit`, objetivos NA (read-only,
sin A/B), descripcion que aclara que NO es un campeon de trafico. El champion D4 existente (keep) no se
toca. Recibo `artifacts/autoresearch/stage1717a_command_center_1721a_band_refresh_receipt.json`.

## Limites y advertencias (honestas)

- **Sin campeon de trafico nuevo** esta wave: todo es RE/datos/plan estatico + una auditoria en vivo de
  solo lectura. El retune del colo NO es ejecutable (3 pasos bloqueados); la migracion de Panel3 es un
  blueprint.
- **scholar INCONCLUSIVO** por rate-limit (ReadTimeout), no un negativo; motor vivo (P=0.96).
- Gaps abiertos: el u16 de 6035 MHz en firmware y la gramatica de escritura WMI 4addr/regdomain siguen
  sin resolver.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI
  (HTTP 200 + bytes servidos) y balance de etiquetas. El daemon :8787 (hot-reload) se atrasa bajo
  escrituras rapidas; se dejo un restart limpio al cierre para reflejar la banda 1721.

## Que sigue (abierto, decision del operador)

- Ejecutar el cutover en vivo del PtP-Colo (hoy bloqueado), la migracion de Panel3 y la reconciliacion
  en vivo de los knobs XC/LTU.
- Re-correr scholar cuando afloje el rate-limit para grounding real.

Recibos: `stage1716a_hyperresearch_wmi_colo_panel3_xc_ltu_note623_receipt.json`,
`stage1717a_command_center_1721a_band_refresh_receipt.json`, `stage1721a_wave113_opus2_gate.json`.
