#!/usr/bin/env python3

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "gen_release_docs.py"
GIT = ["git", "-c", "user.name=Example", "-c", "user.email=example@example.invalid", "-c", "commit.gpgsign=false"]

MIXED_TESTS = """import unittest


class Mixed(unittest.TestCase):
    def test_pass(self):
        pass

    @unittest.skip("example")
    def test_skip(self):
        pass

    @unittest.expectedFailure
    def test_expected_failure(self):
        self.fail()

    @unittest.expectedFailure
    def test_unexpected_success(self):
        pass

    def test_failure(self):
        self.fail()

    def test_error(self):
        raise RuntimeError
"""


def load():
    spec = importlib.util.spec_from_file_location("poodo_gen_release_docs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUBTEST_TESTS = """import unittest


class Sub(unittest.TestCase):
    def test_pass(self):
        pass

    def test_two_failing_subtests(self):
        for i in range(2):
            with self.subTest(i=i):
                self.fail()
"""

SKIPPED_TESTS = """import unittest


class Skipped(unittest.TestCase):
    @unittest.skip("example")
    def test_one(self):
        pass

    @unittest.skip("example")
    def test_two(self):
        pass
"""

COLOURED_OUTPUT = (
    "test_fail (test_c.C.test_fail) ... \x1b[31mFAIL\x1b[0m\n"
    "test_pass (test_c.C.test_pass) ... \x1b[32mok\x1b[0m\n"
    "test_skip (test_c.C.test_skip) ... \x1b[33mskipped\x1b[0m 'example'\n"
    "\n"
    "----------------------------------------------------------------------\n"
    "Ran 3 tests in 0.001s\n"
    "\n"
    "\x1b[1;31mFAILED\x1b[0m (\x1b[1;31mfailures=1\x1b[0m, \x1b[33mskipped=1\x1b[0m)\n"
)


def result(tests=None, returncode=0, summary="OK", **outcomes):
    counts = {key: 0 for key in ("failures", "errors", "skipped", "expected failures", "unexpected successes")}
    counts.update({key.replace("_", " "): value for key, value in outcomes.items()})
    passed = max(0, (tests or 0) - sum(counts.values()))
    return {"returncode": returncode, "tests": tests, "passed": passed, "statuses": 0 if tests is None else 1,
            "outcomes": counts, "failures": "", "summary": summary, "digest": "0" * 64}


def passing(suite_id):
    return result(tests=4) if suite_id in {"S2", "S5"} else result()


TRACE = {"requirements": 1, "full": 1, "partial": 0, "none": 0, "gaps": 0, "tests_traced": 1, "tests_supporting": 0, "links": 1, "errors": 0}


class GenReleaseDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = Path(tempfile.mkdtemp())
        archive = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=ROOT, check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", str(cls.template)], input=archive, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.template)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        shutil.copytree(self.template, self.root)
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "baseline"]):
            subprocess.run([*GIT, *args], cwd=self.root, check=True, capture_output=True)
        self.head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()
        self.module = load()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def generate(self, *flags, suites=None, trace=None):
        suites = suites or {}
        names = [suite_id for suite_id, _, _ in self.module.SUITES]
        queue = [suites.get(suite_id, passing(suite_id)) for suite_id in names]
        before = set(self.outputs())
        stderr = io.StringIO()
        with mock.patch.object(self.module, "ROOT", self.root), \
                mock.patch.object(self.module, "run_suite", side_effect=queue), \
                mock.patch.object(self.module, "trace_counts", return_value=dict(trace or TRACE)), \
                mock.patch.object(self.module, "gh_json", return_value=None), \
                mock.patch.object(self.module, "python_version", return_value="3.0.0"), \
                mock.patch.object(self.module, "pyyaml_version", return_value="0.0"), \
                mock.patch.object(sys, "argv", ["gen_release_docs.py", "--python", sys.executable, *flags]), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = self.module.main()
        written = [path for path in self.outputs() if path not in before]
        return code, [path.read_text(encoding="utf-8") for path in written]

    def outputs(self):
        reports = sorted((self.root / "docs/verification/reports").glob("STR-*.md"))
        releases = sorted((self.root / "docs/releases").glob("VDD-*.md"))
        return reports + releases

    def report(self, **kwargs):
        code, texts = self.generate(**kwargs)
        self.assertEqual(len(texts), 2)
        return code, texts[0]

    def test_clean_tree_is_baselined_at_head(self):
        code, texts = self.generate()
        self.assertEqual(code, 0)
        self.assertEqual(len(texts), 2)
        for text in texts:
            self.assertIn("| Status | Baselined (generated) |", text)
            self.assertIn(f"| Baseline commit | `{self.head}` |", text)
        self.assertIn("all structural suites passed", texts[0])

    def test_dirty_tree_without_flag_is_refused(self):
        (self.root / "SKILL.md").write_text("changed\n", encoding="utf-8")
        code, texts = self.generate()
        self.assertEqual(code, 2)
        self.assertEqual(texts, [])

    def test_untracked_file_counts_as_dirty(self):
        (self.root / "tools" / "test_extra.py").write_text("", encoding="utf-8")
        code, texts = self.generate()
        self.assertEqual(code, 2)
        self.assertEqual(texts, [])

    def test_dirty_tree_report_does_not_claim_head_as_baseline(self):
        skill = self.root / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        code, texts = self.generate("--allow-dirty")
        self.assertEqual(len(texts), 2)
        for text in texts:
            self.assertNotIn("Baselined", text)
            self.assertNotIn(f"| Baseline commit | `{self.head}` |", text)
            self.assertNotIn(f"| Commit | `{self.head}` |", text)
            self.assertNotIn("inspected at the baseline commit", text)
            self.assertIn("not a baseline", text)
            self.assertIn("\nSKILL.md\n", text)
        self.assertIn("not a baseline result", texts[0])
        self.assertFalse((self.root / f"docs/verification/reports/STR-main-{self.head[:7]}.md").exists())

    def test_skipped_test_does_not_report_all_passed(self):
        code, text = self.report(suites={"S5": result(tests=3, summary="OK (skipped=1)", skipped=1)})
        self.assertNotEqual(code, 0)
        self.assertNotIn("all structural suites passed", text)
        self.assertIn("1 skipped", text)
        self.assertNotIn("No failing", text)
        self.assertIn("| 7 / 6 |", text)

    def test_suite_that_runs_no_tests_does_not_report_all_passed(self):
        code, text = self.report(suites={"S2": result(tests=0, summary="OK")})
        self.assertNotEqual(code, 0)
        self.assertNotIn("all structural suites passed", text)
        self.assertIn("ran no tests", text)

    def test_failed_trace_gate_does_not_report_all_passed(self):
        code, text = self.report(trace={**TRACE, "errors": 2})
        self.assertNotEqual(code, 0)
        self.assertNotIn("all structural suites passed", text)
        self.assertIn("2 trace error(s)", text)
        self.assertNotIn("No failing", text)

    def test_suite_result_counts_every_non_pass_outcome(self):
        case = self.tmp / "case"
        case.mkdir()
        (case / "test_mixed.py").write_text(MIXED_TESTS, encoding="utf-8")
        args = ["-m", "unittest", "discover", "-s", str(case), "-p", "test_*.py", "-v"]
        with mock.patch.object(self.module, "ROOT", self.tmp):
            parsed = self.module.run_suite(sys.executable, args)
        self.assertNotEqual(parsed["returncode"], 0)
        self.assertEqual(parsed["tests"], 6)
        self.assertEqual(parsed["outcomes"], {"failures": 1, "errors": 1, "skipped": 1, "expected failures": 1, "unexpected successes": 1})
        self.assertEqual(self.module.tests_passed(parsed), 1)
        problems = self.module.suite_problems("S5", parsed)
        for expected in ("1 failures", "1 errors", "1 skipped", "1 expected failures", "1 unexpected successes"):
            self.assertIn(expected, problems)
        skipped_only = self.module.parse_suite(0, "Ran 2 tests in 0.001s\n\nOK (skipped=2)\n")
        self.assertEqual(self.module.suite_problems("S2", skipped_only), ["2 skipped", "2 of 2 tests not passed"])
        self.assertEqual(self.module.tests_passed(skipped_only), 0)

    def run_case(self, source, environ=None):
        case = self.tmp / "case"
        case.mkdir()
        (case / "test_case.py").write_text(source, encoding="utf-8")
        args = ["-m", "unittest", "discover", "-s", str(case), "-p", "test_*.py", "-v"]
        with mock.patch.object(self.module, "ROOT", self.tmp), mock.patch.dict("os.environ", environ or {}):
            return self.module.run_suite(sys.executable, args)

    def test_failing_subtests_do_not_hide_a_passing_method(self):
        parsed = self.run_case(SUBTEST_TESTS)
        self.assertEqual(parsed["tests"], 2)
        self.assertEqual(parsed["outcomes"]["failures"], 2)
        self.assertEqual(self.module.tests_passed(parsed), 1)
        problems = self.module.suite_problems("S5", parsed)
        self.assertIn("2 failures", problems)
        self.assertIn("1 of 2 tests not passed", problems)

    def test_subtest_failures_are_reported_in_metrics(self):
        code, text = self.report(suites={"S5": self.run_case(SUBTEST_TESTS)})
        self.assertNotEqual(code, 0)
        self.assertNotIn("all structural suites passed", text)
        self.assertIn("| 6 / 5 |", text)
        self.assertIn("1 of 2 tests not passed", text)

    def test_coloured_output_is_parsed(self):
        parsed = self.module.parse_suite(1, COLOURED_OUTPUT)
        self.assertEqual(parsed["tests"], 3)
        self.assertEqual(parsed["outcomes"]["failures"], 1)
        self.assertEqual(parsed["outcomes"]["skipped"], 1)
        self.assertEqual(self.module.tests_passed(parsed), 1)
        self.assertNotIn("\x1b", parsed["summary"])
        coloured_skip = self.module.parse_suite(0, "Ran 2 tests in 0.001s\n\n\x1b[1;32mOK\x1b[0m (\x1b[33mskipped=2\x1b[0m)\n")
        self.assertIn("2 skipped", self.module.suite_problems("S2", coloured_skip))

    def test_suites_run_without_colour_when_colour_is_forced(self):
        parsed = self.run_case(SKIPPED_TESTS, {"PYTHON_COLORS": "1", "FORCE_COLOR": "1"})
        self.assertEqual(parsed["returncode"], 0)
        self.assertEqual(parsed["outcomes"]["skipped"], 2)
        self.assertEqual(self.module.suite_problems("S2", parsed), ["2 skipped", "2 of 2 tests not passed"])
        env = self.module.suite_env()
        self.assertEqual((env["PYTHON_COLORS"], env["NO_COLOR"]), ("0", "1"))
        self.assertNotIn("FORCE_COLOR", env)

    def test_missing_status_line_is_a_problem(self):
        parsed = self.module.parse_suite(0, "test_a (m.C.test_a) ... ok\n\nRan 1 test in 0.001s\n")
        self.assertIn("no unittest status line", self.module.suite_problems("S5", parsed))


if __name__ == "__main__":
    unittest.main()
