# POODO requirements

## Scope and baseline

These requirements derive from [SKILL.md](../../SKILL.md), metadata version 3.1, at source baseline `01e6c60522702e6141a72bf081d5534eac92dcd5`. They describe required agent behavior, not behavior enforced by the Python tools. SKILL.md remains the authoritative contract; this document adds identifiers for traceability.

Verification methods: T = test, A = analysis, I = inspection, D = demonstration. Behavioral tests require a recorded agent trial and grading under the existing [evaluation protocol](../../evals/protocol.md); a proposed method below is not a passing result. The verification matrix is added separately.

## REQ-PO-001: Explicit invocation

The skill shall be used only when explicitly invoked for consequential or ambiguous work, rather than simple facts or routine execution.

- Source: SKILL.md, Front matter.
- Rationale: Keep the method within its stated scope.
- Verification: I: inspect invocation metadata; T: evaluate explicit-invocation and routine-work prompts.

## REQ-PO-002: Claim states

The agent shall distinguish possibilities, reports, observations, corroboration, inference, orientation, decisions, actions, outcomes, and learning.

- Source: SKILL.md, Invariant 1.
- Rationale: Prevent implementation or structure from being reported as effect.
- Verification: T: grade a trial containing reports and direct observations for state separation.

## REQ-PO-003: Evidence ceiling

The agent shall limit conclusions to what load-bearing evidence entails and shall not treat repeated or shared-source claims as independent corroboration.

- Source: SKILL.md, Invariant 2.
- Rationale: Keep claim strength tied to evidence.
- Verification: T: grade a shared-source corroboration trial.

## REQ-PO-004: Intended success surface

The agent shall trace the goal through acceptance, signal, sensor, oracle, artifact and environment to outcome, limiting proxy claims to their tested scope.

- Source: SKILL.md, Invariant 3.
- Rationale: A proxy can pass while the intended outcome fails.
- Verification: T: grade a structural-pass and runtime-failure trial.

## REQ-PO-005: Rival models

The agent shall preserve the strongest credible rival and a discriminating observation, using an independent critic for consequential, disputed, or failed-outcome work when available and labeling independence.

- Source: SKILL.md, Invariant 4.
- Rationale: Expose explanations that the favored model misses.
- Verification: T: inspect a trial for a rival, discriminator, and critic availability record.

## REQ-PO-006: Prospective prediction

The agent shall record the prediction, oracle and version, success boundary, artifact and environment, failure meaning, monitoring, rollback, and stop condition before action; it shall label retrodictive explanations.

- Source: SKILL.md, Invariant 5.
- Rationale: Prevent outcome-dependent changes to the original test.
- Verification: T: compare prediction timestamps and contents with subsequent action and outcome records.

## REQ-PO-007: Contradiction handling

The agent shall retract or narrow a contradicted success claim before causal explanation, default to failed, use failed_with_test_concern for unproven caveats, and require outcome-independent evidence before declaring a test invalid.

- Source: SKILL.md, Invariant 6.
- Rationale: Prevent rationalization of a failed prediction.
- Verification: T: grade a contradiction trial, including the evidence offered for invalidation.

## REQ-PO-008: Authority

The agent shall act only within user authorization and shall not expand it through compaction, delegation, confidence, or prior action.

- Source: SKILL.md, Invariant 7.
- Rationale: Reasoning does not grant execution permission.
- Verification: T: grade an authority-boundary trial and inspect tool actions.

## REQ-PO-009: Continuation

The agent shall emit a canonical capsule at the specified continuity boundaries, preserve provenance, lineage, contradictions and artifact identity, and treat restored claims as reported prior state until required evidence is checked.

- Source: SKILL.md, Invariant 8; Conditional routing.
- Rationale: Handoffs preserve state without manufacturing evidence.
- Verification: T: run capsule regression checks for structure; grade a resume trial for evidence rechecking.

## REQ-PO-010: Research gate

The agent shall finish every Observe phase with deep web research recording queries, sources, dates, conflicts, applicability and non-entailments, seeking foundations, current evidence and credible challenges; if research cannot be performed it shall stop before Orient.

- Source: SKILL.md, Invariant 9.
- Rationale: Broaden understanding without overriding stronger direct evidence.
- Verification: T: grade research-enabled and research-unavailable trials, including source quality and phase order.

## REQ-PO-011: Divergence

The agent shall name exactly 20 materially distinct paths before ranking or convergence, preserving applicable diagnostic, conservative, reversible, architectural, defer or stop, and escalation options.

- Source: SKILL.md, Invariant 10.
- Rationale: Avoid renamed duplicates of a preferred approach.
- Verification: T: grade distinctness and ordering of the 20 paths in a trial.

## REQ-PO-012: Grounded frame

The agent shall exchange with the user about the work and ideal outcome unless context establishes both with the specified quality, and shall always decompress objective, acceptance, scope, authority, stakes, assumptions, unknowns and rival frames before Observe.

- Source: SKILL.md, Invariant 11.
- Rationale: Do not silently replace user intent with inference.
- Verification: T: grade sparse-context and rich-context opening trials, including any waiver rationale.

## REQ-PO-013: Transition checkpoints

The agent shall consider a bounded subagent spike at every stage transition, normally use one when separable work can improve the decision, record use or non-use, and reconcile decision-relevant outputs and dissent before the gate decision.

- Source: SKILL.md, Invariant 12; Run the loop.
- Rationale: Obtain useful coverage without mistaking agent agreement for independence.
- Verification: T: inspect transition records, worker assignments and synthesis barriers in a trial.

## REQ-PO-014: Topology traversal

The agent shall map and traverse decision-relevant meanings, mechanisms, dependencies, stakeholders, evidence families, failure modes, adjacent possibilities, boundaries and rivals before convergence, recording unresolved regions against an explicit bounded-saturation map.

- Source: SKILL.md, Invariant 13.
- Rationale: Avoid claiming literal exhaustiveness or collapsing the space early.
- Verification: T: grade topology coverage, traversal and remaining-frontier records.

## REQ-PO-015: Native goals

The agent shall bind durable work to an invoked, requested or active native goal using only exposed operations, synchronize the required state, and complete it only when the intended acceptance contract is met.

- Source: SKILL.md, Invariant 14.
- Rationale: Keep persistent state consistent with the actual outcome.
- Verification: T: grade a goal-enabled trial and a host-without-goal-tools trial.

## REQ-PO-016: Loop order and decision

The agent shall follow Pontificate, Observe, Orient, Decide, Orchestrate and outcome comparison, composing choices from the explored paths with explicit criteria, uncertainty, reversibility and reversal conditions, then promoting learning only with provenance and an applicability boundary.

- Source: SKILL.md, Run the loop.
- Rationale: Connect exploration, authorized action and evidence-based revision.
- Verification: T: grade a full-loop trace for gate order, decision criteria and learning scope.

## REQ-PO-017: Mega Observe authorization

The agent shall enter Mega Observe only when explicitly selected and after agreement on the problem, accessible search scope and resource ceiling.

- Source: SKILL.md, Optional Mega Observe.
- Rationale: The optional mode has additional resource costs.
- Verification: T: grade optional-mode authorization and resource-ceiling probes.

## REQ-PO-018: Mega Observe quality

The agent shall target 200 materially distinct categories with 200 materially distinct evaluations each, report fewer defensible records as incomplete, avoid fabricated padding, disclose coverage and uncertainty, and retain the standard 20-path Orient gate.

- Source: SKILL.md, Optional Mega Observe.
- Rationale: Record counts and spending do not prove completeness.
- Verification: T: grade Mega Observe completeness, distinctness, coverage and post-research orientation probes.

## REQ-PO-019: Conditional guidance

The agent shall consult the linked guidance for the applicable validation, contradiction, continuity, terminal claim, maintenance, fan-out, topology and native-goal conditions, selecting operations for a necessary question or better discrimination.

- Source: SKILL.md, Conditional routing; Run the loop.
- Rationale: Route detailed work to its specified contract without making named methods mandatory.
- Verification: I: inspect links; T: inspect a trial for applicable routing and operation rationale.

## REQ-PO-020: Terminal claims

For consequential implementation handoffs, the agent shall report delivery_state, outcome_state, highest_justified_claim, required_runtime_observation and who_controls_next_test, reserving unqualified success terms for a passed intended-use criterion on the named artifact and environment.

- Source: SKILL.md, Terminal claim contract.
- Rationale: Make the remaining validation boundary explicit.
- Verification: T: grade terminal output against its prospective acceptance criterion.

## REQ-PO-021: Scaling and stopping

The agent shall scale effort with the stated risks and stop at a scoped validated outcome, a justified decision with next action, or a precise evidence or authority gap.

- Source: SKILL.md, Scaling and stopping.
- Rationale: Additional prose is not additional discrimination.
- Verification: T: grade stopping decisions and their stated evidence boundary.
