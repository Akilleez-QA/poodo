# POODO software requirements specification

| Field | Value |
|---|---|
| Document ID | POODO-SRS |
| Version | 2.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit (method 3.1, capsule schema POODO_CONTINUATION/3.0) |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Introduction

### 1.1 Purpose and audience

This document gives every POODO requirement a stable ID, one "shall" statement, a source and a verification method. It is for contributors changing the skill or its validators, and for anyone checking what the repository does and does not verify.

### 1.2 Scope

POODO has two kinds of requirement:

- **Agent-behavior requirements** (REQ-PO-001 to REQ-PO-021). These are obligations that [SKILL.md](../../SKILL.md) places on an agent that runs the skill. An agent host executes them; no code in this repository does. They are accepted obligations, not inspected code behavior. Their only planned verification is a recorded, graded agent trial. No such trial has been recorded, so all 21 are untested gaps in the [verification matrix](../verification/verification-matrix.md).
- **Tool requirements** (REQ-PO-022 onward). These describe what the two Python validators do, as read from [validate_skill.py](../../scripts/validate_skill.py) and [check_capsule.py](../../scripts/check_capsule.py). Each one is either covered by a named automated test or listed as an untested gap.

Out of scope: the agent host, its model, its tools, its permissions, web search, subagents and native goals. The skill cannot create or grant any of these. Trust assumption: the person invoking the skill is the only source of authority; capsule and evaluation files are untrusted input to the validators.

### 1.3 System overview

POODO is an instruction package with two structural validators. It sits in the Cstack family as a skill/tool. Cstack carries a byte-pinned partial snapshot of it. See the [design description](../architecture/architecture.md) and the interface documents for the [skill host](../icd/icd-skill-host.md), the [capsule checker](../icd/icd-capsule-checker.md) and [Cstack](../icd/icd-cstack.md).

## 2. Requirement record format

Each requirement has: an ID, one "shall" statement, rationale, derivation (source paths), allocated-to (SDD section), verification method (T test, A analysis, I inspection, D demonstration) and status (Proposed, Baselined, Deleted). IDs are never reused. For agent-behavior requirements, "T" means a recorded agent trial graded under [protocol.md](../../evals/protocol.md) and [rubric.md](../../evals/rubric.md), not a Python test.

`tools/check_trace.py` parses this file. It fails if a requirement lacks a field, has more or fewer than one "shall", names a derivation path that does not exist, or names a missing SDD section.

## 3. Functional requirements: agent behavior

These derive from SKILL.md metadata version 3.1. SKILL.md stays the authoritative contract; this section only adds IDs.

### REQ-PO-001 — Explicit invocation

The skill shall be used only when explicitly invoked for consequential or ambiguous work, rather than simple facts or routine execution.

- Rationale: Keep the method within its stated scope.
- Derivation: `SKILL.md` (front matter); `agents/openai.yaml`
- Allocated to: SDD §4 (entry contract, host metadata)
- Verification: I (the package validator checks `allow_implicit_invocation: false`, REQ-PO-024); T (trial with explicit-invocation and routine-work prompts)
- Status: Baselined

### REQ-PO-002 — Claim states

The agent shall distinguish possibilities, reports, observations, corroboration, inference, orientation, decisions, actions, outcomes, and learning.

- Rationale: Prevent implementation or structure from being reported as effect.
- Derivation: `SKILL.md` (invariant 1); `references/epistemic-integrity.md`
- Allocated to: SDD §4 (entry contract)
- Verification: T (grade a trial containing reports and direct observations)
- Status: Baselined

### REQ-PO-003 — Evidence ceiling

The agent shall limit conclusions to what load-bearing evidence entails, without treating repeated or shared-source claims as independent corroboration.

- Rationale: Keep claim strength tied to evidence.
- Derivation: `SKILL.md` (invariant 2); `references/epistemic-integrity.md`
- Allocated to: SDD §4 (entry contract)
- Verification: T (grade a shared-source corroboration trial)
- Status: Baselined

### REQ-PO-004 — Intended success surface

The agent shall trace the goal through acceptance, signal, sensor, oracle, artifact and environment to outcome, limiting proxy claims to their tested scope.

- Rationale: A proxy can pass while the intended outcome fails.
- Derivation: `SKILL.md` (invariant 3); `references/epistemic-integrity.md`
- Allocated to: SDD §4 (entry contract)
- Verification: T (grade a structural-pass, runtime-failure trial)
- Status: Baselined

### REQ-PO-005 — Rival models

The agent shall preserve the strongest credible rival and a discriminating observation, using an independent critic for consequential, disputed, or failed-outcome work when available and labeling independence.

- Rationale: Expose explanations that the favored model misses.
- Derivation: `SKILL.md` (invariant 4); `references/orient.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (inspect a trial for a rival, a discriminator and a critic-availability record)
- Status: Baselined

### REQ-PO-006 — Prospective prediction

The agent shall record the prediction, oracle and version, success boundary, artifact and environment, failure meaning, monitoring, rollback, and stop condition before action, and label retrodictive explanations as such.

- Rationale: Prevent outcome-dependent changes to the original test.
- Derivation: `SKILL.md` (invariant 5); `references/orchestrate.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (compare prediction timestamps and contents with later action and outcome records)
- Status: Baselined

### REQ-PO-007 — Contradiction handling

The agent shall retract or narrow a contradicted success claim before causal explanation, default to failed, use failed_with_test_concern for unproven caveats, and require outcome-independent evidence before declaring a test invalid.

- Rationale: Prevent rationalization of a failed prediction.
- Derivation: `SKILL.md` (invariant 6); `references/contradiction-protocol.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade a contradiction trial, including the evidence offered for invalidation)
- Status: Baselined

### REQ-PO-008 — Authority

The agent shall act only within user authorization, never expanding it through compaction, delegation, confidence, or prior action.

- Rationale: Reasoning does not grant execution permission.
- Derivation: `SKILL.md` (invariant 7)
- Allocated to: SDD §4 (entry contract)
- Verification: T (grade an authority-boundary trial and inspect tool actions)
- Status: Baselined

### REQ-PO-009 — Continuation

The agent shall emit a canonical capsule at the specified continuity boundaries, preserve provenance, lineage, contradictions and artifact identity, and treat restored claims as reported prior state until required evidence is checked.

- Rationale: Handoffs preserve state without manufacturing evidence.
- Derivation: `SKILL.md` (invariant 8, conditional routing); `references/continuity-and-ledger.md`
- Allocated to: SDD §4 (continuity contract, capsule checker)
- Verification: T (capsule checker tests cover structure only, REQ-PO-029 to REQ-PO-043; a resume trial must grade evidence rechecking)
- Status: Baselined

### REQ-PO-010 — Research gate

The agent shall finish every Observe phase with deep web research recording queries, sources, dates, conflicts, applicability and non-entailments, seeking foundations, current evidence and credible challenges, and stop before Orient if research cannot be performed.

- Rationale: Broaden understanding without overriding stronger direct evidence.
- Derivation: `SKILL.md` (invariant 9); `references/observe.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade research-enabled and research-unavailable trials)
- Status: Baselined

### REQ-PO-011 — Divergence

The agent shall name exactly 20 materially distinct paths before ranking or convergence, preserving applicable diagnostic, conservative, reversible, architectural, defer or stop, and escalation options.

- Rationale: Avoid renamed duplicates of a preferred approach.
- Derivation: `SKILL.md` (invariant 10); `references/orient.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade distinctness and ordering of the 20 paths)
- Status: Baselined

### REQ-PO-012 — Grounded frame

The agent shall hold an exchange with the user about the work and ideal outcome unless context establishes both with the specified quality, and in every case decompress objective, acceptance, scope, authority, stakes, assumptions, unknowns and rival frames before Observe.

- Rationale: Do not silently replace user intent with inference.
- Derivation: `SKILL.md` (invariant 11); `references/pontificate.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade sparse-context and rich-context opening trials)
- Status: Baselined

### REQ-PO-013 — Transition checkpoints

The agent shall consider a bounded subagent spike at every stage transition, normally use one when separable work can improve the decision, record use or non-use, and reconcile decision-relevant outputs and dissent before the gate decision.

- Rationale: Get useful coverage without mistaking agent agreement for independence.
- Derivation: `SKILL.md` (invariant 12, run the loop); `references/fan-out-spikes.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (inspect transition records, worker assignments and synthesis barriers)
- Status: Baselined

### REQ-PO-014 — Topology traversal

The agent shall map and traverse decision-relevant meanings, mechanisms, dependencies, stakeholders, evidence families, failure modes, adjacent possibilities, boundaries and rivals before convergence, recording unresolved regions against an explicit bounded-saturation map.

- Rationale: Avoid claiming literal exhaustiveness or collapsing the space early.
- Derivation: `SKILL.md` (invariant 13); `references/semantic-topology.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade topology coverage, traversal and remaining-frontier records)
- Status: Baselined

### REQ-PO-015 — Native goals

The agent shall bind durable work to an invoked, requested or active native goal using only exposed operations, synchronize the required state, and complete it only when the intended acceptance contract is met.

- Rationale: Keep persistent state consistent with the actual outcome.
- Derivation: `SKILL.md` (invariant 14); `references/goal-integration.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: T (grade a goal-enabled trial and a host-without-goal-tools trial)
- Status: Baselined

### REQ-PO-016 — Loop order and decision

The agent shall follow Pontificate, Observe, Orient, Decide, Orchestrate and outcome comparison, composing choices from the explored paths with explicit criteria, uncertainty, reversibility and reversal conditions, then promoting learning only with provenance and an applicability boundary.

- Rationale: Connect exploration, authorized action and evidence-based revision.
- Derivation: `SKILL.md` (run the loop); `references/decide.md`
- Allocated to: SDD §5 (execution concept)
- Verification: T (grade a full-loop trace for gate order, decision criteria and learning scope)
- Status: Baselined

### REQ-PO-017 — Mega Observe authorization

The agent shall enter Mega Observe only when explicitly selected and after agreement on the problem, accessible search scope and resource ceiling.

- Rationale: The optional mode has large resource costs.
- Derivation: `SKILL.md` (optional Mega Observe); `references/mega-observe.md`; `assets/mega-observe-charter.yaml`
- Allocated to: SDD §4 (optional research charter)
- Verification: T (grade optional-mode authorization and resource-ceiling probes)
- Status: Baselined

### REQ-PO-018 — Mega Observe quality

The agent shall target 200 materially distinct categories with 200 materially distinct evaluations each, report fewer defensible records as incomplete, avoid fabricated padding, disclose coverage and uncertainty, and retain the standard 20-path Orient gate.

- Rationale: Record counts and spending do not prove completeness.
- Derivation: `SKILL.md` (optional Mega Observe); `references/mega-observe.md`
- Allocated to: SDD §4 (optional research charter)
- Verification: T (grade completeness, distinctness, coverage and post-research orientation probes)
- Status: Baselined

### REQ-PO-019 — Conditional guidance

The agent shall consult the linked guidance for the applicable validation, contradiction, continuity, terminal claim, maintenance, fan-out, topology and native-goal conditions, selecting operations for a necessary question or better discrimination.

- Rationale: Route detailed work to its contract without making named methods mandatory.
- Derivation: `SKILL.md` (conditional routing, run the loop); `references/method-selection.md`
- Allocated to: SDD §4 (phase guidance)
- Verification: I (the package validator checks that every `.md` link in SKILL.md and `references/` resolves, REQ-PO-025); T (inspect a trial for routing and operation rationale)
- Status: Baselined

### REQ-PO-020 — Terminal claims

For consequential implementation handoffs, the agent shall report delivery_state, outcome_state, highest_justified_claim, required_runtime_observation and who_controls_next_test, reserving unqualified success terms for a passed intended-use criterion on the named artifact and environment.

- Rationale: Make the remaining validation boundary explicit.
- Derivation: `SKILL.md` (terminal claim contract); `references/output-patterns.md`
- Allocated to: SDD §4 (entry contract)
- Verification: T (grade terminal output against its prospective criterion; the capsule checker only checks that the five fields exist and use allowed values)
- Status: Baselined

### REQ-PO-021 — Scaling and stopping

The agent shall scale effort with the stated risks and stop at a scoped validated outcome, a justified decision with next action, or a precise evidence or authority gap.

- Rationale: More prose is not more discrimination.
- Derivation: `SKILL.md` (scaling and stopping)
- Allocated to: SDD §5 (execution concept)
- Verification: T (grade stopping decisions and their stated evidence boundary)
- Status: Baselined

## 4. Functional requirements: package validator

Derived from `scripts/validate_skill.py`. The validator takes no arguments and checks the checkout that contains it.

### REQ-PO-022 — Required package files

The package validator shall exit 1 and name each missing file when any file in its required-file list is absent.

- Rationale: A partial copy breaks the skill's relative links and the CI gates.
- Derivation: `scripts/validate_skill.py` (`REQUIRED`, `main`)
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-28; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-023 — Skill front matter

The package validator shall exit 1 unless SKILL.md starts with a YAML front-matter mapping whose `name` is `poodo` and whose `metadata.version` is `3.1`.

- Rationale: Hosts discover the skill by its front matter; the version ties the package to its CHANGELOG entry.
- Derivation: `scripts/validate_skill.py` (`frontmatter`, `main`)
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-29; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-024 — Explicit-only host metadata

The package validator shall exit 1 unless `agents/openai.yaml` sets `policy.allow_implicit_invocation` to false, has a `default_prompt` containing `$poodo`, and has a `short_description` of 25 to 64 characters.

- Rationale: Implements the metadata half of REQ-PO-001.
- Derivation: `scripts/validate_skill.py` (`main`); `agents/openai.yaml`
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-30; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-025 — Reference links and placeholders

The package validator shall exit 1 when a relative `.md` link in SKILL.md or `references/*.md` does not resolve, or when those files contain `TODO`, `<TODO>` or `<TBD>`.

- Rationale: A broken routing link silently removes guidance the agent is told to read.
- Derivation: `scripts/validate_skill.py` (`main`)
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-31; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-026 — Continuation schema markers

The package validator shall exit 1 unless `references/continuity-and-ledger.md` contains the literals `POODO_CONTINUATION/3.0`, `POODO_CONTINUATION_V3_0` and `END_POODO_CONTINUATION_V3_0`.

- Rationale: Keeps the documented schema and the checker's `SCHEMA` constant on the same version.
- Derivation: `scripts/validate_skill.py` (`main`); `references/continuity-and-ledger.md`
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-32; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-027 — Executable scripts

The package validator shall exit 1 when `scripts/validate_skill.py` or `scripts/check_capsule.py` lacks an execute permission bit.

- Rationale: The scripts carry a shebang and are documented as directly runnable.
- Derivation: `scripts/validate_skill.py` (`main`)
- Allocated to: SDD §4 (package validator)
- Verification: T (no test yet; gap UG-33; the CI run only shows the real package passes)
- Status: Baselined

### REQ-PO-028 — Pass result and disclaimer

The package validator shall exit 0 and print "POODO structural checks passed; behavioral correctness remains untested." when every check passes.

- Rationale: A pass must not read as a behavioral result.
- Derivation: `scripts/validate_skill.py` (`main`)
- Allocated to: SDD §4 (package validator)
- Verification: D (CI step `python scripts/validate_skill.py` on the real package)
- Status: Baselined

## 5. Functional requirements: capsule checker

Derived from `scripts/check_capsule.py`. The interface is in the [capsule checker ICD](../icd/icd-capsule-checker.md) and the fields are in the [data dictionary](../data/data-dictionary.md).

### REQ-PO-029 — Exit status contract

The capsule checker shall exit 0 for a structurally valid capsule, 1 for invalid structure, and 2 when the file cannot be read or parsed.

- Rationale: Callers branch on the status without parsing text.
- Derivation: `scripts/check_capsule.py` (`main`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (exit 0, 1 and 2 on parse errors covered; exit 2 on an unreadable file untested; gap UG-37)
- Status: Baselined

### REQ-PO-030 — ID reference typing

The capsule checker shall reject any ID reference field that is not a valid ID string, or a list of valid ID strings where a list is required, naming the field.

- Rationale: Malformed references must fail closed rather than crash or pass.
- Derivation: `scripts/check_capsule.py` (`_references`, `_reference`, `ID_RE`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (all reference fields covered except `outcomes[].depends_on`; gap UG-36)
- Status: Baselined

### REQ-PO-031 — Enumerated values

The capsule checker shall reject a value outside its allowed set for `schema`, `delivery_state`, `outcome_state`, claim `state` and `status`, evidence `completeness`, prediction `status` and `status_history` entries, including list or mapping values, without a traceback.

- Rationale: Unhashable YAML values previously risked a crash instead of a verdict.
- Derivation: `scripts/check_capsule.py` (`_enum`, state sets)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (list and mapping values covered; out-of-set strings untested; gap UG-35)
- Status: Baselined

### REQ-PO-032 — Timestamps

The capsule checker shall accept `generated_at` only as an RFC 3339 timestamp with a real calendar date, hours 00–23, minutes and seconds 00–59, and an offset of at most 23:59, or as a timezone-aware YAML timestamp.

- Rationale: `datetime.fromisoformat` alone normalizes some impossible offsets.
- Derivation: `scripts/check_capsule.py` (`_timestamp`, `RFC3339_RE`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T
- Status: Baselined

### REQ-PO-033 — String mapping keys

The capsule checker shall treat a mapping key that is not a string as a load error (exit 2) that names the cause.

- Rationale: Non-string keys break field lookups downstream.
- Derivation: `scripts/check_capsule.py` (`UniqueKeyLoader`, `_construct_mapping`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T
- Status: Baselined

### REQ-PO-034 — Size ceiling and declared overflow

The capsule checker shall reject a capsule whose approximate token count, (characters + 3) // 4, exceeds the ceiling (default 1,800, set by `--hard-token-ceiling`) unless it declares a non-blank `capsule_overflow`.

- Rationale: Matches the method's soft ceiling; state may not be dropped silently.
- Derivation: `scripts/check_capsule.py` (`validate`, `main`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (default ceiling and overflow covered; `--hard-token-ceiling` untested; gap UG-34)
- Status: Baselined

### REQ-PO-035 — No prediction resurrection

The capsule checker shall reject a prediction whose `status_history` returns to any state after a terminal (non-`pending`) state.

- Rationale: A retest needs a new prediction ID (REQ-PO-007).
- Derivation: `scripts/check_capsule.py` (`validate`, predictions loop)
- Allocated to: SDD §4 (capsule checker)
- Verification: T
- Status: Baselined

### REQ-PO-036 — Incomplete evidence support

The capsule checker shall reject an evidence bundle marked `partial` or `truncated` that lists `supports_claims`.

- Rationale: Incomplete evidence cannot carry a capsule claim.
- Derivation: `scripts/check_capsule.py` (`validate`, evidence loop)
- Allocated to: SDD §4 (capsule checker)
- Verification: T
- Status: Baselined

### REQ-PO-037 — Pass result and disclaimer

The capsule checker shall print "POODO capsule structure passed; epistemic and behavioral correctness remain untested." to standard output when a capsule passes.

- Rationale: A structural pass must not read as a truth judgment.
- Derivation: `scripts/check_capsule.py` (`main`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T
- Status: Baselined

### REQ-PO-038 — Duplicate keys

The capsule checker shall treat a duplicate mapping key at any depth as a load error (exit 2).

- Rationale: YAML otherwise keeps the last value and hides the conflict.
- Derivation: `scripts/check_capsule.py` (`_construct_mapping`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (no test yet; gap UG-22)
- Status: Baselined

### REQ-PO-039 — Root field set

The capsule checker shall reject a capsule that is not a mapping, lacks any required root field, contains a field outside the required and optional sets, or has an empty `objective`, `next_step`, `constraints`, `user_directives` or terminal-claim field, or a non-mapping `authority` or `rehydration`.

- Rationale: The capsule must carry every decision-relevant slot.
- Derivation: `scripts/check_capsule.py` (`REQUIRED`, `OPTIONAL`, `validate`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (no test yet; gap UG-23)
- Status: Baselined

### REQ-PO-040 — Capsule identity and lineage

The capsule checker shall require `capsule_id` to match `PC-<id>`, `revision` to be a positive integer, revision 1 to have a null `parent_capsule`, and later revisions to name a valid `PC-` parent.

- Rationale: Lineage lets a reader detect forks and gaps between capsules.
- Derivation: `scripts/check_capsule.py` (`CAPSULE_RE`, `validate`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (no test yet; gap UG-24)
- Status: Baselined

### REQ-PO-041 — Record identity and resolution

The capsule checker shall require a unique, valid `id` on every collection record and resolve every referenced ID to a record of the expected kind.

- Rationale: Dangling references hide lost state.
- Derivation: `scripts/check_capsule.py` (`validate`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (partly covered by the malformed-reference tests; unresolved and duplicate IDs untested; gap UG-25)
- Status: Baselined

### REQ-PO-042 — Invalidated dependencies and head

The capsule checker shall reject an active orientation, decision or outcome that depends on an invalidated or superseded record, and a `current_head` that is not null or the ID of an orientation, decision, prediction or contradiction.

- Rationale: Work built on retracted state must be reopened (REQ-PO-007).
- Derivation: `scripts/check_capsule.py` (`validate`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (non-string head covered; dependency rule and head kind untested; gap UG-26)
- Status: Baselined

### REQ-PO-043 — Per-record required fields

The capsule checker shall require claims to carry non-empty text and the fields `source_type`, `locator`, `observed_at`, `freshness`, `evidence_family`, `rehydration_status` and `limits`; contradictions to carry `target`, `evidence`, `scope`, `effect`, `affected_ids`, `disposition` and `repaired_by`; and a prediction's last `status_history` entry to equal its `status`.

- Rationale: Provenance and contradiction state are what make a capsule rehydratable.
- Derivation: `scripts/check_capsule.py` (`validate`)
- Allocated to: SDD §4 (capsule checker)
- Verification: T (no test yet; gap UG-27)
- Status: Baselined

## 6. Interface requirements

The interface requirements are the tool requirements above, read against their interface documents:

| Interface | Requirements | ICD |
|---|---|---|
| Skill host (Agent Skills / Codex) | REQ-PO-001, REQ-PO-019, REQ-PO-022 to REQ-PO-027 | [icd-skill-host.md](../icd/icd-skill-host.md) |
| Capsule checker CLI and capsule file | REQ-PO-009, REQ-PO-029 to REQ-PO-043 | [icd-capsule-checker.md](../icd/icd-capsule-checker.md) |
| Cstack snapshot and `poodo_core` | none: Cstack owns its side (see ICD §7) | [icd-cstack.md](../icd/icd-cstack.md) |

## 7. Non-functional requirements

### REQ-PO-044 — Runtime and dependencies

The Python tooling shall run on Python 3.10 and 3.14 with only the standard library and PyYAML 6.0.3.

- Rationale: Keeps the validators installable with one pinned dependency.
- Derivation: `requirements-dev.txt`; `.github/workflows/checks.yml`; `scripts/validate_skill.py`; `scripts/check_capsule.py`
- Allocated to: SDD §9 (quality attributes)
- Verification: I (imports and `requirements-dev.txt`); D (CI matrix runs every step on 3.10 and 3.14)
- Status: Baselined

Performance, timing and resource limits: none are specified. The only bound is the capsule size ceiling in REQ-PO-034. No performance figure is claimed.

### REQ-PO-045 — Trace check counts only tests unittest runs

`tools/check_trace.py` shall count a test method as verification evidence only when unittest discovers and runs it, recognising every import form of `unittest.TestCase` and `unittest.IsolatedAsyncioTestCase` (module, submodule, alias and star imports, and inherited or mixed-in bases), reporting any matrix or supporting-test reference to a method unittest does not run.

- Rationale: A class that loses its `TestCase` base stops running its assertions while its requirement stays marked covered (2026-11-09 backfill review finding).
- Derivation: `tools/check_trace.py`, `tools/test_check_trace.py`
- Allocated to: SDD §4 (docs tooling)
- Verification: T
- Status: Baselined

### REQ-PO-046 — Release record baseline and result

`tools/gen_release_docs.py` shall mark a record generated from a tree with modified or untracked files as dirty instead of baselining it at HEAD, refuse a dirty tree unless `--allow-dirty` is given, and report all passed only when every suite ran at least one test with no skipped, failed or errored outcome and the trace gate passed.

- Rationale: A record attributed to a commit that does not contain its bytes, or that says all passed over skips, cannot be reproduced or trusted (2026-11-09 backfill review finding).
- Derivation: `tools/gen_release_docs.py`, `tools/test_gen_release_docs.py`
- Allocated to: SDD §4 (docs tooling)
- Verification: T
- Status: Baselined

## 8. Not applicable categories and open items

- Safety requirements: N/A. Not safety-critical ([SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)); no hazard analysis exists.
- Control-system, operating-system, board-support-package, partitioning and hardware-interface requirements: N/A. POODO has no such elements.
- Security and privacy requirements on the validators: none beyond fail-closed parsing (REQ-PO-029 to REQ-PO-033). The skill itself handles authority as an agent obligation (REQ-PO-008).

Open items:

| ID | Question | Owner | Issue |
|---|---|---|---|
| OI-1 | The `proportional-low-stakes` case conflicts with the mandatory research gate (REQ-PO-010). Freeze a scope-routing interpretation before any trial. | Akilleez-QA | none filed |

## 9. Qualification provisions

Automated tests and CI demonstrations qualify the tool requirements. A recorded, graded trial is the only accepted qualification for agent-behavior requirements; a structural pass never qualifies one. See the [test plan](../verification/test-plan.md) and the [verification matrix](../verification/verification-matrix.md).

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-10-30 | squashed into `36bfe78` | REQ-PO-001 to REQ-PO-021 from SKILL.md 3.1 | PR #12 |
| 2.0 | 2026-11-08 | `b969150` | Family metadata and disclaimer; record fields (derivation, allocation, status); one "shall" per requirement (wording only, meaning unchanged, in 003, 006, 008, 010, 012); tool requirements REQ-PO-022 to REQ-PO-044 read from the validators; open items; N/A categories. The 1.0 baseline commit `01e6c60` is not in this repository's history | this PR |
| 2.1 | 2026-11-10 | review backfill | Added REQ-PO-045 (trace check counts only tests unittest runs) and REQ-PO-046 (release record baseline and result) | PR #23 |
