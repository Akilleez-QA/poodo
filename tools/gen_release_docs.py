#!/usr/bin/env python3
"""Generate the POODO version description and test report from a clean checkout."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASES = Path("docs/releases")
REPORTS = Path("docs/verification/reports")
PRODUCT = (
    "SKILL.md",
    "agents/openai.yaml",
    "assets/mega-observe-charter.yaml",
    "requirements-dev.txt",
    "scripts/check_capsule.py",
    "scripts/validate_skill.py",
    "evals/manifest.yaml",
    "evals/mega-observe.yaml",
    "evals/protocol.md",
    "evals/rubric.md",
    "evals/run-record.template.yaml",
)
SUITES = (
    ("S1", "package validator", ["scripts/validate_skill.py"]),
    ("S2", "capsule checker regression tests", ["-m", "unittest", "discover", "-s", "evals", "-p", "test_*.py", "-v"]),
    ("S3", "valid capsule fixture", ["scripts/check_capsule.py", "evals/fixtures/valid-capsule.yaml"]),
    ("S4", "trace and link check", ["tools/check_trace.py"]),
    ("S5", "tool tests", ["-m", "unittest", "discover", "-s", "tools", "-p", "test_*.py", "-v"]),
)
UNITTEST_SUITES = {"S2", "S5"}
NON_PASS = ("failures", "errors", "skipped", "expected failures", "unexpected successes")
DISCLAIMER = (
    "> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), "
    "[NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the "
    "[NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) "
    "documentation guidance. This is not a NASA compliance determination or certification. The software classification "
    "is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, "
    "or hazard analysis is asserted."
)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def gh_json(*args: str) -> list | None:
    if shutil.which("gh") is None:
        return None
    result = subprocess.run(["gh", *args], cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_suite(returncode: int, output: str) -> dict:
    ran = re.findall(r"^Ran (\d+) tests?", output, re.MULTILINE)
    outcomes = dict.fromkeys(NON_PASS, 0)
    for status in re.findall(r"^(?:OK|FAILED|NO TESTS RAN)(?: \((.+)\))?$", output, re.MULTILINE):
        for part in status.split(","):
            key, _, value = part.strip().rpartition("=")
            if key in outcomes and value.isdigit():
                outcomes[key] += int(value)
    last = [line for line in output.strip().splitlines() if line.strip()]
    return {
        "returncode": returncode,
        "tests": sum(int(count) for count in ran) if ran else None,
        "outcomes": outcomes,
        "summary": last[-1] if last else "",
        "digest": hashlib.sha256(output.encode("utf-8")).hexdigest(),
    }


def run_suite(python: str, args: list[str]) -> dict:
    result = subprocess.run([python, *args], cwd=ROOT, check=False, capture_output=True, text=True)
    return parse_suite(result.returncode, result.stdout + result.stderr)


def suite_problems(suite_id: str, result: dict) -> list[str]:
    problems = []
    if result["returncode"] != 0:
        problems.append(f"exit {result['returncode']}")
    if suite_id in UNITTEST_SUITES:
        if result["tests"] is None:
            problems.append("no unittest result line")
        elif result["tests"] == 0:
            problems.append("ran no tests")
    for key in NON_PASS:
        if result["outcomes"].get(key):
            problems.append(f"{result['outcomes'][key]} {key}")
    return problems


def tests_passed(result: dict) -> int:
    return max(0, (result["tests"] or 0) - sum(result["outcomes"].get(key, 0) for key in NON_PASS))


def tree_state() -> tuple[str, list[str]]:
    commit = git("rev-parse", "HEAD")
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout
    return commit, [line[3:] for line in status.splitlines() if line.strip()]


def python_version(python: str) -> str:
    return subprocess.run([python, "-c", "import platform; print(platform.python_version())"],
                          check=True, capture_output=True, text=True).stdout.strip()


def pyyaml_version(python: str) -> str:
    return subprocess.run([python, "-c", "import yaml; print(yaml.__version__)"],
                          check=True, capture_output=True, text=True).stdout.strip()


def trace_counts() -> dict:
    spec = importlib.util.spec_from_file_location("poodo_check_trace", ROOT / "tools" / "check_trace.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    counts, errors = module.run(ROOT)
    counts["errors"] = len(errors)
    return counts


def changelog_unreleased() -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## \[Unreleased\]\s*$(.*?)^## ", text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else "(no Unreleased section)"


def open_items() -> int:
    text = (ROOT / "docs/requirements/requirements.md").read_text(encoding="utf-8")
    return len(re.findall(r"^\| OI-\d+ \|", text, re.MULTILINE))


def line_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for relative in git("ls-files").splitlines():
        suffix = Path(relative).suffix.lower() or "(none)"
        if suffix not in {".py", ".md", ".yaml", ".yml", ".toml", ".txt"}:
            continue
        path = ROOT / relative
        if path.is_file():
            counts[suffix] = counts.get(suffix, 0) + len(path.read_text(encoding="utf-8").splitlines())
    return dict(sorted(counts.items()))


def header(title: str, doc_id: str, commit: str, date: str, dirty: list[str]) -> list[str]:
    if dirty:
        status = "Draft (generated from a dirty working tree; not a baseline)"
        baseline = f"none: working tree differs from `{commit}` in {len(dirty)} path(s)"
        applies = f"uncommitted working tree on top of `{commit}`; not reproducible from any commit"
        scope = "The document describes an uncommitted working tree, not any commit."
        generated = (f"Generated by `python3 tools/gen_release_docs.py --allow-dirty` from uncommitted changes on top of "
                     f"commit `{commit}`. It is not a baseline; commit the changes and rerun the generator.")
    else:
        status = "Baselined (generated)"
        baseline = f"`{commit}`"
        applies = "poodo main at baseline commit (untagged)"
        scope = "The document describes the implementation inspected at the baseline commit."
        generated = f"Generated by `python3 tools/gen_release_docs.py` at commit `{commit}`. Do not edit by hand; rerun the generator."
    lines = [
        f"# {title}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Document ID | {doc_id} |",
        "| Version | 1.0 |",
        f"| Status | {status} |",
        "| Owner | Akilleez-QA |",
        f"| Date | {date} |",
        f"| Baseline commit | {baseline} |",
        f"| Applies to | {applies} |",
        "| Classification | Self-assessed Class E analog; not safety-critical (see SMP §1) |",
        "",
        f"{DISCLAIMER} {scope}",
        "",
        generated,
        "",
    ]
    if dirty:
        lines += ["Paths that differ from the commit (`git status --porcelain --untracked-files=all`):", "", "```text", *dirty, "```", ""]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write docs/releases/VDD-<label>.md and docs/verification/reports/STR-<label>.md.")
    parser.add_argument("--python", action="append", required=True, help="interpreter to run the suites with; repeat for a matrix")
    parser.add_argument("--allow-dirty", action="store_true", help="permit uncommitted tracked changes (output is then not a baseline)")
    args = parser.parse_args(argv)

    commit, dirty = tree_state()
    if dirty and not args.allow_dirty:
        print("refusing to generate from a dirty working tree; commit first", file=sys.stderr)
        return 2
    short = commit[:7]
    label = f"main-{short}-dirty" if dirty else f"main-{short}"
    marker = f"{short} + uncommitted changes" if dirty else short
    on_commit = f"`{commit}` plus uncommitted changes" if dirty else f"`{commit}`"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tags = git("tag", "--list").splitlines()
    describe = subprocess.run(["git", "describe", "--tags", "--always"], cwd=ROOT, check=False, capture_output=True, text=True).stdout.strip()
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r'version:\s*"([^"]+)"', skill)
    method_version = version.group(1) if version else "unknown"

    matrix = []
    for python in args.python:
        entry = {"python": python_version(python), "pyyaml": pyyaml_version(python), "suites": []}
        for suite_id, name, suite_args in SUITES:
            entry["suites"].append((suite_id, name, " ".join(["python", *suite_args]), run_suite(python, suite_args)))
        matrix.append(entry)
    trace = trace_counts()
    problems = []
    for entry in matrix:
        for suite_id, _, _, result in entry["suites"]:
            found = suite_problems(suite_id, result)
            if found:
                problems.append((suite_id, f"Python {entry['python']}", "; ".join(found)))
    if trace["errors"]:
        problems.append(("trace", "the generator's trace check", f"{trace['errors']} trace error(s)"))
    all_passed = not problems

    issues_open = gh_json("issue", "list", "--state", "open", "--json", "number,title,labels", "--limit", "200")
    issues_closed = gh_json("issue", "list", "--state", "closed", "--json", "number", "--limit", "200")
    prs = gh_json("pr", "list", "--state", "merged", "--json", "number,reviews", "--limit", "200")
    log = git("log", "--format=%h %s", "-n", "15")

    conclusion = "all structural suites passed" if all_passed else "NOT all passed; see section 4"
    if dirty:
        conclusion += " (generated from a dirty working tree, so this is not a baseline result)"
    str_lines = header(f"POODO software test report {label}", f"POODO-STR-{label}", commit, date, dirty)
    str_lines += [
        "## 1. Summary",
        "",
        f"- Conclusion: {conclusion} on " + ", ".join(f"Python {entry['python']}" for entry in matrix) + ".",
        "- Remaining deficiencies: no behavioral trial has been recorded, so behavioral requirements REQ-PO-001 to REQ-PO-021 "
        "have no test result. Untested requirement gaps are listed in the verification matrix.",
        "- Test-environment impact: local run, not the GitHub Actions runner; the operating system differs from CI "
        "(`ubuntu-latest`). Python versions match the CI matrix.",
        "",
        "## 2. Test log",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Commit | {on_commit} |",
        f"| `git describe` | `{describe}` |",
        f"| Date (UTC) | {stamp} |",
        "| Environment | " + "; ".join(f"Python {e['python']}, PyYAML {e['pyyaml']}" for e in matrix) + " |",
        "| Run by | operator, `tools/gen_release_docs.py` (local) |",
        "",
        "## 3. Results",
        "",
        "| Python | Suite | Command | Tests | Exit | Last line | Output SHA-256 |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in matrix:
        for suite_id, name, command, result in entry["suites"]:
            tests = "—" if result["tests"] is None else str(result["tests"])
            summary = result["summary"].replace("|", "\\|")
            str_lines.append(f"| {entry['python']} | {suite_id} {name} | `{command}` | {tests} | {result['returncode']} | {summary} | `{result['digest'][:16]}` |")
    str_lines += [
        "",
        "Requirement-level results are in the [verification matrix](../verification-matrix.md); each Full row's tests are in S2 or S5 above.",
        "",
        "## 4. Problems and deviations",
        "",
        "| Item | Description | Disposition |",
        "|---|---|---|",
    ]
    if problems:
        for item, where, found in problems:
            str_lines.append(f"| {item} | Not passed on {where}: {found} | Open |")
    else:
        str_lines.append("| — | No failing, skipped or empty suite and no trace error | — |")
    str_lines += [
        "",
        "## 5. Metrics",
        "",
        "| Measure | Value | Command |",
        "|---|---|---|",
    ]
    for entry in matrix:
        total = sum(result["tests"] or 0 for *_, result in entry["suites"])
        passed = sum(tests_passed(result) for *_, result in entry["suites"])
        str_lines.append(f"| Unit tests run / passed (Python {entry['python']}) | {total} / {passed} | S2 + S5 |")
    str_lines += [
        f"| Requirements total / full / partial / none | {trace['requirements']} / {trace['full']} / {trace['partial']} / {trace['none']} | `python tools/check_trace.py` |",
        f"| Registered untested gaps | {trace['gaps']} | `python tools/check_trace.py` |",
        f"| Tests traced / supporting | {trace['tests_traced']} / {trace['tests_supporting']} | `python tools/check_trace.py` |",
        f"| Doc links checked / trace errors | {trace['links']} / {trace['errors']} | `python tools/check_trace.py` |",
        f"| Open items (TBD) in SRS §8 | {open_items()} | count of `OI-` rows in SRS §8 |",
        "| Requirement changes since previous tag | N/A: no tag exists | `git tag --list` |",
        "| Issues open by severity | " + ("not queried" if issues_open is None else f"{len(issues_open)} open (no severity labels in use)") + " | `gh issue list --state open` |",
        "| Issues closed (all time) | " + ("not queried" if issues_closed is None else str(len(issues_closed))) + " | `gh issue list --state closed` |",
        "| PRs merged / with recorded reviews | " + ("not queried" if prs is None else f"{len(prs)} / {sum(1 for p in prs if p.get('reviews'))}") + " | `gh pr list --state merged` |",
        "| Static-analysis findings | see assurance record (ruff is not a CI gate) | — |",
        "| Coverage | not measured: no coverage tool in `requirements-dev.txt` | — |",
        "| Source lines by extension | " + ", ".join(f"{k} {v}" for k, v in line_counts().items()) + " | `git ls-files` + line count |",
        "",
        "## 6. Rationale for decisions",
        "",
        "The behavioral requirements are accepted with no result because the repository has no automated agent runner and no recorded trial. "
        "They are reported as untested, not as passed.",
        "",
        "## Change history",
        "",
        "| Version | Date | Commit | Change | Reviewed in |",
        "|---|---|---|---|---|",
        f"| 1.0 | {date} | `{marker}` | Generated | this PR |",
        "",
    ]

    vdd_lines = header(f"POODO version description {label}", f"POODO-VDD-{label}", commit, date, dirty)
    vdd_lines += [
        "## 1. Identification",
        "",
        "| Item | Value |",
        "|---|---|",
        "| Name | POODO |",
        f"| Method version | {method_version} (`SKILL.md` metadata) |",
        "| Capsule schema | POODO_CONTINUATION/3.0 |",
        f"| Tag | {'none: no tags exist' if not tags else ', '.join(tags)} |",
        f"| Commit | {on_commit} |",
        "| Previous tag | none |",
        f"| Generated (UTC) | {stamp} |",
        "",
        "## 2. Contents",
        "",
        "The deliverable is the repository tree at the commit: the skill entry point `SKILL.md`, the `references/` library, "
        "`agents/openai.yaml`, the Mega Observe charter in `assets/`, the two validators in `scripts/`, the evaluation material "
        "in `evals/`, synthetic `examples/`, and `docs/`. No package or binary artifact is published.",
        "",
        "## 3. Build and install",
        "",
        "There is no build step. Install by cloning the repository into the host's skill directory; see "
        "[Getting started](../guides/tutorials/getting-started.md). Run the checks with:",
        "",
        "```sh",
        "python -m pip install -r requirements-dev.txt",
        "python scripts/validate_skill.py",
        "python -m unittest discover -s evals -p 'test_*.py' -v",
        "python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml",
        "python tools/check_trace.py",
        "python -m unittest discover -s tools -p 'test_*.py' -v",
        "```",
        "",
        "## 4. Integrity",
        "",
        "| File | SHA-256 |",
        "|---|---|",
    ]
    for relative in PRODUCT:
        vdd_lines.append(f"| `{relative}` | `{sha256(ROOT / relative)}` |")
    references = sorted((ROOT / "references").glob("*.md"))
    joined = hashlib.sha256(b"".join(p.name.encode() + b"\0" + p.read_bytes() for p in references)).hexdigest()
    vdd_lines += [
        f"| `references/*.md` ({len(references)} files, name+bytes, sorted) | `{joined}` |",
        "",
        "## 5. Changes since previous tag",
        "",
        "No previous tag exists. The CHANGELOG Unreleased section at this commit reads:",
        "",
    ]
    vdd_lines += ["> " + line if line else ">" for line in changelog_unreleased().splitlines()]
    vdd_lines += [
        "",
        "Most recent commits (`git log -n 15 --format='%h %s'`):",
        "",
        "```text",
        log,
        "```",
        "",
        "## 6. Open problems and workarounds",
        "",
    ]
    if issues_open is None:
        vdd_lines.append("Issue tracker not queried (`gh` unavailable).")
    elif not issues_open:
        vdd_lines.append("No open issues (`gh issue list --state open` returned none). Known limitations are in the "
                         "[limitations page](../guides/explanation/limitations.md) and the untested gaps in the "
                         "[verification matrix](../verification/verification-matrix.md).")
    else:
        vdd_lines += ["| Issue | Title |", "|---|---|"]
        vdd_lines += [f"| #{i['number']} | {i['title']} |" for i in issues_open]
    vdd_lines += [
        "",
        "## 7. Documentation baseline",
        "",
        "Control documents list their own baseline commits in their headers; the index is [docs/README.md](../README.md).",
        "",
        "## 8. Verification and scans",
        "",
        f"- Test report: [STR-{label}](../verification/reports/STR-{label}.md).",
        "- Secret scan and static analysis: recorded in the [assurance record](../assurance/assurance-record.md); neither is a CI gate.",
        "",
        "## Change history",
        "",
        "| Version | Date | Commit | Change | Reviewed in |",
        "|---|---|---|---|---|",
        f"| 1.0 | {date} | `{marker}` | Generated | this PR |",
        "",
    ]

    (ROOT / REPORTS).mkdir(parents=True, exist_ok=True)
    (ROOT / RELEASES).mkdir(parents=True, exist_ok=True)
    str_path = ROOT / REPORTS / f"STR-{label}.md"
    vdd_path = ROOT / RELEASES / f"VDD-{label}.md"
    str_path.write_text("\n".join(str_lines), encoding="utf-8")
    vdd_path.write_text("\n".join(vdd_lines), encoding="utf-8")
    print(f"wrote {str_path.relative_to(ROOT)} and {vdd_path.relative_to(ROOT)}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
