# Security reporting

Report suspected POODO vulnerabilities privately to [craig@nh3.biz](mailto:craig@nh3.biz).
Do not put exploitable vulnerability details, credentials, personal data, or private
agent transcripts in a public issue or pull request.

Useful report information includes:

- The affected commit or version and the relevant instruction, reference, or validator.
- A minimal reproduction using synthetic data and an environment you control.
- Expected versus actual behavior and the security impact.
- Any suggested mitigation, without disclosing third-party secrets.

Limit testing to systems and data you own or are authorized to assess. Installing
POODO does not authorize testing a host, model provider, or third-party service.
Discuss disclosure with the maintainer before publishing working exploit details.

Use the latest `main` revision as the starting point for reproductions and identify
the exact revision tested. This policy promises no supported-version window,
response deadline, or vulnerability bounty. Check actual commits and releases for
fix availability. Ordinary correctness bugs without sensitive security implications
can use [Issues](https://github.com/Akilleez-QA/poodo/issues).
