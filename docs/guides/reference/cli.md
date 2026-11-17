# Command reference

Every command runs from the checkout root with Python 3.10 or newer and PyYAML 6.0.3 installed (`python -m pip install -r requirements-dev.txt`). None needs a model, an API key or network access, except that `tools/gen_release_docs.py` calls `gh` when it is available. Output below was captured on 2026-11-08 with Python 3.14.9, except the `poodo_tools.py` section, captured on 2026-11-16 with Python 3.13 on macOS.

## `validate_skill.py`

Checks the package that contains it. Takes no arguments.

```sh
python scripts/validate_skill.py
```

| Exit | Output |
|---|---|
| 0 | `POODO structural checks passed; behavioral correctness remains untested.` |
| 1 | `POODO structural checks failed:` then one `- <problem>` line per problem |

It checks: the 19 required files; SKILL.md front matter (`name: poodo`, `metadata.version: "3.1"`); `agents/openai.yaml` (short description 25–64 characters, `$poodo` in the default prompt, implicit invocation off); every relative `.md` link in SKILL.md and `references/*.md`; no `TODO`, `<TODO>` or `<TBD>` in those files; the three continuation-schema literals in `references/continuity-and-ledger.md`; and execute permission on both scripts.

Messages it can print:

| Message | Cause |
|---|---|
| `missing required file: <path>` | A required file is absent |
| `SKILL.md has no YAML frontmatter` / `SKILL.md frontmatter is not a mapping` | Front matter missing or malformed |
| `frontmatter name must be poodo` | Wrong `name` |
| `frontmatter metadata.version must be 3.1` | Wrong method version |
| `openai.yaml short_description must be 25-64 characters` | Length out of range |
| `openai.yaml default_prompt must mention $poodo` | Prompt lacks the invocation |
| `POODO must remain explicit-only` | `allow_implicit_invocation` is not `false` |
| `invalid agents/openai.yaml: <error>` | YAML error or wrong shape |
| `broken reference in <file>: <target>` | A relative `.md` link does not resolve |
| `unfinished placeholder in <file>` | A placeholder token is present |
| `continuation schema missing <literal>` | A schema literal is missing |
| `script is not executable: <path>` | Execute bit missing |

Example failure, run against a copy with SKILL.md set to version 3.2 and `evals/protocol.md` removed:

```text
POODO structural checks failed:
- missing required file: evals/protocol.md
- frontmatter metadata.version must be 3.1
```

## `check_capsule.py`

```text
usage: check_capsule.py [-h] [--hard-token-ceiling HARD_TOKEN_CEILING] capsule

Check POODO capsule format and referential integrity. Passing does not
establish truth.

positional arguments:
  capsule

options:
  -h, --help            show this help message and exit
  --hard-token-ceiling HARD_TOKEN_CEILING
```

| Exit | Stream | Output |
|---|---|---|
| 0 | stdout | `POODO capsule structure passed; epistemic and behavioral correctness remain untested.` |
| 1 | stderr | `INVALID POODO capsule structure:`, one `- <field path>: <reason>` line per error, then `No judgment about epistemic truth was performed.` |
| 2 | stderr | `INVALID: could not load capsule: <reason>` (unreadable file, bad UTF-8, YAML error, duplicate key, non-string key) |

Pass the YAML payload only, without the `POODO_CONTINUATION_V3_0` delimiters. The default ceiling is 1,800 approximate tokens, counted as (characters + 3) // 4. An oversize capsule passes the size check only if it declares a non-blank `capsule_overflow`. To inspect a larger capsule without that declaration, raise the ceiling on purpose:

```sh
python scripts/check_capsule.py path/to/capsule.yaml --hard-token-ceiling 2400
```

Example runs at the baseline:

```text
$ python scripts/check_capsule.py evals/fixtures/invalid-truncated-evidence.yaml
INVALID POODO capsule structure:
- evidence_bundles[0].supports_claims: partial or truncated evidence cannot support a capsule claim
- current_head: must reference an orientation, decision, prediction, or contradiction
No judgment about epistemic truth was performed.
$ python scripts/check_capsule.py nonexistent.yaml
INVALID: could not load capsule: [Errno 2] No such file or directory: 'nonexistent.yaml'
```

The fields and allowed values are in the [data dictionary](../../data/data-dictionary.md). The interface is in the [capsule checker ICD](../../icd/icd-capsule-checker.md).

## `poodo_tools.py`

Agent tools: the same five structural checks as a stdio MCP server and as subcommands. The full contract, including every rule and bound, is in the [agent tools ICD](../../icd/icd-agent-tools.md).

```text
usage: poodo_tools.py [-h] [--json] {serve,check-capsule,precommit-hash,orient-paths-check,research-gate-check,terminal-claim-check} ...
```

| Subcommand | What it checks |
|---|---|
| `serve` | Runs the MCP server on standard input and output (newline-delimited JSON-RPC 2.0) until end of input |
| `check-capsule FILE [--hard-token-ceiling N]` | The capsule checker's rules; also accepts a payload wrapped in both continuation delimiters |
| `precommit-hash FILE [--record] [--name NAME] [--receipt FILE]` | SHA-256 of the file's exact bytes and a `<digest>  <name>` receipt line, as `sha256sum` writes it; `--record` hashes a JSON or YAML record as canonical JSON instead; `--receipt` compares with recorded digests |
| `orient-paths-check FILE` | `{paths: [{name, mechanism}, ...]}`: exactly 20 entries with no duplicates; near-duplicates are warnings |
| `research-gate-check FILE` | An Observe research record: queries, at least two dated sources with URLs, conflicts, non-entailments |
| `terminal-claim-check FILE` | The five terminal-claim fields, and unqualified fixed, resolved, successful or validated without a passed criterion |

| Exit | Output |
|---|---|
| 0 | `<tool>: pass` (or `ok`), warnings, then the disclaimer |
| 1 | `<tool>: fail`, one `- error: <reason>` line per error, warnings, then the disclaimer |
| 2 | `<tool>: error` and the rejected-input reason |

`--json` (before the subcommand) prints the full result object instead. Example:

```text
$ python scripts/poodo_tools.py precommit-hash evals/fixtures/tools/PRECOMMIT.md --name PRECOMMIT.md
precommit_hash: ok
sha256: 8fed6bf28474ce5cc3c00c658e2b7852aa4d8b20660fa04d8ba88eb349599dc1
receipt_line: 8fed6bf28474ce5cc3c00c658e2b7852aa4d8b20660fa04d8ba88eb349599dc1  PRECOMMIT.md
A digest binds exact bytes only. It does not show that the precommit was written before observation, that its content is sound, or that anything it predicts happened.
$ python scripts/poodo_tools.py orient-paths-check evals/fixtures/tools/orient-20-paths.json
orient_paths_check: pass
Structural check only: a pass is not a truth or quality judgement. Structural conformance is not runtime validation.
```

To give an MCP host the tools, register `python /path/to/poodo/scripts/poodo_tools.py serve` as a stdio server.

## `tools/check_trace.py`

Documentation trace and link check, run in CI.

```text
usage: check_trace.py [-h] [--root ROOT] [--json]
```

`--root` points at another checkout (default: the one containing the script). `--json` prints counts and errors as JSON. Exit 0 prints `trace check passed`; exit 1 prints one line per error, then `trace check failed`. The rules are in the [verification matrix](../../verification/verification-matrix.md#how-to-read-this-matrix).

## `tools/gen_release_docs.py`

Writes `docs/releases/VDD-main-<short commit>.md` and `docs/verification/reports/STR-main-<short commit>.md`.

```text
usage: gen_release_docs.py [-h] --python PYTHON [--allow-dirty]
```

Give `--python` once per interpreter to test with. It refuses a tree with uncommitted tracked changes (exit 2) unless `--allow-dirty` is set. Exit 0 means every suite and the trace check passed; exit 1 means at least one failed (the files are still written). See TP-3 in the [test plan](../../verification/test-plan.md#tp-3--generate-the-release-documents).
