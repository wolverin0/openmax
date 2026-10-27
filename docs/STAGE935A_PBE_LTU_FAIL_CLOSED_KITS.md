<!-- doc-head: 935A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PBE/LBE and LTU v23 fail-closed active kit boundary

Active source boundary: 42 entrypoints:2 explicit native transactions and 40 retired legacy actuators.

All active defaults return PLANNED without getters or device commands.
Legacy entrypoints reject apply/verify/rollback; selecting a native replacement is an explicit operator decision.
Native engines require exact board, revision, kernel, driver, firmware and interface-index identity.
PBE/LBE uses an explicit PHY; LTU uses PHY=none and a native driver identity, never a mac80211 assumption.
The current LTU board getter contract requires ubus; unavailable native getters block apply.
Transient scope: egress tx_queue_len1000 and netdev_max_backlog1000; no radio reload or firmware activation.
Optional --uci-mode ram edits only network.lan.mtu to1500, requires no prior pending changes, and never commits/reloads.
Rollback reverts only that UCI key and verifies the original value and empty pending changes.
qdisc-mode auto uses tc when present; tc errors never fall back. sysfs-default requires kernel default fq_codel.
Default-policy readback does not establish an existing active root qdisc or custom tc parameters.
Snapshots must be root-owned0700 directories with0600 single-link regular files; phase writes use noclobber.
Every changed knob is read back; rollback is verified, and restoration failure reports ROLLBACK_FAILED.
103 historical public_release/public_assets source snapshots remain immutable and excluded from v23 packaging.
Original retired source bytes are retained in local Git metadata; credential-bearing legacy sources are not public payloads.
Static-source provenance is not native acceptance, successful conversion, radio performance or safe flash approval.
Physical acceptance, LTU native compatibility and runtime performance: UNKNOWN.
