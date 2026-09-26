# Prompt to paste into pane 20 after `/clear`

Copy everything inside the fence. It is deliberately short — the repo carries the detail.

```
You are the principal engineer for FuturaMAX. Read these in order before doing anything else:

1. AGENTS.md at the repo root — the engineering constitution. Read it completely.
2. handoffs/handoff-2026-08-08T23-45-00-b7c412.md — status delta and, importantly, three
   RETRACTED conclusions from the previous session. Do not cite them.
3. docs/DECISIONS.md — D-0001 through D-0005.
4. docs/CURRENT_STATE.md and docs/EXPERIMENTS.md.

FuturaMAX is a CUSTOM FIRMWARE project for Ubiquiti airMAX AC hardware. It is not a research
report and it is not about tuning airOS config. If you find yourself optimising Ubiquiti's
config file, you have drifted — stop and re-read the handoff.

Do not re-read the raw research corpus under research/ unless verifying a specific claim. It
is an input, not the deliverable.

Your immediate task is the one blocker gating everything physical:

Determine how OpenWrt gets installed on our lab LiteAP AC (LAP-120, sysid 0xe8e5, airOS
8.5.12, 0 clients, reachable on the local network with factory-default credentials), and how
to recover it if a flash fails. The OpenWrt ubnt_lap-120 factory and sysupgrade images are
already downloaded and SHA-256 verified in firmware/openwrt/. The factory image carries magic
'OPEN' and airOS fwupdate validates signatures, so the install path is unresolved.

Read the OpenWrt device page for ubnt_lap-120 THROUGH A BROWSER (claude-in-chrome) — plain
HTTP gets a bot challenge from openwrt.org. Establish the install method and the TFTP/
bootloader recovery procedure, write both into docs/EXPERIMENTS.md, then run FMX-0002
(recovery qualification).

Do not flash anything until recovery is proven on that unit. Never write u-boot, u-boot-env,
or EEPROM. Lab unit only — production radios are read-only.

Work autonomously. Do not ask permission for obvious non-destructive next steps within this
task; make the engineering call, document it in docs/DECISIONS.md, and continue. Ask only for
physical actions I must perform or for genuinely irreversible operations.
```

## Why this prompt is short

The previous handoff failed by trying to *carry* the project's context in prose and losing the
goal in the process. This one carries almost nothing: it points at `AGENTS.md` (the
constitution), names the anti-goal explicitly, and gives one concrete task with its safety
boundary. Everything else is on disk and current.

## Secondary tasks, only if the primary is blocked

- Clone `SVoxel/R7500` (218 MB) and grep for `umac`, `ol_ath`, `AR9888`, `config.wlan`. Its
  manifest states `IPQ8064 + QCA8337 + QT2518 + QCA9880` — our chip, right era, vendor GPL
  lineage. Unresolved because GitHub API rate-limited, **not** because it is dead.
- Capture beacons from any airMAX AP in monitor mode and decode vendor IE **element 221, OUI
  `00:15:6D`**. Needs no hardware we lack and no permission.
- A ChatGPT search is mid-flight at `https://chatgpt.com/c/6a77b935-6bc0-83e9-b40f-ed2006f2e18a`.
  **Verify every URL it returns** — half of the previous LLM-sourced research was false, and one
  cited repository did not exist at all.
