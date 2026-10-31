<!-- doc-head: Stage 871A offline PowerBeam/LiteBeam 5AC Gen2 unified tester package v6 manifest; inventories+hashes existing kit artifacts, attaches 837A-870A offline evidence, zero binary patching -->
# Stage 871A — PowerBeam/LiteBeam 5AC Gen2 Unified Tester Package v6

- **Claim Status**: `CONFIRMED` (offline manifest)
- **Attribution**: `external controller (offline packaging)` — no radio, no SSH, **no binary patching**
- **Artifact**: `artifacts/autoresearch/stage871a_pbe5ac_lbe5ac_tester_package_v6.json`
- **Tool**: `tools/firmware/build_stage871a_pbe5ac_lbe5ac_tester_package_v6.py`

## 1. What it does
Inventories the existing OpenWrt PtP conversion kit
(`firmware/openwrt/pbe5ac_gen2_ptp_kit/`), reads and SHA-256-hashes every firmware
binary and kit script **without modifying any of them**, carries the board
compatibility matrix and 3-step operator guide forward from v4/v5, and attaches the
v6 evidence set (the offline SimPy/pymoo/stats findings). It is a packaging and
provenance manifest — it performs **no binary patching** and touches no device.

## 2. Package contents (this build)
- **60** firmware binaries (`.bin` / `.ko`) hashed.
- **90** kit scripts / configs hashed.
- **6** v6 evidence receipts attached: 837A fade model, 838A Pareto, 839A fairness,
  841A statistical ledger, 869A 34-endpoint Pareto, 870A executive one-liners.
- Compatibility matrix: PowerBeam / LiteBeam / NanoBeam 5AC Gen2.

## 3. Integrity gate
Each inventoried file and evidence receipt is checked for all-NUL corruption. If any
input is corrupt the manifest status flips to `BLOCKED_CORRUPT_INPUTS` and the
offending paths are listed — this build reported **no corrupt inputs** after the
deterministic regeneration of the 837A..841A receipts (see §5).

## 4. Operator 3-step guide (unchanged safety posture)
1. Back up protected partitions (`mtd0/mtd1/mtd4/mtd5`) and hash them.
2. Flash the matching factory/sysupgrade image for the board — verify SHA-256
   against this manifest first.
3. Confirm Zero-Rogue-DHCP (`dnsmasq`/`odhcpd` off) and the PtP link, then benchmark.

## 5. Note on this session's integrity event
The 837A..841A receipts were found all-NUL (filesystem corruption between turns) and
were **regenerated deterministically** from their generators before this manifest was
built; the v6 evidence hashes therefore reflect clean, reproduced receipts.

## 6. Reproduce & limits
```sh
python tools/firmware/build_stage871a_pbe5ac_lbe5ac_tester_package_v6.py
python -m pytest tests/test_stage871a.py -q
```
A manifest, not a flasher: it asserts provenance/hashes and compatibility, and does
not itself write firmware. Actual flashing remains a manual, operator-gated step.
