# POODO data dictionary

| Field | Value |
|---|---|
| Document ID | POODO-DD |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit (capsule schema POODO_CONTINUATION/3.0) |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

Tailoring: minimal data dictionary for a skill/tool repository. Written by hand from `scripts/check_capsule.py`, `scripts/validate_skill.py`, `references/continuity-and-ledger.md` and the YAML files named below. `python tools/check_trace.py` fails if any capsule field name or allowed value in `check_capsule.py` (`REQUIRED`, `OPTIONAL` and the six value sets) is missing from this page.

Not applicable: channelization, rate-group, raw or calibrated sensor, telemetry, data-recorder and partitioning data. The software has no hardware or telemetry interfaces. No unit of measure applies to any field except the token estimate in §6.

## 1. Commands

| Name | Purpose | Parameters | Result | Restrictions | Source |
|---|---|---|---|---|---|
| `scripts/validate_skill.py` | Check package structure | none | Exit 0 pass, 1 fail; messages on stdout | Checks the checkout that contains the script | [CLI reference](../guides/reference/cli.md#validate_skillpy) |
| `scripts/check_capsule.py` | Check one capsule file | `capsule` (path); `--hard-token-ceiling` (int, default 1800) | Exit 0 pass, 1 invalid, 2 load error | YAML payload only, without continuation delimiters | [CLI reference](../guides/reference/cli.md#check_capsulepy) |
| `tools/check_trace.py` | Docs trace and link check | `--root` (path, default checkout); `--json` | Exit 0 pass, 1 fail | Needs PyYAML (imports the capsule checker) | [CLI reference](../guides/reference/cli.md#toolscheck_tracepy) |
| `tools/gen_release_docs.py` | Write the VDD and STR | `--python` (repeatable, required); `--allow-dirty` | Exit 0 all passed, 1 a suite or trace failed, 2 dirty tree | Uses `git`; `gh` optional | [CLI reference](../guides/reference/cli.md#toolsgen_release_docspy) |

## 2. Continuation capsule root fields

Schema `POODO_CONTINUATION/3.0`. The checker also accepts the legacy schema `POODA_CONTINUATION/2.1`. Canonical description: [continuity-and-ledger.md](../../references/continuity-and-ledger.md).

| Name | Type | Required | Range / rule enforced by the checker | Meaning |
|---|---|---|---|---|
| `schema` | string | yes | `POODO_CONTINUATION/3.0` or `POODA_CONTINUATION/2.1` | Capsule format version |
| `capsule_id` | string | yes | Matches `^PC-[A-Za-z0-9][A-Za-z0-9._-]*$` | Capsule identity |
| `revision` | integer | yes | ≥ 1; booleans rejected | Position in the lineage |
| `parent_capsule` | string or null | yes | Null when revision is 1; a `PC-` ID when revision > 1 | Previous capsule |
| `generated_at` | timestamp | yes | RFC 3339 with real date and offset ≤ 23:59, or timezone-aware YAML timestamp | When the capsule was written |
| `objective` | any | yes | Not null, not an empty list or mapping, and non-empty after `str()` and strip | What the work is for |
| `acceptance` | list of records | yes | Each record has a unique valid `id` | Acceptance criteria |
| `authority` | mapping | yes | Must be a mapping | What the user allowed and prohibited |
| `constraints` | string, list or mapping | yes | Non-empty | Binding constraints |
| `user_directives` | string, list or mapping | yes | Non-empty | User instructions in force |
| `current_head` | string or null | yes | Null, or the ID of an orientation, decision, prediction or contradiction | Latest decision-relevant record |
| `claims` | list of records | yes | See §3 | Claims with provenance |
| `evidence_bundles` | list of records | yes | See §3 | Groups of evidence and what they support |
| `orientations` | list of records | yes | `depends_on` resolves; active records may not depend on invalidated ones | Current interpretations |
| `alternatives` | list of records | yes | Unique valid `id` | Rival explanations or paths |
| `decisions` | list of records | yes | As `orientations` | Commitments |
| `predictions` | list of records | yes | See §3 | Precommitted predictions |
| `outcomes` | list of records | yes | As `orientations` | Observed outcomes |
| `contradictions` | list of records | yes | See §3 | Open or repaired contradictions |
| `artifacts` | list of records | yes | Unique valid `id` | Exact artifact identities |
| `rehydration` | mapping | yes | Must be a mapping | Restore status and losses |
| `delivery_state` | string | yes | One of the delivery states in §4 | How far delivery got |
| `outcome_state` | string | yes | One of the outcome states in §4 | What is known about the outcome |
| `highest_justified_claim` | any | yes | Non-empty (null, blank, `[]` and `{}` rejected) | Strongest claim the evidence supports |
| `required_runtime_observation` | any | yes | Non-empty (null, blank, `[]` and `{}` rejected) | Remaining intended-use check, or `none` with evidence IDs |
| `who_controls_next_test` | any | yes | Non-empty (null, blank, `[]` and `{}` rejected) | Agent, user, named party or none |
| `next_step` | any | yes | Non-empty (null, blank, `[]` and `{}` rejected) | The next action |
| `capsule_overflow` | string | no | Non-blank to waive the size ceiling | What could not fit and where it is |

Any other root field is rejected. Record IDs in collections match `^[A-Z]{1,4}-[A-Za-z0-9][A-Za-z0-9._-]*$` and are unique across all ten collections. Collections are read in a fixed order (`acceptance`, `claims`, `evidence_bundles`, `alternatives`, `orientations`, `decisions`, `predictions`, `outcomes`, `contradictions`, `artifacts`), so a duplicate is always reported against the later record whatever the hash seed.

## 3. Capsule record fields checked

| Record | Field | Type | Rule |
|---|---|---|---|
| claim | `id` | ID string | Required, unique |
| claim | `text` or `claim` | string | One must be non-empty |
| claim | `state` | string | A claim state in §4 |
| claim | `status` | string | A record status in §4 |
| claim | `source_type`, `locator`, `observed_at`, `freshness`, `evidence_family`, `rehydration_status`, `limits` | any | Key must be present |
| claim | `supports` | list of IDs | Each resolves to a record |
| evidence bundle | `completeness` | string | A completeness value in §4 |
| evidence bundle | `supports_claims` | list of IDs | Each resolves to a claim; must be empty when `partial` or `truncated` |
| evidence bundle | `artifacts` | list of IDs | Each resolves to an artifact |
| orientation, decision, outcome | `depends_on` | list of IDs | Each resolves; an active record may not depend on an `invalidated` or `superseded` one |
| prediction | `status` | string | A prediction state in §4 |
| prediction | `status_history` | non-empty list | Every entry a prediction state; last entry equals `status`; nothing after the first non-`pending` entry |
| prediction | `oracle`, `artifact` | ID string | Optional; resolves when present |
| prediction | `outcome_evidence` | list of IDs | Each resolves |
| contradiction | `target` | ID string | Required; resolves |
| contradiction | `evidence`, `affected_ids`, `repaired_by` | list of IDs | Required; each resolves |
| contradiction | `scope`, `effect` | any | Key must be present |
| contradiction | `disposition` | string | `unresolved`, `repaired` or `accepted` |

Fields such as `request`, `observable`, `environment`, `discriminator`, `reversible`, `identity` and `mutable` appear in the fixtures and the contract but are not checked.

## 4. Allowed values

| Set (constant in `check_capsule.py`) | Values |
|---|---|
| Claim states (`CLAIM_STATES`) | `reported`, `reported_prior_state`, `observed`, `corroborated`, `inferred` |
| Record statuses (`RECORD_STATES`) | `active`, `stale`, `superseded`, `invalidated` |
| Prediction states (`PREDICTION_STATES`) | `pending`, `passed`, `failed`, `invalid`, `inconclusive`, `failed_with_test_concern` |
| Evidence completeness (`COMPLETENESS`) | `complete`, `partial`, `truncated` |
| Delivery states (`DELIVERY_STATES`) | `authored`, `checked`, `built`, `deployed`, `other` |
| Outcome states (`OUTCOME_STATES`) | `unobserved`, `reported`, `observed`, `corroborated`, `passed`, `failed`, `failed_with_test_concern`, `invalid`, `inconclusive` |

## 5. Other records and files

| File | Format | Schema field | Producer | Consumer | Fields |
|---|---|---|---|---|---|
| `SKILL.md` front matter | YAML | — | Maintainer | Host; package validator | `name` (must be `poodo`), `description`, `metadata.version` (must be `"3.1"`) |
| `agents/openai.yaml` | YAML | — | Maintainer | Codex; package validator | `interface.display_name`, `interface.short_description` (25–64 chars), `interface.default_prompt` (must contain `$poodo`), `policy.allow_implicit_invocation` (must be `false`) |
| `evals/manifest.yaml` | YAML | `POODO_EVALS/1` | Maintainer | Human or future runner | `protocol`, `rubric`, `minimum_trials_per_case` (3), `cases[]`: `id`, `subset`, `prompt`, `required`, `forbidden`, `catastrophic_if`; optional `not_applicable` (rubric dimensions excluded, frozen before scoring; no case uses it at the baseline) |
| `evals/mega-observe.yaml` | YAML | `POODO_MEGA_EVALS/1` | Maintainer | Human or future runner | `status` (`unexecuted-design-cases`), `protocol`, `rubric`, `minimum_trials_per_case` (3), `cases[]`: `id`, `prompt`, `required`, `catastrophic_if` |
| `evals/run-record.template.yaml` | YAML | `POODO_RUN_RECORD/1` | Experimenter, before a trial | Grader, reviewer | Commits, manifest/rubric/protocol SHA-256, model and host, permissions, cases, seed, frozen acceptance criteria, rubric applicability, blinding, continuity cycles, results, failures, disagreements, limitations, `highest_justified_claim` |
| `assets/mega-observe-charter.yaml` | YAML | `POODO_MEGA_OBSERVE_CHARTER/1` | Agent and user, before a run | Agent; reviewer | Problem, scope, exclusions, sources, `category_target` 200, `evaluations_per_category` 200, `matrix_target` 40000, quality contract, `budget.*` (nulls mean unresolved, not unlimited), environment, frontier |
| `evals/runs/` | any | — | Experimenter | Reviewer | Ignored by git; raw runs stay here until reviewed for publication |

None of these files is validated by code except `SKILL.md` front matter and `agents/openai.yaml` (package validator) and capsules (capsule checker). The manifests, run record and charter are read by people.

## 6. Operational limits

| Limit | Value | Enforced in | Test |
|---|---|---|---|
| Capsule size ceiling | 1,800 approximate tokens by default; tokens = (characters + 3) // 4 | `check_capsule.py` `validate()` | `evals/test_check_capsule.py` oversize tests |
| Short description length | 25–64 characters | `validate_skill.py` | `evals/test_validate_skill.py` `test_ug_30_short_description_out_of_range` |
| Minimum trials per behavioral case | 3 | `evals/manifest.yaml` (read by people) | not enforced by code |

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
| 1.1 | 2026-11-10 | findings sweep `07d033a`..`89c25a9` | Empty now includes null, `[]` and `{}` for the required string fields; duplicate IDs reported in a fixed collection order; short-description limit now tested | this PR |
