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
from dataclasses import fields
from pathlib import Path

from gi.repository import GLib

from tokens import Config
from css_gen import generate_css
from pages import PAGES, wrap_export, slugify  # noqa: F401 (réexporté)

_BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.S | re.I)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)


class Project:
    """Tokens + pages, avec chargement et enregistrement sur disque."""

    def __init__(self, cfg=None, pages=None, path=None):
        self.cfg = cfg or Config()
        self.pages = dict(pages) if pages is not None else dict(PAGES)
        self.path = Path(path) if path else None
        self.home = None   # page d'accueil (index.html) ; défaut : la première
        self.publish = {}  # méthode et destination de publication

    def home_page(self):
        """Nom de la page exportée aussi comme index.html."""
        return self.home if self.home in self.pages else next(iter(self.pages))

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
        kf.set_string("project", "home", self.home_page())
        for key, value in self.publish.items():
            if value:
                kf.set_string("publish", key, value)
        kf.save_to_file(str(self.path / "themo.conf"))

        (self.path / "design-system.css").write_text(
            generate_css(self.cfg), encoding="utf-8")

        keep = {"index.html"}
        for name, body in self.pages.items():
            filename = slugify(name) + ".html"
            keep.add(filename)
            (self.path / filename).write_text(
                wrap_export(body, name), encoding="utf-8")
        # la page d'accueil est doublée en index.html, attendu des serveurs
        home = self.home_page()
        (self.path / "index.html").write_text(
            wrap_export(self.pages[home], home), encoding="utf-8")
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
            if f.name == "index.html":
                continue  # doublon généré de la page d'accueil
            text = f.read_text(encoding="utf-8")
            body = _BODY_RE.search(text)
            title = _TITLE_RE.search(text)
            name = title.group(1).strip() if title else f.stem
            pages[name] = (body.group(1).strip() + "\n") if body else text
        if not pages:
            pages = dict(PAGES)

        project = cls(cfg, pages, path)
        try:
            project.home = kf.get_string("project", "home")
        except GLib.Error:
            pass
        for key in ("method", "ssh_dest", "netlify_site", "url",
                    "ftp_host", "ftp_user", "ftp_path", "ftp_secure"):
            try:
                project.publish[key] = kf.get_string("publish", key)
            except GLib.Error:
                pass
        return project
