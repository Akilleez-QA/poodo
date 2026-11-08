# POODO and Cstack interface control document

| Field | Value |
|---|---|
| Document ID | POODO-ICD-CSTACK |
| Version | 2.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` (poodo); `e02a0c43242c856c22501557160c79070bfa1157` (cstack main, inspected read-only) |
| Applies to | poodo main at baseline commit; cstack main at the commit above |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Interfacing entities and ownership

| Side | Revision and version | Owns |
|---|---|---|
| Akilleez-QA/poodo | baseline commit above; SKILL.md metadata 3.1; capsule schema POODO_CONTINUATION/3.0 | The method text, references, validators and evaluation material |
| [Akilleez-QA/cstack](https://github.com/Akilleez-QA/cstack) | `e02a0c43242c856c22501557160c79070bfa1157`; `poodo.domain-extension/0.1`, `poodo.capability-request/0.1`, `poodo.capability-result/0.1` | Its byte-pinned copy of POODO files under `reasoning/poodo/`, the pin record in `contracts/SOURCE-PINS.json`, and its own `poodo_core` Python package |

Cstack is the consumer. POODO does not import, call or test Cstack. Cstack was inspected read-only from a shallow clone of its main branch. This is a source description, not a compatibility test or a deployed-integration claim.

## 2. Interface type and transport

Two separate relationships:

1. **File snapshot.** Cstack copies a subset of POODO files byte for byte into `reasoning/poodo/` and records the upstream commit and file list in `contracts/SOURCE-PINS.json` under `poodo_skill`.
2. **Conceptual correspondence.** Cstack's `poodo_core` package represents parts of the method as typed records and control gates. It is Cstack code, not POODO code. No wire protocol, import or package dependency connects the two repositories.

## 3. Messages and data elements

### 3.1 Snapshot pin (Cstack `contracts/SOURCE-PINS.json`, key `poodo_skill`)

| Field | Value at cstack `e02a0c4` | Meaning |
|---|---|---|
| `root` | `reasoning/poodo` | Where the copy lives |
| `repository` | `https://github.com/Akilleez-QA/poodo` | Upstream |
| `commit` | `d1cce9e58fe80d8e35419c2d7ad335edd2c69044` | Upstream commit copied (poodo PR #16) |
| `status` | `partial-sync` | Not a complete mirror |
| `files` | 45 paths | Byte-exact subset |
| `deferred_existing_files` | `LICENSE`, `README.md` | Present in Cstack but not synced |
| `deferred_new_files` | 16 paths, including every engineering record under `docs/` | Not copied |

Measured on 2026-11-08 by comparing each of the 45 files in the Cstack copy with `git show <commit>:<path>` in this repository:

| Comparison | Identical | Different |
|---|---|---|
| Cstack copy vs poodo `d1cce9e` | 45 | 0 |
| Cstack copy vs poodo main `a61ac75` | 43 | 2 (`.github/workflows/checks.yml`, `CHANGELOG.md`) |

`git diff --stat d1cce9e a61ac75` in this repository shows only `.github/workflows/checks.yml`, `CHANGELOG.md` and `README.md` changed, so the method text, references, validators and evaluation material in the snapshot equal poodo main at `a61ac75`. Files added by this documentation baseline (including `tools/` and new `docs/` files) are not in the snapshot.

### 3.2 `poodo_core` control surface (Cstack-owned)

The [PoodoCore](https://github.com/Akilleez-QA/cstack/blob/e02a0c43242c856c22501557160c79070bfa1157/poodo_core/core.py) class exposes:

| Operation | Input and responsibility | Boundary |
|---|---|---|
| Construction | Domain extension, capability bindings, authority grants and ledger; optional approval port and approver, clock, cost budgets, cost port, admission (capacity) port, EndoForge port and session ID | Host supplies authority and capabilities |
| `start_goal` / `revise_goal` | `GoalContract` | Start in Pontificate; revisions reset the phase |
| `advance` | Goal ID, next phase, `PhaseCheckpoint` | Pontificate → Observe → Orient → Decide → Orchestrate → Observe |
| `decide` | `CapabilityRequest` and `Precommitment` | Requires the Decide phase, new identities and admitted authority |
| `execute` | Decision ID and optional cancellation | Runs through the bound capability port under core policy |
| `snapshot` / `ledger` / `descriptor` / `unresolved_attempts` | Goal ID or none | Read state and recorded events |
| `record_liveness` / `liveness` / `goals_without_live_path` | Host next-action records | Find open goals without a live next action |
| `budget` / `lift_budget_pause` | Budget identity and a revised limit | Inspect spend and lift a recorded pause |

`advance` raises unless Observe → Orient carries research references and Orient → Decide carries exactly 20 distinct option IDs. The class docstring says the gate "checks required records, not research adequacy or option quality", that the core is single-caller, that it is "not a hostile-Python sandbox", and that it has no goal-completion API. `CapabilityOutcome.from_dict` refuses `formal_proof` or `runtime_goal_acceptance` set to true ("Evidence ceiling exceeded").

The [models](https://github.com/Akilleez-QA/cstack/blob/e02a0c43242c856c22501557160c79070bfa1157/poodo_core/models.py) define `GoalContract`, `GoalSnapshot`, `PhaseCheckpoint`, `Precommitment` (expected observation, success boundary, failure meaning, oracle ID and version), `CapabilityRequest`, `CapabilityOutcome`, `DecisionRecord` and `LivenessRecord`. The [ports](https://github.com/Akilleez-QA/cstack/blob/e02a0c43242c856c22501557160c79070bfa1157/poodo_core/ports.py) define `CapabilityPort`, `DomainExtension`, `ApprovalPort`, `CostPort`, `AdmissionPort`, `LedgerPort`, `MemoryPort` and `EndoforgePort`; `MemoryPort` is not a `PoodoCore` constructor argument. The [policy records](https://github.com/Akilleez-QA/cstack/blob/e02a0c43242c856c22501557160c79070bfa1157/poodo_core/policy.py) cover authority grants, approvals, cost budgets and capacity limits.

## 4. Errors and result semantics

| Condition | Effect | Action |
|---|---|---|
| POODO main moves past the Cstack pin | The snapshot is stale; Cstack keeps the old bytes | Cstack re-pins upstream; never edit its copy |
| A POODO file Cstack copies is renamed or deleted | A Cstack re-pin must update its file list | Note the change in the POODO CHANGELOG |
| A POODO capsule passes the checker | Says nothing about a Cstack capability record | Do not convert one into the other without a tested mapping |

## 5. Identity, versioning and compatibility

The snapshot is identified by the upstream commit in `SOURCE-PINS.json`; `poodo_core` record versions are the three `0.1` constants in its `models.py`. The POODO continuation capsule and the Cstack capability records are different contracts. No capsule-to-capability conversion exists. An earlier version of this ICD pinned cstack `6052bd46`; that commit is no longer reachable from cstack main (`gh api .../compare` reports no common ancestor), so this version re-pins to current main.

## 6. Security and input bounds

Authority in Cstack comes from host-supplied grants and approvals in `poodo_core`. POODO's own authority rule (REQ-PO-008) is an agent obligation and is not enforced by any POODO code.

## 7. Requirements addressed

None of POODO's requirements are allocated to this interface. POODO places no obligation on Cstack, and Cstack's requirements (its `CS-REQ-*` IDs) belong to the Cstack repository.

## 8. Change acceptance

Updating either pin requires re-inspecting versions, records, gates, ports and limits, rerunning the byte comparison in §3.1, and updating this document. Any integration claim needs both pinned revisions, actual host bindings, a record-to-record mapping, authority tests, phase-gate tests and an intended-use observation. None exist today.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-10-30 | squashed into `36bfe78` | Source interface at cstack `6052bd46` | PR #13 |
| 2.0 | 2026-11-08 | `b969150` | Family format; re-pinned to cstack main `e02a0c4`; added the byte-pinned snapshot relationship and measured byte comparison; added the EndoForge and memory ports and newer read operations | this PR |
