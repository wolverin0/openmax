<!-- doc-head: Stage 762A AF-LTU (Beetle) IRQ 52 Coalescing, NAPI Budget & Bridge Zero-Rogue-DHCP Guard (<200 lines) -->
`Stage 762A` construye el auditor read-only `firmware/ltu_safe_kit/fmx_ltu_irq_napi_and_dhcp_guard.sh` que audita el aislamiento de `IRQ 52` en `CPU1`, la proporción `NAPI` `480/48` y la ausencia total de servidores DHCP (`udhcpd`/`dnsmasq`/`odhcpd`) en puentes `br0` sin tocar `/dev/ame*`.
<!-- /doc-head -->

# Stage 762A — `AF-LTU` (`Beetle`) IRQ 52, NAPI Budget & Zero-Rogue-DHCP Guard (`mm-9b58`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-9b58`, `id=155477`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_irq_napi_and_dhcp_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_irq_napi_and_dhcp_guard.sh)
- **SHA-256**: `adc2fa88aa76caad574f7a7b4373821f7bffba75252105eeef38c52884ac9380`
- **Artifact**: [`artifacts/autoresearch/stage762a_ltu_irq_napi_and_dhcp_guard.json`](../artifacts/autoresearch/stage762a_ltu_irq_napi_and_dhcp_guard.json)

## 1. Invariantes `IRQ 52`, `NAPI 480/48` e Higiene L2 `Zero-Rogue-DHCP` (`CONFIRMED`)
| Parámetro / Auditoría | Valor / Invariante | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `/proc/irq/52/smp_affinity` | `2` (`CPU1`) | Garantiza que el datapath DMA de `ame_asic0` corra exclusivamente en `CPU1` (`hardware`). |
| `netdev_budget` / `dev_weight` | `480` / `48` | Proporción exacta `10:1` de rodajas `NAPI` por ciclo `NET_RX_SOFTIRQ` (`Linux`). |
| `rogue_dhcp_procs` (`udhcpd`/`dnsmasq`) | `0` | Garantiza que un CPE/AP `LTU` en puente transparente L2 jamás inyecte ofertas DHCP en la LAN (`Linux`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
