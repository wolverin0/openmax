"""Three-phase RAM-only AP IE control; root injects client and capture callback.

No connections/credentials, firmware/config commit or authentication controls.
API acknowledgements remain OTA_PENDING until the independent PCAP is checked.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
AP_NAME = 'root_multi_cpe_ap_window_20261022.py'
AP_SHA = '488bebca7664ae320c03cec051e1d59432bc4d09e2988037c1a40c8aa3a892cf'
# Discovery metadata using layout reconstructed byte-exactly from held native WA capture.
# PtP capability1 derives from held branch; CPE acceptance remains a measurement.
TRIAL_IE = 'dd3a002722ffffff020100300206e82099038138fb0a23214c3513a4a15bfabc3725b021af9049751e2eb3835ff0ff254ecf491a67c5e7e4235a8f4a'
sha = lambda data: hashlib.sha256(data).hexdigest()


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def load_ap():
    path = HERE / AP_NAME
    require(sha(path.read_bytes()) == AP_SHA, 'FROZEN_AP_SOURCE_CHANGED')
    spec = importlib.util.spec_from_file_location('_ie_frozen_ap', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def elements(value):
    require(isinstance(value, str) and re.fullmatch(r'(?:[0-9a-f]{2}){0,2048}', value), 'IE_HEX')
    data = bytes.fromhex(value)
    found, offset = [], 0
    while offset < len(data):
        require(offset + 2 <= len(data), 'IE_HEADER_TRUNCATED')
        end = offset + 2 + data[offset + 1]
        require(end <= len(data) and data[offset] == 221 and data[offset + 1] >= 3, 'IE_LENGTH_OR_TYPE')
        found.append(data[offset:end])
        offset = end
    return found


def original_elements(text, interface):
    """Parse only interface/bss/vendor_elements lines, never a key/config dump."""
    section, matches = None, []
    for line in text.replace('\r', '').splitlines():
        if line.startswith('FILE '):
            section = None
        elif line.startswith(('interface=', 'bss=')):
            section = line.split('=', 1)[1]
            if section == interface:
                matches.append([])
        elif line.startswith('vendor_elements='):
            require(section is not None, 'AMBIGUOUS_VENDOR_SCOPE')
            if section == interface:
                matches[-1].append(line.split('=', 1)[1])
    require(len(matches) == 1 and len(matches[0]) <= 1, 'HOSTAPD_CONFIG_TARGET_AMBIGUOUS')
    value = matches[0][0] if matches[0] else ''
    require(all(entry[2:5] not in (bytes.fromhex('00156d'), bytes.fromhex('002722'))
                for entry in elements(value)), 'BASELINE_ALREADY_HAS_UBIQUITI_IE')
    return value


class Window:
    def __init__(self):
        self.ap = load_ap()
        self.ready = None
        self.original = None
        self.used = False
        self.changed = False
        self.phases = []
        self.restoration = None

    def snapshot(self, client):
        ap = self.ap
        ap.identity(client)
        ap.guard_identity(client)
        changes = ap.checked(client, 'uci changes wireless').decode().splitlines()
        require(set(changes) == {"wireless.radio0.disabled='0'", "wireless.radio0.txpower='0'", "wireless.default_radio0.wds='1'"}
                and len(changes) == 3, 'UNEXPECTED_WIRELESS_RAM_DELTA')
        observed = ap.readiness(ap.checked(client, 'iw dev').decode(), ap.checked(client, 'iw reg get').decode(),
                                ap.checked(client, 'iw phy phy0 info').decode(),
                                json.loads(ap.checked(client, 'ubus call network.wireless status')))
        require(all(observed[name] == self.ready[name] for name in ('interface', 'ifindex', 'bssid')), 'VAP_IDENTITY_CHANGED')
        require((observed['frequency_mhz'], observed['width_mhz'], observed['txpower_dbm']) == (5180, 20, 0), 'RF_CHANGED')
        uptime = float(ap.checked(client, 'cat /proc/uptime').split()[0])
        return dict(host_utc=datetime.now(timezone.utc).isoformat(), host_monotonic=time.monotonic(),
                    ap_uptime_seconds=uptime, interface=observed['interface'], ifindex=observed['ifindex'],
                    bssid=observed['bssid'], frequency_mhz=5180, width_mhz=20, txpower_dbm=0,
                    config_hash_verified=True, only_owned_wireless_ram_deltas=True)

    def arm(self, client):
        require(not self.used, 'ONE_WINDOW_ONLY')
        self.used = True
        require(elements(TRIAL_IE) == [bytes.fromhex(TRIAL_IE)], 'TRIAL_IE_INVALID')
        self.ready = self.ap.arm(client)  # Independent 240s radio-off guard for operator run12.
        try:
            interface = self.ready['interface']
            require(re.fullmatch(r'[a-zA-Z0-9_.-]{1,15}', interface), 'TARGET_INTERFACE_INVALID')
            methods = self.ap.checked(client, 'ubus -v list ' + shlex.quote('hostapd.' + interface)).decode()
            require('"set_vendor_elements":{"vendor_elements":"String"}' in methods.replace(' ', '')
                    and '"update_beacon":{}' in methods.replace(' ', ''), 'CONTROL_METHODS_MISSING')
            filtered = self.ap.checked(client, "set -eu\nfor f in /var/run/hostapd*.conf; do\n"
                " test -f \"$f\" || continue\n printf 'FILE %s\\n' \"$f\"\n"
                " awk '/^(interface|bss|vendor_elements)=/{print}' \"$f\"\ndone").decode()
            self.original = original_elements(filtered, interface)
            return self.snapshot(client)
        except BaseException:
            self.restore(client)
            raise

    def set_elements(self, client, value):
        elements(value)
        obj = shlex.quote('hostapd.' + self.ready['interface'])
        body = shlex.quote(json.dumps(dict(vendor_elements=value), separators=(',', ':')))
        self.changed = True  # Intent precedes uncertain dispatch; cleanup always runs.
        self.ap.checked(client, 'set -e\nubus call ' + obj + ' set_vendor_elements ' + body
                        + '\nubus call ' + obj + ' update_beacon')

    def phase(self, client, name, include_trial):
        require(self.original is not None and self.ready is not None, 'WINDOW_NOT_ARMED')
        self.snapshot(client)
        self.set_elements(client, self.original + (TRIAL_IE if include_trial else ''))
        record = dict(phase=name, trial_ie_expected=include_trial, api_acknowledged=True,
                      ota_accepted=False, **self.snapshot(client))
        self.phases.append(record)
        return record

    def restore(self, client):
        clear_error = None
        if self.changed and self.original is not None:
            try:
                self.set_elements(client, self.original)
            except Exception as error:
                clear_error = type(error).__name__
        try:
            result = self.ap.restore(client)
        except RuntimeError as failure:
            if str(failure) != 'RADIO_VAP_REMAINS':
                raise
            original_failure = dict(type='RuntimeError', gate='RADIO_VAP_REMAINS')
            self.restoration = dict(original_restore_failure=original_failure, status='ASYNC_COMPLETION_PENDING')
            end = time.monotonic() + 10
            checked = self.ap.checked

            def within_deadline(c, command, timeout=25):
                remaining = end - time.monotonic()
                require(remaining > 0, 'ASYNC_COMPLETION_DEADLINE')
                result = checked(c, command, timeout=min(timeout, remaining))
                require(time.monotonic() <= end, 'ASYNC_COMPLETION_DEADLINE')
                return result

            self.ap.checked = within_deadline  # Private imported module only.
            try:
                while True:
                    try:
                        result = self.ap.off(client)
                        break
                    except RuntimeError as pending:
                        if str(pending) != 'RADIO_VAP_REMAINS' or time.monotonic() >= end:
                            raise
                        time.sleep(min(0.2, max(0, end - time.monotonic())))
                # Exact owned scripts/guard and restored marker; read-only completion.
                command = 'set -eu\n' + self.ap.header() + self.ap.file_guards() + '''
test -f "$D/restored"
read p s < "$D/guard.id"
test "$p $s" = "''' + str(self.ready['guard_pid']) + ' ' + str(self.ready['guard_start']) + '''"
if test -e /proc/$p/stat && test "$(awk '{print $22}' /proc/$p/stat)" = "$s" && test "$(awk '{print $3}' /proc/$p/stat)" != Z; then echo LIVE; else echo ENDED; fi
'''
                require(self.ap.checked(client, command).strip() == b'ENDED', 'GUARD_NOT_ENDED')
            finally:
                self.ap.checked = checked
            result.update(guard_ended_verified=True, original_restore_failure=original_failure,
                          readonly_async_completion=True)
        self.restoration = result
        require(result.get('status') == 'PASS_RAM_WINDOW_RESTORED_RADIO_OFF'
                and result.get('guard_ended_verified') is True, 'RESTORATION_INCOMPLETE')
        if clear_error:
            result['ie_clear_failure_type'] = clear_error
            raise RuntimeError('IE_CLEAR_FAILED_RADIO_OFF_VERIFIED')
        return result


def run(client, on_phase, phase_seconds=2):
    require(callable(on_phase) and type(phase_seconds) in (int, float) and 0.5 <= phase_seconds <= 5, 'CAPTURE_CALLBACK_OR_PHASE_DURATION')
    window = Window()
    window.arm(client)
    try:
        for name, present in (('baseline_absent', False), ('trial_present', True), ('restored_absent', False)):
            record = window.phase(client, name, present)
            on_phase(dict(event='phase_started', **record))
            time.sleep(phase_seconds)
            record['end'] = window.snapshot(client)
            on_phase(dict(event='phase_ended', **record))
    finally:
        window.restore(client)
    return dict(status='PASS_AP_IE_API_WINDOW_RESTORED_OTA_PENDING', phases=window.phases,
                restoration=window.restoration, trial_ie=TRIAL_IE, ap_source_sha256=AP_SHA,
                beacon_accepted=False, probe_response_accepted=False, association_accepted=False)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(dict(status='PLAN_ONLY_ROOT_INJECTED_CLIENT_AND_CAPTURE_CALLBACK_REQUIRED',
                          phases=['baseline_absent', 'trial_present', 'restored_absent'], phase_seconds=2,
                          trial_ie=TRIAL_IE, trial_ie_bytes=60, connects=False, persistent_writes=False)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
