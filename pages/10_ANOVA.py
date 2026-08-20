#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
import math
from scipy.stats import norm, f, f_oneway
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · ANOVA de un Factor")

UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"
PURPLE_LINE    = "#7c3aed"
ORANGE_LINE    = "#e67e22"

GROUP_COLORS = [BLUE_LINE, ORANGE_LINE, PURPLE_LINE]
GROUP_NAMES = ["A", "B", "C"]

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
    defaults = {"page": "I"}
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

def draw_strip_plot(samples_dict, colors):
    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="Grupo", y_axis_label="Valor observado",
               title="Muestras observadas por grupo")

    group_names = list(samples_dict.keys())
    for i, name in enumerate(group_names):
        vals = np.asarray(samples_dict[name])
        n = len(vals)
        x = i + np.random.uniform(-0.15, 0.15, n)
        color = colors[i % len(colors)]
        p.scatter(x, vals, size=8, color=color, alpha=0.55, line_color="white", line_width=0.5)
        mean_val = float(np.mean(vals))
        p.segment(x0=i - 0.22, y0=mean_val, x1=i + 0.22, y1=mean_val,
                  line_color=UBU_DARK, line_width=4)

    p.xaxis.ticker = list(range(len(group_names)))
    p.xaxis.major_label_overrides = {i: name for i, name in enumerate(group_names)}
    p.xgrid.grid_line_color = None
    p.x_range.start = -0.5
    p.x_range.end = len(group_names) - 0.5
    return style_axes(p)

def draw_f_distribution(F_obs, df1, df2, alpha):
    x_max = max(f.ppf(0.999, df1, df2), F_obs * 1.3)
    x = np.linspace(1e-6, x_max, 300)
    y = f.pdf(x, df1, df2)
    crit = f.ppf(1 - alpha, df1, df2)

    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="F", y_axis_label="Densidad",
               title=f"Distribución F({df1}, {df2}) y p-valor")

    mask_p = x >= F_obs
    p.varea(x=x[mask_p], y1=0, y2=y[mask_p], color=UBU_RED, alpha=0.35, legend_label="p-valor")
    p.line(x, y, line_width=3, color=BLUE_LINE, legend_label="F(df1, df2)")

    v_obs = Span(location=F_obs, dimension="height", line_color=UBU_DARK, line_width=3)
    p.add_layout(v_obs)
    v_crit = Span(location=crit, dimension="height", line_color=GREEN_LINE, line_dash="dashed", line_width=2)
    p.add_layout(v_crit)

    p.legend.location = "top_right"
    p.legend.label_text_font_size = "11px"
    p.legend.background_fill_alpha = 0.85
    return style_axes(p)

def run_anova(samples_dict):
    arrays = [np.asarray(v) for v in samples_dict.values()]
    F_obs, p_val = f_oneway(*arrays)
    k = len(arrays)
    N = sum(len(a) for a in arrays)
    df1, df2 = k - 1, N - k
    return float(F_obs), float(p_val), df1, df2

def decision_html(p_val, alpha):
    if p_val < alpha:
        return "Rechazar H0", "stat-bad"
    return "No rechazar H0", "stat-ok"

# ---- I) Influencia del tamaño muestral ------------------------------------

MU_A_FIXED, MU_B_FIXED, MU_C_FIXED = 50.0, 55.0, 60.0

def render_n_effect():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El ANOVA de un factor contrasta H0: μ<sub>A</sub>=μ<sub>B</sub>=μ<sub>C</sub> "
            "frente a H1: al menos una media difiere. Con la misma diferencia real entre las medias y la misma "
            "dispersión, <b>aumentar el tamaño muestral n</b> reduce el error de estimación de cada media y facilita "
            "detectar diferencias que ya existían en la población.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>F = MS<sub>entre</sub> / MS<sub>dentro</sub> &nbsp;~&nbsp; F(k−1, N−k)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta el tamaño muestral por grupo:**", unsafe_allow_html=True)
            n = st.slider("Tamaño muestral por grupo (n)", 5, 300, 20, key="a1_n")
            sigma = st.number_input("Desv. típica común (σ)", value=10.0, min_value=0.5, step=0.5, key="a1_sigma")
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="a1_alpha")
            if st.button("🔄 Nueva muestra", use_container_width=True, key="a1_new"):
                st.session_state["a1_force"] = st.session_state.get("a1_force", 0) + 1
                st.rerun()

        params = (n, sigma, st.session_state.get("a1_force", 0))
        if params != st.session_state.get("a1_params"):
            st.session_state["a1_params"] = params
            st.session_state["a1_samples"] = {
                "A": np.random.normal(MU_A_FIXED, sigma, n),
                "B": np.random.normal(MU_B_FIXED, sigma, n),
                "C": np.random.normal(MU_C_FIXED, sigma, n),
            }
        samples = st.session_state["a1_samples"]
        F_obs, p_val, df1, df2 = run_anova(samples)
        decision, cls = decision_html(p_val, alpha)

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con n={n} observaciones por grupo, "
            f"σ={sigma:.1f} y medias reales μA={MU_A_FIXED:.0f}, μB={MU_B_FIXED:.0f}, μC={MU_C_FIXED:.0f}, "
            f"se obtiene F={F_obs:.3f} y p-valor={p_val:.4f}, por lo que se debe <b>{decision}</b> "
            f"(α={alpha:.2f}). Manteniendo fijas las diferencias reales entre medias y la varianza, al "
            f"<b>aumentar n</b> el estadístico F tiende a crecer y el p-valor a bajar: más datos aportan "
            f"más potencia para detectar la misma diferencia real.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_strip_plot(samples, GROUP_COLORS)
        streamlit_bokeh(chart1, use_container_width=True, key="a1_strip")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_f_distribution(F_obs, df1, df2, alpha)
        streamlit_bokeh(chart2, use_container_width=True, key="a1_fdist")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>F observado</div>
                <div class='stat-value'>{F_obs:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p-valor</div>
                <div class='stat-value'>{p_val:.4f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Decisión</div>
                <div class='stat-value {cls}' style='font-size:20px;'>{decision}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>n por grupo</div>
                <div class='stat-value'>{n}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- II) Influencia de las varianzas muestrales ----------------------------

N_FIXED_II = 30

def render_variance_effect():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El denominador del estadístico F, MS<sub>dentro</sub>, mide la "
            "variabilidad <b>dentro</b> de cada grupo (el \"ruido\"). Cuanto mayor sea la dispersión σ dentro "
            "de cada grupo, más difícil resulta distinguir una diferencia real entre medias del simple azar "
            "muestral.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>F = MS<sub>entre</sub> / MS<sub>dentro</sub> &nbsp;~&nbsp; F(k−1, N−k)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta la desviación típica común:**", unsafe_allow_html=True)
            sigma = st.slider("Desv. típica común (σ)", 2.0, 40.0, 10.0, 0.5, key="a2_sigma")
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="a2_alpha")
            if st.button("🔄 Nueva muestra", use_container_width=True, key="a2_new"):
                st.session_state["a2_force"] = st.session_state.get("a2_force", 0) + 1
                st.rerun()

        params = (sigma, st.session_state.get("a2_force", 0))
        if params != st.session_state.get("a2_params"):
            st.session_state["a2_params"] = params
            st.session_state["a2_samples"] = {
                "A": np.random.normal(MU_A_FIXED, sigma, N_FIXED_II),
                "B": np.random.normal(MU_B_FIXED, sigma, N_FIXED_II),
                "C": np.random.normal(MU_C_FIXED, sigma, N_FIXED_II),
            }
        samples = st.session_state["a2_samples"]
        F_obs, p_val, df1, df2 = run_anova(samples)
        decision, cls = decision_html(p_val, alpha)

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con n={N_FIXED_II} por grupo, σ={sigma:.1f} "
            f"y medias reales μA={MU_A_FIXED:.0f}, μB={MU_B_FIXED:.0f}, μC={MU_C_FIXED:.0f}, se obtiene "
            f"F={F_obs:.3f} y p-valor={p_val:.4f}, por lo que se debe <b>{decision}</b> (α={alpha:.2f}). "
            f"Al <b>aumentar σ</b> crece la dispersión dentro de cada grupo (MS<sub>dentro</sub>), F baja y "
            f"el p-valor sube: la misma diferencia real de medias se vuelve más difícil de detectar cuando "
            f"el ruido interno de los grupos aumenta.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_strip_plot(samples, GROUP_COLORS)
        streamlit_bokeh(chart1, use_container_width=True, key="a2_strip")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_f_distribution(F_obs, df1, df2, alpha)
        streamlit_bokeh(chart2, use_container_width=True, key="a2_fdist")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>F observado</div>
                <div class='stat-value'>{F_obs:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p-valor</div>
                <div class='stat-value'>{p_val:.4f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Decisión</div>
                <div class='stat-value {cls}' style='font-size:20px;'>{decision}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>σ común</div>
                <div class='stat-value'>{sigma:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- III) Influencia de las diferencias de medias --------------------------

N_FIXED_III = 30
SIGMA_FIXED_III = 10.0

def render_mean_diff_effect():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El numerador del estadístico F, MS<sub>entre</sub>, mide la "
            "variabilidad <b>entre</b> las medias de los grupos. Cuanto mayor sea la separación real entre "
            "μ<sub>A</sub>, μ<sub>B</sub> y μ<sub>C</sub>, más evidente resulta que no proceden de una única "
            "población con media común.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>F = MS<sub>entre</sub> / MS<sub>dentro</sub> &nbsp;~&nbsp; F(k−1, N−k)</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta la separación entre medias:**", unsafe_allow_html=True)
            delta = st.slider("Separación entre medias (Δ)", 0.0, 25.0, 5.0, 0.5, key="a3_delta")
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="a3_alpha")
            if st.button("🔄 Nueva muestra", use_container_width=True, key="a3_new"):
                st.session_state["a3_force"] = st.session_state.get("a3_force", 0) + 1
                st.rerun()

        mu_a, mu_b, mu_c = 50.0, 50.0 + delta, 50.0 + 2 * delta

        params = (delta, st.session_state.get("a3_force", 0))
        if params != st.session_state.get("a3_params"):
            st.session_state["a3_params"] = params
            st.session_state["a3_samples"] = {
                "A": np.random.normal(mu_a, SIGMA_FIXED_III, N_FIXED_III),
                "B": np.random.normal(mu_b, SIGMA_FIXED_III, N_FIXED_III),
                "C": np.random.normal(mu_c, SIGMA_FIXED_III, N_FIXED_III),
            }
        samples = st.session_state["a3_samples"]
        F_obs, p_val, df1, df2 = run_anova(samples)
        decision, cls = decision_html(p_val, alpha)

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con Δ={delta:.1f}, las medias reales son "
            f"μA={mu_a:.1f}, μB={mu_b:.1f}, μC={mu_c:.1f} (n={N_FIXED_III}, σ={SIGMA_FIXED_III:.0f} fijos). "
            f"Se obtiene F={F_obs:.3f} y p-valor={p_val:.4f}, por lo que se debe <b>{decision}</b> "
            f"(α={alpha:.2f}). Al <b>aumentar Δ</b> crece la variabilidad entre grupos (MS<sub>entre</sub>), "
            f"F sube y el p-valor baja: cuanto mayor es la diferencia real entre las medias, más fácil es "
            f"rechazar H0.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_strip_plot(samples, GROUP_COLORS)
        streamlit_bokeh(chart1, use_container_width=True, key="a3_strip")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_f_distribution(F_obs, df1, df2, alpha)
        streamlit_bokeh(chart2, use_container_width=True, key="a3_fdist")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>F observado</div>
                <div class='stat-value'>{F_obs:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p-valor</div>
                <div class='stat-value'>{p_val:.4f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Decisión</div>
                <div class='stat-value {cls}' style='font-size:20px;'>{decision}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Δ</div>
                <div class='stat-value'>{delta:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · ANOVA de un Factor</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("I) Tamaños muestrales", use_container_width=True):
        st.session_state["page"] = "I"
        st.rerun()
    if nav2.button("II) Varianzas muestrales", use_container_width=True):
        st.session_state["page"] = "II"
        st.rerun()
    if nav3.button("III) Diferencias de medias", use_container_width=True):
        st.session_state["page"] = "III"
        st.rerun()

    paginas = {
        "I": render_n_effect,
        "II": render_variance_effect,
        "III": render_mean_diff_effect,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
