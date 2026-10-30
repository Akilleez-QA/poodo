# POODO architecture

## Context and baseline

This description expands [How POODO works](../guides/explanation/how-it-works.md) at source baseline `01e6c60522702e6141a72bf081d5534eac92dcd5`. POODO is an instruction package executed by an agent host. Its entry point is [SKILL.md](../../SKILL.md), metadata version 3.1. The host supplies model execution, tools, permissions and any subagent or native-goal capabilities; the skill cannot create those capabilities or increase user authority.

The [requirements](../requirements/requirements.md) identify behavioral obligations. The Python validators inspect package or capsule structure; they do not implement the reasoning loop or prove its outcomes.

## Components

| Component | Source | Responsibility |
| --- | --- | --- |
| Entry contract | [SKILL.md](../../SKILL.md) | Invocation scope, invariants, loop, routing and stopping |
| Host metadata | [agents/openai.yaml](../../agents/openai.yaml) | Codex display metadata and explicit invocation policy |
| Phase guidance | [references/](../../references/) | Framing, research, topology, divergence, decisions and orchestration |
| Continuity contract | [continuity-and-ledger.md](../../references/continuity-and-ledger.md) | Capsule format, lineage, rehydration and state boundaries |
| Package validator | [validate_skill.py](../../scripts/validate_skill.py) | Required package files, metadata and selected structural checks |
| Capsule checker | [check_capsule.py](../../scripts/check_capsule.py) | A structural subset of a single continuation capsule |
| Evaluation material | [evals/](../../evals/) | Behavioral cases, rubric, protocol and checker regression fixtures |
| Examples | [examples/](../../examples/) | Synthetic illustrations rather than measured runs |
| Optional research charter | [mega-observe-charter.yaml](../../assets/mega-observe-charter.yaml) | Template for the explicitly requested Mega Observe mode |

## Control and data flow

| Phase | Input or question | Recorded output |
| --- | --- | --- |
| Pontificate | User work, ideal outcome and authority | Objective, acceptance, scope, assumptions and rival frames |
| Observe | Framed question and available evidence | Provenance, freshness, evidence boundaries, topology and deep web research |
| Orient | Research gate satisfied | Traversed topology, bounded saturation, 20 distinct paths and credible rivals |
| Decide | Viable paths and constraints | Composed commitment, tradeoffs, reversal conditions and authority gate |
| Orchestrate | Authorized decision | Prospective prediction, workstreams, monitoring, rollback and observations |
| Loop | Observation compared with prediction | Corrected claims, reopened dependencies or scoped learning |

Before each transition, the agent considers a bounded subagent spike and reconciles decision-relevant results before recording its gate decision. Subagent availability is conditional on the host. A shared source does not become independent evidence because several workers read it.

Before action, the agent records the criterion, oracle version, exact artifact and environment, failure meaning, monitoring, rollback and stop condition. A later change in criterion creates a new prospective test. A contradictory observation narrows or retracts the claim before causal explanation; a test concern alone does not establish invalidity.

## State and trust boundaries

A report locates possible evidence; it is not itself a direct observation. Structural conformance establishes only its checked structure. A plausible cause remains separate from a demonstrated cause. These distinctions constrain every phase and the final claim.

At continuity boundaries, a capsule preserves objective, authority, evidence locators, artifact identity, contradictions and the next checkpoint. On resume, required evidence must be rechecked. The checker cannot inspect the world behind those locators or compare sibling capsule branches.

For consequential handoffs, terminal output separates delivery state, outcome state, the highest justified claim, remaining runtime observation and who controls the next test. Successful file generation or a passing validator cannot establish a user-visible outcome.

## Design decisions represented in the source

- Keep the method as instructions and linked reference material, with structural validators as a separate verification aid.
- Require research and divergent exploration for the full loop; stop at the research boundary when web research is unavailable.
- Preserve rival explanations and prospective predictions so later evidence can change the decision.
- Preserve continuity metadata without promoting restored claims to fresh evidence.
- Keep Mega Observe optional, explicitly authorized and subject to scope, resource and no-padding gates.

These summarize the cited source rather than introduce new architecture decisions. This change does not add ADRs.

## Limits

The full loop has research and exploration costs and is outside the stated scope for routine questions. Behavioral improvement remains unmeasured in the repository's published evaluation discussion. A package check, capsule check or synthetic example does not demonstrate sound reasoning or a successful intended-use outcome. See [Evaluation](../guides/how-to/evaluation.md).
