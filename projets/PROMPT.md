# Mission : adopter le nouveau brand dans l'app BUMO

## Contexte

Tu travailles sur **BUMO**, l'app Flutter de gestion de commerce (backend PocketBase) du dépôt `git@github.com:ssakone/business-mobile.git`, sur téléphone et tablette. Lis d'abord `CLAUDE.md` : ses règles restent valables (outil de traduction, aucun texte en dur, composants réutilisables, aucune ombre…). Une seule exception : sa section « design » décrit l'**ancien** brand (noir/blanc + accent turquoise `#7FCFCF`). Pour les couleurs et la typo, c'est le nouveau brand qui prime.

Le nouveau brand est en ligne sur deux sites :
- https://bumo.app/ — le site de BUMO, l'app mobile : **ta marque** ;
- https://buma.pro/ (et https://buma.pro/fr/) — le site de BUMA, la marque mère (logiciel desktop/web/caisse). Le HTML de bumo.app parle d'ailleurs de « langage BUMA » : même langage visuel.

**Ce ne sont que des sites web, point** : on ne copie pas leurs mises en page. Ce que tu dois en retenir, c'est le **brand** : les nouvelles couleurs, la typo, le style. Ton travail est d'adopter ce brand dans l'app **de manière stratégique**.

Ne sois pas bête en allant changer complètement toutes les couleurs. Ici, on parle d'une app mobile, utilisée au comptoir. Elle suit un brand par ses tokens, son thème et ses styles globaux, pas en repeignant chaque écran. Aujourd'hui, l'app a encore l'ancien design : bumo.app l'affiche même sous « Aperçu réel de l'application ».

## Étape 1 — Comprendre le brand (obligatoire, avant tout code)

Visite les deux sites en entier, en desktop et en mobile. Astuces :
- **Tokens exacts** : ce sont des SPA Vite/React, le HTML est vide. Les tokens sont des variables CSS dans `:root` des fichiers `/assets/*.css` : `curl` + `grep` suffisent.
- **Rendu visuel** : utilise un navigateur headless (Playwright) si tu en as un. Un simple fetch « en markdown » perd tout le visuel.
- **Référence la plus utile** : les captures de l'**app BUMA v2.3.60**, le brand appliqué à une vraie UI produit : `https://buma.pro/screenshots/{dashboard,pos,sales,stock,customers,invoices,extensions}.webp?v=20261001`. Le téléphone du hero de buma.pro montre aussi l'app BUMA mobile.

## Repères déjà relevés (à vérifier toi-même, ne t'en contente pas)

**Palette** (variables CSS, quasi identiques sur les deux sites) :

| Token | Hex | Rôle |
|---|---|---|
| ivory | `#F7F3E9` | fond « papier » |
| ink | `#17302D` | texte (jamais de noir pur) |
| pine | `#0D3F3A` | **primaire** (dans le CSS de bumo.app, `--primary` = pine) |
| pine-deep | `#08302D` | zones sombres |
| sand | `#E8DDC9` | bandeaux, pastilles d'icône |
| clay | `#B65E43` | CTA marketing, accent |
| ochre | `#D2A860` | accent ponctuel : badge, indicateur actif, mot mis en valeur |
| leaf / moss | `#506D4A` / `#8C9D72` | verts secondaires |
| muted-fg | `#4C615F` | texte secondaire |
| border | `#C5D3D0` (BUMO) / `#DCE5E3` (BUMA) | filets |

**Couleurs de modules dans l'app BUMA** : tons terreux désaturés, glyphe ivoire sur carré coloré. Valeurs relevées au pixel, à ± quelques unités près. BUMA **réutilise une teinte par famille de modules** :
- pine `#1C5B51` (Point de vente) et `#0B403A` (Factures) ;
- leaf `#4C6A47` (Ventes, Paiements) ;
- argile `#9B4D35` (Achats) et rouge argile `#A74028` (Portefeuilles) ;
- ocre foncé `#99752F` (Produits) ;
- bleu ardoise `#2C5D6F` (Stockage, Livraisons) ;
- prune `#6D4B69` (Clients, Inventaires, Caisses, Utilisateurs) et mauve `#865A7D` (Applications) ;
- gris-vert `#4A5B55` (Fournisseurs, Paramètres).

**Typo** :
- Manrope 700–800 pour les titres et les montants (très serré, −0.045em, sur les grands titres) ;
- DM Sans pour le texte ;
- sur les sites, un mot par titre en Georgia italique ocre ;
- chez BUMA, une police mono en majuscules espacées pour les petits libellés.

**L'app BUMA** :
- **Surfaces** : contenu sur fond **blanc** ; tuiles, champs, cartes KPI et en-têtes de tableau en ivoire/sable très clair avec un filet fin ; **aucune ombre**.
- **Actions** : une seule action primaire pine par écran, les autres en outline.
- **Montants** : en ink. La couleur ne sert qu'à porter un sens (reste dû en rouge argile, remise en ocre foncé).
- **Badges et statuts** : compteur sur fond ocre avec texte ink, statuts en pastilles teintées.
- **Tuiles de module** : carré icône, titre, description courte, chevron. La tuile principale est remplie en pine, et les modules sont regroupés par catégorie.
- **Cartes KPI** : petit libellé, gros montant, mini-graphique, œil pour masquer les montants sensibles.

**Purement marketing, à NE PAS mettre dans l'app** : blobs et formes organiques, grain papier, trame de points, dégradés, ombres teintées, 3D, marquee, gros titres serif.

**Contrastes WCAG mesurés** :

| Couleur | Contraste | Conclusion |
|---|---|---|
| ochre sur blanc | 2,2:1 | **jamais en texte sur fond clair**. OK en fond avec texte ink (6,4:1) ou en texte sur pine (5,3:1) |
| moss sur blanc | 2,9:1 | décor seulement |
| clay sur blanc | 4,5:1 | limite : fond de bouton ou icône, pas de petit texte |
| ocre foncé `#99752F` sur blanc | 4,25:1 | assombrir pour du petit texte |
| ink, pine, leaf, rouge argile, ardoise, prune, gris-vert sur blanc | 6 à 14:1 | OK |
| texte blanc sur l'ancien turquoise `#7FCFCF` | 1,8:1 | — |

## Stratégie attendue (recommandations : écarte-t'en si tu le justifies)

1. **Le brand passe par les tokens, pas par les écrans.** Dans l'ordre :
   - `lib/core/theme/app_theme.dart` : `ColorScheme` explicite au lieu de `fromSeed(Colors.blue)`, `TextTheme` Manrope + DM Sans, thèmes de composants (boutons, champs, puces, onglets, switch, progress, snackbar, dialog, sheet, app bar) ;
   - `lib/core/utils/app_colors.dart` et `lib/core/layout/app_layout.dart` (tokens tablette : `accent` vaut encore `#7FCFCF`, `border` `#E0E0E0`, `textPrimary` `#1A1A1A`) ;
   - les composants partagés (`lib/core/widgets`, tuiles et cartes de l'accueil, en-têtes, listes, puces d'état).
   
   C'est là que se joue l'essentiel du rendu.
2. **Proportions** : base neutre et calme (fond blanc, texte ink, surfaces ivoire/sable). **Pine est LA couleur d'action et de sélection.** Ochre et clay restent rares et fonctionnels. Pas d'ivoire partout, pas d'argile sur tous les boutons.
3. **Le fond d'écran reste blanc**, comme dans l'app BUMA ; l'ivoire et le sable vont aux composants. Raison : `Colors.white` est écrit en dur environ 1 900 fois, un fond ivoire ferait un patchwork. Aucun chercher-remplacer massif sur `Colors.white` ni `Colors.black`.
4. **Noir** : l'ancien guide faisait du noir la couleur « primaire ».
   - Action ou sélection (bouton plein, onglet ou puce actifs, FAB) → pine.
   - Texte → ink, d'abord via le thème et les composants partagés.
   - Les voiles (`black54`…) peuvent rester.
5. **Ancien turquoise `#7FCFCF`** (environ 175 littéraux, plus `AppLayout.accent` et `AppColors.primary*`) : remplace-le par des **tokens** selon le rôle réel de chaque usage.
   - Accent ou sélection → pine.
   - Fond clair de surbrillance → teinte claire (pine très clair ou sable).
   - **Vérifie ce qui est posé dessus** : le turquoise était clair et pine est foncé, donc le texte ou l'icône doit s'inverser.
   - Pour trouver les points chauds : `grep -rc "0xFF7FCFCF" lib | grep -v ":0$" | sort -t: -k2 -rn`.
6. **Couleurs de modules** (`AppColors.salesColor`, `productsColor`…, déjà utilisées partout via ces tokens) :
   - passe-les sur la gamme terreuse, en alignant sur BUMA quand le module existe chez BUMA ;
   - réutilise une teinte par famille plutôt que d'inventer 25 couleurs ;
   - vérifie que les modules voisins restent distinguables et que le glyphe blanc reste lisible.
7. **Sémantique** :
   - erreur et destructif → vrai rouge `#C72323` (celui de bumo.app) ;
   - dette et négatif → rouge argile ;
   - positif et entrée → leaf ;
   - attente → ocre en fond, ocre foncé en texte ;
   - info → ardoise.
   
   Les montants sont en ink par défaut : plus de montants bleus.
8. **Typo** :
   - Manrope pour les titres et montants, DM Sans pour le texte, **embarquées en assets** (`assets/fonts/` + section `fonts:` du `pubspec.yaml`). L'app marche hors-ligne : pas de téléchargement au runtime. Licences OFL.
   - Le tracking très serré seulement sur les grands titres.
   - Pas de serif italique ni de mono dans les écrans opérationnels.
9. **Formes** : rayons un peu plus doux qu'aujourd'hui et proportionnés à la taille, pas les 28 px du site partout :
   - environ 12 pour les champs et boutons ;
   - environ 16 pour les cartes et tuiles ;
   - filets fins teintés (ex. `#DCE5E3`) au lieu du gris `#E0E0E0`.
   
   **Zéro ombre et zéro dégradé** : règle validée, verrouillée par `test/core/theme/app_theme_test.dart`, qui vérifie aussi que la barre d'en-tête reste blanche au défilement.
10. **Au plus un « moment de marque » par écran.** Exemple : la carte solde/portefeuille de l'accueil en pine avec texte ivoire et un détail ocre, ou la tuile principale en pine.

## Ne PAS toucher

- **Le contenu des utilisateurs, qui n'est pas l'habillage de l'app** :
  - thèmes des sites e-shop (`ma_boutique` : le `'#7FCFCF'` de son test est une donnée) ;
  - modèles et éditeur `marketing` (polices et couleurs de l'utilisateur) ;
  - couleurs choisies par l'utilisateur (types de dépenses…).
- **Les PDF et reçus** (`lib/features/{sales,products,delivery}/presentation/services`) et les illustrations existantes : liste dans ton rapport ceux qui portent l'ancien brand.
- **Logo, icône d'app, splash** : décision en attente (le symbole BUMO est pétrole `#00878E`, celui de BUMA vert `#12776E`).
- **Config native** : Podfile, réglages iOS/Android, flags SwiftPM, lock files. Dans `pubspec.yaml`, ne touche qu'à la déclaration des polices.
- **`lib/core/utils/config.dart`** : il reste sur le serveur de test.
- **Hors périmètre** : le mode sombre, la logique métier, les données.

## Mise en page tablette déjà validée : la structure, pas l'apparence

Ces décisions portent **uniquement sur la structure** : disposition, navigation, contenu des écrans. Elles ne concernent **pas** l'apparence. Le nouveau brand (couleurs, typo, rayons, bordures, couleurs d'icônes) s'applique **pleinement** à ces écrans, sur téléphone comme sur tablette. Rebrande-les comme le reste, sans changer leur disposition.

- **Navigation** : pas de rail ni de sidebar ; les tuiles de l'accueil ouvrent les modules. Jamais 3 colonnes.
- **Accueil** : allégé, sans avatar de profil.
- **Cartes d'app tablette** : carte bordée avec l'icône du module à gauche, le nom et une description de 2–3 mots. Colonnes égales espacées de 12, jamais étalées sur toute la largeur. Pas l'aspect des tuiles du téléphone. Leur fond, leur bordure et la couleur de leur icône suivent les nouveaux tokens.
- **Gestionnaire d'apps** : une page défilante de grilles.
- **Stock** : les boutons Entrée/Sortie gardent leur texte.

La seule règle de style déjà validée qui reste, c'est **zéro ombre et zéro dégradé**, téléphone compris (voir Stratégie, point 9). Elle va d'ailleurs dans le sens du brand : l'app BUMA est plate.

Si tu y as accès, `/Users/omarsisss/Documents/wproject/protech/prompts/ipad-layout-v2/BRIEF_V3.md` et `DESIGN.md` détaillent ces décisions. Ils ont été écrits avec l'ancien brand : suis leur structure, ignore leurs couleurs.

## Méthode

1. **Branche** : `git fetch origin && git switch -c feat/brand-v2 origin/feat/tablet-layout-v2` (base `f6e45527`).
2. **Audit avant de coder** : où vivent les couleurs, et le rôle de chaque usage (action, texte, surface, bordure, sémantique, contenu utilisateur). Établis un **plan de correspondance ancien → nouveau token**. Il va dans ton rapport : pas de README (règle de `CLAUDE.md`).
3. **Commits petits et logiques**, dans cet ordre :
   1. tokens et thème ;
   2. polices ;
   3. composants partagés ;
   4. écrans par module, en commençant par les plus utilisés : accueil (téléphone et tablette), vente/caisse, produits, clients, factures/devis, stock, portefeuille, paramètres ;
   5. section « design » de `CLAUDE.md` réécrite pour le nouveau brand, dans **un commit séparé**.
4. **Textes** : normalement aucun nouveau texte. S'il en faut, uniquement via `./tools/translate.sh`.
5. **Tests** : quand un test vérifie une couleur, ne l'affaiblis pas. Mets-le à jour seulement si l'intention change (ex. `ProductListTile.stockColor` attend `0xFF10B981`). Toute la suite doit rester verte.

## Vérifications

Tu n'as pas d'iPhone ni d'iPad : la revue et les tests sur iPhone puis iPad seront faits après ton push.

1. `flutter analyze` : aucun nouveau problème.
2. `flutter test` : tout vert.
3. Si tu as un émulateur Android, lance l'app sur téléphone **et** sur tablette, et connecte-toi avec le compte de test ci-dessous. Parcours les écrans clés : connexion, accueil, nouvelle vente, listes et fiches, formulaires, dialogues, bottom sheets, snackbars, états vides, erreurs. Vérifie lisibilité et contraste.
4. Ne commite aucune capture d'écran.

## Compte de test (pour l'émulateur)

- **Serveur** : rien à configurer. L'app pointe déjà sur le serveur de **TEST** `https://relais-s2.bumo.app` : c'est la valeur par défaut de `lib/core/utils/config.dart`, en debug comme en release. Ne change pas cette valeur et ne vise **jamais** la production `relais-s1.bumo.app`.
- **Connexion** : email `bumo.tablet.v2@bumo.app`, mot de passe `Bumo@2026` (connexion vérifiée le 2026-10-14). Choisis ensuite le business **« BUMO Tablet Shop »** : il contient beaucoup de données, avec un abonnement PRO de démo jusqu'au 24/11/2026.
- **Données** : ce compte sert aussi aux tests iPhone et iPad après toi.
  - Tu peux créer quelques données de test (une vente…) sur ce serveur.
  - Ne supprime rien.
  - Ne change ni les réglages du compte ni ceux du business : devise, modules actifs, rôles…

## Fin

- `git push -u origin feat/brand-v2`. Pas de merge, pas de PR, pas de force-push, aucune autre branche touchée.
- Rapport final :
  - synthèse du brand tel que tu l'as compris ;
  - table de correspondance des tokens (ancien → nouveau) ;
  - fichiers et écrans modifiés ;
  - ce que tu as vérifié et comment (analyze, tests, émulateur) ;
  - ce que tu n'as pas pu vérifier ;
  - points ouverts (logo, icône, splash, PDF, illustrations, mode sombre).
