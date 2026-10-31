<!-- doc-head: STAGE112A_MULTIRADIO_KERNEL_AND_KNOB_MATRIX.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 112A — Bench Multi-Radio Non-PtP Live Telemetry & `mac80211.ko` Kernel/ABI Matrix (`2026-10-26`)

## 1. Executive Summary & Safety Verification (`CONFIRMED`)
- **Task ID**: `T-S112A-BENCH-MULTIRADIO-NON-PTP-LIVE-TELEMETRY-AND-KNOB-SWEEP`
- **Hard PtP & Production Isolation (`CONFIRMED`)**: `198.18.0.45` and `198.18.0.46` (`PowerBeam 5AC Gen2` PtP pair owned by Stage 105A) and Guarida backbone (`198.18.0.2`, `.200`, `.201`, `.84`) were **100% untouched** (`touched_241_or_242 = False`, `flash_writes = 0`).
- **Key Findings**:
  1. **`H1` (`LAP-120 .20 runs Linux 6.6.73 / OpenWrt 24.10.0`) — `REFUTED` (`CONFIRMED` live kernel is `Linux 6.6.110`, Attribution: `Linux` + `mac80211`)**: Live `uname -a` and `/etc/openwrt_release` on `LAP-120` (`.20`) and `NanoStation 5AC Loco` (`.250`/`.41`) prove both run **`OpenWrt 24.10.4 r28959-29397011cc` (`Linux 6.6.110`)**, matching the kernel version (`Linux 6.6.110`) of `PowerBeam 5AC Gen2` (`.241`).
  2. **`FMX-S112A-ABI-01` (`mac80211.ko` Struct Offset & `struct module` ABI Divergence Under Identical `vermagic`) — `CONFIRMED` (Attribution: `Linux` / `mac80211`)**:
     - `LAP-120` (`.20`) `/lib/modules/6.6.110/mac80211.ko` is `829,464 B` (`SHA-256: 19a8fde6...`) whereas `PBE-5AC-Gen2` (`.241`) `mac80211_rom_241.ko` (`SHA-256: 8566fb1c...`) and `mac80211_teb_6.6.110.ko` (`SHA-256: 3e3d812f...`) are `815,640 B` (`-13,824 B`).
     - Both share `32` ELF sections, identical `vermagic=6.6.110 mod_unload MIPS32_R2 32BIT `, identical `.text` size (`0x89dc0` = `564,672 B` = `141,168` MIPS instructions), and identical `.rel.text` count (`13,917` relocations at identical offsets).
     - However, `Sec 25 (.gnu.linkonce.this_module)` is `384 B` on `LAP-120` vs `352 B` on `PBE-5AC-Gen2`, `Sec 14 (.rodata)` is `33,008 B` vs `33,040 B`, `Sec 30 (.strtab)` is `25,781 B` vs `11,959 B` (`678` local symbols renamed to `_0.._677` by `rstrip.sh`), and `1,831` bytes in `.text` (`1,554` non-relocation immediate bytes + `277` relocation addend bytes) differ due to `+0x10` / `+0x20` struct field offset shifts (`0x1d8 -> 0x1e8`, `0x1178 -> 0x1198`).
     - **Safety Rule**: Never cross-copy `mac80211.ko` binaries between the `829,464 B` (`LAP-120`/`Loco5AC`) and `815,640 B` (`PBE-5AC-Gen2`) builds; always use each build's ABI-matched `ETH_P_TEB`-patched binary.
  3. **`FMX-S112A-ABI-02` (`ETH_P_TEB` `0x6558` WDS Patch `skb->data` `0xa4` vs `0xa8` Offset Shift & `aqm_write` `time_budget` Invariance) — `CONFIRMED` (Attribution: `Linux` / `mac80211`)**:
     - All function entry offsets (`ieee80211_deliver_skb` at `.text+0x033bec`) are 100% invariant between both builds, so the 21-instruction (`84 B`, `71` diff bytes vs ROM) `ETH_P_TEB` (`0x6558`) WDS bridge decapsulation patch sits at `.text+0x033c18..0x033c68` (`file 0x033c88..0x033cdb`) in both modules.
     - Critically, `struct sk_buff->data` is at offset **`0xa4`** on `LAP-120` (`.20`, `8cc900a4` / `acc900a4` at `.text+0x033c34` & `0x033c5c`) vs **`0xa8`** (`+4 B`) on `PBE-5AC-Gen2` (`.241`, `8cc900a8` / `acc900a8` in `mac80211_teb_6.6.110.ko` `3e3d812f...`). Using the `0xa4` patch on `.241` would overwrite `skb->head` (`0xa4` on `.241`) instead of `skb->data` (`0xa8`). Meanwhile, `aqm_write` at `.text+0x0120e4` (`b84a0007a8490008`) identically enforces the `2 * USEC_PER_SEC / HZ = 20,000 us` floor (`HZ=100`).

---

## 2. ELF32 MIPS32 `mac80211.ko` Comparison Matrix (`.20` `LAP-120` vs `.241` `PBE-5AC-Gen2`)

| Property / Section | `LAP-120` (`.20`) `mac80211.ko` | `PBE-5AC-Gen2` (`.241`) `mac80211_teb_6.6.110.ko` | Comparison / Verdict |
| :--- | :---: | :---: | :--- |
| **Kernel `vermagic`** | `6.6.110 mod_unload MIPS32_R2 32BIT ` | `6.6.110 mod_unload MIPS32_R2 32BIT ` | `CONFIRMED` Identical string |
| **Total File Size** | `829,464 B` (`19a8fde6...`) | `815,640 B` (`3e3d812f...`, ROM `8566fb1c...`) | `-13,824 B` (`rstrip.sh` `.strtab`) |
| **`.text` Offset & Size** | `0x70`, `0x89dc0` (`564,672 B`, `141,168` insns) | `0x70`, `0x89dc0` (`564,672 B`, `141,168` insns) | `CONFIRMED` Identical function layout |
| **`.rel.text` Relocations** | `13,917` entries | `13,917` entries (100% identical offsets) | `CONFIRMED` Identical relocation map |
| **`Sec 25 (.gnu.linkonce.this_module)`** | `384 B` | `352 B` (`-32 B`) | `CONFIRMED` Module header ABI shift |
| **`Sec 14 (.rodata)` / `Sec 30 (.strtab)`** | `33,008 B` / `25,781 B` | `33,040 B` (`+32 B`) / `11,959 B` (`-13,822 B`) | `CONFIRMED` `678` local syms `_0.._677` |
| **`.text` `0x000008` / `0x00002c`** | `lw $v0, 0x1d8($a1)` / `lw $v1, 0x1178($a1)` | `lw $v0, 0x1e8($a1)` / `lw $v1, 0x1198($a1)` | `+0x10` / `+0x20` struct field shift (`1,831` B) |
| **`ETH_P_TEB` Patch (`.text+0x033c18..0x033c68`)** | `21` instructions (`71` diff bytes vs ROM) | `21` instructions (`71` diff bytes vs ROM) | `CONFIRMED` 100% byte-identical patch |
| **`aqm_write` `time_budget` (`.text+0x0120e4`)** | `b84a0007a8490008` (`20,000 us` floor) | `b84a0007a8490008` (`20,000 us` floor) | `CONFIRMED` 100% byte-identical |

---

## 3. Non-PtP Multi-Radio Live Telemetry & Knob Stability Matrix

| Radio / Target | Switch Port & IP | OS / Kernel / SoC | Live Status | Verified Knob & Readback Summary |
| :--- | :--- | :--- | :---: | :--- |
| **`LAP-120` AP** | `gi4` (`Boca 4`), `198.18.0.43` | `OpenWrt 24.10.4` (`Linux 6.6.110`), `AR9342 + QCA9882` (`0xe8e5`) | **ONLINE (`CONFIRMED`)** | `fq_quantum=4542`, `fq_limit=2048`, `fq_memory_limit=4194304`, `AQL=1200/2400`, `aql_threshold=4000`, `eth0 BQL=4542..42392 @ 800ms`, `dev_weight_tx_bias=2`, `eth0.107 txq=64`, CAKE `diffserv4` |
| **`Loco 5AC` CPE** | `gi4` / `5180 MHz` OTA, `198.18.0.67` (`.250`) | `OpenWrt 24.10.4` (`Linux 6.6.110`), `AR9342 + QCA9882` (`0xe7fa`) | **ONLINE (`CONFIRMED`)** | `fq_quantum=1514`, `fq_limit=1024`, `fq_memory_limit=4194304`, `aql_threshold=4000`, `mac80211.ko` SHA-256 `19a8fde6...` |
| **`Rocket Prism 5AC Gen2`** | `gi6` (`Boca 6`), `198.18.0.64` | `airOS 8` `XC.v8.7.25` (`Linux 2.6.32.68`), `QCA9558 + QCA9880` (`0xe7e9`) | **ONLINE (`CONFIRMED`)** | `ath0 get_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=5` (written last per `FMX-DISC-11`), `AC*Minfree=0/16/32/48`, `enable_tx_tcp_cksum=1` |
| **`Rocket 2AC Prism`** | `gi8` (`Boca 8`), `198.18.0.65` | `airOS 8` `2XC.v8.7.11` (`Linux 2.6.32.68`), `QCA9558 + QCA988x` (`0xe2f2`) | **ONLINE (`CONFIRMED`)** | `board.sysid=0xe2f2`, `R2AC-PRISM`, L2/L3 bridge to `VLAN 1` (`198.18.0.75/24`) |
| **`LTU-Lite #1`** | `gi5` (`Boca 5`), `198.18.0.63` | `airOS LTU` `afltu.v2.4.0` (`Linux 3.14.65 SMP RT`), `Beetle + ame_ASIC0` (`0xae08`) | **ONLINE (`CONFIRMED`)** | Read-only metadata verified (`board.sysid=0xae08`, `board.qca8337n=1`, `0` AME device opens) |
| **`NanoStation` (`Boca 2` / `XW` `.21`)** | `gi2` (`Boca 2`), `198.18.0.50` (`PUBLIC_DEVICE_0044`) / `.21` | `XM.v6.1.12` on `gi2` (`1.20`) + `XW.v6.1.4` (`Linux 2.6.32.71`) `198.18.0.52` ref | **ONLINE at `198.18.0.50` (`CONFIRMED`)** | `.100.21` ARP `INCOMPLETE`; `gi2` `198.18.0.50` live (`0%` loss, TCP `[22, 80, 443]` open, `SSH-2.0-dropbear`); `XW` Champion knobs (`ath0 txqueuelen=64`, `tcp_limit_output_bytes=65536`, `AC*Minfree=0/16/32/48`) |
| **`LiteAP GPS` (`.10`)** | `198.18.0.76` (Requested) | `airOS 8` `WA.v8.7.22` (`Linux 2.6.32.68`), `AR9342 + QCA988x` (`0xe7fd`) | **OFFLINE on `.100.10` (`CONFIRMED`)** | `.100.10` ARP `INCOMPLETE` (`100%` loss from `.20` & `.253`); Grade-A control surface pinned in `research/raw/hardware/lap-gps-2026-08-08.txt` |

---

## 4. Verification & Reproducibility Receipts
- **Benchmark & ELF Dissector**: [`tools/benchmarks/run_stage112a_multiradio_kernel_and_knob_matrix.py`](../tools/benchmarks/run_stage112a_multiradio_kernel_and_knob_matrix.py)
- **JSON Artifact**: [`artifacts/autoresearch/stage112a_multiradio_kernel_and_knob_matrix.json`](../artifacts/autoresearch/stage112a_multiradio_kernel_and_knob_matrix.json)
- **Pytest Suite**: [`tests/test_stage112a_multiradio_kernel_and_knob_matrix.py`](../tests/test_stage112a_multiradio_kernel_and_knob_matrix.py) (`3/3` passed)
