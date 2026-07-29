import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
from scipy.stats import norm, uniform
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Variables Continuas")

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

# =============================================================================
# 4. APARTADO 1: INTRODUCCIÓN A VARIABLES ALEATORIAS CONTINUAS
# =============================================================================

def render_intro():
    """Apartado 1: Conceptos básicos de V.A. Continuas"""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Apartado 1: Variables Aleatorias Continuas</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='statement-box'>"
            "Una variable aleatoria continua toma infinitos valores en un intervalo. "
            "A diferencia de las discretas, la probabilidad de cualquier valor exacto es cero."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "A) Discretas vs Continuas"):
            st.markdown("<div class='subsection-title'>A) Discretas vs Continuas</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Variables Discretas:</b><br>"
                "Toman valores aislados (1, 2, 3, ...). P(X=k) > 0<br>"
                "Ejemplos: número de monedas, defectos, resultado de un dado.<br><br>"
                "<b>Variables Continuas:</b><br>"
                "Toman infinitos valores en un intervalo [a, b]. P(X=a) = 0<br>"
                "Ejemplos: altura, temperatura, tiempo, rendimiento."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler("¿Por qué P(X=1.5) = 0? Porque si hay infinitos valores en el intervalo, "
                   "cada uno individual tiene probabilidad 0. En su lugar, hablamos de P(a ≤ X ≤ b).")

        if accordion_step("INTRO_B", "B) De Puntos a Áreas"):
            st.markdown("<div class='subsection-title'>B) De Puntos a Áreas</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "En <b>variables discretas:</b> la probabilidad vive en puntos (gráfico de barras).<br>"
                "En <b>variables continuas:</b> la probabilidad vive bajo áreas de una curva (densidad).<br>"
                "P(a ≤ X ≤ b) = <b>área bajo la curva</b> entre a y b."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Ejemplo Visual: Altura de Personas</b></div>",
            unsafe_allow_html=True
        )

        # Generar distribución normal (escueto)
        x = np.linspace(150, 200, 300)
        y = norm.pdf(x, loc=175, scale=10)

        p = figure(
            title="Distribución de alturas (Normal)",
            x_axis_label="Altura (cm)",
            y_axis_label="Densidad f(x)",
            width=500,
            height=350,
            toolbar_location=None,
            tools=""
        )
        p.line(x, y, line_width=2.5, color=BLUE_LINE)
        p.varea(x=x, y1=0, y2=y, alpha=0.3, color=BLUE_LINE)
        p.title.text_font_size = "16px"
        streamlit_bokeh(p)

        st.markdown(
            "<div class='content-box'>"
            "La altura es una magnitud continua: puede tomar cualquier valor en un rango sin saltos. "
            "Por eso la probabilidad de un valor exacto P(X = 175) = 0, y en su lugar hablamos de P(a ≤ X ≤ b) "
            "</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 5. APARTADO 2: PDF Y CDF
# =============================================================================

def render_pdf_cdf():
    """Apartado 2: Funciones de distribución y propiedades"""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Apartado 2: PDF y CDF</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='statement-box'>"
            "PDF (f(x)) mide densidad de probabilidad. CDF (F(x)) mide probabilidad acumulada."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("PDF_A", "A) Función de Densidad (PDF)"):
            st.markdown("<div class='subsection-title'>A) Función de Densidad de Probabilidad (PDF)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='formula-box'>f(x) ≥ 0  para todo x</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>∫<sub>-∞</sub><sup>∞</sup> f(x)dx = 1</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>P(a ≤ X ≤ b) = ∫<sub>a</sub><sup>b</sup> f(x)dx</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Propiedades:</b><br>"
                "1️⃣ f(x) ≥ 0 (no negatividad)<br>"
                "2️⃣ Área total bajo f(x) = 1<br>"
                "3️⃣ P(X = c) = 0 para cualquier valor exacto c<br>"
                "4️⃣ f(x) NO es una probabilidad. Mide la concentración de probabilidad por unidad."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("PDF_B", "B) Función de Distribución Acumulada (CDF)"):
            st.markdown("<div class='subsection-title'>B) Función de Distribución Acumulada (CDF)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='formula-box'>F(x) = P(X ≤ x) = ∫<sub>-∞</sub><sup>x</sup> f(t)dt</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Propiedades:</b><br>"
                "1️⃣ 0 ≤ F(x) ≤ 1 (acotada entre 0 y 1)<br>"
                "2️⃣ F(x) es monótona creciente<br>"
                "3️⃣ F'(x) = f(x)<br>"
                "4️⃣ lim(x→-∞) F(x) = 0<br>"
                "5️⃣ lim(x→+∞) F(x) = 1"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler("La relación F'(x) = f(x) es fundamental: CDF es la integral de PDF, y PDF es la derivada de CDF.")

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Demostración Visual: Uniforme</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Variar los parámetros a y b para ver cómo cambian PDF y CDF."
            "</small></div>",
            unsafe_allow_html=True
        )

        a_param = st.slider("Parámetro a (inicio)", 0.0, 5.0, 2.0, 0.5)
        b_param = st.slider("Parámetro b (fin)", 5.0, 10.0, 8.0, 0.5)

        if a_param >= b_param:
            st.error("⚠️ a debe ser menor que b")
            return

        # Generar datos
        x = np.linspace(0, 10, 500)
        f_x = np.where((x >= a_param) & (x <= b_param), 1/(b_param - a_param), 0)
        
        # CDF Uniforme
        F_x = np.zeros_like(x)
        F_x[x < a_param] = 0
        F_x[(x >= a_param) & (x <= b_param)] = (x[(x >= a_param) & (x <= b_param)] - a_param) / (b_param - a_param)
        F_x[x > b_param] = 1

        # Gráfico PDF
        st.markdown("<small style='text-align: center; color: var(--muted-fg);'><b>PDF: f(x)</b></small>", unsafe_allow_html=True)
        p_pdf = figure(
            title="Función de Densidad (Uniforme)",
            x_axis_label="x",
            y_axis_label="f(x)",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p_pdf.line(x, f_x, line_width=2.5, color=BLUE_LINE)
        p_pdf.varea(x=x, y1=0, y2=f_x, alpha=0.3, color=BLUE_LINE)
        p_pdf.title.text_font_size = "14px"
        streamlit_bokeh(p_pdf)

        # Gráfico CDF
        st.markdown("<small style='text-align: center; color: var(--muted-fg);'><b>CDF: F(x)</b></small>", unsafe_allow_html=True)
        p_cdf = figure(
            title="Función de Distribución Acumulada (Uniforme)",
            x_axis_label="x",
            y_axis_label="F(x)",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p_cdf.line(x, F_x, line_width=2.5, color=GREEN_LINE)
        p_cdf.title.text_font_size = "14px"
        streamlit_bokeh(p_cdf)

        st.markdown(
            "<div class='content-box'>"
            f"<b>Observación:</b> PDF tiene altura 1/{(b_param - a_param):.2f} en [{a_param:.1f}, {b_param:.1f}]. "
            f"CDF es una función a trozos que crece de 0 a 1. La pendiente de CDF = altura de PDF."
            "</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 6. APARTADO 3: INTEGRAL DEFINIDA Y MOMENTOS
# =============================================================================

def render_integral_momentos():
    """Apartado 3: Integral definida y momentos"""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Apartado 3: Integral y Momentos</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='statement-box'>"
            "La integral definida no es solo un cálculo matemático: tiene significado probabilístico. "
            "Los momentos extraen información de la distribución mediante integrales."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INT_A", "A) Integral Definida = Probabilidad"):
            st.markdown("<div class='subsection-title'>A) Integral Definida = Probabilidad</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='formula-box'>P(a ≤ X ≤ b) = ∫<sub>a</sub><sup>b</sup> f(x)dx</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "Toda integral definida de la PDF es una probabilidad.<br>"
                "∫<sub>a</sub><sup>b</sup> f(x)dx = área bajo la curva entre a y b = probabilidad de que X caiga en [a, b]."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler("Ejemplo: Si f(x) es Normal estándar, entonces ∫<sub>-1</sub><sup>1</sup> f(x)dx ≈ 0.68 significa "
                   "que hay 68% de probabilidad de que X esté entre -1 y 1.")

        if accordion_step("INT_B", "B) Momentos: Esperanza y Varianza"):
            st.markdown("<div class='subsection-title'>B) Momentos: Esperanza y Varianza</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='formula-box'>Esperanza: E[X] = μ = ∫<sub>-∞</sub><sup>∞</sup> x·f(x)dx</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'><small>"
                "E[X] es el 'centro de masa' de la distribución. Mide dónde está centrada."
                "</small></div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>Varianza: Var[X] = σ² = ∫<sub>-∞</sub><sup>∞</sup> (x - μ)²·f(x)dx</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'><small>"
                "Var[X] mide la dispersión alrededor de la media. σ = √Var[X] es la desviación estándar."
                "</small></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Derivación de Varianza para Uniforme[a,b]:</b><br><br>"
                "Var[X] = ∫<sub>a</sub><sup>b</sup> (x - μ)²·f(x)dx<br><br>"
                "= ∫<sub>a</sub><sup>b</sup> (x - (a+b)/2)²·(1/(b-a))dx<br><br>"
                "Haciendo cambio de variable u = x - (a+b)/2:<br><br>"
                "= ∫<sub>-L/2</sub><sup>L/2</sup> u²·(1/L) du&nbsp;&nbsp;&nbsp;&nbsp;(donde L = b-a)<br><br>"
                "= (1/L)·[u³/3]<sub>-L/2</sub><sup>L/2</sup><br><br>"
                "= (1/L)·(2/3)·(L/2)³<br><br>"
                "= <b>(b-a)²/12</b> ✓"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Uniforme</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Variar parámetros para ver cómo cambian E[X] y Var[X]."
            "</small></div>",
            unsafe_allow_html=True
        )

        a_int = st.slider("a (inicio)", 0.0, 5.0, 2.0, 0.5, key="integral_a")
        b_int = st.slider("b (fin)", 5.0, 10.0, 8.0, 0.5, key="integral_b")

        if a_int >= b_int:
            st.error("⚠️ a debe ser menor que b")
            return

        # Cálculos para Uniforme
        mu = (a_int + b_int) / 2
        sigma2 = ((b_int - a_int)**2) / 12
        sigma = np.sqrt(sigma2)

        # Generar x y f(x)
        x = np.linspace(0, 10, 500)
        f_x = np.where((x >= a_int) & (x <= b_int), 1/(b_int - a_int), 0)

        # Gráfico
        p = figure(
            title="PDF con E[X] y ±σ",
            x_axis_label="x",
            y_axis_label="f(x)",
            width=500,
            height=350,
            toolbar_location=None,
            tools=""
        )
        p.line(x, f_x, line_width=2.5, color=BLUE_LINE)
        p.varea(x=x, y1=0, y2=f_x, alpha=0.3, color=BLUE_LINE)

        y_max = 1 / (b_int - a_int) + 0.05
        p.line([mu, mu], [0, y_max], line_width=2.5, color=UBU_RED, legend_label="E[X]")
        p.line([mu - sigma, mu - sigma], [0, y_max], line_width=1.5, color=ORANGE_ACCENT, line_dash="dashed")
        p.line([mu + sigma, mu + sigma], [0, y_max], line_width=1.5, color=ORANGE_ACCENT, line_dash="dashed")

        p.title.text_font_size = "14px"
        p.legend.location = "top_right"
        streamlit_bokeh(p)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>E[X]<br>{mu:.3f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>σ<br>{sigma:.3f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>Var[X]<br>{sigma2:.3f}</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='content-box'><small>"
            f"<b>Para Uniforme[{a_int:.1f}, {b_int:.1f}]:</b><br>"
            f"E[X] = (a+b)/2 = {mu:.3f}<br>"
            f"Var[X] = (b-a)²/12 = {sigma2:.3f}"
            "</small></div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 7. APARTADO 4: EJERCICIO RESUELTO
# =============================================================================

def render_ejercicio():
    """Apartado 4: Ejercicio resuelto"""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Apartado 4: Ejercicio Resuelto</div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='statement-box'>"
            "<b>Problema 067:</b> Variable Aleatoria Continua — Función de Densidad y Distribución<br><br>"
            "Sea X una variable aleatoria continua con función de densidad:<br><br>"
            "f(x) = "
            "<div style='display: flex; align-items: center;'>"
            "<div style='font-size: 60px; line-height: 0.8; margin-right: 10px;'>{</div>"
            "<div style='text-align: left;'>"
            "k·x²&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si 0 ≤ x ≤ 4<br>"
            "0&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;en el resto"
            "</div>"
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("EJ_A", "A) Cálculo del parámetro k"):
            st.markdown("<div class='subsection-title'>A) Cálculo del valor de k</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Para que f_X(x) sea una función de densidad de probabilidad válida, el área total bajo la curva debe ser igual a 1:"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>∫<sub>-∞</sub><sup>∞</sup> f(x) dx = 1</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "Dado que la función es distinta de cero únicamente en [0, 4]:<br><br>"
                "∫<sub>0</sub><sup>4</sup> k·x² dx = 1<br><br>"
                "k·[x³/3]<sub>0</sub><sup>4</sup> = 1<br><br>"
                "k·(64/3) = 1<br><br>"
                "<b>k = 3/64 = 0.046875</b>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("EJ_B", "B) Función de distribución acumulada F_X(x)"):
            st.markdown("<div class='subsection-title'>B) Función de Distribución Acumulada F_X(x)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "F_X(x) = P(X ≤ x) = ∫<sub>-∞</sub><sup>x</sup> f(t) dt<br><br>"
                "Analizamos en tres tramos:"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>"
                "f_X(x) = "
                "<div style='display: flex; align-items: center;'>"
                "<div style='font-size: 80px; line-height: 0.8; margin-right: 15px;'>{</div>"
                "<div style='text-align: left;'>"
                "0&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si x < 0<br>"
                "(3/64)·x²&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si 0 ≤ x ≤ 4<br>"
                "0&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si x > 4"
                "</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Por lo tanto, la CDF es:</b>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>"
                "F_X(x) = "
                "<div style='display: flex; align-items: center;'>"
                "<div style='font-size: 80px; line-height: 0.8; margin-right: 15px;'>{</div>"
                "<div style='text-align: left;'>"
                "0&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si x < 0<br>"
                "x³/64&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si 0 ≤ x ≤ 4<br>"
                "1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;si x > 4"
                "</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("EJ_C", "C) Esperanza y Varianza"):
            st.markdown("<div class='subsection-title'>C) Esperanza E(X) y Varianza V(X)</div>", unsafe_allow_html=True)
            
            st.markdown(
                "<div class='content-box'><b>Cálculo de la Esperanza E(X):</b></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>E(X) = ∫<sub>-∞</sub><sup>∞</sup> x·f(x) dx = ∫<sub>0</sub><sup>4</sup> x·(3/64)·x² dx</b><br><br>"
                "= (3/64)·∫<sub>0</sub><sup>4</sup> x³ dx<br><br>"
                "= (3/64)·[x⁴/4]<sub>0</sub><sup>4</sup><br><br>"
                "= (3/64)·(4⁴/4 - 0)<br><br>"
                "= (3/64)·(256/4)<br><br>"
                "= (3/64)·64<br><br>"
                "= <b>3</b>"
            )

            st.markdown(
                "<div class='content-box'><b>Cálculo de la Varianza V(X) (usando V(X) = E(X²) - [E(X)]²):</b></div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Paso 1: Calcular E(X²)</b><br><br>"
                "E(X²) = ∫<sub>0</sub><sup>4</sup> x²·(3/64)·x² dx<br><br>"
                "= (3/64)·∫<sub>0</sub><sup>4</sup> x⁴ dx<br><br>"
                "= (3/64)·[x⁵/5]<sub>0</sub><sup>4</sup><br><br>"
                "= (3/64)·(4⁵/5 - 0)<br><br>"
                "= (3/64)·(1024/5)<br><br>"
                "= (3·1024)/(64·5)<br><br>"
                "= 3072/320<br><br>"
                "= 48/5 = <b>9.6</b><br><br>"
                "<b>Paso 2: Aplicar la fórmula V(X) = E(X²) - [E(X)]²</b><br><br>"
                "V(X) = 9.6 - 3²<br><br>"
                "= 9.6 - 9<br><br>"
                "= <b>0.6</b> (o equivalentemente, 3/5)"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Visualización de f_X(x) y F_X(x)</b></div>",
            unsafe_allow_html=True
        )

        # Generar datos
        x = np.linspace(-0.5, 4.5, 400)
        k_value = 3/64
        f_x = np.where((x >= 0) & (x <= 4), k_value * x**2, 0)
        
        # CDF
        F_x = np.zeros_like(x)
        F_x[x < 0] = 0
        F_x[(x >= 0) & (x <= 4)] = (x[(x >= 0) & (x <= 4)]**3) / 64
        F_x[x > 4] = 1

        # Gráfico PDF
        st.markdown("<small style='text-align: center; color: var(--muted-fg);'><b>Función de Densidad: f_X(x) = (3/64)·x²</b></small>", unsafe_allow_html=True)
        p_pdf = figure(
            title="PDF del Problema 067",
            x_axis_label="x",
            y_axis_label="f_X(x)",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p_pdf.line(x, f_x, line_width=2.5, color=BLUE_LINE)
        p_pdf.varea(x=x, y1=0, y2=f_x, alpha=0.3, color=BLUE_LINE)
        p_pdf.title.text_font_size = "14px"
        streamlit_bokeh(p_pdf)

        # Gráfico CDF
        st.markdown("<small style='text-align: center; color: var(--muted-fg);'><b>Función Acumulada: F_X(x)</b></small>", unsafe_allow_html=True)
        p_cdf = figure(
            title="CDF del Problema 067",
            x_axis_label="x",
            y_axis_label="F_X(x)",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p_cdf.line(x, F_x, line_width=2.5, color=GREEN_LINE)
        p_cdf.title.text_font_size = "14px"
        streamlit_bokeh(p_cdf)

        # Métricas finales
        st.markdown("<small style='text-align: center; color: var(--muted-fg);'><b>Resultados</b></small>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>k<br>3/64</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>E[X]<br>3.000</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>V[X]<br>0.600</div>", unsafe_allow_html=True)

# =============================================================================
# 8. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Variables Aleatorias Continuas</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # Navegación
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state["page"] = "INTRO"
        st.rerun()
    if nav_col2.button("PDF y CDF", use_container_width=True):
        st.session_state["page"] = "PDF_CDF"
        st.rerun()
    if nav_col3.button("Integral y Momentos", use_container_width=True):
        st.session_state["page"] = "INTEGRAL"
        st.rerun()
    if nav_col4.button("Ejercicio", use_container_width=True):
        st.session_state["page"] = "EJERCICIO"
        st.rerun()

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # Mostrar apartado seleccionado
    if st.session_state["page"] == "INTRO":
        render_intro()
    elif st.session_state["page"] == "PDF_CDF":
        render_pdf_cdf()
    elif st.session_state["page"] == "INTEGRAL":
        render_integral_momentos()
    elif st.session_state["page"] == "EJERCICIO":
        render_ejercicio()

if __name__ == "__main__":
    main()
