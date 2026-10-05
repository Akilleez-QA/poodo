# POODO

**Pontificate → Observe → Orient → Decide → Orchestrate**

A reasoning and orchestration skill for consequential decisions, investigations, and ambiguous work. POODO asks an agent to separate what it knows from what it assumes, challenge its preferred explanation, and verify the outcome it was actually asked to achieve.

```text
Frame the goal → Gather evidence → Explore alternatives → Commit → Act and verify
                       ↑                                         │
                       └────────── Learn from the outcome ───────┘
```

## Start here

- [Install and invoke POODO](docs/getting-started.md)
- [Understand the loop](docs/how-it-works.md)
- [Explore examples](examples/README.md)
- [Use Mega Observe: 200 categories × 200 evaluations](references/mega-observe.md)
- [Run checks and design evaluations](docs/evaluation.md)
- [Read the full skill](SKILL.md)

## What it does

POODO structures a decision around evidence, alternatives, authority, and an observable success criterion. It preserves uncertainty and unresolved contradictions across handoffs. Before acting, it records what should happen and how to tell whether it did.

For example, a deployment can pass every schema check while the user-visible feature still fails. POODO requires the agent to retract the outcome claim, preserve the passing checks within their limited scope, and identify the next useful test.

## The loop in pseudocode

A developer's sketch of the control flow. It is illustrative, not executable, and it does not replace [SKILL.md](SKILL.md), which remains the authoritative contract.

```python
def poodo(request, authority):
    # Authority comes only from the user. Reasoning, delegation, compaction,
    # confidence, and prior action never expand it.

    # ── PONTIFICATE: frame the problem before gathering evidence ──   [references/pontificate.md]
    if not context_clearly_establishes(work, ideal_outcome):
        ask_user("What are you working on? What does the ideal outcome look like?")
    frame = decompress(request)        # objective, acceptance criteria, scope, authority,
                                       # stakes, assumptions, unknowns, rival framings
    frame.separate(user_stated, agent_inferred)
    frame.rival = strongest_rival_frame(frame)
    checkpoint("Pontificate -> Observe")

    while True:
        # ── OBSERVE: establish what is actually known ──   [references/observe.md]
        evidence = gather(frame)       # each record: source, locator, freshness, evidence
                                       # family, scope, and what it does NOT establish
        topology = map_neighborhood(frame, evidence)   # meanings, mechanisms, dependencies,
                                                       # stakeholders, failure modes, unknowns
        if user_selected("Mega Observe"):              # optional, expensive, explicit only
            require(agreed_scope and resource_ceiling)
            evidence += mega_observe(categories=200, evaluations_each=200)  # [references/mega-observe.md]
        research = deep_web_research(topology, include_disconfirming_queries=True)
        if not research.satisfied:     # no web access, snippets only, one convenient source...
            return stop(reason="research gate unsatisfied", boundary=evidence.boundary)
        checkpoint("Observe -> Orient")

        # ── ORIENT: diverge before converging ──   [references/semantic-topology.md, references/orient.md]
        traverse(topology, until=bounded_saturation)   # record unreached regions
        paths = enumerate_paths(count=20, materially_distinct=True)  # incl. diagnostic,
                                       # conservative, rollback, defer/stop, escalate
        viable = cluster_and_eliminate(paths)          # every rejection keeps a reason
        favored, rival = rank(viable), strongest_credible_rival(viable)
        discriminator = observation_that_separates(favored, rival)
        checkpoint("Orient -> Decide")

        # ── DECIDE: the 20 paths are a design space, not a ballot ──   [references/decide.md]
        decision = compose(viable)     # select, combine, sequence, condition, test,
                                       # defer, or escalate any subset
        decision.reverse_if = reversal_conditions(decision)
        assert decision.within(authority)
        assert decision.claim_strength <= evidence.ceiling
        checkpoint("Decide -> Orchestrate")

        # ── ORCHESTRATE: precommit, then act and verify ──   [references/orchestrate.md]
        prediction = precommit(        # recorded BEFORE observing the outcome
            observable, acceptance_boundary, oracle, oracle_version,
            artifact_identity, environment, failure_meaning,
            monitoring, rollback, stop_condition)
        outcome = execute_authorized(decision, monitor=True)
        checkpoint("Orchestrate -> Loop")

        # ── LOOP: compare the outcome with the prediction ──   [references/contradiction-protocol.md]
        if contradicts(outcome, prediction):
            retract_or_narrow(success_claim)           # correct the claim first, explain later
            prediction.status = "failed"               # or "failed_with_test_concern";
                                                       # "invalid" only with outcome-independent proof
            reopen(dependents_of(prediction))
            restore(rival)
            frame = frame.with_contradiction(outcome)  # new prediction ID on any retest
            continue
        if validated_in_named_scope(outcome) or justified_decision_and_next_action() \
                or precise_evidence_or_authority_gap():
            return terminal_claim(     # [references/output-patterns.md]
                delivery_state,                # authored | checked | built | deployed
                outcome_state,                 # unobserved | observed | passed | failed | ...
                highest_justified_claim,
                required_runtime_observation,
                who_controls_next_test)
        frame = frame.with_learning(outcome)   # promote learning only with provenance + scope


def checkpoint(boundary):
    # Run at every stage transition.   [references/fan-out-spikes.md, references/continuity-and-ledger.md]
    if separable_workstreams_could_change(boundary):
        results = fan_out(workers_with_distinct_questions_or_evidence)  # bounded, read-only by default
        reconcile_into_ledger(results)         # agents sharing sources != independent corroboration
    record(fanout_used, reason_if_not)
    if handoff or pause or compaction_imminent:
        emit_continuation_capsule()            # state metadata, never evidence
```

Throughout, claim states stay separate: a report is not an observation, a passing structural check is not a runtime outcome, and a plausible cause is not a demonstrated one.

### Where each step is specified

| Pseudocode | Document | What it breaks down |
| --- | --- | --- |
| `poodo()` as a whole | [SKILL.md](SKILL.md) | The 14 invariants, loop order, routing, terminal claim contract, scaling and stopping |
| `ask_user`, `decompress` | [pontificate.md](references/pontificate.md) | Opening exchange, when it may be waived, linguistic decompression |
| `gather`, `deep_web_research` | [observe.md](references/observe.md) | Evidence records and the mandatory web-research gate |
| `mega_observe` | [mega-observe.md](references/mega-observe.md), [charter template](assets/mega-observe-charter.yaml) | 200 × 200 protocol, budget reservations, no-padding review, durable artifacts |
| `map_neighborhood`, `traverse` | [semantic-topology.md](references/semantic-topology.md) | Topology map, traversal operations, bounded-saturation gate |
| `enumerate_paths`, `cluster_and_eliminate` | [orient.md](references/orient.md) | The 20-path rule and what counts as materially distinct |
| `compose`, `reverse_if` | [decide.md](references/decide.md) | Treating paths as a design space; reversal conditions |
| `precommit`, `execute_authorized` | [orchestrate.md](references/orchestrate.md) | Workstream binding, monitoring, rollback, replanning |
| `contradicts`, `retract_or_narrow` | [contradiction-protocol.md](references/contradiction-protocol.md) | `failed` / `failed_with_test_concern` / `invalid` / `inconclusive`, propagation, anti-rationalization |
| `oracle`, `evidence.ceiling` | [epistemic-integrity.md](references/epistemic-integrity.md) | Verification vs. validation, oracle independence, discriminating tests, terminal labels |
| `checkpoint`, `fan_out` | [fan-out-spikes.md](references/fan-out-spikes.md) | Transition checkpoints, worker assignments, barriers, council debate |
| `emit_continuation_capsule` | [continuity-and-ledger.md](references/continuity-and-ledger.md), [`check_capsule.py`](scripts/check_capsule.py) | Capsule schema, lifecycle rules, re-entry and fork handling |
| `terminal_claim` | [output-patterns.md](references/output-patterns.md) | Recommendation, contradiction, and handoff formats |
| Native `/goal` binding (not shown) | [goal-integration.md](references/goal-integration.md) | Codex goal entry, stage sync, status semantics |
| Choosing which operations to run | [method-selection.md](references/method-selection.md) | Matching an operation to the open question; Quick/Standard/Deep depth |

Further reading: [How POODO works](docs/how-it-works.md) explains the reasoning behind each step, [Getting started](docs/getting-started.md) covers installation, and the [examples](examples/README.md) walk through [an architecture decision](examples/architecture-decision.md), [a deployment contradiction](examples/deployment-contradiction.md), [a continuity handoff](examples/continuity-handoff.md), and [a Mega Observe run](examples/mega-observe.md). The behavioral tests are in [evals/](evals/) ([manifest](evals/manifest.yaml), [rubric](evals/rubric.md), [protocol](evals/protocol.md)), and their design is in [evaluation.md](references/evaluation.md) and [docs/evaluation.md](docs/evaluation.md).

## Use it deliberately

Invoke POODO explicitly for architectural choices, difficult investigations, disputed evidence, strategy, and work that must survive multiple sessions. Ordinary facts and routine execution are outside its intended scope.

```text
Use $poodo to investigate why the deployed feature still fails even though
our checks pass. First establish the intended outcome and what evidence
would demonstrate it. You may inspect files and run local tests; do not deploy.
```

The standard loop requires web research before orientation, exactly 20 distinct paths before convergence, and consideration of bounded subagent work at each transition. Those requirements have real latency and context costs. A host without web access cannot complete the research gate. Subagents and native goals depend on the host's available tools; the skill cannot grant permissions or create missing capabilities.

## Mega Observe (expensive)

An optional research mode for a large semantic map: **200 distinct categories × 200 distinct evaluations each = 40,000 substantive records**. Invoke it explicitly:

```text
Use $poodo in Mega Observe mode to map this problem space. First prepare
its scope, source plan, quality criteria, and cost estimate. Do not begin
the expensive run until a resource ceiling is established.
```

Each category and evaluation must earn its place through a distinct, relevant question and traceable evidence or a documented knowledge gap. Duplicate headings, generic text, unsupported certainty, and invented citations fail the quality gate. If 200 meaningful categories cannot be supported, the result is incomplete.

The mode can require substantial inference and review, potentially hundreds of dollars depending on the host and models. It uses budget checkpoints and resumable records. This repository supplies the [protocol](references/mega-observe.md) and [charter](assets/mega-observe-charter.yaml); it does not include a crawler, paid execution service, or a billing cap implementation.

Literal coverage of the entire internet cannot be verified. The output must report the searched corpus, exclusions, uncertainty, and remaining frontier. The 200 × 200 design is experimental; neither spending nor record count proves completeness.

## Project status

This initial public project contains the POODO 3.1 instructions, reference library, capsule checker, regression tests, 14 base behavioral evaluation cases, eight Mega Observe protocol probes, and synthetic examples. CI checks package structure and checker regressions.

**Behavioral improvement is unmeasured.** There is no published baseline comparison or completed behavioral trial set. A passing checker does not demonstrate sound reasoning, truthful evidence, or a successful real-world outcome. See the [evaluation boundaries](docs/evaluation.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Agent entry point and invariants |
| `references/` | Phase guidance, evidence rules, continuity, and evaluation design |
| `agents/openai.yaml` | Codex metadata and explicit invocation policy |
| `scripts/` | Structural validators |
| `evals/` | Behavioral cases, rubric, protocol, and checker regression fixtures |
| `examples/` | Illustrative scenarios, not measured runs |
| `docs/` | Installation, concepts, evaluations, and roadmap |

The skill follows the [Agent Skills directory format](https://agentskills.io/specification). Its host-specific guidance currently targets Codex; other clients require their own installation and capability checks.

## Contribute

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Useful contributions include reproducible failure cases, clearer examples, independently graded trials, and fixes to checker behavior. Changes to the reasoning method should explain the problem and include evidence for their intended effect.

## License

[MIT](LICENSE). External sources linked from the references retain their own terms.
