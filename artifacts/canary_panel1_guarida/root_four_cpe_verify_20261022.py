"""Read-only verification and telemetry reduction of a completed FMX-0016 run."""
from pathlib import Path
import hashlib
import json
import re
import statistics
import sys

HERE=Path(__file__).resolve().parent
MACS={'WA':'fc:ec:da:c2:54:0a','XC':'b4:fb:e4:5c:d5:d2',
      'SXT':'64:d1:54:1b:96:97','LBM5':'f0:9f:c2:b2:b6:ba'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main(label):
    out=HERE/('root_four_cpe_'+label)
    r=json.loads((out/'receipt.json').read_text(encoding='utf-8'))
    assert r['status']=='PASS_FOUR_CPE_60S_RADIO_TRAFFIC_TELEMETRY_ALL_RESTORED'
    assert not r['failures'] and not r['cleanup_errors'] and r['four_way_stability_seconds']>=60
    assert sha(HERE/'root_four_cpe_trial_20261022.py')==r['source_sha256']
    for file,binding in r['bindings'].items():assert sha(HERE/file)==binding
    samples=r['samples'];assert len(samples)>2
    for sample in samples:
        assert set(sample['stations'])==set(MACS.values())
        for name,mac in MACS.items():
            assert all(sample['clients'][mac].get(k) is True for k in ['auth','assoc','authorized'])
            if name in ['WA','XC']:assert sample['clients'][mac]['wds'] is True
            else:assert sample['clients'][mac]['wds'] is False
        assert sha(out/sample['raw']['file'])==sample['raw']['sha256']
    telemetry={};spans=[]
    for name,mac in MACS.items():
        ping=r['pings'][name];assert ping['exit_code']==0 and ping['transmitted']==ping['received']==64
        assert ping['capture_exit_code']==0 and ping['paired']==64
        capref=ping['capture'];assert sha(out/capref['file'])==capref['sha256']
        cap=json.loads((out/capref['file']).read_text(encoding='utf-8'))
        pairs=re.findall(r'ICMP6?,? echo (request|reply), id (\d+), seq (\d+)',cap['stdout'])
        requests={(i,s) for k,i,s in pairs if k=='request'};replies={(i,s) for k,i,s in pairs if k=='reply'}
        assert len(requests)==len(replies)==len(requests&replies)==64
        times=[float(t) for t in re.findall(r'(?m)^(\d+\.\d+) .*echo request,',cap['stdout'])]
        assert len(times)==64;spans.append((min(times),max(times)))
        rows=[s['stations'][mac] for s in samples]
        assert rows[-1]['connected_seconds']>=60
        assert rows[-1]['connected_seconds']-rows[0]['connected_seconds']>=int(r['four_way_stability_seconds'])-2
        assert rows[-1]['rx_bytes']>rows[0]['rx_bytes'] and rows[-1]['tx_bytes']>rows[0]['tx_bytes']
        signals=[s['signal_dbm'] for s in rows if s['signal_dbm'] is not None]
        latencies=[float(v) for v in re.findall(r'time=([0-9.]+) ms',ping['stdout'])]
        assert len(latencies)==64
        telemetry[name]={'mac':mac,'interface':ping['interface'],'ping_transmitted':64,'ping_received':64,
            'radio_request_reply_pairs':64,'loss_percent':0,'first_request_epoch':min(times),'last_request_epoch':max(times),
            'signal_dbm':{'min':min(signals),'median':statistics.median(signals),'max':max(signals)},
            'observed_idle_RTT_ms':{'min':min(latencies),'median':statistics.median(latencies),
                                    'p95':statistics.quantiles(latencies,n=100,method='inclusive')[94],'max':max(latencies)},
            'first_connected_seconds':rows[0]['connected_seconds'],'last_connected_seconds':rows[-1]['connected_seconds'],
            'rx_bytes_delta':rows[-1]['rx_bytes']-rows[0]['rx_bytes'],'tx_bytes_delta':rows[-1]['tx_bytes']-rows[0]['tx_bytes']}
    overlap=min(b for a,b in spans)-max(a for a,b in spans);assert overlap>0
    hashes=lambda text:re.findall(r'(?m)^([0-9a-f]{32,64})\s+(/\S+)$',text)
    def network(text):
        return (re.findall(r'(?m)^\s+inet ([^\n]+)',text),
                [l for l in text.splitlines() if re.match(r'^(default |[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?:/[0-9]+)? (?:dev|via) )',l)])
    for name in ['SXT','LBM5']:
        before=r['legacy_baselines'][name];after=r['legacy_restoration'][name]['snapshot']
        assert before.splitlines()[0]==after.splitlines()[0] and hashes(before)==hashes(after) and network(before)==network(after)
        assert r['legacy_restoration'][name]['RAM_guard_cleanup']['exit_code']==0
        probe=r['legacy_restoration'][name]['ping'];assert '3 packets transmitted, 3 packets received' in probe['stdout']
        logref=r['legacy_restoration'][name]['guard_log'];assert sha(out/logref['file'])==logref['sha256']
    m5log=json.loads((out/r['legacy_restoration']['LBM5']['guard_log']['file']).read_text(encoding='utf-8'))['stdout']
    assert 'Key negotiation completed' in m5log and '[PTK=CCMP GTK=CCMP]' in m5log and 'CTRL-EVENT-TERMINATING' in m5log
    assert r['AP_restoration']['status']=='PASS_RAM_WINDOW_RESTORED_RADIO_OFF' and r['AP_restoration']['guard_ended_verified']
    assert r['AP_restoration']['RAM_guard_cleanup']['exit_code']==0
    assert r['rocket_baseline']==r['rocket_restoration']['evidence']
    report={'status':'PASS_ARTIFACT_CONTRACT_VERIFIED','experiment':'FMX-0016','run':label,
            'raw_receipt_sha256':sha(out/'receipt.json'),'four_way_association_stability_seconds':r['four_way_stability_seconds'],
            'four_ping_streams_overlap_seconds':overlap,'sample_count':len(samples),'total_wireless_echo_pairs':256,
            'telemetry':telemetry,'restoration':'PASS exact AP/Rocket and both original open legacy profiles/protected hashes/boot/IPv4/routes; guards ended and owned temporary guard files removed',
            'classification':'CONFIRMED_EXACT_BENCH_FOUR_CPE_MULTI_GENERATION_COMPATIBILITY_AND_TELEMETRY',
            'limits':['Low-rate ICMP and association test only; no throughput/capacity/loaded-latency gain claim',
                      'AP+four per-station time series plus two legacy CPE self reports; no cooperative relay or optimizer implemented',
                      'Original240s legacy guard deadline retained; accepted run uses2s activation delay and explicit XC native scan before Auth',
                      'IE timestamps are API acknowledgements; over-air IE timing unqualified']}
    with (out/'verification.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    finalpath=HERE/'root_four_cpe_result_20261022.json';final=json.loads(finalpath.read_text(encoding='utf-8'))
    assert final['raw_receipt_sha256']==report['raw_receipt_sha256']
    final['verified_summary']=report;final['verification_artifact']=str((out/'verification.json').relative_to(HERE))
    finalpath.write_text(json.dumps(final,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main(sys.argv[1])
