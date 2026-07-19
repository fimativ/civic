import streamlit as st
import random

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

# Cuadrícula 6x6: (fila = capítulo n, columna = ejercicio m) -> archivo pages/0n_m_vs.py
# Los dos dados dan (n, m); las casillas sin ejercicio muestran "Lorem Ipsum".
EXERCISES = {
    (1, 1): "Orígenes de la probabilidad",
    (1, 2): "Axiomas de Kolmogórov",
    (1, 3): "Probabilidad clásica",
    (1, 4): "El arte de contar",
    (2, 5): "Probabilidad condicionada",
    (2, 6): "Independencia y prob. total",
}

def page_path(n, m):
    return f"pages/{n:02d}_{m}_vs.py"


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
    font-size: clamp(30px, 6vw, 60px); font-weight: 700; color: {UBU_RED}; line-height: 1.05;
}}
.home-hero .tagline {{
    font-size: clamp(14px, 2vw, 22px); color: var(--muted-fg); margin-top: 8px; font-style: italic;
}}
.section-title {{
    font-size: clamp(17px, 2.2vw, 26px); font-weight: 700; color: var(--app-fg);
    margin: 18px 0 14px 0; border-bottom: 3px solid {UBU_YELLOW}; padding-bottom: 8px;
}}

/* ---- Cuadrícula 6x6 (se mantiene en fila también en móvil) ---- */
.st-key-grid [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: clamp(3px, 0.8vw, 8px) !important; }}
.st-key-grid div[data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0 !important; }}
.st-key-grid [data-testid="stVerticalBlock"] {{ gap: clamp(3px, 0.8vw, 8px) !important; }}
.st-key-grid button {{
    height: clamp(48px, 11vw, 104px); width: 100%;
    border-radius: 12px !important; box-shadow: var(--shadow);
    white-space: normal !important; line-height: 1.1 !important;
    padding: 3px 3px !important; border: 2px solid var(--metric-border) !important;
    background: var(--box-bg) !important; color: var(--box-fg) !important;
}}
.st-key-grid button p {{ font-size: clamp(8.5px, 1.35vw, 15px) !important; font-weight: 700 !important; margin: 0 !important; }}
.st-key-grid button p:first-child {{ font-size: clamp(8px, 1.1vw, 12px) !important; opacity: 0.55; font-weight: 600 !important; }}
.st-key-grid button:disabled {{ opacity: 0.45 !important; background: var(--lorem-bg) !important; }}

/* ---- Dados ---- */
.die-svg {{ width: 100%; max-width: 108px; display: block; margin: 0 auto; }}
.dice-msg {{
    background: var(--box-bg); border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 14px 18px; text-align: center; box-shadow: var(--shadow);
    font-size: clamp(15px, 1.9vw, 22px); color: var(--box-fg); margin-top: 6px;
}}
.st-key-roll button {{
    background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;
    border: 2px solid {UBU_YELLOW} !important; border-radius: 12px !important;
    font-weight: 700 !important; height: 100%; min-height: 56px;
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
    dark = detect_dark_theme()
    if "dice" not in st.session_state:
        st.session_state["dice"] = None

    st.markdown(
        "<div class='home-hero'>"
        "<div class='brand'>C1VIC D4TA</div>"
        "<div class='tagline'>Un paseo interactivo por los orígenes y fundamentos de la "
        "probabilidad</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>Elige un ejercicio</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='dice-msg' style='margin-bottom:14px;'>Cada fila es un capítulo y cada columna un "
        "ejercicio. Pulsa una casilla para abrirlo, o tira los dados más abajo.</div>",
        unsafe_allow_html=True
    )

    # Resaltado dinámico de la fila/columna que marcan los dados
    if st.session_state["dice"]:
        d1, d2 = st.session_state["dice"]
        sels = [f".st-key-cell_{r}_{c} button"
                for r in range(1, 7) for c in range(1, 7) if r == d1 or c == d2]
        css = (",".join(sels) +
               f" {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important; "
               f"border-color: {UBU_RED} !important; opacity: 1 !important; }}")
        css += (f" .st-key-cell_{d1}_{d2} button {{ outline: 4px solid {UBU_RED}; "
                f"outline-offset: -4px; }}")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # Cuadrícula 6x6
    with st.container(key="grid"):
        for r in range(1, 7):
            cols = st.columns(6, gap="small")
            for c in range(1, 7):
                with cols[c - 1]:
                    if (r, c) in EXERCISES:
                        label = f"{r}·{c}\n\n{EXERCISES[(r, c)]}"
                        if st.button(label, key=f"cell_{r}_{c}", use_container_width=True):
                            st.switch_page(page_path(r, c))
                    else:
                        st.button(f"{r}·{c}\n\nLorem Ipsum", key=f"cell_{r}_{c}",
                                  use_container_width=True, disabled=True)

    # -------- Dados --------
    st.markdown("<div class='section-title'>¿No sabes por dónde empezar? Tira los dados</div>",
                unsafe_allow_html=True)

    rolled = bool(st.session_state["dice"])
    d1, d2 = st.session_state["dice"] if rolled else (1, 1)

    dcol1, dcol2, dcol3 = st.columns([1, 1, 3], gap="medium")
    with dcol1:
        st.markdown(die_svg(d1, dark, highlight=rolled), unsafe_allow_html=True)
    with dcol2:
        st.markdown(die_svg(d2, dark, highlight=rolled), unsafe_allow_html=True)
    with dcol3:
        with st.container(key="roll"):
            if st.button("Tirar los dados", use_container_width=True, key="roll_btn"):
                st.session_state["dice"] = (random.randint(1, 6), random.randint(1, 6))
                st.rerun()
        if rolled:
            if (d1, d2) in EXERCISES:
                if st.button(f"Ir a la casilla ({d1}, {d2}): {EXERCISES[(d1, d2)]}",
                             use_container_width=True, type="primary", key="go_btn"):
                    st.switch_page(page_path(d1, d2))
            else:
                st.markdown(
                    f"<div class='dice-msg'>Casilla ({d1}, {d2}): <b>Lorem Ipsum</b> — próximamente. "
                    f"¡Vuelve a tirar!</div>",
                    unsafe_allow_html=True
                )

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
