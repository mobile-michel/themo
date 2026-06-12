# Tutoriel Thémo

Ce tutoriel vous guide pas à pas : vous allez créer le design système d'un petit studio fictif, composer un site de trois pages sans écrire une seule classe CSS, puis exporter le tout. Comptez une vingtaine de minutes.

## Sommaire

1. [Installation et lancement](#1-installation-et-lancement)
2. [Tour de l'interface](#2-tour-de-linterface)
3. [Choisir un style graphique](#3-choisir-un-style-graphique)
4. [Ajuster les tokens](#4-ajuster-les-tokens)
5. [Gérer les pages](#5-gérer-les-pages)
6. [Composer une page avec les blocs](#6-composer-une-page-avec-les-blocs)
7. [Éditer le contenu](#7-éditer-le-contenu)
8. [Enregistrer le projet](#8-enregistrer-le-projet)
9. [Utiliser le CSS exporté](#9-utiliser-le-css-exporté)
10. [Référence rapide](#10-référence-rapide)

---

## 1. Installation et lancement

Thémo a besoin de Python 3 et des bibliothèques GNOME courantes :

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-webkit-6.0 gir1.2-gtksource-5
git clone https://github.com/mobile-michel/themo.git
cd themo
python3 themo.py
```

Pour ajouter Thémo au menu d'applications :

```bash
./install.sh
```

> **Note Ubuntu ≥ 24.04** — le système restreint les espaces de noms non privilégiés, ce qui bloque le bac à sable interne de WebKit. Thémo le détecte et le désactive automatiquement ; c'est sans conséquence, l'aperçu ne rendant que du HTML généré localement.

## 2. Tour de l'interface

La fenêtre se divise en deux :

- **À gauche, la barre latérale des tokens.** C'est là que se conçoit le   design système : style graphique, couleurs, typographie, espacements, mise en page. En haut, la flèche ↶ réaligne tous les tokens sur le style graphique courant.
- **À droite, l'aperçu.** Il se met à jour en direct à chaque réglage. Dans son en-tête :

| Élément | Rôle |
|---|---|
| 🌙 | Prévisualiser le thème sombre |
| Curseur de sélection | Éditer le texte directement dans l'aperçu |
| Corbeille | Supprimer un bloc en cliquant dans l'aperçu |
| Image | Remplacer une image en cliquant dans l'aperçu |
| Crayon | Ouvrir l'éditeur HTML de la page |
| Nom central | La page affichée |
| ⋮ | Gérer les pages, aller à une page |
| + | Insérer un bloc dans la page |
| Enregistrer | Enregistrer le projet (Ctrl+S) |
| ☰ | Projet (nouveau, ouvrir, enregistrer sous) et export |

Au lancement, un **écran d'accueil** propose de démarrer depuis un modèle de projet : Démonstration, Blog, Portfolio, Personnel, Événement, Institutionnel ou Page vide — chaque carte montre un schéma du modèle, sa description et son nombre de pages. Choisir un modèle applique d'office le style graphique assorti, et la case « Illustrer avec des photos libres de droits (Openverse) » remplace les images de remplissage par de vraies photos CC0 (décochez-la pour rester hors ligne). On retrouve le même écran via ☰ → *Nouveau projet*, et Échap le referme sans rien changer.

**Pour ce tutoriel, choisissez Démonstration** : trois pages — Vitrine, Article et Formulaire — qui vous serviront de matière première. (Au passage : la fenêtre retient ses dimensions d'une session à l'autre.)

## 3. Choisir un style graphique

Tout en haut de la barre latérale, le **Style graphique** est le premier choix à faire : il prérègle *tous* les tokens selon son caractère.

- **Moderne** — bleu vif et ambre, sans-serif géométrique, pastilles arrondies, ombres présentes.
- **Classique** — bleu profond et cuivre, titres Didone (esprit Bodoni), texte Transitional, contrasté, rayons discrets.
- **Minimal** — ardoise et gris bleuté, ambiance douce, étroit et aéré, sans rayons ni ombres.
- **Éditorial, Galerie, Chaleureux, Festif, Officiel** — pensés pour les modèles de projet (Blog, Portfolio, Personnel, Événement, Institutionnel) qui les appliquent d'office à l'accueil ; rien n'empêche de les utiliser ailleurs.

Essayez-les en observant l'aperçu : couleurs, polices, espacements et formes changent d'un coup. **Choisissez Classique** pour ce tutoriel.

Chaque token reste ensuite ajustable individuellement — le style n'est qu'un point de départ. Si vous vous perdez en route, la flèche ↶ ramène au préréglage du style courant.

## 4. Ajuster les tokens

Donnons une identité propre à notre studio fictif.

### Couleurs

1. **Couleur primaire** : cliquez la pastille et choisissez un vert  forêt, par exemple `#166534`. Toute la gamme 50→900 est recalculée  (en espace OKLCH, votre couleur exacte est conservée sur son palier),  ainsi que la gamme neutre, teintée de la même nuance.
2. **Couleur secondaire** : un ocre, par exemple `#a16207`. Elle colore les citations et la sélection de texte — sélectionnez du texte dans  l'aperçu pour la voir.
3. **Ambiance des couleurs** : la façon dont les couleurs sont appliquées aux rôles (fond, surface, texte, accent…). *Neutre*, *Doux* (fond teinté), *Contrasté*, *Encre* (papier et accents profonds), *Chaleureux* (fond teinté par la secondaire) ou *Vif* (surfaces saturées). Gardez Contrasté.
4. **Inclure le mode sombre** : laissé activé, le CSS exporté contient les deux thèmes. Le bouton 🌙 de l'aperçu permet de vérifier le rendu sombre à tout moment.

### Typographie

Les listes suivent la classification de [Modern Font Stacks](https://modernfontstacks.com/) : uniquement des piles de polices système, rien à télécharger.

- **Police des titres** et **Police du texte** : essayez Slab Serif pour les titres en gardant Transitional pour le texte.
- **Taille de base** et **Ratio de l'échelle** : la taille du texte courant et la progression des niveaux de titres. L'échelle complète (`--text-xs` → `--text-4xl`) est calculée.
- **Hauteur de ligne** : l'interligne du texte courant.

### Espacements, formes, mise en page

- **Unité d'espacement** : le micro-rythme — padding des boutons, des champs, des cartes (2 à 12 px par pas de 0,5).
- **Rayon de bordure** et **Opacité des ombres** : les formes.
- **Mise en page** : le macro-rythme — **Largeur du contenu** (étroit → pleine largeur), **Densité verticale** (espacement entre sections) et **Largeur min. des cartes** (le seuil de la grille automatique).

Micro et macro sont indépendants : resserrez l'intérieur des composants sans toucher à la respiration de la page, et inversement.

## 5. Gérer les pages

Le menu **⋮** à côté du nom de la page permet d'**ajouter** (Ctrl+N), **dupliquer**, **renommer** et **supprimer** des pages.

Ajoutez une page : menu ⋮ → *Ajouter une page…*, nommez-la « Tarifs » et partez du modèle *Page vide*.

Deux choses se produisent automatiquement :

1. La nouvelle page reçoit une **navigation complète** listant toutes les pages du projet, avec sa propre entrée marquée `aria-current="page"`.
2. Le lien « Tarifs » est **ajouté à la nav de toutes les autres pages**. De même, renommer ou supprimer une page met à jour les liens partout. Vos liens personnalisés (`href="#"`, liens externes) ne sont jamais touchés — chaque lien de page est identifié par son `href`.

Les liens sont **fonctionnels dans l'aperçu**, et c'est ainsi que l'on navigue : cliquez « Vitrine » dans la nav, l'aperçu y bascule et le nom en haut suit. Un lien externe s'ouvre dans votre navigateur. Si une page n'a plus de lien dans la nav, le menu ⋮ → *Aller à la page* y mène toujours (la page courante y est cochée).

## 6. Composer une page avec les blocs

Votre page « Tarifs » est presque vide. Le menu **+** insère des blocs prêts à l'emploi, garantis sans classe CSS et placés au bon endroit :

- *Pleine largeur* : **Héro** — bande qui s'étend sur toute la largeur, contenu aligné sur le reste de la page, insérée avant `<main>`.
- *Dans le contenu* : **Titre et texte**, **Grille de cartes**, **Tableau**, **Citation**, **Formulaire de contact**, **Questions fréquentes**, **Illustration**, **Séparateur** — insérés en fin de contenu.

Pour « Tarifs », insérez dans l'ordre : un **Héro pleine largeur**, un **Tableau**, une **Citation** et des **Questions fréquentes**. La page est structurée — reste à écrire le contenu.

Un bloc en trop ? Activez le bouton **corbeille** : le bloc survolé se surligne en rouge dans l'aperçu, un clic le supprime. L'en-tête, la nav et le pied de page ne sont jamais candidats — impossible de casser la structure par mégarde.

### Remplacer les images

Activez le bouton **image** et cliquez une illustration dans l'aperçu : un dialogue s'ouvre, prérempli avec les mots-clés de cet emplacement, et présente une grille de photos libres de droits (licence CC0, via Openverse — mots-clés anglais conseillés). Un clic remplace l'image : elle est téléchargée et embarquée dans la page, qui reste consultable hors ligne.

## 7. Éditer le contenu

Deux modes, complémentaires et exclusifs l'un de l'autre :

### Le texte : directement dans l'aperçu

Activez le bouton **curseur de sélection**. Un liseré pointillé entoure la page : cliquez n'importe quel texte et tapez, comme dans un traitement de texte. Remplacez « Un titre qui annonce la couleur » par votre titre, ajustez les cellules du tableau, la citation…

Les modifications sont synchronisées au fil de la frappe (la pastille ● s'allume dans la barre latérale). Vous pouvez même changer un token pendant l'édition : les styles se mettent à jour sans recharger la page ni perdre votre saisie.

> Ce mode est réservé au **texte**. WebKit normalise le balisage de la page éditée (l'indentation d'origine est perdue), et la structure se travaille dans l'éditeur HTML.

### La structure : l'éditeur HTML

Activez le bouton **crayon** : l'éditeur source s'ouvre sous l'aperçu (coloration syntaxique, numéros de ligne). Réorganisez les sections, dédoublez une carte, ajustez un attribut — l'aperçu suit la frappe.

Règle d'or du design système : **pas d'attribut `class`**. Tout le style vient des éléments HTML eux-mêmes ; si vous sentez le besoin d'une classe, c'est probablement qu'il manque un token ou un bloc.

> L'en-tête et le pied de page sont **communs à tout le site** : modifiez la marque ou le pied sur n'importe quelle page (dans l'aperçu ou l'éditeur), toutes les pages suivent. Seule la mise en évidence de la page courante (`aria-current`) reste propre à chacune.

## 8. Enregistrer le projet

**Ctrl+S** (ou le bouton *Enregistrer*). Au premier enregistrement, choisissez un dossier **dédié** — par exemple `~/Documents/studio/`. Le projet y prend cette forme :

```
studio/
├── themo.conf          ← tous les tokens (format INI)
├── design-system.css   ← la feuille générée, à jour
├── vitrine.html
├── article.html
├── formulaire.html
└── tarifs.html
```

Des fichiers ordinaires : ouvrez `tarifs.html` dans un navigateur, il fonctionne tel quel, liens compris. Le nom de chaque page vit dans sa balise `<title>`. Rouvrez le projet plus tard avec ☰ → *Ouvrir un projet…* (Ctrl+O) : tokens et pages reviennent exactement.

Le menu ☰ propose aussi l'export seul : **Exporter le CSS…** pour la feuille uniquement, **Exporter CSS + pages HTML…** pour tout copier ailleurs sans toucher au projet.

## 9. Utiliser le CSS exporté

`design-system.css` s'utilise dans n'importe quel projet :

```html
<link rel="stylesheet" href="design-system.css">
```

### Trois étages de variables

1. **Primitives** — gammes de couleurs, échelles : `--color-primary-500`, `--text-xl`, `--space-4`, `--radius-md`, `--shadow-2`…
2. **Sémantiques** — les rôles, c'est l'étage à consommer en priorité : `--background`, `--surface`, `--text`, `--text-muted`, `--border`, `--accent`, `--accent-soft`, `--on-accent`, `--link`, `--focus-ring`, `--accent-2` (secondaire), `--selection-background`…
3. **Éléments** — `body`, `h1`…`h6`, `a`, `button`, `table`, formulaires, `details`, `blockquote`… sont stylés directement : du HTML nu suffit.

### Recettes

- **Thème** : sans rien faire, la page suit le système. Pour forcer : `<html data-theme="dark">` ou `data-theme="light"`.
- **Héro pleine largeur** : placez une `<section>` directement dans `<body>`, avant `<main>` — fond sur toute la largeur, contenu aligné sur le conteneur (token `--gutter`).
- **Grille de cartes** : plusieurs `<article>` dans une `<section>` deviennent automatiquement une grille (seuil : `--card-min`).
- **Page courante** : marquez le lien de nav avec `aria-current="page"`.
- **Vos propres styles** : consommez les variables sémantiques — `background: var(--surface); border: 1px solid var(--border);` — elles suivent le thème clair/sombre toutes seules.

## 10. Référence rapide

### Raccourcis

| Raccourci | Action |
|---|---|
| Ctrl+S | Enregistrer le projet |
| Ctrl+O | Ouvrir un projet |
| Ctrl+N | Ajouter une page |

### Tokens générés

| Famille | Tokens |
|---|---|
| Couleurs | `--color-{primary,secondary,neutral}-{50…900}` |
| Polices | `--font-{heading,body,mono}` |
| Échelle typo | `--text-{xs,sm,base,lg,xl,2xl,3xl,4xl}` |
| Interlignes | `--leading-{tight,normal}` |
| Espacements | `--space-{1,2,3,4,6,8,12,16,24}` |
| Mise en page | `--container`, `--density`, `--card-min`, `--gutter` |
| Rayons | `--radius-{sm,md,lg,xl,full}` |
| Ombres | `--shadow-{1…5}` |
| Sémantiques | `--background`, `--surface`, `--text`, `--text-muted`, `--border`, `--border-strong`, `--accent`, `--accent-hover`, `--accent-soft`, `--on-accent`, `--link`, `--link-hover`, `--focus-ring`, `--code-background`, `--selection-background`, `--accent-2`, `--accent-2-soft` |

Bonne composition !
