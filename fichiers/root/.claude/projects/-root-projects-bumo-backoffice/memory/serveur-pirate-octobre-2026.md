---
name: serveur-pirate-octobre-2026
description: "The VPS (169.58.219.108) was taken over through a weak root password on 16–17 Oct 2026; it was reinstalled on 2026-10-18 with key-only SSH"
metadata:
  type: project
---

On 16 Oct 2026 bots guessed the weak root SSH password (IPs in Iran, the Seychelles and the Netherlands) and installed a "BillGates" DDoS bot, a miner, fake passwd/ps/ss/lsof and backdoor accounts. Details: INCIDENT.md in 18BG/serveur-dev-config.

The machine was reinstalled on 2026-10-18 (same IP), following that repo's README:
- root logs in with the user's key `babry-ordi` only; PasswordAuthentication no, PermitRootLogin prohibit-password (`/etc/ssh/sshd_config.d/00-cles-uniquement.conf`);
- ufw allows SSH only, fail2ban and unattended-upgrades are on;
- rac-agent and android-emu-reaper are the user's own legitimate services.

**Why:** brute-force attempts started within minutes of the reinstall; a single password login reopened is enough to lose the machine again.
**How to apply:**
- Never re-enable SSH passwords or open other ports; dev servers stay on 127.0.0.1.
- Secrets from the old server are considered leaked: regenerate, never copy them back. See [[acces-github]].
