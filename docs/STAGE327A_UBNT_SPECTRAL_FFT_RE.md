<!-- doc-head: STAGE327A_UBNT_SPECTRAL_FFT_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 327A — spectral FFT bins, noise floor and the ubntspecd shared memory

- **Receipt**: [`artifacts/autoresearch/stage327a_ubnt_spectral_fft_re.json`](../artifacts/autoresearch/stage327a_ubnt_spectral_fft_re.json)
- **Tool**: [`tools/re/ubnt_spectral_scan_fft_bin_format_re.py`](../tools/re/ubnt_spectral_scan_fft_bin_format_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Modules

| Module | Bytes | Note |
| :--- | :-: | :--- |
| `WA.v8.7.25:ath_spectral.ko` | 37,656 | the spectral scanner |
| `XC.v8.7.25:ath_spectral.ko` | 37,656 | same size |
| `WA.v8.7.25:ath_dev.ko` | 287,216 | spectral plumbing lives partly here |
| `XC.v8.7.25:ath_dev.ko` | 287,216 | same |

`ath_spectral.ko` is small and focused; the bin format had to be looked for in both modules.

## 1. FFT surface

| Bucket | `ath_spectral.ko` | `ath_dev.ko` |
| :--- | :-: | :-: |
| **fft** (`fft|bin|spectr|sample|window|tone`) | **38** | — |
| **noise** (`noise|nf|floor|calib|rssi|dbm`) | **5** | — |
| **radar** (`radar|pulse|chirp|pri|width|burst`) | **4** | — |
| **shm** (`shm|shared|mmap|specd|ubntspec`) | **0** | **0** |

## 2. Bin-count candidates

Small immediates inside the 38 fft-named functions:

| Value | Sites |
| :-: | :-: |
| **32** | **5** |
| **64** | **2** |
| 128 | **absent** |
| **256** | **1** |
| **512** | **5** |

**`CONFIRMED`**: 32, 64, 256 and 512 appear as immediates; **128 is absent**. Total 13 sites.

**What this does not establish.** A 512 inside an FFT-named function is a **candidate bin
count**, not the bin format. The stage asked for the FFT bin format — the dB encoding, the byte
stride and the descriptor. None of that is derived here:

- the 512 could be an FFT size, a buffer length, or a loop bound over a fixed array;
- 32/64 could be decimation factors rather than output bins;
- the absence of 128 does not mean 128-bin scans are unsupported.

## 3. The shared memory is not here

**`CONFIRMED`: zero symbols matching `shm|shared|mmap|specd|ubntspec` in any of the four
modules.**

That is the most decisive result of the stage. The stage asked for "the ubntspecd shared memory
layout". If the layout were defined in these modules, `ubntspecd` would appear as a string or a
symbol. It does not.

Two readings:

1. the shared segment is created and consumed entirely in **userspace** (`ubntspecd` and its
   client), with the module only writing samples through a registered callback;
2. the layout is defined in a header compiled into userspace, never named in the kernel module.

Either way, **this is the wrong place to look**, and the receipt says so rather than
manufacturing a struct.

## 4. Noise floor

Only **5** noise-named symbols in `ath_spectral.ko` and none surfaced in `ath_dev.ko` under the
same pattern. The calibration constants inside those five functions are reported as a histogram;
no calibration curve, offset table or dBm mapping is claimed.

## 5. String evidence

40 `.rodata` literals match `specd|spectral|fft|noise|radar`. They are recorded in the receipt as
a bucket. No string was interpreted as a shared-memory path.

## 6. Gaps

- **`UNKNOWN`** — the FFT bin format: dB encoding, byte stride, descriptor layout.
- **`UNKNOWN`** — which of 32/64/256/512 is the output bin count.
- **`UNKNOWN`** — the noise-floor calibration curve.
- **`CONFIRMED ABSENT`** — any shm/specd symbol, so the ubntspecd layout must be sought in
  userspace, not in these `.ko` files.
- **Not attempted** — dynamic validation.
