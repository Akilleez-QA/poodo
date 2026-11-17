# POODO agent tools interface control document

| Field | Value |
|---|---|
| Document ID | POODO-ICD-TOOLS |
| Version | 0.1 |
| Status | Proposed |
| Owner | Akilleez-QA |
| Date | 2026-11-16 |
| Baseline commit | none yet: draft on branch `feat/poodo-tools` |
| Applies to | `scripts/poodo_tools.py` tools version 1.0.0 (capsule schema POODO_CONTINUATION/3.0) |
| Classification | Self-assessed Class E analog; not safety-critical (see [SMP §1](../plan/software-management-plan.md#1-software-classification-self-assessed)) |

> Organized after [NPR 7150.2D](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7150_002D_&page_name=all), [NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398) and the [NASA Software Engineering Handbook](https://swehb.nasa.gov/display/SWEHBVD/7.18+-+Documentation+Guidance) documentation guidance. This is not a NASA compliance determination or certification. The software classification is a self-assessed analog (Class E, not safety-critical); no NASA authority, independent verification and validation, or hazard analysis is asserted. The document describes the implementation on the branch named above.

## 1. Interfacing entities and ownership

| Side | Entity | Owns |
|---|---|---|
| POODO | `scripts/poodo_tools.py` | Tool names, input schemas, result objects, bounds and the check rules |
| Caller | An MCP host (for example a Claude Code agent such as Cstack's Oracle), a shell, CI or a person | Starting the server or command, supplying records, acting on the result |

Every check is structural or lexical. A pass says a record has the required shape; it says nothing about whether the record is true, whether research or testing happened, or whether the reasoning is sound. Results say so in `disclaimer` and list the unchecked properties in `not_checked`.

## 2. Interface type and transport

**MCP server.** `python scripts/poodo_tools.py serve` speaks JSON-RPC 2.0 over standard input and output, one UTF-8 JSON message per line (the MCP stdio transport). It writes only protocol messages to standard output, exits 0 at end of input, needs no network and opens no port. Batches are refused. A host registers it as a stdio server, for example:

```json
{"mcpServers": {"poodo": {"command": "python", "args": ["/path/to/poodo/scripts/poodo_tools.py", "serve"]}}}
```

| Method | Behaviour |
|---|---|
| `initialize` | Returns `protocolVersion` (the client's if it is one of `2025-11-25`, `2025-06-18`, `2025-03-26`, `2024-11-05`, else `2025-11-25`), `capabilities: {"tools": {"listChanged": false}}`, `serverInfo: {"name": "poodo-tools", "version": "1.0.0"}` and `instructions` |
| `ping` | Returns `{}` |
| `tools/list` | Returns the five tools with `inputSchema` and `annotations` (`readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`) |
| `tools/call` | Runs one tool; result `{content: [{type: "text", text: <JSON>}], structuredContent: <result>, isError}` |
| any notification | No response |

**CLI.** `python scripts/poodo_tools.py [--json] <subcommand> <file>` runs the same check on one file and prints a summary, or the full result object with `--json`.

```text
usage: poodo_tools.py [-h] [--json] {serve,check-capsule,precommit-hash,orient-paths-check,research-gate-check,terminal-claim-check} ...
```

| Subcommand | Tool | File |
|---|---|---|
| `check-capsule FILE [--hard-token-ceiling N]` | `check_capsule` | Capsule YAML payload |
| `precommit-hash FILE [--record] [--name NAME] [--receipt FILE]` | `precommit_hash` | Any file; hashed as raw bytes, or with `--record` read as JSON or YAML and hashed as canonical JSON |
| `orient-paths-check FILE` | `orient_paths_check` | JSON or YAML object `{paths: [...]}` |
| `research-gate-check FILE` | `research_gate_check` | JSON or YAML research record |
| `terminal-claim-check FILE` | `terminal_claim_check` | JSON or YAML terminal claim |

## 3. Messages and data elements

Every result object has `tool`, `tools_version`, `status`, `scope`, `errors` (list of strings), `warnings` (list of strings) and `disclaimer`. Structural results add `not_checked`. Field-level types and limits are in the [data dictionary §7](../data/data-dictionary.md#7-agent-tool-parameters-and-results).

| Tool | Required arguments | Optional arguments | Fails when | Warns when |
|---|---|---|---|---|
| `check_capsule` | `capsule` (string) | `hard_token_ceiling` (integer 1–100000, default 1800) | `check_capsule.validate()` reports any error | never |
| `precommit_hash` | exactly one of `document` (string) or `record` (any JSON value) | `name` (default `PRECOMMIT.md`), `receipt` (sha256sum-format text) | a receipt is given and no digest line matches | never |
| `orient_paths_check` | `paths` (list of `{name, mechanism}`; a bare string counts as a name without a mechanism) | none | not exactly 20 entries; an entry lacks a name or mechanism; two entries share a normalized name, the same name words reordered, or the same normalized mechanism | two entries' name or mechanism word sets overlap with Jaccard ≥ 0.75; a mechanism spans several lines |
| `research_gate_check` | `queries`, `sources`, `conflicts`, `non_entailments` | `implications`, `semantic_additions`, `applicability`, `gate` (`satisfied` or `unsatisfied`) | no query; fewer than 2 sources; a source URL not http(s) with a host, or repeated; a `retrieved`, `published` or `updated` value that is not an ISO 8601 date; `conflicts` not a list; no non-entailment; `gate: satisfied` with any other error | no disconfirming query; one host or one declared evidence family for all sources; a source without published or updated date; empty conflicts; no implication |
| `terminal_claim_check` | `delivery_state`, `outcome_state`, `highest_justified_claim`, `required_runtime_observation`, `who_controls_next_test` | `acceptance` (list of `{id, criterion, status, artifact?, environment?, evidence?}`), `summary` | a field blank; a state outside the capsule checker's sets; `none` observation without an evidence ID; a remaining observation with `none` as controller; `outcome_state: passed` without a passed entry naming artifact and environment; an unnegated fixed, resolved, successful or validated (and inflections) in the claim or summary without both a passed entry and `outcome_state: passed` | never |

Normalization for `orient_paths_check`: Unicode NFKC, case-folded, reduced to alphanumeric tokens; stopwords (a, an, and, as, at, be, by, for, from, in, into, is, it, of, on, or, the, then, to, via, with, without) are dropped for the word-set comparisons.

Negation for `terminal_claim_check`: a success word is not flagged when one of not, no, never, without, cannot, nor, unless, isn't, aren't, wasn't, weren't, hasn't, haven't or yet appears among the three preceding words. Other qualifications ("fixed in staging") are still flagged; the rule is deliberately conservative.

`precommit_hash` methods: a CLI file is hashed as its exact bytes, matching `sha256sum PRECOMMIT.md > receipt/precommit.sha256` as EndoForge's experiment procedure records it. An MCP `document` string is hashed as its UTF-8 bytes; JSON transport cannot carry non-UTF-8 bytes, so hash such files with the CLI. A `record` is hashed as `json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)` encoded as ASCII, the form Cstack's `poodo_core` uses for record digests. A receipt line is `<64 hex>  <name>`; other lines (for example timestamps) are ignored. The result reports `matched_lines`, `matches_first` and `matches_last`, because a receipt may carry an original digest followed by amendment digests and callers decide which one binds.

## 4. Errors and result semantics

| Condition | MCP | CLI exit | `status` |
|---|---|---|---|
| Check passes | result, `isError: false` | 0 | `pass` (`ok` for `precommit_hash` without a receipt) |
| Check fails | result, `isError: false` | 1 | `fail` |
| Arguments rejected (wrong type, unknown or missing field, over a bound, YAML error, duplicate key, one delimiter only) | result, `isError: true` | 2 | `error` |
| File unreadable or not UTF-8 (CLI) | — | 2 | `error`, message `could not load input: <reason>` |
| Line not JSON | error `-32700` | — | — |
| Batch, wrong `jsonrpc`, missing method, null or non-scalar id, line over 1,048,576 bytes | error `-32600` | — | — |
| Unknown method | error `-32601` | — | — |
| Unknown tool or non-object `params` | error `-32602` | — | — |
| Unexpected internal fault | error `-32603` | — | — |

Example at the branch head:

```text
$ python scripts/poodo_tools.py terminal-claim-check claim.json
terminal_claim_check: fail
- error: required_runtime_observation: 'none' must cite the evidence IDs that closed the runtime check
- error: highest_justified_claim: unqualified 'fixed' without a passed intended-use criterion on a named artifact and environment
Structural check only: a pass is not a truth or quality judgement. Structural conformance is not runtime validation.
$ echo $?
1
```

## 5. Identity, versioning and compatibility

- `TOOLS_VERSION = "1.0.0"` is reported in `serverInfo.version` and in every result as `tools_version`.
- Breaking changes: renaming a tool or argument, tightening a rule, or changing a result field. Bump the major version for those.
- `check_capsule` follows `scripts/check_capsule.py`; a capsule-checker change changes this tool's results in the same commit.
- Compatibility check: `evals/test_poodo_tools.py` in CI drives the server with its own minimal client. A manual run on 2026-11-16 with the MCP Python SDK client 2.3.0 (`initialize`, `tools/list`, three `tools/call`s, negotiated protocol `2025-11-25`) succeeded; that run is not in CI. No session with an agent host such as Claude Code or Codex is recorded.

## 6. Security and input bounds

| Bound | Value |
|---|---|
| Text argument (`capsule`, `document`, `receipt`, `summary`, a CLI file) | 262,144 characters (CLI raw-byte hashing: 1,048,576 bytes) |
| List length | 200 items |
| Nesting depth of arguments | 32 levels |
| Path name | 200 characters |
| One-line fields (mechanisms, queries, claims, list entries) | 2,000 characters |
| URL | 2,048 characters |
| MCP message | 1,048,576 bytes per line |

YAML input uses the capsule checker's `SafeLoader` subclass, so tags cannot construct objects and duplicate or non-string keys are refused. No URL is fetched. Results echo only field names and paths, matched success words and the receipt `name`, never the submitted record. The server holds no state between calls.

## 7. Requirements addressed

| Requirement | Section |
|---|---|
| REQ-PO-047 | §2, §4 |
| REQ-PO-048 | §2, §4 |
| REQ-PO-049 | §1, §3 |
| REQ-PO-050 | §4, §6 |
| REQ-PO-051 to REQ-PO-055 | §3 |

## 8. Change acceptance

Change the tool, this document, the [data dictionary §7](../data/data-dictionary.md#7-agent-tool-parameters-and-results), the requirements and the verification matrix together. Add a regression test with a minimal failing input for every new rule.

## Change history

| Version | Date | Commit | Change | Reviewed in |
|---|---|---|---|---|
| 0.1 | 2026-11-16 | feat/poodo-tools | Initial proposal | draft PR |
