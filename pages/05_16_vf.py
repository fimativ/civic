import streamlit as st
import numpy as np
from fractions import Fraction
from bokeh.plotting import figure
from bokeh.models import (ColumnDataSource, LinearColorMapper,
                          HoverTool, Span, BoxAnnotation)
from scipy.stats import norm
import uuid
from streamlit_bokeh import streamlit_bokeh

# numpy >= 2 renombra trapz -> trapezoid; mantenemos compatibilidad
_trapz = getattr(np, "trapezoid", None) or np.trapz

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Vectores Aleatorios")

# Colores
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"
ORANGE_ACCENT  = "#E67E22"

LIGHT_VARS = """
    --app-bg: #fbfbfb;
    --app-fg: #141414;
    --panel-left-bg: #fffde7;
    --panel-right-bg: #f0eff4;
    --box-bg: #ffffff;
    --box-fg: #1a1a1a;
    --spoiler-bg: #e8eeff;
    --spoiler-fg: #4169E1;
    --metric-border: #d0d0d0;
    --muted-fg: #666666;
    --hole-bg: #fdecec;
    --hole-fg: #c62828;
    --ok-bg: #e8f5e9;
    --ok-fg: #1b5e20;
"""

DARK_VARS = """
    --app-bg: #000000;
    --app-fg: #ffffff;
    --panel-left-bg: #121212;
    --panel-right-bg: #0e0e14;
    --box-bg: #2e2e2e;
    --box-fg: #ffffff;
    --spoiler-bg: #1d2440;
    --spoiler-fg: #9db4ff;
    --metric-border: #666666;
    --muted-fg: #bbbbbb;
    --hole-bg: #3a1f1f;
    --hole-fg: #ff8a80;
    --ok-bg: #1b3320;
    --ok-fg: #a5d6a7;
"""

def detect_dark_theme():
    """True/False si Streamlit expone el tema, None si no se puede saber."""
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
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght=0,400;0,600;0,700;1,400;1,600&display=swap');

{theme_block}

.stApp, html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--app-bg) !important;
    color: var(--app-fg) !important;
    font-family: 'Open Sans', Arial, sans-serif;
}}
[data-testid="stSidebar"] {{ display: none; }}
.block-container {{ padding: 1rem 3rem !important; max-width: 100% !important; }}

.top-bar-title {{
    font-size: 34px; font-weight: 700; color: {UBU_RED};
    background: var(--box-bg); padding: 20px 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: flex-start;
    height: 100%; width: 100%; line-height: 1.2;
}}

div[data-testid="column"]:has(.bg-left) {{
    background: var(--panel-left-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
}}
div[data-testid="column"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
    display: flex; flex-direction: column; align-items: center;
}}

.statement-box {{
    border: 4px solid {UBU_RED}; border-radius: 12px;
    padding: 30px 40px; background: var(--box-bg);
    font-style: italic; text-align: justify;
    color: var(--box-fg); font-size: 25px; line-height: 1.5; margin-bottom: 30px;
}}
.content-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: 20px 25px; background: var(--box-bg);
    font-style: normal; text-align: justify;
    color: var(--box-fg); font-size: 25px; line-height: 1.6; margin-bottom: 20px;
}}
.section-title {{
    font-size: 28px; font-weight: 700; color: var(--app-fg);
    margin: 10px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px;
}}
.subsection-title {{
    font-size: 23px; font-weight: 600; color: {ORANGE_ACCENT};
    margin: 20px 0 10px 0; border-left: 5px solid {ORANGE_ACCENT};
    padding-left: 15px;
}}
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 27px; color: var(--spoiler-fg);
}}
.spacer {{ height: 35px; }}

/* ---- Spoiler: borroso en azul hasta que se pulsa ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-click-wrapper {{ cursor: pointer; display: block; text-decoration: none; margin-top: 20px; margin-bottom: 25px; }}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400; font-size: 25px; line-height: 1.5;
    background: var(--spoiler-bg); border-left: 10px solid var(--spoiler-fg);
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(15px); transition: filter 0.3s;
}}
.spoiler-toggle:checked ~ .spoiler-click-wrapper .spoiler-box {{ filter: none; }}

button p {{ font-size: 25px !important; }}
div[data-testid="column"] button {{ padding-top: 15px !important; padding-bottom: 15px !important; }}

/* ---- Sliders ---- */
div[data-testid="stSlider"] > div {{
    display: flex !important;
    flex-direction: column-reverse !important;
}}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{
    display: block !important;
    font-size: 34px !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
[data-testid="stThumbValue"] {{
    display: block !important;
    font-size: 34px !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
.stSlider [data-baseweb="slider"] {{ padding-top: 55px; padding-bottom: 5px; }}
.stSlider {{ margin-bottom: 5px; }}

/* ---- Inputs generales interactivos ---- */
[data-testid="stNumberInput"] input, [data-baseweb="select"] div {{
    font-size: 22px !important; font-weight: 600 !important;
}}
[data-testid="stNumberInput"] label p, label[data-testid="stWidgetLabel"] p {{
    font-size: 22px !important; color: var(--app-fg) !important; font-weight: 600;
}}
button[data-baseweb="tab"] p {{ font-size: 21px !important; font-weight: 600 !important; }}

/* ---- Metric boxes ---- */
.metric-box {{
    font-size: 24px; color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px; white-space: nowrap; overflow: hidden;
}}
.metric-third {{ font-size: 19px; padding: 12px 8px; }}
.metric-a {{ border-color: {BLUE_LINE};  color: {BLUE_LINE};  font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE}; color: {GREEN_LINE}; font-weight: 700; }}
.metric-c {{ border-color: {ORANGE_ACCENT}; color: {ORANGE_ACCENT}; font-weight: 700; }}

.result-bayes {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;  border-color: {UBU_YELLOW} !important; }}
.result-likely {{ background: {GREEN_LINE} !important; color: #ffffff !important; border-color: {GREEN_LINE} !important; }}
.result-unlikely {{ background: #d32f2f !important; color: #ffffff !important; border-color: #d32f2f !important; }}

/* ---- Tablas de distribución conjunta ---- */
.jtable {{
    border-collapse: collapse; margin: 10px auto 20px auto;
    background: var(--box-bg); color: var(--box-fg); font-size: 24px;
    font-family: 'STIX Two Math', 'Cambria Math', serif;
}}
.jtable th, .jtable td {{
    border: 2px solid {UBU_RED}; padding: 10px 20px; text-align: center;
}}
.jtable th {{ background: {UBU_YELLOW}; color: {UBU_DARK}; font-weight: 700; }}
.jtable td.marg {{ background: var(--spoiler-bg); color: var(--spoiler-fg); font-weight: 700; }}
.jtable td.hole {{ background: var(--hole-bg); color: var(--hole-fg); font-weight: 700; }}
.jtable td.given {{ font-weight: 700; }}
.jtable caption {{
    caption-side: top; font-size: 21px; color: var(--muted-fg);
    padding-bottom: 8px; font-family: 'Open Sans', Arial, sans-serif;
}}

.ok-box {{
    border: 3px solid var(--ok-fg); border-radius: 12px; background: var(--ok-bg);
    color: var(--ok-fg); font-size: 24px; padding: 18px 25px; margin-bottom: 20px;
    text-align: center; font-weight: 600;
}}
.ko-box {{
    border: 3px solid var(--hole-fg); border-radius: 12px; background: var(--hole-bg);
    color: var(--hole-fg); font-size: 24px; padding: 18px 25px; margin-bottom: 20px;
    text-align: center; font-weight: 600;
}}

.footer-license {{
    text-align: center; color: var(--muted-fg); font-size: 18px;
    margin-top: 50px; padding-top: 20px; border-top: 1px solid var(--metric-border);
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "INTRO"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "INTRO_A"

# =============================================================================
# 3. COMPONENTES REUTILIZABLES
# =============================================================================

def accordion_step(step_id, label):
    """Accordion con lógica de state management."""
    is_open = st.session_state.get("open_step") == step_id
    if st.button(label, use_container_width=True, key=f"btn_{step_id}"):
        st.session_state["open_step"] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(content):
    """Caja de spoiler con desenfoque blur."""
    unique_id = str(uuid.uuid4())
    html = f"""
    <input type="checkbox" id="spoiler_{unique_id}" class="spoiler-toggle">
    <label for="spoiler_{unique_id}" class="spoiler-click-wrapper">
        <div class="spoiler-box">{content}</div>
    </label>
    """
    st.markdown(html, unsafe_allow_html=True)

def frac_str(value, max_den=400):
    """Representación en fracción irreducible de un número real."""
    f = Fraction(value).limit_denominator(max_den)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

def color_ramp(c_start, c_end, n=256):
    """Paleta continua entre dos colores hex (evita depender de bokeh.palettes)."""
    def h2r(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    r1, g1, b1 = h2r(c_start)
    r2, g2, b2 = h2r(c_end)
    out = []
    for i in range(n):
        t = i / (n - 1)
        out.append("#%02x%02x%02x" % (round(r1 + (r2 - r1) * t),
                                      round(g1 + (g2 - g1) * t),
                                      round(b1 + (b2 - b1) * t)))
    return out

PALETTE_RED  = color_ramp("#ffffff", UBU_RED)
PALETTE_BLUE = color_ramp("#ffffff", PANTONE_2727)

def style_axes(p, title_size="15px", label_size="14px"):
    p.title.text_font_size = title_size
    p.xaxis.axis_label_text_font_size = label_size
    p.yaxis.axis_label_text_font_size = label_size
    p.xaxis.major_label_text_font_size = "13px"
    p.yaxis.major_label_text_font_size = "13px"
    return p

def joint_table_html(P, x_labels, y_labels, caption="", fmt=frac_str,
                     marginals=True, holes=None, blank_marg=False, corner="Y \\ X"):
    """
    Tabla HTML de una función de probabilidad conjunta.
    P tiene forma (len(y_labels), len(x_labels)): filas = valores de Y.
    holes: conjunto de tuplas (fila, columna) que se muestran como '?'.
    """
    holes = holes or set()
    px = P.sum(axis=0)
    py = P.sum(axis=1)

    html = ["<table class='jtable'>"]
    if caption:
        html.append(f"<caption>{caption}</caption>")
    html.append(f"<tr><th>{corner}</th>")
    for xl in x_labels:
        html.append(f"<th>{xl}</th>")
    if marginals:
        html.append("<th>p<sub>Y</sub></th>")
    html.append("</tr>")

    for j, yl in enumerate(y_labels):
        html.append(f"<tr><th>{yl}</th>")
        for i in range(len(x_labels)):
            if (j, i) in holes:
                html.append("<td class='hole'>?</td>")
            else:
                html.append(f"<td class='given'>{fmt(P[j, i])}</td>")
        if marginals:
            if blank_marg or any((j, i) in holes for i in range(len(x_labels))):
                html.append("<td class='hole'>?</td>")
            else:
                html.append(f"<td class='marg'>{fmt(py[j])}</td>")
        html.append("</tr>")

    if marginals:
        html.append("<tr><th>p<sub>X</sub></th>")
        col_has_hole = [any((j, i) in holes for j in range(len(y_labels)))
                        for i in range(len(x_labels))]
        for i in range(len(x_labels)):
            if blank_marg or col_has_hole[i]:
                html.append("<td class='hole'>?</td>")
            else:
                html.append(f"<td class='marg'>{fmt(px[i])}</td>")
        if holes or blank_marg:
            html.append("<td class='marg'>1</td>")
        else:
            html.append(f"<td class='marg'>{fmt(P.sum())}</td>")
        html.append("</tr>")

    html.append("</table>")
    return "".join(html)

def heatmap_pmf(P, x_vals, y_vals, title, palette=PALETTE_RED, fmt="{:.3f}",
                width=430, height=360, pad=0.6):
    """Mapa de calor de una p.m.f. conjunta discreta con etiquetas por celda."""
    pmax = max(float(P.max()), 1e-12)
    xs, ys, ps, ts, tc = [], [], [], [], []
    for j, yv in enumerate(y_vals):
        for i, xv in enumerate(x_vals):
            xs.append(xv); ys.append(yv)
            ps.append(float(P[j, i])); ts.append(fmt.format(P[j, i]))
            tc.append("#ffffff" if P[j, i] > 0.62 * pmax else UBU_DARK)
    src = ColumnDataSource(dict(x=xs, y=ys, p=ps, t=ts, tc=tc))
    mapper = LinearColorMapper(palette=palette, low=0.0, high=max(float(P.max()), 1e-9))

    p = figure(title=title, x_axis_label="x  (valores de X)", y_axis_label="y  (valores de Y)",
               width=width, height=height, tools="", toolbar_location=None,
               x_range=(min(x_vals) - pad, max(x_vals) + pad),
               y_range=(min(y_vals) - pad, max(y_vals) + pad))
    p.rect(x="x", y="y", width=0.92, height=0.92, source=src,
           fill_color={"field": "p", "transform": mapper},
           line_color="white", line_width=2)
    p.text(x="x", y="y", text="t", source=src, text_align="center",
           text_baseline="middle", text_font_size="13px",
           text_color={"field": "tc"})
    p.add_tools(HoverTool(tooltips=[("(x, y)", "(@x, @y)"), ("p(x,y)", "@p{0.0000}")]))
    p.xaxis.ticker = list(x_vals)
    p.yaxis.ticker = list(y_vals)
    return style_axes(p)

# =============================================================================
# 4. DATOS DE LOS EJEMPLOS
# =============================================================================

# Ejemplo de la sección (I): tabla 3x3 (filas Y = 0,1,2 ; columnas X = 0,1,2)
P_CONJ = np.array([[0.10, 0.05, 0.05],
                   [0.05, 0.20, 0.10],
                   [0.05, 0.15, 0.25]])

# Ejercicio 52: primera fila conocida (Y = 0), en dieciochoavos exactos
FILA_DADA = np.array([2 / 9, 1 / 3, 1 / 9])

# Funciones para el experimento de los dos dados (introducción)
DADOS_FUN = {
    "Suma de los dos dados": lambda a, b: a + b,
    "Máximo de los dos dados": lambda a, b: max(a, b),
    "Mínimo de los dos dados": lambda a, b: min(a, b),
    "Resultado del primer dado": lambda a, b: a,
    "Resultado del segundo dado": lambda a, b: b,
    "Diferencia en valor absoluto": lambda a, b: abs(a - b),
}

BOREL_SETS = {
    "B₁ = {(x, y) : x = y}": lambda x, y: x == y,
    "B₂ = {(x, y) : x + y ≤ 8}": lambda x, y: x + y <= 8,
    "B₃ = {(x, y) : x > y}": lambda x, y: x > y,
    "B₄ = (−∞, 4] × (−∞, 5]": lambda x, y: (x <= 4) and (y <= 5),
}

# =============================================================================
# 5. PÁGINAS
# =============================================================================

def render_intro():
    """Introducción: el espacio probabilizable y los vectores aleatorios (5.1)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: Vectores Aleatorios</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Cuando de un mismo experimento aleatorio nos interesan varias magnitudes numéricas a la vez, "
            "una variable aleatoria ya no basta. Extendemos el concepto al de <b>vector aleatorio</b>, "
            "que estudia el comportamiento <i>conjunto</i> de esas magnitudes."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "A) El espacio de partida: la σ-álgebra de Borel en ℝᵏ"):
            st.markdown("<div class='subsection-title'>A) Ingredientes</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La estructura fundamental sobre ℝᵏ es la σ-álgebra de Borel 𝔅<sub>ℝᵏ</sub>, "
                "<b>generada por los rectángulos</b> de la forma:"
                "<div class='formula-box'>(−∞, x₁] × ⋯ × (−∞, x<sub>k</sub>]</div>"
                "Que esos rectángulos generen toda la σ-álgebra es la razón de fondo por la que la función de "
                "distribución conjunta, definida justamente sobre ellos, caracteriza al vector por completo.<br><br>"
                "<b>Aviso importante:</b> 𝔅<sub>ℝᵏ</sub> ≠ 𝔅<sub>ℝ</sub> × ⋯ × 𝔅<sub>ℝ</sub>, ya que el producto "
                "cartesiano de σ-álgebras no tiene estructura de σ-álgebra por sí mismo."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("INTRO_B", "B) Definición de vector aleatorio y medibilidad"):
            st.markdown("<div class='subsection-title'>B) Definición y medibilidad</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Dado un espacio de probabilidad (Ω, 𝒜, P), un <b>vector aleatorio bidimensional</b> es una "
                "aplicación (X, Y) : Ω → ℝ² tal que la anti-imagen de todo conjunto de Borel es medible:"
                "<div class='formula-box'>(X, Y)⁻¹(B) = {ω ∈ Ω : (X(ω), Y(ω)) ∈ B} ∈ 𝒜</div>"
                "Por lo dicho en A), basta exigirlo sobre los rectángulos generadores: para todos c, d ∈ ℝ,"
                "<div class='formula-box'>{ω ∈ Ω : X(ω) ≤ c, Y(ω) ≤ d} ∈ 𝒜</div>"
                "<b>Equivalencia de medibilidad (5.1.3):</b> la aplicación (X₁, …, X<sub>k</sub>) : Ω → ℝᵏ es un "
                "vector aleatorio si, y sólo si, cada componente X₁, …, X<sub>k</sub> es una variable aleatoria "
                "unidimensional. Nada nuevo hay que comprobar componente a componente."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Ojo con el recíproco de la intuición: que cada componente sea medible garantiza que el vector lo es, "
                "pero conocer las dos <i>marginales</i> por separado no determina la distribución conjunta. "
                "Medibilidad y determinación son cosas distintas."
            )

        if accordion_step("INTRO_C", "C) Probabilidad inducida sobre ℝ²"):
            st.markdown("<div class='subsection-title'>C) Probabilidad inducida</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El cumplimiento de la medibilidad Borel permite trasladar toda la probabilidad del espacio "
                "abstracto Ω a ℝ². Se define, para cada B ∈ 𝔅<sub>ℝ²</sub>:"
                "<div class='formula-box'>P<sub>(X,Y)</sub>(B) = P((X, Y) ∈ B)</div>"
                "Con ello, el estudio del espacio abstracto inicial se reduce al de una función real de variable "
                "vectorial: ya podemos olvidarnos de Ω y trabajar con tablas, densidades e integrales."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>🎲 De Ω a ℝ²: dos dados</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Ω son los 36 resultados equiprobables (d₁, d₂). Elige qué dos magnitudes X e Y mides sobre ellos y "
            "un conjunto de Borel B: el applet calcula la anti-imagen (X,Y)⁻¹(B) y la probabilidad inducida."
            "</small></div>",
            unsafe_allow_html=True
        )

        nombre_x = st.selectbox("Definición de X", list(DADOS_FUN.keys()), index=0)
        nombre_y = st.selectbox("Definición de Y", list(DADOS_FUN.keys()), index=1)
        nombre_b = st.selectbox("Conjunto de Borel B ⊂ ℝ²", list(BOREL_SETS.keys()), index=3)

        fx, fy, cond = DADOS_FUN[nombre_x], DADOS_FUN[nombre_y], BOREL_SETS[nombre_b]

        omega = [(a, b) for a in range(1, 7) for b in range(1, 7)]
        puntos = {}
        anti_imagen = []
        for (a, b) in omega:
            x, y = fx(a, b), fy(a, b)
            puntos[(x, y)] = puntos.get((x, y), 0) + 1
            if cond(x, y):
                anti_imagen.append((a, b))

        prob_b = len(anti_imagen) / 36

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"<div class='metric-box metric-a'>Puntos distintos de (X,Y)<br>{len(puntos)} de 36 ω</div>",
                unsafe_allow_html=True)
        with m2:
            st.markdown(
                f"<div class='metric-box result-bayes'>P<sub>(X,Y)</sub>(B) = {len(anti_imagen)}/36 "
                f"= {prob_b:.4f}</div>",
                unsafe_allow_html=True)

        xs = np.array([k[0] for k in puntos.keys()], dtype=float)
        ys = np.array([k[1] for k in puntos.keys()], dtype=float)
        cs = np.array([puntos[k] for k in puntos.keys()], dtype=float)
        dentro = np.array([cond(x, y) for x, y in zip(xs, ys)])

        src_in = ColumnDataSource(dict(x=xs[dentro], y=ys[dentro],
                                       n=cs[dentro], s=8 + 5 * cs[dentro],
                                       pr=cs[dentro] / 36))
        src_out = ColumnDataSource(dict(x=xs[~dentro], y=ys[~dentro],
                                        n=cs[~dentro], s=8 + 5 * cs[~dentro],
                                        pr=cs[~dentro] / 36))

        p = figure(title="Soporte del vector (X, Y): tamaño ∝ nº de ω que caen en el punto",
                   x_axis_label=f"X = {nombre_x.lower()}", y_axis_label=f"Y = {nombre_y.lower()}",
                   width=470, height=380, tools="", toolbar_location=None)
        p.scatter("x", "y", size="s", source=src_out, marker="circle",
                  fill_color="#cccccc", line_color="#888888", alpha=0.85,
                  legend_label="(x, y) ∉ B")
        p.scatter("x", "y", size="s", source=src_in, marker="circle",
                  fill_color=UBU_RED, line_color=UBU_DARK, alpha=0.9,
                  legend_label="(x, y) ∈ B")
        p.add_tools(HoverTool(tooltips=[("(x, y)", "(@x, @y)"),
                                        ("nº de ω", "@n"),
                                        ("p(x,y)", "@pr{0.0000}")]))
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "13px"
        p.legend.background_fill_alpha = 0.7
        streamlit_bokeh(style_axes(p))

        muestra = ", ".join(f"({a},{b})" for a, b in anti_imagen[:10])
        resto = "" if len(anti_imagen) <= 10 else f" … <i>(+{len(anti_imagen) - 10} más)</i>"
        st.markdown(
            f"<div class='content-box'><b>Anti-imagen (X,Y)⁻¹(B) ⊂ Ω:</b><br>"
            f"<span style='font-size: 21px;'>{muestra if muestra else '∅'}{resto}</span><br><br>"
            f"Son los {len(anti_imagen)} resultados del experimento original cuyo par de valores cae dentro de B. "
            f"Al ser todos equiprobables, P<sub>(X,Y)</sub>(B) = {len(anti_imagen)}/36.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><small style='color: var(--muted-fg);'>"
            "Prueba con B₄ = (−∞,4] × (−∞,5]: la probabilidad que obtienes es exactamente F(4, 5), el valor de la "
            "función de distribución conjunta que se estudia en el apartado (I)."
            "</small></div>",
            unsafe_allow_html=True
        )

def render_conjunta():
    """(I) Distribución conjunta: F(x,y), clasificación, p.m.f. y densidad (5.2 y 5.3)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Distribución Conjunta</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La función de distribución conjunta acumula probabilidad sobre los rectángulos "
            "(−∞, x] × (−∞, y]. Como esos rectángulos generan 𝔅<sub>ℝ²</sub>, la función F(x, y) "
            "caracteriza unívocamente la distribución del vector aleatorio."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Función de distribución conjunta"):
            st.markdown("<div class='subsection-title'>A) Definición de F(x, y)</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea (X, Y) un vector aleatorio asociado a (Ω, 𝒜, P). Su función de distribución conjunta es "
                "la aplicación F : ℝ² → ℝ dada por:"
                "<div class='formula-box'>F(x, y) = P((X ≤ x) ∩ (Y ≤ y))</div>"
                "es decir, P({ω ∈ Ω : X(ω) ≤ x, Y(ω) ≤ y}). Se acumula <b>hacia abajo y hacia la izquierda</b> "
                "simultáneamente en las dos variables."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "B) Las cinco propiedades de F(x, y)"):
            st.markdown("<div class='subsection-title'>B) Propiedades caracterizadoras</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>i) Límites asintóticos superiores:</b> lím<sub>x,y→∞</sub> F(x, y) = P(ℝ²) = 1.<br><br>"
                "<b>ii) Límites asintóticos inferiores:</b> "
                "lím<sub>x→−∞</sub> F(x, y) = lím<sub>y→−∞</sub> F(x, y) = 0.<br><br>"
                "<b>iii) Monotonía:</b> F es no decreciente en cada variable; "
                "si x₁ < x₂ ⟹ F(x₁, y) ≤ F(x₂, y).<br><br>"
                "<b>iv) Continuidad:</b> F es continua por la derecha en cada variable.<br><br>"
                "<b>v) Desigualdad del rectángulo:</b> para x₁ < x₂ e y₁ < y₂,"
                "<div class='formula-box'>F(x₂,y₂) − F(x₁,y₂) − F(x₂,y₁) + F(x₁,y₁) ≥ 0</div>"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "La propiedad (v) es la genuinamente bidimensional y no se deduce de las otras cuatro: esa "
                "combinación de cuatro signos <i>es</i> la probabilidad del rectángulo (x₁,x₂] × (y₁,y₂], y por "
                "tanto no puede ser negativa. En dimensión 1 le corresponde simplemente F(b) − F(a) ≥ 0."
            )

        if accordion_step("P1_C", "C) Vectores discretos: función de probabilidad conjunta"):
            st.markdown("<div class='subsection-title'>C) Caso discreto</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "(X, Y) es discreto si sus componentes lo son (toman un número finito o infinito numerable de "
                "valores). Si X toma los valores xᵢ e Y los valores y<sub>j</sub>, la <b>función de probabilidad "
                "conjunta</b> es el conjunto de números:"
                "<div class='formula-box'>p<sub>ij</sub> = P(X = xᵢ, Y = y<sub>j</sub>)</div>"
                "<b>Propiedades:</b><br>"
                "• p<sub>ij</sub> ≥ 0 para todo (xᵢ, y<sub>j</sub>)<br>"
                "• Σ<sub>xᵢ</sub> Σ<sub>y<sub>j</sub></sub> p<sub>ij</sub> = 1<br>"
                "• P((X,Y) ∈ B) = Σ<sub>(xᵢ,y<sub>j</sub>) ∈ B</sub> p<sub>ij</sub> (sumar en los puntos favorables)<br>"
                "• F(x, y) = Σ<sub>xᵢ ≤ x</sub> Σ<sub>y<sub>j</sub> ≤ y</sub> p<sub>ij</sub>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_D", "D) Vectores continuos: densidad conjunta"):
            st.markdown("<div class='subsection-title'>D) Caso continuo</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "(X, Y) es continuo si sus componentes son continuas y F es absolutamente continua, de modo que "
                "puede expresarse mediante una integral doble:"
                "<div class='formula-box'>F(x, y) = ∫<sub>−∞</sub><sup>x</sup> ∫<sub>−∞</sub><sup>y</sup> "
                "f(t, u) du dt</div>"
                "En los puntos donde F es doblemente diferenciable, la densidad se recupera derivando:"
                "<div class='formula-box'>f(x, y) = ∂²F(x, y) / ∂x∂y</div>"
                "<b>Propiedades de f:</b><br>"
                "• No negatividad: f(x, y) ≥ 0<br>"
                "• Normalización: ∫∫<sub>ℝ²</sub> f(x, y) dx dy = 1<br>"
                "• P((X,Y) ∈ B) = ∬<sub>B</sub> f(t, u) dt du (volumen bajo la superficie)<br>"
                "• P(X = x, Y = y) = 0: puntos y líneas tienen probabilidad nula"
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        tab_d, tab_c = st.tabs(["Discreto: acumular F(x,y)", "Continuo: normalizar f(x,y)"])

        # ---------------- Caso discreto: F y desigualdad del rectángulo ----------
        with tab_d:
            st.markdown(
                "<div class='content-box'><b>⚙️ Rectángulos sobre una tabla 3 × 3</b><br>"
                "<small style='color: var(--muted-fg);'>"
                "Mueve los extremos del rectángulo (x₁, x₂] × (y₁, y₂]. El applet lo calcula de dos formas: "
                "sumando las celdas encerradas y mediante los cuatro valores de F en las esquinas."
                "</small></div>",
                unsafe_allow_html=True
            )

            st.markdown(joint_table_html(
                P_CONJ, ["0", "1", "2"], ["0", "1", "2"],
                caption="Función de probabilidad conjunta p_ij del ejemplo (con marginales)",
                fmt=lambda v: f"{v:.2f}"), unsafe_allow_html=True)

            rx = st.slider("Intervalo en X:  (x₁, x₂]", -1.0, 3.0, (-0.5, 1.5), 0.25, key="rx")
            ry = st.slider("Intervalo en Y:  (y₁, y₂]", -1.0, 3.0, (0.5, 2.5), 0.25, key="ry")
            x1, x2 = rx
            y1, y2 = ry

            vals = [0, 1, 2]

            def F(x, y):
                return float(sum(P_CONJ[j, i] for j in range(3) for i in range(3)
                                 if vals[i] <= x and vals[j] <= y))

            suma_directa = float(sum(P_CONJ[j, i] for j in range(3) for i in range(3)
                                     if x1 < vals[i] <= x2 and y1 < vals[j] <= y2))
            f22, f12, f21, f11 = F(x2, y2), F(x1, y2), F(x2, y1), F(x1, y1)
            rect = f22 - f12 - f21 + f11

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"<div class='metric-box metric-third metric-a'>Suma de celdas<br>"
                            f"{suma_directa:.3f}</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-box metric-third metric-b'>Vía F (4 esquinas)<br>"
                            f"{rect:.3f}</div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-box metric-third metric-c'>F(x₂, y₂)<br>"
                            f"{f22:.3f}</div>", unsafe_allow_html=True)

            p = heatmap_pmf(P_CONJ, [0, 1, 2], [0, 1, 2],
                            "p(x,y) y el rectángulo seleccionado", fmt="{:.2f}",
                            width=470, height=380, pad=1.1)
            p.add_layout(BoxAnnotation(left=x1, right=x2, bottom=y1, top=y2,
                                       fill_alpha=0.18, fill_color=PANTONE_2727,
                                       line_color=PANTONE_2727, line_width=3))
            streamlit_bokeh(p)

            st.markdown(
                f"<div class='content-box'>"
                f"<b>Desigualdad del rectángulo, término a término:</b><br>"
                f"<span style='font-size:22px;'>"
                f"F({x2:g}, {y2:g}) − F({x1:g}, {y2:g}) − F({x2:g}, {y1:g}) + F({x1:g}, {y1:g}) = "
                f"{f22:.3f} − {f12:.3f} − {f21:.3f} + {f11:.3f} = <b>{rect:.3f}</b>"
                f"</span><br><br>"
                f"Los dos cálculos coinciden siempre, y el resultado nunca puede ser negativo: restar los dos "
                f"rectángulos laterales elimina dos veces la esquina inferior izquierda, y el término +F(x₁, y₁) "
                f"la devuelve una vez. Es el principio de inclusión-exclusión en dos dimensiones."
                f"</div>",
                unsafe_allow_html=True
            )

        # ---------------- Caso continuo: normalización ---------------------------
        with tab_c:
            st.markdown(
                "<div class='content-box'><b>⚙️ Encuentra la constante de normalización</b><br>"
                "<small style='color: var(--muted-fg);'>"
                "Sea f(x, y) = k (x + y²) sobre el cuadrado unidad [0,1] × [0,1] y cero fuera. "
                "Ajusta k hasta que la integral doble valga exactamente 1."
                "</small></div>",
                unsafe_allow_html=True
            )

            k = st.slider("Constante k", 0.10, 3.00, 1.00, 0.05, key="k_norm")

            n = 220
            xg = np.linspace(0, 1, n)
            yg = np.linspace(0, 1, n)
            XG, YG = np.meshgrid(xg, yg)
            Z = k * (XG + YG ** 2)
            integral = _trapz(_trapz(Z, xg, axis=1), yg)

            ok = abs(integral - 1.0) < 5e-3
            clase = "result-likely" if ok else "result-unlikely"

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"<div class='metric-box metric-third {clase}'>∫∫ f dx dy<br>"
                            f"{integral:.4f}</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-box metric-third'>Valor exacto<br>"
                            f"5k/6 = {5 * k / 6:.4f}</div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-box metric-third metric-c'>f máx (en (1,1))<br>"
                            f"{2 * k:.3f}</div>", unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                pf = figure(title="Densidad conjunta f(x, y)", x_axis_label="x", y_axis_label="y",
                            width=340, height=310, tools="", toolbar_location=None,
                            x_range=(0, 1), y_range=(0, 1))
                pf.image(image=[Z], x=0, y=0, dw=1, dh=1,
                         color_mapper=LinearColorMapper(palette=PALETTE_RED,
                                                        low=0, high=float(Z.max())))
                streamlit_bokeh(style_axes(pf))
            with g2:
                ZF = k * (XG ** 2 * YG / 2 + XG * YG ** 3 / 3)
                pF = figure(title="Distribución conjunta F(x, y)", x_axis_label="x", y_axis_label="y",
                            width=340, height=310, tools="", toolbar_location=None,
                            x_range=(0, 1), y_range=(0, 1))
                pF.image(image=[ZF], x=0, y=0, dw=1, dh=1,
                         color_mapper=LinearColorMapper(palette=PALETTE_BLUE,
                                                        low=0, high=float(ZF.max())))
                streamlit_bokeh(style_axes(pF))

            st.markdown(
                "<div class='content-box'>"
                "<b>Cálculo a mano:</b><br>"
                "∫₀¹ ∫₀¹ k(x + y²) dx dy = k [ ∫₀¹ x dx + ∫₀¹ y² dy ] = k (1/2 + 1/3) = 5k/6.<br>"
                "Igualando a 1 se obtiene <b>k = 6/5 = 1.2</b>, y entonces"
                "<div class='formula-box'>F(x, y) = (6/5)( x²y/2 + xy³/3 ),&nbsp; 0 ≤ x, y ≤ 1</div>"
                "Comprueba en el mapa de la derecha que F crece de 0 en el origen a 1 en la esquina (1,1) "
                "sólo cuando k es la correcta: es la propiedad (i) de F."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Con k = 6/5, derivando dos veces F recuperas f: ∂²F/∂x∂y = (6/5)(x + y²). "
                "Fíjate en que F ya no es un producto de una función de x por una de y, y por eso este vector "
                "<i>no</i> tiene componentes independientes, aunque el recinto sea un rectángulo."
            )

def render_marginal():
    """(II) Distribuciones marginales (5.4.1 y 5.4.2)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) Distribuciones Marginales</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "A partir de la distribución conjunta podemos recuperar el comportamiento de cada variable por "
            "separado: se trata de <b>eliminar</b> la otra variable, sumando o integrando sobre todos sus "
            "valores posibles."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Marginales a partir de F(x, y)"):
            st.markdown("<div class='subsection-title'>A) Marginales por paso al límite</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Dada la función de distribución conjunta F(x, y) de un vector (X, Y), las funciones de "
                "distribución marginales se obtienen dejando que la otra variable tienda a infinito:"
                "<div class='formula-box'>F₁(x) = lím<sub>y→∞</sub> F(x, y)</div>"
                "<div class='formula-box'>F₂(y) = lím<sub>x→∞</sub> F(x, y)</div>"
                "La lectura es transparente: F₁(x) = P(X ≤ x, Y &lt; ∞) = P(X ≤ x), porque el suceso sobre Y "
                "deja de imponer restricción alguna."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) Cálculo de marginales: sumar o integrar"):
            st.markdown("<div class='subsection-title'>B) Caso discreto y caso continuo</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Caso discreto:</b> se suman las probabilidades conjuntas de toda una fila o columna,"
                "<div class='formula-box'>P(X = xᵢ) = Σ<sub>y<sub>j</sub></sub> P(X = xᵢ, Y = y<sub>j</sub>)</div>"
                "<b>Caso continuo:</b> se integra la densidad conjunta respecto de la otra variable,"
                "<div class='formula-box'>f₁(x) = ∫<sub>−∞</sub><sup>∞</sup> f(x, y) dy</div>"
                "De forma completamente simétrica se calculan P(Y = y<sub>j</sub>) y f₂(y), operando respecto de x. "
                "La idea se generaliza a un vector k-dimensional sumando o integrando sobre las k − 1 variables "
                "restantes que no nos interesen."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_C", "C) Lo que las marginales no saben"):
            st.markdown("<div class='subsection-title'>C) Pérdida de información</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El paso conjunta → marginales es <b>irreversible</b>. Dos vectores aleatorios con distribuciones "
                "conjuntas muy distintas pueden tener exactamente las mismas marginales, porque al sumar o "
                "integrar se destruye toda la información sobre cómo se relacionan las variables.<br><br>"
                "La normal bidimensional es el ejemplo más limpio: sus marginales son "
                "𝒩(𝔼[X], σ<sub>X</sub>) y 𝒩(𝔼[Y], σ<sub>Y</sub>) <b>independientemente del valor de "
                "ρ<sub>XY</sub></b>, aunque la nube de puntos cambie por completo de forma."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Consecuencia práctica: nunca podrás reconstruir la conjunta a partir de las marginales salvo que "
                "añadas una hipótesis extra. La hipótesis habitual es la independencia, f(x,y) = f₁(x)·f₂(y), "
                "y es justo la que hace que el ejercicio 52 tenga solución única."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Normal bidimensional: proyectar para marginar</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Cambia ρ y observa las dos marginales de abajo: la nube gira y se estrecha, pero las "
            "campanas proyectadas no se mueven."
            "</small></div>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        with c1:
            mu_x = st.slider("𝔼[X]", -3.0, 3.0, 0.0, 0.5, key="m_mx")
            sig_x = st.slider("σ_X", 0.5, 3.0, 1.0, 0.1, key="m_sx")
        with c2:
            mu_y = st.slider("𝔼[Y]", -3.0, 3.0, 0.0, 0.5, key="m_my")
            sig_y = st.slider("σ_Y", 0.5, 3.0, 1.5, 0.1, key="m_sy")

        rho = st.slider("ρ_XY  (coeficiente de correlación)", -0.95, 0.95, 0.7, 0.05, key="m_rho")
        n_sim = st.slider("Tamaño de la muestra simulada", 200, 5000, 1500, 100, key="m_n")

        lim_x = (mu_x - 4 * sig_x, mu_x + 4 * sig_x)
        lim_y = (mu_y - 4 * sig_y, mu_y + 4 * sig_y)

        gx = np.linspace(lim_x[0], lim_x[1], 200)
        gy = np.linspace(lim_y[0], lim_y[1], 200)
        GX, GY = np.meshgrid(gx, gy)
        zx = (GX - mu_x) / sig_x
        zy = (GY - mu_y) / sig_y
        Z = (1.0 / (2 * np.pi * sig_x * sig_y * np.sqrt(1 - rho ** 2))) * np.exp(
            -(zx ** 2 - 2 * rho * zx * zy + zy ** 2) / (2 * (1 - rho ** 2)))

        rng = np.random.default_rng(42)
        cov = np.array([[sig_x ** 2, rho * sig_x * sig_y],
                        [rho * sig_x * sig_y, sig_y ** 2]])
        muestra = rng.multivariate_normal([mu_x, mu_y], cov, size=n_sim)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third metric-a'>Cov(X, Y)<br>"
                        f"{rho * sig_x * sig_y:.3f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third metric-b'>Marginal de X<br>"
                        f"𝒩({mu_x:g}, {sig_x:g})</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-c'>Marginal de Y<br>"
                        f"𝒩({mu_y:g}, {sig_y:g})</div>", unsafe_allow_html=True)

        pj = figure(title="Densidad conjunta f(x, y) y muestra simulada",
                    x_axis_label="x", y_axis_label="y",
                    width=470, height=380, tools="", toolbar_location=None,
                    x_range=lim_x, y_range=lim_y)
        pj.image(image=[Z], x=lim_x[0], y=lim_y[0],
                 dw=lim_x[1] - lim_x[0], dh=lim_y[1] - lim_y[0],
                 color_mapper=LinearColorMapper(palette=PALETTE_RED, low=0, high=float(Z.max())))
        pj.scatter(muestra[:, 0], muestra[:, 1], size=4, marker="circle",
                   fill_color=PANTONE_2727, line_color=None, alpha=0.35)
        streamlit_bokeh(style_axes(pj))

        st.markdown("<div class='subsection-title'>Marginales: proyecciones sobre cada eje</div>",
                    unsafe_allow_html=True)

        gcol1, gcol2 = st.columns(2)
        with gcol1:
            hist_x, edges_x = np.histogram(muestra[:, 0], bins=28, density=True)
            px = figure(title="f₁(x) = ∫ f(x,y) dy", x_axis_label="x", y_axis_label="densidad",
                        width=340, height=300, tools="", toolbar_location=None, x_range=lim_x)
            px.quad(top=hist_x, bottom=0, left=edges_x[:-1], right=edges_x[1:],
                    fill_color=BLUE_LINE, line_color="white", alpha=0.45,
                    legend_label="muestra")
            px.line(gx, norm.pdf(gx, mu_x, sig_x), line_width=4, color=UBU_RED,
                    legend_label="teórica")
            px.legend.location = "top_right"
            px.legend.label_text_font_size = "12px"
            streamlit_bokeh(style_axes(px))
        with gcol2:
            hist_y, edges_y = np.histogram(muestra[:, 1], bins=28, density=True)
            py = figure(title="f₂(y) = ∫ f(x,y) dx", x_axis_label="y", y_axis_label="densidad",
                        width=340, height=300, tools="", toolbar_location=None, x_range=lim_y)
            py.quad(top=hist_y, bottom=0, left=edges_y[:-1], right=edges_y[1:],
                    fill_color=GREEN_LINE, line_color="white", alpha=0.45,
                    legend_label="muestra")
            py.line(gy, norm.pdf(gy, mu_y, sig_y), line_width=4, color=UBU_RED,
                    legend_label="teórica")
            py.legend.location = "top_right"
            py.legend.label_text_font_size = "12px"
            streamlit_bokeh(style_axes(py))

        num_x = _trapz(Z, gy, axis=0)
        err = float(np.max(np.abs(num_x - norm.pdf(gx, mu_x, sig_x))))
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Marginación numérica:</b> integrando la conjunta sobre la malla en y se obtiene una curva que "
            f"difiere de 𝒩({mu_x:g}, {sig_x:g}) en como mucho {err:.2e}. La integral"
            f"<div class='formula-box'>∫<sub>−∞</sub><sup>∞</sup> f(x, y) dy = f₁(x)</div>"
            f"elimina ρ del resultado: la correlación vive en la conjunta, no en las marginales. "
            f"Prueba a fijar ρ = 0 y ρ = 0.95: las dos campanas de abajo son idénticas, la nube de arriba no."
            f"</div>",
            unsafe_allow_html=True
        )

def render_condicionada():
    """(III) Distribuciones condicionadas, tipo mixto e independencia (5.4.3, 5.5, 5.6)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) Distribuciones Condicionadas</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Si conocemos de antemano el valor de una de las variables, podemos recalcular y actualizar la "
            "distribución de la otra. Frente a las marginales, que <i>proyectan</i>, las condicionadas "
            "<i>cortan</i> la conjunta y renormalizan el corte."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Condicionadas: caso discreto y continuo"):
            st.markdown("<div class='subsection-title'>A) Definiciones</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Caso discreto.</b> Supuesto que P(Y = y<sub>j</sub>) > 0, la función de probabilidad "
                "condicionada de X dado Y = y<sub>j</sub> es una proporción:"
                "<div class='formula-box'>P(xᵢ | y<sub>j</sub>) = P(X = xᵢ, Y = y<sub>j</sub>) / P(Y = y<sub>j</sub>)</div>"
                "<b>Caso continuo.</b> Supuesto que f₂(y) > 0, la densidad condicionada de X por el valor y se "
                "define mediante un paso al límite:"
                "<div class='formula-box'>f(x | y) = f(x, y) / f₂(y)</div>"
                "En ambos casos, al fijar una variable la función resultante se comporta como una distribución "
                "unidimensional válida: suma o integra 1. El denominador es exactamente el factor que hace falta "
                "para lograrlo."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_B", "B) Independencia: cuando condicionar no cambia nada"):
            st.markdown("<div class='subsection-title'>B) Variables independientes</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "X e Y son <b>independientes</b> si, y sólo si, para cualesquiera x, y ∈ ℝ la conjunta se "
                "descompone como producto de marginales:"
                "<div class='formula-box'>F(x, y) = F₁(x) · F₂(y)</div>"
                "La factorización se hereda a las funciones de probabilidad y de densidad:<br><br>"
                "• <b>Discreto:</b> P(X = xᵢ, Y = y<sub>j</sub>) = P(X = xᵢ) · P(Y = y<sub>j</sub>), lo que "
                "equivale a decir que la condicionada coincide con la marginal, P(xᵢ | y<sub>j</sub>) = P(X = xᵢ).<br>"
                "• <b>Continuo:</b> f(x, y) = f₁(x) · f₂(y) en todo punto del espacio.<br><br>"
                "Para un vector k-dimensional se exige que la función conjunta sea exactamente el producto de "
                "las k marginales correspondientes."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Independencia y correlación nula no son lo mismo. Si X e Y son independientes entonces "
                "Cov(X, Y) = 0, pero el recíproco es falso en general: por ejemplo, con X ~ 𝒰(−1, 1) e Y = X², "
                "se tiene Cov(X, Y) = 𝔼[X³] − 𝔼[X]𝔼[X²] = 0 y, sin embargo, Y queda completamente determinada "
                "por X. En la normal bidimensional sí son equivalentes: ρ = 0 ⟺ independencia."
            )

        if accordion_step("P3_C", "C) Vectores de tipo mixto y Bayes extendido"):
            st.markdown("<div class='subsection-title'>C) Tipo mixto (5.5)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Un vector (X, Y) es de <b>tipo mixto</b> o compuesto si una de sus componentes es discreta y la "
                "otra continua.<br><br>"
                "Si X | y tiene distribución discreta P(X = xᵢ | y) e Y tiene marginal continua f₂(y), el "
                "<b>Teorema de Bayes extendido</b> le da la vuelta a la condición adaptando "
                "sumatorios e integrales:"
                "<div class='formula-box'>f(y | xᵢ) = P(X = xᵢ | y) · f₂(y) / "
                "∫<sub>−∞</sub><sup>∞</sup> P(X = xᵢ | u) · f₂(u) du</div>"
                "Análogamente se invertiría si X | y fuese continua e Y marginal discreta, usando sumatorios en "
                "el denominador en lugar de integrales."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        tab_cortes, = st.tabs(["Cortar la conjunta"])

        # ---------------- Cortes de la normal bidimensional ---------------------
        with tab_cortes:
            st.markdown(
                "<div class='content-box'><b>⚙️ Condicionar es cortar y renormalizar</b><br>"
                "<small style='color: var(--muted-fg);'>"
                "Desliza el corte y₀ sobre la normal bidimensional. Abajo verás el perfil f(x, y₀) "
                "renormalizado, comparado con la marginal f₁(x)."
                "</small></div>",
                unsafe_allow_html=True
            )

            rho_c = st.slider("ρ_XY", -0.95, 0.95, 0.75, 0.05, key="c_rho")
            y0 = st.slider("Valor del corte  y₀", -3.0, 3.0, 1.0, 0.1, key="c_y0")

            mx, my, sx, sy = 0.0, 0.0, 1.0, 1.0
            gx = np.linspace(-4, 4, 300)
            gy = np.linspace(-4, 4, 300)
            GX, GY = np.meshgrid(gx, gy)
            Z = (1.0 / (2 * np.pi * np.sqrt(1 - rho_c ** 2))) * np.exp(
                -(GX ** 2 - 2 * rho_c * GX * GY + GY ** 2) / (2 * (1 - rho_c ** 2)))

            mu_cond = mx + rho_c * (sx / sy) * (y0 - my)
            sd_cond = sx * np.sqrt(1 - rho_c ** 2)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"<div class='metric-box metric-third metric-a'>𝔼[X | Y = y₀]<br>"
                            f"{mu_cond:.3f}</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-box metric-third metric-b'>σ(X | Y = y₀)<br>"
                            f"{sd_cond:.3f}</div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-box metric-third metric-c'>Reducción de σ<br>"
                            f"{(1 - sd_cond / sx) * 100:.1f} %</div>", unsafe_allow_html=True)

            pc = figure(title="Conjunta, recta de regresión 𝔼[X | Y = y] y corte en y₀",
                        x_axis_label="x", y_axis_label="y",
                        width=470, height=350, tools="", toolbar_location=None,
                        x_range=(-4, 4), y_range=(-4, 4))
            pc.image(image=[Z], x=-4, y=-4, dw=8, dh=8,
                     color_mapper=LinearColorMapper(palette=PALETTE_RED, low=0, high=float(Z.max())))
            pc.line(mx + rho_c * (sx / sy) * (gy - my), gy, line_width=3,
                    color=GREEN_LINE, line_dash="dashed", legend_label="𝔼[X | Y = y]")
            pc.add_layout(Span(location=y0, dimension="width", line_color=PANTONE_2727,
                               line_width=4, line_dash="solid"))
            pc.scatter([mu_cond], [y0], size=14, marker="circle", fill_color=PANTONE_2727,
                       line_color="white", line_width=2)
            pc.legend.location = "top_left"
            pc.legend.label_text_font_size = "12px"
            streamlit_bokeh(style_axes(pc))

            perfil = np.exp(-((gx - mu_cond) ** 2) / (2 * sd_cond ** 2)) / (
                sd_cond * np.sqrt(2 * np.pi))
            pk = figure(title=f"f(x | Y = {y0:g}) frente a la marginal f₁(x)",
                        x_axis_label="x", y_axis_label="densidad",
                        width=470, height=300, tools="", toolbar_location=None, x_range=(-4, 4))
            pk.varea(x=gx, y1=np.zeros_like(gx), y2=perfil, fill_color=PANTONE_2727,
                     fill_alpha=0.25)
            pk.line(gx, perfil, line_width=4, color=PANTONE_2727, legend_label="condicionada")
            pk.line(gx, norm.pdf(gx, mx, sx), line_width=3, color=UBU_RED,
                    line_dash="dashed", legend_label="marginal f₁(x)")
            pk.add_layout(Span(location=mu_cond, dimension="height", line_color=GREEN_LINE,
                               line_width=2, line_dash="dotted"))
            pk.legend.location = "top_left"
            pk.legend.label_text_font_size = "12px"
            streamlit_bokeh(style_axes(pk))

            st.markdown(
                "<div class='content-box'>"
                "<b>'Corte gaussiano', Distribución condicionada de la normal bivariante:</b>"
                "<div class='formula-box'>X | Y = y ~ 𝒩( 𝔼[X] + ρ (σ<sub>X</sub>/σ<sub>Y</sub>)(y − 𝔼[Y]) , "
                "σ<sub>X</sub>√(1 − ρ²) )</div>"
                "Condicionar produce dos efectos: <b>desplaza</b> el centro proporcionalmente a ρ y "
                "<b>reduce</b> la dispersión en un factor √(1 − ρ²). Con ρ = 0 la curva azul se superpone "
                "exactamente a la roja para cualquier y₀: conocer Y no aporta información sobre X, que es "
                "precisamente la definición de independencia."
                "</div>",
                unsafe_allow_html=True
            )


def render_ejercicio():
    """(IV) Ejercicio 52: completar una tabla para que X e Y sean independientes."""
    col_left, col_right = st.columns([1, 1], gap="large")

    # Tabla del enunciado: fila Y=0 conocida, fila Y=1 desconocida
    P_enunciado = np.zeros((2, 3))
    P_enunciado[0, :] = FILA_DADA

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(IV) Ejercicio 52</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Aquí tienes una tabla parcialmente completa de una función de probabilidad conjunta."
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown(joint_table_html(
            P_enunciado, ["0", "1", "2"], ["0", "1"],
            caption="Enunciado: sólo se conoce la fila Y = 0",
            holes={(1, 0), (1, 1), (1, 2)}, blank_marg=True), unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Completa la tabla para que X, Y sean independientes. ¿Existe una única forma?"
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P4_A", "A) Marginal de Y a partir de la fila conocida"):
            st.markdown("<div class='subsection-title'>A) La única fila completa lo decide todo</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La fila Y = 0 está completa, así que sumándola obtenemos directamente una probabilidad "
                "marginal, sin necesidad de hipótesis alguna:"
                "<div class='formula-box'>p<sub>Y</sub>(0) = 2/9 + 1/3 + 1/9 = "
                "2/9 + 3/9 + 1/9 = 6/9 = 2/3</div>"
                "Como Y sólo toma los valores 0 y 1, la marginal de Y queda determinada por complementario:"
                "<div class='formula-box'>p<sub>Y</sub>(1) = 1 − 2/3 = 1/3</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P4_B", "B) Marginal de X imponiendo la independencia"):
            st.markdown("<div class='subsection-title'>B) Despejar p<sub>X</sub></div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Hasta ahora no hemos usado la hipótesis del enunciado. La independencia exige que cada celda sea "
                "el producto de sus marginales, P(X = x, Y = y) = P(X = x)·P(Y = y). Aplicándolo a las tres "
                "celdas conocidas y despejando p<sub>X</sub>, con p<sub>Y</sub>(0) = 2/3:<br><br>"
                "&nbsp;&nbsp;P(X = 0) = (2/9) / (2/3) = <b>1/3</b><br>"
                "&nbsp;&nbsp;P(X = 1) = (1/3) / (2/3) = <b>1/2</b><br>"
                "&nbsp;&nbsp;P(X = 2) = (1/9) / (2/3) = <b>1/6</b><br><br>"
                "Conviene comprobar que estos tres números forman una distribución legítima:<br>"
                "1/3 + 1/2 + 1/6 = (2 + 3 + 1)/6 = 1 ✓<br><br>"
                "Nótese que la comprobación no es automática: sale 1 porque la fila conocida sumaba exactamente "
                "p<sub>Y</sub>(0), que es justo lo que garantiza la coherencia del sistema."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P4_C", "C) Completar la fila Y = 1"):
            st.markdown("<div class='subsection-title'>C) Multiplicar marginales</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Con ambas marginales conocidas ya no queda nada por decidir: cada celda de la segunda fila es el "
                "producto de p<sub>X</sub>(x) por p<sub>Y</sub>(1) = 1/3.<br><br>"
                "&nbsp;&nbsp;P(X = 0, Y = 1) = (1/3)·(1/3) = <b>1/9</b><br>"
                "&nbsp;&nbsp;P(X = 1, Y = 1) = (1/2)·(1/3) = <b>1/6</b><br>"
                "&nbsp;&nbsp;P(X = 2, Y = 1) = (1/6)·(1/3) = <b>1/18</b><br><br>"
                "Suma de la segunda fila: 2/18 + 3/18 + 1/18 = 6/18 = 1/3 = p<sub>Y</sub>(1) ✓, y el total de la "
                "tabla es 2/3 + 1/3 = 1 ✓."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(joint_table_html(
                np.array([[2 / 9, 1 / 3, 1 / 9],
                          [1 / 9, 1 / 6, 1 / 18]]),
                ["0", "1", "2"], ["0", "1"],
                caption="Tabla completa"), unsafe_allow_html=True)

        if accordion_step("P4_D", "D) ¿Existe una única forma?"):
            st.markdown("<div class='subsection-title'>D) Unicidad</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Sí: la solución es única.</b> El argumento es una cadena de determinaciones sin margen "
                "de elección en ningún eslabón:<br><br>"
                "1. La fila Y = 0 está completa ⟹ p<sub>Y</sub>(0) = 2/3 queda fijada.<br>"
                "2. Y <b>toma sólo dos valores</b> ⟹ p<sub>Y</sub>(1) = 1/3 queda fijada por complementario.<br>"
                "3. La independencia convierte cada celda conocida en una ecuación con una sola incógnita, "
                "p<sub>X</sub>(x) = p<sub>ij</sub> / p<sub>Y</sub>(0) ⟹ p<sub>X</sub> queda fijada.<br>"
                "4. Las celdas que faltan son productos de cantidades ya determinadas.<br><br>"
                "Si Y tomase tres o más valores, la 'masa' restante 1/3 podría "
                "repartirse de infinitas maneras entre las filas que faltan y el problema dejaría de tener "
                "solución única. Explóralo en la pestaña <i>Generalización</i>."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        tab_res, tab_gen = st.tabs(["Resuélvelo tú", "Generalización"])

        # ---------------- Resolver ajustando las marginales --------------------
        with tab_res:
            st.markdown(
                "<div class='content-box'><b>⚙️ Ajusta las marginales, no las celdas</b><br>"
                "<small style='color: var(--muted-fg);'>"
                "Cualquier tabla independiente se construye a partir de p<sub>X</sub> y p<sub>Y</sub>. "
                "Elige esas marginales (en dieciochoavos, para poder dar valores exactos) y busca la única "
                "combinación que reproduce la fila del enunciado."
                "</small></div>",
                unsafe_allow_html=True
            )

            a = st.slider("18 · P(X = 0)", 0, 18, 4, 1, key="e_a")
            b = st.slider("18 · P(X = 1)", 0, 18, 8, 1, key="e_b")
            c = st.slider("18 · P(Y = 1)", 0, 18, 9, 1, key="e_c")

            if a + b > 18:
                st.markdown(
                    "<div class='ko-box'>P(X=0) + P(X=1) > 1: la marginal de X no es válida. "
                    "Reduce alguno de los dos primeros deslizadores.</div>",
                    unsafe_allow_html=True)
            else:
                pX = np.array([a, b, 18 - a - b]) / 18.0
                pY1 = c / 18.0
                pY0 = 1.0 - pY1
                P_user = np.vstack([pX * pY0, pX * pY1])

                err = float(np.max(np.abs(P_user[0, :] - FILA_DADA)))
                resuelto = err < 1e-9

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"<div class='metric-box metric-third metric-a'>p<sub>Y</sub>(0)<br>"
                                f"{frac_str(pY0)}</div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-box metric-third metric-b'>Suma total<br>"
                                f"{P_user.sum():.4f}</div>", unsafe_allow_html=True)
                with m3:
                    clase = "result-likely" if resuelto else "result-unlikely"
                    st.markdown(f"<div class='metric-box metric-third {clase}'>Error máx. fila Y=0<br>"
                                f"{err:.4f}</div>", unsafe_allow_html=True)

                if resuelto:
                    st.markdown(
                        "<div class='ok-box'>✓ Fila Y = 0 reproducida exactamente. "
                        "p<sub>X</sub> = (1/3, 1/2, 1/6) y p<sub>Y</sub> = (2/3, 1/3): "
                        "es la única terna posible.</div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        "<div class='ko-box'>Todavía no coincide con el enunciado. "
                        "Pista: primero acierta p<sub>Y</sub>(0) = 2/3 sumando la fila dada; "
                        "después cada P(X = x) sale de dividir.</div>",
                        unsafe_allow_html=True)

                pos = np.arange(3)
                pcmp = figure(title="Fila Y = 0: enunciado frente a tu construcción",
                              x_axis_label="valor de X", y_axis_label="probabilidad",
                              width=470, height=320, tools="", toolbar_location=None)
                pcmp.vbar(x=pos - 0.18, top=FILA_DADA, width=0.34, fill_color=UBU_RED,
                          line_color="white", legend_label="enunciado")
                pcmp.vbar(x=pos + 0.18, top=P_user[0, :], width=0.34, fill_color=UBU_YELLOW,
                          line_color="white", legend_label="tu tabla")
                pcmp.xaxis.ticker = [0, 1, 2]
                pcmp.legend.location = "top_right"
                pcmp.legend.label_text_font_size = "12px"
                streamlit_bokeh(style_axes(pcmp))

                st.markdown(joint_table_html(
                    P_user, ["0", "1", "2"], ["0", "1"],
                    caption="Tabla generada por tus marginales (independiente por construcción)"),
                    unsafe_allow_html=True)

                st.markdown(
                    "<div class='content-box'>"
                    "<b>Detalle a tener en cuenta:</b> esta tabla es independiente para <i>cualquier</i> posición "
                    "de los deslizadores, porque se construye multiplicando marginales. Lo que restringe el "
                    "problema no es la independencia por sí sola, sino la independencia <b>más</b> el dato de que "
                    "la fila Y = 0 debe valer (2/9, 1/3, 1/9)."
                    "</div>",
                    unsafe_allow_html=True
                )

        # ---------------- Generalización: ¿y si Y tomara más valores? ----------
        with tab_gen:
            st.markdown(
                "<div class='content-box'><b>⚙️ ¿De qué depende la unicidad?</b><br>"
                "<small style='color: var(--muted-fg);'>"
                "Mantenemos la fila Y = 0 del enunciado y la independencia, pero permitimos que Y tome más "
                "valores. El deslizador de reparto mueve la masa sobrante entre las filas nuevas."
                "</small></div>",
                unsafe_allow_html=True
            )

            n_y = st.slider("Número de valores que toma Y", 2, 5, 2, 1, key="g_ny")
            t = st.slider("Reparto de la masa restante entre las filas nuevas", 0.0, 1.0, 0.5, 0.05,
                          key="g_t")

            pX_fix = np.array([1 / 3, 1 / 2, 1 / 6])
            pY0_fix = 2 / 3
            m = n_y - 1
            w = np.full(m, t / m)
            w[0] += (1 - t)
            pY_rest = (1 - pY0_fix) * w
            pY_full = np.concatenate([[pY0_fix], pY_rest])
            P_gen = np.outer(pY_full, pX_fix)

            unico = (m == 1)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"<div class='metric-box metric-third metric-a'>Celdas por determinar<br>"
                            f"{3 * m}</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-box metric-third metric-c'>Masa por repartir<br>"
                            f"1/3 entre {m} fila{'s' if m > 1 else ''}</div>",
                            unsafe_allow_html=True)
            with m3:
                clase = "result-likely" if unico else "result-bayes"
                st.markdown(f"<div class='metric-box metric-third {clase}'>Soluciones<br>"
                            f"{'única' if unico else 'infinitas'}</div>", unsafe_allow_html=True)

            st.markdown(joint_table_html(
                P_gen, ["0", "1", "2"], [str(j) for j in range(n_y)],
                caption=f"Completación con Y ∈ {{0, …, {n_y - 1}}} (independiente y compatible "
                        f"con la fila dada)",
                fmt=lambda v: f"{v:.4f}"), unsafe_allow_html=True)

            pg = heatmap_pmf(P_gen, [0, 1, 2], list(range(n_y)),
                             "p(x, y) de la completación actual", palette=PALETTE_BLUE,
                             fmt="{:.3f}", width=470, height=340)
            streamlit_bokeh(pg)

            if unico:
                st.markdown(
                    "<div class='ok-box'>Con Y tomando sólo dos valores, el deslizador de reparto no "
                    "tiene ningún efecto: no queda reparto posible. Ése es el caso del ejercicio 52.</div>",
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div class='ko-box'>Con {n_y} valores de Y, mover el reparto genera tablas distintas, "
                    f"todas ellas independientes y todas compatibles con la fila del enunciado. "
                    f"La solución deja de ser única.</div>",
                    unsafe_allow_html=True)

            st.markdown(
                "<div class='content-box'>"
                "<b>¿Por qué en el ejercicio 52 no hay nada que elegir?</b><br>"
                "Sumar la fila conocida da p<sub>Y</sub>(0) = 2/3, sin usar todavía ninguna hipótesis. "
                "Lo único que queda por decidir es cómo se reparte la masa restante, 1/3, entre las filas "
                "que faltan:<br><br>"
                "• Si Y <b>toma sólo dos valores</b>, esa masa pertenece entera a la única fila que falta: "
                "p<sub>Y</sub>(1) = 1/3, y no hay reparto que hacer. La independencia convierte entonces cada "
                "celda conocida en p<sub>X</sub>(x)·(2/3), de donde p<sub>X</sub> queda despejada, y las celdas "
                "que faltan son productos de cantidades ya determinadas.<br><br>"
                "• Si Y <b>toma tres o más valores</b>, ese 1/3 admite infinitos repartos. Cada uno produce una "
                "tabla distinta que sigue siendo independiente y sigue conteniendo la fila Y = 0 del enunciado: "
                "mueve el deslizador del reparto y compáralas.<br><br>"
                "Fíjate en que los valores concretos 2/9, 1/3, 1/9 no intervienen en este razonamiento. Lo que "
                "hace única a la solución es que la fila conocida esté completa y que Y tome sólo dos valores."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Conviene separar qué aporta cada hipótesis. Sin exigir independencia, el enunciado sólo obliga "
                "a que la segunda fila sume 1/3, así que valdrían (1/9, 1/9, 1/9), o (1/3, 0, 0), o infinitas "
                "más. Lo que fija cada celda por separado es la factorización "
                "P(X = xᵢ, Y = y<sub>j</sub>) = P(X = xᵢ)·P(Y = y<sub>j</sub>)."
            )

# =============================================================================
# 6. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Vectores Aleatorios</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2, nav3, nav4, nav5 = st.columns(5)

    if nav1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO", "open_step": "INTRO_A"}); st.rerun()
    if nav2.button("(I) Conjunta", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav3.button("(II) Marginales", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav4.button("(III) Condicionadas", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()
    if nav5.button("(IV) Ejercicio 52", use_container_width=True):
        st.session_state.update({"page": "P4", "open_step": "P4_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_conjunta,
        "P2": render_marginal,
        "P3": render_condicionada,
        "P4": render_ejercicio,
    }

    current_page = st.session_state["page"]
    if current_page in paginas:
        paginas[current_page]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
