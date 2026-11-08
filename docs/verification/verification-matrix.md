# POODO verification matrix

| Field | Value |
|---|---|
| Document ID | POODO-VM |
| Version | 2.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## How to read this matrix

Each requirement in the [SRS](../requirements/requirements.md) has one row. Columns:

- **Method**: T test, A analysis, I inspection, D demonstration.
- **Verified by**: `file::Class.method` is an automated test; `ci: <command>` is a step in [checks.yml](../../.github/workflows/checks.yml); `inspect: <path>` is a named inspection target; `evals/<manifest>#<case>` is a behavioral case that has been designed but never run.
- **Coverage**: Full means the listed automated evidence checks the whole statement. Partial means part of it is checked. None means nothing automated checks it. Partial and None rows must name a gap in the [untested requirement gaps](#untested-requirement-gaps) table.
- **Last result**: the test report that holds the run. "No trial recorded" means no agent trial exists for that case.

Trace check: `python tools/check_trace.py` enforces these rules on every CI run. It fails on a requirement with no row, a reference to a missing test, case or CI step, a Full row with no automated evidence, a Partial or None row with no registered gap, and a test that traces to nothing.

Behavioral cases are prospective. A listed case is not a passing result. The repository has no automated agent runner, so behavioral rows stay at None or Partial until a recorded, graded trial exists.

## Requirement traceability

| Requirement | Method | Verified by | Coverage | Gap | Last result |
| --- | --- | --- | --- | --- | --- |
| REQ-PO-001 | I, T | `inspect: agents/openai.yaml`; `ci: python scripts/validate_skill.py`; `evals/manifest.yaml#proportional-low-stakes` | Partial | UG-01 | Metadata: [STR](reports/README.md); trial: no trial recorded |
| REQ-PO-002 | T | `evals/manifest.yaml#structural-pass-outcome-fail`; `evals/manifest.yaml#summary-echo` | None | UG-02 | No trial recorded |
| REQ-PO-003 | T | `evals/manifest.yaml#circular-validator`; `evals/manifest.yaml#summary-echo`; `evals/mega-observe.yaml#mega-syndicated-sources` | None | UG-03 | No trial recorded |
| REQ-PO-004 | T | `evals/manifest.yaml#proxy-as-outcome`; `evals/manifest.yaml#structural-pass-outcome-fail`; `evals/manifest.yaml#favorable-invalid-environment` | None | UG-04 | No trial recorded |
| REQ-PO-005 | T | `evals/manifest.yaml#weak-rival-theater` | None | UG-05 | No trial recorded |
| REQ-PO-006 | T | `evals/manifest.yaml#post-hoc-criterion`; `evals/manifest.yaml#genuinely-invalid-environment` | None | UG-06 | No trial recorded |
| REQ-PO-007 | T | `evals/manifest.yaml#structural-pass-outcome-fail`; `evals/manifest.yaml#genuinely-invalid-environment`; `evals/manifest.yaml#post-hoc-criterion` | None | UG-07 | No trial recorded |
| REQ-PO-008 | T | `evals/manifest.yaml#authority-after-compaction`; `evals/mega-observe.yaml#mega-no-budget`; `evals/mega-observe.yaml#mega-inflight-budget` | None | UG-08 | No trial recorded |
| REQ-PO-009 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule`; `evals/manifest.yaml#summary-echo`; `evals/manifest.yaml#conflicting-capsule-branches`; `evals/manifest.yaml#mutable-path`; `evals/manifest.yaml#interrupted-tool-result`; `evals/manifest.yaml#repeated-compaction-loss` | Partial | UG-09 | Structure: [STR](reports/README.md); trial: no trial recorded |
| REQ-PO-010 | T | none designed | None | UG-10 | No trial recorded |
| REQ-PO-011 | T | none designed | None | UG-11 | No trial recorded |
| REQ-PO-012 | T | none designed | None | UG-12 | No trial recorded |
| REQ-PO-013 | T | none designed | None | UG-13 | No trial recorded |
| REQ-PO-014 | T | none designed | None | UG-14 | No trial recorded |
| REQ-PO-015 | T | none designed | None | UG-15 | No trial recorded |
| REQ-PO-016 | T | none designed | None | UG-16 | No trial recorded |
| REQ-PO-017 | T | `evals/mega-observe.yaml#mega-no-budget`; `evals/mega-observe.yaml#mega-inflight-budget` | None | UG-17 | No trial recorded |
| REQ-PO-018 | T | `evals/mega-observe.yaml#mega-padding-pressure`; `evals/mega-observe.yaml#mega-full-counter-empty-content`; `evals/mega-observe.yaml#mega-unknown-is-not-finding`; `evals/mega-observe.yaml#mega-taxonomy-resume`; `evals/mega-observe.yaml#mega-internet-completeness` | None | UG-18 | No trial recorded |
| REQ-PO-019 | I, T | `ci: python scripts/validate_skill.py`; `inspect: SKILL.md` | Partial | UG-19 | Links: [STR](reports/README.md); trial: no trial recorded |
| REQ-PO-020 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule`; `evals/manifest.yaml#proxy-as-outcome`; `evals/manifest.yaml#structural-pass-outcome-fail`; `evals/manifest.yaml#favorable-invalid-environment` | Partial | UG-20 | Fields: [STR](reports/README.md); trial: no trial recorded |
| REQ-PO-021 | T | `evals/manifest.yaml#proportional-low-stakes`; `inspect: SKILL.md` | None | UG-21 | No trial recorded |
| REQ-PO-022 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-28 | Positive path: [STR](reports/README.md) |
| REQ-PO-023 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-29 | Positive path: [STR](reports/README.md) |
| REQ-PO-024 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-30 | Positive path: [STR](reports/README.md) |
| REQ-PO-025 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-31 | Positive path: [STR](reports/README.md) |
| REQ-PO-026 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-32 | Positive path: [STR](reports/README.md) |
| REQ-PO-027 | T | `ci: python scripts/validate_skill.py` (positive path only) | None | UG-33 | Positive path: [STR](reports/README.md) |
| REQ-PO-028 | D | `ci: python scripts/validate_skill.py` | Full | — | [STR](reports/README.md) |
| REQ-PO-029 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_failed_prediction_resurrection`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_nonstring_mapping_keys`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_impossible_dates_and_offsets` | Partial | UG-37 | [STR](reports/README.md) |
| REQ-PO-030 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_reference_collections`; `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_scalar_references`; `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_contradiction_references` | Partial | UG-36 | [STR](reports/README.md) |
| REQ-PO-031 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_unhashable_enum_values` | Partial | UG-35 | [STR](reports/README.md) |
| REQ-PO-032 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_impossible_dates_and_offsets`; `evals/test_check_capsule.py::CapsuleLinterTests.test_accepts_real_rfc3339_dates`; `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule` | Full | — | [STR](reports/README.md) |
| REQ-PO-033 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_nonstring_mapping_keys` | Full | — | [STR](reports/README.md) |
| REQ-PO-034 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_oversize_capsule_rejected_without_overflow`; `evals/test_check_capsule.py::CapsuleLinterTests.test_declared_overflow_allows_oversize_capsule`; `evals/test_check_capsule.py::CapsuleLinterTests.test_empty_overflow_does_not_waive_ceiling` | Partial | UG-34 | [STR](reports/README.md) |
| REQ-PO-035 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_failed_prediction_resurrection` | Full | — | [STR](reports/README.md) |
| REQ-PO-036 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_truncated_evidence` | Full | — | [STR](reports/README.md) |
| REQ-PO-037 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule` | Full | — | [STR](reports/README.md) |
| REQ-PO-038 | T | none | None | UG-22 | — |
| REQ-PO-039 | T | none (positive path via test_valid_capsule only) | None | UG-23 | — |
| REQ-PO-040 | T | none (positive path via test_valid_capsule only) | None | UG-24 | — |
| REQ-PO-041 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_reference_collections` | Partial | UG-25 | [STR](reports/README.md) |
| REQ-PO-042 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_scalar_references` | Partial | UG-26 | [STR](reports/README.md) |
| REQ-PO-043 | T | none (positive path via test_valid_capsule only) | None | UG-27 | — |
| REQ-PO-044 | I, D | `inspect: requirements-dev.txt`; `ci: python -m pip install -r requirements-dev.txt` | Full | — | [STR](reports/README.md) |

## Untested requirement gaps

Each gap is a behavior the software or the skill is meant to have that no automated test or recorded trial checks. Gaps are listed, not hidden. Closing one means adding a test or a recorded trial and updating the row in the same PR.

| Gap | Requirement | Missing evidence |
| --- | --- | --- |
| UG-01 | REQ-PO-001 | No trial of explicit-invocation scope routing. No case for implicit invocation |
| UG-02 | REQ-PO-002 | No recorded trial of claim-state separation |
| UG-03 | REQ-PO-003 | No recorded trial of evidence-independence probes |
| UG-04 | REQ-PO-004 | No recorded trial of proxy-versus-outcome probes |
| UG-05 | REQ-PO-005 | No recorded trial. No case for critic availability |
| UG-06 | REQ-PO-006 | No recorded trial. No case checks every precommitment field and its timing |
| UG-07 | REQ-PO-007 | No recorded contradiction trial |
| UG-08 | REQ-PO-008 | No recorded authority trial |
| UG-09 | REQ-PO-009 | Capsule structure is tested. Resume, fork and evidence rechecking have no recorded trial |
| UG-10 | REQ-PO-010 | No case in either manifest for the research gate |
| UG-11 | REQ-PO-011 | No case in either manifest for the 20-path rule |
| UG-12 | REQ-PO-012 | No case in either manifest for the opening exchange, waiver or decompression |
| UG-13 | REQ-PO-013 | No case in either manifest for transition spikes and reconciliation |
| UG-14 | REQ-PO-014 | No case in either manifest for topology traversal and bounded saturation |
| UG-15 | REQ-PO-015 | No case in either manifest for native-goal binding |
| UG-16 | REQ-PO-016 | No complete-loop case in either manifest |
| UG-17 | REQ-PO-017 | No recorded trial. No case for unrequested activation of the optional mode |
| UG-18 | REQ-PO-018 | No recorded trial. No full run and no post-Mega 20-path trial |
| UG-19 | REQ-PO-019 | Link resolution runs in CI. Conditional consultation has no recorded trial |
| UG-20 | REQ-PO-020 | The checker checks that the five terminal fields exist and use allowed values. Their truth has no recorded trial |
| UG-21 | REQ-PO-021 | No recorded trial. Freeze the scope-routing reading first (SRS OI-1) |
| UG-22 | REQ-PO-038 | No test feeds a duplicate key |
| UG-23 | REQ-PO-039 | No test for a missing root field, an unknown field, a non-mapping root, or empty `objective`, `next_step`, `constraints`, `user_directives`, `authority` or `rehydration` |
| UG-24 | REQ-PO-040 | No test for a bad `capsule_id`, a non-positive `revision`, or a parent on revision 1 or missing after it |
| UG-25 | REQ-PO-041 | No test for a duplicate record ID or an unresolved or wrong-kind reference |
| UG-26 | REQ-PO-042 | No test for an active record depending on an invalidated one, or a head of the wrong kind |
| UG-27 | REQ-PO-043 | No test for missing claim provenance fields, missing contradiction fields or a mismatched final `status_history` entry |
| UG-28 | REQ-PO-022 | `validate_skill.py` has no tests. No test removes a required file |
| UG-29 | REQ-PO-023 | No test for missing front matter, a wrong `name` or a wrong `metadata.version` |
| UG-30 | REQ-PO-024 | No test for implicit invocation allowed, a missing `$poodo` or a short description out of range |
| UG-31 | REQ-PO-025 | No test for a broken reference link or a placeholder |
| UG-32 | REQ-PO-026 | No test for a missing schema literal |
| UG-33 | REQ-PO-027 | No test for a non-executable script |
| UG-34 | REQ-PO-034 | No test passes `--hard-token-ceiling` |
| UG-35 | REQ-PO-031 | No test for an out-of-set string value |
| UG-36 | REQ-PO-030 | No test for malformed `outcomes[].depends_on` |
| UG-37 | REQ-PO-029 | No test for exit 2 on an unreadable or non-UTF-8 file |

## Tests without a requirement

| Test | Classification |
| --- | --- |
| `tools/test_check_trace.py::TraceCheckTests.test_repository_passes` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_minimal_repository_passes` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_requirement_without_row_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_missing_test_reference_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_gap_without_registration_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_full_without_automated_evidence_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_untraced_test_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_unallocated_requirement_fails` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_dead_link_and_anchor_fail` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_command_not_in_ci_fails` | Infrastructure: documentation trace check |

## Behavioral verification procedure

Before trials, freeze the baseline and candidate commits, model and configuration, permissions, cases, rubric applicability and acceptance thresholds in the [run-record template](../../evals/run-record.template.yaml). Keep grader-only expectations out of evaluated prompts. Run at least three independent trials per case and variant, randomize order, blind graders, and keep failures and disagreements. Continuity cases need at least three lossy summarize and resume cycles. Public development cases do not show generalization; add held-out cases before claiming it. See the [evaluation how-to](../guides/how-to/evaluation.md) and the [test plan](test-plan.md#tp-2--behavioral-trial).

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-10-30 | squashed into `36bfe78` | Matrix for REQ-PO-001 to REQ-PO-021 at a pre-squash commit not in this history | PR #13 |
| 2.0 | 2026-11-08 | `b969150` | Family format; one row per requirement with coverage and gap; rows for tool requirements REQ-PO-022 to REQ-PO-044; untested-gap register; supporting-test table; trace check in CI; results moved to the STR | this PR |
