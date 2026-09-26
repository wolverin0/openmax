# Paced Aggregation, CoTSQ, and Bufferbloat Elimination in 802.11ac Fixed Wireless

> **Status**: CONFIRMED IN ACADEMIC LITERATURE & PEER HARDWARE (Hassani et al. 2018, Gringoli & Leith 2021, CoTSQ 2019).  
> **Key Finding**: Standard Linux TCP Small Queues (TSQ = 1 ms) starves 802.11ac A-MPDU aggregation, collapsing TCP throughput by up to an order of magnitude. Tuning socket-level queue limits to 6 ms (Controlled TSQ) restores full 64-frame aggregation with negligible latency penalty.

---

## 1. The Paradox: Bufferbloat vs Aggregation Starvation

In wireless networking, there is a fundamental tension between **low latency** and **high spectral efficiency**:

```
           [ Short Queues / Low Latency ]          [ Large Queues / High Throughput ]
                       │                                           │
                       ▼                                           ▼
          Insufficient packets buffered              Excess packets buffered in ring
                       │                                           │
                       ▼                                           ▼
      Aggregation engine starves (1-2 MPDUs)         Massive bufferbloat (>2,000 ms)
                       │                                           │
                       ▼                                           ▼
     Massive PHY preamble & contention overhead       Unusable interactive QoE (VoIP/Gaming)
```

### Why 802.11ac Demands Aggregation
In 802.11ac, channel overhead is brutal:
* Clear Channel Assessment (CCA), DIFS, and SIFS deferral: ~50 µs.
* Physical layer preamble and VHT training fields: ~40–56 µs.
* Block-ACK exchange: ~30 µs.
* Total overhead per transmission attempt: **~120–150 µs**.

If the transmitter sends a single 1500-byte frame at 866 Mbps (MCS9, 80 MHz, 2x2 MIMO):
$$\text{Airtime for 1500 bytes} = \frac{1500 \times 8}{866 \times 10^6} \approx 13.85\text{ µs}$$
$$\text{Channel Efficiency} = \frac{13.85\text{ µs}}{13.85\text{ µs} + 130\text{ µs}} \approx \mathbf{9.6\%}$$
Over **90% of the radio's airtime is wasted** on preambles, headers, and channel contention!

To achieve >80% channel efficiency, the hardware must aggregate **32 to 64 MPDUs** into a single A-MPDU (~64 to 96 KB), filling a 2 to 4 ms transmission opportunity (TXOP).

---

## 2. Why Default Linux TSQ Destroys 802.11ac Throughput

In 2012, the Linux kernel introduced **TCP Small Queues (TSQ)** to eliminate bufferbloat inside the host networking stack:
* TSQ sets a strict limit on the number of bytes queued per TCP socket: `sysctl net.ipv4.tcp_limit_output_bytes` (typically 128 KB or 1 ms of transmission time).
* Once this limit is reached, the kernel puts the TCP socket to sleep until the NIC driver issues a TX completion interrupt.

### The Breakdown on 802.11ac Hardware (`ath10k`)
On Gigabit Ethernet, 1 ms of data allows thousands of packets per second with instant hardware interrupt delivery (<50 µs).
On 802.11ac wireless:
1. Transmission is not continuous; it happens in discrete TXOP bursts.
2. When the radio wins the channel, it asks the host queue: *"How many packets do you have for this destination?"*
3. Because TSQ artificially throttled the TCP socket to 1–2 packets, **only 1 or 2 packets are waiting in the queue**.
4. The aggregation engine builds a tiny 2-packet aggregate and transmits it.
5. The socket wakes up only *after* the hardware interrupt fires, missing the TXOP window.
6. **Result**: An order-of-magnitude collapse in TCP throughput on clean 802.11ac links (often capping at 30–50 Mbps on a 400 Mbps physical link).

---

## 3. The CoTSQ (Controlled TSQ) Discovery

Research by academic teams evaluating ath10k testbeds (Hassani, Gringoli, Leith) proved that modifying the TSQ threshold produces an astonishing result:

### Empirical Goodput vs TSQ Threshold on ath10k

```
TCP Goodput (Mbps)
 350 ┼                                      ╭───────╮ (6 ms: Optimal Plateau ~320 Mbps)
 300 ┼                                  ╭───╯       ╰─────╮
 250 ┼                              ╭───╯                 ╰─── (Interactions with firmware ring)
 200 ┼                          ╭───╯
 150 ┼                      ╭───╯
 100 ┼                  ╭───╯
  50 ┼  ╭───────────────╯ (1 ms default: ~40 Mbps)
   0 ┴──┴───────┴───────┴───────┴───────┴───────┴───────┴───────►
        1       2       3       4       5       6       7   (TSQ Airtime Budget in ms)
```

### Key Findings from Testbed Measurements:
1. **The 6 ms Optimum**: Buffering **6 milliseconds** of TCP data provides precisely enough packets (32–64 frames) for the 802.11ac hardware to saturate maximum A-MPDU size on every channel access.
2. **Throughput Multiplier**: Goodput jumps from **~40 Mbps to >300 Mbps**—an order of magnitude increase on clean channels.
3. **Negligible Latency Penalty**: Because 6 ms is smaller than typical Internet RTTs (20–50 ms), the increase in queueing latency is imperceptible to end-users (<5 ms), while bufferbloat remains completely suppressed compared to unmanaged FIFO buffers (>2,000 ms).
4. **Beyond 6 ms**: Increasing TSQ beyond 6 ms does not yield higher throughput; instead, it causes instability due to uncontrolled interactions between host queues and the closed target firmware credit ring.

---

## 4. Paced Aggregation: Regulating Ingress Traffic

In the landmark paper *Modelling Downlink Packet Aggregation in Paced 802.11ac WLANs* (Gringoli & Leith, arXiv:2101.07562) and *Quick and Plenty* (arXiv:1806.07761), the authors derived a closed-form analytic model connecting packet arrival pacing with aggregate formation.

### Core Formulation
Let:
* $R_{phy}$ be the physical transmission bitrate (bps).
* $T_{txop}$ be the maximum duration of a transmission opportunity (typically 4 ms in 802.11ac).
* $L$ be the average packet size (bytes).
* $N_{max}$ be the maximum number of subframes per A-MPDU (64).
* $r_{in}$ be the ingress pacing rate from the core network / qdisc.

The expected aggregate size $K$ (number of subframes per A-MPDU) when paced at rate $r_{in}$ over a channel with service interval $\tau_{serv}$ is:
$$K = \min\left( N_{max}, \; \left\lfloor \frac{r_{in} \cdot \tau_{serv}}{8 \cdot L} \right\rfloor \right)$$

### Tactical Implication for WISP POP / AP Core
Instead of letting ingress packets burst into the AP at wire speed (1 Gbps) from the fiber uplink and slamming into the radio queues:
1. **Apply FQ-CoDel / CAKE with Per-Host Pacing at the Ingress Interface**:
   Pacing subscriber traffic at their purchased service tier (e.g. 50 Mbps, 100 Mbps) distributes packet arrivals into regular bursts matching the Wi-Fi beacon/service interval $\tau_{serv}$.
2. **Synchronize Pacing Intervals with AQL**:
   When the queue limit is calibrated to 4–6 ms of airtime and ingress flows are paced, packets arrive at the driver queue just in time to form optimal 32–64 packet aggregates without accumulating standing queues.

---

## 5. Practical Implementation Guide for FuturaMAX

On OpenWrt / Linux platforms powering airMAX hardware, apply these sysctl and module adjustments:

### 1. Adjust TSQ Limits
```sh
# Set TCP output byte limit to correspond to ~6 ms of peak PHY airtime (approx 256 KB)
sysctl -w net.ipv4.tcp_limit_output_bytes=262144

# Ensure TCP pacing is enabled (default in Linux FQ / BBR)
sysctl -w net.core.default_qdisc=fq_codel
```

### 2. Configure Airtime-Based Queue Limits (AQL)
```sh
# Set AQL threshold to 6000 microseconds (6 ms)
# This limits driver-level pending airtime to match the CoTSQ budget
echo 6000 > /sys/module/mac80211/parameters/aql_threshold
```

### 3. Verification Commands
```sh
# Verify TCP socket queue stats
ss -tin
# Monitor mac80211 AQL queue depth and drops
cat /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
```

---

## 6. Summary: The FuturaMAX Queueing Stack

```
┌────────────────────────────────────────────────────────┐
│ Ingress Shaper: CAKE / FQ-CoDel (Pacing per CPE)       │  <-- Bounded to plan speed
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ TCP Socket Layer: CoTSQ (6 ms Airtime Budget)          │  <-- Keeps aggregation full
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ mac80211 Subsystem: AQL (6 ms Driver Queue Limit)      │  <-- Stops bufferbloat
└──────────────────────────┬─────────────────────────────┘
                           │ (Credit-controlled DMA)
┌──────────────────────────▼─────────────────────────────┐
│ ath10k Hardware: 32–64 Frame A-MPDU Bursts             │  <-- >85% Channel Efficiency
└────────────────────────────────────────────────────────┘
```
