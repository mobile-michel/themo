"""Génération du fichier CSS final.

Trois étages, sans aucune classe CSS :
  1. tokens primitifs dans :root (couleurs, typo, espacements, rayons, ombres) ;
  2. tokens sémantiques (--background, --text, --accent…) via un template,
     en clair et en sombre ;
  3. styles appliqués directement aux éléments HTML via un second template.
"""

from datetime import date

from tokens import (
    Config, FONT_STACKS, FONT_MONO,
    color_scale, type_scale, spacing_scale, radius_scale, shadow_scale,
)


# ---------------------------------------------------------------------------
# Templates sémantiques : primitives -> rôles, en clair et en sombre
# ---------------------------------------------------------------------------

def _sem(background, surface, text, muted, border, border_strong,
         accent, accent_hover, accent_soft, on_accent,
         link, link_hover, focus, code_bg, selection):
    return {
        "background": background, "surface": surface,
        "text": text, "text-muted": muted,
        "border": border, "border-strong": border_strong,
        "accent": accent, "accent-hover": accent_hover,
        "accent-soft": accent_soft, "on-accent": on_accent,
        "link": link, "link-hover": link_hover,
        "focus-ring": focus, "code-background": code_bg,
        "selection-background": selection,
    }


def _v(name, step):
    return f"var(--color-{name}-{step})"


SEMANTIC_TEMPLATES = {
    "Neutre": {
        "light": _sem("#ffffff", _v("neutral", 50),
                      _v("neutral", 900), _v("neutral", 600),
                      _v("neutral", 200), _v("neutral", 300),
                      _v("primary", 600), _v("primary", 700),
                      _v("primary", 100), "#ffffff",
                      _v("primary", 700), _v("primary", 800),
                      _v("primary", 400), _v("neutral", 100),
                      _v("primary", 200)),
        "dark": _sem(_v("neutral", 900), _v("neutral", 800),
                     _v("neutral", 100), _v("neutral", 400),
                     _v("neutral", 700), _v("neutral", 600),
                     _v("primary", 400), _v("primary", 300),
                     _v("primary", 900), _v("neutral", 900),
                     _v("primary", 300), _v("primary", 200),
                     _v("primary", 500), _v("neutral", 800),
                     _v("primary", 800)),
    },
    "Doux": {
        "light": _sem(_v("primary", 50), "#ffffff",
                      _v("neutral", 800), _v("neutral", 500),
                      _v("primary", 100), _v("primary", 200),
                      _v("primary", 500), _v("primary", 600),
                      _v("primary", 100), "#ffffff",
                      _v("primary", 600), _v("primary", 700),
                      _v("primary", 300), _v("primary", 50),
                      _v("primary", 100)),
        "dark": _sem(_v("neutral", 900), _v("neutral", 800),
                     _v("neutral", 200), _v("neutral", 400),
                     _v("neutral", 800), _v("neutral", 700),
                     _v("primary", 400), _v("primary", 300),
                     _v("primary", 900), _v("neutral", 900),
                     _v("primary", 300), _v("primary", 200),
                     _v("primary", 500), _v("neutral", 800),
                     _v("primary", 800)),
    },
    "Contrasté": {
        "light": _sem("#ffffff", "#ffffff",
                      _v("neutral", 900), _v("neutral", 700),
                      _v("neutral", 400), _v("neutral", 500),
                      _v("primary", 700), _v("primary", 800),
                      _v("primary", 100), "#ffffff",
                      _v("primary", 800), _v("primary", 900),
                      _v("primary", 600), _v("neutral", 100),
                      _v("primary", 200)),
        "dark": _sem("#000000", _v("neutral", 900),
                     "#ffffff", _v("neutral", 300),
                     _v("neutral", 600), _v("neutral", 500),
                     _v("primary", 300), _v("primary", 200),
                     _v("primary", 900), _v("neutral", 900),
                     _v("primary", 200), _v("primary", 100),
                     _v("primary", 400), _v("neutral", 900),
                     _v("primary", 700)),
    },
}


# ---------------------------------------------------------------------------
# Templates « éléments » : styles sur les balises HTML, aucune classe
# ---------------------------------------------------------------------------

ELEMENT_BASE = """\
/* ---- Base ------------------------------------------------------------ */

*, *::before, *::after { box-sizing: border-box; }

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  background: var(--background);
  color: var(--text);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
}

::selection { background: var(--selection-background); }

:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

/* ---- Structure de page ------------------------------------------------ */

main {
  max-width: var(--container-md);
  margin-inline: auto;
  padding: var(--space-8) var(--space-4);
}

body > header,
body > footer {
  padding: var(--space-4);
  border-color: var(--border);
}

body > header nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  max-width: var(--container-lg);
  margin-inline: auto;
}

body > header nav ul {
  display: flex;
  gap: var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

body > footer {
  margin-top: var(--space-12);
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  text-align: center;
}

section { margin-block: var(--space-12); }

/* Une section contenant plusieurs <article> devient une grille de cartes */
section:has(> article) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  gap: var(--space-4);
}

section:has(> article) > h2,
section:has(> article) > p { grid-column: 1 / -1; }

article {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-1);
}

article > :first-child { margin-top: 0; }
article > :last-child { margin-bottom: 0; }

/* ---- Typographie ------------------------------------------------------ */

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  line-height: var(--leading-tight);
  margin-block: var(--space-8) var(--space-3);
  text-wrap: balance;
}

h1 { font-size: var(--text-4xl); margin-top: var(--space-4); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
h4 { font-size: var(--text-xl); }
h5 { font-size: var(--text-lg); }
h6 { font-size: var(--text-base); }

p, ul, ol, dl { margin-block: 0 var(--space-4); }

/* Le paragraphe qui suit immédiatement le h1 sert d'introduction */
h1 + p {
  font-size: var(--text-lg);
  color: var(--text-muted);
}

a { color: var(--link); }
a:hover { color: var(--link-hover); }

small { color: var(--text-muted); }

blockquote {
  margin: var(--space-6) 0;
  padding: var(--space-3) var(--space-4);
  border-inline-start: 4px solid var(--accent);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  background: var(--surface);
  color: var(--text-muted);
}

blockquote > :last-child { margin-bottom: 0; }

hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: var(--space-8) 0;
}

mark {
  background: var(--accent-soft);
  color: var(--text);
  padding: 0.1em 0.3em;
  border-radius: var(--radius-sm);
}

code, kbd, samp, pre { font-family: var(--font-mono); font-size: 0.925em; }

code, kbd {
  background: var(--code-background);
  padding: 0.15em 0.4em;
  border-radius: var(--radius-sm);
}

kbd { border: 1px solid var(--border-strong); border-bottom-width: 2px; }

pre {
  background: var(--code-background);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
}

pre code { background: none; padding: 0; }

/* ---- Médias ------------------------------------------------------------ */

img, video, svg, iframe { max-width: 100%; height: auto; }

img, video { border-radius: var(--radius-md); }

figure { margin: var(--space-6) 0; }

figcaption {
  margin-top: var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

/* ---- Tableaux ---------------------------------------------------------- */

table {
  width: 100%;
  border-collapse: collapse;
  margin-block: var(--space-6);
}

caption {
  margin-bottom: var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-sm);
  text-align: start;
}

th, td {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--border);
  text-align: start;
}

thead th { border-bottom: 2px solid var(--border-strong); }

tbody tr:hover { background: var(--surface); }

/* ---- Formulaires ------------------------------------------------------- */

button, input, select, textarea {
  font: inherit;
  color: inherit;
}

label {
  display: inline-block;
  margin-bottom: var(--space-1);
  font-weight: 500;
}

input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),
select, textarea {
  display: block;
  width: 100%;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
}

input:focus, select:focus, textarea:focus {
  border-color: var(--accent);
  outline: 2px solid var(--focus-ring);
  outline-offset: 0;
}

::placeholder { color: var(--text-muted); opacity: 1; }

textarea { resize: vertical; min-height: 6rem; }

input[type="checkbox"], input[type="radio"], input[type="range"] {
  accent-color: var(--accent);
}

fieldset {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin: 0 0 var(--space-6);
}

legend { padding-inline: var(--space-2); font-weight: 600; }

button, input[type="submit"], input[type="button"] {
  display: inline-block;
  background: var(--accent);
  color: var(--on-accent);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-4);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

button:hover, input[type="submit"]:hover, input[type="button"]:hover {
  background: var(--accent-hover);
}

button:active { transform: translateY(1px); }

button:disabled { opacity: 0.55; cursor: not-allowed; }

/* ---- Divers ------------------------------------------------------------ */

details {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  margin-block: var(--space-4);
}

summary { font-weight: 600; cursor: pointer; }

details[open] summary { margin-bottom: var(--space-2); }

dt { font-weight: 600; }
dd { margin: 0 0 var(--space-2); color: var(--text-muted); }
"""

ELEMENT_TEMPLATES = {
    "Moderne": """\
/* ---- Variante : Moderne ------------------------------------------------ */

h1, h2 { letter-spacing: -0.02em; }

a { text-decoration: none; }
a:hover { text-decoration: underline; }

article { border: none; box-shadow: var(--shadow-2); }

button, input[type="submit"], input[type="button"] {
  border-radius: var(--radius-full);
  padding-inline: var(--space-6);
}

body > header {
  position: sticky;
  top: 0;
  background: var(--background);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}
""",
    "Classique": """\
/* ---- Variante : Classique ---------------------------------------------- */

a { text-decoration: underline; }

h2 {
  border-bottom: 1px solid var(--border);
  padding-bottom: var(--space-2);
}

article {
  border-radius: var(--radius-sm);
  box-shadow: none;
}

thead th { background: var(--code-background); }

th, td { border: 1px solid var(--border); }

button, input[type="submit"], input[type="button"] {
  border-radius: var(--radius-sm);
}

body > header { border-bottom: 2px solid var(--border-strong); }
""",
    "Minimal": """\
/* ---- Variante : Minimal ------------------------------------------------ */

a { text-decoration: none; }
a:hover { text-decoration: underline; }

article { box-shadow: none; }

blockquote {
  border-inline-start-width: 2px;
  background: none;
}

button, input[type="submit"], input[type="button"] {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
}

button:hover, input[type="submit"]:hover, input[type="button"]:hover {
  background: var(--accent);
  color: var(--on-accent);
}

hr { width: var(--space-24); margin-inline: auto; }

body > footer { border-top: none; }
""",
}


# ---------------------------------------------------------------------------
# Assemblage du fichier CSS
# ---------------------------------------------------------------------------

def _block(selector, lines, indent="  "):
    body = "\n".join(f"{indent}{line}" for line in lines)
    return f"{selector} {{\n{body}\n}}"


def _semantic_lines(mapping):
    return [f"--{name}: {value};" for name, value in mapping.items()]


def generate_css(cfg: Config) -> str:
    primary = color_scale(cfg.primary)
    secondary = color_scale(cfg.secondary)
    neutral = color_scale(cfg.primary, neutral=True)
    texts = type_scale(cfg.base_size, cfg.ratio)
    spaces = spacing_scale(cfg.spacing_base)
    radii = radius_scale(cfg.radius)
    shadows = shadow_scale(cfg.shadow_alpha)
    semantic = SEMANTIC_TEMPLATES[cfg.semantic_template]

    root = []
    if cfg.include_dark:
        root.append("color-scheme: light dark;")
        root.append("")
    root.append("/* Couleurs primitives */")
    for name, scale in (("primary", primary), ("secondary", secondary),
                        ("neutral", neutral)):
        root += [f"--color-{name}-{step}: {value};" for step, value in scale.items()]
        root.append("")
    root.append("/* Typographie */")
    root.append(f"--font-heading: {FONT_STACKS[cfg.font_heading]};")
    root.append(f"--font-body: {FONT_STACKS[cfg.font_body]};")
    root.append(f"--font-mono: {FONT_MONO};")
    root += [f"--text-{name}: {value};" for name, value in texts.items()]
    root.append("--leading-tight: 1.2;")
    root.append("--leading-normal: 1.65;")
    root.append("")
    root.append("/* Espacements (1rem = 16px) */")
    root += [f"--space-{m}: {value};" for m, value in spaces.items()]
    root.append("--container-sm: 40rem;")
    root.append("--container-md: 56rem;")
    root.append("--container-lg: 72rem;")
    root.append("")
    root.append("/* Rayons de bordure */")
    root += [f"--radius-{name}: {value};" for name, value in radii.items()]
    root.append("")
    root.append("/* Ombres */")
    root += [f"--shadow-{level}: {value};" for level, value in shadows.items()]

    parts = [
        "/* ==========================================================================",
        "   design-system.css — généré par Thémo",
        f"   Date : {date.today().isoformat()}",
        f"   Base : primaire {cfg.primary} · secondaire {cfg.secondary}"
        f" · {cfg.base_size}px · ratio {cfg.ratio}",
        f"   Templates : sémantique « {cfg.semantic_template} »"
        f" · éléments « {cfg.element_template} »",
        "",
        "   Aucune classe CSS : les variables sont consommées directement par",
        "   les éléments HTML. Forcer un thème : <html data-theme=\"dark\">.",
        "   ========================================================================== */",
        "",
        "/* ---- 1. Tokens primitifs ---------------------------------------------- */",
        "",
        _block(":root", root),
        "",
        "/* ---- 2. Tokens sémantiques --------------------------------------------- */",
        "",
        _block(":root", _semantic_lines(semantic["light"])),
    ]

    if cfg.include_dark:
        dark_lines = _semantic_lines(semantic["dark"])
        media_inner = _block(
            ':root:not([data-theme="light"])', dark_lines, indent="    "
        )
        media_inner = "  " + media_inner[:-1] + "  }"
        parts += [
            "",
            f"@media (prefers-color-scheme: dark) {{\n{media_inner}\n}}",
            "",
            _block(':root[data-theme="dark"]', dark_lines),
        ]

    parts += [
        "",
        "/* ---- 3. Styles des éléments HTML --------------------------------------- */",
        "",
        ELEMENT_BASE,
        ELEMENT_TEMPLATES[cfg.element_template],
    ]

    return "\n".join(parts)
