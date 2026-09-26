# Contributing to FuturaMAX

Thank you for your interest in contributing to **FuturaMAX**! Whether you are a WISP operator, a wireless researcher, a Linux kernel developer, or an AI agent engineer, your insight and validation are welcome.

---

## 1. Our Core Principle: The Evidence Hierarchy

FuturaMAX is an experimental R&D project. We do not accept unsupported claims or narrative speculation. Every contribution must respect the project's evidence hierarchy:

1. **Measurements on exact hardware revisions** (Grade A).
2. **Direct source code and commits** for the exact software build.
3. **Official hardware, vendor, or regulatory documentation**.
4. **Peer-reviewed real-hardware research** (IEEE, USENIX, ACM).
5. **Preprints with reproducible code, data, and methodology**.
6. **Simulations and community reports**.

### Mandatory Claim Tagging
When opening issues, proposing hypotheses, or submitting PRs, explicitly label all non-trivial technical assertions:
* `[CONFIRMED]`: Verified directly by reproducible physical test or source inspection.
* `[INFERRED]`: Plausible based on established literature, awaiting hardware test.
* `[UNKNOWN]`: Unmeasured or open question.
* `[REFUTED]`: Disproven by measurement or source audit.

---

## 2. Ways to Contribute

### A. Hardware Inventory & Board Signatures
If you operate Ubiquiti airMAX AC hardware (LiteAP GPS, LAP-120, LiteBeam 5AC Gen2, NanoStation 5AC, Loco 5AC, Rocket Prism 5AC), run our read-only inventory collector:
```sh
python tools/inventory/collect.py --host <radio_ip> --user <ssh_user>
```
*Sanitize any private credentials or customer MACs before submitting.* This helps us expand [docs/HARDWARE_MATRIX.md](docs/HARDWARE_MATRIX.md) with exact SoC versions, bootloader revisions, and radio firmware signatures.

### B. Hypothesis Review & Literature Challenges
Review our Architectural Decision Records in [docs/DECISIONS.md](docs/DECISIONS.md) or our verified paper catalogue in [knowledge/REAL_HARDWARE_LITERATURE.md](knowledge/REAL_HARDWARE_LITERATURE.md).
* Did we misinterpret an ath10k WMI/HTT control hook?
* Is there a published benchmark or dataset that contradicts our inferences?
* Submit an issue or PR with direct citations and reproducible methods.

### C. Testbed & Bench Replication
If you have an isolated bench or outdoor testbed:
1. Replicate our bootloader recovery qualification ([FMX-0002 Runbook](safety/recovery/FMX-0002_recovery_runbook.md)).
2. Run our reproducible OpenWrt 24.10.4 build and report `ath10k` debugfs behavior.
3. Submit raw traces, iperf3/flent logs, or spectral FFT captures.

---

## 3. Hard Safety & Ethical Boundaries

All contributions must strictly adhere to the project's safety boundaries (from [AGENTS.md](AGENTS.md)):

* **No Regulatory Bypasses**: Never submit code or documentation that disables DFS radar detection, exceeds legal EIRP power limits, or bypasses country-code regulatory limits.
* **No Flash Corruption**: Never write to bootloaders (`mtd0`), bootloader environments (`mtd1`), calibration/ART partitions (`mtd5`), or factory MAC storage.
* **Lab Radios Only**: Never test or flash production radios carrying live customer traffic.
* **No Proprietary Code Infringement**: Do not post proprietary, copyrighted vendor source code or decompiled binary trees. Our research is clean-room and based on public GPL releases and open-source Linux kernel interfaces.

---

## 4. Submitting Pull Requests

1. Keep PRs focused on a single technical question, driver hook, or documentation improvement.
2. When proposing an architectural change, include an update to `docs/DECISIONS.md` following the existing `D-XXXX` format.
3. Update `docs/CURRENT_STATE.md` to reflect new milestones or findings.
4. Ensure all documentation includes clear markdown file links using the repository's relative paths.
