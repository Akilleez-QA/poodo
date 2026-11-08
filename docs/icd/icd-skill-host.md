# POODO skill host interface control document

| Field | Value |
|---|---|
| Document ID | POODO-ICD-HOST |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit (method 3.1) |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Interfacing entities and ownership

| Side | Entity | Owns |
|---|---|---|
| POODO | This repository | `SKILL.md` front matter and body, `references/`, `assets/`, `agents/openai.yaml`, the directory layout and relative links |
| Host | An Agent Skills client, such as Codex | Skill discovery, invocation syntax, model, tools, permissions, web search, subagents, native goals, context compaction |
| User | The person invoking the skill | Authority, the problem statement and the acceptance of outcomes |

## 2. Interface type and transport

Files on disk. The host reads a skill directory. POODO expects the whole repository tree to be present, so that relative links from `SKILL.md` to `references/*.md` and `assets/` resolve. [Getting started](../guides/tutorials/getting-started.md) installs it by cloning into the host's skill directory (for Codex, `~/.agents/skills/poodo`). Encoding: UTF-8 Markdown and YAML. No network protocol, no process and no version negotiation exist.

## 3. Data elements

| Element | Field | Type | Range / limits | Required | Meaning |
|---|---|---|---|---|---|
| `SKILL.md` front matter | `name` | string | `poodo` | yes | Skill name the host shows and invokes |
| `SKILL.md` front matter | `description` | string | free text | yes | When to use the skill; says to use it only when explicitly invoked |
| `SKILL.md` front matter | `metadata.version` | string | `"3.1"` | yes | Method version; matches the CHANGELOG |
| `SKILL.md` body | invariants, loop, routing, terminal claim contract | Markdown | 14 invariants | yes | The agent's obligations (REQ-PO-001 to REQ-PO-021) |
| `agents/openai.yaml` | `interface.display_name` | string | `POODO` | no | Codex display name |
| `agents/openai.yaml` | `interface.short_description` | string | 25–64 characters | yes (validator) | Codex list text |
| `agents/openai.yaml` | `interface.default_prompt` | string | contains `$poodo` | yes (validator) | Suggested prompt |
| `agents/openai.yaml` | `policy.allow_implicit_invocation` | boolean | `false` | yes (validator) | Host must not auto-activate the skill |

Invocation: Codex uses `$poodo`. Other hosts may use different syntax and may ignore `agents/openai.yaml`; the description still says to use the skill only when explicitly invoked.

## 4. Errors and result semantics

| Condition | Response | Caller action | Test |
|---|---|---|---|
| Host has no web research tool | The skill tells the agent to stop before Orient and report the evidence boundary | Supply research access or accept the boundary | none (gap UG-10) |
| Host has no subagents | The agent records non-use at each transition | none | none (gap UG-13) |
| Host has no goal tools | The agent must not simulate goal state | none | none (gap UG-15) |
| Package incomplete or metadata changed | `validate_skill.py` exits 1 and names the problem | Restore the files | CI only shows the real package passes (gaps UG-28 to UG-33) |

## 5. Identity, versioning and compatibility

- Identity: the git commit of the checkout. No tags exist. Record the commit you installed.
- Method version: `metadata.version` in SKILL.md. The package validator requires `3.1`, so a version bump must update `validate_skill.py` in the same change.
- Breaking changes: renaming `SKILL.md` or `references/` files, changing `name`, or enabling implicit invocation.
- Compatibility check: `python scripts/validate_skill.py` in CI on every push and pull request.

## 6. Security and input bounds

The skill grants no authority. Invariant 7 says authority comes only from the user. The skill cannot widen host permissions. Mega Observe requires an agreed resource ceiling before launch (REQ-PO-017); the charter is a plan, not an enforced spending limit. See [limitations](../guides/explanation/limitations.md) and [SECURITY.md](../../SECURITY.md).

## 7. Requirements addressed

| Requirement | Section |
|---|---|
| REQ-PO-001 | §3, §5 |
| REQ-PO-019 | §2 (relative links) |
| REQ-PO-022 to REQ-PO-027 | §3, §4, §5 |
| REQ-PO-008, REQ-PO-017 | §6 |

## 8. Change acceptance

A change to the front matter, host metadata or file layout needs the package validator to pass on Python 3.10 and 3.14, the trace check to pass, and an updated CHANGELOG entry. Cstack carries a byte-pinned snapshot; see the [Cstack ICD](icd-cstack.md).

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
