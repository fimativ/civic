import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool, BoxAnnotation
from scipy.stats import expon, norm, binom
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Distribuciones Continuas")

# Colores
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"
ORANGE_ACCENT  = "#E67E22"

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
    height: 100%; width: 100%; line-height: 1.2;
}}

div[data-testid="column"]:has(.bg-left) {{
    background: var(--panel-left-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
}}
div[data-testid="column"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    padding: 40px; border-radius: 16px; min-height: calc(100vh - 150px);
    display: flex; flex-direction: column; align-items: center;
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
.subsection-title {{
    font-size: 23px; font-weight: 600; color: {ORANGE_ACCENT};
    margin: 20px 0 10px 0; border-left: 5px solid {ORANGE_ACCENT};
    padding-left: 15px;
}}
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 27px; color: var(--spoiler-fg);
}}
.spacer {{ height: 35px; }}

/* ---- Spoiler: borroso en azul hasta que se pulsa ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-click-wrapper {{ cursor: pointer; display: block; text-decoration: none; margin-top: 20px; margin-bottom: 25px; }}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400; font-size: 25px; line-height: 1.5;
    background: var(--spoiler-bg); border-left: 10px solid var(--spoiler-fg);
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(15px); transition: filter 0.3s;
}}
.spoiler-toggle:checked ~ .spoiler-click-wrapper .spoiler-box {{ filter: none; }}

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

/* ---- Inputs generales interactivos ---- */
[data-testid="stNumberInput"] input, [data-baseweb="select"] div {{
    font-size: 22px !important; font-weight: 600 !important;
}}
[data-testid="stNumberInput"] label p, label[data-testid="stWidgetLabel"] p {{
    font-size: 22px !important; color: var(--app-fg) !important; font-weight: 600;
}}

/* ---- Metric boxes ---- */
.metric-box {{
    font-size: 24px; color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px; white-space: nowrap; overflow: hidden;
}}
.metric-third {{ font-size: 19px; padding: 12px 8px; }}
.metric-a {{ border-color: {BLUE_LINE};  color: {BLUE_LINE};  font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE}; color: {GREEN_LINE}; font-weight: 700; }}
.metric-c {{ border-color: {ORANGE_ACCENT}; color: {ORANGE_ACCENT}; font-weight: 700; }}

.result-bayes {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;  border-color: {UBU_YELLOW} !important; }}
.result-likely {{ background: {GREEN_LINE} !important; color: #ffffff !important; border-color: {GREEN_LINE} !important; }}
.result-unlikely {{ background: #d32f2f !important; color: #ffffff !important; border-color: #d32f2f !important; }}

.footer-license {{
    text-align: center; color: var(--muted-fg); font-size: 18px;
    margin-top: 50px; padding-top: 20px; border-top: 1px solid var(--metric-border);
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "P1"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "P1_A"
    if "simulaciones" not in st.session_state:
        st.session_state["simulaciones"] = {}

# =============================================================================
# 3. COMPONENTES REUTILIZABLES
# =============================================================================

def accordion_step(step_id, label):
    """Accordion con lógica de state management."""
    is_open = st.session_state.get("open_step") == step_id
    if st.button(label, use_container_width=True, key=f"btn_{step_id}"):
        st.session_state["open_step"] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(content):
    """Caja de spoiler con desenfoque blur."""
    unique_id = str(uuid.uuid4())
    html = f"""
    <input type="checkbox" id="spoiler_{unique_id}" class="spoiler-toggle">
    <label for="spoiler_{unique_id}" class="spoiler-click-wrapper">
        <div class="spoiler-box">{content}</div>
    </label>
    """
    st.markdown(html, unsafe_allow_html=True)

# =============================================================================
# 4. PÁGINAS
# =============================================================================

def render_exponential():
    """Sección I: Introducción a la distribución exponencial."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Distribución Exponencial</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La distribución exponencial modela el tiempo que transcurre entre sucesos "
            "en un proceso de Poisson: tiempos de espera, vida útil de un componente, "
            "intervalos entre llamadas a una centralita. Es la distribución continua "
            "más sencilla para tiempos hasta que algo ocurre."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Función de Densidad (PDF)"):
            st.markdown("<div class='subsection-title'>A) Función de Densidad de Probabilidad</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Una variable aleatoria continua X sigue una distribución exponencial de parámetro "
                "λ &gt; 0 si su función de densidad es:<br>"
                "<div class='formula-box'>f(x) = λ · e<sup>−λx</sup>, &nbsp; x ≥ 0</div>"
                "El parámetro <b>λ</b> (lambda) representa la <b>tasa</b> de ocurrencia del suceso "
                "(sucesos por unidad de tiempo).<br>"
                "El parámetro de escala <b>β = 1/λ</b> es el <b>tiempo medio</b> entre sucesos."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Cuanto mayor sea λ, más rápidamente decae la curva: los sucesos son muy frecuentes "
                "y los tiempos de espera cortos. Cuanto menor sea λ, la cola es más larga."
            )

        if accordion_step("P1_B", "B) Función de Distribución Acumulada (CDF)"):
            st.markdown("<div class='subsection-title'>B) Función de Distribución Acumulada</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La CDF acumula probabilidad hasta un instante t y responde a: "
                "«¿cuál es la probabilidad de que el suceso ocurra antes del tiempo t?»<br>"
                "<div class='formula-box'>F(t) = P(X ≤ t) = 1 − e<sup>−λt</sup></div>"
                "Su complementaria se llama <b>función de fiabilidad</b>:<br>"
                "<div class='formula-box'>R(t) = P(X &gt; t) = e<sup>−λt</sup></div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_C", "C) Esperanza, Varianza y Propiedad de Falta de Memoria"):
            st.markdown("<div class='subsection-title'>C) Esperanza, Varianza y Falta de Memoria</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Esperanza:</b><br>"
                "<div class='formula-box'>E[X] = 1/λ</div>"
                "<b>Varianza:</b><br>"
                "<div class='formula-box'>Var(X) = 1/λ²</div>"
                "<b>Falta de memoria:</b> es la propiedad más característica de la exponencial:<br>"
                "<div class='formula-box'>P(X &gt; s + t | X &gt; s) = P(X &gt; t)</div>"
                "Un componente que ha sobrevivido s horas 'no envejece': su probabilidad de "
                "durar t horas más es la misma que la de uno nuevo."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "La exponencial es la única distribución continua que verifica la falta de memoria. "
                "Su equivalente discreto es la geométrica."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización Interactiva: Exp(λ)</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Ajusta λ y observa cómo cambian la densidad, la CDF y las medidas de la distribución."
            "</small></div>",
            unsafe_allow_html=True
        )

        lam = st.slider("λ: tasa de fallos / ocurrencias", 0.1, 3.0, 0.5, 0.05, key="p1_lambda")

        # Métricas teóricas
        media_teo = 1.0 / lam
        var_teo = 1.0 / (lam ** 2)
        desv_teo = np.sqrt(var_teo)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>E[X] = 1/λ<br>{media_teo:.3f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Var(X) = 1/λ²<br>{var_teo:.3f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>σ = 1/λ<br>{desv_teo:.3f}</div>", unsafe_allow_html=True)

        # Selector de qué graficar
        plot_type = st.radio(
            "Mostrar:", ["PDF (Densidad)", "CDF (Acumulada)", "Fiabilidad R(t)"],
            horizontal=True, label_visibility="collapsed", key="p1_radio"
        )

        # Rango razonable: hasta 5 medias
        x_max = 5.0 / lam
        x_vals = np.linspace(0, x_max, 400)
        pdf_vals = lam * np.exp(-lam * x_vals)
        cdf_vals = 1.0 - np.exp(-lam * x_vals)
        rel_vals = np.exp(-lam * x_vals)

        if plot_type == "PDF (Densidad)":
            p = figure(
                title=f"PDF de la Exponencial · λ = {lam:.2f}",
                x_axis_label="x",
                y_axis_label="f(x)",
                width=450, height=350,
                toolbar_location=None, tools=""
            )
            p.varea(x=x_vals, y1=0, y2=pdf_vals, color=BLUE_LINE, alpha=0.25)
            p.line(x_vals, pdf_vals, line_width=3, color=BLUE_LINE)
            # Línea vertical en la media
            p.line([media_teo, media_teo], [0, lam], line_width=2, color=UBU_RED, line_dash="dashed")
            p.title.text_font_size = "16px"
            p.xaxis.axis_label_text_font_size = "14px"
            p.yaxis.axis_label_text_font_size = "14px"
            streamlit_bokeh(p)
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> El área bajo la curva "
                f"entre a y b es P(a ≤ X ≤ b). La línea roja marca la media E[X] = {media_teo:.2f}."
                "</div>",
                unsafe_allow_html=True
            )
        elif plot_type == "CDF (Acumulada)":
            p = figure(
                title=f"CDF de la Exponencial · λ = {lam:.2f}",
                x_axis_label="t",
                y_axis_label="F(t) = P(X ≤ t)",
                width=450, height=350,
                toolbar_location=None, tools=""
            )
            p.line(x_vals, cdf_vals, line_width=3, color=GREEN_LINE)
            p.title.text_font_size = "16px"
            p.xaxis.axis_label_text_font_size = "14px"
            p.yaxis.axis_label_text_font_size = "14px"
            streamlit_bokeh(p)
            st.markdown(
                f"<div class='content-box'><b>Ejemplo:</b> P(X ≤ {media_teo:.2f}) = "
                f"1 − e<sup>−1</sup> ≈ {1 - np.exp(-1):.3f}. "
                "Es decir, aproximadamente el 63 % de los sucesos ocurren antes de la media."
                "</div>",
                unsafe_allow_html=True
            )
        else:
            p = figure(
                title=f"Fiabilidad R(t) = e^(−λt) · λ = {lam:.2f}",
                x_axis_label="t",
                y_axis_label="R(t) = P(X > t)",
                width=450, height=350,
                toolbar_location=None, tools=""
            )
            p.line(x_vals, rel_vals, line_width=3, color=ORANGE_ACCENT)
            p.title.text_font_size = "16px"
            p.xaxis.axis_label_text_font_size = "14px"
            p.yaxis.axis_label_text_font_size = "14px"
            streamlit_bokeh(p)
            st.markdown(
                "<div class='content-box'><b>Fiabilidad:</b> Proporción de elementos que "
                "sobreviven pasado el instante t. Decae exponencialmente."
                "</div>",
                unsafe_allow_html=True
            )


def render_warranty():
    """Sección II: Aplicación - Garantía de productos."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) Aplicación: Garantía de Productos</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La distribución exponencial aplicada a la garantía de productos es una excelente "
            "herramienta para entender cómo se calcula el riesgo de fallo y los costes asociados. "
            "El tiempo hasta que un producto falla se modela frecuentemente con esta distribución continua."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Modelo y Parámetros"):
            st.markdown("<div class='subsection-title'>A) Modelo y Parámetros Clave</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El tiempo hasta el fallo T se modela con:<br>"
                "<div class='formula-box'>f(t) = λ · e<sup>−λt</sup></div>"
                "Donde <b>λ</b> es la <b>tasa de fallos</b> (fallos por unidad de tiempo) y "
                "el parámetro de escala <b>β = 1/λ</b> es el <b>Tiempo Medio Entre Fallos "
                "(MTBF, Mean Time Between Failures)</b>.<br><br>"
                "Los parámetros de entrada del modelo son:<br>"
                "• <b>MTBF = 1/λ</b>: vida media esperada del producto (ej. 5 años, 10 000 horas).<br>"
                "• <b>Tiempo de Garantía (t)</b>: periodo que la empresa planea cubrir (ej. 2 años).<br>"
                "• <b>Coste de Reparación/Reemplazo (C)</b>: cuánto le cuesta a la empresa cada fallo dentro de la garantía."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) Métricas de Fiabilidad y Coste"):
            st.markdown("<div class='subsection-title'>B) Métricas de Fiabilidad y Coste</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Probabilidad de fallo antes de la garantía:</b> es la CDF y representa el "
                "porcentaje de productos que reclamarán la garantía:<br>"
                "<div class='formula-box'>P(T ≤ t) = 1 − e<sup>−λt</sup></div>"
                "<b>Probabilidad de superar la garantía (Fiabilidad):</b> porcentaje de productos "
                "que sobrevivirán al periodo de garantía:<br>"
                "<div class='formula-box'>R(t) = e<sup>−λt</sup></div>"
                "<b>Coste total esperado de garantías:</b> si se venden N productos, "
                "el coste total estimado en reparaciones es:<br>"
                "<div class='formula-box'>Coste esperado = N × P(T ≤ t) × C</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_C", "C) Interpretación de la Curva"):
            st.markdown("<div class='subsection-title'>C) Interpretación de la Curva de Fallos</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El gráfico principal debe mostrar la curva de densidad exponencial. "
                "El área bajo la curva desde el tiempo 0 hasta el tiempo de garantía t "
                "representa visualmente la probabilidad de fallo, es decir, el porcentaje "
                "de pérdidas para la empresa.<br><br>"
                "Cuanto más se amplíe el periodo de garantía respecto a la vida media, "
                "mayor será el área sombreada y, por tanto, mayor el coste esperado."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Regla práctica:</b> si el periodo de garantía coincide con el MTBF, "
                "ya se ha comprometido aproximadamente el 63 % de las unidades vendidas al "
                "servicio postventa.<br><br>"
                "<b>¿De dónde sale ese 63 %?</b> Directamente de la CDF. "
                "Como λ = 1/MTBF, si hacemos t = MTBF entonces λ·t = 1, y por tanto:<br>"
                "&nbsp;&nbsp;P(T ≤ MTBF) = 1 − e<sup>−λ·MTBF</sup> = 1 − e<sup>−1</sup> "
                "= 1 − 0.3679 ≈ <b>0.6321 = 63.21 %</b>.<br><br>"
                "No es el 50 % (como uno esperaría intuitivamente) porque la exponencial es "
                "<b>asimétrica</b>: tiene una cola larga hacia la derecha. La media (MTBF) "
                "queda «tirada» por esos pocos productos muy longevos, así que la mayoría "
                "falla antes de alcanzarla. De hecho la <b>mediana</b> es "
                "(ln 2)/λ ≈ 0.693·MTBF: la mitad de las unidades ya ha fallado antes del 69 % del MTBF."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulador: Política de Garantía</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Ajusta los parámetros y observa la probabilidad de reclamación y el coste "
            "esperado en tiempo real."
            "</small></div>",
            unsafe_allow_html=True
        )

        mtbf = st.slider("MTBF: tiempo medio entre fallos (años)", 1.0, 20.0, 8.0, 0.5, key="p2_mtbf")
        t_gar = st.slider("Tiempo de garantía t (años)", 0.5, 10.0, 2.0, 0.5, key="p2_t")
        coste = st.slider("Coste unitario de reparación C (€)", 10, 500, 150, 10, key="p2_c")
        n_prod = st.slider("N: número de productos vendidos", 100, 100000, 10000, 100, key="p2_n")

        # Cálculos
        lam = 1.0 / mtbf
        p_fallo = 1.0 - np.exp(-lam * t_gar)
        fiabilidad = np.exp(-lam * t_gar)
        coste_esperado = n_prod * p_fallo * coste
        n_reclama = n_prod * p_fallo

        st.markdown(
            "<div class='content-box'><b>Resultados:</b></div>",
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"<div class='metric-box metric-a metric-third'>P(fallo antes de t)<br>"
                f"{p_fallo*100:.2f} %</div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div class='metric-box metric-b metric-third'>Fiabilidad R(t)<br>"
                f"{fiabilidad*100:.2f} %</div>",
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f"<div class='metric-box metric-c metric-third'>Nº reclamaciones esperadas<br>"
                f"{n_reclama:,.0f}</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            f"<div class='metric-box result-bayes'>Coste total esperado: {coste_esperado:,.2f} €</div>",
            unsafe_allow_html=True
        )

        # Curva de densidad con área sombreada
        x_max = max(5.0 * mtbf, 1.5 * t_gar)
        x_vals = np.linspace(0, x_max, 500)
        pdf_vals = lam * np.exp(-lam * x_vals)

        # Área sombreada dentro de la garantía
        x_gar = np.linspace(0, t_gar, 200)
        pdf_gar = lam * np.exp(-lam * x_gar)

        p = figure(
            title=f"Curva de fallos · MTBF = {mtbf:.1f} años, garantía = {t_gar:.1f} años",
            x_axis_label="Tiempo (años)",
            y_axis_label="f(t)",
            width=500, height=350,
            toolbar_location=None, tools=""
        )
        # Área sombreada de garantía (reclamaciones)
        p.varea(x=x_gar, y1=0, y2=pdf_gar, color=UBU_RED, alpha=0.35,
                legend_label="Área de reclamaciones")
        # Curva completa
        p.line(x_vals, pdf_vals, line_width=3, color=BLUE_LINE, legend_label="f(t) = λe^(−λt)")
        # Línea vertical marcando fin de garantía
        y_top = lam * 1.05
        p.line([t_gar, t_gar], [0, y_top], line_width=2, color=UBU_DARK, line_dash="dashed",
               legend_label=f"t = {t_gar} años")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "11px"
        p.title.text_font_size = "15px"
        p.xaxis.axis_label_text_font_size = "14px"
        p.yaxis.axis_label_text_font_size = "14px"
        streamlit_bokeh(p)

        st.markdown(
            f"<div class='content-box'><b>Interpretación del gráfico:</b> el área roja mide "
            f"P(T ≤ {t_gar}) = <b>{p_fallo*100:.2f} %</b>. "
            f"Con N = {n_prod:,} unidades vendidas y C = {coste} € por reparación, "
            f"la empresa debe provisionar aproximadamente "
            f"<b>{coste_esperado:,.0f} €</b> para cubrir la garantía."
            "</div>",
            unsafe_allow_html=True
        )


def render_gaussian():
    """Sección III: Introducción a la distribución gaussiana (normal)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) Distribución Gaussiana (Normal)</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La distribución normal o gaussiana es la más importante de la estadística. "
            "Aparece de forma natural siempre que un fenómeno es resultado de la suma de "
            "muchos efectos pequeños e independientes: alturas, errores de medida, "
            "ruido en un sensor, rendimientos financieros diarios."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Función de Densidad"):
            st.markdown("<div class='subsection-title'>A) Función de Densidad de Probabilidad</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Una variable X sigue una distribución normal de media μ y desviación σ, "
                "X ~ N(μ, σ²), si su densidad es:<br>"
                "<div class='formula-box'>f(x) = (1 / (σ√(2π))) · exp(−½ ((x−μ)/σ)²)</div>"
                "La curva es simétrica respecto a μ, tiene forma de campana de Gauss y sus dos parámetros son:<br>"
                "• <b>μ</b>: <b>centro</b> de la distribución (media).<br>"
                "• <b>σ</b>: <b>dispersión</b> alrededor de la media (desviación estándar)."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_B", "B) Esperanza y Varianza"):
            st.markdown("<div class='subsection-title'>B) Esperanza y Varianza</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Los propios parámetros de la distribución coinciden con sus momentos:<br>"
                "<div class='formula-box'>E[X] = μ &nbsp;&nbsp;&nbsp; Var(X) = σ²</div>"
                "Esto convierte a μ y σ en los estadísticos naturales para resumir "
                "cualquier conjunto de datos aproximadamente normal."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Visualización Interactiva: N(μ, σ²)</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Ajusta μ y σ, elige un intervalo y observa cómo cambia la probabilidad."
            "</small></div>",
            unsafe_allow_html=True
        )

        mu = st.slider("μ: media", -5.0, 5.0, 0.0, 0.5, key="p3_mu")
        sigma = st.slider("σ: desviación estándar", 0.5, 5.0, 1.0, 0.1, key="p3_sigma")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>E[X] = μ<br>{mu:.2f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Var(X) = σ²<br>{sigma**2:.2f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-c'>σ<br>{sigma:.2f}</div>", unsafe_allow_html=True)

        # Intervalo a resaltar
        st.markdown("<div class='subsection-title'>Intervalo [a, b] para P(a ≤ X ≤ b)</div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            a = st.number_input("a", value=float(mu - sigma), step=0.1, key="p3_a")
        with col_b:
            b = st.number_input("b", value=float(mu + sigma), step=0.1, key="p3_b")
        if a > b:
            a, b = b, a

        prob = norm.cdf(b, loc=mu, scale=sigma) - norm.cdf(a, loc=mu, scale=sigma)

        # Rango para el gráfico
        x_lo = mu - 4 * sigma
        x_hi = mu + 4 * sigma
        x_vals = np.linspace(x_lo, x_hi, 500)
        pdf_vals = norm.pdf(x_vals, loc=mu, scale=sigma)

        # Área del intervalo [a, b]
        x_area = np.linspace(max(a, x_lo), min(b, x_hi), 200)
        pdf_area = norm.pdf(x_area, loc=mu, scale=sigma)

        p = figure(
            title=f"PDF de N({mu:.1f}, {sigma**2:.2f}) · P({a:.2f} ≤ X ≤ {b:.2f}) = {prob:.4f}",
            x_axis_label="x",
            y_axis_label="f(x)",
            width=500, height=340,
            toolbar_location=None, tools=""
        )
        p.varea(x=x_area, y1=0, y2=pdf_area, color=BLUE_LINE, alpha=0.35)
        p.line(x_vals, pdf_vals, line_width=3, color=BLUE_LINE)
        # Media
        y_top = norm.pdf(mu, loc=mu, scale=sigma) * 1.05
        p.line([mu, mu], [0, y_top], line_width=2, color=UBU_RED, line_dash="dashed")
        p.title.text_font_size = "14px"
        p.xaxis.axis_label_text_font_size = "14px"
        p.yaxis.axis_label_text_font_size = "14px"
        streamlit_bokeh(p)

        # Verificación regla 68-95-99.7
        p_1s = norm.cdf(mu + sigma, mu, sigma) - norm.cdf(mu - sigma, mu, sigma)
        p_2s = norm.cdf(mu + 2*sigma, mu, sigma) - norm.cdf(mu - 2*sigma, mu, sigma)
        p_3s = norm.cdf(mu + 3*sigma, mu, sigma) - norm.cdf(mu - 3*sigma, mu, sigma)



def render_galton():
    """Sección IV: Máquina de Galton."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(IV) Aplicación: La Máquina de Galton</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La máquina de Galton es un tablero vertical con filas de clavijas y contenedores "
            "en la base. Ilustra visualmente cómo el azar individual da lugar a una regularidad "
            "colectiva: la distribución normal."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P4_A", "A) La Intuición: Azar Individual vs. Orden Colectivo"):
            st.markdown("<div class='subsection-title'>A) La Intuición: Azar Individual vs. Orden Colectivo</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Cuando soltamos <b>una sola bola</b>, es completamente imposible predecir "
                "en qué contenedor va a caer. En cada clavija que se encuentra, la bola toma "
                "una decisión puramente aleatoria y simétrica:<br><br>"
                "• Ir a la izquierda (I) con probabilidad p = 0.5<br>"
                "• Ir a la derecha (D) con probabilidad q = 1 − p = 0.5<br><br>"
                "Sin embargo, cuando soltamos <b>miles de bolas</b>, el caos individual "
                "desaparece y emerge una estructura geométrica perfecta: la <b>Distribución Normal</b>. "
                "¿Por qué?"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P4_B", "B) El Fundamento Matemático: Combinatoria y Binomial"):
            st.markdown("<div class='subsection-title'>B) El Fundamento Matemático: Combinatoria y Binomial</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Cada fila de clavijas representa una etapa de decisión. Si la máquina tiene "
                "n filas de clavijas, cada bola realizará exactamente n bifurcaciones antes de "
                "llegar al fondo.<br><br>"
                "Para que una bola termine en el <b>contenedor k</b> (contando de izquierda a "
                "derecha, desde 0 hasta n), debe haber tomado exactamente k decisiones de ir a "
                "la derecha (D) y n − k de ir a la izquierda (I).<br><br>"
                "<b>Los extremos (baja probabilidad):</b> Para caer en el contenedor del extremo "
                "derecho (k = n), la bola tiene que ir a la derecha todas las veces (DDDD...). "
                "Solo hay <b>1 camino</b> posible que logre esto. Su probabilidad es insignificante: "
                "0.5<sup>n</sup>.<br><br>"
                "<b>El centro (alta probabilidad):</b> Para caer en el centro, basta con que el número "
                "de desvíos a la izquierda y a la derecha esté equilibrado. El número de caminos "
                "posibles para llegar al contenedor k viene dado por el número combinatorio:<br>"
                "<div class='formula-box'>C(n,k) = n! / (k! · (n−k)!)</div>"
                "El número de caminos posibles es máximo en el centro. "
                "Por eso las columnas centrales se llenan primero. La altura de las barras "
                "sigue una <b>Distribución Binomial</b>: X ~ B(n, 0.5)."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P4_C", "C) El Teorema Central del Límite (TLC)"):
            st.markdown("<div class='subsection-title'>C) El Salto a la Computación: el TLC</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "¿Por qué este experimento de clavijas (discreto) nos sirve para modelar variables "
                "continuas como la estatura humana, los errores de medición de un sensor o el ruido "
                "en una señal digital?<br><br>"
                "Por el <b>Teorema Central del Límite</b>. Este teorema fundamental demuestra que "
                "si sumas un número grande (n → ∞) de variables aleatorias independientes e "
                "idénticamente distribuidas (como los giros I/D de cada fila), <b>la distribución "
                "de la suma se aproxima a una Distribución Normal (Gaussiana)</b>, sin importar la "
                "distribución original de esas variables.<br><br>"
                "La forma de la campana continua que emerge del histograma discreto se define "
                "mediante la función de densidad:<br>"
                "<div class='formula-box'>f(x) = (1/(σ√(2π))) · exp(−½ ((x−μ)/σ)²)</div>"
                "Donde la media (μ) se sitúa en el centro del tablero y la desviación estándar "
                "(σ) mide la dispersión (qué tan abierta o cerrada es la campana según el tamaño "
                "del tablero)."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Para una binomial B(n, 0.5): μ = n/2 y σ = √(n/4) = √n / 2. "
                "La aproximación normal N(n/2, n/4) es excelente para n ≥ 30."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulador de la Máquina de Galton</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Deja caer N bolas por un tablero de n filas y observa cómo el histograma converge "
            "a la campana de Gauss."
            "</small></div>",
            unsafe_allow_html=True
        )

        n_filas = st.slider("n: número de filas de clavijas", 4, 40, 20, 1, key="p4_n")
        n_bolas = st.slider("N: número de bolas", 100, 20000, 5000, 100, key="p4_bolas")

        # Simulación: cada bola realiza n decisiones binarias
        rng = np.random.default_rng(42)
        decisiones = rng.binomial(1, 0.5, size=(n_bolas, n_filas))  # 1 = derecha
        posiciones = decisiones.sum(axis=1)  # nº de "derechas" = contenedor final

        # Métricas
        mu_teo = n_filas * 0.5
        var_teo = n_filas * 0.25
        sigma_teo = np.sqrt(var_teo)
        mu_obs = np.mean(posiciones)
        sigma_obs = np.std(posiciones)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"<div class='metric-box metric-a metric-third'>μ teórica = n/2<br>{mu_teo:.2f}</div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div class='metric-box metric-b metric-third'>σ teórica = √(n/4)<br>{sigma_teo:.2f}</div>",
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f"<div class='metric-box metric-c metric-third'>μ observada<br>{mu_obs:.2f}</div>",
                unsafe_allow_html=True
            )

        # Histograma de resultados
        bins_edges = np.arange(0, n_filas + 2) - 0.5
        hist, edges = np.histogram(posiciones, bins=bins_edges)
        # Normalizamos a densidad para comparar con PDF normal
        anchura_bin = 1.0
        hist_dens = hist / (n_bolas * anchura_bin)

        # Curva binomial teórica
        k_vals = np.arange(0, n_filas + 1)
        pmf_bin = binom.pmf(k_vals, n_filas, 0.5)

        # Curva normal aproximada
        x_norm = np.linspace(0, n_filas, 400)
        pdf_norm = norm.pdf(x_norm, loc=mu_teo, scale=sigma_teo)

        p = figure(
            title=f"Máquina de Galton · n = {n_filas} filas, N = {n_bolas:,} bolas",
            x_axis_label="Contenedor k (nº de derechas)",
            y_axis_label="Frecuencia relativa",
            width=500, height=360,
            toolbar_location=None, tools=""
        )
        # Histograma simulado
        p.quad(top=hist_dens, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=UBU_YELLOW, line_color="white", line_width=1.5, alpha=0.75,
               legend_label="Simulación (histograma)")
        # Binomial teórica: stem plot
        p.segment(x0=k_vals, y0=0, x1=k_vals, y1=pmf_bin,
                  line_width=2, color=UBU_RED, alpha=0.9)
        p.scatter(k_vals, pmf_bin, size=8, color=UBU_RED, alpha=0.95,
                  legend_label="Binomial B(n, 0.5)")
        # Normal aproximada
        p.line(x_norm, pdf_norm, line_width=3, color=BLUE_LINE,
               legend_label=f"Normal N({mu_teo:.1f}, {var_teo:.2f})")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "11px"
        p.title.text_font_size = "15px"
        p.xaxis.axis_label_text_font_size = "14px"
        p.yaxis.axis_label_text_font_size = "14px"
        streamlit_bokeh(p)

        # Interpretación
        st.markdown(
            f"<div class='content-box'><b>Interpretación:</b> con n = {n_filas} filas la "
            f"binomial B({n_filas}, 0.5) es prácticamente indistinguible de la normal "
            f"N({mu_teo:.1f}, {var_teo:.2f}). El histograma amarillo (simulación) se "
            f"aproxima a ambas cuando N es grande. Aquí σ observada = {sigma_obs:.2f} "
            f"frente a σ teórica = {sigma_teo:.2f}."
            "</div>",
            unsafe_allow_html=True
        )

        # Probabilidades extremas: contenedores más y menos probables
        st.markdown("<div class='subsection-title'>Contenedores más y menos probables</div>", unsafe_allow_html=True)
        centro = n_filas // 2
        p_centro = binom.pmf(centro, n_filas, 0.5)
        p_extremo = binom.pmf(0, n_filas, 0.5)
        st.markdown(
            f"<div class='content-box'>"
            f"• Contenedor central (k = {centro}): P = {p_centro:.4f} → "
            f"aprox. <b>{p_centro*100:.2f} %</b> de las bolas.<br>"
            f"• Contenedor extremo (k = 0 o k = {n_filas}): "
            f"P = 0.5<sup>{n_filas}</sup> = {p_extremo:.2e}."
            "</div>",
            unsafe_allow_html=True
        )


# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Distribuciones Continuas: Exponencial y Gaussiana</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("(I) Exponencial", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col2.button("(II) Garantía de Productos", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col3.button("(III) Gaussiana", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()
    if nav_col4.button("(IV) Máquina de Galton", use_container_width=True):
        st.session_state.update({"page": "P4", "open_step": "P4_A"}); st.rerun()

    paginas = {
        "P1": render_exponential,
        "P2": render_warranty,
        "P3": render_gaussian,
        "P4": render_galton,
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
