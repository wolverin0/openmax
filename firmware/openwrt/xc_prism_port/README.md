<!-- doc-head: Offline XC Prism selector and disabled device-tree drafts -->
Six-record native selector reproduced as an offline state-machine model.
No GPIO, netdevice, RF, flash, module, service or network backend exists.
GPIO7/wifi1 blanking is requested intent; routing and polarity remain UNKNOWN.
DTS files are experimental, RF/storage/Ethernet disabled, not boot-qualified.
<!-- /doc-head -->

# XC Prism port: offline prototype

This is enabling work for D5 and the XC board-specific port plan. It is not an
image, installer, upstream-supported profile or physical AirPrism qualification.
Neither the selector test nor a parsed DTS proves filtering, GPS-sync or TDMA.

## Evidence and selection

Inputs held in this repository:

| Input | SHA256 |
| --- | --- |
| `artifacts/adversarial_review_stage10_11/prism_table.json` | `57a91beecd7329e1063dab757c35dc9173fdb9cde67fb1921d37d6c2dae99b6a` |
| `artifacts/adversarial_review_stage10_11/selected_disassembly.json` | `be9b4a0adc98ab06ce0599b65f788f650352374bd3b0e0eebbeb5e35f6095ee8` |

See [Stage11 selector analysis](../../../docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md)
and [D5 plan](../../../docs/STAGE12_XC_PRISM_AND_WA_GPS_OPENWRT_PORT_PLAN.md).
The exact XC 8.7.25 UMAC evidence is `ubnt_prism_hook` at `.text+0xac874`,
selector `.text+0xabeb0..0xabf10`, table `.data+0x1510`, six 44-byte records.
The original stage field is a bitmask; first matching row wins, in original order.
Both occupied edges must fit the row and requested width must not exceed its
maximum. Native `.text+0xac920` computes `half = width >> 1`; this model preserves
that integer truncation for odd widths rather than claiming half-MHz precision.
Stage1 supplies GPIO15/16; stage2 supplies GPIO13/14. Output integer bits are
`bit0=GPIO13, bit1=GPIO14, bit2=GPIO15, bit3=GPIO16`.

The broad fallback rows are filter choices, **not legal frequency permissions**.
Inputs are bounded canonical integers (width1..160MHz); malformed and unmatched
inputs are rejected. Native default values outside the matched table are not
used as permission to release the model interlock.

## Run locally, without a device

```sh
sh fmx-airprism-tuner.sh                         # PLAN_ONLY, no files
sh fmx-airprism-tuner.sh --dry-run 5240 80       # trace only, no files
sh fmx-airprism-tuner.sh --fixture NEW_DIR 5775 80
sh fmx-airprism-tuner.sh --fixture NEW_FAIL_DIR 5775 80 gpio13
```

Fixture outputs are only `owner.txt`, `trace.log` and `state.txt` in a newly
created exclusive directory. No existing output is adopted. Success models:
blank -> write15 -> write16 -> write13 -> write14 -> verify -> logical unblank.
Every write requires confirmed **model** blanking. Injected blank failure leaves
state unknown and performs no switch; later failures retain confirmed model
blanking. Error/signal handling never unblanks. `rf_enabled=0` is invariant,
including success. `--live` and all unknown modes always fail. No background
daemon, arbitrary executable backend or sysfs option is provided.

GPIO7 on wifi1 is an operator-requested hypothesis only. No polarity, GPIO-chip
number or electrical LNA connection is assigned. Keeping wifi1 powered off as a
future safety condition is distinct from hardware per-TX LNA blanking; neither
is measured or implemented by this model. Physical settle time, RF-off proof,
simultaneous pin transition behavior and feedback remain UNKNOWN. A production
backend must not be enabled by replacing the fixture writes without separate
exact-board review and measurement.

## Device-tree scope

The three drafts reference the existing OpenWrt24.10.4 `qca955x.dtsi` family,
not the Rocket-Lite's `qca955x_ubnt_xc.dtsi` board template. Local inspected base
SHA256: `1a0396c03a935744260d37ec9b7739ed5a0ce820beaa6b309b42451c460e6959`.
For comparison only, the sibling XC template SHA is
`e2a98feefdf747a646fd10c4885d077267750f7063a3d3729aafb0caf23cad27`.
No borrowed ART/EEPROM offsets, partition map, MAC address, RAM size, PHY wiring,
LED/reset GPIOs or gpio-hogs are installed. SPI, Ethernet/MDIO, PCI radios and
AHB wmac are explicitly disabled. Protected flash remains inaccessible through
this draft; it has no partition definitions and cannot write bootloader,
factory, calibration or MAC storage. These files must not be used to boot/flash.

QCA9558 is the requested filename/port hypothesis, not proven exact silicon on
each BOM. Rocket e7e9 has stock intake, e7e7 is a separate variant. PrismStation
table identities e7e6/e7e8 do not establish requested e7eb. GPS, HSR transport,
passive Horn and active filtering remain separate qualifications. No GPS, HSR
or RF-enable binding is invented. There is no Makefile image registration.

## Local checks and limits

```powershell
& 'C:/Program Files/Git/bin/bash.exe' -n firmware/openwrt/xc_prism_port/fmx-airprism-tuner.sh
python -B firmware/openwrt/xc_prism_port/test_xc_prism_offline.py
```

Tests use disposable host directories and the already installed Git Bash only:
six-row/hash binding; first-match/edge/max-width/odd-width vectors; ordering;
failure at blank, each of four switches, verification and release; invalid input;
exclusive output; disabled DTS/no inferred storage/calibration bindings.
DTS compilation is **NOT_RUN**: no toolchain/install or copied include chain is
introduced for this offline delivery. Structural checks do not equal dtc/schema
validation, firmware build, boot, recovery or RF acceptance. No proprietary code
is copied: the selector is a small factual table/state-machine model.
