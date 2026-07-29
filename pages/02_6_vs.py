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
    page_title="C1VIC D4TA · Independencia y probabilidad total",
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
    font-size: clamp(16px, 2vw, 24px); color: var(--spoiler-fg);
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
    defaults = {"page": "INTRO", "open_step": "P3_A"}
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

def independence_square(pA, pB, dark):
    th = chart_theme(dark)
    p = figure(height=380, sizing_mode="stretch_width", x_range=(0, 1), y_range=(0, 1),
               match_aspect=True, toolbar_location=None)
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = th["axis"]
    p.grid.visible = False
    p.axis.visible = False
    # A = franja vertical ; B = franja horizontal ; intersección = rectángulo
    p.quad(left=0, right=pA, bottom=0, top=1, fill_color=BLUE_LINE, fill_alpha=0.18, line_color=None)
    p.quad(left=0, right=1, bottom=0, top=pB, fill_color=GREEN_LINE, fill_alpha=0.18, line_color=None)
    p.quad(left=0, right=pA, bottom=0, top=pB, fill_color=UBU_RED, fill_alpha=0.55, line_color=None)
    p.line([pA, pA], [0, 1], line_color=BLUE_LINE, line_width=2)
    p.line([0, 1], [pB, pB], line_color=GREEN_LINE, line_width=2)
    p.text([pA / 2], [0.93], text=["A"], text_color=BLUE_LINE, text_font_size="18px", text_align="center")
    p.text([0.94], [pB / 2], text=["B"], text_color=GREEN_LINE, text_font_size="18px", text_align="center")
    p.text([pA / 2], [pB / 2], text=["A∩B"], text_color="#ffffff", text_font_size="15px",
           text_align="center", text_baseline="middle")
    return p

# Verosimilitudes P(rentabilidad | banco)
LIK = {
    "A": {"7%": 0.25, "6%": 0.50, "8%": 0.25},
    "B": {"7%": 0.50, "6%": 0.20, "8%": 0.30},
    "C": {"7%": 0.40, "6%": 0.40, "8%": 0.20},
}

def posteriors(ret):
    prior = 1 / 3
    num = {b: prior * LIK[b][ret] for b in "ABC"}
    tot = sum(num.values())
    return {b: num[b] / tot for b in "ABC"}, tot

def bayes_bars(ret, dark):
    th = chart_theme(dark)
    post, _ = posteriors(ret)
    cats = ["Banco A", "Banco B", "Banco C"]
    vals = [post["A"], post["B"], post["C"]]
    p = figure(x_range=cats, height=330, sizing_mode="stretch_width", toolbar_location=None,
               y_range=(0, 0.75), y_axis_label="P(banco | rentabilidad)")
    p.vbar(x=cats, top=vals, width=0.6,
           fill_color=[UBU_RED, BLUE_LINE, GREEN_LINE], line_color=None)
    p.add_layout(Span(location=1 / 3, dimension="width", line_color=th["fg"],
                      line_dash="dashed", line_width=2))
    return style_axes(p, th)

def dice_grid(case, dark):
    th = chart_theme(dark)
    xs, ys, colors = [], [], []
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            inA = d1 % 2 == 0
            inB = d2 % 2 == 0
            inC = (d1 + d2) % 2 == 0
            if case == "AB":
                hit = inA and inB
            elif case == "AC":
                hit = inA and inC
            else:
                hit = inA and inB and inC
            xs.append(d1); ys.append(d2)
            colors.append(UBU_RED if hit else th["line"])
    p = figure(height=360, sizing_mode="stretch_width", x_range=(0.5, 6.5), y_range=(0.5, 6.5),
               match_aspect=True, toolbar_location=None,
               x_axis_label="primer dado", y_axis_label="segundo dado")
    p.rect(x=xs, y=ys, width=0.92, height=0.92, fill_color=colors, fill_alpha=0.85,
           line_color=th["axis"], line_width=1)
    p.xaxis.ticker = list(range(1, 7))
    p.yaxis.ticker = list(range(1, 7))
    return style_axes(p, th)

# =============================================================================
# 4. PÁGINAS
# =============================================================================

def render_intro(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Independencia y probabilidad total</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><b>Sucesos independientes.</b> Dos sucesos A y B son "
            "independientes si saber que ocurre uno no cambia la probabilidad del otro. Eso equivale a "
            "que la probabilidad de que ocurran ambos sea el producto de sus "
            "probabilidades.<br><br><i>Trata de escribirlo.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden("P(A &cap; B) = P(A) &middot; P(B)", hint="Pulsa para revelar la definición")

        st.markdown(
            "<div class='content-box'><b>Teorema de la probabilidad total.</b> Si "
            "{B<sub>1</sub>, B<sub>2</sub>, &hellip;} es una partición de &Omega; (trozos disjuntos que "
            "lo cubren todo), la probabilidad de cualquier suceso A se obtiene sumando su contribución en "
            "cada trozo.<br><br><i>Trata de escribir la fórmula.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden(
            "P(A) = &sum;<sub>i</sub> P(A | B<sub>i</sub>) &middot; P(B<sub>i</sub>)",
            hint="Pulsa para revelar la fórmula"
        )

        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Una demostración</b><br><i>Fuerza algebraicamente la independencia de dos "
            "sucesos.</i><br><br>"
            "<b>II. El Teorema de Bayes</b><br><i>Tres bancos, un fondo al azar y una rentabilidad "
            "observada.</i><br><br>"
            "<b>III. Dos dados</b><br><i>Independencia dos a dos frente a independencia mutua.</i>"
            "</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Pruébalo: la independencia como áreas</div>",
                    unsafe_allow_html=True)
        pA = st.slider("P(A)", 0.05, 1.0, 0.5, 0.05, key="pA")
        pB = st.slider("P(B)", 0.05, 1.0, 0.4, 0.05, key="pB")

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>P(A)·P(B) = {pA*pB:.3f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Área roja = {pA*pB:.3f}</div>",
                        unsafe_allow_html=True)
        streamlit_bokeh(independence_square(pA, pB, dark), use_container_width=True)
        st.markdown(
            "<div class='footer-bar'>Si A y B son independientes, el rectángulo rojo (A &cap; B) tiene "
            "exactamente el área P(A)·P(B): el ancho por el alto de las dos franjas.</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Una demostración</b><br><br>"
            "En un espacio (&Omega;, &Ascr;, P), sean A, B y C sucesos con probabilidad positiva. Si se "
            "cumple que P(A|B) = P(A|B&cap;C)·P(C) + P(A|B&cap;C<sup>c</sup>)·P(C<sup>c</sup>) y además "
            "P(A|B&cap;C) &ne; P(A|B), demuestra que B y C son necesariamente "
            "independientes.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Sigue la demostración por etapas con el deslizador de la derecha: "
            "el texto explica cada paso y las fórmulas quedan ocultas para que intentes escribirlas "
            "primero.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box plain'>P(B &cap; C) = P(B)·P(C)</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Ese es el objetivo: llegar a esta igualdad, que es justo la "
            "definición de que B y C sean independientes.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>La demostración por etapas</div>", unsafe_allow_html=True)
        etapa = st.slider("Etapa de la demostración", 1, 3, 1, 1, key="dem_stage",
                          label_visibility="collapsed")

        if etapa == 1:
            st.markdown(
                "<div class='content-box'><b>Etapa 1 · Desarrollar los dos lados.</b><br>"
                "Aplicamos la definición de probabilidad condicionada a cada término del lado derecho, "
                "para que aparezcan las intersecciones triples.<br><br><i>Trata de escribirlo.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A|B) = <sup>P(A&cap;B&cap;C)</sup>&frasl;<sub>P(B&cap;C)</sub>·P(C) + "
                "<sup>P(A&cap;B&cap;C<sup>c</sup>)</sup>&frasl;<sub>P(B&cap;C<sup>c</sup>)</sub>·P(C<sup>c</sup>)"
            )
            st.markdown(
                "<div class='content-box'>Y escribimos también el lado izquierdo como una única "
                "fracción, partiendo A&cap;B según C y su complementario (probabilidad "
                "total).<br><br><i>Trata de escribirlo.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A|B) = <sup>P(A&cap;B&cap;C) + P(A&cap;B&cap;C<sup>c</sup>)</sup>&frasl;<sub>P(B)</sub>"
            )
        elif etapa == 2:
            st.markdown(
                "<div class='content-box'><b>Etapa 2 · Igualar y factorizar.</b><br>"
                "Igualamos las dos expresiones de P(A|B), agrupamos por C y C<sup>c</sup> y, tras operar "
                "los denominadores comunes, todo se factoriza en un <b>producto igual a "
                "cero</b>.<br><br><i>Trata de escribir ese producto.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "[ P(B&cap;C) &minus; P(B)P(C) ] &middot; "
                "[ P(A|B&cap;C) &minus; P(A|B&cap;C<sup>c</sup>) ] = 0"
            )
        else:
            st.markdown(
                "<div class='content-box'><b>Etapa 3 · Conclusión.</b><br>"
                "Si un producto es cero, uno de los factores lo es. El segundo no puede anularse: si "
                "P(A|B&cap;C) = P(A|B&cap;C<sup>c</sup>), entonces P(A|B&cap;C) = P(A|B), contra la "
                "hipótesis. Luego se anula el primero.<br><br><i>Trata de escribir la "
                "conclusión.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(B&cap;C) &minus; P(B)P(C) = 0 &nbsp;&rArr;&nbsp; P(B&cap;C) = P(B)P(C) &nbsp; "
                "&#8718; &nbsp; (B y C independientes)",
                hint="Pulsa para revelar la conclusión"
            )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>El Teorema de Bayes: tres bancos</b><br><br>"
            "En una ciudad hay tres bancos, A, B y C, cada uno con un fondo de inversión. Según el banco, "
            "la rentabilidad del 7% se da con probabilidad 0.25 (A), 0.50 (B) o 0.40 (C). Se contrata al "
            "azar uno de los fondos y resulta una rentabilidad del 7%. ¿Cuál es la probabilidad de que "
            "fuera el banco A?</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "(A) Sucesos y datos"):
            st.markdown(
                "<div class='content-box'>La elección del banco es al azar, así que P(A) = P(B) = P(C) = "
                "1/3. Sea R<sub>7</sub> = \"obtener el 7%\". De la tabla: P(R<sub>7</sub>|A) = 0.25, "
                "P(R<sub>7</sub>|B) = 0.50, P(R<sub>7</sub>|C) = 0.40.<br><br>A priori, el banco B es el "
                "candidato más prometedor.</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "(B) Probabilidad total"):
            st.markdown(
                "<div class='content-box'>Sumamos la contribución de cada banco para obtener la "
                "probabilidad global de sacar un 7%.<br><br><i>Trata de escribirla.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(R<sub>7</sub>) = <sup>1</sup>&frasl;<sub>3</sub>(0.25 + 0.50 + 0.40) = "
                "<sup>1.15</sup>&frasl;<sub>3</sub> &asymp; 0.3833"
            )

        if accordion_step("P2_C", "(C) Teorema de Bayes"):
            st.markdown(
                "<div class='content-box'>Invertimos la condición para hallar la probabilidad a "
                "posteriori de que fuera el banco A, sabiendo que salió un 7%.<br><br><i>Trata de "
                "escribirlo.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A|R<sub>7</sub>) = "
                "<sup>P(A)·P(R<sub>7</sub>|A)</sup>&frasl;<sub>P(R<sub>7</sub>)</sub> = "
                "<sup>0.25</sup>&frasl;<sub>1.15</sub> = <sup>5</sup>&frasl;<sub>23</sub> &asymp; 0.2174",
                hint="Pulsa para revelar el resultado"
            )
            st.markdown(
                "<div class='content-box'>La probabilidad de A baja del 33.3% inicial al 21.7%: como A "
                "era el que menos favorecía el 7%, observarlo desvía la sospecha hacia los otros "
                "bancos.</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Probabilidades a posteriori</div>", unsafe_allow_html=True)
        ret = st.radio("Rentabilidad observada", ["7%", "6%", "8%"], horizontal=True, key="ret_obs")

        post, _ = posteriors(ret)
        m1, m2, m3 = st.columns(3)
        for col, b in zip((m1, m2, m3), "ABC"):
            with col:
                st.markdown(f"<div class='metric-box'>P({b}|R) = {post[b]*100:.1f}%</div>",
                            unsafe_allow_html=True)
        streamlit_bokeh(bayes_bars(ret, dark), use_container_width=True)
        st.markdown(
            "<div class='footer-bar'>La línea discontinua marca la probabilidad a priori (1/3). El "
            "Teorema de Bayes invierte la probabilidad: de P(rentabilidad | banco) a "
            "P(banco | rentabilidad).</div>",
            unsafe_allow_html=True
        )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Dos dados</b><br><br>"
            "Se lanzan dos dados no cargados. Definimos: A<sub>2</sub> = \"el primer dado es par\", "
            "B<sub>2</sub> = \"el segundo dado es par\" y C<sub>2</sub> = \"la suma es par\". El espacio "
            "muestral tiene 36 resultados equiprobables. ¿Qué sucesos son independientes?</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "(A) ¿A₂ y B₂ independientes?"):
            st.markdown(
                "<div class='content-box'>P(A<sub>2</sub>) = P(B<sub>2</sub>) = 1/2. La intersección "
                "(ambos pares) tiene 9 casos de 36.<br><br><i>Trata de compararlo con el "
                "producto.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A<sub>2</sub>&cap;B<sub>2</sub>) = <sup>9</sup>&frasl;<sub>36</sub> = "
                "<sup>1</sup>&frasl;<sub>4</sub> = P(A<sub>2</sub>)·P(B<sub>2</sub>) &nbsp; &rArr; SÍ",
                hint="Pulsa para revelar la respuesta"
            )

        if accordion_step("P3_B", "(B) ¿A₂ y C₂ independientes?"):
            st.markdown(
                "<div class='content-box'>P(C<sub>2</sub>) = 1/2 (par+par o impar+impar). La "
                "intersección con A<sub>2</sub> obliga al segundo dado a ser par: 9 casos de "
                "36.<br><br><i>Compáralo con el producto.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A<sub>2</sub>&cap;C<sub>2</sub>) = <sup>9</sup>&frasl;<sub>36</sub> = "
                "<sup>1</sup>&frasl;<sub>4</sub> = P(A<sub>2</sub>)·P(C<sub>2</sub>) &nbsp; &rArr; SÍ "
                "(aunque sorprenda)",
                hint="Pulsa para revelar la respuesta"
            )

        if accordion_step("P3_C", "(C) ¿A₂, B₂ y C₂ mutuamente independientes?"):
            st.markdown(
                "<div class='content-box'>Si el primer dado es par y el segundo es par, la suma es par "
                "forzosamente: la intersección triple son de nuevo esos 9 casos. Pero el producto de las "
                "tres probabilidades es 1/8.<br><br><i>Compáralos.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(A<sub>2</sub>&cap;B<sub>2</sub>&cap;C<sub>2</sub>) = <sup>1</sup>&frasl;<sub>4</sub> "
                "&ne; <sup>1</sup>&frasl;<sub>8</sub> = "
                "P(A<sub>2</sub>)·P(B<sub>2</sub>)·P(C<sub>2</sub>) &nbsp; &rArr; NO",
                hint="Pulsa para revelar la respuesta"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Los 36 resultados</div>", unsafe_allow_html=True)
        caso = st.radio("Sucesos a comparar",
                        ["A₂ ∩ B₂", "A₂ ∩ C₂", "A₂ ∩ B₂ ∩ C₂"],
                        horizontal=True, key="dice_case")
        case_map = {"A₂ ∩ B₂": "AB", "A₂ ∩ C₂": "AC", "A₂ ∩ B₂ ∩ C₂": "ABC"}
        case = case_map[caso]

        counts = {"AB": 9, "AC": 9, "ABC": 9}
        prods = {"AB": "1/4 = P(A₂)·P(B₂)", "AC": "1/4 = P(A₂)·P(C₂)",
                 "ABC": "1/8 = P(A₂)·P(B₂)·P(C₂)"}
        veredicto = {"AB": "independientes", "AC": "independientes",
                     "ABC": "NO independientes"}
        st.markdown(
            f"<div class='result-badge'>{caso}: {counts[case]}/36 = "
            f"{counts[case]/36:.3f} &nbsp;|&nbsp; producto = {prods[case]}</div>",
            unsafe_allow_html=True
        )
        streamlit_bokeh(dice_grid(case, dark), use_container_width=True)
        st.markdown(
            f"<div class='footer-bar'>En rojo, los casos favorables ({veredicto[case]}). La "
            f"independencia dos a dos no garantiza la independencia mutua.</div>",
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
        st.markdown("<div class='top-bar-title'>C1VIC D4TA · Independencia y probabilidad total</div>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("INTRO", "Introducción", None),
        ("P1", "(I) Una demostración", None),
        ("P2", "(II) Teorema de Bayes", "P2_A"),
        ("P3", "(III) Dos dados", "P3_A"),
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
