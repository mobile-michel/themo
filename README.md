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
2. **Tokens sémantiques** (`--background`, `--text`, `--accent`…) via un template au choix — *Neutre*, *Doux*, *Contrasté* — déclinés en clair et en sombre (`prefers-color-scheme` + `data-theme`) ;
3. **Styles appliqués directement aux éléments HTML** (`body`, `h1`, `a`, `button`, `table`, formulaires…) via un second template — *Moderne*, *Classique*, *Minimal*. Aucune classe : le HTML reste nu.

## Lancement

```bash
python3 themo.py
```

Dépendances (présentes sur la plupart des distributions avec GNOME) : `python3-gi`, GTK 4, libadwaita ≥ 1.5, WebKitGTK 6.0 et GtkSourceView 5 (`gir1.2-webkit-6.0` et `gir1.2-gtksource-5` sous Debian/Ubuntu).

Pour l'avoir dans le menu d'applications :

```bash
cp themo.desktop ~/.local/share/applications/
```

## Utilisation

- Le style graphique, tout en haut, prérègle l'ensemble des tokens selon son caractère (Moderne, Classique, Minimal) ; chaque token reste ensuite ajustable librement, et le bouton de réinitialisation réaligne le tout sur le style courant.
- La barre latérale modifie les tokens, l'aperçu se met à jour en direct.
- Le sélecteur en haut change la page affichée ; le menu adjacent permet d'**ajouter** (depuis un modèle : page vide, Vitrine, Article, Formulaire), **dupliquer**, **renommer** et **supprimer** des pages. Le bouton lune bascule clair/sombre.
- Le bouton crayon ouvre l'**éditeur HTML** de la page courante (GtkSourceView, coloration syntaxique) ; l'aperçu se met à jour pendant la frappe. Seul le corps de la page s'édite — et pour rester fidèle au design système, n'utilisez pas d'attribut `class`.
- Le bouton **+** insère un **bloc** prêt à l'emploi dans la page courante : héro pleine largeur, titre et texte, grille de cartes, tableau, citation, formulaire de contact, questions fréquentes, illustration, séparateur. Chaque bloc est garanti sans classe et placé au bon endroit (le héro avant `<main>`, le reste en fin de contenu) ; réorganisez ensuite dans l'éditeur HTML.
- Le bouton d'**édition du texte** (curseur de sélection) rend l'aperçu directement éditable : cliquez et tapez dans la page, un liseré pointillé signale le mode actif. Les modifications sont synchronisées au fil de la frappe, et changer un token pendant l'édition met à jour les styles sans recharger la page. Ce mode est réservé au texte : pour la structure (ajouter des sections, des tableaux…), passez par l'éditeur HTML — les deux modes sont exclusifs. À noter : WebKit normalise le balisage de la page éditée (indentation perdue).
- Le travail s'organise en **projet** : un dossier contenant `themo.conf` (tokens, format INI), `design-system.css` et une page HTML complète par page du projet — des fichiers ordinaires, utilisables tels quels. Menu ☰ : Nouveau / Ouvrir / Enregistrer (Ctrl+S) / Enregistrer sous… Utilisez un dossier dédié par projet.
- Menu ☰ → **Exporter le CSS…** : écrit `design-system.css` seul ; **Exporter CSS + pages HTML…** : écrit aussi toutes les pages du projet.

Pour forcer un thème dans vos pages : `<html data-theme="dark">` ou `<html data-theme="light">` ; sans attribut, le thème suit le système.

Héro pleine largeur : placez une `<section>` directement dans `<body>`, avant `<main>` — son fond s'étend sur toute la largeur et son contenu reste aligné sur le conteneur (token `--gutter`). Le groupe « Mise en page » règle le rythme **macro** (largeur du contenu, espacement entre sections, grille de cartes), tandis que l'unité d'espacement règle le **micro** (intérieur des composants).

## Fichiers

- `themo.py` — application GTK4/Adwaita (fenêtre, aperçu WebKit, éditeur, export)
- `tokens.py` — calculs des tokens dérivés (OKLCH, échelles), préréglages
- `css_gen.py` — templates sémantiques + éléments, assemblage du CSS
- `pages.py` — modèles de pages HTML (sans classes)
- `project.py` — projet sur disque : tokens (INI) + pages HTML
- `themo.desktop` — lanceur pour le menu d'applications

## Note Ubuntu

Ubuntu ≥ 24.04 restreint les espaces de noms non privilégiés, ce qui empêche le bac à sable interne de WebKit de démarrer pour les applications sans profil AppArmor. Thémo le détecte et désactive ce bac à sable — sans conséquence ici, l'aperçu ne rendant que du HTML généré localement.
