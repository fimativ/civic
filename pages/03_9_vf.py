import streamlit as st
import numpy as np
from scipy.stats import binom, nbinom, poisson
from bokeh.plotting import figure
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Ejemplos de V.A. Discretas")

# Colores
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
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
    color: var(--box-fg); font-size: 28px; line-height: 1.5; margin-bottom: 30px;
}}
.content-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: 20px 25px; background: var(--box-bg);
    font-style: normal; text-align: justify;
    color: var(--box-fg); font-size: 28px; line-height: 1.6; margin-bottom: 20px;
}}
.section-title {{
    font-size: 28px; font-weight: 700; color: var(--app-fg);
    margin: 10px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px;
}}
.subsection-title {{
    font-size: 28px; font-weight: 600; color: {ORANGE_ACCENT};
    margin: 20px 0 10px 0; border-left: 5px solid {ORANGE_ACCENT};
    padding-left: 15px;
}}
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 28px; color: var(--spoiler-fg);
}}
.metric-box {{
    font-size: 28px; color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px; white-space: nowrap; overflow: hidden;
}}
.metric-a {{ border-color: {BLUE_LINE};  color: {BLUE_LINE};  font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE}; color: {GREEN_LINE}; font-weight: 700; }}
.metric-c {{ border-color: {ORANGE_ACCENT}; color: {ORANGE_ACCENT}; font-weight: 700; }}

.result-bayes {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;  border-color: {UBU_YELLOW} !important; }}

/* ---- Spoiler ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-click-wrapper {{ cursor: pointer; display: block; text-decoration: none; margin-top: 20px; margin-bottom: 25px; }}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400; font-size: 28px; line-height: 1.5;
    background: var(--spoiler-bg); border-left: 10px solid var(--spoiler-fg);
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(15px); transition: filter 0.3s;
}}
.spoiler-toggle:checked ~ .spoiler-click-wrapper .spoiler-box {{ filter: none; }}

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
label[data-testid="stWidgetLabel"] p {{ font-size: 28px !important; font-weight: 600 !important; }}
[data-testid="stSlider"] > label p {{ font-size: 28px !important; font-weight: 600 !important; }}
button p {{ font-size: 28px !important; font-weight: 600 !important; }}

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
        st.session_state["page"] = "PROB036"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = None

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
# 4. EJEMPLO 1: PROBLEMA 036 - DEFECTUOSAS
# =============================================================================

def render_prob036():
    """Problema 036: Defectuosas de proveedores - Probabilidad Total y Bayes."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Problema 036</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Un fabricante compra unidades de cierto producto a dos proveedores A y B. "
            "El 60% de la compra la realiza al proveedor A y el resto al B. "
            "El porcentaje de unidades defectuosas del proveedor A es 3% mientras que en B es el 5%."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P036_A", "A) ¿Alguna defectuosa en 5 muestras?"):
            st.markdown("<div class='subsection-title'>A) Si el fabricante mezcla las unidades y elige 5, ¿cuál es la probabilidad de que encuentre alguna defectuosa?</div>", unsafe_allow_html=True)
            
            st.markdown(
                "<div class='content-box'><b>Definición de sucesos y datos:</b><br>"
                "A: El producto proviene del proveedor A.<br>"
                "B: El producto proviene del proveedor B.<br>"
                "D: El producto es defectuoso.<br>"
                "D̅: El producto no es defectuoso.<br><br>"
                "P(A) = 0.60, P(B) = 0.40<br>"
                "P(D|A) = 0.03, P(D|B) = 0.05"
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='content-box'><b>Paso 1: Probabilidad total de defectuoso</b><br>"
                "P(D) = P(D|A)·P(A) + P(D|B)·P(B)<br>"
                "P(D) = 0.03·0.60 + 0.05·0.40 = 0.018 + 0.020 = 0.038<br>"
                "P(D̅) = 1 - 0.038 = 0.962"
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='content-box'><b>Paso 2: Distribución Binomial</b><br>"
                "Sea X = número de unidades defectuosas en muestra de 5.<br>"
                "X ~ B(n=5, p=0.038)<br>"
                "<b>Buscamos P(X ≥ 1):</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "P(X ≥ 1) = 1 - P(X = 0)<br>"
                "P(X = 0) = (0.962)⁵ ≈ 0.8205<br>"
                "P(X ≥ 1) = 1 - 0.8205 ≈ <b>0.1795</b><br>"
                "La probabilidad de encontrar al menos una unidad defectuosa entre las 5 seleccionadas es de aproximadamente 0.1795."
            )


        if accordion_step("P036_B", "B) Teorema de Bayes"):
            st.markdown("<div class='subsection-title'>B) Si ambos proveedores empaquetan en lotes de 20 unidades y un lote contenía 2 unidades defectuosas, ¿cuál es la probabilidad de que provenga del proveedor A?</div>", unsafe_allow_html=True)
            
            st.markdown(
                "<div class='content-box'><b>Sea E el evento: 'un lote de 20 unidades contiene exactamente 2 unidades defectuosas'</b><br><br>"
                "Queremos calcular P(A|E) usando el Teorema de Bayes:<br>"
                "<div class='formula-box'>P(A|E) = P(E|A)·P(A) / [P(E|A)·P(A) + P(E|B)·P(B)]</div>"
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='content-box'><b>Paso 1: Calcular P(E|A) y P(E|B)</b><br>"
                "Modelamos defectuosos como Binomial B(20, p).<br><br>"
                "<b>Para proveedor A (p=0.03):</b><br>"
                "P(E|A) = P(X=2) = C(20,2)·(0.03)²·(0.97)¹⁸ ≈ 0.2753<br><br>"
                "<b>Para proveedor B (p=0.05):</b><br>"
                "P(E|B) = P(X=2) = C(20,2)·(0.05)²·(0.95)¹⁸ ≈ 0.1887"
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                "<div class='content-box'><b>Paso 2: Aplicar Teorema de Bayes</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "P(A|E) = (0.2753 × 0.60) / [(0.2753 × 0.60) + (0.1887 × 0.40)]<br>"
                "P(A|E) = 0.1652 / [0.1652 + 0.0755]<br>"
                "P(A|E) ≈ <b>0.6863</b><br><br>"
                "La probabilidad de que el lote que contiene 2 unidades defectuosas provenga del proveedor A es de aproximadamente 0.6863."
            )


    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Probabilidad Total</b></div>",
            unsafe_allow_html=True
        )

        p_a = st.slider("P(A) - Proveedor A", 0.3, 0.9, 0.6, 0.05)
        p_d_a = st.slider("P(D|A) - Defectuosos en A (%)", 1, 10, 3, 1) / 100
        p_d_b = st.slider("P(D|B) - Defectuosos en B (%)", 1, 10, 5, 1) / 100
        n_muestras = st.slider("n: Número de muestras", 3, 20, 5, 1)

        p_b = 1 - p_a
        p_d = p_d_a * p_a + p_d_b * p_b
        p_no_d = 1 - p_d

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>P(D) Combinada<br>{p_d:.4f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>P(D̅)<br>{p_no_d:.4f}</div>", unsafe_allow_html=True)
        with m3:
            p_x_0 = (p_no_d) ** n_muestras
            p_x_geq_1 = 1 - p_x_0
            st.markdown(f"<div class='metric-box metric-c'>P(X ≥ 1) en {n_muestras}<br>{p_x_geq_1:.4f}</div>", unsafe_allow_html=True)

        # Simulación
        np.random.seed(42)
        num_simulations = 10000
        defectuosos_sim = np.random.binomial(n_muestras, p_d, num_simulations)
        freq_al_menos_una = np.sum(defectuosos_sim >= 1) / num_simulations

        st.markdown(
            f"<div class='content-box'><b>Validación por Simulación ({num_simulations} experimentos):</b><br>"
            f"P(X ≥ 1) Teórica: {p_x_geq_1:.4f}<br>"
            f"P(X ≥ 1) Simulada: {freq_al_menos_una:.4f}<br>"
            f"Diferencia: {abs(p_x_geq_1 - freq_al_menos_una):.4f}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Gráfico
        hist, edges = np.histogram(defectuosos_sim, bins=range(0, n_muestras + 2))
        p = figure(
            title=f"Distribución de defectuosos (Simulación de {num_simulations} exp.)",
            x_axis_label="Número de defectuosos",
            y_axis_label="Frecuencia",
            width=450,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=1.5, alpha=0.8)
        p.title.text_font_size = "16px"
        streamlit_bokeh(p)

# =============================================================================
# 5. EJEMPLO 2: DISTRIBUCIÓN BINOMIAL NEGATIVA - ARQUERO
# =============================================================================

def render_ejemplo3():
    """Ejemplo 3: Distribución Binomial Negativa - Tiro con Arco."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Tiro con Arco</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Un arquero profesional tiene una probabilidad del 80% de dar en el centro de la diana en cada tiro. "
            "Los lanzamientos son independientes. ¿Cuál es la probabilidad de que el arquero necesite exactamente 6 tiros para conseguir su tercer centro de diana?"
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("ARQ_A", "Solución Paso a Paso"):
            st.markdown("<div class='subsection-title'>1. Identificar los datos</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "r = 3: Número de éxitos deseados.<br>"
                "x = 6: Número total de intentos necesarios.<br>"
                "p = 0.8: Probabilidad de éxito.<br>"
                "q = 1 - p = 0.2: Probabilidad de fracaso."
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown("<div class='subsection-title'>2. Aplicar la fórmula</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La fórmula de la binomial negativa calcula la probabilidad de obtener el éxito número r en el intento número x:<br>"
                "<div class='formula-box'>P(X=x) = C(x-1, r-1) · p<sup>r</sup> · q<sup>x-r</sup></div>"
                "</div>",
                unsafe_allow_html=True
            )

            st.markdown("<div class='subsection-title'>3. Sustituir los valores</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "P(X=6) = C(5, 2) · (0.8)<sup>3</sup> · (0.2)<sup>3</sup>"
                "</div>",
                unsafe_allow_html=True
            )

            spoiler(
                "<b>Paso 4: Resolver las operaciones</b><br><br>"
                "Combinatoria: C(5,2) = 5!/(2!·3!) = 10<br>"
                "Éxitos: (0.8)³ = 0.512<br>"
                "Fracasos: (0.2)³ = 0.008<br><br>"
                "P(X=6) = 10 · 0.512 · 0.008<br>"
                "P(X=6) = <b>0.04096</b><br><br>"
                "La probabilidad de que logre su tercer centro exactamente en el sexto tiro es del 0.041, muy baja."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Binomial Negativa</b></div>",
            unsafe_allow_html=True
        )

        p_acierto = st.slider("p: Probabilidad de acierto (%)", 50, 99, 80, 1) / 100
        r_exitos = st.slider("r: Número de éxitos deseados", 1, 10, 3, 1)
        x_intentos = st.slider("x: Número de intentos", r_exitos, 30, 6, 1)

        # Calcular probabilidad teórica
        prob_teorica = nbinom.pmf(x_intentos - r_exitos, r_exitos, p_acierto)

        # Simulación
        np.random.seed(42)
        num_sim = 50000
        num_intentos_sim = []
        for _ in range(num_sim):
            exitos = 0
            intento = 0
            while exitos < r_exitos:
                if np.random.random() < p_acierto:
                    exitos += 1
                intento += 1
            num_intentos_sim.append(intento)

        num_intentos_sim = np.array(num_intentos_sim)
        freq_observada = np.sum(num_intentos_sim == x_intentos) / num_sim

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>P(X={x_intentos}) Teórica<br>{prob_teorica:.5f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>P(X={x_intentos}) Simulada<br>{freq_observada:.5f}</div>", unsafe_allow_html=True)
        with m3:
            diff = abs(prob_teorica - freq_observada)
            st.markdown(f"<div class='metric-box metric-c'>Diferencia<br>{diff:.5f}</div>", unsafe_allow_html=True)

        # Gráfico: Distribución actual
        hist, edges = np.histogram(num_intentos_sim, bins=range(r_exitos, min(max(num_intentos_sim) + 2, 35)))
        p = figure(
            title=f"Distribución de intentos para {r_exitos} éxito(s) (p={p_acierto:.1%})",
            x_axis_label="Número de intentos",
            y_axis_label="Frecuencia",
            width=450,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=GREEN_LINE, line_color="white", line_width=1.5, alpha=0.8)
        p.title.text_font_size = "16px"
        streamlit_bokeh(p)

        # Comparación con otro valor de r
        st.markdown("<div class='subsection-title'>Comparación: Efecto de cambiar r</div>", unsafe_allow_html=True)
        
        r_comparacion = max(1, r_exitos - 1) if r_exitos > 1 else r_exitos + 1
        
        # Simular para r diferente
        num_intentos_sim_comp = []
        for _ in range(num_sim):
            exitos = 0
            intento = 0
            while exitos < r_comparacion:
                if np.random.random() < p_acierto:
                    exitos += 1
                intento += 1
            num_intentos_sim_comp.append(intento)
        
        num_intentos_sim_comp = np.array(num_intentos_sim_comp)
        
        # Gráfico comparativo
        hist_comp, edges_comp = np.histogram(num_intentos_sim_comp, bins=range(r_comparacion, min(max(num_intentos_sim_comp) + 2, 35)))
        
        p_comp = figure(
            title=f"Distribución de intentos para {r_comparacion} éxito(s) (p={p_acierto:.1%})",
            x_axis_label="Número de intentos",
            y_axis_label="Frecuencia",
            width=450,
            height=300,
            toolbar_location=None,
            tools=""
        )
        p_comp.quad(top=hist_comp, bottom=0, left=edges_comp[:-1], right=edges_comp[1:],
               fill_color=ORANGE_ACCENT, line_color="white", line_width=1.5, alpha=0.8)
        p_comp.title.text_font_size = "16px"
        streamlit_bokeh(p_comp)
        
        st.markdown(
            f"<div class='content-box'><b>Análisis:</b><br>"
            f"• Con r={r_exitos}: Necesitas {r_exitos} éxito(s) → E[X] ≈ {np.mean(num_intentos_sim):.1f} intentos<br>"
            f"• Con r={r_comparacion}: Necesitas {r_comparacion} éxito(s) → E[X] ≈ {np.mean(num_intentos_sim_comp):.1f} intentos<br><br>"
            f"<b>Observación:</b> La distribución se <b>desplaza hacia la derecha</b> cuando aumentas r. "
            f"Más éxitos deseados = más intentos en promedio."
            f"</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 6. EJEMPLO 3: PLACEHOLDER
# =============================================================================

def render_no_memoria():
    """Ejemplo 2: Propiedad de No Memoria - Distribución Geométrica."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Propiedad de No Memoria</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La distribución Geométrica carece de memoria. "
            "Sea G ~ 𝒢(p), que cuenta los fracasos antes del primer éxito, con ℙ(G = k) = (1−p)<sup>k−1</sup>p. "
            "Supongamos que ya llevamos 100 intentos fallidos. ¿Cuál es la probabilidad de necesitar k intentos en total, sabiendo que G > 100?"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='subsection-title'>La Idea Esencial</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "Después de 100 fracasos, la distribución condicionada de intentos adicionales es <b>idéntica a la distribución original</b>."
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='content-box'>"
            "<b>¿Por qué?</b><br><br>"
            "La probabilidad condicionada es:<br>"
            "<div class='formula-box'>ℙ(G = 100 + l|G > 100) = (1−p)<sup>100+l−1</sup>p / (1−p)<sup>100</sup></div><br>"
            "Al simplificar, los términos (1−p)<sup>100</sup> se cancelan:<br>"
            "<div class='formula-box'>ℙ(G = 100 + l|G > 100) = (1−p)<sup>l−1</sup>p</div><br>"
            "¡Exactamente la función original en l!"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='content-box'>"
            "<b>Conclusión:</b> El sistema <b>no arrastra</b> los 100 fracasos. "
            "La esperanza condicionada es simplemente:<br>"
            "<div class='formula-box'>𝔼[G|G > 100] = 100 + 1/p</div>"
            "Pero la esperanza de intentos <b>adicionales</b> (G - 100) es solo 1/p, como si empezáramos de cero."
            "</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: No Memoria</b></div>",
            unsafe_allow_html=True
        )

        p_exito = st.slider("p: Probabilidad de éxito (%)", 1, 99, 20, 1) / 100
        n_fracasos_previos = st.slider("Fracasos previos observados", 0, 200, 100, 10)

        # Simulación
        np.random.seed(42)
        num_sim = 500000  # Aumentar a 500k para tener más muestras
        
        # Generar intentos totales hasta el primer éxito
        intentos_totales = []
        for _ in range(num_sim):
            intentos = 0
            while np.random.random() > p_exito:
                intentos += 1
            intentos_totales.append(intentos + 1)  # +1 para contar el éxito
        
        intentos_totales = np.array(intentos_totales)
        
        # Filtrar solo los que tienen más fracasos que n_fracasos_previos
        filtrados = intentos_totales[intentos_totales > n_fracasos_previos]
        num_filtrados = len(filtrados)
        porcentaje_filtrados = (num_filtrados / num_sim) * 100
        
        # Intentos adicionales (después de los n_fracasos_previos)
        intentos_adicionales = filtrados - n_fracasos_previos
        
        # Esperanza teórica
        esperanza_teorica_completa = 1 / p_exito
        esperanza_teorica_adicional = 1 / p_exito
        esperanza_simulada_adicional = np.mean(intentos_adicionales) if len(intentos_adicionales) > 0 else 0

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"<div class='metric-box metric-a'>E[G] Teórica<br>{esperanza_teorica_completa:.2f}</div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div class='metric-box metric-b'>E[G - {n_fracasos_previos}] Teórica<br>{esperanza_teorica_adicional:.2f}</div>",
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f"<div class='metric-box metric-c'>E[G - {n_fracasos_previos}] Simulada<br>{esperanza_simulada_adicional:.2f}</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            f"<div class='content-box'><b>Validación de Muestras:</b><br>"
            f"Simulaciones totales: {num_sim:,}<br>"
            f"Casos con G > {n_fracasos_previos}: {num_filtrados:,} ({porcentaje_filtrados:.2f}%)<br>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Gráfico: Comparación de distribuciones
        if num_filtrados > 500:  # Umbral más bajo pero razonable
            hist_adicionales, edges_adicionales = np.histogram(
                intentos_adicionales, 
                bins=range(1, min(int(np.percentile(intentos_adicionales, 95)) + 2, 50))
            )
            
            p = figure(
                title=f"Intentos adicionales tras {n_fracasos_previos} fracasos (Geométrica, p={p_exito:.2f})",
                x_axis_label="Intentos adicionales (l)",
                y_axis_label="Frecuencia",
                width=450,
                height=300,
                toolbar_location=None,
                tools=""
            )
            p.quad(top=hist_adicionales, bottom=0, left=edges_adicionales[:-1], right=edges_adicionales[1:],
                   fill_color=ORANGE_ACCENT, line_color="white", line_width=1.5, alpha=0.8)
            p.title.text_font_size = "16px"
            streamlit_bokeh(p)

            st.markdown(
                f"<div class='content-box'><b>Interpretación:</b><br>"
                f"La distribución de intentos adicionales es idéntica a la original, "
                f"demostrando la propiedad de no memoria. "
                f"Los {n_fracasos_previos} fracasos previos no afectan la probabilidad futura."
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='content-box' style='border-color: #ff6b6b; background: #ffe0e0;'>"
                f"<b>⚠️ Muestras insuficientes para visualizar</b><br><br>"
                f"<b>¿Por qué ocurre esto?</b><br>"
                f"Con p={p_exito:.2%}, la esperanza es E[G] = 1/p = {esperanza_teorica_completa:.1f} intentos.<br>"
                f"Pedir G > {n_fracasos_previos} es pedir eventos muy extremos. "
                f"Solo {num_filtrados} de {num_sim:,} muestras cumplen esta condición ({porcentaje_filtrados:.3f}%).<br><br>"
                f"<b>Solución:</b><br>"
                f"• Reduce los 'Fracasos previos' a un valor más cercano a E[G]<br>"
                f"• O aumenta 'p' (mayor probabilidad de éxito) para que E[G] sea más pequeño"
                f"</div>",
                unsafe_allow_html=True
            )

# =============================================================================
# 7. EJEMPLO 4: PLACEHOLDER
# =============================================================================

def render_ejemplo4():
    """Ejemplo 4: Problema 032 - Distribución de Poisson y Geométrica."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Problema 032</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "En uno de los servidores web de la universidad, el número de intentos de acceso no autorizados (ataques) por hora "
            "sigue una distribución de Poisson con una tasa media de λ = 2.5 ataques por hora."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P032_A", "A) Probabilidad de hora pacífica"):
            st.markdown(
                "<div class='content-box'>"
                "<b>Calcula la probabilidad de que en una hora determinada el servidor registre una 'hora pacífica', "
                "es decir, que no reciba ningún intento de acceso no autorizado.</b><br><br>"
                "Definimos la variable aleatoria X como el número de intentos de acceso no autorizados por hora. "
                "Dado que sigue una distribución de Poisson con tasa media λ = 2.5 ataques por hora, su función de probabilidad es:<br><br>"
                "<div class='formula-box'>P(X = k) = (e<sup>-λ</sup> · λ<sup>k</sup>) / k!</div>"
                "Una 'hora pacífica' ocurre cuando X = 0:"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "<div class='formula-box'>P(X = 0) = e<sup>-2.5</sup> ≈ 0.0821 </div>"
            )

        if accordion_step("P032_B", "B) Distribución de Y"):
            st.markdown(
                "<div class='content-box'>"
                "<b>Sea Y el número de horas que el administrador debe monitorizar hasta que observa por primera vez una 'hora pacífica'. "
                "¿Qué distribución sigue Y y cuál es su parámetro?</b><br><br>"
                "Cada hora monitorizada es un ensayo de Bernoulli independiente con:<br>"
                "• 'Éxito' = observar hora pacífica (p = 0.0821)<br>"
                "• 'Fracaso' = no observar hora pacífica (1-p = 0.9179)<br><br>"
                "Y representa el número de ensayos hasta el primer éxito.<br>"
                "<b>Y sigue una Distribución Geométrica con parámetro p = e<sup>-λ</sup> = e<sup>-2.5</sup></b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "<div class='formula-box'>P(Y = k) = (1-p)<sup>k-1</sup> · p</div>"
            )

        if accordion_step("P032_C", "C) Valor esperado de Y"):
            st.markdown(
                "<div class='content-box'>"
                "<b>Calcula el número esperado de horas que habrá que esperar para que ocurra la primera 'hora pacífica'.</b><br><br>"
                "Para una distribución geométrica, el valor esperado es:"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "<div class='formula-box'>E[Y] = 1/p = 1/e<sup>-2.5</sup> = e<sup>2.5</sup></div>"
                "Sustituyendo el valor de p = 0.0821:<br>"
                "E[Y] = 1/0.0821 ≈ <b>12.18 horas</b> (aprox. 12 h y 11 min)<br>"
            )

        if accordion_step("P032_D", "D) Primera hora pacífica en la cuarta hora"):
            st.markdown(
                "<div class='content-box'>"
                "<b>¿Cuál es la probabilidad de que la primera 'hora pacífica' sea exactamente la cuarta hora de observación?</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            spoiler(
                "Para que la primera hora pacífica ocurra en Y = 4:<br>"
                "• Las 3 primeras horas NO son pacíficas (fracasos)<br>"
                "• La 4ta hora SÍ es pacífica (éxito)<br><br>"
                "P(Y = 4) = (1-p)<sup>3</sup> · p<br>"
                "P(Y = 4) = (0.9179)<sup>3</sup> · 0.0821<br>"
                "P(Y = 4) ≈ <b>0.0635 </b><br><br>"
                "La probabilidad de que la primera 'hora pacífica' sea exactamente la cuarta hora de observación es aproximadamente 0.0635."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Ataques y Horas Pacíficas</b></div>",
            unsafe_allow_html=True
        )

        lambda_param = st.slider("λ: Tasa media de ataques/hora", 1.0, 5.0, 2.5, 0.1)
        n_horas_sim = st.slider("Número de horas a simular", 100, 10000, 1000, 500)

        # Calcular probabilidad teórica de hora pacífica
        p_pacifica_teorica = np.exp(-lambda_param)
        
        # Simulación: Generar ataques por hora usando Poisson
        np.random.seed(42)
        ataques_por_hora = np.random.poisson(lambda_param, n_horas_sim)
        
        # Identificar horas pacíficas (0 ataques)
        horas_pacificas = (ataques_por_hora == 0).astype(int)
        
        # Encontrar la primera hora pacífica
        primeras_horas_pacificas = []
        for _ in range(1000):  # Repetir 1000 veces
            ataques = np.random.poisson(lambda_param, 200)  # Simular hasta 200 horas
            horas_pacificas_temp = np.where(ataques == 0)[0]
            if len(horas_pacificas_temp) > 0:
                primeras_horas_pacificas.append(horas_pacificas_temp[0] + 1)  # +1 para contar desde 1
        
        primeras_horas_pacificas = np.array(primeras_horas_pacificas)
        
        # Frecuencia observada de hora pacífica
        freq_pacifica_observada = np.sum(horas_pacificas) / n_horas_sim

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"<div class='metric-box metric-a'>P(X=0) Teórica (Poisson)<br>e^-{lambda_param:.1f} = {p_pacifica_teorica:.4f}</div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div class='metric-box metric-b'>P(X=0) Observada<br>{freq_pacifica_observada:.4f}</div>",
                unsafe_allow_html=True
            )

        # Gráfico 1: Distribución de ataques por hora
        hist_ataques, edges_ataques = np.histogram(
            ataques_por_hora, 
            bins=range(0, max(ataques_por_hora) + 2)
        )
        
        p1 = figure(
            title=f"Distribución de ataques por hora (λ={lambda_param})",
            x_axis_label="Número de ataques",
            y_axis_label="Frecuencia",
            width=450,
            height=280,
            toolbar_location=None,
            tools=""
        )
        p1.quad(top=hist_ataques, bottom=0, left=edges_ataques[:-1], right=edges_ataques[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=1.5, alpha=0.8)
        p1.title.text_font_size = "16px"
        streamlit_bokeh(p1)

        st.markdown(
            f"<div class='content-box'>"
            f"De {n_horas_sim} horas observadas, <b>{np.sum(horas_pacificas)} fueron pacíficas.</b> "
            f"Esto responde a la pregunta A) → P(X=0) = {p_pacifica_teorica:.4f}"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='content-box'><b>Derivada: Distribución Geométrica (apartados B, C, D)</b><br>"
            "Ahora hagamos una pregunta diferente: Si cada hora es un 'ensayo de Bernoulli' (pacífica sí/no), "
            "¿cuántas horas debo esperar hasta la <b>primera hora pacífica</b>?"
            "</div>",
            unsafe_allow_html=True
        )

        # Calcular E[Y] primero
        e_y_teorica = 1 / p_pacifica_teorica

        # Gráfico 2: Distribución de primeras horas pacíficas
        if len(primeras_horas_pacificas) > 0:
            e_y_observada = np.mean(primeras_horas_pacificas)
            
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"<div class='metric-box metric-a'>E[Y] Teórica (Geom)<br>1/p = {e_y_teorica:.2f} horas</div>",
                    unsafe_allow_html=True
                )
            with m2:
                st.markdown(
                    f"<div class='metric-box metric-b'>E[Y] Observada<br>{e_y_observada:.2f} horas</div>",
                    unsafe_allow_html=True
                )
            hist_primeras, edges_primeras = np.histogram(
                primeras_horas_pacificas,
                bins=range(1, min(int(np.percentile(primeras_horas_pacificas, 95)) + 2, 50))
            )
            
            p2 = figure(
                title=f"Distribución Geométrica: tiempo hasta 1ª hora pacífica (p={p_pacifica_teorica:.4f})",
                x_axis_label="Hora en la que ocurre (Y)",
                y_axis_label="Frecuencia",
                width=450,
                height=280,
                toolbar_location=None,
                tools=""
            )
            p2.quad(top=hist_primeras, bottom=0, left=edges_primeras[:-1], right=edges_primeras[1:],
                   fill_color=ORANGE_ACCENT, line_color="white", line_width=1.5, alpha=0.8)
            p2.title.text_font_size = "16px"
            streamlit_bokeh(p2)

            st.markdown(
                f"<div class='content-box'><b>Conexión Poisson ↔ Geométrica:</b><br><br>"
                f"<b>Poisson (A):</b> Cuenta eventos en un intervalo fijo (ataques/hora)<br>"
                f"<b>Geométrica (B, C, D):</b> Cuenta intervalos hasta el primer evento (horas hasta 1ª pacífica)<br><br>"
                f"Son <b>duales</b>: Poisson pregunta '¿cuántos eventos?', Geométrica pregunta '¿cuándo el primero?'<br>"
                f"El parámetro p = e^-λ conecta ambas: la probabilidad de éxito en cada ensayo Bernoulli "
                f"es la probabilidad de 'cero ataques' del Poisson."
                f"</div>",
                unsafe_allow_html=True
            )

# =============================================================================
# 8. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Ejemplos de Variables Aleatorias Discretas</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Bernoulli/Binomial", use_container_width=True):
        st.session_state.update({"page": "PROB036"}); st.rerun()
    if nav_col2.button("Geométrica", use_container_width=True):
        st.session_state.update({"page": "NOMEM"}); st.rerun()
    if nav_col3.button("Binomial Negativa", use_container_width=True):
        st.session_state.update({"page": "EJ3"}); st.rerun()
    if nav_col4.button("Poisson", use_container_width=True):
        st.session_state.update({"page": "EJ4"}); st.rerun()

    paginas = {
        "PROB036": render_prob036,
        "NOMEM": render_no_memoria,
        "EJ3": render_ejemplo3,
        "EJ4": render_ejemplo4,
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
