<!-- doc-head: 984A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# stage984a guarded ptp startup watchdog

A source-bound startup watchdog requires an already verified native RAM transaction and explicit --apply.
Default inspection performs no getters. Explicit channel class selects45s non-DFS or120s DFS; unknown class fails.
The fixed sibling fmx_pbe_lbe_runtime_transaction.sh must match the supplied SHA256 and root0755 single-link metadata.
Native identity/snapshot validation is delegated to that reviewed exact source, under lock before arming.
Trusted readback immediately assigns rollback responsibility before any watchdog snapshot IO.
Every arming mkdir/write failure and early signal restores without requiring a writable watchdog directory.
A failed state record is reported separately from native rollback/readback; false restoration still exits70.
Monotonic /proc/uptime checks bracket every probe and native verification; late success cannot disarm the deadline.
Unreachable startup link dispatches verified native --rollback; probe/clock/sleep failures and signals do the same once armed.
Failed rollback/readback is ROLLBACK_FAILED, never safe. A watch directory cannot restart its original deadline.
Healthy exit proves only the fresh ping plus native configuration readback at that moment.
It does not prove ongoing uptime, zero false positives, factory bootability or physical interoperability.
A later --verify of a rolled-back event fails closed rather than mutating or inventing fresh baseline proof.
No flash, reboot, vendor firmware restore, global DHCP change or protected partition operation is implemented.
Physical acceptance remains UNKNOWN; research and memory ingestion remain deferred offline.
