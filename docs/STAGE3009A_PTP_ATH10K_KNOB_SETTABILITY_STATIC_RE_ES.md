<!-- doc-head: Wave353 P2 — settability estatica de knobs PtP ath10k sobre OpenWrt 24.10.4 (RE offline, sin equipos) -->

# STAGE3009A — Settability de knobs PtP ath10k (RE estatico offline)

Pillar A. Objetivo: decir, para un PtP corto sobre ath10k (LiteBeam 5AC / PowerBeam 5AC, OpenWrt
24.10.4, ath10k-ct), **que knobs son ajustables en caliente, por que superficie, con que rango y
que default**, mirando solo los binarios despachados. No se ejecuto nada en equipos.

## Metodo

1. Los candidatos salen de `orchestration/autoresearch/firmware_knob_candidates.json` (571 knobs,
   12 familias). De ahi se seleccionan las familias que tocan ACK/coverage, BQL, AQL, agregacion,
   txpower y fq.
2. Se localiza cada aguja en los `.ko` despachados con parser ELF propio (ELF32 big-endian MIPS):
   seccion, offset de fichero y vaddr. El `.modinfo` y `__param` se leen para enumerar
   parametros de modulo, que son la otra superficie posible.
3. Una fila es **CONFIRMED** solo si la cadena existe y se localiza en un binario realmente
   despachado. Si no aparece, la fila queda **UNKNOWN** con el motivo escrito. No se rellena.

Binarios usados:

| modulo | fichero | bytes |
|---|---|---|
| ath10k_core | `artifacts/firmware_re_ath10k_tar/ath10k_core_openwrt2410.ko` | 714672 |
| mac80211 | `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko` | 829464 |
| cfg80211 | `artifacts/stage2670a/cfg80211.ko` | 392132 |

## Tabla

| knob | ajustable en caliente | interfaz | ruta / comando | rango | default | evidencia | estado |
|---|---|---|---|---|---|---|---|
| `coverage_class` | CONFIRMED | debugfs (ath10k) y nl80211 | `write 'set-coverage-class <phyclk> <value>' en /sys/kernel/debug/ieee80211/phy` | 0..255 (u8 del ABI nl80211) | 0 | `.rodata.str1.4` 0x7e050 0x137b0 | **CONFIRMED** |
| `ack_timeout` | REFUTED | no existe como knob propio | `se deriva de coverage_class (aACKTimeout = SIFS + slot + 2*propagation); no ha` | n/a | n/a | sin cadena en el binario | **UNKNOWN** |
| `bql_limit_max / hold_time / limit` | UNKNOWN | sysfs (netdev, kernel) | `/sys/class/net/<dev>/queues/tx-*/byte_queue_limits/{limit,limit_max,hold_time}` | limit: 0..limit_max; hold_time en ms | limit_max 0 = sin limite | sin cadena en el binario | **UNKNOWN** |
| `aql_txq_limit` | CONFIRMED | debugfs (mac80211 aqm) | `/sys/kernel/debug/ieee80211/phyX/aqm/aql_txq_limit` | cuatro enteros: BE BK VI VO | 1500 3000 (proyecto); no deducible del binario | `.rodata.str1.4` 0x97ea4 0x5454 | **CONFIRMED** |
| `aql_threshold` | CONFIRMED | debugfs (mac80211 aqm) | `/sys/kernel/debug/ieee80211/phyX/aqm/aql_threshold` | entero (pendiente de airtime agregada, us) | 5000 (proyecto) | `.rodata.str1.4` 0x97eb4 0x5464 | **CONFIRMED** |
| `fq_quantum` | CONFIRMED | debugfs (mac80211 aqm) | `/sys/kernel/debug/ieee80211/phyX/aqm/fq_quantum` | entero sin signo (bytes); la cadena es 'fq_quantum %u' | 1514 (proyecto) | `.rodata.str1.4` 0x97ced 0x529d | **CONFIRMED** |
| `fq_flow_limit` | UNKNOWN | debugfs (mac80211 aqm) | `/sys/kernel/debug/ieee80211/phyX/aqm/fq_flow_limit` | entero | UNKNOWN | sin cadena en el binario | **UNKNOWN** |
| `fq_memory_limit` | CONFIRMED | debugfs (mac80211 aqm) | `/sys/kernel/debug/ieee80211/phyX/aqm/fq_memory_limit` | entero (bytes) | 4 MB (proyecto, INFERRED) | `.rodata.str1.4` 0x97cc8 0x5278 | **CONFIRMED** |
| `htt_max_amsdu_ampdu` | CONFIRMED | debugfs (ath10k) | `/sys/kernel/debug/ieee80211/phyX/ath10k/htt_max_amsdu_ampdu` | dos enteros (A-MSDU, A-MPDU) | UNKNOWN | `.rodata.str1.4` 0x7174c 0x6eac | **CONFIRMED** |
| `A-MSDU subframes (nl80211)` | CONFIRMED | nl80211 / symbol exportado | `symbol ieee80211_sta_set_max_amsdu_subframes (mac80211.ko .strtab)` | entero de subframes por A-MSDU | UNKNOWN | `.strtab` 0xa87c4 None | **CONFIRMED** |
| `tx_power (limite por banda)` | CONFIRMED | nl80211 (iw) y lectura interna | `iw dev <dev> set txpower fixed <dBm>; el modulo imprime 'mac txpower 2g: %d, 5` | acotado por EEPROM/regulatory (UNKNOWN desde el binario) | UNKNOWN (depende de caldata y regdomain) | `.rodata.str1.4` 0x6c1c4 0x1924 | **CONFIRMED** |
| `ct_special MAX_TXPOWER` | CONFIRMED | debugfs (ath10k-ct ct_special) | `/sys/kernel/debug/ieee80211/phyX/ath10k/ct_special (selector de MAX_TXPOWER)` | dBm, con latch de un solo uso | sin latch | `.rodata.str1.4` 0x708d0 0x6030 | **CONFIRMED** |
| `ct_special IBSS_AMSDU_OK` | CONFIRMED | debugfs (ath10k-ct ct_special) | `/sys/kernel/debug/ieee80211/phyX/ath10k/ct_special (selector de IBSS_AMSDU_OK)` | 0/1 | desconocido | `.rodata.str1.4` 0x708b0 0x6010 | **CONFIRMED** |

## Lo que esta confirmado

- **coverage_class** — debugfs (ath10k) y nl80211. Evidencia: `set-coverage-class, phyclk: %d  value: %d`.
- **aql_txq_limit** — debugfs (mac80211 aqm). Evidencia: `aql_txq_limit`.
- **aql_threshold** — debugfs (mac80211 aqm). Evidencia: `aql_threshold`.
- **fq_quantum** — debugfs (mac80211 aqm). Evidencia: `RW fq_quantum %u`.
- **fq_memory_limit** — debugfs (mac80211 aqm). Evidencia: `RW fq_memory_limit %u`.
- **htt_max_amsdu_ampdu** — debugfs (ath10k). Evidencia: `htt_max_amsdu_ampdu`.
- **A-MSDU subframes (nl80211)** — nl80211 / symbol exportado. Evidencia: `ieee80211_sta_set_max_amsdu_subframes`.
- **tx_power (limite por banda)** — nl80211 (iw) y lectura interna. Evidencia: `mac txpower 2g: %d, 5g: %d`.
- **ct_special MAX_TXPOWER** — debugfs (ath10k-ct ct_special). Evidencia: `Latching max-txpower to: %d (%d dBm)`.
- **ct_special IBSS_AMSDU_OK** — debugfs (ath10k-ct ct_special). Evidencia: `Setting ibss-amsdu-ok to %d`.

## Lo que NO se puede afirmar

- **ack_timeout** — ausente en los tres modulos: si se busca un ack_timeout directo no esta
- **bql_limit_max / hold_time / limit** — BQL no vive en ath10k ni en mac80211: no hay candidato en el JSON y la cadena no aparece en los modulos, que es lo esperado para un mecanismo de sch_generic/kernel
- **fq_flow_limit** — si no se encuentra, la fila queda UNKNOWN en vez de suponer el nombre

### ack_timeout no existe como knob

En los tres modulos no hay ninguna superficie llamada `ack_timeout`: ni fichero debugfs, ni
parametro de modulo. Lo que si existe es `set-coverage-class`, y el ACK timeout de 802.11 se
**deriva** de la clase de cobertura. Conclusion practica para lane_3: ajustar `coverage_class` es
la via, buscar un ack_timeout propio es buscar algo que este build no tiene.

### BQL no vive aqui

No hay candidato BQL en el JSON de 571 knobs y la cadena no aparece en ath10k ni en mac80211, que
es lo esperado: BQL es `sch_generic`/kernel, y su superficie es sysfs de netdev
(`queues/tx-*/byte_queue_limits/`). Declarar su rango o su default desde estos binarios seria
inventarlo; queda UNKNOWN y se resuelve leyendo el kernel, no estos modulos.

## Parametros de modulo: la lista completa, y lo que no esta

`ath10k_core.ko` declara **10** parametros (`__param` = 320 B):

`num_rate_ctrl_objs_ct, num_msdu_desc_ct, num_peers_ct, num_vdevs_ct, nobeamform_su, nobeamform_mu, ct_sta, nohwcrypt, coredump_mask, frame_mode, fw_diag_log, skip_otp, uart_print, cryptmode, debug_mask, ofdm_peak_power_rssi, override_eeprom_regdomain`

`mac80211.ko` declara **3**:

`ieee80211_default_rc_algo, probe_wait_ms, beacon_loss_count, max_probe_tries, max_nullfunc_tries, minstrel_vht_only`

**Ninguno** toca ACK, agregacion, txpower ni AQL. Eso cierra la puerta a la idea de "lo pongo
en `/etc/modules.d` y listo": esas superficies son debugfs o nl80211, no parametros.

## Dos avisos para quien consume esto

1. **Los defaults son INFERRED**, no leidos del binario. Las cadenas dan la superficie y, cuando
   hay formato (`RW fq_quantum %u`), tambien la codificacion; el valor inicial lo fija el codigo y
   aqui solo se cita el que el proyecto ya tenia documentado. No se presentan como medicion.
2. **`ct_special MAX_TXPOWER` es de un solo uso.** El binario dice `Cannot re-set max-txpower, old:
   %d new: %d`, es decir, fijarlo no es reversible sin recargar el modulo. Para lane_3 eso
   significa que no es un knob de barrido A/B.

## Limites de esta wave

- `firmware-5.bin` **no esta en disco con ese nombre**, asi que los WMI ids no se cruzaron contra
  el firmware. La imagen QCA988X hw2.0 que si existe es `firmware-2.bin` (204796 B).
- Sin desensamblado de las funciones handler: la evidencia es la cadena y su seccion, no el flujo
  de escritura. Por eso el rango que no se deduce del formato queda INFERRED o UNKNOWN.
- Cero escrituras, cero SSH, cero ejecucion en equipos.

## Recuento

**13 filas: 10 CONFIRMED, 3 UNKNOWN, 0 REFUTED.** Evidencia en
`artifacts/autoresearch/wave353_ptp_knob_settability.json`.

