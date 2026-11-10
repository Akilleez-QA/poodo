#!/usr/bin/env python3

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_trace.py"

SRS = """# Requirements

### REQ-PO-001 — Example

The checker shall reject bad input.

- Rationale: Example.
- Derivation: `scripts/check_capsule.py`
- Allocated to: SDD §4
- Verification: T
- Status: Baselined

### REQ-PO-002 — Behavior

The agent shall behave.

- Rationale: Example.
- Derivation: `evals/manifest.yaml`
- Allocated to: SDD §4
- Verification: T
- Status: Baselined
"""

VM = """# Matrix

## Requirement traceability

| Requirement | Method | Verified by | Coverage | Gap | Last result |
| --- | --- | --- | --- | --- | --- |
| REQ-PO-001 | T | `evals/test_demo.py::DemoTests.test_one`; `ci: python demo.py` | Full | — | STR-x |
| REQ-PO-002 | T | `evals/manifest.yaml#case-a` | None | UG-01 | No trial recorded |

## Untested requirement gaps

| Gap | Requirement | Missing evidence |
| --- | --- | --- |
| UG-01 | REQ-PO-002 | No recorded trial |

## Tests without a requirement

| Test | Classification |
| --- | --- |
| `evals/test_demo.py::DemoTests.test_two` | Supporting |
"""

SDD = """# Design

## 4. Components

| Component | Path | Responsibility | Requirements |
| --- | --- | --- | --- |
| Checker | `scripts/check_capsule.py` | Checks | REQ-PO-001 |
| Skill | `SKILL.md` | Instructions | REQ-PO-002 |
| Tooling | `tools/` | Trace | infrastructure |
"""

INHERITED_TEST = """import unittest
from unittest import TestCase as Case


class Mixin:
    def test_two(self):
        pass


class Base(unittest.IsolatedAsyncioTestCase, Case):
    pass


class DemoTests(Mixin, Base):
    async def test_one(self):
        pass
"""

WORKFLOW = """steps:
      - run: python demo.py
      - run: python -m unittest discover -s evals -p 'test_*.py' -v
"""

HELPER = """import unittest


class Base(unittest.TestCase):
    pass
"""

HELPER_TEST = """from helper import Base


class DemoTests(Base):
    def test_one(self):
        pass

    def test_two(self):
        pass
"""

DISABLED_TEST = """import unittest


class Mixin:
    def test_one(self):
        pass

    def test_two(self):
        pass


class DemoTests(Mixin, unittest.TestCase):
    test_two = None
"""

SKIPPED_TEST = """import unittest


class DemoTests(unittest.TestCase):
    def test_one(self):
        pass

    @unittest.skip("disabled")
    def test_two(self):
        pass
"""

TEST = """import unittest


class DemoTests(unittest.TestCase):
    def test_one(self):
        pass

    def test_two(self):
        pass
"""


DISCOVER = """import sys
import unittest


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


loader = unittest.TestLoader()
suite = loader.discover(sys.argv[1], pattern="test_*.py", top_level_dir=sys.argv[1])
if loader.errors:
    sys.exit("".join(loader.errors))
tests = [test for test in flatten(suite) if type(test).__module__.split(".")[0] != "unittest"]
print(f"discovered {len(tests)}")
"""


class TraceCheckTests(unittest.TestCase):
    def make_repo(self, directory: Path) -> Path:
        (directory / "docs/requirements").mkdir(parents=True)
        (directory / "docs/verification").mkdir(parents=True)
        (directory / "docs/architecture").mkdir(parents=True)
        (directory / "docs/data").mkdir(parents=True)
        (directory / ".github/workflows").mkdir(parents=True)
        (directory / "scripts").mkdir()
        (directory / "evals").mkdir()
        (directory / "docs/requirements/requirements.md").write_text(SRS, encoding="utf-8")
        (directory / "docs/verification/verification-matrix.md").write_text(VM, encoding="utf-8")
        (directory / "docs/architecture/architecture.md").write_text(SDD, encoding="utf-8")
        shutil.copy(ROOT / "scripts/check_capsule.py", directory / "scripts/check_capsule.py")
        (directory / "docs/data/data-dictionary.md").write_text(self.dictionary(), encoding="utf-8")
        (directory / "evals/manifest.yaml").write_text("cases:\n  - id: case-a\n", encoding="utf-8")
        (directory / "evals/test_demo.py").write_text(TEST, encoding="utf-8")
        (directory / ".github/workflows/checks.yml").write_text(WORKFLOW, encoding="utf-8")
        (directory / "README.md").write_text("[req](docs/requirements/requirements.md#req-po-001--example)\n", encoding="utf-8")
        return directory

    def dictionary(self) -> str:
        spec = importlib.util.spec_from_file_location("capsule_for_test", ROOT / "scripts/check_capsule.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        names = set(module.REQUIRED) | set(module.OPTIONAL)
        for enum in ("CLAIM_STATES", "RECORD_STATES", "PREDICTION_STATES", "COMPLETENESS", "DELIVERY_STATES", "OUTCOME_STATES"):
            names |= set(getattr(module, enum))
        return "# Data\n\n" + "\n".join(f"- `{name}`" for name in sorted(names)) + "\n"

    def check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            check=False, capture_output=True, text=True,
        )

    def edit(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_repository_passes(self) -> None:
        result = self.check(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("trace check passed", result.stdout)

    def discovered(self, root: Path) -> int:
        result = subprocess.run(
            [sys.executable, "-B", "-c", DISCOVER, str(root / "evals")],
            check=False, capture_output=True, text=True, cwd=root,
        )
        match = re.fullmatch(r"discovered (\d+)\n", result.stdout)
        if result.returncode != 0 or match is None:
            self.fail(f"unittest discovery failed (exit {result.returncode}):\n{result.stdout}{result.stderr}")
        return int(match.group(1))

    def test_minimal_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.check(self.make_repo(Path(directory)))
            self.assertEqual(result.returncode, 0, result.stdout)
        with self.subTest("inherited, imported and asynchronous TestCase bases"), tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/test_demo.py").write_text(INHERITED_TEST, encoding="utf-8")
            self.assertEqual(self.discovered(root), 2)
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("; 2 tests (1 traced, 1 supporting)", result.stdout)
        for imports, base in (
            ("from unittest.case import TestCase", "TestCase"),
            ("from unittest.case import TestCase as T", "T"),
            ("import unittest.case", "unittest.case.TestCase"),
            ("import unittest.case as uc", "uc.TestCase"),
            ("from unittest import case", "case.TestCase"),
            ("from unittest import case as c", "c.TestCase"),
            ("from unittest import TestCase as T", "T"),
            ("import unittest as ut", "ut.TestCase"),
            ("from unittest import *", "TestCase"),
            ("from unittest.case import *", "TestCase"),
            ("from unittest.async_case import *", "TestCase"),
            ("from unittest.async_case import *", "IsolatedAsyncioTestCase"),
            ("from unittest import IsolatedAsyncioTestCase", "IsolatedAsyncioTestCase"),
            ("import unittest", "unittest.IsolatedAsyncioTestCase"),
            ("from unittest.async_case import IsolatedAsyncioTestCase as A", "A"),
            ("import unittest.async_case", "unittest.async_case.IsolatedAsyncioTestCase"),
            ("from unittest import async_case", "async_case.IsolatedAsyncioTestCase"),
            ("try:\n    from unittest.case import TestCase\nexcept ImportError:\n    raise", "TestCase"),
        ):
            with self.subTest(imports), tempfile.TemporaryDirectory() as directory:
                root = self.make_repo(Path(directory))
                self.edit(root / "evals/test_demo.py", "import unittest\n", imports + "\n")
                self.edit(root / "evals/test_demo.py", "class DemoTests(unittest.TestCase):", f"class DemoTests({base}):")
                self.assertEqual(self.discovered(root), 2)
                result = self.check(root)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("; 2 tests (1 traced, 1 supporting)", result.stdout)
        with self.subTest("TestCase base imported from a helper module"):
            self.case_base_imported_from_helper_module_counts()

    def case_base_imported_from_helper_module_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/helper.py").write_text(HELPER, encoding="utf-8")
            (root / "evals/test_demo.py").write_text(HELPER_TEST, encoding="utf-8")
            self.assertEqual(self.discovered(root), 2)
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("; 2 tests (1 traced, 1 supporting)", result.stdout)

    def case_inherited_test_disabled_in_subclass_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/test_demo.py").write_text(DISABLED_TEST, encoding="utf-8")
            self.assertEqual(self.discovered(root), 1)
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("supporting-test row names test evals/test_demo.py::DemoTests.test_two that unittest does not run", result.stdout)
            self.assertIn("; 1 tests (1 traced, 1 supporting)", result.stdout)

    def case_skipped_test_is_not_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/test_demo.py").write_text(SKIPPED_TEST, encoding="utf-8")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("supporting-test row names test evals/test_demo.py::DemoTests.test_two that unittest skips", result.stdout)
            self.assertIn("; 1 tests (1 traced, 1 supporting)", result.stdout)

    def case_import_error_during_discovery_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/test_broken.py").write_text("import missing_module_for_trace_test\n", encoding="utf-8")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("DISCOVER: unittest discover -s evals -p test_*.py could not import module test_broken", result.stdout)
            self.assertIn("missing_module_for_trace_test", result.stdout)

    def case_tests_follow_ci_discover_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / ".github/workflows/checks.yml", "-p 'test_*.py'", "-p 'check_*.py'")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("REQ-PO-001 references test evals/test_demo.py::DemoTests.test_one that unittest does not run", result.stdout)
        with self.subTest("no discover command"), tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / ".github/workflows/checks.yml", "      - run: python -m unittest discover -s evals -p 'test_*.py' -v\n", "")
            result = self.check(root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("DISCOVER: CI runs no 'python -m unittest discover' command", result.stdout)

    def test_requirement_without_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/verification/verification-matrix.md",
                      "| REQ-PO-002 | T | `evals/manifest.yaml#case-a` | None | UG-01 | No trial recorded |\n", "")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REQ-PO-002 has no verification row", result.stdout)

    def test_missing_test_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/verification/verification-matrix.md", "test_one`;", "test_gone`;")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing test evals/test_demo.py::DemoTests.test_gone", result.stdout)
        with self.subTest("discovery failure is reported"), tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "evals/test_demo.py").write_text("import missing_module_for_trace_test\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, r"(?s)unittest discovery failed .*missing_module_for_trace_test"):
                self.discovered(root)
        for label, replacement in (
            ("no base class", "class DemoTests:"),
            ("non-TestCase base class", "class Base:\n    pass\n\n\nclass DemoTests(Base):"),
            ("same-named class outside unittest", "class TestCase:\n    pass\n\n\nclass DemoTests(TestCase):"),
            ("unittest attribute that is not TestCase", "class DemoTests(unittest.TestResult):"),
        ):
            with self.subTest(label), tempfile.TemporaryDirectory() as directory:
                root = self.make_repo(Path(directory))
                self.edit(root / "evals/test_demo.py", "class DemoTests(unittest.TestCase):", replacement)
                self.assertEqual(self.discovered(root), 0)
                result = self.check(root)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("REQ-PO-001 references test evals/test_demo.py::DemoTests.test_one that unittest does not run", result.stdout)
                self.assertIn("supporting-test row names test evals/test_demo.py::DemoTests.test_two that unittest does not run", result.stdout)
                self.assertIn("; 0 tests (0 traced,", result.stdout)
        with self.subTest("inherited test disabled in the subclass"):
            self.case_inherited_test_disabled_in_subclass_fails()
        with self.subTest("skipped test"):
            self.case_skipped_test_is_not_evidence()
        with self.subTest("import error during discovery"):
            self.case_import_error_during_discovery_fails()
        with self.subTest("CI discover commands"):
            self.case_tests_follow_ci_discover_commands()

    def test_gap_without_registration_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/verification/verification-matrix.md", "| None | UG-01 |", "| None | — |")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REQ-PO-002 is None without an untested-gap ID", result.stdout)

    def test_full_without_automated_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/verification/verification-matrix.md", "| None | UG-01 |", "| Full | — |")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REQ-PO-002 is Full without an automated test", result.stdout)

    def test_untraced_test_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/verification/verification-matrix.md",
                      "| `evals/test_demo.py::DemoTests.test_two` | Supporting |\n", "")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("test evals/test_demo.py::DemoTests.test_two traces to no requirement", result.stdout)

    def test_unallocated_requirement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / "docs/architecture/architecture.md", "| Instructions | REQ-PO-002 |", "| Instructions | infrastructure |")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("REQ-PO-002 is not allocated to any component", result.stdout)

    def test_dead_link_and_anchor_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            (root / "README.md").write_text("[a](missing.md) [b](docs/requirements/requirements.md#nope)\n", encoding="utf-8")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("dead link missing.md", result.stdout)
            self.assertIn("missing anchor #nope", result.stdout)

    def test_command_not_in_ci_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_repo(Path(directory))
            self.edit(root / ".github/workflows/checks.yml", "python demo.py", "python other.py")
            result = self.check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("command not run by CI: python demo.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
