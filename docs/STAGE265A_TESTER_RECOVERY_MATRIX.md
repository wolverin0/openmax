<!-- doc-head: Stage265A gated public tester troubleshooting and recovery guidance -->
Two public guides share one evidence-bound matrix; no recovery was executed.
<!-- /doc-head -->

# Stage265A

Parent: reproducible public firmware and safe recovery documentation.
Question: can a tester distinguish first configuration, TFTP, raw partition
recovery and conditional PtP migration without mistaking one image format for another?

`python tools/firmware/update_stage265a_tester_recovery_matrix.py` checks pinned
Stage138/157 receipts and the actual raw-image bytes before updating either guide.
It rejects missing/drifted evidence and ambiguous generated-section markers.
Both guides must remain below 220 lines with one initial doc-head pair.
The dedicated receipt records sources, resulting guide hashes and line counts.

The matrix covers disabled public Wi-Fi, wrong subnet/VLAN, boot failure,
stock recovery, PtP association without data, WDS/admitter faults, regressions
and image mismatch. TFTP 192.168.1.20 requires exact board-specific recovery
confirmation. It never treats a raw firmware-partition payload as a TFTP image.
The legacy 8711 filename differs from Stage157's declared v8.7.25 source.
The historical mtd2 mapping is not portable: inspect partition names/geometry
and recovery/backup evidence before any separately authorized write.

Stage138 is static analysis. STA-first or applied ptpmode=0 ordering is conditional;
the public Wi-Fi-disabled kit has no unattended OTA migration/watchdog profile.
No flash command is executed by the updater or its tests. Boot, restore and RF
acceptance remain UNKNOWN. This stage changes documentation in the external controller.
