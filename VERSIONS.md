# Historique des versions — Thémo

Les versions sont ajoutées ici une fois validées, de la plus récente à la plus ancienne. Chaque entrée : titre et numéro, description courte, puis explication commentée.

---

## v1.6.0 — Édition WYSIWYG du texte dans l'aperçu (11 juin 2026)

**Description courte :** l'aperçu devient directement éditable au clic (designMode), avec synchronisation au fil de la frappe et mise à jour des tokens sans rechargement de la page.

**Explication commentée :**

- *Mode édition* — un bouton bascule (curseur de sélection) rend la page éditable comme un traitement de texte ; un liseré pointillé couleur d'accent signale le mode, porté par les attributs de `<body>` donc jamais enregistré.
- *Synchronisation événementielle* — un script injecté (UserContentManager) renvoie le `<body>` modifié à l'application à chaque frappe (débounce 200 ms via postMessage) ; le projet est à jour en permanence, la pastille ● s'allume dès la première retouche.
- *Pas de rechargement pendant l'édition* — les changements de tokens mettent à jour le `<style>` et le thème par JavaScript sans recharger la page : saisie et position du curseur préservées ; le mode se réactive automatiquement après un changement de page.
- *Garde-fous* — édition WYSIWYG et éditeur HTML source exclusifs (une seule source de vérité, resynchronisation en sortie de mode) ; les modifications ciblent la page réellement rendue et non la sélection courante (condition de course éliminée).
- *Limite documentée* — WebKit normalise le balisage de la page éditée : l'indentation d'origine est perdue à la première retouche WYSIWYG ; le mode est réservé au texte, la structure passe par l'éditeur HTML.

---

## v1.5.0 — Projets, édition des pages et pages supplémentaires (11 juin 2026)

**Description courte :** le travail s'organise en projet sur disque (tokens + pages), les pages s'éditent dans un éditeur HTML intégré avec aperçu en direct, et peuvent être ajoutées, dupliquées, renommées et supprimées.

**Explication commentée :**

- *Projet sur disque* — nouveau module `project.py` : un dossier par projet avec `themo.conf` (tokens au format INI via GLib.KeyFile, pas de JSON), `design-system.css` régénéré à chaque enregistrement, et une page HTML complète par page, liée à la feuille et utilisable hors de l'application. Menu ☰ Nouveau / Ouvrir (Ctrl+O) / Enregistrer (Ctrl+S) / Enregistrer sous… ; pastille ● dans la barre latérale en cas de modifications non enregistrées.
- *Gestion des pages* — ajout (Ctrl+N) depuis un modèle (Page vide, Vitrine, Article, Formulaire), duplication, renommage, suppression avec confirmation ; la dernière page est protégée ; noms de fichiers en slugs Unicode (`<title>` porte le nom de la page).
- *Éditeur HTML intégré* — GtkSourceView 5 (coloration, numéros de ligne, thème suivant le système) révélé sous l'aperçu par le bouton crayon ; l'aperçu se rafraîchit pendant la frappe ; seul le corps de la page s'édite. Nouvelle dépendance : `gir1.2-gtksource-5`.
- *Garde-fou* — le nettoyage des pages orphelines à l'enregistrement ne s'applique que dans un dossier déjà reconnu comme projet Thémo, jamais dans un dossier quelconque.
- *Limite assumée* — pas encore d'avertissement à la fermeture avec des modifications non enregistrées (prévu en suite possible avec l'édition WYSIWYG, phase 2 de l'étude de faisabilité).

---

## v1.4.0 — Le style graphique devient un préréglage complet (11 juin 2026)

**Description courte :** barre latérale réorganisée — Style graphique en tête, Ambiance des couleurs et mode sombre dans Couleurs — et chaque style graphique prérègle désormais l'ensemble des tokens selon son caractère.

**Explication commentée :**

- *Réorganisation* — « Style graphique » occupe le haut de la barre latérale ; « Ambiance des couleurs » et « Inclure le mode sombre » rejoignent le groupe Couleurs ; le groupe Templates disparaît.
- *Préréglages* — choisir Moderne, Classique ou Minimal aligne tous les tokens (couleurs, ambiance, typographie, taille, ratio, interligne, espacement, rayon, ombres, largeur, densité, cartes) sur le caractère du style : Moderne = bleu vif/ambre, Neutre, Geometric Humanist + Neo-Grotesque, rayons 8 px ; Classique = bleu profond/cuivre, Contrasté, Didone + Transitional + Monospace Slab Serif, 17 px, rayons 2 px, ombres discrètes ; Minimal = ardoise/gris bleuté, Doux, Industrial + Humanist, étroit et aéré, sans rayons ni ombres.
- *Ajustement libre* — après application du préréglage, chaque token reste modifiable individuellement ; un toast confirme l'alignement.
- *Réinitialisation* — le bouton réaligne les tokens sur le préréglage du style courant (et non plus sur un défaut unique) ; les défauts de l'application correspondent au préréglage Moderne.

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
