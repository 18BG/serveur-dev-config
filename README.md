# Serveur de développement — configuration

Ce dépôt permet de remonter le serveur de développement : web (React, Vite), mobile (Flutter, React Native, Android) et les sessions Claude Code pilotées par relais.dev.

L'ancien serveur (VPS Contabo, Ubuntu 24.04, 4 CPU, 8 Go de RAM, 96 Go de disque) a été piraté en octobre 2026. La cause : un mot de passe root faible, ouvert à tout Internet. Voir [INCIDENT.md](INCIDENT.md).

**Règle n° 1 : connexion par clé SSH uniquement, jamais par mot de passe.**

`fichiers/` reproduit l'arborescence du serveur. Chaque fichier se copie à l'emplacement indiqué par son chemin, par exemple `fichiers/usr/local/bin/android-emu` vers `/usr/local/bin/android-emu`.

---

## 1. Installer et sécuriser (avant tout le reste)

1. Dans le panneau de l'hébergeur, réinstaller **Ubuntu 24.04**. **Ajouter la clé SSH publique** de l'ordinateur personnel (`~/.ssh/id_ed25519.pub`) au moment de l'installation.
2. Se connecter avec `ssh root@IP`. Aucun mot de passe ne doit être demandé.
3. Couper les mots de passe SSH :
   ```bash
   cat > /etc/ssh/sshd_config.d/00-cles-uniquement.conf <<'EOF'
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   PermitRootLogin prohibit-password
   EOF
   sshd -t && systemctl reload ssh
   sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'   # no / without-password
   ```
   Les fichiers de `/etc/ssh/sshd_config.d/` sont lus par ordre alphabétique et **la première valeur gagne**. Le préfixe `00-` passe donc avant le `50-cloud-init.conf` de l'image, qui remettait `PasswordAuthentication yes`.
4. Ouvrir un **second terminal** et vérifier que `ssh root@IP` marche encore avant de fermer le premier.
5. Pare-feu : ne laisser passer que SSH. Les serveurs de dev (Vite, Metro…) restent sur `127.0.0.1`.
   ```bash
   ufw allow OpenSSH && ufw --force enable && ufw status
   ```
6. Appliquer les mises à jour de sécurité automatiquement :
   ```bash
   apt update && apt -y full-upgrade && apt -y install unattended-upgrades
   dpkg-reconfigure -f noninteractive unattended-upgrades
   ```
7. Facultatif : `apt -y install fail2ban`. Les robots ne peuvent plus deviner de mot de passe, mais fail2ban allège les journaux.

## 2. Outils de développement

Versions installées sur l'ancien serveur :

| Outil | Version | Emplacement |
|---|---|---|
| Node.js (nvm 0.40.8) | 24.x LTS | `~/.nvm` |
| Flutter | 3.47.x, canal stable | `~/development/flutter` |
| Java (OpenJDK) | 17 | `/usr/lib/jvm/java-17-openjdk-amd64` |
| Android SDK | platforms 34, 35, 36 ; build-tools 35.0.0, 36.0.0 ; platform-tools, cmdline-tools, ndk, cmake | `~/Android/Sdk` |
| Docker | 29.x | paquet `docker-ce` |
| Go | 1.25 | `/usr/local/go` |
| Python | 3.12 (celui d'Ubuntu) | |
| Playwright | Chromium, Firefox, WebKit | `~/.cache/ms-playwright` |

```bash
apt -y install git curl unzip zip xz-utils build-essential python3-venv python3-pip \
  openjdk-17-jdk clang cmake ninja-build pkg-config libgtk-3-dev
# Node
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
. ~/.nvm/nvm.sh && nvm install --lts && nvm alias default 'lts/*'
# Flutter
mkdir -p ~/development && git clone -b stable https://github.com/flutter/flutter.git ~/development/flutter
# Android SDK : cmdline-tools dans ~/Android/Sdk/cmdline-tools/latest, puis
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0" "ndk;<version>" "cmake;<version>"
flutter doctor --android-licenses
# Docker : https://docs.docker.com/engine/install/ubuntu/
# Playwright (depuis un projet qui l'utilise)
npx playwright install --with-deps chromium firefox webkit
```

Variables d'environnement : copier `fichiers/root/.dev-env.sh` vers `~/.dev-env.sh` et ajouter en tête de `~/.bashrc` :

```bash
[ -f ~/.dev-env.sh ] && . ~/.dev-env.sh
```

Ce fichier règle nvm, `JAVA_HOME`, `ANDROID_HOME`, Flutter et `SDK_TEST_BASE_URL`. Les sessions Claude Code le chargent aussi, via `CLAUDE_ENV_FILE`.

## 3. Proxy Maven Google (Gradle)

`dl.google.com` bloquait les gros téléchargements depuis l'ancien serveur. Gradle passe donc par un petit proxy local sur `127.0.0.1:8765`. Sur un nouveau serveur, vérifier d'abord si c'est encore utile : `./gradlew build` sur un projet Flutter.

```bash
mkdir -p /opt/google-maven-proxy && cp fichiers/opt/google-maven-proxy/proxy.py /opt/google-maven-proxy/
cp fichiers/etc/systemd/system/google-maven-proxy.service /etc/systemd/system/
mkdir -p ~/.gradle/init.d && cp fichiers/root/.gradle/init.d/google-maven-mirror.gradle ~/.gradle/init.d/
systemctl daemon-reload && systemctl enable --now google-maven-proxy
```

## 4. Émulateur Android partagé (Redroid)

Un seul Android 14 dans Docker, partagé par toutes les sessions. Il se pilote uniquement par `android-emu` (`android-emu help`). Les règles des agents sont dans `fichiers/root/.claude/rules/emulateur-android.md`.

```bash
apt -y install linux-modules-extra-$(uname -r) adb
cp fichiers/etc/modules-load.d/redroid.conf /etc/modules-load.d/
cp fichiers/etc/modprobe.d/redroid.conf /etc/modprobe.d/
modprobe binder_linux devices=binder,hwbinder,vndbinder
docker pull redroid/redroid:14.0.0_64only-latest
install -m 755 fichiers/usr/local/bin/android-emu /usr/local/bin/android-emu
cp fichiers/etc/systemd/system/android-emu-reaper.{service,timer} /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now android-emu-reaper.timer
android-emu doctor   # vérifie module binder, Docker, image, adb
```

L'appareil répond sur `127.0.0.1:5600`. Une réservation dure 30 minutes, et le minuteur `android-emu-reaper` fait le ménage.

## 5. Claude Code et relais.dev

- Copier `fichiers/root/.claude/settings.json` vers `~/.claude/settings.json`. Il déclare `CLAUDE_ENV_FILE=/root/.dev-env.sh`.
- Copier `fichiers/root/.claude/rules/*.md` vers `~/.claude/rules/` : règles « sessions en parallèle » et « émulateur Android ».
- Copier `fichiers/root/.claude/projects/` vers `~/.claude/projects/` : notes de mémoire de Claude sur les projets (état de la fonctionnalité d’activité, incident).
- Réinstaller l'agent relais (`rac`) en suivant la procédure de relais.dev. Copier ensuite `fichiers/etc/systemd/system/rac-agent.service`, puis lancer `systemctl enable --now rac-agent`.
- Se reconnecter à Claude Code : la connexion de l'ancien serveur doit être considérée comme compromise.

## 6. Projets

Créer une **nouvelle** clé SSH pour GitHub sur ce serveur (`ssh-keygen -t ed25519`) et l'ajouter au compte. Ne jamais réutiliser une clé de l'ancien serveur.

```bash
mkdir -p ~/projects && cd ~/projects
for r in bumo_backoffice bumo-hooks buma_pro business-mobile buma-extensions; do
  git clone git@github.com:ssakone/$r.git
done
cd buma_pro && git submodule update --init --recursive
```

`projets/PROMPT.md` est la note qui se trouvait dans `~/projects`, en dehors de tout dépôt.

Fichiers `.env` à recréer, ils ne sont pas dans git : `bumo_backoffice/.env.local` contient `VITE_POCKETBASE_URL=…`. Les secrets de l'ancien serveur sont à **regénérer**, pas à recopier.

## 7. Vérifications finales

```bash
sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'   # no / without-password
ufw status                                                        # active, OpenSSH seulement
flutter doctor
node -v && docker run --rm hello-world
android-emu doctor
```
