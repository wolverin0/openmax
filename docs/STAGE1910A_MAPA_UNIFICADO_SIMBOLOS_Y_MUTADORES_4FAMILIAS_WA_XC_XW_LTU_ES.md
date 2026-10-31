<!-- doc-head -->
*STAGE1910A — mapa unificado de símbolos y mutadores en las cuatro familias WA, XC, XW y LTU*
# STAGE 1910A — Mapa de 4 familias

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Se analizaron **19 módulos** de cuatro familias con el mismo censo: símbolos, reubicaciones, cadenas de `.rodata`, secciones `__param` y presencia de interfaces.
- Etiquetas `CONFIRMED`, `INFERRED` y `UNKNOWN`. Identificadores de CPE con prefijo `cpe_`; no se usan apellidos.

## 1. Stage 1908A — las cuatro familias
- `CONFIRMED`: WA y XC comparten los mismos cuatro módulos y los mismos totales: **3239** símbolos y **1339** cadenas cada una. XW tiene **2320** símbolos y **1056** cadenas en tres módulos. LTU suma **4920** símbolos y **1267** cadenas en ocho módulos AME.
- `CONFIRMED`: la matriz cubre **24** tokens de superficie de control en las cuatro familias.
- `CONFIRMED`: el **núcleo común** son **11** tokens: `ack`, `airtime`, `dfs`, `distance`, `duty`, `gps`, `qos`, `rate`, `retry`, `slot` y `txpower`.
- `CONFIRMED`: solo **1** token es exclusivo de una familia: `arq`, únicamente en XW. Es coherente con el TDMA propietario del M5.
- `CONFIRMED`: **10** tokens aparecen en dos o tres familias: `aggr`, `ampdu`, `chainmask`, `country`, `spectral`, `station`, `vap`, `voip`, `wds` y `wmm`.
- `INFERRED`: que un token exista no prueba la misma semántica. `airtime` en AME y en airOS puede medir cosas distintas.

## 2. Stage 1908A — interfaces
| Interfaz | WA | XC | XW | LTU |
| :--- | :---: | :---: | :---: | :---: |
| ioctl | 19 | 19 | 14 | 12 |
| procfs | 5 | 5 | 6 | 3 |
| sysctl | 7 | 7 | 7 | 0 |
| sysfs | 1 | 1 | 0 | 6 |
| debugfs | 0 | 0 | 0 | 5 |
| firmware message | 155 | 155 | 1 | 0 |
| `sch_*.ko` en el rootfs | 5 | 5 | **0** | 11 |

- `CONFIRMED`: solo **ioctl** y **procfs** aparecen en las cuatro familias.
- `CONFIRMED`: **XW no trae ningún `sch_*.ko`**, mientras LTU trae **11** y WA y XC traen **5** cada una.
- `CONFIRMED`: LTU es la única familia con **debugfs** y la que más **sysfs** usa.
- `INFERRED`: la ausencia de `sch_*` en XW sugiere que ese rootfs no ofrece qdisc por módulo; no prueba que no haya qdisc compilado dentro del kernel.

## 3. Stage 1909A — mutadores seguros en ejecución
- `CONFIRMED`: **8** mutadores clasificados: ioctl, procfs, sysctl, sysfs, debugfs, mensaje de firmware, parámetro de módulo y qdisc.
- `CONFIRMED`: solo **1** es común a las cuatro familias: **ioctl** (339 knobs del catálogo en la frontera airOS).
- `CONFIRMED`: **4** son específicos de familia: `sysctl` (WA/XC/XW, 68 knobs), `sysfs` (LTU con 20 knobs y presencia binaria también en WA/XC), `module_param` (WA/XC/XW con 30 knobs) y `tc_qdisc` (WA/XC/LTU, 3 knobs de frontera Linux).
- `CONFIRMED`: **3** son solo binarios: `procfs` (en las cuatro familias, sin knob en el catálogo), `debugfs` (solo LTU) y `firmware_message` (WA/XC/XW; los 106 knobs de esa vía pertenecen a la frontera QCA 10.1, no a airOS ni a AME).
- `CONFIRMED`: **0** mutadores quedan solo en el catálogo.
- `CONFIRMED`: los mutadores seguros en ejecución en las cuatro familias son **ioctl** y **procfs**.
- `CONFIRMED`: conjuntos seguros por familia: WA y XC `{ioctl, procfs, sysctl, sysfs, tc_qdisc}`; XW `{ioctl, procfs, sysctl}`; LTU `{debugfs, ioctl, procfs, sysfs, tc_qdisc}`.
- `INFERRED`: la superficie universal y reversible se reduce a dos interfaces. Todo lo demás exige conocer la familia antes de tocar un knob.

## 4. Stage 1911A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate`.
- `CONFIRMED`: ambos recibos llevan los identificadores en `pillar_e_memory_master_claim_id`.

## 5. Lo que no se prueba
- `UNKNOWN`: si un knob concreto de una interfaz presente es escribible. La presencia de la interfaz no es permiso.
- `UNKNOWN`: los permisos de sysfs y debugfs; no se leyó ningún bit de modo.
- `UNKNOWN`: si la migración a OpenWrt conserva la misma superficie de mutadores.
- `UNKNOWN`: que `airtime` o `qos` midan lo mismo en AME y en airOS.
- `UNKNOWN`: los `sch_*` del kernel de XW, que no está en este conjunto.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1908A` | `tools/re/extract_stage1908a_4family_wa_xc_xw_ltu_unified_knob_symbol_map.py` y su recibo |
| `1909A` | `tools/re/reconcile_stage1909a_4family_safe_runtime_mutators.py` y su recibo |
| `1911A` | `tools/verify/record_stage1911a_memorymaster_ingest.py` y su recibo |
| `1912A` | `tests/test_stage1908a_to_1913a_suite.py` |
| `1913A` | `tools/verify/verify_stage1913a_wave145_opencode_gate.py` y la compuerta de la wave |
