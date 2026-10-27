<!-- doc-head: STAGE647A_QCA988X_HTT_RX_RING_DECAP_AND_AMSDU_SUBFRAME_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 647A — HTT RX ring, decap modes, A-MSDU and attention flags

- **Receipt**: [`artifacts/autoresearch/stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.json`](../artifacts/autoresearch/stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.json)
- **Tool**: [`tools/re/build_stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.py`](../tools/re/build_stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Four modules

`WA:umac.ko` and `XC:umac.ko` (2.36 MB each), `WA:ath_dev.ko` and `XC:ath_dev.ko` (287,216 each).
The device modules contribute only `amsdu`/`msdu` traces; everything else is UMAC.

## 1. The RX ring is configured by three separate messages

**30 `htt_*` symbols.** The transport lifecycle and the ring configuration:

```
htt_attach   htt_attach_target   htt_detach   htt_display
htt_h2t_rx_ring_cfg_msg
htt_h2t_rx_ring_cfg_msg_hl        <- high-level
htt_h2t_rx_ring_cfg_msg_ll        <- low-level
htt_h2t_aggr_cfg_msg   htt_h2t_send_complete   htt_h2t_sync_msg
htt_h2t_dbg_stats_get  htt_h2t_ver_req_msg     htt_h2t_full
htt_rx_ring_elems
```

**`CONFIRMED`**: `ring_cfg_variant_count = 3`, `ring_cfg_has_hl_ll = 1`. The ring is set up by a
base message **plus two variants**, high-level and low-level.

That is what a transport needs when the two ends use different descriptor formats: the same logical
configuration has a compact form and an extended form. `htt_rx_ring_elems` carries the element count,
so the ring **depth** is a host-supplied parameter, not a compiled constant.

## 2. The attention flag is pinned to bit 31 — a rare concrete constant

`umac.ko` carries a hard assertion with the mask spelled out:

```
Assertion failed! %s:%s %s:%d
((*(u_int32_t *) &rx_desc->attention) & 0x80000000)
```

**`CONFIRMED`**: `attention_mask = 0x80000000`, `attention_flag_recovered = 1`.

This is one of the **very few concrete numeric constants** the series has recovered. The assertion
fires if bit 31 of the `attention` word is clear, so bit 31 is a **mandatory** flag — a descriptor
arriving with it unset is a bug, not a variant.

The retriever is also present: `htt_rx_msdu_rx_attention_retrieve_ll` (`attention_retriever_present = 1`).
The `_ll` suffix ties it to the low-level ring variant of §1.

**`UNKNOWN`**: what bits 0..30 mean. Only bit 31 is pinned.

## 3. `decap` means decryption, not decapsulation

`decap` has 9 hits, and none of them is an RX decapsulation path:

```
ieee80211_crypto_decap     ccmp_decap     ieee80211_crypto_encap
ieee80211_crypto_setkey    ieee80211_hdrsize
```

**`REFUTED`**: `raw_mode`, `native_wifi` and `decap_mode` all return **0**
(`native_raw_enum_absent = 1`). The four-way decap enum the stage assumes does not exist by name.

**`CONFIRMED`**: `decap_is_crypto_modules = 2` — in this module the word means **decryption**.

The mode that *does* exist is a boolean, documented in its own parameter string:

```
host_80211_enable: Enable reception of 802.11 frames & conversion to 802.3 frames on host
```

**`CONFIRMED`**: `host_80211_boundary = 1` (`host_80211_modules = 2`).

So the decap choice is **binary, not quaternary**:

| `host_80211_enable` | What the host receives |
| :--- | :--- |
| **1** | **802.11 frames** — host performs the 802.3 conversion |
| **0** | **802.3 frames** — target has already converted |

That is a cleaner finding than a four-way enum, because it identifies **where the boundary sits**
rather than naming four modes.

## 4. A-MSDU is split across TX staging and RX pop

`amsdu` has 28 raw hits and **17 distinct symbols**, and the family is **mixed**
(`amsdu_is_mixed = 1`):

| Side | Symbols | Examples |
| :--- | :-: | :--- |
| **TX staging** | **9** | `ath_amsdu_send`, `ath_amsdu_stageq_flush`, `ath_amsdu_tx_drain` |
| **RX pop** | **3** | `htt_rx_amsdu_pop` (`rx_amsdu_pop_hits = 8`) |

**`CONFIRMED`**: aggregation and deaggregation are **different subsystems** in different code paths —
the TX side stages and drains, the RX side pops from the HTT ring. Reading `ath_amsdu_*` as
deaggregation would be wrong.

And Stage 395A already established the important negative: `htt_rx_amsdu_pop` contains **zero**
`skb_pull` sites. Whatever it does with the descriptor prefix, it does not do it with `skb_pull`, and
it never pulls 84 bytes.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| the RX ring is configured by a host-to-target message with HL and LL variants | **CONFIRMED** (3 forms) |
| the ring element count is a host parameter | **CONFIRMED** (`htt_rx_ring_elems`) |
| the attention flag is bit 31, enforced by assertion | **CONFIRMED** (`0x80000000`) |
| an attention retriever exists at the LL layer | **CONFIRMED** |
| `decap` here means decryption | **CONFIRMED** (ccmp/crypto decap) |
| a raw / native-wifi / ethernet / 802.3 decap enum exists | **REFUTED** (0 hits) |
| the 802.11-vs-802.3 boundary is a boolean | **CONFIRMED** (`host_80211_enable`) |
| A-MSDU has separate TX staging and RX pop subsystems | **CONFIRMED** (9 vs 3 symbols) |
| the other 31 attention bits | **UNKNOWN / not decoded** |
| the subframe deaggregation loop | **UNKNOWN / not decoded** |

## 6. The operational reading

Two facts matter on a bench:

- **the host/802.3 boundary is a module parameter**, so "is the host seeing 802.11 or 802.3" is a
  configuration question with a yes/no answer, not an inference from frame sizes;
- **the attention assertion is hard**, so a descriptor word with bit 31 clear will produce an
  explicit failure line with file and line number. If a log shows that assertion, the RX ring is
  delivering malformed descriptors — not a marginal signal problem.

Everything else about the ring (depth, HL/LL choice, element layout) is host-supplied and therefore
not recoverable from the module.

## 7. Gaps

- **`UNKNOWN`** — attention bits 0..30.
- **`UNKNOWN`** — the HL vs LL ring descriptor layouts.
- **`UNKNOWN`** — the A-MSDU subframe iteration and where the subframe length is read.
- **`UNKNOWN`** — whether the four decap modes exist in the firmware rather than the host driver.
- **`UNKNOWN`** — the ring element struct beyond `attention`.
- **Known limit** — one pinned bit is not a decoded descriptor.
- **Not attempted** — dynamic validation, on-air ring capture.
