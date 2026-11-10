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
| REQ-PO-022 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_28_each_missing_required_file_is_named`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_28_every_missing_file_is_reported`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_28_required_file_replaced_by_directory`; `evals/test_validate_skill.py::PackageValidatorTests.test_f_4_failures_are_all_reported_together`; `evals/test_validate_skill.py::PackageValidatorTests.test_f_4_missing_skill_and_config_do_not_crash`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-023 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_29_front_matter_not_a_mapping`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_29_invalid_front_matter_yaml`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_29_missing_front_matter`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_29_wrong_metadata_version`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_29_wrong_name`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-024 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_30_default_prompt_missing_poodo`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_30_implicit_invocation_allowed`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_30_malformed_openai_yaml`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_30_short_description_out_of_range`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-025 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_31_broken_reference_link`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_31_link_resolves_relative_to_the_linking_file`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_31_placeholders`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_31_unreadable_markdown_is_reported`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-026 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_32_missing_schema_literal`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-027 | T | `evals/test_validate_skill.py::PackageValidatorTests.test_ug_33_non_executable_script`; `evals/test_validate_skill.py::PackageValidatorTests.test_ug_33_real_scripts_are_executable`; `ci: python scripts/validate_skill.py` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-028 | T, D | `evals/test_validate_skill.py::PackageValidatorTests.test_copied_package_passes`; `ci: python scripts/validate_skill.py` | Full | — | CI step: [STR](reports/README.md); test: pending, added 2026-11-10 |
| REQ-PO-029 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_failed_prediction_resurrection`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_nonstring_mapping_keys`; `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_impossible_dates_and_offsets`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_37_non_utf8_file_exits_2`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_37_permission_denied_exits_2`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_37_unreadable_path_exits_2` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-030 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_reference_collections`; `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_scalar_references`; `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_contradiction_references`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_36_malformed_outcome_depends_on` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-031 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_unhashable_enum_values`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_35_out_of_set_string_values` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-032 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_impossible_dates_and_offsets`; `evals/test_check_capsule.py::CapsuleLinterTests.test_accepts_real_rfc3339_dates`; `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule` | Full | — | [STR](reports/README.md) |
| REQ-PO-033 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_nonstring_mapping_keys` | Full | — | [STR](reports/README.md) |
| REQ-PO-034 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_oversize_capsule_rejected_without_overflow`; `evals/test_check_capsule.py::CapsuleLinterTests.test_declared_overflow_allows_oversize_capsule`; `evals/test_check_capsule.py::CapsuleLinterTests.test_empty_overflow_does_not_waive_ceiling`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_34_hard_token_ceiling_option` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-035 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_failed_prediction_resurrection` | Full | — | [STR](reports/README.md) |
| REQ-PO-036 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_rejects_truncated_evidence` | Full | — | [STR](reports/README.md) |
| REQ-PO-037 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_valid_capsule` | Full | — | [STR](reports/README.md) |
| REQ-PO-038 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_22_duplicate_keys_are_load_errors_at_any_depth` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-039 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_23_authority_and_rehydration_must_be_mappings`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_23_empty_required_values_are_rejected`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_23_missing_root_field_is_named`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_23_non_mapping_root_is_rejected`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_23_unknown_root_field_is_named` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-040 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_24_capsule_id_must_match_pattern`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_24_parent_lineage_rules`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_24_revision_must_be_positive_integer` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-041 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_reference_collections`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_25_duplicate_record_id_across_collections`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_25_missing_or_invalid_record_id`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_25_unresolved_references_are_named`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_25_wrong_kind_references_are_rejected` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-042 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_malformed_scalar_references`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_26_active_record_depending_on_retracted_record`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_26_current_head_must_be_a_head_kind`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_26_inactive_record_may_depend_on_retracted_record` | Full | — | Existing tests: [STR](reports/README.md); new tests: pending, added 2026-11-10 |
| REQ-PO-043 | T | `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_27_claim_provenance_fields_required`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_27_claim_text_required`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_27_contradiction_fields_required`; `evals/test_check_capsule.py::CapsuleLinterTests.test_ug_27_final_status_history_entry_must_equal_status` | Full | — | Pending: tests added 2026-11-10, not yet in a recorded STR |
| REQ-PO-044 | I, D | `inspect: requirements-dev.txt`; `ci: python -m pip install -r requirements-dev.txt` | Full | — | [STR](reports/README.md) |
| REQ-PO-045 | T | `tools/test_check_trace.py::TraceCheckTests.test_minimal_repository_passes`; `tools/test_check_trace.py::TraceCheckTests.test_missing_test_reference_fails` | Full | — | Pending: added 2026-11-10, not yet in a recorded STR |
| REQ-PO-046 | T | `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_clean_tree_is_baselined_at_head`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_dirty_tree_report_does_not_claim_head_as_baseline`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_dirty_tree_without_flag_is_refused`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_failed_trace_gate_does_not_report_all_passed`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_skipped_test_does_not_report_all_passed`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_suite_result_counts_every_non_pass_outcome`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_suite_that_runs_no_tests_does_not_report_all_passed`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_untracked_file_counts_as_dirty`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_coloured_output_is_parsed`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_failing_subtests_do_not_hide_a_passing_method`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_missing_status_line_is_a_problem`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_subtest_failures_are_reported_in_metrics`; `tools/test_gen_release_docs.py::GenReleaseDocsTests.test_suites_run_without_colour_when_colour_is_forced` | Full | — | Pending: added 2026-11-10, not yet in a recorded STR |

## Untested requirement gaps

Each gap is a behavior the software or the skill is meant to have that no automated test or recorded trial checks. Gaps are listed, not hidden. Closing one means adding a test or a recorded trial, updating the row and removing the gap from this table in the same PR. Gap IDs are not reused: UG-22 to UG-37 were closed on 2026-11-10 by the tests now listed against REQ-PO-022 to REQ-PO-027, REQ-PO-029 to REQ-PO-031, REQ-PO-034 and REQ-PO-038 to REQ-PO-043.

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

## Tests without a requirement

| Test | Classification |
| --- | --- |
| `tools/test_check_trace.py::TraceCheckTests.test_repository_passes` | Infrastructure: documentation trace check |
| `tools/test_check_trace.py::TraceCheckTests.test_requirement_without_row_fails` | Infrastructure: documentation trace check |
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
| 2.1 | 2026-11-10 | review backfill | Rows for REQ-PO-045 and REQ-PO-046: the trace check counts only tests unittest runs, and release records mark dirty trees and never report all passed over skips, unrun suites or a failed trace gate | PR #23 |
| 2.2 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | 49 new tests in `evals/test_validate_skill.py` and `evals/test_check_capsule.py` traced; REQ-PO-022 to REQ-PO-027, REQ-PO-029 to REQ-PO-031, REQ-PO-034 and REQ-PO-038 to REQ-PO-043 raised to Full; gaps UG-22 to UG-37 closed and removed from the register; REQ-PO-028 method T, D | this PR |
