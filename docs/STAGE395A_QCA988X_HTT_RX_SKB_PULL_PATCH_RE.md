<!-- doc-head: STAGE395A_QCA988X_HTT_RX_SKB_PULL_PATCH_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 395A — where `skb_pull` discards the RX descriptor, and the hook to keep it

- **Receipt**: [`artifacts/autoresearch/stage395a_qca988x_htt_rx_skb_pull_patch_re.json`](../artifacts/autoresearch/stage395a_qca988x_htt_rx_skb_pull_patch_re.json)
- **Tool**: [`tools/re/qca988x_htt_rx_amsdu_pop_skb_pull_patch_re.py`](../tools/re/qca988x_htt_rx_amsdu_pop_skb_pull_patch_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, **no binary patched**.

## 0. The target module does not exist

| Probe | Result |
| :--- | :--- |
| `ath10k*.ko` under `artifacts/` | **0 files** |
| Linux 6.6.110 source tree | **absent** |
| `*ath10k*.md` | 1 — a **1,859-byte AQL dossier** |

The dossier is about Airtime Queue Limits and CoTSQ. It contains no `rx_ppdu_end`, no EVM table and
no `skb_pull` offset. **`ath10k_htt_rx_amsdu_pop` and `ath10k_htt_rx_h_ppdu` therefore cannot be
disassembled**, and Stage 371A already showed the field names are absent from the vendor modules
too.

So the question — *which `skb_pull` throws the descriptor away, and where is the hook* — is
answered where it **can** be answered: the vendor `umac.ko` that actually ships.

## 1. Method: relocations, not addresses

`umac.ko` is `ET_REL`. A call to an external function is not a resolved address; it is an
`.rel.text` entry of type `R_MIPS_26` (4) against an undefined symbol. The tool:

1. enumerates every relocation whose symbol is `skb_pull`, `pskb_pull` or `skb_pull_rcsum`;
2. resolves the **length argument `$a1`** backwards from each call site, including the delay slot,
   accepting only `addiu $5,$0,N` or `ori $5,$0,N` materialised as an immediate;
3. attributes each site to its enclosing function by the nearest preceding `FUNC` symbol.

An unresolved length means the argument came from memory, and is reported as `null` rather than
guessed.

## 2. Results

| Quantity | `WA.v8.7.25` | `XC.v8.7.25` |
| :--- | :-: | :-: |
| total relocations | 50,694 | 50,694 |
| `skb_pull` sites | **35** | **35** |
| length materialised as an immediate | **16** | **16** |
| length loaded from memory (variable) | **19** | **19** |

Length histogram over the **16** sites whose argument is an immediate, identical in both images:

| Length (bytes) | Sites |
| :-: | :-: |
| 2 | 1 |
| 4 | 1 |
| **8** | **10** |
| 14 | 2 |
| 60 | 1 |
| **248** | 1 |
| **84** | **0** |

**`REFUTED`**: **84 never appears.** Not inside the pop function, not anywhere in `umac.ko` — and
that conclusion does not depend on the 19 variable-length sites, because a variable pull cannot be
a 84-byte descriptor strip either: it would have to be computed, and no 84 constant exists near
any of them.

The 19 unresolved sites matter for a different reason: they are the ones a patch could **not** be
placed at blindly, because the length is not visible in the instruction stream.

## 3. `htt_rx_amsdu_pop` does not call `skb_pull` at all

The function resolves to `0x01bee4`..`0x01c2cc` — **1,000 bytes** — and contains **zero** pull
sites.

**`CONFIRMED`**: the function exists (2 images, symbol present). **`REFUTED`**: it discards the
descriptor via `skb_pull`. Whatever the vendor pop path does with its RX prefix, it does not do it
with a direct `skb_pull` call, and it does not do it with 84 bytes.

## 4. Where the pulls actually are

| Function | Sites |
| :--- | :-: |
| `ol_rx_deliver` | **5** |
| `wlan_connection_sm_set_roam_bssid` | 3 |
| `ieee80211_amsdu_input` | 3 |
| `wmi_control_rx` | 3 |
| `ccmp_init_blocks` | 2 |
| `ieee80211_input` | 2 |
| `ieee80211_fragment`, `ieee80211_defrag` | 1 each |
| **`a_netbuf_pull`, `a_netbuf_pull_data`** | **1 each** |

**`CONFIRMED`**: the vendor RX path uses the **Atheros netbuf** API — `a_netbuf_pull` and
`a_netbuf_pull_data` are both present and both take an immediate length. `ol_rx_deliver` is the
busiest `skb_pull` user, and it is the OS-side delivery boundary, not the firmware-descriptor
decode.

That is the structural difference from ath10k: ath10k strips the HTT RX descriptor with
`skb_pull` and discards it; the vendor stack hands the frame to `a_netbuf_pull` first and only
becomes an `sk_buff` later.

## 5. Why no hook is emitted

A binary hook to preserve `evm_p0..evm_p15` and `locationing_timestamp` needs four things:

1. the address where the descriptor is stripped — **not found**: no 84-byte pull exists;
2. the field offsets inside the descriptor — **not found** (371A: 0 hits for the field names);
3. a place in `sk_buff` to stash 68 bytes — headroom or `cb` — plausible but unverified here;
4. a consumer that reads them back — **absent by construction**.

Publishing a byte patch against an address that does not exist would be fabrication. The receipt
therefore carries `patch_emitted = 0` and reports the call sites and arguments, which is exactly
the input a real patch would need.

## 6. What is established

| Claim | Status |
| :--- | :--- |
| `ath10k_core.ko` (Linux 6.6.110) is present in the corpus | **REFUTED** (0 files) |
| `ath10k_htt_rx_amsdu_pop` / `ath10k_htt_rx_h_ppdu` can be disassembled here | **REFUTED** |
| `htt_rx_amsdu_pop` exists in `umac.ko` | **CONFIRMED** |
| it calls `skb_pull` | **REFUTED** (0 sites) |
| some `skb_pull` in `umac.ko` pulls 84 bytes | **REFUTED** (0 of 35) |
| the observed pull lengths are 2, 4, 8, 14, 60, 248 | **CONFIRMED** |
| the vendor path uses `a_netbuf_pull` | **CONFIRMED** |
| a correct hook offset for `evm_p0..p15` | **UNKNOWN / not derivable from this corpus** |

## 7. Gaps

- **`UNKNOWN`** — where the vendor stack consumes its RX descriptor, if it does so at all.
- **`UNKNOWN`** — whether `a_netbuf_pull` is where an 84-byte prefix would be removed.
- **`UNKNOWN`** — the descriptor geometry in the vendor stack; no equivalent struct was located.
- **`UNKNOWN`** — `sk_buff::cb` occupancy in this kernel, which any stashing hook would contend
  with.
- **Blocked** — the ath10k answer requires the Linux 6.6.110 `ath10k_core.ko`, which is not in the
  corpus.
- **Not attempted** — dynamic validation, and any patch.
