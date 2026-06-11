#!/usr/bin/env python3
"""Thémo — générateur de design système CSS pour Linux (GTK4 / libadwaita).

Quelques tokens de base saisis dans la barre latérale, tout le reste est
dérivé automatiquement ; aperçu en direct via WebKitGTK ; export d'un
fichier design-system.css (et de pages HTML de démonstration), sans la
moindre classe CSS.
"""

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
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, WebKit  # noqa: E402

from tokens import (Config, HEADING_FONTS, BODY_FONTS, CODE_FONTS,  # noqa: E402
                    RATIOS, CONTAINERS, DENSITIES, STYLE_PRESETS)
from css_gen import generate_css, SEMANTIC_TEMPLATES, ELEMENT_TEMPLATES  # noqa: E402
from pages import PAGES, wrap_preview, wrap_export  # noqa: E402

APP_ID = "li.maillard.Themo"


def _rgba_to_hex(rgba: Gdk.RGBA) -> str:
    return "#%02x%02x%02x" % (
        round(rgba.red * 255), round(rgba.green * 255), round(rgba.blue * 255)
    )


class ThemoWindow(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = Config()
        self._refresh_id = 0
        self._setters = {}  # attr -> fn(valeur) pour réaligner les widgets

        self.set_title("Thémo")
        self.set_default_size(1280, 860)

        split = Adw.OverlaySplitView()
        split.set_min_sidebar_width(330)
        split.set_max_sidebar_width(380)
        split.set_sidebar(self._build_sidebar())
        split.set_content(self._build_content())

        self.toasts = Adw.ToastOverlay()
        self.toasts.set_child(split)
        self.set_content(self.toasts)

        self._install_actions()
        self._refresh()

    # -- Barre latérale : les tokens de base --------------------------------

    def _build_sidebar(self):
        page = Adw.PreferencesPage()

        grp = Adw.PreferencesGroup(
            title="Style graphique",
            description="Prérègle tous les tokens selon son caractère",
        )
        row = self._combo_row("Style", list(ELEMENT_TEMPLATES),
                              "element_template", tracked=False)
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
        header.set_title_widget(Adw.WindowTitle(
            title="Thémo", subtitle="Design système → CSS"))
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

    def _combo_row(self, title, labels, attr, values=None, default_index=0,
                   tracked=True):
        row = Adw.ComboRow(title=title)
        row.set_model(Gtk.StringList.new(labels))
        current = getattr(self.cfg, attr)
        options = values if values is not None else labels
        index = options.index(current) if current in options else default_index
        row.set_selected(index)
        row.connect("notify::selected", self._on_combo, attr, options)
        if tracked:
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

    # -- Zone d'aperçu -------------------------------------------------------

    def _build_content(self):
        self.webview = WebKit.WebView()

        self.page_selector = Gtk.DropDown.new_from_strings(list(PAGES))
        self.page_selector.connect("notify::selected",
                                   lambda *a: self._schedule_refresh())

        self.dark_toggle = Gtk.ToggleButton(
            icon_name="weather-clear-night-symbolic",
            tooltip_text="Prévisualiser le thème sombre")
        self.dark_toggle.connect("toggled", lambda *a: self._schedule_refresh())

        menu = Gio.Menu()
        menu.append("Exporter le CSS…", "win.export-css")
        menu.append("Exporter CSS + pages HTML…", "win.export-all")
        export = Gtk.MenuButton(label="Exporter", menu_model=menu)
        export.add_css_class("suggested-action")

        header = Adw.HeaderBar()
        header.set_title_widget(self.page_selector)
        header.pack_start(self.dark_toggle)
        header.pack_end(export)

        view = Adw.ToolbarView()
        view.add_top_bar(header)
        view.set_content(self.webview)
        return view

    # -- Réactions aux changements -------------------------------------------

    def _on_color(self, btn, _pspec, attr):
        setattr(self.cfg, attr, _rgba_to_hex(btn.get_rgba()))
        self._schedule_refresh()

    def _on_combo(self, row, _pspec, attr, options):
        setattr(self.cfg, attr, options[row.get_selected()])
        if attr == "element_template":
            self._apply_preset(self.cfg.element_template)
        self._schedule_refresh()

    def _on_spin(self, row, _pspec, attr):
        value = row.get_value()
        setattr(self.cfg, attr,
                round(value, 2) if row.get_digits() else int(value))
        self._schedule_refresh()

    def _apply_preset(self, style):
        """Aligne tous les tokens sur le préréglage du style graphique."""
        for attr, value in STYLE_PRESETS[style].items():
            setattr(self.cfg, attr, value)
            self._setters[attr](value)
        self._schedule_refresh()
        self.toasts.add_toast(Adw.Toast(
            title=f"Tokens alignés sur le style « {style} »"))

    def _reset_tokens(self, *_args):
        self._apply_preset(self.cfg.element_template)

    def _on_switch(self, row, _pspec, attr):
        setattr(self.cfg, attr, row.get_active())
        self._schedule_refresh()

    def _schedule_refresh(self):
        if self._refresh_id:
            GLib.source_remove(self._refresh_id)
        self._refresh_id = GLib.timeout_add(120, self._refresh)

    def _refresh(self):
        self._refresh_id = 0
        css = generate_css(self.cfg)
        page_name = list(PAGES)[self.page_selector.get_selected()] \
            if hasattr(self, "page_selector") else next(iter(PAGES))
        # Thème forcé dans l'aperçu pour rester indépendant du thème système
        theme = "dark" if (hasattr(self, "dark_toggle")
                           and self.dark_toggle.get_active()) else "light"
        self.webview.load_html(wrap_preview(PAGES[page_name], css, theme),
                               "file:///")
        return GLib.SOURCE_REMOVE

    # -- Export ----------------------------------------------------------------

    def _install_actions(self):
        for name, cb in (("export-css", self._export_css),
                         ("export-all", self._export_all)):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", cb)
            self.add_action(action)

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
        for name, body in PAGES.items():
            slug = (name.lower()
                    .replace("é", "e").replace("è", "e").replace(" ", "-"))
            (folder / f"{slug}.html").write_text(
                wrap_export(body, name), encoding="utf-8")
        self.toasts.add_toast(Adw.Toast(
            title=f"CSS et {len(PAGES)} pages HTML exportés dans "
                  f"{folder.name}/"))


class ThemoApp(Adw.Application):

    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        win = self.get_active_window() or ThemoWindow(application=self)
        win.present()


if __name__ == "__main__":
    raise SystemExit(ThemoApp().run(sys.argv))
