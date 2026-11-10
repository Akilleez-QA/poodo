# POODO requirements mapping matrix

| Field | Value |
|---|---|
| Document ID | POODO-RMM |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

Self-assessed class: Class E analog, not safety-critical. Baseline: Class E with voluntary adoption of the Class D documentation set. Rows are NPR 7150.2D requirement IDs (SWE). The class column comes from a text extraction of NPR 7150.2D Appendix C; check edge cases against the NPR itself before citing them. Decisions: Applies, Tailored, N/A.

| SWE | Topic | NPR classes | Decision | How met / rationale |
|---|---|---|---|---|
| 013 | Software plans | A–E | Applies | [SMP](software-management-plan.md) |
| 020 | Classification | A–E | Applies | [SMP §1](software-management-plan.md#1-software-classification-self-assessed) |
| 176 | Classification records | A–E | Applies | SMP §1 and its change history |
| 205 | Safety-critical determination | A–E | Applies | SMP §1: not safety-critical |
| 022 | SA / safety / IV&V planning | A–E | Tailored | [SMP §6](software-management-plan.md#6-software-assurance); no independent SA organization; no IV&V |
| 033 | Acquire vs develop | A–E | Applies | [SMP §8](software-management-plan.md#8-open-source-reused-and-vendored-components): developed in house; one third-party library |
| 042 | Source code access | A–E | Applies | Public repository |
| 121 / 139 / 125 | Tailoring, compliance, this matrix | A–E | Applies | This document |
| 148 | Contribute to reuse | A–E | Applies | GPL-3.0-only [LICENSE](../../LICENSE); [README](../../README.md#related-projects) family table |
| 156 | Cybersecurity assessment | A–E | Applies | [SMP §7](software-management-plan.md#7-security-privacy-and-secure-coding), [SECURITY.md](../../SECURITY.md) |
| 024 / 034 / 036 / 037 | Tracking, acceptance criteria, doc plan, milestones | A–D | Tailored | Issues; [SMP §5](software-management-plan.md#5-verification-and-validation-approach) acceptance criteria; [docs index](../README.md); no milestones in use |
| 039 / 040 | Developer status reporting and deliverables to acquirer | A–D | N/A | No acquirer/supplier split; the public repository serves the purpose |
| 027 | COTS/OSS components | A–D | Applies | SMP §8 |
| 015 / 151 / 174 / 016 / 046 / 018 | Cost and schedule | A–D (018: A–C) | N/A | Unfunded single-maintainer project |
| 017 | Training | A–C | N/A | [SMP §14](software-management-plan.md#14-training) |
| 141 / 131 / 178 / 179 | IV&V | A–B | N/A | Not an IV&V-category project |
| 023 / 134 / 219 / 220 | Safety-critical software | A–D if safety-critical | N/A | Not safety-critical (SWE-205) |
| 032 | CMMI rating | A–B | N/A | Not applicable to single-maintainer open source |
| 146 / 206 | Auto-generated code | A–C / A–D | Applies (documents only) | No generated source code. Generated documents (VDD, STR) are controlled in [SCMP §6](../configuration/configuration-management.md#6-generated-outputs) |
| 147 | Reusability requirements | A–D | Applies | [SRS §7](../requirements/requirements.md#7-non-functional-requirements) REQ-PO-044 |
| 154 / 157 / 159 / 207 / 185 / 210 | Cybersecurity risks, protections, secure coding, verification | A–D (210: A–C) | Tailored | SMP §7; [assurance record](../assurance/assurance-record.md) static-analysis and secret-scan entries; ruff and gitleaks run as CI gates |
| 050 / 051 / 053 / 054 / 055 | Requirements | A–D (051: A–C) | Applies | [SRS](../requirements/requirements.md); assurance record requirements analysis |
| 184 | Safety constraints in requirements | A–C | N/A | No hazards ([SRS §8](../requirements/requirements.md#8-not-applicable-categories-and-open-items)) |
| 052 | Bidirectional traceability | A–D | Applies | [Verification matrix](../verification/verification-matrix.md); `tools/check_trace.py` in CI |
| 057 / 058 | Architecture and design | A–C | Applies (voluntary) | [SDD](../architecture/architecture.md); [ICDs](../icd/icd-skill-host.md) |
| 143 | Architecture review | A–C | Tailored | PR review of SDD changes |
| 060 / 061 | Code, coding standards | A–C / A–D | Tailored | [CONTRIBUTING.md](../../CONTRIBUTING.md) and [AGENTS.md](../../AGENTS.md) rules (no code comments, small PRs); ruff 0.17.0 default rules as a CI gate |
| 135 | Static analysis | A–D | Tailored | ruff 0.17.0 (default rules) as a CI gate; security-rule runs by hand, recorded in the assurance record |
| 062 / 186 | Unit test, repeatable | A–D | Applies | [Test plan](../verification/test-plan.md) |
| 063 | Version description | A–D | Applies | [docs/releases](../releases/README.md), generated by `tools/gen_release_docs.py` |
| 136 / 070 | Tool / model accreditation | A–C | Tailored | Tools pinned in [SMP §4](software-management-plan.md#4-engineering-and-test-environment); no accreditation |
| 065 / 066 / 068 / 071 | Test plan, testing, evaluate results, update | A–D | Applies | [docs/verification](../verification/test-plan.md) |
| 187 | CM before test | A–C | Applies | CI runs on committed code |
| 073 | Target platform validation | A–C | Tailored | CI matrix: Python 3.10 and 3.14 on `ubuntu-latest`; agent hosts untested |
| 189 / 190 | Code coverage | A–D / A–C | Tailored | Not measured; no coverage tool pinned; recorded as such in the STR |
| 191 | Regression testing | A–C | Applies | Full suite on every push and PR |
| 192 / 193 | Hazard tests, uplinked data | A–D / A–B | N/A | No hazards; no uplink |
| 211 | Test reused components | A–C | N/A | No vendored code; PyYAML is exercised only through the validator tests |
| 075 / 077 / 194 / 195 / 196 | Operations, delivery, maintenance, retirement | A–D | Tailored | [SMP §11](software-management-plan.md#11-operations-maintenance-and-retirement), VDD |
| 079–085 | Configuration management | A–D | Applies | [SCMP](../configuration/configuration-management.md) |
| 045 | Joint audits | A–C | N/A | No acquirer |
| 086 | Risk management | A–C | Tailored | [SMP §12](software-management-plan.md#12-risk-register) |
| 087 / 088 / 089 | Peer review | A–C | Tailored | [PR template](../../.github/pull_request_template.md); assurance record summary; no effort metrics |
| 090 / 093 / 094 / 199 / 200 | Measurement | A–C (200: A–B) | Tailored | STR metrics block |
| 201 / 202 | Non-conformances, severity | A–D / A–C | Applies | Issues; [SMP §9](software-management-plan.md#9-problem-reporting-and-severity) |
| 203 / 204 | OSS defect assessment, process assessment | A–C / A–B | Tailored | Dependabot PRs reviewed before merge; S1 root-cause note in the issue |

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
| 1.1 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | ruff and gitleaks are now CI gates | this PR |
