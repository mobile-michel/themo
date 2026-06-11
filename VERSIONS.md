# Historique des versions — Thémo

Les versions sont ajoutées ici une fois validées, de la plus récente à la plus ancienne. Chaque entrée : titre et numéro, description courte, puis explication commentée.

---

## v1.3.0 — Mise en page, navigation et couleur secondaire (11 juin 2026)

**Description courte :** nouveau groupe de réglages « Mise en page » avec héro pleine largeur, unité d'espacement plus fine, libellés de templates clarifiés, navigation principale stylée et couleur secondaire réaffectée aux citations et à la sélection.

**Explication commentée :**

- *Groupe « Mise en page »* — largeur du contenu (Étroit 40 rem / Moyen 56 rem / Large 72 rem / Pleine largeur, token `--container`), densité verticale (Compact / Normal / Aéré, token `--density`, limité au rythme macro pour ne pas doubler l'unité d'espacement qui règle le micro), largeur minimale des cartes (token `--card-min`). La hauteur de ligne (`--leading-normal`, 1,3 → 2,0) est placée dans le groupe Typographie.
- *Héro pleine largeur* — une `<section>` placée directement dans `<body>` avant `<main>` devient une bande full-bleed dont le contenu reste aligné sur le conteneur grâce au token calculé `--gutter`, partagé avec l'en-tête et le pied de page ; la page Vitrine l'utilise.
- *Unité d'espacement* — réglage fin de 2 à 12 px par pas de 0,5 (au lieu du choix 4/8 px).
- *Templates renommés* — « Sémantique » devient « Ambiance des couleurs » et « Éléments HTML » devient « Style graphique », avec sous-titres techniques ; l'en-tête du CSS exporté reprend ces termes.
- *Navigation principale* — liens de nav distincts des liens de contenu (couleur atténuée, graisse 500, sans soulignement, transition au survol), page courante signalée par `aria-current="page"` ; déclinaisons par style : pastille (Moderne), barre d'accent (Classique), soulignement décalé (Minimal).
- *Couleur secondaire* — retirée de `<mark>` (qui revient au ton primaire doux) ; elle colore désormais les citations (`blockquote`, bordure et fond teinté) et la sélection de texte (`::selection`). Tokens `--highlight`/`--highlight-text` remplacés par `--accent-2`/`--accent-2-soft`, déclinés dans les trois ambiances en clair et en sombre.

---

## v1.2.0 — Listes de polices dédiées par usage (11 juin 2026)

**Description courte :** sélecteurs de polices distincts pour les titres, le texte et le code, chacun avec sa propre liste de classifications Modern Font Stacks dans un ordre défini.

**Explication commentée :**

- *Police des titres* — Geometric Humanist (défaut), Industrial, Rounded Sans, Handwritten, Slab Serif, Antique, Didone, Old Style.
- *Police du texte* — Classical Humanist (défaut), Rounded Sans, Neo-Grotesque, Humanist, Antique, Transitional.
- *Police du code* — nouveau sélecteur : Monospace Code (défaut), Monospace Slab Serif ; le token `--font-mono` du CSS généré suit désormais ce choix au lieu d'être figé.
- *Réinitialisation* — la police du code fait partie des tokens restaurés par le bouton de réinitialisation ; « System UI » n'étant plus proposé, les défauts sont les premières entrées de chaque liste.

---

## v1.1.0 — Polices Modern Font Stacks, couleur secondaire, corrections (10 juin 2026)

**Description courte :** sélection des polices selon la classification de modernfontstacks.com (classées sans-serif, serif, monospace), couleur secondaire réellement utilisée dans les pages, correction du champ `select` sombre en thème clair, bouton de réinitialisation des tokens.

**Explication commentée :**

- *Polices* — les deux sélecteurs (titres et texte) proposent les 15 classifications officielles de https://modernfontstacks.com/ (piles de polices système uniquement, aucun téléchargement), classées par famille : sans-serif, puis serif, puis monospace, puis cursive. `--font-mono` utilise la pile « Monospace Code ».
- *Couleur secondaire* — nouveaux tokens sémantiques `--highlight` / `--highlight-text` mappés sur la gamme `--color-secondary-*` dans les trois templates sémantiques (clair et sombre), consommés par l'élément `<mark>` ; chaque page de démonstration contient désormais un passage surligné.
- *Correctif `select`* — avec `color-scheme: light dark` sur `:root` et un bureau sombre, WebKit rendait les contrôles natifs en sombre même en thème clair forcé. Le CSS généré ajoute un `color-scheme` explicite par thème (`:root[data-theme="light"] { color-scheme: light; }` et équivalent sombre).
- *Bouton de réinitialisation* — dans l'en-tête de la barre latérale, remet les neuf tokens de base à leurs valeurs par défaut en conservant les templates (sémantique, éléments HTML, mode sombre) ; la configuration est restaurée directement puis les widgets réalignés, avec toast de confirmation.

---

## v1.0.0 — Première version stable (10 juin 2026)

**Description courte :** générateur de design système pour Linux (GTK4/libadwaita) exportant un fichier CSS unique, sans JSON et sans classes CSS, avec aperçu en direct.

**Explication commentée :**

- *Tokens de base saisis, le reste calculé* — l'utilisateur ne fournit que   deux couleurs, les polices, une taille de base, un ratio typographique,   une unité d'espacement, un rayon et une opacité d'ombres. L'application   dérive automatiquement les gammes de couleurs 50→900 (espace OKLCH,   couleur saisie conservée telle quelle sur son palier), la gamme neutre   teintée, l'échelle typographique, les espacements, les rayons et cinq   niveaux d'ombres.
- *CSS à trois étages* — tokens primitifs dans `:root` ; tokens   sémantiques (`--background`, `--text`, `--accent`…) via un template au   choix (Neutre, Doux, Contrasté), déclinés en clair et en sombre (`prefers-color-scheme` + `data-theme`) ; styles appliqués directement aux éléments HTML via un second template (Moderne, Classique, Minimal). Aucune classe CSS : le HTML reste nu.
- *Aperçu en direct* — rendu WebKitGTK des trois pages de démonstration (Vitrine, Article, Formulaire), bascule clair/sombre indépendante du thème du bureau, mise à jour à chaque modification de token.
- *Export* — `design-system.css` seul, ou accompagné des trois gabarits HTML sans classes liés à la feuille de styles.
- *Compatibilité Ubuntu* — détection de la restriction AppArmor sur les espaces de noms non privilégiés (Ubuntu ≥ 24.04) et désactivation du bac à sable WebKit dans ce cas, sans risque puisque l'aperçu ne rend que du HTML généré localement.
