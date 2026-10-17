---
name: serveur-pirate-octobre-2026
description: "The VPS (169.58.219.108) was taken over through a weak root password on 16–17 Oct 2026, then cleaned; SSH is now key-only, reinstalling is still advised"
metadata:
  node_type: memory
  type: project
  originSessionId: f62e308e-c1c7-4609-901d-87f4b48a7040
  modified: 2026-10-17T20:36:07.506Z
---

On 16 Oct 2026 at 00:30, bots guessed the weak root SSH password; the IPs were in Iran, the Seychelles and the Netherlands.

What the attacker did:
- installed the "BillGates"-type DDoS bot: /etc/kswpad, /usr/bin/.sshd, /usr/bin/bsd-port, /usr/lib/system.mark, /boot/system.pub, /etc/profile.d/bash.cfg;
- installed a miner in /var/tmp/<hex>;
- replaced passwd, ps, ss and lsof with fakes;
- added /etc/profile.d/gateway.sh, which wraps ls, ps, find… to hide its files;
- injected `/lib/system.mark` lines into 28 /etc/init.d scripts;
- added persistence through cron and myservices.service;
- created a backdoor user `node`, took over `ubuntu`, and changed the root password.

Cleaned on 17 Oct (22:00–22:35). Evidence and hashes are in /root/incident-2026-10-17/.

Current state:
- root logs in with the user's key `babry-ordi` only;
- PasswordAuthentication no, PermitRootLogin prohibit-password;
- the root password is random and unknown to anyone;
- rac-agent, android-emu-reaper and google-maven-proxy are the user's own legitimate services.

**Why:** an attacker who had root for about 2 days may have left something the scan missed, and every secret stored on this server should be treated as leaked.
**How to apply:**
- Never put a GitHub key or other secrets on this server until it is reinstalled.
- Bypass shell functions (`unset -f ls ps find`, or use /usr/bin/...) when investigating.
- The GitHub key `server-dev-vps` was revoked by the user. See [[git-pull-github-indisponible]].
