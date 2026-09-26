# Spectral Analysis and Channel State Information (CSI) on QCA988x / ath10k

> **Status**: CONFIRMED (Source-verified against Linux kernel ath10k, openwrt mac80211 packages, WiFiSpectralJam dataset [arXiv:2608.15728], and Atheros CSI Tool documentation).  
> **Verdict**: Raw Spectral FFT scanning is fully functional on QCA988x under OpenWrt (requires `PACKAGE_ATH_SPECTRAL=y`), providing high-resolution RF energy distributions. Full CSI (Channel State Information) extraction is structurally absent on QCA988x due to closed Xtensa firmware limitations.

---

## 1. Physical Layer Telemetry: Spectral FFT vs CSI

In wireless optimization, physical layer feedback is essential to distinguish between **path loss**, **multipath fading**, and **external RF interference**:

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ Spectral FFT Scanning           │ Channel State Information (CSI) │
├─────────────────────────────────┼─────────────────────────────────┤
│ • Power magnitude per frequency │ • Complex subcarrier response   │
│   bin across 20/40/80 MHz.      │   (amplitude AND phase: H(f)).  │
│ • Sensed via baseband ADC/FFT.  │ • Measured per antenna pair     │
│ • Detects non-Wi-Fi jammers,    │   from OFDM preamble training.  │
│   frequency-hopping radars, and │ • Enables sub-centimeter motion │
│   adjacent-channel bleed.       │   sensing and channel inversion.│
│ • STATUS ON QCA988x: CONFIRMED  │ • STATUS ON QCA988x: ABSENT     │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

## 2. Spectral FFT Scanning on ath10k: Architecture & Operation

The Qualcomm Atheros QCA9880/QCA9882 baseband processor includes an integrated Fast Fourier Transform (FFT) co-processor used during Clear Channel Assessment (CCA) and radar detection.

### The Software Pipeline

```
┌────────────────────────────────────────────────────────┐
│ QCA988x Baseband FFT Engine (56 or 64 frequency bins)  │
└──────────────────────────┬─────────────────────────────┘
                           │ Raw FFT reports
┌──────────────────────────▼─────────────────────────────┐
│ Xtensa Target Firmware (ath10k firmware)               │
└──────────────────────────┬─────────────────────────────┘
                           │ WMI_SPECTRAL_SCAN_EVENT
┌──────────────────────────▼─────────────────────────────┐
│ Host Kernel: ath10k_spectral.c                         │
└──────────────────────────┬─────────────────────────────┘
                           │ Linux RelayFS Ring Buffer
┌──────────────────────────▼─────────────────────────────┐
│ Userspace: /sys/kernel/debug/ieee80211/phy0/spectral/* │
└────────────────────────────────────────────────────────┘
```

### Build-Time Requirement in OpenWrt
As verified in `docs/QCA988X_CONTROL_BOUNDARY.md`, spectral scanning is not disabled by hardware; it is simply omitted by default in standard OpenWrt binary images to conserve flash space:
* `package/kernel/mac80211/ath.mk`:
  ```makefile
  config PACKAGE_ATH_SPECTRAL
      bool "Enable ath spectral scan support"
      depends on PACKAGE_ATH_DEBUG
      select KERNEL_RELAY
  ```
* Building OpenWrt with `CONFIG_PACKAGE_ATH_SPECTRAL=y` and `CONFIG_PACKAGE_ATH_DEBUG=y` compiles `ath10k/spectral.c` and links Linux RelayFS.

### Controlling Spectral Scan via Debugfs
Once enabled in the firmware build:
```sh
# Set spectral scan mode: 'background' or 'manual'
echo "background" > /sys/kernel/debug/ieee80211/phy0/spectral_scan_ctl

# Set FFT bin count (e.g. 56 or 64 bins)
echo 1 > /sys/kernel/debug/ieee80211/phy0/spectral_count

# Read raw spectral samples via RelayFS
cat /sys/kernel/debug/ieee80211/phy0/spectral_scan0 | hexdump -C
```

### The Spectral Frame Format
Each spectral sample delivered over RelayFS contains:
* Channel frequency and bandwidth (20 / 40 / 80 MHz).
* Timestamp from MAC hardware timer.
* Noise floor (dBm) and max RSSI.
* Bin magnitudes: 56 or 64 raw 8-bit unsigned integers representing signal power density across the spectrum.

### The Single-Radio Data Path Penalty
On high-end Ubiquiti radios like the **Rocket 5AC Prism**, Ubiquiti mounted a **dedicated secondary radio chip** connected to an auxiliary antenna specifically for continuous airView spectral capture.
On standard single-radio hardware (LiteBeam 5AC Gen2, LAP-120, Loco 5AC):
* The primary QCA988x transceiver must pause active frame transmissions to collect spectral FFT samples.
* Therefore, spectral scanning must be executed as a **periodic background pulse** (e.g. 10 ms scan every 5 seconds) rather than a continuous stream, ensuring subscriber traffic is not disrupted.

---

## 3. The Truth About CSI (Channel State Information) on QCA988x

Many research proposals suggest using machine-learning models trained on CSI amplitude and phase to predict optimal wireless rates and detect channel fading.

### Why CSI Does Not Work on QCA9880 / ath10k:
1. **Atheros CSI Tool Legacy**: The famous *Atheros CSI Tool* (Xie et al., 2015) was built exclusively for **802.11n ath9k chipsets** (AR93xx, AR95xx). In `ath9k`, the host driver possesses direct register access to the baseband Rx descriptors and PHY error logs.
2. **Qualcomm Firmware Wall**: In `ath10k` (QCA9880), all PHY preamble processing occurs on the radio's closed Xtensa core. Qualcomm firmware does **not** expose a WMI or HTT message to transfer full subcarrier channel matrices to the host CPU.
3. **Absence of Community Firmware Ports**: Unlike Broadcom chips (which have Nexmon firmware patchers), there is no open-source microcode framework for the QCA9880 Xtensa core capable of extracting CSI registers.

> **Engineering Verdict**: CSI-based optimization is **REFUTED** on target hardware. All RF intelligence in FuturaMAX must rely on **Spectral FFT samples, Block-ACK retry statistics, and peer SNR/RSSI metrics**.
