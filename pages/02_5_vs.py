import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · Probabilidad condicionada",
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
.metric-box {{
    font-size: clamp(15px, 1.9vw, 22px); color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 12px; box-shadow: var(--shadow);
}}
.metric-a {{ border-color: {BLUE_LINE};  color: {BLUE_LINE};  font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE}; color: {GREEN_LINE}; font-weight: 700; }}

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

[data-testid="stRadio"] > label p {{ font-size: clamp(14px, 1.8vw, 21px) !important; font-weight: 700 !important; color: var(--app-fg) !important; }}
[data-testid="stRadio"] div[role="radiogroup"] label p {{ font-size: clamp(14px, 1.7vw, 20px) !important; color: var(--app-fg) !important; }}

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
# 2. ESTADO Y AUXILIARES
# =============================================================================

def init_session_state():
    defaults = {"page": "INTRO", "open_step": "P1_A"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def accordion_step(step_id: str, title: str) -> bool:
    is_open = st.session_state["open_step"] == step_id
    if st.button(title, key=f"acc_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state["open_step"] = step_id if not is_open else None
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

def formula_hidden(formula: str, hint: str = "Pulsa para revelar su expresión matemática"):
    spoiler(f"<div class='formula-box'>{formula}</div>", hint=hint)

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

# =============================================================================
# 3. GRÁFICAS INTERACTIVAS
# =============================================================================

SEASONS = ["Primavera", "Verano", "Otoño", "Invierno"]
BASE_RAIN = [0.50, 0.15, 0.60, 0.70]   # fracción base de días de lluvia por estación

def seasons_chart(ps, sel_idx, pa, dark):
    th = chart_theme(dark)
    p = figure(x_range=SEASONS, height=340, sizing_mode="stretch_width",
               toolbar_location=None, y_range=(0, 1.0),
               y_axis_label="fracción de días")
    p.vbar(x=SEASONS, top=ps, width=0.8, fill_color=BLUE_LINE, fill_alpha=0.80, line_color=None)
    p.vbar(x=SEASONS, bottom=ps, top=1.0, width=0.8, fill_color=th["line"],
           fill_alpha=0.30, line_color=None)
    p.vbar(x=[SEASONS[sel_idx]], top=1.0, width=0.84, fill_alpha=0,
           line_color=UBU_RED, line_width=4)
    p.add_layout(Span(location=pa, dimension="width", line_color=GREEN_LINE,
                      line_dash="dashed", line_width=2))
    return style_axes(p, th)

def linda_bars(p_fc, dark):
    th = chart_theme(dark)
    cats = ["Cajeras", "Cajeras y feministas"]
    vals = [1.0, p_fc]
    p = figure(x_range=cats, height=320, sizing_mode="stretch_width",
               toolbar_location=None, y_range=(0, 1.05),
               y_axis_label="proporción respecto a las cajeras")
    p.vbar(x=cats, top=vals, width=0.6, fill_color=[BLUE_LINE, UBU_RED], line_color=None)
    return style_axes(p, th)

def ducks_curve(n_cur, dark):
    th = chart_theme(dark)
    ns = list(range(2, 51))
    frac = [1 - (1 - 1 / k) ** k for k in ns]
    p = figure(height=320, sizing_mode="stretch_width",
               x_axis_label="nº de patos = nº de cazadores",
               y_axis_label="fracción de patos cazados",
               toolbar_location=None, x_range=(2, 50), y_range=(0, 1.0))
    p.line(ns, frac, line_width=5, color=BLUE_LINE)
    p.add_layout(Span(location=1 - 1 / np.e, dimension="width", line_color=GREEN_LINE,
                      line_dash="dashed", line_width=2))
    cur = 1 - (1 - 1 / n_cur) ** n_cur
    p.scatter([n_cur], [cur], size=16, marker="circle", color=UBU_RED,
              line_color="white", line_width=2)
    return style_axes(p, th)

def medicine_bars(p_epos, dark):
    th = chart_theme(dark)
    cats = ["P(+ | enfermo)", "P(enfermo | +)"]
    vals = [1.0, p_epos]
    p = figure(x_range=cats, height=320, sizing_mode="stretch_width",
               toolbar_location=None, y_range=(0, 1.05), y_axis_label="probabilidad")
    p.vbar(x=cats, top=vals, width=0.55, fill_color=[BLUE_LINE, UBU_RED], line_color=None)
    return style_axes(p, th)

# =============================================================================
# 4. PÁGINAS
# =============================================================================

def render_intro(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>¿Qué es la probabilidad condicionada?</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>La probabilidad condicionada es la posibilidad de que ocurra un "
            "suceso A <b>sabiendo que ya ha ocurrido</b> otro suceso B. Su origen se remonta al siglo "
            "XVIII, cuando Thomas Bayes formuló su famoso teorema para calcular probabilidades inversas, "
            "y fue formalizada poco después por Pierre-Simon Laplace. La idea clave es que la información "
            "previa reduce el espacio de posibilidades: ya no miramos todo &Omega;, solo la parte "
            "compatible con B.<br><br><i>En palabras: la probabilidad de A dado B es la parte de B que "
            "también está en A, dividida entre todo B. Prueba a escribirlo.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden(
            "P(A | B) = <sup>P(A &cap; B)</sup>&frasl;<sub>P(B)</sub>",
            hint="Pulsa para revelar la definición"
        )

        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Linda la cajera</b><br><i>Descubre por qué el 85% de la gente se equivoca con la "
            "falacia de la conjunción.</i><br><br>"
            "<b>II. La caza de gamusinos... y de patos</b><br><i>Cómo la información previa cambia una "
            "probabilidad de 0 a 1, y cuántos patos cenan los cazadores.</i><br><br>"
            "<b>III. El falso positivo médico</b><br><i>Por qué dar positivo no significa estar "
            "enfermo, y cómo esto anticipa el Teorema de Bayes.</i>"
            "</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Pruébalo: &Omega; partido en 4 estaciones</div>",
                    unsafe_allow_html=True)

        sel = st.radio("¿Qué estación ha ocurrido? (suceso B)", SEASONS,
                       horizontal=True, key="season_sel")
        factor = st.slider("Factor de humedad del año", 0.4, 1.4, 1.0, 0.1, key="humedad")

        ps = [min(1.0, b * factor) for b in BASE_RAIN]
        sel_idx = SEASONS.index(sel)
        p_ab = ps[sel_idx]
        p_a = sum(ps) / 4

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>P(lluvia | {sel}) = {p_ab:.2f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>P(lluvia) = {p_a:.2f}</div>",
                        unsafe_allow_html=True)

        streamlit_bokeh(seasons_chart(ps, sel_idx, p_a, dark), use_container_width=True)
        st.markdown(
            "<div class='footer-bar'>Caso práctico: A = \"día de lluvia\" y B = estación del año. "
            "La probabilidad de lluvia cambia según la estación (azul = A dentro de cada B); la línea "
            "verde marca P(A) global. Saber la estación lo cambia todo.</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Linda la cajera</b><br><br>"
            "El problema de \"Linda la cajera\", diseñado por los psicólogos Daniel Kahneman y Amos "
            "Tversky en 1983, es uno de los recursos más célebres para introducir la probabilidad de la "
            "intersección y la condicionada.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "(A) Conocer a Linda"):
            st.markdown(
                "<div class='content-box'>Linda tiene 31 años, es soltera, sincera y muy brillante. Se "
                "especializó en Filosofía y de estudiante le preocupaban la discriminación y la justicia "
                "social.<br><br><b>¿Qué te parece más probable?</b><br>&bull; Opción A: Linda es cajera "
                "de banco.<br>&bull; Opción B: Linda es cajera de banco <b>y</b> activista "
                "feminista.</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "En los experimentos originales, alrededor del <b>85%</b> de las personas eligió la "
                "opción B. Pero, ¿es eso matemáticamente posible?"
            )

        if accordion_step("P1_B", "(B) El error: la falacia de la conjunción"):
            st.markdown(
                "<div class='content-box'>Sea C = \"ser cajera\" y F = \"ser feminista\". Las cajeras "
                "que además son feministas (C &cap; F) forman un <b>subconjunto</b> de todas las "
                "cajeras (C). Por tanto la intersección nunca puede ser más probable que el "
                "todo.<br><br><i>Trata de escribir la desigualdad.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden("P(C &cap; F) &le; P(C)", hint="Pulsa para revelar la desigualdad")

        if accordion_step("P1_C", "(C) Por qué nos engaña el cerebro"):
            st.markdown(
                "<div class='content-box'>El cerebro no calcula la intersección P(C &cap; F); en su "
                "lugar evalúa sin darse cuenta una <b>condicionada</b>: P(F | C), lo bien que \"encaja\" "
                "el perfil. Como P(C &cap; F) = P(F | C)·P(C) y P(F | C) &le; 1, el resultado siempre es "
                "menor o igual que P(C).<br><br><b>Moraleja:</b> confundimos condicionadas con "
                "intersecciones.</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "P(F | C) = <sup>P(C &cap; F)</sup>&frasl;<sub>P(C)</sub>. Como es un número entre 0 y "
                "1, al multiplicarlo por P(C) nunca puede aumentar la probabilidad."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>El experimento original, en una gráfica</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='comment-box'>Kahneman y Tversky (1983) pidieron ordenar por probabilidad varios "
            "perfiles de Linda. Muchos colocaron \"cajera y feminista\" por encima de \"cajera\", algo "
            "imposible: mueve el deslizador y verás que la barra roja nunca supera a la azul.</div>",
            unsafe_allow_html=True
        )
        p_fc = st.slider("De cada 100 cajeras, ¿cuántas crees que son feministas? (P(F | C), %)",
                         0, 100, 60, 5, key="linda_pfc") / 100.0
        streamlit_bokeh(linda_bars(p_fc, dark), use_container_width=True)
        st.markdown(
            f"<div class='footer-bar'>P(cajera y feminista) = P(F | C)·P(cajera) = {p_fc:.2f}·P(cajera) "
            f"&le; P(cajera). La conjunción nunca gana.</div>",
            unsafe_allow_html=True
        )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>La caza de gamusinos</b><br><br>"
            "El gamusino, ese animal imaginario con el que en España se gasta la broma de mandar de "
            "noche al bosque con un saco a los excursionistas novatos, sirve para explicar la "
            "probabilidad condicionada de forma rápida y muy intuitiva.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "(A) La escena"):
            st.markdown(
                "<div class='content-box'>Llevas de acampada nocturna a 10 amigos. 6 son "
                "<b>veteranos (V)</b>, que ya conocen la broma, y 4 son <b>novatos (N)</b>, que se creen "
                "la historia. Repartes un saco a cada uno y los dejas esperando en la "
                "oscuridad.<br><br>Definimos el suceso C = \"el amigo cree de verdad que va a cazar un "
                "gamusino\".</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "(B) Las probabilidades"):
            st.markdown(
                "<div class='content-box'>Si eliges a un amigo al azar, ¿cuál es P(C)? Depende por "
                "completo de la información previa que tenga.<br><br>&bull; Sabiendo que es veterano: "
                "P(C | V) = ?<br>&bull; Sabiendo que es novato: P(C | N) = ?<br><br><i>Piénsalo antes de "
                "revelarlo.</i></div>",
                unsafe_allow_html=True
            )
            spoiler("P(C | V) = 0 (sabe que es una broma) &nbsp; y &nbsp; P(C | N) = 1 (se la cree).")

        if accordion_step("P2_C", "(C) Ahora son patos"):
            st.markdown(
                "<div class='content-box'>Cambiemos de escena: hay <b>10 patos</b> en un lago y "
                "<b>10 cazadores</b>. De repente se oye \"¡fuego!\" y cada cazador dispara al azar a un "
                "pato, con puntería perfecta (dos cazadores pueden elegir el mismo pato). ¿Cuántos patos "
                "esperas que acaben cenando los cazadores?<br><br><i>Usa el deslizador de la derecha y "
                "trata de deducir la fórmula.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "E[patos cazados] = n &middot; (1 &minus; (1 &minus; <sup>1</sup>&frasl;<sub>n</sub>)"
                "<sup>n</sup>) &nbsp;&xrarr;&nbsp; n(1 &minus; <sup>1</sup>&frasl;<sub>e</sub>)",
                hint="Pulsa para revelar la fórmula"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Patos y cazadores</div>", unsafe_allow_html=True)

        n = st.slider("Número de patos = número de cazadores", 2, 50, 10, 1, key="n_patos")
        frac = 1 - (1 - 1 / n) ** n
        esperados = n * frac
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>Patos cazados &asymp; {esperados:.1f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Fracción &asymp; {frac*100:.1f}%</div>",
                        unsafe_allow_html=True)
        streamlit_bokeh(ducks_curve(n, dark), use_container_width=True)
        st.markdown(
            f"<div class='footer-bar'>Con {n} patos, cenan unos {esperados:.1f}. Al crecer n, la "
            f"fracción cazada tiende a 1 &minus; 1/e &asymp; 63.2% (línea verde): ¡otra vez el número e!</div>",
            unsafe_allow_html=True
        )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>El falso positivo médico</b><br><br>"
            "El ejemplo clásico de medicina sirve para desmontar un error muy común: confundir "
            "P(A | B) con P(B | A).</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "(A) El escenario"):
            st.markdown(
                "<div class='content-box'>Una enfermedad muy rara la tiene 1 de cada 1000 personas. El "
                "test es excelente: solo falla el 5% de las veces dando un falso positivo (y detecta "
                "siempre al enfermo).<br><br><i>Si analizas a 1000 personas, ¿cuántos positivos "
                "esperas?</i></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "El único enfermo da positivo. De los 999 sanos, el 5% da positivo por error &asymp; 50. "
                "<b>Total de positivos &asymp; 51</b>."
            )

        if accordion_step("P3_B", "(B) La pregunta tramposa"):
            st.markdown(
                "<div class='content-box'>Es fácil confundir la fiabilidad del test con la probabilidad "
                "real de estar enfermo. ¿Un positivo significa que tienes un 95% de probabilidad de "
                "estar enfermo?</div>",
                unsafe_allow_html=True
            )
            spoiler("¡Falso! No es el 95%, ni de lejos.")

        if accordion_step("P3_C", "(C) La respuesta contraintuitiva"):
            st.markdown(
                "<div class='content-box'>La probabilidad de estar enfermo <b>sabiendo</b> que has dado "
                "positivo es la fracción de enfermos entre todos los positivos.<br><br><i>Compárala con "
                "P(+ | enfermo).</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(E | +) = <sup>1</sup>&frasl;<sub>51</sub> &asymp; 2% &nbsp;&nbsp; frente a &nbsp;&nbsp; "
                "P(+ | E) = 1",
                hint="Pulsa para revelar los dos valores"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>P(enfermo | +) frente a P(+ | enfermo)</div>",
                    unsafe_allow_html=True)

        prev = st.slider("La enfermedad la tiene 1 de cada N personas", 100, 5000, 1000, 100,
                         key="prevalencia")
        fpr = st.slider("Falsos positivos del test (%)", 1, 20, 5, 1, key="fpr") / 100.0
        p_e = 1 / prev
        p_epos = p_e / (p_e + fpr * (1 - p_e))   # sensibilidad = 1

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>P(+ | enfermo) = 100%</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>P(enfermo | +) = {p_epos*100:.1f}%</div>",
                        unsafe_allow_html=True)
        streamlit_bokeh(medicine_bars(p_epos, dark), use_container_width=True)
        st.markdown(
            "<div class='footer-bar'>Ambas condicionadas son muy distintas porque la enfermedad es rara. "
            "Invertir P(+ | E) para obtener P(E | +) es justo lo que resolverá el <b>Teorema de "
            "Bayes</b>.</div>",
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
        st.markdown("<div class='top-bar-title'>C1VIC D4TA · Probabilidad condicionada</div>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("INTRO", "Introducción", None),
        ("P1", "(I) Linda la cajera", "P1_A"),
        ("P2", "(II) Caza de gamusinos", "P2_A"),
        ("P3", "(III) Falso positivo", "P3_A"),
    ]
    nav_cols = st.columns(4)
    for col, (page_id, label, first_step) in zip(nav_cols, nav):
        is_active = current_page == page_id
        if col.button(label, use_container_width=True,
                      type="primary" if is_active else "secondary",
                      key=f"nav_{page_id}"):
            update = {"page": page_id}
            if first_step:
                update["open_step"] = first_step
            st.session_state.update(update)
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if current_page == "INTRO":
        render_intro(dark)
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
