# Documentation

[SKILL.md](../SKILL.md) is the authoritative agent contract. The documents below organize its supporting material and its engineering records. Structural checks and synthetic examples do not establish behavioral improvement.

Control documents carry their own baseline commits. Reading or indexing them does not create a new verification result. Classification: self-assessed Class E analog, not safety-critical; this is not a NASA compliance determination or certification (see the [software management plan](plan/software-management-plan.md#1-software-classification-self-assessed)).

## Start here

| Need | Document |
|---|---|
| Install and invoke POODO for the first time | [Getting started](guides/tutorials/getting-started.md) |
| Run the local checks or prepare a behavioral study | [Evaluation and verification](guides/how-to/evaluation.md) |
| Look up commands, exit codes, fields and source material | [Reference guide](guides/reference/README.md), [command reference](guides/reference/cli.md) |
| Understand the loop and its evidence distinctions | [How POODO works](guides/explanation/how-it-works.md) |
| Know what POODO does not do | [Limitations and safety-relevant use](guides/explanation/limitations.md) |
| See what is proposed next | [Roadmap](guides/explanation/roadmap.md) |
| Find where each user-manual topic lives | [User manual map](guides/SUM-MAP.md) |

## Control documents

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

## Other source material

- [Reference library](../references/) for phase-specific instructions.
- [Examples](../examples/README.md) for synthetic scenarios.
- [Contributing](../CONTRIBUTING.md), [Security](../SECURITY.md) and [Support](../SUPPORT.md) for participation and reporting.
