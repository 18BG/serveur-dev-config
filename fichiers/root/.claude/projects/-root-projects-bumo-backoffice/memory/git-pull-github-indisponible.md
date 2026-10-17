---
name: git-pull-github-indisponible
description: git pull/fetch to GitHub fails from this server (no SSH key); the user pulls themselves
metadata:
  node_type: memory
  type: reference
  originSessionId: f62e308e-c1c7-4609-901d-87f4b48a7040
  modified: 2026-10-17T18:02:01.446Z
---

The remote is `git@github.com:ssakone/bumo_backoffice.git`. The server was compromised in Oct 2026 (see [[serveur-pirate-octobre-2026]]); its GitHub key was revoked. A temporary key `bumo-vps-temporaire` was used once on 2026-10-17 to push, then deleted. Server setup lives in the private repo 18BG/serveur-dev-config. The user sometimes pulls on their own: check `git log origin/<branch>` and `git reflog` before saying a commit is missing.
