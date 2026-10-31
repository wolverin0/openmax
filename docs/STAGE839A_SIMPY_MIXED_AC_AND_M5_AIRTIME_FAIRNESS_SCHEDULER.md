<!-- doc-head: Stage 839A offline SimPy airtime-fairness scheduler for mixed 802.11ac + 802.11n/M5 stations; reproduces the 802.11 performance anomaly and quantifies airtime-fair aggregate gain -->
<!-- /doc-head -->
# Stage 839A — SimPy Mixed 802.11ac + 802.11n/M5 Airtime-Fairness Scheduler

- **Claim Status**: `CONFIRMED` (offline model)
- **Attribution**: `external controller (offline model)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage839a_simpy_mixed_ac_and_m5_airtime_fairness_scheduler.json`
- **Tool**: `tools/sim/run_stage839a_simpy_mixed_ac_and_m5_airtime_fairness_scheduler.py`

## 1. What it models
A saturated shared Wi-Fi medium with a ~50/50 mix of fast 802.11ac stations
(300 Mbps class) and slow 802.11n / M5 XW stations (65 Mbps class), as a SimPy
serialized-TXOP process. Per-frame MAC overhead (DIFS+SIFS+preamble+ACK, 60 µs)
grows with the number of contending stations (`+2 %` per station) to capture
rising backoff/collision cost. Two scheduling policies run on the identical medium.

## 2. Policies
- **equal_txop** — legacy DCF round-robin: one equal-size (1500 B) frame per TXOP.
- **airtime_fair** — each station gets an equal *medium-time* quantum (2 ms); fast
  stations fit more frames into their slice.

## 3. Results (sweep N = 2..32)
| N | equal_txop agg (Mbps) | equal Jain-airtime | airtime_fair agg | fair Jain-airtime | gain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2 | 69.2 | 0.852 | 83.3 | 1.000 | +20.4 % |
| 8 | 66.4 | 0.862 | 80.6 | 0.998 | +21.3 % |
| 16 | 63.1 | 0.874 | 74.1 | 1.000 | +17.5 % |
| 32 | 57.3 | 0.894 | 64.7 | 1.000 | +13.0 % |

- **Mean aggregate gain (airtime-fair vs equal-TXOP): +18.55 %.**
- Jain fairness on **airtime** ≈ 1.0 under the fair scheduler vs ~0.85–0.89 under equal-TXOP.

## 4. The 802.11 performance anomaly, made explicit
Under `equal_txop`, every station gets the *same bytes* (equal frames) — Jain on
*throughput* is 1.0 — but the slow stations consume disproportionate **airtime** per
frame (Jain airtime ~0.85), dragging aggregate down. The airtime-fair scheduler
reverses the fairness axis: it equalizes airtime (Jain airtime ~1.0), lets fast ac
stations carry more bytes, and recovers **+13–22 %** aggregate. This is the classic
result motivating airtime fairness in mixed ac/n and mixed-vendor M5 sectors.

## 5. Reproduce & limits
```sh
python tools/sim/run_stage839a_simpy_mixed_ac_and_m5_airtime_fairness_scheduler.py
python -m pytest tests/test_stage839a.py -q
```
Model, not measurement: saturated traffic, idealized round-robin (no real backoff
distribution), fixed 1500 B frames, single rate per class. It quantifies the
*direction and rough magnitude* of airtime fairness, not a calibrated sector figure.
