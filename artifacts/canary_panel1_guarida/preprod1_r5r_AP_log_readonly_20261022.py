"""Read existing AP logs after restored R; no writes or CPE contact."""
from datetime import datetime, timezone
import json
from pathlib import Path
import root_four_cpe_access_20261022 as access

HERE = Path(__file__).resolve().parent
receipt = HERE / 'preprod1_20261022_run5r/receipt.json'
r = json.loads(receipt.read_text())
access.require(r.get('ended_utc') and not r['cleanup_errors'] and
               r['AP_restoration']['guard_ended_verified'], 'R_NOT_RESTORED')
out = HERE / 'preprod1_r5r_AP_log_readonly_20261022.json'
access.require(not out.exists(), 'DIAGNOSTIC_COLLISION')
ap = access.load('root_goal_direct_link_connection_20261022.py').ap_client()
try:
    helper = access.ap_helper()
    helper.identity(ap)
    state = access.remote(ap, 'ubus -t 4 call network.wireless status; iw dev')
    logs = access.remote(ap, "logread | grep -i 'b4:fb:e4:5c:d5:d2' | tail -n 100", check=False)
    data = dict(utc=datetime.now(timezone.utc).isoformat(),
                status='READ_ONLY_EXISTING_LOG_OBSERVATION_NOT_TRIAL_ACCEPTANCE',
                raw_receipt=receipt.name, raw_receipt_sha256=access.sha(receipt.read_bytes()),
                AP_state=state, XC_MAC_filtered_AP_logs=logs,
                source_sha256=access.sha(Path(__file__).read_bytes()),
                CPE_contact=False, device_writes=False,
                limit='Existing log retention only; absence is not proof of no RF frame.')
    with out.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))
finally:
    ap.close()
