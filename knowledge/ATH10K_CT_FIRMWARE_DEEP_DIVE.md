# ath10k and ath10k-ct Firmware Internals: Architecture, Control Knobs, and the Airtime Cliff

> **Status**: CONFIRMED & INFERRED (Source-verified against Linux kernel mainline, Candela Technologies ath10k-ct, and openwrt/openwrt tracking issues).  
> **Hardware Target**: Ubiquiti airMAX AC (Qualcomm Atheros QCA9880 / QCA9882 on Atheros AR9342 MIPS 74Kc).  
> **Firmware Version Baseline**: `10.2.4-1.0-00037` (stock airOS Xtensa core) vs Candela Technologies `10.1-ct-8x-__fW-022` / `10.2.4-ct`.

---

## 1. Executive Summary & The Core Architectural Reality

Most networking discussions treat Wi-Fi cards as transparent hardware where the host OS schedules packets and selects transmission rates. **On QCA988x (802.11ac Wave 1), this mental model is completely false.**

QCA988x is a **firmware-offloaded FullMAC-hybrid architecture**:
1. An on-chip **Tensilica Xtensa 32-bit RISC core** runs compiled proprietary firmware inside the radio module.
2. The Linux host (`mac80211` / `ath10k`) communicates with this core via two message-passing interfaces over PCIe:
   * **WMI (Wireless Module Interface)**: Control plane (channel, VIF creation, peer association, regulatory power, beacon configuration, spectral scan).
   * **HTT (Host-Target Transport)**: Data plane (TX frame descriptors, TX completion descriptors, RX packet notifications, credit exchange).
3. Rate selection is hardcoded to the firmware: `ieee80211_hw_set(ar->hw, HAS_RATE_CONTROL)` in `drivers/net/wireless/ath/ath10k/mac.c`. **mac80211 minstrel / minstrel_ht does not run.**
4. Upstream Qualcomm firmware was tuned for indoor consumer Wi-Fi, using aggressive 30-retry loops and large internal buffers that create massive bufferbloat and collapse outdoor PtMP links during fades.
5. Ben Greear’s **Candela Technologies (`ath10k-ct`)** firmware and driver fork rewrite key internal behaviors, opening crucial host-control knobs while introducing specific memory and stability constraints on low-RAM MIPS hardware.

---

## 2. Upstream ath10k Firmware vs Candela Technologies (ath10k-ct)

The choice between upstream Qualcomm firmware and Candela Technologies firmware represents a fundamental engineering trade-off:

| Feature / Behavior | Upstream Qualcomm Firmware (`10.2.4`) | Candela Technologies (`ath10k-ct`) | Engineering Impact on Fixed PtMP |
|:---|:---|:---|:---|
| **Max Frame Retries** | **30 retries (`0x1e`)** | **4 retries** (0 non-agg, 4 agg) | Upstream stalls entire sectors when one CPE fades. CT drops failed frames quickly, preserving airtime. |
| **Initial Rate Selection** | Starts at MCS5 / high rate | Starts at MCS0 / MCS3 | Upstream drops DHCP packets to distant CPEs during association. CT reliably associates far stations. |
| **Rate Mask Control** | None (firmware blackbox) | `ATH10K_FW_FEATURE_CT_RATEMASK` | CT allows host to ban high-order modulation states (e.g. force max MCS7 or ban MCS9). |
| **Max A-MPDU/A-MSDU** | Fixed internal heuristic | Exposed via debugfs `htt_max_amsdu_ampdu` | Allows host outer-loop optimization of aggregate sizes. |
| **RAM Footprint (Host)** | Moderate (~20–30 MB) | High unless `kmod-ath10k-ct-smallbuffers` | On 64 MB–128 MB devices (LiteBeam, LAP-120), full CT can trigger OOM kernel panics. |
| **802.11s Mesh Mode** | Fully functional in driver | Known stability/routing regressions | For PtMP AP/STA mode, CT is viable; for 802.11s mesh, upstream is preferred. |
| **Management Path** | WMI commands | Optional `ath10k-ct-htt-mgt` path | Using HTT for management avoids head-of-line blocking in WMI command queues. |

### The 30-Retry Disaster in Fixed Wireless
In dense indoor Wi-Fi, 30 retries may salvage a packet as a smartphone moves. In outdoor fixed wireless, where path loss is high and interference bursts occur, **30 retries on a single aggregate at low MCS can consume 50 ms to 100 ms of continuous channel airtime**. Under CSMA, every other CPE in the sector is silenced during this window. Candela Technologies capping retries to 4 is one of the single biggest structural airtime saves for fixed wireless.

---

## 3. HTT Data Path & The Credit Ring Mechanism

To understand why latency explodes and how host scheduling operates, we must examine the HTT credit ring:

```
[ Host: mac80211 TXQ / FQ-CoDel ]
               │
               ▼
[ Host: ath10k PCIe Driver ]  ◄─── HTT TX Credits Available?
               │
               │ (PCIe DMA push)
               ▼
┌─────────────────────────────────────────────────────────┐
│ QCA988x Target Firmware (Xtensa Core)                  │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │ Firmware Internal TX Buffer Ring (HTT Descriptors)│ │
│   └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│   ┌─────────────────────────────────────────────────┐   │
│   │ Hardware Baseband / PHY TX FIFO                 │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

1. **Credit Management**: The target firmware issues a fixed number of TX credits (typically 300 to 500 descriptors on QCA9880) to the host driver.
2. **Bufferbloat at the Lower Boundary**: Whenever the host has packets, `ath10k` transfers them to the target until credits reach zero. If 300 frames of 1500 bytes sit in firmware buffers at MCS1 (13 Mbps), the hardware queue holds:
   $$\text{Queue Latency} = \frac{300 \times 1500 \times 8 \text{ bits}}{13 \times 10^6 \text{ bps}} \approx 276 \text{ milliseconds}$$
3. **No In-Flight Abort**: Once a packet descriptor is committed across PCIe to the target ring, **the host cannot abort or revoke it**. The firmware will attempt transmission until completion or retry exhaustion.
4. **The Role of AQL (Airtime-Based Queue Limits)**: AQL does not change the firmware ring size directly; instead, it intercepts packets at `mac80211`, refusing to push frames down to `ath10k` once the airtime of pending packets exceeds a tight threshold (e.g. 4–12 ms), forcing excess packets to wait in the host FQ-CoDel queue where they can be paced, reordered, or dropped.

---

## 4. The `last_tx_bitrate` Airtime Cliff

This is the most critical driver-level finding for FuturaMAX.

### The Problem: Wave 1 Silicon Lacks Firmware Airtime Reporting
In 802.11ac Wave 2 chips (QCA9984, QCA4019), firmware explicitly reports exact airtime consumed per frame via `WMI_10_4_SERVICE_REPORT_AIRTIME`.
**On QCA9880/QCA9882 (Wave 1), this service is structurally absent (`10.2.4` codebase).**

Consequently, Linux `mac80211` must calculate airtime using host-side estimation:

```c
/* drivers/net/wireless/ath/ath10k/mac.c: ath10k_mac_update_airtime() */
if (arsta->last_tx_bitrate) {
    airtime = (pktlen * 8 * 10) / arsta->last_tx_bitrate;
    airtime += IEEE80211_ATF_OVERHEAD_IFS;
} else {
    /* THE CLIFF: Fallback to 6 Mbps */
    airtime = (pktlen * 8 * 10) / 60;
    airtime += IEEE80211_ATF_OVERHEAD;
}
```

### The Mechanism of the Cliff
`arsta->last_tx_bitrate` is populated in exactly **one place**:
`ath10k_update_per_peer_tx_stats()` in `htt_rx.c`, triggered by `HTT_T2H_MSG_TYPE_PEER_STATS`.

This event is delivered **only if**:
```c
(ar->flags & ATH10K_FLAG_PEER_STATS) && test_bit(WMI_SERVICE_PEER_STATS, ar->wmi.svc_map)
```

> **The Catastrophic Degeneration**:
> If peer stats are disabled, delayed, or dropped, `last_tx_bitrate` remains `0`.
> In this state, `mac80211` calculates the airtime of **every single station as if it were transmitting at 6 Mbps**!
> On a WISP sector with near clients (MCS9, 866 Mbps) and far clients (MCS1, 58 Mbps), the airtime fairness scheduler loses all visibility into rate disparity. Fast stations are throttled because the scheduler falsely believes they consume 6 Mbps airtime, destroying multi-user throughput gains and converting airtime fairness into degraded packet fairness.

### Verification Check for Testbed Radios
To confirm on live OpenWrt whether peer stats are active and populating `last_tx_bitrate`:
```sh
# Check if peer stats are non-zero
cat /sys/kernel/debug/ieee80211/phy0/ath10k/peer_stats
# Monitor station transmission rates in mac80211
iw dev wlan0 station dump
```

---

## 5. Host-Accessible Control Knobs in ath10k-ct

While rate selection is offloaded to firmware, Candela Technologies and mac80211 expose several high-leverage control hooks:

### 1. Rate-Mask Bounding (`ratemask-CT`)
* **Path**: Configured at peer association via WMI.
* **Function**: Restricts the firmware from attempting high MCS indices that are physically unsustainable on a specific CPE link (e.g. banning MCS8/9 on a link with 22 dB SNR).
* **Benefit**: Prevents the firmware rate controller from periodically probing doomed rates, eliminating packet drop cycles and saving 15–25% of wasted sector airtime.

### 2. Device-Wide Max Aggregation (`htt_max_amsdu_ampdu`)
* **Path**: `/sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu`
* **Syntax**: `echo "<max_amsdu> <max_ampdu>" > htt_max_amsdu_ampdu`
* **Function**: Sets hard upper bounds on A-MSDU subframes and A-MPDU MPDUs across the radio.
* **Benefit**: Allows tuning aggregation depth under mixed traffic or heavy interference.

### 3. Airtime-Based Queue Limits (AQL)
* **Path**: `/sys/kernel/debug/ieee80211/phy0/aql_txq_limit` and `/sys/module/mac80211/parameters/aql_threshold`
* **Function**: Restricts the maximum duration of packets queued in the hardware driver per station (typically 2 ms to 12 ms).
* **Benefit**: Eliminates bufferbloat; reduces p99 latency from >4,000 ms to <60 ms under saturation.

### 4. Small Buffers Profile (`kmod-ath10k-ct-smallbuffers`)
* **Function**: Reduces driver DMA pool descriptor counts.
* **Criticality**: **Mandatory** on LiteBeam 5AC Gen2 and LAP-120 boards with 64 MB / 128 MB RAM to prevent kernel OOM panics during multi-client speedtests.

---

## 6. Summary of Engineering Directives for FuturaMAX

1. **Do not attempt to write a host rate-control algorithm** (e.g. Minstrel/Minstrel-HT/IteRate in mac80211). It has no attachment point in ath10k.
2. **Focus rate optimization on outer-loop rate-masking**: Learn optimal per-CPE rate bounds over hours/days and apply them via rate masks.
3. **Verify peer stats on every OpenWrt build**: Ensure `last_tx_bitrate` is actively tracking client MCS to prevent falling off the 6 Mbps airtime cliff.
4. **Use smallbuffers packages on all MIPS 74Kc boards**: Never deploy standard `kmod-ath10k-ct` without the `smallbuffers` patch on 64 MB / 128 MB hardware.
5. **Combine AQL with CoTSQ**: Control queue depth at both the socket layer (TCP Small Queues) and the mac80211 driver ring (AQL) to preserve frame aggregation while squashing latency.
