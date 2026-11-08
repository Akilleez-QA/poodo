#!/usr/bin/env python3

import importlib.util
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

TEST = """import unittest


class DemoTests(unittest.TestCase):
    def test_one(self):
        pass

    def test_two(self):
        pass
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
        (directory / ".github/workflows/checks.yml").write_text("steps:\n      - run: python demo.py\n", encoding="utf-8")
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

    def test_minimal_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.check(self.make_repo(Path(directory)))
            self.assertEqual(result.returncode, 0, result.stdout)

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
