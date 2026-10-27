#!/usr/bin/env python3
"""Deterministic Guarida ANI/NAPI sensitivity model, not RF measurements."""
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage782a_guarida_32cpe_ani_and_napi_pareto'
TOPOLOGY = [dict(panel=1, provisioned=4, active=3, pending=1),
            dict(panel=2, provisioned=22, active=22, pending=0),
            dict(panel=3, provisioned=6, active=6, pending=0)]


def model(ani, budget, weight, offered_mbps):
    if ani not in range(5) or budget not in (300, 480, 600) or weight not in (48, 64, 96):
        raise ValueError('unsupported model input')
    if offered_mbps not in (40, 80, 120):
        raise ValueError('unsupported offered load')
    # Assumptions: normalized per-panel 90 Mbps capacity, convex CPU cost and
    # level-4 weak-signal penalty. These coefficients are deliberately uncalibrated.
    noise = (1.0, .6, .25, .2, .15)[ani]
    weak_loss = (0, .1, .3, .8, 4.0)[ani]
    cpu = 100 * weight / budget
    capacity = 90 * (1 - noise * .12) * (1 - weak_loss / 100) * (1 - cpu / 1000)
    panels = []
    for p in TOPOLOGY:
        demand = offered_mbps * p['active'] / 31
        served = min(demand, capacity)
        utilization = min(.99, demand / capacity)
        panels.append(dict(panel=p['panel'], active=p['active'],
                           modeled_goodput_mbps=served,
                           modeled_p95_ms=2 + 3 * utilization / (1 - utilization) + noise * 4,
                           modeled_loss_pct=100 * max(0, demand - capacity) / demand + weak_loss))
    gp = sum(p['modeled_goodput_mbps'] for p in panels)
    return dict(ani=ani, budget=budget, weight=weight, offered_mbps=offered_mbps,
                negative_goodput=-gp, p95_ms=max(p['modeled_p95_ms'] for p in panels),
                loss_pct=max(p['modeled_loss_pct'] for p in panels), cpu_cost=cpu, panels=panels)


def build(root=ROOT):
    rows = [model(*x) for x in product(range(5), (300, 480, 600), (48, 64, 96), (40, 80, 120))]
    # Compare alternatives only at equal offered load, preventing optimizer gaming.
    fronts = {str(load): c.pareto([r for r in rows if r['offered_mbps'] == load],
                                ('negative_goodput', 'p95_ms', 'loss_pct', 'cpu_cost'))
              for load in (40, 80, 120)}
    sources = [c.snapshot(root, p) for p in [
        'tools/sim/run_stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.py',
        'artifacts/guarida_32cpe_radiography_20261024.json']]
    data = c.receipt(782, 'Guarida 32-CPE ANI and NAPI Pareto', sources)
    data.update(claim_classification='INFERRED', execution_mode='OFFLINE_SIMULATION',
                topology=TOPOLOGY, provisioned_cpes=32, active_cpes=31,
                candidate_count=len(rows), pareto_by_offered_load=fronts,
                baseline_by_offered_load={str(n): model(0, 300, 64, n) for n in (40, 80, 120)},
                assumptions=['Uncalibrated 90 Mbps per-panel capacity',
                             'Equal active-CPE demand; no measured interference or queue trace',
                             'CPU weight/budget cost proxy; no LTU IRQ setting is applied to QCA988x'],
                measured_gain='UNKNOWN')
    return c.save(root, STEM, data, 'INFERRED: deterministic sensitivity model over 135 candidates.\n\n'
                  'Three panels: 4/22/6 provisioned CPEs; panel 1 has 3 active and 1 pending.\n'
                  'Separate Pareto fronts compare equal offered load (40/80/120 Mbps).\n'
                  'Objectives minimize negative goodput, p95, loss and a CPU proxy.\n'
                  'Coefficients and capacity are assumptions; hardware gains remain UNKNOWN.\n')


def main():
    result = build(); print(f'{STEM}: {result["candidate_count"]} modeled candidates; live=0'); return 0


if __name__ == '__main__':
    raise SystemExit(main())
