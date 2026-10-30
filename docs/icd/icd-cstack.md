# POODO and Cstack interface

## Scope and pinned baselines

| Side | Revision and version | Role |
| --- | --- | --- |
| Akilleez-QA/poodo | `4f47a9d67a1382e219bc1850107648eacfc541b8`; SKILL.md metadata 3.1; capsule schema POODO_CONTINUATION/3.0 | Instruction contract and structural validators |
| Akilleez-QA/cstack | `6052bd46e9db9b822f32092c9780a89fd0fe27da`; poodo.domain-extension/0.1, poodo.capability-request/0.1, poodo.capability-result/0.1 | Local poodo_core control layer and host ports |

Cstack was inspected read-only with `gh api` at the pinned revision. Links to that repository may require access. This is a source interface description, not a compatibility test or a deployed-integration claim.

## Relationship

POODO supplies the reasoning method through [SKILL.md](../../SKILL.md) and [references/](../../references/). Cstack contains its own [poodo_core](https://github.com/Akilleez-QA/cstack/tree/6052bd46e9db9b822f32092c9780a89fd0fe27da/poodo_core) Python package. Its pinned `requirements.txt` has no poodo dependency entry. The two repositories do not thereby establish a versioned import dependency or wire protocol between them.

Cstack's local implementation represents parts of the POODO method as typed records and control gates. The conceptual correspondence is phase order, research-boundary records, 20 option identifiers, prospective commitments, scoped authority and evidence ceilings. It does not show that the full behavioral requirements have passed evaluation.

## Cstack-facing control surface

The inspected [PoodoCore](https://github.com/Akilleez-QA/cstack/blob/6052bd46e9db9b822f32092c9780a89fd0fe27da/poodo_core/core.py) exposes these operations:

| Operation | Input and responsibility | Boundary |
| --- | --- | --- |
| Construction | Domain extension, capability bindings, authority grants and ledger; optional host approval, clock, budget, cost and admission ports | Host supplies authority and capabilities |
| start_goal / revise_goal | GoalContract | Start in Pontificate; revisions reset the phase |
| advance | Goal identifier, next phase and PhaseCheckpoint | Follow Pontificate → Observe → Orient → Decide → Orchestrate → Observe |
| decide | CapabilityRequest and Precommitment | Require Decide phase, new identities and admitted authority |
| execute | Decision identifier and optional cancellation | Execute through the bound capability port under core policy |
| snapshot / ledger | Goal identity or no argument | Read control state and recorded events |
| record_liveness / liveness / goals_without_live_path | Host next-action ownership records and queries | Identify open goals without a live next-action path |
| budget / lift_budget_pause | Host budget identity and revised limit where applicable | Inspect spend state and lift a recorded pause |

`advance` requires research references for Observe → Orient and exactly 20 distinct option identifiers for Orient → Decide. The source explicitly labels the checkpoint as host-authored and structural: the gate does not judge research adequacy or option distinctness in meaning.

## Records and ports

The pinned [models](https://github.com/Akilleez-QA/cstack/blob/6052bd46e9db9b822f32092c9780a89fd0fe27da/poodo_core/models.py) define:

- `GoalContract`, `GoalSnapshot` and `PhaseCheckpoint` for goal and phase state.
- `Precommitment` with expected observation, success boundary, failure meaning, oracle identifier and oracle version.
- `CapabilityRequest` with schema, request, goal/revision and decision identities, capability, operation, arguments and required evidence.
- `CapabilityOutcome` with request/attempt identity, execution status and certainty, assessment, epistemic status, raw result, provenance identities, scope and limitations. Accepted outcomes cannot set formal proof or runtime goal acceptance to true.

The [ports](https://github.com/Akilleez-QA/cstack/blob/6052bd46e9db9b822f32092c9780a89fd0fe27da/poodo_core/ports.py) separate domain admission and interpretation from capability invocation, ledger storage, approval lookup and consumption, cost estimates and actuals, and capacity admission. The [policy records](https://github.com/Akilleez-QA/cstack/blob/6052bd46e9db9b822f32092c9780a89fd0fe27da/poodo_core/policy.py) represent host-supplied authority, approvals, budgets and capacity limits.

The core is single-caller: the host must serialize calls across threads. It refuses same-call-stack mutation reentry. The source does not present it as a hostile-Python sandbox or provide automatic goal closure.

## Compatibility and open verification

The POODO continuation capsule and Cstack capability records are different contracts. No capsule-to-capability conversion is demonstrated by this inspection. Do not assume that a passing POODO capsule check validates a Cstack request, or that a completed capability proves a user outcome.

Any integration claim needs both pinned revisions, actual host bindings, a record-to-record mapping, authority tests, phase-gate tests and an intended-use observation. This documentation change runs no Cstack code or tests and claims no such result. Updating either pin requires reinspection of versions, records, gates, ports and limitations.
