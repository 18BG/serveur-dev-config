# Émulateur Android partagé

Ce serveur a un seul émulateur Android (Android 14 dans Docker, « Redroid »), partagé par toutes les sessions d'agents. Il n'existe que pendant une réservation et se pilote uniquement avec la commande `android-emu` (`android-emu help`).

- Ne lance jamais d'émulateur toi-même : pas de `docker run`/`docker start` de Redroid, pas d'AVD, jamais de second émulateur. Si `android-emu` échoue, signale-le à l'utilisateur au lieu de contourner.
- Prépare tout avant de réserver (APK compilé, tests écrits) : la réservation ne doit couvrir que le temps des tests.
- Réserve avec `android-emu start --task "<ce que tu vas tester>"`. Tu obtiens un Android tout neuf (≈40 s), pour ta session seule.
- Code de sortie 75 = occupé par une autre session. Deux options :
  - attendre : `android-emu start --task "…" --wait 8` (8 min max par appel, sous la limite de 10 min de l'outil Bash ; relance si besoin) ;
  - ou finir ta tâche sans test Android, puis donner à l'utilisateur la liste précise des tests à faire (étapes, résultat attendu).
  N'utilise jamais un émulateur réservé par une autre session.
- L'appareil est `127.0.0.1:5600` : précise-le toujours (`adb -s 127.0.0.1:5600 …`, `flutter run -d 127.0.0.1:5600`). Jamais de `adb kill-server`.
- La réservation dure 30 min ; `android-emu renew` la prolonge. Si elle expire, ou si ta session se ferme, l'émulateur est détruit automatiquement.
- Dès que tes tests sont finis, réussis ou non : arrête ce que tu as lancé pour eux (`flutter run`, Metro…), puis `android-emu stop`. Cette commande désinstalle les apps, détruit l'émulateur et libère la RAM. Ne le garde jamais allumé « au cas où » : le relancer prend moins d'une minute.
- N'arrête jamais l'émulateur d'une autre session ; `android-emu stop --force` est réservé à l'utilisateur. `android-emu status` indique qui l'utilise et pour quoi.
