"""Recherche d'images libres de droits via l'API Openverse.

Photos sous licence CC0 uniquement : utilisables sans attribution. Pendant
l'édition, les images vivent en data URI dans le corps des pages — l'aperçu
ne référence jamais de contenu distant. À l'enregistrement et à la
publication, elles sont sorties dans un dossier `images/` (fichiers
référencés en relatif, avec `loading="lazy"` et dimensions) ; au
rechargement, elles redeviennent des data URI. Voir `externalize` /
`internalize`.

Les emplacements d'images des modèles portent un attribut data-keywords :
il sert de requête pour l'illustration automatique à la création du projet
et préremplit la recherche lors d'un remplacement manuel.
"""

import base64
import hashlib
import html
import json
import os
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


# -- Images : data URI <-> fichiers du dossier images/ -----------------------

_EXT_FOR_MIME = {"image/jpeg": ".jpg", "image/png": ".png",
                 "image/gif": ".gif", "image/webp": ".webp"}
_MIME_FOR_EXT = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".png": "image/png", ".gif": "image/gif",
                 ".webp": "image/webp", ".svg": "image/svg+xml"}
_DATA_URI_RE = re.compile(r"data:(image/[a-z0-9.+-]+);base64,(.*)$", re.I | re.S)


def image_dimensions(data):
    """(largeur, hauteur) d'une image PNG/GIF/JPEG, ou None si inconnu."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        return (int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"))
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return (int.from_bytes(data[6:8], "little"),
                int.from_bytes(data[8:10], "little"))
    if data[:2] == b"\xff\xd8":  # JPEG : chercher un marqueur SOF
        i, n = 2, len(data)
        while i + 9 < n:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            if marker == 0xD8 or marker == 0xD9 or 0xD0 <= marker <= 0xD7:
                i += 2
            else:
                i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return None


def image_name(data, mime):
    """Nom de fichier stable (par contenu) sous images/."""
    ext = _EXT_FOR_MIME.get(mime.lower(), ".img")
    return f"images/{hashlib.sha1(data).hexdigest()[:16]}{ext}"


def externalize(body):
    """Sort les images raster en data URI vers des fichiers.

    Renvoie (corps réécrit, {nom_fichier: octets}). Les placeholders SVG
    en ligne sont laissés tels quels. Ajoute loading="lazy" et les
    dimensions si elles peuvent être lues. Idempotent.
    """
    files = {}

    def repl(m):
        tag = m.group(0)
        dm = _DATA_URI_RE.match(_attr(tag, "src") or "")
        if not dm:
            return tag
        mime = dm.group(1).lower()
        if mime.startswith("image/svg"):
            return tag  # placeholder : reste en ligne (léger)
        try:
            data = base64.b64decode(dm.group(2))
        except (ValueError, TypeError):
            return tag
        name = image_name(data, mime)
        files[name] = data
        tag = re.sub(r'src="[^"]*"', lambda _m: f'src="{name}"', tag, count=1)
        if "loading=" not in tag:
            tag = "<img loading=\"lazy\"" + tag[4:]
        dims = image_dimensions(data)
        if dims and "width=" not in tag:
            tag = f'<img width="{dims[0]}" height="{dims[1]}"' + tag[4:]
        return tag

    return _IMG_RE.sub(repl, body), files


def internalize(body, images):
    """Réinjecte en data URI les images référencées comme fichiers."""
    def repl(m):
        tag = m.group(0)
        src = _attr(tag, "src") or ""
        if src in images:
            mime = _MIME_FOR_EXT.get(os.path.splitext(src)[1].lower(),
                                     "image/jpeg")
            uri = data_uri(images[src], mime)
            return re.sub(r'src="[^"]*"', lambda _m: f'src="{uri}"',
                          tag, count=1)
        return tag
    return _IMG_RE.sub(repl, body)
