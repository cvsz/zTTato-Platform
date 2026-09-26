# Security Policy

Security reports are treated as engineering work and should be handled with care, reproducibility, and minimal unnecessary exposure.

This file defines ZeaZDev's organization-wide default. A repository-specific `SECURITY.md` takes precedence when present.

## Reporting a Vulnerability

Please avoid filing a public issue for a vulnerability that could be exploited before maintainers have had a reasonable opportunity to assess and remediate it.

Preferred reporting order:

1. Use GitHub Private Vulnerability Reporting when it is enabled for the affected repository.
2. Follow the repository-specific private reporting instructions, if present.
3. If neither mechanism exists, contact the maintainers through a private channel documented by that repository or organization.

Do not include real production secrets, credentials, private customer data, access tokens, personal data, or destructive proof-of-concept payloads unless explicitly requested through a secure channel.

## What to Include

A useful report includes:

- affected repository and component;
- affected version, tag, branch, or commit when known;
- vulnerability class and concise impact statement;
- prerequisites required to exploit the issue;
- minimal, safe reproduction steps;
- expected versus observed behavior;
- relevant logs or traces with sensitive values redacted;
- whether exploitation crosses authentication, authorization, tenant, filesystem, network, or privilege boundaries;
- suggested mitigation if you have one.

## Security Areas We Care About

Examples include:

- authentication and session vulnerabilities;
- broken authorization or tenant isolation;
- remote code execution or command injection;
- SQL/NoSQL/template/LDAP or other injection;
- path traversal and filesystem escape;
- unsafe file upload/download behavior;
- SSRF and unintended network access;
- XSS, CSRF, open redirects, or origin-policy bypasses;
- secrets exposure;
- insecure cryptography or token handling;
- privilege escalation;
- dependency or supply-chain compromise;
- CI/CD or release-pipeline compromise;
- container or infrastructure isolation failures;
- insecure defaults that expose services unexpectedly;
- AI/agent tool-boundary bypass, unsafe data mutation, or permission bypass.

## Our Handling Principles

When assessing a report, maintainers should aim to:

- reproduce before changing behavior;
- identify the exact trust boundary involved;
- add regression coverage where practical;
- prefer minimal fixes that close the boundary without weakening unrelated controls;
- review similar code paths for the same vulnerability class;
- validate affected supported versions;
- document upgrade or mitigation guidance;
- preserve evidence for release and incident review.

## Coordinated Disclosure

We support responsible, coordinated disclosure. Publication timing should allow a reasonable opportunity for remediation and user upgrade guidance, while recognizing that severe actively exploited vulnerabilities may require accelerated action.

## Supported Versions

Supported versions vary by repository. Check release documentation, maintained branches, or repository-specific security policy for the authoritative support window.

## Secrets and Credentials

If you discover a committed credential or secret:

1. treat the credential as compromised;
2. rotate/revoke it through the appropriate provider;
3. remove or redact it from current code and documentation;
4. assess whether repository-history rewriting is necessary;
5. inspect logs and usage where appropriate;
6. add preventive scanning or policy controls when practical.

Deleting a secret from the latest commit alone is not sufficient remediation.

## Safe Research

Do not intentionally degrade service availability, destroy data, access data you are not authorized to access, persist access, or pivot into unrelated systems while testing a suspected vulnerability.

Thank you for helping improve the security of ZeaZDev projects.
