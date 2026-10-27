# Public XC / XW / XM diagnostic starter

This is a tester kit, not firmware. No installation image, kernel module,
automatic startup hook, configuration, RF command or apply script is supplied.
It does not reproduce proprietary airMAX scheduling or qualify a migration.

1. Verify SHA256SUMS (SHA256SUMS.txt is the identical compatibility alias).
2. Read PROFILE_MATRIX.json. Reported sysids are historical claims, not unique
   board identifiers or an instruction to select a firmware image.
3. On an already booted, tester-owned radio, inspect collect_capabilities.sh.
   Optionally run it manually with sh and save its JSON output yourself.
   It reads board/kernel/RAM/driver/interface metadata only. It never connects
   to another device, reads IP/MAC/configuration credentials or changes knobs.
   Missing fields stay UNKNOWN/null; metadata does not authenticate hardware.
4. Compare the saved identity to the candidate JSON for the correct family.
   Exact model/revision, RAM, flash map, DTS/calibration layout, driver ABI,
   recovery and direct physical tests still need separate qualification.

Rocket Prism / PrismStation active filtering has unqualified GPIO/HSR support:
retain the existing stock airOS environment. PBE-620 and IsoStation have no
exact profile in the held OpenWrt 24.10.4 ath79/generic inventory. A PBE-500
profile is not permission to install it on PBE-620. NanoBeam variants differ.
32 MiB XM remains stock-airOS-only here; do not infer 24.10.4 safety from a
historical script. XW/XM sysids and RAM classifications conflict across sources.

All candidate tuning is disabled and unqualified. Historical numeric values
are configuration proposals, not measured safe defaults, gains, fairness,
capacity, loaded-latency or stability evidence. No WA mac80211 module is copied
to XC or ath9k. The older XC overlay that included one is explicitly excluded.

Original proprietary firmware/configuration is not redistributed. The new
collector and packager are GPL-2.0-or-later. Official inventory provenance is
HTTPS/hash based; GPG verification and exact-board hardware acceptance are absent.
