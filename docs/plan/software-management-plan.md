# POODO software management plan

| Field | Value |
|---|---|
| Document ID | POODO-SMP |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see §1) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

This plan merges the development, maintenance (SWEHB 5.04), assurance (5.17) and risk (5.27) plans into one short document, as the family standard allows for a skill/tool repository.

## 1. Software classification (self-assessed)

- Assessed against: NPR 7150.2D Appendix D and NASA-STD-8739.8B §4.2, as an analog. POODO is not NASA software and no NASA authority has reviewed this assessment.
- Analog class: **Class E** (general-purpose research/technology software). Rationale: POODO is a set of instructions and two validators that run on general-purpose computers; it supports no ground test, flight test or operation; a defect affects the productivity of an individual user or a small group; it is not used for decisions about an operational system.
- Not Class F: not Agency business or IT infrastructure.
- Safety-critical determination (SWE-205 analog): **not safety-critical.** POODO meets none of the five criteria in NASA-STD-8739.8B §4.2, and no hazard analysis assigns it a hazard cause, control or mitigation. The skill can steer an agent that has tools, but the host and the user hold every permission; the skill grants none (REQ-PO-008).
- Documentation baseline: Class E with voluntary adoption of the Class D documentation set; see the [compliance matrix](compliance-matrix.md).
- Re-evaluation triggers: commanding physical hardware; use in a regulated, safety or production decision path; handling personal or secret data beyond local configuration; external deployment as a shared service; shipping code that drives an agent's tools directly.
- Assessed by / date / baseline commit: Akilleez-QA (documentation lane, agent-authored, not independent) / 2026-11-08 / `b969150462c5fde83bbec9358ad17aa1d3663ec2`.

## 2. Purpose, scope and organization

POODO is the family's skill/tool repository: an explicit-invocation reasoning and orchestration skill for Codex and Agent Skills clients, with a package validator and a continuation-capsule checker. Cstack carries a byte-pinned partial snapshot of it ([Cstack ICD](../icd/icd-cstack.md)).

Authority: the maintainer (GitHub `Akilleez-QA`, the only entry in [CODEOWNERS](../../.github/CODEOWNERS)) is the sole approver. Agent lanes and Dependabot open pull requests. External contributors use pull requests under [CONTRIBUTING.md](../../CONTRIBUTING.md).

## 3. Life-cycle model and work tracking

Trunk-based. Every change is a pull request to `main`; the maintainer merges it after the CI checks pass. GitHub Issues are the work breakdown and the problem-report system; no milestones are in use. Releases: none tagged yet; the CHANGELOG records method versions 3.0.0 and 3.1.0 and an Unreleased section (see the [SCMP](../configuration/configuration-management.md)). Cost estimation, staffing, budgets, subcontractor management and CMMI: N/A (unfunded, single-maintainer open source).

## 4. Engineering and test environment

| Item | Version / source | Where defined |
|---|---|---|
| Language runtime | Python 3.10 and 3.14 | [checks.yml](../../.github/workflows/checks.yml) matrix |
| Dependency | PyYAML 6.0.3 | [requirements-dev.txt](../../requirements-dev.txt) |
| Test runner | `unittest` (standard library) | checks.yml |
| CI | GitHub Actions on `ubuntu-latest`, `actions/checkout@v7`, `actions/setup-python@v7` | checks.yml |
| Static analysis / type check | ruff 0.17.0, default rules, as a CI job (`uvx ruff@0.17.0 check .` via `astral-sh/setup-uv@v7`); no type checker | checks.yml |
| Secret scanning | gitleaks 8.28.0 as a CI job over the full git history, release archive checked against its published SHA-256; `.gitleaks.toml` (default rules) | checks.yml; [.gitleaks.toml](../../.gitleaks.toml) |
| Dependency updates | Dependabot, weekly, for GitHub Actions and pip, up to 3 open PRs each | [dependabot.yml](../../.github/dependabot.yml) |

## 5. Verification and validation approach

Verification: pull-request review, the CI suites in §6, and the trace check. Records: [verification matrix](../verification/verification-matrix.md), test reports under [verification/reports](../verification/reports/README.md), and the [assurance record](../assurance/assurance-record.md). The [test plan](../verification/test-plan.md) gives levels, commands and procedures.

Validation (does the skill help an agent do the intended job?) needs recorded, graded agent trials under [protocol.md](../../evals/protocol.md). None have been run. Behavioral improvement is unmeasured, and the docs say so wherever a result could be implied.

Acceptance criteria for a release (SWE-034): every CI step passes on both Python versions; the trace check passes; the CHANGELOG has a section for the release; a VDD and STR are generated at the release commit; any behavioral claim in the release notes cites a recorded trial.

## 6. Software assurance

There is one maintainer, so there is no organizational independence. Agent reviewers and CI gates give separation of method, not of organization. Agent-authored analysis, including this documentation set, is labelled as not independent.

| Gate | Command | Fails on | Record |
|---|---|---|---|
| Package validator | `python scripts/validate_skill.py` | Missing files, front matter, host metadata, broken reference links, placeholders, schema literals, execute bits | CI; STR |
| Checker regression tests | `python -m unittest discover -s evals -p 'test_*.py' -v` | Any capsule-checker or package-validator regression | CI; STR |
| Capsule fixture | `python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml` | The valid fixture failing | CI; STR |
| Trace and link check | `python tools/check_trace.py` | Untraced requirement, missing test, untraced test, unregistered gap, SDD allocation gap, data-dictionary gap, dead link | CI; STR |
| Trace checker tests | `python -m unittest discover -s tools -p 'test_*.py' -v` | Any trace-checker regression | CI; STR |
| Static analysis | `uvx ruff@0.17.0 check .` | Any ruff default-rule finding | CI |
| Secret scan | `gitleaks git --redact --no-banner --exit-code 1 --config .gitleaks.toml .` | Any secret found in the git history | CI |
| Peer review | Pull request | Maintainer does not approve | PR; SAR summary |

Static analysis (ruff) and secret scanning (gitleaks) are CI gates since the 2026-11-10 findings sweep. ruff's security rules (`--select S`) are not in the gate; they are run by hand at each documentation baseline and recorded in the assurance record.

## 7. Security, privacy and secure coding

Attack surface: two command-line scripts that read local files. No network access, no file writes, no subprocesses in the product scripts, no `eval`. YAML is parsed with `yaml.safe_load` or a `SafeLoader` subclass. The larger risk is behavioral: an agent following the skill acts with whatever tools the host grants. The skill's mitigation is an obligation, not code: authority comes only from the user (REQ-PO-008), and the expensive Mega Observe mode needs an agreed ceiling (REQ-PO-017).

Privacy: examples and fixtures are synthetic. Raw evaluation runs go in ignored `evals/runs/` until reviewed. [CONTRIBUTING.md](../../CONTRIBUTING.md) forbids secrets, private paths and customer data in issues and fixtures. Reporting route: [SECURITY.md](../../SECURITY.md).

## 8. Open-source, reused and vendored components

| Component | License | Pin | Use |
|---|---|---|---|
| PyYAML | MIT | `==6.0.3` in requirements-dev.txt | YAML parsing in both validators |
| actions/checkout, actions/setup-python | MIT | major tag `@v7` (not a commit SHA) | CI only |
| Contributor Covenant 2.1 | CC BY 4.0 | text in CODE_OF_CONDUCT.md | Community policy |

No vendored source. Dependabot proposes updates; the maintainer reviews and merges them after CI passes. Reuse by others: GPL-3.0-only ([LICENSE](../../LICENSE), [NOTICE.md](../../NOTICE.md)); Cstack reuses a byte-pinned subset.

## 9. Problem reporting and severity

| Severity | Meaning | Response |
|---|---|---|
| S1 | Wrong result presented as valid (for example a validator passing malformed input, or docs claiming a behavioral result that does not exist), data loss, or security exposure | Fix or withdraw before the next merge |
| S2 | Feature unusable, no workaround | Next release |
| S3 | Feature degraded, workaround exists | Scheduled |
| S4 | Cosmetic or documentation | As convenient |

Report through the [problem report](../../.github/ISSUE_TEMPLATE/problem-report.md) or [change request](../../.github/ISSUE_TEMPLATE/change-request.md) templates. Severity is a field in the template; the repository has no severity labels. Closing an issue requires a linked PR that names its verification.

## 10. Configuration management

Baselines are commits; no tags exist yet. Change control is the pull request plus CI. Details: [SCMP](../configuration/configuration-management.md).

## 11. Operations, maintenance and retirement

- Changes: analyze in an issue or PR description, implement in a PR, review, merge after CI. Method changes must explain their effect on evidence separation, authority, research, divergence, contradiction handling and continuity (CONTRIBUTING).
- Supported versions: only `main` ([SECURITY.md](../../SECURITY.md)).
- Migration notes: the CHANGELOG. Capsule schema changes need a new schema version; the checker keeps accepting the legacy 2.1 schema.
- Delivery: `git clone` into the host's skill directory. No package registry.
- Version data for users: SKILL.md `metadata.version`, the CHANGELOG, and the VDDs in [docs/releases](../releases/README.md).
- Backup operational software: N/A; the previous commit is the fallback.
- Retirement: final tag, an archive notice in README Status, then GitHub archive.

## 12. Risk register

Reviewed at every release. Likelihood (L) and consequence (C) on a 1–5 scale.

| ID | Risk | L | C | Mitigation | Status | Issue |
|---|---|---|---|---|---|---|
| R-1 | A reader takes structural checks or synthetic examples as proof that the skill improves agent behavior | 3 | 3 | Every pass message and doc states the limit; behavioral rows stay None/Partial; trace check | Open | none |
| R-2 | Validator rules regress unnoticed | 1 | 2 | Every validator requirement (REQ-PO-022 to REQ-PO-043) has Full test coverage (former gaps UG-22 to UG-37 closed 2026-11-10); new rules need a test or a registered gap | Mitigated | none |
| R-3 | The Cstack snapshot drifts from POODO main and readers assume they match | 2 | 2 | Cstack ICD records the pin and a byte comparison; re-run on each pin change | Open | none |
| R-4 | An agent following the skill acts beyond what the user intended (for example an expensive Mega Observe run) | 2 | 3 | Authority invariant, explicit-only invocation, budget charter; host permissions | Open | none |
| R-5 | Unpinned action tags (`@v7`) change behavior under CI | 2 | 1 | Dependabot; CI runs on every PR | Accepted | none |

## 13. Measurement

Each test report carries a metrics block generated by `tools/gen_release_docs.py`: tests run and passed per Python version, requirement coverage counts and gaps from the trace check, link count, open items, issues, merged PRs and line counts. Static-analysis counts are in the assurance record. Coverage is not measured; no coverage tool is pinned.

## 14. Training

Not applicable. SWEHB 5.15 anticipates one training plan per NASA Center, NPR SWE-017 applies only to Classes A–C, and the repo has no staff. Contributor onboarding is CONTRIBUTING plus the tutorials.

## 15. Documentation list

The [documentation index](../README.md) lists every control document and guide.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
| 1.1 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | §4 and §6: ruff and gitleaks are CI gates (F-7 closed); R-2 mitigated by validator tests (F-4, F-5 closed) | this PR |
