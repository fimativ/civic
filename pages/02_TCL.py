import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA - Teorema del Límite Central")

# Colores UBU y diseño unificado
UBU_RED      = "#9b2743"
UBU_YELLOW   = "#F5C400"
UBU_DARK     = "#1a1a1a"
PANTONE_2727 = "#4169E1"

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
    font-size: 25px;
    color: var(--box-fg); line-height: 1.6;
    min-height: 250px; height: auto; margin-top: 30px; width: 100%;
}}
.comment-label {{ font-weight: 700; font-style: normal; color: {UBU_RED}; }}

/* ---- Sliders & Selectbox ---- */
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

.statement-box p, .comment-box p, .comment-box ul {{ color: var(--box-fg) !important; }}

.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px; width: 100%;
}}

.stats-container {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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
</style>
"""

# =============================================================================
# 2. FUNCIONES ESTADÍSTICAS Y SIMULACIÓN
# =============================================================================

def generate_population(pop_type, size=10000):
    np.random.seed(42)
    if pop_type == "Normal":
        return np.random.normal(loc=0, scale=1, size=size)
    elif pop_type == "Uniforme":
        return np.random.uniform(low=0, high=1, size=size)
    elif pop_type == "Exponencial":
        return np.random.exponential(scale=1, size=size)
    elif pop_type == "Poisson":
        return np.random.poisson(lam=3, size=size)
    else:  # bernoulli
        return np.random.binomial(n=1, p=0.5, size=size)

def draw_sample(population, n):
    return np.random.choice(population, size=n, replace=True)

# =============================================================================
# 3. INTERFAZ Y FLUJO DE LA APLICACIÓN
# =============================================================================

def main():
    st.markdown(build_css(), unsafe_allow_html=True)
    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Teorema del Límite Central</div>", unsafe_allow_html=True)

    # Inicializar estado interno de la simulación
    if "population_type" not in st.session_state:
        st.session_state.population_type = "normal"
    if "sample_size" not in st.session_state:
        st.session_state.sample_size = 50
    if "all_sample_means" not in st.session_state:
        st.session_state.all_sample_means = []
    if "current_sample" not in st.session_state:
        st.session_state.current_sample = None
    if "num_simulations" not in st.session_state:
        st.session_state.num_simulations = 0

    population = generate_population(st.session_state.population_type, size=10000)
    pop_mean = np.mean(population)
    pop_std = np.std(population, ddof=1)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El Teorema del Límite Central establece que, al extraer muestras lo suficientemente grandes, la distribución de las medias muestrales tenderá a seguir una distribución normal, sin importar la distribución original de la población.</div>", 
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Configura la simulación:**", unsafe_allow_html=True)
            
            pop_option = st.selectbox(
                "Tipo de distribución poblacional (X)",
                options=["normal", "uniforme", "exponencial", "poisson", "bernoulli"]
            )
            
            if pop_option != st.session_state.population_type:
                st.session_state.population_type = pop_option
                st.session_state.all_sample_means = []
                st.session_state.num_simulations = 0
                st.session_state.current_sample = None
                st.rerun()

            new_sample_size = st.slider("Tamaño muestral (n)", min_value=5, max_value=500, value=st.session_state.sample_size, step=5)
            if new_sample_size != st.session_state.sample_size:
                st.session_state.sample_size = new_sample_size
                st.rerun()

        # Botones de control para extraer muestras
        st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            if st.button("+1 muestra", use_container_width=True):
                sample = draw_sample(population, st.session_state.sample_size)
                st.session_state.current_sample = sample
                st.session_state.all_sample_means.append(np.mean(sample))
                st.session_state.num_simulations += 1
                st.rerun()
        with btn_col2:
            if st.button("+5 muestras", use_container_width=True):
                for _ in range(5):
                    sample = draw_sample(population, st.session_state.sample_size)
                    st.session_state.all_sample_means.append(np.mean(sample))
                st.session_state.current_sample = sample
                st.session_state.num_simulations += 5
                st.rerun()
        with btn_col3:
            if st.button("+1000 muestras", use_container_width=True):
                with st.spinner("Simulando..."):
                    for _ in range(1000):
                        sample = draw_sample(population, st.session_state.sample_size)
                        st.session_state.all_sample_means.append(np.mean(sample))
                st.session_state.current_sample = sample
                st.session_state.num_simulations += 1000
                st.rerun()
        with btn_col4:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.all_sample_means = []
                st.session_state.num_simulations = 0
                st.session_state.current_sample = None
                st.rerun()

        texto_explicativo = """
        <span class='comment-label'>Propiedades del TCL:</span><br>
        • <b>E[x̄] = μ</b> : La media de las medias muestrales converge a la media real de la población.<br>
        • <b>σ_x̄ = σ / √n</b> : La dispersión de las medias disminuye conforme aumenta el tamaño de la muestra.<br>
        • A mayor número de simulaciones, el histograma inferior se ajustará de manera más exacta a la campana de Gauss teórica.
        """
        st.markdown(f"<div class='comment-box'>{texto_explicativo}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        theme_is_dark = detect_dark_theme()
        plot_bg = "rgba(0,0,0,0)"
        grid_color = "#444444" if theme_is_dark else "#e0e0e0"
        text_color = "#ffffff" if theme_is_dark else "#141414"

        # 1. Gráfico de la población
        fig1 = go.Figure()
        fig1.add_trace(go.Histogram(x=population, nbinsx=40, marker_color=UBU_RED, opacity=0.75))
        fig1.add_vline(x=pop_mean, line_dash="dash", line_color=UBU_YELLOW, line_width=3)
        fig1.update_layout(
            title=f"1. Distribución Poblacional Original (X) — μ: {pop_mean:.2f}, σ: {pop_std:.2f}",
            height=250, margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor=plot_bg, paper_bgcolor=plot_bg, font=dict(color=text_color),
            xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color), showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        # 2. Gráfico de la muestra actual
        if st.session_state.current_sample is not None:
            current_mean = np.mean(st.session_state.current_sample)
            fig2 = go.Figure()
            fig2.add_trace(go.Histogram(x=st.session_state.current_sample, nbinsx=15, marker_color=PANTONE_2727, opacity=0.8))
            fig2.add_vline(x=current_mean, line_dash="dash", line_color=UBU_YELLOW, line_width=3)
            fig2.update_layout(
                title=f"2. Última Muestra Extraída (n = {st.session_state.sample_size}) — x̄: {current_mean:.2f}",
                height=250, margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor=plot_bg, paper_bgcolor=plot_bg, font=dict(color=text_color),
                xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color), showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("💡 Extrae una muestra en el panel izquierdo para visualizar su distribución interna.")

        # 3. Distribución de las medias y validación TCL
        if len(st.session_state.all_sample_means) > 0:
            means_array = np.array(st.session_state.all_sample_means)
            means_mean = np.mean(means_array)
            means_std = np.std(means_array, ddof=1)
            theoretical_std = pop_std / np.sqrt(st.session_state.sample_size)

            fig3 = go.Figure()
            fig3.add_trace(go.Histogram(x=means_array, nbinsx=30, histnorm='probability density', marker_color="#059669", opacity=0.6, name="Simuladas"))
            
            x_range = np.linspace(means_array.min() - 0.5, means_array.max() + 0.5, 200)
            y_theory = norm.pdf(x_range, pop_mean, theoretical_std)
            fig3.add_trace(go.Scatter(x=x_range, y=y_theory, mode='lines', line=dict(color=UBU_YELLOW, width=4), name="Teórica Gauss"))

            fig3.update_layout(
                title="3. Distribución de las Medias Muestrales (x̄) vs. TCL Teórico",
                height=280, margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor=plot_bg, paper_bgcolor=plot_bg, font=dict(color=text_color),
                xaxis=dict(gridcolor=grid_color), yaxis=dict(gridcolor=grid_color),
                legend=dict(x=0.75, y=0.95, bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

            # Métricas inferiores empíricas vs teóricas
            st.markdown(f"""
            <div class='stats-container'>
                <div class='stat-box'>
                    <div class='stat-label'>Muestras (m)</div>
                    <div class='stat-value'>{st.session_state.num_simulations}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Media de Medias (x̄̄)</div>
                    <div class='stat-value'>{means_mean:.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. Empírica (σ_x̄)</div>
                    <div class='stat-value'>{means_std:.2f}</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-label'>Desv. Teórica (σ/√n)</div>
                    <div class='stat-value'>{theoretical_std:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        "<div class='footer-bar'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; [AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()