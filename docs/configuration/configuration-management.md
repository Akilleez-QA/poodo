# POODO software configuration management plan

| Field | Value |
|---|---|
| Document ID | POODO-SCMP |
| Version | 2.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Organization and responsibilities

The maintainer (`Akilleez-QA`, sole CODEOWNER) approves and merges every change. Agent lanes and Dependabot open pull requests. Cstack owns its own copy of POODO files and re-pins it from upstream; see the [Cstack ICD](../icd/icd-cstack.md).

## 2. Configuration identification

A baseline is a full commit SHA. Branch names and checkout paths are mutable and do not identify a version. No tags exist (`git tag --list` is empty at the baseline commit).

| Item | Identity at baseline | Control point |
|---|---|---|
| Skill method | 3.1 | `SKILL.md` front matter `metadata.version`; the package validator requires `3.1` |
| Continuation capsule schema | POODO_CONTINUATION/3.0 (legacy POODA_CONTINUATION/2.1 accepted) | `scripts/check_capsule.py` `SCHEMA`; literals in `references/continuity-and-ledger.md` checked by the package validator |
| Base evaluation manifest | POODO_EVALS/1 | [manifest.yaml](../../evals/manifest.yaml) |
| Mega Observe manifest | POODO_MEGA_EVALS/1 | [mega-observe.yaml](../../evals/mega-observe.yaml) |
| Run record | POODO_RUN_RECORD/1 | [run-record.template.yaml](../../evals/run-record.template.yaml) |
| Mega Observe charter | POODO_MEGA_OBSERVE_CHARTER/1 | [mega-observe-charter.yaml](../../assets/mega-observe-charter.yaml) |
| Validator dependency | PyYAML==6.0.3 | [requirements-dev.txt](../../requirements-dev.txt) |
| CI Python versions | 3.10 and 3.14 | [checks.yml](../../.github/workflows/checks.yml) |
| Workflow actions | `actions/checkout@v7`, `actions/setup-python@v7` | checks.yml; major-version tags, not commit SHAs |
| Control documents | Each header names its baseline commit | [docs/README.md](../README.md) |

The method version, capsule schema and manifests are separate version axes. Method 3.1 kept capsule schema 3.0. A method version change must update `validate_skill.py` in the same PR.

History note: the repository history was squashed into `36bfe78` ("Initial commit", 2026-10-30) after PRs #1–#15 merged. Commits cited by earlier versions of these documents (`01e6c60`, `4f47a9d`) are not in this history.

### 2.1 Byte identities

Generated with `sha256sum` at the baseline commit; the VDD for each baseline regenerates the same table with `tools/gen_release_docs.py`.

| File | SHA-256 |
|---|---|
| `SKILL.md` | `f89da350367ba102138e197aee51a23b6dd06d17c5cce9b4829c47e7953cce99` |
| `agents/openai.yaml` | `b69e08206ae75a1327bc9142770833c7992ee8091f43e736f48092fbbe9e7a5e` |
| `assets/mega-observe-charter.yaml` | `500fdcc902a7e877bd9c8d26f775a5ff7efe0624e0f53cc10dcbf94ef05a5ea3` |
| `requirements-dev.txt` | `0969da99a0bc2a1b71ed50584560f4588a37567ac63af3ddbaf3c4617ca5621a` |
| `scripts/check_capsule.py` | `a8dde2ffa2c45acdd600e9a02a4baa942c18244d3c7f5cd5048654a14d439e7f` |
| `scripts/validate_skill.py` | `c192718ea7e1233cf0ce663fef4631ddcc9b1f033ff104b4deb0e56082518a3e` |
| `evals/manifest.yaml` | `9b060ef34bd740e8ce478d831aa83f1589d8ecda332f49945b835f4b71bba593` |
| `evals/mega-observe.yaml` | `8d90591ee9aeaa0199c49f4ca3fb3c82ba17e0b67c99e972acd9d065a1bfc284` |
| `evals/protocol.md` | `6ff35454bf3a514063d727bd19656aca2803831d8b69d341317cca7fab30d9a3` |
| `evals/rubric.md` | `155a96e0e4ee2590cfd5309f637c23114bb65254fc2a81779af1f4615624970e` |
| `evals/run-record.template.yaml` | `56fd0364998f12bf8a486bca9dc397a5b1c305cd551be93b706fa42ff7621ab0` |

Command: `git show b969150:<file> | sha256sum` for each file.

## 3. Change control

- Every change goes through a pull request to `main`. The maintainer merges after CI passes.
- `main` has no branch protection and no rulesets (`gh api repos/Akilleez-QA/poodo/branches/main/protection` returns 404 "Branch not protected"; the rulesets endpoint returns an empty list). Review discipline is procedural, not enforced.
- CI ([checks.yml](../../.github/workflows/checks.yml)) runs on every push, every pull request and on manual dispatch, with read-only `contents` permission.
- Dependabot opens weekly update PRs for GitHub Actions and pip, at most three open per ecosystem.
- Follow [CONTRIBUTING.md](../../CONTRIBUTING.md) for reproductions and behavioral evidence. Keep method text, metadata, references and checker assumptions consistent in one PR.

## 4. Status accounting

- [CHANGELOG.md](../../CHANGELOG.md) (Keep a Changelog style) records 3.0.0 and 3.1.0 (both dated 2026-10-01) and an Unreleased section. Its headings use three-component versions; SKILL.md metadata uses two (`3.1`). No tags correspond to either heading.
- Version descriptions and test reports are indexed in [docs/releases/README.md](../releases/README.md).
- Cstack's pin of this repository is recorded on the Cstack side (`contracts/SOURCE-PINS.json`, key `poodo_skill`).

## 5. Configuration audits

At each documentation baseline or release, record in the [assurance record](../assurance/assurance-record.md): docs baseline commit versus the code it describes (`git log <baseline>..HEAD -- <derivation paths>` must be empty), the byte table above versus the files, and the VDD versus the tree.

## 6. Generated outputs

| Output | Generator | Inputs | Committed | Rule |
|---|---|---|---|---|
| `docs/releases/VDD-<label>.md` | `tools/gen_release_docs.py` | git, CHANGELOG, product files, `gh` | yes | Do not edit by hand; rerun |
| `docs/verification/reports/STR-<label>.md` | `tools/gen_release_docs.py` | the five CI suites, trace check, `gh` | yes | Do not edit by hand; rerun |
| §2.1 byte table | `sha256sum` (command recorded above) | product files | yes | Regenerate when a listed file changes |

No source code is generated.

## 7. Release management and delivery

No release or tag has been created. Delivery is `git clone` of a chosen commit into the host's skill directory ([Getting started](../guides/tutorials/getting-started.md)). To cut a release:

1. Choose the method and schema versions and a reviewed commit. Reconcile SKILL.md metadata, the validator's version check, docs and CHANGELOG.
2. Run TP-1 in the [test plan](../verification/test-plan.md) on both Python versions. Record any behavioral study separately from structural results.
3. Re-inspect the Cstack pin when integration changes; record gaps rather than inferring compatibility from version numbers.
4. Generate the VDD and STR with TP-3 and index them.
5. The maintainer reviews the exact commit and evidence before tagging. Consumers keep the selected commit and their host configuration as their baseline and preserve local edits before updating.

## 8. Plan maintenance

Update this plan in the same PR as any change to versions, pins, CI, release steps or generated outputs.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-10-30 | squashed into `36bfe78` | Version axes, pins, baselines and a future release checklist | PR #13 |
| 2.0 | 2026-11-08 | `b969150` | Family format; corrected stale action pins (v4/v5 → v7) and CHANGELOG version form; replaced unreachable baseline commits; added byte table, change control facts, generated outputs and audit steps | this PR |
