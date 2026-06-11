"""Projet Thémo sur disque.

Un projet est un dossier contenant :
  - themo.conf          tokens et templates, format INI (GLib.KeyFile) ;
  - design-system.css   la feuille générée, toujours à jour ;
  - *.html              les pages, fichiers complets liés à la feuille,
                        donc consultables et éditables hors de l'application.

Dans l'application, seul le corps (<body>) des pages est édité ; le nom de
la page est porté par la balise <title>.
"""

import re
import unicodedata
from dataclasses import fields
from pathlib import Path

from gi.repository import GLib

from tokens import Config
from css_gen import generate_css
from pages import PAGES, wrap_export

_BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.S | re.I)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)


def slugify(name):
    norm = unicodedata.normalize("NFKD", name)
    ascii_ = norm.encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
    return slug or "page"


class Project:
    """Tokens + pages, avec chargement et enregistrement sur disque."""

    def __init__(self, cfg=None, pages=None, path=None):
        self.cfg = cfg or Config()
        self.pages = dict(pages) if pages is not None else dict(PAGES)
        self.path = Path(path) if path else None

    @property
    def name(self):
        return self.path.name if self.path else "Projet sans titre"

    # -- Enregistrement ------------------------------------------------------

    def save(self, path=None):
        if path is not None:
            self.path = Path(path)
        if self.path is None:
            raise ValueError("Aucun dossier de projet défini")
        self.path.mkdir(parents=True, exist_ok=True)
        # Ne nettoyer les pages orphelines que si le dossier était déjà un
        # projet Thémo : on ne supprime jamais rien dans un dossier quelconque.
        was_project = (self.path / "themo.conf").exists()

        kf = GLib.KeyFile()
        for f in fields(Config):
            value = getattr(self.cfg, f.name)
            if isinstance(value, bool):
                kf.set_boolean("tokens", f.name, value)
            elif isinstance(value, int):
                kf.set_integer("tokens", f.name, value)
            elif isinstance(value, float):
                kf.set_double("tokens", f.name, value)
            else:
                kf.set_string("tokens", f.name, value)
        kf.save_to_file(str(self.path / "themo.conf"))

        (self.path / "design-system.css").write_text(
            generate_css(self.cfg), encoding="utf-8")

        keep = set()
        for name, body in self.pages.items():
            filename = slugify(name) + ".html"
            keep.add(filename)
            (self.path / filename).write_text(
                wrap_export(body, name), encoding="utf-8")
        # retirer les fichiers des pages supprimées ou renommées
        if was_project:
            for f in self.path.glob("*.html"):
                if f.name not in keep:
                    f.unlink()

    # -- Chargement ------------------------------------------------------------

    @classmethod
    def load(cls, path):
        path = Path(path)
        conf = path / "themo.conf"
        if not conf.exists():
            raise FileNotFoundError(
                "themo.conf introuvable : ce dossier n'est pas un projet Thémo")

        kf = GLib.KeyFile()
        kf.load_from_file(str(conf), GLib.KeyFileFlags.NONE)
        cfg = Config()
        for f in fields(Config):
            default = getattr(cfg, f.name)
            try:
                if isinstance(default, bool):
                    value = kf.get_boolean("tokens", f.name)
                elif isinstance(default, int):
                    value = kf.get_integer("tokens", f.name)
                elif isinstance(default, float):
                    value = kf.get_double("tokens", f.name)
                else:
                    value = kf.get_string("tokens", f.name)
                setattr(cfg, f.name, value)
            except GLib.Error:
                pass  # clé absente ou invalide : la valeur par défaut reste

        pages = {}
        for f in sorted(path.glob("*.html")):
            text = f.read_text(encoding="utf-8")
            body = _BODY_RE.search(text)
            title = _TITLE_RE.search(text)
            name = title.group(1).strip() if title else f.stem
            pages[name] = (body.group(1).strip() + "\n") if body else text
        if not pages:
            pages = dict(PAGES)

        return cls(cfg, pages, path)
