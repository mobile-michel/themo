"""Templates HTML de démonstration — strictement sans classes CSS.

Ces pages servent à la fois d'aperçu dans l'application et de gabarits
exportés à côté de design-system.css. Tout le rendu vient des styles
appliqués aux éléments HTML par la feuille générée.
"""

import re
import unicodedata


def slugify(name):
    norm = unicodedata.normalize("NFKD", name)
    ascii_ = norm.encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
    return slug or "page"


_SVG_PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='800' height='360'%3E%3Crect width='800' height='360' "
    "fill='%23d0d7e2'/%3E%3Ccircle cx='400' cy='150' r='70' "
    "fill='%23ffffff' opacity='.7'/%3E%3Crect x='250' y='250' width='300' "
    "height='18' rx='9' fill='%23ffffff' opacity='.7'/%3E%3C/svg%3E"
)

PAGES = {
    "Vitrine": f"""\
<header>
  <nav>
    <strong>Atelier Lumen</strong>
    <ul>
      <li><a href="vitrine.html" aria-current="page">Vitrine</a></li>
      <li><a href="article.html">Article</a></li>
      <li><a href="formulaire.html">Formulaire</a></li>
    </ul>
  </nav>
</header>
<section>
  <h1>Concevez vos interfaces avec un système, pas au hasard</h1>
  <p>Atelier Lumen unifie couleurs, typographie et espacements dans
     <mark>une seule feuille de styles</mark>, prête à servir tous
     vos projets.</p>
  <p>
    <button>Commencer gratuitement</button>
    <a href="#">Voir la démonstration</a>
  </p>
</section>
<main>
  <section>
    <h2>Pourquoi un design système&nbsp;?</h2>
    <article>
      <h3>Cohérence</h3>
      <p>Chaque écran parle la même langue visuelle : mêmes teintes,
         mêmes rythmes, mêmes formes.</p>
    </article>
    <article>
      <h3>Rapidité</h3>
      <p>Plus de débat sur le bleu exact ou la taille du titre :
         les décisions sont déjà prises.</p>
    </article>
    <article>
      <h3>Accessibilité</h3>
      <p>Contrastes vérifiés, focus visibles et mode sombre intégré
         dès le départ.</p>
    </article>
  </section>

  <section>
    <h2>Des tarifs simples</h2>
    <table>
      <thead>
        <tr><th>Formule</th><th>Pour qui&nbsp;?</th><th>Prix</th></tr>
      </thead>
      <tbody>
        <tr><td>Solo</td><td>Indépendants</td><td>0&nbsp;€</td></tr>
        <tr><td>Studio</td><td>Petites équipes</td><td>19&nbsp;€ / mois</td></tr>
        <tr><td>Agence</td><td>Projets clients multiples</td><td>49&nbsp;€ / mois</td></tr>
      </tbody>
    </table>
  </section>

  <section>
    <h2>Ils en parlent</h2>
    <blockquote>
      <p>«&nbsp;Nous avons divisé par trois le temps passé sur le CSS.
         La feuille générée est devenue notre référence commune.&nbsp;»</p>
      <p><small>— Camille R., directrice artistique</small></p>
    </blockquote>
  </section>
</main>
<footer>
  <p>© 2026 Atelier Lumen — Tous droits réservés</p>
</footer>
""",

    "Article": f"""\
<header>
  <nav>
    <strong>Le Carnet</strong>
    <ul>
      <li><a href="vitrine.html">Vitrine</a></li>
      <li><a href="article.html" aria-current="page">Article</a></li>
      <li><a href="formulaire.html">Formulaire</a></li>
    </ul>
  </nav>
</header>
<main>
  <h1>Les variables CSS, colonne vertébrale d'un design système</h1>
  <p>Publié le 10 juin 2026 · 6 minutes de lecture</p>
  <hr>
  <p>Un design système n'a pas besoin d'un outillage lourd pour exister.
     Une feuille de styles bien construite, organisée autour de
     <mark>variables CSS</mark>, suffit à garantir la cohérence d'un site
     entier — et même de plusieurs.</p>

  <h2>Primitives et sémantique</h2>
  <p>La première couche définit les valeurs brutes&nbsp;: les gammes de
     couleurs, l'échelle typographique, les espacements. La seconde leur
     donne un <em>rôle</em>&nbsp;:</p>
  <pre><code>:root {{
  --background: var(--color-neutral-50);
  --text: var(--color-neutral-900);
  --accent: var(--color-primary-600);
}}</code></pre>
  <p>Les éléments HTML ne consomment que la couche sémantique. Changer de
     thème revient alors à changer quelques lignes, pas tout le fichier.</p>

  <blockquote>
    <p>Le meilleur design système est celui qu'on n'a pas besoin
       d'expliquer&nbsp;: il est lisible dans le CSS lui-même.</p>
  </blockquote>

  <h2>Ce que l'on gagne</h2>
  <ul>
    <li>un mode sombre obtenu en redéfinissant la couche sémantique&nbsp;;</li>
    <li>des contrastes maîtrisés, calculés une fois pour toutes&nbsp;;</li>
    <li>du HTML propre, sans classes utilitaires à rallonge.</li>
  </ul>

  <h3>Comparatif rapide</h3>
  <table>
    <caption>Approches de theming les plus courantes</caption>
    <thead>
      <tr><th>Approche</th><th>HTML</th><th>Changement de thème</th></tr>
    </thead>
    <tbody>
      <tr><td>Classes utilitaires</td><td>verbeux</td><td>laborieux</td></tr>
      <tr><td>CSS-in-JS</td><td>propre</td><td>coût à l'exécution</td></tr>
      <tr><td>Variables CSS</td><td>propre</td><td>instantané</td></tr>
    </tbody>
  </table>

  <figure>
    <img src="{_SVG_PLACEHOLDER}" alt="Illustration abstraite"
         data-keywords="abstract geometric pattern">
    <figcaption>Les trois couches d'un design système fondé sur les
      variables CSS.</figcaption>
  </figure>

  <p>Pour recharger l'aperçu, appuyez sur <kbd>Ctrl</kbd> + <kbd>R</kbd>.
     Le code source complet est disponible dans
     <code>design-system.css</code>.</p>
</main>
<footer>
  <p>© 2026 Le Carnet</p>
</footer>
""",

    "Formulaire": """\
<header>
  <nav>
    <strong>Support</strong>
    <ul>
      <li><a href="vitrine.html">Vitrine</a></li>
      <li><a href="article.html">Article</a></li>
      <li><a href="formulaire.html" aria-current="page">Formulaire</a></li>
    </ul>
  </nav>
</header>
<main>
  <h1>Nous contacter</h1>
  <p>Une question, un problème&nbsp;? Remplissez ce formulaire,
     nous répondons <mark>sous 24&nbsp;heures</mark>.</p>

  <form>
    <fieldset>
      <legend>Vos coordonnées</legend>
      <label for="nom">Nom complet</label>
      <input id="nom" type="text" placeholder="Marie Dupont">
      <label for="email">Adresse e-mail</label>
      <input id="email" type="email" placeholder="marie@exemple.fr">
      <label for="pays">Pays</label>
      <select id="pays">
        <option>Suisse</option>
        <option>France</option>
        <option>Belgique</option>
        <option>Canada</option>
      </select>
    </fieldset>

    <fieldset>
      <legend>Votre demande</legend>
      <label for="sujet">Sujet</label>
      <input id="sujet" type="text" placeholder="Objet de votre message">
      <label for="message">Message</label>
      <textarea id="message" placeholder="Décrivez votre demande…"></textarea>
      <p>
        <label><input type="checkbox" checked> M'envoyer une copie</label><br>
        <label><input type="radio" name="prio" checked> Priorité normale</label><br>
        <label><input type="radio" name="prio"> Priorité haute</label>
      </p>
    </fieldset>

    <button type="submit">Envoyer le message</button>
    <button type="button" disabled>Enregistrer le brouillon</button>
  </form>

  <details>
    <summary>Quels délais de réponse&nbsp;?</summary>
    <p>Sous 24&nbsp;heures ouvrées pour les demandes standard, sous
       4&nbsp;heures pour les priorités hautes.</p>
  </details>
  <details>
    <summary>Où trouver mes données&nbsp;?</summary>
    <p>Dans votre espace client, rubrique <em>Confidentialité</em>.</p>
  </details>
</main>
<footer>
  <p>© 2026 Support — <a href="#">Mentions légales</a></p>
</footer>
""",
}


# Modèles proposés à la création d'une page (les pages de démonstration
# servent de point de départ, copiées dans le projet).
BLANK_PAGE = """\
<header>
  <nav>
    <strong>Mon site</strong>
    <ul>
      <li><a href="#" aria-current="page">Accueil</a></li>
    </ul>
  </nav>
</header>
<main>
  <h1>Nouvelle page</h1>
  <p>Le contenu de cette page est à éditer.</p>
</main>
<footer>
  <p>© 2026</p>
</footer>
"""

MODELS = {"Page vide": BLANK_PAGE, **PAGES}


# ---------------------------------------------------------------------------
# Modèles de projet — jeux de pages complets proposés à la création d'un
# nouveau projet. Chaque page du modèle reçoit la même nav d'en-tête (liens
# en slugs, page courante marquée aria-current) et le même pied de page.
# ---------------------------------------------------------------------------

def _nav(brand, names, current):
    items = "".join(
        '      <li><a href="{}.html"{}>{}</a></li>\n'.format(
            slugify(n), ' aria-current="page"' if n == current else "", n)
        for n in names)
    return ("<header>\n  <nav>\n    <strong>" + brand + "</strong>\n"
            "    <ul>\n" + items + "    </ul>\n  </nav>\n</header>\n")


def _model(brand, footer, bodies):
    names = list(bodies)
    foot = f"<footer>\n  <p>{footer}</p>\n</footer>\n"
    return {name: _nav(brand, names, name) + body + foot
            for name, body in bodies.items()}


_BLOG = _model("Encre &amp; Café", "© 2026 Encre &amp; Café — un billet chaque jeudi", {
    "Accueil": """\
<main>
  <h1>Des mots, du papier et un peu de vapeur</h1>
  <p>Carnet d'une rédactrice indépendante&nbsp;: l'<mark>écriture au
     quotidien</mark>, des lectures et quelques trouvailles, publiées
     chaque jeudi.</p>
  <section>
    <h2>Derniers billets</h2>
    <article>
      <h3><a href="article.html">Écrire tous les jours, même mal</a></h3>
      <p><small>5 juin 2026 · 4 minutes</small></p>
      <p>La régularité compte plus que l'inspiration. Récit d'un mois
         d'écriture quotidienne, ratures comprises.</p>
    </article>
    <article>
      <h3><a href="article.html">Relire à voix haute</a></h3>
      <p><small>29 mai 2026 · 3 minutes</small></p>
      <p>Le moyen le plus sûr de débusquer les phrases bancales ne
         demande aucun outil&nbsp;: il suffit de s'écouter.</p>
    </article>
    <article>
      <h3><a href="article.html">Mes trois carnets</a></h3>
      <p><small>22 mai 2026 · 5 minutes</small></p>
      <p>Un pour les idées, un pour les brouillons, un pour les listes.
         Visite guidée d'un système faillible mais fidèle.</p>
    </article>
  </section>
  <section>
    <h2>Recevoir les billets</h2>
    <form>
      <label for="abo-email">Adresse e-mail</label>
      <input id="abo-email" type="email" placeholder="vous@exemple.fr">
      <button type="submit">S'abonner</button>
    </form>
  </section>
</main>
""",
    "Article": f"""\
<main>
  <h1>Écrire tous les jours, même mal</h1>
  <p>Publié le 5 juin 2026 · 4 minutes de lecture</p>
  <hr>
  <p>On attend souvent le bon moment pour écrire&nbsp;: le matin calme,
     la grande idée, la tasse fumante. Le bon moment n'existe pas —
     il n'y a que <mark>le moment où l'on s'assoit</mark>.</p>
  <h2>La règle des dix lignes</h2>
  <p>Dix lignes par jour, bonnes ou mauvaises. Les mauvaises s'effacent,
     les bonnes restent, et la page n'est plus jamais blanche.</p>
  <blockquote>
    <p>«&nbsp;Je n'écris pas parce que j'ai des idées&nbsp;;
       j'ai des idées parce que j'écris.&nbsp;»</p>
  </blockquote>
  <h2>Ce que le rituel change</h2>
  <ul>
    <li>la peur de commencer disparaît avec l'habitude&nbsp;;</li>
    <li>les idées arrivent en écrivant, rarement avant&nbsp;;</li>
    <li>relire la veille donne le point de départ du jour.</li>
  </ul>
  <figure>
    <img src="{_SVG_PLACEHOLDER}" alt="Illustration à remplacer"
         data-keywords="notebook handwriting pen">
    <figcaption>Le carnet du mois, ratures comprises.</figcaption>
  </figure>
  <p>La suite au prochain billet — ou sur la page
     <a href="a-propos.html">À propos</a>.</p>
</main>
""",
    "À propos": f"""\
<main>
  <h1>À propos</h1>
  <figure>
    <img src="{_SVG_PLACEHOLDER}" alt="Portrait à remplacer"
         data-keywords="writing desk coffee">
    <figcaption>Le bureau, le carnet, le café.</figcaption>
  </figure>
  <p>Je m'appelle <strong>Jeanne Borel</strong>, rédactrice indépendante.
     Ce carnet rassemble ce que j'apprends en écrivant pour les autres —
     et ce que je n'ose pas leur facturer.</p>
  <h2>Questions fréquentes</h2>
  <details>
    <summary>Puis-je republier un billet&nbsp;?</summary>
    <p>Oui, avec un lien vers l'original et le nom de l'autrice.</p>
  </details>
  <details>
    <summary>Acceptez-vous des articles invités&nbsp;?</summary>
    <p>Volontiers, si le sujet touche à l'écriture ou à la lecture.</p>
  </details>
</main>
""",
})


_PORTFOLIO = _model("Studio Méridien", "© 2026 Studio Méridien — design graphique", {
    "Accueil": """\
<section>
  <h1>Des identités visuelles qui tiennent la distance</h1>
  <p>Studio Méridien conçoit des marques, des livres et des sites
     <mark>simples, lisibles et durables</mark>.</p>
  <p>
    <button>Démarrer un projet</button>
    <a href="realisations.html">Voir les réalisations</a>
  </p>
</section>
<main>
  <section>
    <h2>Savoir-faire</h2>
    <article>
      <h3>Identité visuelle</h3>
      <p>Logotypes, palettes et typographies pensés comme un système,
         pas comme un coup d'éclat.</p>
    </article>
    <article>
      <h3>Édition</h3>
      <p>Livres, rapports et catalogues, de la maquette au bon à tirer.</p>
    </article>
    <article>
      <h3>Web</h3>
      <p>Sites sobres et rapides, construits sur un design système.</p>
    </article>
  </section>
  <section>
    <h2>Ils nous font confiance</h2>
    <blockquote>
      <p>«&nbsp;Le studio a donné à notre coopérative une image claire,
         déclinée du papier à l'écran sans une fausse note.&nbsp;»</p>
      <p><small>— Élise T., Coopérative du Val</small></p>
    </blockquote>
  </section>
</main>
""",
    "Réalisations": f"""\
<main>
  <h1>Réalisations</h1>
  <p>Une sélection de projets récents — identités, éditions et sites.</p>
  <section>
    <figure>
      <img src="{_SVG_PLACEHOLDER}" alt="Aperçu du projet"
           data-keywords="graphic design workspace">
      <figcaption>Coopérative du Val — identité complète, 2026.</figcaption>
    </figure>
    <figure>
      <img src="{_SVG_PLACEHOLDER}" alt="Aperçu du projet"
           data-keywords="vintage poster art">
      <figcaption>Festival du Doc — affiches et programme, 2025.</figcaption>
    </figure>
    <figure>
      <img src="{_SVG_PLACEHOLDER}" alt="Aperçu du projet"
           data-keywords="bookstore shelves">
      <figcaption>Librairie Page 12 — site et papeterie, 2025.</figcaption>
    </figure>
  </section>
  <section>
    <h2>Prestations</h2>
    <table>
      <thead>
        <tr><th>Prestation</th><th>Délai indicatif</th><th>À partir de</th></tr>
      </thead>
      <tbody>
        <tr><td>Identité visuelle</td><td>6 semaines</td><td>3&nbsp;800&nbsp;€</td></tr>
        <tr><td>Édition</td><td>4 semaines</td><td>1&nbsp;900&nbsp;€</td></tr>
        <tr><td>Site vitrine</td><td>5 semaines</td><td>2&nbsp;600&nbsp;€</td></tr>
      </tbody>
    </table>
  </section>
</main>
""",
    "Contact": """\
<main>
  <h1>Parlons de votre projet</h1>
  <p>Décrivez votre besoin en quelques lignes&nbsp;; nous répondons
     <mark>sous deux jours ouvrés</mark>.</p>
  <form>
    <label for="ct-nom">Nom</label>
    <input id="ct-nom" type="text" placeholder="Votre nom">
    <label for="ct-email">Adresse e-mail</label>
    <input id="ct-email" type="email" placeholder="vous@exemple.fr">
    <label for="ct-projet">Votre projet</label>
    <textarea id="ct-projet" placeholder="Contexte, envies, délais…"></textarea>
    <button type="submit">Envoyer</button>
  </form>
  <details>
    <summary>Travaillez-vous à distance&nbsp;?</summary>
    <p>Oui, la plupart de nos projets se mènent en visio et par écrit.</p>
  </details>
</main>
""",
})


_PERSONNEL = _model("Camille Vasseur", "© 2026 Camille Vasseur", {
    "Accueil": f"""\
<main>
  <h1>Bonjour, je suis Camille</h1>
  <figure>
    <img src="{_SVG_PLACEHOLDER}" alt="Portrait à remplacer"
         data-keywords="hiking mountain trail">
    <figcaption>Quelque part entre deux randonnées.</figcaption>
  </figure>
  <p>Développeuse le jour, photographe le week-end. Ce site rassemble
     <mark>ce que je fais et ce que j'aime</mark>, sans algorithme
     entre nous.</p>
  <h2>En ce moment</h2>
  <ul>
    <li>j'apprends la reliure japonaise&nbsp;;</li>
    <li>je photographie les gares de ma région&nbsp;;</li>
    <li>je relis <em>Le Rivage des Syrtes</em>, lentement.</li>
  </ul>
  <p>Mon parcours complet est sur la page
     <a href="parcours.html">Parcours</a>.</p>
</main>
""",
    "Parcours": """\
<main>
  <h1>Parcours</h1>
  <h2>Expérience</h2>
  <article>
    <h3>Développeuse front-end — Atelier Numérique</h3>
    <p>Depuis 2023. Interfaces accessibles pour des services publics.</p>
  </article>
  <article>
    <h3>Intégratrice — Agence Horizon</h3>
    <p>2020 – 2023. Sites éditoriaux, design systems, formation interne.</p>
  </article>
  <h2>Formation</h2>
  <ul>
    <li>Master informatique, université de Grenoble, 2020&nbsp;;</li>
    <li>Licence d'arts appliqués, 2018.</li>
  </ul>
  <h2>Compétences</h2>
  <table>
    <thead>
      <tr><th>Domaine</th><th>Outils</th></tr>
    </thead>
    <tbody>
      <tr><td>Web</td><td>HTML, CSS, JavaScript</td></tr>
      <tr><td>Design</td><td>Figma, Inkscape</td></tr>
      <tr><td>Photo</td><td>Argentique, Darktable</td></tr>
    </tbody>
  </table>
</main>
""",
    "Contact": """\
<main>
  <h1>Me contacter</h1>
  <p>Pour un projet, une question ou une balade photo&nbsp;:
     écrivez-moi, je réponds <mark>sous quelques jours</mark>.</p>
  <form>
    <label for="me-nom">Nom</label>
    <input id="me-nom" type="text" placeholder="Votre nom">
    <label for="me-email">Adresse e-mail</label>
    <input id="me-email" type="email" placeholder="vous@exemple.fr">
    <label for="me-message">Message</label>
    <textarea id="me-message" placeholder="Votre message…"></textarea>
    <button type="submit">Envoyer</button>
  </form>
  <h2>Ailleurs</h2>
  <ul>
    <li><a href="#">Mes photos</a></li>
    <li><a href="#">Mon code</a></li>
  </ul>
</main>
""",
})


_EVENEMENT = _model("Festival Interlude", "© 2026 Festival Interlude — Annecy", {
    "Accueil": """\
<section>
  <h1>Festival Interlude — musique de chambre au bord du lac</h1>
  <p>Trois jours de concerts <mark>du 21 au 23 août 2026</mark> à Annecy,
     dans des lieux qui n'accueillent jamais de musique le reste de
     l'année.</p>
  <p>
    <button>Réserver un pass</button>
    <a href="programme.html">Consulter le programme</a>
  </p>
</section>
<main>
  <section>
    <h2>L'édition 2026 en bref</h2>
    <article>
      <h3>Douze concerts</h3>
      <p>Du quatuor à cordes au récital de piano, dans six lieux
         du vieux bourg.</p>
    </article>
    <article>
      <h3>Trois créations</h3>
      <p>Des œuvres commandées à de jeunes compositrices, jouées
         pour la première fois.</p>
    </article>
    <article>
      <h3>Entrée libre le dimanche</h3>
      <p>Le concert de clôture, sur les quais, est ouvert à toutes
         et tous.</p>
    </article>
  </section>
  <section>
    <h2>La presse en parle</h2>
    <blockquote>
      <p>«&nbsp;Un festival à taille humaine, où l'on entend respirer
         les musiciens.&nbsp;»</p>
      <p><small>— La Gazette des Alpes, août 2025</small></p>
    </blockquote>
  </section>
</main>
""",
    "Programme": """\
<main>
  <h1>Programme</h1>
  <h2>Vendredi 21 août</h2>
  <table>
    <thead>
      <tr><th>Heure</th><th>Lieu</th><th>Concert</th></tr>
    </thead>
    <tbody>
      <tr><td>18&nbsp;h</td><td>Cour du château</td><td>Quatuor Lumen — Haydn, Ravel</td></tr>
      <tr><td>21&nbsp;h</td><td>Église Saint-Maurice</td><td>Récital d'orgue — Bach</td></tr>
    </tbody>
  </table>
  <h2>Samedi 22 août</h2>
  <table>
    <thead>
      <tr><th>Heure</th><th>Lieu</th><th>Concert</th></tr>
    </thead>
    <tbody>
      <tr><td>11&nbsp;h</td><td>Halle du marché</td><td>Trio Méandre — création</td></tr>
      <tr><td>18&nbsp;h</td><td>Jardin de l'Europe</td><td>Octuor à vents — Mozart</td></tr>
      <tr><td>21&nbsp;h</td><td>Théâtre municipal</td><td>Nuit du piano — Chopin, Liszt</td></tr>
    </tbody>
  </table>
  <h2>Dimanche 23 août</h2>
  <table>
    <thead>
      <tr><th>Heure</th><th>Lieu</th><th>Concert</th></tr>
    </thead>
    <tbody>
      <tr><td>17&nbsp;h</td><td>Quais du Thiou</td><td>Concert de clôture — entrée libre</td></tr>
    </tbody>
  </table>
  <details>
    <summary>Comment venir&nbsp;?</summary>
    <p>Tous les lieux sont à moins de dix minutes à pied de la gare
       d'Annecy. Parkings relais gratuits en périphérie.</p>
  </details>
</main>
""",
    "Inscription": """\
<main>
  <h1>Réserver un pass</h1>
  <p>Les places sont limitées&nbsp;: la réservation garantit l'accès
     à <mark>tous les concerts du pass choisi</mark>.</p>
  <form>
    <fieldset>
      <legend>Vos coordonnées</legend>
      <label for="ins-nom">Nom complet</label>
      <input id="ins-nom" type="text" placeholder="Marie Dupont">
      <label for="ins-email">Adresse e-mail</label>
      <input id="ins-email" type="email" placeholder="marie@exemple.fr">
    </fieldset>
    <fieldset>
      <legend>Votre pass</legend>
      <label for="ins-pass">Formule</label>
      <select id="ins-pass">
        <option>Pass 3 jours — 75&nbsp;€</option>
        <option>Pass week-end — 55&nbsp;€</option>
        <option>Concert à l'unité — 18&nbsp;€</option>
      </select>
      <p>
        <label><input type="checkbox" checked> Recevoir le programme détaillé</label><br>
        <label><input type="radio" name="tarif" checked> Plein tarif</label><br>
        <label><input type="radio" name="tarif"> Tarif réduit (justificatif demandé)</label>
      </p>
    </fieldset>
    <button type="submit">Valider la réservation</button>
  </form>
  <details>
    <summary>Puis-je annuler&nbsp;?</summary>
    <p>Oui, remboursement intégral jusqu'à sept jours avant le festival.</p>
  </details>
</main>
""",
})


_INSTITUTIONNEL = _model("Commune de Valrive", "© 2026 Commune de Valrive", {
    "Accueil": """\
<main>
  <h1>Bienvenue à Valrive</h1>
  <p>Toutes vos démarches et l'actualité de la commune,
     <mark>au même endroit</mark>.</p>
  <section>
    <h2>Démarches les plus demandées</h2>
    <article>
      <h3>État civil</h3>
      <p>Actes de naissance, mariage et décès, livret de famille.</p>
    </article>
    <article>
      <h3>Urbanisme</h3>
      <p>Permis de construire, déclarations de travaux, cadastre.</p>
    </article>
    <article>
      <h3>Vie scolaire</h3>
      <p>Inscriptions à l'école, cantine et accueil périscolaire.</p>
    </article>
  </section>
  <section>
    <h2>Horaires de la mairie</h2>
    <table>
      <thead>
        <tr><th>Jour</th><th>Matin</th><th>Après-midi</th></tr>
      </thead>
      <tbody>
        <tr><td>Lundi – vendredi</td><td>8&nbsp;h&nbsp;30 – 12&nbsp;h</td><td>13&nbsp;h&nbsp;30 – 17&nbsp;h</td></tr>
        <tr><td>Samedi</td><td>9&nbsp;h – 12&nbsp;h</td><td>fermé</td></tr>
      </tbody>
    </table>
  </section>
</main>
""",
    "Services": """\
<main>
  <h1>Services municipaux</h1>
  <h2>État civil et citoyenneté</h2>
  <p>Délivrance des actes, recensement citoyen, inscriptions sur les
     listes électorales. La plupart des demandes se font en ligne ou
     au guichet, sans rendez-vous.</p>
  <h2>Enfance et écoles</h2>
  <p>Inscriptions scolaires, restauration et accueil périscolaire.
     Les tarifs suivent le quotient familial.</p>
  <h2>Travaux et urbanisme</h2>
  <p>Dépôt des permis et déclarations préalables, consultation du plan
     local d'urbanisme.</p>
  <details>
    <summary>Quels documents pour un acte de naissance&nbsp;?</summary>
    <p>Une pièce d'identité suffit pour une demande vous concernant.</p>
  </details>
  <details>
    <summary>Quel délai pour un permis de construire&nbsp;?</summary>
    <p>Deux à trois mois selon la zone, à compter du dossier complet.</p>
  </details>
</main>
""",
    "Actualités": """\
<main>
  <h1>Actualités</h1>
  <article>
    <h2>Réfection de la rue des Tilleuls</h2>
    <p><small>Publié le 8 juin 2026</small></p>
    <p>Les travaux commencent le 22 juin pour six semaines. La
       circulation sera alternée&nbsp;; l'accès des riverains est
       maintenu.</p>
  </article>
  <hr>
  <article>
    <h2>Inscriptions scolaires ouvertes</h2>
    <p><small>Publié le 26 mai 2026</small></p>
    <p>Les inscriptions pour la rentrée 2026 sont ouvertes jusqu'au
       10 juillet, en mairie ou en ligne.</p>
  </article>
  <hr>
  <article>
    <h2>Marché des producteurs</h2>
    <p><small>Publié le 12 mai 2026</small></p>
    <p>Le marché reprend chaque dimanche matin sur la place de l'Église,
       d'avril à octobre.</p>
  </article>
</main>
""",
    "Contact": """\
<main>
  <h1>Contacter la mairie</h1>
  <p>Mairie de Valrive — 1&nbsp;place de la République, 74&nbsp;000 Valrive<br>
     Téléphone&nbsp;: 04&nbsp;50&nbsp;00&nbsp;00&nbsp;00</p>
  <form>
    <label for="ma-nom">Nom</label>
    <input id="ma-nom" type="text" placeholder="Votre nom">
    <label for="ma-email">Adresse e-mail</label>
    <input id="ma-email" type="email" placeholder="vous@exemple.fr">
    <label for="ma-objet">Service concerné</label>
    <select id="ma-objet">
      <option>État civil</option>
      <option>Urbanisme</option>
      <option>Vie scolaire</option>
      <option>Autre demande</option>
    </select>
    <label for="ma-message">Message</label>
    <textarea id="ma-message" placeholder="Votre demande…"></textarea>
    <button type="submit">Envoyer</button>
  </form>
</main>
""",
})


PROJECT_MODELS = {
    "Démonstration": PAGES,
    "Blog": _BLOG,
    "Portfolio": _PORTFOLIO,
    "Personnel": _PERSONNEL,
    "Événement": _EVENEMENT,
    "Institutionnel": _INSTITUTIONNEL,
    "Page vide": {
        "Accueil": _nav("Mon site", ["Accueil"], "Accueil") + """\
<main>
  <h1>Nouvelle page</h1>
  <p>Le contenu de cette page est à éditer.</p>
</main>
<footer>
  <p>© 2026</p>
</footer>
"""},
}

MODEL_DESCRIPTIONS = {
    "Démonstration": "Vitrine, article et formulaire : tous les éléments"
                     " du design système passés en revue.",
    "Blog": "Un carnet de billets : accueil, page article et À propos.",
    "Portfolio": "La vitrine d'un studio : savoir-faire, réalisations"
                 " en galerie et contact.",
    "Personnel": "Un site à son nom : présentation, parcours et contact.",
    "Événement": "Festival ou conférence : présentation, programme"
                 " et réservation.",
    "Institutionnel": "Commune ou organisme : démarches, services,"
                      " actualités et contact.",
    "Page vide": "Une seule page minimale, pour composer librement.",
}


# ---------------------------------------------------------------------------
# Blocs de composition — fragments sans classes, conformes au design système.
# Chaque entrée : nom -> (emplacement, html). Emplacements :
#   "hero"  pleine largeur, avant <main> ;
#   "main"  dans le contenu, avant </main>.
# ---------------------------------------------------------------------------

BLOCKS = {
    "Héro pleine largeur": ("hero", """\
<section>
  <h1>Un titre qui annonce la couleur</h1>
  <p>Une ou deux phrases pour situer le propos et donner envie
     de poursuivre la lecture.</p>
  <p>
    <button>Action principale</button>
    <a href="#">Action secondaire</a>
  </p>
</section>
"""),
    "Titre et texte": ("main", """\
  <section>
    <h2>Titre de section</h2>
    <p>Premier paragraphe. Présentez l'idée principale en quelques
       phrases courtes et concrètes.</p>
    <p>Second paragraphe, pour développer ou nuancer.</p>
  </section>
"""),
    "Grille de cartes": ("main", """\
  <section>
    <h2>Trois points clés</h2>
    <article>
      <h3>Premier point</h3>
      <p>Une phrase ou deux pour décrire ce point.</p>
    </article>
    <article>
      <h3>Deuxième point</h3>
      <p>Une phrase ou deux pour décrire ce point.</p>
    </article>
    <article>
      <h3>Troisième point</h3>
      <p>Une phrase ou deux pour décrire ce point.</p>
    </article>
  </section>
"""),
    "Tableau": ("main", """\
  <section>
    <h2>Comparatif</h2>
    <table>
      <caption>Légende du tableau</caption>
      <thead>
        <tr><th>Critère</th><th>Option A</th><th>Option B</th></tr>
      </thead>
      <tbody>
        <tr><td>Premier critère</td><td>oui</td><td>non</td></tr>
        <tr><td>Deuxième critère</td><td>non</td><td>oui</td></tr>
        <tr><td>Troisième critère</td><td>oui</td><td>oui</td></tr>
      </tbody>
    </table>
  </section>
"""),
    "Citation": ("main", """\
  <section>
    <blockquote>
      <p>«&nbsp;Une citation marquante, mise en valeur par la couleur
         secondaire du design système.&nbsp;»</p>
      <p><small>— Prénom Nom, fonction</small></p>
    </blockquote>
  </section>
"""),
    "Formulaire de contact": ("main", """\
  <section>
    <h2>Nous écrire</h2>
    <form>
      <label for="bloc-nom">Nom</label>
      <input id="bloc-nom" type="text" placeholder="Votre nom">
      <label for="bloc-email">Adresse e-mail</label>
      <input id="bloc-email" type="email" placeholder="vous@exemple.fr">
      <label for="bloc-message">Message</label>
      <textarea id="bloc-message" placeholder="Votre message…"></textarea>
      <button type="submit">Envoyer</button>
    </form>
  </section>
"""),
    "Questions fréquentes": ("main", """\
  <section>
    <h2>Questions fréquentes</h2>
    <details>
      <summary>Première question&nbsp;?</summary>
      <p>La réponse, en une ou deux phrases.</p>
    </details>
    <details>
      <summary>Seconde question&nbsp;?</summary>
      <p>La réponse, en une ou deux phrases.</p>
    </details>
  </section>
"""),
    "Illustration": ("main", f"""\
  <section>
    <figure>
      <img src="{_SVG_PLACEHOLDER}" alt="Illustration à remplacer"
           data-keywords="abstract background">
      <figcaption>Légende de l'illustration.</figcaption>
    </figure>
  </section>
"""),
    "Séparateur": ("main", "  <hr>\n"),
}


# ---------------------------------------------------------------------------
# Navigation principale : mise à jour automatique des liens entre pages.
# Les liens sont identifiés par leur href (slug de la page) ; les liens
# personnalisés (href="#", liens externes…) ne sont jamais touchés.
# ---------------------------------------------------------------------------

def _nav_ul_span(body):
    """Bornes (début, fin) du contenu du premier <ul> de la nav d'en-tête."""
    m = re.search(r"<header>.*?<nav>.*?<ul>", body, re.S | re.I)
    if not m:
        return None
    end = body.find("</ul>", m.end())
    return (m.end(), end) if end != -1 else None


def nav_add_link(body, name):
    """Ajoute en fin de nav un lien vers la page `name` (s'il n'y est pas)."""
    span = _nav_ul_span(body)
    if span is None:
        return body
    start, end = span
    href = f"{slugify(name)}.html"
    if f'href="{href}"' in body[start:end]:
        return body
    line_start = body.rfind("\n", start, end) + 1
    li = f'      <li><a href="{href}">{name}</a></li>\n'
    return body[:line_start] + li + body[line_start:]


def nav_remove_link(body, name):
    """Retire de la nav le lien vers la page `name`."""
    href = re.escape(f"{slugify(name)}.html")
    pattern = re.compile(
        r'[ \t]*<li>\s*<a\b[^>]*href="' + href + r'"[^>]*>.*?</a>\s*</li>[ \t]*\n?',
        re.S | re.I)
    return pattern.sub("", body, count=1)


def nav_rename_link(body, old, new):
    """Met à jour libellé et href du lien vers la page renommée."""
    old_href = re.escape(f"{slugify(old)}.html")
    new_href = f"{slugify(new)}.html"
    pattern = re.compile(
        r'(<a\b[^>]*?href=")' + old_href + r'("[^>]*>).*?(</a>)', re.S | re.I)
    return pattern.sub(rf"\g<1>{new_href}\g<2>{new}\g<3>", body, count=1)


def nav_set_links(body, names, current=None):
    """Remplace la nav entière par des liens vers `names` (page créée)."""
    span = _nav_ul_span(body)
    if span is None:
        return body
    start, end = span
    items = "".join(
        '      <li><a href="{}.html"{}>{}</a></li>\n'.format(
            slugify(n), ' aria-current="page"' if n == current else "", n)
        for n in names)
    return body[:start] + "\n" + items + "    " + body[end:]


# ---------------------------------------------------------------------------
# Charpente commune : <header> et <footer> sont partagés par tout le site.
# Toute modification sur une page est répercutée sur les autres, en
# préservant le lien aria-current propre à chaque page.
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.S | re.I)
_FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.S | re.I)


def _chrome(body):
    """Premier <header> et dernier <footer> de la page (None si absent)."""
    headers = _HEADER_RE.findall(body)
    footers = _FOOTER_RE.findall(body)
    return (headers[0] if headers else None,
            footers[-1] if footers else None)


def _strip_current(html):
    return re.sub(r'\s*aria-current="page"', "", html)


def _mark_current(header, name):
    """aria-current sur le lien vers la page `name`, retiré des autres."""
    header = _strip_current(header)
    href = re.escape(f"{slugify(name)}.html")
    return re.sub(r'(<a\b[^>]*?href="' + href + '")',
                  r'\1 aria-current="page"', header, count=1)


def _chrome_norm(html):
    """Forme canonique pour comparer : sans aria-current ni blancs variables
    (l'édition WYSIWYG renvoie un HTML aux espaces normalisés)."""
    return " ".join(_strip_current(html).split())


def propagate_chrome(pages, source):
    """Répercute l'en-tête et le pied de la page `source` sur les autres.

    Une page sans <header> ou sans <footer> n'en reçoit pas : l'absence est
    respectée comme un choix. Renvoie True si au moins une page a changé.
    """
    src_header, src_footer = _chrome(pages[source])
    changed = False
    for name, body in pages.items():
        if name == source:
            continue
        header, footer = _chrome(body)
        if (src_header and header
                and _chrome_norm(header) != _chrome_norm(src_header)):
            marked = _mark_current(src_header, name)
            body = _HEADER_RE.sub(lambda _m: marked, body, count=1)
            changed = True
        if (src_footer and footer
                and _chrome_norm(footer) != _chrome_norm(src_footer)):
            i = body.rfind(footer)
            body = body[:i] + src_footer + body[i + len(footer):]
            changed = True
        pages[name] = body
    return changed


def insert_block(body: str, name: str) -> str:
    """Insère un bloc dans le corps de page, à l'emplacement qui lui revient.

    Héro : avant <main>, sinon après </header>, sinon en tête.
    Contenu : avant </main>, sinon avant <footer>, sinon à la fin.
    """
    placement, html = BLOCKS[name]
    if placement == "hero":
        i = body.find("<main")
        if i != -1:
            return body[:i] + html + body[i:]
        i = body.find("</header>")
        if i != -1:
            j = i + len("</header>")
            if body[j:j + 1] == "\n":
                j += 1
            return body[:j] + html + body[j:]
        return html + body
    i = body.rfind("</main>")
    if i != -1:
        return body[:i] + html + body[i:]
    i = body.rfind("<footer")
    if i != -1:
        return body[:i] + html + body[i:]
    return body + html


def wrap_preview(body: str, css: str, theme: str | None = None) -> str:
    """Page complète avec CSS embarqué, pour l'aperçu WebKit."""
    attr = f' data-theme="{theme}"' if theme else ""
    return (f'<!DOCTYPE html>\n<html lang="fr"{attr}>\n<head>\n'
            f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<style>\n{css}\n</style>\n</head>\n<body>\n{body}</body>\n</html>\n')


def wrap_export(body: str, title: str) -> str:
    """Page complète liée à design-system.css, pour l'export."""
    return (f'<!DOCTYPE html>\n<html lang="fr">\n<head>\n'
            f'<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n'
            f'<link rel="stylesheet" href="design-system.css">\n'
            f'</head>\n<body>\n{body}</body>\n</html>\n')
