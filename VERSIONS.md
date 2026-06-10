# Historique des versions — Thémo

Les versions sont ajoutées ici une fois validées, de la plus récente à la plus ancienne. Chaque entrée : titre et numéro, description courte, puis explication commentée.

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
