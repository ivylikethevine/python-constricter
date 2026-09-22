# Security

Report a vulnerability privately through GitHub's [private vulnerability reporting](https://github.com/ivylikethevine/python-constricter/security/advisories/new), not in a public issue. Only the latest release gets fixes.

constricter only reads the files it's given: it parses them with `ast` and never imports or runs them. It has no runtime dependencies. Releases are built in CI from hash-pinned tools, with build provenance attestations.
