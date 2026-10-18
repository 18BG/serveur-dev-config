# Serveur de développement — configuration

Ce dépôt permet de remonter le serveur de développement : web (React, Vite), mobile (Flutter, React Native, Android) et les sessions Claude Code pilotées par relais.dev.

Le serveur (VPS Contabo, Ubuntu 24.04, 4 CPU, 8 Go de RAM, 96 Go de disque) a été piraté en octobre 2026. La cause : un mot de passe root faible, ouvert à tout Internet. Voir [INCIDENT.md](INCIDENT.md). Il a été réinstallé le 18 octobre 2026 en suivant ce README.

**Règle n° 1 : connexion par clé SSH uniquement, jamais par mot de passe.** Après la réinstallation, les robots ont commencé à essayer des mots de passe en quelques minutes.

`fichiers/` reproduit l'arborescence du serveur. Chaque fichier se copie à l'emplacement indiqué par son chemin, par exemple `fichiers/usr/local/bin/android-emu` vers `/usr/local/bin/android-emu`.

---

## 1. Installer et sécuriser (avant tout le reste)

1. Dans le panneau de l'hébergeur, réinstaller **Ubuntu 24.04**. **Ajouter la clé SSH publique** de l'ordinateur personnel (`~/.ssh/id_ed25519.pub`, clé `babry-ordi`) au moment de l'installation. Si le panneau ne l'a pas fait, `/root/.ssh/authorized_keys` est vide : l'y ajouter avant l'étape 3.
2. Se connecter avec `ssh root@IP`. Aucun mot de passe ne doit être demandé. Pour en être sûr :
   ```bash
   ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no root@IP
   ```
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
   Attention : Docker contourne ufw pour les ports publiés. Toujours publier sur `127.0.0.1` (`-p 127.0.0.1:PORT:PORT`), comme le fait `android-emu`.
6. Appliquer les mises à jour de sécurité automatiquement, et installer fail2ban :
   ```bash
   apt update && apt -y full-upgrade && apt -y install unattended-upgrades fail2ban
   dpkg-reconfigure -f noninteractive unattended-upgrades
   systemctl enable --now fail2ban
   ```
7. Changer le mot de passe root (`passwd`) pour un mot de passe long et aléatoire, rangé dans un gestionnaire de mots de passe. Il ne sert plus en SSH, mais c'est lui qui ouvre la **console VNC** de Contabo, le seul accès de secours si la clé SSH est perdue.

## 2. Mémoire : swap

8 Go de RAM ne suffisent pas pour un build Android : Gradle (`-Xmx4G` dans les projets), le démon Kotlin et Dart ont saturé la mémoire, et le noyau a tué le build. Ajouter 4 Go de swap :

```bash
fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
cp fichiers/etc/sysctl.d/90-swap.conf /etc/sysctl.d/ && sysctl -p /etc/sysctl.d/90-swap.conf   # vm.swappiness=10
```

## 3. Outils de développement

Versions installées :

| Outil | Version | Emplacement |
|---|---|---|
| Node.js (nvm 0.40.8) | 24.x LTS | `~/.nvm` |
| Flutter | 3.47.x, canal stable | `~/development/flutter` |
| Java (OpenJDK) | 17 | `/usr/lib/jvm/java-17-openjdk-amd64` |
| Android SDK | platforms 34, 35, 36 ; build-tools 35.0.0, 36.0.0 ; platform-tools, cmdline-tools, NDK 28.2.13676358, CMake 3.22.1 | `~/Android/Sdk` |
| Docker | 29.x | paquet `docker-ce` |
| Python | 3.12 (celui d'Ubuntu) | |
| Playwright | Chromium, Firefox, WebKit | `~/.cache/ms-playwright` |

Go n'est plus installé.

```bash
apt -y install git curl unzip zip xz-utils build-essential python3-venv python3-pip \
  openjdk-17-jdk clang cmake ninja-build pkg-config libgtk-3-dev
# Node
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
. ~/.nvm/nvm.sh && nvm install --lts && nvm alias default 'lts/*'
# Flutter
mkdir -p ~/development && git clone -b stable https://github.com/flutter/flutter.git ~/development/flutter
# Docker : https://docs.docker.com/engine/install/ubuntu/
```

**Android SDK.** Télécharger les cmdline-tools (`commandlinetools-linux-*_latest.zip`, voir https://dl.google.com/android/repository/repository2-3.xml) et les décompresser dans `~/Android/Sdk/cmdline-tools/latest`, puis :

```bash
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "platforms;android-35" "platforms;android-36" \
  "build-tools;35.0.0" "build-tools;36.0.0" "ndk;28.2.13676358" "cmake;3.22.1"
flutter doctor --android-licenses
```

- `sdkmanager` est désormais obsolète : Google l'a remplacé par le nouvel « Android CLI » (`android sdk`, dans le même dossier). L'ancienne commande marche encore, avec un avertissement, et `--list` affiche les paquets avec `/` au lieu de `;`.
- La version du NDK est celle qu'attend Flutter : `ndkVersion` dans `~/development/flutter/packages/flutter_tools/gradle/src/main/kotlin/FlutterExtension.kt`. À revérifier après une mise à jour de Flutter.
- N'installer **pas** le paquet `adb` d'Ubuntu : deux versions d'adb se coupent mutuellement leur serveur. Celui du SDK (`~/Android/Sdk/platform-tools`) suffit, et c'est celui qu'utilise `android-emu`.

**Keystore de debug Android.** Sans lui, `flutter build apk --debug` échoue (`Keystore file '/root/.android/debug.keystore' not found`). Ce ne sont pas des secrets, ce sont les valeurs standard d'Android :

```bash
mkdir -p ~/.android && keytool -genkeypair -keystore ~/.android/debug.keystore -storepass android \
  -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
```

**Playwright**, depuis un projet qui l'utilise (`buma_pro`) :

```bash
npm ci && npx playwright install --with-deps chromium firefox webkit
```

Variables d'environnement : copier `fichiers/root/.dev-env.sh` vers `~/.dev-env.sh` et ajouter en tête de `~/.bashrc` :

```bash
[ -f ~/.dev-env.sh ] && . ~/.dev-env.sh
```

Ce fichier règle nvm, `JAVA_HOME`, `ANDROID_HOME` et le PATH de Flutter et du SDK Android. Les sessions Claude Code le chargent aussi, via `CLAUDE_ENV_FILE`.

## 4. Proxy Maven Google (Gradle) — seulement si nécessaire

Sur l'ancien serveur, `dl.google.com` bloquait les gros téléchargements, et les HEAD/404 en HTTP/1.1. Gradle passait donc par un petit proxy local sur `127.0.0.1:8765`. **Depuis la réinstallation du 18 octobre 2026, ce n'est plus le cas : le proxy n'est pas installé.**

Vérifier d'abord, les deux commandes doivent répondre en quelques secondes :

```bash
curl -s --http1.1 --max-time 60 -o /dev/null -w '%{http_code} %{size_download}\n' \
  https://dl.google.com/android/maven2/com/android/tools/build/gradle/8.7.3/gradle-8.7.3.jar   # 200 12429787
curl -sI --http1.1 --max-time 20 -o /dev/null -w '%{http_code}\n' https://dl.google.com/android/maven2/nexiste/pas.pom   # 404
```

Seulement si elles bloquent :

```bash
mkdir -p /opt/google-maven-proxy && cp fichiers/opt/google-maven-proxy/proxy.py /opt/google-maven-proxy/
cp fichiers/etc/systemd/system/google-maven-proxy.service /etc/systemd/system/
mkdir -p ~/.gradle/init.d && cp fichiers/root/.gradle/init.d/google-maven-mirror.gradle ~/.gradle/init.d/
systemctl daemon-reload && systemctl enable --now google-maven-proxy
```

Ajouter aussi dans `~/.dev-env.sh`, pour que `sdkmanager` contourne le blocage :

```bash
export SDK_TEST_BASE_URL=https://redirector.gvt1.com/edgedl/android/repository/
```

`android-emu doctor` ne vérifie le proxy que s'il est installé.

## 5. Émulateur Android partagé (Redroid)

Un seul Android 14 dans Docker, partagé par toutes les sessions. Il se pilote uniquement par `android-emu` (`android-emu help`). Les règles des agents sont dans `fichiers/root/.claude/rules/emulateur-android.md`.

L'image Contabo utilise le noyau `linux-virtual`, qui n'a pas le module `binder` d'Android. `linux-image-generic` installe le noyau générique avec `linux-modules-extra`, et le module suit ainsi les mises à jour du noyau. Redémarrer ensuite pour passer sur ce noyau.

```bash
apt -y install linux-image-generic linux-modules-extra-$(uname -r)
cp fichiers/etc/modules-load.d/redroid.conf /etc/modules-load.d/
cp fichiers/etc/modprobe.d/redroid.conf /etc/modprobe.d/
modprobe binder_linux devices=binder,hwbinder,vndbinder && systemctl restart systemd-modules-load
docker pull redroid/redroid:14.0.0_64only-latest
install -m 755 fichiers/usr/local/bin/android-emu /usr/local/bin/android-emu
cp fichiers/etc/systemd/system/android-emu-reaper.{service,timer} /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now android-emu-reaper.timer
android-emu doctor   # vérifie module binder, Docker, image, adb
```

L'appareil répond sur `127.0.0.1:5600`. Une réservation dure 30 minutes, et le minuteur `android-emu-reaper` fait le ménage.

Pour lancer une app installée, utiliser `am start` plutôt que `monkey`, qui ne la démarre pas sur Redroid :

```bash
adb -s 127.0.0.1:5600 shell am start -n "$(adb -s 127.0.0.1:5600 shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER <paquet> | tail -1)"
```

## 6. Claude Code et relais.dev

- Copier `fichiers/root/.claude/settings.json` vers `~/.claude/settings.json`. Il déclare `CLAUDE_ENV_FILE=/root/.dev-env.sh`.
- Copier `fichiers/root/.claude/rules/*.md` vers `~/.claude/rules/` : règles « sessions en parallèle » et « émulateur Android ».
- Copier `fichiers/root/.claude/projects/` vers `~/.claude/projects/` : notes de mémoire de Claude sur les projets (accès GitHub, état de la fonctionnalité d’activité, incident).
- Réinstaller l'agent relais (`rac`) en suivant la procédure de relais.dev. Copier ensuite `fichiers/etc/systemd/system/rac-agent.service`, puis lancer `systemctl enable --now rac-agent`.
- Se reconnecter à Claude Code : la connexion de l'ancien serveur doit être considérée comme compromise.

## 7. Projets

Créer une **nouvelle** clé SSH pour GitHub sur ce serveur et l'ajouter au compte. Ne jamais réutiliser une clé de l'ancien serveur.

```bash
ssh-keygen -t ed25519 -C "root@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
ssh-keyscan -t ed25519,rsa,ecdsa github.com >> ~/.ssh/known_hosts
cat ~/.ssh/id_ed25519.pub   # à ajouter dans GitHub → Settings → SSH and GPG keys
ssh -T git@github.com       # « Hi 18BG! »
```

Configurer Git. Les sous-modules privés de `buma_pro` sont déclarés en `https://github.com/ssakone/…` : la règle `insteadOf` les fait passer par SSH, sans modifier `.gitmodules`.

```bash
git config --global user.name "Babry Galedou"
git config --global user.email "babrigaledou7@gmail.com"
git config --global url."git@github.com:ssakone/".insteadOf "https://github.com/ssakone/"
```

```bash
mkdir -p ~/projects && cd ~/projects
for r in bumo_backoffice bumo-hooks buma_pro business-mobile buma-extensions; do
  git clone git@github.com:ssakone/$r.git
done
cd buma_pro && git submodule update --init --recursive
```

`projets/PROMPT.md` est la note qui se trouvait dans `~/projects`, en dehors de tout dépôt.

Avec Flutter 3.47, `business-mobile` ne compile que sur une branche en Gradle ≥ 8.14 : c'est le cas de `feat/brand-v2` (8.14.3), pas de `main` ni de `feat/tablet-layout-v2` (8.11.1).

Fichiers `.env` à recréer, ils ne sont pas dans git : `bumo_backoffice/.env.local` contient `VITE_POCKETBASE_URL=…`. Les secrets de l'ancien serveur sont à **regénérer**, pas à recopier.

## 8. Vérifications finales

```bash
sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'   # no / without-password
ufw status                                                        # active, OpenSSH seulement
swapon --show                                                     # /swapfile 4G
flutter doctor                                                    # seul Chrome manque (Flutter web)
node -v && docker run --rm hello-world
android-emu doctor
cd ~/projects/business-mobile && flutter build apk --debug       # sur feat/brand-v2
```
