---
name: Problem report
about: Report a reproducible failure in the skill, validators, or documentation
labels: ["bug"]
---

<!-- Problem report (SWEHB 5.01 tailored). Report security vulnerabilities privately to craig@nh3.biz instead of opening a public issue. Do not include secrets, customer data, or private conversation records. -->

## Affected item and configuration

- Component: skill instructions / references / validator / capsule checker / docs / other
- Commit or version:
- Agent host and version, if applicable:
- Python version, if using validators:
- Operating system:

## Expected behavior

Describe the intended outcome and what would demonstrate it.

## Actual behavior

Describe what you observed. Separate the observation from a suspected cause.

## Reproduction

Provide minimal steps and a synthetic or sanitized input. Attach the full validator output if relevant.

## Severity (your assessment)

- [ ] S1 wrong result presented as valid (for example a validator passing malformed input), data loss, or security exposure
- [ ] S2 feature unusable, no workaround
- [ ] S3 degraded, workaround exists
- [ ] S4 cosmetic or documentation

## Workaround

## Found during

<!-- use, development, test, review, release audit -->

## Verification

List commands or checks run, their results, and what remains untested. Passing structural checks do not establish behavioral correctness.

---

### Maintainer section (fill on triage and closure)

- Disposition: accepted / rejected (reason) / duplicate
- Analysis and corrective action:
- Verified by: PR #, test name or matrix row
- Released in:
