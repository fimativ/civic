import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="Esperanza y Varianza")

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

.metric-large {{
    font-size: 32px; font-weight: 700; color: var(--app-fg); text-align: center;
    border: 3px solid {GREEN_LINE}; border-radius: 12px;
    padding: 20px 15px; background: var(--box-bg); width: 100%;
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

/* ---- Checkboxes para tarjetas ---- */
[data-testid="stCheckbox"] label {{
    font-size: 20px !important;
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "I",
        "expectation_rolls": [],
        "expectation_means": [],
        "variance_draws": [],
        "variance_vars": [],
        "variance_means": [],
    }
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

def create_expectation_convergence_chart(rolls, means, theoretical_ex):
    """Gráfico de convergencia de la media a E[X]."""
    if len(rolls) == 0:
        # Gráfico vacío
        plot = figure(
            height=300, width=500,
            x_axis_label="Número de lanzamientos",
            y_axis_label="Media muestral",
            toolbar_location=None,
            x_range=(0, 10),
            y_range=(0, 7)
        )
        line_ex = Span(location=theoretical_ex, dimension="width", 
                       line_color=GREEN_LINE, line_dash="dashed", line_width=2)
        plot.add_layout(line_ex)
        return style_axes(plot)
    
    plot = figure(
        height=300, width=500,
        x_axis_label="Número de lanzamientos",
        y_axis_label="Media muestral",
        toolbar_location=None,
        x_range=(0, max(50, len(rolls))),
        y_range=(0.5, 6.5)
    )
    
    x_vals = np.arange(1, len(means) + 1)
    plot.line(x_vals, means, line_width=3, color=BLUE_LINE, alpha=0.8)
    plot.circle(x_vals, means, size=6, color=BLUE_LINE, alpha=0.6)
    
    # Línea horizontal en E[X]
    line_ex = Span(location=theoretical_ex, dimension="width", 
                   line_color=GREEN_LINE, line_dash="dashed", line_width=2)
    plot.add_layout(line_ex)
    
    return style_axes(plot)

def create_die_distribution_chart(die_probs):
    """Gráfico de barras de la distribución del dado."""
    faces = np.arange(1, 7)
    
    plot = figure(
        height=250, width=500,
        x_range=[str(i) for i in faces],
        y_axis_label="Probabilidad",
        toolbar_location=None
    )
    
    plot.vbar(x=[str(i) for i in faces], top=die_probs, width=0.6,
              fill_color=BLUE_LINE, line_color="white", alpha=0.8, line_width=2)
    
    return style_axes(plot)

def create_variance_convergence_chart(draws, vars_list, theoretical_var):
    """Gráfico de convergencia de la varianza a Var[X]."""
    if len(vars_list) == 0:
        plot = figure(
            height=300, width=500,
            x_axis_label="Número de observaciones",
            y_axis_label="Varianza muestral",
            toolbar_location=None,
            x_range=(0, 10),
            y_range=(0, 10)
        )
        line_var = Span(location=theoretical_var, dimension="width", 
                        line_color=GREEN_LINE, line_dash="dashed", line_width=2)
        plot.add_layout(line_var)
        return style_axes(plot)
    
    plot = figure(
        height=300, width=500,
        x_axis_label="Número de observaciones",
        y_axis_label="Varianza muestral",
        toolbar_location=None,
        x_range=(0, max(50, len(vars_list))),
        y_range=(0, max(theoretical_var * 1.5, 10))
    )
    
    x_vals = np.arange(1, len(vars_list) + 1)
    plot.line(x_vals, vars_list, line_width=3, color=BLUE_LINE, alpha=0.8)
    plot.circle(x_vals, vars_list, size=6, color=BLUE_LINE, alpha=0.6)
    
    # Línea horizontal en Var[X]
    line_var = Span(location=theoretical_var, dimension="width", 
                    line_color=GREEN_LINE, line_dash="dashed", line_width=2)
    plot.add_layout(line_var)
    
    return style_axes(plot)

# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_expectation():
    """Sección I: Expectation (Esperanza)"""
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Esperanza: El centro de la distribución</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "La esperanza de una variable aleatoria es un número que intenta capturar el <b>centro</b> "
            "de su distribución. Puede interpretarse como el <b>promedio a largo plazo</b>: si repites "
            "el experimento muchas veces, la media muestral convergerá a E[X].<br><br>"
            "Se define como la suma <b>ponderada por probabilidades</b> de todos los posibles valores."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>Fórmula:</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='formula-box'>E[X] = Σ x·P(x)</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'><b>Ejemplo:</b><br>"
            "Lanza un dado justo 6 caras. La esperanza es:<br>"
            "E[X] = 1·(1/6) + 2·(1/6) + ... + 6·(1/6) = 3.5"
            "</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        
        st.markdown(
            "<div class='content-box'><b>Ajusta la distribución del dado:</b> "
            "Modifica las probabilidades de cada cara y observa cómo cambia E[X].</div>",
            unsafe_allow_html=True
        )
        
        # Sliders para las probabilidades
        st.markdown("<div style='font-size: 20px; color: var(--box-fg); margin: 15px 0;'><b>Probabilidades:</b></div>", 
                   unsafe_allow_html=True)
        
        probs = []
        for face in range(1, 7):
            p = st.slider(f"P(cara = {face})", 0.0, 1.0, 1/6, 0.01, key=f"prob_{face}")
            probs.append(p)
        
        # Normalizar
        total = sum(probs)
        if total > 0:
            probs = [p/total for p in probs]
        else:
            probs = [1/6] * 6
        
        # Calcular E[X]
        theoretical_ex = sum((i+1) * probs[i] for i in range(6))
        
        # Botones de simulación
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Lanzar una vez", use_container_width=True):
                roll = np.random.choice([1, 2, 3, 4, 5, 6], p=probs)
                st.session_state["expectation_rolls"].append(roll)
                if len(st.session_state["expectation_rolls"]) > 0:
                    mean_so_far = np.mean(st.session_state["expectation_rolls"])
                    st.session_state["expectation_means"].append(mean_so_far)
                st.rerun()
        
        with col_btn2:
            if st.button("Lanzar 100 veces", use_container_width=True):
                rolls = np.random.choice([1, 2, 3, 4, 5, 6], size=100, p=probs)
                st.session_state["expectation_rolls"].extend(rolls)
                for i in range(100):
                    mean_so_far = np.mean(st.session_state["expectation_rolls"][:len(st.session_state["expectation_rolls"])-(99-i)])
                    st.session_state["expectation_means"].append(mean_so_far)
                st.rerun()
        
        if st.button("Reiniciar", use_container_width=True):
            st.session_state["expectation_rolls"] = []
            st.session_state["expectation_means"] = []
            st.rerun()
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Gráfico de convergencia
        st.markdown("#### Convergencia de la media", help="La línea azul converge a E[X] (línea verde)")
        conv_chart = create_expectation_convergence_chart(
            st.session_state["expectation_rolls"],
            st.session_state["expectation_means"],
            theoretical_ex
        )
        streamlit_bokeh(conv_chart, use_container_width=True)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        # Gráfico de distribución
        st.markdown("#### Distribución del dado", help="Probabilidades de cada cara")
        dist_chart = create_die_distribution_chart(probs)
        streamlit_bokeh(dist_chart, use_container_width=True)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Resultados:</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box'><b>E[X] teórica</b><br>{theoretical_ex:.3f}</div>",
                       unsafe_allow_html=True)
        with m2:
            if len(st.session_state["expectation_means"]) > 0:
                sample_mean = st.session_state["expectation_means"][-1]
                st.markdown(f"<div class='metric-box'><b>Media muestral</b><br>{sample_mean:.3f}</div>",
                           unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric-box'><b>Media muestral</b><br>—</div>",
                           unsafe_allow_html=True)

def render_variance():
    """Sección II: Variance (Varianza)"""
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='statement-box'><b>Varianza: La dispersión de la distribución</b></div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'>"
            "Mientras que la esperanza mide el centro, la varianza mide <b>cuánto se dispersan</b> "
            "los valores alrededor de ese centro. Es el <b>promedio de las desviaciones al cuadrado</b> "
            "respecto a la esperanza."
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("<div class='section-title'>Fórmula:</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='formula-box'>Var[X] = E[(X - E[X])²]</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='content-box'><b>Concepto:</b><br>"
            "La varianza cuantifica la dispersión de los datos. "
            "A medida que realizas más observaciones, la varianza muestral converge a Var[X]."
            "</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        
        st.markdown(
            "<div class='content-box'><b>Selecciona qué valores incluir:</b> "
            "Elige qué cartas quieres en el mazo (de 1 a 10) y observa cómo "
            "esto cambia la varianza.</div>",
            unsafe_allow_html=True
        )
        
        # Checkboxes para seleccionar cartas
        st.markdown("<div style='font-size: 20px; color: var(--box-fg); margin: 15px 0;'><b>Cartas disponibles:</b></div>", 
                   unsafe_allow_html=True)
        
        selected_cards = []
        cols = st.columns(5)
        for i in range(10):
            with cols[i % 5]:
                if st.checkbox(f"Carta {i+1}", value=True, key=f"card_{i+1}"):
                    selected_cards.append(i + 1)
        
        if len(selected_cards) == 0:
            st.warning("⚠️ Debes seleccionar al menos una carta")
            return
        
        # Calcular esperanza y varianza
        theoretical_mean = np.mean(selected_cards)
        theoretical_var = np.var(selected_cards, ddof=0)  # Varianza poblacional
        
        # Botones de simulación
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Sacar una carta", use_container_width=True, key="draw_1"):
                card = np.random.choice(selected_cards)
                st.session_state["variance_draws"].append(card)
                if len(st.session_state["variance_draws"]) > 0:
                    var_so_far = np.var(st.session_state["variance_draws"], ddof=0)
                    mean_so_far = np.mean(st.session_state["variance_draws"])
                    st.session_state["variance_vars"].append(var_so_far)
                    st.session_state["variance_means"].append(mean_so_far)
                st.rerun()
        
        with col_btn2:
            if st.button("Sacar 100 cartas", use_container_width=True, key="draw_100"):
                cards = np.random.choice(selected_cards, size=100)
                st.session_state["variance_draws"].extend(cards)
                for i in range(100):
                    var_so_far = np.var(st.session_state["variance_draws"][:len(st.session_state["variance_draws"])-(99-i)], ddof=0)
                    mean_so_far = np.mean(st.session_state["variance_draws"][:len(st.session_state["variance_draws"])-(99-i)])
                    st.session_state["variance_vars"].append(var_so_far)
                    st.session_state["variance_means"].append(mean_so_far)
                st.rerun()
        
        if st.button("Reiniciar", use_container_width=True, key="reset_var"):
            st.session_state["variance_draws"] = []
            st.session_state["variance_vars"] = []
            st.session_state["variance_means"] = []
            st.rerun()
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        
        # Gráfico de convergencia de varianza
        st.markdown("#### Convergencia de la varianza", help="La línea azul converge a Var[X] (línea verde)")
        var_chart = create_variance_convergence_chart(
            st.session_state["variance_draws"],
            st.session_state["variance_vars"],
            theoretical_var
        )
        streamlit_bokeh(var_chart, use_container_width=True)
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Resultados:</div>", unsafe_allow_html=True)
        
        # Mostrar Average y Variance como cajas grandes
        if len(st.session_state["variance_means"]) > 0:
            sample_mean = st.session_state["variance_means"][-1]
            sample_var = st.session_state["variance_vars"][-1]
        else:
            sample_mean = theoretical_mean
            sample_var = theoretical_var
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"<div style='border: 4px solid {GREEN_LINE}; border-radius: 12px; "
                f"padding: 30px; background: var(--box-bg); text-align: center;'>"
                f"<div style='font-size: 18px; color: var(--muted-fg); margin-bottom: 10px;'>Average</div>"
                f"<div style='font-size: 36px; font-weight: 700; color: {BLUE_LINE};'>{sample_mean:.2f}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div style='border: 4px solid {BLUE_LINE}; border-radius: 12px; "
                f"padding: 30px; background: var(--box-bg); text-align: center;'>"
                f"<div style='font-size: 18px; color: var(--muted-fg); margin-bottom: 10px;'>Variance</div>"
                f"<div style='font-size: 36px; font-weight: 700; color: {BLUE_LINE};'>{sample_var:.2f}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        
        m3, m4 = st.columns(2)
        with m3:
            st.markdown(f"<div class='metric-box'><b>Var[X] teórica</b><br>{theoretical_var:.3f}</div>",
                       unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-box'><b>E[X] teórica</b><br>{theoretical_mean:.3f}</div>",
                       unsafe_allow_html=True)

# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown(
        "<div class='top-bar-title'>C1VIC D4TA · Esperanza y Varianza</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2 = st.columns(2)
    
    if nav_col1.button("(I) Esperanza: E[X]", use_container_width=True):
        st.session_state["page"] = "I"
        st.rerun()
    if nav_col2.button("(II) Varianza: Var[X]", use_container_width=True):
        st.session_state["page"] = "II"
        st.rerun()
    
    paginas = {
        "I": render_expectation,
        "II": render_variance,
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
