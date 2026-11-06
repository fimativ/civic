#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Portada: código de sesión, dados de la suerte y cuadrícula de fichas."""

from __future__ import annotations

import random

import streamlit as st

import civic_ui as ui

TOPICS = {
    1: "Espacios de probabilidad",
    2: "Probabilidad condicionada",
    3: "Variables aleatorias",
    4: "Distribuciones continuas",
    5: "Vectores aleatorios",
    6: "Teoremas límite",
}

DIE_FACES = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

VOWELS = set("aeiouáéíóúü")
CLUSTERS = {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tr", "ch", "ll", "rr"}
SOFT_HYPHEN = "\u00ad"


def hyphenate(word: str) -> str:
    """Marca con guiones blandos las sílabas de las palabras largas, para que las
    casillas pequeñas partan «Probabi-lidad» y no «Probabilida-d»."""
    if len(word) < 8:
        return word
    low = word.lower()
    cuts = []
    i = 1
    while i < len(low) - 2:
        if low[i] in VOWELS and low[i + 1] not in VOWELS:
            if low[i + 2] in VOWELS:
                cuts.append(i + 1)
            elif low[i + 1:i + 3] in CLUSTERS:
                cuts.append(i + 1)
            elif low[i + 3:i + 4] and low[i + 3] in VOWELS:
                cuts.append(i + 2)
        i += 1
    cuts = [c for c in cuts if 2 <= c <= len(word) - 2]
    out, last = [], 0
    for c in cuts:
        out.append(word[last:c])
        last = c
    out.append(word[last:])
    return SOFT_HYPHEN.join(out)


def grid_label(title: str) -> str:
    return " ".join(hyphenate(w) for w in title.split())

HOME_CSS = f"""
<style>
/* ---- Barra superior: arriba los rótulos, una línea amarilla, debajo su contenido ---- */
.st-key-topbar [data-testid="stHorizontalBlock"] {{ gap: 0 !important; }}
.st-key-topbar div[data-testid="stColumn"] > div {{ gap: 10px !important; }}
.top-head, .st-key-code_head, .st-key-luck_head {{
    box-sizing: border-box; height: clamp(56px, 4.8vw, 68px) !important; min-height: 0 !important;
    display: flex; align-items: flex-end !important;
    border-bottom: 3px solid {ui.UBU_YELLOW}; padding: 0 clamp(8px, 1.2vw, 18px) 8px clamp(8px, 1.2vw, 18px);
}}
.st-key-code_head, .st-key-luck_head {{ flex: 0 0 auto !important; flex-direction: row !important; gap: 10px !important; }}
div:has(> .st-key-code_head), div:has(> .st-key-luck_head) {{ flex: 0 0 auto !important; height: auto !important; }}
.st-key-code_head > div, .st-key-luck_head > div {{ margin: 0 !important; width: auto !important; }}
.st-key-code_head > div:first-child, .st-key-luck_head > div:first-child {{ flex: 0 0 auto; }}
.st-key-code_head > div:last-child {{ flex: 1 1 auto; min-width: 0; }}
.top-head.brand {{
    font-size: clamp(26px, 3.2vw, 44px); font-weight: 700; color: {ui.UBU_RED}; line-height: 1;
}}
.top-label {{
    font-size: clamp(15px, 1.6vw, 24px); font-weight: 700; color: var(--app-fg); white-space: nowrap;
    line-height: 1.2;
}}
.st-key-code_head, .st-key-luck_head, .top-head.brand {{ align-items: center !important; padding-top: 6px !important; }}
.st-key-code_head > div, .st-key-luck_head > div {{ align-self: center; }}
.st-key-code_head [data-testid="stMarkdownContainer"] p, .st-key-luck_head [data-testid="stMarkdownContainer"] p,
.st-key-code_head [data-testid="stMarkdown"], .st-key-luck_head [data-testid="stMarkdown"] {{ margin: 0 !important; }}

.top-sub {{ padding: 0 clamp(8px, 1.2vw, 18px); margin-top: -6px; }}
.tagline {{ font-size: clamp(13px, 1.2vw, 17px); color: var(--muted-fg); font-style: italic; }}
.st-key-home_code input {{
    text-align: center; font-weight: 700; letter-spacing: 3px;
    font-size: clamp(17px, 1.9vw, 24px) !important;
}}
.st-key-die_1, .st-key-die_2 {{ flex: 0 0 auto !important; width: auto !important; }}
.st-key-die_1 button, .st-key-die_2 button {{
    width: clamp(34px, 3vw, 46px) !important; height: clamp(34px, 3vw, 46px) !important;
    min-height: 0 !important; padding: 0 !important;
    border-radius: 8px !important; background: var(--box-bg) !important; color: var(--box-fg) !important;
    border: 2px solid var(--metric-border) !important; line-height: 1 !important;
}}
.st-key-die_1 button p, .st-key-die_2 button p {{ font-size: clamp(27px, 2.5vw, 38px) !important; line-height: 1 !important; }}
.st-key-die_1 button:active, .st-key-die_2 button:active {{ animation: dice-shake 0.45s ease-in-out; }}
@keyframes dice-shake {{
    0%, 100% {{ transform: rotate(0deg) scale(1); }}
    25% {{ transform: rotate(-12deg) scale(1.08); }}
    50% {{ transform: rotate(12deg) scale(1.12); }}
    75% {{ transform: rotate(-8deg) scale(1.06); }}
}}

/* ---- Títulos de bloque en vertical ---- */
.vertical-section-title {{
    writing-mode: vertical-rl; transform: rotate(180deg); height: 100%;
    display: flex; align-items: center; justify-content: center;
    font-size: clamp(16px, 1.8vw, 24px); font-weight: 700; color: var(--app-fg);
    border-right: 3px solid {ui.UBU_YELLOW}; padding-right: 8px;
}}
div[data-testid="stColumn"]:has(.prob-title):not(:has(div[data-testid="stColumn"])) {{ position: relative; min-height: 120px; }}
div[data-testid="stColumn"]:has(.prob-title):not(:has(div[data-testid="stColumn"])) div:has(.prob-title) {{ position: static !important; }}
.prob-title {{ position: absolute; inset: 0; }}

/* ---- Cuadrícula 6x6 de probabilidad ---- */
.st-key-grid [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: clamp(3px, 0.7vw, 10px) !important; }}
.st-key-grid div[data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0 !important; }}
.st-key-grid [data-testid="stVerticalBlock"] {{ gap: clamp(3px, 0.7vw, 10px) !important; }}
.st-key-grid button {{
    aspect-ratio: 1 / 1; height: auto; min-height: 0; width: 100%;
    border-radius: 12px !important; box-shadow: var(--shadow);
    padding: clamp(3px, 0.5vw, 8px) !important; border: 2px solid var(--metric-border) !important;
    background: var(--box-bg) !important; color: var(--box-fg) !important;
    display: flex !important; align-items: stretch !important; justify-content: stretch !important;
}}
.st-key-grid button > div {{ width: 100%; height: 100%; }}
.st-key-grid button [data-testid="stMarkdownContainer"] {{
    width: 100%; height: 100%; display: grid; grid-template-columns: auto 1fr;
    grid-template-rows: 1fr auto; column-gap: clamp(2px, 0.4vw, 6px); row-gap: 2px;
}}
.st-key-grid button p {{ margin: 0 !important; line-height: 1.05 !important; }}
.st-key-grid button p:nth-child(1) {{
    grid-column: 1; grid-row: 1; align-self: start; white-space: pre-line !important;
    font-size: clamp(15px, 2.3vw, 34px) !important; line-height: 0.95 !important; opacity: 0.85;
}}
.st-key-grid button p:nth-child(2) {{
    grid-column: 2; grid-row: 1; align-self: center; text-align: center; font-size: clamp(9px, 1.55vw, 24px) !important; font-weight: 700 !important; color: {ui.UBU_RED};
    line-height: 1.05 !important; white-space: nowrap !important; overflow: hidden;
}}
.st-key-grid button p:nth-child(3) {{
    grid-column: 1 / span 2; grid-row: 2; text-align: center; white-space: normal !important;
    font-size: clamp(7px, 0.82vw, 12px) !important; font-weight: 600 !important; opacity: 0.75;
}}
.st-key-grid button:disabled {{ opacity: 0.45 !important; background: var(--disabled-bg) !important; }}

/* ---- Estadística: tan alta como la cuadrícula, con desplazamiento propio ---- */
div[data-testid="stHorizontalBlock"]:has(.st-key-stats_panel) {{ align-items: stretch !important; }}
div[data-testid="stColumn"]:has(.st-key-stats_panel) {{ position: relative; }}
.st-key-stats_panel {{
    position: absolute !important; inset: 0; flex-direction: row !important; gap: 8px !important;
}}
.st-key-stats_panel > div {{ height: 100%; min-height: 0; }}
.st-key-stats_panel > div:first-child {{ flex: 0 0 auto; width: auto !important; }}
.st-key-stats_panel > div:last-child {{ flex: 1 1 auto; min-width: 0; }}
.st-key-tools {{
    flex: 1 1 auto; height: 100%; overflow-y: auto; padding: 2px 8px 2px 2px;
    gap: clamp(4px, 0.6vw, 8px) !important; scrollbar-width: thin;
}}
.st-key-tools button {{
    min-height: 52px; border-radius: 10px !important; box-shadow: var(--shadow);
    background: var(--box-bg) !important; color: var(--box-fg) !important;
    border: 2px solid var(--metric-border) !important; font-weight: 700;
}}
.st-key-tools button p {{ font-size: clamp(11px, 1.05vw, 15px) !important; line-height: 1.1 !important; margin: 0 !important; }}
.st-key-tools button:disabled {{ opacity: 0.45 !important; background: var(--disabled-bg) !important; }}

/* ---- Móvil ---- */
@media (max-width: 640px) {{
    .vertical-section-title {{
        writing-mode: horizontal-tb; transform: none; min-height: 0; height: auto;
        justify-content: flex-start; border-right: none; padding-right: 0;
        border-bottom: 3px solid {ui.UBU_YELLOW}; padding-bottom: 6px; margin: 10px 0 6px 0;
    }}
    .top-head.brand, .st-key-code_head {{ border-bottom: none; }}
    .st-key-grid button p:nth-child(3) {{ display: none; }}
    .st-key-grid button p:nth-child(1) {{ font-size: 11px !important; }}
    div[data-testid="stColumn"]:has(.prob-title):not(:has(div[data-testid="stColumn"])) {{ min-height: 0; }}
    .prob-title {{ position: static; }}
    .st-key-grid button p:nth-child(2) {{ font-size: 8.5px !important; }}
    .st-key-stats_panel {{ position: static !important; flex-direction: column !important; }}
    .st-key-stats_panel > div {{ height: auto; }}
    .st-key-grid button [data-testid="stMarkdownContainer"] {{ grid-template-rows: 1fr; }}
    .st-key-tools {{ height: auto; overflow: visible; padding: 0; }}
}}
</style>
"""


def cell_label(chapter: int, number: int, symbol: str, title: str) -> str:
    """Casilla de la cuadrícula: los dos dados en columna a la izquierda, el símbolo a su lado y
    el título en pequeño debajo."""
    return f"{DIE_FACES[chapter]}\n{DIE_FACES[number]}\n\n{symbol or '·'}\n\n{grid_label(title)}"


def main():
    ui.sync_code_with_url()
    st.markdown(ui.build_css(), unsafe_allow_html=True)
    st.markdown(HOME_CSS, unsafe_allow_html=True)

    sheets = st.session_state.get("sheets", [])
    exercises = {}
    for s in sheets:
        if not s.is_statistics:
            exercises.setdefault(s.chapter, []).append(s)
    tools = [s for s in sheets if s.is_statistics]
    unlocked = ui.has_code()

    def go_to_random_sheet():
        candidates = [s for chapter in exercises.values() for s in chapter]
        if candidates:
            target = random.choice(candidates)
            st.session_state["dice"] = (target.chapter, target.number)
            ui.go(target.route)

    if "dice" not in st.session_state:
        st.session_state["dice"] = (random.randint(1, 6), random.randint(1, 6))
    d1, d2 = st.session_state["dice"]

    # Barra superior: tres columnas con la misma línea amarilla, que en pantalla ancha se ve continua.
    with st.container(key="topbar"):
        brand_col, code_col, luck_col = st.columns([7, 8, 7], gap=None)
        with brand_col:
            st.markdown("<div class='top-head brand'>C1VIC D4TA</div>", unsafe_allow_html=True)
        with code_col:
            with st.container(key="code_head"):
                st.markdown("<div class='top-label'>Código:</div>", unsafe_allow_html=True)
                with st.container(key="home_code"):
                    ui.code_input("home_code_input", "Código de sesión", "una palabra, cifras, símbolos...")
        with luck_col:
            with st.container(key="luck_head"):
                st.markdown("<div class='top-label'>Voy a tener suerte</div>", unsafe_allow_html=True)
                if st.button(DIE_FACES[d1], key="die_1", disabled=not unlocked):
                    go_to_random_sheet()
                if st.button(DIE_FACES[d2], key="die_2", disabled=not unlocked):
                    go_to_random_sheet()

    r_text = f" (r = {ui.r():.3f})" if unlocked else ""
    st.markdown("<div class='top-sub tagline'>Una posible aproximación a la "
                f"<strong>probabilidad</strong> y la <strong>estadística</strong>{r_text}</div>",
                unsafe_allow_html=True)

    ui.spacer()
    probability_panel, statistics_panel = st.columns([3, 1], gap="large")

    with probability_panel:
        title_col, grid_col = st.columns([1, 24], gap="small")
        with title_col:
            st.markdown("<div class='vertical-section-title prob-title'>Probabilidad</div>", unsafe_allow_html=True)
        with grid_col:
            with st.container(key="grid"):
                for chapter in range(1, 7):
                    cols = st.columns(6, gap="small")
                    chapter_sheets = exercises.get(chapter, [])
                    for position in range(1, 7):
                        with cols[position - 1]:
                            sheet = next((s for s in chapter_sheets if s.number == position), None)
                            if sheet:
                                if st.button(cell_label(chapter, position, sheet.symbol, sheet.title),
                                             key=f"cell_{chapter}_{position}",
                                             width="stretch", disabled=not unlocked):
                                    ui.go(sheet.route)
                            else:
                                st.button(cell_label(chapter, position, "", "En preparación"),
                                          key=f"cell_{chapter}_{position}", width="stretch", disabled=True)

    with statistics_panel:
        with st.container(key="stats_panel"):
            st.markdown("<div class='vertical-section-title'>Estadística univariante</div>",
                        unsafe_allow_html=True)
            with st.container(key="tools"):
                for sheet in tools:
                    if st.button(sheet.title, key=f"tool_{sheet.number}", width="stretch",
                                 disabled=not unlocked):
                        ui.go(sheet.route)
                if not tools:
                    st.button("En preparación", key="tool_none", width="stretch", disabled=True)

    ui.footer()


main()
