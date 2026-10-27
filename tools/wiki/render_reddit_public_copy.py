#!/usr/bin/env python3
"""Render the two local Reddit drafts from one explicit, qualified content model."""
from __future__ import annotations
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"
DISCOVERIES = [
 (1,"Protect authentication daemons from OOM on 64 MiB boards","Linux","Memory guard; not unlimited load capacity"),
 (2,"Bound mac80211 FQ memory","mac80211","Use limits suitable for the exact RAM class"),
 (3,"ETH_P_TEB 0x6558 WDS decapsulation","mac80211","Exact ABI and image required"),
 (4,"Two-stage vendor-IE withdrawal interoperability hypothesis","airMAX","Public kit does not prove stock-CPE zero-touch acceptance"),
 (5,"Big-endian MIPS iperf3 JSON crash","userspace","Use plain-text output; no iperf3 JSON mode"),
 (6,"Separate AirPrism GPIO filters, HSR and passive ISO hardware","hardware","Active-filter support needs exact hardware qualification"),
 (7,"airOS rc.poststart versus cron persistence","airOS","Saved configuration is not cold-boot proof"),
 (8,"LTU FPGA architecture and 4096-QAM rate-table analysis","LTU","Binary presence does not establish RF operation"),
 (9,"32-CPE sector topology and backhaul fault isolation","network","Topology-specific evidence; no migration approval"),
 (10,"AP ACK pacing and relay/capacity crossover models","controller","Models are not measured subscriber capacity"),
 (11,"ubnt_poll_host 16-integer control vector","airMAX","Validate the exact handler and bounds"),
 (12,"ZeroClaw external-controller architecture","controller","Architecture proposal, not firmware feature acceptance"),
 (13,"Multi-VDEV cooperative CPE relay","controller","Feasibility depends on the control boundary"),
 (14,"PowerBeam M5 XW diversity behavior","ath9k","Board-specific, not an AC feature"),
 (15,"2.4 GHz Rocket 2AC Prism and Loco M2 experiments","hardware","Separate band and driver populations"),
 (16,"OpenWrt BusyBox ip-link tool behavior","userspace","Tool capability must be checked on the installed build"),
 (17,"LTU AME/EAB bug catalogue 01-08","LTU","Static/runtime evidence and memory impact remain distinct"),
 (18,"XW rate-control cold-start MCS0 airtime cost","ath9k","Warm-up changes must not hide failed windows"),
 (19,"AQL threshold/high-limit interaction and CoDel drops","mac80211","A configured knob is not a measured actuator"),
 (20,"XC daprot symbol mapping and AirPrism stage-one bank","airMAX","Symbol identity is build-specific"),
 (21,"ATPC/timing vector layout and CPU-class budgets","Linux/airMAX","Do not transfer budgets between CPU classes"),
 (22,"BusyBox fractional ping timing and per-window warm-up","userspace","Retain sample counts and tool failures"),
 (23,"UMAC/ATHDEV defects, multiq and VLAN/PPPoE DSCP","airMAX","Saved benchmark and static security findings differ"),
 (24,"DFS-aware watchdog and migration safety gates","operations","Preserve CAC, recovery and zero-touch acceptance gates"),
 (25,"airOS scan whitelist and host_80211 behavior","airMAX","No regulatory or channel bypass in public kits"),
 (26,"Three-argument CSA channel-switch interface","airMAX","CSA success is not unrestricted channel support"),
 (27,"XC packet-log removal and dual-radio failure mode","airMAX","Do not apply module-removal recipes across boards"),
 (28,"Statistics-unsubscribe pointer handling","airMAX","Safe telemetry flags differ from unsafe unload paths"),
 (29,"LTU privileged tools and embedded-key review","LTU","Access prerequisites and disclosure impact are qualified"),
 (30,"LTU gain-table gate and early poststart exit","LTU","Persistence still requires independent cold-boot evidence"),
 (31,"Dynamic 20/40 MHz VHT width following","mac80211","Peer/driver-specific interoperability"),
 (32,"BNG shaping, LTU frame geometry and 2XC interrupt load","network/LTU","Keep the independent experiments separate"),
 (33,"Module control-boundary audit and WDS churn healing","controller","Static defects and live healing require separate proof"),
 (34,"LTU superframe tail bounds and constrained Pareto ranking","LTU/controller","Offline ranking is not runtime authorization"),
 (35,"Flash-unlock and firmware-signature gate analysis","firmware","No signature bypass or flash instructions supplied"),
 (36,"Linux 6.6.110 module layout and skb data offsets","mac80211","A matching version string alone is insufficient"),
 (37,"Dynamic AP-interface admitter rebinding","controller","Public helper has no fixed peer or captured vendor IE"),
 (38,"Four-address EAPOL delivery and AP_VLAN event ordering","mac80211","Association alone does not prove bridged data"),
 (39,"Different mac80211 ABIs within the same kernel version","mac80211","Use exact module hash, layout and original build"),
 (40,"Board-specific WA image packaging and control mapping","firmware","Shared WA family does not make DTBs interchangeable"),
 (41,"Authorized-gated four-address event patch, mac80211 v3","mac80211","Event gating is not general RX-security acceptance"),
 (42,"Stock PtP STA data gate and remote-first migration order","airMAX","Stage138 is offline static analysis/simulation; not a flash receipt")]

TITLE_EN = "openMAX update: WA public tester v4, 42 findings, and benchmark evidence"
TITLE_ES = "openMAX: tester publico WA v4, 42 hallazgos y evidencia de benchmarks"

SUMMARY_EN = """openMAX is our open-source research project for existing Ubiquiti airMAX hardware: https://github.com/wolverin0/openmax

We have prepared local public tester v4 candidates for PowerBeam 5AC Gen2, LiteBeam 5AC Gen2, LAP-120 and NanoStation 5AC Loco. Each model retains its own kernel/DTB. The package includes the exact mac80211 v3 WDS/ETH_P_TEB patch and an opt-in champion-v2 profile; it is not official/vendor-signed firmware, a deployment, or a universal compatibility claim.

The saved WA programme covers 18 RF comparisons (72 windows) plus one separate forwarding comparison (4 windows): 76 saved windows, not 76 repeats of one treatment.

- Stage161 R16 reports +13.68% goodput with distance=300 on that bench. This is not a distance recommendation for every link.
- The reported eight-flow comparison rises from 22.611 Mbps in Stage145 R15 to 38.055 Mbps average and 43.108 Mbps peak in Stage161 R17 (+68% to +90%). It combines changes across runs, including vm.min_free_kbytes=4096; it does not isolate that VM setting as the cause.
- Stage162/163 reports -25.78% E2E p95 RTT under packet_steering=1/flow_offloading=1 labels. Audit qualification: auxiliary ping data contain 999 sentinels with samples=1, and the runner does not demonstrate a real activated flowtable. The claimed E2E benefit remains UNPROVEN.

The v2 requested profile includes AQL threshold=4000, TCP pacing CA/SS=110/150, fq initial_quantum=3028 and conntrack_max=16384. fq initial_quantum is not a fq_codel parameter; its application and dependencies are explicitly qualified. Saved tail-latency regressions and getter conflicts remain visible.

FMX-DISC-42 / Stage138 explains a conditional stock-PtP data gate: keep a compatible airOS AP while converting the remote STA first, or clear radio.1.ptpmode=0 with applied configuration, reassociation and data-path checks before considering an OpenWrt AP. This is an offline finding, not permission or proof of a safe flash. Vendor IEs or successful EAPOL alone do not prove bridged data.

Public candidates start wired-only at 192.168.1.20/24 with Wi-Fi/DHCP disabled, no supplied key and no remote migration watchdog. They are NOT an unattended OTA migration profile. Do not flash a remote unit with them expecting it to reconnect automatically. Use a recoverable spare, exact-board images, checksums, your own credentials and a supported installation path.

The full local catalogue now lists FMX-DISC-01 through FMX-DISC-42. Static analysis, simulations, saved physical results and local software tests are labelled separately. XC/XW/XM diagnostic starters are separate from WA firmware; unsupported identities and active AirPrism remain qualified. No radios were touched and nothing was posted or published by this documentation update."""

SUMMARY_ES = """openMAX investiga mejoras sobre hardware Ubiquiti airMAX existente: https://github.com/wolverin0/openmax

Preparamos candidatos locales del tester publico WA v4 para PowerBeam 5AC Gen2, LiteBeam 5AC Gen2, LAP-120 y NanoStation 5AC Loco. Cada modelo conserva su kernel/DTB. Incluyen mac80211 v3 para WDS/ETH_P_TEB y el perfil champion-v2 optativo. No son firmware oficial firmado, un despliegue ni una promesa de compatibilidad universal.

El programa guardado contiene 18 comparaciones RF (72 ventanas) mas una comparacion de forwarding separada (4 ventanas): 76 ventanas, no 76 repeticiones del mismo tratamiento.

- Stage161 R16 reporta +13.68% de goodput con distance=300 en ese banco; no recomienda esa distancia para cualquier enlace.
- La comparacion reportada de ocho flujos pasa de 22.611 Mbps en Stage145 R15 a 38.055 Mbps promedio y 43.108 Mbps pico en Stage161 R17 (+68% a +90%). Cambiaron varios factores entre corridas, incluido vm.min_free_kbytes=4096: no demuestra causalidad aislada del ajuste VM.
- Stage162/163 reporta -25.78% de p95 RTT E2E bajo las etiquetas packet_steering=1/flow_offloading=1. La auditoria encuentra sentinelas 999 con samples=1 y no demuestra una flowtable activa. El beneficio E2E sigue SIN PROBAR / UNPROVEN.

El perfil solicitado incluye AQL threshold=4000, pacing TCP CA/SS=110/150, fq initial_quantum=3028 y conntrack_max=16384. initial_quantum no pertenece a fq_codel: su aplicacion y dependencias se califican por separado. Se conservan regresiones de latencia y conflictos entre configuracion y getters.

FMX-DISC-42 / Stage138 describe una condicion de datos de la STA stock PtP: mantener un AP airOS compatible mientras se convierte primero la STA remota, o cambiar radio.1.ptpmode=0 y verificar aplicacion, reasociacion y datos antes de considerar un AP OpenWrt. Es evidencia offline; no autoriza un flash ni demuestra que sea seguro. Asociacion/EAPOL o vendor IEs no prueban forwarding.

Los candidatos publicos arrancan por cable en 192.168.1.20/24, Wi-Fi/DHCP apagados, sin clave compartida y sin watchdog de migracion remota. NO sirven para una migracion OTA desatendida: no flashear una unidad remota esperando reconexion automatica. Usar un repuesto recuperable, imagen exacta, checksums, credenciales propias y un metodo soportado.

El catalogo completo incluye FMX-DISC-01..FMX-DISC-42 y distingue analisis estatico, simulaciones, resultados fisicos guardados y tests locales. Los kits diagnosticos XC/XW/XM son independientes del firmware WA; identidades sin soporte exacto y AirPrism activo siguen sin calificar. Esta actualizacion no toco radios ni publico mensajes o paquetes."""


def _summary_html(text):
    return "\n".join("<p>" + html.escape(p).replace("\n", "<br>") + "</p>" for p in text.split("\n\n"))


def render():
    if [r[0] for r in DISCOVERIES] != list(range(1,43)):
        raise ValueError("Exactly DISC01..42 required")
    for text in (SUMMARY_EN,SUMMARY_ES):
        if len(text) >= 10000 or len(_summary_html(text)) >= 10000:
            raise ValueError("Reddit summary budget exceeded")
    md = "<!-- doc-head: Synchronized Reddit drafts through DISC42 and Stage163; source claims qualified -->\nCopy only a language summary for a Reddit post; each is below10000 characters.\nThe complete catalogue is separate and does not imply every historical claim is accepted.\n<!-- /doc-head -->\n\n# openMAX Reddit drafts: public tester v4\n\n"
    for language,title,summary in (("EN",TITLE_EN,SUMMARY_EN),("ES",TITLE_ES,SUMMARY_ES)):
        md += f"## {language} Reddit-ready summary\n\nTitle: {title}\n\n```text\n{summary}\n```\n\n"
    md += "## Full discovery catalogue (historical source index)\n\n| ID | Finding | Layer | Evidence limit |\n| :--- | :--- | :--- | :--- |\n"
    for i,title,layer,limit in DISCOVERIES:
        md += f"| FMX-DISC-{i:02d} | {title} | {layer} | {limit} |\n"
    md += "\nSources: [historical catalogue](CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md), [Stage138](../artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json), [Stage161](../artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json), [Stage162](../artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json), [Stage163](../artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json).\n\n[Tester guide](GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md) and [public-v4 limits](OPENMAX_WA_PUBLIC_V4_TESTER_GUIDE.md). Local drafts only; no external posting.\n"
    rows = "\n".join(f'<tr data-discovery="FMX-DISC-{i:02d}"><td>FMX-DISC-{i:02d}</td><td>{html.escape(title)}</td><td>{html.escape(layer)}</td><td>{html.escape(limit)}</td></tr>' for i,title,layer,limit in DISCOVERIES)
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>openMAX Reddit copy helper - DISC42 / Stage163</title>
<style>
:root{color-scheme:light;--page:#f3f6fb;--card:#fff;--ink:#182b44;--muted:#465870;--line:#a6b7ca;--header:#173b62;--header-ink:#fff;--button:#174c85}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--page:#0b1422;--card:#132237;--ink:#e6eefb;--muted:#b2c4db;--line:#516b8c;--header:#b7d7ff;--header-ink:#102640;--button:#2b61a2}}
:root[data-theme=light]{color-scheme:light;--page:#f3f6fb;--card:#fff;--ink:#182b44;--muted:#465870;--line:#a6b7ca;--header:#173b62;--header-ink:#fff;--button:#174c85}
:root[data-theme=dark]{color-scheme:dark;--page:#0b1422;--card:#132237;--ink:#e6eefb;--muted:#b2c4db;--line:#516b8c;--header:#b7d7ff;--header-ink:#102640;--button:#2b61a2}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:16px/1.55 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:24px}header{margin-bottom:28px}h1{font-size:clamp(1.7rem,4vw,2.7rem);line-height:1.12}h2{line-height:1.2}.meta{color:var(--muted)}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0}button,select{font:inherit;padding:10px 14px;border:1px solid var(--line);border-radius:8px}button{background:var(--button);color:#fff;cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid #df8a05;outline-offset:3px}article,section.catalogue{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:24px;margin:24px 0}.summary p{white-space:normal}.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.92rem}caption{text-align:left;font-weight:600;margin:0 0 12px}th,td{border:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}thead th{background:var(--header);color:var(--header-ink);font-weight:750}td:first-child{white-space:nowrap}#status{min-height:1.5em;color:var(--muted)}a{color:var(--ink)}@media(max-width:600px){main{padding:14px}article,section.catalogue{padding:16px}th,td{padding:8px}}
</style></head><body><main>
<header><p class="meta">LOCAL DRAFT / NOTHING POSTED</p><h1>openMAX research update</h1><p>Public tester v4, 42 discoveries, and explicit evidence limits.</p>
<label for="theme">Preview theme</label> <select id="theme"><option value="auto">System</option><option value="light">Light</option><option value="dark">Dark</option></select>
<p id="status" role="status" aria-live="polite">Choose a language summary. Full catalogue is below.</p></header>
'''
    for language,title,summary in (("en",TITLE_EN,SUMMARY_EN),("es",TITLE_ES,SUMMARY_ES)):
        page += f'<article lang="{language}"><h2>{html.escape(title)}</h2><div class="toolbar"><button data-copy="post-{language}">Copy {language.upper()} summary</button><span class="meta" id="count-{language}"></span></div><div id="post-{language}" class="summary">{_summary_html(summary)}</div></article>\n'
    page += '<section class="catalogue"><h2>Full historical discovery catalogue</h2><p>Source index, not universal hardware acceptance. The summary buttons do not copy this table.</p><div class="table-scroll"><table id="discovery-table"><caption>FMX-DISC-01 through FMX-DISC-42</caption><thead><tr>'
    page += ''.join(f'<th scope="col">{c}</th>' for c in ("ID","Finding","Layer","Evidence limit")) + '</tr></thead><tbody>' + rows + '</tbody></table></div></section>\n'
    page += '''<footer><p>Sources: <a href="CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md">historical catalogue</a>, <a href="../artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json">Stage138</a>, <a href="STAGE163A_CUMULATIVE_18ROUND_WA_CHAMPION_V2.md">Stage163 reported consolidation</a>, <a href="OPENMAX_WA_PUBLIC_V4_TESTER_GUIDE.md">public tester v4 qualifications</a>. No upload or posting function exists.</p></footer>
<script>
function summaryText(node){return Array.from(node.querySelectorAll('p')).map(p=>p.innerText).join(String.fromCharCode(10,10));}
async function copySummary(id){const node=document.getElementById(id),text=summaryText(node),markup=node.innerHTML;
if(text.length>=10000||markup.length>=10000){document.getElementById('status').textContent='Summary exceeds the 10000-character limit.';return;}
try{if(window.ClipboardItem&&navigator.clipboard.write){await navigator.clipboard.write([new ClipboardItem({'text/plain':new Blob([text],{type:'text/plain'}),'text/html':new Blob([markup],{type:'text/html'})})]);}else{await navigator.clipboard.writeText(text);}document.getElementById('status').textContent='Summary copied. Nothing posted.';}
catch(error){const selection=window.getSelection(),range=document.createRange();range.selectNodeContents(node);selection.removeAllRanges();selection.addRange(range);document.getElementById('status').textContent='Clipboard unavailable. Summary selected; copy it manually.';}}
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',()=>copySummary(button.dataset.copy)));
document.getElementById('theme').addEventListener('change',event=>{if(event.target.value==='auto'){delete document.documentElement.dataset.theme;}else{document.documentElement.dataset.theme=event.target.value;}});
for(const language of ['en','es']){const node=document.getElementById('post-'+language);document.getElementById('count-'+language).textContent=summaryText(node).length+' text / '+node.innerHTML.length+' HTML characters; both below 10000.';}
</script></main></body></html>
'''
    return md, page


def build(root=ROOT):
    root = Path(root)
    md,page = render()
    if len(md.splitlines()) >= 220:
        raise ValueError("Compact Markdown budget exceeded")
    for name,data in (("REDDIT_POST.md",md),("reddit_post_copy.html",page)):
        (root/"docs"/name).write_text(data,encoding="utf-8",newline="\n")
    return {"outputs":{name:hashlib.sha256((root/"docs"/name).read_bytes()).hexdigest() for name in ("REDDIT_POST.md","reddit_post_copy.html")},
        "summary_characters": {"en":len(SUMMARY_EN),"es":len(SUMMARY_ES)},"discovery_count":42}


if __name__ == "__main__":
    print(json.dumps(build(),indent=2))
