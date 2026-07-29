import streamlit as st
import numpy as np
from scipy.stats import t as t_dist, norm
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.layouts import column
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA - Intervalos de Confianza")

# Colores UBU y diseño
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
COLOR_CONTAINS = "#059669"  
COLOR_MISSING  = "#dc2626"  

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
    height: 100%; width: 100%; line-height: 1.2; margin-bottom: 30px;
}}

/* -- PANELS -- */
div[data-testid="column"]:has(.bg-left) {{
    background: var(--panel-left-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
}}
div[data-testid="column"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
    display: flex; flex-direction: column; align-items: center;
}}

/* -- TEXT ELEMENTS -- */
.statement-box {{
    border: 4px solid {UBU_RED}; border-radius: 12px;
    padding: 30px 40px; background: var(--box-bg); 
    text-align: justify;
    color: var(--box-fg); font-size: 25px; line-height: 1.5; margin-bottom: 30px;
}}

/* CAJA PARA CONTROLES */
div.st-key-controls_box {{
    border: 4px solid {UBU_RED} !important; border-radius: 12px !important;
    padding: 30px 40px !important; background: var(--box-bg) !important;
    margin-bottom: 30px; margin-top: 30px;
}}

div.st-key-controls_box p {{
    color: var(--box-fg) !important;
    font-size: 25px !important;
    font-weight: 700 !important;
    margin-bottom: 35px !important;
    line-height: 1.3 !important;
}}

.comment-box {{
    border: 4px solid {UBU_RED}; border-radius: 12px;
    padding: 30px 40px; background: var(--box-bg);
    font-style: italic; font-size: 25px;
    color: var(--box-fg); line-height: 1.6;
    min-height: 250px; height: auto; margin-top: 30px; width: 100%;
}}
.comment-label {{ font-weight: 700; font-style: normal; color: {UBU_RED}; }}

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

label[data-testid="stWidgetLabel"] p {{
    font-size: 22px !important; color: var(--app-fg) !important; font-weight: 600;
}}

button p {{ font-size: 25px !important; }}
div[data-testid="column"] button {{ padding-top: 15px !important; padding-bottom: 15px !important; }}

/* Info boxes */
.stInfo {{ color: var(--app-fg) !important; }}

.statement-box p, .comment-box p {{ color: var(--box-fg) !important; }}

.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px; width: 100%;
}}

.stats-container {{
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 20px; margin-bottom: 30px; width: 100%;
}}

.stat-box {{
    background: var(--box-bg); border: 3px solid {UBU_YELLOW};
    border-radius: 12px; padding: 20px; text-align: center;
}}

.stat-label {{
    font-size: 22px; font-weight: 600; color: var(--box-fg); margin-bottom: 10px;
}}

.stat-value {{
    font-size: 34px; font-weight: 700; color: {UBU_RED};
}}

.stat-value-success {{ color: {COLOR_CONTAINS}; }}
.stat-value-danger {{ color: {COLOR_MISSING}; }}
</style>
"""

# =============================================================================
# 2. FUNCIONES ESTADÍSTICAS
# =============================================================================

def simulate_intervals(ci_level, sample_size, num_samples, mu=50, sigma=10):
    """Simular intervalos de confianza"""
    alpha = 1 - ci_level / 100
    df = sample_size - 1
    t_crit = t_dist.ppf(1 - alpha / 2, df)

    samples = np.random.normal(mu, sigma, size=(num_samples, sample_size))
    means = samples.mean(axis=1)
    stds = samples.std(axis=1, ddof=1)
    se = stds / np.sqrt(sample_size)

    margin_error = t_crit * se
    lowers = means - margin_error
    uppers = means + margin_error
    contains_mu = (lowers <= mu) & (mu <= uppers)

    return [
        {'lower': lo, 'upper': up, 'mean': m, 'contains_mu': c}
        for lo, up, m, c in zip(lowers, uppers, means, contains_mu)
    ]

# =============================================================================
# 3. FUNCIONES DE VISUALIZACIÓN (BOKEH)
# =============================================================================

def draw_intervals(intervals, sample_size, ci_level, mu=50, x_range=None):
    """Dibujar intervalos de confianza con Bokeh"""
    num_intervals = len(intervals)
    lowers = [i['lower'] for i in intervals]
    uppers = [i['upper'] for i in intervals]

    min_val = min(lowers) - 5
    max_val = max(uppers) + 5

    p = figure(
        height=max(400, min(1000, num_intervals * 3)),
        width=900,
        toolbar_location=None,
        x_range=x_range if x_range is not None else (min_val, max_val),
        title=f"Intervalos de confianza al {ci_level}% (n={sample_size}, m={num_intervals})",
        title_location="below",
        y_range=(0, num_intervals)
    )

    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    p.outline_line_color = "#dddddd"
    p.xgrid.grid_line_color = "#dddddd"
    p.ygrid.grid_line_color = None
    p.title.text_font_size = "16px"
    p.title.align = "center"
    p.xaxis.major_label_text_font_size = "25px"
    p.yaxis.major_label_text_font_size = "20px"

    p.line([mu, mu], [0, num_intervals], line_color="#1a1a1a", line_width=3, 
           line_dash="dashed", alpha=0.3)
    
    for i, interval in enumerate(intervals):
        color = COLOR_CONTAINS if interval['contains_mu'] else COLOR_MISSING
        p.line(
            [interval['lower'], interval['upper']], 
            [i + 0.5, i + 0.5],
            line_color=color,
            line_width=2,
            alpha=0.8
        )
        p.scatter(
            [interval['mean']],
            [i + 0.5],
            marker="circle",
            size=6,
            color=color,
            alpha=0.9
        )
    return p

def draw_normal_curves(intervals, sample_size, mu=50, sigma=10, x_range=None):
    """Curva teórica N(μ, σ/√n) vs. curva normal simulada"""
    means = np.array([i['mean'] for i in intervals])
    se_theoretical = sigma / np.sqrt(sample_size)
    emp_mean = means.mean()
    emp_std = means.std(ddof=1)

    if x_range is not None:
        x_min, x_max = x_range.start, x_range.end
    else:
        x_min = min(mu - 4 * se_theoretical, emp_mean - 4 * emp_std)
        x_max = max(mu + 4 * se_theoretical, emp_mean + 4 * emp_std)
    x = np.linspace(x_min, x_max, 300)

    y_theoretical = norm.pdf(x, mu, se_theoretical)
    y_empirical = norm.pdf(x, emp_mean, emp_std)

    p = figure(
        height=300,
        width=900,
        toolbar_location=None,
        x_range=x_range if x_range is not None else (x_min, x_max),
        title="Distribución teórica vs. simulada",
    )

    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    p.outline_line_color = "#dddddd"
    p.xgrid.grid_line_color = "#dddddd"
    p.ygrid.grid_line_color = None
    p.title.text_font_size = "16px"
    p.title.align = "center"
    p.yaxis.major_label_text_font_size = "20px"
    p.yaxis.axis_label = "Densidad"
    p.xaxis.visible = False

    p.line(x, y_theoretical, line_color=PANTONE_2727, line_width=4,
           legend_label=f"Teórica N(μ={mu}, σ={sigma})")
    p.line(x, y_empirical, line_color=UBU_RED, line_width=4, line_dash="dashed",
           legend_label=f"Simulada N(μ={mu}, σ/√n={se_theoretical:.2f})")

    p.legend.location = "top_right"
    p.legend.label_text_font_size = "14px"
    p.legend.background_fill_alpha = 0.8
    return p

def draw_combined_chart(intervals, sample_size, ci_level, mu=50, sigma=10):
    lowers = [i['lower'] for i in intervals]
    uppers = [i['upper'] for i in intervals]
    shared_range = Range1d(min(lowers) - 5, max(uppers) + 5)

    p_normal = draw_normal_curves(intervals, sample_size, mu, sigma, x_range=shared_range)
    p_intervals = draw_intervals(intervals, sample_size, ci_level, mu, x_range=shared_range)
    return column(p_normal, p_intervals, sizing_mode="stretch_width")

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA: Intervalos de Confianza</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Se trata de elegir un conjunto más o menos amplio del que tenemos bastante confianza en que contenga al verdadero valor del parámetro buscado (en este caso, la media μ).</div>", 
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta los parámetros y simula:**", unsafe_allow_html=True)
            ci_level = st.slider("Nivel de confianza (%)", 80, 99, 95)
            sample_size = st.slider("Tamaño muestral", 5, 100, 30)
            num_samples = st.slider("Número de muestras", 10, 1000, 100, step=50)
        
        if ci_level >= 95:
            texto = f"""<br>
            • Se tiene un nivel de confianza del {ci_level}% <br>
            • Extraemos muestras de la población (hasta 100) <br>
            • Para cada muestra: <br>
            &nbsp;&nbsp;→ Calculamos la media muestral x̄ <br>
            &nbsp;&nbsp;→ Estimamos μ con un IC <br>
            • El <b>{ci_level}%</b> de los IC incluyen el verdadero valor de μ <br>
            • El porcentaje restante de los IC no lo incluyen, representados en rojo.
            """
        else:
            texto = f"Con un nivel de confianza del <b>{ci_level}%</b>, estamos siendo más tolerantes. Solo aproximadamente <b>{ci_level}% de los intervalos</b> capturarán μ, pero obtenemos intervalos más estrechos y estimaciones más precisas del parámetro poblacional."
        
        st.markdown(f"<div class='comment-box'><span class='comment-label'>Interpretación:</span> {texto}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        if st.button("🔄 Simular ahora", key="simulate_btn", use_container_width=True):
            with st.spinner("Generando muestras..."):
                intervals = simulate_intervals(ci_level, sample_size, num_samples)
            st.session_state["results"] = (intervals, sample_size, ci_level, num_samples)

        results = st.session_state.get("results")
        if results:
            intervals, res_sample_size, res_ci_level, res_num_samples = results

            contained = sum(1 for i in intervals if i['contains_mu'])
            percentage = round((contained / res_num_samples) * 100)

            st.markdown(f"""
            <div class='stats-container'>
                <div class='stat-box'>
                    <div class='stat-label'>Contienen μ</div>
                    <div class='stat-value stat-value-success'>{contained}/{res_num_samples}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Porcentaje</div>
                    <div class='stat-value stat-value-success'>{percentage}%</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>No contienen μ</div>
                    <div class='stat-value stat-value-danger'>{res_num_samples - contained}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            combined_chart = draw_combined_chart(intervals, res_sample_size, res_ci_level)
            streamlit_bokeh(combined_chart, use_container_width=True, key="combined_chart")
        else:
            st.info("👆 Presiona el botón para ejecutar la simulación")

    st.markdown(
        "<div class='footer-bar'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; [AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()