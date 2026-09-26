# Research assignment: find the source for `umac.ko` (QCA988x / AR9888 offload driver)

Summary: a bounded, high-value hunt for the GPL-obligated source of the Qualcomm Atheros
`umac` WLAN driver, 10.1/10.2 branch, as shipped on Ubiquiti airMAX AC hardware.
Keywords: umac.ko, qca-wifi-10.1, qca-wifi-10.2, LSDK-WLAN, QSDK, ol_ath, AR9888, QCA988x,
GPL source release, Dual BSD/GPL. Read when: assigning this to a researcher, or resuming it.
Status: CURRENT (2026-08-08). Give the section "THE PROMPT" verbatim to the researcher.

## Context for whoever assigns this (not part of the prompt)

We tore down airOS 8.5.12/8.7.22 from Ubiquiti's public firmware and established:

- The radio driver stack is Qualcomm's vendor "offload" driver, **not** ath10k:
  `ath_pci: 10.1.467 (Atheros/multi-bss)`, with modules `umac.ko`, `ath_hal.ko`, `ath_dev.ko`,
  `ath_rate_atheros.ko`, `ath_spectral.ko`.
- **`umac.ko` (2,361,256 B) declares `license=Dual BSD/GPL`, author "Atheros Communications, Inc."**
  Every other Atheros module (`ath_hal`, `ath_dev`, `ath_dfs`, `ath_rate_atheros`,
  `ath_spectral`) declares `Proprietary`, as do all `ubnt_*` modules.
- `umac.ko` embeds three QCA988x radio-firmware images as symbols
  (`athwlan_AR9888v2_ptp_bin`, `_ptmp_ap_bin`, `_ptmp_sta_bin`).
- Qualcomm's own build docs reference `LSDK-WLAN-10.1.354.tgz` and
  `make BOARD_TYPE=ap135 11AC_OFFLOAD=1`.
- The public OpenWrt feed `qca-wifi-10.2` only *packages* the driver; its Makefile fetches from
  `ssh://qca-git01.qualcomm.com:29418/wifi/qca-wifi-10.2.git` — Qualcomm-internal, not public.

**Why it matters:** if the 10.1/10.2 `umac`/`ol_ath` source is obtainable, we can build our own
scheduler in the same architectural position Ubiquiti used (their `ubnt_poll_host.ko` sits on
top of `umac.ko`), instead of fighting mainline ath10k's much narrower control surface. This
is potentially the difference between a constrained project and an unconstrained one.

**The legal hook:** a `Dual BSD/GPL` kernel module distributed in a shipped product carries a
source-availability obligation. That is the strongest lead and most of the prompt leans on it.

---

## THE PROMPT

> I need you to find the **source code** for a specific Qualcomm Atheros Linux kernel module,
> or establish with evidence that it is not publicly available.
>
> ### What I am looking for
>
> The WLAN driver known as **`qca-wifi`** / **`umac`** / the Atheros "**offload**" (`ol_ath`)
> driver, **branch 10.1 or 10.2**, for the **AR9888 / QCA988x** 802.11ac chipset. Also known in
> Qualcomm build packages as **`LSDK-WLAN-10.1.x`**.
>
> Concretely, any of these would be a hit:
> - a tarball named like `LSDK-WLAN-10.1.354.tgz`, `LSDK-10.1.354.tgz`, `LSDK-SPECTRAL-10.1.354.tgz`
> - a source tree named `qca-wifi-10.1` or `qca-wifi-10.2`
> - a directory tree containing `os/linux/` plus `umac/`, `lmac/`, `hal/`, and a file like
>   `os/linux/configs/config.wlan.*`
> - source that builds a kernel module named `umac.ko` for MIPS, referencing symbols such as
>   `ol_ath_attach`, `ol_transfer_bin_file`, `athwlan_AR9888v2_*`
>
> ### The strongest angle: GPL source obligations
>
> `umac.ko` declares `license=Dual BSD/GPL`. Any vendor that shipped a Linux product containing
> it has an obligation to publish the corresponding source. So search **vendor GPL source
> releases**, not just Qualcomm. Specifically look for GPL/open-source tarballs from companies
> that shipped **QCA988x / AR9888-based 802.11ac outdoor or AP products around 2013–2018**:
>
> - **Ubiquiti** (airOS 8.x GPL releases — highest priority; they ship exactly this module)
> - Cambium Networks (ePMP), Mimosa, MikroTik, Netgear, TP-Link, EnGenius, Open-Mesh / Datto,
>   Comfast, Zyxel, Ruckus, Aruba, Altai, Ligowave, IgniteNet, Wallys, Compex
> - ODMs and reference designs: the **AP135 / AP136 / AP152** Qualcomm reference boards
>
> Useful search phrasings:
> - `Ubiquiti GPL source airOS 8 download`
> - `"qca-wifi" 10.2 source tarball`
> - `"LSDK-WLAN" 10.1 download`
> - `AR9888 "11AC_OFFLOAD" driver source`
> - `"config.wlan" qca-wifi umac lmac source`
> - `<vendor name> GPL source code request 802.11ac QCA9880`
> - site-restricted searches on `gpl.back2roots.org`, `sourceforge`, `archive.org`,
>   `git.openwrt.org`, `github.com`, `gitlab.com`, `codeberg.org`
>
> Also worth trying: **archive.org / Wayback Machine snapshots of `codeaurora.org`**, especially
> `www.codeaurora.org/mirrored_source/external/wfr/` and `source.codeaurora.org/quic/qsdk/*`.
> Codeaurora was shut down and migrated to CodeLinaro/GitHub; some content did not survive the
> move and only exists in archives.
>
> ### What I have already ruled out — do not re-report these
>
> - `github.com/CodeLinaro-mirror/qsdk_oss_system_openwrt_feeds_qca-wifi-10.2` — packaging only.
>   Its Makefile fetches from `ssh://qca-git01.qualcomm.com:29418/wifi/qca-wifi-10.2.git`, which
>   is Qualcomm-internal and not publicly reachable.
> - `www.codeaurora.org/mirrored_source/external/wfr/` — returns HTTP 404 today.
> - `source.codeaurora.org` — DNS no longer resolves.
> - **`github.com/CodeLinaro-mirror/qsdk_wifi_qca-wifi-oss` — CLONED AND CHECKED 2026-08-08.**
>   Does **not** contain the QCA988x driver. `AR9888`: 0 matches. `athwlan`: 0 matches. The one
>   `QCA988` hit is `TARGET_TYPE_QCA9888` (a different, Wave-2 chip). `umac/` holds only
>   `cfr/ cp_stats/ dfs/ mlme/` — modern common components, not the `ol_ath` tree. Chipset
>   references are dominated by AR9300 (ath9k-era, under `direct_attach/`).
>   **Trap to avoid:** it has branches named `NHSS.QSDK.10.0.*`. Those are **QSDK release 10.0**,
>   NOT the `qca-wifi` **driver** branch 10.1/10.2. Different numbering schemes. Do not report a
>   QSDK 10.x branch as if it were the 10.1/10.2 driver.
> - Mainline `ath10k` — this is a *different* driver. I already have it. Not what I want.
> - `github.com/kvalo/ath10k-firmware` — 404, and it is firmware blobs, not driver source.
>
> ### What counts as a real answer
>
> For each candidate you find, give me:
> 1. **Direct URL** to the file or repository (not a search-results page, not a landing page)
> 2. **What it actually contains** — did you open it and see `umac/` or `os/linux/configs/`?
> 3. **Version / branch** — 10.1.x, 10.2.x, 10.4, 11.x, or unknown
> 4. **Whether AR9888 / QCA988x is supported** — grep the tree for `AR9888`, `QCA988`,
>    `9888`, `ol_ath`. A 10.4 or 11.x tree probably targets newer IPQ/AX silicon and is likely
>    useless to me — say so rather than reporting it as a hit
> 5. **Licence file(s)** present in the tree
> 6. **Size and format** so I know what I am downloading
>
> ### Ground rules
>
> - Do **not** report a link you have not opened.
> - Do **not** give me the mainline ath10k driver, ath9k, or any AX/Wi-Fi-6 driver.
> - "Probably here" is not an answer. Either you opened it and saw the source tree, or the
>   result is negative.
> - A well-evidenced **negative** ("I searched X, Y, Z; here is what each returned; the source
>   appears to be Qualcomm-internal") is a genuinely valuable outcome. Do not pad with
>   near-misses to look productive.
> - I am not asking anyone to bypass access controls, leak NDA material, or obtain anything
>   improperly. I am looking for **publicly published source**, including source that vendors
>   are obliged to publish under the GPL. If the honest answer is that it was never published,
>   say that.
>
> ### Bonus, only if the main hunt is exhausted
>
> Has anyone publicly documented **how Ubiquiti's airMAX polling MAC integrates with this
> driver** — reverse engineering of `ubnt_poll_host`, the airMAX information elements exchanged
> in association/beacon frames, or the airMAX TDMA frame structure? Blog posts, conference
> talks, theses, forum threads by engineers, or patent claims all count.
