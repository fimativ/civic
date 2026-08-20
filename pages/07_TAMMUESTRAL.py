#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
import math
import uuid
from scipy.stats import norm
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA · Tamaño Muestral")

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

.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 25px; text-align: center;
    font-size: 22px; color: var(--muted-fg); margin-top: 30px;
}}

/* ---- Spoiler blur ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-click-wrapper {{ cursor: pointer; display: block; text-decoration: none; margin-top: 20px; margin-bottom: 25px; }}
.spoiler-box {{
    color: {BLUE_LINE}; font-weight: 400; font-size: 23px; line-height: 1.6;
    background: #e8eeff; border-left: 10px solid {BLUE_LINE};
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(15px); transition: filter 0.3s;
}}
.spoiler-toggle:checked ~ .spoiler-click-wrapper .spoiler-box {{ filter: none; }}

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
    defaults = {"page": "INTRO"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def spoiler(content):
    """Caja de spoiler con desenfoque blur — pulsa para revelar."""
    uid = str(uuid.uuid4())
    html = f"""
    <input type="checkbox" id="spoiler_{uid}" class="spoiler-toggle">
    <label for="spoiler_{uid}" class="spoiler-click-wrapper">
        <div class="spoiler-box">{content}</div>
    </label>
    """
    st.markdown(html, unsafe_allow_html=True)

def style_axes(p, label_size="18px", tick_size="15px"):
    p.xaxis.axis_label_text_font_size = label_size
    p.yaxis.axis_label_text_font_size = label_size
    p.xaxis.major_label_text_font_size = tick_size
    p.yaxis.major_label_text_font_size = tick_size
    p.background_fill_color = "#ffffff"
    p.border_fill_color = "#ffffff"
    return p

def draw_curve(x_vals, y_vals, x_now, y_now, x_label, title, log_y=False):
    p = figure(height=320, width=560, toolbar_location=None,
               x_axis_label=x_label, y_axis_label="n necesario", title=title,
               y_axis_type="log" if log_y else "linear")
    p.line(x_vals, y_vals, line_width=3, color=BLUE_LINE)
    p.circle([x_now], [y_now], size=14, color=UBU_RED, line_color="white", line_width=3)
    vline = Span(location=x_now, dimension="height", line_color=UBU_RED, line_dash="dashed", line_width=2)
    p.add_layout(vline)
    return style_axes(p)

def draw_power_diagram(alpha, power, d):
    """Diagrama H0 vs H1 en escala bruta (sigma=1) con n resultante de alpha, power y d."""
    z_a = norm.ppf(1 - alpha)
    z_b = norm.ppf(power)
    n = ((z_a + z_b) / d) ** 2
    se = 1 / math.sqrt(n)

    x_min = -4 * se
    x_max = d + 4 * se
    x = np.linspace(x_min, x_max, 400)
    y0 = norm.pdf(x, 0, se)
    y1 = norm.pdf(x, d, se)
    crit = z_a * se

    p = figure(height=340, width=560, toolbar_location=None,
               x_axis_label="Estadístico (escala de μ, σ=1)", y_axis_label="Densidad",
               title=f"H0 vs H1  (n ≈ {math.ceil(n)})")

    mask_alpha = x >= crit
    p.varea(x=x[mask_alpha], y1=0, y2=y0[mask_alpha], color=UBU_RED, alpha=0.35, legend_label="α (Error tipo I)")
    mask_beta = x <= crit
    p.varea(x=x[mask_beta], y1=0, y2=y1[mask_beta], color="#888888", alpha=0.35, legend_label="β (Error tipo II)")
    mask_power = x >= crit
    p.varea(x=x[mask_power], y1=0, y2=y1[mask_power], color=GREEN_LINE, alpha=0.25, legend_label="Potencia (1−β)")

    p.line(x, y0, line_width=3, color=UBU_RED, legend_label="H0: N(0, σ/√n)")
    p.line(x, y1, line_width=3, color=BLUE_LINE, legend_label="H1: N(δ, σ/√n)")

    vline = Span(location=crit, dimension="height", line_color=UBU_DARK, line_dash="dashed", line_width=2)
    p.add_layout(vline)

    p.legend.location = "top_right"
    p.legend.label_text_font_size = "11px"
    p.legend.background_fill_alpha = 0.85
    return style_axes(p), math.ceil(n)

# ---- INTRO -------------------------------------------------------------

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El cálculo del tamaño muestral necesario depende, ante todo, "
            "de <b>qué tipo de parámetro</b> queremos estimar: una media (variable continua) o una "
            "proporción (variable binaria) exigen fórmulas distintas.</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Elige el parámetro y los datos:**", unsafe_allow_html=True)
            tipo = st.radio("Parámetro a estimar", ["Media (μ)", "Proporción (p)"], horizontal=True)
            conf = st.slider("Nivel de confianza (%)", 80, 99, 95)
            E = st.slider("Error máximo admisible (E)", 0.01, 10.0, 1.0, 0.01)
            if tipo == "Media (μ)":
                sigma = st.number_input("Desv. típica poblacional (σ)", value=10.0, min_value=0.1, step=0.5)
            else:
                p_est = st.slider("Proporción estimada (p̃)", 0.01, 0.99, 0.5, 0.01)

        alpha = 1 - conf / 100
        z = norm.ppf(1 - alpha / 2)

        if tipo == "Media (μ)":
            n_needed = (z * sigma / E) ** 2
            st.markdown("<div class='formula-box'>n = (z<sub>α/2</sub> · σ / E)²</div>", unsafe_allow_html=True)
            E_range = np.linspace(max(E * 0.2, 0.05), E * 3, 100)
            n_range = (z * sigma / E_range) ** 2
        else:
            n_needed = (z ** 2) * p_est * (1 - p_est) / (E ** 2)
            st.markdown("<div class='formula-box'>n = z<sub>α/2</sub>² · p̃(1−p̃) / E²</div>", unsafe_allow_html=True)
            E_range = np.linspace(max(E * 0.2, 0.005), E * 3, 100)
            n_range = (z ** 2) * p_est * (1 - p_est) / (E_range ** 2)

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con un nivel de confianza del {conf}% "
            f"y admitiendo un error máximo de {E:.2f}, se necesitan al menos "
            f"<b>{math.ceil(n_needed)}</b> observaciones. Cuanto más pequeño sea el error tolerado E, "
            f"mayor será el tamaño muestral requerido: la relación no es lineal, sino cuadrática inversa.</div>",
            unsafe_allow_html=True
        )
        spoiler(
            "📐 <b>¿De dónde sale la fórmula?</b><br><br>"
            "Un intervalo de confianza al (1−α)% para la media es:<br>"
            "<div class='formula-box' style='font-size:22px;'>X̄ ± z<sub>α/2</sub> · σ/√n</div>"
            "El margen de error del intervalo es el error máximo E que estamos dispuestos a tolerar:<br>"
            "<div class='formula-box' style='font-size:22px;'>E = z<sub>α/2</sub> · σ/√n</div>"
            "Despejando √n y elevando al cuadrado:<br>"
            "<div class='formula-box' style='font-size:22px;'>√n = z<sub>α/2</sub> · σ / E "
            "&nbsp;⟹&nbsp; n = (z<sub>α/2</sub> · σ / E)²</div>"
            "Para proporciones, σ² = p̃(1−p̃), con lo que la fórmula queda:<br>"
            "<div class='formula-box' style='font-size:22px;'>n = z<sub>α/2</sub>² · p̃(1−p̃) / E²</div>"
            "En ambos casos n crece con z² (más confianza) y decrece con E² (más tolerancia al error)."
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-large'>n necesario ≈ {math.ceil(n_needed)}</div>", unsafe_allow_html=True)

        chart = draw_curve(E_range, n_range, E, n_needed, "Error máximo E", "n necesario en función de E")
        streamlit_bokeh(chart, use_container_width=True, key="intro_chart")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"El <b>punto rojo</b> es tu configuración actual (E={E:.2f} → n≈{math.ceil(n_needed)}). "
            f"Fíjate en la asimetría de la curva: pasar de E={E:.2f} a E={E/2:.2f} "
            f"no dobla n, lo <b>cuadruplica</b>. En cambio, doblar E a {E*2:.2f} lo divide entre cuatro. "
            f"El precio de la precisión crece mucho más rápido de lo que parece."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>Nivel de confianza</div>
                <div class='stat-value'>{conf}%</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>z<sub>α/2</sub></div>
                <div class='stat-value'>{z:.3f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Tipo</div>
                <div class='stat-value' style='font-size:20px;'>{tipo}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- A) Nivel de significación ------------------------------------------

def render_alpha():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>En un contraste de hipótesis, cuanto más <b>exigente</b> sea el "
            "nivel de significación α (más pequeño), mayor será el valor crítico z<sub>α</sub> y, por tanto, "
            "mayor el tamaño muestral necesario para mantener la misma potencia.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>n = ((z<sub>α</sub> + z<sub>β</sub>) / d)²</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Contraste unilateral H0: μ=μ₀ frente a H1: μ=μ₀+δ, con "
            "tamaño del efecto estandarizado d = δ/σ.</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta el nivel de significación:**", unsafe_allow_html=True)
            alpha = st.slider("Nivel de significación α", 0.01, 0.30, 0.05, 0.01)
            power = st.number_input("Potencia deseada (1−β)", 0.50, 0.999, 0.80, 0.01)
            d = st.number_input("Tamaño del efecto d = δ/σ", 0.05, 3.0, 0.5, 0.05)

        alphas = np.linspace(0.01, 0.30, 100)
        z_b = norm.ppf(power)
        ns = ((norm.ppf(1 - alphas) + z_b) / d) ** 2
        n_now = ((norm.ppf(1 - alpha) + z_b) / d) ** 2

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con α={alpha:.2f}, potencia {power:.0%} "
            f"y efecto d={d:.2f}, se necesitan <b>{math.ceil(n_now)}</b> observaciones. Si exigieras "
            f"α=0.01 en vez de {alpha:.2f}, el tamaño muestral necesario cambiaría a "
            f"<b>{math.ceil(((norm.ppf(0.99) + z_b) / d) ** 2)}</b>.</div>",
            unsafe_allow_html=True
        )
        spoiler(
            "📐 <b>¿De dónde sale la fórmula?</b><br><br>"
            "Planteamos el contraste unilateral H0: μ=μ₀ frente a H1: μ=μ₀+δ. "
            "Bajo H0, rechazamos cuando X̄ supera el valor crítico:<br>"
            "<div class='formula-box' style='font-size:22px;'>c = μ₀ + z<sub>α</sub> · σ/√n</div>"
            "Queremos que bajo H1 la probabilidad de rechazar sea exactamente 1−β (la potencia). "
            "Eso significa que c debe quedar z<sub>β</sub> desviaciones típicas a la <i>izquierda</i> de μ₁:<br>"
            "<div class='formula-box' style='font-size:22px;'>c = μ₁ − z<sub>β</sub> · σ/√n "
            "= μ₀ + δ − z<sub>β</sub> · σ/√n</div>"
            "Igualando las dos expresiones de c y agrupando:<br>"
            "<div class='formula-box' style='font-size:22px;'>"
            "z<sub>α</sub> · σ/√n + z<sub>β</sub> · σ/√n = δ</div>"
            "<div class='formula-box' style='font-size:22px;'>"
            "(z<sub>α</sub> + z<sub>β</sub>) · σ/√n = δ</div>"
            "Despejando n y usando d = δ/σ:<br>"
            "<div class='formula-box' style='font-size:22px;'>"
            "n = ((z<sub>α</sub> + z<sub>β</sub>) / d)²</div>"
            "Esta misma fórmula rige los apartados II y III, cambiando solo qué parámetro se deja variar."
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_curve(alphas, ns, alpha, n_now, "Nivel de significación (α)", "n necesario en función de α")
        streamlit_bokeh(chart, use_container_width=True, key="alpha_chart")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"Reducir α desplaza el <b>valor crítico hacia la derecha</b>: la zona de rechazo se estrecha "
            f"y el test se vuelve más conservador. Para compensar esa exigencia extra manteniendo la misma potencia, "
            f"hay que aumentar n. Con α={alpha:.2f} el valor crítico es z={norm.ppf(1-alpha):.2f}; "
            f"bajar a α=0.01 lo elevaría a z={norm.ppf(0.99):.2f} y necesitarías "
            f"<b>{math.ceil(((norm.ppf(0.99) + norm.ppf(power)) / d)**2)}</b> observaciones."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        diagram, n_int = draw_power_diagram(alpha, power, d)
        streamlit_bokeh(diagram, use_container_width=True, key="alpha_diagram")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"Mueve el deslizador de α y observa cómo la línea discontinua (valor crítico) se desplaza. "
            f"Al bajar α, la línea se mueve a la derecha: la <b>zona roja se hace más pequeña</b> (menos error tipo I) "
            f"pero la <b>zona gris crece</b> (más error tipo II). Las campanas no cambian de posición; "
            f"solo cambia dónde colocas el umbral de decisión. Compensar esa pérdida de potencia "
            f"exige subir n, que es lo que refleja la curva superior."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>α</div>
                <div class='stat-value'>{alpha:.2f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>Potencia (fija)</div>
                <div class='stat-value'>{power:.0%}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>n necesario</div>
                <div class='stat-value'>{n_int}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- B) Potencia del test ------------------------------------------------

def render_power():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>La <b>potencia</b> de un test (1−β) es la probabilidad de "
            "rechazar H0 cuando realmente es falsa. A mayor potencia exigida, menor margen se deja al "
            "error de tipo II, y eso se traduce en un tamaño muestral mayor.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>n = ((z<sub>α</sub> + z<sub>β</sub>) / d)²</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta la potencia deseada:**", unsafe_allow_html=True)
            power = st.slider("Potencia deseada (1−β)", 0.50, 0.99, 0.80, 0.01)
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="pow_alpha")
            d = st.number_input("Tamaño del efecto d = δ/σ", 0.05, 3.0, 0.5, 0.05, key="pow_d")

        powers = np.linspace(0.50, 0.995, 100)
        z_a = norm.ppf(1 - alpha)
        ns = ((z_a + norm.ppf(powers)) / d) ** 2
        n_now = ((z_a + norm.ppf(power)) / d) ** 2

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> para detectar un efecto d={d:.2f} con "
            f"α={alpha:.2f}, alcanzar una potencia del {power:.0%} exige <b>{math.ceil(n_now)}</b> "
            f"observaciones. Subir la potencia al 95% elevaría el requisito a "
            f"<b>{math.ceil(((z_a + norm.ppf(0.95)) / d) ** 2)}</b> observaciones. Cada punto extra de "
            f"potencia cuesta cada vez más muestra.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_curve(powers, ns, power, n_now, "Potencia deseada (1−β)", "n necesario en función de la potencia")
        streamlit_bokeh(chart, use_container_width=True, key="power_chart")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"Pasar del {power:.0%} al 95% de potencia cuesta "
            f"<b>{math.ceil(((norm.ppf(1-alpha) + norm.ppf(0.95)) / d)**2) - math.ceil(n_now):+d} observaciones</b> extra. "
            f"Pero ir del 95% al 99% costaría "
            f"<b>{math.ceil(((norm.ppf(1-alpha) + norm.ppf(0.99)) / d)**2) - math.ceil(((norm.ppf(1-alpha) + norm.ppf(0.95)) / d)**2):+d} más</b>. "
            f"Cada décima extra de potencia es más cara que la anterior: por eso en práctica el estándar se fija en 80% o 90%."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        diagram, n_int = draw_power_diagram(alpha, power, d)
        streamlit_bokeh(diagram, use_container_width=True, key="power_diagram")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"A diferencia del apartado anterior, aquí el umbral (línea discontinua) no se mueve: α={alpha:.2f} está fijo. "
            f"Lo que cambia al pedir más potencia es que n crece, lo que reduce σ/√n y hace las campanas más <b>estrechas y separadas</b>. "
            f"El solapamiento disminuye y la zona verde (potencia) se agranda sin tocar el valor crítico."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>Potencia</div>
                <div class='stat-value'>{power:.0%}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>α (fijo)</div>
                <div class='stat-value'>{alpha:.2f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>n necesario</div>
                <div class='stat-value'>{n_int}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---- C) Diferencia a observar --------------------------------------------

def render_effect():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Cuanto más <b>pequeña</b> sea la diferencia (efecto) que "
            "queremos ser capaces de detectar, más difícil es distinguirla del azar y, por tanto, "
            "mayor será el tamaño muestral necesario: la relación es n=k·(1/d²) con k cte.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='formula-box'>n = ((z<sub>α</sub> + z<sub>β</sub>) / d)²</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True, key="controls_box"):
            st.markdown("**Ajusta la diferencia a detectar:**", unsafe_allow_html=True)
            d = st.slider("Tamaño del efecto d = δ/σ", 0.05, 2.0, 0.5, 0.05)
            alpha = st.number_input("Nivel de significación α", 0.01, 0.30, 0.05, 0.01, key="eff_alpha")
            power = st.number_input("Potencia deseada (1−β)", 0.50, 0.999, 0.80, 0.01, key="eff_power")

        ds = np.linspace(0.05, 2.0, 100)
        z_a, z_b = norm.ppf(1 - alpha), norm.ppf(power)
        ns = ((z_a + z_b) / ds) ** 2
        n_now = ((z_a + z_b) / d) ** 2

        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con α={alpha:.2f} y potencia {power:.0%}, "
            f"detectar un efecto d={d:.2f} exige <b>{math.ceil(n_now)}</b> observaciones. Si la diferencia "
            f"real fuera el doble (d={2*d:.2f}), bastarían solo "
            f"<b>{math.ceil(((z_a + z_b) / (2*d)) ** 2)}</b> observaciones: los efectos grandes son mucho "
            f"más fáciles (y baratos) de detectar.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        chart = draw_curve(ds, ns, d, n_now, "Tamaño del efecto (d)", "n necesario en función de d", log_y=True)
        streamlit_bokeh(chart, use_container_width=True, key="effect_chart")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"El eje Y está en escala logarítmica porque para d pequeños n se dispara a valores "
            f"inmanejables en escala lineal. Con d={d:.2f} necesitas n≈{math.ceil(n_now)}; "
            f"con d={d/2:.2f} (la mitad) necesitarías n≈{math.ceil(n_now*4)}, cuatro veces más. "
            f"En escala log esa relación cuadrática aparece como una <b>recta de pendiente −2</b>, "
            f"lo que hace visualmente evidente que detectar efectos pequeños es exponencialmente más caro."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        diagram, n_int = draw_power_diagram(alpha, power, d)
        streamlit_bokeh(diagram, use_container_width=True, key="effect_diagram")
        st.markdown(
            f"<div class='content-box' style='font-size:20px;'>"
            f"Con d={d:.2f}, la campana azul (H1) está desplazada {d:.2f}·σ/√n a la derecha de la roja (H0). "
            f"Reduce d a 0.2 y las campanas casi se fusionan: α y β compiten por el mismo espacio "
            f"y no hay n razonable que las separe bien. Aumenta d a 1.0 o más y el solapamiento desaparece: "
            f"con pocos datos el test ya detecta el efecto sin esfuerzo."
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-label'>d</div>
                <div class='stat-value'>{d:.2f}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>α / Potencia</div>
                <div class='stat-value' style='font-size:22px;'>{alpha:.2f} / {power:.0%}</div>
            </div>
            <div class='stat-box'>
                <div class='stat-label'>n necesario</div>
                <div class='stat-value'>{n_int}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Tamaño Muestral</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav0, nav1, nav2, nav3 = st.columns(4)
    if nav0.button("Introducción", use_container_width=True):
        st.session_state["page"] = "INTRO"
        st.rerun()
    if nav1.button("I) Nivel de significación", use_container_width=True):
        st.session_state["page"] = "A"
        st.rerun()
    if nav2.button("II) Potencia del test", use_container_width=True):
        st.session_state["page"] = "B"
        st.rerun()
    if nav3.button("III) Diferencia a observar", use_container_width=True):
        st.session_state["page"] = "C"
        st.rerun()

    paginas = {
        "INTRO": render_intro,
        "A": render_alpha,
        "B": render_power,
        "C": render_effect,
    }
    paginas[st.session_state["page"]]()

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
