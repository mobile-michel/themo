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
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, GtkSource, WebKit  # noqa: E402

from tokens import (Config, HEADING_FONTS, BODY_FONTS, CODE_FONTS,  # noqa: E402
                    RATIOS, CONTAINERS, DENSITIES, STYLE_PRESETS)
from css_gen import generate_css, SEMANTIC_TEMPLATES, ELEMENT_TEMPLATES  # noqa: E402
from pages import (MODELS, PROJECT_MODELS, MODEL_DESCRIPTIONS,  # noqa: E402
                   BLOCKS, insert_block, propagate_chrome,
                   nav_add_link, nav_remove_link, nav_rename_link,
                   nav_set_links, wrap_preview, wrap_export)
from project import Project, slugify  # noqa: E402

APP_ID = "li.maillard.Themo"

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
        self.project = Project()
        self.cfg = self.project.cfg
        self._refresh_id = 0
        self._setters = {}   # attr -> fn(valeur) pour réaligner les widgets
        self._loading = False    # vrai pendant la synchronisation des widgets
        self._buffer_lock = False  # vrai pendant le chargement de l'éditeur
        self._dirty = False
        self._loaded_page = None  # page actuellement rendue dans l'aperçu
        self._current_page = None  # page affichée et éditée

        self.set_default_size(1280, 900)

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

        project_menu = Gio.Menu()
        sect = Gio.Menu()
        sect.append("Nouveau projet", "win.project-new")
        sect.append("Ouvrir un projet…", "win.project-open")
        sect.append("Enregistrer", "win.project-save")
        sect.append("Enregistrer sous…", "win.project-save-as")
        project_menu.append_section("Projet", sect)
        sect = Gio.Menu()
        sect.append("Exporter le CSS…", "win.export-css")
        sect.append("Exporter CSS + pages HTML…", "win.export-all")
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

    def _choose_model(self, heading):
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
        dialog = Adw.Dialog(title=heading,
                            content_width=780, content_height=620)

        def activated(_flow, child):
            dialog.close()
            self._create_project_from_model(names[child.get_index()])
        flow.connect("child-activated", activated)

        scroller = Gtk.ScrolledWindow(child=flow)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        view = Adw.ToolbarView()
        view.add_top_bar(Adw.HeaderBar())
        view.set_content(scroller)
        dialog.set_child(view)
        dialog.present(self)

    def _create_project_from_model(self, name):
        cfg = Config()
        style = MODEL_STYLES.get(name)
        if style:
            cfg.element_template = style
            for attr, value in STYLE_PRESETS[style].items():
                setattr(cfg, attr, value)
        self._adopt_project(Project(cfg=cfg, pages=PROJECT_MODELS[name]))
        self.toasts.add_toast(Adw.Toast(
            title=f"Nouveau projet — modèle « {name} »"))

    def show_welcome(self):
        self._choose_model("Bienvenue dans Thémo — choisissez un modèle")

    def _project_new(self, *_args):
        self._choose_model("Nouveau projet")

    def _project_open(self, *_args):
        dialog = Gtk.FileDialog(title="Ouvrir un dossier de projet Thémo")
        dialog.select_folder(self, None, self._project_open_done)

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
            return
        self._do_save(folder)

    def _do_save(self, path=None):
        try:
            self.project.save(path)
        except OSError as exc:
            self.toasts.add_toast(Adw.Toast(
                title=f"Échec de l'enregistrement : {exc}"))
            return
        self._dirty = False
        self._update_title()
        self.toasts.add_toast(Adw.Toast(
            title=f"Projet enregistré dans {self.project.path.name}/"))

    # -- Export ----------------------------------------------------------------

    def _install_actions(self):
        for name, cb in (("export-css", self._export_css),
                         ("export-all", self._export_all),
                         ("project-new", self._project_new),
                         ("project-open", self._project_open),
                         ("project-save", self._project_save),
                         ("project-save-as", self._project_save_as),
                         ("page-add", self._page_add),
                         ("page-duplicate", self._page_duplicate),
                         ("page-rename", self._page_rename),
                         ("page-delete", self._page_delete)):
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
        (folder / "design-system.css").write_text(
            generate_css(self.cfg), encoding="utf-8")
        for name, body in self.project.pages.items():
            (folder / f"{slugify(name)}.html").write_text(
                wrap_export(body, name), encoding="utf-8")
        self.toasts.add_toast(Adw.Toast(
            title=f"CSS et {len(self.project.pages)} pages HTML exportés "
                  f"dans {folder.name}/"))


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
