<!-- doc-head: 1262A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# v17 PtP RSSI LED companion and SquashFS overlay integration

Status: CONFIRMED_STATIC; attribution: local packaging / OpenWrt procd.

The existing v17 queue/radio script remains byte-identical.
The companion adds the canonical RSSI service, procd init and first-boot enable/start hook.
Copy rssi_led_overlay/ into the SquashFS root before packing, preserving executable mode 0755.
On OpenWrt first boot, rc.common enable creates the normal S<START> service symlink.
No interface name or LED sysfs prefix is fixed in this overlay: the canonical daemon discovers them.
A Linux deployment may materialize the same overlay directly into the target root and execute the hook.
This receipt proves source/copy hashes and boot wiring only; physical LEDs need the Stage1261 live receipt.
No radio commands, partition writes, image flashing or SSH were executed by this builder.
