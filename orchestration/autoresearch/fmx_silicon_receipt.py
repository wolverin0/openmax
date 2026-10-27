"""Audit a caller-pinned saved probe; no device access or physical acceptance."""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re


EXPERIMENT = 'FMX-PB-021-031-050-LIVE-LAP120-SILICON-20261024'
TIMING = 'pb_050_hardware_timing_and_clock_jitter'
CHANINFO = 'pb_021_baseband_chaninfo_and_implicit_calibration'
CONTROLS = 'pb_031_ldpc_ampdu_tpc_authority'
CONTEXTS = {0:0, 2:1000, 6:3000, 13:6000, 20:9000, 26:12000, 31:14000}


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON field')
        value[key] = item
    return value


def _decode(raw):
    def nonfinite(_):
        raise ValueError('Nonfinite JSON constant')
    def finite_float(token):
        value=float(token)
        if not math.isfinite(value):
            raise ValueError('Nonfinite JSON number')
        return value
    value = json.loads(raw, object_pairs_hook=_object, parse_constant=nonfinite,
                       parse_float=finite_float)
    if not isinstance(value, dict):
        raise ValueError('Saved receipt must be an object')
    return value


def _number(value):
    if type(value) not in (int, float) or value < 0:
        raise ValueError('Finite nonnegative number required')
    try:
        valid=math.isfinite(value)
    except OverflowError as error:
        raise ValueError('Finite representable number required') from error
    if not valid:
        raise ValueError('Finite nonnegative number required')
    return value


def _integer(value):
    if type(value) is not int or value < 0:
        raise ValueError('Nonnegative exact integer required')
    return value


def _hex(value):
    if type(value) is not str or not re.fullmatch(r'0x[0-9a-fA-F]{1,8}', value):
        raise ValueError('Explicit unsigned 32-bit hexadecimal word required')
    return int(value, 16)


@dataclass(frozen=True)
class SavedSiliconReceipt:
    payload: bytes
    sha256: str

    def parse(self):
        if (type(self.payload) is not bytes or type(self.sha256) is not str or
                not re.fullmatch('[0-9a-f]{64}', self.sha256) or
                hashlib.sha256(self.payload).hexdigest() != self.sha256):
            raise ValueError('Saved receipt hash mismatch')
        return _decode(self.payload)


def load_saved_silicon_receipt(path, *, expected_sha256):
    """Read only the explicit local file; never follow paths in its metadata."""
    if type(expected_sha256) is not str or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('Caller-accepted SHA256 required')
    text = str(path)
    if '://' in text or text.startswith(('\\\\', '//')):
        raise ValueError('Explicit local file required')
    receipt = SavedSiliconReceipt(Path(path).read_bytes(), expected_sha256)
    receipt.parse()
    return receipt


def audit_saved_silicon_receipt(receipt):
    """Separate reported observations and arithmetic from unqualified authority."""
    if not isinstance(receipt, SavedSiliconReceipt):
        raise ValueError('Authenticated saved receipt required')
    value = receipt.parse()
    if value.get('experiment_id') != EXPERIMENT:
        raise ValueError('Exact saved PB experiment required')
    try:
        hardware = value['target_hardware']
        timing, channel, controls = (value[key] for key in (TIMING, CHANINFO, CONTROLS))
        if any(not isinstance(item, dict) for item in (hardware, timing, channel, controls)):
            raise ValueError('Explicit probe sections required')
        if hardware.get('ap_hostname') != 'LAP-120':
            raise ValueError('Exact saved target identity required')
        hz = _integer(timing['mac_core_clock_hz'])
        rate = _number(timing['mac_core_clock_cycles_per_us'])
        if hz != 88000000 or rate != 88:
            raise ValueError('This audit only covers the recorded 88MHz hypothesis')
        table = timing['coverage_class_silicon_table']
        if not isinstance(table, list) or len(table) != len(CONTEXTS):
            raise ValueError('All seven explicit saved timing contexts required')
        rows = []
        seen = set()
        for index, row in enumerate(table):
            c = _integer(row['coverage_class'])
            if c not in CONTEXTS or c in seen or _integer(row['nominal_distance_m']) != CONTEXTS[c]:
                raise ValueError('Unique exact coverage/distance contexts required')
            seen.add(c)
            slot = _hex(row['dcu_gbl_ifs_slot_0x21070_hex'])
            sifs = _hex(row['dcu_gbl_ifs_sifs_0x21030_hex'])
            eifs = _hex(row['dcu_gbl_ifs_eifs_0x210b0_hex'])
            timeout = _hex(row['pcu_time_out_0x28014_hex'])
            tsf = _hex(row['sample_mac_pcu_tsf2_l32_0x28120'])
            _hex(row['sample_mac_pcu_cycle_cnt_0x280f8'])
            _hex(row['pcu_usec_latency_0x2801c_hex'])
            expected = {'slot':(slot, 792+264*c, row['dcu_gbl_ifs_slot_cycles_88mhz'], row['dcu_gbl_ifs_slot_us']),
                        'sifs':(sifs, 1232, row['dcu_gbl_ifs_sifs_cycles_88mhz'], row['dcu_gbl_ifs_sifs_us']),
                        'eifs':(eifs, 8096, row['dcu_gbl_ifs_eifs_cycles_88mhz'], row['dcu_gbl_ifs_eifs_us']),
                        'ack':(timeout & 65535, 2640+264*c, row['ack_timeout_cycles_88mhz'], row['ack_timeout_us']),
                        'cts':(timeout >> 16, 2640+264*c, row['cts_timeout_cycles_88mhz'], row['cts_timeout_us'])}
            checks = {name: word == formula == _integer(cycles) and _number(us) == word/rate
                      for name, (word,formula,cycles,us) in expected.items()}
            rows.append(dict(coverage_class=c, declared_distance_m=CONTEXTS[c],
                pointer=f'/{TIMING}/coverage_class_silicon_table/{index}', arithmetic=checks,
                reported_ack_timeout_us=row['ack_timeout_us'], historical_advisory_ack_us=18+6*c,
                same_as_historical_advisory=row['ack_timeout_us']==18+6*c, reported_tsf2_word=tsf))
        clock = timing['n160_paired_clock_benchmark']
        if not isinstance(clock,dict):
            raise ValueError('Clock benchmark must be an explicit object')
        for section, key in ((clock,'pb_050_verdict'),(channel,'pb_021_verdict'),(controls,'pb_031_verdict')):
            if type(section.get(key)) is not str or not section[key].strip():
                raise ValueError('Explicit source verdict text required')
        if _integer(clock['n_samples']) != 160:
            raise ValueError('Exact reported sample-count context required')
        quantiles = {}
        for name in ('single_pcie_mmio_syscall_us','debugfs_two_reg_mmio_roundtrip_us','host_vs_target_midpoint_jitter_abs_us'):
            items = [_number(clock[f'{name}_{q}']) for q in ('p50','p95','p99')]
            quantiles[name] = dict(zip(('p50','p95','p99'), items))
            if items != sorted(items):
                raise ValueError('Reported quantiles must be ordered')
        ratios = {name:_number(clock[name]) for name in ('measured_clock_ratio_cycles_per_us_mean','measured_clock_ratio_cycles_per_us_median')}
        decoded = channel['chaninfo_ctrl_decoded']
        word = _hex(channel['bb_registers']['PHY_BB_CHANINFO_CTRL_0x2a370'])
        decode_ok = (word == _hex(decoded['raw_hex']) and
            _integer(decoded['CAPTURE_CHAN_INFO_bit0']) == word & 1 and
            _integer(decoded['CHANINFOMEM_S2_READ_bit3']) == (word >> 3) & 1 and
            _integer(decoded['CHANINFO_20MHZ_SUBBAND_bits7_6']) == (word >> 6) & 3)
        banks = {}
        for key, start in (('chan_tab_chain0_0x29b00_0x29b3c',0x29b00),('chan_tab_chain1_0x2ab00_0x2ab3c',0x2ab00)):
            bank=channel[key]
            if not isinstance(bank, dict) or set(bank)!={hex(start+4*i) for i in range(16)}:
                raise ValueError('Exact saved bank coordinates required')
            banks[key]=[_hex(bank[hex(start+4*i)]) for i in range(16)]
        readbacks = controls['htt_max_amsdu_ampdu_readbacks']
        if not isinstance(readbacks,list) or len(readbacks)!=3:
            raise ValueError('Three explicit saved HTT readbacks required')
        readback_ok=[]
        for row, limit in zip(readbacks,(16,32,64)):
            readback_ok.append(_integer(row['requested_ampdu'])==limit and row['readback']==f'3 {limit}')
        ldpc=[_hex(controls[key]) for key in ('PHY_BB_LDPC_CNTL1_0x29c04','PHY_BB_LDPC_CNTL2_0x29c08')]
        latency_cycles=_integer(controls['ldpc_latency_cycles'])
        restoration=value['restoration_verified']
        if (not isinstance(restoration,dict) or _integer(restoration['coverage_class_restored'])!=0 or
                restoration['htt_max_amsdu_ampdu_restored']!='3 64'):
            raise ValueError('Exact reported restoration states required')
    except (KeyError, TypeError, IndexError) as error:
        raise ValueError('Incomplete or malformed saved probe receipt') from error
    arithmetic_ok = all(all(row['arithmetic'].values()) for row in rows) and decode_ok and all(readback_ok)
    missing = [
        'RAW_160_CLOCK_SAMPLES_AND_COMMAND_TRANSCRIPTS', 'EXACT_FIRMWARE_DRIVER_BOARD_BUILD_HASHES',
        'CLOCK_ORIGIN_WRAP_AND_HOST_TARGET_SYNCHRONIZATION', 'BOUNDED_TX_RELEASE_COMPLETION_AND_LOWER_QUEUE_OWNERSHIP',
        'LOADED_ASSOCIATED_CPE_ACK_RETRY_BEACON_AND_MISSED_SLOT_SURVIVAL',
        'PER_PACKET_CSI_CAPTURE_TRIGGER_AND_CHANNEL_SAMPLE_ATTRIBUTION',
        'EFFECTIVE_LDPC_AGGREGATION_AND_PER_PEER_POWER_CONTROL',
        'INDEPENDENT_BASELINE_RESTORATION_AND_HEALTH_POSTCHECK']
    reasons = ['SAVED_SUMMARY_DOES_NOT_QUALIFY_SILICON_CONTROL', *missing]
    if not arithmetic_ok:
        reasons.append('SAVED_ARITHMETIC_OR_READBACK_CONFLICT')
    return dict(schema_version=1, experiment_id=EXPERIMENT, source_sha256=receipt.sha256,
        status='DOCUMENTARY_PROBE_ONLY' if arithmetic_ok else 'DOCUMENTARY_PROBE_CONFLICT',
        reported_target=hardware, internally_consistent_under_reported_clock=arithmetic_ok,
        reported_clock_hz=hz, clock_frequency_independently_verified=False, timing_rows=rows,
        reported_sample_count=160, reported_clock_ratios=ratios, reported_quantiles=quantiles,
        quantiles_independently_recomputed=False, raw_clock_samples_present=False,
        repeated_tsf2_words=len({row['reported_tsf2_word'] for row in rows})==1,
        historical_ack_metadata_rewritten=False, historical_ack_formula='18 + 6*c', reported_ack_formula='30 + 3*c',
        timing_formula_transfer_qualified=False, physical_distance_verified=False,
        channel_capture_bit=word & 1, channel_decode_internally_consistent=decode_ok,
        channel_bank_word_counts={key:len(values) for key,values in banks.items()}, operational_csi_qualified=False,
        ldpc_register_words=ldpc, reported_ldpc_latency_cycles=latency_cycles,
        ldpc_control_or_latency_qualified=False, host_htt_readback_consistent=all(readback_ok),
        effective_ampdu_qualified=False, per_peer_power_qualified=False,
        reported_restoration=restoration, restoration_independently_verified=False,
        source_claims={key:section[key] for section,key in ((clock,'pb_050_verdict'),(channel,'pb_021_verdict'),(controls,'pb_031_verdict'))},
        stage4_tdma_qualified=False, coarse_hmac_cadence_qualified=False, missing_evidence=missing,
        blocking_reasons=sorted(reasons), automatic_execution_allowed=False, physical_acceptance=False,
        behavior_layer='OFFLINE_EXTERNAL_CONTROLLER_ANALYSIS')
