import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
from scipy.stats import norm, poisson
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Desigualdades")

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

/* ---- Spoiler ---- */
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

/* ---- Inputs ---- */
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
        st.session_state["page"] = "P0"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "P0"

init_session_state()

# =============================================================================
# 3. FUNCIONES DE RENDERIZADO
# =============================================================================

def render_markov_chebyshev():
    """Apartado A: Desigualdades de Markov y Chebyshev"""
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>Las desigualdades de Markov y Chebyshev son herramientas de probabilidad que sirven para acotar "
            "probabilidades cuando solo se conocen la media y/o la varianza. Markov funciona solo para variables no negativas, mientras "
            "que Chebyshev se aplica a cualquier variable con varianza finita.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>A. Desigualdades de Markov y Chebyshev</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>1. Desigualdad de Markov</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>Enunciado:</b> Sea X una variable aleatoria no negativa con media E[X]. Para cualquier a > 0:"
            "</div>",
            unsafe_allow_html=True
        )
        st.latex(r"P(X \geq a) \leq \frac{E[X]}{a}")
        
        # Spoiler para demostración
        unique_id_markov = str(uuid.uuid4())
        st.markdown(f"""
        <input class='spoiler-toggle' id='spoiler_{unique_id_markov}' type='checkbox'>
        <label class='spoiler-click-wrapper' for='spoiler_{unique_id_markov}'>
            <div class='spoiler-box'>
            <b>Demostración (Caso Continuo)</b><br><br>
            1. Partimos de la esperanza matemática:<br>
            E[X] = ∫₀^∞ x·f(x) dx<br><br>
            2. Separamos la integral en dos partes:<br>
            E[X] = ∫₀^a x·f(x) dx + ∫ₐ^∞ x·f(x) dx<br><br>
            3. Eliminamos la primera integral (es no negativa):<br>
            E[X] ≥ ∫ₐ^∞ x·f(x) dx<br><br>
            4. Reemplazamos x por a (como cota inferior):<br>
            E[X] ≥ ∫ₐ^∞ a·f(x) dx = a·∫ₐ^∞ f(x) dx<br><br>
            5. Reconocemos la integral como probabilidad:<br>
            E[X] ≥ a·P(X ≥ a)<br><br>
            6. Dividimos entre a > 0:<br>
            P(X ≥ a) ≤ E[X]/a ✓ <br><br>
            TAREA: Demuestra el caso discreto.
            </div>
        </label>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>2. Desigualdad de Chebyshev</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>Enunciado:</b> Sea X una variable aleatoria con media μ y varianza σ². Para cualquier k > 0:"
            "</div>",
            unsafe_allow_html=True
        )
        st.latex(r"P(|X - \mu| \geq k) \leq \frac{\sigma^2}{k^2}")
        
        st.markdown(
            "<div class='content-box' style='background: #fff9e6;'>"
            "<b>O en forma normalizada (k = m·σ):</b>"
            "</div>",
            unsafe_allow_html=True
        )
        st.latex(r"P(|X - \mu| \geq m\sigma) \leq \frac{1}{m^2}")
        
        unique_id_cheby = str(uuid.uuid4())
        st.markdown(f"""
        <input class='spoiler-toggle' id='spoiler_{unique_id_cheby}' type='checkbox'>
        <label class='spoiler-click-wrapper' for='spoiler_{unique_id_cheby}'>
            <div class='spoiler-box'>
            <b>Demostración</b><br><br>
            1. Definimos una variable no negativa:<br>
            Y = (X - μ)² ≥ 0<br><br>
            2. Aplicamos Markov a Y con a = k²:<br>
            P(Y ≥ k²) ≤ E[Y] / k²<br><br>
            3. Sustituimos Y = (X - μ)²:<br>
            P((X - μ)² ≥ k²) ≤ E[(X - μ)²] / k²<br><br>
            4. Reconocemos equivalencias:<br>
            • El evento (X - μ)² ≥ k² ⟺ |X - μ| ≥ k<br>
            • E[(X - μ)²] = σ²<br><br>
            5. Reemplazamos:<br>
            P(|X - μ| ≥ k) ≤ σ² / k²<br><br>
            6. Si k = m·σ (número de desviaciones):<br>
            P(|X - μ| ≥ m·σ) ≤ σ² / (m²σ²) = 1/m² ✓
            </div>
        </label>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>3. Interpretación</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>Forma General:</b> La cota depende de σ:"
            "</div>",
            unsafe_allow_html=True
        )
        st.latex(r"P(|X - \mu| \geq k) \leq \frac{\sigma^2}{k^2}")
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Forma Normalizada (en desviaciones típicas):</b> Si expresamos k = m·σ (donde m es el número de desviaciones típicas):"
            "</div>",
            unsafe_allow_html=True
        )
        st.latex(r"P(|X - \mu| \geq m\sigma) \leq \frac{1}{m^2}")
        
        st.markdown(
            "<div class='content-box'>"
            "Esta forma simplificada <b>1/m²</b> es independiente de σ y funciona para <b>cualquier distribución</b> con varianza finita:"
            "<br><br>"
            "<b>m=1:</b> P(|X - μ| ≥ σ) ≤ 1/1² = 100%<br>"
            "<b>m=2:</b> P(|X - μ| ≥ 2σ) ≤ 1/2² = 25%<br>"
            "<b>m=3:</b> P(|X - μ| ≥ 3σ) ≤ 1/3² ≈ 11.1%<br>"
            "<b>m=4:</b> P(|X - μ| ≥ 4σ) ≤ 1/4² = 6.25%"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Visualización: Cota Superior de Chebyshev</b></div>",
            unsafe_allow_html=True
        )
        st.markdown("En forma normalizada:", unsafe_allow_html=True)
        st.latex(r"P(|X - \mu| \geq m \cdot \sigma) \leq \frac{1}{m^2}")
        
        m_values = np.linspace(0.5, 5, 100)
        chebyshev_bounds = 1 / m_values**2
        
        p = figure(
            title="P(|X - μ| ≥ m·σ) ≤ 1/m²",
            x_axis_label="m (número de desviaciones típicas)",
            y_axis_label="Cota superior de probabilidad",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        p.line(m_values, chebyshev_bounds, line_width=3, color=BLUE_LINE, legend_label="Cota = 1/m²")
        p.circle(m_values[::10], chebyshev_bounds[::10], size=8, color=BLUE_LINE, alpha=0.6)
        
        # Añade puntos específicos
        for m in [1, 2, 3, 4]:
            bound = 1 / m**2
            p.circle([m], [bound], size=12, color=UBU_RED, alpha=0.8)
            
        p.title.text_font_size = "16px"
        p.legend.location = "top_right"
        streamlit_bokeh(p)
        
        st.markdown(
            "<div class='content-box'><b>🔍 Interpretación:</b><br>"
            "• Conforme aumentamos m (alejarse más de la media en desviaciones típicas), la cota disminuye exponencialmente<br>"
            "• A m=2: máximo 25% de los datos puede estar fuera del intervalo [μ-2σ, μ+2σ]<br>"
            "• A m=3: máximo 11.1% de los datos puede estar fuera del intervalo [μ-3σ, μ+3σ]"
            "</div>",
            unsafe_allow_html=True
        )


def render_arbitrary_distribution():
    """Apartado B: Distribución Arbitraria con Markov"""
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>Markov funciona con CUALQUIER distribución de valores no negativos. Solo necesita el valor de la esperanza.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>B. Distribución Arbitraria y Markov</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>Parámetros de la simulación</div>", unsafe_allow_html=True)
        
        dist_type = st.radio(
            "Elige una distribución:",
            ["Uniforme", "Exponencial", "Lognormal"],
            key="dist_type"
        )
        
        if dist_type == "Uniforme":
            a_unif = st.slider("Límite inferior a", 0.0, 5.0, 1.0, 0.5, key="a_unif")
            b_unif = st.slider("Límite superior b", 5.0, 20.0, 10.0, 1.0, key="b_unif")
            np.random.seed(42)
            samples = np.random.uniform(a_unif, b_unif, 5000)
            mean = (a_unif + b_unif) / 2
            dist_name = f"Uniforme({a_unif}, {b_unif})"
        
        elif dist_type == "Exponencial":
            lambda_exp = st.slider("Parámetro λ", 0.1, 2.0, 0.5, 0.1, key="lambda_exp")
            np.random.seed(42)
            samples = np.random.exponential(1/lambda_exp, 5000)
            mean = 1/lambda_exp
            dist_name = f"Exponencial(λ={lambda_exp})"
        
        else:  # Lognormal
            mu_ln = st.slider("Parámetro μ (log)", 0.0, 2.0, 0.5, 0.2, key="mu_ln")
            sigma_ln = st.slider("Parámetro σ (log)", 0.1, 1.0, 0.5, 0.1, key="sigma_ln")
            np.random.seed(42)
            samples = np.random.lognormal(mu_ln, sigma_ln, 5000)
            mean = np.exp(mu_ln + sigma_ln**2 / 2)
            dist_name = f"Lognormal(μ={mu_ln}, σ={sigma_ln})"
        
        a_threshold = st.slider("Umbral a para P(X ≥ a)", mean * 0.5, mean * 3, mean * 1.5, mean * 0.1, key="a_threshold")
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Distribución:</b> {dist_name}<br>"
            f"<b>Media E[X]:</b> {mean:.3f}<br>"
            f"<b>Umbral a:</b> {a_threshold:.3f}<br>"
            f"<b>Cota Markov:</b> P(X ≥ {a_threshold:.3f}) ≤ {mean/a_threshold:.3f}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Distribución y Cota de Markov</b></div>",
            unsafe_allow_html=True
        )
        
        hist, edges = np.histogram(samples, bins=40, range=(0, np.percentile(samples, 99)))
        
        p = figure(
            title=f"{dist_name}",
            x_axis_label="Valor",
            y_axis_label="Frecuencia",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", line_width=1.5, alpha=0.7)
        
        # Línea del umbral
        p.line([a_threshold, a_threshold], [0, max(hist)], 
               line_width=3, color=UBU_RED, legend_label=f"a = {a_threshold:.2f}")
        
        p.title.text_font_size = "16px"
        p.legend.location = "top_right"
        streamlit_bokeh(p)
        
        # Probabilidades reales vs Markov
        prob_real = np.sum(samples >= a_threshold) / len(samples)
        prob_markov = mean / a_threshold
        
        st.markdown(
            f"<div class='content-box'>"
            f"<b>Probabilidad Real:</b> P(X ≥ a) = {prob_real:.4f}<br>"
            f"<b>Cota Markov:</b> P(X ≥ a) ≤ {prob_markov:.4f}<br>"
            f"<b>Factor de holgura:</b> {prob_markov / max(prob_real, 0.0001):.2f}x"
            f"</div>",
            unsafe_allow_html=True
        )


def render_normal_comparison():
    """Apartado C: Distribución Normal y Chebyshev"""
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Chebyshev</b> no asume nada sobre la forma de la distribución (por eso es tan potente y general), "
            "pero paga el precio siendo muy conservadora, es decir, da una cota superior muy amplia u holgada comparada con la realidad. " 
            "La <b>Normal</b>, en cambio, tiene estructura: sabemos exactamente cómo se distribuyen los datos alrededor de la media.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>C. Normal vs Chebyshev</div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box' style='background: #fff3e0; border-color: " + ORANGE_ACCENT + ";'>"
            "<b>¿Por qué no aplicamos Markov aquí?</b><br>"
            "Markov requiere que X ≥ 0 (variables no negativas). La distribución normal puede tomar valores negativos, así que Markov "
            "no se aplica. En cambio, Chebyshev funciona para cualquier distribución con varianza finita, independientemente de si puede ser negativa."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>Parámetros Normal</div>", unsafe_allow_html=True)
        
        mu_normal = st.slider("Media μ", -5.0, 5.0, 0.0, 0.5, key="mu_normal")
        sigma_normal = st.slider("Desv. Est. σ", 0.5, 3.0, 1.0, 0.2, key="sigma_normal")
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Cotas Chebyshev (válidas para cualquier distribución):</b><br>"
            "• P(|X - μ| ≥ σ) ≤ 1/1² = 100%<br>"
            "• P(|X - μ| ≥ 2σ) ≤ 1/2² = 25%<br>"
            "• P(|X - μ| ≥ 3σ) ≤ 1/3² ≈ 11.1%"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>Comparación de cotas</div>", unsafe_allow_html=True)
        
        m_values = np.array([1, 2, 3, 4])
        chebyshev_upper = 1 / m_values**2
        normal_real = 2 * (1 - norm.cdf(m_values))
        
        st.markdown(
            "<div class='content-box'>"
            f"<b>m=1:</b> Cheby ≤ 100%, Normal ≈ {normal_real[0]*100:.1f}%<br>"
            f"<b>m=2:</b> Cheby ≤ 25%, Normal ≈ {normal_real[1]*100:.1f}%<br>"
            f"<b>m=3:</b> Cheby ≤ 11.1%, Normal ≈ {normal_real[2]*100:.2f}%<br>"
            f"<b>m=4:</b> Cheby ≤ 6.25%, Normal ≈ {normal_real[3]*100:.3f}%"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Normal vs Chebyshev</b></div>",
            unsafe_allow_html=True
        )
        
        # Gráfico de la distribución normal
        x_vals = np.linspace(mu_normal - 4*sigma_normal, mu_normal + 4*sigma_normal, 500)
        y_vals = norm.pdf(x_vals, mu_normal, sigma_normal)
        
        p = figure(
            title=f"N({mu_normal}, {sigma_normal}²)",
            x_axis_label="Valor",
            y_axis_label="Densidad",
            width=500,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        p.line(x_vals, y_vals, line_width=2.5, color=BLUE_LINE, legend_label="Normal")
        
        # Sombrear regiones
        for k, color in [(1, "#2e7d32"), (2, "#E67E22"), (3, UBU_RED)]:
            left = mu_normal - k * sigma_normal
            right = mu_normal + k * sigma_normal
            idx = (x_vals >= left) & (x_vals <= right)
            if idx.any():
                p.varea(x=x_vals[idx], y1=0, y2=y_vals[idx], 
                       fill_color=color, fill_alpha=0.15, legend_label=f"±{k}σ")
        
        p.title.text_font_size = "16px"
        p.legend.location = "top_right"
        streamlit_bokeh(p)
        
        st.markdown(
            "<div class='metric-box metric-a'>Chebyshev es muy conservador</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='metric-box metric-b'>Pero funciona para cualquier distribución</div>",
            unsafe_allow_html=True
        )


def render_poisson_comparison():
    """Apartado D: Distribución de Poisson - Markov vs Chebyshev"""
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'>Poisson modela conteos (X ≥ 0). Aquí podemos aplicar AMBAS desigualdades: Markov y Chebyshev. "
            "Miden cosas diferentes: Markov acota la cola derecha en unidades reales, mientras que Chebyshev acota ambas colas en unidades de desviaciones típicas.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>D. Markov & Chebyshev VS. Poisson</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='subsection-title'>Parámetro λ (tasa media)</div>", unsafe_allow_html=True)
        
        lambda_poisson = st.slider("λ (media = varianza)", 1.0, 50.0, 10.0, 1.0, key="lambda_poisson")
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Distribución de Poisson(λ):</b><br>"
            "• Media: E[X] = λ<br>"
            "• Varianza: Var(X) = λ<br>"
            "• P(X = k) = (e^(-λ) · λ^k) / k!<br><br>"
            "<b>Característica:</b> Cuando λ es pequeño, está sesgada. "
            "Cuando λ → ∞, Poisson → Normal."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "<b>Nota importante:</b> Markov y Chebyshev miden cosas <b>diferentes</b>:<br>"
            "• <b>Markov:</b> P(X ≥ a) acota la cola derecha en unidades reales<br>"
            "• <b>Chebyshev:</b> P(|X - μ| ≥ m·σ) acota ambas colas en unidades de desviaciones típicas"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>1. Cota de Markov (cola derecha)</div>", unsafe_allow_html=True)
        
        # Markov: P(X ≥ a) ≤ λ/a
        a_threshold = st.slider("Umbral a para P(X ≥ a)", lambda_poisson, lambda_poisson * 4, lambda_poisson * 2, lambda_poisson * 0.5, key="a_markov")
        
        prob_markov_bound = lambda_poisson / a_threshold
        
        # Calcular probabilidad real
        x_range_markov = np.arange(0, int(lambda_poisson * 5) + 10)
        pmf_markov = poisson.pmf(x_range_markov, lambda_poisson)
        prob_markov_real = np.sum(pmf_markov[x_range_markov >= a_threshold])
        
        st.markdown(
            "<div class='content-box'>"
            f"<b>P(X ≥ {a_threshold:.1f}):</b><br>"
            f"• Cota Markov: P(X ≥ a) ≤ λ/a = {lambda_poisson}/{a_threshold:.1f} ≤ {prob_markov_bound:.4f}<br>"
            f"• Probabilidad Real: ≈ {prob_markov_real:.4f}<br>"
            f"• Holgura: {prob_markov_bound / max(prob_markov_real, 0.0001):.2f}x"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='subsection-title'>2. Cota de Chebyshev (ambas colas)</div>", unsafe_allow_html=True)
        
        m_vals = np.array([1, 2, 3, 4])
        sigma_pois = np.sqrt(lambda_poisson)
        
        # Calcular probabilidades reales
        prob_real_chebyshev = []
        for m in m_vals:
            # P(|X - λ| ≥ m·σ)
            lower = lambda_poisson - m * sigma_pois
            upper = lambda_poisson + m * sigma_pois
            x_range = np.arange(0, max(int(upper) + 10, 100))
            pmf = poisson.pmf(x_range, lambda_poisson)
            p_outside = np.sum(pmf[(x_range < lower) | (x_range > upper)])
            prob_real_chebyshev.append(p_outside)
        
        prob_chebyshev = 1 / m_vals**2
        
        st.markdown(
            "<div class='content-box'>"
            f"<b>m=1:</b> Real ≈ {prob_real_chebyshev[0]:.3f}, Cheby ≤ {prob_chebyshev[0]:.3f}<br>"
            f"<b>m=2:</b> Real ≈ {prob_real_chebyshev[1]:.3f}, Cheby ≤ {prob_chebyshev[1]:.3f}<br>"
            f"<b>m=3:</b> Real ≈ {prob_real_chebyshev[2]:.3f}, Cheby ≤ {prob_chebyshev[2]:.3f}<br>"
            f"<b>m=4:</b> Real ≈ {prob_real_chebyshev[3]:.3f}, Cheby ≤ {prob_chebyshev[3]:.3f}"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Crear tabs para los tres gráficos
        tab1, tab2, tab3 = st.tabs(["Markov", "Chebyshev", "Comparación Analítica"])
        
        with tab1:
            st.markdown(
                "<div class='content-box'><b>📊 PDF Poisson con Cota Markov</b></div>",
                unsafe_allow_html=True
            )
            
            # Generar PDF de Poisson
            x_range_pmf = np.arange(0, int(lambda_poisson) + 6 * np.sqrt(lambda_poisson) + 1)
            pmf = poisson.pmf(x_range_pmf, lambda_poisson)
            
            p_visual = figure(
                title=f"P(X ≥ {a_threshold:.1f}): Real = {prob_markov_real:.4f} | Markov ≤ {prob_markov_bound:.4f}",
                x_axis_label="k (conteos)",
                y_axis_label="Probabilidad",
                width=500,
                height=400,
                toolbar_location=None,
                tools=""
            )
            
            # Mostrar PDF
            p_visual.circle(x_range_pmf, pmf, size=8, color=BLUE_LINE, alpha=0.6)
            p_visual.line(x_range_pmf, pmf, line_width=1.5, color=BLUE_LINE, alpha=0.5, legend_label="PDF Poisson")
            
            # Sombrear el área donde X ≥ a
            idx_shade = x_range_pmf >= a_threshold
            if idx_shade.any():
                p_visual.varea(
                    x=x_range_pmf[idx_shade], 
                    y1=0, 
                    y2=pmf[idx_shade],
                    fill_color=GREEN_LINE, 
                    fill_alpha=0.3, 
                    legend_label=f"P(X ≥ {a_threshold:.1f})"
                )
            
            # Línea vertical en el umbral a
            p_visual.line([a_threshold, a_threshold], [0, max(pmf)], 
                         line_width=2.5, color=UBU_RED, line_dash="solid", 
                         legend_label=f"Umbral a = {a_threshold:.1f}")
            
            # Línea horizontal para la cota Markov
            p_visual.line(
                [x_range_pmf.min(), x_range_pmf.max()], 
                [prob_markov_bound, prob_markov_bound],
                line_width=2, 
                color=ORANGE_ACCENT, 
                line_dash="dashed",
                legend_label=f"Cota Markov = {prob_markov_bound:.4f}"
            )
            
            p_visual.title.text_font_size = "16px"
            p_visual.legend.location = "top_right"
            streamlit_bokeh(p_visual)
            
            st.markdown(
                "<div class='content-box'><b>🔍 Interpretación:</b><br>"
                "El área verde sombreada muestra P(X ≥ a) real. La línea naranja discontinua es la cota que garantiza Markov. "
                "Markov es conservador: su cota es mayor que la probabilidad real."
                "</div>",
                unsafe_allow_html=True
            )
        
        with tab2:
            st.markdown(
                "<div class='content-box'><b>📊 PDF Poisson con Límites Chebyshev</b></div>",
                unsafe_allow_html=True
            )
            
            # Generar PDF de Poisson
            x_range_cheby = np.arange(0, int(lambda_poisson) + 6 * np.sqrt(lambda_poisson) + 1)
            pmf_cheby = poisson.pmf(x_range_cheby, lambda_poisson)
            
            p_cheby = figure(
                title=f"Poisson(λ={lambda_poisson}): Chebyshev ±2σ y ±3σ",
                x_axis_label="k (conteos)",
                y_axis_label="Probabilidad",
                width=500,
                height=400,
                toolbar_location=None,
                tools=""
            )
            
            # Mostrar PDF
            p_cheby.circle(x_range_cheby, pmf_cheby, size=8, color=BLUE_LINE, alpha=0.6)
            p_cheby.line(x_range_cheby, pmf_cheby, line_width=1.5, color=BLUE_LINE, alpha=0.5, legend_label="PDF Poisson")
            
            # Líneas de Chebyshev
            sigma_pois = np.sqrt(lambda_poisson)
            
            # ±2σ
            for m, color, style in [(2, UBU_RED, "dashed"), (3, ORANGE_ACCENT, "dotted")]:
                left_limit = lambda_poisson - m * sigma_pois
                right_limit = lambda_poisson + m * sigma_pois
                
                p_cheby.line([left_limit, left_limit], [0, max(pmf_cheby)], 
                           line_width=2.5, color=color, line_dash=style, alpha=0.7,
                           legend_label=f"±{m}σ (límite Chebyshev)")
                p_cheby.line([right_limit, right_limit], [0, max(pmf_cheby)], 
                           line_width=2.5, color=color, line_dash=style, alpha=0.7)
            
            p_cheby.title.text_font_size = "16px"
            p_cheby.legend.location = "top_right"
            streamlit_bokeh(p_cheby)
            
            st.markdown(
                f"<div class='content-box'><b>🔍 Interpretación:</b><br>"
                f"Las líneas punteadas marcan donde Chebyshev garantiza que están los datos:<br>"
                f"• <b>Líneas rojas (±2σ):</b> Chebyshev garantiza al menos 75% dentro<br>"
                f"• <b>Líneas naranjas (±3σ):</b> Chebyshev garantiza al menos 89% dentro<br>"
                f"• En realidad, Poisson es más concentrado: la mayoría está dentro de ±2σ"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with tab3:
            st.markdown(
                "<div class='content-box'><b>📊 Comparación Analítica: Markov vs Chebyshev</b></div>",
                unsafe_allow_html=True
            )
            
            # Para Markov: P(X ≥ a)
            a_values = np.linspace(lambda_poisson * 0.5, lambda_poisson * 4, 30)
            markov_bounds = lambda_poisson / a_values
            
            prob_real_markov_array = []
            for a in a_values:
                x_range_temp = np.arange(0, max(int(a + 10), 100))
                pmf_temp = poisson.pmf(x_range_temp, lambda_poisson)
                p_real = np.sum(pmf_temp[x_range_temp >= a])
                prob_real_markov_array.append(p_real)
            
            prob_real_markov_array = np.array(prob_real_markov_array)
            
            # Para Chebyshev: P(|X - λ| ≥ m·σ) en diferentes m
            m_vals = np.array([0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4])
            sigma_pois = np.sqrt(lambda_poisson)
            chebyshev_bounds = 1 / m_vals**2
            
            prob_real_chebyshev_array = []
            for m in m_vals:
                lower = lambda_poisson - m * sigma_pois
                upper = lambda_poisson + m * sigma_pois
                x_range_temp = np.arange(0, max(int(upper) + 10, 100))
                pmf_temp = poisson.pmf(x_range_temp, lambda_poisson)
                p_outside = np.sum(pmf_temp[(x_range_temp < lower) | (x_range_temp > upper)])
                prob_real_chebyshev_array.append(p_outside)
            
            prob_real_chebyshev_array = np.array(prob_real_chebyshev_array)
            
            p_comparacion = figure(
                title=f"Markov vs Chebyshev: Cotas y Realidad",
                x_axis_label="Parámetro (a para Markov, m para Chebyshev)",
                y_axis_label="Probabilidad",
                width=500,
                height=400,
                toolbar_location=None,
                tools=""
            )
            
            # Markov
            p_comparacion.line(a_values, markov_bounds, line_width=2.5, color=UBU_RED, legend_label="Cota Markov: λ/a")
            p_comparacion.circle(a_values, prob_real_markov_array, size=6, color=BLUE_LINE, alpha=0.7, legend_label="Real (cola derecha)")
            
            # Chebyshev
            p_comparacion.line(m_vals, chebyshev_bounds, line_width=2.5, color=ORANGE_ACCENT, line_dash="dashed", legend_label="Cota Chebyshev: 1/m²")
            p_comparacion.circle(m_vals, prob_real_chebyshev_array, size=6, color=GREEN_LINE, alpha=0.7, legend_label="Real (ambas colas)")
            
            p_comparacion.title.text_font_size = "16px"
            p_comparacion.legend.location = "top_right"
            streamlit_bokeh(p_comparacion)
            
            st.markdown(
                "<div class='content-box'><b>🔍 Interpretación:</b><br>"
                "<b>Rojo (Markov):</b> Acota cola derecha P(X ≥ a). Cota = λ/a. Mide en unidades reales.<br>"
                "<b>Naranja (Chebyshev):</b> Acota ambas colas P(|X-μ| ≥ m·σ). Cota = 1/m². Mide en desviaciones típicas.<br>"
                "<b>Puntos azules/verdes:</b> Las probabilidades reales de Poisson. Ambas cotas están siempre por encima (conservadoras)."
                "</div>",
                unsafe_allow_html=True
            )
        
        st.markdown(
            f"<div class='metric-box metric-a'>λ = {lambda_poisson} | σ = √λ = {np.sqrt(lambda_poisson):.2f}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='metric-box metric-b'>Markov: P(X ≥ a) acota cola derecha. <br> "
            "Chebyshev: P(|X-μ| ≥ m·σ) acota ambas colas.</div>",
            unsafe_allow_html=True
        )


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Desigualdades de Markov y Chebyshev</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("I) Desigualdades", use_container_width=True):
        st.session_state["page"] = "P0"
        st.rerun()
    if nav_col2.button("II) Distribución arbitraria", use_container_width=True):
        st.session_state["page"] = "P1"
        st.rerun()
    if nav_col3.button("III) vs. Normal", use_container_width=True):
        st.session_state["page"] = "P2"
        st.rerun()
    if nav_col4.button("IV) vs. Poisson", use_container_width=True):
        st.session_state["page"] = "P3"
        st.rerun()

    paginas = {
        "P0": render_markov_chebyshev,
        "P1": render_arbitrary_distribution,
        "P2": render_normal_comparison,
        "P3": render_poisson_comparison,
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
