"""Audit d'accessibilité des pages (corps HTML, sans classes).

Vérifications simples et locales, sans dépendance : images sans alternative
textuelle, titre principal absent ou multiple, niveaux de titres sautés,
liens vides, et attributs `class` (contraires au principe du design système).
Renvoie des messages lisibles, pas un score.
"""

import re

_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
_HEADING_RE = re.compile(r"<h([1-6])\b", re.I)
_EMPTY_LINK_RE = re.compile(r"<a\b[^>]*>\s*</a>", re.I)
_CLASS_RE = re.compile(r"<[^>]*\sclass\s*=", re.I)
_ALT_RE = re.compile(r"\balt\s*=", re.I)


def lint_page(body):
    """Liste de messages d'accessibilité pour le corps d'une page."""
    issues = []

    missing_alt = sum(1 for m in _IMG_RE.finditer(body)
                      if not _ALT_RE.search(m.group(0)))
    if missing_alt:
        issues.append(f"{missing_alt} image(s) sans attribut alt "
                      "(texte alternatif)")

    levels = [int(n) for n in _HEADING_RE.findall(body)]
    if not levels:
        issues.append("aucun titre (h1–h6)")
    else:
        h1 = levels.count(1)
        if h1 == 0:
            issues.append("pas de titre principal h1")
        elif h1 > 1:
            issues.append(f"{h1} titres h1 (un seul attendu par page)")
        prev = levels[0]
        for lvl in levels[1:]:
            if lvl > prev + 1:
                issues.append(f"niveau de titre sauté (h{prev} → h{lvl})")
                break
            prev = lvl

    empty_links = len(_EMPTY_LINK_RE.findall(body))
    if empty_links:
        issues.append(f"{empty_links} lien(s) sans texte")

    classes = len(_CLASS_RE.findall(body))
    if classes:
        issues.append(f"{classes} attribut(s) class (le design système "
                      "se passe de classes)")

    return issues


def lint_pages(pages):
    """[(nom_page, message)] pour toutes les pages ; vide si tout est conforme."""
    results = []
    for name, body in pages.items():
        for issue in lint_page(body):
            results.append((name, issue))
    return results
