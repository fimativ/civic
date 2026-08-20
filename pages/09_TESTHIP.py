#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
import math
from scipy.stats import norm
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Test de Hipótesis")

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
.metric-large {{
    font-size: 32px; font-weight: 700; color: var(--app-fg); text-align: center;
    border: 3px solid {GREEN_LINE}; border-radius: 12px;
    padding: 20px 15px; background: var(--box-bg); width: 100%;
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
.stat-ok {{ color: {GREEN_LINE} !important; }}
.stat-bad {{ color: #dc2626 !important; }}

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
label[data-testid="stWidgetLabel"] p {{ font-size: 20px !important; color: var(--app-fg) !important; font-weight: 600; }}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "I",
        "p1_last": None,
        "p1_sim_pvals": [],
        "p2_sim_rate": None,
        "p3_sim_power": None,
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

def draw_pvalue_diagram(z_obs, pval):
    x = np.linspace(-4.5, 4.5, 400)
    y = norm.pdf(x)
    title = "Curva N(0,1) bajo H0 (sin muestra extraída)" if z_obs is None else \
            f"Curva N(0,1) bajo H0 (p-valor = {pval:.4f})"

    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="Z", y_axis_label="Densidad", title=title)
    p.line(x, y, line_width=3, color=BLUE_LINE)

    if z_obs is not None:
        mask = x >= z_obs
        p.varea(x=x[mask], y1=0, y2=y[mask], color=UBU_RED, alpha=0.4, legend_label="p-valor")
        vline = Span(location=z_obs, dimension="height", line_color=UBU_DARK, line_dash="dashed", line_width=2)
        p.add_layout(vline)
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "11px"
        p.legend.background_fill_alpha = 0.85

    return style_axes(p)

def draw_pvalue_histogram(pvals):
    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="p-valor", y_axis_label="Densidad",
               title=f"Distribución de {len(pvals)} p-valores bajo H0" if pvals else "Distribución de p-valores bajo H0")
    if not pvals:
        return style_axes(p)

    hist, edges = np.histogram(pvals, bins=20, range=(0, 1), density=True)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=BLUE_LINE, line_color="white", alpha=0.6, line_width=1)

    ref = Span(location=1.0, dimension="width", line_color=UBU_RED, line_dash="dashed", line_width=2)
    p.add_layout(ref)
    return style_axes(p)

def draw_alpha_diagram(alpha, z_crit):
    x = np.linspace(-4.5, 4.5, 400)
    y = norm.pdf(x)

    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="Z", y_axis_label="Densidad",
               title=f"Región de rechazo (α = {alpha:.2f}, z_crit = {z_crit:.3f})")
    p.line(x, y, line_width=3, color=BLUE_LINE, legend_label="H0: N(0,1)")

    mask = x >= z_crit
    p.varea(x=x[mask], y1=0, y2=y[mask], color=UBU_RED, alpha=0.4, legend_label="Región de rechazo (α)")

    vline = Span(location=z_crit, dimension="height", line_color=UBU_DARK, line_dash="dashed", line_width=2)
    p.add_layout(vline)

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "11px"
    p.legend.background_fill_alpha = 0.85
    return style_axes(p)

def draw_power_diagram(alpha, d, n):
    z_crit = norm.ppf(1 - alpha)
    shift = d * math.sqrt(n)

    x_min = min(-4.5, shift - 4.5)
    x_max = max(4.5, shift + 4.5)
    x = np.linspace(x_min, x_max, 500)
    y0 = norm.pdf(x, 0, 1)
    y1 = norm.pdf(x, shift, 1)

    p = figure(height=360, width=560, toolbar_location=None,
               x_axis_label="Z", y_axis_label="Densidad",
               title=f"H0 vs H1 en escala Z  (z_crit = {z_crit:.3f})")

    mask_alpha = x >= z_crit
    p.varea(x=x[mask_alpha], y1=0, y2=y0[mask_alpha], color=UBU_RED, alpha=0.4, legend_label="α")
    mask_beta = x <= z_crit
    p.varea(x=x[mask_beta], y1=0, y2=y1[mask_beta], color="#888888", alpha=0.35, legend_label="β")
    mask_power = x >= z_crit
    p.varea(x=x[mask_power], y1=0, y2=y1[mask_power], color=GREEN_LINE, alpha=0.3, legend_label="Potencia (1−β)")

    p.line(x, y0, line_width=3, color=UBU_RED, legend_label="H0: N(0,1)")
    p.line(x, y1, line_width=3, color=BLUE_LINE, legend_label=f"H1: N({shift:.2f},1)")

    vline = Span(location=z_crit, dimension="height", line_color=UBU_DARK, line_dash="dashed", line_width=2)
    p.add_layout(vline)

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "11px"
    p.legend.background_fill_alpha = 0.85
    return style_axes(p)

# ---- I) Significado del valor p -------------------------------------------

def render_pvalue():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El <b>p-valor</b> es la probabilidad, calculada asumiendo que H0 "
            "es cierta, de observar un estadístico de contraste tan extremo o más que el que realmente se "
            "ha observado. No es la probabilidad de que H0 sea cierta.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>Z = (X̄ − μ₀) / (σ/√n) &nbsp;&nbsp;|&nbsp;&nbsp; p = P(Z ≥ Z<sub>obs</sub> | H0)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura la población bajo H0 y extrae una muestra:**", unsafe_allow_html=True)
            mu0 = st.number_input("μ₀ (H0: μ = μ₀)", value=100.0, step=1.0, key="p1_mu0")
            sigma = st.number_input("σ (desv. típica poblacional)", value=10.0, min_value=0.1, step=0.5, key="p1_sigma")
            n = st.slider("Tamaño muestral (n)", 5, 200, 30, key="p1_n")

        params = (mu0, sigma, n)
        if params != st.session_state.get("_p1_params"):
            st.session_state["_p1_params"] = params
            st.session_state["p1_last"] = None
            st.session_state["p1_sim_pvals"] = []

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Extraer una muestra", use_container_width=True, key="p1_sample_btn"):
                x = np.random.normal(mu0, sigma, n)
                xbar = x.mean()
                se = sigma / math.sqrt(n)
                z_obs = (xbar - mu0) / se
                pval = 1 - norm.cdf(z_obs)
                st.session_state["p1_last"] = {"xbar": xbar, "z_obs": z_obs, "pval": pval}
                st.rerun()
        with b2:
            if st.button("Simular 2000 experimentos bajo H0", use_container_width=True, key="p1_sim_btn"):
                se = sigma / math.sqrt(n)
                samples = np.random.normal(mu0, sigma, size=(2000, n))
                xbars = samples.mean(axis=1)
                z_all = (xbars - mu0) / se
                pvals = 1 - norm.cdf(z_all)
                st.session_state["p1_sim_pvals"] = pvals.tolist()
                st.rerun()

        last = st.session_state["p1_last"]
        sim = st.session_state["p1_sim_pvals"]

        if last is not None:
            texto = (
                f"Se ha observado X̄ = {last['xbar']:.3f}, lo que da Z<sub>obs</sub> = {last['z_obs']:.3f} y "
                f"p-valor = {last['pval']:.4f}. Interpretación correcta: <i>si H0 fuese cierta, la probabilidad "
                f"de observar un valor de Z tan grande o mayor es de {last['pval']*100:.2f}%</i>. "
                f"Esto NO significa que la probabilidad de que H0 sea cierta sea {last['pval']*100:.2f}%. "
                f"El p-valor se calcula suponiendo H0 verdadera, nunca al revés."
            )
        else:
            texto = "Pulsa \"Extraer una muestra\" para calcular un p-valor concreto bajo H0."
        st.markdown(f"<div class='content-box'><b>Interpretación:</b> {texto}</div>", unsafe_allow_html=True)

        if sim:
            prop05 = np.mean(np.array(sim) <= 0.05)
            texto2 = (
                f"Bajo H0, el p-valor se distribuye <b>Uniforme(0,1)</b>: por eso el histograma de los "
                f"{len(sim)} p-valores simulados es aproximadamente plano, y por eso P(p-valor ≤ α) = α "
                f"exactamente. En esta simulación, la proporción de p-valores ≤ 0.05 fue {prop05*100:.2f}%, "
                f"muy cercana al 5% teórico."
            )
        else:
            texto2 = "Pulsa \"Simular 2000 experimentos bajo H0\" para comprobar que el p-valor es Uniforme(0,1) bajo H0."
        st.markdown(f"<div class='content-box'><b>Clave:</b> {texto2}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        z_obs = last["z_obs"] if last is not None else None
        pval = last["pval"] if last is not None else None
        chart1 = draw_pvalue_diagram(z_obs, pval)
        streamlit_bokeh(chart1, use_container_width=True, key="p1_chart_curve")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_pvalue_histogram(sim)
        streamlit_bokeh(chart2, use_container_width=True, key="p1_chart_hist")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        prop_txt = f"{np.mean(np.array(sim) <= 0.05)*100:.2f}%" if sim else "—"
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>Z observado</div>
                <div class='stat-value'>{f"{z_obs:.3f}" if z_obs is not None else "—"}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p-valor</div>
                <div class='stat-value'>{f"{pval:.4f}" if pval is not None else "—"}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>% p-valores ≤ 0.05 (sim.)</div>
                <div class='stat-value'>{prop_txt}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- II) Nivel de significación (α) ---------------------------------------

def render_alpha():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El nivel de significación <b>α</b> es la probabilidad de rechazar "
            "H0 cuando en realidad es cierta (error de tipo I). Se fija de antemano y determina el valor "
            "crítico z<sub>α</sub> que separa la región de rechazo.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>Región de rechazo: Z ≥ z<sub>α</sub> &nbsp;&nbsp; con &nbsp; "
            "z<sub>α</sub> = Φ<sup>−1</sup>(1−α)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta el nivel de significación y la población bajo H0:**", unsafe_allow_html=True)
            alpha = st.slider("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="a2_alpha")
            mu0 = st.number_input("μ₀ (H0: μ = μ₀)", value=100.0, step=1.0, key="a2_mu0")
            sigma = st.number_input("σ (desv. típica poblacional)", value=10.0, min_value=0.1, step=0.5, key="a2_sigma")
            n = st.slider("Tamaño muestral (n)", 5, 200, 30, key="a2_n")

        z_crit = norm.ppf(1 - alpha)

        params = (alpha, mu0, sigma, n)
        if params != st.session_state.get("_a2_params"):
            st.session_state["_a2_params"] = params
            st.session_state["p2_sim_rate"] = None

        if st.button("Simular 3000 muestras bajo H0", use_container_width=True, key="a2_sim_btn"):
            se = sigma / math.sqrt(n)
            samples = np.random.normal(mu0, sigma, size=(3000, n))
            xbars = samples.mean(axis=1)
            z_all = (xbars - mu0) / se
            rate = np.mean(z_all > z_crit)
            st.session_state["p2_sim_rate"] = rate
            st.rerun()

        rate = st.session_state["p2_sim_rate"]

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con α = {alpha:.2f}, el valor crítico es "
            f"z<sub>α</sub> = {z_crit:.3f}: solo se rechaza H0 si Z ≥ {z_crit:.3f}. Al bajar α, z<sub>α</sub> "
            f"sube y la región de rechazo se estrecha, reduciendo la probabilidad de un falso positivo "
            f"(error de tipo I), pero a cambio se necesita evidencia más fuerte para rechazar H0.</div>",
            unsafe_allow_html=True
        )

        if rate is not None:
            diff_pp = abs(rate - alpha) * 100
            texto = (
                f"En la simulación, de 3000 muestras generadas bajo H0, se rechazó H0 en el "
                f"{rate*100:.2f}% de los casos, muy cercano al α teórico ({alpha*100:.2f}%). Esta tasa "
                f"de rechazo bajo H0 estima empíricamente el error de tipo I."
            )
        else:
            texto = "Pulsa \"Simular 3000 muestras bajo H0\" para estimar empíricamente la tasa de error de tipo I."
        st.markdown(f"<div class='content-box'><b>Simulación:</b> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_alpha_diagram(alpha, z_crit)
        streamlit_bokeh(chart, use_container_width=True, key="a2_chart")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        if rate is not None:
            diff_pp = abs(rate - alpha) * 100
            cls = "stat-ok" if diff_pp <= 1.5 else "stat-bad"
        else:
            cls = ""
        rate_txt = f"{rate*100:.2f}%" if rate is not None else "—"
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>α teórico</div>
                <div class='stat-value'>{alpha*100:.2f}%</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Tasa de rechazo empírica</div>
                <div class='stat-value {cls}'>{rate_txt}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>z<sub>α</sub></div>
                <div class='stat-value'>{z_crit:.3f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- III) Potencia del test (1−β) ------------------------------------------

def render_power():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>La <b>potencia</b> (1−β) es la probabilidad de rechazar H0 cuando "
            "H1 es realmente cierta. Depende de α, del tamaño del efecto d = δ/σ y del tamaño muestral n: "
            "más n o más efecto detectable ⇒ más potencia; un α más exigente ⇒ menos potencia.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>Bajo H1: Z ~ N(d·√n , 1) &nbsp;&nbsp; Potencia = 1 − Φ(z<sub>α</sub> − d√n)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta α, el efecto y el tamaño muestral:**", unsafe_allow_html=True)
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="p3_alpha")
            d = st.slider("Tamaño del efecto d = δ/σ", 0.05, 2.0, 0.5, 0.05, key="p3_d")
            n = st.slider("Tamaño muestral (n)", 5, 200, 30, key="p3_n")

        mu0_fix, sigma_fix = 100.0, 10.0
        z_crit = norm.ppf(1 - alpha)
        shift = d * math.sqrt(n)
        power_theo = 1 - norm.cdf(z_crit - shift)
        beta_theo = 1 - power_theo

        params = (alpha, d, n)
        if params != st.session_state.get("_p3_params"):
            st.session_state["_p3_params"] = params
            st.session_state["p3_sim_power"] = None

        if st.button("Simular bajo H1", use_container_width=True, key="p3_sim_btn"):
            delta = d * sigma_fix
            se = sigma_fix / math.sqrt(n)
            samples = np.random.normal(mu0_fix + delta, sigma_fix, size=(3000, n))
            xbars = samples.mean(axis=1)
            z_all = (xbars - mu0_fix) / se
            power_emp = np.mean(z_all > z_crit)
            st.session_state["p3_sim_power"] = power_emp
            st.rerun()

        power_emp = st.session_state["p3_sim_power"]

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con α = {alpha:.2f}, efecto d = {d:.2f} y "
            f"n = {n}, la potencia teórica es {power_theo*100:.1f}% (β = {beta_theo*100:.1f}%). Aumentar n "
            f"o el efecto d desplaza la curva de H1 hacia la derecha, agrandando la región verde de "
            f"potencia; exigir un α más pequeño desplaza z<sub>α</sub> hacia la derecha y reduce la "
            f"potencia.</div>",
            unsafe_allow_html=True
        )

        if power_emp is not None:
            texto = (
                f"En la simulación bajo H1 (3000 muestras con μ = μ₀ + δ), se rechazó H0 correctamente en "
                f"el {power_emp*100:.1f}% de los casos (potencia empírica), muy próxima a la teórica "
                f"({power_theo*100:.1f}%)."
            )
        else:
            texto = "Pulsa \"Simular bajo H1\" para comparar la potencia teórica con la potencia empírica."
        st.markdown(f"<div class='content-box'><b>Simulación:</b> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_power_diagram(alpha, d, n)
        streamlit_bokeh(chart, use_container_width=True, key="p3_chart")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        power_emp_txt = f"{power_emp*100:.1f}%" if power_emp is not None else "—"
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>Potencia teórica</div>
                <div class='stat-value'>{power_theo*100:.1f}%</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Potencia empírica</div>
                <div class='stat-value'>{power_emp_txt}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>β teórico</div>
                <div class='stat-value'>{beta_theo*100:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Test de Hipótesis</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("I) Significado del valor p", use_container_width=True):
        st.session_state["page"] = "I"
        st.rerun()
    if nav2.button("II) Nivel de significación (α)", use_container_width=True):
        st.session_state["page"] = "II"
        st.rerun()
    if nav3.button("III) Potencia del test (1−β)", use_container_width=True):
        st.session_state["page"] = "III"
        st.rerun()

    paginas = {
        "I": render_pvalue,
        "II": render_alpha,
        "III": render_power,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
