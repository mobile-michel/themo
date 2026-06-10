"""Calcul des design tokens dérivés à partir de quelques tokens de base.

Tout le travail de dérivation se fait ici : gammes de couleurs (espace OKLCH),
échelle typographique modulaire, échelles d'espacement, de rayons et d'ombres.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Configuration : les seuls tokens saisis par l'utilisateur
# ---------------------------------------------------------------------------

FONT_STACKS = {
    "Système (sans-serif)": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    "Inter": "'Inter', system-ui, sans-serif",
    "Roboto": "'Roboto', system-ui, sans-serif",
    "Open Sans": "'Open Sans', system-ui, sans-serif",
    "Système (serif)": "Georgia, 'Times New Roman', serif",
    "Georgia": "Georgia, serif",
    "Playfair Display": "'Playfair Display', Georgia, serif",
}

FONT_MONO = "ui-monospace, 'JetBrains Mono', 'Fira Code', Consolas, monospace"

# (libellé affiché, valeur)
RATIOS = [
    ("1.125 — Seconde majeure", 1.125),
    ("1.2 — Tierce mineure", 1.2),
    ("1.25 — Tierce majeure", 1.25),
    ("1.333 — Quarte juste", 1.333),
    ("1.414 — Quinte diminuée", 1.414),
    ("1.5 — Quinte juste", 1.5),
    ("1.618 — Nombre d'or", 1.618),
]

SPACING_BASES = [4, 8]


@dataclass
class Config:
    primary: str = "#3b82f6"
    secondary: str = "#f59e0b"
    font_heading: str = "Système (sans-serif)"
    font_body: str = "Système (sans-serif)"
    base_size: int = 16          # px — taille du texte courant
    ratio: float = 1.25          # ratio de l'échelle typographique
    spacing_base: int = 4        # px — unité d'espacement
    radius: int = 8              # px — rayon de bordure de référence
    shadow_alpha: int = 12       # % — opacité des ombres
    semantic_template: str = "Neutre"
    element_template: str = "Moderne"
    include_dark: bool = True


# ---------------------------------------------------------------------------
# Conversions sRGB <-> OKLCH
# ---------------------------------------------------------------------------

import math


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, round(c * 255))) for c in (r, g, b)
    )


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _rgb_to_oklab(r, g, b):
    r, g, b = (_srgb_to_linear(c) for c in (r, g, b))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _oklab_to_linear(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def hex_to_oklch(h):
    L, a, b = _rgb_to_oklab(*hex_to_rgb(h))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def oklch_to_hex(L, C, H):
    """Convertit en sRGB en réduisant la chroma jusqu'à rester dans le gamut."""
    rad = math.radians(H)
    for _ in range(32):
        lin = _oklab_to_linear(L, C * math.cos(rad), C * math.sin(rad))
        if all(-0.0001 <= c <= 1.0001 for c in lin):
            break
        C *= 0.92
    return rgb_to_hex(*(_linear_to_srgb(c) for c in lin))


# ---------------------------------------------------------------------------
# Gammes de couleurs 50 -> 900
# ---------------------------------------------------------------------------

# Clarté OKLab visée pour chaque palier, et facteur de chroma (cloche centrée
# sur les tons moyens, atténuée aux extrêmes pour éviter les couleurs criardes)
_STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
_L_LADDER = [0.974, 0.940, 0.882, 0.812, 0.733, 0.648, 0.568, 0.494, 0.418, 0.342]
_C_CURVE = [0.22, 0.38, 0.60, 0.80, 0.94, 1.00, 1.00, 0.93, 0.82, 0.68]


def color_scale(base_hex, neutral=False, anchor=True):
    """Génère une gamme 50→900 depuis une couleur de base.

    La teinte et la chroma viennent de la couleur saisie ; si `anchor` est
    vrai, le palier dont la clarté est la plus proche reçoit la couleur exacte.
    """
    _, C, H = hex_to_oklch(base_hex)
    if neutral:
        C = min(C * 0.14, 0.014)
    scale = {}
    for step, L, cf in zip(_STEPS, _L_LADDER, _C_CURVE):
        scale[step] = oklch_to_hex(L, C * (1.0 if neutral else cf), H)
    if anchor and not neutral:
        base_L = hex_to_oklch(base_hex)[0]
        closest = min(_STEPS, key=lambda s: abs(_L_LADDER[_STEPS.index(s)] - base_L))
        scale[closest] = base_hex.lower()
    return scale


# ---------------------------------------------------------------------------
# Échelles dérivées
# ---------------------------------------------------------------------------

def _fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s or "0"


def type_scale(base_px, ratio):
    """Échelle modulaire en rem (1rem = 16px), le corps de texte étant base_px."""
    base = base_px / 16
    names = [("xs", -2), ("sm", -1), ("base", 0), ("lg", 1),
             ("xl", 2), ("2xl", 3), ("3xl", 4), ("4xl", 5)]
    return {n: f"{_fmt(base * ratio ** e)}rem" for n, e in names}


def spacing_scale(unit_px):
    multiples = [1, 2, 3, 4, 6, 8, 12, 16, 24]
    return {m: f"{_fmt(m * unit_px / 16)}rem" for m in multiples}


def radius_scale(base_px):
    return {
        "sm": f"{_fmt(base_px / 2)}px",
        "md": f"{base_px}px",
        "lg": f"{base_px * 2}px",
        "xl": f"{base_px * 3}px",
        "full": "9999px",
    }


def shadow_scale(alpha_pct):
    a1 = alpha_pct / 100
    a2 = a1 * 0.7
    return {
        1: f"0 1px 2px rgb(0 0 0 / {_fmt(a1)})",
        2: f"0 1px 3px rgb(0 0 0 / {_fmt(a1)}), 0 2px 8px rgb(0 0 0 / {_fmt(a2)})",
        3: f"0 2px 6px rgb(0 0 0 / {_fmt(a1)}), 0 6px 18px rgb(0 0 0 / {_fmt(a2)})",
        4: f"0 4px 10px rgb(0 0 0 / {_fmt(a1)}), 0 12px 32px rgb(0 0 0 / {_fmt(a2)})",
        5: f"0 8px 16px rgb(0 0 0 / {_fmt(a1)}), 0 24px 56px rgb(0 0 0 / {_fmt(a2)})",
    }
