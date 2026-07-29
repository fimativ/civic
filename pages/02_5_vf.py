import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh
from math import comb as C

# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Definición y origen de la probabilidad condicionada")

# Colores
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
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
.spacer {{ height: 35px; }}

/* ---- Spoiler: borroso en azul hasta que se pulsa ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-lbl {{ cursor: pointer; display: block; margin-top: 20px; margin-bottom: 25px; }}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400; font-size: 25px; line-height: 1.5;
    background: var(--spoiler-bg); border-left: 10px solid var(--spoiler-fg);
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(15px); transition: filter 0.3s;
}}
.spoiler-toggle:checked + .spoiler-box {{ filter: none; color: var(--box-fg) !important; }}

.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: 27px; color: var(--spoiler-fg);
    display: flex; align-items: center; justify-content: center;
}}

/* Formateo de fracciones en HTML puro */
.fraction {{
    display: inline-flex;
    flex-direction: column;
    vertical-align: middle;
    text-align: center;
    line-height: 1.2;
    margin-left: 8px;
    margin-right: 8px;
}}
.numerator {{
    border-bottom: 2px solid var(--spoiler-fg);
    padding-bottom: 2px;
}}
.denominator {{
    padding-top: 2px;
}}

button p {{ font-size: 25px !important; }}
div[data-testid="column"] button {{ padding-top: 15px !important; padding-bottom: 15px !important; }}

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
# ESTADO DE LA SESIÓN Y FUNCIONES AUXILIARES
# =============================================================================

def init_session_state():
    defaults = {"page": "INTRO", "open_step": "P1_A"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def planteamiento_header():
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Planteamiento:</div>", unsafe_allow_html=True)

def accordion_step(step_id: str, title: str) -> bool:
    """Implementación de acordeón idéntica a 01_1_vs.py"""
    is_open = st.session_state["open_step"] == step_id
    if st.button(title, key=f"acc_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state["open_step"] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(html_content: str):
    """Implementación limpia del spoiler interactivo usando el CSS de 01_1_vs.py"""
    st.markdown(
        f"""<label class='spoiler-lbl'>
            <input type='checkbox' class='spoiler-toggle'>
            <div class='spoiler-box'>{html_content}</div>
        </label>""",
        unsafe_allow_html=True,
    )

# =============================================================================
# INTRO
# =============================================================================

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>Probabilidad Condicionada</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'La probabilidad condicionada es la posibilidad de que ocurra un evento A, sabiendo que ya ha '
            'sucedido otro evento B. Su origen se remonta al siglo XVIII, cuando el matemático Thomas Bayes '
            'formuló su conocido teorema para calcular probabilidades inversas, y fue formalizado poco después '
            'por Pierre-Simon Laplace.'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            '<div class="content-box"><b>Definición formal:</b> Dado un espacio de probabilidad '
            '(&Omega;, <b>&Ascr;</b>, <i>P</i>) y un suceso <i>B</i> tal que <i>P</i>(<i>B</i>) &gt; 0, '
            'definimos la probabilidad condicionada de <i>A</i> dado <i>B</i> como:'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>"
            "<i>P</i>(<i>A</i>|<i>B</i>) ="
            "<div class='fraction'>"
            "<span class='numerator'><i>P</i>(<i>A</i> &cap; <i>B</i>)</span>"
            "<span class='denominator'><i>P</i>(<i>B</i>)</span>"
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>La información previa altera por completo la probabilidad de un suceso.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA 1: LINDA LA CAJERA
# =============================================================================

def render_problem_1():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'El problema de "Linda la cajera" fue diseñado por los psicólogos Daniel Kahneman y Amos Tversky '
            'en 1983. Es uno de los recursos más atractivos de la psicología cognitiva y la didáctica de las '
            'matemáticas para introducir la probabilidad condicionada y la probabilidad de la intersección.'
            '</div>',
            unsafe_allow_html=True
        )
        
        # ===== APARTADO A =====
        if accordion_step("P1_A", "(A) Conocer a Linda"):
            st.markdown(
                '<div class="content-box">'
                'Linda tiene 31 años, es mujer soltera, sincera y brillante. Se especializó en Filosofía. '
                'Como estudiante, estaba profundamente preocupada por los problemas de discriminación y justicia.'
                '<br><br>'
                '<b>¿Cuál de estas opciones te parece más probable?</b>'
                '<br>• Opción A: Linda es cajera de un banco.'
                '<br>• Opción B: Linda es cajera de un banco y activista del movimiento feminista.'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                '<b>⚠️ Resultado experimental:</b> En los experimentos originales, '
                'aproximadamente el 85% de las personas eligieron la opción B. Pero... ¿es eso matemáticamente posible?'
            )
        
        # ===== APARTADO B =====
        if accordion_step("P1_B", "(B) El error: la falacia de la conjunción"):
            st.markdown(
                '<div class="content-box">'
                'La opción B es matemáticamente <b>imposible</b> que sea más probable que la opción A.<br><br>'
                'Recurrimos a un diagrama de Venn:'
                '<br>• C = todas las cajeras de banco del mundo'
                '<br>• F = todas las personas feministas'
                '<br>• C &cap; F = cajeras de banco que además son feministas'
                '<br><br>'
                'Visualmente: el conjunto de cajeras que son feministas es un <b>subconjunto</b> del total de '
                'cajeras. Por tanto: <i>P</i>(<i>C</i> &cap; <i>F</i>) &le; <i>P</i>(<i>C</i>)'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                'A este error de razonamiento se le conoce como la <b>falacia de la conjunción</b>: '
                'la probabilidad de dos eventos simultáneos nunca puede ser mayor que la probabilidad de '
                'uno solo de ellos.'
            )
        
        # ===== APARTADO C =====
        if accordion_step("P1_C", "(C) Por qué nos engaña el cerebro"):
            st.markdown(
                '<div class="content-box">'
                'El cerebro no es bueno calculando probabilidades conjuntas <i>P</i>(<i>C</i> &cap; <i>F</i>), sino que tiende a '
                'evaluar la probabilidad condicionada sin darse cuenta.'
                '<br><br>'
                'Al leer la descripción de Linda (llamémosla suceso L):'
                '<br>• Estimamos <i>P</i>(<i>F</i>|<i>L</i>) &asymp; 0.9 —> es muy probable que sea feminista dado su perfil.'
                '<br>• Estimamos <i>P</i>(<i>C</i>|<i>L</i>) &asymp; 0.1 —> es poco probable que sea cajera dado su perfil.'
                '<br><br>'
                'Pero al evaluar la opción B, nuestro cerebro está intentando calcular <i>P</i>(<i>F</i>|<i>C</i>): '
                '¿cuál es la probabilidad de que sea feminista <b>sabiendo que es</b> cajera de banco?'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                'Al escribir <i>P</i>(<i>F</i>|<i>C</i>) = <i>P</i>(<i>C</i> &cap; <i>F</i>) / <i>P</i>(<i>C</i>), y despejar '
                '<i>P</i>(<i>C</i> &cap; <i>F</i>) '
                'vemos que como <i>P</i>(<i>F</i>|<i>C</i>) es una probabilidad (número entre 0 y 1), al multiplicarla por <i>P</i>(<i>C</i>) '
                'el resultado siempre será igual o menor que <i>P</i>(<i>C</i>).<br><br>'
                '<b>Moraleja:</b> La información previa (descripción de Linda) altera radicalmente cómo '
                'nuestro cerebro estima las probabilidades, llevándonos a confundir probabilidades condicionadas '
                'con probabilidades de intersecciones.'
            )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>El 85% de los sujetos elegía B, pero <i>P</i>(<i>A</i> &cap; <i>B</i>) &le; <i>P</i>(<i>A</i>) siempre.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA 2: CAZA DE GAMUSINOS
# =============================================================================

def render_problem_2():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'El ejemplo de la caza de los gamusinos, ese animal imaginario con el que tradicionalmente se '
            'gasta una broma en España a los excursionistas novatos, mandándolos de noche al bosque con un saco, '
            'es excelente para explicar la probabilidad condicionada de forma humorística, rápida y muy intuitiva.'
            '</div>',
            unsafe_allow_html=True
        )
        
        # ===== APARTADO A =====
        if accordion_step("P2_A", "(A) La escena"):
            st.markdown(
                '<div class="content-box">'
                'Imagina que llevas de acampada a un grupo de 10 amigos al bosque por la noche.'
                '<br><br>'
                '• 6 son veteranos (V): ya conocen la broma del gamusino.'
                '<br>• 4 son novatos (N): nunca han oído hablar de ellos y se creen la historia.'
                '<br><br>'
                'A todos les repartes un saco y los dejas esperando en la oscuridad.'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                "Definimos el suceso: <b>C = el amigo cree que va a cazar un gamusino </b>"
            )
        
        # ===== APARTADO B =====
        if accordion_step("P2_B", "(B) Las probabilidades"):
            st.markdown(
                '<div class="content-box">'
                'Si eliges a un amigo al azar en mitad de la noche, la probabilidad de que de verdad crea que '
                'va a cazar algo (<i>P</i>(<i>C</i>)) está totalmente condicionada a la información previa que posee:'
                '<br><br>'
                '• Sabiendo que es veterano (V): <i>P</i>(<i>C</i>|<i>V</i>) = ?'
                '<br>• Sabiendo que es novato (N): <i>P</i>(<i>C</i>|<i>N</i>) = ?'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                "• <i>P</i>(<i>C</i>|<i>V</i>) = 0 porque sabe que es una broma."
                "<br>• <i>P</i>(<i>C</i>|<i>N</i>) = 1 "
            )
        
        # ===== APARTADO C =====
        if accordion_step("P2_C", "(C) La lección"):
            st.markdown(
                '<div class="content-box">'
                'La probabilidad del suceso <b>creer en la caza</b> (C) cambia radicalmente de 0 a 1 dependiendo '
                'de la condición previa del sujeto (conocer o no la broma).'
                '<br><br>'
                '¿Qué nos enseña esto sobre la probabilidad condicionada?'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Moraleja:</b> Así es como funciona la probabilidad condicionada: "
                "<b>la información previa altera por completo la probabilidad de un suceso.</b> "
                "Sin conocimiento previo, la probabilidad es máxima (1). Con conocimiento, es nula."
            )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>La misma situación tiene probabilidades completamente diferentes según la información previa.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA 3: FALSO POSITIVO EN PRUEBAS MEDICAS
# =============================================================================

def render_problem_3():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'Este es el ejemplo clásico de medicina. Sirve para desmontar una idea errónea muy común en '
            'probabilidad: <b>confundir <i>P</i>(<i>A</i>|<i>B</i>) con <i>P</i>(<i>B</i>|<i>A</i>).</b>'
            '</div>',
            unsafe_allow_html=True
        )
        
        # ===== APARTADO A =====
        if accordion_step("P3_A", "(A) El escenario"):
            st.markdown(
                '<div class="content-box">'
                'Imagina una enfermedad muy rara que solo tiene 1 de cada 1000 personas.'
                '<br><br>'
                '• E = 1 persona está realmente enferma'
                '<br>• S = 999 personas están sanas'
                '<br><br>'
                'El test es excelente: tiene un 95% de fiabilidad (solo falla el 5% de las veces dando un '
                'falso positivo).'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                '• El único enfermo da positivo (+)'
                '<br>• De los 999 sanos, el 5% da positivo por error (falso positivo) &asymp; 50 personas'
                '<br><br>'
                '<b>Total de positivos en el laboratorio: 51</b>'
            )
        
        # ===== APARTADO B =====
        if accordion_step("P3_B", "(B) La pregunta tramposa"):
            st.markdown(
                '<div class="content-box">'
                'A primera vista, es muy fácil confundir la precisión del test con la probabilidad real de tener la enfermedad tras obtener un positivo. <br>'
                ' ¿Significa un positivo que tenemos un 95% de probabilidad de estar enfermos?'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                "<b>¡FALSO! </b>"
            )
        
        # ===== APARTADO C =====
        if accordion_step("P3_C", "(C) La respuesta (y por qué es contraintuitiva)"):
            st.markdown(
                '<div class="content-box">'
                'La probabilidad de estar enfermo sabiendo que has dado positivo es:'
                '<br><br>'
                '<i>P</i>(<i>E</i>|+) = (personas realmente enfermas que dan +) / (total de positivos)'
                '<br><i>P</i>(<i>E</i>|+) = 1 / 51 &asymp; <b>2%</b>'
                '<br><br>'
                'Mientras que la probabilidad de dar positivo si sabes que estás enfermo es:'
                '<br><i>P</i>(+|<i>E</i>) = 1 (el test acierta en el enfermo)'
                '<br><br>'
                'Entonces: <i>P</i>(<i>E</i>|+) &ne; <i>P</i>(+|<i>E</i>) '
                '</div>',
                unsafe_allow_html=True
            )
            spoiler(
                '<b>Moraleja:</b> Aunque la probabilidad de dar positivo por error (siendo sano) es solo del 5%, '
                'si tu test da positivo, la probabilidad de estar enfermo es de apenas el 2%.'
                '<br><br>'
                '¿Por qué? Porque la enfermedad de partida es <b>extremadamente rara</b>. Hay muchas más personas '
                'sanas que enfermas, así que los falsos positivos (50 personas) superan ampliamente al verdadero '
                'positivo (1 persona).'
                '<br><br>'
                'Este es el poder de la probabilidad condicionada: <b>cambia radicalmente nuestras conclusiones '
                'cuando la información previa sobre la prevalencia es incluida correctamente.</b>'
            )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>Con 95% de fiabilidad, si das positivo solo tienes 2% de probabilidad de estar enfermo.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown("<div class='top-bar-title'>C1VIC D4TA, Definición y origen de la probabilidad condicionada</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO"}); st.rerun()
    if nav_col2.button("(I) Linda la cajera", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) Caza de gamusinos", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Falso positivo", use_container_width=True):
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