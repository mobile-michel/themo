#!/usr/bin/env python3
"""Thémo — générateur de design système CSS pour Linux (GTK4 / libadwaita).

Quelques tokens de base saisis dans la barre latérale, tout le reste est
dérivé automatiquement ; aperçu en direct via WebKitGTK ; pages éditables
(GtkSourceView) et organisées en projet sur disque ; export d'un fichier
design-system.css et de pages HTML, sans la moindre classe CSS.
"""

import json
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ubuntu ≥ 24.04 interdit les espaces de noms non privilégiés aux programmes
# sans profil AppArmor, ce qui casse le bac à sable bubblewrap de WebKit.
# L'aperçu ne rend que du HTML généré localement, jamais de contenu distant :
# désactiver ce bac à sable est ici sans conséquence.
_userns = Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns")
if _userns.exists() and _userns.read_text().strip() == "1":
    os.environ.setdefault("WEBKIT_DISABLE_SANDBOX_THIS_IS_DANGEROUS", "1")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")
gi.require_version("GtkSource", "5")
from gi.repository import (Adw, Gdk, Gio, GLib, Gtk, GtkSource,  # noqa: E402
                           Pango, WebKit)

# Trousseau de secrets (jeton Netlify) ; repli sur fichier 0600 sans libsecret
try:
    gi.require_version("Secret", "1")
    from gi.repository import Secret
    _SECRET_SCHEMA = Secret.Schema.new(
        "li.maillard.Themo", Secret.SchemaFlags.NONE,
        {"key": Secret.SchemaAttributeType.STRING})
except (ValueError, ImportError):
    Secret = None

from tokens import (Config, HEADING_FONTS, BODY_FONTS, CODE_FONTS,  # noqa: E402
                    RATIOS, CONTAINERS, DENSITIES, STYLE_PRESETS)
from css_gen import generate_css, SEMANTIC_TEMPLATES, ELEMENT_TEMPLATES  # noqa: E402
from pages import (MODELS, PROJECT_MODELS, MODEL_DESCRIPTIONS,  # noqa: E402
                   BLOCKS, insert_block, propagate_chrome,
                   nav_add_link, nav_remove_link, nav_rename_link,
                   nav_set_links, wrap_preview)
from project import Project, slugify  # noqa: E402
import openverse  # noqa: E402
import publish  # noqa: E402

APP_ID = "li.maillard.Themo"

# État de la fenêtre (dimensions, maximisation), conservé entre les sessions
STATE_FILE = Path(GLib.get_user_config_dir()) / "themo" / "state.conf"
# Secrets (jeton Netlify, mots de passe FTP) quand le trousseau est absent
SECRETS_FILE = STATE_FILE.parent / "secrets.conf"


def _state_keyfile():
    """state.conf existant (ou vide) — à modifier puis réenregistrer."""
    kf = GLib.KeyFile()
    try:
        kf.load_from_file(str(STATE_FILE), GLib.KeyFileFlags.NONE)
    except GLib.Error:
        pass
    return kf


def recent_projects():
    """Chemins des projets récents encore présents sur disque."""
    try:
        paths = _state_keyfile().get_string_list("recent", "projects")
    except GLib.Error:
        return []
    return [p for p in paths if (Path(p) / "themo.conf").exists()]


def remember_recent(path):
    paths = [str(path)] + [p for p in recent_projects() if p != str(path)]
    kf = _state_keyfile()
    kf.set_string_list("recent", "projects", paths[:6])
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        kf.save_to_file(str(STATE_FILE))
    except (GLib.Error, OSError):
        pass


def published_url(path):
    """URL en ligne d'un projet sur disque, si elle est connue."""
    kf = GLib.KeyFile()
    try:
        kf.load_from_file(str(Path(path) / "themo.conf"),
                          GLib.KeyFileFlags.NONE)
        return kf.get_string("publish", "url")
    except GLib.Error:
        return None

# Style graphique appliqué d'office au modèle de projet qui a le sien ;
# l'utilisateur peut ensuite en changer librement dans la barre latérale.
MODEL_STYLES = {
    "Blog": "Éditorial",
    "Portfolio": "Galerie",
    "Personnel": "Chaleureux",
    "Événement": "Festif",
    "Institutionnel": "Officiel",
}


def _model_thumbnail_svg(model):
    """Vignette d'un modèle de projet : schéma filaire de sa page d'accueil,
    coloré avec les couleurs du préréglage de style associé."""
    preset = STYLE_PRESETS[MODEL_STYLES.get(model, "Moderne")]
    p, s = preset["primary"], preset["secondary"]
    g, t = "#dde3ea", "#b6c0cb"  # filets / lignes de texte
    e = []

    def line(x, y, w, color, h=4):
        e.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' "
                 f"rx='{h / 2}' fill='{color}'/>")

    def box(x, y, w, h, color, rx=3, op=1.0):
        e.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' "
                 f"rx='{rx}' fill='{color}' opacity='{op}'/>")

    # en-tête commun : marque + liens de navigation
    line(12, 10, 30, p, 5)
    for x in (128, 148, 168):
        line(x, 11, 14, t, 3)
    box(0, 24, 200, 1, g, rx=0)

    if model == "Blog":
        line(12, 36, 104, t, 6)
        line(12, 47, 44, g, 3)
        for y in (60, 84, 108):
            line(12, y, 76, t, 5)
            line(12, y + 9, 176, g, 3)
            line(12, y + 15, 120, g, 3)
    elif model == "Portfolio":
        line(12, 36, 80, t, 6)
        for x in (12, 73, 134):
            box(x, 48, 54, 40, p, 2, 0.3)
            line(x, 94, 34, g, 3)
        line(12, 108, 140, g, 3)
        line(12, 116, 100, g, 3)
    elif model == "Personnel":
        e.append(f"<circle cx='34' cy='58' r='18' fill='{p}' opacity='0.3'/>")
        line(62, 44, 92, t, 6)
        line(62, 56, 120, g, 3)
        line(62, 64, 104, g, 3)
        for y, w in ((92, 130), (102, 112), (112, 124)):
            line(12, y, w, g, 3)
    elif model == "Événement":
        e.append("<defs><linearGradient id='h' x1='0' y1='0' x2='1' y2='1'>"
                 f"<stop offset='0' stop-color='{p}'/>"
                 f"<stop offset='1' stop-color='{s}'/></linearGradient></defs>")
        e.append("<rect x='12' y='32' width='176' height='32' rx='4' "
                 "fill='url(#h)' opacity='0.3'/>")
        line(24, 40, 96, t, 5)
        box(24, 50, 28, 8, p, rx=4)
        for y in (76, 90, 104, 118):
            line(12, y, 20, s, 4)
            line(40, y, 120, g, 4)
    elif model == "Institutionnel":
        for x in (12, 73, 134):
            box(x, 34, 54, 30, g, 3, 0.45)
            box(x, 34, 54, 3, p, rx=1.5)
        for y, w in ((76, 150), (88, 176), (100, 132), (112, 160)):
            line(12, y, w, g, 3)
    elif model == "Page vide":
        line(12, 40, 70, t, 6)
        line(12, 52, 110, g, 3)
    else:  # Démonstration
        box(12, 32, 176, 28, p, 4, 0.15)
        line(24, 40, 80, t, 5)
        line(24, 50, 56, g, 3)
        for x in (12, 73, 134):
            box(x, 68, 54, 34, g, 4, 0.45)
        line(12, 112, 120, g, 3)
        line(12, 121, 90, g, 3)

    return ("<svg xmlns='http://www.w3.org/2000/svg' width='200' "
            "height='140' viewBox='0 0 200 140'>"
            "<rect width='200' height='140' rx='8' fill='#ffffff'/>"
            + "".join(e) +
            f"<rect x='0.5' y='0.5' width='199' height='139' rx='8' "
            f"fill='none' stroke='{g}'/></svg>")


def _rgba_to_hex(rgba: Gdk.RGBA) -> str:
    return "#%02x%02x%02x" % (
        round(rgba.red * 255), round(rgba.green * 255), round(rgba.blue * 255)
    )


class ThemoWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # État initial neutre : un canevas vierge sous l'écran d'accueil,
        # pas le projet Démonstration (qu'on n'a pas encore choisi). C'est
        # aussi ce qui reste si l'on referme l'accueil sans rien choisir.
        self.project = Project(pages=dict(PROJECT_MODELS["Page vide"]))
        self.cfg = self.project.cfg
        self._refresh_id = 0
        self._setters = {}   # attr -> fn(valeur) pour réaligner les widgets
        self._loading = False    # vrai pendant la synchronisation des widgets
        self._buffer_lock = False  # vrai pendant le chargement de l'éditeur
        self._dirty = False
        self._loaded_page = None  # page actuellement rendue dans l'aperçu
        self._current_page = None  # page affichée et éditée
        self._illustrate_token = None    # invalidation des illustrations
        self._image_search_token = None  # invalidation des recherches
        self._close_after_save = False   # fermeture demandée via le dialogue

        self._restore_window_state()
        self.connect("close-request", self._on_close_request)

        split = Adw.OverlaySplitView()
        split.set_min_sidebar_width(330)
        split.set_max_sidebar_width(380)
        split.set_sidebar(self._build_sidebar())
        split.set_content(self._build_content())

        self.toasts = Adw.ToastOverlay()
        self.toasts.set_child(split)
        self.set_content(self.toasts)

        self._install_actions()
        self._update_title()
        self._show_page()

    # -- État de la fenêtre --------------------------------------------------

    def _restore_window_state(self):
        self.set_default_size(1280, 900)
        kf = GLib.KeyFile()
        try:
            kf.load_from_file(str(STATE_FILE), GLib.KeyFileFlags.NONE)
            width = kf.get_integer("window", "width")
            height = kf.get_integer("window", "height")
            if width > 0 and height > 0:
                self.set_default_size(width, height)
            if kf.get_boolean("window", "maximized"):
                self.maximize()
        except GLib.Error:
            pass  # premier lancement ou fichier invalide : taille par défaut

    def _save_window_state(self, *_args):
        # default-width/height suivent la taille courante hors maximisation
        kf = _state_keyfile()  # préserver les autres clés (projets récents)
        width, height = self.get_default_size()
        kf.set_integer("window", "width", width)
        kf.set_integer("window", "height", height)
        kf.set_boolean("window", "maximized", self.is_maximized())
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            kf.save_to_file(str(STATE_FILE))
        except (GLib.Error, OSError):
            pass  # ne jamais bloquer la fermeture pour un état non enregistré

    def _on_close_request(self, *_args):
        self._save_window_state()
        if not self._dirty:
            return False  # poursuivre la fermeture
        dialog = Adw.AlertDialog(
            heading="Modifications non enregistrées",
            body=f"Le projet « {self.project.name} » contient des "
                 f"modifications non enregistrées.")
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("discard", "Quitter sans enregistrer")
        dialog.add_response("save", "Enregistrer")
        dialog.set_response_appearance("discard",
                                       Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_response_appearance("save",
                                       Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("save")
        dialog.set_close_response("cancel")

        def done(d, result):
            response = d.choose_finish(result)
            if response == "discard":
                self._dirty = False
                self.close()
            elif response == "save":
                self._close_after_save = True
                self._project_save()
        dialog.choose(self, None, done)
        return True  # le dialogue décide de la suite

    # -- Barre latérale : les tokens de base --------------------------------

    def _build_sidebar(self):
        page = Adw.PreferencesPage()

        grp = Adw.PreferencesGroup(
            title="Style graphique",
            description="Prérègle tous les tokens selon son caractère",
        )
        row = self._combo_row("Style", list(ELEMENT_TEMPLATES),
                              "element_template")
        row.set_subtitle("Styles des balises HTML")
        grp.add(row)
        page.add(grp)

        grp = Adw.PreferencesGroup(title="Couleurs")
        grp.add(self._color_row("Couleur primaire", "primary"))
        grp.add(self._color_row("Couleur secondaire", "secondary"))
        row = self._combo_row("Ambiance des couleurs",
                              list(SEMANTIC_TEMPLATES), "semantic_template")
        row.set_subtitle("Tokens sémantiques")
        grp.add(row)
        dark = Adw.SwitchRow(title="Inclure le mode sombre")
        dark.set_active(self.cfg.include_dark)
        dark.connect("notify::active", self._on_switch, "include_dark")
        self._setters["include_dark"] = dark.set_active
        grp.add(dark)
        page.add(grp)

        grp = Adw.PreferencesGroup(
            title="Typographie",
            description="L'échelle complète est calculée automatiquement",
        )
        grp.add(self._combo_row("Police des titres", HEADING_FONTS,
                                "font_heading"))
        grp.add(self._combo_row("Police du texte", BODY_FONTS, "font_body"))
        grp.add(self._combo_row("Police du code", CODE_FONTS, "font_mono"))
        grp.add(self._spin_row("Taille de base (px)", 12, 24, "base_size"))
        grp.add(self._combo_row(
            "Ratio de l'échelle", [label for label, _ in RATIOS], "ratio",
            values=[v for _, v in RATIOS], default_index=2))
        grp.add(self._spin_row("Hauteur de ligne", 1.3, 2.0, "leading",
                               step=0.05, digits=2))
        page.add(grp)

        grp = Adw.PreferencesGroup(title="Espacements et formes")
        grp.add(self._spin_row("Unité d'espacement (px)", 2, 12,
                               "spacing_base", step=0.5, digits=1))
        grp.add(self._spin_row("Rayon de bordure (px)", 0, 32, "radius"))
        grp.add(self._spin_row("Opacité des ombres (%)", 0, 60, "shadow_alpha"))
        page.add(grp)

        grp = Adw.PreferencesGroup(
            title="Mise en page",
            description="Rythme macro de la page — l'unité d'espacement"
                        " règle, elle, l'intérieur des composants",
        )
        grp.add(self._combo_row("Largeur du contenu", list(CONTAINERS),
                                "container"))
        grp.add(self._combo_row("Densité verticale", list(DENSITIES),
                                "density"))
        grp.add(self._spin_row("Largeur min. des cartes (rem)", 10, 24,
                               "card_min"))
        page.add(grp)

        header = Adw.HeaderBar()
        self.win_title = Adw.WindowTitle(title="Thémo")
        header.set_title_widget(self.win_title)
        reset = Gtk.Button(
            icon_name="edit-undo-symbolic",
            tooltip_text="Réaligner les tokens sur le style graphique courant")
        reset.connect("clicked", self._reset_tokens)
        header.pack_start(reset)

        view = Adw.ToolbarView()
        view.add_top_bar(header)
        view.set_content(page)
        return view

    def _color_row(self, title, attr):
        row = Adw.ActionRow(title=title)
        btn = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
        rgba = Gdk.RGBA()
        rgba.parse(getattr(self.cfg, attr))
        btn.set_rgba(rgba)
        btn.set_valign(Gtk.Align.CENTER)
        btn.connect("notify::rgba", self._on_color, attr)

        def set_hex(value):
            rgba = Gdk.RGBA()
            rgba.parse(value)
            btn.set_rgba(rgba)
        self._setters[attr] = set_hex
        row.add_suffix(btn)
        row.set_activatable_widget(btn)
        return row

    def _combo_row(self, title, labels, attr, values=None, default_index=0):
        row = Adw.ComboRow(title=title)
        row.set_model(Gtk.StringList.new(labels))
        current = getattr(self.cfg, attr)
        options = values if values is not None else labels
        index = options.index(current) if current in options else default_index
        row.set_selected(index)
        row.connect("notify::selected", self._on_combo, attr, options)
        self._setters[attr] = lambda v: row.set_selected(options.index(v))
        return row

    def _spin_row(self, title, lo, hi, attr, step=1, digits=0):
        row = Adw.SpinRow.new_with_range(lo, hi, step)
        row.set_digits(digits)
        row.set_title(title)
        row.set_value(getattr(self.cfg, attr))
        row.connect("notify::value", self._on_spin, attr)
        self._setters[attr] = row.set_value
        return row

    # -- Zone d'aperçu et éditeur ----------------------------------------------

    def _build_content(self):
        # À chaque modification du contenu (mode édition), la page renvoie
        # son <body> à l'application — synchronisation événementielle.
        ucm = WebKit.UserContentManager()
        ucm.register_script_message_handler("edited", None)
        ucm.connect("script-message-received::edited", self._on_wysiwyg_edit)
        sync_js = """
        (function () {
          let t = null;
          document.addEventListener('input', function () {
            clearTimeout(t);
            t = setTimeout(function () {
              window.webkit.messageHandlers.edited.postMessage(
                document.body.innerHTML);
            }, 200);
          });
        })();
        """
        ucm.add_script(WebKit.UserScript.new(
            sync_js, WebKit.UserContentInjectedFrames.TOP_FRAME,
            WebKit.UserScriptInjectionTime.END, None, None))

        # Mode « supprimer un bloc » : survol = surlignage du bloc candidat
        # (enfant direct de <main>, ou section héro sous <body>), clic =
        # suppression puis renvoi du <body> à l'application.
        ucm.register_script_message_handler("blockRemoved", None)
        ucm.connect("script-message-received::blockRemoved",
                    self._on_block_removed)
        delete_js = """
        (function () {
          let armed = false, cur = null;
          function candidate(el) {
            while (el && el !== document.body) {
              const par = el.parentElement;
              if (par && (par.tagName === 'MAIN' ||
                  (par === document.body && el.tagName === 'SECTION')))
                return el;
              el = par;
            }
            return null;
          }
          function clear() {
            if (cur) { cur.style.outline = ''; cur.style.cursor = ''; }
            cur = null;
          }
          document.addEventListener('mouseover', function (ev) {
            if (!armed) return;
            const c = candidate(ev.target);
            if (c === cur) return;
            clear();
            if (c) {
              cur = c;
              cur.style.outline = '2px dashed #dc2626';
              cur.style.cursor = 'pointer';
            }
          });
          document.addEventListener('click', function (ev) {
            if (!armed) return;
            ev.preventDefault();
            ev.stopPropagation();
            const c = candidate(ev.target);
            if (!c) return;
            clear();
            c.remove();
            window.webkit.messageHandlers.blockRemoved.postMessage(
              document.body.innerHTML);
          }, true);
          window._themoBlockDelete = function (on) {
            armed = on;
            if (!on) clear();
          };
        })();
        """
        ucm.add_script(WebKit.UserScript.new(
            delete_js, WebKit.UserContentInjectedFrames.TOP_FRAME,
            WebKit.UserScriptInjectionTime.END, None, None))

        # Mode « remplacer une image » : survol = surlignage de l'image,
        # clic = envoi de son indice et de ses mots-clés à l'application.
        ucm.register_script_message_handler("imagePicked", None)
        ucm.connect("script-message-received::imagePicked",
                    self._on_image_picked)
        image_js = """
        (function () {
          let armed = false, cur = null;
          function clear() {
            if (cur) { cur.style.outline = ''; cur.style.cursor = ''; }
            cur = null;
          }
          document.addEventListener('mouseover', function (ev) {
            if (!armed) return;
            clear();
            if (ev.target.tagName === 'IMG') {
              cur = ev.target;
              cur.style.outline = '3px solid #2563eb';
              cur.style.cursor = 'pointer';
            }
          });
          document.addEventListener('click', function (ev) {
            if (!armed) return;
            ev.preventDefault();
            ev.stopPropagation();
            if (ev.target.tagName !== 'IMG') return;
            const imgs = Array.from(document.querySelectorAll('img'));
            const index = imgs.indexOf(ev.target);
            const keywords = ev.target.getAttribute('data-keywords') || '';
            clear();
            window.webkit.messageHandlers.imagePicked.postMessage(
              JSON.stringify({index: index, keywords: keywords}));
          }, true);
          window._themoImagePick = function (on) {
            armed = on;
            if (!on) clear();
          };
        })();
        """
        ucm.add_script(WebKit.UserScript.new(
            image_js, WebKit.UserContentInjectedFrames.TOP_FRAME,
            WebKit.UserScriptInjectionTime.END, None, None))

        self.webview = WebKit.WebView(user_content_manager=ucm)
        self.webview.set_vexpand(True)
        self.webview.connect("load-changed", self._on_load_changed)
        self.webview.connect("decide-policy", self._on_decide_policy)

        # La page courante s'affiche en titre ; on passe de page en page
        # par les liens de navigation de l'aperçu.
        self.page_label = Gtk.Label()
        self.page_label.add_css_class("heading")

        manage_menu = Gio.Menu()
        manage_menu.append("Ajouter une page…", "win.page-add")
        manage_menu.append("Dupliquer la page", "win.page-duplicate")
        manage_menu.append("Renommer la page…", "win.page-rename")
        manage_menu.append("Supprimer la page…", "win.page-delete")
        manage_menu.append("Définir comme page d'accueil", "win.page-home")
        # Garde-fou : toutes les pages restent accessibles ici, même si
        # leur lien a disparu de la navigation.
        self.pages_list_menu = Gio.Menu()
        pages_menu = Gio.Menu()
        pages_menu.append_section(None, manage_menu)
        pages_menu.append_section("Aller à la page", self.pages_list_menu)
        pages_btn = Gtk.MenuButton(icon_name="view-more-symbolic",
                                   menu_model=pages_menu,
                                   tooltip_text="Gérer les pages")

        full_width = Gio.Menu()
        in_content = Gio.Menu()
        for block_name, (placement, _html) in BLOCKS.items():
            item = Gio.MenuItem.new(block_name, None)
            item.set_action_and_target_value(
                "win.block-insert", GLib.Variant.new_string(block_name))
            (full_width if placement == "hero" else in_content).append_item(item)
        blocks_menu = Gio.Menu()
        blocks_menu.append_section("Pleine largeur", full_width)
        blocks_menu.append_section("Dans le contenu", in_content)
        blocks_btn = Gtk.MenuButton(icon_name="list-add-symbolic",
                                    menu_model=blocks_menu,
                                    tooltip_text="Insérer un bloc dans la page")

        title_box = Gtk.Box(spacing=6)
        title_box.append(self.page_label)
        title_box.append(pages_btn)
        title_box.append(blocks_btn)

        self.dark_toggle = Gtk.ToggleButton(
            icon_name="weather-clear-night-symbolic",
            tooltip_text="Prévisualiser le thème sombre")
        self.dark_toggle.connect("toggled", lambda *a: self._schedule_refresh())

        self.editor_toggle = Gtk.ToggleButton(
            icon_name="document-edit-symbolic",
            tooltip_text="Afficher l'éditeur HTML de la page")
        self.editor_toggle.connect("toggled", self._on_editor_toggled)

        self.wysiwyg_toggle = Gtk.ToggleButton(
            icon_name="edit-select-text-symbolic",
            tooltip_text="Éditer le texte directement dans l'aperçu")
        self.wysiwyg_toggle.connect("toggled", self._on_wysiwyg_toggled)

        self.delete_toggle = Gtk.ToggleButton(
            icon_name="user-trash-symbolic",
            tooltip_text="Supprimer des blocs en cliquant dans l'aperçu")
        self.delete_toggle.connect("toggled", self._on_delete_toggled)

        self.image_toggle = Gtk.ToggleButton(
            icon_name="image-x-generic-symbolic",
            tooltip_text="Remplacer une image en cliquant dans l'aperçu")
        self.image_toggle.connect("toggled", self._on_image_toggled)

        project_menu = Gio.Menu()
        sect = Gio.Menu()
        sect.append("Nouveau projet", "win.project-new")
        sect.append("Ouvrir un projet…", "win.project-open")
        sect.append("Ouvrir un projet récent…", "win.project-recent")
        sect.append("Enregistrer", "win.project-save")
        sect.append("Enregistrer sous…", "win.project-save-as")
        project_menu.append_section("Projet", sect)
        sect = Gio.Menu()
        sect.append("Exporter le CSS…", "win.export-css")
        sect.append("Exporter CSS + pages HTML…", "win.export-all")
        sect.append("Publier sur un serveur…", "win.publish")
        project_menu.append_section("Export", sect)
        burger = Gtk.MenuButton(icon_name="open-menu-symbolic",
                                menu_model=project_menu,
                                tooltip_text="Projet et export")

        export = Gtk.Button(label="Enregistrer")
        export.add_css_class("suggested-action")
        export.connect("clicked",
                       lambda *a: self.activate_action("win.project-save"))

        header = Adw.HeaderBar()
        header.set_title_widget(title_box)
        header.pack_start(self.dark_toggle)
        header.pack_start(self.wysiwyg_toggle)
        header.pack_start(self.delete_toggle)
        header.pack_start(self.image_toggle)
        header.pack_start(self.editor_toggle)
        header.pack_end(burger)
        header.pack_end(export)

        # éditeur HTML de la page courante
        GtkSource.init()
        self.src_buffer = GtkSource.Buffer()
        lang = GtkSource.LanguageManager.get_default().get_language("html")
        if lang:
            self.src_buffer.set_language(lang)
        self._update_editor_scheme()
        Adw.StyleManager.get_default().connect(
            "notify::dark", self._update_editor_scheme)
        self.src_buffer.connect("changed", self._on_editor_changed)

        src_view = GtkSource.View(buffer=self.src_buffer)
        src_view.set_monospace(True)
        src_view.set_show_line_numbers(True)
        src_view.set_tab_width(2)
        src_view.set_insert_spaces_instead_of_tabs(True)
        src_view.set_top_margin(6)
        src_view.set_left_margin(6)

        scroller = Gtk.ScrolledWindow(child=src_view)
        scroller.set_min_content_height(300)
        self.editor_revealer = Gtk.Revealer(child=scroller)
        self.editor_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_UP)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self.webview)
        box.append(self.editor_revealer)

        view = Adw.ToolbarView()
        view.add_top_bar(header)
        view.set_content(box)
        return view

    def _update_editor_scheme(self, *_args):
        dark = Adw.StyleManager.get_default().get_dark()
        scheme = GtkSource.StyleSchemeManager.get_default().get_scheme(
            "Adwaita-dark" if dark else "Adwaita")
        if scheme:
            self.src_buffer.set_style_scheme(scheme)

    # -- Pages -------------------------------------------------------------------

    def _current_page_name(self):
        if self._current_page not in self.project.pages:
            self._current_page = next(iter(self.project.pages))
        return self._current_page

    def _show_page(self, name=None):
        """Fait de `name` (ou d'une page valide) la page affichée et éditée."""
        if name in self.project.pages:
            self._current_page = name
        current = self._current_page_name()
        self.page_label.set_text(current)
        self.pages_list_menu.remove_all()
        for page in self.project.pages:
            item = Gio.MenuItem.new(page, None)
            item.set_action_and_target_value(
                "win.page-show", GLib.Variant.new_string(page))
            self.pages_list_menu.append_item(item)
        self._page_show_action.set_state(GLib.Variant.new_string(current))
        self._load_page_into_editor()
        self._schedule_refresh()

    def _page_show(self, _action, param):
        self._show_page(param.get_string())

    def _load_page_into_editor(self):
        self._buffer_lock = True
        self.src_buffer.set_text(
            self.project.pages.get(self._current_page_name(), ""))
        self._buffer_lock = False

    def _on_editor_toggled(self, btn):
        # exclusif avec l'édition dans l'aperçu : une seule source de vérité
        if btn.get_active() and self.wysiwyg_toggle.get_active():
            self.wysiwyg_toggle.set_active(False)
        if btn.get_active():
            self._load_page_into_editor()
        self.editor_revealer.set_reveal_child(btn.get_active())

    # -- Édition WYSIWYG dans l'aperçu ---------------------------------------

    def _run_js(self, code):
        self.webview.evaluate_javascript(code, -1, None, None, None,
                                         None, None)

    def _set_design_mode(self, active):
        if active:
            self._run_js(
                "document.designMode = 'on';"
                "document.body.style.outline = '3px dashed var(--accent)';"
                "document.body.style.outlineOffset = '-3px';")
        else:
            self._run_js(
                "document.designMode = 'off';"
                "document.body.style.outline = '';"
                "document.body.style.outlineOffset = '';")

    def _on_wysiwyg_toggled(self, btn):
        if btn.get_active():
            if self.editor_toggle.get_active():
                self.editor_toggle.set_active(False)
            if self.delete_toggle.get_active():
                self.delete_toggle.set_active(False)
            if self.image_toggle.get_active():
                self.image_toggle.set_active(False)
            self._set_design_mode(True)
            self.toasts.add_toast(Adw.Toast(
                title="Édition du texte activée — cliquez dans l'aperçu"))
        else:
            self._set_design_mode(False)
            self._load_page_into_editor()

    def _on_delete_toggled(self, btn):
        if btn.get_active():
            if self.wysiwyg_toggle.get_active():
                self.wysiwyg_toggle.set_active(False)
            if self.image_toggle.get_active():
                self.image_toggle.set_active(False)
            self._run_js("window._themoBlockDelete(true);")
            self.toasts.add_toast(Adw.Toast(
                title="Cliquez un bloc dans l'aperçu pour le supprimer"))
        else:
            self._run_js("window._themoBlockDelete(false);")

    def _on_block_removed(self, _ucm, value):
        if self._loaded_page not in self.project.pages:
            return
        html = value.to_string()
        if not html.endswith("\n"):
            html += "\n"
        self.project.pages[self._loaded_page] = html
        self._touch()
        self._load_page_into_editor()
        self.toasts.add_toast(Adw.Toast(title="Bloc supprimé"))

    # -- Remplacement d'images (Openverse) ------------------------------------

    def _on_image_toggled(self, btn):
        if btn.get_active():
            if self.wysiwyg_toggle.get_active():
                self.wysiwyg_toggle.set_active(False)
            if self.delete_toggle.get_active():
                self.delete_toggle.set_active(False)
            self._run_js("window._themoImagePick(true);")
            self.toasts.add_toast(Adw.Toast(
                title="Cliquez une image dans l'aperçu pour la remplacer"))
        else:
            self._run_js("window._themoImagePick(false);")

    def _on_image_picked(self, _ucm, value):
        try:
            info = json.loads(value.to_string())
        except ValueError:
            return
        self._image_search_dialog(int(info.get("index", -1)),
                                  info.get("keywords", ""))

    def _replace_page_image(self, page, index, data, ctype, title):
        """Embarque l'image (data URI) à la place de la `index`-ième <img>."""
        if page not in self.project.pages:
            return
        self.project.pages[page] = openverse.replace_img(
            self.project.pages[page], index,
            openverse.data_uri(data, ctype), title or None)
        self._touch()
        if page == self._current_page_name():
            self._load_page_into_editor()
            self._loaded_page = None  # forcer un rechargement de l'aperçu
            self._schedule_refresh()

    def _image_search_dialog(self, index, keywords):
        if index < 0 or self._loaded_page not in self.project.pages:
            return
        page = self._loaded_page
        dialog = Adw.Dialog(title="Remplacer l'image",
                            content_width=760, content_height=560)

        entry = Gtk.SearchEntry(text=keywords,
                                placeholder_text="Mots-clés (anglais conseillé)")
        entry.set_hexpand(True)
        status = Gtk.Label()
        status.add_css_class("dim-label")
        flow = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE,
                           homogeneous=True, column_spacing=12,
                           row_spacing=12, margin_top=12, margin_bottom=12,
                           margin_start=12, margin_end=12,
                           valign=Gtk.Align.START,
                           min_children_per_line=2, max_children_per_line=3)
        results = []  # (octets, type MIME, titre), alignés sur les cartes

        def add_card(token, data, ctype, title):
            if token is not self._image_search_token:
                return False
            try:
                texture = Gdk.Texture.new_from_bytes(GLib.Bytes.new(data))
            except GLib.Error:
                return False
            pic = Gtk.Picture.new_for_paintable(texture)
            pic.set_content_fit(Gtk.ContentFit.COVER)
            pic.set_size_request(200, 140)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4,
                          margin_top=8, margin_bottom=8,
                          margin_start=8, margin_end=8)
            box.append(pic)
            label = Gtk.Label(label=title or "Sans titre")
            label.add_css_class("caption")
            label.set_ellipsize(Pango.EllipsizeMode.END)
            label.set_max_width_chars(24)
            box.append(label)
            child = Gtk.FlowBoxChild(child=box)
            child.add_css_class("card")
            child.add_css_class("activatable")
            results.append((data, ctype, title))
            flow.append(child)
            return False

        def search_done(token, found, error):
            if token is not self._image_search_token:
                return False
            if error:
                status.set_text("Recherche impossible — êtes-vous en ligne ?")
            elif not found:
                status.set_text("Aucun résultat CC0 pour ces mots-clés")
            else:
                status.set_text(f"{found} photos CC0 — cliquez pour remplacer")
            return False

        def do_search(*_args):
            terms = entry.get_text().strip()
            if not terms:
                status.set_text("Saisissez des mots-clés puis Entrée")
                return
            token = self._image_search_token = object()
            results.clear()
            flow.remove_all()
            status.set_text("Recherche…")

            def worker():
                try:
                    found = openverse.search(terms, count=9)
                except Exception:
                    GLib.idle_add(search_done, token, 0, True)
                    return
                shown = 0
                for n, r in enumerate(found):
                    if token is not self._image_search_token:
                        return  # nouvelle recherche lancée entre-temps
                    if n:
                        time.sleep(0.4)  # ménager la limite de débit
                    try:
                        data, ctype = openverse.fetch(r["thumbnail"])
                    except Exception:
                        continue
                    shown += 1
                    GLib.idle_add(add_card, token, data, ctype, r["title"])
                GLib.idle_add(search_done, token, shown, False)
            threading.Thread(target=worker, daemon=True).start()
        entry.connect("activate", do_search)

        def activated(_flow, child):
            data, ctype, title = results[child.get_index()]
            dialog.close()
            self._replace_page_image(page, index, data, ctype, title)
            self.toasts.add_toast(Adw.Toast(title="Image remplacée"))
        flow.connect("child-activated", activated)

        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6,
                      margin_top=8, margin_start=12, margin_end=12)
        top.append(entry)
        top.append(status)
        scroller = Gtk.ScrolledWindow(child=flow)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(top)
        content.append(scroller)
        view = Adw.ToolbarView()
        view.add_top_bar(Adw.HeaderBar())
        view.set_content(content)
        dialog.set_child(view)
        dialog.present(self)
        do_search()  # recherche immédiate avec les mots-clés de l'image

    def _on_decide_policy(self, _webview, decision, dtype):
        """Suivre les liens internes dans l'aperçu, sans fichiers réels.

        L'aperçu est chargé en mémoire (base file:///) : un lien
        « tarifs.html » ne correspond à aucun fichier. On intercepte la
        navigation : lien interne -> bascule sur la page du projet ;
        lien externe -> navigateur par défaut ; ancres (#…) inchangées.
        """
        if dtype != WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            return False
        uri = decision.get_navigation_action().get_request().get_uri()
        if uri.startswith(("http://", "https://", "mailto:")):
            decision.ignore()
            Gio.AppInfo.launch_default_for_uri(uri, None)
            return True
        if not (uri.startswith("file://") and uri.endswith(".html")):
            return False  # base file:///, ancres… : comportement normal
        decision.ignore()
        slug = uri.rsplit("/", 1)[-1][:-len(".html")]
        for name in self.project.pages:
            if slugify(name) == slug:
                self._show_page(name)
                break
        else:
            self.toasts.add_toast(Adw.Toast(
                title=f"Aucune page « {slug}.html » dans le projet"))
        return True

    def _on_load_changed(self, _webview, event):
        # réactiver les modes d'édition après chaque rechargement de l'aperçu
        if event != WebKit.LoadEvent.FINISHED:
            return
        if self.wysiwyg_toggle.get_active():
            self._set_design_mode(True)
        if self.delete_toggle.get_active():
            self._run_js("window._themoBlockDelete(true);")
        if self.image_toggle.get_active():
            self._run_js("window._themoImagePick(true);")

    def _on_wysiwyg_edit(self, _ucm, value):
        # cible : la page rendue dans l'aperçu (et non la sélection courante,
        # qui peut déjà avoir changé quand le message arrive)
        if self._loaded_page not in self.project.pages:
            return
        html = value.to_string()
        if not html.endswith("\n"):
            html += "\n"
        self.project.pages[self._loaded_page] = html
        # header et footer sont communs à tout le site
        propagate_chrome(self.project.pages, self._loaded_page)
        self._touch()

    def _on_editor_changed(self, buffer):
        if self._buffer_lock:
            return
        text = buffer.get_text(buffer.get_start_iter(),
                               buffer.get_end_iter(), True)
        name = self._current_page_name()
        self.project.pages[name] = text
        propagate_chrome(self.project.pages, name)
        self._touch()
        self._schedule_refresh()

    def _unique_page_name(self, wanted):
        name, n = wanted, 2
        while name in self.project.pages:
            name = f"{wanted} ({n})"
            n += 1
        return name

    def _page_add(self, *_args):
        entry = Gtk.Entry(placeholder_text="Nom de la page",
                          activates_default=True)
        models = Gtk.DropDown.new_from_strings(list(MODELS))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.append(entry)
        box.append(models)
        dialog = Adw.AlertDialog(heading="Ajouter une page",
                                 body="Nom et modèle de départ :")
        dialog.set_extra_child(box)
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("add", "Ajouter")
        dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("add")
        dialog.set_close_response("cancel")

        def done(d, result):
            if d.choose_finish(result) != "add":
                return
            name = self._unique_page_name(
                entry.get_text().strip() or "Nouvelle page")
            model = list(MODELS)[models.get_selected()]
            self.project.pages[name] = MODELS[model]
            self._sync_navigation_add(name)
            self._touch()
            self._show_page(name)
        dialog.choose(self, None, done)

    def _sync_navigation_add(self, name):
        """Nouvelle page : lien ajouté partout, nav complète sur la page."""
        for other in self.project.pages:
            if other != name:
                self.project.pages[other] = nav_add_link(
                    self.project.pages[other], name)
        self.project.pages[name] = nav_set_links(
            self.project.pages[name], list(self.project.pages), current=name)

    def _page_duplicate(self, *_args):
        current = self._current_page_name()
        name = self._unique_page_name(f"{current} (copie)")
        self.project.pages[name] = self.project.pages[current]
        self._sync_navigation_add(name)
        self._touch()
        self._show_page(name)

    def _page_rename(self, *_args):
        current = self._current_page_name()
        entry = Gtk.Entry(text=current, activates_default=True)
        dialog = Adw.AlertDialog(heading="Renommer la page")
        dialog.set_extra_child(entry)
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("rename", "Renommer")
        dialog.set_response_appearance("rename",
                                       Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("rename")
        dialog.set_close_response("cancel")

        def done(d, result):
            if d.choose_finish(result) != "rename":
                return
            new = entry.get_text().strip()
            if not new or new == current:
                return
            if new in self.project.pages:
                self.toasts.add_toast(Adw.Toast(
                    title=f"Une page « {new} » existe déjà"))
                return
            self.project.pages = {
                (new if k == current else k): nav_rename_link(v, current, new)
                for k, v in self.project.pages.items()}
            if self.project.home == current:
                self.project.home = new
            self._touch()
            self._show_page(new)
        dialog.choose(self, None, done)

    def _block_insert(self, _action, param):
        name = param.get_string()
        current = self._current_page_name()
        self.project.pages[current] = insert_block(
            self.project.pages[current], name)
        self._touch()
        self._load_page_into_editor()
        self._loaded_page = None  # forcer un rechargement complet de l'aperçu
        self._schedule_refresh()
        self.toasts.add_toast(Adw.Toast(title=f"Bloc « {name} » inséré"))

    def _page_delete(self, *_args):
        current = self._current_page_name()
        if len(self.project.pages) == 1:
            self.toasts.add_toast(Adw.Toast(
                title="Impossible de supprimer la dernière page"))
            return
        dialog = Adw.AlertDialog(
            heading=f"Supprimer « {current} » ?",
            body="La page sera retirée du projet au prochain enregistrement.")
        dialog.add_response("cancel", "Annuler")
        dialog.add_response("delete", "Supprimer")
        dialog.set_response_appearance("delete",
                                       Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_close_response("cancel")

        def done(d, result):
            if d.choose_finish(result) != "delete":
                return
            del self.project.pages[current]
            for other in self.project.pages:
                self.project.pages[other] = nav_remove_link(
                    self.project.pages[other], current)
            self._touch()
            self._show_page()
        dialog.choose(self, None, done)

    def _page_home(self, *_args):
        current = self._current_page_name()
        self.project.home = current
        self._touch()
        self.toasts.add_toast(Adw.Toast(
            title=f"« {current} » est la page d'accueil (index.html)"))

    # -- Publication ----------------------------------------------------------

    def _load_secret(self, key):
        """Lit un secret (trousseau, sinon fichier de repli 0600)."""
        if Secret:
            try:
                return Secret.password_lookup_sync(
                    _SECRET_SCHEMA, {"key": key}, None)
            except GLib.Error:
                return None
        kf = GLib.KeyFile()
        try:
            kf.load_from_file(str(SECRETS_FILE), GLib.KeyFileFlags.NONE)
            return kf.get_string("secrets", key)
        except GLib.Error:
            return None

    def _save_secret(self, key, value):
        if Secret:
            try:
                Secret.password_store_sync(
                    _SECRET_SCHEMA, {"key": key},
                    Secret.COLLECTION_DEFAULT, f"Thémo — {key}", value, None)
                return
            except GLib.Error:
                pass
        kf = GLib.KeyFile()
        try:
            kf.load_from_file(str(SECRETS_FILE), GLib.KeyFileFlags.NONE)
        except GLib.Error:
            pass
        kf.set_string("secrets", key, value)
        SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        kf.save_to_file(str(SECRETS_FILE))
        SECRETS_FILE.chmod(0o600)

    def _load_netlify_token(self):
        return self._load_secret("netlify")

    def _save_netlify_token(self, token):
        self._save_secret("netlify", token)

    def _procedure_row(self, title, heading, steps, url=None,
                       url_label="Ouvrir Netlify"):
        """Ligne d'aide : ouvre la procédure pas à pas, lien facultatif."""
        row = Adw.ActionRow(title=title, activatable=True)
        row.add_suffix(Gtk.Image.new_from_icon_name("help-about-symbolic"))

        def show(*_args):
            dialog = Adw.AlertDialog(heading=heading, body=steps)
            dialog.add_response("close", "Fermer")
            if url:
                dialog.add_response("open", url_label)
                dialog.set_response_appearance(
                    "open", Adw.ResponseAppearance.SUGGESTED)
            dialog.set_close_response("close")

            def done(d, result):
                if d.choose_finish(result) == "open":
                    Gio.AppInfo.launch_default_for_uri(url, None)
            dialog.choose(self, None, done)
        row.connect("activated", show)
        return row

    def _publish_dialog(self, *_args):
        settings = self.project.publish
        dialog = Adw.Dialog(title="Publier sur un serveur",
                            content_width=560, content_height=780)
        page = Adw.PreferencesPage()

        grp = Adw.PreferencesGroup(
            title="Destination",
            description=f"La page d'accueil du projet "
                        f"(« {self.project.home_page()} ») est publiée "
                        f"comme index.html")
        method = Adw.ComboRow(title="Publier vers")
        method.set_model(Gtk.StringList.new(
            ["Netlify", "Serveur SSH (rsync)", "FTP / FTPS"]))
        method.set_selected({"ssh": 1, "ftp": 2}.get(
            settings.get("method"), 0))
        grp.add(method)
        page.add(grp)

        netlify_grp = Adw.PreferencesGroup(
            title="Netlify",
            description="Un jeton d'accès personnel suffit, conservé "
                        "dans le trousseau ; le site est créé au premier "
                        "envoi")
        token_row = Adw.PasswordEntryRow(title="Jeton d'accès")
        token_row.set_text(self._load_netlify_token() or "")
        netlify_grp.add(token_row)
        netlify_grp.add(self._procedure_row(
            "Comment créer le jeton ?",
            "Créer le jeton d'accès",
            "1. Connectez-vous sur app.netlify.com.\n"
            "2. Avatar (en haut à droite) → User settings → Applications "
            "→ Personal access tokens → New access token.\n"
            "3. Nommez-le (« Thémo »), choisissez une expiration, "
            "puis Generate token.\n"
            "4. Copiez le jeton immédiatement — Netlify ne le réaffiche "
            "jamais — et collez-le dans le champ « Jeton d'accès ». "
            "Thémo le conserve ensuite dans le trousseau.",
            "https://app.netlify.com/user/applications"))
        netlify_grp.add(self._procedure_row(
            "Comment personnaliser le nom du site ?",
            "Nom de site personnalisé",
            "Le site est créé au premier envoi avec un nom aléatoire "
            "(quelque-chose.netlify.app).\n\n"
            "1. Ouvrez le tableau de bord Netlify et choisissez votre "
            "site.\n"
            "2. Site configuration → Change site name : « monsite » "
            "donne monsite.netlify.app.\n"
            "3. Pour un domaine à vous : Domain management → "
            "Add a domain.\n\n"
            "Le renommage ne casse rien : Thémo continuera de publier "
            "vers le même site.",
            "https://app.netlify.com/"))
        page.add(netlify_grp)

        ssh_grp = Adw.PreferencesGroup(
            title="Serveur SSH",
            description="Authentification par clé SSH uniquement ; "
                        "le dossier distant doit exister")
        dest_row = Adw.EntryRow(title="Destination (user@hôte:/chemin/)")
        dest_row.set_text(settings.get("ssh_dest", ""))
        ssh_grp.add(dest_row)
        url_row = Adw.EntryRow(
            title="Adresse publique du site (facultatif)")
        url_row.set_text(settings.get("url", "")
                         if settings.get("method") == "ssh" else "")
        ssh_grp.add(url_row)
        ssh_grp.add(self._procedure_row(
            "Quelles données indiquer ?",
            "Publier par SSH",
            "Destination — trois parties, sur le modèle "
            "michel@exemple.fr:/var/www/monsite/ :\n"
            "• user : votre nom d'utilisateur SSH sur le serveur ;\n"
            "• hôte : l'adresse du serveur (domaine ou IP) ;\n"
            "• /chemin/ : le dossier servi par le serveur web (souvent "
            "/var/www/… ou ~/public_html/), qui doit déjà exister.\n\n"
            "La connexion utilise vos clés SSH, jamais de mot de passe. "
            "Si la publication échoue (« Permission denied »), installez "
            "votre clé depuis un terminal :\n"
            "ssh-keygen (une seule fois), puis ssh-copy-id user@hôte.\n\n"
            "Adresse publique (facultatif) : l'URL où le site est visible "
            "(https://exemple.fr) — elle alimente le bouton « Ouvrir » "
            "après publication et l'écran d'accueil."))
        page.add(ssh_grp)

        is_ftp = settings.get("method") == "ftp"
        ftp_grp = Adw.PreferencesGroup(
            title="FTP / FTPS",
            description="Identifiants fournis par votre hébergeur ; "
                        "FTPS (connexion chiffrée) recommandé")
        host_row = Adw.EntryRow(title="Hôte (ftp.exemple.fr)")
        host_row.set_text(settings.get("ftp_host", ""))
        ftp_grp.add(host_row)
        user_row = Adw.EntryRow(title="Utilisateur")
        user_row.set_text(settings.get("ftp_user", ""))
        ftp_grp.add(user_row)
        pass_row = Adw.PasswordEntryRow(title="Mot de passe")
        if is_ftp and settings.get("ftp_host") and settings.get("ftp_user"):
            pass_row.set_text(self._load_secret(
                f"ftp:{settings['ftp_user']}@{settings['ftp_host']}") or "")
        ftp_grp.add(pass_row)
        ftp_path_row = Adw.EntryRow(
            title="Dossier distant (ex. sites/monsite, facultatif)")
        ftp_path_row.set_text(settings.get("ftp_path", ""))
        ftp_grp.add(ftp_path_row)
        secure_row = Adw.SwitchRow(title="Connexion sécurisée (FTPS)")
        secure_row.set_active(settings.get("ftp_secure", "1") != "0")
        ftp_grp.add(secure_row)
        ftp_url_row = Adw.EntryRow(
            title="Adresse publique du site (facultatif)")
        ftp_url_row.set_text(settings.get("url", "") if is_ftp else "")
        ftp_grp.add(ftp_url_row)
        ftp_grp.add(self._procedure_row(
            "Quelles données indiquer ?",
            "Publier par FTP",
            "Votre hébergeur (espace client, e-mail de bienvenue ou "
            "panneau cPanel/Plesk) vous a fourni :\n"
            "• hôte : l'adresse FTP, du type ftp.exemple.fr ;\n"
            "• utilisateur et mot de passe du compte FTP ;\n"
            "• dossier distant : le dossier servi par le site, souvent "
            "www, public_html ou htdocs. Beaucoup d'hébergeurs (comptes "
            "FTP par site, comme Infomaniak) vous déposent DÉJÀ dans la "
            "racine du site — dans ce cas, laissez ce champ VIDE. Indice : "
            "si, une fois connecté, vous voyez déjà un index.html, c'est "
            "que vous y êtes. Le chemin éventuel est relatif au dossier "
            "d'accueil (un « / » initial est sans effet) ; un dossier qui "
            "n'existe pas encore est créé automatiquement.\n\n"
            "Laissez « Connexion sécurisée (FTPS) » activé ; ne la "
            "désactivez que si votre hébergeur ne propose pas TLS. Le mot "
            "de passe est conservé dans le trousseau.\n\n"
            "Adresse publique (facultatif) : l'URL où le site est visible "
            "(https://exemple.fr) — elle alimente le bouton « Ouvrir » "
            "après publication et l'écran d'accueil."))
        page.add(ftp_grp)

        def update_visibility(*_a):
            selected = method.get_selected()
            netlify_grp.set_visible(selected == 0)
            ssh_grp.set_visible(selected == 1)
            ftp_grp.set_visible(selected == 2)
        method.connect("notify::selected", update_visibility)
        update_visibility()

        button = Gtk.Button(label="Publier")
        button.add_css_class("suggested-action")
        button.connect("clicked", lambda *_a: start())
        bar = Gtk.ActionBar()
        bar.pack_end(button)
        view = Adw.ToolbarView()
        view.add_top_bar(Adw.HeaderBar())
        view.set_content(page)
        view.add_bottom_bar(bar)
        dialog.set_child(view)

        def start():
            files = publish.site_files(self.project)
            selected = method.get_selected()
            if selected == 0:
                token = token_row.get_text().strip()
                if not token:
                    self.toasts.add_toast(Adw.Toast(
                        title="Renseignez le jeton Netlify"))
                    return
                self._save_netlify_token(token)
                settings["method"] = "netlify"
                self._touch()
                dialog.close()
                self._publish_netlify(token, files)
            elif selected == 1:
                dest = dest_row.get_text().strip()
                if not dest:
                    self.toasts.add_toast(Adw.Toast(
                        title="Renseignez la destination rsync"))
                    return
                settings["method"] = "ssh"
                settings["ssh_dest"] = dest
                settings["url"] = url_row.get_text().strip()
                self._touch()
                dialog.close()
                self._publish_ssh(dest, files, settings["url"] or None)
            else:
                host = host_row.get_text().strip()
                user = user_row.get_text().strip()
                password = pass_row.get_text()
                if not (host and user and password):
                    self.toasts.add_toast(Adw.Toast(
                        title="Renseignez hôte, utilisateur et mot de passe"))
                    return
                secure = secure_row.get_active()
                self._save_secret(f"ftp:{user}@{host}", password)
                settings["method"] = "ftp"
                settings["ftp_host"] = host
                settings["ftp_user"] = user
                settings["ftp_path"] = ftp_path_row.get_text().strip()
                settings["ftp_secure"] = "1" if secure else "0"
                settings["url"] = ftp_url_row.get_text().strip()
                self._touch()
                dialog.close()
                self._publish_ftp(host, user, password,
                                  settings["ftp_path"], secure, files,
                                  settings["url"] or None)
        dialog.present(self)

    def _publish_netlify(self, token, files):
        site_id = self.project.publish.get("netlify_site")
        self.toasts.add_toast(Adw.Toast(title="Publication vers Netlify…"))

        def remember(key, value):
            self.project.publish[key] = value
            self._touch()
            return False

        def worker():
            try:
                sid = site_id
                if not sid:
                    site = publish.netlify_create_site(token)
                    sid = site["id"]
                    GLib.idle_add(remember, "netlify_site", sid)
                deploy = publish.netlify_deploy(token, sid, files)
                url = deploy.get("ssl_url") or deploy.get("url")
                if url:
                    GLib.idle_add(remember, "url", url)
                GLib.idle_add(self._publish_done, None, url)
            except Exception as exc:
                message = str(exc)
                if "401" in message:
                    message = "jeton refusé — vérifiez-le sur Netlify"
                GLib.idle_add(self._publish_done, message, None)
        threading.Thread(target=worker, daemon=True).start()

    def _publish_ssh(self, dest, files, url=None):
        self.toasts.add_toast(Adw.Toast(title=f"Publication vers {dest}…"))

        def worker():
            ok, message = publish.rsync(dest, files)
            GLib.idle_add(self._publish_done,
                          None if ok else message, url if ok else None)
        threading.Thread(target=worker, daemon=True).start()

    def _publish_ftp(self, host, user, password, path, secure, files,
                     url=None):
        self.toasts.add_toast(Adw.Toast(title=f"Publication vers {host}…"))

        def worker():
            ok, message = publish.ftp_upload(
                host, user, password, path, files, secure)
            GLib.idle_add(self._publish_done,
                          None if ok else message, url if ok else None)
        threading.Thread(target=worker, daemon=True).start()

    def _publish_done(self, error, url):
        if error:
            self.toasts.add_toast(Adw.Toast(
                title=f"Échec de la publication : {error[:120]}"))
            return False
        toast = Adw.Toast(title="Site publié")
        if url:
            toast.set_button_label("Ouvrir")
            toast.connect("button-clicked", lambda *_a:
                          Gio.AppInfo.launch_default_for_uri(url, None))
            toast.set_timeout(10)
        self.toasts.add_toast(toast)
        if self._dirty:
            self.toasts.add_toast(Adw.Toast(
                title="Enregistrez le projet (Ctrl+S) pour conserver "
                      "la destination de publication"))
        return False

    # -- Réactions aux changements -------------------------------------------

    def _touch(self):
        if not self._loading:
            self._dirty = True
            self._update_title()

    def _on_color(self, btn, _pspec, attr):
        setattr(self.cfg, attr, _rgba_to_hex(btn.get_rgba()))
        self._touch()
        self._schedule_refresh()

    def _on_combo(self, row, _pspec, attr, options):
        setattr(self.cfg, attr, options[row.get_selected()])
        if attr == "element_template" and not self._loading:
            self._apply_preset(self.cfg.element_template)
        self._touch()
        self._schedule_refresh()

    def _on_spin(self, row, _pspec, attr):
        value = row.get_value()
        setattr(self.cfg, attr,
                round(value, 2) if row.get_digits() else int(value))
        self._touch()
        self._schedule_refresh()

    def _on_switch(self, row, _pspec, attr):
        setattr(self.cfg, attr, row.get_active())
        self._touch()
        self._schedule_refresh()

    def _apply_preset(self, style):
        """Aligne tous les tokens sur le préréglage du style graphique."""
        for attr, value in STYLE_PRESETS[style].items():
            setattr(self.cfg, attr, value)
            self._setters[attr](value)
        self._touch()
        self._schedule_refresh()
        self.toasts.add_toast(Adw.Toast(
            title=f"Tokens alignés sur le style « {style} »"))

    def _reset_tokens(self, *_args):
        self._apply_preset(self.cfg.element_template)

    def _schedule_refresh(self):
        if self._refresh_id:
            GLib.source_remove(self._refresh_id)
        self._refresh_id = GLib.timeout_add(120, self._refresh)

    def _refresh(self):
        self._refresh_id = 0
        css = generate_css(self.cfg)
        name = self._current_page_name()
        # Thème forcé dans l'aperçu pour rester indépendant du thème système
        theme = "dark" if self.dark_toggle.get_active() else "light"
        if self.wysiwyg_toggle.get_active() and self._loaded_page == name:
            # édition en cours : mettre à jour styles et thème par JS,
            # sans recharger, pour ne pas perdre la saisie
            self._run_js(
                f"document.querySelector('style').textContent = {json.dumps(css)};"
                f"document.documentElement.setAttribute('data-theme', {json.dumps(theme)});")
        else:
            body = self.project.pages.get(name, "")
            self.webview.load_html(wrap_preview(body, css, theme), "file:///")
            self._loaded_page = name
        return GLib.SOURCE_REMOVE

    # -- Projet ------------------------------------------------------------------

    def _update_title(self):
        star = "● " if self._dirty else ""
        self.win_title.set_subtitle(f"{star}{self.project.name}")
        self.set_title(f"Thémo — {self.project.name}")

    def _adopt_project(self, project):
        self.project = project
        self.cfg = project.cfg
        self._loading = True
        for attr, setter in self._setters.items():
            setter(getattr(self.cfg, attr))
        self._loading = False
        self._dirty = False
        self._current_page = None
        self._show_page()
        self._update_title()

    def _model_card(self, name):
        """Carte d'un modèle : vignette, nom, nombre de pages, description."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6,
                      margin_top=12, margin_bottom=12,
                      margin_start=12, margin_end=12)
        try:
            texture = Gdk.Texture.new_from_bytes(
                GLib.Bytes.new(_model_thumbnail_svg(name).encode()))
            box.append(Gtk.Picture.new_for_paintable(texture))
        except GLib.Error:
            pass  # pas de chargeur SVG : la carte reste textuelle
        title = Gtk.Label(label=name)
        title.add_css_class("heading")
        box.append(title)
        n = len(PROJECT_MODELS[name])
        count = Gtk.Label(label=f"{n} page{'s' if n > 1 else ''}")
        count.add_css_class("caption")
        count.add_css_class("dim-label")
        box.append(count)
        desc = Gtk.Label(label=MODEL_DESCRIPTIONS.get(name, ""))
        desc.add_css_class("caption")
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.set_max_width_chars(28)
        box.append(desc)
        child = Gtk.FlowBoxChild(child=box)
        child.add_css_class("card")
        child.add_css_class("activatable")
        return child

    def _recent_projects_list(self, dialog, header=True):
        """Liste des projets récents, avec ouverture de la version en ligne."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6,
                      margin_top=12, margin_bottom=12,
                      margin_start=12, margin_end=12)
        if header:
            title = Gtk.Label(label="Projets récents", xalign=0)
            title.add_css_class("heading")
            box.append(title)
        listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        listbox.add_css_class("boxed-list")
        home = GLib.get_home_dir()

        def open_recent(_row, path):
            try:
                project = Project.load(path)
            except (FileNotFoundError, GLib.Error, OSError) as exc:
                self.toasts.add_toast(Adw.Toast(title=str(exc)))
                return
            dialog.close()
            self._adopt_project(project)
            remember_recent(path)
            self.toasts.add_toast(Adw.Toast(
                title=f"Projet « {project.name} » ouvert"))

        for path in recent_projects():
            subtitle = path.replace(home, "~", 1)
            row = Adw.ActionRow(title=Path(path).name, subtitle=subtitle,
                                activatable=True)
            url = published_url(path)
            if url:
                online = Gtk.Button(icon_name="web-browser-symbolic",
                                    tooltip_text=f"Ouvrir la version "
                                                 f"en ligne — {url}")
                online.add_css_class("flat")
                online.set_valign(Gtk.Align.CENTER)
                online.connect("clicked", lambda _b, u=url:
                               Gio.AppInfo.launch_default_for_uri(u, None))
                row.add_suffix(online)
            row.connect("activated", open_recent, path)
            listbox.append(row)
        box.append(listbox)
        return box

    def _choose_model(self, heading, welcome=False):
        """Galerie des modèles de projet ; Échap conserve le projet courant."""
        names = list(PROJECT_MODELS)
        flow = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE,
                           homogeneous=True, column_spacing=12,
                           row_spacing=12, margin_top=12, margin_bottom=12,
                           margin_start=12, margin_end=12,
                           valign=Gtk.Align.START,
                           min_children_per_line=2, max_children_per_line=3)
        for name in names:
            flow.append(self._model_card(name))
        has_recents = welcome and recent_projects()
        dialog = Adw.Dialog(
            title=heading, content_width=780,
            content_height=860 if has_recents else 620)

        illustrate = Gtk.CheckButton(
            label="Illustrer avec des photos libres de droits (Openverse)")
        illustrate.set_active(True)
        illustrate.set_tooltip_text(
            "Remplace les images de remplissage par des photos CC0 "
            "téléchargées — décochez pour rester hors ligne")

        def activated(_flow, child):
            dialog.close()
            self._create_project_from_model(names[child.get_index()],
                                            illustrate.get_active())
        flow.connect("child-activated", activated)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(flow)
        if has_recents:
            content.append(self._recent_projects_list(dialog))
        scroller = Gtk.ScrolledWindow(child=content)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        bar = Gtk.ActionBar()
        bar.pack_start(illustrate)
        if welcome:
            open_btn = Gtk.Button(label="Ouvrir un projet…")
            open_btn.connect("clicked", lambda *_a: (
                dialog.close(), self._project_open()))
            bar.pack_end(open_btn)
        view = Adw.ToolbarView()
        view.add_top_bar(Adw.HeaderBar())
        view.set_content(scroller)
        view.add_bottom_bar(bar)
        dialog.set_child(view)
        dialog.present(self)

    def _create_project_from_model(self, name, illustrate=False):
        cfg = Config()
        style = MODEL_STYLES.get(name)
        if style:
            cfg.element_template = style
            for attr, value in STYLE_PRESETS[style].items():
                setattr(cfg, attr, value)
        self._adopt_project(Project(cfg=cfg, pages=PROJECT_MODELS[name]))
        self.toasts.add_toast(Adw.Toast(
            title=f"Nouveau projet — modèle « {name} »"))
        if illustrate:
            self._illustrate_project()

    def _illustrate_project(self):
        """Remplace en arrière-plan les placeholders par des photos CC0.

        Hors ligne ou en cas d'échec, les placeholders SVG restent : la
        création de projet n'est jamais bloquante.
        """
        tasks = []
        for page, body in self.project.pages.items():
            for _i, keywords in openverse.placeholder_slots(body):
                tasks.append((page, keywords))
        if not tasks:
            return
        token = self._illustrate_token = object()
        self.toasts.add_toast(Adw.Toast(
            title="Recherche d'illustrations libres (Openverse)…"))

        def apply(page, keywords, data, ctype, title):
            # cible le premier placeholder restant avec ces mots-clés :
            # robuste aux éditions survenues pendant le téléchargement
            if self._illustrate_token is not token:
                return False
            body = self.project.pages.get(page)
            if body is None:
                return False
            for i, kw in openverse.placeholder_slots(body):
                if kw == keywords:
                    self._replace_page_image(page, i, data, ctype, title)
                    break
            return False

        def worker():
            cache = {}
            for n, (page, keywords) in enumerate(tasks):
                if n:
                    time.sleep(1.5)  # limite de débit anonyme d'Openverse
                try:
                    if keywords not in cache:
                        cache[keywords] = openverse.search(keywords, count=8)
                except Exception:
                    continue  # réseau indisponible : placeholder conservé
                # certaines vignettes sont mortes (HTTP 424) : on essaie
                # les résultats suivants jusqu'à en obtenir une
                while cache[keywords]:
                    result = cache[keywords].pop(0)
                    try:
                        data, ctype = openverse.fetch(result["thumbnail"])
                    except Exception:
                        continue
                    GLib.idle_add(apply, page, keywords, data, ctype,
                                  result["title"])
                    break
        threading.Thread(target=worker, daemon=True).start()

    def show_welcome(self):
        self._choose_model("Bienvenue dans Thémo — choisissez un modèle",
                           welcome=True)

    def _project_new(self, *_args):
        self._choose_model("Nouveau projet")

    def _project_open(self, *_args):
        dialog = Gtk.FileDialog(title="Ouvrir un dossier de projet Thémo")
        dialog.select_folder(self, None, self._project_open_done)

    def _project_recent(self, *_args):
        if not recent_projects():
            self.toasts.add_toast(Adw.Toast(title="Aucun projet récent"))
            return
        dialog = Adw.Dialog(title="Projets récents",
                            content_width=560, content_height=480)
        scroller = Gtk.ScrolledWindow(
            child=self._recent_projects_list(dialog, header=False))
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        view = Adw.ToolbarView()
        view.add_top_bar(Adw.HeaderBar())
        view.set_content(scroller)
        dialog.set_child(view)
        dialog.present(self)

    def _project_open_done(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result).get_path()
        except GLib.Error:
            return
        try:
            project = Project.load(folder)
        except (FileNotFoundError, GLib.Error, OSError) as exc:
            self.toasts.add_toast(Adw.Toast(title=str(exc)))
            return
        self._adopt_project(project)
        remember_recent(folder)
        self.toasts.add_toast(Adw.Toast(
            title=f"Projet « {project.name} » ouvert"))

    def _project_save(self, *_args):
        if self.project.path is None:
            self._project_save_as()
            return
        self._do_save()

    def _project_save_as(self, *_args):
        dialog = Gtk.FileDialog(title="Choisir le dossier du projet")
        dialog.select_folder(self, None, self._project_save_as_done)

    def _project_save_as_done(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result).get_path()
        except GLib.Error:
            self._close_after_save = False  # choix de dossier annulé
            return
        self._do_save(folder)

    def _do_save(self, path=None):
        try:
            self.project.save(path)
        except OSError as exc:
            self._close_after_save = False
            self.toasts.add_toast(Adw.Toast(
                title=f"Échec de l'enregistrement : {exc}"))
            return
        self._dirty = False
        self._update_title()
        remember_recent(self.project.path)
        self.toasts.add_toast(Adw.Toast(
            title=f"Projet enregistré dans {self.project.path.name}/"))
        if self._close_after_save:
            self.close()

    # -- Export ----------------------------------------------------------------

    def _install_actions(self):
        for name, cb in (("export-css", self._export_css),
                         ("export-all", self._export_all),
                         ("project-new", self._project_new),
                         ("project-open", self._project_open),
                         ("project-recent", self._project_recent),
                         ("project-save", self._project_save),
                         ("project-save-as", self._project_save_as),
                         ("page-add", self._page_add),
                         ("page-duplicate", self._page_duplicate),
                         ("page-rename", self._page_rename),
                         ("page-delete", self._page_delete),
                         ("page-home", self._page_home),
                         ("publish", self._publish_dialog)):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", cb)
            self.add_action(action)
        action = Gio.SimpleAction.new("block-insert",
                                      GLib.VariantType.new("s"))
        action.connect("activate", self._block_insert)
        self.add_action(action)
        # action à état : la page courante est cochée dans le menu
        self._page_show_action = Gio.SimpleAction.new_stateful(
            "page-show", GLib.VariantType.new("s"),
            GLib.Variant.new_string(""))
        self._page_show_action.connect("activate", self._page_show)
        self.add_action(self._page_show_action)

    def _export_css(self, *_args):
        dialog = Gtk.FileDialog(initial_name="design-system.css")
        dialog.save(self, None, self._export_css_done)

    def _export_css_done(self, dialog, result):
        try:
            gfile = dialog.save_finish(result)
        except GLib.Error:
            return
        Path(gfile.get_path()).write_text(generate_css(self.cfg),
                                          encoding="utf-8")
        self.toasts.add_toast(Adw.Toast(
            title=f"CSS exporté : {gfile.get_basename()}"))

    def _export_all(self, *_args):
        dialog = Gtk.FileDialog()
        dialog.select_folder(self, None, self._export_all_done)

    def _export_all_done(self, dialog, result):
        try:
            folder = Path(dialog.select_folder_finish(result).get_path())
        except GLib.Error:
            return
        for name, content in publish.site_files(self.project).items():
            (folder / name).write_text(content, encoding="utf-8")
        self.toasts.add_toast(Adw.Toast(
            title=f"CSS, {len(self.project.pages)} pages et index.html "
                  f"exportés dans {folder.name}/"))


class ThemoApp(Adw.Application):

    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.set_accels_for_action("win.project-save", ["<Control>s"])
        self.set_accels_for_action("win.project-open", ["<Control>o"])
        self.set_accels_for_action("win.page-add", ["<Control>n"])

    def do_activate(self):
        win = self.get_active_window()
        if win is None:
            win = ThemoWindow(application=self)
            win.present()
            win.show_welcome()
        else:
            win.present()


if __name__ == "__main__":
    raise SystemExit(ThemoApp().run(sys.argv))
