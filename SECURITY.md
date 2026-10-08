# Security Policy

This repository is an offline reference implementation for cost gates. It must
not contain live pricing credentials, billing account data, provider keys,
customer telemetry, or real financial claims.

## Supported Scope

- Deterministic task-provided estimates.
- Local tool fixtures only.
- Explicit no-fake-savings policy.
- Local validation through `make validate`.

## Reporting

Before publishing, route security concerns through the repository maintainer.
Any live credential, billing identifier, or unsupported financial claim should
block release.

