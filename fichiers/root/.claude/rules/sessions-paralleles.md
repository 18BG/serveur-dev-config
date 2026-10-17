# Sessions d'agents en parallèle

Plusieurs sessions peuvent travailler en même temps sur ce serveur (4 CPU, 8 Go de RAM).

- N'arrête que les processus que tu as lancés toi-même. Jamais de `pkill node`, `pkill -f gradle`, `./gradlew --stop`, `adb kill-server`, ni de `docker stop`/`docker rm` sur un conteneur qui n'est pas à toi : ils servent peut-être à une autre session.
- Serveurs de dev (Vite, Metro, Flutter web…) : prends un port libre et échoue s'il est pris (`--strictPort` pour Vite) plutôt que de réutiliser celui d'une autre session. Dans une config Playwright, mets `reuseExistingServer: false`, sinon tu risques de tester l'app d'une autre session.
- Playwright (Chromium, Firefox, WebKit) peut tourner dans plusieurs sessions à la fois : pas de réservation nécessaire.
- Un build Gradle (Flutter, React Native) prend jusqu'à 4 Go de RAM : si un autre build tourne déjà (`pgrep -f GradleWrapperMain`), attends sa fin avant de lancer le tien.
