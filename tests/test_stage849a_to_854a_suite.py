from pathlib import Path

import pytest

from tools.verify.stage779_822_offline_common import read_json, snapshot
from tools.verify.stage849_854_release_common import STEMS, artifact, audit_stage

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('stage', range(849, 854))
def test_offline_release_artifact_contract(stage):
    result = audit_stage(ROOT, stage)
    assert result['compliant'], result


def test_scorecard_matches_simulation():
    model = read_json(ROOT, artifact(851))
    score = read_json(ROOT, artifact(852))
    ids = [row['window_id'] for row in model['windows']]
    assert len(ids) == len(set(ids)) == 1050
    assert score['accounting']['window_ids'] == ids
    assert score['accounting']['actual_synthetic_windows'] == len(ids)
    assert score['accounting']['physical_windows_executed'] == 0


def test_source_drift_fails_closed(tmp_path):
    import shutil
    # Copy only the audited manifest's declared dependencies, not private worktree data.
    stage = 852
    data = read_json(ROOT, artifact(stage))
    labels = [artifact(stage), f'docs/{STEMS[stage].upper()}.md',
              'tools/verify/build_stage852a_1050window_cross_lane_master_scorecard.py']
    labels += [source['path'] for source in data['sources'] if source['available']]
    for label in set(labels):
        destination = tmp_path / label
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / label, destination)
    assert audit_stage(tmp_path, stage)['compliant']
    victim = tmp_path / data['sources'][0]['path']
    victim.write_bytes(victim.read_bytes() + b' ')
    assert not audit_stage(tmp_path, stage)['compliant']
