# Working on POODO

POODO is an explicit-invocation reasoning and orchestration skill for Codex and
Agent Skills clients, licensed GPL-3.0-only. Start with [README.md](README.md) and
[CONTRIBUTING.md](CONTRIBUTING.md). [SKILL.md](SKILL.md) defines the packaged
method; structural checks do not establish behavioral improvement.

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Skill entry point, invariants, and method contract |
| `references/` | Phase guidance, evidence rules, continuity, and evaluation design |
| `agents/openai.yaml` | Codex metadata and explicit invocation policy |
| `assets/` | Mega Observe charter template |
| `scripts/` | Package and continuation capsule validators |
| `evals/` | Behavioral cases, rubric, protocol, run-record template, and checker tests and fixtures |
| `examples/` | Synthetic illustrative scenarios |
| `docs/` | Engineering records and guides; start at `docs/README.md` |
| `.github/` | CI workflow, contribution templates, ownership, and repository automation |
| `requirements-dev.txt` | Pinned Python development dependency |

## Local checks

Run from the checkout root. [The CI workflow](.github/workflows/checks.yml) runs
these checks on Python 3.10 and 3.14. Use an environment for each version when
checking compatibility with the full matrix.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_skill.py
python -m unittest discover -s evals -p 'test_*.py' -v
python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml
```

Report the Python version, commands run, results, and untested outcomes. These
checks validate package and capsule structure and checker regressions; they do
not run a behavioral evaluation.

## Change rules

- Subtract first: remove unnecessary material before adding new machinery.
- Keep PRs small and focused on one concern. Explain the concrete problem and
  resulting behavior.
- Do not add code comments. Keep code clear and put explanations in documentation.
- Make only measured or cited claims. Separate observations from assumptions and
  suspected causes; keep behavioral improvement unmeasured without trial evidence.
- Do not include personal data or secrets. Keep examples synthetic and sanitize
  fixtures, traces, paths, and conversation records before publication.
- Follow the existing `docs/` layout: `requirements/` for requirements,
  `architecture/` for design and boundaries, `icd/` for interface contracts,
  `verification/` for coverage and results, and `configuration/` for versions,
  pins, and baselines. Put tutorials, how-to guides, references, and explanations
  under the corresponding `docs/guides/` directory.
- Preserve explicit invocation and the boundary between the standard method and
  optional modes unless the change explicitly proposes a method revision.
- For checker fixes, include a minimal failing input and meaningful regression
  assertions. Follow the evaluation guide for behavioral claims.
