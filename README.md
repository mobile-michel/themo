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

Dépendances (présentes sur la plupart des distributions avec GNOME) : `python3-gi`, GTK 4, libadwaita ≥ 1.4, WebKitGTK 6.0 (`gir1.2-webkit-6.0` sous Debian/Ubuntu).

Pour l'avoir dans le menu d'applications :

```bash
cp themo.desktop ~/.local/share/applications/
```

## Utilisation

- La barre latérale modifie les tokens, l'aperçu se met à jour en direct.
- Le sélecteur en haut change la page de démonstration (Vitrine / Article / Formulaire) ; le bouton lune bascule clair/sombre.
- **Exporter → Exporter le CSS…** : écrit `design-system.css`.
- **Exporter → Exporter CSS + pages HTML…** : écrit en plus les trois gabarits HTML (sans classes) liés à la feuille de styles, pour tester ou démarrer un projet.

Pour forcer un thème dans vos pages : `<html data-theme="dark">` ou `<html data-theme="light">` ; sans attribut, le thème suit le système.

Héro pleine largeur : placez une `<section>` directement dans `<body>`, avant `<main>` — son fond s'étend sur toute la largeur et son contenu reste aligné sur le conteneur (token `--gutter`). Le groupe « Mise en page » règle le rythme **macro** (largeur du contenu, espacement entre sections, grille de cartes), tandis que l'unité d'espacement règle le **micro** (intérieur des composants).

## Fichiers

- `themo.py` — application GTK4/Adwaita (fenêtre, aperçu WebKit, export)
- `tokens.py` — calculs des tokens dérivés (OKLCH, échelles)
- `css_gen.py` — templates sémantiques + éléments, assemblage du CSS
- `pages.py` — gabarits HTML de démonstration (sans classes)
- `themo.desktop` — lanceur pour le menu d'applications

## Note Ubuntu

Ubuntu ≥ 24.04 restreint les espaces de noms non privilégiés, ce qui empêche le bac à sable interne de WebKit de démarrer pour les applications sans profil AppArmor. Thémo le détecte et désactive ce bac à sable — sans conséquence ici, l'aperçu ne rendant que du HTML généré localement.
