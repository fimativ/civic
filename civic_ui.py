#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Elementos comunes a todas las páginas de C1VIC D4TA.

Aquí viven los estilos (tema claro y oscuro, reflujo en móvil), las cajas de
texto, los spoilers, la navegación interna de cada ficha, el código de sesión
que fija los valores iniciales de los problemas y unas pocas utilidades para
dibujar con Bokeh con los colores de la casa.
"""

from __future__ import annotations

import hashlib

import numpy as np
import streamlit as st
from bokeh.plotting import figure
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. COLORES Y CONSTANTES
# =============================================================================

UBU_RED = "#9b2743"
UBU_YELLOW = "#F5C400"
UBU_DARK = "#1a1a1a"
BLUE_LINE = "#2b6cb0"
GREEN_LINE = "#2e7d32"
RED_LINE = "#c62828"
ORANGE_LINE = "#d97706"
PURPLE_LINE = "#6a1b9a"
GREY_LINE = "#8a8a8a"

YEAR = 2026
BRAND = "C1VIC D4TA"
FOOTER_TEXT = (
    "MIT License &nbsp;|&nbsp; CC BY-SA 4.0 &nbsp;|&nbsp; "
    f"[AOD, OVG, SPP] {YEAR}"
)

CODE_KEY = "civic_code"
CODE_PARAM = "c"
CODE_MAX = 40
DEFAULT_CODE = "UBU-GMAyC"        # código con el que arranca una sesión nueva
CODE_WIDGETS = ("code_field_input", "home_code_input")

LIGHT_VARS = """
    --app-bg: #fbfbfb;
    --app-fg: #141414;
    --panel-left-bg: #fffdef;
    --panel-right-bg: #f0eff4;
    --box-bg: #ffffff;
    --box-fg: #1a1a1a;
    --spoiler-bg: #e8eeff;
    --spoiler-fg: #35509e;
    --metric-border: #d0d0d0;
    --muted-fg: #666666;
    --disabled-bg: #efeef2;
    --pass-bg: #eaf5e9; --pass-fg: #2e7d32;
    --fail-bg: #fdecec; --fail-fg: #c62828;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
"""

DARK_VARS = """
    --app-bg: #0d0d0f;
    --app-fg: #f2f2f2;
    --panel-left-bg: #17160f;
    --panel-right-bg: #0f0f16;
    --box-bg: #1e1e24;
    --box-fg: #f2f2f2;
    --spoiler-bg: #1d2440;
    --spoiler-fg: #9db4ff;
    --metric-border: #4a4a52;
    --muted-fg: #adadad;
    --disabled-bg: #16161b;
    --pass-bg: #16261a; --pass-fg: #7bd88f;
    --fail-bg: #2a1717; --fail-fg: #ef9a9a;
    --shadow: 0 1px 3px rgba(0,0,0,0.45);
"""


def detect_dark_theme():
    """True/False si Streamlit expone el tema activo, None si no se puede saber."""
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return None


# =============================================================================
# 2. HOJA DE ESTILOS
# =============================================================================

def build_css() -> str:
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
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{
    padding: clamp(0.5rem, 2vw, 1.25rem) clamp(0.6rem, 3vw, 3rem) !important;
    max-width: 1600px !important;
}}

/* ---- Barra superior: casita, título y código de sesión ---- */
[data-testid="stHorizontalBlock"]:has(.st-key-home_btn) {{
    flex-wrap: nowrap !important; align-items: stretch !important;
}}
div[data-testid="stColumn"]:has(.st-key-home_btn) {{
    flex: 0 0 auto !important; width: 84px !important; min-width: 84px !important;
}}
.st-key-home_btn button {{
    background: var(--box-bg) !important; color: {UBU_RED} !important;
    border: none !important; border-radius: 12px !important;
    box-shadow: var(--shadow); height: 100%; min-height: 56px;
}}
.st-key-home_btn button p {{ font-size: clamp(24px, 3.6vw, 36px) !important; line-height: 1 !important; }}
.top-bar-title {{
    font-size: clamp(20px, 3.4vw, 34px); font-weight: 700; color: {UBU_RED};
    background: var(--box-bg); padding: clamp(12px, 2vw, 22px) clamp(16px, 3vw, 40px);
    border-radius: 12px; box-shadow: var(--shadow);
    display: flex; align-items: center; line-height: 1.2; min-height: 56px;
}}
div[data-testid="stColumn"]:has(.st-key-code_field) {{
    flex: 0 0 auto !important; width: 150px !important; min-width: 150px !important;
}}
.st-key-code_field input {{
    text-align: center; font-weight: 700; letter-spacing: 2px;
    font-size: clamp(15px, 1.8vw, 20px) !important;
}}
.st-key-code_field [data-testid="stWidgetLabel"] {{ display: none; }}
.code-badge {{
    background: var(--box-bg); border-radius: 12px; box-shadow: var(--shadow);
    text-align: center; font-size: clamp(11px, 1.2vw, 13px); color: var(--muted-fg);
    padding: 4px 8px; margin-top: 4px; letter-spacing: 0.3px;
}}

/* ---- Paneles izquierdo (lectura) y derecho (interacción) ---- */
div[data-testid="stColumn"]:has(.bg-left),
div[data-testid="stColumn"]:has(.bg-right) {{
    padding: clamp(16px, 3vw, 40px); border-radius: 16px;
    min-height: calc(100vh - 150px);
}}
div[data-testid="stColumn"]:has(.bg-left)  {{ background: var(--panel-left-bg); }}
div[data-testid="stColumn"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    display: flex; flex-direction: column; align-items: center;
}}

/* ---- Cajas de texto ---- */
.statement-box {{
    border: 3px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(16px, 2.5vw, 32px); background: var(--box-bg);
    font-style: italic; text-align: justify; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(16px, 2vw, 24px);
    line-height: 1.5; margin-bottom: clamp(16px, 2.5vw, 30px);
}}
.content-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(14px, 2vw, 24px); background: var(--box-bg);
    text-align: justify; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(15px, 1.9vw, 22px);
    line-height: 1.6; margin-bottom: clamp(12px, 1.6vw, 20px);
}}
.content-box table {{ width: 100%; border-collapse: collapse; text-align: center; }}
.content-box td, .content-box th {{ padding: 6px 4px; border-bottom: 1px solid var(--metric-border); }}
.content-box th {{ border-bottom: 2px solid {UBU_RED}; font-weight: 600; }}
.section-title {{
    font-size: clamp(18px, 2.3vw, 27px); font-weight: 700; color: var(--app-fg);
    margin: 10px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px;
}}
.spacer {{ height: clamp(16px, 3vw, 35px); }}

/* ---- Comentario dinámico y etiqueta de resultado ---- */
.comment-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(14px, 2vw, 24px); background: var(--box-bg);
    font-style: italic; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(15px, 1.9vw, 22px);
    line-height: 1.5; margin-bottom: 15px; width: 100%;
}}
.result-badge {{
    display: block; background: {UBU_YELLOW};
    border: 3px solid var(--metric-border); border-radius: 10px;
    padding: 12px 22px; font-weight: 700;
    font-size: clamp(15px, 1.9vw, 22px); color: {UBU_DARK};
    margin-bottom: 18px; box-shadow: var(--shadow); text-align: center;
}}

/* ---- Cajas de resultados ---- */
.metric-box {{
    font-size: clamp(15px, 1.8vw, 22px); color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 10px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px; box-shadow: var(--shadow); line-height: 1.35;
}}
.metric-box b {{ font-weight: 700; }}
.metric-a {{ border-color: {BLUE_LINE};   color: {BLUE_LINE};   font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE};  color: {GREEN_LINE};  font-weight: 700; }}
.metric-c {{ border-color: {ORANGE_LINE}; color: {ORANGE_LINE}; font-weight: 700; }}
.metric-d {{ border-color: {PURPLE_LINE}; color: {PURPLE_LINE}; font-weight: 700; }}
.result-yes   {{ background: {GREEN_LINE} !important; color: #ffffff !important; border-color: {GREEN_LINE} !important; }}
.result-no    {{ background: {RED_LINE} !important;   color: #ffffff !important; border-color: {RED_LINE} !important; }}
.result-gold  {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important; border-color: {UBU_YELLOW} !important; }}

/* ---- Verificador (cumple / no cumple) ---- */
.check-box {{
    font-size: clamp(15px, 1.9vw, 22px); color: var(--box-fg);
    padding: clamp(12px, 1.8vw, 20px); background: var(--box-bg);
    border-radius: 10px; margin-bottom: 14px; width: 100%;
    border-left: 8px solid var(--metric-border); box-shadow: var(--shadow);
    line-height: 1.45;
}}
.check-pass {{ border-left-color: var(--pass-fg); background: var(--pass-bg); }}
.check-fail {{ border-left-color: var(--fail-fg); background: var(--fail-bg); }}

/* ---- Spoiler: borroso hasta que se pulsa ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-lbl {{ cursor: pointer; display: block; position: relative; margin: 18px 0 22px 0; }}
.spoiler-hint {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2; pointer-events: none;
    font-size: clamp(14px, 1.7vw, 20px); font-weight: 700;
    color: var(--spoiler-fg); letter-spacing: 0.3px;
    background: var(--box-bg); padding: 8px 18px; border-radius: 999px;
    box-shadow: var(--shadow); white-space: nowrap; max-width: 95%;
    overflow: hidden; text-overflow: ellipsis;
}}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400;
    font-size: clamp(15px, 1.9vw, 22px); line-height: 1.5;
    background: var(--spoiler-bg); border-left: 8px solid var(--spoiler-fg);
    padding: clamp(16px, 2vw, 28px); border-radius: 0 12px 12px 0;
    filter: blur(9px); transition: filter 0.25s ease;
}}
.spoiler-toggle:checked ~ .spoiler-box  {{ filter: none; }}
.spoiler-toggle:checked ~ .spoiler-hint {{ opacity: 0; }}
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 12px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: clamp(17px, 2.2vw, 26px); color: var(--spoiler-fg);
    overflow-x: auto;
}}
.formula-box.plain {{ color: var(--box-fg); border-color: {UBU_RED}; }}

/* ---- Botones (navegación, acordeón, selección) ---- */
button p {{ font-size: clamp(14px, 1.7vw, 21px) !important; line-height: 1.2 !important; }}
div[data-testid="stColumn"] button {{
    padding-top: 14px !important; padding-bottom: 14px !important;
    white-space: normal !important; height: 100%;
}}

/* ---- Deslizadores: extremos y valor bien visibles ---- */
[data-testid="stSliderTickBar"] {{ opacity: 1 !important; }}
[data-testid="stSliderTickBar"], [data-testid="stSliderTickBar"] * {{
    font-size: clamp(16px, 2vw, 24px) !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
[data-testid="stSliderThumbValue"] {{
    font-size: clamp(16px, 2vw, 24px) !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
.stSlider [data-baseweb="slider"] {{ padding-top: 38px; padding-bottom: 5px; }}
.stSlider {{ margin-bottom: 5px; }}
.stSlider label p {{ font-size: clamp(14px, 1.6vw, 19px) !important; color: var(--muted-fg) !important; }}

/* ---- Entradas numéricas y selectores ---- */
[data-testid="stNumberInput"] input {{ font-size: clamp(16px, 1.9vw, 22px) !important; font-weight: 600 !important; }}
[data-testid="stNumberInput"] label p, [data-testid="stSelectbox"] label p, [data-testid="stCheckbox"] p {{
    font-size: clamp(14px, 1.7vw, 20px) !important; color: var(--app-fg) !important;
}}

/* ---- Leyendas, SVG y tablas sueltas ---- */
.caption-center {{
    text-align: center; color: var(--muted-fg); font-weight: 600;
    font-size: clamp(14px, 1.6vw, 18px); margin: 4px 0 8px 0;
}}
.svg-wrap {{ display: flex; justify-content: center; width: 100%; }}
.svg-wrap svg {{ max-width: 100%; height: auto; }}
.mono {{ font-family: 'DejaVu Sans Mono', Menlo, Consolas, monospace; letter-spacing: 1px; }}

/* ---- Pie de página ---- */
.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: clamp(14px, 2vw, 22px); text-align: center;
    font-style: italic; font-size: clamp(15px, 1.9vw, 22px); color: var(--box-fg);
    margin-top: 20px; width: 100%; box-shadow: var(--shadow);
}}
.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 20px; text-align: center;
    font-size: clamp(13px, 1.6vw, 20px); color: var(--muted-fg); margin-top: 28px;
}}

/* ============ Móvil: una sola columna ============ */
@media (max-width: 640px) {{
    div[data-testid="stColumn"]:has(.bg-left),
    div[data-testid="stColumn"]:has(.bg-right) {{
        min-height: auto !important; margin-bottom: 14px;
    }}
    .statement-box, .content-box, .comment-box {{ text-align: left; }}
    [data-testid="stHorizontalBlock"]:has(.st-key-home_btn) > div[data-testid="stColumn"] {{
        flex: 1 1 0 !important; width: auto !important; min-width: 0 !important;
    }}
    [data-testid="stHorizontalBlock"]:has(.st-key-home_btn) > div[data-testid="stColumn"]:has(.st-key-home_btn) {{
        flex: 0 0 auto !important; width: 60px !important; min-width: 60px !important;
    }}
    [data-testid="stHorizontalBlock"]:has(.st-key-home_btn) > div[data-testid="stColumn"]:has(.st-key-code_field) {{
        flex: 0 0 auto !important; width: 96px !important; min-width: 96px !important;
    }}
    .top-bar-title {{ font-size: 17px; padding: 10px 12px; }}
    .spoiler-hint {{ font-size: 13px; padding: 6px 12px; }}
}}
</style>
"""


# =============================================================================
# 3. CÓDIGO DE SESIÓN Y VALORES INICIALES
# =============================================================================

def normalize_code(code: str | None) -> str:
    """Cualquier palabra o combinación de letras, cifras y símbolos. Se quitan
    los espacios de los extremos y se compactan los interiores."""
    return " ".join(str(code or "").split())[:CODE_MAX]


def session_code() -> str:
    return st.session_state.get(CODE_KEY, "")


def set_session_code(code: str | None, source: str | None = None) -> None:
    """Fija el código de sesión, lo escribe en la dirección (?c=) y descarta los
    valores de los controles ya tocados para que entren los nuevos iniciales."""
    new = normalize_code(code)
    if new == session_code():
        return
    st.session_state[CODE_KEY] = new
    for key in list(st.session_state):
        if key.startswith("w_") or (key in CODE_WIDGETS and key != source):
            del st.session_state[key]
    if new:
        st.query_params[CODE_PARAM] = new
    elif CODE_PARAM in st.query_params:
        del st.query_params[CODE_PARAM]


def sync_code_with_url() -> None:
    """Un código en la dirección (recarga, enlace compartido) manda sobre el de
    la sesión; si la dirección no lo lleva, se le añade el de la sesión. Una
    sesión nueva sin código empieza con DEFAULT_CODE."""
    url_code = normalize_code(st.query_params.get(CODE_PARAM, ""))
    if not url_code and CODE_KEY not in st.session_state:
        url_code = DEFAULT_CODE      # primera visita sin código: se usa el de la asignatura
    if url_code and url_code != session_code():
        set_session_code(url_code)
    elif session_code() and not url_code:
        st.query_params[CODE_PARAM] = session_code()


def go(page: str) -> None:
    """Cambia de ficha conservando el código en la dirección."""
    code = session_code()
    st.switch_page(page, query_params={CODE_PARAM: code} if code else None)


def has_code() -> bool:
    return bool(session_code())


def r(tag: str = "") -> float:
    """Número en [0, 1) determinado por el código de sesión.

    Sin código vale 0.5 (los valores del enunciado clásico). Con una
    etiqueta se obtiene una segunda cifra independiente de la principal.
    """
    code = session_code()
    if not code:
        return 0.5
    seed = code.casefold()
    digest = hashlib.sha256(f"{seed}|{tag}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / 16 ** 12


def rint(lo: int, hi: int, tag: str = "") -> int:
    """Entero en [lo, hi] a partir de r(tag)."""
    return lo + int(r(tag) * (hi - lo + 1)) if hi > lo else lo


def rfloat(lo: float, hi: float, tag: str = "", decimals: int = 2) -> float:
    """Real en [lo, hi] a partir de r(tag), redondeado."""
    return round(lo + r(tag) * (hi - lo), decimals)


def rchoice(options, tag: str = ""):
    return options[rint(0, len(options) - 1, tag)]


def dint(classic: int, lo: int, hi: int, tag: str = "") -> int:
    """Valor inicial entero: el clásico sin código, uno derivado del código si lo hay."""
    return rint(lo, hi, tag) if has_code() else classic


def dfloat(classic: float, lo: float, hi: float, tag: str = "", decimals: int = 2) -> float:
    return rfloat(lo, hi, tag, decimals) if has_code() else classic


def dchoice(classic, options, tag: str = ""):
    return rchoice(options, tag) if has_code() else classic


def wkey(page: str, name: str) -> str:
    """Clave de un control cuyo valor inicial depende del código."""
    return f"w_{page}_{name}"


def _code_changed(widget_key: str):
    set_session_code(st.session_state.get(widget_key, ""), source=widget_key)


def code_input(widget_key: str, label: str, placeholder: str, compact: bool = True):
    """Campo de texto para el código de sesión (portada o barra superior)."""
    if widget_key not in st.session_state:
        st.session_state[widget_key] = session_code()
    st.text_input(
        label,
        key=widget_key,
        max_chars=CODE_MAX,
        placeholder=placeholder,
        on_change=_code_changed,
        args=(widget_key,),
        label_visibility="collapsed" if compact else "visible",
    )


# =============================================================================
# 4. ESTADO Y ESQUELETO DE CADA FICHA
# =============================================================================

def init_state(defaults: dict) -> None:
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def page_setup(title: str):
    """Estilos, barra superior (casita, título, código). Devuelve el tema."""
    sync_code_with_url()
    st.markdown(build_css(), unsafe_allow_html=True)
    dark = detect_dark_theme()

    c_home, c_title, c_code = st.columns([1, 10, 2], gap="small")
    with c_home:
        if st.button("⌂", key="home_btn", width="stretch", help="Volver al inicio"):
            go("inicio.py")
    with c_title:
        st.markdown(f"<div class='top-bar-title'>{BRAND} · {title}</div>",
                    unsafe_allow_html=True)
    with c_code:
        with st.container(key="code_field"):
            code_input("code_field_input", "Código", "código")
            if has_code():
                st.markdown(f"<div class='code-badge'>r = {r():.3f}</div>",
                            unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    return dark


def nav_bar(items, state_key: str = "page", part_key: str = "open_part") -> str:
    """Botonera de navegación: items = [(id, etiqueta, primera_parte | None)]."""
    current = st.session_state[state_key]
    cols = st.columns(len(items))
    for col, (page_id, label, first_part) in zip(cols, items):
        active = current == page_id
        if col.button(label, width="stretch",
                      type="primary" if active else "secondary",
                      key=f"nav_{page_id}"):
            update = {state_key: page_id}
            if first_part:
                update[part_key] = first_part
            st.session_state.update(update)
            st.rerun()
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    return current


def accordion_step(step_id: str, title: str, part_key: str = "open_part") -> bool:
    is_open = st.session_state.get(part_key) == step_id
    if st.button(title, key=f"acc_{step_id}", width="stretch",
                 type="primary" if is_open else "secondary"):
        st.session_state[part_key] = step_id if not is_open else None
        st.rerun()
    return is_open


def choice_buttons(options, state_key: str, labels=None, per_row: int = 4) -> str:
    """Fila(s) de botones de los que solo uno está activo. Devuelve el activo."""
    labels = labels or {o: str(o) for o in options}
    rows = [options[i:i + per_row] for i in range(0, len(options), per_row)]
    for row in rows:
        cols = st.columns(per_row)
        for col, opt in zip(cols, row):
            with col:
                active = st.session_state[state_key] == opt
                if st.button(labels[opt], key=f"ch_{state_key}_{opt}", width="stretch",
                             type="primary" if active else "secondary"):
                    st.session_state[state_key] = opt
                    st.rerun()
    return st.session_state[state_key]


# =============================================================================
# 5. CAJAS DE TEXTO
# =============================================================================

def _box(cls: str, html: str) -> None:
    st.markdown(f"<div class='{cls}'>{html}</div>", unsafe_allow_html=True)


def left_panel():
    st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)


def right_panel():
    st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)


def statement(html: str) -> None:
    _box("statement-box", html)


def content(html: str) -> None:
    _box("content-box", html)


def comment(html: str) -> None:
    _box("comment-box", html)


def badge(html: str) -> None:
    _box("result-badge", html)


def section(title: str) -> None:
    _box("section-title", title)


def spacer() -> None:
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)


def planteamiento() -> None:
    spacer()
    section("Planteamiento")


def try_it(html: str) -> None:
    section(f"Pruébalo tú mismo: {html}")


def metric(html: str, cls: str = "") -> None:
    _box(f"metric-box {cls}".strip(), html)


def metrics(items) -> None:
    """items = [(html, clase)] en una sola fila."""
    cols = st.columns(len(items))
    for col, (html, cls) in zip(cols, items):
        with col:
            metric(html, cls)


def check(ok: bool, html: str) -> None:
    _box("check-box " + ("check-pass" if ok else "check-fail"), html)


def footer_bar(html: str) -> None:
    _box("footer-bar", html)


def formula(expr: str) -> None:
    _box("formula-box plain", expr)


def spoiler(html: str, hint: str = "Pulsa para revelar la solución") -> None:
    st.markdown(
        f"""<label class='spoiler-lbl'>
            <input type='checkbox' class='spoiler-toggle'>
            <span class='spoiler-hint'>{hint}</span>
            <div class='spoiler-box'>{html}</div>
        </label>""",
        unsafe_allow_html=True,
    )


def formula_hidden(expr: str, hint: str = "Pulsa para revelar su expresión matemática") -> None:
    spoiler(f"<div class='formula-box'>{expr}</div>", hint=hint)


def caption(html: str) -> None:
    _box("caption-center", html)


def svg(markup: str) -> None:
    _box("svg-wrap", markup)


def stage(key: str, n: int, label: str = "Etapa de la demostración") -> int:
    """Deslizador para recorrer una demostración por etapas."""
    return st.slider(label, 1, n, 1, 1, key=key, label_visibility="collapsed")


def fmt_int(n: int) -> str:
    """Entero con separador de millares fino (no se confunde con el punto decimal).

    Como en la norma de la RAE, los números de cuatro cifras se escriben sin separar.
    """
    if abs(int(n)) < 10_000:
        return str(int(n))
    return f"{int(n):,}".replace(",", "\u202f")


def fmt_pct(x: float, digits: int = 0) -> str:
    """Porcentaje con espacio antes del signo, como recomienda la RAE: 95 %."""
    return f"{100 * x:.{digits}f} %"


def fmt_sci(x: float, digits: int = 2) -> str:
    """Número en notación científica para HTML (2.95·10⁻⁵); los moderados, en decimal."""
    if x == 0:
        return "0"
    exp = int(np.floor(np.log10(abs(x))))
    if -3 <= exp <= 4:
        return f"{x:.4f}" if exp < 0 else f"{x:.{digits}f}"
    mant = x / 10 ** exp
    return f"{mant:.{digits}f}&middot;10<sup>{exp}</sup>".replace("<sup>-", "<sup>&minus;")


def footer() -> None:
    _box("footer-license", FOOTER_TEXT)


def two_columns():
    return st.columns([1, 1], gap="large")


# =============================================================================
# 6. FIGURAS
# =============================================================================

def new_figure(dark, height: int = 300, **kwargs):
    """Figura de Bokeh con fondo transparente y ejes legibles en ambos temas."""
    p = figure(height=height, sizing_mode="stretch_width", toolbar_location=None, **kwargs)
    fg = "#e6e6e6" if dark else "#333333"
    grid = "#3a3a44" if dark else "#dddddd"
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    p.grid.grid_line_color = grid
    for ax in (p.xaxis, p.yaxis):
        ax.axis_label_text_font_size = "17px"
        ax.major_label_text_font_size = "15px"
        ax.axis_label_text_color = fg
        ax.major_label_text_color = fg
        ax.axis_line_color = grid
        ax.major_tick_line_color = grid
        ax.minor_tick_line_color = None
        ax.axis_label_text_font_style = "normal"
    if p.legend:
        p.legend.label_text_color = fg
    return p


def style_legend(p, dark, location: str = "top_left"):
    fg = "#e6e6e6" if dark else "#333333"
    p.legend.location = location
    p.legend.label_text_color = fg
    p.legend.label_text_font_size = "14px"
    p.legend.background_fill_alpha = 0.15
    p.legend.border_line_color = None
    return p


def show(p, key: str | None = None) -> None:
    streamlit_bokeh(p, use_container_width=True, theme="streamlit", key=key)
