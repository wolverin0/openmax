# FMX-0011 build manifest — OpenWrt v24.10.4 (r28959) + ath10k spectral, 2026-09-26

Summary: what was built, from which sources, with which config, on which host, with which hashes,
and how to reproduce it. Keywords: FMX-0011, OpenWrt 24.10.4, r28959, ath79/generic, LAP-120,
LiteBeam AC Gen2, NanoStation 5AC, Loco 5AC, PACKAGE_ATH_SPECTRAL, CONFIG_RELAY, ath10k-ct
2024.07.30, CT firmware FW022, gcc-12 shim, WSL caveats, sha256.
Read when: flashing the spectral image, reproducing the build, or auditing why an image differs.
Status: BUILT + exit checks PASS, **PROVISIONAL** (flaky build host), **NOT YET FLASHED**.

## 1. What

| Item | Value |
|---|---|
| Source | `https://github.com/openwrt/openwrt.git` tag `v24.10.4`, commit `78b23a26c4c98938d549e7ff5876508544e33d4d`, shallow clone |
| Revision string | `r28959-29397011cc` (identical to the stock 24.10.4 image already on the LiteAP) |
| Target | `ath79/generic`, multi-profile: `ubnt_lap-120`, `ubnt_litebeam-ac-gen2`, `ubnt_nanostation-ac`, `ubnt_nanostation-ac-loco` |
| Kernel | Linux 6.6.110 (`kernel - 6.6.110~ad3fdbaa024356925ca19332da2acf0d-r1`), `CONFIG_RELAY=y`, `CONFIG_DEBUG_FS=y` |
| Wireless | `kmod-mac80211 6.6.110.6.12.52-r1`, `kmod-ath10k-ct-smallbuffers 6.6.110.2024.07.30~ac71b14d-r2` built with `CONFIG_ATH10K_SPECTRAL=y` |
| Radio firmware | `ath10k-firmware-qca988x-ct 2020.11.08-r1` → `/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin` = `firmware-2-ct-full-community-22.bin.lede.022`, embedded version string `10.1-ct-8x-__fW-022-ecad3248` (same as the running device), sha256 `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e` |
| Extras vs stock | `PACKAGE_ATH_DEBUG`, `PACKAGE_ATH_SPECTRAL`, `MAC80211_DEBUGFS`, `ATH_DFS`, `iperf3`, `tcpdump-mini`, `iw-full`, `ethtool`; target `gdb` disabled; `DEVEL`+`BUILD_LOG` (diagnostics only) |
| Feeds | as recorded in `feeds.buildinfo` beside the images |

Why: stock 24.10.4 omits `PACKAGE_ATH_SPECTRAL` (→ no `CONFIG_RELAY`, no `spectral_scan_*` debugfs),
settled from source 2026-09-20 (`docs/QCA988X_CONTROL_BOUNDARY.md` §4a). Everything else is kept
identical to stock on purpose so that FMX-0010/C1 changes exactly one variable.

## 2. Output (`firmware/openwrt/futuramax-r28959-spectral/`)

| sha256 | file | bytes |
|---|---|---|
| `8e0cbba1f7b85929ef75c74f3ec1b935dfb631afaf404937b8a88a38043a85e3` | `openwrt-ath79-generic-ubnt_lap-120-squashfs-factory.bin` | 7,013,016 |
| `6a1b8cf3ef5bb9e0280b1f162b620c1391625865012c7ac7d8f9d3e826c1cab6` | `openwrt-ath79-generic-ubnt_lap-120-squashfs-sysupgrade.bin` | 7,013,149 |
| `f418bfa010e2a23cab8edd871ebb0518972e1464b6c12bfc319835fe4e6db0df` | `openwrt-ath79-generic-ubnt_litebeam-ac-gen2-squashfs-factory.bin` | 7,013,016 |
| `30e8bf83400c4aecc4a0f4490c2b4cd6693dc2a56e5f4556f95341e8af963f2a` | `openwrt-ath79-generic-ubnt_litebeam-ac-gen2-squashfs-sysupgrade.bin` | 7,013,167 |
| `f9f079c56b04afec1f668b6bfe8c49a50f6ad336aee446377a6aefc64999935d` | `openwrt-ath79-generic-ubnt_nanostation-ac-squashfs-factory.bin` | 7,013,016 |
| `915977092c2a673c2bbdfb02e3f521575e632d3a1cb5ff3eee2549ce82d125ee` | `openwrt-ath79-generic-ubnt_nanostation-ac-squashfs-sysupgrade.bin` | 7,013,163 |
| `56c6dc861cf56c3317894ec7e1146fdba0980e62ade9a9dd3b1aa762dedb46aa` | `openwrt-ath79-generic-ubnt_nanostation-ac-loco-squashfs-factory.bin` | 7,013,016 |
| `7fbb6b7a4bb4dec1849082f99f17ca91cd818fff817fdc8e544e6e37fcdd0f00` | `openwrt-ath79-generic-ubnt_nanostation-ac-loco-squashfs-sysupgrade.bin` | 7,013,173 |

Also there: `*-initramfs-kernel.bin` (RAM-boot images; need a serial/tftpboot path we do not have),
`sha256sums` (upstream-generated), `openwrt-ath79-generic.manifest`, `profiles.json`,
`config.buildinfo`, `feeds.buildinfo`, `version.buildinfo`, `dot.config` (full), `futuramax.diffconfig`,
`build.log`. File names lack the `24.10.4-` prefix because a shallow clone has no
`CONFIG_VERSION_NUMBER`; the revision string proves the tree.

**Which one to flash on the LiteAP:** `…ubnt_lap-120-squashfs-sysupgrade.bin` via `sysupgrade`
from the running OpenWrt (routine, keeps u-boot/env/ART untouched — `docs/EXPERIMENTS.md`
"FMX-0011 needs a reflash — but the EASY kind"). Factory images are for the dd-unlock install
path on radios still on airOS (see `safety/recovery/install_openwrt_ddunlock.py`).

## 3. Exit checks — all PASS (2026-09-26, `exit-checks.sh`)

1. All 8 squashfs images present.
2. Kernel `.config`: `CONFIG_RELAY=y`, `CONFIG_DEBUG_FS=y`.
3. `PACKAGE_ATH_SPECTRAL=y` wired into `package/kernel/ath10k-ct/Makefile` (`CONFIG_ATH10K_SPECTRAL=y`);
   `readelf` on `ath10k_core.ko` shows `ath10k_spectral_process_fft` (defined) and `relay_open` (UND,
   imported from the kernel) — i.e. `spectral.c` was compiled in.
4. Shipped `firmware-2.bin` embeds `10.1-ct-8x-__fW-022-ecad3248` (same string the device reports).
5. `mac80211.ko` carries debugfs code.
6. Manifest lists the expected packages and revision `r28959-29397011cc`.

Still UNVERIFIED (needs the radio): that `/sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl`
actually appears, that `spectral_scan0` yields FFT samples on QCA988x hw2.0 with FW022, and that
the image boots and persists config across a reboot.

## 4. How it was built (reproduce)

Host: WSL Ubuntu 24.04 on the operator's Windows 10 PC, 8 vCPU, 8 GB. Steps, all in this directory:

```
# once (WSL):  apt deps as root via `wsl -u root`, then
git clone --depth 1 -b v24.10.4 https://github.com/openwrt/openwrt.git ~/futuramax/openwrt-24.10.4
cd ~/futuramax/openwrt-24.10.4 && ./scripts/feeds update -a && ./scripts/feeds install -a
cp <repo>/tools/openwrt-build/futuramax-24.10.4.seed.config .config && make defconfig
bash <repo>/tools/openwrt-build/hostcc-shim.sh          # gcc-12 for HOST tools (see §5)
# from Windows PowerShell (keeps a wsl.exe client attached for the whole build):
Start-Process wsl.exe -ArgumentList '-- bash -c "bash \"<repo-mnt>/tools/openwrt-build/run-attached.sh\" <label>"' -WindowStyle Hidden
# then: exit-checks.sh, copy-artifacts.sh <dest-name>
```

`futuramax-24.10.4.diffconfig` is the authoritative delta from defaults; `dot.config` beside the
images is the full config actually used. `build.sh` uses `JOBS=6`, a bounded retry loop and a
clean Linux-only `PATH`.

## 5. Caveats — read before trusting this image

- **Flaky build host.** During this build the WSL VM (WSL 2.7.14, pre-release kernel 6.18.33.2,
  `.wslconfig` `autoMemoryReclaim=gradual`) produced: a kernel deadlock in the mmap path (D-state at
  `__vma_start_write`, cleared by `wsl --terminate Ubuntu`), a deterministic gcc-13 ICE compiling host
  cmake (worked around with a gcc-12 shim), a gcc-12 segfault compiling target gdb (gdb dropped), and a
  target `lto1` ICE in libnftnl that passed on rerun. The delivered images come from a single clean pass
  (`build.log`: `MAKE_ATTEMPT=1 … BUILD_EXIT=0`), but random memory faults can miscompile silently.
  Treat the image as **provisional** until it is validated on the LiteAP or rebuilt on a healthy Linux
  host. MemoryMaster claim `mm-d90b` has the full diagnosis.
- **Windows PATH leak.** WSL appends the Windows PATH; `package/install` then fails in
  `find -execdir` ("relative path … included in the PATH"). `build.sh` exports a clean PATH.
- **Host compiler.** Host tools were compiled with gcc-12 (shim), target code with the OpenWrt
  cross gcc 13.3.0 — the target toolchain is unaffected by the shim.
- **No LAP-GPS profile exists in OpenWrt 24.10.4** (`target/linux/ath79/image/generic-ubnt.mk`).
  The testbed plan naming LAP-GPS as the APs cannot be served by this build.
