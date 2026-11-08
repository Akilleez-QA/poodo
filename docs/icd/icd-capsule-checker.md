# POODO capsule checker interface control document

| Field | Value |
|---|---|
| Document ID | POODO-ICD-CAPSULE |
| Version | 1.0 |
| Status | Baselined |
| Owner | Akilleez-QA |
| Date | 2026-11-08 |
| Baseline commit | `b969150462c5fde83bbec9358ad17aa1d3663ec2` |
| Applies to | poodo main at baseline commit (capsule schema POODO_CONTINUATION/3.0) |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation inspected at the baseline commit.

## 1. Interfacing entities and ownership

| Side | Entity | Owns |
|---|---|---|
| POODO | `scripts/check_capsule.py` and `references/continuity-and-ledger.md` | The capsule schema, its allowed values and the check |
| Caller | An agent, a person or CI | Writing the capsule file, invoking the checker, acting on the exit status |

## 2. Interface type and transport

A command-line program. Input is one file path holding the YAML payload of a capsule, without the `POODO_CONTINUATION_V3_0` and `END_POODO_CONTINUATION_V3_0` delimiters. The file is read as UTF-8. Output is text: the pass line on stdout, error lines on stderr. The program reads one file, writes nothing and opens no network connection.

```text
usage: check_capsule.py [-h] [--hard-token-ceiling HARD_TOKEN_CEILING] capsule
```

## 3. Messages and data elements

| Call | Field | Type | Range / limits | Required | Meaning |
|---|---|---|---|---|---|
| argument | `capsule` | path | readable UTF-8 file | yes | Capsule YAML payload |
| option | `--hard-token-ceiling` | integer | any int; default 1800 | no | Size ceiling in approximate tokens, (characters + 3) // 4 |

The capsule's fields, types and allowed values are in the [data dictionary §2–§4](../data/data-dictionary.md#2-continuation-capsule-root-fields).

## 4. Errors and result semantics

| Condition | Exit | Output | Caller action | Test |
|---|---|---|---|---|
| Structure passes | 0 | stdout: `POODO capsule structure passed; epistemic and behavioral correctness remain untested.` | Treat as structural only | `test_valid_capsule` |
| Structure invalid | 1 | stderr: `INVALID POODO capsule structure:`, one `- <path>: <reason>` line per error, then `No judgment about epistemic truth was performed.` | Fix every listed field | `test_rejects_failed_prediction_resurrection` and others |
| File unreadable, not UTF-8, YAML error, duplicate key or non-string key | 2 | stderr: `INVALID: could not load capsule: <reason>` | Fix the file | `test_rejects_nonstring_mapping_keys`; duplicate and unreadable untested (UG-22, UG-37) |
| Oversize without `capsule_overflow` | 1 | `- size: approximately N tokens exceeds ceiling C; emit a non-empty capsule_overflow rather than silently deleting critical state` | Declare overflow or raise the ceiling deliberately | oversize tests |

All errors are collected before exit, so one run lists every structural problem. Example run at the baseline:

```text
$ python scripts/check_capsule.py evals/fixtures/invalid-resurrection.yaml
INVALID POODO capsule structure:
- predictions[0].status_history: terminal prediction was resurrected; create a new prediction ID
- predictions[0].oracle: unresolved ID AC-demo-visible
No judgment about epistemic truth was performed.
$ echo $?
1
```

## 5. Identity, versioning and compatibility

- Schema constant: `SCHEMA = "POODO_CONTINUATION/3.0"`; legacy accepted: `POODA_CONTINUATION/2.1`.
- The package validator checks that `references/continuity-and-ledger.md` carries the same version literals (REQ-PO-026).
- Breaking changes: adding a required field, removing an allowed value, or tightening a rule. A new schema version is needed for those. Method 3.1 kept schema 3.0.
- Compatibility check: `evals/test_check_capsule.py` in CI.

## 6. Security and input bounds

Parsing uses a `yaml.SafeLoader` subclass, so YAML tags cannot construct Python objects. Duplicate and non-string keys are refused at load. The whole file is read into memory; there is no file-size limit beyond the token ceiling applied after loading. The checker does not follow evidence locators.

## 7. Requirements addressed

| Requirement | Section |
|---|---|
| REQ-PO-009 | §1, §5 |
| REQ-PO-029, REQ-PO-033, REQ-PO-037, REQ-PO-038 | §4 |
| REQ-PO-030, REQ-PO-031, REQ-PO-032, REQ-PO-035, REQ-PO-036, REQ-PO-039 to REQ-PO-043 | §3 (via the data dictionary) |
| REQ-PO-034 | §3, §4 |

## 8. Change acceptance

Change the checker, the continuity reference and the data dictionary together. Add a regression test with a minimal failing input for every new rule. `python tools/check_trace.py` fails if a field or allowed value is missing from the data dictionary.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 1.0 | 2026-11-08 | `b969150` | Initial baseline | this PR |
