# Operating manual

For coding agents working here, and for people. Read [CONTRIBUTING.md](CONTRIBUTING.md)
and the [setup and checks](docs/getting-started.md) before changing the repository.
These are contribution rules; the POODO reasoning method remains explicitly invoked.

## The loop

1. Describe the concrete problem, proposed behavior, and evidence that would show improvement.
2. Inspect the relevant instructions, references, validators, and evaluation cases.
3. Make the smallest change addressing that concern.
4. Run the local checks below and inspect the diff before committing.
5. Report exact commands, results, and untested outcomes in the pull request.

## Short rules

- Keep one concern per change and aim for fewer than 400 changed lines.
- Add no code comments. Explain contributor guidance in documentation.
- Never delete files. If relocation is essential, move them to `TODELETE/`; otherwise leave them.
- Never edit test expected results or fixtures. For checker fixes,
  include a minimal failing input and a regression test with meaningful assertions,
  following [CONTRIBUTING.md](CONTRIBUTING.md).
- Preserve explicit invocation and the existing method and optional-mode boundary.
  Identify a proposed method revision and explain its effects on evidence separation,
  authority, research, divergence, contradiction handling, and continuity.
- Keep client-specific capabilities conditional on actual availability.
- Use synthetic examples or material explicitly authorized for publication. Never
  commit secrets, personal data, private paths, customer details, or private traces.
- Use [craig@nh3.biz](mailto:craig@nh3.biz) as the only contact address in new guidance.
  Follow [SECURITY.md](SECURITY.md) for sensitive reports.
- Cite external foundations and preserve licenses for included third-party material.
- Make only measured or cited claims. Separate observations from suspected causes;
  structural checks do not establish behavioral improvement or successful outcomes.
- For behavioral claims, follow [docs/evaluation.md](docs/evaluation.md). Fix adopted
  thresholds and rubric applicability before examining trial outcomes.

## Local checks

Use Python 3.10 or newer. The [setup guide](docs/getting-started.md) and
[CI workflow](.github/workflows/checks.yml) reference a pinned `requirements-dev.txt`;
that file is absent from this revision. Report the setup gap rather than inventing
a dependency pin. The validators import PyYAML; record the Python and PyYAML versions
used when running with an existing environment.

From the checkout root, run each command:

```sh
python scripts/validate_skill.py
python -m unittest discover -s evals -p 'test_*.py' -v
python scripts/check_capsule.py evals/fixtures/valid-capsule.yaml
git diff --check
```

The [evaluation guide](docs/evaluation.md) describes what these checks establish.
Record failures and missing prerequisites honestly. Do not weaken checks or change
expected outcomes to obtain a pass. A local pass does not establish results on every
Python version in CI or substitute for a recorded behavioral evaluation.
