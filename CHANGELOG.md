# Changelog

## [Unreleased]

Tooling and evaluation-rule fixes.

### Added

- Add root coding-agent guidance and weekly Dependabot checks for GitHub Actions and Python dependencies, with up to three open PRs per ecosystem.

### Changed

- Rubric: define N/A via a per-case `not_applicable` manifest field frozen before scoring.

### Fixed

- Capsule checker: an oversize capsule now passes the size check only when it declares a non-empty `capsule_overflow`, matching the method's soft ceiling. Add regression tests.

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
