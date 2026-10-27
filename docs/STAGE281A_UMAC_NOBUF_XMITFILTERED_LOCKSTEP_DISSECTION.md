<!-- doc-head: STAGE281A_UMAC_NOBUF_XMITFILTERED_LOCKSTEP_DISSECTION.md preserved document content -->
<!-- /doc-head -->


# Stage 281A — Binary Dissection of the `1,852,520,415` vs `1,852,520,403` `no tx buffer (data)` == `xmit filtered` Lockstep in `WA.v8.7.25`

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`bin/athbox` / `umac.ko` `SIOCGATHSTATS` `0x89f0` ABI aliasing) + `QCA firmware` (`wal_dbg_stats`)
- **Safety Boundary**: `0` writes performed (`SG-01..05` compliant)
- **Receipt**: [`artifacts/autoresearch/stage281a_umac_nobuf_xmitfiltered_lockstep_dissection.json`](../artifacts/autoresearch/stage281a_umac_nobuf_xmitfiltered_lockstep_dissection.json)

---

## 1. Executive Summary (`CONFIRMED`)

Across the 4 `WA.v8.7.25` Guarida / Almafuerte radios (`.60`, `.61`, `.82`, `.83`), default `athstats` reported:
- `tx failed 'cuz no tx buffer (data)` = **`1,852,520,415`** (`144,613,596` + `356,331,089` + `1,053,619,098` + `297,956,632`)
- `tx failed 'cuz xmit filtered` = **`1,852,520,403`** (`144,613,596` + `356,331,089` + `1,053,619,086` + `297,956,632`)

Disassembly of `WA.v8.7.25` `bin/athbox` (`athstats` applet), `umac.ko`, and `ath_dev.ko` proves **100% deterministically** why these two numbers match to within `0..12` packets on every `QCA9882` (`wifi0`) radio:

1. **Unchecked `SIOCGATHSTATS` (`0x89f0`) Union/Struct Aliasing**:
   - In `bin/athbox`, `athstats` checks for the `-ol` CLI flag at `0x00402440` (`strncmp(argv[i], "-ol", 16)`, string at `0x0041758c`):
     - **With `-ol` (`0x00401930`)**: allocates a `0x0310` (`784`-byte) `struct ol_ath_stats` buffer at `$sp + 0x1250` and invokes `ioctl(fd, 0x89f0 /* SIOCGATHSTATS */, &ifr)`.
     - **Without `-ol` (`0x00402468`, default `athstats`)**: allocates a `0x1210` (`4,624`-byte) Direct-Attach `struct ath_stats` buffer at `$sp + 0x0040` and invokes the **exact same `ioctl(fd, 0x89f0, &ifr)`** on `wifi0`.
   - Because `wifi0` on `WA` is an Offload (`QCA9882`) radio registered to `umac.ko:ol_ath_ioctl` (`.text + 0x000bcc40`), `ol_ath_ioctl` handles `0x89f0` (`0x000bcc5c`) without checking `ifr_data` buffer length. It populates a `0x0310`-byte `struct ol_ath_stats` on the kernel stack (`$sp_kern + 0x0028`) via:
     - `ol_txrx_stats_publish(pdev, $sp_kern + 0x0030)` (`.text + 0x000d31b8`: copies `0x0138` bytes from `pdev + 0x0128`),
     - `ol_get_wal_dbg_stats(scn, $sp_kern + 0x0168)` (`.text + 0x000bcd30`),
     - `ol_get_radio_stats(scn, $sp_kern + 0x0238)` (`.text + 0x000bcd40`),
     and calls `copy_to_user(user_buf, $sp_kern + 0x0028, 0x0310)` (`0x000bcdc0`).

2. **Exact `+0x28` (`40`-Byte) Stride Between `multiqueue_sent[5]` and `multiqueue_compl[5]`**:
   - In `umac.ko:ol_tx_send` (`.text + 0x000d324c..0x000d3270`), every transmitted packet on queue `q` (`0..4`) increments the 64-bit big-endian counter `pdev->stats.pub.tx.multiqueue_sent[q]` at `pdev + 0x01c8 + q*8` (`user_buffer + 0x00a8 + q*8`).
   - In `umac.ko:ol_tx_completion_handler` (`.text + 0x000d3638..0x000d3664`) and `ol_tx_inspect_handler` (`0x000d3a84`), every completed packet on queue `q` (`0..4`) increments the 64-bit big-endian counter `pdev->stats.pub.tx.multiqueue_compl[q]` at `pdev + 0x01f0 + q*8` (`user_buffer + 0x00d0 + q*8`, **exact `+0x28` (`40`-byte) stride**).
   - For queue `1` (`WME_AC_BE` / Best-Effort data):
     - `low32(multiqueue_sent[1])` lands at **`user_buffer + 0x00b8`** (`$sp + 0x00f8`), which default `athstats` (`0x00402594: lw $a2, 0x00f8($sp)`) prints as **`"%10u tx failed 'cuz no tx buffer (data)\n"` (`0x004177dc`)**!
     - `low32(multiqueue_compl[1])` lands at **`user_buffer + 0x00e0`** (`$sp + 0x0120`, `+0x28` bytes later), which default `athstats` (`0x004025dc: lw $a2, 0x0120($sp)`) prints as **`"%10u tx failed 'cuz xmit filtered\n"` (`0x004178cc`)**!
   - Therefore, on `QCA9882` (`wifi0`), `no tx buffer (data) - xmit filtered` in default `athstats` is literally **`multiqueue_sent[1] - multiqueue_compl[1]`** = the instantaneous number of in-flight Best-Effort descriptors in the `QCA9882` HTT/CE ring (`0` on `.60`/`.61`/`.83`, and `11..12` on busy `.82`).

---

## 2. Byte-Exact Struct Aliasing Table (`SIOCGATHSTATS` `0x89f0` on `wifi0`)

| User Buffer Offset | `pdev` Offset (`umac.ko`) | True `struct ol_ath_stats` Field (`athstats -ol`) | Misinterpreted Default `athstats` Label (`struct ath_stats`) |
| :--- | :--- | :--- | :--- |
| `0x00a8..0x00af` | `0x01c8..0x01cf` | `multiqueue_sent[0]` (`BK` sent, `uint64_t` BE) | `0x00b0`: `tx encapsulation failed` |
| **`0x00b0..0x00b7`** | **`0x01d0..0x01d7`** | **`multiqueue_sent[1]` (`BE` sent, `uint64_t` BE)** | **`0x00b8`: `tx failed 'cuz no tx buffer (data)`** |
| `0x00b8..0x00bf` | `0x01d8..0x01df` | `multiqueue_sent[2]` (`VI` sent, `uint64_t` BE) | `0x00c0`: `Number of times netif_wake called` |
| `0x00c0..0x00c7` | `0x01e0..0x01e7` | `multiqueue_sent[3]` (`VO` sent, `uint64_t` BE) | `0x00c8`: `tx failed 'cuz too many retries` |
| **`0x00d8..0x00df`** | **`0x01f8..0x01ff`** | **`multiqueue_compl[1]` (`BE` compl, `uint64_t` BE)** | **`0x00e0`: `tx failed 'cuz xmit filtered`** |
| `0x00e0..0x00e7` | `0x0200..0x0207` | `multiqueue_compl[2]` (`VI` compl, `uint64_t` BE) | `0x00e8`: `tx frames with no ack marked` |
| `0x00e8..0x00ef` | `0x0208..0x020f` | `multiqueue_compl[3]` (`VO` compl, `uint64_t` BE) | `0x00f0`: `tx frames with short preamble` |
| `0x0110..0x0113` | `0x0230..0x0233` | `multiqueue_stopped_cnt[1]` (`BE` stops, `uint32_t`) | `0x0110`: `Radio profile: number of received data packets` |

---

## 3. True `athstats -ol` (`wal_dbg_stats`) vs Aliased Default `athstats` Across `.60`, `.61`, `.82`, `.83`

Running `athstats -ol` on all 4 radios exposes the **true** `QCA9882` firmware `wal_dbg_stats` (`0x00401930` branch):

| Radio | `q1_sent` (Aliased `nobuf`) | `q1_compl` (Aliased `xmit_filtered`) | `q1_stopped_cnt` | True `ast_be_nobuf` | True `ast_tx_buf_count` | True `mpdus_queued` | True `mpdus_requed` | True `excess_retries` | True `tx_underrun` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`.60` (`Almafuerte` AP)** | `146,350,690` | `146,350,690` | `24` | `0` | `1,424` | `340,395,119` | `30,900,030` (`9.08%`) | `4,170,241` | `2,124` |
| **`.61` (`Guarida` STA)** | `360,448,085` | `360,448,085` | `0` | `0` | `1,424` | `389,389,903` | `18,934,701` (`4.86%`) | `10,495,377` | `0` |
| **`.82` (`Panel2` AP)** | `1,066,596,331` | `1,066,596,320` | `2,214` | `0` | `1,424` | `686,772,512` | **`139,634,216` (`20.33%`)** | `23` | `0` |
| **`.83` (`Panel3` AP)** | `301,334,789` | `301,334,789` | `1,894` | `0` | `1,424` | `62,912,432` | `4,896,555` (`7.78%`) | **`9,506,061` (`15.11%`)** | `2,124` |

### Key Diagnostic Impact (`Stage 59A` Zero-False-Positive Rule)
1. **Always invoke `athstats -ol` on `wifi0` (`QCA9882`) and `athstats -i wifi1` on `wifi1` (`AR9342`)**:
   - On `Panel2 (.82)` (`polling=enabled`), true `mpdus_requed` is **`139,634,216` (`20.33%` of all `686.77M` queued MPDUs)** and `q1_stopped_cnt = 2,214`, while `excess_retries = 23` because `ubnt_poll_host.ko` handles TDMA slice deferral and requeues unpolled/NAK'd MPDUs in the WAL prior to hardware retry exhaustion.
   - On `Panel3 (.83)` (`polling=disabled`), CSMA/CA hardware retries run to exhaustion without TDMA slice scheduling, producing **`9,506,061` true `excess_retries` (`15.11%` of `62.91M` queued MPDUs)** and `2,124` `tx_underrun` events.
2. **Where `IRQ 33` (`ath-spectral-filter`) touches `ath_dev.ko`**:
   - In `ath_dev.ko`, `ath_spectral_filter_init` (`.text + 0x00027c00`) registers `IRQ 33` (`isr = 0x00027be0`). Each rising/falling GPIO edge sets `*(uint32_t *)(sc->sc_ah + 0x0384) = 1` on the Direct-Attach `wifi1` (`AR9342`) HAL, which `ath_rx_intr+0x204` (`0x00025a30`) clears (`wifi1` `recv eol interrupts`: `2.69M` on `.60`, `7.45M` on `.61`, `7.48M` on `.82`, `7.25M` on `.83`), while burning `1,150..2,285 irq/s` in kernel hard-IRQ context across all 4 radios (`4.53 Billion` cumulative interrupts).
