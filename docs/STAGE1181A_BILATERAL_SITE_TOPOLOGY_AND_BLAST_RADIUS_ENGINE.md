<!-- doc-head: Stage1181A offline bilateral PtP site topology model that vetoes channel changes colliding at either tower and weights risk by downstream CPEs -->
<!-- /doc-head -->

# Stage1181A - Bilateral site topology and blast-radius engine

Evidence class `BILATERAL_SITE_TOPOLOGY_MODEL`. This is a simulated, offline model. No device, UISP or NMS call is made and `live_devices_touched=false`.

## Topology (data, not logic)

`DEFAULT_GRAPH` in `tools/uisp/bilateral_site_topology_and_blast_radius_engine.py` holds sites, datalinks, APs, PtPs and customer counts (`station_count`, `ac2_devices`).

- Almafuerte: AP end of the PtP, radio `.60`.
- Guarida tower: PtP STA `.61` plus sibling sector APs for Guarida, Panel2, Panel3 and Panel1.
- Panel1 `.84` is modelled as a PoP at the Guarida tower (assumption, see below).
- Blast-radius weights (CPEs): Guarida=32, Panel2=22, Panel3=6, Panel1=4 (3+1).

Channel and width values per radio are model placeholders, not live readings. A JSON file can replace the graph through `--graph-json`.

## Public API

- `build_site_graph(override_json=None) -> dict` returns `sites`, `datalinks`, `aps`, `ptps`, `customer_counts`.
- `evaluate_channel_change(graph, ptp_id, candidate_channel_mhz, width_mhz=20) -> dict`.
- `main()` with `--write-receipt`.

## Bilateral evaluation

For both PtP ends (A near, B far) the engine collects every radio at that tower: co-located sector APs and sibling PtP radios, excluding the PtP's own two radios.

- Veto when `abs(candidate - other) < (width + other_width)/2 + guard`, guard default 20 MHz, at EITHER tower.
- `vetoes` entries: `end`, `tower`, `reason`, `overlapping_channel`.
- `blast_radius_cpes` is the deduplicated union of customer sites served by all radios at both towers.
- `interference_cost` sums overlap fraction times CPEs served by the colliding radio. It is 0.0 when nothing collides.
- `evaluated_ends` is always 2.

Example: PtP `ptp-almafuerte60-guarida61` at 5745 MHz is vetoed at Guarida by the Guarida sector, with `blast_radius_cpes=64`. At 5500 MHz it is allowed.

## Commands

```powershell
python tools/uisp/bilateral_site_topology_and_blast_radius_engine.py --write-receipt
python -m pytest tests/test_stage1181a_bilateral_engine.py
```

Receipt: `artifacts/autoresearch/stage1181a_bilateral_site_topology_graph.json`. It is written with up to 3 write/read-back attempts and rejected if it contains NUL bytes. Claim id `FMX-STAGE1181A-BILATERAL-SITE-TOPOLOGY-AND-BLAST-RADIUS-ENGINE`.

## Limits

- Single center frequency per radio, no spectral mask, no antenna pattern or isolation model (shortcut).
- Assumption: Panel1 sits at the Guarida tower and Almafuerte has no sibling radios. Edit the graph data if the field layout differs.
- A pass is a model result only. It does not authorize any channel change.
