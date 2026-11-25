---
description: Reviews Sloperator for bugs and missing regression coverage
mode: primary
steps: 2
permissions:
  - action: "*"
    resource: "*"
    effect: deny
  - action: read
    resource: "*"
    effect: allow
  - action: glob
    resource: "*"
    effect: allow
  - action: grep
    resource: "*"
    effect: allow
---

# Review

Inspect the relevant code and tests. Report concrete bugs and missing regression coverage with file references. Suggest focused fixes without changing files.
