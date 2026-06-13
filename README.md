# Thémo — générateur de design système → CSS

Application Linux native (GTK4 / libadwaita) pour construire un design système à partir de **quelques tokens de base** et l'exporter en **un seul fichier CSS**, sans JSON et **sans aucune classe CSS**.

## Principe

Vous saisissez peu de choses — deux couleurs, des polices, une taille de base, un ratio, une unité d'espacement, un rayon, une opacité d'ombres.

Tout le reste est **calculé automatiquement** :

| Saisi | Dérivé automatiquement |
|---|---|
| Couleur primaire / secondaire | Gammes 50→900 (espace OKLCH, gamut sRGB respecté) + gamme neutre teintée |
| Taille de base + ratio | Échelle typographique complète (`--text-xs` → `--text-4xl`) |
| Unité d'espacement (2 à 12 px, pas de 0,5) | Échelle `--space-1` → `--space-24`, conteneurs |
| Rayon de bordure | `--radius-sm/md/lg/xl/full` |
| Opacité des ombres | 5 niveaux d'élévation `--shadow-1` → `--shadow-5` |

Le CSS généré a trois étages :

1. **Tokens primitifs** dans `:root` ;
2. **Tokens sémantiques** (`--background`, `--text`, `--accent`…) via un template au choix — *Neutre*, *Doux*, *Contrasté*, *Encre*, *Chaleureux*, *Vif* — déclinés en clair et en sombre (`prefers-color-scheme` + `data-theme`) ;
3. **Styles appliqués directement aux éléments HTML** (`body`, `h1`, `a`, `button`, `table`, formulaires…) via un second template — *Moderne*, *Classique*, *Minimal*, *Éditorial*, *Galerie*, *Chaleureux*, *Festif*, *Officiel*. Aucune classe : le HTML reste nu.

Un parcours guidé pas à pas est disponible dans [TUTORIEL.md](TUTORIEL.md).

## Lancement

```bash
python3 themo.py
```

Dépendances (présentes sur la plupart des distributions avec GNOME) : `python3-gi`, GTK 4, libadwaita ≥ 1.5, WebKitGTK 6.0 et GtkSourceView 5 (`gir1.2-webkit-6.0` et `gir1.2-gtksource-5` sous Debian/Ubuntu). Pour la publication : `rsync` (méthode SSH) et, pour conserver jeton et mots de passe dans le trousseau, libsecret (`gir1.2-secret-1`) — à défaut, ils sont stockés dans un fichier local en 0600. La publication FTP/FTPS et Netlify n'utilise que la bibliothèque standard de Python.

Pour l'avoir dans le menu d'applications (le script injecte le chemin du dépôt dans le lanceur) :

```bash
./install.sh
```

## Utilisation

- Au démarrage (et via ☰ → Nouveau projet), un **écran d'accueil** propose des **modèles de projet** complets — Démonstration, Blog, Portfolio, Personnel, Événement, Institutionnel, Page vide — avec vignette, description et nombre de pages. Choisir un modèle applique d'office le style graphique et l'ambiance assortis. La case **« Illustrer avec des photos libres de droits (Openverse) »**, cochée par défaut, remplace les images de remplissage par des photos CC0 trouvées selon les mots-clés de chaque emplacement, téléchargées puis embarquées dans les pages ; décochée (ou hors ligne), les placeholders SVG restent en place. Tant qu'aucun modèle n'est choisi, l'aperçu montre un canevas vierge (et non un projet de démonstration).
- L'écran d'accueil liste aussi les **projets récents** (avec un bouton « En ligne » vers le site publié, le cas échéant) et un bouton **Ouvrir un projet…**. Les récents restent accessibles à tout moment par ☰ → **Ouvrir un projet récent…**
- Le style graphique, tout en haut, prérègle l'ensemble des tokens selon son caractère (Moderne, Classique, Minimal, Éditorial, Galerie, Chaleureux, Festif, Officiel) ; chaque token reste ensuite ajustable librement, et le bouton de réinitialisation réaligne le tout sur le style courant.
- La barre latérale modifie les tokens, l'aperçu se met à jour en direct.
- Le nom de la **page courante** s'affiche en haut de l'aperçu ; on passe de page en page par les liens de la nav, ou par la section « Aller à la page » du menu ⋮ (page courante cochée). Ce menu permet aussi d'**ajouter** (depuis un modèle de page), **dupliquer**, **renommer**, **supprimer** des pages, et **définir la page d'accueil** (celle qui sera exportée et publiée comme `index.html`). Le bouton lune bascule clair/sombre.
- La **navigation principale est tenue à jour automatiquement** : ajouter, dupliquer, renommer ou supprimer une page répercute le lien correspondant dans la nav d'en-tête de toutes les pages (identifié par son `href` en slug) ; la page créée reçoit une nav complète avec sa propre entrée marquée `aria-current="page"`. Les liens personnalisés (`href="#"`, liens externes) ne sont jamais touchés.
- Les **liens fonctionnent dans l'aperçu** : un clic sur un lien interne (`page.html`) bascule l'aperçu sur la page correspondante du projet, un lien externe (`http…`, `mailto:`) s'ouvre dans l'application par défaut, et les ancres (`#…`) défilent normalement. Dans les pages exportées, les mêmes liens fonctionnent tels quels puisque les fichiers existent côte à côte.
- Le bouton crayon ouvre l'**éditeur HTML** de la page courante (GtkSourceView, coloration syntaxique) ; l'aperçu se met à jour pendant la frappe. Seul le corps de la page s'édite — et pour rester fidèle au design système, n'utilisez pas d'attribut `class`.
- Le bouton **+** insère un **bloc** prêt à l'emploi dans la page courante : héro pleine largeur, titre et texte, grille de cartes, tableau, citation, formulaire de contact, questions fréquentes, illustration, appel à l'action, liens sociaux, séparateur. Chaque bloc est garanti sans classe et placé au bon endroit (le héro avant `<main>`, le reste en fin de contenu) ; réorganisez ensuite dans l'éditeur HTML.
- Le bouton **corbeille** active la **suppression de blocs** : le bloc survolé dans l'aperçu (enfant direct de `<main>` ou section héro) se surligne en rouge, un clic le supprime — l'en-tête, la nav et le pied de page ne sont jamais candidats. Un toast « Annuler » permet de revenir en arrière.
- Le bouton **image** active le **remplacement d'images** : cliquez une image dans l'aperçu, un dialogue prérempli avec ses mots-clés présente une grille de photos CC0 (Openverse) ; un clic la remplace. À l'enregistrement et à l'export, les images sont écrites comme fichiers dans `images/` (avec `loading="lazy"` et dimensions), pas en base64 — pages plus légères et indexables.
- L'**en-tête et le pied de page sont communs à tout le site** : les modifier sur une page (texte de la marque, pied…) se répercute sur toutes les autres, en préservant la mise en évidence `aria-current` propre à chacune.
- Le bouton d'**édition du texte** (curseur de sélection) rend l'aperçu directement éditable : cliquez et tapez dans la page, un liseré pointillé signale le mode actif. Les modifications sont synchronisées au fil de la frappe, et changer un token pendant l'édition met à jour les styles sans recharger la page. Une **barre de formatage** apparaît alors : mettre la sélection en **gras** (`<strong>`), **emphase** (`<em>`), **surligné** (`<mark>`) ou en **lien** ; Ctrl+B / Ctrl+I produisent aussi des balises sémantiques. Ce mode est réservé au texte : pour la structure (ajouter des sections, des tableaux…), passez par l'éditeur HTML — les deux modes sont exclusifs. À noter : WebKit normalise le balisage de la page éditée (indentation perdue).
- **Annuler / Rétablir** (☰ → Édition, ou Ctrl+Z / Ctrl+Maj+Z) couvrent les opérations de structure (insertion et suppression de bloc, remplacement d'image, opérations de page) ; l'édition de texte conserve, elle, l'annulation native de ses éditeurs.
- **Référencement (SEO)** : ☰ → **Réglages du site…** fixe la langue et une description par défaut ; ⋮ → **Description de la page…** en donne une par page. À l'export et à la publication, chaque page reçoit un en-tête complet (description, langue, URL canonique, Open Graph, `theme-color`), et le site reçoit `favicon.svg`, `robots.txt` et `sitemap.xml`.
- **Accessibilité** : la barre latérale affiche le contraste WCAG (AA/AAA) des couleurs en direct ; ☰ → **Vérifier l'accessibilité…** signale images sans `alt`, `h1` manquant ou multiple, niveaux de titres sautés, liens vides et attributs `class`.
- Le travail s'organise en **projet** : un dossier contenant `themo.conf` (tokens + métadonnées, format INI), `design-system.css`, une page HTML par page du projet, `index.html` (la page d'accueil), le dossier `images/`, `favicon.svg`, `robots.txt` et `sitemap.xml` — des fichiers ordinaires, utilisables tels quels. Menu ☰ : Nouveau / Ouvrir / Ouvrir un projet récent / Enregistrer (Ctrl+S) / Enregistrer sous… Utilisez un dossier dédié par projet. Fermer avec des modifications non enregistrées demande confirmation (Annuler / Quitter sans enregistrer / Enregistrer).
- Menu ☰ → **Exporter le CSS…** : écrit `design-system.css` seul ; **Exporter CSS + pages HTML…** : écrit le site complet (pages, `index.html`, images, fichiers SEO).
- Menu ☰ → **Publier sur un serveur…** : met le site en ligne directement depuis Thémo, vers **Netlify** (un jeton d'accès personnel suffit, le site est créé au premier envoi), un **serveur SSH** (rsync, authentification par clé) ou en **FTP / FTPS** (identifiants d'hébergement mutualisé classique ; FTPS chiffré par défaut, dossier distant créé au besoin). La destination est mémorisée par projet ; le jeton et les mots de passe sont conservés dans le trousseau. Une aide intégrée détaille les données à fournir pour chaque méthode, et un bouton « Ouvrir » mène au site en ligne après publication.

Pour forcer un thème dans vos pages : `<html data-theme="dark">` ou `<html data-theme="light">` ; sans attribut, le thème suit le système.

Héro pleine largeur : placez une `<section>` directement dans `<body>`, avant `<main>` — son fond s'étend sur toute la largeur et son contenu reste aligné sur le conteneur (token `--gutter`). Le groupe « Mise en page » règle le rythme **macro** (largeur du contenu, espacement entre sections, grille de cartes), tandis que l'unité d'espacement règle le **micro** (intérieur des composants).

## Fichiers

- `themo.py` — application GTK4/Adwaita (fenêtre, aperçu WebKit, éditeur, export)
- `tokens.py` — calculs des tokens dérivés (OKLCH, échelles), préréglages
- `css_gen.py` — templates sémantiques + éléments, assemblage du CSS
- `pages.py` — modèles de pages et de projets HTML (sans classes), en-tête SEO
- `project.py` — projet sur disque : tokens + métadonnées (INI), pages, index.html, images/, fichiers SEO
- `openverse.py` — photos CC0 (API Openverse) ; data URI en mémoire, fichiers `images/` à l'export
- `publish.py` — publication du site (Netlify, SSH/rsync, FTP/FTPS)
- `audit.py` — audit d'accessibilité des pages
- `themo.desktop` — lanceur pour le menu d'applications

## Applications comparables

Thémo se situe à l'intersection de quatre familles d'outils, sans appartenir à aucune. Ses différenciateurs : natif Linux, 100 % CSS (pas de JSON), sans classes, et un générateur de tokens couplé à un mini-éditeur de site.

**Générateurs de design tokens** — la catégorie la plus proche, presque entièrement web et centrée JSON (format W3C/DTCG) :

- [Tokens Studio](https://tokens.studio/) — la référence professionnelle (plugin Figma, éditeur nodal) ; sortie JSON d'abord, CSS ensuite.
- [Utopia](https://utopia.fyi/) — très proche dans l'esprit : peu d'entrées, échelles typographiques et d'espacement calculées, variables CSS pures.
- [Realtime Colors](https://www.realtimecolors.com/) et [uicolors.app](https://uicolors.app/) — aperçu couleurs/polices sur un vrai site ; gammes 50→900 depuis une couleur, comme les gammes OKLCH de Thémo.
- [Penpot](https://penpot.app/) — outil de design open source, design tokens natifs au format DTCG avec export CSS.

**Applications Linux natives** — [Gradience](https://github.com/GradienceTeam/Gradience) (GTK4/libadwaita) est le cousin le plus proche en forme : tokens de couleurs, aperçu en direct… mais il thème les applications GTK, pas le web. Le créneau « app de bureau Linux → design système CSS » est quasiment vide.

**Frameworks CSS sans classes** — le CSS généré est de la famille de [Pico.css](https://picocss.com/), [Water.css](https://watercss.kognise.dev/), [MVP.css](https://andybrewer.github.io/mvp/) ou [Simple.css](https://simplecss.org/) : du HTML nu stylé par éléments. Ces frameworks sont figés ou paramétrables à la marge ; Thémo en génère un sur mesure.

**Éditeurs de pages** — l'édition WYSIWYG + source avec aperçu rappelle la lignée BlueGriffon/KompoZer (aujourd'hui à l'abandon) et [Publii](https://getpublii.com/) (CMS de bureau pour sites statiques) — mais aucun n'est piloté par un design système.

L'équivalent fonctionnel le plus direct reste la combinaison web Utopia + uicolors + Realtime Colors — en trois onglets au lieu d'une application.

## Note Ubuntu

Ubuntu ≥ 24.04 restreint les espaces de noms non privilégiés, ce qui empêche le bac à sable interne de WebKit de démarrer pour les applications sans profil AppArmor. Thémo le détecte et désactive ce bac à sable — sans conséquence ici, l'aperçu ne rendant que du HTML généré localement.
