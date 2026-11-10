#!/usr/bin/env python3

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_skill", ROOT / "scripts" / "validate_skill.py")
validate_skill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_skill)

PASS = "POODO structural checks passed; behavioral correctness remains untested."
FAIL = "POODO structural checks failed:"
PACKAGE = ("SKILL.md", "agents", "references", "assets", "evals", "scripts")


class PackageValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fresh()

    def fresh(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        for name in PACKAGE:
            source = ROOT / name
            if source.is_dir():
                shutil.copytree(source, self.root / name, ignore=ignore)
            else:
                shutil.copy2(source, self.root / name)
        for script in ("validate_skill.py", "check_capsule.py"):
            path = self.root / "scripts" / script
            path.chmod(path.stat().st_mode | 0o755)

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "validate_skill.py")],
            check=False, capture_output=True, text=True,
        )

    def assert_fails(self, *messages: str) -> subprocess.CompletedProcess[str]:
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(FAIL, result.stdout)
        self.assertNotIn(PASS, result.stdout)
        for message in messages:
            self.assertIn(message, result.stdout)
        return result

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def write_yaml(self, relative: str, data: object) -> None:
        (self.root / relative).write_text(yaml.safe_dump(data), encoding="utf-8")

    def openai_config(self) -> dict:
        return yaml.safe_load((self.root / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    def test_copied_package_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), PASS)

    def test_ug_28_each_missing_required_file_is_named(self) -> None:
        for relative in validate_skill.REQUIRED:
            with self.subTest(relative=relative):
                path = self.root / relative
                backup = path.read_bytes()
                mode = path.stat().st_mode
                path.unlink()
                try:
                    result = self.assert_fails(f"missing required file: {relative}")
                    self.assertEqual(result.stdout.count("missing required file:"), 1)
                finally:
                    path.write_bytes(backup)
                    path.chmod(mode)
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_ug_28_required_file_replaced_by_directory(self) -> None:
        path = self.root / "evals" / "rubric.md"
        path.unlink()
        path.mkdir()
        self.assert_fails("missing required file: evals/rubric.md")

    def test_ug_28_every_missing_file_is_reported(self) -> None:
        (self.root / "evals" / "protocol.md").unlink()
        (self.root / "assets" / "mega-observe-charter.yaml").unlink()
        self.assert_fails(
            "missing required file: evals/protocol.md",
            "missing required file: assets/mega-observe-charter.yaml",
        )

    def test_ug_29_missing_front_matter(self) -> None:
        path = self.root / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        body = text.split("\n---\n", 1)[1]
        for content in (body, "# POODO\n", "---\nname: poodo\n"):
            with self.subTest(content=content[:20]):
                path.write_text(content, encoding="utf-8")
                self.assert_fails("SKILL.md has no YAML frontmatter")

    def test_ug_29_front_matter_not_a_mapping(self) -> None:
        for front in ("- poodo\n- 3.1", "poodo", "null"):
            with self.subTest(front=front):
                (self.root / "SKILL.md").write_text(f"---\n{front}\n---\n# POODO\n", encoding="utf-8")
                self.assert_fails("SKILL.md frontmatter is not a mapping")

    def test_ug_29_invalid_front_matter_yaml(self) -> None:
        (self.root / "SKILL.md").write_text("---\nname: [poodo\n---\n# POODO\n", encoding="utf-8")
        result = self.assert_fails()
        self.assertRegex(result.stdout, r"\n- .*(flow sequence|expected)")

    def test_ug_29_wrong_name(self) -> None:
        for value in ("pooda", "Poodo", '""', "null", "[poodo]"):
            with self.subTest(value=value):
                self.fresh()
                self.edit("SKILL.md", "\nname: poodo\n", f"\nname: {value}\n")
                self.assert_fails("frontmatter name must be poodo")
        self.fresh()
        self.edit("SKILL.md", "\nname: poodo\n", "\n")
        self.assert_fails("frontmatter name must be poodo")

    def test_ug_29_wrong_metadata_version(self) -> None:
        for value in ('"3.0"', '"3.10"', "3.2", '""', "null", "[3.1]"):
            with self.subTest(value=value):
                self.fresh()
                self.edit("SKILL.md", '  version: "3.1"\n', f"  version: {value}\n")
                self.assert_fails("frontmatter metadata.version must be 3.1")
        self.fresh()
        self.edit("SKILL.md", 'metadata:\n  version: "3.1"\n', "")
        self.assert_fails("frontmatter metadata.version must be 3.1")
        for value in ("3.1", '"3.1"', "[3.1]", "null"):
            with self.subTest(metadata=value):
                self.fresh()
                self.edit("SKILL.md", 'metadata:\n  version: "3.1"\n', f"metadata: {value}\n")
                self.assert_fails("frontmatter metadata.version must be 3.1")

    def test_ug_30_implicit_invocation_allowed(self) -> None:
        for value in (True, None, "false", 0):
            with self.subTest(value=value):
                config = self.openai_config()
                config["policy"]["allow_implicit_invocation"] = value
                self.write_yaml("agents/openai.yaml", config)
                self.assert_fails("POODO must remain explicit-only")
        config = self.openai_config()
        del config["policy"]
        self.write_yaml("agents/openai.yaml", config)
        self.assert_fails("POODO must remain explicit-only")

    def test_ug_30_default_prompt_missing_poodo(self) -> None:
        for value in ("Use POODO to analyze this.", "", None, ["$poodo"], 7):
            with self.subTest(value=value):
                config = self.openai_config()
                config["interface"]["default_prompt"] = value
                self.write_yaml("agents/openai.yaml", config)
                self.assert_fails("openai.yaml default_prompt must mention $poodo")
        config = self.openai_config()
        del config["interface"]["default_prompt"]
        self.write_yaml("agents/openai.yaml", config)
        self.assert_fails("openai.yaml default_prompt must mention $poodo")

    def test_ug_30_short_description_out_of_range(self) -> None:
        for value in ("x" * 24, "x" * 65, "", None, 42, ["x" * 30]):
            with self.subTest(value=value):
                config = self.openai_config()
                config["interface"]["short_description"] = value
                self.write_yaml("agents/openai.yaml", config)
                self.assert_fails("openai.yaml short_description must be 25-64 characters")
        for value in ("x" * 25, "x" * 64):
            with self.subTest(value=value):
                config = self.openai_config()
                config["interface"]["short_description"] = value
                self.write_yaml("agents/openai.yaml", config)
                result = self.run_validator()
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_ug_30_malformed_openai_yaml(self) -> None:
        for content in ("- a\n- b\n", "", "interface: [1]\npolicy: {}\n", "interface: {}\npolicy: [1]\n"):
            with self.subTest(content=content):
                (self.root / "agents" / "openai.yaml").write_text(content, encoding="utf-8")
                self.assert_fails()
        (self.root / "agents" / "openai.yaml").write_text("interface: [\n", encoding="utf-8")
        self.assert_fails("invalid agents/openai.yaml")
        (self.root / "agents" / "openai.yaml").write_bytes(b"interface:\n  display_name: \xff\n")
        self.assert_fails("invalid agents/openai.yaml")

    def test_ug_31_broken_reference_link(self) -> None:
        with open(self.root / "SKILL.md", "a", encoding="utf-8") as handle:
            handle.write("\nSee [gone](references/gone.md).\n")
        self.assert_fails("broken reference in SKILL.md: references/gone.md")
        self.fresh()
        with open(self.root / "references" / "observe.md", "a", encoding="utf-8") as handle:
            handle.write("\nSee [missing](missing-phase.md).\n")
        self.assert_fails("broken reference in references/observe.md: missing-phase.md")

    def test_ug_31_link_resolves_relative_to_the_linking_file(self) -> None:
        with open(self.root / "references" / "observe.md", "a", encoding="utf-8") as handle:
            handle.write("\nSee [orient](references/orient.md).\n")
        self.assert_fails("broken reference in references/observe.md: references/orient.md")
        self.fresh()
        with open(self.root / "references" / "observe.md", "a", encoding="utf-8") as handle:
            handle.write("\nSee [orient](orient.md) and [skill](../SKILL.md).\n")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_ug_31_placeholders(self) -> None:
        for target in ("SKILL.md", "references/decide.md"):
            for marker in ("TODO", "<TODO>", "<TBD>", "TODO: finish"):
                with self.subTest(target=target, marker=marker):
                    self.fresh()
                    with open(self.root / target, "a", encoding="utf-8") as handle:
                        handle.write(f"\n{marker}\n")
                    self.assert_fails(f"unfinished placeholder in {target}")

    def test_ug_31_unreadable_markdown_is_reported(self) -> None:
        with open(self.root / "references" / "decide.md", "ab") as handle:
            handle.write(b"\n\xff\xfe\n")
        self.assert_fails("unreadable references/decide.md")

    def test_ug_32_missing_schema_literal(self) -> None:
        path = self.root / "references" / "continuity-and-ledger.md"
        original = path.read_text(encoding="utf-8")
        removals = (
            ("POODO_CONTINUATION/3.0", r"POODO_CONTINUATION/3\.0"),
            ("POODO_CONTINUATION_V3_0", r"(?<!END_)POODO_CONTINUATION_V3_0"),
            ("END_POODO_CONTINUATION_V3_0", r"END_POODO_CONTINUATION_V3_0"),
        )
        for literal, pattern in removals:
            with self.subTest(literal=literal):
                text = re.sub(pattern, "REMOVED", original)
                self.assertNotEqual(text, original)
                path.write_text(text, encoding="utf-8")
                try:
                    result = self.assert_fails(f"continuation schema missing {literal}")
                    missing = re.findall(r"^- continuation schema missing (\S+)$", result.stdout, re.MULTILINE)
                    self.assertEqual(missing, [literal])
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_ug_33_non_executable_script(self) -> None:
        for script in ("check_capsule.py", "validate_skill.py"):
            for mode in (0o644, 0o600, 0o444):
                with self.subTest(script=script, mode=oct(mode)):
                    path = self.root / "scripts" / script
                    path.chmod(mode)
                    try:
                        self.assert_fails(f"script is not executable: scripts/{script}")
                    finally:
                        path.chmod(0o755)
        for mode in (0o744, 0o654, 0o645):
            with self.subTest(mode=oct(mode)):
                path = self.root / "scripts" / "check_capsule.py"
                path.chmod(mode)
                result = self.run_validator()
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_ug_33_real_scripts_are_executable(self) -> None:
        if os.name == "nt":
            self.skipTest("POSIX permission bits required")
        for script in ("check_capsule.py", "validate_skill.py"):
            with self.subTest(script=script):
                self.assertTrue((ROOT / "scripts" / script).stat().st_mode & 0o111)

    def test_f_4_failures_are_all_reported_together(self) -> None:
        (self.root / "evals" / "rubric.md").unlink()
        self.edit("SKILL.md", "\nname: poodo\n", "\nname: other\n")
        config = self.openai_config()
        config["policy"]["allow_implicit_invocation"] = True
        self.write_yaml("agents/openai.yaml", config)
        (self.root / "scripts" / "check_capsule.py").chmod(0o644)
        result = self.assert_fails(
            "missing required file: evals/rubric.md",
            "frontmatter name must be poodo",
            "POODO must remain explicit-only",
            "script is not executable: scripts/check_capsule.py",
        )
        self.assertEqual(sum(1 for line in result.stdout.splitlines() if line.startswith("- ")), 4)

    def test_f_4_missing_skill_and_config_do_not_crash(self) -> None:
        (self.root / "SKILL.md").unlink()
        (self.root / "agents" / "openai.yaml").unlink()
        (self.root / "references" / "continuity-and-ledger.md").unlink()
        self.assert_fails(
            "missing required file: SKILL.md",
            "missing required file: agents/openai.yaml",
            "missing required file: references/continuity-and-ledger.md",
        )


if __name__ == "__main__":
    unittest.main()
