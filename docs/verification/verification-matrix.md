# Verification matrix

## Baseline and interpretation

Requirements: [REQ-PO-001 through REQ-PO-021](../requirements/requirements.md). All rows refer to poodo source commit `4f47a9d67a1382e219bc1850107648eacfc541b8` (baseline P). These results are local checks of that commit; the documentation files in this PR do not change executable sources.

No behavioral trial was run. Existing probes are prospective coverage, not passing evidence. A gap means the current manifests do not directly verify the full requirement; this PR does not add cases or alter expected results.

## Executed structural checks

Environment: Python 3.14.8, PyYAML 6.0.3. Commands ran from the checkout root against baseline P.

| ID | Command | Result | Commit |
| --- | --- | --- | --- |
| S1 | `python3 scripts/validate_skill.py` | Passed selected package checks; behavior untested | P |
| S2 | `python3 -m unittest discover -s evals -p 'test_*.py' -v` | 13 checker regression tests passed | P |
| S3 | `python3 scripts/check_capsule.py evals/fixtures/valid-capsule.yaml` | Passed capsule structural checks; evidence truth untested | P |

S2 includes malformed fields, timestamp handling, overflow, failed-prediction resurrection and truncated evidence cases in [test_check_capsule.py](../../evals/test_check_capsule.py). A checker regression pass establishes only the assertions of those named tests.

## Requirement traceability

Base cases are in [manifest.yaml](../../evals/manifest.yaml); Mega cases are in [mega-observe.yaml](../../evals/mega-observe.yaml). For any listed behavioral case, the method is a recorded trial and grading under [protocol.md](../../evals/protocol.md) and [rubric.md](../../evals/rubric.md), not a Python test command. The repo has no automated agent runner.

| Requirement | Test file, case or command | Result and remaining boundary | Commit |
| --- | --- | --- | --- |
| REQ-PO-001 | S1; base case `proportional-low-stakes` | Metadata inspected and structurally checked; scope-routing trial unexecuted; no dedicated implicit-invocation case. | P |
| REQ-PO-002 | Base: `structural-pass-outcome-fail`, `summary-echo` | Unexecuted; partial coverage of claim-state distinctions. | P |
| REQ-PO-003 | Base: `circular-validator`, `summary-echo`; Mega: `mega-syndicated-sources` | Unexecuted; targeted evidence-independence probes. | P |
| REQ-PO-004 | Base: `proxy-as-outcome`, `structural-pass-outcome-fail`, `favorable-invalid-environment` | Unexecuted; targeted proxy and outcome probes. | P |
| REQ-PO-005 | Base: `weak-rival-theater` | Unexecuted; no dedicated critic-availability probe. | P |
| REQ-PO-006 | Base: `post-hoc-criterion`, `genuinely-invalid-environment` | Unexecuted; partial precommitment coverage, not a complete field/timing test. | P |
| REQ-PO-007 | Base: `structural-pass-outcome-fail`, `genuinely-invalid-environment`, `post-hoc-criterion` | Unexecuted contradiction probes. | P |
| REQ-PO-008 | Base: `authority-after-compaction`; Mega: `mega-no-budget`, `mega-inflight-budget` | Unexecuted authority probes. | P |
| REQ-PO-009 | S2; S3; base: `summary-echo`, `conflicting-capsule-branches`, `mutable-path`, `interrupted-tool-result`, `repeated-compaction-loss` | S2/S3 passed only structural checks and checker cases; resume and fork behavior unexecuted. | P |
| REQ-PO-010 | No dedicated behavioral case in either manifest | Coverage gap: research-enabled/unavailable trials and source-quality grading needed. | P |
| REQ-PO-011 | No dedicated behavioral case in either manifest | Coverage gap: exactly 20 semantic paths and pre-ranking order need a trial. | P |
| REQ-PO-012 | No dedicated behavioral case in either manifest | Coverage gap: opening exchange, waiver and decompression need trials. | P |
| REQ-PO-013 | No dedicated behavioral case in either manifest | Coverage gap: transition spikes, distinct assignments and reconciliation need trials. | P |
| REQ-PO-014 | No dedicated behavioral case in either manifest | Coverage gap: topology traversal and bounded saturation need trials. | P |
| REQ-PO-015 | No dedicated behavioral case in either manifest | Coverage gap: native goal binding and unsupported-tool boundaries need trials. | P |
| REQ-PO-016 | No complete-loop behavioral case in either manifest | Coverage gap: phase order, composed decision, reversal conditions and learning need a full trace. | P |
| REQ-PO-017 | Mega: `mega-no-budget`, `mega-inflight-budget` | Unexecuted; no dedicated probe for unrequested optional-mode activation. | P |
| REQ-PO-018 | Mega: `mega-padding-pressure`, `mega-full-counter-empty-content`, `mega-unknown-is-not-finding`, `mega-taxonomy-resume`, `mega-internet-completeness` | Unexecuted protocol probes; no full run or post-Mega 20-path trial. | P |
| REQ-PO-019 | S1; inspect SKILL.md routing and referenced files | Selected Markdown references passed S1; conditional consultation and operation selection unexecuted. | P |
| REQ-PO-020 | S2/S3 structural fields; base: `proxy-as-outcome`, `structural-pass-outcome-fail`, `favorable-invalid-environment` | Structural subset passed; behavioral probes unexecuted; no full terminal-field trial. | P |
| REQ-PO-021 | Base: `proportional-low-stakes`; inspect SKILL.md stopping rules | Unexecuted; resolve the documented scope-routing interpretation before grading. | P |

## Behavioral verification procedure

Before trials, freeze baseline and candidate commits, model/configuration, permissions, cases, rubric applicability and acceptance thresholds. Keep grader-only expectations out of evaluated prompts. Use at least three independent trials per case and variant, randomize order, blind graders, and preserve failures and disagreement. Continuity cases require at least three lossy summarize/resume cycles.

The evaluation guide records a conflict between the low-stakes case and mandatory full-loop research. Freeze its scope-routing interpretation prospectively. Public development cases do not establish generalization; add held-out evidence before making that claim. See [Evaluation](../guides/how-to/evaluation.md) for the existing procedure and limitations.
