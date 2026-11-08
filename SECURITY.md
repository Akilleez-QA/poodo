# Security policy

## Report a vulnerability

Send suspected security vulnerabilities to craig@nh3.biz. Do not disclose vulnerability details in a public issue.

Include the affected commit or version, reproduction steps, the observed impact, and a minimal sanitized example. State whether the issue involves the skill instructions, validators, or a host integration. Do not include credentials, private conversation records, or customer data.

## Supported versions

No release has been tagged (`git tag --list` is empty). Only the current `main` branch is supported. Fixes land on `main`; older commits are not patched.

| Version | Supported |
| --- | --- |
| `main` (method 3.1) | Yes |
| Any earlier commit | No |

## Security posture

- The validators read local files only. They make no network connections, write no files and start no subprocesses. YAML is parsed with `yaml.safe_load` or a `SafeLoader` subclass, and the capsule checker refuses duplicate and non-string keys.
- The skill grants no authority beyond the user's instructions. Host permissions and available tools decide what an agent can do; the skill's authority rule is an instruction to the model, not an enforced control.
- Mega Observe can spend large amounts of model and search budget. The bundled charter is a plan, not a billing cap.
- Secret scanning (`.gitleaks.toml`, default rules) and static analysis are run by hand and recorded in the [assurance record](docs/assurance/assurance-record.md); they are not CI gates.

A structural check does not establish safe behavior by an agent or its host. See [Limitations and safety-relevant use](docs/guides/explanation/limitations.md).

## Updates

This policy does not specify a response deadline. Include the exact affected revision so the report can be assessed against the source.
