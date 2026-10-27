<!-- doc-head: TESTBED_ENVIRONMENT_GUIDE.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](TESTBED_ENVIRONMENT_GUIDE.md) | Part 1/2
<a id="6-automated-remote-recovery-urescue-without-physical-reset-press"></a> [6. Automated Remote Recovery (`urescue`) Without Physical Reset Press](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#6-automated-remote-recovery-urescue-without-physical-reset-press) | <a id="61-the-electrical-remote-reset-mechanism"></a> [6.1 The Electrical Remote Reset Mechanism](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#61-the-electrical-remote-reset-mechanism) | <a id="62-automating-remote-reset-without-human-intervention"></a> [6.2 Automating Remote Reset Without Human Intervention](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#62-automating-remote-reset-without-human-intervention) | <a id="7-research-tooling-integration-scholarengine--notebooklm"></a> [7. Research Tooling Integration: ScholarEngine & NotebookLM](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#7-research-tooling-integration-scholarengine--notebooklm) | <a id="71-scholarengine-g_onedriveonedrivedesktoppy-appswezbridgescholar"></a> [7.1 ScholarEngine (`G:\_OneDrive\OneDrive\Desktop\Py Apps\wezbridge\scholar`)](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#71-scholarengine-g_onedriveonedrivedesktoppy-appswezbridgescholar) | <a id="72-notebooklm-cli-nlm"></a> [7.2 NotebookLM CLI (`nlm`)](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_002.md#72-notebooklm-cli-nlm)

<!-- stage822a-payload-begin -->
# FuturaMAX Testbed Environment Guide: 2 APs + 20 CPEs

Summary: Architectural specifications, RF propagation analysis, network segmentation, and automated remote recovery procedures for building a 22-node airMAX AC research testbed (2 APs, 20 CPEs) without physical button intervention.
Keywords: testbed, RF attenuation, Fraunhofer distance, receiver saturation, warehouse vs cabled matrix, urescue automation, PoE remote reset, VLAN architecture, ScholarEngine, NotebookLM.
Read when: Preparing, scaling, or troubleshooting the multi-station FuturaMAX laboratory environment.
Current verdict: Do NOT lease a warehouse; warehouse metal multipath distorts 802.11ac LOS channel characteristics. Use a cabled RF attenuation matrix for deterministic PHY/MAC benchwork, and a multi-room attenuated distributed layout for over-the-air (OTA) spatial and hidden-node experiments. Status: CURRENT (2026-09-26).

---

## 1. Executive Summary & The Confined-Space Problem

Scaling from a 2-radio link (1 AP + 1 CPE) to a 22-radio multi-station sector (2 APs + 20 CPEs) introduces three severe physical failure modes if attempted carelessly inside a single room:

1. **Receiver Saturation & LNA Clipping**: High-gain antennas (16–23 dBi) at 1–3 meters distance deliver signal levels greater than `+0 dBm` directly into the radio front-end. The QCA988x low-noise amplifier (LNA) saturates above `-20 dBm`, destroying Error Vector Magnitude (EVM), triggering 100% packet retries, and causing the rate controller to collapse to MCS 0.
2. **Fraunhofer Far-Field Violation**: Dish and sector antennas do not form their designed radiation patterns, beamwidths, or cross-polarization isolation in the radiative near-field (Fresnel zone). Radios must be separated by at least the Fraunhofer distance ($R_{far} \ge 2D^2 / \lambda \approx 5\text{ to }8\text{ meters}$).
3. **The Warehouse Fallacy**: Moving to a metal warehouse is worse than a lab room. Metal walls and roofs create extreme multipath reflections and delay spread (Rayleigh fading), which contradicts the outdoor fixed-wireless channel (predominantly Rician fading with strong Line-of-Sight). Furthermore, wall reflections prevent creating genuine "hidden nodes" because every radio hears every other radio via reflections.

---

## 2. RF Physics & Link Budget Calculations

### 2.1 Free-Space Path Loss (FSPL) at 5.8 GHz

$$\text{FSPL (dB)} = 20\log_{10}(d\text{ in km}) + 20\log_{10}(f\text{ in MHz}) + 32.44$$

At $f = 5800\text{ MHz}$:

| Physical Distance | Path Loss (FSPL) |
|---|---|
| **1 meter** | **47.7 dB** |
| **3 meters** | **57.3 dB** |
| **10 meters** | **67.7 dB** |
| **30 meters** | **77.3 dB** |
| **100 meters** | **87.7 dB** |
| **1 kilometer** | **107.7 dB** |
| **5 kilometers** | **121.7 dB** |

### 2.2 Antenna Gain & Power Overload Analysis

Target Hardware Parameters:
* **LiteAP GPS (LAP-GPS)**: $17\text{ dBi}$ sector antenna.
* **LiteBeam 5AC Gen2 (LBE-5AC-Gen2)**: $23\text{ dBi}$ dish reflector.
* **NanoStation 5AC (NS-5AC)**: $16\text{ dBi}$ integrated panel.
* **NanoStation Loco 5AC (Loco5AC)**: $13\text{ dBi}$ integrated panel.

**Unattenuated Benchtop Scenario (3 meters, Stock Radios)**:
* AP TX Power: $+17\text{ dBm}$
* AP Antenna Gain: $+17\text{ dBi}$ (EIRP = $+34\text{ dBm}$)
* CPE Antenna Gain (LiteBeam): $+23\text{ dBi}$
* Path Loss at 3m: $-57.3\text{ dB}$
* **Received Power ($P_{rx}$)**:
  $$P_{rx} = 17\text{ dBm} + 17\text{ dBi} - 57.3\text{ dB} + 23\text{ dBi} = \mathbf{+0.7\text{ dBm}}$$

> [!CAUTION]
> A $+0.7\text{ dBm}$ input signal will severely overdrive the QCA988x receiver. The maximum linear input level for 256-QAM (MCS 8/9) is $-25\text{ dBm}$ to $-30\text{ dBm}$. Normal outdoor operating targets are **$-55\text{ dBm}$ to $-65\text{ dBm}$**. An unattenuated bench will fail immediately.

### 2.3 Far-Field (Fraunhofer) Boundary

The antenna radiation pattern only stabilizes beyond distance $R_{far}$:

$$R_{far} \ge \frac{2 D^2}{\lambda}$$

Where $\lambda = \frac{c}{f} = \frac{3 \times 10^8}{5.8 \times 10^9} \approx 0.0517\text{ m}$ (5.17 cm):

* **LiteBeam Dish** ($D \approx 0.358\text{ m}$): $R_{far} \ge \frac{2 \times 0.128}{0.0517} \approx \mathbf{4.95\text{ meters}}$
* **LiteAP 120/GPS Sector** ($D \approx 0.45\text{ m}$): $R_{far} \ge \frac{2 \times 0.2025}{0.0517} \approx \mathbf{7.83\text{ meters}}$

If antennas are positioned closer than 5–8 meters, mutual coupling, side-lobe distortion, and phase cancellation invalidate any directional beamforming or spatial measurements.

---

## 3. Comparative Testbed Architectures: Where & How to Test

### 3.1 Why a Warehouse is NOT Recommended

| Factor | Warehouse Facility | Cabled RF Matrix (Bench) | Multi-Room Building |
|---|---|---|---|
| **RF Multipath** | Severe delay spread from corrugated steel walls & concrete. | Zero multipath (ideal clean baseline). | Controlled attenuation via drywall/brick. |
| **Hidden Nodes** | Impaired (signals bounce off steel ceilings). | 100% controllable via matrix isolation. | Realistic (isolated rooms block LOS). |
| **Reproducibility** | Low (moving forklifts, temperature shifts). | **100% Deterministic (Golden Reference)**. | High (static building structures). |
| **Cost & Overhead** | High lease, heating, 50m cable runs. | Low (SMA cables, splitters, attenuators). | Zero (uses existing office/home footprint). |
| **Rapid Iteration** | Slow (walking to adjust antennas). | **Instant (software/step attenuators)**. | Moderate. |

### 3.2 Academic & Industry Precedents

1. **Rutgers ORBIT Testbed**:
   * Installed 400 802.11 nodes in a 20m × 20m grid. Encountered severe mutual interference and receiver overload. Solved it by operating at minimum TX power, adding programmable AWGN noise injection, and using RF shielding baffles between node rows.
2. **Commercial WISP Testbeds (OctoScope / Spirent / Mini-Circuits)**:
   * Do not use warehouses. They place 16–32 CPE devices in shielded rack enclosures connected through **programmable coaxial attenuator matrices** and Wilkinson power dividers. Every subscriber link distance (100m to 10km) is simulated purely by adjusting RF attenuation in 0.5 dB steps.
3. **MIT IteRate (arXiv:2605.02542)**:
   * Operated 58 nodes distributed across an academic building over multiple floors and rooms. This naturally exploited drywall/concrete floor attenuation (15–30 dB per partition) to establish diverse SNR, near-far client distributions, and real hidden nodes.

---

## 4. Recommended Testbed Implementation: Three-Tier Plan

### Tier 1: The Bench-Top Cabled RF Matrix (Immediate / Primary Method)

* **Objective**: Reproducible, interference-free evaluation of aggregation (`htt_max_amsdu_ampdu`), rate-masks (`ratemask-CT`), AQL queue limits, and soft scheduling (Campaigns C1–C5).
* **Setup**:
  * Radios remain on the bench or rack.
  * Disconnect antenna elements or connect directly via SMA coax cables.
  * Insert a **30 dB or 40 dB fixed RF attenuator** (50-ohm, DC–6 GHz, SMA male/female) on each chain.
  * Use a passive RF power combiner/splitter (e.g., Mini-Circuits 1:8 or 1:16 Wilkinson divider) to combine CPE signals into the AP port.
  * Add inexpensive USB or manual step attenuators (e.g., PE4302 digital step attenuator boards, $12 each, 0–31.5 dB range) to independently adjust individual CPE link budgets from $-50\text{ dBm}$ (near client) to $-85\text{ dBm}$ (edge client).

### Tier 2: The Multi-Room Over-the-Air (OTA) Fleet (Stage 3 Multi-Station Testing)

* **Objective**: Near-far fairness (Campaign C6), interference classification (C7), and multi-station TDMA/CSMA contention.
* **Setup**:
  * **Remove the LiteBeam Dish Reflectors**: Operate LiteBeam units using **only the bare feed horn**. Removing the dish drops antenna gain from $+23\text{ dBi}$ to $\approx +5\text{ dBi}$ (an immediate 18 dB reduction).
  * **Lock TX Power to Minimum**: Configure `txpower` on all radios to `-4 dBm` to `0 dBm`.
  * **Physical Distribution Across Rooms**:
    * AP located in central hub.
    * 5 CPEs in adjacent room (drywall attenuation $\approx 4\text{ dB}$).
    * 5 CPEs in far room (brick/concrete wall attenuation $\approx 15–20\text{ dB}$).
    * 5 CPEs down the corridor / opposite wing.
    * 5 CPEs behind metal door / basement (simulating extreme edge / hidden node).
  * This layout creates a realistic link SNR distribution (MCS 0 through MCS 9) without requiring a warehouse.

---

## 5. Network Architecture, Cabling & Power Infrastructure

### 5.1 Power & Cabling Infrastructure (22 Radios)

* **Do NOT use 22 individual wall-wart PoE injectors**: This requires 44 Ethernet patches, 22 AC plugs, and prevents programmatic power cycling.
* **Required Hardware**:
  * **Managed 24-Port 24V Passive PoE Switch**:
    * e.g., Ubiquiti EdgeSwitch 24 500W, TOUGHSwitch/EdgePoint, Netonix WispSwitch WS-26-400-IDC, or MikroTik CRS328-4C-20S-4S+RM (configured for 24V passive PoE).
  * **Programmatic Power Cycling**:
    * Allows the Linux test runner to power-cycle any individual radio on demand via SSH or SNMP (`snmpset` or CLI port power toggle).

### 5.2 VLAN Segmentation & Collision Avoidance

When Ubiquiti hardware resets to factory defaults or enters recovery mode, it defaults to **`192.168.1.20`**. If 20 CPEs reset on a flat Layer-2 switch, an unrecoverable IP collision storm occurs.

**VLAN Isolation Architecture**:

```
Switch Port Mapping:
Port 1: Linux Test Server (Trunk: VLAN 10, 20)
Port 2: AP 1 (LAP-120 / LAP-GPS) -> Untagged VLAN 10 (IP: 192.168.10.11) [LAP-120 for OpenWrt; LAP-GPS for stock airOS]
Port 3: AP 2 (LAP-120 / LAP-GPS) -> Untagged VLAN 10 (IP: 192.168.10.12)
Ports 4–23: CPE 1 .. 20     -> Isolated Private VLANs / Port Isolation
```

1. **Port Isolation / Private VLANs**: Enable port isolation on ports 4–23 so CPEs cannot communicate with each other at Layer 2 over Ethernet; they can only communicate upstream to the AP and Linux controller.
2. **Management Subnet (VLAN 10)**:
   * Subnet: `192.168.10.0/24`
   * Static mappings configured by MAC address:
     * AP 1: `192.168.10.11`
     * AP 2: `192.168.10.12`
     * CPE 1–20: `192.168.10.101` through `192.168.10.120`
3. **Data Subnet (VLAN 20)**:
<!-- stage822a-payload-end -->
