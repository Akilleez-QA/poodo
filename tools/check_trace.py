#!/usr/bin/env python3
"""Check requirement, design, test and link traceability for the POODO docs."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SRS = Path("docs/requirements/requirements.md")
VM = Path("docs/verification/verification-matrix.md")
SDD = Path("docs/architecture/architecture.md")
DD = Path("docs/data/data-dictionary.md")
WORKFLOW = Path(".github/workflows/checks.yml")
CAPSULE_CHECKER = Path("scripts/check_capsule.py")
MANIFESTS = ("evals/manifest.yaml", "evals/mega-observe.yaml")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

REQ_HEADING = re.compile(r"^### (REQ-PO-\d{3}) — (.+)$", re.MULTILINE)
REQ_ID = re.compile(r"REQ-PO-\d{3}")
GAP_ID = re.compile(r"UG-\d{2}")
FIELDS = ("Rationale:", "Derivation:", "Allocated to:", "Verification:", "Status:")
STATUSES = {"Baselined", "Proposed", "Deleted"}
COVERAGE = {"Full", "Partial", "None"}
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def rows(text: str, first_cell: re.Pattern[str]) -> list[list[str]]:
    result = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and first_cell.fullmatch(cells[0]):
            result.append(cells)
    return result


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return ""
    rest = text[match.end():]
    end = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


def parse_requirements(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    requirements: dict[str, dict[str, str]] = {}
    matches = list(REQ_HEADING.finditer(text))
    for index, match in enumerate(matches):
        req_id = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        body = re.split(r"^## ", body, maxsplit=1, flags=re.MULTILINE)[0]
        if req_id in requirements:
            errors.append(f"SRS: duplicate requirement {req_id}")
            continue
        record: dict[str, str] = {"name": match.group(2).strip()}
        statement = body.strip().split("\n- ", 1)[0]
        if statement.count(" shall ") != 1:
            errors.append(f"SRS: {req_id} must have exactly one 'shall' statement")
        for field in FIELDS:
            found = re.search(rf"^- {re.escape(field)}\s*(.+)$", body, re.MULTILINE)
            if not found:
                errors.append(f"SRS: {req_id} missing field '{field}'")
            else:
                record[field.rstrip(":")] = found.group(1).strip()
        status = record.get("Status", "")
        if status and status.split()[0] not in STATUSES:
            errors.append(f"SRS: {req_id} has unknown status '{status}'")
        requirements[req_id] = record
    if not requirements:
        errors.append("SRS: no requirements found")
    return requirements, errors


DISCOVER = """import json
import sys
import unittest

start, pattern, top, output = sys.argv[1:5]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def skipped(test):
    method = getattr(test, test._testMethodName, None)
    return bool(getattr(type(test), "__unittest_skip__", False) or getattr(method, "__unittest_skip__", False))


loader = unittest.TestLoader()
suite = loader.discover(start, pattern=pattern, top_level_dir=top or None)
tests, failures = [], []
for test in flatten(suite):
    if type(test).__module__ == "unittest.loader":
        failures.append(test._testMethodName)
        continue
    module = sys.modules.get(type(test).__module__)
    path = getattr(module, "__file__", None) or type(test).__module__
    tests.append([path, type(test).__qualname__ + "." + test._testMethodName, skipped(test)])
with open(output, "w", encoding="utf-8") as handle:
    json.dump({"tests": tests, "failures": failures, "errors": loader.errors}, handle)
"""
DISCOVER_FLAGS = {
    "-s": "start", "--start-directory": "start",
    "-p": "pattern", "--pattern": "pattern",
    "-t": "top", "--top-level-directory": "top",
}


def discover_commands(commands: set[str]) -> list[tuple[str, str, str]]:
    result = []
    for command in sorted(commands):
        try:
            words = shlex.split(command)
        except ValueError:
            continue
        if "unittest" not in words or "discover" not in words:
            continue
        if words.index("discover") != words.index("unittest") + 1:
            continue
        args = words[words.index("discover") + 1:]
        options = {"start": ".", "pattern": "test*.py", "top": ""}
        positional = []
        index = 0
        while index < len(args):
            word = args[index]
            name, equals, value = word.partition("=")
            if equals and name in DISCOVER_FLAGS:
                options[DISCOVER_FLAGS[name]] = value
            elif word in DISCOVER_FLAGS and index + 1 < len(args):
                options[DISCOVER_FLAGS[word]] = args[index + 1]
                index += 1
            elif not word.startswith("-"):
                positional.append(word)
            index += 1
        for key, value in zip(("start", "pattern", "top"), positional):
            options[key] = value
        result.append((options["start"], options["pattern"], options["top"]))
    return result


def relative_path(root: Path, path: str) -> str:
    location = Path(path)
    if not location.is_absolute():
        return location.as_posix()
    try:
        return location.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return location.as_posix()


def collect_tests(root: Path, commands: set[str]) -> tuple[dict[str, set[str]], dict[str, set[str]], list[str]]:
    methods: dict[str, set[str]] = {}
    skipped: dict[str, set[str]] = {}
    errors: list[str] = []
    discoveries = discover_commands(commands)
    if not discoveries:
        errors.append("DISCOVER: CI runs no 'python -m unittest discover' command")
    for start, pattern, top in discoveries:
        where = f"unittest discover -s {start} -p {pattern}"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "tests.json"
            result = subprocess.run(
                [sys.executable, "-B", "-c", DISCOVER, start, pattern, top, str(output)],
                cwd=root, check=False, capture_output=True, text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            if result.returncode != 0 or not output.is_file():
                detail = (result.stderr.strip().splitlines() or ["no output"])[-1]
                errors.append(f"DISCOVER: {where} failed: {detail}")
                continue
            data = json.loads(output.read_text(encoding="utf-8"))
        messages = data["errors"] + [""] * len(data["failures"])
        for module, message in zip(data["failures"], messages):
            lines = [line.strip() for line in message.splitlines() if line.strip()]
            detail = f": {lines[-1]}" if lines else ""
            errors.append(f"DISCOVER: {where} could not import module {module}{detail}")
        for path, name, is_skipped in data["tests"]:
            (skipped if is_skipped else methods).setdefault(relative_path(root, path), set()).add(name)
    return methods, skipped, errors


def defined_methods(root: Path, path: str) -> set[str]:
    location = root / path
    if not location.is_file():
        return set()
    try:
        tree = ast.parse(location.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    return {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    }


def missing_test(root: Path, methods: dict[str, set[str]], skipped: dict[str, set[str]], token: str) -> str | None:
    path, _, name = token.partition("::")
    if name in methods.get(path, set()):
        return None
    if name in skipped.get(path, set()):
        return f"test {token} that unittest skips"
    if name.rpartition(".")[2] in defined_methods(root, path):
        return f"test {token} that unittest does not run"
    return f"missing test {token}"


def manifest_cases(root: Path) -> set[str]:
    cases = set()
    for relative in MANIFESTS:
        path = root / relative
        if path.is_file():
            for case_id in re.findall(r"^\s*- id:\s*(\S+)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE):
                cases.add(f"{relative}#{case_id}")
    return cases


def workflow_commands(root: Path) -> set[str]:
    path = root / WORKFLOW
    if not path.is_file():
        return set()
    return {match.strip() for match in re.findall(r"^\s*- run:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)}


def check_matrix(root: Path, requirements: dict[str, dict[str, str]]) -> tuple[dict[str, int], list[str]]:
    text = (root / VM).read_text(encoding="utf-8")
    trace_rows = rows(section(text, "Requirement traceability"), REQ_ID)
    gap_rows = rows(section(text, "Untested requirement gaps"), GAP_ID)
    orphan_rows = rows(section(text, "Tests without a requirement"), re.compile(r"`[^`]+::[^`]+`"))
    gaps = {row[0]: row for row in gap_rows}
    cases = manifest_cases(root)
    commands = workflow_commands(root)
    methods, skipped, errors = collect_tests(root, commands)
    referenced_tests: set[str] = set()
    referenced_gaps: set[str] = set()
    coverage_by_req: dict[str, str] = {}

    for row in trace_rows:
        if len(row) < 6:
            errors.append(f"VM: row for {row[0]} needs 6 columns")
            continue
        req_id, method, verified_by, coverage, gap, _result = row[:6]
        if req_id not in requirements:
            errors.append(f"VM: {req_id} is not in the SRS")
        if req_id in coverage_by_req:
            errors.append(f"VM: duplicate row for {req_id}")
        if coverage not in COVERAGE:
            errors.append(f"VM: {req_id} coverage must be Full, Partial or None")
        coverage_by_req[req_id] = coverage
        automated = False
        inspected = False
        for token in re.findall(r"`([^`]+)`", verified_by):
            if "::" in token:
                problem = missing_test(root, methods, skipped, token)
                if problem:
                    errors.append(f"VM: {req_id} references {problem}")
                else:
                    referenced_tests.add(token)
                    automated = True
            elif token.startswith("ci: "):
                if token[4:] not in commands:
                    errors.append(f"VM: {req_id} references a command not run by CI: {token[4:]}")
                else:
                    automated = True
            elif token.startswith("inspect: "):
                if not (root / token[9:]).exists():
                    errors.append(f"VM: {req_id} inspection target missing: {token[9:]}")
                else:
                    inspected = True
            elif "#" in token and token.split("#", 1)[0] in MANIFESTS:
                if token not in cases:
                    errors.append(f"VM: {req_id} references missing evaluation case {token}")
            else:
                errors.append(f"VM: {req_id} has an unrecognized verification reference `{token}`")
        gap_ids = GAP_ID.findall(gap)
        referenced_gaps.update(gap_ids)
        if coverage == "Full":
            if gap_ids:
                errors.append(f"VM: {req_id} is Full but names gap {', '.join(gap_ids)}")
            if not automated and not ("I" in method and inspected):
                errors.append(f"VM: {req_id} is Full without an automated test, CI command or named inspection")
        elif coverage in {"Partial", "None"}:
            if not gap_ids:
                errors.append(f"VM: {req_id} is {coverage} without an untested-gap ID")
            for gap_id in gap_ids:
                if gap_id not in gaps:
                    errors.append(f"VM: {req_id} names unregistered gap {gap_id}")

    for req_id, record in requirements.items():
        if record.get("Status", "").startswith("Deleted"):
            continue
        if req_id not in coverage_by_req:
            errors.append(f"VM: requirement {req_id} has no verification row")
    for gap_id, row in gaps.items():
        if gap_id not in referenced_gaps:
            errors.append(f"VM: gap {gap_id} is not referenced by any requirement row")
        for req_id in REQ_ID.findall(row[1] if len(row) > 1 else ""):
            if req_id not in requirements:
                errors.append(f"VM: gap {gap_id} names unknown requirement {req_id}")

    listed_orphans = set()
    for row in orphan_rows:
        listed_orphans.update(re.findall(r"`([^`]+::[^`]+)`", row[0]))
    for path, names in methods.items():
        for name in sorted(names):
            token = f"{path}::{name}"
            if token not in referenced_tests and token not in listed_orphans:
                errors.append(f"VM: test {token} traces to no requirement and is not listed as supporting")
    for token in sorted(listed_orphans):
        problem = missing_test(root, methods, skipped, token)
        if problem:
            errors.append(f"VM: supporting-test row names {problem}")

    counts = {
        "requirements": sum(1 for r in requirements.values() if not r.get("Status", "").startswith("Deleted")),
        "rows": len(coverage_by_req),
        "full": sum(1 for c in coverage_by_req.values() if c == "Full"),
        "partial": sum(1 for c in coverage_by_req.values() if c == "Partial"),
        "none": sum(1 for c in coverage_by_req.values() if c == "None"),
        "gaps": len(gaps),
        "tests": sum(len(names) for names in methods.values()),
        "tests_traced": len(referenced_tests),
        "tests_supporting": len(listed_orphans),
    }
    return counts, errors


def check_design(root: Path, requirements: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    text = (root / SDD).read_text(encoding="utf-8")
    headings = set(re.findall(r"^## (\d+)\.", text, re.MULTILINE))
    component_rows = rows(section(text, "4. Components"), re.compile(r"[^|]+"))
    allocated: set[str] = set()
    for row in component_rows:
        if row[0] == "Component" or set(row[0]) <= {"-", ":"}:
            continue
        last = row[-1]
        ids = REQ_ID.findall(last)
        if not ids and "infrastructure" not in last.lower():
            errors.append(f"SDD: component '{row[0]}' lists no requirement and is not marked infrastructure")
        for req_id in ids:
            if req_id not in requirements:
                errors.append(f"SDD: component '{row[0]}' names unknown requirement {req_id}")
            allocated.add(req_id)
    for req_id, record in requirements.items():
        if record.get("Status", "").startswith("Deleted"):
            continue
        if req_id not in allocated:
            errors.append(f"SDD: requirement {req_id} is not allocated to any component")
        target = re.search(r"SDD §(\d+)", record.get("Allocated to", ""))
        if not target:
            errors.append(f"SRS: {req_id} 'Allocated to' must name an SDD section (SDD §N)")
        elif target.group(1) not in headings:
            errors.append(f"SRS: {req_id} is allocated to missing SDD §{target.group(1)}")
    return errors


def check_derivations(root: Path, requirements: dict[str, dict[str, str]]) -> list[str]:
    errors = []
    for req_id, record in requirements.items():
        tokens = re.findall(r"`([^`]+)`", record.get("Derivation", ""))
        paths = [token for token in tokens if "/" in token or re.search(r"\.[A-Za-z]+$", token)]
        if not paths:
            errors.append(f"SRS: {req_id} derivation must name at least one source path in backticks")
        for path in paths:
            if not (root / path.split("#", 1)[0]).exists():
                errors.append(f"SRS: {req_id} derivation path does not exist: {path}")
    return errors


def check_data_dictionary(root: Path) -> list[str]:
    spec = importlib.util.spec_from_file_location("poodo_check_capsule", root / CAPSULE_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    text = (root / DD).read_text(encoding="utf-8")
    errors = []
    names = set(module.REQUIRED) | set(module.OPTIONAL)
    for enum in ("CLAIM_STATES", "RECORD_STATES", "PREDICTION_STATES", "COMPLETENESS", "DELIVERY_STATES", "OUTCOME_STATES"):
        names |= set(getattr(module, enum))
    for name in sorted(names):
        if f"`{name}`" not in text:
            errors.append(f"DD: capsule field or value `{name}` is not in the data dictionary")
    return errors


def slug(heading: str) -> str:
    value = re.sub(r"[`*]", "", heading.strip().lower())
    value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            base = slug(match.group(1))
            count = seen.get(base, 0)
            seen[base] = count + 1
            found.add(base if count == 0 else f"{base}-{count}")
    return found


def markdown_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*.md")):
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.startswith(".venv") for part in parts):
            continue
        files.append(path)
    return files


def check_links(root: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    checked = 0
    cache: dict[Path, set[str]] = {}
    for path in markdown_files(root):
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target):
                    continue
                checked += 1
                file_part, _, anchor = target.partition("#")
                destination = (path.parent / file_part).resolve() if file_part else path
                where = f"{path.relative_to(root).as_posix()}:{number}"
                if not destination.exists():
                    errors.append(f"LINK: {where} dead link {target}")
                    continue
                if anchor and destination.suffix == ".md":
                    if destination not in cache:
                        cache[destination] = anchors(destination)
                    if anchor not in cache[destination]:
                        errors.append(f"LINK: {where} missing anchor #{anchor} in {destination.relative_to(root).as_posix()}")
    return checked, errors


def run(root: Path) -> tuple[dict[str, int], list[str]]:
    requirements, errors = parse_requirements((root / SRS).read_text(encoding="utf-8"))
    counts, matrix_errors = check_matrix(root, requirements)
    errors += matrix_errors
    errors += check_design(root, requirements)
    errors += check_derivations(root, requirements)
    errors += check_data_dictionary(root)
    links, link_errors = check_links(root)
    errors += link_errors
    counts["links"] = links
    return counts, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail on untraced requirements, missing tests, untraced tests or dead doc links.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true", help="print counts and errors as JSON")
    args = parser.parse_args(argv)
    counts, errors = run(args.root.resolve())
    if args.json:
        print(json.dumps({"counts": counts, "errors": errors}, indent=2, sort_keys=True))
    else:
        for error in errors:
            print(error)
        print(
            "trace: {requirements} requirements, {full} full, {partial} partial, {none} none, {gaps} untested gaps; "
            "{tests} tests ({tests_traced} traced, {tests_supporting} supporting); {links} links checked".format(**counts)
        )
        print("trace check failed" if errors else "trace check passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
