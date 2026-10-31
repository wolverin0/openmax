<!-- doc-head: Indice de perillas por familia de equipo (W354, v2 con titulos de ronda vinculados a perillas canonicas): cada comando/ruta/valor cambiable con como se cambia, rango, si se probo (campana, stage, ventanas), mejor valor, efecto medido y valor en produccion, armado solo con evidencia existente (catalogo 571, ledger 1256A 548 filas, kits 99-fmx, rosetta 175A, tabla W353, lecturas del daemon); conteos por familia y como regenerarlo -->
Que cubre: donde esta el indice, como leerlo, cuantas perillas hay por familia y que significa cada columna.
Estado: fusion offline de evidencia existente. Ninguna medicion nueva. Lo que no consta dice "sin dato".
Tabla navegable: artifacts/2026-10-29-indice-perillas.html. Datos maquina: artifacts/knob_index/knob_index.json.
Leer cuando: antes de proponer, probar o desplegar un cambio de parametro en cualquier radio.
<!-- /doc-head -->
# Indice de perillas por equipo

## 1. Como se usa

- **Abrir** `artifacts/2026-10-29-indice-perillas.html`. Hay una tabla por familia, cada una con su buscador.
- **Regenerar** despues de un ledger, un kit o un catalogo nuevo: `python tools/research/build_knob_index.py`. Es determinista: con las mismas entradas da los mismos bytes.
- **Test:** `python -m pytest -q tests/test_build_knob_index.py`.

## 2. Columnas

| Columna | De donde sale |
| :-- | :-- |
| perilla | nombre normalizado; se juntan las variantes (`ap_`/`sta_`, prefijo de familia, `net.core.`) |
| como se cambia | superficie del catalogo (ruta, selector, acceso), comando de los kits, interfaz del ledger, ruta de la tabla W353 y equivalente OpenWrt de la rosetta 175A |
| rango y default | `encoding_domain` del catalogo, o rango/default de W353 |
| probado? | filas del ledger 1256A: campana, stage, ronda, ventanas, veredicto, antes -> probado y el titulo de la ronda como contexto |
| mejor valor | valor `tuned` del ultimo CHAMPION; si no hay, el del ultimo KEPT |
| efecto medido | metrica y % registrados en el ledger, con su alcance |
| valor en produccion | ultima lectura nativa VALID del daemon before/after para cada nodo de produccion |
| fuente | archivo y puntero de cada dato |

**Ojo con el alcance del efecto:** `whole_champion_profile` es el efecto del perfil champion completo, no de esa perilla sola. `round_variant` si es una ronda que cambio esa perilla.

## 3. Conteos por familia

| Familia | Total | Probadas | Con efecto medido | Sin probar | Con valor en produccion |
| :-- | --: | --: | --: | --: | --: |
| PtP OpenWrt (LiteBeam / PowerBeam 5AC) | 220 | 76 | 60 | 144 | 8 |
| PtMP OpenWrt (LAP-120 / LiteAP AC + CPE) | 284 | 116 | 96 | 168 | 6 |
| airOS WA / XC / XW | 414 | 75 | 53 | 339 | 0 |
| LTU | 78 | 69 | 65 | 9 | 0 |

**Version 2 (W354 P1b):** las filas del ledger que son titulos de ronda o comandos ya no quedan como perillas sueltas. Cada una se cuelga de cada perilla canonica que nombra (por ejemplo `AC_BK aql_txq_limit=500/1000 vs ...=300/600` va a `aql_txq_limit` con antes 500/1000 y probado 300/600). El titulo queda como contexto.
- **Lado de control:** el lado que dice stock/defaults; si no hay, el que nombra el kit o champion instalado; si no hay ninguno, el izquierdo. La regla usada queda escrita en cada prueba.
- **Sin valor legible:** si un lado no trae un valor, queda `sin dato`.
- **Pruebas combinadas:** los titulos que no nombran ninguna perilla canonica quedan como "prueba combinada": 17 en PtP, 11 en airOS y 3 en LTU.
- **Version 1:** 245/96/58/149 (PtP), 284/116/96/168 (PtMP), 423/81/59/342 (airOS) y 80/70/66/10 (LTU). Las probadas bajan porque cada titulo contaba como una perilla probada aparte.

- **Repetidos entre familias:** las perillas de ath10k-ct y mac80211 del catalogo aparecen en las dos familias OpenWrt, porque el hardware y el firmware son los mismos.
- **Kits fuera del indice:** los kits OpenWrt para XC/XW (72 escrituras) no entran en ninguna de las cuatro tablas. Estan contados en el JSON (`kits_outside_families_rows`).
- **Produccion:** solo hay lecturas nativas para los nodos OpenWrt que observa el daemon (paneles, CPE y PtP-Colo). Para airOS y LTU no consta nada.

## 4. Fuentes (solo lectura)

1. `orchestration/autoresearch/firmware_knob_candidates.json`: 571 perillas que existen.
2. `artifacts/verification/stage1256a_complete_tuned_knobs_production_ledger.json`: 548 filas de 4 campanas.
3. `firmware/openwrt/*/99-fmx-*`: 31 kits; se leen sus `sysctl -w`, `echo > /sys|/proc`, `iw set`, `uci set` y `tc qdisc`.
4. `artifacts/autoresearch/stage175a_571knob_airos_to_openwrt_rosetta_stone.json` y `artifacts/autoresearch/wave353_ptp_knob_settability.json`.
5. `tools/observability/telemetry.db`, abierta en solo lectura: ultima fila OBSERVED por nodo.

## 5. Limites

- **Nombres:** la union es por nombre normalizado. Dos perillas distintas con el mismo ultimo segmento dentro de una familia quedan en la misma fila, con sus dos formas de cambio listadas.
- **Ledger:** el ledger 1256A registra lo que dicen los recibos. Sus propias limitaciones (`claim_limits`, `gaps`) siguen valiendo.
- **IPs:** los comandos del ledger traen IPs; en el indice quedan como `x.x.x.N`.
- **Fuera del indice:** el resultado de AQL de la W353 todavia no esta en el ledger, asi que no aparece aca.
