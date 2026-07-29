import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span, HoverTool
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="Máxima Verosimilitud: Bernoulli vs Normal")

# Colores
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"

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
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600&display=swap');

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
    display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
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
.spacer {{ height: 35px; }}

.formula-box {{
    border: 3px solid {BLUE_LINE}; border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 27px; color: {BLUE_LINE};
}}

.metric-box {{
    font-size: 24px; color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px;
}}

.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: 20px 25px; text-align: center;
    font-style: italic; font-size: 25px; color: var(--box-fg);
    margin-top: 20px; width: 100%;
}}
.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px;
}}

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

/* ---- Number inputs ---- */
[data-testid="stNumberInput"] input {{
    font-size: 25px !important; font-weight: 600 !important;
}}
[data-testid="stNumberInput"] label p, .stNumberInput label p {{
    font-size: 25px !important; color: var(--app-fg) !important;
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {"page": "I"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def style_axes(p, label_size="20px", tick_size="16px"):
    p.xaxis.axis_label_text_font_size = label_size
    p.yaxis.axis_label_text_font_size = label_size
    p.xaxis.major_label_text_font_size = tick_size
    p.yaxis.major_label_text_font_size = tick_size
    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    return p

def planteamiento_header():
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Parámetros:</div>", unsafe_allow_html=True)

def create_bernoulli_likelihood_chart(n, k):
    """Crea gráfico de verosimilitud L(p) para Bernoulli."""
    p_vals = np.linspace(0.001, 0.999, 200)
    likelihood_vals = np.power(p_vals, k) * np.power(1 - p_vals, n - k)
    
    p_mle = k / n
    lik_max = np.power(p_mle, k) * np.power(1 - p_mle, n - k)
    
    plot = figure(
        height=300, width=500,
        x_axis_label="p (probabilidad)",
        y_axis_label="L(p) (Verosimilitud)",
        toolbar_location=None,
        x_range=(0, 1),
        y_range=(0, lik_max * 1.1)
    )
    
    plot.line(p_vals, likelihood_vals, line_width=3, color=BLUE_LINE, alpha=0.8)
    plot.varea(x=p_vals, y1=0, y2=likelihood_vals, color=BLUE_LINE, alpha=0.15)
    
    # Marcar el MLE
    plot.circle([p_mle], [lik_max], size=15, color=GREEN_LINE, line_color="white", line_width=3)
    
    # Línea vertical en MLE
    vline = Span(location=p_mle, dimension="height", line_color=GREEN_LINE, 
                 line_dash="dashed", line_width=2)
    plot.add_layout(vline)
    
    return style_axes(plot)

def create_bernoulli_data_chart(n, k):
    """Crea gráfico de datos observados (barras)."""
    caras = k
    cruces = n - k
    
    plot = figure(
        height=300, width=500,
        x_range=["Caras", "Cruces"],
        y_axis_label="Conteo",
        toolbar_location=None
    )
    
    plot.vbar(x=["Caras", "Cruces"], top=[caras, cruces], width=0.6,
              color=[BLUE_LINE, GREEN_LINE], alpha=0.8, line_color="white", line_width=2)
    
    return style_axes(plot)

def create_normal_data_chart(data):
    """Crea histograma de datos normales."""
    hist, edges = np.histogram(data, bins=12)
    
    plot = figure(
        height=300, width=500,
        x_axis_label="Valor",
        y_axis_label="Frecuencia",
        toolbar_location=None
    )
    
    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
              fill_color=BLUE_LINE, line_color="white", alpha=0.7, line_width=2)
    
    return style_axes(plot)

def create_normal_loglik_chart(data, mu_true, sigma):
    """Crea gráfico de log-verosimilitud como función de μ."""
    n = len(data)
    mean = np.mean(data)
    
    mu_range = np.linspace(mean - 4*sigma/np.sqrt(n), mean + 4*sigma/np.sqrt(n), 200)
    loglik_vals = []
    
    for mu_test in mu_range:
        sum_sq = np.sum((data - mu_test) ** 2)
        loglik = -0.5 * n * np.log(2 * np.pi * sigma**2) - (1 / (2 * sigma**2)) * sum_sq
        loglik_vals.append(loglik)
    
    loglik_vals = np.array(loglik_vals)
    loglik_max = loglik_vals.max()
    
    plot = figure(
        height=300, width=500,
        x_axis_label="μ (media)",
        y_axis_label="ℓ(μ) (Log-Verosimilitud)",
        toolbar_location=None
    )
    
    plot.line(mu_range, loglik_vals, line_width=3, color=BLUE_LINE, alpha=0.8)
    plot.varea(x=mu_range, y1=loglik_vals.min(), y2=loglik_vals, color=BLUE_LINE, alpha=0.15)
    
    # Marcar el MLE
    plot.circle([mean], [loglik_max], size=15, color=GREEN_LINE, line_color="white", line_width=3)
    
    # Línea vertical en MLE
    vline = Span(location=mean, dimension="height", line_color=GREEN_LINE, 
                 line_dash="dashed", line_width=2)
    plot.add_layout(vline)
    
    return style_axes(plot), mean, np.var(data), loglik_max

# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_mle_bernoulli():
    """Sección I: Distribución Bernoulli (Moneda)"""
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Moneda: ¿Cuál es la probabilidad p?</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Lanzas una moneda <b>n</b> veces y obtienes <b>k</b> caras. "
            "La pregunta es: ¿cuál es el valor de p (probabilidad de cara) que hace <b>máxima</b> "
            "la probabilidad de observar exactamente estos datos?"
            "</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        
        col_n, col_k = st.columns(2)
        with col_n:
            n = st.number_input("Lanzamientos (n)", min_value=1, max_value=500, value=20)
        with col_k:
            k = st.number_input("Caras (k)", min_value=0, max_value=500, value=12)
        
        if k > n:
            st.error("⚠️ El número de caras no puede exceder el número de lanzamientos")
            return
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>Fórmula:</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='formula-box'>L(p) = p<sup>k</sup> × (1-p)<sup>n-k</sup></div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='blue-spoiler-container'>", unsafe_allow_html=True)
        with st.expander("📖 Mostrar cómo se llega a esta función de verosimilitud"):
            st.markdown(
                "Tenemos $n$ lanzamientos, luego $x = \\{x_1, x_2, \\dots, x_n\\}$.\n\n"
                "Sea $p \\in [0,1]$. Asignamos los siguientes valores:\n"
                "* Si $x_i = 1$, sale cara con probabilidad $p$.\n"
                "* Si $x_i = 0$, sale cruz con probabilidad $1-p$.\n\n"
                "$$L(p|x) = \\prod_{i=1}^n p^{x_i}(1-p)^{1-x_i} = p^{\\sum_{i=1}^{n} x_i} \\cdot (1-p)^{\\sum_{i=1}^{n} (1-x_i)}$$\n\n"
                "Tomamos $k = \\sum_{i=1}^{n} x_i$ como el número total de caras y "
                "$n-k = \\sum_{i=1}^{n} (1-x_i)$ como el número total de cruces.\n\n"
                "Entonces la función de verosimilitud queda de la siguiente manera:\n"
                "$$L(p) = p^k \\cdot (1-p)^{n-k}$$\n"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>EMV (Estimador de Máxima Verosimilitud):</b><br>"
            "<div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>p̂ = k/n</div>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='blue-spoiler-container'>", unsafe_allow_html=True)
        with st.expander("🧮 Mostrar demostración paso a paso"):
            st.markdown(
                "### Demostración matemática:\n\n"
                "**1. Aplicar logaritmo:**\n"
                "$$\\ell(p) = \\ln(L(p))$$\n"
                "$$= k \\cdot \\ln(p) + (n-k) \\cdot \\ln(1-p)$$\n\n"
                "**2. Derivar con respecto a p:**\n"
                "$$\\frac{d\\ell}{dp} = \\frac{k}{p} - \\frac{n-k}{1-p}$$\n\n"
                "**3. Igualar a cero:**\n"
                "$$\\frac{d\\ell}{dp} = 0$$\n"
                "$$\\frac{k}{p} - \\frac{n-k}{1-p} = 0$$\n"
                "$$\\frac{k}{p} = \\frac{n-k}{1-p}$$\n\n"
                "**4. Despejar p:**\n"
                "$$k(1-p) = p(n-k)$$\n"
                "$$k - kp = pn - kp$$\n"
                "$$k = pn$$\n"
                "$$p = \\frac{k}{n} = \\hat{p}$$\n"
            )
        st.markdown(
            "<div class='content-box'><b>Interpretación:</b><br>"
            "El EMV es simplemente la <b>proporción de caras</b> que observaste. "
            "Cuanto mayor sea n, más puntiaguda se volverá la curva de verosimilitud,"
            "lo que refleja mayor certeza en la estimación.</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        p_mle = k / n
        lik_max = (p_mle ** k) * ((1 - p_mle) ** (n - k))
        log_lik = k * np.log(p_mle + 1e-10) + (n - k) * np.log(1 - p_mle + 1e-10)
        
        # Gráfico de datos
        st.markdown("#### Datos Observados", help="Conteo de caras y cruces")
        data_chart = create_bernoulli_data_chart(n, k)
        streamlit_bokeh(data_chart, use_container_width=True)
        
        # Gráfico de verosimilitud
        st.markdown("#### Función de Verosimilitud L(p)", help="La curva muestra cuán probable es cada valor de p")
        lik_chart = create_bernoulli_likelihood_chart(n, k)
        streamlit_bokeh(lik_chart, use_container_width=True)
        
        # Resultados
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Resultados:</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box'><b>p̂ (EMV)</b><br>{p_mle:.4f}</div>",
                       unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box'><b>L(p̂)</b><br>{lik_max:.6f}</div>",
                       unsafe_allow_html=True)

def render_mle_normal():
    """Sección II: Distribución Normal"""
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Datos Continuos: ¿Cuál es la media μ?</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Tienes <b>n</b> observaciones de una distribución normal con media <b>desconocida</b>. "
            "¿Cuál es el valor de μ que hace <b>máxima</b> la verosimilitud de los datos observados?"
            "</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        
        col_mu, col_sigma, col_samp = st.columns(3)
        with col_mu:
            mu_true = st.number_input("Media verdadera (μ)", min_value=-20.0, max_value=20.0, value=5.0, step=0.5)
        with col_sigma:
            sigma = st.number_input("Desv. Estándar (σ)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        with col_samp:
            n = st.number_input("Tamaño muestral (n)", min_value=5, max_value=500, value=50, step=5)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>Fórmula:</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='formula-box'>ℓ(μ) = -n/2 × log(2πσ²) - 1/(2σ²) × Σ(xᵢ - μ)²</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='blue-spoiler-container'>", unsafe_allow_html=True)
        with st.expander("📖 Mostrar cómo se llega a esta función de verosimilitud"):
            st.markdown(
                "Sabemos que la función de densidad de una distribución normal es de la siguiente manera:\n"
                "$$f(x|\\mu,\\sigma^2)=\\frac{1}{\\sigma\\sqrt{2\\pi}}\\exp\\left(\\frac{-(x-\\mu)^2}{2\\sigma^2}\\right)$$\n\n"
                "Como en nuestro caso el tamaño muestral es $n$, la función de verosimilitud es:\n"
                "$$L(x_1, \\dots, x_n \\mid \\mu, \\sigma^2) = \\prod_{i=1}^n \\left[ \\frac{1}{\\sigma\\sqrt{2\\pi}} \\exp\\left( \\frac{-(x_i-\\mu)^2}{2\\sigma^2} \\right) \\right]$$\n"
                "$$= \\frac{1}{(\\sigma\\sqrt{2\\pi})^n} \\exp\\left( -\\frac{\\sum_{i=1}^n (x_i-\\mu)^2}{2\\sigma^2} \\right)$$\n\n"
                "Tomando logaritmos y aplicando las propiedades de los logaritmos llegamos a la expresión deseada."
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>EMV (Estimador de Máxima Verosimilitud):</b><br>"
            "<div style='font-size: 28px; font-weight: bold; margin: 10px 0;'>μ̂ = x̄ (media muestral)</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='blue-spoiler-container'>", unsafe_allow_html=True)
        with st.expander("🧮 Mostrar Demostración Matemática paso a paso"):
            st.markdown(
                "### Demostración matemática:\n\n"
                "$$\\textbf{1. Derivar } \\ell(\\mu) \\textbf{ con respecto a } \\mu:$$\n"
                "$$\\ell(\\mu) = -\\frac{n}{2} \\ln(2\\pi\\sigma^2) - \\frac{1}{2\\sigma^2} \\sum_{i=1}^n (x_i - \\mu)^2$$\n"
                "$$\\frac{d\\ell}{d\\mu} = 0 - \\frac{1}{2\\sigma^2} \\cdot \\sum_{i=1}^n 2(x_i - \\mu) \\cdot (-1)$$\n"
                "$$\\frac{d\\ell}{d\\mu} = \\frac{1}{\\sigma^2} \\sum_{i=1}^n (x_i - \\mu)$$\n\n"
                "$$\\textbf{2. Igualar a cero:}$$\n"
                "$$\\frac{d\\ell}{d\\mu} = 0 \\implies \\frac{1}{\\sigma^2} \\sum_{i=1}^n (x_i - \\mu) = 0$$\n"
                "$$\\implies \\sum_{i=1}^n x_i - \\sum_{i=1}^n \\mu = 0 \\implies \\sum_{i=1}^n x_i - n\\mu = 0$$\n\n"
                "$$\\textbf{3. Despejar } \\mu:$$\n"
                "$$n\\mu = \\sum_{i=1}^n x_i \\implies \\mu = \\frac{\\sum_{i=1}^n x_i}{n} = \\bar{x}$$\n"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='content-box'><b>Nota sobre log-verosimilitud:</b><br>"
            "Hacemos el cambio <b>ℓ(μ) = log(L(μ))</b> porque L(μ) es tan minúscula (~10<sup>-50</sup>) "
            "que es imperceptible. El máximo de log(L) está en el mismo lugar que el máximo de L, "
            "pero es numéricamente visible. La curva tiene forma de <b>parábola invertida</b>.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'><b>Interpretación:</b><br>"
            "Cuanto mayor sea n, más puntiaguda será la parábola, lo que refleja "
            "mayor certeza en que la verdadera media está cerca de x̄.</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Generar datos
        np.random.seed(42)
        data = np.random.normal(mu_true, sigma, n)
        mean = np.mean(data)
        variance = np.var(data)
        
        # Gráfico de datos
        st.markdown("#### Histograma de Datos", help="Distribución de las observaciones")
        data_chart = create_normal_data_chart(data)
        streamlit_bokeh(data_chart, use_container_width=True)
        
        # Gráfico de log-verosimilitud
        st.markdown("#### Log-Verosimilitud ℓ(μ)", help="Parábola invertida con máximo en x̄")
        loglik_chart, mu_mle, sigma_mle, loglik_max = create_normal_loglik_chart(data, mu_true, sigma)
        streamlit_bokeh(loglik_chart, use_container_width=True)
        
        # Resultados
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Resultados:</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box'><b>μ̂ (media)</b><br>{mu_mle:.4f}</div>",
                       unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box'><b>σ̂² (var.)</b><br>{sigma_mle:.4f}</div>",
                       unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box'><b>ℓ(μ̂)</b><br>{loglik_max:.2f}</div>",
                       unsafe_allow_html=True)

# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown(
        "<div class='top-bar-title'>Máxima Verosimilitud: Bernoulli vs Normal</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2 = st.columns(2)
    
    if nav_col1.button("(I) Bernoulli — Moneda", use_container_width=True):
        st.session_state["page"] = "I"
        st.rerun()
    if nav_col2.button("(II) Normal — Datos Continuos", use_container_width=True):
        st.session_state["page"] = "II"
        st.rerun()
    
    paginas = {
        "I": render_mle_bernoulli,
        "II": render_mle_normal,
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
