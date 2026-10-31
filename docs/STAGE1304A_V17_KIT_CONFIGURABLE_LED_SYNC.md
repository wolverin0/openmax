<!-- doc-head: 1304A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# v17 PtP configurable RSSI LED overlay synchronization

Status: CONFIRMED_STATIC; attribution: local packaging / OpenWrt procd.

The existing v17 queue/radio script remains byte-identical.
The companion adds the canonical RSSI service, procd init, configuration and first-boot hook.
Production defaults: LED1=-80, LED2=-73, LED3=-65, LED4=-60 dBm, inclusive.
The separate live bench65 profile remains in Stage1302 evidence and is not packaged here.
Use the verified stage1304a_v17_rssi_led_overlay.tar for SquashFS overlay transfer.
Extract on a POSIX filesystem preserving archive modes: scripts 0755, config 0644.
TAR members, exact bytes, SHA256 and modes are validated independently of host filesystem modes.
Windows/DrvFS may expose 0777; observed host modes are recorded and do not establish target modes.
The first-boot hook also requires regular files and chmods shell0755/config0644 before start.
The service parses LED1_DBM..LED4_DBM as integer data, accepts --config and emits JSON telemetry.
Real AUTO readback is written atomically to /tmp/fmx_rssi_leds_status.json.
On OpenWrt first boot, rc.common enable creates the normal S<START> service symlink.
No interface name or LED sysfs prefix is fixed in this overlay: the canonical daemon discovers them.
A Linux deployment may materialize the same overlay directly into the target root and execute the hook.
This receipt proves source/copy hashes and boot wiring only; live acceptance is separate.
Historical Stage1262 receipts and documentation are preserved, with hashes recorded here.
No radio commands, partition writes, image flashing or SSH were executed by this builder.
