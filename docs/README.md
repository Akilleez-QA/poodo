# POODO documentation

POODO is an agent skill that makes a coding agent show its evidence before it acts. [SKILL.md](../SKILL.md) is the skill itself, and it is the authority whenever a guide disagrees with it. New here? Start with the [project README](../README.md).

## Learn

| If you want to | Read |
|---|---|
| Install POODO and make your first request | [Getting started](guides/tutorials/getting-started.md) |
| See what a POODO-guided answer looks like | [README example](../README.md#what-changes) and the [examples](../examples/README.md) (hand-written, not measured runs) |

## Do

| If you want to | Read |
|---|---|
| Run the package and capsule checks | [Evaluation and verification](guides/how-to/evaluation.md) |
| Design or run a behavioral study | [Evaluation and verification](guides/how-to/evaluation.md), [evaluation protocol](../evals/protocol.md), [rubric](../evals/rubric.md) |
| Plan a Mega Observe run (expensive, optional) | [Mega Observe protocol](../references/mega-observe.md), [charter template](../assets/mega-observe-charter.yaml), [example](../examples/mega-observe.md) |
| Contribute a change | [CONTRIBUTING.md](../CONTRIBUTING.md) |

## Look up

| If you want to | Read |
|---|---|
| Checker commands, messages and exit codes | [Command reference](guides/reference/cli.md) |
| Capsule fields and allowed values | [Data dictionary](data/data-dictionary.md) |
| The stage-by-stage instructions the agent loads | [Reference library](../references/), indexed in the [reference guide](guides/reference/README.md) |
| How POODO talks to an agent host | [Skill host interface](icd/icd-skill-host.md) |

## Understand

| If you want to | Read |
|---|---|
| Why the loop is shaped this way, the loop in pseudocode, and where each step is specified | [How POODO works](guides/explanation/how-it-works.md) |
| What POODO does not do, and safety-relevant use | [Limitations](guides/explanation/limitations.md) |
| What is proposed next | [Roadmap](guides/explanation/roadmap.md) |

## Help and reporting

[SUPPORT.md](../SUPPORT.md) for questions, [SECURITY.md](../SECURITY.md) for vulnerabilities, and the [problem report](../.github/ISSUE_TEMPLATE/problem-report.md) and [change request](../.github/ISSUE_TEMPLATE/change-request.md) templates for issues.

## Engineering records

These are POODO's requirements, design, interface and verification records, organized after NASA software documentation guidance. Classification: self-assessed Class E analog under NPR 7150.2D, not safety-critical; this is not a NASA compliance determination or certification (see the [software management plan](plan/software-management-plan.md#1-software-classification-self-assessed)). Each control document carries its own baseline commit; reading or indexing it does not create a new verification result.

This is a skill/tool repository, so the software management plan also holds the maintenance, assurance and risk plans, and the test plan also holds the test procedures.

| Document | ID | SWEHB | Path |
|---|---|---|---|
| Software management plan | POODO-SMP | 5.08, 5.04, 5.17, 5.27 | [plan/software-management-plan.md](plan/software-management-plan.md) |
| Requirements mapping matrix | POODO-RMM | 7.16 | [plan/compliance-matrix.md](plan/compliance-matrix.md) |
| Requirements | POODO-SRS | 5.09 | [requirements/requirements.md](requirements/requirements.md) |
| Design | POODO-SDD | 5.13 | [architecture/architecture.md](architecture/architecture.md) |
| Interface: skill host | POODO-ICD-HOST | 5.02 | [icd/icd-skill-host.md](icd/icd-skill-host.md) |
| Interface: capsule checker | POODO-ICD-CAPSULE | 5.02 | [icd/icd-capsule-checker.md](icd/icd-capsule-checker.md) |
| Interface: Cstack | POODO-ICD-CSTACK | 5.02 | [icd/icd-cstack.md](icd/icd-cstack.md) |
| Data dictionary | POODO-DD | 5.07 | [data/data-dictionary.md](data/data-dictionary.md) |
| Test plan and procedures | POODO-STP | 5.10, 5.14 | [verification/test-plan.md](verification/test-plan.md) |
| Verification matrix | POODO-VM | SWE-052 | [verification/verification-matrix.md](verification/verification-matrix.md) |
| Test reports | POODO-STR-* | 5.11, 5.05 | [verification/reports/](verification/reports/README.md) |
| Configuration management | POODO-SCMP | 5.06 | [configuration/configuration-management.md](configuration/configuration-management.md) |
| Version descriptions | POODO-VDD-* | 5.16 | [releases/](releases/README.md) |
| Assurance record | POODO-SAR | 5.21–5.23, 5.25, 5.26 | [assurance/assurance-record.md](assurance/assurance-record.md) |
| User manual map | POODO-SUM-MAP | 5.12 | [guides/SUM-MAP.md](guides/SUM-MAP.md) |
| Documentation checklist | — | 5.03 | [rules/documentation-checklist.md](rules/documentation-checklist.md) |

Not applicable (rationale in the SMP and compliance matrix): training plan (5.15), safety plan (5.18), assurance status report (5.19), IV&V plan (5.20), hazard report (5.24; replaced by the [limitations page](guides/explanation/limitations.md)).

`python tools/check_trace.py` checks the requirement trace and every relative link in the repository's Markdown on each CI run.
