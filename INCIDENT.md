# Incident du 16–17 octobre 2026 — VPS 169.58.219.108

## Résumé

Des robots ont deviné le **mot de passe root**, qui était faible. La connexion SSH par mot de passe était ouverte, avec `PermitRootLogin yes` et `PasswordAuthentication yes`. Le journal compte plus de 27 000 tentatives ratées.

Une fois root, ils ont installé un bot de la famille « BillGates », qui sert aux attaques DDoS, et un mineur de cryptomonnaie. Ils ont aussi tout mis en place pour garder la machine.

## Chronologie (heure de Paris)

| Date | Adresse | Événement |
|---|---|---|
| 13–14 oct. | 74.244.87.75 (Bamako, Starlink) | Connexions légitimes du propriétaire |
| 16 oct. 00:30 | 185.125.246.13 (Téhéran) | Première connexion root du pirate |
| 16 oct. 02:01 | 94.26.104.43 (Seychelles) | Connexion root. À 02:04–02:09 : installation du bot, des lanceurs dans 28 scripts `/etc/init.d` et du camouflage `/etc/profile.d/gateway.sh` |
| 17 oct. 12:13 | 77.239.124.152 (Pays-Bas) | Clés SSH remplacées (« ElPatrono1337 »), comptes `node` et `ubuntu` piégés, mot de passe root changé, faux `passwd`, `ps`, `ss`, `lsof`, mineur dans `/var/tmp` |
| 17 oct. 22:00–22:35 | | Nettoyage (voir ci-dessous) |

## Ce que le pirate avait mis en place

- **Programmes** :
  - le bot : `/etc/kswpad`, `/usr/bin/.sshd`, `/usr/bin/bsd-port/getty`, `/lib/systemd/system/kswpad` ;
  - une deuxième copie du bot : `/usr/lib/system.mark`, `/boot/system.pub`, `/etc/profile.d/bash.cfg` ;
  - `/tmp/cache` et `/usr/lib/libgdi.so.0.8.2` ;
  - le mineur : `/var/tmp/<8 caractères hexa>/` ;
  - un voleur de mots de passe : `/var/tmp/sniff`.
- **Relances** :
  - `/etc/crontab`, avec `/.mod` lancé toutes les minutes ;
  - la crontab de root ;
  - `myservices.service`, qui lance `/usr/bin/ssshd`, un script qui retélécharge le malware sur `195.24.237.240` et `digital.digitaldatainsights.org` ;
  - les scripts `DbSecuritySpt`, `selinux` et `dns-udp4` dans `/etc/init.d`, avec leurs liens `rc*.d` ;
  - 123 lignes `/lib/system.mark` ajoutées à 28 scripts `/etc/init.d` ;
  - `/etc/profile.d/bash.cfg.sh`.
- **Camouflage** : `/etc/profile.d/gateway.sh` redéfinissait `ls`, `ps`, `ss`, `find`, `lsof` et `dir` pour cacher ses fichiers. Les programmes `passwd` (faux changement de mot de passe), `ps`, `ss` et `lsof` étaient remplacés.
- **Accès** :
  - sa clé RSA (`SHA256:AkrAM6Cdbkqok1OHU527WzpYGQqPQJrubcEP9Dlj7yI`) dans root et ubuntu, avec le fichier rendu non modifiable par `chattr +ia` ;
  - un compte `node` avec sudo sans mot de passe ;
  - le mot de passe de `ubuntu` changé, et sudo sans mot de passe pour ce compte.

## Nettoyage effectué

1. Clé du pirate remplacée par la clé du propriétaire, comptes `node` supprimé et `ubuntu` verrouillé.
2. Mot de passe root aléatoire, connu de personne. SSH par clé uniquement.
3. Programmes du pirate gelés puis tués, et leurs relances supprimées avant de les tuer.
4. Fichiers supprimés. Leurs empreintes sont dans `/root/incident-2026-10-17/malware-sha256.txt` sur l'ancien serveur.
5. `passwd`, `procps`, `iproute2` et `lsof` réinstallés. Les 28 scripts `/etc/init.d`, `sysctl.conf` et les scripts `ssh` et `procps` remis à l'original. `dpkg -V` ne signale plus rien sur les paquets touchés.

Le pirate a été root pendant environ deux jours. La machine a donc été **réinstallée** plutôt que gardée.

## À faire après un tel incident

- Supprimer de GitHub toute clé qui était sur le serveur. C'est fait pour `server-dev-vps` et `bumo-vps-temporaire`.
- Regénérer les secrets qui étaient sur le serveur : `.env`, jetons, mots de passe de base de données et d'admin, connexions Claude et relais.
- Ne jamais réutiliser le mot de passe tapé dans le faux `passwd`.
