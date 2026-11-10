# Limitations and safety-relevant use

This page collects what POODO does not do and what its outputs are not. It replaces a hazard report, which does not apply because nothing in POODO is safety-critical ([SMP §1](../../plan/software-management-plan.md#1-software-classification-self-assessed)).

## What the outputs are

- **The skill's output** is an agent's reasoning record and final answer. It is shaped by SKILL.md but produced by the host's model with the host's tools. POODO does not check it.
- **A validator pass** means the package or one capsule file has the structure the scripts check. Each pass message says so: "behavioral correctness remains untested" and "epistemic and behavioral correctness remain untested."
- **The evaluation manifests** describe 22 trial designs. None has been run. They are not results.
- **The examples** are synthetic teaching material, not measured runs.

## What POODO does not do

- It does not grant authority or permissions. Authority comes only from the user (invariant 7), and the host enforces permissions.
- It does not search the web, run subagents or manage goals. It tells the agent to use those features when the host provides them and to stop or record non-use when it does not.
- It does not enforce a spending limit. The Mega Observe charter is a plan; the repository ships no crawler, paid runner or billing cap.
- It does not prove that an agent reasoned soundly, that evidence is true, or that an outcome succeeded.
- It has no measured effect. No baseline comparison or behavioral trial set has been published.

## Use in safety, engineering or regulated decisions

Do not use a POODO-guided agent's output as the sole basis for a safety, engineering, legal, medical, financial or regulatory decision. Verify the conclusion against the authoritative sources for that field and with the people accountable for the decision. Using it that way moves your application to a higher assurance class (a Class D analog or above) that this project does not provide.

## Misuse and security considerations

- An agent following the skill acts with whatever tools the host allows. Set host permissions to what you would allow without POODO. The skill's authority rule is an instruction to the model, not an enforced control.
- Mega Observe can consume large amounts of model and search budget. Set a ceiling in the host before starting it.
- Capsules and evaluation records can contain private context. Keep raw runs in ignored `evals/runs/` and sanitize anything you publish.
- Report vulnerabilities privately ([SECURITY.md](../../../SECURITY.md)).

## Known limitations

| Limitation | Effect | Where tracked |
|---|---|---|
| No behavioral trial recorded | REQ-PO-001 to REQ-PO-021 have no result | Verification matrix UG-01 to UG-21 |
| The research gate needs web access | Hosts without it stop before Orient | REQ-PO-010 |
| The full loop is slow and costly | Wrong tool for routine questions | REQ-PO-001, REQ-PO-021 |
| The checker reads one capsule | It cannot compare sibling capsules or follow locators | [Capsule checker ICD](../../icd/icd-capsule-checker.md) |
| CI covers Linux only | Other operating systems are untested | [Test plan §8](../../verification/test-plan.md#8-test-risks-and-limitations) |
