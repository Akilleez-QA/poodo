# POODO user manual map

| Field | Value |
|---|---|
| Document ID | POODO-SUM-MAP |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

The user manual (SWEHB 5.12) is the README plus the guides. This map shows where each element lives.

| SUM element | Where | Verified how |
|---|---|---|
| Application summary and intended users | [README](../../README.md) intro and [Status and limitations](../../README.md#status-and-limitations) | Claims checked against the tree at the baseline |
| Inventory (what is shipped) | [README What's inside](../../README.md#whats-inside); [VDD](../releases/README.md) | VDD generated |
| Environment and prerequisites | [Getting started: Requirements](tutorials/getting-started.md#requirements) | Inspection |
| Modes and states of operation | [How POODO works](explanation/how-it-works.md); [How POODO works: Mega Observe](explanation/how-it-works.md#mega-observe-expensive) | Inspection against SKILL.md |
| Security and privacy | [SECURITY.md](../../SECURITY.md); [limitations](explanation/limitations.md#misuse-and-security-considerations) | Inspection |
| Assistance and problem reporting | [SUPPORT.md](../../SUPPORT.md); [problem report](../../.github/ISSUE_TEMPLATE/problem-report.md) and [change request](../../.github/ISSUE_TEMPLATE/change-request.md) templates | Inspection |
| First-time use | [Getting started](tutorials/getting-started.md) | Package-check commands run on 2026-11-08 at the baseline; the agent invocation needs a host and was not run |
| Starting, stopping, suspending | [Getting started: First use, Updates and removal](tutorials/getting-started.md#updates-and-removal); continuation in [how it works](explanation/how-it-works.md#across-sessions) | Inspection |
| Capabilities and commands reference | [Reference index](reference/README.md); [command reference](reference/cli.md) | Help text captured from `--help` |
| Conventions (IDs, file layout) | [Data dictionary](../data/data-dictionary.md); [README What's inside](../../README.md#whats-inside) | Trace check asserts every capsule field is in the data dictionary |
| Processing procedures | [Evaluation and verification](how-to/evaluation.md) | Commands run at the baseline |
| Data backup and recovery from errors | [Getting started: Updates and removal](tutorials/getting-started.md#updates-and-removal) (preserve local edits; keep ledgers separately) | Inspection |
| Messages, errors and exit codes | [Command reference](reference/cli.md) | Messages copied from the scripts; example runs captured |
| Assumptions and limitations | [README Status and limitations](../../README.md#status-and-limitations); [limitations](explanation/limitations.md) | Inspection |
| Safety-related constraints | [Limitations: safety, engineering or regulated decisions](explanation/limitations.md#use-in-safety-engineering-or-regulated-decisions) | Inspection |
| Version-specific changes | [CHANGELOG](../../CHANGELOG.md); [releases](../releases/README.md) | VDD generated |

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
| 1.0 | 2026-11-08 | docs/reader-first | Link targets follow the rewritten README and the moved Mega Observe section; no element moved | docs/reader-first PR |
