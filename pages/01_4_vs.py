import streamlit as st
import numpy as np
import random
from math import factorial, perm, comb
from scipy import stats
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · El arte de contar",
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
    --panel-left-bg: #fffdef;
    --panel-right-bg: #f0eff4;
    --box-bg: #ffffff;
    --box-fg: #1a1a1a;
    --spoiler-bg: #e8eeff;
    --spoiler-fg: #35509e;
    --metric-border: #d0d0d0;
    --muted-fg: #666666;
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
    --shadow: 0 1px 3px rgba(0,0,0,0.45);
"""


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
    padding: clamp(0.5rem, 2vw, 1.25rem) clamp(0.6rem, 3vw, 3rem) !important;
    max-width: 1600px !important;
}}

/* ---- Botón Home (casita) ---- */
[data-testid="stHorizontalBlock"]:has(.st-key-home_btn) {{ flex-wrap: nowrap !important; align-items: stretch !important; }}
div[data-testid="stColumn"]:has(.st-key-home_btn) {{ flex: 0 0 auto !important; width: 84px !important; min-width: 84px !important; }}
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
    display: flex; align-items: center; line-height: 1.2;
}}

div[data-testid="column"]:has(.bg-left),
div[data-testid="column"]:has(.bg-right) {{
    padding: clamp(16px, 3vw, 40px); border-radius: 16px;
    min-height: calc(100vh - 150px);
}}
div[data-testid="column"]:has(.bg-left)  {{ background: var(--panel-left-bg); }}
div[data-testid="column"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    display: flex; flex-direction: column; align-items: center;
}}

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
.section-title {{
    font-size: clamp(18px, 2.3vw, 27px); font-weight: 700; color: var(--app-fg);
    margin: 10px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px;
}}
.spacer {{ height: clamp(16px, 3vw, 35px); }}

.comment-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(14px, 2vw, 24px); background: var(--box-bg);
    font-style: italic; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(15px, 1.9vw, 22px);
    line-height: 1.5; margin-bottom: 15px; width: 100%;
}}
.result-badge {{
    display: inline-block; background: {UBU_YELLOW};
    border: 3px solid var(--metric-border); border-radius: 10px;
    padding: 12px 22px; font-weight: 700;
    font-size: clamp(15px, 1.9vw, 22px); color: {UBU_DARK};
    margin-bottom: 18px; box-shadow: var(--shadow); text-align: center; width: 100%;
}}
.urn-caption {{ text-align: center; font-weight: 700; color: var(--app-fg);
    font-size: clamp(14px, 1.7vw, 20px); margin-bottom: 6px; }}

/* ---- Spoiler ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-lbl {{ cursor: pointer; display: block; position: relative; margin: 18px 0 22px 0; }}
.spoiler-hint {{
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 2; pointer-events: none;
    font-size: clamp(14px, 1.7vw, 20px); font-weight: 700;
    color: var(--spoiler-fg); letter-spacing: 0.3px;
    background: var(--box-bg); padding: 8px 18px; border-radius: 999px;
    box-shadow: var(--shadow); white-space: nowrap;
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
}}
.formula-box.plain {{ color: var(--box-fg); border-color: {UBU_RED}; }}

button p {{ font-size: clamp(14px, 1.7vw, 21px) !important; line-height: 1.2 !important; }}
div[data-testid="column"] button {{
    padding-top: 14px !important; padding-bottom: 14px !important;
    white-space: normal !important; height: 100%;
}}

/* ---- Radios (clasificador combinatorio) ---- */
[data-testid="stRadio"] > label p {{
    font-size: clamp(14px, 1.8vw, 21px) !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
[data-testid="stRadio"] div[role="radiogroup"] label p {{
    font-size: clamp(14px, 1.7vw, 20px) !important; color: var(--app-fg) !important;
}}

/* ---- Sliders: números min/max ARRIBA y grandes ---- */
div[data-testid="stSlider"] > div {{ display: flex !important; flex-direction: column-reverse !important; }}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"], [data-testid="stThumbValue"] {{
    display: block !important;
    font-size: clamp(16px, 2.2vw, 26px) !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
[data-testid="stSlider"] label p {{ font-size: clamp(14px, 1.7vw, 20px) !important; color: var(--app-fg) !important; }}
.stSlider [data-baseweb="slider"] {{ padding-top: 46px; padding-bottom: 5px; }}
.stSlider {{ margin-bottom: 5px; }}

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

@media (max-width: 640px) {{
    div[data-testid="column"]:has(.bg-left),
    div[data-testid="column"]:has(.bg-right) {{ min-height: auto !important; margin-bottom: 14px; }}
    .statement-box, .content-box, .comment-box {{ text-align: left; }}
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "TEO",
        "open_p1": "U_A",
        "open_p3": "C_A",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. AUXILIARES
# =============================================================================

def accordion(state_key: str, step_id: str, title: str) -> bool:
    is_open = st.session_state[state_key] == step_id
    if st.button(title, key=f"acc_{state_key}_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state[state_key] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(html_content: str, hint: str = "Pulsa para revelar la solución"):
    st.markdown(
        f"""<label class='spoiler-lbl'>
            <input type='checkbox' class='spoiler-toggle'>
            <span class='spoiler-hint'>{hint}</span>
            <div class='spoiler-box'>{html_content}</div>
        </label>""",
        unsafe_allow_html=True,
    )

def fmt(x):
    return f"{x:,}".replace(",", ".")

def chart_theme(dark):
    if dark is True:
        return dict(fg="#e6e6e6", grid="#3a3a42", axis="#8a8a92", line="#5a5a62")
    if dark is False:
        return dict(fg="#2a2a2a", grid="#e2e2e2", axis="#9a9a9a", line="#c2c2c2")
    return dict(fg="#8a8a8a", grid="#8a8a8a", axis="#8a8a8a", line="#8a8a8a")

def style_axes(p, th, label_size="18px", tick_size="14px"):
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    for axis in (p.xaxis, p.yaxis):
        axis.axis_label_text_font_size = label_size
        axis.major_label_text_font_size = tick_size
        axis.axis_label_text_color = th["fg"]
        axis.major_label_text_color = th["fg"]
        axis.axis_line_color = th["axis"]
        axis.major_tick_line_color = th["axis"]
        axis.minor_tick_line_color = None
    p.xgrid.grid_line_color = th["grid"]
    p.ygrid.grid_line_color = th["grid"]
    p.xgrid.grid_line_alpha = 0.5
    p.ygrid.grid_line_alpha = 0.5
    return p

# ---- Clasificador combinatorio ----

def combi_kind(orden, repeticion, todos):
    if orden and todos:
        return "PR" if repeticion else "P"
    if orden and not todos:
        return "VR" if repeticion else "V"
    if not orden and not todos:
        return "CR" if repeticion else "C"
    return "DEG"

def combi_value(kind, m, n):
    if kind == "V":
        return perm(m, n)
    if kind == "VR":
        return m ** n
    if kind == "P":
        return factorial(m)
    if kind == "C":
        return comb(m, n)
    if kind == "CR":
        return comb(m + n - 1, n)
    if kind == "DEG":
        return 1
    return None  # PR: depende de las multiplicidades

COMBI_INFO = {
    "V":  ("Variaciones sin repetición", "V<sub>m</sub><sup>n</sup> = m! / (m&minus;n)!",
           "Medallas de oro, plata y bronce entre 10 atletas."),
    "VR": ("Variaciones con repetición", "VR<sub>m</sub><sup>n</sup> = m<sup>n</sup>",
           "Un candado de 3 ruedas del 0 al 9."),
    "P":  ("Permutaciones sin repetición", "P<sub>m</sub> = m!",
           "El orden de llegada de m corredores a meta."),
    "PR": ("Permutaciones con repetición", "PR = m! / (n<sub>1</sub>! &middot; n<sub>2</sub>! &middot; &hellip;)",
           "Ordenar las letras de BANANA: 6!/(3!·2!·1!) = 60."),
    "C":  ("Combinaciones sin repetición", "C<sub>m</sub><sup>n</sup> = ( m sobre n )",
           "Elegir un comité de n personas entre m."),
    "CR": ("Combinaciones con repetición", "CR<sub>m</sub><sup>n</sup> = ( m+n&minus;1 sobre n )",
           "n bolas de helado eligiendo entre m sabores."),
    "DEG": ("Caso degenerado", "1",
            "Sin orden y usando todos los elementos, solo hay una agrupación: el propio conjunto."),
}

# ---- Urna en SVG (tema claro/oscuro, responsive) ----

def draw_urn(white_balls, black_balls, dark, seed=42):
    total = white_balls + black_balls
    stroke = UBU_RED
    fg = "#e6e6e6" if dark else "#333333"
    w_fill, w_stroke = "#ffffff", "#333333"
    b_fill, b_stroke = ("#0c0c0c", "#9a9aa2") if dark else ("#1a1a1a", "#666666")
    r = 12
    svg = f'''<svg viewBox="0 0 300 300" width="100%" style="max-width:280px" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="150" cy="70" rx="80" ry="24" fill="none" stroke="{stroke}" stroke-width="3"/>
        <path d="M 70 70 L 70 190" stroke="{stroke}" stroke-width="3" fill="none"/>
        <path d="M 230 70 L 230 190" stroke="{stroke}" stroke-width="3" fill="none"/>
        <ellipse cx="150" cy="190" rx="80" ry="24" fill="none" stroke="{stroke}" stroke-width="3"/>
        <path d="M 100 70 Q 55 35 100 70" fill="none" stroke="{stroke}" stroke-width="3"/>
        <path d="M 200 70 Q 245 35 200 70" fill="none" stroke="{stroke}" stroke-width="3"/>
    '''
    random.seed(seed)
    for _ in range(white_balls):
        x = random.randint(92, 208); y = random.randint(88, 172)
        svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{w_fill}" stroke="{w_stroke}" stroke-width="2"/>'
    for _ in range(black_balls):
        x = random.randint(92, 208); y = random.randint(88, 172)
        svg += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{b_fill}" stroke="{b_stroke}" stroke-width="2"/>'
    svg += (f'<text x="150" y="238" text-anchor="middle" font-size="16" fill="{fg}">'
            f'{white_balls} blancas · {black_balls} negras</text>'
            f'<text x="150" y="262" text-anchor="middle" font-size="14" fill="{fg}">Total: {total} bolas</text></svg>')
    return svg

def probability_all_different(n):
    if n > 365:
        return 0.0
    p = 1.0
    for i in range(n):
        p *= (365 - i) / 365
    return p

# ---- Gráficas ----

def birthday_chart(n_cur, dark):
    th = chart_theme(dark)
    ns = list(range(1, 81))
    ps = [1 - probability_all_different(k) for k in ns]
    p = figure(height=310, sizing_mode="stretch_width",
               x_axis_label="nº de personas (n)", y_axis_label="P(coincidencia)",
               toolbar_location=None, x_range=(1, 80), y_range=(0, 1.03))
    p.line(ns, ps, line_width=5, color=BLUE_LINE)
    p.add_layout(Span(location=0.5, dimension="width", line_color=th["axis"],
                      line_dash="dashed", line_width=1))
    p.add_layout(Span(location=23, dimension="height", line_color=th["axis"],
                      line_dash="dotted", line_width=1))
    cur = 1 - probability_all_different(n_cur)
    p.scatter([n_cur], [cur], size=16, marker="circle", color=UBU_RED,
              line_color="white", line_width=2)
    return style_axes(p, th)

def binomial_chart(n, p_ok, kmin, dark):
    th = chart_theme(dark)
    ks = np.arange(0, n + 1)
    pmf = stats.binom.pmf(ks, n, p_ok)
    colors = [UBU_RED if k >= kmin else BLUE_LINE for k in ks]
    fig = figure(height=310, sizing_mode="stretch_width",
                 x_axis_label="k (nº de caras)", y_axis_label="P(X = k)",
                 toolbar_location=None)
    fig.vbar(x=ks, top=pmf, width=0.92, fill_color=colors, line_color=None)
    fig.add_layout(Span(location=kmin - 0.5, dimension="height",
                        line_color=th["fg"], line_dash="dashed", line_width=2))
    return style_axes(fig, th)

# =============================================================================
# 4. PÁGINAS
# =============================================================================

def render_theory(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>El arte de contar</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Antes que el álgebra o el cálculo estuvo la aritmética, y antes que "
            "medir estuvo <b>contar</b>. La combinatoria es precisamente el arte de contar sin escribir "
            "una a una todas las posibilidades: nos dice cuántas hay. Sus orígenes son muy antiguos —los "
            "matemáticos de la India, como Pingala, ya contaban métricas y combinaciones—, y hoy sabemos "
            "que el cardinal de un conjunto puede dispararse de forma vertiginosa: Ronald Graham hizo "
            "célebre un número tan colosal (el número de Graham) que ni todo el universo bastaría para "
            "escribir sus cifras. Contar bien es, por tanto, imprescindible.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Seguramente ya lo trataste en Matemática Discreta, pero conviene "
            "recordar que todo se reduce a tres ideas fundamentales: <b>¿importa el orden?</b>, <b>¿puede "
            "haber repetición?</b> y <b>¿se usan todos los elementos?</b>. Juega con las tres respuestas y "
            "con los deslizadores para descubrir de qué agrupación se trata.</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-title'>Calculadora combinatoria</div>", unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        m = cs1.slider("Total de elementos (m)", 1, 20, 10, key="slider_m")
        n = cs2.slider("Elementos a tomar (n)", 1, 20, 3, key="slider_n")

        q1, q2, q3 = st.columns(3)
        orden = q1.radio("¿Importa el orden?", ["Sí", "No"], key="q_orden", horizontal=True) == "Sí"
        rep   = q2.radio("¿Hay repetición?", ["Sí", "No"], index=1, key="q_rep", horizontal=True) == "Sí"
        todos = q3.radio("¿Todos los elementos?", ["Sí", "No"], index=1, key="q_todos", horizontal=True) == "Sí"

        kind = combi_kind(orden, rep, todos)
        name, expr, example = COMBI_INFO[kind]
        val = combi_value(kind, m, n)
        val_txt = f" = <b>{fmt(val)}</b>" if val is not None else ""

        st.markdown(
            f"<div class='content-box'><b>{name}.</b><br>Ejemplo: {example}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='formula-box plain'>{expr}{val_txt}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-title'>Ahora inténtalo tú</div>", unsafe_allow_html=True)
        if val is not None:
            st.markdown(
                f"<div class='content-box'>Si tuvieras <b>un elemento más</b> en el total "
                f"(m + 1 = {m + 1}), ¿cuántas agrupaciones de este mismo tipo habría?</div>",
                unsafe_allow_html=True
            )
            spoiler(f"Habría <b>{fmt(combi_value(kind, m + 1, n))}</b> agrupaciones.")
        else:
            st.markdown(
                "<div class='content-box'>¿Cuántas ordenaciones distintas tiene la palabra "
                "<b>PROBABILIDAD</b>? (12 letras, con la B, la A y la D repetidas).</div>",
                unsafe_allow_html=True
            )
            palabra = factorial(12) // (factorial(2) * factorial(3) * factorial(2))
            spoiler(f"12! / (2!·3!·2!) = <b>{fmt(palabra)}</b> ordenaciones.")

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Urnas de Pólya</b><br>"
            "<i>Explora junto con George Pólya (1887-1985) el problema de la urna y el de las "
            "oposiciones.</i><br><br>"
            "<b>II. La paradoja del cumpleaños</b><br>"
            "<i>Descubre si alguien en clase comparte tu fecha de nacimiento con un pequeño sistema "
            "digital.</i><br><br>"
            "<b>III. Monedas cargadas</b><br>"
            "<i>Adéntrate en una isla desierta y consigue una probabilidad perfecta con monedas "
            "imperfectas.</i>"
            "</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Pruébalo tú mismo: cambia el número de "
                    "<u>bolas blancas W</u></div>", unsafe_allow_html=True)
        w_balls = st.slider("Bolas blancas iniciales (W)", 1, 10, 5, key="slider_w",
                            label_visibility="collapsed")

        st.markdown(
            "<div class='statement-box'><b>Urnas de Pólya</b><br><br>"
            "Una urna contiene W bolas blancas y 4 negras. Se extrae una bola al azar y resulta ser "
            "<b>negra</b>; después se eligen 3 de las bolas restantes para formar una segunda urna. ¿Cuál "
            "es la probabilidad de que entre esas 3 haya <b>al menos una blanca</b>?</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p1", "U_A", "(A) Dos colores, una decisión"):
            st.markdown(
                "<div class='content-box'>Tras sacar la primera bola negra, en la urna quedan W blancas y "
                "3 negras. Formamos la segunda urna eligiendo 3 de esas bolas al azar. Es más cómodo "
                "calcular el <b>complementario</b>: que las 3 elegidas sean todas negras.<br><br>"
                "<i>Trata de escribir la probabilidad antes de revelarla.</i></div>",
                unsafe_allow_html=True
            )
            total_rest = w_balls + 3
            casos = comb(total_rest, 3)
            p_negras = 1 / casos
            spoiler(
                f"<div class='formula-box'>P(al menos 1 blanca) = 1 &minus; "
                f"<sup>1</sup>&frasl;<sub>C({total_rest},3)</sub> = 1 &minus; "
                f"<sup>1</sup>&frasl;<sub>{casos}</sub> = {1 - p_negras:.4f}</div>",
                hint="Pulsa para revelar el cálculo"
            )

        if accordion("open_p1", "U_B", "(B) Cucharas engañosas"):
            st.markdown(
                "<div class='content-box'>Tienes un vaso de agua y un vaso de aceite. Coges una cucharada "
                "del de agua y la echas en el de aceite; agitas bien. Luego coges una cucharada de esa "
                "mezcla y la devuelves al vaso de agua. ¿Dónde es mayor el ratio de intruso: aceite en el "
                "agua, o agua en el aceite?<br><br><i>Piénsalo antes de mirar la respuesta.</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Son <b>exactamente iguales</b>. Como el volumen final de cada vaso vuelve a ser el de "
                "partida, todo el aceite que falta en su vaso ha sido reemplazado por agua, y viceversa: "
                "la cantidad de agua en el aceite es igual a la de aceite en el agua."
            )

        if accordion("open_p1", "U_C", "(C) Más que estudiar, opositar"):
            st.markdown(
                "<div class='content-box'>En unas oposiciones hay 90 temas. En el examen se sortean 5 al "
                "azar y debes desarrollar 1 de ellos. ¿Cuántos temas necesitas llevar preparados para "
                "asegurarte <b>siempre</b> un 10 (es decir, que al menos uno de los 5 sorteados lo tengas "
                "estudiado)?<br><br><i>Piensa en el peor caso posible.</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "En el peor caso, los 5 temas sorteados serían justo de los que no llevas. Para que eso "
                "sea imposible, los no estudiados deben ser como mucho 4: 90 &minus; 4 = <b>86 temas</b>. "
                "Con 86 preparados, cualquier grupo de 5 contiene al menos uno tuyo."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Las urnas, paso a paso</div>", unsafe_allow_html=True)

        total_rest = w_balls + 3
        casos = comb(total_rest, 3)
        p_negras = 1 / casos
        p_blanca = 1 - p_negras

        u1, u2 = st.columns(2)
        with u1:
            st.markdown("<div class='urn-caption'>Urna inicial</div>", unsafe_allow_html=True)
            st.markdown(draw_urn(w_balls, 4, dark, seed=42), unsafe_allow_html=True)
        with u2:
            st.markdown("<div class='urn-caption'>Tras sacar una negra</div>", unsafe_allow_html=True)
            st.markdown(draw_urn(w_balls, 3, dark, seed=7), unsafe_allow_html=True)

        st.markdown(
            f"<div class='comment-box'>Con W = {w_balls}: quedan {total_rest} bolas y hay "
            f"C({total_rest}, 3) = {casos} formas de elegir 3. Solo una de ellas es \"todas negras\".</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='result-badge'>P(al menos 1 blanca) &asymp; {p_blanca*100:.2f}%</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='footer-bar'>¿Qué le ocurre a la probabilidad cuando aumentas el número de bolas "
            "blancas W? ¿Tiende a algo?</div>",
            unsafe_allow_html=True
        )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Pruébalo tú mismo: cambia el "
                    "<u>número de personas n</u></div>", unsafe_allow_html=True)
        n_people = st.slider("Número de personas (n)", 2, 100, 23, key="slider_n_bday",
                             label_visibility="collapsed")

        st.markdown(
            "<div class='statement-box'><b>La paradoja del cumpleaños</b><br><br>"
            "En un grupo de tan solo 23 personas la probabilidad de que al menos dos cumplan años el "
            "mismo día ya supera el 50%. Antes de calcular nada: <b>¿cuántas personas crees tú que harían "
            "falta?</b> Anota tu estimación y compruébala con el deslizador.</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p2", "D_A", "(A) Pasando la pelota en voleibol"):
            st.markdown(
                "<div class='content-box'>Imagina 5 jugadores que se pasan la pelota: cada <b>pareja</b> "
                "es una oportunidad de coincidencia, y hay más parejas de las que parece. Calculémoslo "
                "explícitamente para n = 5. La probabilidad de que los 5 cumplan en días distintos "
                "es:<br><br><i>Trata de escribirla antes de revelarla.</i></div>",
                unsafe_allow_html=True
            )
            p5 = probability_all_different(5)
            spoiler(
                "<div class='formula-box'>P(distintos) = "
                "<sup>365·364·363·362·361</sup>&frasl;<sub>365<sup>5</sup></sub> = "
                f"{p5:.4f}</div>"
                f"Luego P(coincidencia) = 1 &minus; {p5:.4f} = <b>{1-p5:.4f}</b>, "
                f"y hay C(5,2) = {comb(5,2)} parejas posibles."
            )

        if accordion("open_p2", "D_B", "(B) El caso general de la clase"):
            st.markdown(
                "<div class='content-box'>Para n personas, los casos posibles son 365<sup>n</sup> "
                "(variaciones con repetición) y los favorables a que nadie coincida son "
                "365·364·&hellip;·(365&minus;n+1) (variaciones ordinarias). El gráfico de la derecha "
                "muestra cómo se dispara la probabilidad.<br><br><i>Trata de escribir la fórmula "
                "general.</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<div class='formula-box'>P(coinciden) = 1 &minus; "
                "<sup>365 · 364 · &hellip; · (365&minus;n+1)</sup>&frasl;<sub>365<sup>n</sup></sub></div>"
                "El crecimiento tan rápido se debe a que con n personas hay C(n,2) = n(n&minus;1)/2 "
                "parejas, no n."
            )

        if accordion("open_p2", "D_C", "(C) Se nos va de las manos"):
            st.markdown(
                "<div class='content-box'>Puedes comprobar este sorprendente resultado en clase usando "
                "solo tus manos. Con la <b>mano derecha en binario</b> codifica el día del mes (dedo "
                "arriba = 1, dedo abajo = 0: con 5 dedos llegas hasta 31). Con la <b>mano izquierda</b> "
                "usa las falanges para señalar el mes. Que cada persona muestre su fecha a la vez y buscad "
                "coincidencias: casi siempre aparece alguna. Eso sí, ¡cuidado con enseñar el día "
                "<i>may the force</i> (4 de mayo)!</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Cómo evoluciona la probabilidad</div>",
                    unsafe_allow_html=True)

        p_diff = probability_all_different(n_people)
        p_coin = 1 - p_diff
        parejas = comb(n_people, 2)

        st.markdown(
            f"<div class='result-badge'>Con {n_people} personas: P(coincidencia) = {p_coin*100:.2f}%</div>",
            unsafe_allow_html=True
        )
        streamlit_bokeh(birthday_chart(n_people, dark), use_container_width=True)
        st.markdown(
            f"<div class='footer-bar'>Hay {fmt(parejas)} parejas posibles entre {n_people} personas. "
            f"Las líneas marcan el 50% y las 23 personas.</div>",
            unsafe_allow_html=True
        )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Pruébalo tú mismo: ajusta las "
                    "<u>monedas y el umbral</u></div>", unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        p1 = cs1.slider("Moneda 1 — P(cara)", 0.0, 1.0, 0.4, 0.05, key="slider_p1")
        p2 = cs2.slider("Moneda 2 — P(cara)", 0.0, 1.0, 0.7, 0.05, key="slider_p2")
        cs3, cs4 = st.columns(2)
        n_lanz = cs3.slider("Nº de lanzamientos (n)", 10, 200, 100, 10, key="slider_nlanz")
        umbral = cs4.slider("Más del X% de caras", 10, 90, 60, 5, key="slider_umbral")

        p_ok = 1 - (1 - p1) * (1 - p2)
        kmin = int((umbral / 100) * n_lanz) + 1

        st.markdown(
            "<div class='statement-box'><b>Monedas cargadas</b><br><br>"
            "Dos monedas parecen idénticas, pero están trucadas: una da cara con probabilidad 0.4 y la "
            "otra con 0.7. Se lanzan a la vez 100 veces y contamos como \"éxito\" que salga <b>al menos "
            "una cara</b>. ¿Cuál es la probabilidad de obtener éxito en más del 60% de los "
            "lanzamientos?</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p3", "C_A", "(A) Planteamiento y fórmula"):
            st.markdown(
                "<div class='content-box'>Sea X el número de éxitos en n = 100 lanzamientos "
                "independientes. X sigue una distribución <b>binomial</b> B(n, p), donde p es la "
                "probabilidad de éxito en un lanzamiento. Como éxito = \"al menos una cara\", p = 1 &minus; "
                "P(las dos cruces).<br><br><i>Trata de escribir p y la probabilidad pedida.</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<div class='formula-box'>p = 1 &minus; (0.6 &middot; 0.3) = 0.82</div>"
                "<div class='formula-box'>P(X &gt; 60) = &sum;<sub>k=61</sub><sup>100</sup> "
                "( 100 sobre k ) 0.82<sup>k</sup> · 0.18<sup>100&minus;k</sup></div>",
                hint="Pulsa para revelar p y la fórmula"
            )

        if accordion("open_p3", "C_B", "(B) La isla desierta"):
            st.markdown(
                "<div class='content-box'>Pablo y Adriana están en una isla desierta y solo tienen una "
                "moneda gastada que favorece las caras. ¿Cómo decidir de forma justa sin conocer su "
                "sesgo? El truco (de von Neumann): lanzarla <b>dos veces</b>. Se descartan CARA-CARA y "
                "CRUZ-CRUZ; si sale CARA-CRUZ gana Pablo y si sale CRUZ-CARA gana "
                "Adriana.<br><br><i>¿Por qué es justo aunque la moneda esté trucada?</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<div class='formula-box'>P(C,X) = p(1&minus;p) = (1&minus;p)p = P(X,C)</div>"
                "El orden de los factores no altera el producto: ambas secuencias tienen exactamente la "
                "misma probabilidad, sea cual sea el valor desconocido de p. ¡Moneda imperfecta, decisión "
                "perfecta!"
            )

        if accordion("open_p3", "C_C", "(C) De la binomial a la campana"):
            st.markdown(
                "<div class='content-box'>Cuando n es grande, calcular la suma binomial a mano es "
                "inviable. El teorema de De Moivre-Laplace nos dice que la binomial se parece cada vez más "
                "a una <b>campana de Gauss</b> de media &mu; = np y desviación &sigma; = &radic;(np(1&minus;p)). "
                "Fíjate en el histograma de la derecha: su silueta es ya casi una "
                "normal.<br><br><i>Trata de escribir &mu; y &sigma;.</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<div class='formula-box'>&mu; = n·p &nbsp;&nbsp; "
                "&sigma; = &radic;(n·p·(1&minus;p))</div>"
                "Así P(X &gt; k) se aproxima con el área de la cola de esa campana."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Distribución de X = nº de éxitos</div>",
                    unsafe_allow_html=True)

        p_exact = float(stats.binom.sf(kmin - 1, n_lanz, p_ok))
        mu = n_lanz * p_ok
        sigma = (n_lanz * p_ok * (1 - p_ok)) ** 0.5

        st.markdown(
            f"<div class='comment-box'>p = 1 &minus; ({1-p1:.2f}·{1-p2:.2f}) = <b>{p_ok:.4f}</b>. "
            f"Buscamos P(X &gt; {kmin-1}) en B({n_lanz}, {p_ok:.2f}). "
            f"&mu; = {mu:.1f}, &sigma; = {sigma:.2f}.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='result-badge'>P(X &gt; {kmin-1}) &asymp; {p_exact*100:.2f}%</div>",
            unsafe_allow_html=True
        )
        streamlit_bokeh(binomial_chart(n_lanz, p_ok, kmin, dark), use_container_width=True)
        st.markdown(
            f"<div class='footer-bar'>En rojo, la cola k &ge; {kmin} que suma la probabilidad pedida. "
            f"¿Cómo cambia al mover el umbral o el sesgo de las monedas?</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    dark = detect_dark_theme()

    c_home, c_title = st.columns([1, 11], gap="small")
    with c_home:
        if st.button("⌂", key="home_btn", use_container_width=True, help="Volver al inicio"):
            try:
                st.switch_page("home.py")
            except Exception:
                st.toast("Ejecuta home.py para ver el índice")
    with c_title:
        st.markdown("<div class='top-bar-title'>C1VIC D4TA · El arte de contar</div>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("TEO", "Introducción"),
        ("P1", "(I) Urnas de Pólya"),
        ("P2", "(II) La paradoja del cumpleaños"),
        ("P3", "(III) Monedas cargadas"),
    ]
    nav_cols = st.columns(4)
    for col, (page_id, label) in zip(nav_cols, nav):
        is_active = current_page == page_id
        if col.button(label, use_container_width=True,
                      type="primary" if is_active else "secondary",
                      key=f"nav_{page_id}"):
            st.session_state["page"] = page_id
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if current_page == "TEO":
        render_theory(dark)
    elif current_page == "P1":
        render_problem_1(dark)
    elif current_page == "P2":
        render_problem_2(dark)
    elif current_page == "P3":
        render_problem_3(dark)

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
