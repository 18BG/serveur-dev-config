---
name: git-pull-github-indisponible
description: git pull/fetch to GitHub fails from this server (no SSH key); the user pulls themselves
metadata:
  node_type: memory
  type: reference
  originSessionId: f62e308e-c1c7-4609-901d-87f4b48a7040
  modified: 2026-10-17T18:02:01.446Z
---

The remote is `git@github.com:ssakone/bumo_backoffice.git`. From this server, `git pull` fails with "Host key verification failed" (no GitHub SSH key in ~/.ssh). The user sometimes pulls on their own: check `git log origin/<branch>` and `git reflog` before saying a commit is missing.
