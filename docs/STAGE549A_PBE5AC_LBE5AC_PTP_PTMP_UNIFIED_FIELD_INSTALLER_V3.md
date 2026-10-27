<!-- doc-head: Stage 549A PBE-5AC-Gen2 & LBE-5AC-Gen2 PtP/PtMP Unified Field Installer v3 -->
Documents the one-command field installer (`fmx_pbe5ac_lbe5ac_field_installer_v3.sh`) for `PowerBeam 5AC Gen2` (`0xe3e5`) and `LiteBeam 5AC Gen2` (`0xe4e5`), integrating `mtd0/1/5` preflight verification, Staged Hybrid OTA conversion, and `VHT40` (`24.83 Mbps`, `0%` loss) tuning.
<!-- /doc-head -->

# Stage 549A — `PBE-5AC-Gen2` (`0xe3e5`) & `LBE-5AC-Gen2` (`0xe4e5`) PtP/PtMP Unified Field Installer v3

- **Epistemic Status**: `CONFIRMED` (Backed by live `.241 <-> .242` `PBE-5AC-Gen2` bench proof in `Stages 425A–429A` & `487A–488A`)
- **Attribution**: `Linux` · `mac80211` · `ath10k` · `QCA firmware`
- **Field Installer**: [`fmx_pbe5ac_lbe5ac_field_installer_v3.sh`](../firmware/openwrt/common/fmx_pbe5ac_lbe5ac_field_installer_v3.sh) (`SHA-256: 519535c39796174f...`, strict `LF`)
- **JSON Receipt**: [`stage549a_pbe5ac_lbe5ac_ptp_ptmp_unified_field_installer_v3.json`](../artifacts/autoresearch/stage549a_pbe5ac_lbe5ac_ptp_ptmp_unified_field_installer_v3.json)

---

## 1. Supported Hardware & Validated Performance Envelope

| Board ID | Radio Model | Dish / Antenna | Fraunhofer Limit | Verified `VHT40` Goodput | `1472 B` Full-MTU Loss | VoIP (`64 B`) Under Load |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **`0xe3e5`** | **`PowerBeam 5AC Gen2` (`PBE-5AC-Gen2`)** | `420 mm` (`25 dBi`) | `6.20 m` | **`24.83 Mbps`** (`16.74 DL / 8.09 UL`) | **`0.0%`** (`8/8`) | **`0.0%` loss** (`p50=2.55 ms`) |
| **`0xe4e5`** | **`LiteBeam 5AC Gen2` (`LBE-5AC-Gen2`)** | `23 dBi` Reflector | `4.85 m` | **`24.83 Mbps`** (`16.74 DL / 8.09 UL`) | **`0.0%`** (`8/8`) | **`0.0%` loss** (`p50=2.55 ms`) |

---

## 2. Three-Gate Field Installation Workflow

1. **Gate 0 — `preflight` (`mtd0`, `mtd1`, `mtd5` Read-Only Hash Backup)**:
   - Computes SHA-256 hashes of `/dev/mtd0ro` (`u-boot`), `/dev/mtd1ro` (`u-boot-env`), and `/dev/mtd5ro` (`ART` caldata: `0x1000` 2.4 GHz management + `0x5000` 5 GHz `QCA9882`) into `/tmp/fmx_caldata_backup/`.
2. **Gate 1 — Staged 100% Remote OTA Conversion (`Step 1 Hybrid -> Step 2 Full OpenWrt`)**:
   - Enables `allow_80211=1` + `op_mode=0` on the local `airOS 8` AP first, converts the remote STA over-the-air with the `45 s` Non-DFS / `120 s` DFS rollback watchdog, verifies `0%` `1472 B` loss, and only then converts the local AP.
3. **Gate 2 — `apply` (Runtime v3 Champion Knobs)**:
   - Sets `aql_txq_limit = 1550 / 2100`, `htt_max_amsdu_ampdu = "3 64"`, `ani_enable = 1`, and unlocks `VHT80` STA capabilities so `VHT40` (`40 MHz`) negotiates cleanly.
