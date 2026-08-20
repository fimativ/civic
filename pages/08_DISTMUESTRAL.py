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

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Distribución Muestral de un Estadístico")

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
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "A",
        "prop_estimates": [],
        "diff_estimates": [],
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

def draw_sampling_histogram(values, theo_mean, theo_std, x_label, title):
    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label=x_label, y_axis_label="Densidad", title=title)
    if len(values) == 0:
        return style_axes(p)

    hist, edges = np.histogram(values, bins=30, density=True)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=BLUE_LINE, line_color="white", alpha=0.6, line_width=1)

    x = np.linspace(theo_mean - 4 * theo_std, theo_mean + 4 * theo_std, 200)
    y = norm.pdf(x, theo_mean, theo_std)
    p.line(x, y, line_color=UBU_RED, line_width=3, line_dash="dashed")

    v = Span(location=theo_mean, dimension="height", line_color=GREEN_LINE, line_dash="dotted", line_width=2)
    p.add_layout(v)
    return style_axes(p)

# ---- A) Proporción muestral en muestras grandes --------------------------

def render_proportion():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Si X₁,...,Xₙ son ensayos Bernoulli independientes, la "
            "proporción muestral p̂ = ΣXᵢ/n es, en muestras grandes, aproximadamente normal por el "
            "Teorema Central del Límite.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>p̂ ≈ N( p , √(p(1−p)/n) )</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura la población y simula:**", unsafe_allow_html=True)
            p_true = st.slider("Proporción real (p)", 0.01, 0.99, 0.30, 0.01)
            n = st.slider("Tamaño muestral (n)", 5, 1000, 50, 5)

        if (p_true, n) != st.session_state.get("_prop_params"):
            st.session_state["_prop_params"] = (p_true, n)
            st.session_state["prop_estimates"] = []

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("+100 muestras", use_container_width=True, key="prop_100"):
                st.session_state["prop_estimates"].extend(
                    (np.random.binomial(n, p_true, size=100) / n).tolist())
                st.rerun()
        with b2:
            if st.button("+1000 muestras", use_container_width=True, key="prop_1000"):
                st.session_state["prop_estimates"].extend(
                    (np.random.binomial(n, p_true, size=1000) / n).tolist())
                st.rerun()
        with b3:
            if st.button("🔄 Reset", use_container_width=True, key="prop_reset"):
                st.session_state["prop_estimates"] = []
                st.rerun()

        cond_ok = n >= 30
        cond_cls = "stat-ok" if cond_ok else "stat-bad"
        cond_txt = "se cumple ✔" if cond_ok else "NO se cumple ✘"

        estimates = st.session_state["prop_estimates"]
        theo_std = math.sqrt(p_true * (1 - p_true) / n)

        st.markdown(
            f"<div class='content-box'><b>Condición de aproximación normal:</b> el Teorema Central del "
            f"Límite exige n grande, con n=30 como regla habitual; aquí n={n} "
            f"<span class='{cond_cls}'>{cond_txt}</span>. Cuanto más alejado esté p de 0.5, más lento es "
            f"el acercamiento a la normalidad para un mismo n.</div>",
            unsafe_allow_html=True
        )

        if len(estimates) > 0:
            texto = (
                f"Con {len(estimates)} muestras simuladas de tamaño n={n}, la media empírica de p̂ es "
                f"{np.mean(estimates):.4f} (real p={p_true:.2f}) y su desviación empírica es "
                f"{np.std(estimates, ddof=1):.4f} frente a la teórica √(p(1−p)/n)={theo_std:.4f}."
            )
        else:
            texto = "Pulsa uno de los botones para generar muestras."
        st.markdown(f"<div class='content-box'><b>Interpretación:</b> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_sampling_histogram(estimates, p_true, theo_std, "p̂", f"Distribución muestral de p̂ (n={n})")
        streamlit_bokeh(chart, use_container_width=True, key="prop_chart")

        if len(estimates) > 0:
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='stats-container'>
                <div class='stat-box'>
                    <div class='stat-label'>p real</div>
                    <div class='stat-value'>{p_true:.3f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Media empírica p̂</div>
                    <div class='stat-value'>{np.mean(estimates):.3f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. empírica</div>
                    <div class='stat-value'>{np.std(estimates, ddof=1):.4f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. teórica</div>
                    <div class='stat-value'>{theo_std:.4f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👆 Genera muestras en el panel izquierdo para construir la distribución.")

# ---- B) Diferencia de medias en poblaciones normales ----------------------

def render_mean_diff():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Si X̄₁ y X̄₂ son las medias de dos muestras independientes "
            "procedentes de poblaciones normales N(μ₁,σ₁) y N(μ₂,σ₂), su diferencia X̄₁−X̄₂ es también "
            "exactamente normal, para cualquier tamaño muestral.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>X̄₁−X̄₂ ~ N( μ₁−μ₂ , √(σ₁²/n₁ + σ₂²/n₂) )</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura ambas poblaciones:**", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<b>Población 1</b>", unsafe_allow_html=True)
                mu1 = st.number_input("μ₁", value=50.0, step=1.0, key="mu1")
                sigma1 = st.number_input("σ₁", value=10.0, min_value=0.1, step=0.5, key="s1")
                n1 = st.slider("n₁", 5, 500, 30, key="n1")
            with c2:
                st.markdown("<b>Población 2</b>", unsafe_allow_html=True)
                mu2 = st.number_input("μ₂", value=45.0, step=1.0, key="mu2")
                sigma2 = st.number_input("σ₂", value=8.0, min_value=0.1, step=0.5, key="s2")
                n2 = st.slider("n₂", 5, 500, 30, key="n2")

        params = (mu1, sigma1, n1, mu2, sigma2, n2)
        if params != st.session_state.get("_diff_params"):
            st.session_state["_diff_params"] = params
            st.session_state["diff_estimates"] = []

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("+100 muestras", use_container_width=True, key="diff_100"):
                s1 = np.random.normal(mu1, sigma1, size=(100, n1)).mean(axis=1)
                s2 = np.random.normal(mu2, sigma2, size=(100, n2)).mean(axis=1)
                st.session_state["diff_estimates"].extend((s1 - s2).tolist())
                st.rerun()
        with b2:
            if st.button("+1000 muestras", use_container_width=True, key="diff_1000"):
                s1 = np.random.normal(mu1, sigma1, size=(1000, n1)).mean(axis=1)
                s2 = np.random.normal(mu2, sigma2, size=(1000, n2)).mean(axis=1)
                st.session_state["diff_estimates"].extend((s1 - s2).tolist())
                st.rerun()
        with b3:
            if st.button("🔄 Reset", use_container_width=True, key="diff_reset"):
                st.session_state["diff_estimates"] = []
                st.rerun()

        estimates = st.session_state["diff_estimates"]
        theo_mean = mu1 - mu2
        theo_std = math.sqrt(sigma1 ** 2 / n1 + sigma2 ** 2 / n2)

        if len(estimates) > 0:
            texto = (
                f"Con {len(estimates)} pares de muestras simulados, la media empírica de X̄₁−X̄₂ es "
                f"{np.mean(estimates):.3f} (teórica μ₁−μ₂={theo_mean:.3f}) y su desviación empírica es "
                f"{np.std(estimates, ddof=1):.3f} frente a la teórica {theo_std:.3f}."
            )
        else:
            texto = "Pulsa uno de los botones para generar pares de muestras."
        st.markdown(f"<div class='content-box'><b>Interpretación:</b> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_sampling_histogram(estimates, theo_mean, theo_std, "X̄₁ − X̄₂",
                                         "Distribución muestral de X̄₁ − X̄₂")
        streamlit_bokeh(chart, use_container_width=True, key="diff_chart")

        if len(estimates) > 0:
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='stats-container'>
                <div class='stat-box'>
                    <div class='stat-label'>μ₁−μ₂ real</div>
                    <div class='stat-value'>{theo_mean:.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Media empírica</div>
                    <div class='stat-value'>{np.mean(estimates):.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. empírica</div>
                    <div class='stat-value'>{np.std(estimates, ddof=1):.3f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. teórica</div>
                    <div class='stat-value'>{theo_std:.3f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👆 Genera muestras en el panel izquierdo para construir la distribución.")

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Distribución Muestral de un Estadístico</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2 = st.columns(2)
    if nav1.button("I) Proporción muestral (muestras grandes)", use_container_width=True):
        st.session_state["page"] = "A"
        st.rerun()
    if nav2.button("II) Diferencia de medias (poblaciones normales)", use_container_width=True):
        st.session_state["page"] = "B"
        st.rerun()

    paginas = {
        "A": render_proportion,
        "B": render_mean_diff,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
