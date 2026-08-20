#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
import math
from scipy.stats import norm, f
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Regresión Lineal Simple: Validación del Modelo")

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

def fit_ols(x, y):
    b1, b0 = np.polyfit(x, y, 1)
    y_hat = b0 + b1 * x
    resid = y - y_hat
    sse = np.sum(resid ** 2)
    sst = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - sse / sst
    return b0, b1, y_hat, resid, r2

def draw_scatter_fit(x, y, y_hat, title):
    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="x", y_axis_label="y", title=title)
    p.circle(x, y, size=8, color=BLUE_LINE, alpha=0.6, line_color="white", line_width=1)
    order = np.argsort(x)
    p.line(x[order], y_hat[order], line_width=3, color=UBU_RED)
    return style_axes(p)

def draw_residuals_vs_fitted(y_hat, resid, title):
    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="ŷ (valores ajustados)", y_axis_label="Residuos", title=title)
    p.circle(y_hat, resid, size=8, color=UBU_RED, alpha=0.6, line_color="white", line_width=1)
    hline = Span(location=0, dimension="width", line_color=UBU_DARK, line_dash="dashed", line_width=2)
    p.add_layout(hline)
    return style_axes(p)

def draw_residuals_hist(resid, title):
    p = figure(height=300, width=560, toolbar_location=None,
               x_axis_label="Residuos", y_axis_label="Frecuencia", title=title)
    bins = max(5, min(20, len(resid) // 3))
    hist, edges = np.histogram(resid, bins=bins)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=GREEN_LINE, line_color="white", alpha=0.6, line_width=1)
    return style_axes(p)

# ---- I) Diagnóstico con gráficas de errores --------------------------------

def render_diagnostico():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>En un modelo de regresión lineal simple, "
            "y = β₀ + β₁x + ε, los residuos deben comportarse como ruido aleatorio: sin patrón alguno "
            "al representarlos frente a los valores ajustados ŷ. Esta gráfica es la herramienta "
            "básica para validar el modelo.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>y = β₀ + β₁x + ε &nbsp;&nbsp; ε̂ᵢ = yᵢ − ŷᵢ</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Genera datos de un modelo lineal correcto:**", unsafe_allow_html=True)
            n = st.slider("Tamaño muestral (n)", 10, 300, 60, key="r1_n")
            beta1 = st.number_input("Pendiente real (β₁)", value=2.0, step=0.1, key="r1_b1")
            beta0 = st.number_input("Intercepto real (β₀)", value=5.0, step=0.5, key="r1_b0")
            sigma = st.slider("Ruido (σ)", 0.5, 15.0, 3.0, 0.5, key="r1_sigma")
            nueva = st.button("🔄 Nueva muestra", use_container_width=True, key="r1_new")

        params = (n, beta1, beta0, sigma)
        if nueva or "r1_data" not in st.session_state or st.session_state.get("r1_params") != params:
            x = np.random.uniform(0, 10, n)
            y = beta0 + beta1 * x + np.random.normal(0, sigma, n)
            st.session_state["r1_data"] = (x, y)
            st.session_state["r1_params"] = params

        x, y = st.session_state["r1_data"]
        b0_hat, b1_hat, y_hat, resid, r2 = fit_ols(x, y)
        sigma_hat = math.sqrt(np.sum(resid ** 2) / (n - 2))

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> el modelo ajustado es "
            f"ŷ = {b0_hat:.2f} + {b1_hat:.2f}·x, con R²={r2:.3f}. En un modelo como "
            f"este, la nube de residuos frente a ŷ debe verse <b>sin ningún patrón</b>: centrada en 0 "
            f"y con una anchura aproximadamente constante en todo el rango. Ésta es la referencia "
            f"visual «correcta» con la que se compararán los fallos de las secciones II y III.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_scatter_fit(x, y, y_hat, "Datos y recta ajustada")
        streamlit_bokeh(chart1, use_container_width=True, key="r1_scatter")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_residuals_vs_fitted(y_hat, resid, "Residuos vs. valores ajustados")
        streamlit_bokeh(chart2, use_container_width=True, key="r1_resid_fitted")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart3 = draw_residuals_hist(resid, "Histograma de residuos")
        streamlit_bokeh(chart3, use_container_width=True, key="r1_resid_hist")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>R²</div>
                <div class='stat-value'>{r2:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>β̂₀</div>
                <div class='stat-value'>{b0_hat:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>β̂₁</div>
                <div class='stat-value'>{b1_hat:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>σ̂ (residuos)</div>
                <div class='stat-value'>{sigma_hat:.3f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- II) Fallo de ajuste ----------------------------------------------------

def render_lack_of_fit():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El <b>fallo de ajuste</b> ocurre cuando la "
            "relación real entre x e y no es lineal, pero se le impone un modelo de regresión lineal "
            "simple. El resultado es un patrón sistemático (curvatura) en los residuos frente a ŷ, "
            "que un modelo correcto jamás debería mostrar.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>y = β₀ + β₁x + c·(x−5)² + ε &nbsp;·&nbsp; ajuste: ŷ = β̂₀ + β̂₁x</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown(
                "**Genera datos con curvatura real, centrada en x=5 para aislarla visualmente del término lineal:**",
                unsafe_allow_html=True
            )
            n = st.slider("Tamaño muestral (n)", 10, 300, 60, key="r2_n")
            beta1 = st.number_input("Pendiente real (β₁)", value=2.0, step=0.1, key="r2_b1")
            beta0 = st.number_input("Intercepto real (β₀)", value=5.0, step=0.5, key="r2_b0")
            sigma = st.slider("Ruido (σ)", 0.5, 15.0, 3.0, 0.5, key="r2_sigma")
            c = st.slider("Curvatura (c)", 0.0, 3.0, 0.0, 0.1, key="r2_c")
            nueva = st.button("🔄 Nueva muestra", use_container_width=True, key="r2_new")

        params = (n, beta1, beta0, sigma, c)
        if nueva or "r2_data" not in st.session_state or st.session_state.get("r2_params") != params:
            x = np.random.uniform(0, 10, n)
            y = beta0 + beta1 * x + c * (x - 5) ** 2 + np.random.normal(0, sigma, n)
            st.session_state["r2_data"] = (x, y)
            st.session_state["r2_params"] = params

        x, y = st.session_state["r2_data"]
        b0_hat, b1_hat, y_hat, resid, r2_lin = fit_ols(x, y)

        coef_quad = np.polyfit(x, y, 2)
        y_hat_quad = np.polyval(coef_quad, x)
        resid_quad = y - y_hat_quad
        sse_lin = np.sum(resid ** 2)
        sse_quad = np.sum(resid_quad ** 2)
        sst = np.sum((y - np.mean(y)) ** 2)
        r2_quad = 1 - sse_quad / sst
        F = (sse_lin - sse_quad) / (sse_quad / (n - 3))
        pval = 1 - f.cdf(F, 1, n - 3)

        sig_cls = "stat-bad" if pval < 0.05 else "stat-ok"
        sig_txt = "SÍ es significativo" if pval < 0.05 else "NO es significativo"

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con c={c:.1f}, el F de comparación de "
            f"modelos anidados (lineal vs. cuadrático) vale {F:.2f} (p={pval:.4f}), que "
            f"<span class='{sig_cls}'>{sig_txt}</span> al 5%. Con c=0 el modelo lineal es adecuado: "
            f"residuos sin patrón y F no significativo. Al aumentar c aparece una curvatura sistemática "
            f"en los residuos frente a ŷ y el F se vuelve significativo: evidencia de que el modelo "
            f"lineal simple no capta la relación real (fallo de ajuste).</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_scatter_fit(x, y, y_hat, "Datos y recta ajustada (relación real cuadrática)")
        streamlit_bokeh(chart1, use_container_width=True, key="r2_scatter")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_residuals_vs_fitted(y_hat, resid, "Residuos vs. valores ajustados")
        streamlit_bokeh(chart2, use_container_width=True, key="r2_resid_fitted")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>R² lineal</div>
                <div class='stat-value'>{r2_lin:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>R² cuadrático</div>
                <div class='stat-value'>{r2_quad:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>F comparación</div>
                <div class='stat-value'>{F:.2f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>p-valor</div>
                <div class='stat-value {sig_cls}'>{pval:.4f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- III) Falta de homocedasticidad ----------------------------------------

def render_heteroscedasticity():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>La <b>homocedasticidad</b> exige que la varianza del error sea "
            "constante para todos los valores de x. Cuando esa varianza crece con x (heterocedasticidad), "
            "el modelo sigue siendo correcto en media, pero los residuos muestran un característico "
            "«abanico» que invalida los intervalos y contrastes clásicos.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>y = β₀ + β₁x + ε &nbsp;&nbsp; ε ~ N(0, σ₀·(1+k·x))</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Genera datos con dispersión del error creciente en x:**", unsafe_allow_html=True)
            n = st.slider("Tamaño muestral (n)", 10, 300, 60, key="r3_n")
            beta1 = st.number_input("Pendiente real (β₁)", value=2.0, step=0.1, key="r3_b1")
            beta0 = st.number_input("Intercepto real (β₀)", value=5.0, step=0.5, key="r3_b0")
            sigma0 = st.slider("Ruido base (σ₀)", 0.5, 10.0, 2.0, 0.5, key="r3_sigma0")
            k = st.slider("Heterocedasticidad (k)", 0.0, 2.0, 0.0, 0.05, key="r3_k")
            nueva = st.button("🔄 Nueva muestra", use_container_width=True, key="r3_new")

        params = (n, beta1, beta0, sigma0, k)
        if nueva or "r3_data" not in st.session_state or st.session_state.get("r3_params") != params:
            x = np.random.uniform(0, 10, n)
            sigma_i = sigma0 * (1 + k * x)
            y = beta0 + beta1 * x + np.random.normal(0, sigma_i)
            st.session_state["r3_data"] = (x, y)
            st.session_state["r3_params"] = params

        x, y = st.session_state["r3_data"]
        b0_hat, b1_hat, y_hat, resid, r2 = fit_ols(x, y)
        corr = np.corrcoef(np.abs(resid), y_hat)[0, 1]

        hete_cls = "stat-bad" if corr > 0.3 else "stat-ok"
        hete_txt = "clara evidencia" if corr > 0.3 else "poca evidencia"

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> la correlación entre |residuos| e ŷ es "
            f"{corr:.3f}, lo que sugiere <span class='{hete_cls}'>{hete_txt}</span> de heterocedasticidad. "
            f"Con k=0 la dispersión de los residuos es aproximadamente constante en todo el rango "
            f"(homocedasticidad). Al aumentar k aparece un patrón de embudo en los residuos frente a ŷ y "
            f"la correlación entre |residuos| y ŷ crece, evidenciando que la varianza del error no es "
            f"constante, lo que invalida los intervalos de confianza y contrastes clásicos basados en "
            f"este modelo.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart1 = draw_scatter_fit(x, y, y_hat, "Datos y recta ajustada (dispersión creciente en x)")
        streamlit_bokeh(chart1, use_container_width=True, key="r3_scatter")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        chart2 = draw_residuals_vs_fitted(y_hat, resid, "Residuos vs. valores ajustados")
        streamlit_bokeh(chart2, use_container_width=True, key="r3_resid_fitted")

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>R²</div>
                <div class='stat-value'>{r2:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Corr(|resid|, ŷ)</div>
                <div class='stat-value {hete_cls}'>{corr:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>σ₀</div>
                <div class='stat-value'>{sigma0:.2f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>k</div>
                <div class='stat-value'>{k:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown(
        "<div class='top-bar-title'>C1VIC D4TA · Regresión Lineal Simple: Validación del Modelo</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("I) Diagnóstico con gráficas de errores", use_container_width=True):
        st.session_state["page"] = "I"
        st.rerun()
    if nav2.button("II) Fallo de ajuste", use_container_width=True):
        st.session_state["page"] = "II"
        st.rerun()
    if nav3.button("III) Falta de homocedasticidad", use_container_width=True):
        st.session_state["page"] = "III"
        st.rerun()

    paginas = {
        "I": render_diagnostico,
        "II": render_lack_of_fit,
        "III": render_heteroscedasticity,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
