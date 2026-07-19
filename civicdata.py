import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh
from math import comb as C

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · Orígenes de la probabilidad",
    initial_sidebar_state="collapsed",
)

# Colores de marca
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"

LIGHT_VARS = """
    --app-bg: #fbfbfb;
    --app-fg: #141414;
    --panel-left-bg: #fffdef;
    --panel-right-bg: #f0eff4;
    --box-bg: #ffffff;
    --box-fg: #1a1a1a;
    --spoiler-bg: #e8eeff;
    --spoiler-fg: #35509e;
    --metric-border: #d0d0d0;
    --muted-fg: #666666;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
"""

DARK_VARS = """
    --app-bg: #0d0d0f;
    --app-fg: #f2f2f2;
    --panel-left-bg: #17160f;
    --panel-right-bg: #0f0f16;
    --box-bg: #1e1e24;
    --box-fg: #f2f2f2;
    --spoiler-bg: #1d2440;
    --spoiler-fg: #9db4ff;
    --metric-border: #4a4a52;
    --muted-fg: #adadad;
    --shadow: 0 1px 3px rgba(0,0,0,0.45);
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
        # Sin información de Streamlit: seguir la preferencia del navegador/SO
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
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{
    padding: clamp(0.5rem, 2vw, 1.25rem) clamp(0.6rem, 3vw, 3rem) !important;
    max-width: 1600px !important;
}}

/* ---- Barra de título ---- */
.top-bar-title {{
    font-size: clamp(20px, 3.4vw, 34px); font-weight: 700; color: {UBU_RED};
    background: var(--box-bg); padding: clamp(12px, 2vw, 22px) clamp(16px, 3vw, 40px);
    border-radius: 12px; box-shadow: var(--shadow);
    display: flex; align-items: center; line-height: 1.2;
}}

/* ---- Paneles izquierdo (lectura) y derecho (interacción) ---- */
div[data-testid="column"]:has(.bg-left),
div[data-testid="column"]:has(.bg-right) {{
    padding: clamp(16px, 3vw, 40px); border-radius: 16px;
    min-height: calc(100vh - 150px);
}}
div[data-testid="column"]:has(.bg-left)  {{ background: var(--panel-left-bg); }}
div[data-testid="column"]:has(.bg-right) {{
    background: var(--panel-right-bg);
    display: flex; flex-direction: column; align-items: center;
}}

/* ---- Cajas de texto ---- */
.statement-box {{
    border: 3px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(16px, 2.5vw, 32px); background: var(--box-bg);
    font-style: italic; text-align: justify; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(16px, 2vw, 24px);
    line-height: 1.5; margin-bottom: clamp(16px, 2.5vw, 30px);
}}
.content-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(14px, 2vw, 24px); background: var(--box-bg);
    text-align: justify; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(15px, 1.9vw, 22px);
    line-height: 1.6; margin-bottom: clamp(12px, 1.6vw, 20px);
}}
.section-title {{
    font-size: clamp(18px, 2.3vw, 27px); font-weight: 700; color: var(--app-fg);
    margin: 10px 0 15px 0; border-bottom: 3px solid {UBU_YELLOW};
    padding-bottom: 10px;
}}
.spacer {{ height: clamp(16px, 3vw, 35px); }}

/* ---- Spoiler: borroso hasta que se pulsa ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-lbl {{
    cursor: pointer; display: block; position: relative;
    margin: 18px 0 22px 0;
}}
.spoiler-hint {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2; pointer-events: none;
    font-size: clamp(14px, 1.7vw, 20px); font-weight: 700;
    color: var(--spoiler-fg); letter-spacing: 0.3px;
    background: var(--box-bg); padding: 8px 18px; border-radius: 999px;
    box-shadow: var(--shadow); white-space: nowrap;
}}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400;
    font-size: clamp(15px, 1.9vw, 22px); line-height: 1.5;
    background: var(--spoiler-bg); border-left: 8px solid var(--spoiler-fg);
    padding: clamp(16px, 2vw, 28px); border-radius: 0 12px 12px 0;
    filter: blur(9px); transition: filter 0.25s ease;
}}
.spoiler-toggle:checked ~ .spoiler-box  {{ filter: none; }}
.spoiler-toggle:checked ~ .spoiler-hint {{ opacity: 0; }}
.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: clamp(17px, 2.2vw, 26px); color: var(--spoiler-fg);
}}

/* ---- Botones (navegación + acordeón) ---- */
button p {{ font-size: clamp(14px, 1.7vw, 21px) !important; line-height: 1.2 !important; }}
div[data-testid="column"] button {{
    padding-top: 14px !important; padding-bottom: 14px !important;
    white-space: normal !important; height: 100%;
}}

/* ---- Sliders: números min/max ARRIBA y grandes ---- */
div[data-testid="stSlider"] > div {{
    display: flex !important; flex-direction: column-reverse !important;
}}
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
[data-testid="stThumbValue"] {{
    display: block !important;
    font-size: clamp(18px, 2.5vw, 30px) !important; font-weight: 700 !important;
    color: var(--app-fg) !important;
}}
.stSlider [data-baseweb="slider"] {{ padding-top: 50px; padding-bottom: 5px; }}
.stSlider {{ margin-bottom: 5px; }}

/* ---- Number inputs ---- */
[data-testid="stNumberInput"] input {{
    font-size: clamp(15px, 1.9vw, 22px) !important; font-weight: 600 !important;
}}
[data-testid="stNumberInput"] label p, .stNumberInput label p {{
    font-size: clamp(14px, 1.8vw, 22px) !important; color: var(--app-fg) !important;
}}

/* ---- Cajas de resultados ---- */
.metric-box {{
    font-size: clamp(15px, 1.9vw, 22px); color: var(--app-fg); text-align: center;
    border: 3px solid var(--metric-border); border-radius: 12px;
    padding: 12px 15px; background: var(--box-bg); width: 100%;
    margin-bottom: 15px; box-shadow: var(--shadow);
}}
.metric-third {{ font-size: clamp(13px, 1.5vw, 18px); padding: 12px 8px; }}
.metric-a {{ border-color: {BLUE_LINE};  color: {BLUE_LINE};  font-weight: 700; }}
.metric-b {{ border-color: {GREEN_LINE}; color: {GREEN_LINE}; font-weight: 700; }}

.result-jugador {{ background: {UBU_YELLOW} !important; color: {UBU_DARK} !important; border-color: {UBU_YELLOW} !important; }}
.result-banca   {{ background: #d32f2f !important;      color: #ffffff !important;   border-color: #d32f2f !important; }}
.result-justo   {{ background: {GREEN_LINE} !important; color: #ffffff !important;   border-color: {GREEN_LINE} !important; }}

.footer-bar {{
    background: var(--box-bg); border: 3px solid var(--metric-border);
    border-radius: 12px; padding: clamp(14px, 2vw, 22px); text-align: center;
    font-style: italic; font-size: clamp(15px, 1.9vw, 22px); color: var(--box-fg);
    margin-top: 20px; width: 100%; box-shadow: var(--shadow);
}}
.footer-license {{
    background: var(--box-bg); border-radius: 12px;
    padding: 20px; text-align: center;
    font-size: clamp(13px, 1.6vw, 20px); color: var(--muted-fg); margin-top: 28px;
}}

/* ============ MÓVIL: reflow de una sola columna ============ */
@media (max-width: 640px) {{
    div[data-testid="column"]:has(.bg-left),
    div[data-testid="column"]:has(.bg-right) {{
        min-height: auto !important;
        margin-bottom: 14px;
    }}
    .statement-box, .content-box {{ text-align: left; }}
    .metric-third {{ white-space: normal; }}
    /* Los controles/acordeones de navegación ocupan todo el ancho */
    [data-testid="stHorizontalBlock"]:has(button) {{ flex-wrap: wrap; }}
}}
</style>
"""

# =============================================================================
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {"page": "INTRO", "open_step": "P1_1"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def accordion_step(step_id: str, title: str) -> bool:
    is_open = st.session_state["open_step"] == step_id
    if st.button(title, key=f"acc_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state["open_step"] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(html_content: str, hint: str = "🔒 Pulsa para revelar la solución"):
    st.markdown(
        f"""<label class='spoiler-lbl'>
            <input type='checkbox' class='spoiler-toggle'>
            <span class='spoiler-hint'>{hint}</span>
            <div class='spoiler-box'>{html_content}</div>
        </label>""",
        unsafe_allow_html=True,
    )

def planteamiento_header():
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Planteamiento:</div>", unsafe_allow_html=True)

def prob_a_gana(need_a: int, need_b: int, p: float) -> float:
    if need_a <= 0:
        return 1.0
    if need_b <= 0:
        return 0.0
    max_rounds = need_a + need_b - 1
    return sum(C(max_rounds, k) * (p ** k) * ((1 - p) ** (max_rounds - k))
               for k in range(need_a, max_rounds + 1))

# ---- Tematización de las gráficas (claro / oscuro / desconocido) ----

def chart_theme(dark):
    if dark is True:
        return dict(fg="#e6e6e6", grid="#3a3a42", axis="#8a8a92",
                    region_good="#1f3524", region_bad="#3a2020", region_alpha=0.6)
    if dark is False:
        return dict(fg="#2a2a2a", grid="#e2e2e2", axis="#9a9a9a",
                    region_good="#EAF3DE", region_bad="#FCEBEB", region_alpha=0.5)
    # Tema desconocido: gris neutro legible sobre fondo claro u oscuro
    return dict(fg="#8a8a8a", grid="#8a8a8a", axis="#8a8a8a",
                region_good="#7aa06a", region_bad="#c08080", region_alpha=0.28)

def style_axes(p, th, label_size="18px", tick_size="14px"):
    # Fondo transparente para integrarse con el panel en claro y oscuro
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    for axis in (p.xaxis, p.yaxis):
        axis.axis_label_text_font_size = label_size
        axis.major_label_text_font_size = tick_size
        axis.axis_label_text_color = th["fg"]
        axis.major_label_text_color = th["fg"]
        axis.axis_line_color = th["axis"]
        axis.major_tick_line_color = th["axis"]
        axis.minor_tick_line_color = None
    p.xgrid.grid_line_color = th["grid"]
    p.ygrid.grid_line_color = th["grid"]
    p.xgrid.grid_line_alpha = 0.5
    p.ygrid.grid_line_alpha = 0.5
    return p

def create_probability_curve(a_vals, pa_vals, th):
    p = figure(height=230, sizing_mode="stretch_width",
               x_axis_label="p (prob. de que A gane cada ronda)",
               y_axis_label="Prob. de ganar",
               toolbar_location=None, x_range=(0, 1), y_range=(0, 1))
    p.line(a_vals, pa_vals, line_width=5, color=BLUE_LINE)
    p.line(a_vals, 1 - pa_vals, line_width=5, color=GREEN_LINE, line_dash="dashed")
    sp = Span(location=0.5, dimension="height", line_color=th["axis"],
              line_dash="dotted", line_width=1)
    p.add_layout(sp)
    return style_axes(p, th)

def create_ev_chart(a_vals, ev_vals, th):
    top = max(ev_vals.max(), 2)
    p = figure(height=230, sizing_mode="stretch_width",
               x_axis_label="Probabilidad", y_axis_label="Esperanza",
               toolbar_location=None, x_range=(0, 0.5), y_range=(0, top))
    p.quad(top=top, bottom=1, left=0, right=0.5,
           fill_color=th["region_good"], fill_alpha=th["region_alpha"], line_color=None)
    p.quad(top=1, bottom=0, left=0, right=0.5,
           fill_color=th["region_bad"], fill_alpha=th["region_alpha"], line_color=None)
    p.line(a_vals, ev_vals, line_width=5, color=BLUE_LINE)
    sp = Span(location=1, dimension="width", line_color=th["axis"],
              line_dash="dashed", line_width=1)
    p.add_layout(sp)
    return style_axes(p, th)

def create_survival_data(mortality_rate):
    franjas = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80+"]
    edades_mid = [5, 15, 25, 35, 45, 55, 65, 75, 85]
    edades_plot = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    n_franjas = len(franjas)
    superv = [1.0]
    for _ in range(n_franjas):
        superv.append(superv[-1] * (1 - mortality_rate))
    superv = np.array(superv)
    p_muerte = superv[:-1] - superv[1:]
    ev = sum(edades_mid[k] * p_muerte[k] for k in range(n_franjas)) + 85 * superv[-1]
    return edades_plot, superv, ev

def create_survival_chart(edades_plot, superv, th):
    p = figure(height=230, sizing_mode="stretch_width",
               x_axis_label="Edad (años)", y_axis_label="Supervivencia S(t)",
               toolbar_location=None, x_range=(0, 90), y_range=(0, 1.05))
    p.varea(x=edades_plot, y1=0, y2=superv, color=BLUE_LINE, alpha=0.10)
    p.line(edades_plot, superv, line_width=5, color=BLUE_LINE)
    p.scatter(edades_plot, superv, size=12, marker="circle",
              color=BLUE_LINE, line_color="white", line_width=2)
    return style_axes(p, th)

# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>¿De dónde surge la probabilidad?</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>En Europa, el azar acompañó durante siglos a tabernas y cortes en "
            "forma de dados, cartas y apuestas, pero nadie lo consideraba un objeto digno de estudio: era "
            "cosa de la fortuna o de la providencia. Fue el ambiente del Renacimiento, con jugadores tan "
            "variopintos como el algebrista Gerolamo Cardano, quien también trató el problema de resolver "
            "las ecuaciones cúbicas y escribió el primer tratado sobre juegos de azar, el que empezó a "
            "sospechar que detrás de los dados había regularidades que podían contarse y, por tanto, "
            "calcularse.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Mucho antes, en Asia ya se había convivido de forma sofisticada con "
            "la incertidumbre. En China, el I Ching (transliterado, el libro de las mutaciones) organizaba "
            "el azar de los tallos de milenrama en 64 hexagramas, un catálogo sistemático de resultados "
            "posibles. En la India, el épico relato del Mahabharata, en donde los cinco legendarios "
            "hermanos Pándavas libran la gran batalla contra los Kauravas, describe expertos capaces de "
            "estimar cantidades enormes a partir de pequeñas muestras (contar las hojas de un árbol "
            "contando una sola rama), y los matemáticos del subcontinente desarrollaron la combinatoria, "
            "la aritmética de contar casos, siglos antes de que llegara a Europa.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Las ideas matemáticas de fondo son sorprendentemente pocas: "
            "enumerar todos los casos posibles y tratarlos como igual de verosímiles (equiprobabilidad), "
            "observar con qué frecuencia ocurre algo cuando se repite muchas veces (frecuencia relativa) y "
            "ponderar cada resultado por lo que vale (valor esperado). Sobre estos tres pilares, "
            "formalizados mucho después por Laplace y finalmente axiomatizados por Kolmogórov, se levanta "
            "toda la teoría moderna de la probabilidad, que trataremos de desentrañar aquí.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Problema de los puntos (1654)</b><br>"
            "<i>Ayuda a Pascal y Fermat a realizar el reparto de su apuesta</i><br><br>"
            "<b>II. Un fraude en la Lotería (1757)</b><br>"
            "<i>Sé un Casanova y descubre cómo saber si una lotería es injusta mediante el valor esperado</i><br><br>"
            "<b>III. Estadísticas y estado (1662)</b><br>"
            "<i>Analiza junto con el inglés John Graunt los boletines parroquiales de Londres</i>"
            "</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        # --- Controles arriba ---
        st.markdown(
            "<div class='section-title'>Pruébalo tú mismo: modifica el valor de "
            "<u>la probabilidad p</u></div>",
            unsafe_allow_html=True
        )
        p_cara = st.slider("Probabilidad p (que A gane cada ronda)", 0.0, 1.0, 0.5, 0.01,
                           key="p_pascal_slider", label_visibility="collapsed")
        c1, c2, c3 = st.columns(3)
        wins_a = c1.number_input("Victorias A", 0, 9, 8, key="wins_a")
        wins_b = c2.number_input("Victorias B", 0, 9, 7, key="wins_b")
        meta = c3.number_input("Meta", 2, 10, 10, key="meta")

        planteamiento_header()
        st.markdown(
            "<div class='statement-box'><b>El nacimiento de la probabilidad (1654)</b><br><br>"
            "Podemos encontrar los primeros pasos de la discusión entre los matemáticos franceses "
            "Blaise Pascal y Pierre de Fermat quienes trataban de cuantificar numéricamente eventos "
            "complejos. En particular, se interesaron en varios problemas sobre apuestas y desafíos.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_1", "(A) El problema de los puntos"):
            st.markdown(
                "<div class='content-box'>La formulación clásica del problema habla de dos caballeros "
                "A y B, quienes compiten apostando un tharni (la unidad monetaria que utilizaremos en "
                "este entorno, y que permite adquirir un googol de épsilones) hasta que uno de ellos "
                "obtenga 10 victorias. En cada ronda A puede ganar con una probabilidad p. Comienzan a "
                "jugar y, cuando el jugador A lleva 8 victorias y el jugador B por su parte otras 7, el "
                "rey les manda a palacio. La pregunta es, ¿cómo deben repartirse justamente el premio "
                "de su apuesta?</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_2", "(B) La discusión probabilística"):
            st.markdown(
                "<div class='content-box'>Pascal imaginó que el juego continuaba de todas formas, pero "
                "por un número máximo de rondas (igual al total de victorias que faltaban para que uno "
                "de los jugadores ganara). Así enumeró todos los escenarios posibles dándoles igual "
                "importancia (es decir, siendo equiprobables) hasta que el juego terminara. Este fue el "
                "primer uso riguroso de la probabilidad y que se vería luego reflejado en la definición "
                "(clásica) de Laplace de la probabilidad.<br><br>"
                "<b>El método (algoritmo) de Pascal:</b><br>"
                "1. Enumera todos los escenarios equiprobables hasta que uno de los dos jugadores gane "
                "(casos totales)<br>"
                "2. Cuenta cuántos casos de los anteriores favorecen a A (favorables)<br>"
                "3. El valor asociado de la probabilidad de que A gane será: casos favorables / casos "
                "totales<br><br>"
                "Observa cómo varían estos valores dependiendo de cuál es el valor de p (la probabilidad "
                "de que A gane). ¿Observas alguna relación entre la probabilidad de que gane A y la de "
                "que gane B?</div>",
                unsafe_allow_html=True
            )
            spoiler("Ambas probabilidades suman uno (son eventos complementarios: o gana A, o gana B).")

        if accordion_step("P1_3", "(C) La fórmula general"):
            st.markdown(
                "<div class='content-box'>En general, si para ganar se requieren n partidas, si A "
                "necesita a victorias para llegar a la meta y B necesita b victorias, el juego termina "
                "en un máximo de (a+b−1) rondas. El conjunto de todos los posibles eventos (espacio "
                "muestral, &Omega;) tiene 2<sup>a+b−1</sup> eventos. A gana si, en esas rondas, obtiene "
                "al menos a victorias.</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<div class='formula-box'>"
                "&#8473;(A gana) = &sum;<sub>k=a</sub><sup>a+b−1</sup> "
                "( <sup>a+b−1</sup>&frasl;<sub>k</sub> ) "
                "p<sup>k</sup> (1−p)<sup>a+b−1−k</sup>"
                "</div>"
                "Prueba a sustituir los valores del problema para comprobar que obtienes los mismos "
                "valores que en la simulación."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        need_a = meta - wins_a
        need_b = meta - wins_b
        p_a = prob_a_gana(need_a, need_b, p_cara)
        p_b = 1 - p_a

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>&#8473;(A gana) = {p_a:.4f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>&#8473;(B gana) = {p_b:.4f}</div>",
                        unsafe_allow_html=True)

        th = chart_theme(dark)
        a_vals = np.linspace(0, 1, 200)
        pa_vals = np.array([prob_a_gana(need_a, need_b, av) for av in a_vals])

        p = create_probability_curve(a_vals, pa_vals, th)
        p.scatter([p_cara], [p_a], size=16, marker="circle", color=BLUE_LINE, line_color="white", line_width=2)
        p.scatter([p_cara], [p_b], size=16, marker="circle", color=GREEN_LINE, line_color="white", line_width=2)
        streamlit_bokeh(p, use_container_width=True)

        st.markdown(
            f"<div class='footer-bar'>Con p={p_cara:.2f}, A necesita {max(need_a, 0)} victorias, "
            f"B necesita {max(need_b, 0)}. Reparto de tharni: {p_a*100:.1f}% para A, "
            f"{p_b*100:.1f}% para B.</div>",
            unsafe_allow_html=True
        )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        # --- Controles arriba ---
        st.markdown(
            "<div class='section-title'>Pruébalo tú mismo: modifica el <u>valor del premio Q</u>, "
            "y el <u>número de jugadores</u> 1/p</div>",
            unsafe_allow_html=True
        )
        n_jugadores = st.slider("Número de jugadores (1/p)", 2, 100, 10, 1,
                                key="n_players", label_visibility="collapsed")
        premio = st.slider("Premio Q (tharni)", 1, 50, 10, 1,
                           key="prize", label_visibility="collapsed")

        planteamiento_header()
        st.markdown(
            "<div class='statement-box'>Al veneciano Casanova (sí, este aventurero tuvo una faceta "
            "matemática, así como literaria, diplomática, o de libre pensador dialogando con Goethe, "
            "Mozart, Benjamin Franklin, los masones o la inquisición) también se le atribuye la "
            "invención de la lotería estatal como un evento de la alta sociedad que posteriormente se "
            "extendió a toda la población como una medida de incrementar el tesoro estatal.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_1", "(A) Un nuevo concepto: valor esperado"):
            st.markdown(
                "<div class='content-box'>El mero concepto de equiprobable del problema anterior no es "
                "suficiente para que un juego sea justo (es decir, que ninguno de sus participantes "
                "tenga ventaja sobre otro). Lo que determina si un juego conviene, perjudica, o es "
                "aleatorio es su valor esperado o esperanza, que se corresponde con el resultado que se "
                "obtendría en promedio, tras jugar un número elevado de partidas (cuántas se tratará en "
                "otro tema más avanzado).</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_2", "(B) La tabla de decisión"):
            st.markdown(
                "<div class='content-box'>Si en un juego de azar como la lotería compras un billete de "
                "1 tharni, ganando un premio Q con probabilidad p, entonces ¿cuándo te interesaría "
                "jugar al juego?</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Para calcular la esperanza se aglutinan todos los casos posibles junto con su "
                "probabilidad correspondiente:"
                "<div class='formula-box'>"
                "&#120124;[lotería] = P[ganar]&middot;Q + P[perder]&middot;0 = p&middot;Q"
                "</div>"
                "Y entonces:<br>"
                "Si &#120124;[lotería] &gt; 1 tharni: el juego es favorable al jugador.<br>"
                "Si &#120124;[lotería] = 1 tharni: el juego es matemáticamente justo.<br>"
                "Si &#120124;[lotería] &lt; 1 tharni: el juego es favorable a \"la casa\"."
            )

        if accordion_step("P2_3", "(C) En la mesa y en el juego se conoce al caballero"):
            st.markdown(
                "<div class='content-box'>Por tanto, Casanova utilizó la siguiente estrategia: encontró "
                "loterías en donde se verificara que pQ &gt; 1 (y recuerda que p, la probabilidad, es "
                "sencillamente el inverso del número de billetes). Por ejemplo, la Lotería Nacional "
                "española (1763), que todas las navidades cantan los niños de San Ildefonso, corresponde "
                "a 80000 números, cada uno con 185 series y cada billete con diez fracciones (lo que se "
                "corresponde a un décimo)... ¿cuánto tendría que ser el primer premio (asumiendo que no "
                "hubiera más) para que se tratara de un juego justo, suponiendo que cada décimo cuesta "
                "20 tharni?</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Resuélvelo numéricamente: en un juego justo p&middot;Q = precio del billete. "
                "La probabilidad de que tu número sea premiado es p = 1/80000, y cada décimo cuesta 20 "
                "tharni, luego el premio justo por décimo sería Q = 20 &middot; 80000 = 1.600.000 tharni."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        a = 1.0 / n_jugadores
        ev = a * premio
        es_justo = abs(ev - 1) < 0.001

        if es_justo:
            resultado, clase = "Juego justo", "result-justo"
        elif ev > 1:
            resultado, clase = "Favorable al jugador", "result-jugador"
        else:
            resultado, clase = "Favorable a la banca", "result-banca"

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box'>&#120124;[X] = {ev:.4f} tharni</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box {clase}'>Resultado: {resultado}</div>",
                        unsafe_allow_html=True)

        th = chart_theme(dark)
        a_vals = np.linspace(0.001, 0.5, 300)
        ev_vals = a_vals * premio

        p1 = create_ev_chart(a_vals, ev_vals, th)
        p1.scatter([a], [min(ev, ev_vals.max())], size=18, marker="circle",
                   color=BLUE_LINE, line_color="white", line_width=2)
        streamlit_bokeh(p1, use_container_width=True)

        st.markdown(
            f"<div class='footer-bar'>Con p={a:.3f} y el premio={premio} tharni: "
            f"&#120124;[X]={ev:.4f} tharni</div>",
            unsafe_allow_html=True
        )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)

        # --- Controles arriba ---
        st.markdown(
            "<div class='section-title'>Pruébalo tú mismo: modifica la "
            "<u>tasa de mortalidad M</u> de cada franja</div>",
            unsafe_allow_html=True
        )
        M = st.slider("M — tasa de mortalidad por franja", 0.01, 0.60, 0.20, 0.01,
                      format="%.2f", key="mortality_rate", label_visibility="collapsed")

        planteamiento_header()
        st.markdown(
            "<div class='statement-box'>En 1662, mientras Londres convivía con la peste, un mercero "
            "llamado John Graunt tuvo una idea revolucionaria: en lugar de especular sobre la muerte, "
            "decidió contarla. Con los boletines parroquiales de la ciudad construyó la primera tabla "
            "de mortalidad de la historia, fundando de paso la estadística demográfica.</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_1", "(A) Los boletines parroquiales de Londres"):
            st.markdown(
                "<div class='content-box'>Cada semana, las parroquias londinenses publicaban los "
                "Bills of Mortality: listados de bautizos y entierros con sus causas (peste, viruela, "
                "\"dientes\", e incluso \"planeta\": si fuiste maldecido, tuviste una mala influencia "
                "planetaria, o una afección paranormal te afectó demasiado). Nadie los usaba más que "
                "para saber si convenía huir de la ciudad. Graunt los recopiló durante décadas y "
                "descubrió regularidades asombrosas: nacen ligeramente más niños que niñas, la "
                "mortalidad urbana supera a la rural, y ciertas causas de muerte mantienen proporciones "
                "estables año tras año. ¿Qué tiene esto que ver con la probabilidad?</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Que los datos masivos convierten el azar individual (nadie sabe cuándo morirá) en "
                "regularidad colectiva: las proporciones estables son, en el fondo, probabilidades."
            )

        if accordion_step("P3_2", "(B) La definición frecuentista"):
            st.markdown(
                "<div class='content-box'>Graunt no usó nunca la palabra probabilidad, pero su método "
                "es el germen de la segunda gran definición de la misma:<br><br>"
                "1. Cuenta los casos observados en los registros (n<sub>A</sub> de un total de n)<br>"
                "2. Calcula la proporción n<sub>A</sub>/n<br>"
                "3. Asume que las proporciones pasadas predicen el futuro<br><br>"
                "¿Cómo se formaliza esta idea matemáticamente?</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Es la definición frecuentista de la probabilidad:"
                "<div class='formula-box'>&#8473;(A) = lim<sub>n&rarr;&infin;</sub> n<sub>A</sub>/n</div>"
                "La probabilidad de un suceso es el límite de su frecuencia relativa cuando el número "
                "de observaciones crece indefinidamente."
            )

        if accordion_step("P3_3", "(C) La curva de supervivencia"):
            st.markdown(
                "<div class='content-box'>La curva de supervivencia S(t) indica qué fracción de la "
                "población inicial sigue viva a la edad t. Si la tasa de mortalidad en cada franja de "
                "edad es M (igual para todas, como supuso Graunt en su tabla), la supervivencia decrece "
                "en cada etapa: S(t<sub>k+1</sub>) = S(t<sub>k</sub>)&middot;(1−M).<br><br>"
                "¿Cómo se calcula entonces la esperanza de vida?</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "La esperanza de vida es el promedio de las edades de muerte ponderado por su "
                "probabilidad:"
                "<div class='formula-box'>&#120124;[edad] = &sum;<sub>k</sub> edad<sub>k</sub> "
                "&middot; &#8473;(morir en la franja k)</div>"
                "Exactamente la misma idea de valor esperado que usó Casanova con la lotería, ahora "
                "aplicada a la vida humana. Sobre esta base nacieron los seguros de vida modernos."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)

        edades_plot, superv, ev = create_survival_data(M)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third'><b>Esperanza de vida:</b> {ev:.1f} años</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third'><b>Superv. a los 40:</b> {superv[4]*100:.1f}%</div>",
                        unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third'><b>Superv. a los 70:</b> {superv[7]*100:.1f}%</div>",
                        unsafe_allow_html=True)

        th = chart_theme(dark)
        streamlit_bokeh(create_survival_chart(edades_plot, superv, th), use_container_width=True)

        st.markdown(
            f"<div class='footer-bar'>Con tasa de mortalidad M={M:.2f} por franja: "
            f"esperanza de vida = {ev:.1f} años</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    dark = detect_dark_theme()

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Orígenes de la probabilidad</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("INTRO", "Introducción", None),
        ("P1", "(I) Otra apuesta de Pascal", "P1_1"),
        ("P2", "(II) Una lotería justa", "P2_1"),
        ("P3", "(III) Con estadística y a lo loco", "P3_1"),
    ]
    nav_cols = st.columns(4)
    for col, (page_id, label, first_step) in zip(nav_cols, nav):
        is_active = current_page == page_id
        if col.button(label, use_container_width=True,
                      type="primary" if is_active else "secondary",
                      key=f"nav_{page_id}"):
            update = {"page": page_id}
            if first_step:
                update["open_step"] = first_step
            st.session_state.update(update)
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    paginas = {
        "INTRO": render_intro,
        "P1": render_problem_1,
        "P2": render_problem_2,
        "P3": render_problem_3,
    }
    render = paginas.get(current_page, render_intro)
    if current_page == "INTRO":
        render()
    else:
        render(dark)

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
