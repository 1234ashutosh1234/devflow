# Security Policy

DevFlow handles GitHub repository information, pull-request changes, webhook events, and authenticated API requests. Security reports help keep the project and its users safe.

## Supported Versions

Until versioned releases are published, security fixes are made against the latest code on the `main` branch. Older commits, forks, and independently maintained deployments may not receive security updates.

| Version | Security updates |
| --- | --- |
| Latest code on `main` | Supported |
| Older commits and unreleased snapshots | Not guaranteed |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues, Discussions, or pull requests.** Public reports can expose users before a fix is available.

1. Open the [DevFlow repository](https://github.com/1234ashutosh1234/devflow).
2. Select the **Security** tab.
3. Choose **Report a vulnerability** (GitHub private vulnerability reporting) and submit a private report.
4. Include enough detail for the maintainer to understand and reproduce the issue safely.

If the private reporting option is not available, contact the maintainer through the [GitHub profile](https://github.com/1234ashutosh1234) and ask for a private reporting channel. Do not include exploit details, credentials, personal data, or a proof of concept in a public message.

### What to include

Where possible, provide:

- A concise description of the vulnerability and its potential impact.
- The affected version, commit, endpoint, or component.
- Clear reproduction steps and any required configuration.
- A minimal proof of concept that does not access other users' data or damage systems.
- Relevant logs or screenshots after removing tokens, passwords, personal information, and other secrets.
- Any suggested mitigation, if known.

Please do not attach live credentials, private repository data, or production user information.

## Areas of particular interest

Reports related to the following DevFlow components are especially useful:

- Authentication, JWT handling, session management, and authorization checks.
- GitHub access tokens, permissions, and repository access boundaries.
- GitHub webhook signature verification and event handling.
- Pull-request diff parsing, automated review processing, and publishing review comments.
- API input validation, data isolation, and access to stored project or review information.
- Secret management, configuration, dependencies, and deployment settings.

This list is not exhaustive. Please report any security issue that could affect DevFlow or its users.

## What happens after a report

The maintainer will review the report, attempt to validate the issue, assess its impact, and determine an appropriate fix or mitigation. When appropriate, the maintainer will coordinate a fix and public disclosure so users have a reasonable opportunity to update.

DevFlow is maintained independently. A response or resolution time is not guaranteed, but responsible reports will be considered carefully. Please avoid public disclosure until the issue has been assessed and a coordinated disclosure plan has been agreed.

## Good-faith security research

Please:

- Test only systems and accounts that you own or are explicitly authorized to test.
- Avoid accessing, changing, or deleting another user's data.
- Avoid denial-of-service testing, spam, social engineering, and actions that disrupt services.
- Stop testing and report the issue if you encounter data that does not belong to you.
- Keep vulnerability details private while the maintainer investigates.

Thank you for helping improve DevFlow's security.
