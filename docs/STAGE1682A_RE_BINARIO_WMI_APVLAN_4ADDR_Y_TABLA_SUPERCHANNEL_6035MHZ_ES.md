<!-- doc-head -->
*STAGE1682A — RE binario del camino 4addr AP_VLAN/WMI y del límite regd frente a 6035 MHz*
# STAGE 1682A — 4addr AP_VLAN/WMI y límite de 6035 MHz

## 0. Método
- **100% estático y offline**: sin SSH y sin acceso a radio (`ssh_connections=0`, `radio_access=0` registrados en el recibo).
- Etiquetas: `CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`.

## 1. Stage 1680A — superficie 4addr / AP_VLAN
- `CONFIRMED`: la imagen WA aporta 3 módulos; `mac80211.ko` expone **145** símbolos y `ath10k_core.ko` **61**.
- `CONFIRMED`: entre los exports de `mac80211.ko` hay **4** nombres con `wds`/`ap`/`vif`; entre los de `ath10k_core.ko` hay **0** con `peer`/`key`/`vdev` (los símbolos internos están borrados, así que los comandos WMI no son consultables por nombre).
- `CONFIRMED`: `wpad` de WA contiene **4** aciertos de los tokens 4addr/WDS; `hostapd` de XC contiene **0**.
- `CONFIRMED`: `firmware-2.bin` (204.796 B) contiene **0** aciertos para los once tokens WMI. Es esperable: los opcodes son números compilados, no cadenas.
- `INFERRED`: el camino `nl80211_set_wds_sta -> mac80211 -> ath10k -> WMI` es coherente con la superficie medida, pero **no** se prueba con un call graph.
- `UNKNOWN`: la carrera dual-bind de netifd. Es una propiedad de ordenación en ejecución; **ningún** artefacto binario la demuestra y no se afirma.
- `REFUTED`: que el firmware contenga evidencia textual de `PEER_ASSOC` o `INSTALL_KEY`.

## 2. Stage 1680A — límite regd y 6035 MHz
- `CONFIRMED`: `regulatory.db` mide **6.232 B** y viaja en la imagen.
- `REFUTED`: el sondeo por dword little-endian. **0** de los límites (5170, 5250, 5330, 5490, 5650, 5725, 5850, 5925, 6035, 6425) aparece como `u32` crudo, incluidos límites que necesariamente existen. El método es inválido, no la tabla.
- `CONFIRMED`: la versión RGDB **no** es un `u32` en `0x10`; este recibo no la re-deriva y cita el decode estructurado de `1405A`.
- `CONFIRMED` (citado de `1405A`): la tabla global de 5 GHz tiene **55** registros y cubre **5650–6425 MHz**. Por tanto **6035 MHz cae dentro** de la banda global.
- `UNKNOWN`: si 6035 MHz es **usable**. Depende de los flags por registro (DFS / no-IR) y de la potencia declarada, que `1405A` publicó registro a registro pero este recibo no re-evalúa.
- `INFERRED`: el límite práctico no lo pone el firmware (sin tabla de canales) sino la base regulatoria más la lista del driver.

## 3. Stage 1681A — reconciliación con el catálogo de 571 knobs
- `CONFIRMED`: el catálogo contiene exactamente **571** knobs.
- `CONFIRMED`: coincidencias por token: `wds` **7**, `dfs` **3**, y **0** para `4addr`, `ap_vlan`, `vlan`, `regd`, `6035` y `superchannel`.
- `INFERRED`: el camino 4addr/AP_VLAN está representado en el catálogo solo de forma tangencial (7 knobs con `wds`), y el límite de 6035 MHz no es un knob: es una cuestión regulatoria.
- `REFUTED`: que exista un knob dedicado a 6035 MHz o a supercanal en este catálogo.

## 4. Stage 1685A — compuerta
- Corre `enforce_5pillar_research_gate.py` sobre los dos recibos y exige `compliant = true`.
- Se ejecuta dos veces (medición y confirmación).

## 5. Abierto
- `UNKNOWN`: la carrera netifd y el bloqueo a MCS0 NSS1 del enlace descendente; sin telemetría no se puede atribuir.
- `UNKNOWN`: usabilidad de 6035 MHz según flags por registro.
- `UNKNOWN`: mapeo exacto de opcodes WMI a partir de nombres, imposible con símbolos internos borrados.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1680A` | `tools/re/extract_stage1680a_4addr_apvlan_wmi_and_superchannel_re.py` + recibo |
| `1681A` | `tools/re/extract_stage1681a_apvlan_and_regd_knob_reconciliation.py` + recibo |
| `1682A` | este documento (menos de 200 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1683A..1685A` | `tests/test_stage1680a_to_1685a_suite.py` y `tools/verify/verify_stage1685a_wave107_opencode_gate.py` |
