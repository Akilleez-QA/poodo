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
- [Run checks and design evaluations](docs/evaluation.md)
- [Read the full skill](SKILL.md)

## What it does

POODO structures a decision around evidence, alternatives, authority, and an observable success criterion. It preserves uncertainty and unresolved contradictions across handoffs. Before acting, it records what should happen and how to tell whether it did.

For example, a deployment can pass every schema check while the user-visible feature still fails. POODO requires the agent to retract the outcome claim, preserve the passing checks within their limited scope, and identify the next useful test.

## Use it deliberately

Invoke POODO explicitly for architectural choices, difficult investigations, disputed evidence, strategy, and work that must survive multiple sessions. Ordinary facts and routine execution are outside its intended scope.

```text
Use $poodo to investigate why the deployed feature still fails even though
our checks pass. First establish the intended outcome and what evidence
would demonstrate it. You may inspect files and run local tests; do not deploy.
```

The complete 3.0 loop requires web research before orientation, exactly 20 distinct paths before convergence, and consideration of bounded subagent work at each transition. Those requirements have real latency and context costs. A host without web access cannot complete the research gate. Subagents and native goals depend on the host's available tools; the skill cannot grant permissions or create missing capabilities.

## Project status

This initial public project contains the POODO 3.0 instructions, reference library, capsule checker, regression tests, 14 behavioral evaluation cases, and synthetic examples. CI checks package structure and checker regressions.

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
