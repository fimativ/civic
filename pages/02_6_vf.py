import streamlit as st
import numpy as np
from bokeh.plotting import figure
from bokeh.models import Span
from streamlit_bokeh import streamlit_bokeh
from math import comb as C
import hashlib

# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Sucesos Independientes y Teorema Probabilidad Total")

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

/* ---- Spoiler interactivo directo ---- */
.spoiler-toggle {{ display: none; }}
.spoiler-lbl {{ display: block; cursor: pointer; margin: 20px 0; }}
.spoiler-box {{
    color: var(--spoiler-fg); font-weight: 400; font-size: 25px; line-height: 1.5;
    background: var(--spoiler-bg); border-left: 10px solid var(--spoiler-fg);
    padding: 25px 35px; border-radius: 0 12px 12px 0;
    filter: blur(12px); transition: filter 0.3s, color 0.3s;
    user-select: none;
}}
.spoiler-toggle:checked ~ .spoiler-lbl .spoiler-box {{
    filter: none;
    color: var(--box-fg) !important;
    user-select: text;
}}

.formula-box {{
    border: 3px solid var(--spoiler-fg); border-radius: 12px;
    background: var(--box-bg); padding: 15px 20px; margin: 15px 0;
    text-align: center; font-family: 'Open Sans', Arial, sans-serif;
    font-size: 27px; color: var(--spoiler-fg);
    display: flex; align-items: center; justify-content: center;
    flex-wrap: wrap;
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
</style>
"""

def init_session_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "INTRO"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = ""

def planteamiento_header():
    st.markdown(
        '<div style="font-size: 26px; font-weight: 600; color: var(--app-fg); '
        'margin: 10px 0 20px 0;"><u>Planteamiento</u></div>',
        unsafe_allow_html=True
    )

def accordion_step(step_id, label):
    if st.session_state.get("open_step") == step_id:
        if st.button(f"▼ {label}", use_container_width=True, key=f"btn_{step_id}"):
            st.session_state["open_step"] = ""
            st.rerun()
        return True
    else:
        if st.button(f"▶ {label}", use_container_width=True, key=f"btn_{step_id}"):
            st.session_state["open_step"] = step_id
            st.rerun()
        return False

def spoiler(content_html):
    stable_key = hashlib.md5(content_html.encode('utf-8')).hexdigest()[:8]
    st.markdown(f"""
    <div style='margin: 20px 0;'>
        <input type='checkbox' id='spoiler_{stable_key}' class='spoiler-toggle'>
        <label for='spoiler_{stable_key}' class='spoiler-lbl' title='Haz clic para revelar'>
            <div class='spoiler-box'>{content_html}</div>
        </label>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# INTRO
# =============================================================================

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        st.markdown(
            "<div class='section-title'>Introducción</div>",
            unsafe_allow_html=True
        )
        
        planteamiento_header()
        
        # Sucesos independientes
        st.markdown(
            '<div class="statement-box">'
            '<b>Sucesos independientes:</b> Dos sucesos <i>A</i> y <i>B</i> son independientes '
            'si y solo si la probabilidad de su intersección es igual al producto de sus '
            'probabilidades individuales:'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>"
            "<i>P</i>(<i>A</i> &cap; <i>B</i>) = <i>P</i>(<i>A</i>) &middot; <i>P</i>(<i>B</i>)"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

        # Teorema de la probabilidad total (NUEVA SECCIÓN AÑADIDA)
        st.markdown(
            '<div class="statement-box">'
            '<b>Teorema de la probabilidad total:</b> Si {<i>B</i><sub>1</sub>, <i>B</i><sub>2</sub>, ...} es una partición de &Omega; '
            'y <i>P</i>(<i>B</i><sub><i>i</i></sub>) &gt; 0, entonces para cualquier suceso <i>A</i>:'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<div class='formula-box'>"
            "<i>P</i>(<i>A</i>) = &sum;<sub><i>i</i></sub> <i>P</i>(<i>A</i>|<i>B</i><sub><i>i</i></sub>) <i>P</i>(<i>B</i><sub><i>i</i></sub>)"
            "</div>",
            unsafe_allow_html=True
        )
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>La independencia simplifica enormemente el cálculo de probabilidades conjuntas en problemas complejos, mientras que la probabilidad total nos permite descomponer un problema global en ramas condicionales más sencillas.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA I: DEMOSTRACIÓN (021)
# =============================================================================

def render_problem_1():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        
        # ===== APARTADO A =====
        if accordion_step("P1_A", "(A) Enunciado del problema"):
            st.markdown(
                '<div class="content-box">'
                'En un espacio probabilístico (&Omega;, <b>&Ascr;</b>, <i>P</i>), sean <i>A</i>, <i>B</i> y <i>C</i> '
                'tres sucesos con probabilidad estrictamente positiva. Si se cumple la siguiente igualdad:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i>|<i>B</i>) = <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i>) <i>P</i>(<i>C</i>) + <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i><sup>c</sup>) <i>P</i>(<i>C</i><sup>c</sup>)"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="content-box">'
                'y además se sabe que <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i>) &ne; <i>P</i>(<i>A</i>|<i>B</i>), '
                'demuestra que <i>B</i> y <i>C</i> deben ser necesariamente independientes.'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler('💡 <b>Pista para arrancar:</b> Comienza aplicando la definición de probabilidad condicionada a las fracciones del miembro de la derecha.')
        
        # ===== PASO 1 =====
        if accordion_step("P1_B1", "(B) Paso 1: Definición condicional"):
            st.markdown(
                '<div class="content-box">'
                '<b>Paso 1: Desarrollar el miembro derecho</b><br>'
                'Aplicamos la definición de probabilidad condicionada <i>P</i>(<i>X</i>|<i>Y</i>) = <i>P</i>(<i>X</i> &cap; <i>Y</i>) / <i>P</i>(<i>Y</i>) '
                'a cada término del miembro derecho:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "(1) &nbsp; <i>P</i>(<i>A</i>|<i>B</i>) ="
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i>)</span>"
                "<span class='denominator'><i>P</i>(<i>B</i> &cap; <i>C</i>)</span>"
                "</div>"
                "&middot; <i>P</i>(<i>C</i>) +"
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i><sup>c</sup>)</span>"
                "<span class='denominator'><i>P</i>(<i>B</i> &cap; <i>C</i><sup>c</sup>)</span>"
                "</div>"
                "&middot; <i>P</i>(<i>C</i><sup>c</sup>)"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('🔍 <b>¿Por qué hacemos esto?</b> Al expandir las condicionales, logramos que aparezca la intersección triple de los tres sucesos en los numeradores, permitiéndonos trabajar a nivel de intersecciones básicas.')
        
        # ===== PASO 2 =====
        if accordion_step("P1_B2", "(B) Paso 2: Desarrollar miembro izquierdo"):
            st.markdown(
                '<div class="content-box">'
                '<b>Paso 2: Desarrollar el miembro izquierdo</b><br>'
                'Por otro lado, escribimos el término izquierdo como una fracción simple y expandimos la intersección '
                'usando el teorema de la probabilidad total sobre el suceso <i>C</i>:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "(2) &nbsp; <i>P</i>(<i>A</i>|<i>B</i>) ="
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i>) + <i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i><sup>c</sup>)</span>"
                "<span class='denominator'><i>P</i>(<i>B</i>)</span>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('⚖️ <b>Dos caminos, un mismo valor:</b> Observa que tanto la ecuación (1) como la (2) valen exactamente lo mismo: <i>P</i>(<i>A</i>|<i>B</i>). El siguiente paso lógico será igualarlas.')
        
        # ===== PASO 3 =====
        if accordion_step("P1_B3", "(B) Paso 3: Igualación y agrupación"):
            st.markdown(
                '<div class="content-box">'
                '<b>Paso 3: Igualar las expresiones y agrupar por suceso</b><br>'
                'Igualamos las ecuaciones (1) y (2), y agrupamos en un miembro los términos que multiplican a <i>C</i>, '
                'y en el otro miembro los términos de <i>C</i><sup>c</sup>:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i>)"
                "&Big[ "
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'><i>P</i>(<i>B</i>)</span>"
                "</div>"
                "&minus;"
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>C</i>)</span>"
                "<span class='denominator'><i>P</i>(<i>B</i> &cap; <i>C</i>)</span>"
                "</div>"
                "&Big]"
                "&nbsp;=&nbsp;"
                "<i>P</i>(<i>A</i> &cap; <i>B</i> &cap; <i>C</i><sup>c</sup>)"
                "&Big[ "
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>C</i><sup>c</sup>)</span>"
                "<span class='denominator'><i>P</i>(<i>B</i> &cap; <i>C</i><sup>c</sup>)</span>"
                "</div>"
                "&minus;"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'><i>P</i>(<i>B</i>)</span>"
                "</div>"
                "&Big]"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('🛠️  <b>Estrategia matemática:</b> Resolver los corchetes buscando el común denominador nos va a revelar una estructura común en los numeradores de ambos lados.')
        
        # ===== PASO 4 =====
        if accordion_step("P1_B4", "(B) Paso 4: Simplificación a producto nulo"):
            st.markdown(
                '<div class="content-box">'
                '<b>Paso 4: Obtener común denominador y factorizar</b><br>'
                'Operando las fracciones de los corchetes, simplificando denominadores y extrayendo factor común '
                'llegamos a la siguiente expresión producto nulo:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "[ <i>P</i>(<i>B</i> &cap; <i>C</i>) &minus; <i>P</i>(<i>B</i>)<i>P</i>(<i>C</i>) ] &middot; [ <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i>) &minus; <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i><sup>c</sup>) ] = 0"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('🎯 <b>La regla del producto cero:</b> Si un producto es igual a cero, necesariamente uno de los dos bloques entre corchetes debe valer cero. ¡Analicemos cuál!')
        
        # ===== APARTADO C =====
        if accordion_step("P1_C", "(C) Paso 5: Conclusión analítica"):
            st.markdown(
                '<div class="content-box">'
                '<b>Análisis final de los factores:</b><br><br>'
                '1) Si el segundo corchete fuera cero, significaría que:<br>'
                '&emsp;<i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i>) = <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i><sup>c</sup>)<br>'
                'Pero si esto ocurre, por la probabilidad total, la condición se diluye y implicaría que '
                '<i>P</i>(<i>A</i>|<i>B</i>) = <i>P</i>(<i>A</i>|<i>B</i> &cap; <i>C</i>). ¡Esto entra en contradicción directa '
                'con la hipótesis del enunciado!'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="content-box">'
                '2) Por consiguiente, obligatoriamente el primer término debe ser cero:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>B</i> &cap; <i>C</i>) &minus; <i>P</i>(<i>B</i>)<i>P</i>(<i>C</i>) = 0 &nbsp;&rArr;&nbsp; <i>P</i>(<i>B</i> &cap; <i>C</i>) = <i>P</i>(<i>B</i>)<i>P</i>(<i>C</i>)"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="content-box">'
                'Al cumplirse esta igualdad, queda demostrado formalmente que los sucesos <i>B</i> y <i>C</i> son '
                '<b>independientes</b>. &blacksquare;'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler('🎉  <b>¡Demostración completada con éxito!</b> Hemos forzado algebraicamente la independencia debido a la restricción inicial del problema.')
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>La hipótesis de desigualdad en las condicionales es el motor que fuerza la independencia matemática.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA II: TEOREMA DE BAYES (026)
# =============================================================================

def render_problem_2():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'Problema 026 · En una ciudad hay tres bancos, A, B y C. El banco A dispone de un fondo de inversión que produce el 7% con probabilidad 0.25, el 6% con probabilidad 0.5 y el 8% con probabilidad 0.25. El banco B dispone de un fondo de inversión que produce el 7% con probabilidad 0.5, el 6% con probabilidad 0.2 y el 8% con probabilidad 0.3, mientras que el banco C dispone de un fondo de inversión que produce el 7% con probabilidad 0.4, el 6% con probabilidad 0.4 y el 8% con probabilidad 0.2. Se ha subscrito al azar uno de los fondos de inversión, y se obtiene una rentabilidad del 7 %. Hallar la probabilidad de que se haya escogido el banco A.'
            '</div>',
            unsafe_allow_html=True
        )
        
        # ===== APARTADO A =====
        if accordion_step("P2_A", "(A) Paso 1: Definición de sucesos y probabilidades"):
            st.markdown(
                '<div class="content-box">'
                'Definimos los sucesos de elección del banco de forma equiprobable por azar:<br>'
                '<i>P</i>(<i>A</i>) = <i>P</i>(<i>B</i>) = <i>P</i>(<i>C</i>) = 1/3<br><br>'
                'Definimos el suceso <i>R</i><sub>7</sub>: "Obtener una rentabilidad del 7%". '
                'Las probabilidades condicionales para cada banco según la tabla de datos son:<br>'
                '• <i>P</i>(<i>R</i><sub>7</sub>|<i>A</i>) = 0.25<br>'
                '• <i>P</i>(<i>R</i><sub>7</sub>|<i>B</i>) = 0.50<br>'
                '• <i>P</i>(<i>R</i><sub>7</sub>|<i>C</i>) = 0.40'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler('📈 <b>¿Cuál es el banco que mejor pinta tiene?</b> A priori, el banco B ofrece la mayor seguridad para conseguir nuestro objetivo del 7% (50% de probabilidad frente al 25% del banco A).')
        
        # ===== APARTADO B =====
        if accordion_step("P2_B", "(B) Paso 2: Aplicación del Teorema de la probabilidad total"):
            st.markdown(
                '<div class="content-box">'
                'Calculamos la probabilidad total de conseguir la rentabilidad del 7% sumando la contribución de cada banco:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>R</i><sub>7</sub>) = <i>P</i>(<i>A</i>)<i>P</i>(<i>R</i><sub>7</sub>|<i>A</i>) + <i>P</i>(<i>B</i>)<i>P</i>(<i>R</i><sub>7</sub>|<i>B</i>) + <i>P</i>(<i>C</i>)<i>P</i>(<i>R</i><sub>7</sub>|<i>C</i>)"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>R</i><sub>7</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>3</span>"
                "</div>"
                "&middot; 0.25 +"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>3</span>"
                "</div>"
                "&middot; 0.50 +"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>3</span>"
                "</div>"
                "&middot; 0.40 ="
                "<div class='fraction'>"
                "<span class='numerator'>1.15</span>"
                "<span class='denominator'>3</span>"
                "</div>"
                "&approx; 0.3833"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('📊 <b>Conclusión:</b> Existe un 38.33% de probabilidad global de obtener la rentabilidad deseada en un banco elegido al azar.')
        
        # ===== APARTADO C =====
        if accordion_step("P2_C", "(C) Paso 3: Aplicación del Teorema de Bayes"):
            st.markdown(
                '<div class="content-box">'
                'Calculamos la probabilidad a posteriori de haber elegido el banco A:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i>|<i>R</i><sub>7</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'><i>P</i>(<i>A</i>) &middot; <i>P</i>(<i>R</i><sub>7</sub>|<i>A</i>)</span>"
                "<span class='denominator'><i>P</i>(<i>R</i><sub>7</sub>)</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'><sup>1</sup>&frasl;<sub>3</sub> &middot; 0.25</span>"
                "<span class='denominator'><sup>1.15</sup>&frasl;<sub>3</sub></span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'>0.25</span>"
                "<span class='denominator'>1.15</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'>5</span>"
                "<span class='denominator'>23</span>"
                "</div>"
                "&approx; 0.2174"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="content-box">'
                'Por tanto, la probabilidad de que se haya escogido el banco A dado que la rentabilidad obtenida fue del 7% es de un <b>21.74%</b>.'
                '</div>',
                unsafe_allow_html=True
            )
            spoiler('💡 <b>Análisis crítico:</b> ¿Por qué ha disminuido la probabilidad de elegir A de un 33.3% (inicial) a un 21.74%? Es lógico, como el banco A es el que menor probabilidad tenía de producir un 7%, la ocurrencia de ese suceso nos hace desviar la sospecha hacia los otros bancos.')
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>El Teorema de Bayes invierte la probabilidad: de P(evidencia|causa) a P(causa|evidencia).</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# PROBLEMA III: INDEPENDENCIA EN DOS DADOS (028)
# =============================================================================

def render_problem_3():
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        
        planteamiento_header()
        st.markdown(
            '<div class="statement-box">'
            'Problema 028 · Se lanzan dos dados (no cargados) de parchís. Para i = 2, 3, 4, 5, 6 sea:<br>'
            '• A<sub>i</sub>: "el resultado del primer dado es múltiplo de i"<br>'
            '• B<sub>i</sub>: "el resultado del segundo dado es múltiplo de i"<br>'
            '• C<sub>i</sub>: "la suma de los resultados es múltiplo de i"<br><br>'
            'Indicar si: A) A<sub>2</sub> y B<sub>2</sub> son independientes. B) A<sub>2</sub> y C<sub>2</sub> son independientes. C) A<sub>2</sub>, B<sub>2</sub> y C<sub>2</sub> son independientes.'
            '</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            '<div class="content-box">'
            'El espacio muestral del lanzamiento de dos dados consta de 36 resultados equiprobables del tipo (x, y) con probabilidad 1/36.'
            '</div>',
            unsafe_allow_html=True
        )
        
        # ===== APARTADO A =====
        if accordion_step("P3_A", "(A) ¿Son A_2 y B_2 independientes?"):
            st.markdown(
                '<div class="content-box">'
                '• Sucesos:<br>'
                'A<sub>2</sub>: primer dado par &rArr; x &in; {2,4,6} &rArr; P(A<sub>2</sub>) = 1/2<br>'
                'B<sub>2</sub>: segundo dado par &rArr; y &in; {2,4,6} &rArr; P(B<sub>2</sub>) = 1/2<br><br>'
                '• Intersección A<sub>2</sub> &cap; B<sub>2</sub>: ambos dados muestran par (9 casos favorables de 36).'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i><sub>2</sub> &cap; <i>B</i><sub>2</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'>9</span>"
                "<span class='denominator'>36</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>4</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<i>P</i>(<i>A</i><sub>2</sub>) &middot; <i>P</i>(<i>B</i><sub>2</sub>)"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('✅ <b>Respuesta: SÍ son independientes.</b> El resultado físico obtenido en el primer dado no influye bajo ningún concepto en el resultado del segundo dado.')
        
        # ===== APARTADO B =====
        if accordion_step("P3_B", "(B) ¿Son A_2 y C_2 independientes?"):
            st.markdown(
                '<div class="content-box">'
                '• Sucesos:<br>'
                'A<sub>2</sub>: primer dado par &rArr; P(A<sub>2</sub>) = 1/2<br>'
                'C<sub>2</sub>: suma par &rArr; (par+par) o (impar+impar) &rArr; 9 + 9 = 18 casos favorables &rArr; P(C<sub>2</sub>) = 1/2<br><br>'
                '• Intersección A<sub>2</sub> &cap; C<sub>2</sub>: primer dado es par y la suma es par, lo que obliga al segundo dado a ser par.'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i><sub>2</sub> &cap; <i>C</i><sub>2</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'>9</span>"
                "<span class='denominator'>36</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>4</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<i>P</i>(<i>A</i><sub>2</sub>) &middot; <i>P</i>(<i>C</i><sub>2</sub>)"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('✅ <b>Respuesta: SÍ son independientes.</b> Aunque sea contraintuitivo, saber que el primer dado es par no altera la probabilidad de que la suma de ambos sea par (esta sigue manteniéndose en un 50%).')
        
        # ===== APARTADO C =====
        if accordion_step("P3_C", "(C) ¿Son A_2, B_2 y C_2 independientes?"):
            st.markdown(
                '<div class="content-box">'
                'Para determinar la independencia mutua de los tres sucesos, comprobamos si la probabilidad conjunta '
                'de la intersección triple es igual al producto de las probabilidades individuales:'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i><sub>2</sub> &cap; <i>B</i><sub>2</sub> &cap; <i>C</i><sub>2</sub>) = <i>P</i>(<i>A</i><sub>2</sub>) &middot; <i>P</i>(<i>B</i><sub>2</sub>) &middot; <i>P</i>(<i>C</i><sub>2</sub>)"
                "</div>",
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="content-box">'
                '• Lado izquierdo: Si el primer dado es par (A<sub>2</sub>) y el segundo es par (B<sub>2</sub>), la suma es obligatoriamente par (C<sub>2</sub>). '
                'Por tanto, la intersección de los tres sucesos se reduce a que salgan dos números pares (9 casos).'
                '</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                "<div class='formula-box'>"
                "<i>P</i>(<i>A</i><sub>2</sub> &cap; <i>B</i><sub>2</sub> &cap; <i>C</i><sub>2</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'>9</span>"
                "<span class='denominator'>36</span>"
                "</div>"
                "&nbsp;=&nbsp;"
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>4</span>"
                "</div>"
                "&nbsp;&ne;&nbsp;"
                "<i>P</i>(<i>A</i><sub>2</sub>) &middot; <i>P</i>(<i>B</i><sub>2</sub>) &middot; <i>P</i>(<i>C</i><sub>2</sub>) ="
                "<div class='fraction'>"
                "<span class='numerator'>1</span>"
                "<span class='denominator'>8</span>"
                "</div>"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler('❌ <b>Respuesta: NO son mutuamente independientes.</b> Dado que 1/4 es diferente de 1/8, los tres sucesos no son independientes conjuntamente a pesar de ser independientes dos a dos. La información agregada de A y B nos dice con 100% de precisión el estado de C.')
    
    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='footer-bar'>La independencia dos a dos es una condición necesaria pero no suficiente para asegurar la independencia mutua.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    
    st.markdown("<div class='top-bar-title'>C1VIC D4TA, Sucesos Independientes y Teorema Probabilidad Total</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO"}); st.rerun()
    if nav_col2.button("(I) Demostración", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) Teorema Bayes", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Dos dados", use_container_width=True):
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