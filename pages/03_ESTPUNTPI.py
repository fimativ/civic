import streamlit as st
import numpy as np
from bokeh.plotting import figure
from streamlit_bokeh import streamlit_bokeh
import math

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA - Estimación de π")

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

.content-box {{
    border: 3px solid {UBU_RED}; border-radius: 12px;
    padding: 25px 35px; background: var(--box-bg);
    font-size: 25px; color: var(--box-fg); line-height: 1.6; margin-bottom: 25px;
}}

.section-title {{
    font-size: 26px; font-weight: 700; color: {UBU_RED};
    margin: 30px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px; width: 100%;
}}

.formula-box {{
    border: 3px solid {UBU_RED}; border-radius: 12px;
    padding: 20px 25px; background: var(--box-bg);
    text-align: center; font-size: 25px; color: var(--box-fg); margin: 20px 0;
}}

.comment-box {{
    border: 4px solid {UBU_RED}; border-radius: 12px;
    padding: 30px 40px; background: var(--box-bg);
    font-size: 25px; color: var(--box-fg); line-height: 1.6;
    margin-top: 30px; width: 100%;
}}
.comment-label {{ font-weight: 700; font-style: normal; color: {UBU_RED}; }}

button p {{ font-size: 25px !important; }}
div[data-testid="column"] button {{ padding-top: 15px !important; padding-bottom: 15px !important; }}

.statement-box p, .content-box p, .comment-box p {{ color: var(--box-fg) !important; }}

.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px; width: 100%;
}}

.stats-container {{
    display: grid; grid-template-columns: repeat(3, 1fr);
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
# 2. FUNCIONES DE SIMULACIÓN Y LÓGICA DE ESTADO
# =============================================================================

def init_session_state():
    defaults = {
        "samples_in_circle": 0,
        "total_samples": 0,
        "samples_history": [],
        "pi_estimates": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def drop_samples(n_samples):
    """Genera n_samples aleatorios en [-1,1]x[-1,1] y calcula distancias"""
    x = np.random.uniform(-1, 1, n_samples)
    y = np.random.uniform(-1, 1, n_samples)
    distances = np.sqrt(x**2 + y**2)
    in_circle = distances <= 1.0
    return x, y, in_circle

def update_estimates(n_new_samples):
    x, y, in_circle = drop_samples(n_new_samples)
    st.session_state["samples_in_circle"] += np.sum(in_circle)
    st.session_state["total_samples"] += n_new_samples
    st.session_state["samples_history"].append((x, y, in_circle))
    
    if st.session_state["total_samples"] > 0:
        pi_estimate = 4 * st.session_state["samples_in_circle"] / st.session_state["total_samples"]
        st.session_state["pi_estimates"].append(pi_estimate)

# =============================================================================
# 3. GRÁFICOS (BOKEH)
# =============================================================================

def plot_circle_and_samples():
    """Visualización del plano con Bokeh"""
    p = figure(width=550, height=550, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
               toolbar_location=None, tools="", title="Simulación del Espacio Muestral", match_aspect=True)
    
    # Cuadrado delimitador [-1,1]
    p.quad(left=[-1], right=[1], top=[1], bottom=[-1], fill_color="#fcfcfc", 
           line_color=UBU_RED, line_width=3)
    
    # Círculo unitario inscrito
    angles = np.linspace(0, 2*np.pi, 150)
    p.line(np.cos(angles), np.sin(angles), line_color=PANTONE_2727, line_width=3)
    
    # Agregar todos los puntos acumulados de manera optimizada
    all_x, all_y, all_in = [], [], []
    for x, y, in_circle in st.session_state["samples_history"]:
        all_x.extend(x)
        all_y.extend(y)
        all_in.extend(in_circle)
    
    if len(all_x) > 0:
        all_x, all_y, all_in = np.array(all_x), np.array(all_y), np.array(all_in)
        # Puntos dentro del círculo
        p.scatter(all_x[all_in], all_y[all_in], size=4, fill_color=UBU_YELLOW, 
                  line_color=UBU_YELLOW, fill_alpha=0.7)
        # Puntos fuera del círculo
        p.scatter(all_x[~all_in], all_y[~all_in], size=4, fill_color=UBU_RED, 
                  line_color=UBU_RED, fill_alpha=0.6)
    
    p.xaxis.major_label_text_font_size = "20px"
    p.yaxis.major_label_text_font_size = "20px"
    p.title.text_font_size = "18px"
    p.title.align = "center"
    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    return p

def plot_convergence():
    """Historial de aproximaciones de pi hacia el valor teórico"""
    estimates = st.session_state["pi_estimates"]
    if len(estimates) == 0:
        return None
        
    p = figure(width=600, height=350, x_axis_label="Iteraciones / Lotes", 
               y_axis_label="Estimación de π^", toolbar_location=None, tools="",
               title="Convergencia Empírica")
    
    x_axis = list(range(1, len(estimates) + 1))
    p.line(x_axis, estimates, line_color=UBU_RED, line_width=3)
    p.scatter(x_axis, estimates, size=6, fill_color=UBU_YELLOW, line_color=UBU_RED, line_width=2)
    
    # Línea de control horizontal (pi real)
    p.line(x_axis, [math.pi]*len(estimates), line_color="#444444", line_width=2, line_dash="dashed")
    
    p.xaxis.major_label_text_font_size = "20px"
    p.yaxis.major_label_text_font_size = "20px"
    p.title.text_font_size = "18px"
    p.title.align = "center"
    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    return p

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Estimación Puntual de π</div>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Estimación Puntual:</b> El objetivo consiste en calcular un valor numérico único a partir de datos muestrales para aproximar un parámetro poblacional desconocido (en este caso, la constante matemática π).</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'><b>Fundamento geométrico:</b> Al inscribir un círculo de radio r=1 en un cuadrado de lado 2r=2, la proporción de sus áreas es exactamente pi. Al simular puntos aleatorios uniformes, el porcentaje de aciertos dentro del círculo nos aproxima esta relación.</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>📐 Formulación Matemática</div>", unsafe_allow_html=True)
        st.latex(r"\pi = 4 \cdot \frac{\text{Área del Círculo}}{\text{Área del Cuadrado}} \approx 4 \cdot \frac{m \text{ (puntos dentro)}}{n \text{ (puntos totales)}}")
        
        st.markdown("<div class='section-title'>🎲 Controles y Simulación</div>", unsafe_allow_html=True)
        
        # Panel de botones simétricos
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("+100 Puntos", use_container_width=True):
                update_estimates(100)
                st.rerun()
        with btn_col2:
            if st.button("+1000 Puntos", use_container_width=True):
                update_estimates(1000)
                st.rerun()
        with btn_col3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state["samples_in_circle"] = 0
                st.session_state["total_samples"] = 0
                st.session_state["samples_history"] = []
                st.session_state["pi_estimates"] = []
                st.rerun()

        # Cálculos previos y formateo limpio antes de pasar al f-string HTML
        total_n = st.session_state['total_samples']
        inside_m = st.session_state['samples_in_circle']
        pi_est = 4 * inside_m / total_n if total_n > 0 else 0.0
        error_val = abs(pi_est - math.pi) if total_n > 0 else 0.0

        pi_text = f"{pi_est:.4f}" if total_n > 0 else "—"
        error_text = f"{error_val:.6f}" if total_n > 0 else "—"

        # Renderizado de las métricas principales sin expresiones complejas dentro de las llaves
        st.markdown(f"""
        <div class='stats-container' style='margin-top: 25px;'>
            <div class='stat-box'>
                <div class='stat-label'>Aciertos (m)</div>
                <div class='stat-value'>{inside_m}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Totales (n)</div>
                <div class='stat-value'>{total_n}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Estimación π^</div>
                <div class='stat-value' style='color:{PANTONE_2727};'>{pi_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='comment-box'>
            <span class='comment-label'>Propiedades del Estimador:</span><br>
            • <b>Insesgadez:</b> El valor esperado del estimador es exactamente el parámetro real $E[\\hat{{\\pi}}] = \\pi$.<br>
            • <b>Consistencia:</b> Conforme $n \\to \\infty$, el error del estimador se reduce a cero.<br><br>
            <b>π Teórico:</b> {math.pi:.6f} &nbsp;|&nbsp; <b>Error absoluto actual:</b> {error_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>🎯 Plano de Muestreo Geométrico</div>", unsafe_allow_html=True)
        streamlit_bokeh(plot_circle_and_samples(), use_container_width=True, key="circle_plot")
        
        if len(st.session_state["pi_estimates"]) > 0:
            st.markdown("<div class='section-title' style='margin-top: 20px;'>📈 Curva de Convergencia</div>", unsafe_allow_html=True)
            conv_p = plot_convergence()
            if conv_p:
                streamlit_bokeh(conv_p, use_container_width=True, key="convergence_plot")
        else:
            st.info("📢 Agrega puntos aleatorios en el panel izquierdo para inicializar el análisis visual.")

    st.markdown(
        "<div class='footer-bar'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; [AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()