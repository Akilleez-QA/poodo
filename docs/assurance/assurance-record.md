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

## Entry 2026-11-10 — findings sweep `07d033a`..`89c25a9`

- Analyzed by: records lane (agent) for the family findings sweep. Agent analysis is not independent.
- Inputs: poodo main `aeba967` plus the sweep commits `07d033a`..`89c25a9` on `fix/findings-sweep`; Python 3.10.22 and 3.14.9 with PyYAML 6.0.3; ruff 0.17.0; gitleaks 8.30.1 locally (CI pins 8.28.0).

### Testing analysis

- Technique: each untested gap UG-22 to UG-37 got tests named after it (`test_ug_NN_*`), plus two `test_f_4_*` tests of combined failures and missing files. The sweep author reports that 26 subtests failed against the unchanged scripts, and that switching each existing rule off one at a time was caught by a UG test in all 32 cases; this lane did not repeat that mutation run.
- Result: 49 new tests (26 in `evals/test_check_capsule.py`, 23 in `evals/test_validate_skill.py`). Trace: 46 requirements, 25 Full, 4 Partial, 17 None; 21 registered untested gaps, all behavioral (UG-01 to UG-21).
- Defects the tests exposed, fixed in the same commits. Capsule checker: `objective`, `next_step`, `highest_justified_claim`, `required_runtime_observation`, `who_controls_next_test` and claim `text` passed when null, `[]` or `{}`, because `str(None)` is `"None"`; the collection set made the record reported as a duplicate depend on the hash seed. Package validator: removing the opening `POODO_CONTINUATION_V3_0` marker passed, because it is a substring of `END_POODO_CONTINUATION_V3_0`; a non-mapping `metadata`, a non-string `default_prompt` or `short_description`, or a non-UTF-8 file raised a traceback.

### Source code quality

| Tool | Command | Findings |
|---|---|---|
| ruff 0.17.0 (defaults) | `ruff check --no-cache .` | 0 after the sweep. The 12 findings in the 2026-11-08 entry were fixed without Python 3.11-only APIs: FURB162 and UP017 by switching to `date.fromisoformat(value[:10])` and `time.gmtime()`; TRY004 by raising `TypeError` for a non-mapping front matter, with the message unchanged; ISC004 by parenthesizing the joined strings; I001 by sorting imports |
| gitleaks 8.30.1 | `gitleaks git --redact --no-banner --exit-code 1 --config .gitleaks.toml .` | No leaks found in the full history |

ruff and gitleaks are now CI jobs in `.github/workflows/checks.yml`. The ruff job runs `uvx ruff@0.17.0 check .`. The gitleaks job downloads the 8.28.0 release, checks it against the release's `checksums.txt`, and scans the full history (`fetch-depth: 0`). The repository has no ruff configuration, so ruff assumes the newest Python target and some suggested fixes would break Python 3.10; the CI matrix on 3.10 catches that.

### Findings status

| ID | Status | Evidence |
|---|---|---|
| F-4 | Closed in `07d033a`..`89c25a9` | `evals/test_validate_skill.py` covers every failure path of REQ-PO-022 to REQ-PO-027 (UG-28 to UG-33 closed) |
| F-5 | Closed in `07d033a`..`89c25a9` | `evals/test_check_capsule.py` `test_ug_22_*` to `test_ug_27_*` and `test_ug_34_*` to `test_ug_37_*` (UG-22 to UG-27 and UG-34 to UG-37 closed) |
| F-6 | Accepted, unchanged | Branch protection is a repository setting; no change in this sweep |
| F-7 | Closed in `07d033a`..`89c25a9` | ruff and gitleaks CI jobs in `.github/workflows/checks.yml` |

The behavioral gaps UG-01 to UG-21 stay open; they need recorded agent trials.

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
| F-4 | S3 | `validate_skill.py` has no tests; a regression in any failure path would pass CI | scripts/validate_skill.py | none | Closed in `07d033a`..`89c25a9` (entry 2026-11-10) |
| F-5 | S3 | Ten capsule-checker rules or options have no test | scripts/check_capsule.py | none | Closed in `07d033a`..`89c25a9` (entry 2026-11-10) |
| F-6 | S4 | No branch protection on `main`; review is procedural | repository settings | none | Accepted (SCMP §3) |
| F-7 | S4 | ruff and gitleaks are not CI gates | .github/workflows/checks.yml | none | Closed in `07d033a`..`89c25a9` (entry 2026-11-10) |

No major (S1 or S2) finding, so no issue was filed.

### Overall assessment

The repository does what its docs now say, within structural scope. The validators match their requirements where tested. The main assurance weakness is test depth of the validators and the complete absence of behavioral trials; both are recorded as gaps, not hidden.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline entry | this PR |
| 1.1 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | Entry 2026-11-10: F-4, F-5 and F-7 closed; validator defects found by the new tests recorded; ruff and gitleaks results | this PR |
