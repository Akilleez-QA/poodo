# Configuration management

## Baseline

The source baseline for this document is poodo commit `4f47a9d67a1382e219bc1850107648eacfc541b8`. The [Cstack ICD](../icd/icd-cstack.md) pins the counterpart separately. A branch name or mutable checkout path is not a reproducible version identifier.

| Item | Observed version or pin | Source |
| --- | --- | --- |
| Skill method | 3.1 | [SKILL.md](../../SKILL.md) metadata |
| Continuation capsule | POODO_CONTINUATION/3.0 | [check_capsule.py](../../scripts/check_capsule.py), [continuity contract](../../references/continuity-and-ledger.md) |
| Base evaluation manifest | POODO_EVALS/1 | [manifest.yaml](../../evals/manifest.yaml) |
| Mega Observe manifest | POODO_MEGA_EVALS/1 | [mega-observe.yaml](../../evals/mega-observe.yaml) |
| Validator dependency | PyYAML==6.0.3 | [requirements-dev.txt](../../requirements-dev.txt) |
| CI Python versions | 3.10 and 3.14 | [checks.yml](../../.github/workflows/checks.yml) |
| Workflow actions | actions/checkout@v4, actions/setup-python@v5 | checks.yml; major-version references rather than immutable commit pins |

The skill version, capsule schema and behavioral manifests are separate version axes. The 3.1 method addition retains the 3.0 capsule schema. The package validator currently checks method metadata against 3.1; a version change must account for that check.

## Versioning and release state

[CHANGELOG.md](../../CHANGELOG.md) records 3.0, 3.1 and unreleased tooling/evaluation-rule fixes. It uses two-component method versions; the repository does not currently define a three-component SemVer release policy. `git tag --list` returned no tags in the fresh clone at the baseline. The inspected workflow runs checks rather than publishing releases.

For a future SemVer policy, distinguish a public-contract break (major), a compatible addition (minor), and a compatible correction (patch), and choose an explicit mapping from existing 3.1 metadata to a three-component release version. This is a proposed release convention, not an assertion that existing metadata or tags follow it. This documentation change creates no release or tag and changes no version.

## Controlled changes

Keep method text, metadata, references and checker assumptions consistent when changing a contract. Keep schema changes explicit and preserve the interpretation of historical records. Follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for reproductions and behavioral evidence.

Record the exact commit and dependency versions for local verification. Re-run the package validator, checker regression suite and named capsule fixture after relevant changes; record command, environment, result and limits in the [verification matrix](../verification/verification-matrix.md). A structural pass cannot replace a behavioral study.

Before behavioral trials, freeze the baseline/candidate, model/configuration, permissions, manifest, grading rules and acceptance thresholds in the [run-record template](../../evals/run-record.template.yaml). Keep raw runs in ignored `evals/runs/` until reviewed for intentional publication. Do not commit credentials or private traces.

## Future release and tag checklist

This checklist describes review inputs for a maintainer; it does not authorize publication or claim an existing automated process.

1. Choose the intended method/schema versions and a reviewed source commit. Reconcile package metadata, checker version assumptions, documentation and changelog.
2. Install the pinned development dependency in an isolated environment and run the commands documented in the verification matrix. Record any behavioral study separately from structural results.
3. Reinspect counterpart pins and contract versions in the ICD when integration changes. Record compatibility gaps rather than inferring compatibility from version numbers.
4. Have the maintainer review the exact source commit and evidence before any release or tag decision. Release/tag creation is outside this documentation rollout.
5. Consumers should retain the selected source commit and their actual host configuration as a baseline. Preserve local edits before updating, following [Getting started](../getting-started.md).
