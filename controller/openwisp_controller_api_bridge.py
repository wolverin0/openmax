"""OpenWISP 26.09 controller/monitoring bridge; imports and default CLI are offline.

Templates contain inactive profile JSON, never executable shell hooks. Stock devices
are inventory/telemetry targets; netjsonconfig.OpenWisp is not a stock airOS backend.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import ipaddress
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import ssl
import stat
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import (HTTPSHandler, HTTPRedirectHandler, ProxyHandler,
                            Request, build_opener)
from uuid import UUID

from controller.openwisp_netjson_rollback_agent import classify_command_layer

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S32B-CODEX-OPENWISP-CONTROLLER-BRIDGE-AND-TEMPLATE-PACK"
PROFILE_SOURCE = ROOT/"controller/multiradio_golden_profile_applicator.py"
LEDGER = ROOT/"artifacts/autoresearch/champion_state_ledger.json"
TEMPLATE_DIR = ROOT/"artifacts/openwisp_templates"
OPENWRT_BACKEND = "netjsonconfig.OpenWrt"
PROFILE_IDS = (
    "af4x_invictus", "ltu_lite_amesoc", "r2ac_prism_ap", "r5ac_prism_sta",
    "pbm5_xw_weak_ota", "openwrt_lap120_ptp_1cpe_champion",
    "openwrt_lap120_ptmp_multicpe_champion", "ltu_ptmp_3unit_sector_champion",
)
PROFILE_FIELDS = {
    "profile_id", "device_family", "firmware_baseline", "soc_and_radio",
    "apply_commands", "rollback_commands", "verify_commands",
    "validated_rounds", "key_findings_summary",
}
FAMILIES = {"openwrt", "airos8", "airos6", "ltu", "airfiber"}
MAX_BYTES = 4*1024*1024
MAX_RESPONSE = 16*1024*1024
MANAGED_NOTE = "FuturaMAX Stage32B inactive profile reference: "
# Independently retained value hash from the reviewed Stage31A/v8 source+ledger.
# New champions require an intentional reviewed pack revision, not self-rehashing.
APPROVED_PROFILE_SET_SHA256 = "f6bcc464f137894f1bf93d6201b1b41b808002981485f36aee654153b4849875"
WIRELESS_REQUIRED = {"channel", "country", "frequency", "mode", "noise", "ssid", "tx_power"}
CLIENT_REQUIRED = {"auth", "authorized", "ht", "vht", "wmm", "mac", "mfp"}


def _require(condition: Any, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json(raw: str | bytes) -> Any:
    def pairs(items):
        out = {}
        for key, value in items:
            _require(key not in out, "Duplicate JSON key")
            out[key] = value
        return out
    def bad(_):
        raise ValueError("Nonfinite JSON constant")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def _local(path: str | Path) -> Path:
    text = os.fspath(path)
    _require(type(text) is str and not text.replace("/", "\\").startswith(("\\\\", "\\??\\"))
             and "://" not in text and not PureWindowsPath(text).is_reserved(),
             "Regular local path required")
    result = Path(text).absolute()
    if os.name == "nt":
        import ctypes
        _require(ctypes.windll.kernel32.GetDriveTypeW(str(result.anchor)) != 4,
                 "Mapped remote paths are not local artifacts")
    for parent in reversed((result, *result.parents)):
        try:
            info = parent.lstat()
        except FileNotFoundError:
            break
        _require(not stat.S_ISLNK(info.st_mode)
                 and not getattr(info, "st_file_attributes", 0) & 0x400,
                 "Symlink/reparse artifact path")
    return result


def _read(path: str | Path) -> bytes:
    path = _local(path)
    info = path.stat()
    _require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_BYTES, "Bounded regular input required")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES+1)
    _require(len(raw) <= MAX_BYTES, "Input too large")
    return raw


def _uuid(value: str) -> str:
    _require(type(value) is str, "UUID string required")
    try:
        return str(UUID(value))
    except (ValueError, AttributeError):
        raise ValueError("Invalid UUID") from None


def _text(value: str, maximum: int = 255) -> str:
    _require(type(value) is str and 0 < len(value) <= maximum
             and not any(ord(c) < 32 for c in value), "Bounded text without controls required")
    return value


def _key(value: str) -> str:
    _require(type(value) is str and re.fullmatch(r"[A-Za-z0-9._~+/=-]{1,4096}", value),
             "Invalid authentication token")
    return value


def _mac(value: str) -> str:
    _require(type(value) is str and re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", value),
             "Canonical MAC address required")
    return value.lower()


def _observed(value: str | datetime) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Observation timestamp must include a timezone") from None
    _require(isinstance(value, datetime) and value.tzinfo is not None
             and value.utcoffset() is not None, "Observation timestamp must include a timezone")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class HTTPResult:
    status: int
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)


class OpenWISPAPIError(RuntimeError):
    """Deliberately excludes response bodies, tokens, query keys and passwords."""
    def __init__(self, message: str, *, status: int | None = None,
                 method: str = "", resource: str = "", ambiguous_write: bool = False):
        self.status = status
        self.method = method
        self.resource = resource
        self.ambiguous_write = ambiguous_write
        self.partial_results = []
        self.failed_profile_id = None
        super().__init__(f"{message} ({method} {resource}; status={status}; "
                         f"ambiguous_write={ambiguous_write})")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _http_transport(method, url, headers, body, timeout) -> HTTPResult:
    # Neither ambient proxies nor redirects may forward controller/device credentials.
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()),
                          _NoRedirect())
    request = Request(url, data=body, headers=headers, method=method)
    try:
        stream = opener.open(request, timeout=timeout)
    except HTTPError as exc:
        stream = exc
    with stream:
        raw = stream.read(MAX_RESPONSE+1)
        _require(len(raw) <= MAX_RESPONSE, "Controller response too large")
        return HTTPResult(stream.code, raw, dict(stream.headers.items()))


class OpenWISPClient:
    """Complete scoped device/template CRUD, agent protocol and monitoring client.

    Mutations require allow_writes=True. Supplying a fake transport makes every
    operation local; this module never enables writes or constructs a live client
    during import or template generation.
    """
    def __init__(self, base_url: str, token: str | None = None, *,
                 allow_writes: bool = False, allow_insecure_localhost: bool = False,
                 timeout: float = 10, retries: int = 2,
                 transport: Callable | None = None, sleep: Callable = time.sleep):
        parts = urlsplit(_text(base_url, 2048))
        _require(parts.hostname and not parts.username and not parts.password
                 and not parts.query and not parts.fragment
                 and "%" not in parts.path and ".." not in parts.path.split("/"),
                 "Controller URL must not contain credentials, query or traversal")
        loopback = parts.hostname == "localhost"
        try:
            loopback = loopback or ipaddress.ip_address(parts.hostname).is_loopback
        except ValueError:
            pass
        _require(parts.scheme == "https" or parts.scheme == "http"
                 and allow_insecure_localhost is True and loopback,
                 "HTTPS required; HTTP is limited to explicit localhost development")
        _require(type(allow_writes) is bool and type(allow_insecure_localhost) is bool,
                 "Boolean write/development flags required")
        _require(type(timeout) in (int, float) and math.isfinite(timeout) and 0 < timeout <= 120,
                 "Timeout must be finite and bounded")
        _require(type(retries) is int and 0 <= retries <= 3, "Bounded retry count required")
        self.base_url = base_url.rstrip("/")
        self._origin = (parts.scheme, parts.netloc.lower())
        self._prefix = parts.path.rstrip("/")
        self._token = _key(token) if token is not None else None
        self.allow_writes, self.timeout, self.retries = allow_writes, timeout, retries
        self._transport, self._sleep = transport or _http_transport, sleep

    def request(self, method: str, resource: str, *, data=None, params=None,
                auth: bool = True, response: str = "json", form: bool = False):
        _require(method in {"GET", "POST", "PUT", "PATCH", "DELETE"}, "Unsupported HTTP method")
        _require(type(resource) is str and resource.startswith(("/api/v1/", "/controller/device/"))
                 and not any(c in resource for c in ("?", "#", "%", "\\"))
                 and ".." not in resource.split("/") and "//" not in resource,
                 "Relative OpenWISP resource required")
        _require(response in ("json", "text", "binary"), "Unsupported response format")
        write = method != "GET"
        if write and not self.allow_writes:
            raise PermissionError("Controller writes require explicit allow_writes=True")
        if auth and self._token is None:
            raise PermissionError("Admin API requires a user Bearer token")
        headers = {"Accept": "application/json" if response == "json" else "*/*"}
        if auth:
            headers["Authorization"] = "Bearer "+self._token
        body = None
        if data is not None:
            body = urlencode(data).encode() if form else _canonical(data)
            _require(len(body) <= MAX_BYTES, "Request body too large")
            headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
        url = self.base_url+resource
        if params:
            url += "?"+urlencode(params)
        for attempt in range(self.retries+1):
            try:
                result = self._transport(method, url, headers, body, self.timeout)
            except (URLError, TimeoutError, OSError):
                if not write and attempt < self.retries:
                    self._sleep(min(.25*2**attempt, 2))
                    continue
                raise OpenWISPAPIError("Transport failed", method=method, resource=resource,
                                       ambiguous_write=write) from None
            _require(isinstance(result, HTTPResult) and type(result.status) is int
                     and type(result.body) is bytes and len(result.body) <= MAX_RESPONSE,
                     "Invalid bounded transport response")
            if result.status in (429, 500, 502, 503, 504) and not write and attempt < self.retries:
                self._sleep(min(.25*2**attempt, 2))
                continue
            if not 200 <= result.status < 300:
                raise OpenWISPAPIError("Controller rejected request", status=result.status,
                                       method=method, resource=resource,
                                       ambiguous_write=write and result.status >= 500)
            if response == "binary":
                return result.body
            try:
                text = result.body.decode("utf-8")
                return _json(text) if text and response == "json" else text if response == "text" else None
            except (ValueError, UnicodeDecodeError):
                raise OpenWISPAPIError("Invalid controller response", status=result.status,
                                       method=method, resource=resource,
                                       ambiguous_write=write) from None
        raise AssertionError("Unreachable bounded request state")

    def authenticate(self, username: str, password: str) -> str:
        payload = self.request("POST", "/api/v1/users/token/", auth=False,
                               data={"username": _text(username), "password": _text(password, 4096)})
        _require(type(payload) is dict and "token" in payload, "Token response missing token")
        self._token = _key(payload["token"])
        return self._token

    def _list(self, resource: str, params=None) -> list[dict]:
        output, seen, next_params, total_bytes = [], set(), params or {}, 0
        original_params = dict(next_params)
        for _ in range(100):
            marker = urlencode(sorted(next_params.items()))
            _require(marker not in seen, "Pagination cycle")
            seen.add(marker)
            value = self.request("GET", resource, params=next_params)
            total_bytes += len(_canonical(value))
            _require(total_bytes <= MAX_RESPONSE, "Total collection byte limit exceeded")
            if isinstance(value, list):
                rows, next_url = value, None
            else:
                _require(type(value) is dict and type(value.get("results")) is list,
                         "Invalid paginated collection")
                rows, next_url = value["results"], value.get("next")
            _require(all(type(row) is dict for row in rows), "Object collection required")
            output.extend(rows)
            _require(len(output) <= 10000, "Collection size limit exceeded")
            if not next_url:
                return output
            parts = urlsplit(next_url)
            _require(not parts.fragment and not parts.username and not parts.password
                     and (not parts.netloc or (parts.scheme, parts.netloc.lower()) == self._origin)
                     and parts.path in (self._prefix+resource, "") and "%" not in parts.path,
                     "Cross-origin/resource pagination forbidden")
            pairs = parse_qsl(parts.query, keep_blank_values=True, max_num_fields=30)
            _require(len({k for k, _ in pairs}) == len(pairs), "Duplicate pagination parameter")
            next_params = dict(pairs)
            for key, original in original_params.items():
                _require(key not in next_params or next_params[key] == str(original),
                         "Pagination changed a scoped collection filter")
                next_params[key] = original
        raise ValueError("Pagination page limit exceeded")

    def list_devices(self, organization=None):
        return self._list("/api/v1/controller/device/",
                          {"organization": _uuid(organization)} if organization else None)

    def get_device(self, device_id):
        return self.request("GET", f"/api/v1/controller/device/{_uuid(device_id)}/")

    def create_device(self, payload):
        return self.request("POST", "/api/v1/controller/device/", data=payload)

    def update_device(self, device_id, payload):
        return self.request("PATCH", f"/api/v1/controller/device/{_uuid(device_id)}/", data=payload)

    def delete_device(self, device_id):
        return self.request("DELETE", f"/api/v1/controller/device/{_uuid(device_id)}/")

    def list_templates(self, organization=None):
        return self._list("/api/v1/controller/template/",
                          {"organization": _uuid(organization)} if organization else None)

    def get_template(self, template_id):
        return self.request("GET", f"/api/v1/controller/template/{_uuid(template_id)}/")

    def create_template(self, payload):
        return self.request("POST", "/api/v1/controller/template/", data=payload)

    def update_template(self, template_id, payload):
        return self.request("PATCH", f"/api/v1/controller/template/{_uuid(template_id)}/", data=payload)

    def delete_template(self, template_id):
        return self.request("DELETE", f"/api/v1/controller/template/{_uuid(template_id)}/")

    def register_device(self, *, organization, name, mac_address, family,
                        model="", os_version="", management_ip=None):
        _require(family in FAMILIES, "Unknown device family")
        organization, mac_address = _uuid(organization), _mac(mac_address)
        existing = [d for d in self.list_devices(organization)
                    if d.get("organization") == organization
                    and str(d.get("mac_address", "")).lower() == mac_address]
        _require(len(existing) <= 1, "Ambiguous device identity")
        if existing:
            return existing[0]
        payload = dict(organization=organization, name=_text(name), mac_address=mac_address,
                       model=_text(model) if model else "", os=_text(os_version) if os_version else family,
                       system="FuturaMAX "+family,
                       notes="FuturaMAX Stage32B: "+("native OpenWrt inventory" if family == "openwrt"
                             else "hybrid inventory/telemetry only; no native configuration backend"))
        if management_ip is not None:
            payload["management_ip"] = str(ipaddress.ip_address(management_ip))
        if family == "openwrt":
            payload["config"] = {"backend": OPENWRT_BACKEND, "config": {"type": "DeviceConfiguration"}}
        return self.create_device(payload)

    def attach_templates(self, device_id, template_ids):
        _require(type(template_ids) is list and len(template_ids) <= 100, "Bounded template list required")
        device = self.get_device(device_id)
        config = device.get("config")
        _require(type(config) is dict and config.get("backend") == OPENWRT_BACKEND,
                 "Native OpenWrt configuration required; hybrid inventory cannot attach it")
        current = config.get("templates", [])
        _require(type(current) is list, "Existing template list required")
        merged = list(dict.fromkeys(_uuid(v) for v in current+template_ids))
        replacement = {k: copy.deepcopy(config[k]) for k in ("backend", "config", "context") if k in config}
        replacement["templates"] = merged
        return self.update_device(device_id, {"config": replacement})

    def get_device_configuration(self, device_id):
        return self.request("GET", f"/api/v1/controller/device/{_uuid(device_id)}/configuration/",
                            response="binary")

    def list_device_metrics(self, device_id):
        return self._list(f"/api/v1/monitoring/device/{_uuid(device_id)}/metric/")

    def post_monitoring(self, device_id, device_key, payload, observed_at=None):
        device_id = _uuid(device_id)
        validate_device_monitoring(payload)
        declared = payload.get("futuramax", {}).get("device_id")
        _require(declared is None or declared == device_id, "Telemetry device mismatch")
        params = {"key": _key(device_key)}
        if observed_at is not None:
            params["time"] = _observed(observed_at).strftime("%d-%m-%Y_%H:%M:%S.%f")
        return self.request("POST", f"/api/v1/monitoring/device/{device_id}/",
                            data=payload, params=params, auth=False)

    def register_openwrt_agent(self, *, organization_secret, name, mac_address,
                               backend=OPENWRT_BACKEND):
        _require(backend == OPENWRT_BACKEND, "Only the native OpenWrt agent is supported")
        text = self.request("POST", "/controller/device/register/", auth=False, form=True,
                            response="text", data={"secret": _key(organization_secret),
                            "name": _text(name), "mac_address": _mac(mac_address), "backend": backend})
        result = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                _require(key not in result, "Duplicate registration field")
                result[key] = value.strip()
        _require(result.get("registration-result", "success") == "success", "Registration did not succeed")
        result["uuid"], result["key"] = _uuid(result.get("uuid")), _key(result.get("key"))
        return result

    def get_agent_checksum(self, device_id, device_key):
        return self.request("GET", f"/controller/device/checksum/{_uuid(device_id)}/",
                            params={"key": _key(device_key)}, auth=False, response="text")

    def get_agent_configuration(self, device_id, device_key):
        return self.request("GET", f"/controller/device/download-config/{_uuid(device_id)}/",
                            params={"key": _key(device_key)}, auth=False, response="binary")

    def report_agent_status(self, device_id, device_key, status, error_reason=None):
        data = {"key": _key(device_key), "status": _text(status, 32)}
        if error_reason is not None:
            data["error_reason"] = _text(error_reason, 4096)
        return self.request("POST", f"/controller/device/report-status/{_uuid(device_id)}/",
                            data=data, auth=False, form=True, response="text")

    def sync_templates(self, pack, organization):
        validate_template_pack(pack)
        organization = _uuid(organization)
        existing = self.list_templates(organization)
        receipts = []
        for profile_id, source in pack["templates"].items():
            try:
                payload = copy.deepcopy(source)
                payload["organization"] = organization
                matches = [row for row in existing if row.get("name") == payload["name"]
                           and row.get("organization") == organization]
                _require(len(matches) <= 1, "Duplicate managed template name")
                if not matches:
                    result = self.create_template(payload)
                    action = "CREATED"
                else:
                    current = matches[0]
                    _require(current.get("notes", "").startswith(MANAGED_NOTE+profile_id+"\n"),
                             "Existing template is not owned by this bridge")
                    if all(current.get(k) == v for k, v in payload.items()):
                        result, action = current, "UNCHANGED"
                    else:
                        result = self.update_template(_uuid(current["id"]), payload)
                        action = "UPDATED"
                _require(type(result) is dict and "id" in result, "Template API did not return an ID")
                receipts.append({"profile_id": profile_id, "id": _uuid(result["id"]), "action": action})
            except (OpenWISPAPIError, ValueError, PermissionError) as exc:
                exc.partial_results = copy.deepcopy(receipts)
                exc.failed_profile_id = profile_id
                raise
        return receipts


def _source_profiles(raw: bytes) -> dict:
    tree = ast.parse(raw.decode("utf-8"))
    node = next((n.value for n in tree.body if isinstance(n, ast.AnnAssign)
                 and isinstance(n.target, ast.Name) and n.target.id == "GOLDEN_PROFILES"), None)
    _require(isinstance(node, ast.Dict), "Literal Golden Profile declaration required")
    profiles = {}
    for key, value in zip(node.keys, node.values):
        ident = ast.literal_eval(key)
        _require(isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                 and value.func.id == "GoldenRadioProfile" and not value.args,
                 "Literal GoldenRadioProfile constructor required")
        row = {kw.arg: ast.literal_eval(kw.value) for kw in value.keywords}
        _require(set(row) == PROFILE_FIELDS and ident not in profiles and row["profile_id"] == ident,
                 "Invalid or duplicate Golden Profile")
        profiles[ident] = row
    _validate_profiles(profiles)
    return profiles


def _validate_profiles(profiles):
    _require(type(profiles) is dict and set(profiles) == set(PROFILE_IDS), "Exactly eight Golden Profiles required")
    for ident, row in profiles.items():
        _require(type(row) is dict and set(row) == PROFILE_FIELDS and row["profile_id"] == ident,
                 "Invalid profile fields")
        for key in ("apply_commands", "rollback_commands", "verify_commands", "validated_rounds"):
            _require(type(row[key]) is list and all(type(v) is str and len(v) <= 16384 for v in row[key]),
                     "Ordered profile string lists required")
        for key in PROFILE_FIELDS-{"apply_commands", "rollback_commands", "verify_commands", "validated_rounds"}:
            _require(type(row[key]) is str and len(row[key]) <= 16384, "Bounded profile strings required")
    for ident in ("openwrt_lap120_ptp_1cpe_champion", "openwrt_lap120_ptmp_multicpe_champion"):
        _require("S31A-R1" in profiles[ident]["validated_rounds"], "Stage31A Champion v8 evidence missing")
    _require(_sha(_canonical(profiles)) == APPROVED_PROFILE_SET_SHA256,
             "Profile values differ from the independently approved Stage32B/v8 cutoff")


def _template(profile):
    ident = profile["profile_id"]
    reference = {
        "schema_version": 1, "profile": copy.deepcopy(profile),
        "profile_sha256": _sha(_canonical(profile)),
        "command_layers": [{"index": i, "layer": classify_command_layer(command)}
                           for i, command in enumerate(profile["apply_commands"])],
        "runtime_dispatch_allowed": False, "rollback_runtime_verified": False,
        "semantics": "Inactive ordered source reference; no execution or exact restoration authority",
    }
    return dict(name="FMX "+ident, organization=None, type="generic", backend=OPENWRT_BACKEND,
                default=False, required=False, notes=MANAGED_NOTE+ident+"\n"+reference["profile_sha256"],
                config={"type": "DeviceConfiguration", "files": [{
                    "path": "/tmp/futuramax/"+ident+".json", "mode": "0600",
                    "contents": _canonical(reference).decode()+"\n",
                }]})


def build_template_pack(ledger_path=LEDGER, profile_source_path=PROFILE_SOURCE):
    source, ledger_raw = _read(profile_source_path), _read(ledger_path)
    profiles, ledger = _source_profiles(source), _json(ledger_raw)
    _require(type(ledger) is dict and ledger.get("profiles_count") == 8
             and ledger.get("profiles") == profiles, "Golden Profile source/ledger drift")
    templates = {ident: _template(profiles[ident]) for ident in PROFILE_IDS}
    manifest = dict(schema_version=1, task_id=TASK_ID, profiles_count=8,
                    profile_set_sha256=_sha(_canonical(profiles)), source_profiles=profiles,
                    source_bindings=[
                        {"path": str(profile_source_path), "bytes": len(source), "sha256": _sha(source)},
                        {"path": str(ledger_path), "bytes": len(ledger_raw), "sha256": _sha(ledger_raw)},
                    ],
                    artifacts={ident+".json": _sha(_canonical(value)+b"\n")
                               for ident, value in templates.items()},
                    runtime_dispatch_allowed=False, physical_acceptance=False)
    return {"manifest": manifest, "templates": templates}


def validate_template_pack(pack):
    _require(type(pack) is dict and set(pack) == {"manifest", "templates"}, "Template pack required")
    manifest = pack["manifest"]
    fields = {"schema_version", "task_id", "profiles_count", "profile_set_sha256",
              "source_profiles", "source_bindings", "artifacts",
              "runtime_dispatch_allowed", "physical_acceptance"}
    _require(type(manifest) is dict and set(manifest) == fields
             and manifest.get("schema_version") == 1
             and manifest.get("task_id") == TASK_ID and manifest.get("profiles_count") == 8,
             "Invalid template manifest")
    bindings = manifest["source_bindings"]
    _require(type(bindings) is list and len(bindings) == 2, "Two observed input bindings required")
    for row in bindings:
        _require(type(row) is dict and set(row) == {"path", "bytes", "sha256"}
                 and type(row["path"]) is str and type(row["bytes"]) is int
                 and 0 <= row["bytes"] <= MAX_BYTES and type(row["sha256"]) is str
                 and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "Invalid observed source binding")
    profiles = manifest.get("source_profiles")
    _validate_profiles(profiles)
    expected = {ident: _template(profiles[ident]) for ident in PROFILE_IDS}
    _require(_canonical(pack["templates"]) == _canonical(expected), "Template differs from inactive source contract")
    _require(manifest.get("profile_set_sha256") == _sha(_canonical(profiles))
             and manifest.get("artifacts") == {i+".json": _sha(_canonical(v)+b"\n") for i, v in expected.items()}
             and manifest.get("runtime_dispatch_allowed") is False
             and manifest.get("physical_acceptance") is False, "Template integrity/dispatch metadata mismatch")
    return True


def write_template_pack(pack, output_dir=TEMPLATE_DIR) -> Path:
    validate_template_pack(pack)
    folder = _local(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    # Validate every target before the first write; never remove unrelated artifacts.
    targets = {ident: _local(folder/(ident+".json")) for ident in PROFILE_IDS}
    manifest_path = _local(folder/"manifest.json")
    for ident, path in targets.items():
        path.write_bytes(_canonical(pack["templates"][ident])+b"\n")
    manifest_path.write_bytes(_canonical(pack["manifest"])+b"\n")
    return manifest_path


def load_template_pack(output_dir=TEMPLATE_DIR):
    folder = _local(output_dir)
    pack = {"manifest": _json(_read(folder/"manifest.json")),
            "templates": {ident: _json(_read(folder/(ident+".json"))) for ident in PROFILE_IDS}}
    validate_template_pack(pack)
    for ident in PROFILE_IDS:
        _require(_sha(_read(folder/(ident+".json"))) == pack["manifest"]["artifacts"][ident+".json"],
                 "Template file bytes changed")
    return pack


def _mapping(value):
    if value is None:
        return {}
    if isinstance(value, str):
        _require(len(value) <= MAX_BYTES, "Telemetry input too large")
        if value.lstrip().startswith("{"):
            value = _json(value)
        else:
            fields = {}
            for line in value.splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                _require("=" in line, "Telemetry status must be JSON or key=value lines")
                key, item = line.split("=", 1)
                _require(key.strip() not in fields, "Duplicate status key")
                fields[key.strip()] = item.strip()
            value = fields
    _require(type(value) is dict and len(_canonical(value)) <= MAX_BYTES, "Telemetry object required")
    return value


def _number(value, *, integer=False, minimum=None, maximum=None):
    if isinstance(value, str) and re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value.strip()):
        value = int(value) if re.fullmatch(r"[-+]?\d+", value.strip()) else float(value)
    if type(value) not in (int, float):
        return None
    try:
        if not math.isfinite(value):
            return None
    except OverflowError:
        return None
    if integer and int(value) != value or minimum is not None and value < minimum or maximum is not None and value > maximum:
        return None
    return int(value) if integer else value


def translate_stock_telemetry(family, payload, *, device_id, observed_at, radio_interface=None):
    _require(family in FAMILIES-{"airfiber"}, "Unsupported telemetry family")
    payload, device_id, observed = _mapping(payload), _uuid(device_id), _observed(observed_at)
    status = _mapping(payload.get("status", payload))
    host = _mapping(status.get("host", {}))
    wireless = _mapping(status.get("wireless", {}))
    extension = dict(family=family, device_id=device_id, observed_at=observed.isoformat(),
                     metrics=[], missing_fields=[], custom_charts_configured=False)
    result = {"type": "DeviceMonitoring", "futuramax": extension}
    metrics, missing = extension["metrics"], extension["missing_fields"]

    def observed_number(name, value, unit, source, scope="device", minimum=None, maximum=None, integer=False):
        number = _number(value, integer=integer, minimum=minimum, maximum=maximum)
        if number is None:
            missing.append(source)
        else:
            metrics.append(dict(name=name, value=number, unit=unit, scope=scope, source=source))
        return number

    general = {}
    for key in ("uptime", "local_time"):
        value = host.get(key, status.get(key))
        number = observed_number(key, value, "s", "status.host."+key, minimum=0, integer=True)
        if number is not None:
            general[key] = number
    if general:
        result["general"] = general
    source_resources = _mapping(payload.get("resources", host.get("resources", host)))
    resources = {}
    cpus = _number(source_resources.get("cpus"), integer=True, minimum=1)
    load = source_resources.get("load")
    if (cpus is not None and type(load) is list and len(load) == 3
            and all(_number(v, minimum=0) is not None for v in load)):
        resources.update(cpus=cpus, load=[_number(v) for v in load])
    elif cpus is not None or load is not None:
        missing.append("resources.load_and_cpus_complete_pair")
    memory = source_resources.get("memory")
    if type(memory) is dict:
        converted = {k: _number(v, integer=True, minimum=0) for k, v in memory.items()
                     if k in {"total", "free", "buffered", "shared", "cached", "available"}}
        if (all(converted.get(k) is not None for k in ("total", "free", "buffered", "shared"))
                and converted["total"] > 0
                and all(v is None or v <= converted["total"] for v in converted.values())):
            resources["memory"] = {k: v for k, v in converted.items() if v is not None}
        else:
            missing.append("resources.memory.complete_bytes")
    if resources:
        result["resources"] = resources

    # Names below have explicit units. Raw RSSI chains, capacities and HTTP timings
    # never become dBm, measured goodput or packet loss by inference.
    mappings = [
        ("signal_dbm", "dBm", ("signal_dbm", "signal", "rxpower0"), -160, 0),
        ("noise_dbm", "dBm", ("noise_dbm", "noisefloor", "noisef", "noise"), -180, 0),
        ("tx_rate_mbps", "Mbit/s", ("tx_rate_mbps", "tx_rate", "tx_bitrate_mbps"), 0, None),
        ("rx_rate_mbps", "Mbit/s", ("rx_rate_mbps", "rx_rate", "rx_bitrate_mbps"), 0, None),
        ("goodput_mbps", "Mbit/s", ("goodput_mbps",), 0, None),
        ("ssh_stream_mbps", "Mbit/s", ("ssh_stream_mbps",), 0, None),
        ("frequency_mhz", "MHz", ("frequency_mhz", "frequency"), 1, 100000),
        ("channel_width_mhz", "MHz", ("channel_width_mhz", "chanbw", "txchanbw"), 1, 320),
        ("rtt_p50_ms", "ms", ("p50_ms", "p50_rtt_ms"), 0, None),
        ("rtt_p95_ms", "ms", ("p95_ms", "p95_rtt_ms"), 0, None),
        ("rtt_p99_ms", "ms", ("p99_ms", "p99_rtt_ms"), 0, None),
        ("packet_loss_pct", "%", ("loss_pct",), 0, 100),
        ("cpu_utilization_pct", "%", ("cpuload", "cpu_utilization_pct"), 0, 100),
    ]

    def extract(scope, objects):
        for name, unit, aliases, low, high in mappings:
            for prefix, data in objects:
                found = next((key for key in aliases if key in data), None)
                if found is not None:
                    observed_number(name, data[found], unit, prefix+"."+found, scope, low, high)
                    break

    extract("device", [("status.wireless", wireless), ("status.host", host),
                        ("status", status), ("payload", payload), ("payload.latency", _mapping(payload.get("latency")))])
    interfaces = payload.get("interfaces", [])
    _require(type(interfaces) is list and len(interfaces) <= 256, "Bounded interface list required")
    if radio_interface is not None:
        _text(radio_interface, 64)
        if not any(r.get("name") == radio_interface for r in interfaces if type(r) is dict):
            interfaces = interfaces+[{"name": radio_interface}]
    native_interfaces = []
    for interface in interfaces:
        _require(type(interface) is dict, "Interface object required")
        name = _text(interface.get("name"), 64)
        native = {"name": name}
        counters = interface.get("statistics", interface)
        _require(type(counters) is dict, "Interface statistics object required")
        rx = _number(counters.get("rx_bytes"), integer=True, minimum=0)
        tx = _number(counters.get("tx_bytes"), integer=True, minimum=0)
        if rx is not None and tx is not None:
            native["statistics"] = {"rx_bytes": rx, "tx_bytes": tx}
        elif "rx_bytes" in counters or "tx_bytes" in counters:
            missing.append("interfaces."+name+".rx_tx_bytes_pair")
            for key in ("rx_bytes", "tx_bytes"):
                if key in counters:
                    observed_number(key, counters[key], "bytes", "interfaces."+name+"."+key, name, minimum=0, integer=True)
        given_wireless = interface.get("wireless", wireless if name == radio_interface else {})
        _require(type(given_wireless) is dict, "Wireless object required")
        if given_wireless:
            if WIRELESS_REQUIRED <= set(given_wireless):
                native_wireless = {k: copy.deepcopy(given_wireless[k]) for k in WIRELESS_REQUIRED}
                clients = given_wireless.get("clients", [])
                _require(type(clients) is list, "Wireless clients list required")
                complete = [copy.deepcopy(c) for c in clients if type(c) is dict and CLIENT_REQUIRED <= set(c)]
                if "clients" in given_wireless and len(complete) == len(clients):
                    native_wireless["clients"] = complete
                elif clients:
                    missing.append("interfaces."+name+".wireless.client_flags")
                native["wireless"] = native_wireless
            else:
                missing.extend("interfaces."+name+".wireless."+k for k in sorted(WIRELESS_REQUIRED-set(given_wireless)))
        native_interfaces.append(native)
    if native_interfaces:
        _require(len({r["name"] for r in native_interfaces}) == len(native_interfaces), "Duplicate interface name")
        result["interfaces"] = native_interfaces
    stations = payload.get("stations", payload.get("wstalist", []))
    if isinstance(stations, str):
        stations = _json(stations)
    if isinstance(stations, dict):
        stations = stations.get("stations", [])
    _require(type(stations) is list and len(stations) <= 1024, "Bounded station list required")
    seen = set()
    for station in stations:
        _require(type(station) is dict, "Station object required")
        mac = _mac(station.get("mac"))
        _require(mac not in seen, "Duplicate station MAC")
        seen.add(mac)
        extract("station:"+mac, [("stations."+mac, station),
                ("stations."+mac+".latency", _mapping(station.get("latency")))])
    extension["missing_fields"] = sorted(set(missing))
    validate_device_monitoring(result)
    return result


def validate_device_monitoring(payload):
    _require(type(payload) is dict and payload.get("type") == "DeviceMonitoring"
             and len(_canonical(payload)) <= MAX_BYTES, "Finite DeviceMonitoring object required")
    general = payload.get("general", {})
    _require(type(general) is dict, "General object required")
    for key in ("local_time", "uptime"):
        if key in general:
            _require(type(general[key]) is int and general[key] >= 0, "Integer seconds required")
    resources = payload.get("resources", {})
    _require(type(resources) is dict, "Resources object required")
    if "load" in resources or "cpus" in resources:
        load = resources.get("load")
        _require(type(resources.get("cpus")) is int and resources["cpus"] > 0
                 and type(load) is list and len(load) == 3
                 and all(type(v) in (int, float) and _number(v, minimum=0) is not None for v in load),
                 "Complete finite load triple and positive CPU count required")
    if "memory" in resources:
        memory = resources["memory"]
        required = {"total", "free", "buffered", "shared"}
        _require(type(memory) is dict and required <= set(memory)
                 and all(type(v) is int and v >= 0 for v in memory.values())
                 and memory["total"] > 0 and all(v <= memory["total"] for v in memory.values()),
                 "Complete integer byte memory values with positive total required")
    interfaces = payload.get("interfaces", [])
    _require(type(interfaces) is list, "Interfaces list required")
    for interface in interfaces:
        _require(type(interface) is dict, "Interface object required")
        _text(interface.get("name"), 64)
        if "statistics" in interface:
            counters = interface["statistics"]
            _require(type(counters) is dict and all(type(counters.get(k)) is int and counters[k] >= 0
                     for k in ("rx_bytes", "tx_bytes")), "Complete cumulative RX/TX counters required")
        if "wireless" in interface:
            wireless = interface["wireless"]
            _require(type(wireless) is dict and WIRELESS_REQUIRED <= set(wireless), "Incomplete native wireless object")
            for key in ("channel", "frequency", "noise", "tx_power"):
                _require(type(wireless[key]) is int, "Native wireless integer required")
            _text(wireless["country"], 8)
            _require(type(wireless["ssid"]) is str, "Native SSID string required")
            _text(wireless["mode"], 32)
            for client in wireless.get("clients", []):
                _require(type(client) is dict and CLIENT_REQUIRED <= set(client), "Incomplete native wireless client")
                _mac(client["mac"])
                _require(all(type(client[k]) is bool for k in CLIENT_REQUIRED-{"mac"}), "Native client flags must be booleans")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", default="export-templates", choices=["export-templates"])
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--output-dir", type=Path, default=TEMPLATE_DIR)
    args = parser.parse_args(argv)
    pack = build_template_pack(args.ledger)
    path = write_template_pack(pack, args.output_dir)
    print(f"WROTE 8 inactive OpenWISP templates: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
