# Tutoriel Thémo

Ce tutoriel vous guide pas à pas : vous allez créer le design système d'un petit studio fictif, composer un site de trois pages sans écrire une seule classe CSS, puis l'exporter et le publier en ligne. Comptez une vingtaine de minutes.

## Sommaire

1. [Installation et lancement](#1-installation-et-lancement)
2. [Tour de l'interface](#2-tour-de-linterface)
3. [Choisir un style graphique](#3-choisir-un-style-graphique)
4. [Ajuster les tokens](#4-ajuster-les-tokens)
5. [Gérer les pages](#5-gérer-les-pages)
6. [Composer une page avec les blocs](#6-composer-une-page-avec-les-blocs)
7. [Éditer le contenu](#7-éditer-le-contenu)
8. [Enregistrer le projet](#8-enregistrer-le-projet)
9. [Publier le site en ligne](#9-publier-le-site-en-ligne)
10. [Utiliser le CSS exporté](#10-utiliser-le-css-exporté)
11. [Référence rapide](#11-référence-rapide)

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

Optionnel, pour la publication (section 9) : `rsync` si vous publiez par SSH, et `gir1.2-secret-1` pour conserver jetons et mots de passe dans le trousseau (sinon ils sont stockés dans un fichier local protégé). La publication Netlify et FTP/FTPS ne demande rien de plus.

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
| ☰ | Annuler/rétablir, projet (nouveau, ouvrir, récent, enregistrer), réglages du site, accessibilité, export et publication |

En bas de la barre latérale, un groupe **Contraste** affiche en direct le rapport WCAG (AA/AAA) des couleurs pour le thème prévisualisé — pratique pour garder un texte lisible en ajustant les teintes.

Au lancement, un **écran d'accueil** propose de démarrer depuis un modèle de projet : Démonstration, Blog, Portfolio, Personnel, Événement, Institutionnel ou Page vide — chaque carte montre un schéma du modèle, sa description et son nombre de pages. Choisir un modèle applique d'office le style graphique assorti, et la case « Illustrer avec des photos libres de droits (Openverse) » remplace les images de remplissage par de vraies photos CC0 (décochez-la pour rester hors ligne). Tant que rien n'est choisi, l'aperçu derrière reste un canevas vierge (pas un site de démonstration). L'écran liste aussi vos **projets récents** (avec un bouton « En ligne » vers le site publié, le cas échéant) et un bouton *Ouvrir un projet…*. On le retrouve via ☰ → *Nouveau projet*, et Échap le referme sans rien changer.

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

Le menu **⋮** à côté du nom de la page permet d'**ajouter** (Ctrl+N), **dupliquer**, **renommer**, **supprimer** des pages, et **définir la page d'accueil** — celle qui sera publiée comme `index.html` (par défaut, la première du projet).

Ajoutez une page : menu ⋮ → *Ajouter une page…*, nommez-la « Tarifs » et partez du modèle *Page vide*.

Deux choses se produisent automatiquement :

1. La nouvelle page reçoit une **navigation complète** listant toutes les pages du projet, avec sa propre entrée marquée `aria-current="page"`.
2. Le lien « Tarifs » est **ajouté à la nav de toutes les autres pages**. De même, renommer ou supprimer une page met à jour les liens partout. Vos liens personnalisés (`href="#"`, liens externes) ne sont jamais touchés — chaque lien de page est identifié par son `href`.

Les liens sont **fonctionnels dans l'aperçu**, et c'est ainsi que l'on navigue : cliquez « Vitrine » dans la nav, l'aperçu y bascule et le nom en haut suit. Un lien externe s'ouvre dans votre navigateur. Si une page n'a plus de lien dans la nav, le menu ⋮ → *Aller à la page* y mène toujours (la page courante y est cochée).

## 6. Composer une page avec les blocs

Votre page « Tarifs » est presque vide. Le menu **+** insère des blocs prêts à l'emploi, garantis sans classe CSS et placés au bon endroit :

- *Pleine largeur* : **Héro** — bande qui s'étend sur toute la largeur, contenu aligné sur le reste de la page, insérée avant `<main>`.
- *Dans le contenu* : **Titre et texte**, **Grille de cartes**, **Tableau**, **Citation**, **Formulaire de contact**, **Questions fréquentes**, **Illustration**, **Appel à l'action**, **Liens sociaux**, **Séparateur** — insérés en fin de contenu.

Pour « Tarifs », insérez dans l'ordre : un **Héro pleine largeur**, un **Tableau**, une **Citation** et des **Questions fréquentes**. La page est structurée — reste à écrire le contenu.

Un bloc en trop ? Activez le bouton **corbeille** : le bloc survolé se surligne en rouge dans l'aperçu, un clic le supprime (un toast « Annuler » permet de revenir en arrière). L'en-tête, la nav et le pied de page ne sont jamais candidats — impossible de casser la structure par mégarde. Plus largement, **Ctrl+Z / Ctrl+Maj+Z** (ou ☰ → *Annuler/Rétablir*) défont et refont les opérations de structure : blocs, images, pages.

### Remplacer les images

Activez le bouton **image** et cliquez une illustration dans l'aperçu : un dialogue s'ouvre, prérempli avec les mots-clés de cet emplacement, et présente une grille de photos libres de droits (licence CC0, via Openverse — mots-clés anglais conseillés). Un clic remplace l'image. À l'enregistrement et à l'export, les images sont écrites comme **fichiers dans `images/`** (avec `loading="lazy"` et dimensions) plutôt qu'en base64 : pages plus légères, cacheables et indexables.

## 7. Éditer le contenu

Deux modes, complémentaires et exclusifs l'un de l'autre :

### Le texte : directement dans l'aperçu

Activez le bouton **curseur de sélection**. Un liseré pointillé entoure la page : cliquez n'importe quel texte et tapez, comme dans un traitement de texte. Remplacez « Un titre qui annonce la couleur » par votre titre, ajustez les cellules du tableau, la citation…

Les modifications sont synchronisées au fil de la frappe (la pastille ● s'allume dans la barre latérale). Vous pouvez même changer un token pendant l'édition : les styles se mettent à jour sans recharger la page ni perdre votre saisie.

Une **barre de formatage** apparaît dans l'en-tête : sélectionnez du texte puis cliquez **Gras** (`<strong>`), **Emphase** (`<em>`), **Surligner** (`<mark>`) ou **Lien** (une adresse vous est demandée). Recliquer le même bouton sur une sélection déjà formatée retire le formatage. Ctrl+B / Ctrl+I fonctionnent aussi et produisent des balises sémantiques (jamais de style en ligne).

> Ce mode est réservé au **texte**. WebKit normalise le balisage de la page éditée (l'indentation d'origine est perdue), et la structure se travaille dans l'éditeur HTML.

### La structure : l'éditeur HTML

Activez le bouton **crayon** : l'éditeur source s'ouvre sous l'aperçu (coloration syntaxique, numéros de ligne). Réorganisez les sections, dédoublez une carte, ajustez un attribut — l'aperçu suit la frappe.

Règle d'or du design système : **pas d'attribut `class`**. Tout le style vient des éléments HTML eux-mêmes ; si vous sentez le besoin d'une classe, c'est probablement qu'il manque un token ou un bloc.

> L'en-tête et le pied de page sont **communs à tout le site** : modifiez la marque ou le pied sur n'importe quelle page (dans l'aperçu ou l'éditeur), toutes les pages suivent. Seule la mise en évidence de la page courante (`aria-current`) reste propre à chacune.

## 8. Enregistrer le projet

**Ctrl+S** (ou le bouton *Enregistrer*). Au premier enregistrement, choisissez un dossier **dédié** — par exemple `~/Documents/studio/`. Le projet y prend cette forme :

```
studio/
├── themo.conf          ← tokens et métadonnées (format INI)
├── design-system.css   ← la feuille générée, à jour
├── index.html          ← la page d'accueil (Vitrine), servie à la racine
├── article.html
├── formulaire.html
├── tarifs.html
├── favicon.svg
├── robots.txt
└── images/             ← photos, si vous en avez inséré
```

Des fichiers ordinaires : ouvrez `tarifs.html` dans un navigateur, il fonctionne tel quel, liens compris. Le nom de chaque page vit dans sa balise `<title>`. La **page d'accueil** (menu ⋮ → *Définir comme page d'accueil*, la première par défaut) est écrite comme `index.html` — pas de doublon, et c'est ce qu'un serveur sert à la racine. Un `sitemap.xml` s'ajoute dès que l'adresse du site est connue (après publication). Rouvrez le projet plus tard avec ☰ → *Ouvrir un projet…* (Ctrl+O), ou via ☰ → *Ouvrir un projet récent…* : tout revient exactement.

Si vous fermez l'application avec des modifications non enregistrées, Thémo demande confirmation (Annuler / Quitter sans enregistrer / Enregistrer).

Le menu ☰ propose aussi l'export seul : **Exporter le CSS…** pour la feuille uniquement, **Exporter CSS + pages HTML…** pour copier le site complet ailleurs sans toucher au projet.

### Référencement et accessibilité

Avant de publier, deux réglages utiles :

- **Référencement** — ☰ → *Réglages du site…* fixe la langue et une description par défaut ; ⋮ → *Description de la page…* en donne une propre à chaque page. À l'export, chaque page reçoit un en-tête complet (description, langue, URL canonique, Open Graph, `theme-color`, favicon), et le site reçoit `robots.txt` et `sitemap.xml`.
- **Accessibilité** — ☰ → *Vérifier l'accessibilité…* parcourt les pages et signale les images sans `alt`, les titres manquants ou désordonnés, les liens vides et les attributs `class`. Combiné aux badges de contraste de la barre latérale, de quoi livrer un site lisible par tous.

## 9. Publier le site en ligne

Quand le site vous convient, ☰ → **Publier sur un serveur…** le met en ligne directement depuis Thémo. Trois méthodes, au choix dans le dialogue ; la destination est mémorisée par projet, et le bouton **Publier** renvoie l'adresse du site une fois l'envoi terminé.

- **Netlify** — le plus simple pour débuter. Collez un *jeton d'accès personnel* (l'aide « Comment créer le jeton ? » vous guide pas à pas sur le site de Netlify). Au premier envoi, Thémo crée le site et affiche son adresse ; les fois suivantes, il met à jour le même site. Aucun serveur à gérer, HTTPS automatique.
- **Serveur SSH** — pour un VPS ou un hébergement avec accès SSH. Indiquez `utilisateur@hôte:/chemin/` ; l'authentification se fait par clé SSH (jamais de mot de passe). L'aide « Quelles données indiquer ? » rappelle comment installer votre clé si besoin.
- **FTP / FTPS** — l'identifiant des hébergements mutualisés classiques. Renseignez hôte, utilisateur, mot de passe et, au besoin, un dossier distant (créé s'il n'existe pas ; laissez-le vide si votre compte vous dépose déjà dans la racine du site). Laissez **« Connexion sécurisée (FTPS) »** activé.

Le jeton et les mots de passe sont conservés dans le trousseau du système. Renseignez une **adresse publique** (facultative) pour que le bouton « Ouvrir » et l'écran d'accueil pointent vers votre site en ligne.

> Pensez à enregistrer le projet (Ctrl+S) après la première publication : la destination (et, pour Netlify, l'identifiant du site) est alors conservée dans `themo.conf`.

## 10. Utiliser le CSS exporté

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

## 11. Référence rapide

### Raccourcis

| Raccourci | Action |
|---|---|
| Ctrl+S | Enregistrer le projet |
| Ctrl+O | Ouvrir un projet |
| Ctrl+N | Ajouter une page |
| Ctrl+Z / Ctrl+Maj+Z | Annuler / Rétablir (opérations de structure) |
| Ctrl+B / Ctrl+I | Gras / Emphase (édition du texte dans l'aperçu) |

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
