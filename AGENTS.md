# AGENTS.md

Notes for coding agents working in this repository.

## What this repo is

POODO is an agent skill (`SKILL.md` + `references/` + `agents/openai.yaml`), not a library. `SKILL.md` is the authoritative contract. README and docs explain it; they never override it.

## Rules

- **Keep explicit invocation.** `agents/openai.yaml` must keep implicit invocation disabled. Don't change the method text, loop order or continuation schema without a clearly labelled method revision and a version bump in `SKILL.md` frontmatter.
- **No unmeasured claims.** Structural checks passing is not behavioral evidence. Don't write "improves", "better" or thresholds as adopted facts unless a run record under `evals/` supports it.
- **Synthetic examples only.** No secrets, private paths, customer details or real conversation logs in `examples/`, `evals/` or docs.
- **Changelog.** User-visible changes get a bullet under the top `## Unreleased` heading in `CHANGELOG.md`. Releases rename that heading to `## <version> — <title> — YYYY-MM-DD`.
- **Commits.** Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`, `build(deps):`, with a scope where useful (`fix(capsule): …`). One logical change per PR.

## Before you push

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate_skill.py
python -m unittest discover -s evals -p 'test_*.py' -v
python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml
```

CI (`.github/workflows/checks.yml`) runs the same commands on Python 3.10 and 3.14. For checker fixes, add a minimal failing fixture and a regression test.
