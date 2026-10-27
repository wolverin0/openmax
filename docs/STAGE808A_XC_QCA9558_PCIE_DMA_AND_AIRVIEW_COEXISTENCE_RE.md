<!-- doc-head: STAGE808A_XC_QCA9558_PCIE_DMA_AND_AIRVIEW_COEXISTENCE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 808A — XC (QCA9558) PCIe DMA and AirView coexistence

- **Receipt**: [`artifacts/autoresearch/stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json`](../artifacts/autoresearch/stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json)
- **Tool**: [`tools/re/dissect_stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.py`](../tools/re/dissect_stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. AirView is userspace, not a driver

| Probe | Result |
| :--- | :-: |
| `airview` / `AirView` / `AIRVIEW` in **3 XC kernel modules** | **0** |
| `bin/airview` present | **yes — 8,647 bytes** |
| `airview` naming itself inside that binary | **60** |

**`REFUTED`**: `airview_in_kernel = 0`.
**`CONFIRMED`**: `airview_is_userspace = 1`.

This is the **same architecture Stage 823A found for airMagic**: the analysis product is a daemon, and
the kernel only supplies raw samples. A 8,647-byte binary naming itself 60 times is a **thin client**,
not a spectrum engine — the engine is `ubntspecd` (47,192 bytes).

So "AirView coexistence" is **not a kernel arbitration problem**. It is userspace clients contending
for the spectral path that `ubntspecd` serves.

## 1. The daemon set on XC

| Daemon | Bytes | Self-name hits |
| :--- | :-: | :-: |
| `ubntspecd` | **47,192** | 17 |
| `provmode` | 14,291 | 29 |
| **`airview`** | **8,647** | **60** |
| `dfsprescan` | 4,186 | 0 |

**`CONFIRMED`**: `daemons_present = 4`, `daemons_readable = 4` — all four are **real binaries**, none
is a zero-byte stub.

`dfsprescan` at 4,186 bytes with **0** self-name hits is worth noting: it is the smallest and does not
name itself, so its identity is inferred from its path rather than its content.

## 2. PCIe and DMA are split across layers — and that split is the finding

| Module | Bytes | `pci`+`PCI` | `dma`+`DMA` |
| :--- | :-: | :-: | :-: |
| **`XC:umac.ko`** | 2,358,768 | **62** | 14 |
| **`XC:ath_dev.ko`** | 287,216 | 21 | **43** |
| `XC:ath_hal.ko` | 360,896 | 3 | 6 |

**`CONFIRMED`**: `dma_in_device_layer = 1`, `pci_in_umac = 1`.

- **DMA mass is in `ath_dev.ko`** (43 tokens): descriptor rings, buffer management, the per-frame
  work.
- **PCIe mass is in `umac.ko`** (62 tokens): bus enumeration and configuration.

That matters when tracing a stall: a **PCIe enumeration** failure and a **DMA descriptor** failure
live in **different modules**, and a search confined to one will miss the other.

## 3. `coexist` appears exactly once

**`CONFIRMED`**: `coexist_token_hits = 1`, in `umac.ko`. `coexist_is_thin = 1`.

A single coexistence reference in 2.36 MB is **thin**, and it is exactly what the userspace finding
predicts: if two analysis clients arbitrate in the daemon, the kernel needs only a passing mention.

**`REFUTED`**: `airview_kernel_arbitration_recovered = 0`. There is no kernel-side arbitration
between AirView clients, because none is named.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| AirView is a kernel symbol | **REFUTED** (0 hits in 3 modules) |
| AirView is a userspace binary | **CONFIRMED** (8,647 bytes, 60 self-hits) |
| the daemon set is complete and readable | **CONFIRMED** (4 of 4, none zero-byte) |
| DMA work sits in `ath_dev.ko` | **CONFIRMED** (43 vs 14 tokens) |
| PCIe configuration sits in `umac.ko` | **CONFIRMED** (62 tokens) |
| a coexistence mechanism is named in the kernel | **REFUTED** (1 lone token) |
| kernel-side AirView arbitration | **REFUTED** |
| the PCIe descriptor layout and ring geometry | **UNKNOWN / 713A's limit** |
| how `ubntspecd` multiplexes clients | **UNKNOWN / not decoded** |

## 5. The operational reading

Three consequences for an XC spectral or DMA investigation:

1. **do not look for AirView in the kernel** — look at `ubntspecd` and the client processes;
2. **split the search by layer**: a `dma` symptom belongs in `ath_dev.ko`, a `pci` symptom in
   `umac.ko`, and neither will explain the other;
3. **a slow or empty AirView is a userspace contention question**, and the kernel will not log it —
   which is consistent with `coexist` appearing once.

## 6. Gaps

- **`UNKNOWN`** — the PCIe descriptor layout and ring geometry (Stage 713A's limit on the AC side).
- **`UNKNOWN`** — how `ubntspecd` multiplexes AirView and airMagic clients.
- **`UNKNOWN`** — what `provmode` (29 self-hits) changes, and whether it interacts with the spectral
  path.
- **`UNKNOWN`** — the identity of `dfsprescan`, which does not name itself.
- **Known limit** — a 60-self-hit binary proves identity, not capability.
- **Not attempted** — dynamic validation, live spectral capture.
