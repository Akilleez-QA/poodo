# Changelog

## [Unreleased]

Tooling and evaluation-rule fixes.

### Added

- Add root coding-agent guidance and weekly Dependabot checks for GitHub Actions and Python dependencies, with up to three open PRs per ecosystem.
- Engineering records organized after NASA documentation guidance (self-assessed Class E analog, not safety-critical; not a NASA compliance determination): software management plan, compliance matrix, data dictionary, test plan, assurance record, skill-host and capsule-checker interface documents, limitations page, command reference, user manual map, and a generated version description and test report.
- Requirements REQ-PO-022 to REQ-PO-044 for the validators, each traced to a test or listed as an untested gap.
- `tools/check_trace.py`, run in CI: fails on an untraced requirement, a missing or untraced test, an unregistered gap, or a dead link. `tools/gen_release_docs.py` generates the version description and test report.
- Problem-report and change-request issue templates (the bug template became the problem report); the pull request template now records the peer review.
- `evals/test_validate_skill.py`: failure-path tests for the package validator, run against a temporary copy of the package. Capsule-checker tests for duplicate keys, the root field set, lineage, record identity and resolution, invalidated dependencies and head kind, per-record fields, `--hard-token-ceiling`, out-of-set strings, `outcomes[].depends_on` and exit 2 on unreadable or non-UTF-8 files. Untested gaps UG-22 to UG-37 are closed.
- CI gates: ruff 0.17.0 (default rules) and a gitleaks 8.28.0 scan of the full git history, with the gitleaks download checked against its published SHA-256.

### Changed

- Rubric: define N/A via a per-case `not_applicable` manifest field frozen before scoring.
- README rewritten for first-time readers: a guided-versus-unguided example built from an evaluation case, a flow diagram, real checker output, and Codex install steps checked on a throwaway home folder. The loop pseudocode, its specification table and the Mega Observe section moved to [How POODO works](docs/guides/explanation/how-it-works.md). The documentation index now leads with reader tasks and lists the engineering records last.
- CI: `actions/checkout` v4 → v7 and `actions/setup-python` v5 → v7 (Dependabot).
- Requirements, design, verification matrix, configuration and Cstack interface documents re-baselined to commits in this history; the Cstack interface is re-pinned to current Cstack main.

### Fixed

- Capsule checker: an oversize capsule now passes the size check only when it declares a non-empty `capsule_overflow`, matching the method's soft ceiling. Add regression tests.
- Capsule checker: `objective`, `next_step`, the three terminal-claim fields and claim text no longer pass when null, `[]` or `{}`. A duplicate record ID is reported against the same record whatever the hash seed.
- Package validator: removing the opening `POODO_CONTINUATION_V3_0` marker is now reported (it was matched inside the `END_` marker). A non-mapping `metadata`, a non-string `default_prompt` or `short_description`, and a non-UTF-8 file are reported instead of raising a traceback.

No change to the method text or skill version.

## [3.1.0] - 2026-10-01

Optional Mega Observe.

### Added

- Add an explicit expensive research mode targeting 200 distinct categories and 200 distinct evaluations per category.
- Define provenance, semantic-distinctness review, budget reservations, checkpoints, and incomplete-run reporting.
- Add a prospective charter, invocation example, and eight unexecuted protocol probes.

### Changed

- Preserve the standard loop and the 3.0 continuation schema.

No full Mega Observe run or measured improvement is claimed. The mode is a host-executed protocol; no paid runner or billing enforcement service is bundled.

## [3.0.0] - 2026-10-01

Initial public project.

### Added

- Package the existing POODO 3.0 method, references, and Codex metadata.
- Add installation and concept guides, synthetic examples, contributor guidance, and a roadmap.
- Document the 14-case behavioral manifest and its unmeasured status; add a run-record template.
- Declare PyYAML and automate structural checks and checker regressions with GitHub Actions.

### Fixed

- Harden capsule timestamp and malformed-input handling with targeted regression coverage.

This is a packaging and tooling milestone. It does not assert behavioral improvement over a baseline.
