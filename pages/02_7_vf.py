import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh
from math import comb as C

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Teorema de Bayes")

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
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 27px; color: var(--spoiler-fg);
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

.result-bayes {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;  border-color: {UBU_YELLOW} !important; }}
.result-likely {{ background: {GREEN_LINE} !important; color: #ffffff !important; border-color: {GREEN_LINE} !important; }}
.result-unlikely {{ background: #d32f2f !important; color: #ffffff !important; border-color: #d32f2f !important; }}

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
</style>
"""

# =============================================================================
# 2. FUNCIONES AUXILIARES
# =============================================================================

def init_session_state():
    """Inicializa el estado de sesión de Streamlit."""
    if "page" not in st.session_state:
        st.session_state["page"] = "INTRO"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = None

def accordion_step(key, label):
    """Acordeón que se abre/cierra con session_state."""
    is_open = st.session_state.get("open_step") == key
    if st.button(label, use_container_width=True, key=f"btn_{key}"):
        st.session_state["open_step"] = key if not is_open else None
        st.rerun()
    return is_open

def spoiler(content):
    """Muestra contenido con efecto spoiler (blur hasta clicar directamente sobre él)."""
    spoiler_id = f"sp_{abs(hash(content))}"
    st.markdown(
        f"""
        <input type="checkbox" class="spoiler-toggle" id="{spoiler_id}">
        <label for="{spoiler_id}" class="spoiler-click-wrapper">
            <div class="spoiler-box">{content}</div>
        </label>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# 3. PÁGINAS PRINCIPALES
# =============================================================================

def render_intro():
    """Página de introducción al Teorema de Bayes."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: El Teorema de Bayes</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>El Teorema de Bayes es una de las herramientas más poderosas "
            "de la probabilidad. Nos permite revisar, corregir o actualizar las probabilidades iniciales "
            "(a priori) a la luz de la ocurrencia de un nuevo suceso, obteniendo las probabilidades "
            "a posteriori.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><b>¿Quién fue Thomas Bayes?</b><br>"
            "Fue un matemático y ministro presbiteriano inglés. Su teorema, publicado póstumamente "
            "en 1763, pasó desapercibido durante más de un siglo. Hoy es el "
            "fundamento de innumerables aplicaciones: desde diagnósticos médicos hasta sistemas de "
            "inteligencia artificial.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><b>¿Por qué es revolucionario?</b><br>"
            "Antes de Bayes, la probabilidad se entendía como algo estático: la probabilidad de que "
            "caiga cara en una moneda es 50% y punto. Bayes cambió el paradigma: la probabilidad es "
            "información. Cuando adquirimos nuevos datos (la alarma suena, el test da positivo), "
            "debemos actualizar lo que creemos. Es una forma completa de razonar bajo "
            "incertidumbre.</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='subsection-title'>La fórmula de Bayes ¡FALTA PONERLA, QUE ME HA DADO PROBLEMAS Y LA HE QUITADO!</div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'><b>La trampa más común:</b><br>Confundir P(A|B) con P(B|A). Son lo contrario.</div>", unsafe_allow_html=True)
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'><b>Veamos tres aplicaciones clásicas del Teorema de Bayes:</b></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box' style='background: #f5f5f5; border-left: 5px solid " + UBU_RED + ";'>"
            "<b>(I) La alarma de incendios</b><br>"
            "Un instituto tiene una alarma de incendios 99% fiable. Cuando suena, ¿realmente hay fuego? "
            "Bayes revela una sorpresa: solo 9% de probabilidad. ¿Por qué? Porque pese a la fiabilidad de la alarma, la rareza del suceso hace que <br>"
            "predomine la idea de un fallo del sistema.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box' style='background: #f5f5f5; border-left: 5px solid " + GREEN_LINE + ";'>"
            "<b>(II) Los test de COVID-19</b><br>"
            "Un test rápido da positivo en tu casa. ¿Tienes COVID? Depende de cuánto circule el virus. "
            "En baja incidencia (como en algunas temporadas), un positivo solo significa ~15% de contagio "
            "real. Por eso exigían confirmar con PCR.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box' style='background: #f5f5f5; border-left: 5px solid " + PANTONE_2727 + ";'>"
            "<b>(III) El concurso de Monty Hall</b><br>"
            "La puerta que elegiste parece neutral (50-50 entre coche y cabra), pero cambia cuando el "
            "presentador abre otras. Monty Hall es Bayes disfrazado de concurso.</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

def render_problem_1():
    """Problema I: La alarma de incendios."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) El problema de la alarma de incendios</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Este problema es excelente para ilustrar el Teorema de Bayes. "
            "Cuando suena la alarma de incendios, tu primer instinto es: '¡Hay fuego!'. Pero Bayes dice "
            "algo muy distinto.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "(A) El escenario y los datos"):
            st.markdown("<div class='subsection-title'>A) El escenario y los datos</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Evaluamos un total de <b>10.000 días</b> en el instituto.<br><br>"
                "Definimos nuestros eventos:<br>"
                "• <b>I</b> = Hay incendio<br>"
                "• <b>A</b> = Suena la alarma<br><br>"
                "Datos sobre el incendio:<br>"
                "Un incendio en el instituto es muy raro, ocurre solo <b>1 de cada 10.000 días</b><br>"
                "Por tanto: <b>P(I) = 0.0001</b><br><br>"
                "Datos sobre la alarma:<br>"
                "1. Si hay incendio, la alarma suena el 99% de las veces → <b>P(A|I) = 0.99</b><br>"
                "2. Si no hay incendio, la alarma falla y suena por error el 1% de las veces → <b>P(A|I<sup>c</sup>) = 0.01</b>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "(B) La pregunta y Bayes"):
            st.markdown("<div class='subsection-title'>B) La pregunta y aplicación de Bayes</div>", unsafe_allow_html=True)
            st.markdown("<div class='content-box'>¿Cuál es la probabilidad de que realmente haya un incendio dado que la alarma suena?</div>", unsafe_allow_html=True)
            spoiler(
                "<b>Aplicamos el Teorema de Bayes:</b><br>"
                "<div class='formula-box'>P(I|A) = P(A|I)·P(I) / (P(A|I)·P(I) + P(A|I<sup>c</sup>)·P(I<sup>c</sup>))</div>"
                "Sustituyendo los datos base (0.99 × 0.0001) / (...) llegamos a un <b>0.98%</b> de probabilidad real."
            )

        if accordion_step("P1_C", "(C) Análisis: la moraleja"):
            st.markdown("<div class='subsection-title'>C) Análisis: la moraleja</div>", unsafe_allow_html=True)
            st.markdown("<div class='content-box'>Los falsos positivos abruman a los verdaderos porque el evento inicial (incendio) es extremadamente raro.</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'><b>⚙️ Simulación Interactiva:</b></div>", unsafe_allow_html=True)

        # Controles interactivos
        total_dias = 10000
        dias_incendio = st.number_input("Número de días con incendio (de 10.000)", min_value=1, max_value=500, value=1, step=1)
        sensibilidad_alarma = st.slider("Fiabilidad de la alarma si hay incendio P(A|I)", 0.80, 1.00, 0.99, 0.01)
        falso_positivo_alarma = st.slider("Fallo de la alarma si NO hay incendio P(A|Iᶜ)", 0.00, 0.20, 0.01, 0.01)

        p_incendio_priori = dias_incendio / total_dias
        p_incendio_posteriori = (sensibilidad_alarma * p_incendio_priori) / \
                                (sensibilidad_alarma * p_incendio_priori + falso_positivo_alarma * (1 - p_incendio_priori))

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box'><b>P(I) Inicial:</b><br>{p_incendio_priori*100:.3f}%</div>", unsafe_allow_html=True)
        with m2:
            clase_res = "result-likely" if p_incendio_posteriori > 0.5 else "result-unlikely"
            st.markdown(f"<div class='metric-box {clase_res}'><b>P(I|A) Real Bayes:</b><br>{p_incendio_posteriori*100:.2f}%</div>", unsafe_allow_html=True)

        # Cálculos de contingencia reactivos
        dias_no_incendio = total_dias - dias_incendio
        v_positivos = dias_incendio * sensibilidad_alarma
        f_positivos = dias_no_incendio * falso_positivo_alarma
        total_alertas = v_positivos + f_positivos

        st.markdown(
            f"<div class='content-box'><b>Frecuencias para {total_dias} días:</b><br><br>"
            f"• Días reales de Incendio: <b>{dias_incendio}</b><br>"
            f"&nbsp;&nbsp;→ Alarma suena con éxito: {v_positivos:.2f} días<br>"
            f"• Días sin Incendio: <b>{dias_no_incendio}</b><br>"
            f"&nbsp;&nbsp;→ Alarma suena por error: {f_positivos:.2f} días<br><br>"
            f"<b>Total de alertas sonoras: {total_alertas:.2f}</b><br>"
            f"Proporción de incendios reales: {v_positivos:.2f} / {total_alertas:.2f}</div>",
            unsafe_allow_html=True
        )

def render_problem_2():
    """Problema II: Los test de COVID-19."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) El problema de los test de COVID-19</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Este ejemplo conecta el teorema directamente con la experiencia "
            "real que vivimos durante la pandemia con los test rápidos de antígenos.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "(A) El contexto epidemiológico"):
            st.markdown("<div class='subsection-title'>A) El contexto epidemiológico</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Imagina un aula con 1.000 alumnos en un momento de baja incidencia (1% de positivos).<br>"
                "• Sensibilidad: <b>P(+|C) = 0.90</b><br>"
                "• Falsos positivos: <b>P(+|S) = 0.05</b>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "(B) El test da positivo"):
            st.markdown("<div class='subsection-title'>B) El test da positivo: ¿qué significa?</div>", unsafe_allow_html=True)
            spoiler("De las 59 personas que darían positivo bajo las condiciones estándar, solo 9 tienen el virus: <b>P(C|+) ≈ 15.25%</b>")

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'><b>⚙️ Simulación Epidemiológica:</b></div>", unsafe_allow_html=True)

        # Selección interactiva de Prevalencia usando un selectbox semántico
        incidencia_tipo = st.selectbox(
            "Incidencia del virus en la población",
            ["Baja (1% de contagiados)", "Media (10% de contagiados)", "Alta (30% de contagiados)", "Ola Crítica (50% de contagiados)"]
        )
        
        # Mapeo semántico del selectbox
        incidencia_map = {
            "Baja (1% de contagiados)": 0.01,
            "Media (10% de contagiados)": 0.10,
            "Alta (30% de contagiados)": 0.30,
            "Ola Crítica (50% de contagiados)": 0.50
        }
        prevalencia = incidencia_map[incidencia_tipo]

        sensibilidad = st.slider("Sensibilidad del test P(+|C)", 0.70, 1.00, 0.90, 0.05)
        falsos_pos_rate = st.slider("Tasa de Falsos Positivos P(+|S)", 0.01, 0.15, 0.05, 0.01)

        total_poblacion = 1000
        contagiados = total_poblacion * prevalencia
        sanos = total_poblacion - contagiados

        positivos_reales = contagiados * sensibilidad
        falsos_positivos = sanos * falsos_pos_rate
        total_positivos = positivos_reales + falsos_positivos

        p_contagio_posterior = positivos_reales / total_positivos if total_positivos > 0 else 0

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box'><b>Infección Inicial:</b><br>{prevalencia*100:.0f}%</div>", unsafe_allow_html=True)
        with m2:
            clase_res = "result-likely" if p_contagio_posterior > 0.5 else "result-unlikely"
            st.markdown(f"<div class='metric-box {clase_res}'><b>P(C|+) Confianza:</b><br>{p_contagio_posterior*100:.2f}%</div>", unsafe_allow_html=True)

        st.markdown(
            f"<div class='content-box'>"
            f"<table style='width:100%; border-collapse: collapse; text-align:center;'>"
            f"<tr style='border-bottom: 2px solid {UBU_RED}; font-weight:600;'><td>Resultado</td><td>Enfermos</td><td>Sanos</td><td>Total</td></tr>"
            f"<tr style='border-bottom: 1px solid #ccc;'><td>Test (+)</td><td>{positivos_reales:.0f}</td><td>{falsos_positivos:.0f}</td><td><b>{total_positivos:.0f}</b></td></tr>"
            f"<tr><td>Test (-)</td><td>{contagiados - positivos_reales:.0f}</td><td>{sanos - falsos_positivos:.0f}</td><td><b>{total_poblacion - total_positivos:.0f}</b></td></tr>"
            f"</table></div>",
            unsafe_allow_html=True
        )

def render_problem_3():
    """Problema III: El concurso de Monty Hall."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) El concurso de Monty Hall</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>Sea r ∈ [0,1]. En un concurso hay N = 3 + 7r puertas, "
            "luego N ∈ {3, 4, ..., 10}. Detrás de una de ellas hay un coche y detrás del resto hay cabras.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "(A) Probabilidad inicial"):
            st.markdown("<div class='subsection-title'>A) ¿Cuál es la probabilidad inicial de haber elegido el coche?</div>", unsafe_allow_html=True)
            spoiler("<b>P(Coche al inicio) = 1/N</b>")

        if accordion_step("P3_B", "(B) Probabilidad si cambias de puerta"):
            st.markdown("<div class='subsection-title'>B) Probabilidad de ganar si decides cambiar a la única puerta alternativa</div>", unsafe_allow_html=True)
            spoiler("<b>P(Ganar cambiando) = (N-1)/N</b>")

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'><b>Controla el número de puertas (3 a 10):</b></div>", unsafe_allow_html=True)

        N = st.slider("N — número de puertas", 3, 10, 3, 1, label_visibility="collapsed")
        p_ganar_cambiar = (N - 1) / N
        p_ganar_no_cambiar = 1 / N

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box result-likely'><b>P(ganar | cambias):</b><br>{p_ganar_cambiar*100:.1f}%</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box result-unlikely'><b>P(ganar | no cambias):</b><br>{p_ganar_no_cambiar*100:.1f}%</div>", unsafe_allow_html=True)

# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA, Teorema de Bayes</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO"}); st.rerun()
    if nav_col2.button("(I) Alarma de incendios", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) Test de COVID", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Monty Hall", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_problem_1,
        "P2": render_problem_2,
        "P3": render_problem_3,
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