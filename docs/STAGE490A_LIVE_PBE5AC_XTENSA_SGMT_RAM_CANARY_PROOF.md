<!-- doc-head: STAGE490A_LIVE_PBE5AC_XTENSA_SGMT_RAM_CANARY_PROOF.md preserved document content -->
<!-- /doc-head -->



# Stage 490A — Live `PowerBeam 5AC Gen2` (`.241`) Xtensa `SGMT` RAM Bind-Mount Canary Proof (Zero Flash Touch)

## 1. Objective & Zero-Flash-Touch Safety Mechanism
- Prove live on `.241` (`FMX-PBE5AC-AP-241`, `AR9342` + `QCA9882` `168c:003c`) that `QCA988X/hw2.0` Xtensa radio firmware images (`firmware-2.bin` / `ct-firmware-2.bin` and `board.bin`) can be staged in volatile RAM (`/tmp/fmx_xtensa_canary`), bind-mounted over `/lib/firmware/ath10k/QCA988X/hw2.0`, and reloaded into the `QCA9882` target processor via `wifi reload` with **zero bytes written to SPI NOR flash (`mtd0..mtd5`)**.

---

## 2. Live Verification Results (`CONFIRMED`, attribution: `QCA firmware` / `ath10k`)
1. **Volatile RAM Staging & Bind-Mount**:
   - `/lib/firmware/ath10k/QCA988X/hw2.0/*` was copied into `/tmp/fmx_xtensa_canary/`, hashed with SHA-256, and mounted via `mount --bind /tmp/fmx_xtensa_canary /lib/firmware/ath10k/QCA988X/hw2.0`.
2. **Clean `QCA9882` Target Reload & `.242` Reassociation**:
   - Triggering `wifi reload` on `.241` booted the `QCA9882` firmware directly from the `/tmp/fmx_xtensa_canary` RAM mount, re-applied `/etc/hotplug.d/net/99-fmx-wa-universal-champion`, reassociated `.242` (`FMX-PBE5AC-STA-242`) automatically over `4addr` WDS, and passed the `1472B` full-MTU ping test.
   - Any power cycle automatically boots from the untouched SquashFS `/lib/firmware/ath10k/QCA988X/hw2.0` partition, guaranteeing 100% fail-safe experimentation for Pillar 1 (`SGMT`) Xtensa patches.

---

## 3. Artifacts & Verification
- Script: [`run_stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.py`](../tools/benchmarks/run_stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.py)
- JSON Artifact: [`stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.json`](../artifacts/autoresearch/stage490a_live_pbe5ac_xtensa_sgmt_ram_canary_proof.json)
- Test Suite: [`test_stage490a.py`](../tests/test_stage490a.py)
