import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Estadística Descriptiva")

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

# =============================================================================
# 3. FUNCIONES RENDER - PÁGINAS
# =============================================================================

def render_intro():
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "La <b>Estadística Descriptiva</b> resume y describe los aspectos clave de un conjunto de datos. "
            "Aprenderemos cómo la <b>media</b>, <b>mediana</b>, <b>moda</b>, <b>varianza</b> y otros indicadores "
            "nos ayudan a entender la distribución y características de nuestros datos."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>Conceptos Fundamentales</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>A. Media (Esperanza)</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "La <b>media</b> es el valor promedio de todos los datos. Se calcula sumando todos los valores "
            "y dividiendo entre la cantidad de datos."
            "<div class='formula-box'>μ = Σxᵢ/n</div>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>B. Mediana</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "La <b>mediana</b> es el valor central cuando los datos están ordenados. Si hay un número par de datos, "
            "es el promedio de los dos valores centrales. Es <b>robusta</b> a valores extremos/atípicos (outliers)."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>C. Moda</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "La <b>moda</b> es el valor que aparece con mayor frecuencia en el conjunto de datos. "
            "Un conjunto puede ser unimodal, bimodal o multimodal."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>D. Varianza y Desviación Estándar</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "La <b>varianza</b> mide qué tan dispersos están los datos respecto a la media. "
            "La <b>desviación estándar</b> (σ) es su raíz cuadrada."
            "<div class='formula-box'>Var(X) = E[(X - μ)²]<br>σ = √Var(X)</div>"
            "</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Visualización de Conceptos</b></div>",
            unsafe_allow_html=True
        )
        
        # Datos de ejemplo
        np.random.seed(42)
        datos = np.concatenate([np.random.normal(50, 8, 80), [100]])  # con un outlier
        
        media = np.mean(datos)
        mediana = np.median(datos)
        std = np.std(datos)
        varianza = np.var(datos)
        
        # Encontrar la moda (bin con mayor frecuencia)
        hist, edges = np.histogram(datos, bins=20)
        max_bin_idx = np.argmax(hist)
        moda_aprox = (edges[max_bin_idx] + edges[max_bin_idx + 1]) / 2
        
        # Gráfico de distribución
        p = figure(
            title="Distribución de Datos (con Outlier)",
            x_axis_label="Valor",
            y_axis_label="Frecuencia",
            width=500,
            height=350,
            toolbar_location=None,
            tools=""
        )
        
        # Histograma normal
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=1.5, alpha=0.8, legend_label="Frecuencia")
        
        # Resaltar bin de la moda
        p.quad(top=[hist[max_bin_idx]], bottom=0, left=[edges[max_bin_idx]], right=[edges[max_bin_idx+1]],
               fill_color=UBU_RED, line_color="white", line_width=1.5, alpha=1.0, legend_label="Moda")
        
        # Línea de media
        p.line([media, media], [0, max(hist)], line_color=GREEN_LINE, line_width=3, legend_label="Media")
        
        # Línea de mediana
        p.line([mediana, mediana], [0, max(hist)*0.9], line_color=ORANGE_ACCENT, line_width=3, legend_label="Mediana")
        
        # Área sombreada ±σ
        p.quad(left=[media - std], right=[media + std], bottom=0, top=max(hist)*0.6,
               fill_color=UBU_YELLOW, line_color=UBU_YELLOW, alpha=0.15, legend_label="Rango ±σ")
        
        # Bandas ±σ
        p.line([media + std, media + std], [0, max(hist)*0.5], line_color=UBU_YELLOW, line_width=3, 
               line_dash="dashed", alpha=0.8)
        p.line([media - std, media - std], [0, max(hist)*0.5], line_color=UBU_YELLOW, line_width=3, 
               line_dash="dashed", alpha=0.8, legend_label=f"±σ")
        
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        p.title.text_font_size = "18px"
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "14px"
        streamlit_bokeh(p)
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Estadísticos Calculados:</b><br><br>"
            f"<b>Tendencia Central:</b><br>"
            f"📊 Media: <b>{media:.2f}</b><br>"
            f"📈 Mediana: <b>{mediana:.2f}</b><br>"
            f"🎯 Moda (aprox.): <b>{moda_aprox:.2f}</b><br><br>"
            f"<b>Dispersión:</b><br>"
            f"📉 Varianza: <b>{varianza:.2f}</b><br>"
            f"σ Desv. Est.: <b>{std:.2f}</b><br>"
            f"Rango ±σ: [{media - std:.2f}, {media + std:.2f}]<br>"
            f"</div>",
            unsafe_allow_html=True
        )

def render_temperature():
    """Ejemplo 1: Chiste "medio quemado, medio congelado" - Media vs Desviación Típica"""
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "<b>El Chiste del \"Medio Quemado, Medio Congelado\"</b><br><br>"
            "Un señor está parado en un horno (100°C) y otro en un congelador (0°C). "
            "En promedio, ambos están a una \"temperatura perfecta\" de 50°C. "
            "¿Pero realmente están cómodos?"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>¿Por qué falla la Media?</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>media</b> es sensible a valores extremos. Cuando hay mucha dispersión, "
            "el promedio puede ser engañoso. La <b>desviación estándar</b> nos dice la dispersión "
            "real de los datos."
            "<div class='formula-box'>σ = √(E[(X - μ)²])</div>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>Controles Interactivos</div>", unsafe_allow_html=True)
        
        # Sliders para las temperaturas
        temp_hot = st.slider("🔥 Temperatura Horno (°C)", 0.0, 100.0, 100.0, 5.0, key="temp_hot")
        temp_cold = st.slider("❄️ Temperatura Congelador (°C)", 0.0, 100.0, 0.0, 5.0, key="temp_cold")
        
        # Cálculos
        media = (temp_hot + temp_cold) / 2
        varianza = ((temp_hot - media)**2 + (temp_cold - media)**2) / 2
        desv_est = np.sqrt(varianza)
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Resultados:</b><br>"
            f"Media: {media:.1f}°C<br>"
            f"Varianza: {varianza:.1f}<br>"
            f"Desviación Estándar: {desv_est:.1f}°C"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📈 Visualización: Distribución de Temperaturas</b></div>",
            unsafe_allow_html=True
        )
        
        media = (temp_hot + temp_cold) / 2
        desv_est = np.sqrt(((temp_hot - media)**2 + (temp_cold - media)**2) / 2)
        
        # Crear gráfico de dispersión
        p = figure(
            title="Temperatura del Horno vs Congelador",
            x_axis_label="Posición",
            y_axis_label="Temperatura (°C)",
            width=500,
            height=350,
            toolbar_location=None,
            tools=""
        )
        
        # Puntos
        p.scatter([0, 1], [temp_cold, temp_hot], size=15, color=[BLUE_LINE, ORANGE_ACCENT], alpha=0.8)
        
        # Línea de media
        p.line([-0.5, 1.5], [media, media], line_color=GREEN_LINE, line_width=3, 
               legend_label=f"Media: {media:.1f}°C")
        
        # Bandas de ±σ
        p.line([-0.5, 1.5], [media + desv_est, media + desv_est], line_color=ORANGE_ACCENT, 
               line_width=2, line_dash="dashed", alpha=0.6)
        p.line([-0.5, 1.5], [media - desv_est, media - desv_est], line_color=ORANGE_ACCENT, 
               line_width=2, line_dash="dashed", alpha=0.6, legend_label=f"±σ: ±{desv_est:.1f}°C")
        
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        p.title.text_font_size = "18px"
        p.legend.location = "top_right"
        streamlit_bokeh(p)
        
        st.markdown(
            "<div class='content-box'>"
            "<b>📌 Conclusión:</b><br>"
            "La desviación estándar es sensible a la diferencia entre los valores. Cuanto mayor sea la brecha "
            "entre el horno y el congelador, mayor será la dispersión. La media es simplemente el punto "
            "central, pero no nos dice nada sobre cómo están distribuidos los datos."
            "</div>",
            unsafe_allow_html=True
        )

def render_gini():
    """Ejemplo 2: Índice de Gini - División de Clases"""
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "<b>Índice de Gini: Pureza vs. Impureza</b><br><br>"
            "El Índice de Gini mide cuán mezcladas están dos (o más) clases en un conjunto de datos. "
            "Los árboles de decisión lo usan para saber dónde cortar (dividir) los datos."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>¿Qué es Gini?</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'>"
            "El <b>Índice de Gini</b> cuantifica la impureza de un conjunto de datos. "
            "Gini = 0 significa <b>pureza total</b> (todos los datos de la misma clase). "
            "Gini = 0.5 significa <b>máxima impureza</b> (50% de cada clase)."
            "<div class='formula-box'>Gini = 1 - Σ(pᵢ)²</div>"
            "donde pᵢ es la proporción de la clase i."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>Simulación Interactiva</div>", unsafe_allow_html=True)
        
        # Sliders para la distribución
        n_red = st.slider("🔴 Datos Rojos", 0, 100, 50, 5, key="n_red")
        n_blue = st.slider("🔵 Datos Azules", 0, 100, 50, 5, key="n_blue")
        
        total = n_red + n_blue
        if total == 0:
            total = 1
        
        p_red = n_red / total
        p_blue = n_blue / total
        
        gini = 1 - (p_red**2 + p_blue**2)
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Cálculo Paso a Paso:</b><br>"
            f"<b>1. Proporciones:</b><br>"
            f"p₁ (Rojos) = {n_red}/{total} = {p_red:.3f}<br>"
            f"p₂ (Azules) = {n_blue}/{total} = {p_blue:.3f}<br>"
            f"<b>2. Cuadrados:</b><br>"
            f"p₁² = {p_red:.3f}² = {p_red**2:.3f}<br>"
            f"p₂² = {p_blue:.3f}² = {p_blue**2:.3f}<br>"
            f"<b>3. Suma:</b><br>"
            f"Σ(pᵢ)² = {p_red**2:.3f} + {p_blue**2:.3f} = {(p_red**2 + p_blue**2):.3f}<br>"
            f"<b>4. Fórmula Final:</b><br>"
            f"Gini = 1 - {(p_red**2 + p_blue**2):.3f} = <b style='color:#E67E22; font-size:28px;'>{gini:.3f}</b>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Visualización: Pureza vs. Impureza</b></div>",
            unsafe_allow_html=True
        )
        
        total = n_red + n_blue
        if total == 0:
            total = 1
        
        p_red = n_red / total
        p_blue = n_blue / total
        gini = 1 - (p_red**2 + p_blue**2)
        
        # Gráfico de barras
        p = figure(
            title=f"Composición de Clases (Gini = {gini:.3f})",
            x_axis_label="Clase",
            y_axis_label="Cantidad",
            width=500,
            height=350,
            x_range=["Rojos", "Azules"],
            toolbar_location=None,
            tools=""
        )
        
        p.vbar(x=["Rojos", "Azules"], top=[n_red, n_blue], width=0.5, 
               color=[UBU_RED, BLUE_LINE], alpha=0.8)
        
        p.title.text_font_size = "18px"
        streamlit_bokeh(p)
        
        # Gauge de Gini
        col_gauge1, col_gauge2 = st.columns(2)
        
        with col_gauge1:
            st.metric("Gini Index", f"{gini:.3f}", 
                     delta=None, delta_color="off")
        
        with col_gauge2:
            if gini < 0.1:
                estado = "✅ Muy Puro"
            elif gini < 0.3:
                estado = "🟢 Puro"
            elif gini < 0.5:
                estado = "🟡 Mixto"
            else:
                estado = "🔴 Muy Impuro"
            st.markdown(
                f"<div class='metric-box'>{estado}</div>",
                unsafe_allow_html=True
            )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>📌 Conclusión:</b><br>"
            "Cuando Gini = 0 (todas las muestras de una clase), el nodo es puro y no necesita dividirse más. "
            "Cuando Gini es alto, hay mucha mezcla: el árbol necesita crear divisiones adicionales."
            "</div>",
            unsafe_allow_html=True
        )

def render_robustness():
    """Ejemplo 3: Robustez - Media vs. Mediana con Outliers"""
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>"
            "<b>Robustez: Media vs. Mediana</b><br><br>"
            "5 personas normales con sueldos promedio... hasta que llega un multimillonario. "
            "¿Cómo afecta eso a nuestros estadísticos?"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>¿Cuál es más Robusto?</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>media</b> es sensible a valores extremos (outliers): un solo valor muy alto o muy bajo "
            "puede cambiarla dramáticamente.<br><br>"
            "La <b>mediana</b> es <b>robusta</b>: el valor central permanece estable incluso con outliers presentes."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>Simulación Interactiva</div>", unsafe_allow_html=True)
        
        # Sueldos base de 5 personas
        sueldos_base = np.array([30000, 35000, 40000, 38000, 42000], dtype=float)
        
        # Slider para el sueldo del multimillonario
        sueldo_billonario = st.slider("💰 Sueldo del Multimillonario (€)", 
                                     42000.0, 1000000.0, 100000.0, 50000.0, key="sueldo_bill")
        
        # Todos los sueldos
        todos_sueldos = np.append(sueldos_base, sueldo_billonario)
        
        media = np.mean(todos_sueldos)
        mediana = np.median(todos_sueldos)
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Estadísticos:</b><br>"
            f"Media: €{media:,.0f}<br>"
            f"Mediana: €{mediana:,.0f}<br>"
            f"Diferencia: €{abs(media - mediana):,.0f}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>💼 Distribución de Sueldos</b></div>",
            unsafe_allow_html=True
        )
        
        sueldos_base = np.array([30000, 35000, 40000, 38000, 42000], dtype=float)
        todos_sueldos = np.append(sueldos_base, sueldo_billonario)
        
        media = np.mean(todos_sueldos)
        mediana = np.median(todos_sueldos)
        
        # Gráfico de barras
        personas = ["P1", "P2", "P3", "P4", "P5", "Multimillonario"]
        colores = [BLUE_LINE, BLUE_LINE, BLUE_LINE, BLUE_LINE, BLUE_LINE, ORANGE_ACCENT]
        
        p = figure(
            title="Sueldos de 6 Personas",
            x_axis_label="Persona",
            y_axis_label="Sueldo (€)",
            width=500,
            height=350,
            x_range=personas,
            toolbar_location=None,
            tools=""
        )
        
        p.vbar(x=personas, top=todos_sueldos.tolist(), width=0.6, 
               color=colores, alpha=0.8)
        
        # Líneas de media y mediana
        p.line([-0.5, 5.5], [media, media], line_color=GREEN_LINE, line_width=3, 
               legend_label=f"Media: €{media:,.0f}")
        p.line([-0.5, 5.5], [mediana, mediana], line_color=PANTONE_2727, line_width=3, 
               legend_label=f"Mediana: €{mediana:,.0f}")
        
        p.title.text_font_size = "18px"
        p.legend.location = "top_left"
        streamlit_bokeh(p)
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>📌 Conclusión:</b><br>"
            f"La <b>media</b> saltó a €{media:,.0f} (inflada por el multimillonario).<br>"
            f"La <b>mediana</b> se quedó en €{mediana:,.0f} (resistió al outlier).<br>"
            f"<br>Para datos con outliers, la mediana es más representativa."
            f"</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Estadística Descriptiva</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO"}); st.rerun()
    if nav_col2.button("(I) Temperatura", use_container_width=True):
        st.session_state.update({"page": "TEMP", "open_step": "TEMP_A"}); st.rerun()
    if nav_col3.button("(II) Índice Gini", use_container_width=True):
        st.session_state.update({"page": "GINI", "open_step": "GINI_A"}); st.rerun()
    if nav_col4.button("(III) Robustez", use_container_width=True):
        st.session_state.update({"page": "ROBUST", "open_step": "ROBUST_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "TEMP": render_temperature,
        "GINI": render_gini,
        "ROBUST": render_robustness,
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
