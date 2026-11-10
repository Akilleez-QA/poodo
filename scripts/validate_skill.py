#!/usr/bin/env python3
"""Validate POODO package structure; never claims behavioral correctness."""

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/continuity-and-ledger.md",
    "references/contradiction-protocol.md",
    "references/epistemic-integrity.md",
    "references/evaluation.md",
    "references/method-selection.md",
    "references/mega-observe.md",
    "assets/mega-observe-charter.yaml",
    "evals/mega-observe.yaml",
    "references/output-patterns.md",
    "evals/manifest.yaml",
    "evals/protocol.md",
    "evals/rubric.md",
    "evals/test_check_capsule.py",
    "evals/test_validate_skill.py",
    "evals/fixtures/valid-capsule.yaml",
    "evals/fixtures/invalid-resurrection.yaml",
    "evals/fixtures/invalid-truncated-evidence.yaml",
    "scripts/check_capsule.py",
)


def frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md has no YAML frontmatter")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("SKILL.md frontmatter is not a mapping")
    return value


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        try:
            meta = frontmatter(skill_path.read_text(encoding="utf-8"))
            if meta.get("name") != "poodo":
                errors.append("frontmatter name must be poodo")
            metadata = meta.get("metadata")
            if not isinstance(metadata, dict) or str(metadata.get("version")) != "3.1":
                errors.append("frontmatter metadata.version must be 3.1")
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))

    config_path = ROOT / "agents" / "openai.yaml"
    if config_path.is_file():
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            interface = config.get("interface", {})
            policy = config.get("policy", {})
            short = interface.get("short_description", "")
            if not isinstance(short, str) or not 25 <= len(short) <= 64:
                errors.append("openai.yaml short_description must be 25-64 characters")
            prompt = interface.get("default_prompt", "")
            if not isinstance(prompt, str) or "$poodo" not in prompt:
                errors.append("openai.yaml default_prompt must mention $poodo")
            if policy.get("allow_implicit_invocation") is not False:
                errors.append("POODO must remain explicit-only")
        except (AttributeError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"invalid agents/openai.yaml: {exc}")

    markdown = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
    for path in markdown:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except ValueError as exc:
            errors.append(f"unreadable {path.relative_to(ROOT)}: {exc}")
            continue
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", text):
            if not (path.parent / target).resolve().is_file():
                errors.append(f"broken reference in {path.relative_to(ROOT)}: {target}")
        if re.search(r"<(?:TODO|TBD)>|\bTODO\b", text):
            errors.append(f"unfinished placeholder in {path.relative_to(ROOT)}")

    continuity = ROOT / "references" / "continuity-and-ledger.md"
    if continuity.is_file():
        try:
            body = continuity.read_text(encoding="utf-8")
        except ValueError:
            body = ""
        for literal in ("POODO_CONTINUATION/3.0", "POODO_CONTINUATION_V3_0", "END_POODO_CONTINUATION_V3_0"):
            if not re.search(rf"(?<![\w/]){re.escape(literal)}(?![\w/])", body):
                errors.append(f"continuation schema missing {literal}")

    for relative in ("scripts/validate_skill.py", "scripts/check_capsule.py"):
        path = ROOT / relative
        if path.is_file() and not (path.stat().st_mode & 0o111):
            errors.append(f"script is not executable: {relative}")

    if errors:
        print("POODO structural checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("POODO structural checks passed; behavioral correctness remains untested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
