# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead:

1. Use GitHub’s **[Private vulnerability reporting](https://github.com/Pooya-Ideas/markitdown-cli/security/advisories/new)** if available, or
2. Contact the repository owner via their GitHub profile.

Include:

- Description of the issue
- Steps to reproduce
- Affected versions / platforms
- Impact assessment (if known)

We aim to acknowledge reports within **7 days** and provide a status update within **14 days**.

## Scope

In scope:

- Code execution via malicious document conversion (when not expected)
- Path traversal when writing output files
- Unsafe handling of untrusted archives or embedded resources

Out of scope:

- Issues only present when running as administrator / root by choice
- Vulnerabilities in third-party dependencies that already have public CVEs (please report upstream; we will bump versions when fixes ship)
- Social engineering or physical attacks

## Safe Harbor

We support good-faith security research. We will not pursue legal action against researchers who:

- Avoid privacy violations, destruction of data, and service disruption
- Report findings promptly and privately
- Give us reasonable time to remediate before public disclosure
