# POODO software test plan and procedures

| Field | Value |
|---|---|
| Document ID | POODO-STP |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Scope and approach

Two kinds of verification apply. Structural checks run in CI and test the validators and the documentation trace. Behavioral trials would test whether an agent following the skill meets REQ-PO-001 to REQ-PO-021; they are designed (22 cases) but have never been run. This plan merges the test plan (SWEHB 5.10) and test procedures (5.14).

## 2. Test levels

All commands run from the checkout root and are identical to the `run:` steps in [checks.yml](../../.github/workflows/checks.yml). S1–S5 run on Python 3.10 and 3.14; S6 and S7 run once per CI run in their own jobs.

| ID | Level | What it covers | Location | Command |
|---|---|---|---|---|
| S1 | System (package) | The real package passes the package validator | `scripts/validate_skill.py` | `python scripts/validate_skill.py` |
| S2 | Unit / regression | 61 subprocess tests: 39 of the capsule checker and 22 of the package validator on a temporary package copy | `evals/test_check_capsule.py`, `evals/test_validate_skill.py` | `python -m unittest discover -s evals -p 'test_*.py' -v` |
| S3 | System (fixture) | The valid capsule fixture passes | `evals/fixtures/valid-capsule.yaml` | `python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml` |
| S4 | Documentation | Requirement, design, test and link trace | `tools/check_trace.py` | `python tools/check_trace.py` |
| S5 | Unit | 23 tests: 10 of the trace checker and 13 of the release-document generator | `tools/test_check_trace.py`, `tools/test_gen_release_docs.py` | `python -m unittest discover -s tools -p 'test_*.py' -v` |
| S6 | Static analysis | ruff 0.17.0 default rules over the repository | whole tree | `uvx ruff@0.17.0 check .` |
| S7 | Security | gitleaks 8.28.0 over the full git history | whole history | `gitleaks git --redact --no-banner --exit-code 1 --config .gitleaks.toml .` |
| TP-2 | Acceptance (behavioral) | Agent behavior against the manifests | `evals/` | manual; see §7 |
| — | Regression | All of S1–S7 on every push and pull request | CI | the seven commands above |

No performance test level exists. S7 is the only security check; it scans for committed secrets and does not test the software.

## 3. Test environment

| Item | Values | Source |
|---|---|---|
| OS | `ubuntu-latest` (GitHub-hosted) | checks.yml |
| Runtime | Python 3.10 and 3.14 | checks.yml matrix |
| Dependency | PyYAML 6.0.3 | requirements-dev.txt |
| External services | None for S1–S5. S6 and S7 download ruff and gitleaks from their release hosts. TP-2 needs an agent host, a model and web access | — |

Local runs on another OS are allowed; the STR records the versions used.

## 4. Pass criteria and acceptance

S1–S5 must all exit 0 on both Python versions, and S6 and S7 must exit 0. No known failures are accepted. A behavioral claim needs a TP-2 run that meets thresholds frozen before scoring; [evaluation.md](../../references/evaluation.md) proposes thresholds but none are adopted.

## 5. Coverage

Not measured: no coverage tool is pinned in `requirements-dev.txt`. Requirement coverage is reported instead by the trace check (counts in the STR). MC/DC: N/A (not safety-critical, SWE-219).

## 6. Test data and fixtures

| Fixture | Purpose | Used by |
|---|---|---|
| `evals/fixtures/valid-capsule.yaml` | Passing capsule, revision 2 with a parent | S2, S3 |
| `evals/fixtures/invalid-resurrection.yaml` | Prediction status returns after a terminal state | S2 |
| `evals/fixtures/invalid-truncated-evidence.yaml` | Truncated evidence supporting a claim | S2 |
| Generated in temporary directories | Mutated copies of the valid capsule; mutated copies of the package for the package validator; minimal repositories for the trace checker | S2, S5 |

All fixtures are synthetic.

## 7. Procedures

Automated suites S1–S5: the code is the procedure. Run them with the commands in §2 after `python -m pip install -r requirements-dev.txt` in a fresh virtual environment.

### TP-1 — Full local check on both CI Python versions

- Purpose / requirements: every Full and Partial row in the verification matrix; REQ-PO-044.
- Preconditions: clean checkout; Python 3.10 and 3.14 available.
- Steps: for each version, create a virtual environment, install `requirements-dev.txt`, run S1–S5.
- Expected result and pass/fail criteria: each command exits 0; S2 reports `Ran 61 tests` and `OK`; S5 reports `Ran 23 tests` and `OK`; S4 prints `trace check passed`.
- Last run: 2026-11-08, see the STR in [reports](reports/README.md) for the commit and output digests.

### TP-2 — Behavioral trial

- Purpose / requirements: REQ-PO-001 to REQ-PO-021.
- Preconditions: frozen baseline and candidate commits, model and configuration, permissions, case set, rubric applicability and thresholds, recorded in a copy of [run-record.template.yaml](../../evals/run-record.template.yaml).
- Steps: follow [protocol.md](../../evals/protocol.md). Give the agent only the case prompt and permitted evidence. Run at least three independent trials per case and variant in random order. Blind graders. Continuity cases need at least three lossy summarize and resume cycles.
- Inputs: [manifest.yaml](../../evals/manifest.yaml) (14 cases), [mega-observe.yaml](../../evals/mega-observe.yaml) (8 cases), [rubric.md](../../evals/rubric.md).
- Expected result and pass/fail criteria: per-case and aggregate scores, catastrophic failures and disagreements recorded; pass only against thresholds frozen beforehand.
- Last run: never. Raw runs belong in ignored `evals/runs/`.

### TP-3 — Generate the release documents

- Purpose: produce the VDD and STR for a baseline.
- Preconditions: TP-1 environments; clean tracked tree; `gh` authenticated if issue and PR counts are wanted.
- Steps: `python3 tools/gen_release_docs.py --python <python3.10> --python <python3.14>`; commit the two files it writes and add them to [docs/releases/README.md](../releases/README.md).
- Expected result: exit 0 and two files named `*-main-<short commit>.md`.
- Last run: 2026-11-08 (see [releases](../releases/README.md)).

## 8. Test risks and limitations

- No agent trial exists, so no behavioral requirement has a result.
- CI runs on Linux only.

## 9. Traceability

See the [verification matrix](verification-matrix.md).

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
| 1.1 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | S2 adds package-validator tests; S5 counts updated; S6 ruff and S7 gitleaks added; validator test-gap risks removed | this PR |
