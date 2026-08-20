#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
import math
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Tipos de Estimadores")

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

/* CAJA PARA CONTROLES */
div.st-key-controls_box {{
    border: 4px solid {UBU_RED} !important; border-radius: 12px !important;
    padding: 30px 40px !important; background: var(--box-bg) !important;
    margin-bottom: 30px; margin-top: 10px;
}}
div.st-key-controls_box p {{
    color: var(--box-fg) !important;
    font-size: 25px !important;
    font-weight: 700 !important;
    margin-bottom: 20px !important;
    line-height: 1.3 !important;
}}

.metric-box {{
    font-size: 24px; color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px;
}}

.stats-container {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px; margin-bottom: 20px; width: 100%;
}}
.stat-box {{
    background: var(--box-bg); border: 3px solid {UBU_YELLOW};
    border-radius: 12px; padding: 20px; text-align: center;
}}
.stat-label {{ font-size: 20px; font-weight: 600; color: var(--box-fg); margin-bottom: 8px; }}
.stat-value {{ font-size: 30px; font-weight: 700; color: {UBU_RED}; }}

.seq-box {{
    font-family: 'Consolas', monospace; font-size: 22px; letter-spacing: 4px;
    border: 2px solid var(--metric-border); border-radius: 10px;
    padding: 12px 18px; background: var(--box-bg); color: var(--box-fg);
    margin-bottom: 12px;
}}

.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px;
}}

button p {{ font-size: 24px !important; }}
div[data-testid="column"] button {{ padding-top: 15px !important; padding-bottom: 15px !important; }}

div[data-testid="stSlider"] > div {{
    display: flex !important;
    flex-direction: column-reverse !important;
}}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {{
    display: block !important;
    font-size: 30px !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
[data-testid="stThumbValue"] {{
    display: block !important;
    font-size: 30px !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
.stSlider [data-baseweb="slider"] {{ padding-top: 50px; padding-bottom: 5px; }}
.stSlider {{ margin-bottom: 5px; }}

[data-testid="stNumberInput"] input {{ font-size: 22px !important; font-weight: 600 !important; }}
[data-testid="stNumberInput"] label p, .stNumberInput label p {{ font-size: 22px !important; color: var(--app-fg) !important; }}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "A",
        "biased_estimates": [],
        "unbiased_estimates": [],
        "suf_seqs": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def style_axes(p, label_size="18px", tick_size="15px"):
    p.xaxis.axis_label_text_font_size = label_size
    p.yaxis.axis_label_text_font_size = label_size
    p.xaxis.major_label_text_font_size = tick_size
    p.yaxis.major_label_text_font_size = tick_size
    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    return p

def planteamiento_header():
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Parámetros de la simulación:</div>", unsafe_allow_html=True)

# ---- A) Insesgadez ----------------------------------------------------------

def draw_variance_histogram(estimates, true_var, color, title):
    if len(estimates) == 0:
        p = figure(height=260, width=520, title=title, toolbar_location=None,
                   x_axis_label="σ̂² estimado", y_axis_label="Frecuencia")
        return style_axes(p)

    hist, edges = np.histogram(estimates, bins=30)
    p = figure(height=260, width=520, title=title, toolbar_location=None,
               x_axis_label="σ̂² estimado", y_axis_label="Frecuencia")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=color, line_color="white", alpha=0.75, line_width=1)

    v_true = Span(location=true_var, dimension="height", line_color=UBU_DARK,
                  line_dash="dashed", line_width=3)
    p.add_layout(v_true)
    v_mean = Span(location=float(np.mean(estimates)), dimension="height", line_color=GREEN_LINE,
                  line_dash="solid", line_width=3)
    p.add_layout(v_mean)
    return style_axes(p)

def render_insesgado():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Insesgadez:</b> un estimador θ̂ es insesgado para θ "
            "si su valor esperado coincide exactamente con el parámetro poblacional, "
            "sea cual sea el tamaño de la muestra.</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='formula-box'>E[θ̂] = θ &nbsp;&nbsp;⇒&nbsp;&nbsp; Sesgo = E[θ̂] − θ = 0</div>",
                   unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "El ejemplo clásico es la <b>varianza muestral</b>. Si dividimos la suma de "
            "desviaciones al cuadrado entre <b>n</b>, el estimador queda ligeramente "
            "sesgado hacia abajo. Dividiendo entre <b>n−1</b> (corrección de Bessel) se "
            "corrige el sesgo y el estimador se vuelve insesgado."
            "</div>", unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>Ŝ²ₙ = (1/n)·Σ(xᵢ−x̄)² &nbsp;&nbsp;vs&nbsp;&nbsp; "
            "Ŝ²ₙ₋₁ = (1/(n−1))·Σ(xᵢ−x̄)²</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura la población y simula:**", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                mu = st.number_input("Media poblacional (μ)", value=50.0, step=1.0)
            with c2:
                sigma = st.number_input("Desv. típica poblacional (σ)", value=10.0, min_value=0.1, step=0.5)
            n = st.slider("Tamaño muestral (n)", 2, 100, 5)

        if (mu, sigma, n) != st.session_state.get("_bias_params"):
            st.session_state["_bias_params"] = (mu, sigma, n)
            st.session_state["biased_estimates"] = []
            st.session_state["unbiased_estimates"] = []

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("+100 muestras", use_container_width=True, key="bias_100"):
                samples = np.random.normal(mu, sigma, size=(100, n))
                means = samples.mean(axis=1, keepdims=True)
                sq = ((samples - means) ** 2).sum(axis=1)
                st.session_state["biased_estimates"].extend((sq / n).tolist())
                st.session_state["unbiased_estimates"].extend((sq / (n - 1)).tolist())
                st.rerun()
        with b2:
            if st.button("+1000 muestras", use_container_width=True, key="bias_1000"):
                samples = np.random.normal(mu, sigma, size=(1000, n))
                means = samples.mean(axis=1, keepdims=True)
                sq = ((samples - means) ** 2).sum(axis=1)
                st.session_state["biased_estimates"].extend((sq / n).tolist())
                st.session_state["unbiased_estimates"].extend((sq / (n - 1)).tolist())
                st.rerun()
        with b3:
            if st.button("🔄 Reset", use_container_width=True, key="bias_reset"):
                st.session_state["biased_estimates"] = []
                st.session_state["unbiased_estimates"] = []
                st.rerun()

        true_var = sigma ** 2
        biased = st.session_state["biased_estimates"]
        unbiased = st.session_state["unbiased_estimates"]

        if len(biased) > 0:
            bias_n = float(np.mean(biased)) - true_var
            bias_n1 = float(np.mean(unbiased)) - true_var
            texto = (
                f"Con <b>{len(biased)}</b> muestras simuladas de tamaño n={n}: "
                f"el sesgo empírico del estimador que divide entre n es <b>{bias_n:.3f}</b> "
                f"(teóricamente −σ²/n = {-true_var/n:.3f}), mientras que el que divide "
                f"entre n−1 tiene un sesgo empírico de <b>{bias_n1:.3f}</b>, prácticamente nulo. "
                f"Cuanto mayor es n, menor es la diferencia entre ambos."
            )
        else:
            texto = "Pulsa uno de los botones para generar muestras y comparar ambos estimadores."

        st.markdown(f"<div class='content-box'><b>Interpretación:</b> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        st.markdown("#### Estimador sesgado: Ŝ²ₙ (÷n)", help="Línea negra = σ² real, línea verde = media de las estimaciones")
        chart1 = draw_variance_histogram(biased, true_var, UBU_RED, "")
        streamlit_bokeh(chart1, use_container_width=True, key="chart_biased")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("#### Estimador insesgado: Ŝ²ₙ₋₁ (÷n−1)", help="Línea negra = σ² real, línea verde = media de las estimaciones")
        chart2 = draw_variance_histogram(unbiased, true_var, BLUE_LINE, "")
        streamlit_bokeh(chart2, use_container_width=True, key="chart_unbiased")

        if len(biased) > 0:
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='stats-container'>
                <div class='stat-box'>
                    <div class='stat-label'>σ² real</div>
                    <div class='stat-value'>{true_var:.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Media Ŝ²ₙ</div>
                    <div class='stat-value'>{np.mean(biased):.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Media Ŝ²ₙ₋₁</div>
                    <div class='stat-value'>{np.mean(unbiased):.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Nº muestras</div>
                    <div class='stat-value'>{len(biased)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👆 Genera muestras en el panel izquierdo para visualizar ambas distribuciones.")

        if len(biased) > 0:
            mean_biased  = float(np.mean(biased))
            mean_unbiased = float(np.mean(unbiased))
            sesgo_emp    = mean_biased - true_var
            sesgo_teo    = -true_var / n
            sesgo_n1_emp = mean_unbiased - true_var

            # Dirección del sesgo para el texto
            dir_sesgo = "por debajo" if sesgo_emp < 0 else "por encima"

            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='content-box'>"
                f"<b>Interpretación:</b> Con {len(biased)} muestras de tamaño n={n}, "
                f"el estimador sesgado (÷n) da una media de <b>{mean_biased:.3f}</b>, "
                f"que queda {dir_sesgo} del valor real σ²={true_var:.2f} "
                f"(sesgo empírico: <b>{sesgo_emp:+.3f}</b>; teórico: {sesgo_teo:+.3f}). "
                f"La corrección de Bessel (÷n−1) sitúa la media en <b>{mean_unbiased:.3f}</b>, "
                f"con un sesgo empírico de <b>{sesgo_n1_emp:+.3f}</b>, prácticamente nulo. "
                f"En la gráfica esto se ve claramente: la línea verde del histograma rojo "
                f"<i>no</i> coincide con la línea negra (σ² real), mientras que en el azul sí. "
                f"Aumenta n para comprobar cómo el sesgo del estimador dividido entre n se reduce, "
                f"aunque nunca desaparece del todo."
                f"</div>",
                unsafe_allow_html=True
            )

# ---- B) Consistencia --------------------------------------------------------

def draw_convergence_path(path, mu, sigma, current_n):
    t = np.arange(1, len(path) + 1)
    cum_means = np.cumsum(path) / t

    p = figure(height=320, width=520, toolbar_location=None,
               x_axis_label="Tamaño muestral (n)", y_axis_label="x̄ acumulada",
               title="Trayectoria de una única muestra creciente")

    band = 1.96 * sigma / np.sqrt(t)
    p.varea(x=t, y1=mu - band, y2=mu + band, fill_color=UBU_YELLOW, fill_alpha=0.25)

    p.line(t, cum_means, line_color=BLUE_LINE, line_width=3)
    mu_line = Span(location=mu, dimension="width", line_color=GREEN_LINE, line_dash="dashed", line_width=2)
    p.add_layout(mu_line)

    idx = min(current_n, len(path)) - 1
    p.circle([t[idx]], [cum_means[idx]], size=12, color=UBU_RED, line_color="white", line_width=2)
    marker = Span(location=t[idx], dimension="height", line_color=UBU_RED, line_dash="dotted", line_width=2)
    p.add_layout(marker)

    return style_axes(p)

def draw_estimator_distribution(mu, sigma, n, m=3000):
    from scipy.stats import norm as normal_dist
    samples = np.random.normal(mu, sigma, size=(m, n))
    means = samples.mean(axis=1)

    hist, edges = np.histogram(means, bins=30, density=True)
    p = figure(height=320, width=520, toolbar_location=None,
               x_axis_label="x̄", y_axis_label="Densidad",
               title=f"Distribución muestral de x̄ para n={n}")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=BLUE_LINE, line_color="white", alpha=0.6, line_width=1)

    theo_std = sigma / math.sqrt(n)
    x = np.linspace(mu - 4 * theo_std, mu + 4 * theo_std, 200)
    y = normal_dist.pdf(x, mu, theo_std)
    p.line(x, y, line_color=UBU_RED, line_width=3, line_dash="dashed")

    return style_axes(p), float(np.std(means, ddof=1)), theo_std

def render_consistente():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Consistencia:</b> un estimador θ̂ₙ es consistente si, "
            "a medida que crece el tamaño muestral n, converge en probabilidad al parámetro real θ. "
            "Su varianza tiende a cero y la distribución del estimador se concentra cada vez más en θ.</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='formula-box'>lim<sub>n→∞</sub> P(|θ̂ₙ − θ| &gt; ε) = 0</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>La media muestral x̄ es consistente para μ: es insesgada y "
            "Var(x̄) = σ²/n → 0 cuando n → ∞.</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura la población:**", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                mu = st.number_input("Media poblacional (μ)", value=20.0, step=1.0, key="cons_mu")
            with c2:
                sigma = st.number_input("Desv. típica poblacional (σ)", value=5.0, min_value=0.1, step=0.5, key="cons_sigma")
            n = st.slider("Tamaño muestral (n)", 2, 1000, 30, key="cons_n")

        if st.button("🔄 Regenerar trayectoria", use_container_width=True):
            st.session_state["cons_path"] = None
            st.rerun()

        if "cons_path" not in st.session_state or st.session_state["cons_path"] is None \
           or st.session_state.get("_cons_pop") != (mu, sigma):
            st.session_state["cons_path"] = np.random.normal(mu, sigma, size=1000)
            st.session_state["_cons_pop"] = (mu, sigma)

        emp_std, theo_std = None, sigma / math.sqrt(n)
        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> Arriba se muestra cómo la media "
            f"acumulada de <b>una sola muestra creciente</b> se va acercando a μ={mu:.1f}, dentro de la "
            f"banda amarilla ±1.96·σ/√n. Abajo se generan {3000} muestras independientes de "
            f"tamaño n={n} para construir la distribución muestral de x̄ y compararla con la curva "
            f"teórica N(μ, σ/√n). Mueve el deslizador n y observa cómo la campana se estrecha.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        path_chart = draw_convergence_path(st.session_state["cons_path"], mu, sigma, n)
        streamlit_bokeh(path_chart, use_container_width=True, key="path_chart")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        dist_chart, emp_std, theo_std = draw_estimator_distribution(mu, sigma, n)
        streamlit_bokeh(dist_chart, use_container_width=True, key="dist_chart")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>Desv. empírica de x̄</div>
                <div class='stat-value'>{emp_std:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Desv. teórica σ/√n</div>
                <div class='stat-value'>{theo_std:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Tamaño muestral n</div>
                <div class='stat-value'>{n}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- C) Suficiencia ---------------------------------------------------------

def generate_sequences(n, k, num=4):
    base = np.array([1] * k + [0] * (n - k))
    return [np.random.permutation(base) for _ in range(num)]

def draw_likelihood_curve(n, k):
    p_vals = np.linspace(0.001, 0.999, 200)
    lik = np.power(p_vals, k) * np.power(1 - p_vals, n - k)
    p_mle = k / n
    lik_max = (p_mle ** k) * ((1 - p_mle) ** (n - k))

    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="p", y_axis_label="L(p)",
               title="L(p) (idéntica para las 4 secuencias mostradas)", x_range=(0, 1))
    p.line(p_vals, lik, line_width=3, color=BLUE_LINE)
    p.varea(x=p_vals, y1=0, y2=lik, color=BLUE_LINE, alpha=0.15)
    p.circle([p_mle], [lik_max], size=14, color=GREEN_LINE, line_color="white", line_width=3)
    vline = Span(location=p_mle, dimension="height", line_color=GREEN_LINE, line_dash="dashed", line_width=2)
    p.add_layout(vline)
    return style_axes(p)

def render_suficiente():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Suficiencia:</b> un estadístico T(X) es suficiente para θ "
            "si la distribución condicionada de la muestra dado T no depende de θ. Dicho de otro modo: "
            "T resume <b>toda</b> la información de la muestra relevante para estimar θ; conocido T, el "
            "orden concreto de los datos no aporta nada más.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Para n lanzamientos Bernoulli(p), el estadístico "
            "<b>T = Σxᵢ = k</b> (número de caras) es suficiente para p. La función de verosimilitud "
            "<b>L(p) = p<sup>k</sup>(1−p)<sup>n−k</sup></b> depende únicamente de k, sea cual sea el orden "
            "en que salieron las caras y cruces.</div>", unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Elige n y k, y genera secuencias:**", unsafe_allow_html=True)
            n = st.slider("Lanzamientos (n)", 4, 40, 10)
            k = st.slider("Caras observadas (k)", 0, n, min(5, n))

        if st.button("🎲 Generar 4 secuencias con ese k", use_container_width=True):
            st.session_state["suf_seqs"] = generate_sequences(n, k, 4)
            st.session_state["_suf_params"] = (n, k)
            st.rerun()

        if st.session_state["suf_seqs"] is None or st.session_state.get("_suf_params") != (n, k):
            st.session_state["suf_seqs"] = generate_sequences(n, k, 4)
            st.session_state["_suf_params"] = (n, k)

        seqs = st.session_state["suf_seqs"]
        st.markdown("<div class='section-title'>4 secuencias distintas, mismo T = k:</div>", unsafe_allow_html=True)
        for i, s in enumerate(seqs):
            txt = "".join("C" if v == 1 else "X" for v in s)
            st.markdown(f"<div class='seq-box'>Secuencia {i+1}: {txt}</div>", unsafe_allow_html=True)

        comb = math.comb(n, k)
        p_ref = 0.5
        lik_ref = (p_ref ** k) * ((1 - p_ref) ** (n - k))
        st.markdown(
            f"<div class='content-box'><b>Comprobación:</b> para cualquiera de las 4 secuencias, "
            f"L(p=0.5) = {lik_ref:.3e}, el mismo valor exacto. Además, la probabilidad de observar "
            f"una secuencia concreta <i>dado</i> que T=k es 1/C(n,k) = <b>{1/comb:.3e}</b>, un número que "
            f"<b>no depende de p</b>: esa es la definición formal de suficiencia.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_likelihood_curve(n, k)
        streamlit_bokeh(chart, use_container_width=True, key="suf_chart")

        p_mle = k / n
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>n</div>
                <div class='stat-value'>{n}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>k = T(X)</div>
                <div class='stat-value'>{k}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p̂ = k/n</div>
                <div class='stat-value'>{p_mle:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>C(n,k) órdenes</div>
                <div class='stat-value'>{comb}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Tipos de Estimadores</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("A) Insesgado", use_container_width=True):
        st.session_state["page"] = "A"
        st.rerun()
    if nav2.button("B) Consistente", use_container_width=True):
        st.session_state["page"] = "B"
        st.rerun()
    if nav3.button("C) Suficiente", use_container_width=True):
        st.session_state["page"] = "C"
        st.rerun()

    paginas = {
        "A": render_insesgado,
        "B": render_consistente,
        "C": render_suficiente,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
