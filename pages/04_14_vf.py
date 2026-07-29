import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
from scipy.stats import norm, f, t
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Distribuciones Continuas")

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
        st.session_state["page"] = "SNEDECOR"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "SNEDECOR_A"

# =============================================================================
# 3. RENDERS - SECCIONES
# =============================================================================

def render_snedecor():
    """Sección: Distribución de Snedecor (F)"""
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>📊 Distribución de Snedecor (F)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>distribución de Snedecor</b> (también llamada <b>distribución F</b>) "
            "surge del cociente de dos varianzas muestrales independientes, cada una dividida "
            "por sus grados de libertad. Es fundamental en inferencia estadística, especialmente "
            "en análisis de varianza (ANOVA)."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>A. Definición</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Si <b>U</b> y <b>V</b> son variables aleatorias independientes que siguen "
            "distribuciones chi-cuadrado con <i>m</i> y <i>n</i> grados de libertad respectivamente, "
            "entonces:"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>F = (U/m) / (V/n)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "sigue una distribución F de Snedecor con <b><i>m</i> grados de libertad en el numerador</b> "
            "y <b><i>n</i> grados de libertad en el denominador</b>. Se denota como <b>F(m,n)</b>."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>B. Propiedades</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>1. Rango:</b> F > 0 (siempre positiva)<br><br>"
            "<b>2. Simetría:</b> Asimétrica hacia la derecha<br><br>"
            "<b>3. Esperanza:</b> E[F] = n/(n-2) para n > 2<br><br>"
            "<b>4. Varianza:</b> Var(F) = 2n²(m+n-2) / [m(n-2)²(n-4)] para n > 4<br><br>"
            "<b>5. Relación con chi-cuadrado:</b> F(1,n) = [χ²(1)]² / χ²(n)<br><br>"
            "<b>6. Relación con t-Student:</b> Si T ~ t(n), entonces T² ~ F(1,n)"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>C. Aplicaciones</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "• <b>ANOVA:</b> Comparar medias de 3+ grupos<br>"
            "• <b>Relación entre distribuciones:</b>cómo se relaciona con la Normal, t-Student<br>"
            "• <b>Propiedades:</b> Cómo cambia la distribución según los grados de libertad<br>"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización: Distribución F</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>Parámetros</div>",
            unsafe_allow_html=True
        )
        
        m_df = st.slider("Grados de libertad (m) - numerador", 1, 50, 5, 1, key="f_m")
        n_df = st.slider("Grados de libertad (n) - denominador", 1, 50, 10, 1, key="f_n")
        
        # Generar datos
        x_vals = np.linspace(0.01, 5, 500)
        y_vals = f.pdf(x_vals, m_df, n_df)
        
        # Gráfico
        p = figure(
            title=f"F({m_df}, {n_df})",
            x_axis_label="Valor de F",
            y_axis_label="Densidad",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.line(x_vals, y_vals, line_width=3, color=BLUE_LINE, alpha=0.8)
        p.title.text_font_size = "18px"
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        
        streamlit_bokeh(p)
        
        # Estadísticos
        st.markdown(
            "<div class='subsection-title'>Estadísticos</div>",
            unsafe_allow_html=True
        )
        
        if n_df > 2:
            media = n_df / (n_df - 2)
            media_str = f"{media:.3f}"
        else:
            media_str = "∞"
        
        if n_df > 4:
            var = (2 * n_df**2 * (m_df + n_df - 2)) / (m_df * (n_df - 2)**2 * (n_df - 4))
            var_str = f"{var:.3f}"
        else:
            var_str = "∞"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='metric-box metric-a'>Media<br>{media_str}</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div class='metric-box metric-b'>Varianza<br>{var_str}</div>",
                unsafe_allow_html=True
            )
        with col3:
            quantil = f.ppf(0.95, m_df, n_df)
            st.markdown(
                f"<div class='metric-box metric-c'>Q(0.95)<br>{quantil:.3f}</div>",
                unsafe_allow_html=True
            )

def render_student():
    """Sección: Distribución t de Student"""
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>📊 Distribución t de Student</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>distribución t de Student</b> es fundamental en estadística inferencial. "
            "Surge naturalmente al estandarizar la media muestral cuando la varianza poblacional "
            "es desconocida. Con muestras pequeñas tiene colas más pesadas que la normal, "
            "aproximándose a esta cuando n → ∞."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>A. Definición</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Si <b>Z</b> ~ N(0,1) y <b>χ²(n)</b> es una variable chi-cuadrado con <i>n</i> grados de libertad, "
            "independientes entre sí, entonces:"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>T = Z / √(χ²(n)/n)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "sigue una distribución <b>t de Student</b> con <i>n</i> grados de libertad, "
            "denotada como <b>T(n)</b> o <b>t<sub>n</sub></b>."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>B. Propiedades</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>1. Simetría:</b> Simétrica alrededor de 0 (como la normal)<br><br>"
            "<b>2. Colas pesadas:</b> Más colas que N(0,1) para n pequeño<br><br>"
            "<b>3. Esperanza:</b> E[T] = 0 (para n > 1)<br><br>"
            "<b>4. Varianza:</b> Var(T) = n/(n-2) (para n > 2)<br><br>"
            "<b>5. Convergencia:</b> T(n) → N(0,1) cuando n → ∞<br><br>"
            "<b>6. Cuantiles:</b> t<sub>n,α/2</sub> para intervalos de confianza"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>C. Aplicaciones</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "• <b>IC para μ:</b> Intervalo de confianza para media con σ desconocida<br>"
            "• <b>Contraste T:</b> Comparar media muestral con valor teórico<br>"
            "• <b>Diferencia de medias:</b> Dos muestras independientes o pareadas<br>"
            "• <b>Regresión:</b> Significancia de coeficientes"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización: Distribución t</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>Parámetros</div>",
            unsafe_allow_html=True
        )
        
        n_df = st.slider("Grados de libertad (n)", 1, 100, 10, 1, key="t_n")
        
        # Generar datos
        x_vals = np.linspace(-5, 5, 500)
        y_vals_t = t.pdf(x_vals, n_df)
        y_vals_norm = norm.pdf(x_vals, 0, 1)
        
        # Gráfico
        p = figure(
            title=f"t({n_df}) vs N(0,1)",
            x_axis_label="Valor",
            y_axis_label="Densidad",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.line(x_vals, y_vals_t, line_width=3, color=BLUE_LINE, alpha=0.8, legend_label=f"t({n_df})")
        p.line(x_vals, y_vals_norm, line_width=2.5, color=GREEN_LINE, alpha=0.6, legend_label="N(0,1)")
        p.title.text_font_size = "18px"
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        p.legend.location = "top_right"
        
        streamlit_bokeh(p)
        
        # Estadísticos
        st.markdown(
            "<div class='subsection-title'>Comparativa</div>",
            unsafe_allow_html=True
        )
        
        if n_df > 2:
            var_t = n_df / (n_df - 2)
            var_t_str = f"{var_t:.3f}"
        else:
            var_t_str = "∞"
        
        q_t = t.ppf(0.975, n_df)
        q_norm = norm.ppf(0.975)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='metric-box metric-a'>Var(t)<br>{var_t_str}</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div class='metric-box metric-b'>t<sub>0.975</sub><br>{q_t:.3f}</div>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<div class='metric-box metric-c'>z<sub>0.975</sub><br>{q_norm:.3f}</div>",
                unsafe_allow_html=True
            )

def render_moivre():
    """Sección: Tipificación de Moivre-Laplace"""
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>⚡ Tipificación de Moivre-Laplace</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "La <b>tipificación</b> (o <b>estandarización</b>) es la transformación "
            "de una variable aleatoria normal en una <b>variable aleatoria normal estándar</b> N(0,1). "
            "Este proceso es fundamental para usar tablas de la distribución normal y resolver "
            "problemas de probabilidad."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>A. Concepto</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Si <b>X ~ N(μ, σ)</b> (variable normal con media μ y desv. estándar σ), "
            "entonces la variable tipificada es:"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>Z = (X - μ) / σ</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Esta nueva variable <b>Z</b> tiene distribución <b>N(0,1)</b>, es decir, "
            "media 0 y desviación estándar 1. Entonces: <b>E[Z] = 0</b> y <b>σ(Z) = 1</b>."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>B. Propiedades</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>1. Linealidad:</b> Si X ~ N(μ, σ), entonces Z = (X-μ)/σ ~ N(0,1)<br><br>"
            "<b>2. Reversibilidad:</b> X = μ + σ·Z<br><br>"
            "<b>3. Probabilidades:</b> P(X < a) = P(Z < (a-μ)/σ)<br><br>"
            "<b>4. Tabla estándar:</b> Usamos φ(z) = P(Z ≤ z) de la tabla N(0,1)<br><br>"
            "<b>5. Simetría:</b> φ(-z) = 1 - φ(z)"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>C. Procedimiento</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Paso 1:</b> Identificar μ y σ de X ~ N(μ, σ)<br><br>"
            "<b>Paso 2:</b> Aplicar fórmula Z = (X - μ) / σ<br><br>"
            "<b>Paso 3:</b> Buscar P(Z ≤ valor) en tabla N(0,1)<br><br>"
            "<b>Paso 4:</b> Usar propiedades de simetría si es necesario"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización: Tipificación</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>Parámetros de X</div>",
            unsafe_allow_html=True
        )
        
        mu = st.slider("Media (μ)", -50.0, 50.0, 0.0, 5.0, key="moivre_mu")
        sigma = st.slider("Desv. Estándar (σ)", 0.5, 15.0, 1.0, 0.5, key="moivre_sigma")
        
        # Generar datos
        x_vals = np.linspace(mu - 4*sigma, mu + 4*sigma, 500)
        y_vals_x = norm.pdf(x_vals, mu, sigma)
        
        z_vals = (x_vals - mu) / sigma
        y_vals_z = norm.pdf(z_vals, 0, 1)
        
        # Gráfico
        p = figure(
            title=f"X ~ N({mu:.1f}, {sigma:.1f})",
            x_axis_label="Valor de X",
            y_axis_label="Densidad",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.line(x_vals, y_vals_x, line_width=3, color=BLUE_LINE, alpha=0.8)
        p.title.text_font_size = "18px"
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        
        streamlit_bokeh(p)
        
        st.markdown(
            "<div class='subsection-title'>Transformación</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"<div class='formula-box'>Z = (X - {mu:.1f}) / {sigma:.1f}</div>",
            unsafe_allow_html=True
        )
        
        # Estadísticos
        col1, col2 = st.columns(2)
        with col1:
            x_val = st.number_input("Evaluar X en:", value=mu, step=0.1, key="x_eval")
            z_val = (x_val - mu) / sigma
            prob_z = norm.cdf(z_val)
            
            st.markdown(
                f"<div class='metric-box metric-a'>Z = {z_val:.3f}</div>",
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"<div class='metric-box metric-b'>P(X ≤ {x_val:.1f}) = {prob_z:.4f}</div>",
                unsafe_allow_html=True
            )

def render_problema071():
    """Sección: Problema 071 - Calibración de máquina"""
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>🏭 Problema 071: Calibración de Máquina</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='statement-box'>"
            "Una máquina está programada para llenar recipientes con 10 litros de capacidad. "
            "Sin embargo, la variabilidad inherente en cualquier máquina es la causa de que las "
            "cantidades de contenido sean distintas de recipiente a recipiente. Si la distribución "
            "del contenido que arroja la máquina en cada recipiente es normal con una desviación "
            "típica de 0.02 litros:"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>Apartado (a)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Determinar a qué cantidad media objetivo de llenado debe calibrarse la máquina para "
            "asegurar que sólo el 5% de los recipientes reciban menos de los 10 litros estipulados."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>B. Datos del Problema</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>•</b> X = cantidad de líquido por recipiente (litros)<br>"
            "<b>•</b> X ~ N(μ, 0.02) donde μ es desconocido<br>"
            "<b>•</b> Desviación típica: σ = 0.02 litros<br>"
            "<b>•</b> Condición: P(X < 10) = 0.05<br>"
            "<b>•</b> Capacidad mínima: 10 litros"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>C. Demostración</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Paso 1: Tipificar la variable</b><br>"
            "Como X ~ N(μ, 0.02), tipificamos:<br><br>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>P(X < 10) = P((X - μ)/0.02 < (10 - μ)/0.02)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Si Z = (X - μ)/0.02 ~ N(0,1), entonces:<br>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>P(X < 10) = P(Z < (10 - μ)/0.02) = 0.05</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Paso 2: Buscar en tabla N(0,1)</b><br>"
            "Buscamos en las tablas de la distribución normal estándar el valor de z tal que "
            "Φ(z) = 0.05. Como la probabilidad es menor a 0.5, estamos en la cola izquierda "
            "(z negativo). La tabla muestra que Φ(-1.645) ≈ 0.05<br><br>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>(10 - μ)/0.02 = -1.645</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Paso 3: Despejar μ</b><br>"
            "10 - μ = -1.645 × 0.02<br>"
            "10 - μ = -0.0329<br>"
            "μ = 10 + 0.0329<br>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>μ = 10.0329 litros</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Conclusión:</b> La máquina debe calibrarse para una media de "
            "<b>10.0329 litros</b> (aproximadamente 10.03 litros). "
            "Así, el 5% de los recipientes recibirán menos de 10 litros, "
            "cumpliendo con el requisito especificado."
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización Interactiva</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='subsection-title'>Simulación</div>",
            unsafe_allow_html=True
        )
        
        mu_real = 10.0329
        sigma = 0.02
        
        n_sim = st.slider("Número de recipientes simulados", 1000, 10000, 5000, 1000, key="prob_n")
        
        # Simulación
        np.random.seed(42)
        muestras = np.random.normal(mu_real, sigma, n_sim)
        
        # Contar recipientes con < 10 litros
        menores_10 = np.sum(muestras < 10)
        porcentaje = (menores_10 / n_sim) * 100
        
        # Histograma con línea en 10
        hist, edges = np.histogram(muestras, bins=40)
        
        p = figure(
            title=f"Distribución X ~ N(10.0329, 0.02)",
            x_axis_label="Contenido (litros)",
            y_axis_label="Frecuencia",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=1, alpha=0.7)
        
        # Línea en 10 litros
        max_hist = np.max(hist)
        p.line([10, 10], [0, max_hist], line_width=3, color=ORANGE_ACCENT, alpha=0.8, legend_label="X = 10 L")
        
        p.title.text_font_size = "18px"
        p.xaxis.axis_label_text_font_size = "16px"
        p.yaxis.axis_label_text_font_size = "16px"
        p.legend.location = "top_right"
        
        streamlit_bokeh(p)
        
        st.markdown(
            "<div class='subsection-title'>Resultados</div>",
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"<div class='metric-box metric-a'>Media<br>{mu_real:.4f} L</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div class='metric-box metric-b'>Desv. Est.<br>{sigma:.4f} L</div>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<div class='metric-box metric-c'>% < 10 L<br>{porcentaje:.2f}%</div>",
                unsafe_allow_html=True
            )
        
        st.markdown(
            "<div class='content-box'>"
            f"<b>Recipientes con menos de 10 litros:</b> {menores_10} de {n_sim} ({porcentaje:.2f}%)<br><br>"
            f"<b>Probabilidad teórica:</b> 5.00%<br>"
            f"<b>Diferencia:</b> {abs(porcentaje - 5):.2f}%"
            "</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown(
        "<div class='top-bar-title'>C1VIC D4TA · Distribuciones Continuas</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    if nav_col1.button("Snedecor (F)", use_container_width=True):
        st.session_state.update({"page": "SNEDECOR"}); st.rerun()
    if nav_col2.button("Student (t)", use_container_width=True):
        st.session_state.update({"page": "STUDENT"}); st.rerun()
    if nav_col3.button("Moivre-Laplace", use_container_width=True):
        st.session_state.update({"page": "MOIVRE"}); st.rerun()
    if nav_col4.button("Problema 071", use_container_width=True):
        st.session_state.update({"page": "PROBLEMA"}); st.rerun()
    
    paginas = {
        "SNEDECOR": render_snedecor,
        "STUDENT": render_student,
        "MOIVRE": render_moivre,
        "PROBLEMA": render_problema071,
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
