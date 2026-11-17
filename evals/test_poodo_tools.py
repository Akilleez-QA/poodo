#!/usr/bin/env python3

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "poodo_tools.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
TOOL_FIXTURES = FIXTURES / "tools"
SPEC = importlib.util.spec_from_file_location("poodo_tools", SCRIPT)
poodo_tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(poodo_tools)

TOOL_NAMES = {"check_capsule", "precommit_hash", "orient_paths_check", "research_gate_check", "terminal_claim_check"}
DISCLAIMER = "Structural check only: a pass is not a truth or quality judgement. Structural conformance is not runtime validation."


def fixture(name: str) -> dict:
    return json.loads((TOOL_FIXTURES / name).read_text(encoding="utf-8"))


def call(name: str, arguments: dict) -> dict:
    result, is_error = poodo_tools.run_tool(name, arguments)
    if is_error:
        raise AssertionError(result["errors"])
    return result


class McpServerTests(unittest.TestCase):
    def exchange(self, *messages: object, raw: bytes = b"") -> list[dict]:
        payload = b"".join(
            (message if isinstance(message, bytes) else json.dumps(message).encode("utf-8")) + b"\n" for message in messages
        ) + raw
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "serve"], input=payload, capture_output=True, check=False, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertNotIn(b"Traceback", result.stderr)
        return [json.loads(line) for line in result.stdout.decode("utf-8").splitlines() if line.strip()]

    def test_initialize_list_and_call(self) -> None:
        responses = self.exchange(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                "name": "check_capsule", "arguments": {"capsule": (FIXTURES / "valid-capsule.yaml").read_text()}}},
            {"jsonrpc": "2.0", "id": 4, "method": "ping"},
        )
        self.assertEqual([response["id"] for response in responses], [1, 2, 3, 4])
        init = responses[0]["result"]
        self.assertEqual(init["protocolVersion"], "2025-06-18")
        self.assertEqual(init["serverInfo"]["name"], "poodo-tools")
        self.assertEqual(init["capabilities"], {"tools": {"listChanged": False}})
        tools = responses[1]["result"]["tools"]
        self.assertEqual({tool["name"] for tool in tools}, TOOL_NAMES)
        for tool in tools:
            self.assertEqual(tool["inputSchema"]["type"], "object")
            self.assertFalse(tool["inputSchema"]["additionalProperties"])
            self.assertTrue(tool["annotations"]["readOnlyHint"])
            self.assertFalse(tool["annotations"]["openWorldHint"])
        called = responses[2]["result"]
        self.assertFalse(called["isError"])
        self.assertEqual(called["structuredContent"]["status"], "pass")
        self.assertEqual(json.loads(called["content"][0]["text"]), called["structuredContent"])
        self.assertEqual(responses[3]["result"], {})

    def test_unsupported_protocol_version_gets_latest(self) -> None:
        response = self.exchange({"jsonrpc": "2.0", "id": "a", "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})[0]
        self.assertEqual(response["result"]["protocolVersion"], poodo_tools.PROTOCOL_VERSIONS[0])

    def test_json_rpc_errors(self) -> None:
        responses = self.exchange(
            b"{not json",
            [{"jsonrpc": "2.0", "id": 1, "method": "ping"}],
            {"jsonrpc": "1.0", "id": 2, "method": "ping"},
            {"jsonrpc": "2.0", "id": 3, "method": "resources/list"},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "rm_rf", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": []},
            {"jsonrpc": "2.0", "id": None, "method": "ping"},
            {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 9}},
        )
        codes = [response["error"]["code"] for response in responses]
        self.assertEqual(codes, [-32700, -32600, -32600, -32601, -32602, -32602, -32600])
        self.assertEqual(responses[3]["id"], 3)
        self.assertEqual(responses[4]["id"], 4)

    def test_invalid_arguments_are_tool_errors_not_crashes(self) -> None:
        responses = self.exchange(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "check_capsule", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "orient_paths_check", "arguments": {"paths": "x", "extra": 1}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_capsule", "arguments": {"capsule": "a: [unclosed"}}},
            {"jsonrpc": "2.0", "id": 4, "method": "ping"},
        )
        for response in responses[:3]:
            result = response["result"]
            self.assertTrue(result["isError"])
            self.assertEqual(result["structuredContent"]["status"], "error")
            self.assertTrue(result["structuredContent"]["errors"])
        self.assertIn("unknown fields: extra", responses[1]["result"]["structuredContent"]["errors"][0])
        self.assertEqual(responses[3]["result"], {})

    def test_oversize_line_is_rejected_and_server_continues(self) -> None:
        big = b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":"' + b"a" * (poodo_tools.MAX_LINE_BYTES + 10) + b'"}}'
        responses = self.exchange(big, {"jsonrpc": "2.0", "id": 2, "method": "ping"})
        self.assertEqual(responses[0]["error"]["code"], -32600)
        self.assertIn("exceeds", responses[0]["error"]["message"])
        self.assertEqual(responses[1], {"jsonrpc": "2.0", "id": 2, "result": {}})


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False, timeout=60)

    def test_cli_matches_tool_results(self) -> None:
        cases = (
            ("orient-paths-check", "orient_paths_check", "orient-20-paths.json"),
            ("research-gate-check", "research_gate_check", "research-record.json"),
            ("terminal-claim-check", "terminal_claim_check", "terminal-claim.json"),
        )
        for command, tool, name in cases:
            with self.subTest(command=command):
                result = self.run_cli("--json", command, str(TOOL_FIXTURES / name))
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(json.loads(result.stdout), call(tool, fixture(name)))
        result = self.run_cli("--json", "check-capsule", str(FIXTURES / "valid-capsule.yaml"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout), call("check_capsule", {"capsule": (FIXTURES / "valid-capsule.yaml").read_text()}))

    def test_cli_exit_codes(self) -> None:
        self.assertEqual(self.run_cli("check-capsule", str(FIXTURES / "invalid-resurrection.yaml")).returncode, 1)
        with tempfile.TemporaryDirectory() as directory:
            missing = self.run_cli("orient-paths-check", str(Path(directory) / "absent.json"))
            self.assertEqual(missing.returncode, 2)
            self.assertIn("could not load input", missing.stdout)
            self.assertNotIn("Traceback", missing.stderr)
        text = self.run_cli("research-gate-check", str(TOOL_FIXTURES / "research-record.json")).stdout
        self.assertIn("research_gate_check: pass", text)
        self.assertIn(DISCLAIMER, text)


class ResultEnvelopeTests(unittest.TestCase):
    def test_every_result_states_its_scope(self) -> None:
        results = [
            call("check_capsule", {"capsule": (FIXTURES / "valid-capsule.yaml").read_text()}),
            call("orient_paths_check", fixture("orient-20-paths.json")),
            call("research_gate_check", fixture("research-record.json")),
            call("terminal_claim_check", fixture("terminal-claim.json")),
            call("orient_paths_check", {"paths": []}),
        ]
        for result in results:
            with self.subTest(tool=result["tool"], status=result["status"]):
                self.assertEqual(result["scope"], "structural")
                self.assertEqual(result["disclaimer"], DISCLAIMER)
                self.assertTrue(result["not_checked"])
                self.assertIn(result["status"], {"pass", "fail"})
        digest = call("precommit_hash", {"document": "x"})
        self.assertEqual(digest["scope"], "identity")
        self.assertIn("does not show that the precommit was written before observation", digest["disclaimer"])

    def test_input_bounds(self) -> None:
        big = "a" * (poodo_tools.MAX_TEXT_CHARS + 1)
        nested: object = "x"
        for _ in range(poodo_tools.MAX_DEPTH + 2):
            nested = [nested]
        cases = (
            ("check_capsule", {"capsule": big}, "exceeds"),
            ("check_capsule", {"capsule": "a: 1", "hard_token_ceiling": 0}, "hard_token_ceiling"),
            ("precommit_hash", {"document": big}, "exceeds"),
            ("precommit_hash", {"record": nested}, "nesting"),
            ("orient_paths_check", {"paths": ["p"] * (poodo_tools.MAX_ITEMS + 1)}, "exceeds"),
            ("orient_paths_check", {"paths": [{"name": "n" * (poodo_tools.MAX_NAME_CHARS + 1), "mechanism": "m"}]}, "exceeds"),
            ("research_gate_check", {**fixture("research-record.json"), "queries": ["q"] * (poodo_tools.MAX_ITEMS + 1)}, "exceeds"),
            ("terminal_claim_check", {**fixture("terminal-claim.json"), "summary": big}, "exceeds"),
            ("terminal_claim_check", [], "must be an object"),
        )
        for name, arguments, message in cases:
            with self.subTest(tool=name, message=message):
                result, is_error = poodo_tools.run_tool(name, arguments)
                self.assertTrue(is_error)
                self.assertEqual(result["status"], "error")
                self.assertIn(message, result["errors"][0])


class CheckCapsuleToolTests(unittest.TestCase):
    def test_matches_capsule_checker(self) -> None:
        for name in ("valid-capsule.yaml", "invalid-resurrection.yaml", "invalid-truncated-evidence.yaml"):
            with self.subTest(fixture=name):
                raw = (FIXTURES / name).read_text()
                data = poodo_tools.yaml.load(raw, Loader=poodo_tools.check_capsule.UniqueKeyLoader)
                expected = poodo_tools.check_capsule.validate(data, raw, 1800)
                result = call("check_capsule", {"capsule": raw})
                self.assertEqual(result["errors"], expected)
                self.assertEqual(result["status"], "fail" if expected else "pass")

    def test_delimiters(self) -> None:
        raw = (FIXTURES / "valid-capsule.yaml").read_text()
        wrapped = call("check_capsule", {"capsule": f"POODO_CONTINUATION_V3_0\n{raw}END_POODO_CONTINUATION_V3_0\n"})
        self.assertEqual(wrapped["status"], "pass")
        self.assertTrue(wrapped["delimiters_stripped"])
        result, is_error = poodo_tools.run_tool("check_capsule", {"capsule": f"POODO_CONTINUATION_V3_0\n{raw}"})
        self.assertTrue(is_error)
        self.assertIn("only one", result["errors"][0])

    def test_duplicate_key_is_input_error(self) -> None:
        result, is_error = poodo_tools.run_tool("check_capsule", {"capsule": "schema: a\nschema: b\n"})
        self.assertTrue(is_error)
        self.assertIn("duplicate key", result["errors"][0])


class PrecommitHashTests(unittest.TestCase):
    def test_known_vectors(self) -> None:
        self.assertEqual(call("precommit_hash", {"document": ""})["sha256"],
                         "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(call("precommit_hash", {"document": "abc"})["sha256"],
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_document_bytes_are_not_normalized(self) -> None:
        unix = call("precommit_hash", {"document": "a\nb\n"})["sha256"]
        windows = call("precommit_hash", {"document": "a\r\nb\r\n"})["sha256"]
        trailing = call("precommit_hash", {"document": "a\nb"})["sha256"]
        self.assertEqual(len({unix, windows, trailing}), 3)
        self.assertEqual(call("precommit_hash", {"document": "é"})["sha256"], hashlib.sha256("é".encode()).hexdigest())

    def test_file_matches_sha256sum_receipt_format(self) -> None:
        path = TOOL_FIXTURES / "PRECOMMIT.md"
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "precommit-hash", str(path), "--name", "PRECOMMIT.md"],
            capture_output=True, text=True, check=False,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["sha256"], expected)
        self.assertEqual(data["receipt_line"], f"{expected}  PRECOMMIT.md")
        self.assertEqual(data, {**call("precommit_hash", {"document": path.read_text(encoding="utf-8")}), "method": data["method"]})

    def test_receipt_comparison(self) -> None:
        document = (TOOL_FIXTURES / "PRECOMMIT.md").read_text(encoding="utf-8")
        digest = hashlib.sha256(document.encode()).hexdigest()
        other = "0" * 64
        amended = call("precommit_hash", {"document": document, "receipt": f"{digest}  PRECOMMIT.md\n2026-11-16T00:00:00Z\n{other}  PRECOMMIT.md\n"})
        self.assertEqual(amended["status"], "pass")
        self.assertEqual(amended["receipt"], {"digest_lines": [1, 3], "matched_lines": [1], "matches_first": True, "matches_last": False})
        mismatch = call("precommit_hash", {"document": document + " ", "receipt": f"{digest}  PRECOMMIT.md\n"})
        self.assertEqual(mismatch["status"], "fail")
        self.assertIn("no recorded digest matches", mismatch["errors"][0])
        empty = call("precommit_hash", {"document": document, "receipt": "nothing here\n"})
        self.assertEqual(empty["status"], "fail")

    def test_record_uses_canonical_json(self) -> None:
        left = call("precommit_hash", {"record": {"b": 1, "a": ["é", None]}})
        right = call("precommit_hash", {"record": {"a": ["é", None], "b": 1}})
        canonical = json.dumps({"a": ["é", None], "b": 1}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        self.assertEqual(canonical, '{"a":["\\u00e9",null],"b":1}')
        self.assertEqual(left["sha256"], right["sha256"])
        self.assertEqual(left["sha256"], hashlib.sha256(canonical.encode("ascii")).hexdigest())

    def test_exactly_one_input(self) -> None:
        for arguments in ({}, {"document": "a", "record": {}}, {"document": "a", "name": "x\ny"}):
            with self.subTest(arguments=arguments):
                self.assertTrue(poodo_tools.run_tool("precommit_hash", arguments)[1])


class OrientPathsTests(unittest.TestCase):
    def paths(self) -> list[dict]:
        return copy.deepcopy(fixture("orient-20-paths.json")["paths"])

    def test_twenty_distinct_paths_pass(self) -> None:
        result = call("orient_paths_check", {"paths": self.paths()})
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual((result["count"], result["distinct_count"]), (20, 20))
        self.assertEqual(result["near_duplicates"], [])

    def test_count_must_be_exactly_twenty(self) -> None:
        for paths in (self.paths()[:19], [*self.paths(), {"name": "Extra path", "mechanism": "Something new entirely"}]):
            with self.subTest(count=len(paths)):
                result = call("orient_paths_check", {"paths": paths})
                self.assertEqual(result["status"], "fail")
                self.assertIn(f"{len(paths)} entries given; exactly 20", result["errors"][-1])

    def test_duplicates_fail(self) -> None:
        cases = (
            ({"name": "  ROLLBACK!  ", "mechanism": "Revert the change and observe"}, "same name after normalization"),
            ({"name": "Correction minimal", "mechanism": "Change just the comparator"}, "same name words in another order"),
            ({"name": "Undo deploy", "mechanism": "restore the previous deploy and watch whether the error rate returns to baseline."}, "same mechanism"),
        )
        for replacement, reason in cases:
            with self.subTest(reason=reason):
                paths = self.paths()
                paths[19] = replacement
                result = call("orient_paths_check", {"paths": paths})
                self.assertEqual(result["status"], "fail")
                self.assertEqual(result["distinct_count"], 19)
                self.assertTrue(any(reason in error for error in result["errors"]), result["errors"])

    def test_near_duplicates_are_flagged_not_failed(self) -> None:
        paths = self.paths()
        paths[19] = {"name": "Escalate to the domain authority team", "mechanism": "Ask the vendor's support engineers to review the trace"}
        result = call("orient_paths_check", {"paths": paths})
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["near_duplicates"], [{"paths": [13, 20], "field": "name", "jaccard": 0.75}])
        self.assertIn("possible near-duplicate", result["warnings"][0])

    def test_entries_need_name_and_mechanism(self) -> None:
        paths = self.paths()
        paths[0] = "Bare name only"
        paths[1] = {"name": "", "mechanism": "x"}
        paths[2] = {"name": "Odd", "mechanism": "y", "score": 3}
        paths[3] = 7
        result = call("orient_paths_check", {"paths": paths})
        joined = "\n".join(result["errors"])
        self.assertIn("paths[1].mechanism: state the distinguishing mechanism", joined)
        self.assertIn("paths[2].name: must be a non-empty string", joined)
        self.assertIn("paths[3]: unknown fields: score", joined)
        self.assertIn("paths[4]: must be a string or an object", joined)


class ResearchGateTests(unittest.TestCase):
    def test_complete_record_passes(self) -> None:
        result = call("research_gate_check", fixture("research-record.json"))
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["warnings"], [])
        self.assertEqual((result["source_count"], result["distinct_hosts"], result["disconfirming_query_count"]), (2, 2, 1))

    def test_required_parts(self) -> None:
        base = fixture("research-record.json")
        cases = (
            ({"queries": []}, "queries: must name at least one query"),
            ({"sources": base["sources"][:1]}, "a single source cannot satisfy the gate"),
            ({"non_entailments": []}, "non_entailments: must name at least one entry"),
            ({"conflicts": "none"}, "conflicts: must be a list"),
            ({"gate": "maybe"}, "gate: must be satisfied or unsatisfied"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                result = call("research_gate_check", {**base, **change})
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any(message in error for error in result["errors"]), result["errors"])
        for key in ("queries", "sources", "conflicts", "non_entailments"):
            with self.subTest(missing=key):
                arguments = {k: v for k, v in base.items() if k != key}
                result, is_error = poodo_tools.run_tool("research_gate_check", arguments)
                self.assertTrue(is_error)
                self.assertIn(key, result["errors"][0])

    def test_source_url_and_dates(self) -> None:
        base = fixture("research-record.json")
        cases = (
            ({"url": "ftp://example.org/x", "retrieved": "2026-11-16"}, "url: must be an http or https URL"),
            ({"url": "https://", "retrieved": "2026-11-16"}, "url: must be an http or https URL"),
            ({"url": "https://a.example/x"}, "retrieved: must be an ISO 8601 date"),
            ({"url": "https://a.example/x", "retrieved": "2026-02-30"}, "retrieved: must be an ISO 8601 date"),
            ({"url": "https://a.example/x", "retrieved": "yesterday"}, "retrieved: must be an ISO 8601 date"),
            ({"url": "https://a.example/x", "retrieved": "2026-11-16", "published": "16/11/2026"}, "published: must be an ISO 8601 date"),
            ({"url": base["sources"][0]["url"] + "/", "retrieved": "2026-11-16"}, "url: repeats sources[1]"),
        )
        for source, message in cases:
            with self.subTest(message=message, source=source):
                result = call("research_gate_check", {**base, "sources": [base["sources"][0], source]})
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any(message in error for error in result["errors"]), result["errors"])

    def test_warnings_do_not_fail(self) -> None:
        base = fixture("research-record.json")
        record = {
            **base,
            "queries": ["only confirming query"],
            "sources": [{"url": "https://one.example/a", "retrieved": "2026-11-16T10:00:00Z", "evidence_family": "EF-x"},
                        {"url": "https://one.example/b", "retrieved": "2026-11-16", "evidence_family": "EF-x"}],
            "conflicts": [],
        }
        record.pop("implications")
        result = call("research_gate_check", record)
        self.assertEqual(result["status"], "pass", result["errors"])
        joined = "\n".join(result["warnings"])
        for message in ("none is marked disconfirming", "every source is on one host", "same evidence_family",
                        "no published or updated date", "conflicts: empty", "implications: none recorded"):
            self.assertIn(message, joined)

    def test_satisfied_gate_with_errors_is_called_out(self) -> None:
        base = fixture("research-record.json")
        result = call("research_gate_check", {**base, "sources": base["sources"][:1]})
        self.assertIn("gate: declared satisfied but the record is structurally incomplete", result["errors"])


class TerminalClaimTests(unittest.TestCase):
    def test_well_formed_claim_passes(self) -> None:
        result = call("terminal_claim_check", fixture("terminal-claim.json"))
        self.assertEqual(result["status"], "pass", result["errors"])

    def test_fields_and_states(self) -> None:
        base = fixture("terminal-claim.json")
        cases = (
            ({"delivery_state": "shipped"}, "delivery_state: must be one of"),
            ({"outcome_state": "great"}, "outcome_state: must be one of"),
            ({"highest_justified_claim": "  "}, "highest_justified_claim: must be a non-empty string"),
            ({"who_controls_next_test": None}, "who_controls_next_test: must be a non-empty string"),
            ({"required_runtime_observation": "none"}, "'none' must cite the evidence IDs"),
            ({"who_controls_next_test": "none"}, "someone must control the next test"),
            ({"outcome_state": "passed"}, "'passed' needs an acceptance entry"),
            ({"acceptance": [{"id": "AC-x", "criterion": "c", "status": "passed"}]}, "must name its artifact and environment"),
            ({"acceptance": [{"id": "AC-x", "criterion": "c", "status": "done"}]}, "status: must be one of"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                result = call("terminal_claim_check", {**base, **change})
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any(message in error for error in result["errors"]), result["errors"])
        result, is_error = poodo_tools.run_tool("terminal_claim_check", {k: v for k, v in base.items() if k != "outcome_state"})
        self.assertTrue(is_error)
        self.assertIn("outcome_state", result["errors"][0])

    def test_none_with_evidence_ids_passes(self) -> None:
        claim = {**fixture("terminal-claim.json"), "required_runtime_observation": "none; closed by E-demo-run1", "who_controls_next_test": "none"}
        self.assertEqual(call("terminal_claim_check", claim)["status"], "pass")

    def test_unqualified_success_words(self) -> None:
        base = fixture("terminal-claim.json")
        for text in ("The import bug is fixed.", "Resolved the drift.", "Change validated in staging.", "A successful rollout."):
            with self.subTest(text=text):
                result = call("terminal_claim_check", {**base, "highest_justified_claim": text})
                self.assertEqual(result["status"], "fail")
                self.assertIn("without a passed intended-use criterion", result["errors"][0])
        summary = call("terminal_claim_check", {**base, "summary": "All fixed now."})
        self.assertEqual(summary["success_words"], [{"field": "summary", "word": "fixed"}])
        for text in ("Not yet validated on staging.", "The defect is not fixed.", "Unvalidated patch; tests pass.", "It isn't resolved."):
            with self.subTest(negated=text):
                self.assertEqual(call("terminal_claim_check", {**base, "highest_justified_claim": text})["status"], "pass")

    def test_success_words_allowed_after_passed_criterion(self) -> None:
        claim = {
            **fixture("terminal-claim.json"),
            "delivery_state": "deployed", "outcome_state": "passed",
            "highest_justified_claim": "Import fixed on the staging dataset.",
            "required_runtime_observation": "none; E-demo-nightly", "who_controls_next_test": "none",
            "acceptance": [{"id": "AC-demo-import", "criterion": "Nightly import row counts match", "status": "passed",
                            "artifact": "A-demo-build", "environment": "staging"}],
        }
        result = call("terminal_claim_check", claim)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["passed_criteria"], ["AC-demo-import"])
        self.assertEqual(call("terminal_claim_check", {**claim, "outcome_state": "observed"})["status"], "fail")


if __name__ == "__main__":
    unittest.main()
