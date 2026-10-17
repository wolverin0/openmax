"""Regression checks on saved static evidence, NOT execution of target firmware.

These pin the addresses/dataflow supporting our two layout claims. They do not
qualify the QCA core or turn a LITBASE hypothesis into measured register state.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def rows(filename, address):
    report = json.loads((ROOT / "research/raw" / filename).read_text(encoding="utf-8"))
    if report["module_sha256"] != "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5":
        raise ValueError("unexpected target profile")
    window = next(w for w in report["tool"]["windows"] if w["address"] == address)
    if window["returncode"] != 0:
        raise ValueError("failed decoder result")
    return {i["address"]: i for i in window["instructions"][:len(window["syntax_prefix_addresses"]) ]}


class StaticLayoutEvidenceTests(unittest.TestCase):
    def test_jump_table_dispatch_formula_and_cases(self):
        code = rows("airmax-target-ap-trace-20261006-validated.json", 0x9b546c)
        self.assertEqual(code[0x9b54dd]["operands"], "a14, 51")
        self.assertEqual(code[0x9b54f4]["mnemonic"], "bltu")
        self.assertEqual(code[0x9b54fd]["mnemonic"], "addx2")
        self.assertEqual(code[0x9b54fd]["operands"], "a9, a10, a10")
        literal = code[0x9b54fa]["literal_model"]
        self.assertEqual(literal["status"], "CONDITIONAL_ON_UNVERIFIED_LITBASE")
        self.assertEqual(literal["hypothesis_literal_mapped_word_le"], 0x9b5505)
        self.assertEqual(code[0x9b5505 + 3 * 0x17]["operands"], "9b5c02")
        self.assertEqual(code[0x9b5505 + 3 * 0x1e]["operands"], "9b5b2f")

    def test_type17_positional_sources_and_destinations(self):
        code = rows("airmax-target-ap-cases-20261006-validated.json", 0x9b5c02)
        observed = {(i["mnemonic"], i["operands"]) for a, i in code.items() if a <= 0x9b5c93}
        for pair in [("l8ui", "a9, a3, 9"), ("addi.n", "a11, a3, 10"),
                     ("addi.n", "a11, a3, 12"), ("addi.n", "a11, a3, 14"),
                     ("addi", "a11, a3, 16"), ("s8i", "a9, a5, 12"),
                     ("s16i", "a9, a5, 14"), ("s16i", "a9, a5, 16"),
                     ("s16i", "a9, a5, 18"), ("s32i.n", "a14, a5, 20")]:
            self.assertIn(pair, observed)
        self.assertEqual(code[0x9b5c93]["operands"], "9b55b6")

    def test_type1e_byte_load_store_pairs(self):
        code = rows("airmax-target-ap-cases-20261006-validated.json", 0x9b5b2f)
        for index, reg in enumerate(("a13", "a12", "a11", "a10", "a9")):
            load = code[0x9b5b2f + 6 * index]
            store = code[0x9b5b32 + 6 * index]
            self.assertEqual((load["mnemonic"], load["operands"]), ("l8ui", f"{reg}, a3, {9 + index}"))
            self.assertEqual((store["mnemonic"], store["operands"]), ("s8i", f"{reg}, a5, {12 + index}"))
        self.assertEqual(code[0x9b5b4d]["operands"], "9b55b6")

    def test_common_exit_is_return_not_fallthrough_into_other_case(self):
        code = rows("airmax-target-ap-cases-20261006-validated.json", 0x9b55b6)
        self.assertEqual(code[0x9b55b6]["operands"], "a2, 0")
        self.assertEqual(code[0x9b55b8]["mnemonic"], "retw.n")

    def test_ptp_and_sta_parser_branches_match_same_two_subtypes(self):
        for role, parser, table, case17, case1e in (
                ("ptp", 0x9b3d9c, 0x9b3e35, "9b4093", "9b3fc4"),
                ("ptmp_sta", 0x9b4dbc, 0x9b4e55, "9b5552", "9b547f")):
            with self.subTest(role=role):
                code = rows(f"airmax-target-{role}-parser-20261006.json", parser)
                self.assertEqual(code[table + 3 * 0x17]["operands"], case17)
                self.assertEqual(code[table + 3 * 0x1e]["operands"], case1e)

    def test_ptp_and_sta_fields_match_ap(self):
        for role, case17, case1e in (("ptp", 0x9b4093, 0x9b3fc4), ("ptmp_sta", 0x9b5552, 0x9b547f)):
            with self.subTest(role=role):
                code = rows(f"airmax-target-{role}-cases-20261006.json", case17)
                pairs = []
                for row in code.values():
                    if row["mnemonic"] == "j":
                        break
                    pairs.append((row["mnemonic"], row["operands"]))
                for pair in (("l8ui", "a9, a3, 9"), ("s8i", "a9, a5, 12"),
                             ("s16i", "a9, a5, 14"), ("s16i", "a9, a5, 16"),
                             ("s16i", "a9, a5, 18"), ("s32i.n", "a14, a5, 20")):
                    self.assertIn(pair, pairs)
                code = rows(f"airmax-target-{role}-cases-20261006.json", case1e)
                for index in range(5):
                    load, store = code[case1e + 6 * index], code[case1e + 6 * index + 3]
                    reg = load["operands"].split(",")[0]
                    self.assertEqual((load["mnemonic"], load["operands"]), ("l8ui", f"{reg}, a3, {9 + index}"))
                    self.assertEqual((store["mnemonic"], store["operands"]), ("s8i", f"{reg}, a5, {12 + index}"))


if __name__ == "__main__":
    unittest.main()
