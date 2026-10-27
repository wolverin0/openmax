"""Offline evidence and safety checks; never import a bench runner or target code."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, ValidationError
import pytest


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "orchestration/autoresearch/firmware_knob_candidates.json"
SCHEMA_PATH = CATALOG_PATH.with_suffix(".schema.json")


def load_json(path):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON constant: {value}")

    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Non-finite JSON number: {value}")
        return number

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant, parse_float=finite_float)


def validate_catalog(catalog):
    def check_finite(value):
        if isinstance(value, dict):
            for child in value.values():
                check_finite(child)
        elif isinstance(value, list):
            for child in value:
                check_finite(child)
        elif isinstance(value, float):
            assert math.isfinite(value), "Non-finite evidence"

    check_finite(catalog)
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(catalog)
    sources = {source["id"]: source for source in catalog["sources"]}
    assert len(sources) == len(catalog["sources"]), "Duplicate source identity"
    knobs = {knob["id"]: knob for knob in catalog["knobs"]}
    assert len(knobs) == len(catalog["knobs"]), "Duplicate knob identity"
    identities = {identity["id"] for identity in catalog["firmware_identities"]}
    assert len(identities) == len(catalog["firmware_identities"])

    def check_domain(domain):
        low, high = domain["minimum"], domain["maximum"]
        assert (low is None) == (high is None), "Incomplete range"
        if low is not None:
            assert math.isfinite(low) and math.isfinite(high)
            assert low <= high, "Reversed range"
            if domain["kind"] in {"integer", "boolean", "bitfield"}:
                assert type(low) is int and type(high) is int
            for value in domain["values"]:
                assert type(value) in {int, float} and low <= value <= high
                if domain["kind"] in {"integer", "boolean", "bitfield"}:
                    assert type(value) is int, "Fractional integer domain"
        if domain["kind"] == "tuple":
            for value in domain["values"]:
                assert isinstance(value, list) and value
                assert all(type(item) is int and item >= 0 for item in value)

    for owner in catalog["firmware_identities"] + catalog["knobs"]:
        for reference in owner["source_refs"]:
            assert reference["source_id"] in sources, "Unbound evidence"
    for knob in catalog["knobs"]:
        assert set(knob["platform_scope"]) <= identities, "Unbound firmware scope"
        encoding = knob["encoding_domain"]
        safety = knob["ram_safety"]
        check_domain(encoding)
        for value in safety["observed_values"]:
            if encoding["kind"] in {"integer", "boolean", "bitfield"}:
                assert type(value) is int, "Fractional integer observation"
            if encoding["minimum"] is not None:
                assert type(value) in {int, float}
                assert encoding["minimum"] <= value <= encoding["maximum"], "Observation exceeds encoding"
        proposal = safety["proposal"]
        if proposal is not None:
            check_domain(proposal)
            assert proposal["kind"] != "unknown", "Unknown is not a proposal"
            assert encoding["kind"] != "unknown", "No proposal without a source domain"
            assert proposal["kind"] == encoding["kind"], "Proposal kind mismatch"
            assert proposal["unit"] == encoding["unit"], "Unit mismatch"
            if proposal["minimum"] is not None:
                assert encoding["minimum"] is not None
                assert encoding["minimum"] <= proposal["minimum"]
                assert proposal["maximum"] <= encoding["maximum"], "Proposal exceeds encoding"
            if encoding["values"]:
                assert all(value in encoding["values"] for value in proposal["values"])
        assert safety["approved_range"] is None and not knob["enabled"]
        assert not knob["rollback"]["verified"]

    ct = [knob for knob in catalog["knobs"] if knob["family"] == "ct_special"]
    assert {knob["interface"]["selector"] for knob in ct} == {str(i) for i in range(3, 17)}
    assert len(ct) == 14
    for knob in ct:
        assert knob["interface"]["state_readback"] == "help_only"
    for selector in ("3", "4", "6", "9", "11", "13"):
        knob = next(knob for knob in ct if knob["interface"]["selector"] == selector)
        assert knob["classification"] == "excluded", "Hazard/unsupported CT selector"
    for knob in catalog["knobs"]:
        if knob["family"] in {"wmi_pdev", "wmi_vdev"}:
            assert knob["platform_scope"] == ["ct_source_10_1"]
            assert knob["ram_safety"]["proposal"] is None, "Raw WMI is not an actuator"
        if knob["family"] in {"airos_sysctl", "airos_ioctl", "airos_module", "ltu_sysfs", "hardware"}:
            assert knob["ram_safety"]["proposal"] is None, "Closed-firmware range unqualified"
        if knob["id"].startswith("aql_"):
            assert knob["encoding_domain"]["unit"] == "us", "AQL counts airtime"
        if knob["id"] == "aql_txq_limit":
            for low, high in knob["ram_safety"]["observed_values"]:
                assert 0 < low <= high, "AQL low/high relation"
        if knob["id"] == "htt_aggr_size":
            for amsdu, ampdu in knob["ram_safety"]["observed_values"]:
                assert 1 <= amsdu <= 31 and 1 <= ampdu <= 64, "HTT semantic limits"
    return catalog


@pytest.fixture
def catalog():
    return load_json(CATALOG_PATH)


def test_catalog_schema_and_safety(catalog):
    validate_catalog(catalog)


def test_all_sources_are_local_and_hash_bound(catalog):
    for source in catalog["sources"]:
        relative = PurePosixPath(source["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT.resolve())
        assert path.is_file(), source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], source["path"]


def test_frozen_inputs_remain_bound(catalog):
    manifest_path = ROOT / "artifacts/autoresearch/firmware_knob_audit_20261024/input_snapshots.json"
    by_path = {source["path"]: source for source in catalog["sources"]}
    for snapshot in load_json(manifest_path):
        assert by_path[snapshot["path"]]["sha256"] == snapshot["sha256"]
        assert (ROOT / snapshot["path"]).stat().st_size == snapshot["bytes"]


def test_closed_firmware_inventory_and_integer_domains(catalog):
    findings = load_json(ROOT / "artifacts/autoresearch/firmware_knob_audit_20261024/wa_xc_ltu_findings.json")
    platform_ids = {"XC8.7.25": "xc_8_7_25", "WA8.7.25": "wa_8_7_25",
                    "aflturocket2.4.2": "ltu_ap_2_4_2", "afltu2.4.2": "ltu_cpe_2_4_2"}
    for finding in findings["findings"]:
        if finding["family"] == "WA8.7.25" and finding["path"] == "/sys/module/umac/parameters/*":
            # This original unknown was resolved by WaveA exact-image extraction.
            resolved = [knob for knob in catalog["knobs"] if knob["platform_scope"] == ["wa_8_7_25"]
                        and knob["family"] == "airos_module"]
            assert len(resolved) == 15 and all(knob["confidence"] == "CONFIRMED" for knob in resolved)
            continue
        matches = [knob for knob in catalog["knobs"]
                   if knob["platform_scope"] == [platform_ids[finding["family"]]]
                   and knob["interface"]["surface"] == finding["path"]]
        assert len(matches) == 1, finding["id"]
        knob = matches[0]
        assert knob["ram_safety"]["proposal"] is None
        assert finding["readback_truth"] in knob["limitations"]
        assert knob["rollback"]["method"] == finding["restoration_plan"]
        parser = finding["syntactic_domain"].get("parser")
        if parser in {"param_set_int", "param_set_uint"}:
            domain = knob["encoding_domain"]
            assert domain["minimum"] == (0 if parser == "param_set_uint" else -2147483648)
            assert domain["maximum"] == (4294967295 if parser == "param_set_uint" else 2147483647)
        if finding["confidence"] == "UNKNOWN":
            assert knob["confidence"] == "UNKNOWN" and knob["encoding_domain"]["kind"] == "unknown"


def test_wave_a_exact_wa_identity_tables_and_scalar_bounds(catalog):
    facts = load_json(ROOT / "artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/facts_final.json")
    assert facts["expected_umac_match"] is True
    modules = {module["name"]:module for module in facts["modules"]}
    assert modules["umac.ko"]["sha256"] == "660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6"
    wa = [knob for knob in catalog["knobs"] if knob["platform_scope"] == ["wa_8_7_25"]]
    assert len([knob for knob in wa if knob["family"] == "airos_module"]) == 15
    assert len([knob for knob in wa if knob["family"] == "airos_sysctl"]) == 34
    ioctl = [knob for knob in wa if knob["family"] == "airos_ioctl"]
    assert len(ioctl) == 309
    for descriptor in facts["umac_wext"]["8.7.25"]["records"]:
        offset = descriptor["evidence"]["section_offset"]
        matches = [knob for knob in ioctl if knob["interface"]["selector"].endswith("@ .rodata+" + offset)]
        assert len(matches) == 1
        knob = matches[0]
        assert knob["name"] == (descriptor["name"] or "Unnamed WEXT dispatcher " + offset)
        assert knob["interface"]["selector"].startswith(hex(descriptor["command_or_subcommand"]) + " ")
        args = descriptor["set_arguments"]
        if args["type"] == "signed32_integer" and args["count_or_capacity"] == 1:
            assert knob["encoding_domain"]["minimum"] == -2147483648
            assert knob["encoding_domain"]["maximum"] == 2147483647
        else:
            assert knob["encoding_domain"]["kind"] == "unknown"
        assert knob["ram_safety"]["approved_range"] is None and knob["ram_safety"]["proposal"] is None
    # The two chwidth aliases are different descriptors, not one name-keyed row.
    aliases = [knob for knob in ioctl if knob["name"] == "chwidth"]
    assert len(aliases) == 2 and len({knob["interface"]["selector"] for knob in aliases}) == 2


@pytest.mark.parametrize("field,value", [
    ("automatic_execution_allowed", True), ("actuation", "ssh"),
    ("mode", "live"), ("schema_version", 2),
])
def test_reject_catalog_activation(catalog, field, value):
    catalog[field] = value
    with pytest.raises((AssertionError, ValueError, ValidationError)):
        validate_catalog(catalog)


@pytest.mark.parametrize("mutation", [
    "enabled", "approved_range", "rollback", "command", "duplicate_id",
    "unbound_source", "unbound_platform", "reversed_range", "proposal_overflow",
    "unknown_range", "excluded_proposal", "aql_units", "aql_pair", "htt_overflow",
    "ct_hazard", "raw_wmi_proposal", "ct_missing", "remote_source", "path_escape",
    "null_range_bypass", "kind_bypass", "observed_infinity", "proposal_infinity",
    "ct_cca_3", "ct_cca_4",
    "fractional_proposal", "fractional_observation",
])
def test_reject_unsafe_mutations(catalog, mutation):
    knobs = {knob["id"]: knob for knob in catalog["knobs"]}
    first = catalog["knobs"][0]
    if mutation == "enabled":
        first["enabled"] = True
    elif mutation == "approved_range":
        first["ram_safety"]["approved_range"] = [0, 1]
    elif mutation == "rollback":
        first["rollback"]["verified"] = True
    elif mutation == "command":
        first["command"] = "target execution is forbidden"
    elif mutation == "duplicate_id":
        catalog["knobs"].append(deepcopy(first))
    elif mutation == "unbound_source":
        first["source_refs"][0]["source_id"] = "missing"
    elif mutation == "unbound_platform":
        first["platform_scope"] = ["not_this_firmware"]
    elif mutation == "reversed_range":
        knobs["aql_threshold"]["encoding_domain"]["minimum"] = 4294967296
    elif mutation == "proposal_overflow":
        knobs["aql_threshold"]["ram_safety"]["proposal"]["maximum"] = 4294967296
    elif mutation == "unknown_range":
        first["encoding_domain"].update(kind="unknown", minimum=0, maximum=1)
    elif mutation == "excluded_proposal":
        excluded = next(knob for knob in catalog["knobs"] if knob["classification"] == "excluded")
        excluded["ram_safety"]["proposal"] = deepcopy(knobs["aql_threshold"]["ram_safety"]["proposal"])
    elif mutation == "aql_units":
        knobs["aql_txq_limit"]["encoding_domain"]["unit"] = "KB"
    elif mutation == "aql_pair":
        knobs["aql_txq_limit"]["ram_safety"]["observed_values"] = [[12000, 5000]]
    elif mutation == "htt_overflow":
        knobs["htt_aggr_size"]["ram_safety"]["observed_values"] = [[3, 256]]
    elif mutation == "ct_hazard":
        next(knob for knob in catalog["knobs"] if knob["id"] == "ct_special_6")["classification"] = "research_candidate"
    elif mutation == "raw_wmi_proposal":
        wmi = next(knob for knob in catalog["knobs"] if knob["family"] == "wmi_pdev")
        wmi["ram_safety"]["proposal"] = deepcopy(knobs["aql_threshold"]["ram_safety"]["proposal"])
    elif mutation == "ct_missing":
        catalog["knobs"] = [knob for knob in catalog["knobs"] if knob["id"] != "ct_special_16"]
    elif mutation == "remote_source":
        catalog["sources"][0]["path"] = "https://example.invalid/evidence"
    elif mutation == "path_escape":
        catalog["sources"][0]["path"] = "../outside"
    elif mutation == "null_range_bypass":
        knobs["aql_threshold"]["ram_safety"]["proposal"].update(minimum=None, maximum=None, values=[-1, 4294967296])
    elif mutation == "kind_bypass":
        knobs["aql_threshold"]["ram_safety"]["proposal"].update(kind="string", minimum=None, maximum=None, values=[])
    elif mutation == "observed_infinity":
        first["ram_safety"]["observed_values"] = [float("inf")]
    elif mutation == "proposal_infinity":
        knobs["aql_threshold"]["ram_safety"]["proposal"].update(minimum=None, maximum=None, values=[float("inf")])
    elif mutation in {"ct_cca_3", "ct_cca_4"}:
        knobs["ct_special_" + mutation[-1]]["classification"] = "research_candidate"
    elif mutation == "fractional_proposal":
        proposal = deepcopy(knobs["ct_special_7"]["encoding_domain"])
        proposal.update(minimum=28, maximum=50, values=[28.5])
        knobs["ct_special_7"]["ram_safety"]["proposal"] = proposal
    elif mutation == "fractional_observation":
        knobs["ct_special_7"]["ram_safety"]["observed_values"] = [28.5]
    with pytest.raises((AssertionError, ValueError, ValidationError)):
        validate_catalog(catalog)


@pytest.mark.parametrize("literal", ["1e999", "NaN", "Infinity", "-Infinity"])
def test_reject_nonfinite_json_literals(tmp_path, literal):
    path = tmp_path / "nonfinite.json"
    path.write_text('{"value":' + literal + '}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(path)
