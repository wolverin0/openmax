<!-- doc-head: Stage353A source and binary qualified sub20 PLL and OFDM timing -->
Offline dissection does not establish installed-board sub20 support or regulatory eligibility.
<!-- /doc-head -->

# Stage353A

Parent: reproducible firmware/control-boundary RE1. Question: where are actual
half/quarter clock and timing controls, and where are only ABI names or bits?
Run `python tools/re/build_stage353a_sub20mhz_pll_ofdm_timing_matrix.py`.
The dedicated JSON retains hashed Linuxv6.6.110 sources with line anchors and
held vendor ELF symbol offsets, bytes, hashes and first MIPS instructions.
No module is executed, loaded, patched, or used to write a register.

| Legacy OFDM width | Divisor | Useful+GI us | Symbol us | Spacing kHz | ath9k5GHz SIFS/slot us |
| :--- | ---: | :--- | ---: | ---: | :--- |
| 20MHz | 1 | 3.2+0.8 | 4 | 312.5 | 16/9 |
| 10MHz | 2 | 6.4+1.6 | 8 | 156.25 | 32/13 |
| 5MHz | 4 | 12.8+3.2 | 16 | 78.125 | 64/21 |

Slot time is NOT naively multiplied by2/4. The ACK values in JSON are upstream
pre-coverage settings, not universal over-air ACK durations or timeout getters.
The20MHz row assumes ah->slottime=9; every ACK/slot row excludes dynack and
uses coverage_class=0. Actual configured slot, coverage and dynack can change it.
Noise-bandwidth arithmetic assumes fixed NF and temperature; it is not measured gain.
These are legacy OFDM timing models, not proof of VHT operation at5/10MHz.

ath9k ar9003 has PLL CLKSEL half/quarter branches and delta-slope scaling.
AR934x/QCA955x host identification alone does not identify the actual RF path.
WA/XC QCA988x remains firmware-offloaded: inspected upstream chan_to_phymode
has no5/10 cases. Regulatory capability bits, fork flags, vendor named tables,
and chanbw ioctl metadata do not authenticate a working end-to-end control path.
The qca6174 PLL function is not a QCA988x PLL recipe. XM is not one silicon revision.

Primary anchors: [ath9k hw.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath9k/hw.c),
[ar9003_phy.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath9k/ar9003_phy.c),
[ath10k mac.c](https://github.com/gregkh/linux/blob/v6.6.110/drivers/net/wireless/ath/ath10k/mac.c).
The source cache and module pins are the reproducibility record; observed hardware
support, spectral compliance, PLL lock and peer interoperability remain UNKNOWN.
Decision: KEEP this offline matrix; no device configuration or sub20 enablement.
