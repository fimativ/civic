import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
from scipy.stats import norm, binom
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Variables Aleatorias")

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

.result-bayes {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;  border-color: {UBU_YELLOW} !important; }}
.result-likely {{ background: {GREEN_LINE} !important; color: #ffffff !important; border-color: {GREEN_LINE} !important; }}
.result-unlikely {{ background: #d32f2f !important; color: #ffffff !important; border-color: #d32f2f !important; }}

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
    if "simulaciones" not in st.session_state:
        st.session_state["simulaciones"] = {}

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
# 4. PÁGINAS
# =============================================================================

def render_intro():
    """Introducción: Definición y propiedades de variables aleatorias."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: Variables Aleatorias</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Una variable aleatoria es una función que asigna valores numéricos a los resultados "
            "de un experimento aleatorio. Transforma los resultados inciertos de un experimento en números " 
            "sobre los que podemos operar."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "Definición Formal"):
            st.markdown("<div class='subsection-title'>A) Definición Formal</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea Ω el espacio muestral de un experimento aleatorio. Una <b>variable aleatoria</b> X es una aplicación:<br>"
                "<div class='formula-box'>X : Ω → ℝ</div>"
                "que asigna a cada resultado ω ∈ Ω un número real X(ω).<br><br>"
                "<b>Definición por preimagen:</b> Para cualquier conjunto de Borel B ⊆ ℝ, definimos el evento<br>"
                "<div class='formula-box'>X⁻¹(B) = {X ∈ B} = {ω ∈ Ω : X(ω) ∈ B} ∈ 𝒜</div>"
                "donde 𝒜 es la σ-álgebra del espacio muestral. Esto garantiza que podemos asignar probabilidades."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Ejemplo: Lanzar dos dados. Ω = {(1,1), (1,2), ..., (6,6)}. Si X = suma, entonces X⁻¹({7}) = {(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)}, y P(X=7) = 6/36."
            )

        if accordion_step("INTRO_B", "Propiedades Fundamentales"):
            st.markdown("<div class='subsection-title'>B) Propiedades Fundamentales</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>1. Linealidad de la esperanza:</b><br>"
                "E[aX + bY] = a·E[X] + b·E[Y]<br><br>"
                "<b>2. Varianza de sumas:</b> (si X e Y independientes)<br>"
                "Var(X + Y) = Var(X) + Var(Y)<br><br>"
                "<b>3. Desviación estándar:</b><br>"
                "σ(X) = √Var(X)<br><br>"
                "<b>4. Teorema del Límite Central:</b><br>"
                "La suma de muchas v.a. independientes tiende a una distribución normal."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Clasificación de Variables Aleatorias</b></div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='content-box'>"
            "<b style='color: #2b6cb0;'>Discretas:</b><br>"
            "Toman valores en un conjunto finito o numerable.<br>"
            "Ejemplos: número de caras en n lanzamientos, número de defectos, resultado de un dado.<br><br>"
            "<b style='color: #2e7d32;'>Continuas:</b><br>"
            "Toman valores en un intervalo de ℝ.<br>"
            "Ejemplos: altura, temperatura, tiempo de espera, rendimiento de acciones."
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='content-box'><b>Medidas de Centralidad y Dispersión:</b><br>"
            "• <b>Media (Esperanza)</b>: E[X] = Σ x·P(X=x)<br>"
            "• <b>Varianza</b>: Var(X) = E[(X - E[X])²]<br>"
            "• <b>Desv. Estándar</b>: σ = √Var(X)</div>",
            unsafe_allow_html=True
        )

def render_discrete():
    """Sección I: Variables aleatorias discretas con simulación."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Variables Aleatorias Discretas</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Las variables aleatorias discretas toman un número finito o contable de valores. "
            "Un ejemplo clásico es el número de éxitos en ensayos independientes: la distribución Binomial."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Distribución Binomial"):
            st.markdown("<div class='subsection-title'>A) Distribución Binomial B(n,p)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Cuenta el número de éxitos X en n ensayos independientes, cada uno con probabilidad p de éxito:<br><br>"
                "<div class='formula-box'>P(X = k) = C(n,k) · p<sup>k</sup> · (1-p)<sup>n-k</sup></div>"
                "<b>Esperanza:</b> E[X] = n·p<br>"
                "<b>Varianza:</b> Var(X) = n·p·(1-p)"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "B) Ejemplo: Lanzar una moneda 10 veces"):
            st.markdown("<div class='subsection-title'>B) Ejemplo: Lanzar una moneda 10 veces</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea X = número de caras en 10 lanzamientos (cada lanzamiento tiene p = 0.5 de éxito).<br>"
                "Entonces X ~ B(10, 0.5)<br><br>"
                "<b>E[X] = 10 · 0.5 = 5 caras esperadas</b><br>"
                "<b>Var(X) = 10 · 0.5 · 0.5 = 2.5</b>"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler("La probabilidad de obtener exactamente 7 caras es P(X=7) ≈ 0.117 (11.7%)")

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Monedas</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Se lanzan n monedas repetidamente. Contamos cuántas caras salen en cada experimento. "
            "El histograma muestra la distribución observada."
            "</small></div>",
            unsafe_allow_html=True
        )

        n_lanzamientos = st.slider("n: Número de lanzamientos por experimento", 5, 50, 10, 1)
        p_exito = st.slider("p: Probabilidad de éxito (caras)", 0.0, 1.0, 0.5, 0.05)
        n_repeticiones = st.slider("Número de repeticiones (simulaciones)", 100, 5000, 1000, 100)

        # Simulación: Generamos n_repeticiones experimentos de n_lanzamientos cada uno
        # Cada experimento cuenta cuántas caras salen (éxitos)
        np.random.seed(42)
        resultados = np.random.binomial(n_lanzamientos, p_exito, n_repeticiones)

        # Métricas teóricas vs observadas
        media_teorica = n_lanzamientos * p_exito
        var_teorica = n_lanzamientos * p_exito * (1 - p_exito)
        desv_teorica = np.sqrt(var_teorica)

        m1, m2, m3 = st.columns(3)
        with m1:
            media_sim = np.mean(resultados)
            st.markdown(f"<div class='metric-box metric-a'>Media Observada<br>{media_sim:.2f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box'>Media Teórica<br>{media_teorica:.2f}</div>", unsafe_allow_html=True)
        with m3:
            desv_sim = np.std(resultados)
            st.markdown(f"<div class='metric-box'>Desv. Est. Observada<br>{desv_sim:.2f}</div>", unsafe_allow_html=True)

        # Histograma con Bokeh
        hist, edges = np.histogram(resultados, bins=np.arange(0, n_lanzamientos + 2) - 0.5)

        p = figure(
            title=f"Distribución Binomial B({n_lanzamientos}, {p_exito}) - {n_repeticiones} simulaciones",
            x_axis_label="Número de Caras Obtenidas",
            y_axis_label="Frecuencia Observada",
            width=450,
            height=320,
            toolbar_location=None,
            tools=""
        )
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=2, alpha=0.8)
        p.title.text_font_size = "16px"
        p.xaxis.axis_label_text_font_size = "14px"
        p.yaxis.axis_label_text_font_size = "14px"

        streamlit_bokeh(p)

        # Tabla de probabilidades teóricas
        st.markdown(
            "<div class='content-box'><b>Probabilidades Teóricas del ejemplo B):</b><br>",
            unsafe_allow_html=True
        )
        probs = binom.pmf(range(0, n_lanzamientos + 1), n_lanzamientos, p_exito)
        df_probs = []
        for k in range(0, min(n_lanzamientos + 1, 12)):
            df_probs.append(f"P(X={k}) = {probs[k]:.4f}")
        st.markdown(
            "<div class='content-box'>" + "<br>".join(df_probs) + "</div>",
            unsafe_allow_html=True
        )

def render_pdf_cdf():
    """Sección II: Función de Densidad (PDF) y Función de Distribución Acumulada (CDF) para v.a. discretas."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) Función de Densidad y Distribución (Discretas)</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Para variables aleatorias discretas, usamos la función de densidad (Probability Density Function) y la función de "
            "distribución acumulada (Cumulative Distribution Function) para caracterizar su comportamiento probabilístico."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Función de Densidad (PDF)"):
            st.markdown("<div class='subsection-title'>A) Función de Densidad de Probabilidad (PDF)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Para v.a. discreta:</b><br>"
                "p(k) = P(X = k) asigna una probabilidad a cada valor k posible.<br>"
                "<div class='formula-box'>P(X = k) = p(k)</div>"
                "<b>Propiedades:</b><br>"
                "• p(k) ≥ 0 para todo k<br>"
                "• Σ<sub>k</sub> p(k) = 1 (suma de todas las probabilidades)"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) Función de Distribución Acumulada (CDF)"):
            st.markdown("<div class='subsection-title'>B) Función de Distribución Acumulada (CDF)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "F(k) = P(X ≤ k) acumula las probabilidades hasta el valor k.<br><br>"
                "<div class='formula-box'>F(k) = Σ<sub>i≤k</sub> p(i)</div>"
                "<b>Propiedades:</b><br>"
                "• F(-∞) = 0 y F(∞) = 1<br>"
                "• F es no-decreciente (escalonada)<br>"
                "• p(k) = F(k) - F(k-1)"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_C", "C) Relación entre PDF y CDF"):
            st.markdown("<div class='subsection-title'>C) Relación entre PDF y CDF</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Diferencias importantes:</b><br>"
                "• PDF da la probabilidad en cada punto k<br>"
                "• CDF acumula probabilidades desde -∞ hasta k<br>"
                "• En PDF: Σ p(k) = 1<br>"
                "• En CDF: crece de 0 a 1 en forma escalonada<br><br>"
                "Para cualquier intervalo:<br>"
                "P(a ≤ X ≤ b) = F(b) - F(a-1)"
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización Interactiva: Distribución Binomial B(n,p)</b></div>",
            unsafe_allow_html=True
        )

        n_param = st.slider("n: Número de ensayos", 5, 50, 20, 1)
        p_param = st.slider("p: Probabilidad de éxito", 0.1, 0.9, 0.5, 0.05)

        # Generar PMF y CDF
        x_vals = np.arange(0, n_param + 1)
        pmf_vals = binom.pmf(x_vals, n_param, p_param)
        cdf_vals = binom.cdf(x_vals, n_param, p_param)

        # Métricas teóricas
        media_teorica = n_param * p_param
        var_teorica = n_param * p_param * (1 - p_param)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>E[X] = np<br>{media_teorica:.2f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Var(X) = np(1-p)<br>{var_teorica:.2f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box'>σ = √Var(X)<br>{np.sqrt(var_teorica):.2f}</div>", unsafe_allow_html=True)

        # Selector de qué graficar
        plot_type = st.radio("Mostrar:", ["PDF (Función de Densidad)", "CDF (Distribución Acumulada)"], 
                             horizontal=True, label_visibility="collapsed")

        if plot_type == "PDF (Función de Densidad)":
            p = figure(
                title=f"Función de Densidad de Probabilidad B({n_param},{p_param})",
                x_axis_label="Valor k",
                y_axis_label="P(X = k)",
                width=450,
                height=350,
                toolbar_location=None,
                tools=""
            )
            # Stem plot: líneas verticales + puntos
            p.segment(x0=x_vals, y0=0, x1=x_vals, y1=pmf_vals, 
                     line_width=3, color=BLUE_LINE, alpha=0.8)
            p.circle(x_vals, pmf_vals, size=8, color=UBU_RED, alpha=0.9)
            p.title.text_font_size = "16px"
            p.xaxis.axis_label_text_font_size = "14px"
            p.yaxis.axis_label_text_font_size = "14px"
            streamlit_bokeh(p)
            
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> Cada punto muestra P(X=k). "
                "La suma de todas las probabilidades = 1</div>",
                unsafe_allow_html=True
            )
        else:
            p = figure(
                title=f"Función de Distribución Acumulada B({n_param},{p_param})",
                x_axis_label="Valor k",
                y_axis_label="F(k) = P(X ≤ k)",
                width=450,
                height=350,
                toolbar_location=None,
                tools=""
            )
            # Escalera: líneas horizontales y saltos
            for i in range(len(x_vals)-1):
                p.segment(x0=x_vals[i], y0=cdf_vals[i], x1=x_vals[i+1], y1=cdf_vals[i],
                         line_width=3, color=GREEN_LINE, alpha=0.8)
                p.segment(x0=x_vals[i+1], y0=cdf_vals[i], x1=x_vals[i+1], y1=cdf_vals[i+1],
                         line_width=2, color=GREEN_LINE, alpha=0.5)
            p.circle(x_vals, cdf_vals, size=8, color=UBU_RED, alpha=0.9)
            p.title.text_font_size = "16px"
            p.xaxis.axis_label_text_font_size = "14px"
            p.yaxis.axis_label_text_font_size = "14px"
            streamlit_bokeh(p)
            
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> CDF crece de 0 a 1 en forma escalonada. "
                f"P(X ≤ {n_param//2}) = {cdf_vals[n_param//2]:.3f}</div>",
                unsafe_allow_html=True
            )

def render_horse_race():
    """Sección III: Operaciones con variables aleatorias - Varga's Horse Race."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) Carrera de Caballos de Varga</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "En una carrera, cada caballo tiene una velocidad aleatoria. Podemos sumar, restar y multiplicar "
            "variables aleatorias para analizar diferencias de rendimiento y combinaciones de estrategias."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Suma de Variables Aleatorias"):
            st.markdown("<div class='subsection-title'>A) Suma de Variables Aleatorias</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si X e Y son independientes con E[X] = μ<sub>X</sub> y E[Y] = μ<sub>Y</sub>:<br><br>"
                "<div class='formula-box'>E[X + Y] = E[X] + E[Y]</div>"
                "<div class='formula-box'>Var(X + Y) = Var(X) + Var(Y)</div>"
                "<b>En la carrera:</b> Velocidad total de dos caballos = V₁ + V₂"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_B", "B) Diferencia de Variables Aleatorias"):
            st.markdown("<div class='subsection-title'>B) Diferencia de Variables Aleatorias</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La diferencia entre dos v.a. independientes:<br><br>"
                "<div class='formula-box'>E[X - Y] = E[X] - E[Y]</div>"
                "<div class='formula-box'>Var(X - Y) = Var(X) + Var(Y)</div>"
                "✓ <b>Nota:</b> ¡La varianza se SUMA, no se resta! Porque restamos los valores, no sus varianzas.<br>"
                "Realiza la demostración (usando la definición de varianza para demostrarlo.<br><br>"
                "<b>En la carrera:</b> Ventaja de un caballo sobre otro = V₁ - V₂"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_C", "C) Producto de Variables Aleatorias"):
            st.markdown("<div class='subsection-title'>C) Producto de Variables Aleatorias</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si X e Y son independientes:<br><br>"
                "<div class='formula-box'>E[X · Y] = E[X] · E[Y]</div>"
                "La varianza es más compleja. Para variables positivas independientes:<br>"
                "<div class='formula-box'>Var(X·Y) = E[X]²Var(Y) + E[Y]²Var(X) + Var(X)Var(Y)</div>"
                "<b>En la carrera:</b> Ganancia de una apuesta = Velocidad × Factor de riesgo"
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación: Carrera con 3 Caballos</b></div>",
            unsafe_allow_html=True
        )

        # Parámetros de cada caballo
        st.markdown("<div class='subsection-title'>Parámetros de los Caballos</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div style='color: #2b6cb0; font-weight: bold; font-size: 20px;'>🐴 Caballo 1</div>", unsafe_allow_html=True)
            v1_mean = st.slider("Velocidad Media (km/h)", 50.0, 120.0, 80.0, 5.0, key="v1_m")
            v1_std = st.slider("Desviación estándar (σ)", 5.0, 30.0, 15.0, 2.0, key="v1_s")
        with c2:
            st.markdown("<div style='color: #2e7d32; font-weight: bold; font-size: 20px;'>🐴 Caballo 2</div>", unsafe_allow_html=True)
            v2_mean = st.slider("Velocidad Media (km/h)", 50.0, 120.0, 90.0, 5.0, key="v2_m")
            v2_std = st.slider("Desviación estándar (σ)", 5.0, 30.0, 12.0, 2.0, key="v2_s")
        with c3:
            st.markdown("<div style='color: #E67E22; font-weight: bold; font-size: 20px;'>🐴 Caballo 3</div>", unsafe_allow_html=True)
            v3_mean = st.slider("Velocidad Media (km/h)", 50.0, 120.0, 85.0, 5.0, key="v3_m")
            v3_std = st.slider("Desviación estándar (σ)", 5.0, 30.0, 18.0, 2.0, key="v3_s")

        n_carreras = st.slider("Número de carreras simuladas", 500, 5000, 2000, 500)

        # Simulación
        np.random.seed(42)
        v1 = np.random.normal(v1_mean, v1_std, n_carreras)
        v2 = np.random.normal(v2_mean, v2_std, n_carreras)
        v3 = np.random.normal(v3_mean, v3_std, n_carreras)

        # Operaciones
        suma_v1_v2 = v1 + v2
        dif_v1_v2 = v1 - v2
        producto_v1_v2 = v1 * v2

        # Métrica: Ganador en cada carrera
        ganadores = np.argmax(np.column_stack([v1, v2, v3]), axis=1)
        wins = [np.sum(ganadores == i) for i in range(3)]

        st.markdown(
            "<div class='content-box'><b>Resultados de la Carrera:</b></div>",
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>Caballo 1<br>{wins[0]} victorias</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Caballo 2<br>{wins[1]} victorias</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>Caballo 3<br>{wins[2]} victorias</div>", unsafe_allow_html=True)

        # Visualización: Distribuciones de velocidades (tres gráficos)
        col_g1, col_g2, col_g3 = st.columns(3)
        
        with col_g1:
            hist1, edges1 = np.histogram(v1, bins=25)
            p1 = figure(
                title="Caballo 1",
                x_axis_label="Velocidad (km/h)",
                y_axis_label="Frecuencia",
                width=300,
                height=280,
                toolbar_location=None,
                tools=""
            )
            p1.quad(top=hist1, bottom=0, left=edges1[:-1], right=edges1[1:],
                   fill_color=BLUE_LINE, line_color="white", line_width=1.5, alpha=0.8)
            p1.title.text_font_size = "16px"
            streamlit_bokeh(p1)
        
        with col_g2:
            hist2, edges2 = np.histogram(v2, bins=25)
            p2 = figure(
                title="Caballo 2",
                x_axis_label="Velocidad (km/h)",
                y_axis_label="Frecuencia",
                width=300,
                height=280,
                toolbar_location=None,
                tools=""
            )
            p2.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                   fill_color=GREEN_LINE, line_color="white", line_width=1.5, alpha=0.8)
            p2.title.text_font_size = "16px"
            streamlit_bokeh(p2)
        
        with col_g3:
            hist3, edges3 = np.histogram(v3, bins=25)
            p3 = figure(
                title="Caballo 3",
                x_axis_label="Velocidad (km/h)",
                y_axis_label="Frecuencia",
                width=300,
                height=280,
                toolbar_location=None,
                tools=""
            )
            p3.quad(top=hist3, bottom=0, left=edges3[:-1], right=edges3[1:],
                   fill_color=ORANGE_ACCENT, line_color="white", line_width=1.5, alpha=0.8)
            p3.title.text_font_size = "16px"
            streamlit_bokeh(p3)

        # Operaciones
        st.markdown("<div class='subsection-title'>Análisis de Operaciones</div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Suma (V₁+V₂)", "Diferencia (V₁-V₂)", "Producto (V₁×V₂)"])

        with tab1:
            st.markdown(
                f"<div class='content-box'>"
                f"<b>Suma V₁ + V₂:</b><br>"
                f"E[V₁+V₂] = {v1_mean + v2_mean:.1f} km/h<br>"
                f"Var(V₁+V₂) = {(v1_std**2 + v2_std**2):.1f}<br>"
                f"σ(V₁+V₂) = {np.sqrt(v1_std**2 + v2_std**2):.1f} km/h<br><br>"
                f"<b>Valores observados:</b><br>"
                f"Media simulada: {np.mean(suma_v1_v2):.1f}<br>"
                f"Desv. Est.: {np.std(suma_v1_v2):.1f}"
                f"</div>",
                unsafe_allow_html=True
            )

        with tab2:
            st.markdown(
                f"<div class='content-box'>"
                f"<b>Diferencia V₁ - V₂:</b><br>"
                f"E[V₁-V₂] = {v1_mean - v2_mean:.1f} km/h<br>"
                f"Var(V₁-V₂) = {(v1_std**2 + v2_std**2):.1f}<br>"
                f"σ(V₁-V₂) = {np.sqrt(v1_std**2 + v2_std**2):.1f} km/h<br><br>"
                f"<b>Valores observados:</b><br>"
                f"Media simulada: {np.mean(dif_v1_v2):.1f}<br>"
                f"Desv. Est.: {np.std(dif_v1_v2):.1f}"
                f"</div>",
                unsafe_allow_html=True
            )

        with tab3:
            exp_producto = v1_mean * v2_mean
            var_producto = (v1_mean**2 * v2_std**2) + (v2_mean**2 * v1_std**2) + (v1_std**2 * v2_std**2)
            st.markdown(
                f"<div class='content-box'>"
                f"<b>Producto V₁ × V₂:</b><br>"
                f"E[V₁×V₂] = {exp_producto:.1f}<br>"
                f"Var(V₁×V₂) ≈ {var_producto:.1f}<br>"
                f"σ(V₁×V₂) ≈ {np.sqrt(var_producto):.1f}<br><br>"
                f"<b>Valores observados:</b><br>"
                f"Media simulada: {np.mean(producto_v1_v2):.1f}<br>"
                f"Desv. Est.: {np.std(producto_v1_v2):.1f}"
                f"</div>",
                unsafe_allow_html=True
            )

# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Variables Aleatorias</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO"}); st.rerun()
    if nav_col2.button("(I) V.A. Discretas", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) PDF y CDF", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Varga's Race", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_discrete,
        "P2": render_pdf_cdf,
        "P3": render_horse_race,
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
