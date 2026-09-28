# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 7.9.x   | yes       |
| < 7.9   | no        |

## Reporting a Vulnerability

If you discover a security issue in this tool, please do not open a public
GitHub issue. Instead:

1. Email the maintainer (contact info in README).
2. Or open a **private security advisory** via GitHub:
   https://github.com/temidev1/hashbreak-toolkit/security/advisories/new

Include:
- a description of the issue
- steps to reproduce
- the affected version and platform
- any proposed fix, if you have one

## Response Timeline

- **acknowledgement** within 72 hours
- **initial assessment** within 7 days
- **fix or mitigation plan** within 30 days for valid reports

## Scope

This tool is intended for:
- authorized penetration testing
- capture-the-flag competitions
- security research on systems you own or have permission to test
- password auditing of your own systems

It is NOT intended for unauthorized access to systems or accounts.

Users are solely responsible for ensuring they have proper authorization
before using any feature of this tool against a target.

## Out of Scope

The following are not considered vulnerabilities in this project:

- the tool successfully cracking a hash (that is the intended function)
- the tool scanning a host that responded to a network probe
- users misusing the tool against systems they do not own
- third-party services used for online hash lookup (md5.gromweb.com, md5decrypt.net)

## Contact

See the README for the current maintainer's contact information.
