"""Recherche d'images libres de droits via l'API Openverse.

Photos sous licence CC0 uniquement : utilisables sans attribution. Les
images choisies sont téléchargées puis embarquées en data URI dans les
pages — l'aperçu ne référence jamais de contenu distant.

Les emplacements d'images des modèles portent un attribut data-keywords :
il sert de requête pour l'illustration automatique à la création du projet
et préremplit la recherche lors d'un remplacement manuel.
"""

import base64
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.openverse.org/v1/images/"
_HEADERS = {"User-Agent": "Themo (https://github.com/mobile-michel/themo)"}
TIMEOUT = 10  # secondes


def _get(url):
    """GET avec retentative sur la limite de débit (HTTP 429)."""
    req = urllib.request.Request(url, headers=_HEADERS)
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=TIMEOUT)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            time.sleep(float(exc.headers.get("Retry-After") or 4))


def search(keywords, count=10):
    """Résultats CC0 pour `keywords` : dicts (title, creator, thumbnail)."""
    query = urllib.parse.urlencode({
        "q": keywords, "license": "cc0", "page_size": count})
    with _get(f"{API_URL}?{query}") as resp:
        data = json.load(resp)
    return [{"title": r.get("title") or "",
             "creator": r.get("creator") or "",
             "thumbnail": r["thumbnail"]}
            for r in data.get("results", []) if r.get("thumbnail")]


def fetch(url):
    """Télécharge `url` ; renvoie (octets, type MIME)."""
    with _get(url) as resp:
        ctype = resp.headers.get_content_type() or "image/jpeg"
        return resp.read(), ctype


def data_uri(data, ctype):
    return f"data:{ctype};base64,{base64.b64encode(data).decode()}"


# -- Manipulation des <img> dans le corps des pages --------------------------

_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)


def _attr(tag, name):
    m = re.search(rf'{name}="([^"]*)"', tag, re.I)
    return m.group(1) if m else None


def placeholder_slots(body):
    """[(indice, mots-clés)] des images encore en placeholder SVG."""
    slots = []
    for i, m in enumerate(_IMG_RE.finditer(body)):
        keywords = _attr(m.group(0), "data-keywords")
        src = _attr(m.group(0), "src") or ""
        if keywords and src.startswith("data:image/svg"):
            slots.append((i, keywords))
    return slots


def replace_img(body, index, src, alt=None):
    """Remplace le src (et l'alt) de la `index`-ième <img> de la page."""
    for i, m in enumerate(_IMG_RE.finditer(body)):
        if i < index:
            continue
        tag = m.group(0)
        tag = re.sub(r'src="[^"]*"', lambda _m: f'src="{src}"', tag, count=1)
        if alt:
            escaped = html.escape(alt, quote=True)
            tag = re.sub(r'alt="[^"]*"', lambda _m: f'alt="{escaped}"',
                         tag, count=1)
        return body[:m.start()] + tag + body[m.end():]
    return body
