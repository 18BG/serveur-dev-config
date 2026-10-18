---
name: acces-github
description: The reinstalled server (2026-10-18) has its own GitHub SSH key; git pull/push to ssakone/* works directly
metadata:
  type: reference
---

Since the reinstall on 2026-10-18, this server has a new GitHub SSH key (`~/.ssh/id_ed25519`, comment `root@vmi3661571`) added to the user's account (18BG). It can pull and push all `ssakone/*` repos; HTTPS URLs for `github.com/ssakone/` are rewritten to SSH (global git `insteadOf`), which the private submodules of buma_pro need.

The remote is `git@github.com:ssakone/bumo_backoffice.git`. Server setup lives in the private repo 18BG/serveur-dev-config (clone in ~/repos). The user sometimes pushes from their own computer: check `git log origin/<branch>` and `git reflog` before saying a commit is missing.

Before the reinstall the old server had no key (see [[serveur-pirate-octobre-2026]]); the keys `server-dev-vps` and `bumo-vps-temporaire` were revoked and must never be reused.
