# Environnement de développement Flutter / React / React Native.
# Chargé en tête de ~/.bashrc (terminal) et, pour les sessions d'agents IA, avant
# chacune de leurs commandes via CLAUDE_ENV_FILE (~/.claude/settings.json) : le PATH
# de leur session écrase sinon celui défini par ~/.bashrc.

export NVM_DIR="$HOME/.nvm"
if [ -n "$PS1" ]; then
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
else
  # Agents : charger nvm.sh coûterait ~0,7 s par commande. On ajoute seulement le
  # Node par défaut de nvm au PATH, en suivant ses alias (default -> lts/* -> … -> v24.x).
  _nvm_v=default
  for _nvm_i in 1 2 3 4 5; do
    [ -f "$NVM_DIR/alias/$_nvm_v" ] || break
    _nvm_v=$(cat "$NVM_DIR/alias/$_nvm_v")
  done
  if [ ! -d "$NVM_DIR/versions/node/$_nvm_v/bin" ]; then
    _nvm_v=$(ls "$NVM_DIR/versions/node" 2>/dev/null | sort -V | tail -n 1)
  fi
  [ -n "$_nvm_v" ] && PATH="$NVM_DIR/versions/node/$_nvm_v/bin:$PATH"
  unset _nvm_v _nvm_i
fi

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$HOME/development/flutter/bin:$HOME/.pub-cache/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
# dl.google.com bloque les gros téléchargements depuis ce serveur : sdkmanager passe
# par redirector.gvt1.com (même stockage Google). Voir aussi ~/.gradle/init.d/google-maven-mirror.gradle
export SDK_TEST_BASE_URL=https://redirector.gvt1.com/edgedl/android/repository/
