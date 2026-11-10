#!/usr/bin/env python3

import copy
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_capsule.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CapsuleLinterTests(unittest.TestCase):
    def run_fixture(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / name)],
            check=False,
            capture_output=True,
            text=True,
        )

    def run_payload(self, payload: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capsule.yaml"
            path.write_text(payload, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False, capture_output=True, text=True,
            )

    def valid_data(self) -> dict:
        return yaml.safe_load((FIXTURES / "valid-capsule.yaml").read_text())

    def assert_invalid(self, data: dict, message: str) -> None:
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(message, result.stderr)

    def test_malformed_reference_collections(self) -> None:
        for field, key in (
            ("claims", "supports"), ("evidence_bundles", "supports_claims"),
            ("evidence_bundles", "artifacts"), ("orientations", "depends_on"),
            ("decisions", "depends_on"), ("predictions", "outcome_evidence"),
        ):
            for value in (None, "D-demo-retest", {}, [{}], [[]], [42]):
                with self.subTest(field=field, key=key, value=value):
                    data = self.valid_data()
                    data[field][0][key] = value
                    self.assert_invalid(data, f"{field}[0].{key}")

    def test_malformed_scalar_references(self) -> None:
        for key in ("oracle", "artifact"):
            for value in (None, [], {}, ["AC-demo-visible"], 42):
                with self.subTest(key=key, value=value):
                    data = self.valid_data()
                    data["predictions"][0][key] = value
                    self.assert_invalid(data, f"predictions[0].{key}")
        for value in ([], {}, ["D-demo-retest"]):
            data = self.valid_data()
            data["current_head"] = value
            self.assert_invalid(data, "current_head")

    def test_unhashable_enum_values(self) -> None:
        paths = (
            ("schema",), ("delivery_state",), ("outcome_state",),
            ("claims", 0, "state"), ("claims", 0, "status"),
            ("evidence_bundles", 0, "completeness"),
            ("predictions", 0, "status"),
            ("predictions", 0, "status_history", 0),
        )
        for path in paths:
            for value in ([], {}):
                with self.subTest(path=path, value=value):
                    data = self.valid_data()
                    target = data
                    for key in path[:-1]:
                        target = target[key]
                    target[path[-1]] = value
                    self.assert_invalid(data, "invalid" if path[0] != "schema" else "schema")

    def test_malformed_contradiction_references(self) -> None:
        base = self.valid_data()
        base["contradictions"] = [{
            "id": "C-demo-one", "target": "D-demo-retest", "evidence": [],
            "scope": "demo", "effect": "reopen", "affected_ids": [],
            "disposition": "unresolved", "repaired_by": [],
        }]
        for key in ("target", "evidence", "affected_ids", "repaired_by", "disposition"):
            for value in (None, {}, [[1]]):
                with self.subTest(key=key, value=value):
                    data = copy.deepcopy(base)
                    data["contradictions"][0][key] = value
                    self.assert_invalid(data, f"contradictions[0].{key}")

    def test_rejects_impossible_dates_and_offsets(self) -> None:
        for value in ("2026-99-99T99:99:99Z", "2026-02-29T12:00:00Z",
                      "2026-10-01T24:00:00Z", "2026-10-01T12:00:00+01:99"):
            with self.subTest(value=value):
                data = self.valid_data()
                data["generated_at"] = value
                self.assert_invalid(data, "generated_at")
        result = self.run_payload("generated_at: 2026-99-99T99:99:99Z\n")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_accepts_real_rfc3339_dates(self) -> None:
        for value in ("2024-02-29T12:00:00Z", "2026-10-01T12:00:00.123-04:00"):
            data = self.valid_data()
            data["generated_at"] = value
            result = self.run_payload(yaml.safe_dump(data))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_nonstring_mapping_keys(self) -> None:
        for payload in ("? [a, b]\n: value\n", "42: value\n"):
            result = self.run_payload(payload)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("mapping keys must be strings", result.stderr)

    def oversize(self) -> dict:
        data = self.valid_data()
        data["constraints"] = "x" * 8000
        return data

    def test_oversize_capsule_rejected_without_overflow(self) -> None:
        self.assert_invalid(self.oversize(), "exceeds ceiling")

    def test_declared_overflow_allows_oversize_capsule(self) -> None:
        data = self.oversize()
        data["capsule_overflow"] = "Raw logs archived; locator in rehydration."
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_overflow_does_not_waive_ceiling(self) -> None:
        data = self.oversize()
        data["capsule_overflow"] = "  "
        self.assert_invalid(data, "exceeds ceiling")

    def test_valid_capsule(self) -> None:
        result = self.run_fixture("valid-capsule.yaml")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("epistemic and behavioral correctness remain untested", result.stdout)

    def test_rejects_failed_prediction_resurrection(self) -> None:
        result = self.run_fixture("invalid-resurrection.yaml")
        self.assertEqual(result.returncode, 1)
        self.assertIn("terminal prediction was resurrected", result.stderr)

    def test_rejects_truncated_evidence(self) -> None:
        result = self.run_fixture("invalid-truncated-evidence.yaml")
        self.assertEqual(result.returncode, 1)
        self.assertIn("partial or truncated evidence", result.stderr)

    def run_path(self, path: Path, *options: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path), *options],
            check=False, capture_output=True, text=True,
        )

    def assert_load_error(self, result: subprocess.CompletedProcess[str], message: str) -> None:
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("could not load capsule", result.stderr)
        self.assertIn(message, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_ug_22_duplicate_keys_are_load_errors_at_any_depth(self) -> None:
        text = (FIXTURES / "valid-capsule.yaml").read_text(encoding="utf-8")
        cases = {
            "root": text + "objective: A second objective.\n",
            "nested mapping": text.replace(
                "  allowed: Read-only analysis.\n",
                "  allowed: Read-only analysis.\n  allowed: Everything.\n",
            ),
            "list record": text.replace(
                "    state: observed\n",
                "    state: observed\n    state: inferred\n",
            ),
        }
        for label, payload in cases.items():
            with self.subTest(label=label):
                self.assertNotEqual(payload, text)
                self.assert_load_error(self.run_payload(payload), "duplicate key")

    def test_ug_23_non_mapping_root_is_rejected(self) -> None:
        for payload in ("- a\n- b\n", "just a string\n", "42\n", "null\n", ""):
            with self.subTest(payload=payload):
                result = self.run_payload(payload)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("root: must be a mapping", result.stderr)

    def test_ug_23_missing_root_field_is_named(self) -> None:
        for field in sorted(self.valid_data()):
            with self.subTest(field=field):
                data = self.valid_data()
                del data[field]
                result = self.run_payload(yaml.safe_dump(data))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertRegex(result.stderr, rf"root: missing required fields: [^\n]*\b{field}\b")

    def test_ug_23_unknown_root_field_is_named(self) -> None:
        data = self.valid_data()
        data["notes"] = "Not part of the schema."
        self.assert_invalid(data, "root: unknown fields: notes")

    def test_ug_23_empty_required_values_are_rejected(self) -> None:
        cases = {
            "objective": ("", "   ", None, [], {}),
            "next_step": ("", "  ", None, [], {}),
            "highest_justified_claim": ("", None, []),
            "required_runtime_observation": ("", None, {}),
            "who_controls_next_test": (" ", None),
            "constraints": ("", [], {}, None, 0),
            "user_directives": ("", [], {}, None, 0),
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    data = self.valid_data()
                    data[field] = value
                    self.assert_invalid(data, f"{field}: must")

    def test_ug_23_authority_and_rehydration_must_be_mappings(self) -> None:
        for field in ("authority", "rehydration"):
            for value in ("text", ["a"], None, 1):
                with self.subTest(field=field, value=value):
                    data = self.valid_data()
                    data[field] = value
                    self.assert_invalid(data, f"{field}: must be a mapping")

    def test_ug_24_capsule_id_must_match_pattern(self) -> None:
        for value in ("demo-0002", "PC-", "PC--x", "pc-demo", "PC-demo 2", 7, None, ["PC-demo"]):
            with self.subTest(value=value):
                data = self.valid_data()
                data["capsule_id"] = value
                self.assert_invalid(data, "capsule_id: must match")

    def test_ug_24_revision_must_be_positive_integer(self) -> None:
        for value in (0, -1, "2", 2.0, True, None):
            with self.subTest(value=value):
                data = self.valid_data()
                data["revision"] = value
                self.assert_invalid(data, "revision: must be a positive integer")

    def test_ug_24_parent_lineage_rules(self) -> None:
        data = self.valid_data()
        data["revision"] = 1
        self.assert_invalid(data, "parent_capsule: revision 1 must not declare a parent")
        data = self.valid_data()
        data["parent_capsule"] = None
        self.assert_invalid(data, "parent_capsule: revisions after 1 require a parent")
        for value in ("demo-0001", "PC-", 5, ["PC-demo-0001"]):
            with self.subTest(value=value):
                data = self.valid_data()
                data["parent_capsule"] = value
                self.assert_invalid(data, "parent_capsule: must be null or a valid PC-* identifier")
        data = self.valid_data()
        data["revision"] = 1
        data["parent_capsule"] = None
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_25_duplicate_record_id_across_collections(self) -> None:
        data = self.valid_data()
        data["alternatives"][0]["id"] = "D-demo-retest"
        data["decisions"][0]["depends_on"] = ["CL-demo-structural"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capsule.yaml"
            path.write_text(yaml.safe_dump(data), encoding="utf-8")
            for seed in ("0", "1", "2", "3"):
                with self.subTest(seed=seed):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), str(path)],
                        check=False, capture_output=True, text=True,
                        env={**os.environ, "PYTHONHASHSEED": seed},
                    )
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("decisions[0].id: duplicate ID D-demo-retest", result.stderr)
                    self.assertNotIn("alternatives[0].id: duplicate", result.stderr)
        data = self.valid_data()
        data["artifacts"].append(dict(data["artifacts"][0]))
        self.assert_invalid(data, "artifacts[1].id: duplicate ID A-demo-candidate")

    def test_ug_25_missing_or_invalid_record_id(self) -> None:
        for value in (None, "", "demo", "TOOLONG-x", 3, ["A-x"]):
            with self.subTest(value=value):
                data = self.valid_data()
                data["artifacts"][0]["id"] = value
                self.assert_invalid(data, "artifacts[0].id: missing or invalid stable ID")
        data = self.valid_data()
        del data["acceptance"][0]["id"]
        self.assert_invalid(data, "acceptance[0].id: missing or invalid stable ID")

    def test_ug_25_unresolved_references_are_named(self) -> None:
        cases = (
            (("claims", 0, "supports"), ["D-demo-missing"], "claims[0].supports: unresolved ID D-demo-missing"),
            (("evidence_bundles", 0, "supports_claims"), ["CL-demo-missing"], "evidence_bundles[0].supports_claims: unresolved claim CL-demo-missing"),
            (("evidence_bundles", 0, "artifacts"), ["A-demo-missing"], "evidence_bundles[0].artifacts: unresolved artifact A-demo-missing"),
            (("orientations", 0, "depends_on"), ["CL-demo-missing"], "orientations[0].depends_on: unresolved ID CL-demo-missing"),
            (("decisions", 0, "depends_on"), ["H-demo-missing"], "decisions[0].depends_on: unresolved ID H-demo-missing"),
            (("predictions", 0, "oracle"), "AC-demo-missing", "predictions[0].oracle: unresolved ID AC-demo-missing"),
            (("predictions", 0, "artifact"), "A-demo-missing", "predictions[0].artifact: unresolved ID A-demo-missing"),
            (("predictions", 0, "outcome_evidence"), ["EB-demo-missing"], "predictions[0].outcome_evidence: unresolved ID EB-demo-missing"),
            (("current_head",), "D-demo-missing", "current_head: unresolved ID D-demo-missing"),
        )
        for path, value, message in cases:
            with self.subTest(path=path):
                data = self.valid_data()
                target = data
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                self.assert_invalid(data, message)
        base = self.valid_data()
        base["contradictions"] = [{
            "id": "C-demo-one", "target": "D-demo-retest", "evidence": ["CL-demo-structural"],
            "scope": "demo", "effect": "reopen", "affected_ids": ["D-demo-retest"],
            "disposition": "unresolved", "repaired_by": [],
        }]
        result = self.run_payload(yaml.safe_dump(base))
        self.assertEqual(result.returncode, 0, result.stderr)
        for key, value in (("target", "D-demo-missing"), ("evidence", ["EB-demo-missing"]),
                           ("affected_ids", ["OR-demo-missing"]), ("repaired_by", ["D-demo-missing"])):
            with self.subTest(key=key):
                data = copy.deepcopy(base)
                data["contradictions"][0][key] = value
                self.assert_invalid(data, f"contradictions[0].{key}: unresolved ID")

    def test_ug_25_wrong_kind_references_are_rejected(self) -> None:
        data = self.valid_data()
        data["evidence_bundles"][0]["supports_claims"] = ["A-demo-candidate"]
        self.assert_invalid(data, "evidence_bundles[0].supports_claims: unresolved claim A-demo-candidate")
        data = self.valid_data()
        data["evidence_bundles"][0]["artifacts"] = ["CL-demo-structural"]
        self.assert_invalid(data, "evidence_bundles[0].artifacts: unresolved artifact CL-demo-structural")

    def test_ug_26_active_record_depending_on_retracted_record(self) -> None:
        for status in ("invalidated", "superseded"):
            for record_status in (None, "active"):
                with self.subTest(status=status, record_status=record_status):
                    data = self.valid_data()
                    data["claims"][0]["status"] = status
                    if record_status:
                        data["orientations"][0]["status"] = record_status
                    self.assert_invalid(data, "orientations[0]: active record depends on invalidated CL-demo-structural")
        data = self.valid_data()
        data["alternatives"][0]["status"] = "invalidated"
        self.assert_invalid(data, "decisions[0]: active record depends on invalidated H-demo-ineffective")
        data = self.valid_data()
        data["outcomes"] = [{"id": "OU-demo-one", "depends_on": ["H-demo-ineffective"]}]
        data["alternatives"][0]["status"] = "superseded"
        self.assert_invalid(data, "outcomes[0]: active record depends on invalidated H-demo-ineffective")

    def test_ug_26_inactive_record_may_depend_on_retracted_record(self) -> None:
        for status in ("stale", "superseded", "invalidated"):
            with self.subTest(status=status):
                data = self.valid_data()
                data["claims"][0]["status"] = "invalidated"
                data["orientations"][0]["status"] = status
                data["decisions"][0]["status"] = status
                result = self.run_payload(yaml.safe_dump(data))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_26_current_head_must_be_a_head_kind(self) -> None:
        for head in ("CL-demo-structural", "EB-demo-validator", "H-demo-ineffective", "A-demo-candidate", "AC-demo-visible"):
            with self.subTest(head=head):
                data = self.valid_data()
                data["current_head"] = head
                self.assert_invalid(data, "current_head: must reference an orientation, decision, prediction, or contradiction")
        for head in (None, "OR-demo-uncertain", "D-demo-retest", "PR-demo-visible"):
            with self.subTest(head=head):
                data = self.valid_data()
                data["current_head"] = head
                result = self.run_payload(yaml.safe_dump(data))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_27_claim_provenance_fields_required(self) -> None:
        for key in ("source_type", "locator", "observed_at", "freshness", "evidence_family", "rehydration_status", "limits"):
            with self.subTest(key=key):
                data = self.valid_data()
                del data["claims"][0][key]
                self.assert_invalid(data, f"claims[0].{key}: required")

    def test_ug_27_claim_text_required(self) -> None:
        for text in ("", "   ", None, []):
            with self.subTest(text=text):
                data = self.valid_data()
                data["claims"][0]["text"] = text
                self.assert_invalid(data, "claims[0]: non-empty text or claim required")
        data = self.valid_data()
        del data["claims"][0]["text"]
        self.assert_invalid(data, "claims[0]: non-empty text or claim required")
        data["claims"][0]["claim"] = "Structural checks passed."
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_27_contradiction_fields_required(self) -> None:
        base = self.valid_data()
        base["contradictions"] = [{
            "id": "C-demo-one", "target": "D-demo-retest", "evidence": [],
            "scope": "demo", "effect": "reopen", "affected_ids": [],
            "disposition": "unresolved", "repaired_by": [],
        }]
        result = self.run_payload(yaml.safe_dump(base))
        self.assertEqual(result.returncode, 0, result.stderr)
        for key in ("target", "evidence", "scope", "effect", "affected_ids", "disposition", "repaired_by"):
            with self.subTest(key=key):
                data = copy.deepcopy(base)
                del data["contradictions"][0][key]
                self.assert_invalid(data, f"contradictions[0].{key}: required")

    def test_ug_27_final_status_history_entry_must_equal_status(self) -> None:
        data = self.valid_data()
        data["predictions"][0]["status"] = "passed"
        self.assert_invalid(data, "predictions[0].status_history: final entry must equal status")
        data = self.valid_data()
        data["predictions"][0]["status_history"] = ["pending", "failed"]
        self.assert_invalid(data, "predictions[0].status_history: final entry must equal status")
        for history in ([], None, "pending"):
            with self.subTest(history=history):
                data = self.valid_data()
                data["predictions"][0]["status_history"] = history
                self.assert_invalid(data, "predictions[0].status_history: non-empty list required")
        data = self.valid_data()
        data["predictions"][0]["status"] = "passed"
        data["predictions"][0]["status_history"] = ["pending", "passed"]
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_34_hard_token_ceiling_option(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capsule.yaml"
            raw = yaml.safe_dump(self.valid_data())
            path.write_text(raw, encoding="utf-8")
            tokens = (len(raw) + 3) // 4
            result = self.run_path(path, "--hard-token-ceiling", str(tokens - 1))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(f"approximately {tokens} tokens exceeds ceiling {tokens - 1}", result.stderr)
            result = self.run_path(path, "--hard-token-ceiling", str(tokens))
            self.assertEqual(result.returncode, 0, result.stderr)
            data = self.valid_data()
            data["capsule_overflow"] = "Raw logs archived; locator in rehydration."
            path.write_text(yaml.safe_dump(data), encoding="utf-8")
            result = self.run_path(path, "--hard-token-ceiling", "10")
            self.assertEqual(result.returncode, 0, result.stderr)
            big = self.oversize()
            path.write_text(yaml.safe_dump(big), encoding="utf-8")
            result = self.run_path(path, "--hard-token-ceiling", "100000")
            self.assertEqual(result.returncode, 0, result.stderr)
            for value in ("ten", "1.5", ""):
                with self.subTest(value=value):
                    result = self.run_path(path, "--hard-token-ceiling", value)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("--hard-token-ceiling", result.stderr)

    def test_ug_35_out_of_set_string_values(self) -> None:
        cases = (
            (("schema",), "POODO_CONTINUATION/2.0", "schema: expected"),
            (("delivery_state",), "shipped", "delivery_state: invalid state"),
            (("outcome_state",), "succeeded", "outcome_state: invalid state"),
            (("claims", 0, "state"), "certain", "claims[0].state: invalid claim state"),
            (("claims", 0, "status"), "retracted", "claims[0].status: invalid record status"),
            (("evidence_bundles", 0, "completeness"), "mostly", "evidence_bundles[0].completeness: invalid value"),
            (("predictions", 0, "status"), "done", "predictions[0].status: invalid prediction status"),
            (("predictions", 0, "status_history", 0), "queued", "predictions[0].status_history: invalid state 'queued'"),
        )
        for path, value, message in cases:
            with self.subTest(path=path, value=value):
                data = self.valid_data()
                target = data
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                self.assert_invalid(data, message)
        for value in ("Active", " active", "PENDING"):
            with self.subTest(value=value):
                data = self.valid_data()
                data["claims"][0]["status"] = value
                self.assert_invalid(data, "claims[0].status: invalid record status")
        base = self.valid_data()
        base["contradictions"] = [{
            "id": "C-demo-one", "target": "D-demo-retest", "evidence": [],
            "scope": "demo", "effect": "reopen", "affected_ids": [],
            "disposition": "ignored", "repaired_by": [],
        }]
        self.assert_invalid(base, "contradictions[0].disposition: invalid value")
        data = self.valid_data()
        data["schema"] = "POODA_CONTINUATION/2.1"
        result = self.run_payload(yaml.safe_dump(data))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ug_36_malformed_outcome_depends_on(self) -> None:
        base = self.valid_data()
        base["outcomes"] = [{"id": "OU-demo-one", "depends_on": ["PR-demo-visible"]}]
        result = self.run_payload(yaml.safe_dump(base))
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in (None, "PR-demo-visible", {}, [{}], [[]], [42], ["not an id"]):
            with self.subTest(value=value):
                data = copy.deepcopy(base)
                data["outcomes"][0]["depends_on"] = value
                self.assert_invalid(data, "outcomes[0].depends_on")

    def test_ug_37_unreadable_path_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "absent.yaml"
            self.assert_load_error(self.run_path(missing), "absent.yaml")
            self.assert_load_error(self.run_path(Path(directory)), "could not load capsule")

    def test_ug_37_permission_denied_exits_2(self) -> None:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root ignores file permission bits")
        if os.name == "nt":
            self.skipTest("POSIX permission bits required")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capsule.yaml"
            path.write_text(yaml.safe_dump(self.valid_data()), encoding="utf-8")
            path.chmod(0)
            try:
                self.assert_load_error(self.run_path(path), "Permission denied")
            finally:
                path.chmod(0o600)

    def test_ug_37_non_utf8_file_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capsule.yaml"
            raw = (FIXTURES / "valid-capsule.yaml").read_text(encoding="utf-8")
            path.write_bytes(raw.replace("Read-only analysis.", "Read-only é.").encode("latin-1"))
            self.assert_load_error(self.run_path(path), "codec can't decode")
            path.write_bytes(b"\xff\xfe\x00schema")
            self.assert_load_error(self.run_path(path), "could not load capsule")


if __name__ == "__main__":
    unittest.main()
