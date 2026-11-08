# POODO software assurance record

| Field | Value |
|---|---|
| Document ID | POODO-SAR |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

Rolling record of requirements, design, test, code-quality and configuration analyses (SWEHB 5.21, 5.22, 5.23, 5.25, 5.26) and the peer-review summary (5.03). Newest entry first.

## Entry 2026-11-08 — baseline `b969150` (documentation baseline PR)

- Analyzed by: documentation lane (agent). Agent analysis is not independent.
- Inputs: poodo main `a61ac75` plus the docs tooling commits on this branch; cstack main `e02a0c4` (read-only); Python 3.10.22 and 3.14.9 with PyYAML 6.0.3; ruff 0.17.0; gitleaks 8.30.1.

### Requirements analysis

- Techniques: `python tools/check_trace.py` (record format, one "shall", derivation paths, allocation, matrix rows, gap registration, orphan tests); manual reading of SKILL.md against REQ-PO-001 to REQ-PO-021; manual reading of both validators to derive REQ-PO-022 to REQ-PO-044.
- Result: 44 requirements; 7 Full, 10 Partial, 27 None; 37 registered untested gaps; 0 trace errors.
- Findings: five requirements had two "shall" clauses (003, 006, 008, 010, 012) and were reworded without changing meaning. The previous SRS covered agent behavior only; the validators had no requirements, so their rules are now REQ-PO-022 to REQ-PO-044. All 21 behavioral requirements remain untested because no trial exists. One open item (OI-1): the `proportional-low-stakes` case conflicts with the research gate.

### Design analysis

- Technique: compare the SDD component table with the tree (`git ls-files`) and with the code paths named in requirement derivations.
- Findings: the previous SDD omitted `assets/`, the evaluation material's role and CI; added. Every requirement is now allocated to a component (enforced by the trace check). No documented component is absent from the tree.

### Testing analysis

- Technique: map each of the 13 capsule-checker tests to the rules it asserts; check each rule in `check_capsule.py` and `validate_skill.py` for a test.
- Findings: `validate_skill.py` has no tests (UG-28 to UG-33); CI only shows the real package passes. Capsule-checker rules without tests: duplicate keys, root field set, lineage, record identity and resolution, invalidated dependencies and head kind, per-record required fields, the `--hard-token-ceiling` option, out-of-set strings, `outcomes[].depends_on`, and exit 2 on an unreadable file (UG-22 to UG-27, UG-34 to UG-37). Exit 2 on a missing file was run by hand on 2026-11-08 and behaved as documented; a hand run is not a test. The `invalid-truncated-evidence.yaml` fixture also triggers the head-kind error, but the test asserts only the evidence message. Coverage is not measured (no tool pinned).

### Source code quality

| Tool | Command | Findings |
|---|---|---|
| ruff 0.17.0 (defaults) | `ruff check --no-cache --isolated --statistics scripts evals tools` | 12: in `scripts/` and `evals/`, 3 I001 import order, 1 FURB162, 1 TRY004; in `tools/`, 5 ISC004 implicit concatenation, 2 UP017 |
| ruff 0.17.0 (security rules) | `ruff check --no-cache --isolated --select S --ignore S603,S101 --statistics scripts evals tools` | 4: 1 S506 in `check_capsule.py`, 3 S607 in `tools/` (`git`/`gh` by name) |
| gitleaks 8.30.1 | `gitleaks git --redact .` and `gitleaks dir --redact .` | No leaks found |

Dispositions: S506 is a false positive (`UniqueKeyLoader` subclasses `yaml.SafeLoader`). FURB162 would break Python 3.10, where `fromisoformat` rejects `Z`, so the `replace` must stay. UP017 suggests `datetime.UTC`, which needs Python 3.11; rejected. I001, TRY004 and ISC004 are style. S607 is accepted for developer tooling. ruff and gitleaks are not CI gates.

### Configuration audit

- The earlier docs named baselines `01e6c60` and `4f47a9d`, which are not in this history (`git cat-file` fails); history was squashed into `36bfe78`. All control documents now name `b969150`.
- The earlier SCMP listed `actions/checkout@v4` and `actions/setup-python@v5`; the workflow uses `@v7` (PRs #17, #18). Corrected.
- The earlier SCMP said the CHANGELOG uses two-component versions; since PR #19 its headings are `3.1.0` and `3.0.0`. Corrected.
- The earlier Cstack ICD pinned cstack `6052bd46`, which shares no history with cstack main; re-pinned to `e02a0c4`. Cstack's 45-file snapshot equals poodo `d1cce9e` byte for byte; versus `a61ac75`, only `.github/workflows/checks.yml` and `CHANGELOG.md` differ.
- Staleness: `git log b969150..HEAD -- SKILL.md references scripts evals agents assets tools .github/workflows` is empty for this PR's documentation commits.
- Byte table in [SCMP §2.1](../configuration/configuration-management.md#21-byte-identities) generated at the baseline.

### Peer review summary

`gh pr list --state all` shows 20 PRs: 16 merged before this one, 4 closed unmerged. None of the 16 has a formal GitHub review. 13 carry a comment from the `chatgpt-codex-connector` app. There is no human second reviewer, which is consistent with the single-maintainer model in SMP §6.

### Findings

| ID | Severity | Finding | Location | Issue | Status |
|---|---|---|---|---|---|
| F-1 | S4 | Control documents cited baseline commits that are not in this history | docs/ | none | Closed in this PR |
| F-2 | S4 | SCMP listed stale action versions and CHANGELOG version form | docs/configuration | none | Closed in this PR |
| F-3 | S4 | Cstack ICD pinned an unreachable Cstack commit | docs/icd/icd-cstack.md | none | Closed in this PR |
| F-4 | S3 | `validate_skill.py` has no tests; a regression in any failure path would pass CI | scripts/validate_skill.py | none | Open (UG-28 to UG-33) |
| F-5 | S3 | Ten capsule-checker rules or options have no test | scripts/check_capsule.py | none | Open (UG-22 to UG-27, UG-34 to UG-37) |
| F-6 | S4 | No branch protection on `main`; review is procedural | repository settings | none | Accepted (SCMP §3) |
| F-7 | S4 | ruff and gitleaks are not CI gates | .github/workflows/checks.yml | none | Accepted (SMP §6) |

No major (S1 or S2) finding, so no issue was filed.

### Overall assessment

The repository does what its docs now say, within structural scope. The validators match their requirements where tested. The main assurance weakness is test depth of the validators and the complete absence of behavioral trials; both are recorded as gaps, not hidden.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline entry | this PR |
