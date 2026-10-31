<!-- doc-head: GUIA_UNIVERSAL_LTU_SAFE_CHAMPION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Guía Universal: LTU Safe Linux Champion v2 (`rc.poststart_ltu_safe_champion.sh`)

## 1. Propósito y Garantía de Seguridad (`CONFIRMED` — Atribución: `Linux` / `hardware`)
- **Script Universal v2**: `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` (SHA-256 `e7f7662474a073051ab06601f5c9064340852875881339d98b645f54b5eb176e`).
- **Compatibilidad**: Toda la familia `AF-LTU` (`LTU-Lite 0xae08`, `LTU-LR 0xae07`, `LTU-Pro 0xae02`, `LTU-XR 0xae09`, `LTU-Instant 0xae0b`, `LTU-Rocket`) sobre `Linux 3.14.65 SMP PREEMPT RT`.
- **Regla de Oro de Seguridad**: **CERO accesos a nodos de caracteres `/dev/ame*`**. Todo el tuning opera exclusivamente sobre el kernel Linux (`sysctl`, `/proc/irq`, `RPS`/`XPS`, `BQL`, `bridge` y `tc fq_codel`).

## 2. Resumen de Ganadores Rondas 1 a 4 (`Stages 185A, 188A, 218A, 247A`)
| Ronda | Subsistema | Parámetros Ganadores Verificados en `198.18.0.63` |
| :---: | :--- | :--- |
| **R1 (`S185A`)** | SMP IRQ & RPS/XPS | `IRQ 52` (`ame_asic0`) + `ath0` RPS/XPS en `CPU1` (`2`); `IRQ 63` (`eth0`) + `eth0` RPS/XPS en `CPU0` (`1`) |
| **R1/R2 (`S188A`)** | BQL & Colas NIC | `eth0`/`ath0`/`br0`/`br1` `tx_queue_len = 256`, `byte_queue_limits/limit_max = 36288` B |
| **R2/R3 (`S218A`)** | NAPI, Memoria y TCP | `netdev_budget = 480`, `dev_weight = 48`, `somaxconn = 512`, `optmem_max = 65536`, `vm.min_free_kbytes = 4096`, `tcp_limit_output_bytes = 65536` |
| **R4 (`S247A`)** | TCP Pacing, Bridge & AQM | `tcp_pacing_ca_ratio = 120`, `ss_ratio = 200`, `multicast_snooping = 0`, `ageing_time = 30000`, `nf_conntrack_max = 16384`, `fq_codel` (`quantum 1514 target 2500us interval 50000us ecn`) |

## 3. Instalación No Destructiva (RAM Primero, Persistencia Opcional)
1. **Prueba en RAM (con reversión automática al reiniciar)**:
   - Copiar `rc.poststart_ltu_safe_champion.sh` a `/tmp/rc.poststart_ltu_safe_champion.sh` y ejecutar `sh /tmp/rc.poststart_ltu_safe_champion.sh`.
2. **Persistencia en `/etc/persistent/rc.poststart` (tras validar telemetría)**:
   - Instalar en `/etc/persistent/rc.poststart`, `chmod +x /etc/persistent/rc.poststart` y ejecutar `cfgmtd -w -p /etc/`.
