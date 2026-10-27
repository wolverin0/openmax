<!-- doc-head: TESTBED_ENVIRONMENT_GUIDE.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](TESTBED_ENVIRONMENT_GUIDE.md) | Part 2/2
<a id="futuramax-testbed-environment-guide-2-aps--20-cpes"></a> [FuturaMAX Testbed Environment Guide: 2 APs + 20 CPEs](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#futuramax-testbed-environment-guide-2-aps--20-cpes) | <a id="1-executive-summary--the-confined-space-problem"></a> [1. Executive Summary & The Confined-Space Problem](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#1-executive-summary--the-confined-space-problem) | <a id="2-rf-physics--link-budget-calculations"></a> [2. RF Physics & Link Budget Calculations](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#2-rf-physics--link-budget-calculations) | <a id="21-free-space-path-loss-fspl-at-58-ghz"></a> [2.1 Free-Space Path Loss (FSPL) at 5.8 GHz](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#21-free-space-path-loss-fspl-at-58-ghz) | <a id="22-antenna-gain--power-overload-analysis"></a> [2.2 Antenna Gain & Power Overload Analysis](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#22-antenna-gain--power-overload-analysis) | <a id="23-far-field-fraunhofer-boundary"></a> [2.3 Far-Field (Fraunhofer) Boundary](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#23-far-field-fraunhofer-boundary) | <a id="3-comparative-testbed-architectures-where--how-to-test"></a> [3. Comparative Testbed Architectures: Where & How to Test](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#3-comparative-testbed-architectures-where--how-to-test) | <a id="31-why-a-warehouse-is-not-recommended"></a> [3.1 Why a Warehouse is NOT Recommended](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#31-why-a-warehouse-is-not-recommended) | <a id="32-academic--industry-precedents"></a> [3.2 Academic & Industry Precedents](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#32-academic--industry-precedents) | <a id="4-recommended-testbed-implementation-three-tier-plan"></a> [4. Recommended Testbed Implementation: Three-Tier Plan](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#4-recommended-testbed-implementation-three-tier-plan) | <a id="tier-1-the-bench-top-cabled-rf-matrix-immediate--primary-method"></a> [Tier 1: The Bench-Top Cabled RF Matrix (Immediate / Primary Method)](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#tier-1-the-bench-top-cabled-rf-matrix-immediate--primary-method) | <a id="tier-2-the-multi-room-over-the-air-ota-fleet-stage-3-multi-station-testing"></a> [Tier 2: The Multi-Room Over-the-Air (OTA) Fleet (Stage 3 Multi-Station Testing)](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#tier-2-the-multi-room-over-the-air-ota-fleet-stage-3-multi-station-testing) | <a id="5-network-architecture-cabling--power-infrastructure"></a> [5. Network Architecture, Cabling & Power Infrastructure](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#5-network-architecture-cabling--power-infrastructure) | <a id="51-power--cabling-infrastructure-22-radios"></a> [5.1 Power & Cabling Infrastructure (22 Radios)](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#51-power--cabling-infrastructure-22-radios) | <a id="52-vlan-segmentation--collision-avoidance"></a> [5.2 VLAN Segmentation & Collision Avoidance](TESTBED_ENVIRONMENT_GUIDE_CONTINUATION_3a9c8a8e1d_001.md#52-vlan-segmentation--collision-avoidance)

<!-- stage822a-payload-begin -->
   * Subnet: `192.168.20.0/24` dedicated exclusively to high-throughput `iperf3`, `flent`, and latency probe traffic.

---

## 6. Automated Remote Recovery (`urescue`) Without Physical Reset Press

### 6.1 The Electrical Remote Reset Mechanism

Ubiquiti 24V passive PoE injectors equipped with a reset button (e.g., `POE-24-12W-G`) do not communicate via software packets. They use a hardware DC signaling circuit:

```
[ PoE Injector ]                                             [ airMAX Radio PCB ]
+----------------------+                                    +----------------------+
|                      |  Ethernet Pins 4,5 (+24V DC)       |                      |
|  24V Power Supply    +------------------------------------> Power Regulation     |
|                      |  Ethernet Pins 7,8 (GND Return)    | (Buck Converter)     |
|                      +------------------------------------>                      |
|                      |                                    |                      |
|  Tactile Switch      |  Data Pairs Center-Tap             | Detection Circuit    |
|  [Remote Reset]      +------------------------------------> (Zener + Transistor) |
|  (Injects +18-24V DC)|                                    |         |            |
+----------------------+                                    +---------|------------+
                                                                      v
                                                              Shorts Reset GPIO
                                                              Line Directly to GND!
```

* When the reset button is energized, it applies a DC offset to the center taps of the Ethernet data transformers.
* Inside the airMAX unit (LAP-GPS, LiteBeam, Loco 5AC), a sensing circuit detects this voltage and electronically pulls the SoC reset GPIO low.
* Holding this state for **15–20 seconds after power-up** forces U-Boot to execute:
  ```text
  sleep 2; urescue
  ```
  The device enters TFTP recovery server mode at `192.168.1.20`.

### 6.2 Automating Remote Reset Without Human Intervention

To achieve 100% unattended remote recovery:

1. **Option A: USB/Network Relay on PoE Injector Tactile Switch**:
   * Solder two thin lead wires across the tactile reset button contacts on a Ubiquiti remote-reset PoE injector.
   * Connect these leads to a channel on a USB relay module (e.g., Numato 2-Channel USB Relay or ESP32 relay board).
   * **Unattended Recovery Sequence**:
     ```python
     def trigger_remote_urescue(switch_port, relay_channel):
         # 1. Power off radio
         poe_switch.set_port_power(switch_port, state=False)
         time.sleep(2)
         # 2. Close reset relay (simulate physical button hold)
         relay.close(relay_channel)
         # 3. Restore power while holding reset
         poe_switch.set_port_power(switch_port, state=True)
         # 4. Hold for 17 seconds to trigger urescue
         time.sleep(17)
         # 5. Release relay
         relay.open(relay_channel)
         # 6. Radio is now at 192.168.1.20 waiting for TFTP upload!
     ```
2. **Option B: Managed Switch Native Remote Reset**:
   * Netonix WispSwitches provide an integrated "Ubiquiti Remote Reset" software button that modulates the port DC line directly from the switch firmware.
3. **Option C: Software-Initiated Recovery via U-Boot Env (PROHIBITED by AGENTS.md §4)**:
   * > [!WARNING]
     > While `fw_setenv bootcmd "urescue"` can theoretically force U-Boot into TFTP server mode from userspace, **AGENTS.md §4 strictly protects `mtd1` (`u-boot-env`) from modifications**. Writing to bootloader environment partitions risks permanent flash corruption during power dips. **Option A (the hardware PoE-injector remote-reset relay) is the sole approved and constitutional unattended recovery mechanism.**

---

## 7. Research Tooling Integration: ScholarEngine & NotebookLM

### 7.1 ScholarEngine (`G:\_OneDrive\OneDrive\Desktop\Py Apps\wezbridge\scholar`)

The custom-built `ScholarEngine` MCP tool provides high-speed paper retrieval and semantic analysis:

* **Command-line search**:
  ```powershell
  python -m scholar.cli search "query string" --limit 5
  ```
* **Deep inspection & OpenAlex metrics**:
  ```powershell
  python -m scholar.cli inspect "<arxiv_id>"
  ```
* **Jev Semantic Gating**:
  ```powershell
  python -m scholar.cli research "<question>" --threshold 0.50
  ```
  Automatically screens out non-empirical papers and ranks candidates based on applicability to FuturaMAX.

### 7.2 NotebookLM CLI (`nlm`)

The `nlm` tool maintains the project memory and source library under notebook `ebf66972-afc2-4173-95cf-bc5ff07ceb03` ("futuraMAX", 47 sources):

* **Authenticate**:
  ```powershell
  nlm login
  ```
* **Query Sources**:
  ```powershell
  nlm query notebook ebf66972-afc2-4173-95cf-bc5ff07ceb03 "<prompt>"
  ```
* **Add New Source (e.g., fresh arXiv paper or URL)**:
  ```powershell
  nlm source add ebf66972-afc2-4173-95cf-bc5ff07ceb03 --url "<paper_url>"
  ```
<!-- stage822a-payload-end -->
