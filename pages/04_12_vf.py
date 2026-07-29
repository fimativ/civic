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

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Distribución Uniforme")

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
        st.session_state["page"] = "AMANTES"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "AMANTES_A"

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def accordion_step(step_id, title):
    """Simula un acordeón clickeable."""
    if f"step_{step_id}" not in st.session_state:
        st.session_state[f"step_{step_id}"] = False
    
    if st.button(title, use_container_width=True, key=f"btn_{step_id}"):
        st.session_state[f"step_{step_id}"] = not st.session_state[f"step_{step_id}"]
        st.rerun()
    
    return st.session_state[f"step_{step_id}"]

def spoiler(content_html, label="Respuesta"):
    """Crea una caja de spoiler con reveal."""
    spoiler_id = str(uuid.uuid4())[:8]
    st.markdown(
        f"""
        <label class='spoiler-toggle' for='{spoiler_id}'>
            <input type='checkbox' id='{spoiler_id}' class='spoiler-toggle'>
            <a class='spoiler-click-wrapper'>
                <div class='spoiler-box'>
                    {content_html}
                </div>
            </a>
        </label>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# 4. PÁGINA 1: EL ENCUENTRO DE LOS AMANTES
# =============================================================================

def render_amantes():
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>🕐 El Encuentro de los Amantes</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "Dos personas acuerdan encontrarse en un lugar entre las 4:00 y las 5:00 PM. "
            "Cada una llega de manera independiente y aleatoria, y acuerdan esperar un máximo de 15 minutos. "
            "¿Cuál es la probabilidad de que coincidan?"
            "</div>",
            unsafe_allow_html=True
        )
        
        if accordion_step("AMANTES_A", "A) El Caso Uniforme"):
            st.markdown("<div class='subsection-title'>A) El Caso Uniforme</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Los tiempos de llegada <b>X</b> (primer amante) e <b>Y</b> (segundo amante) "
                "se distribuyen de forma uniforme en el intervalo [0, 60] minutos:<br><br>"
                "<b>X, Y ~ U(0, 60)</b><br><br>"
                "La condición de encuentro es: <b>|X - Y| ≤ 15</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='content-box'><b>Cálculo de la probabilidad:</b></div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>P(encuentro) = (60² - 2·45²) / 60² = 7/16 = 43.75%</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='content-box'>"
                "La región donde se encuentran forma una franja diagonal en el plano (60×60). "
                "Los dos triángulos esquineros (donde NO se encuentran) tienen área (45)² cada uno."
                "</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("AMANTES_B", "B) El Caso Normal (Realista)"):
            st.markdown("<div class='subsection-title'>B) El Caso Normal (Realista)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "En la realidad, las personas intentan llegar a una hora objetivo (ej: 4:30 PM), "
                "pero sufren retrasos o adelantos aleatorios. Este comportamiento se modela asumiendo "
                "que las llegadas siguen una <b>distribución normal</b>:<br><br>"
                "<b>X, Y ~ N(μ, σ²)</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            sigma = st.slider("Desviación estándar σ (minutos)", 2.0, 15.0, 5.0, key="amantes_sigma")
            
            # Cálculo de probabilidad para caso normal
            prob_normal = norm.cdf(15, 0, np.sqrt(2 * sigma**2)) - norm.cdf(-15, 0, np.sqrt(2 * sigma**2))
            
            st.markdown(
                "<div class='content-box'>"
                "La diferencia <b>D = X - Y</b> sigue una distribución normal: <b>D ~ N(0, 2σ²)</b><br><br>"
                f"<b>Con σ = {sigma:.1f} min:</b> P(encuentro) = <b>{prob_normal*100:.2f}%</b>"
                "</div>",
                unsafe_allow_html=True
            )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>📊 Región de Encuentro: Caso Uniforme</b></div>",
            unsafe_allow_html=True
        )
        
        # Gráfico uniforme
        p_uniform = figure(
            title="Encuentro U(0,60): |X - Y| ≤ 15",
            x_axis_label="Llegada Amante 1 (min)",
            y_axis_label="Llegada Amante 2 (min)",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        # Cuadrado total
        p_uniform.quad(top=[60], bottom=[0], left=[0], right=[60], 
                      fill_alpha=0.1, line_color=UBU_DARK, line_width=2, fill_color="white")
        
        # Región de encuentro (|X - Y| <= 15)
        x_region = np.array([0, 45, 60, 60, 45, 0, 0])
        y_region = np.array([0, 0, 15, 60, 60, 45, 0])
        p_uniform.patch(x_region, y_region, fill_alpha=0.4, fill_color=UBU_YELLOW, 
                       line_color=UBU_RED, line_width=2.5)
        
        # Líneas diagonales
        p_uniform.line([0, 45], [15, 60], line_color=UBU_RED, line_width=2.5, line_dash="dashed")
        p_uniform.line([15, 60], [0, 45], line_color=UBU_RED, line_width=2.5, line_dash="dashed")
        
        p_uniform.title.text_font_size = "14px"
        streamlit_bokeh(p_uniform)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>El área amarilla = 43.75% del cuadrado total</b></small>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>📊 Diferencia de Llegadas: Caso Normal</b></div>",
            unsafe_allow_html=True
        )
        
        # Gráfico normal
        sigma_display = st.session_state.get("amantes_sigma", 5.0)
        x_norm = np.linspace(-40, 40, 500)
        y_norm = norm.pdf(x_norm, 0, np.sqrt(2 * sigma_display**2))
        
        p_normal = figure(
            title=f"D = X - Y con σ = {sigma_display:.1f}",
            x_axis_label="D (minutos)",
            y_axis_label="Densidad",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        
        p_normal.line(x_norm, y_norm, line_width=2.5, color=UBU_DARK)
        
        # Región de encuentro [-15, 15]
        x_fill = x_norm[(x_norm >= -15) & (x_norm <= 15)]
        y_fill = norm.pdf(x_fill, 0, np.sqrt(2 * sigma_display**2))
        p_normal.varea(x=x_fill, y1=0, y2=y_fill, alpha=0.3, color=UBU_YELLOW)
        
        # Líneas verticales
        p_normal.line([-15, -15], [0, max(y_norm)*1.1], line_color=UBU_RED, line_width=2.5, line_dash="dashed")
        p_normal.line([15, 15], [0, max(y_norm)*1.1], line_color=UBU_RED, line_width=2.5, line_dash="dashed")
        
        p_normal.title.text_font_size = "14px"
        streamlit_bokeh(p_normal)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Área amarilla = P(encuentro)</b></small>",
            unsafe_allow_html=True
        )

# =============================================================================
# 5. PÁGINA 2: LA ESPERA DEL AUTOBÚS
# =============================================================================

def render_autobus():
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>🚌 La Espera del Autobús</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "Si un autobús pasa en promedio cada 10 minutos, ¿cuánto tiempo espera de media "
            "un pasajero que llega a una hora aleatoria a la parada?"
            "</div>",
            unsafe_allow_html=True
        )
        
        if accordion_step("AUTOBUS_A", "A) El Caso Idealizado (Uniforme)"):
            st.markdown("<div class='subsection-title'>A) El Caso Idealizado (Uniforme)</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si el autobús llega puntualmente cada 10 minutos, la hora de llegada del pasajero "
                "respecto al último autobús sigue una distribución uniforme:<br><br>"
                "<b>T ~ U(0, 10)</b>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>E[Espera] = 10 / 2 = 5 minutos</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='content-box'>"
                "En el caso ideal con distribución uniforme, la esperanza matemática es simplemente "
                "el punto medio del intervalo [0, 10]."
                "</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("AUTOBUS_B", "B) La Paradoja: Variabilidad Real"):
            st.markdown("<div class='subsection-title'>B) La Paradoja: Variabilidad Real</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Cuando los autobuses no son puntuales (intervalos variables), "
                "la espera media sube por encima de 5 minutos. Esta es la <b>paradoja del tiempo de espera</b>."
                "</div>",
                unsafe_allow_html=True
            )
            
            interval_var = st.slider("Variabilidad de intervalos (Coef. Variación %)", 0.0, 50.0, 20.0, key="bus_cv")
            
            # Media de espera con variabilidad
            cv = interval_var / 100.0
            mean_wait = 5 * (1 + cv**2)
            
            st.markdown(
                "<div class='formula-box'>E[Espera] = 5 · (1 + CV²)</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"<div class='content-box'>"
                f"<b>Con CV = {interval_var:.0f}%:</b><br><br>"
                f"E[Espera] = <b>{mean_wait:.2f} minutos</b><br><br>"
                f"Exceso sobre 5 minutos: <b>{mean_wait - 5:.2f} minutos</b>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>📊 Distribución del Tiempo de Espera</b></div>",
            unsafe_allow_html=True
        )
        
        # Gráfico de distribución uniforme
        x_bus = np.linspace(0, 10, 100)
        
        p_bus = figure(
            title="Tiempo de Espera ~ U(0, 10)",
            x_axis_label="Tiempo de espera (minutos)",
            y_axis_label="Densidad",
            width=500,
            height=350,
            toolbar_location=None,
            tools=""
        )
        
        # Distribución uniforme
        p_bus.quad(top=[0.1], bottom=[0], left=[0], right=[10], 
                  fill_alpha=0.4, fill_color=UBU_YELLOW, line_color=UBU_RED, line_width=2.5)
        
        # Línea de esperanza (5 minutos)
        p_bus.line([5, 5], [0, 0.1], line_color=UBU_RED, line_width=3, line_dash="dashed")
        
        # Anotación
        p_bus.text(x=[5], y=[0.11], text=["E[T]=5"], text_font_size="12px", text_align="center")
        
        p_bus.y_range.start = 0
        p_bus.y_range.end = 0.15
        p_bus.title.text_font_size = "14px"
        streamlit_bokeh(p_bus)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Caso idealizado: uniforme</b></small>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>📊 Impacto de la Variabilidad</b></div>",
            unsafe_allow_html=True
        )
        
        cv_display = st.session_state.get("bus_cv", 20.0) / 100.0
        mean_wait_display = 5 * (1 + cv_display**2)
        
        p_impact = figure(
            title="E[Espera] vs Variabilidad",
            x_axis_label="Coeficiente de Variación (%)",
            y_axis_label="Esperanza de espera (min)",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        
        cv_range = np.linspace(0, 50, 50)
        mean_wait_range = 5 * (1 + (cv_range/100)**2)
        
        p_impact.line(cv_range, mean_wait_range, line_width=2.5, color=BLUE_LINE)
        p_impact.circle([st.session_state.get("bus_cv", 20.0)], [mean_wait_display], 
                       size=10, color=UBU_RED)
        p_impact.line([0, 50], [5, 5], line_color="gray", line_width=1, line_dash="dotted")
        
        p_impact.title.text_font_size = "14px"
        streamlit_bokeh(p_impact)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>Caso Ideal<br>5.00 min</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Con Variabilidad<br>{mean_wait_display:.2f} min</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>Exceso<br>{mean_wait_display-5:.2f} min</div>", unsafe_allow_html=True)

# =============================================================================
# 6. PÁGINA 3: LA PARADOJA DE BERTRAND
# =============================================================================

def render_bertrand():
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>🎪 La Paradoja de Bertrand</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "¿Cuál es la probabilidad de que una cuerda elegida al azar en un círculo "
            "sea más larga que el lado de un triángulo equilátero inscrito?"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>paradoja</b> de Bertrand (1889) es que, según cómo definas 'al azar', "
            "obtienes <b>tres respuestas distintas: 1/3, 1/2 ó 1/4</b>"
            "</div>",
            unsafe_allow_html=True
        )
        
        if accordion_step("BERTRAND_A", "A) Método 1: Extremos Aleatorios (P = 1/3)"):
            st.markdown("<div class='subsection-title'>A) Método 1: Extremos Aleatorios</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Procedimiento:</b> Se eligen dos puntos sobre la circunferencia "
                "de manera independiente y uniforme. Luego se traza la cuerda.<br><br>"
                "<b>Análisis:</b> Por simetría, fijamos el primer punto en un vértice del triángulo. "
                "El triángulo divide la circunferencia en tres arcos de 120°. "
                "La cuerda es larga si el segundo punto cae en el arco opuesto.<br><br>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>P = 120° / 360° = 1/3</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("BERTRAND_B", "B) Método 2: Radio Aleatorio (P = 1/2)"):
            st.markdown("<div class='subsection-title'>B) Método 2: Radio Aleatorio</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Procedimiento:</b> Se elige un radio del círculo al azar. "
                "Luego se elige un punto sobre ese radio con distribución uniforme.<br><br>"
                "<b>Análisis:</b> El lado del triángulo corta el radio a mitad de su longitud (R/2). "
                "La cuerda perpendicular es larga si el punto está más cerca del centro que R/2.<br><br>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>P = (R/2) / R = 1/2</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("BERTRAND_C", "C) Método 3: Punto Medio Aleatorio (P = 1/4)"):
            st.markdown("<div class='subsection-title'>C) Método 3: Punto Medio Aleatorio</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Procedimiento:</b> Cualquier cuerda se define de forma única por su punto medio. "
                "Se elige un punto de manera uniforme dentro del área del círculo y se toma como punto medio de la cuerda.<br><br>"
                "<b>Análisis:</b> La cuerda es larga si su punto medio está dentro de un círculo concéntrico "
                "de radio R/2 (tangente a los lados del triángulo). La probabilidad es la proporción de áreas.<br>"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box'>P = π(R/2)² / πR² = 1/4</div>",
                unsafe_allow_html=True
            )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Conclusión:</b> La paradoja demuestra que <b>la distribución uniforme NO es invariante</b> "
            "ante transformaciones no lineales. Definir una variable como uniforme en un espacio "
            "(circunferencia) no significa que sea uniforme en otro (área)."
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Método 1
        st.markdown(
            "<div class='content-box'><b>Método 1: Extremos</b></div>",
            unsafe_allow_html=True
        )
        
        p1 = figure(
            title="P = 1/3",
            width=400,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        theta = np.linspace(0, 2*np.pi, 100)
        p1.line(np.cos(theta), np.sin(theta), line_color=UBU_DARK, line_width=2)
        
        # Triángulo
        triangle_angle = np.array([0, 2*np.pi/3, 4*np.pi/3, 0])
        p1.line(np.cos(triangle_angle), np.sin(triangle_angle), line_color=UBU_RED, line_width=2)
        
        # Arco donde cuerda es larga (120°)
        arc_angles = np.linspace(2*np.pi/3, 4*np.pi/3, 50)
        p1.line(np.cos(arc_angles), np.sin(arc_angles), line_color=UBU_YELLOW, line_width=4)
        
        # Punto fijo
        p1.circle([1], [0], size=8, color=UBU_RED)
        
        p1.axis.visible = False
        p1.grid.grid_line_color = None
        p1.title.text_font_size = "14px"
        streamlit_bokeh(p1)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Arco amarillo = 120° (1/3 del total)</b></small>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        # Método 2
        st.markdown(
            "<div class='content-box'><b>Método 2: Radio</b></div>",
            unsafe_allow_html=True
        )
        
        p2 = figure(
            title="P = 1/2",
            width=400,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p2.line(np.cos(theta), np.sin(theta), line_color=UBU_DARK, line_width=2)
        p2.line(np.cos(triangle_angle), np.sin(triangle_angle), line_color=UBU_RED, line_width=2)
        p2.line([0, 0], [0, 1], line_color=UBU_DARK, line_width=2)
        p2.circle([0], [0.5], size=8, color=UBU_YELLOW)
        p2.quad(top=[0.5], bottom=[0], left=[-0.15], right=[0.15], 
               fill_alpha=0.3, fill_color=UBU_YELLOW)
        
        p2.axis.visible = False
        p2.grid.grid_line_color = None
        p2.title.text_font_size = "14px"
        streamlit_bokeh(p2)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Zona amarilla = mitad del radio</b></small>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        # Método 3
        st.markdown(
            "<div class='content-box'><b>Método 3: Punto Medio</b></div>",
            unsafe_allow_html=True
        )
        
        p3 = figure(
            title="P = 1/4",
            width=400,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p3.line(np.cos(theta), np.sin(theta), line_color=UBU_DARK, line_width=2)
        p3.line(np.cos(triangle_angle), np.sin(triangle_angle), line_color=UBU_RED, line_width=2)
        
        circle_small = np.linspace(0, 2*np.pi, 100)
        p3.patch(0.5*np.cos(circle_small), 0.5*np.sin(circle_small), 
                fill_alpha=0.3, fill_color=UBU_YELLOW, line_color=UBU_YELLOW, line_width=2)
        
        p3.axis.visible = False
        p3.grid.grid_line_color = None
        p3.title.text_font_size = "14px"
        streamlit_bokeh(p3)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Círculo amarillo = (1/4) del área total</b></small>",
            unsafe_allow_html=True
        )

# =============================================================================
# 7. PÁGINA 4: BOX-MULLER
# =============================================================================

def render_box_muller():
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>⚙️ Generador Box-Muller</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "Es un transformador matemático que convierte variables uniformes en normales. "
            "Los ordenadores generan fácilmente números uniformes; Box-Muller los moldea para obtener "
            "una distribución normal."
            "</div>",
            unsafe_allow_html=True
        )
        
        if accordion_step("BOXMULLER_A", "A) El Bloque de Construcción"):
            st.markdown("<div class='subsection-title'>A) El Bloque de Construcción</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Los ordenadores solo pueden generar números pseudoaleatorios uniformes "
                "en el intervalo (0, 1):<br>"
                "<b>U₁, U₂ ~ U(0, 1)</b> (independientes)<br>"
                "<b>Nota:</b> Es importante que U₁ ≠ 0 porque necesitamos calcular ln(U₁), "
                "y el logaritmo de 0 es indefinido."
                "</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("BOXMULLER_B", "B) La Transformación: Las Fórmulas"):
            st.markdown("<div class='subsection-title'>B) La Transformación: Las Fórmulas</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El algoritmo Box-Muller toma dos uniformes independientes y aplica:<br>"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "Z₀ = √(-2 ln(U₁)) · cos(2π U₂)<br><br>"
                "Z₁ = √(-2 ln(U₁)) · sin(2π U₂)"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='content-box'>"
                "<b>Resultado:</b> Z₀, Z₁ ~ N(0, 1)<br>"
                "Ambos valores son números normales independientes con media 0 y desviación estándar 1."
                "</div>",
                unsafe_allow_html=True
            )
        
        if accordion_step("BOXMULLER_C", "C) Procedimiento Paso a Paso"):
            st.markdown("<div class='subsection-title'>C) Procedimiento Paso a Paso</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Paso 1: Generar dos uniformes independientes</b><br>"
                "Se generan U₁ y U₂ de manera aleatoria e independiente, ambas en (0, 1). "
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Paso 2: Transformación logarítmica de U₁</b><br>"
                "Se calcula: <b>r = √(-2 ln(U₁))</b><br>"
                "El logaritmo natural de un uniforme también es uniforme, y la expresión √(-2 ln) "
                "produce la magnitud (radio) en coordenadas polares."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Paso 3: Transformación angular de U₂</b><br>"
                "Se calcula: <b>θ = 2π U₂</b><br>"
                "Como U₂ es uniforme en (0, 1), el ángulo θ es uniforme en (0, 2π). "
                "Esto representa una rotación aleatoria en el plano."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>Paso 4: Conversión a coordenadas cartesianas</b><br>"
                "Se aplican funciones trigonométricas:<br><br>"
                "<b>Z₀ = r · cos(θ)</b><br>"
                "<b>Z₁ = r · sin(θ)</b><br><br>"
                "Esto transforma las coordenadas polares (r, θ) a coordenadas cartesianas (Z₀, Z₁)."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>¿Por qué funciona?</b><br><br>"
                "La clave matemática es que en el plano normal bidimensional, el radio r y el ángulo θ "
                "son independientes: el radio sigue una distribución de Rayleigh, y el ángulo es uniforme. "
                "La combinación √(-2 ln(U₁)) genera exactamente la distribución de Rayleigh necesaria. "
                "Al transformar a cartesianas, obtenemos dos normales independientes N(0, 1)."
                "</div>",
                unsafe_allow_html=True
            )
        
        n_samples = st.slider("Número de muestras", 100, 5000, 1000, step=100, key="bm_samples")
        
        st.markdown(
            f"<div class='content-box'>"
            f"Generando <b>{n_samples}</b> pares uniformes y transformando a normales..."
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Generar muestras
        np.random.seed(42)
        U1 = np.random.uniform(0, 1, n_samples)
        U2 = np.random.uniform(0, 1, n_samples)
        
        # Transformar a normales
        Z0 = np.sqrt(-2 * np.log(U1)) * np.cos(2 * np.pi * U2)
        Z1 = np.sqrt(-2 * np.log(U1)) * np.sin(2 * np.pi * U2)
        
        # Histograma de uniformes
        st.markdown(
            "<div class='content-box'><b>Entrada: Distribución Uniforme</b></div>",
            unsafe_allow_html=True
        )
        
        p_unif = figure(
            title="U₁ ~ U(0, 1)",
            x_axis_label="Valor",
            y_axis_label="Frecuencia",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        
        hist_u, edges_u = np.histogram(U1, bins=30)
        p_unif.quad(top=hist_u, bottom=0, left=edges_u[:-1], right=edges_u[1:],
                   fill_color=UBU_YELLOW, line_color=UBU_RED, alpha=0.7, line_width=1.5)
        
        p_unif.title.text_font_size = "14px"
        streamlit_bokeh(p_unif)
        
        st.markdown(
            "<small style='text-align: center; color: var(--muted-fg);'><b>Forma rectangular: todos los valores con igual probabilidad</b></small>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        # Histograma de normales
        st.markdown(
            "<div class='content-box'><b>Salida: Distribución Normal</b></div>",
            unsafe_allow_html=True
        )
        
        p_norm = figure(
            title="Z₀ ~ N(0, 1)",
            x_axis_label="Valor",
            y_axis_label="Frecuencia",
            width=500,
            height=300,
            toolbar_location=None,
            tools=""
        )
        
        hist_z, edges_z = np.histogram(Z0, bins=30)
        p_norm.quad(top=hist_z, bottom=0, left=edges_z[:-1], right=edges_z[1:],
                   fill_color=UBU_YELLOW, line_color=UBU_RED, alpha=0.7, line_width=1.5)
        
        # Teórica normal
        x_theory = np.linspace(-4, 4, 100)
        y_theory = norm.pdf(x_theory) * n_samples * (edges_z[1] - edges_z[0])
        p_norm.line(x_theory, y_theory, line_width=2.5, color=GREEN_LINE)
        
        p_norm.title.text_font_size = "14px"
        streamlit_bokeh(p_norm)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>μ<br>{Z0.mean():.3f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>σ<br>{Z0.std():.3f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>N muestras<br>{n_samples}</div>", unsafe_allow_html=True)

# =============================================================================
# 8. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Distribución Uniforme: Aplicaciones y Paradojas</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    # Navegación
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    if nav_col1.button("Encuentro Amantes", use_container_width=True):
        st.session_state["page"] = "AMANTES"
        st.rerun()
    if nav_col2.button("Espera Autobús", use_container_width=True):
        st.session_state["page"] = "AUTOBUS"
        st.rerun()
    if nav_col3.button("Paradoja Bertrand", use_container_width=True):
        st.session_state["page"] = "BERTRAND"
        st.rerun()
    if nav_col4.button("Box-Muller", use_container_width=True):
        st.session_state["page"] = "BOXMULLER"
        st.rerun()
    
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    # Mostrar página seleccionada
    if st.session_state["page"] == "AMANTES":
        render_amantes()
    elif st.session_state["page"] == "AUTOBUS":
        render_autobus()
    elif st.session_state["page"] == "BERTRAND":
        render_bertrand()
    elif st.session_state["page"] == "BOXMULLER":
        render_box_muller()
    
    st.markdown("<div class='footer-license'>C1VIC D4TA · Universidad de Burgos</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
