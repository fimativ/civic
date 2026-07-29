from __future__ import annotations

import random
import re
import ast
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · Inicio",
    initial_sidebar_state="collapsed",
)

UBU_RED    = "#9b2743"
UBU_YELLOW = "#F5C400"
UBU_DARK   = "#1a1a1a"
BLUE_LINE  = "#2b6cb0"
GREEN_LINE = "#2e7d32"

LIGHT_VARS = """
    --app-bg: #fbfbfb;
    --app-fg: #141414;
    --panel-bg: #fffdef;
    --box-bg: #ffffff;
    --box-fg: #1a1a1a;
    --metric-border: #d0d0d0;
    --muted-fg: #666666;
    --lorem-bg: #efeef2;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
"""

DARK_VARS = """
    --app-bg: #0d0d0f;
    --app-fg: #f2f2f2;
    --panel-bg: #17160f;
    --box-bg: #1e1e24;
    --box-fg: #f2f2f2;
    --metric-border: #4a4a52;
    --muted-fg: #adadad;
    --lorem-bg: #16161b;
    --shadow: 0 1px 3px rgba(0,0,0,0.45);
"""

PAGES_DIR = Path(__file__).parent / "pages"
NUMERIC_PAGE_RE = re.compile(
    r"^(?P<chapter>\d+)_(?P<exercise>\d+)_(?P<variant>vs|vf)\.py$",
    re.IGNORECASE,
)
EXTRA_PAGE_RE = re.compile(r"^(?P<chapter>\d+)_(?P<name>[A-Za-z][A-Za-z0-9]*)\.py$")


@dataclass(frozen=True)
class Page:
    path: Path
    chapter: int
    exercise: int | None = None
    name: str | None = None
    title: str = ""

    @property
    def route(self) -> str:
        return f"pages/{self.path.name}"

    @property
    def label(self) -> str:
        return self.title or self.path.stem


def page_title(path: Path) -> str:
    """Read the introductory title configured by the Streamlit page."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return path.stem

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "set_page_config":
            continue
        for keyword in node.keywords:
            if keyword.arg == "page_title" and isinstance(keyword.value, ast.Constant):
                title = keyword.value.value
                if isinstance(title, str):
                    return re.sub(r"^C1VIC D4TA\s*[,·-]\s*", "", title).strip()
    return path.stem


def discover_pages() -> tuple[list[Page], list[Page]]:
    """Find pages dynamically; when both variants exist, use the VS page."""
    numeric: dict[tuple[int, int], Page] = {}
    extras: list[Page] = []

    for path in PAGES_DIR.glob("*.py"):
        numeric_match = NUMERIC_PAGE_RE.match(path.name)
        if numeric_match:
            chapter = int(numeric_match.group("chapter"))
            exercise = int(numeric_match.group("exercise"))
            candidate = Page(path, chapter, exercise=exercise, title=page_title(path))
            key = (chapter, exercise)
            current = numeric.get(key)
            if current is None or path.stem.lower().endswith("_vs"):
                numeric[key] = candidate
            continue

        extra_match = EXTRA_PAGE_RE.match(path.name)
        if extra_match:
            extras.append(
                Page(
                    path,
                    int(extra_match.group("chapter")),
                    name=extra_match.group("name"),
                    title=page_title(path),
                )
            )

    numeric_pages = sorted(
        numeric.values(), key=lambda page: (page.chapter, page.exercise or 0, page.path.name)
    )
    extras.sort(key=lambda page: (page.chapter, page.path.name))
    return numeric_pages, extras


def detect_dark_theme():
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return None


def build_css():
    dark = detect_dark_theme()
    if dark is True:
        theme_block = f":root {{ {DARK_VARS} }}"
    elif dark is False:
        theme_block = f":root {{ {LIGHT_VARS} }}"
    else:
        theme_block = (
            f":root {{ {LIGHT_VARS} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root {{ {DARK_VARS} }} }}"
        )

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600&display=swap');

{theme_block}

.stApp, html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--app-bg) !important;
    color: var(--app-fg) !important;
    font-family: 'Open Sans', Arial, sans-serif;
}}
[data-testid="stSidebar"] {{ display: none; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{
    padding: clamp(0.6rem, 2vw, 1.5rem) clamp(0.6rem, 3vw, 3rem) !important;
    max-width: 1500px !important;
}}

/* ---- Cabecera ---- */
.home-hero {{
    background: var(--box-bg); border-radius: 16px; box-shadow: var(--shadow);
    padding: clamp(18px, 3vw, 40px); text-align: center; margin-bottom: 18px;
}}
.home-hero .brand {{
    font-size: clamp(22px, 4vw, 42px); font-weight: 700; color: {UBU_RED}; line-height: 1.05;
}}
.home-hero .tagline {{
    font-size: clamp(14px, 2vw, 22px); color: var(--muted-fg); margin-top: 8px; font-style: italic;
}}
.section-title {{
    font-size: clamp(17px, 2.2vw, 26px); font-weight: 700; color: var(--app-fg);
    margin: 18px 0 14px 0; border-bottom: 3px solid {UBU_YELLOW}; padding-bottom: 8px;
}}
.vertical-section-title {{
    writing-mode: vertical-rl; transform: rotate(180deg); height: 100%;
    min-height: 300px; display: flex; align-items: center; justify-content: center;
    font-size: clamp(16px, 2vw, 24px); font-weight: 700; color: var(--app-fg);
    border-left: 3px solid {UBU_YELLOW}; padding-left: 8px;
}}

/* ---- Cuadrícula 6x6 (se mantiene en fila también en móvil) ---- */
.st-key-grid, .st-key-extra-page {{ max-width: 90%; margin-left: auto; }}
.st-key-grid [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: clamp(3px, 0.8vw, 8px) !important; }}
.st-key-grid div[data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0 !important; }}
.st-key-grid [data-testid="stVerticalBlock"] {{ gap: clamp(3px, 0.8vw, 8px) !important; }}
.st-key-grid button {{
    aspect-ratio: 1 / 1; height: auto; min-height: 0; width: 100%;
    border-radius: 10px !important; box-shadow: var(--shadow);
    white-space: normal !important; line-height: 1.1 !important;
    padding: 3px 3px !important; border: 2px solid var(--metric-border) !important;
    background: var(--box-bg) !important; color: var(--box-fg) !important;
}}
.st-key-grid button p {{ font-size: clamp(8.5px, 1.35vw, 15px) !important; font-weight: 700 !important; margin: 0 !important; }}
.st-key-grid button p:first-child {{ font-size: clamp(8px, 1.1vw, 12px) !important; opacity: 0.55; font-weight: 600 !important; }}
.st-key-grid button:disabled {{ opacity: 0.45 !important; background: var(--lorem-bg) !important; }}

/* ---- Páginas adicionales ---- */
.st-key-extra-page button {{
    min-height: 56px; border-radius: 10px !important; box-shadow: var(--shadow);
    background: var(--box-bg) !important; color: var(--box-fg) !important;
    border: 2px solid var(--metric-border) !important; font-weight: 700;
}}
.st-key-extra-page button p {{
    font-size: clamp(10px, 1.1vw, 14px) !important;
    line-height: 1.1 !important; margin: 0 !important;
}}

/* ---- Dados ---- */
.st-key-die_1 button, .st-key-die_2 button {{
    aspect-ratio: 1 / 1; height: auto; min-height: 125px; border-radius: 12px !important;
    background: var(--box-bg) !important; color: var(--box-fg) !important;
    border: 3px solid var(--metric-border) !important; font-size: clamp(90px, 13vw, 150px) !important;
    line-height: 1 !important; padding: 0 !important;
}}
.st-key-die_1 button:active, .st-key-die_2 button:active {{
    animation: dice-shake 0.45s ease-in-out;
}}
@keyframes dice-shake {{
    0%, 100% {{ transform: rotate(0deg) scale(1); }}
    25% {{ transform: rotate(-12deg) scale(1.08); }}
    50% {{ transform: rotate(12deg) scale(1.12); }}
    75% {{ transform: rotate(-8deg) scale(1.06); }}
}}
button p {{ font-size: clamp(14px, 1.7vw, 21px) !important; }}
div[data-testid="stColumn"] button {{ padding-top: 12px !important; padding-bottom: 12px !important; }}

.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 18px; text-align: center;
    font-size: clamp(13px, 1.6vw, 20px); color: var(--muted-fg); margin-top: 26px;
}}
</style>
"""

# =============================================================================
# 2. DADOS EN SVG
# =============================================================================

PIP_LAYOUT = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (2, 0), (0, 2), (2, 2)],
    5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
    6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],
}

DIE_FACES = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

def die_svg(value, dark, highlight=False):
    if highlight:
        face, pip, edge = UBU_YELLOW, "#1a1a1a", UBU_RED
    elif dark:
        face, pip, edge = "#2a2a30", "#f0f0f0", "#4a4a52"
    else:
        face, pip, edge = "#ffffff", "#1a1a1a", "#d0d0d0"
    dots = ""
    for gx, gy in PIP_LAYOUT[value]:
        cx = 22 + gx * 28
        cy = 22 + gy * 28
        dots += f'<circle cx="{cx}" cy="{cy}" r="8" fill="{pip}"/>'
    return (
        f'<svg class="die-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="4" y="4" width="92" height="92" rx="18" fill="{face}" '
        f'stroke="{edge}" stroke-width="4"/>{dots}</svg>'
    )

# =============================================================================
# 3. APLICACIÓN
# =============================================================================

def main():
    st.markdown(build_css(), unsafe_allow_html=True)
    numeric_pages, extra_pages = discover_pages()
    pages_by_chapter: dict[int, list[Page]] = {}
    for page in numeric_pages:
        pages_by_chapter.setdefault(page.chapter, []).append(page)

    def go_to_random_page() -> None:
        available = [
            (chapter, position, page)
            for chapter, chapter_pages in pages_by_chapter.items()
            for position, page in enumerate(chapter_pages, start=1)
        ]
        if available:
            chapter, position, page = random.choice(available)
            st.session_state["dice"] = (chapter, position)
            st.switch_page(page.route)

    left_col, right_col = st.columns([1, 4], gap="large")
    with left_col:
        st.markdown(
            "<div class='home-hero'>"
            "<div class='brand'>C1VIC D4TA</div>"
            "<div class='tagline'>Una posible aproximación a la <strong>probabilidad</strong> y la "
            "<strong>estadística</strong></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if "dice" not in st.session_state:
            st.session_state["dice"] = (random.randint(2, 6), random.randint(2, 6))
        d1, d2 = st.session_state["dice"]
        st.markdown("<div class='section-title'>Voy a tener suerte</div>", unsafe_allow_html=True)
        dcol1, dcol2 = st.columns(2, gap="small")
        with dcol1:
            if st.button(DIE_FACES[d1], key="die_1", use_container_width=True):
                go_to_random_page()
        with dcol2:
            if st.button(DIE_FACES[d2], key="die_2", use_container_width=True):
                go_to_random_page()

    with right_col:
        probability_panel, statistics_panel = st.columns([5, 2], gap="large")

        with probability_panel:
            probability_title, probability_content = st.columns([1, 20], gap="small")
            with probability_title:
                st.markdown(
                    "<div class='vertical-section-title'>Probabilidad</div>",
                    unsafe_allow_html=True,
                )
            with probability_content:
                # Siempre seis filas y seis columnas: una fila por capítulo.
                with st.container(key="grid"):
                    for chapter in range(1, 7):
                        cols = st.columns(6, gap="small")
                        for position in range(1, 7):
                            with cols[position - 1]:
                                chapter_pages = pages_by_chapter.get(chapter, [])
                                page = chapter_pages[position - 1] if position <= len(chapter_pages) else None
                                if page:
                                    if st.button(page.label, key=f"cell_{chapter}_{position}", use_container_width=True):
                                        st.switch_page(page.route)
                                else:
                                    st.button(
                                        f"{chapter}·{position}\n\nLorem Ipsum",
                                        key=f"cell_{chapter}_{position}",
                                        use_container_width=True,
                                        disabled=True,
                                    )

        with statistics_panel:
            statistics_title, statistics_content = st.columns([1, 8], gap="small")
            with statistics_title:
                st.markdown(
                    "<div class='vertical-section-title'>Estadística univariante</div>",
                    unsafe_allow_html=True,
                )
            with statistics_content:
                with st.container(key="extra-page"):
                    for page in extra_pages:
                        if st.button(page.label, key=f"extra_{page.path.stem}", use_container_width=True):
                            st.switch_page(page.route)

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
