"""Templates HTML de démonstration — strictement sans classes CSS.

Ces pages servent à la fois d'aperçu dans l'application et de gabarits
exportés à côté de design-system.css. Tout le rendu vient des styles
appliqués aux éléments HTML par la feuille générée.
"""

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
      <li><a href="#" aria-current="page">Produit</a></li>
      <li><a href="#">Tarifs</a></li>
      <li><a href="#">Contact</a></li>
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
      <li><a href="#" aria-current="page">Articles</a></li>
      <li><a href="#">Archives</a></li>
      <li><a href="#">À propos</a></li>
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
    <img src="{_SVG_PLACEHOLDER}" alt="Illustration abstraite">
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
      <li><a href="#" aria-current="page">Documentation</a></li>
      <li><a href="#">Statut</a></li>
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
