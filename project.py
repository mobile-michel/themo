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
from pages import (PAGES, wrap_export, slugify,  # noqa: F401 (réexporté)
                   favicon_svg, robots_txt, sitemap_xml)
from openverse import externalize, internalize

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
        self.site = {"lang": "fr", "description": ""}  # métadonnées SEO
        self.descriptions = {}  # description par page (nom -> texte)

    def home_page(self):
        """Nom de la page exportée aussi comme index.html."""
        return self.home if self.home in self.pages else next(iter(self.pages))

    @property
    def name(self):
        return self.path.name if self.path else "Projet sans titre"

    # -- Métadonnées et fichiers du site -------------------------------------

    def base_url(self):
        """Adresse publique du site (sans / final), si elle est connue."""
        return (self.publish.get("url") or "").rstrip("/")

    def page_meta(self, name):
        """Métadonnées d'en-tête (SEO) pour la page `name`."""
        base = self.base_url()
        canonical = None
        if base:
            canonical = (base + "/" if name == self.home_page()
                         else f"{base}/{slugify(name)}.html")
        return {
            "lang": self.site.get("lang") or "fr",
            "description": (self.descriptions.get(name)
                            or self.site.get("description") or ""),
            "canonical": canonical,
            "theme_color": self.cfg.primary,
            "favicon": "favicon.svg",
        }

    def site_urls(self):
        """URL absolues du site (accueil à la racine), pour le sitemap."""
        base = self.base_url()
        if not base:
            return []
        home = self.home_page()
        urls = [base + "/"]
        urls += [f"{base}/{slugify(n)}.html" for n in self.pages if n != home]
        return urls

    def web_files(self):
        """Tous les fichiers du site publiable : nom -> contenu (str ou
        octets pour les images). Les images en data URI sont sorties dans
        images/."""
        files = {"design-system.css": generate_css(self.cfg)}
        images = {}
        bodies = {}
        for name, body in self.pages.items():
            bodies[name], imgs = externalize(body)
            images.update(imgs)
        for name in self.pages:
            files[slugify(name) + ".html"] = wrap_export(
                bodies[name], name, self.page_meta(name))
        home = self.home_page()
        files["index.html"] = wrap_export(
            bodies[home], home, self.page_meta(home))
        files["favicon.svg"] = favicon_svg(self.cfg.primary)
        files["robots.txt"] = robots_txt(self.base_url())
        urls = self.site_urls()
        if urls:
            files["sitemap.xml"] = sitemap_xml(urls)
        files.update(images)
        return files

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
        kf.set_string("site", "lang", self.site.get("lang") or "fr")
        kf.set_string("site", "description",
                      self.site.get("description") or "")
        for name, desc in self.descriptions.items():
            if desc and name in self.pages:
                kf.set_string("descriptions", slugify(name), desc)
        kf.save_to_file(str(self.path / "themo.conf"))

        # tous les fichiers du site (css, pages, index, favicon, robots,
        # sitemap, images/), construits une seule fois ici et à la publication
        files = self.web_files()
        for filename, content in files.items():
            target = self.path / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
        # retirer les pages et images orphelines (supprimées ou renommées)
        if was_project:
            keep = set(files)
            for f in self.path.glob("*.html"):
                if f.name not in keep:
                    f.unlink()
            img_dir = self.path / "images"
            if img_dir.is_dir():
                for f in img_dir.iterdir():
                    if f.is_file() and f"images/{f.name}" not in keep:
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

        # réinjecter les images du dossier images/ comme data URI (forme
        # de travail en mémoire), l'inverse de l'export
        img_dir = path / "images"
        if img_dir.is_dir():
            images = {f"images/{f.name}": f.read_bytes()
                      for f in img_dir.iterdir() if f.is_file()}
            if images:
                pages = {n: internalize(b, images) for n, b in pages.items()}

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
        for key in ("lang", "description"):
            try:
                project.site[key] = kf.get_string("site", key)
            except GLib.Error:
                pass
        # descriptions par page : indexées par slug dans le fichier,
        # réassociées au nom de chaque page
        for name in pages:
            try:
                project.descriptions[name] = kf.get_string(
                    "descriptions", slugify(name))
            except GLib.Error:
                pass
        return project
