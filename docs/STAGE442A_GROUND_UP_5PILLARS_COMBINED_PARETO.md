<!-- doc-head: Stage 442A Ground-Up 5-Pillars Combined SimPy + pymoo NSGA-II Pareto Optimization (<220 lines) -->
Ejecuta la optimización multi-objetivo `SimPy` + `pymoo` (`NSGA-II`) combinando simultáneamente los **5 Pilares Ground-Up** frente a `Stock airOS 8` y `OpenWrt Stock`, demostrando dominancia de Pareto estricta en goodput agregado, latencia `p99` y tasa de falsos positivos (`0.0%`).
<!-- /doc-head -->

# Stage 442A — Ground-Up 5-Pillars Combined `SimPy` + `pymoo` (`NSGA-II`) Pareto (`mm-6005`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-6005`, `id=155408`)
- **Attribution**: `external controller`, `mac80211`, `ath10k`, `QCA firmware`
- **Simulator**: [`tools/sim/run_stage442a_ground_up_5pillars_combined_pareto.py`](../tools/sim/run_stage442a_ground_up_5pillars_combined_pareto.py)
- **Artifact**: [`artifacts/autoresearch/stage442a_ground_up_5pillars_combined_pareto.json`](../artifacts/autoresearch/stage442a_ground_up_5pillars_combined_pareto.json)

## 1. Comparación Head-to-Head: `Stock airOS 8` vs `OpenWrt Stock` vs `5-Pillar Champion`

| Arquitectura Evaluada | `airMAX AC` Goodput (`Mbps`) | `LTU SQ + Split-Freq` (`Mbps`) | Goodput Combinado (`Mbps`) | Triple-Play `p99` (`ms`) | Falsos Positivos RF (`%`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Stock airOS 8`** | `43.85` | `307.52` | `351.37` | `25.792` | `28.5%` |
| **`OpenWrt 24.10.4 Stock`** | `51.19` | `307.52` | `358.71` | `19.136` | `19.0%` |
| **`FuturaMAX 5-Pillar Ground-Up Champion`** | **`77.67`** | **`560.48`** | **`638.15`** | **`4.784`** | **`0.0%`** |

## 2. Sinergia de los 5 Pilares Ground-Up (`CONFIRMED`)
1. **Pilar 1 (`SGMT` RAM Patch)**: `PB040-CCA-AGC-OVERRIDE` (`+4 dB`) elimina bloqueos de CCA por ruido co-localizado en torre.
2. **Pilar 2 (`16-Pilot EVM` + `12.5 ns` Ranging)**: Distingue multicamino selectivo de Fresnel frente a interferencia plana.
3. **Pilar 3 (`WMI 0x9044/0x9064`)**: Escalera hardware de `4` series (`S2 1x1 CDD`) + descriptores de cola en IRAM (`0x00981a00`).
4. **Pilar 4 (`LTU SQ <= 16 CPEs + AD9361 Split-Freq`)**: Reduce el overhead de polling y separa `TX_LO != RX_LO`.
5. **Pilar 5 (`Cooperative CPE + SIMO-TX / 2x2-MRC-RX`)**: Rescata enlaces con desbalance `>= 6 dB` con `0.0%` falsos positivos.
