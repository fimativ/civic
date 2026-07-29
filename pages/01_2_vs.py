import streamlit as st
from bokeh.plotting import figure
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · Los axiomas de Kolmogórov",
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
    --pass-bg: #eaf5e9; --pass-fg: #2e7d32;
    --fail-bg: #fdecec; --fail-fg: #c62828;
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
    --pass-bg: #16261a; --pass-fg: #7bd88f;
    --fail-bg: #2a1717; --fail-fg: #ef9a9a;
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
/* ---- Botón Home (casita) ---- */
[data-testid="stHorizontalBlock"]:has(.st-key-home_btn) {{ flex-wrap: nowrap !important; align-items: stretch !important; }}
div[data-testid="stColumn"]:has(.st-key-home_btn) {{ flex: 0 0 auto !important; width: 84px !important; min-width: 84px !important; }}
.st-key-home_btn button {{
    background: var(--box-bg) !important; color: {UBU_RED} !important;
    border: none !important; border-radius: 12px !important;
    box-shadow: var(--shadow); height: 100%; min-height: 56px;
}}
.st-key-home_btn button p {{ font-size: clamp(24px, 3.6vw, 36px) !important; line-height: 1 !important; }}

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

/* ---- Comentario dinámico y badge de resultado ---- */
.comment-box {{
    border: 2px solid {UBU_RED}; border-radius: 12px;
    padding: clamp(14px, 2vw, 24px); background: var(--box-bg);
    font-style: italic; box-shadow: var(--shadow);
    color: var(--box-fg); font-size: clamp(15px, 1.9vw, 22px);
    line-height: 1.5; margin-bottom: 15px; width: 100%;
}}
.result-badge {{
    display: inline-block; background: {UBU_YELLOW};
    border: 3px solid var(--metric-border); border-radius: 10px;
    padding: 12px 22px; font-weight: 700;
    font-size: clamp(15px, 1.9vw, 22px); color: {UBU_DARK};
    margin-bottom: 18px; box-shadow: var(--shadow); text-align: center;
}}

/* ---- Verificador de axiomas ---- */
.axiom-check {{
    font-size: clamp(15px, 1.9vw, 22px); color: var(--box-fg);
    padding: clamp(12px, 1.8vw, 20px); background: var(--box-bg);
    border-radius: 10px; margin-bottom: 14px; width: 100%;
    border-left: 8px solid var(--metric-border); box-shadow: var(--shadow);
    line-height: 1.45;
}}
.axiom-pass {{ border-left-color: var(--pass-fg); background: var(--pass-bg); }}
.axiom-fail {{ border-left-color: var(--fail-fg); background: var(--fail-bg); }}
.validity-badge {{
    font-size: clamp(13px, 1.5vw, 18px); font-weight: 700; width: 100%;
    text-align: center; padding: 10px 14px; border-radius: 10px;
    margin-top: 6px; box-shadow: var(--shadow);
}}
.validity-ok  {{ background: var(--pass-bg); color: var(--pass-fg); }}
.validity-no  {{ background: var(--fail-bg); color: var(--fail-fg); }}

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
    background: var(--box-bg); padding: 15px 20px; margin: 12px 0;
    text-align: center; font-family: 'STIX Two Math', 'Cambria Math', serif;
    font-size: clamp(17px, 2.2vw, 26px); color: var(--spoiler-fg);
}}
/* Fórmula visible (recuadro, sin spoiler) */
.formula-box.plain {{ color: var(--box-fg); border-color: {UBU_RED}; }}

/* ---- Botones (navegación + acordeón + selección) ---- */
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

/* ---- Pie de página ---- */
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

/* ============ MÓVIL: reflujo de una sola columna ============ */
@media (max-width: 640px) {{
    div[data-testid="column"]:has(.bg-left),
    div[data-testid="column"]:has(.bg-right) {{
        min-height: auto !important; margin-bottom: 14px;
    }}
    .statement-box, .content-box, .comment-box {{ text-align: left; }}
}}
</style>
"""

# =============================================================================
# 2. DATOS
# =============================================================================

# Espacio muestral: tres lanzamientos de una moneda (C = cara, X = cruz)
OMEGA = ["CCC", "CCX", "CXC", "XCC", "CXX", "XCX", "XXC", "XXX"]

EVENTS = {
    "E":    ("E", "hay exactamente dos cruces", ["CXX", "XCX", "XXC"]),
    "F":    ("F", "hay al menos dos cruces", ["CXX", "XCX", "XXC", "XXX"]),
    "G":    ("G", "no aparece cruz antes que la primera cara", ["CCC", "CCX", "CXC", "CXX"]),
    "H":    ("H", "el primer lanzamiento es cruz", ["XCC", "XCX", "XXC", "XXX"]),
    "Ec":   ("E<sup>c</sup>", "NO hay exactamente dos cruces", [x for x in OMEGA if x not in ["CXX", "XCX", "XXC"]]),
    "FmE":  ("F \\ E", "está en F pero no en E", ["XXX"]),
    "EuGH": ("E &cup; (G &cap; H)", "como G &cap; H = &empty;, el resultado es E", ["CXX", "XCX", "XXC"]),
    "EiHc": ("E &cap; H<sup>c</sup>", "está en E pero no en H", ["CXX"]),
}
PART_A_KEYS = ["E", "F", "G", "H"]
PART_B_KEYS = ["Ec", "FmE", "EuGH", "EiHc"]

# Candidatos a función de probabilidad (Problema II: "Descubre al impostor")
CANDIDATOS = [
    {
        "label": "P(A) = 0 si A es finito, 1 si A es infinito",
        "ax": [True, True, False],
        "why": [
            "Solo toma los valores 0 y 1, ambos &ge; 0.",
            "&Omega; es infinito, luego P(&Omega;) = 1.",
            "Contraejemplo: &Omega; = &#8469; = &#8899; {n}, cada {n} finito con P = 0, "
            "pero P(&Omega;) = 1 &ne; &sum; 0 = 0.",
        ],
    },
    {
        "label": "P(A) = a si A &ne; &empty;, 0 si A = &empty; (con a constante)",
        "ax": [True, True, False],
        "why": [
            "a &isin; (0, 1], luego P(A) &ge; 0.",
            "P(&Omega;) = a, y solo vale 1 si a = 1.",
            "Si A y B son disjuntos y no vacíos: P(A&cup;B) = a, pero P(A)+P(B) = 2a &ne; a.",
        ],
    },
    {
        "label": "Probabilidad clásica o de Laplace: P(A) = |A| / |&Omega;|",
        "ax": [True, True, True],
        "why": [
            "|A| / |&Omega;| &ge; 0 siempre.",
            "P(&Omega;) = |&Omega;| / |&Omega;| = 1.",
            "Si A &cap; B = &empty;, entonces |A&cup;B| = |A| + |B|, luego P(A&cup;B) = P(A) + P(B).",
        ],
    },
]
AXIOM_NAMES = ["(I) No negatividad", "(II) Normalización", "(III) Aditividad"]

# Demostración de Bonferroni agrupada en 3 etapas (texto + fórmula en spoiler)
F_GOAL   = ("&#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) &ge; "
            "1 &minus; &sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub><sup>c</sup>)")
F_DEMOR  = ("(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>)<sup>c</sup> = "
            "&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>")
F_COMPL  = ("&#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) = "
            "1 &minus; &#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>)")
F_BOOLE  = ("&#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>) &le; "
            "&sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub><sup>c</sup>)")

# =============================================================================
# 3. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "INTRO",
        "open_part": "P1_A",
        "sel_a": "E",
        "sel_b": "Ec",
        "sel_c": "XXX",
        "sel_cand": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 4. FUNCIONES AUXILIARES
# =============================================================================

def accordion_step(step_id: str, title: str) -> bool:
    is_open = st.session_state["open_part"] == step_id
    if st.button(title, key=f"acc_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state["open_part"] = step_id if not is_open else None
        st.rerun()
    return is_open

def spoiler(html_content: str, hint: str = "Pulsa para revelar la solución"):
    st.markdown(
        f"""<label class='spoiler-lbl'>
            <input type='checkbox' class='spoiler-toggle'>
            <span class='spoiler-hint'>{hint}</span>
            <div class='spoiler-box'>{html_content}</div>
        </label>""",
        unsafe_allow_html=True,
    )

def formula_hidden(formula: str, hint: str = "Pulsa para revelar su expresión matemática"):
    spoiler(f"<div class='formula-box'>{formula}</div>", hint=hint)

# ---- Diagrama en árbol del espacio muestral (tema claro/oscuro) ----

def tree_diagram(highlighted, dark):
    HI = GREEN_LINE
    if dark:
        fill_def, line_def = "#24242b", "#5a5a62"
        text_def, text_leaf = "#cfcfcf", "#9a9aa2"
        hi_fill = "#1f3d27"
    else:
        fill_def, line_def = "#ffffff", "#c2c2c2"
        text_def, text_leaf = "#555555", "#888888"
        hi_fill = "#dff0df"

    # Coordenadas: árbol ancho y chato (3 niveles + raíz)
    nodes = {
        "root": (0.0, 3.0),
        "C": (-3.0, 2.0), "X": (3.0, 2.0),
        "CC": (-4.5, 1.0), "CX": (-1.5, 1.0), "XC": (1.5, 1.0), "XX": (4.5, 1.0),
        "CCC": (-5.25, 0.0), "CCX": (-3.75, 0.0), "CXC": (-2.25, 0.0), "CXX": (-0.75, 0.0),
        "XCC": (0.75, 0.0), "XCX": (2.25, 0.0), "XXC": (3.75, 0.0), "XXX": (5.25, 0.0),
    }
    children = {
        "root": ["C", "X"],
        "C": ["CC", "CX"], "X": ["XC", "XX"],
        "CC": ["CCC", "CCX"], "CX": ["CXC", "CXX"],
        "XC": ["XCC", "XCX"], "XX": ["XXC", "XXX"],
    }

    def active(name):
        return any(h.startswith(name) for h in highlighted)

    p = figure(height=340, sizing_mode="stretch_width",
               x_range=(-6.2, 6.2), y_range=(-0.5, 3.5), toolbar_location=None)
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    p.grid.visible = False
    p.axis.visible = False

    # Aristas
    for parent, chs in children.items():
        x0, y0 = nodes[parent]
        for c in chs:
            x1, y1 = nodes[c]
            on = active(c)
            p.line([x0, x1], [y0, y1], line_color=HI if on else line_def,
                   line_width=6 if on else 2.5)

    # Nodos
    for name, (x, y) in nodes.items():
        if name == "root":
            p.scatter([x], [y], size=42, marker="circle",
                      fill_color=fill_def, line_color=UBU_RED, line_width=4)
            p.text([x], [y], text=["Ω"], text_align="center",
                   text_baseline="middle", text_font_size="22px", text_color=UBU_RED)
            continue
        is_leaf = len(name) == 3
        is_hi = name in highlighted
        act = active(name)
        p.scatter([x], [y], size=44 if is_leaf else 38, marker="circle",
                  fill_color=hi_fill if is_hi else fill_def,
                  line_color=HI if act else line_def, line_width=5 if act else 2.5)
        p.text([x], [y], text=[name], text_align="center", text_baseline="middle",
               text_font_size="18px" if is_leaf else "17px",
               text_color=HI if act else (text_leaf if is_leaf else text_def))
    return p

# =============================================================================
# 5. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>¿Qué es la probabilidad?</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>A lo largo de la historia la probabilidad ha recibido cuatro "
            "grandes definiciones, y todas conviven hoy. La <b>clásica</b> (o de Laplace) cuenta casos "
            "favorables entre casos posibles cuando todos son igual de verosímiles; la <b>frecuentista</b> "
            "la entiende como el límite de la frecuencia relativa al repetir un experimento muchísimas "
            "veces; la <b>bayesiana</b> la interpreta como un grado de creencia que se actualiza con la "
            "evidencia; y la <b>axiomática</b> de Kolmogórov no dice qué <i>es</i> la probabilidad, sino "
            "qué reglas debe cumplir. Iremos detallando cada una en otros temas: aquí nos quedamos con "
            "esta última, la que puso los cimientos de todas.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Andréi Kolmogórov (1903-1987) fue tan aficionado al deporte como a "
            "las matemáticas: se cuenta que esquiaba y nadaba durante los crudos inviernos rusos, a veces "
            "ligero de ropa bajo el sol helado, convencido de que el cuerpo y la mente se entrenan igual. "
            "En 1933, con apenas unas páginas, hizo por el azar lo que Maxwell había hecho por la "
            "electricidad y el magnetismo: así como cuatro ecuaciones bastaban para describir todo campo "
            "electromagnético, Kolmogórov buscó las leyes mínimas que gobernaran <i>cualquier</i> sistema "
            "regido por la incertidumbre. Y las encontró en apenas <b>tres axiomas</b>, sobre los que se "
            "levanta toda la teoría moderna de la probabilidad.</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-title'>Los tres axiomas de Kolmogórov</div>",
                    unsafe_allow_html=True)

        st.markdown(
            "<div class='content-box'><b>(I) No negatividad.</b> La probabilidad de cualquier suceso "
            "nunca es negativa.<br><br><i>Prueba ahora a escribir esto matemáticamente.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden("&#8473;(A) &ge; 0")

        st.markdown(
            "<div class='content-box'><b>(II) Normalización.</b> La probabilidad del suceso seguro (todo "
            "el espacio muestral &Omega;) es 1.<br><br><i>Prueba ahora a escribir esto "
            "matemáticamente.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden("&#8473;(&Omega;) = 1")

        st.markdown(
            "<div class='content-box'><b>(III) Aditividad numerable.</b> Para sucesos incompatibles "
            "(disjuntos), la probabilidad de su unión es la suma de sus probabilidades.<br><br>"
            "<i>Prueba ahora a escribir esto matemáticamente.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden(
            "A<sub>i</sub> &cap; A<sub>j</sub> = &empty; &rArr; "
            "&#8473;(&#8899;<sub>i=1</sub><sup>&infin;</sup> A<sub>i</sub>) = "
            "&sum;<sub>i=1</sub><sup>&infin;</sup> &#8473;(A<sub>i</sub>)"
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Encerrando a Venn</b><br>"
            "<i>Ayuda a John Venn (1823-1923) a convencer a la London Mathematical Society de la utilidad "
            "de sus diagramas.</i><br><br>"
            "<b>II. Esperando a Kolmogórov (descubre al impostor)</b><br>"
            "<i>Varios compañeros del primer curso del grado del año pasado intentaron describir su propia "
            "definición de probabilidad. Descubre cuáles lo serían también para Kolmogórov.</i><br><br>"
            "<b>III. Corrigiendo con Bonferroni</b><br>"
            "<i>Comprueba junto con Carlo Emilio Bonferroni (1892-1960) que es necesario corregir el nivel "
            "de significación (&alpha;; no te preocupes, lo verás en Estadística Univariante) para evitar "
            "falsos positivos al hacer pruebas simultáneas.</i>"
            "</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Encerrando a Venn</b><br><br>"
            "Llamamos C a cara y X a cruz. Al lanzar una moneda una sola vez, el conjunto de todos los "
            "resultados posibles es &Omega; = {C, X}. Si la lanzamos tres veces, ese conjunto crece hasta "
            "los 2<sup>3</sup> = 8 resultados:<br><br>"
            "&Omega; = {CCC, CCX, CXC, XCC, CXX, XCX, XXC, XXX}</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "(A) Eventos simples"):
            st.markdown(
                "<div class='content-box'>Escribe el conjunto de resultados de cada suceso:<br><br>"
                "<b>E:</b> exactamente dos cruces.<br>"
                "<b>F:</b> al menos dos cruces.<br>"
                "<b>G:</b> no aparece cruz antes que la primera cara.<br>"
                "<b>H:</b> el primer lanzamiento es cruz.<br><br>"
                "Pulsa cada suceso para verlo resaltado en el árbol de la derecha.</div>",
                unsafe_allow_html=True
            )
            cols = st.columns(4)
            for i, k in enumerate(PART_A_KEYS):
                with cols[i]:
                    active = st.session_state["sel_a"] == k
                    if st.button(k, key=f"btn_a_{k}", use_container_width=True,
                                 type="primary" if active else "secondary"):
                        st.session_state["sel_a"] = k
                        st.rerun()
            spoiler(
                "E = {CXX, XCX, XXC}<br>"
                "F = {CXX, XCX, XXC, XXX}<br>"
                "G = {CCC, CCX, CXC, CXX}<br>"
                "H = {XCC, XCX, XXC, XXX}"
            )

        if accordion_step("P1_B", "(B) Eventos compuestos"):
            st.markdown(
                "<div class='content-box'>Ahora consideramos la unión, intersección o diferencia de "
                "varios de los anteriores. ¿Cómo podrías describir estos sucesos?<br><br>"
                "E<sup>c</sup>, &nbsp; F \\ E, &nbsp; E &cup; (G &cap; H), &nbsp; E &cap; H<sup>c</sup>"
                "</div>",
                unsafe_allow_html=True
            )
            cols = st.columns(4)
            labels_b = {"Ec": "Eᶜ", "FmE": "F\\E", "EuGH": "E∪(G∩H)", "EiHc": "E∩Hᶜ"}
            for i, k in enumerate(PART_B_KEYS):
                with cols[i]:
                    active = st.session_state["sel_b"] == k
                    if st.button(labels_b[k], key=f"btn_b_{k}", use_container_width=True,
                                 type="primary" if active else "secondary"):
                        st.session_state["sel_b"] = k
                        st.rerun()
            spoiler(
                "E<sup>c</sup> = {CCC, CCX, CXC, XCC, XXX}<br>"
                "F \\ E = {XXX}<br>"
                "E &cup; (G &cap; H) = E &cup; &empty; = {CXX, XCX, XXC}<br>"
                "E &cap; H<sup>c</sup> = {CXX}"
            )

        if accordion_step("P1_C", "(C) Monedas sospechosas"):
            st.markdown(
                "<div class='content-box'>En principio la probabilidad de cara o cruz es idéntica e igual "
                "a un medio. Definamos ahora la probabilidad de <b>cruz</b> con p.<br><br>"
                "Un amigo te ha propuesto jugaros quién hace la tarea con una moneda que sacó de su "
                "bolsillo. Sospechosamente, ha dicho que se pide cruz. ¿Cómo se modifica la probabilidad "
                "de cada resultado? Elige un resultado en los botones de abajo y mueve el deslizador p de "
                "la derecha.</div>",
                unsafe_allow_html=True
            )
            row1 = st.columns(4)
            row2 = st.columns(4)
            for i, outcome in enumerate(OMEGA):
                target = row1[i] if i < 4 else row2[i - 4]
                with target:
                    active = st.session_state["sel_c"] == outcome
                    if st.button(outcome, key=f"btn_c_{outcome}", use_container_width=True,
                                 type="primary" if active else "secondary"):
                        st.session_state["sel_c"] = outcome
                        st.rerun()
            formula_hidden(
                "P(resultado) = p<sup>&#8203;(nº de cruces)</sup> (1&minus;p)<sup>&#8203;(nº de caras)</sup>",
                hint="Pulsa para revelar la fórmula general"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>El espacio muestral en árbol</div>",
                    unsafe_allow_html=True)

        open_part = st.session_state["open_part"]

        if open_part == "P1_B":
            key = st.session_state["sel_b"]
            label, desc, hi = EVENTS[key]
            st.markdown(
                f"<div class='comment-box'><b>{label}</b>: {desc}. "
                f"Cardinalidad |{label}| = {len(hi)} de {len(OMEGA)}.</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='result-badge'>{label} = {{ {', '.join(hi)} }}</div>",
                        unsafe_allow_html=True)
            streamlit_bokeh(tree_diagram(hi, dark), use_container_width=True)
            prob = len(hi) / len(OMEGA)
            st.markdown(
                f"<div class='footer-bar'>Si todos los resultados son equiprobables, la probabilidad de "
                f"un suceso es su nº de casos favorables entre 8. Aquí: P = {len(hi)}/8 = {prob:.3f}.</div>",
                unsafe_allow_html=True
            )

        elif open_part == "P1_C":
            p_cruz = st.slider("p (probabilidad de cruz)", 0.0, 1.0, 0.5, 0.01,
                               key="p_cruz", label_visibility="collapsed")
            outcome = st.session_state["sel_c"]
            n_x = outcome.count("X")
            n_c = outcome.count("C")
            prob = (p_cruz ** n_x) * ((1 - p_cruz) ** n_c)
            st.markdown(
                f"<div class='comment-box'>Con p = {p_cruz:.2f}, el resultado <b>{outcome}</b> tiene "
                f"{n_x} cruces y {n_c} caras.</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='result-badge'>P({outcome}) = "
                f"{p_cruz:.2f}<sup>{n_x}</sup> · {1-p_cruz:.2f}<sup>{n_c}</sup> = {prob:.3f}</div>",
                unsafe_allow_html=True
            )
            streamlit_bokeh(tree_diagram([outcome], dark), use_container_width=True)
            st.markdown(
                "<div class='footer-bar'>Cuando la moneda no es justa los ocho resultados dejan de ser "
                "equiprobables: cada uno pesa según cuántas cruces y caras contiene.</div>",
                unsafe_allow_html=True
            )

        else:  # P1_A por defecto
            key = st.session_state["sel_a"]
            label, desc, hi = EVENTS[key]
            st.markdown(
                f"<div class='comment-box'><b>{label}</b>: {desc}. "
                f"Cardinalidad |{label}| = {len(hi)} de {len(OMEGA)}.</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='result-badge'>{label} = {{ {', '.join(hi)} }}</div>",
                        unsafe_allow_html=True)
            streamlit_bokeh(tree_diagram(hi, dark), use_container_width=True)
            prob = len(hi) / len(OMEGA)
            st.markdown(
                f"<div class='footer-bar'>Si todos los resultados son equiprobables, la probabilidad de "
                f"un suceso es su nº de casos favorables entre 8. Aquí: P = {len(hi)}/8 = {prob:.3f}.</div>",
                unsafe_allow_html=True
            )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Esperando a Kolmogórov · Descubre al impostor</b><br><br>"
            "Varios compañeros del primer curso del grado del año pasado intentaron inventar su propia "
            "definición de probabilidad. Cada una es un <i>candidato</i> a función de probabilidad, pero "
            "solo será válida si cumple los <b>tres axiomas</b> de Kolmogórov. Estos fueron sus "
            "candidatos:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>"
            "<b>1.</b> P(A) = 0 si A es finito, 1 si A es infinito.<br><br>"
            "<b>2.</b> P(A) = a si A &ne; &empty;, 0 si A = &empty; (con a constante).<br><br>"
            "<b>3.</b> Probabilidad clásica o de Laplace: P(A) = |A| / |&Omega;|."
            "</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)

        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                active = st.session_state["sel_cand"] == i
                if st.button(f"Candidato {i+1}", key=f"cand_{i}", use_container_width=True,
                             type="primary" if active else "secondary"):
                    st.session_state["sel_cand"] = i
                    st.rerun()

        c = CANDIDATOS[st.session_state["sel_cand"]]
        st.markdown(f"<div class='comment-box'>{c['label']}</div>", unsafe_allow_html=True)

        for i in range(3):
            ok = c["ax"][i]
            css = "axiom-pass" if ok else "axiom-fail"
            veredicto = "cumple" if ok else "no cumple"
            st.markdown(
                f"<div class='axiom-check {css}'><b>{AXIOM_NAMES[i]} — {veredicto}.</b><br>{c['why'][i]}</div>",
                unsafe_allow_html=True
            )

        if all(c["ax"]):
            st.markdown(
                "<div class='validity-badge validity-ok'>Es una medida de probabilidad válida</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='validity-badge validity-no'>No es una medida de probabilidad válida</div>",
                unsafe_allow_html=True
            )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Corrigiendo con Bonferroni</b><br><br>"
            "Carlo Emilio Bonferroni (1892-1960) fue un matemático italiano que trabajó en Bari y "
            "Florencia sobre cálculo de probabilidades y matemática actuarial (la de los seguros). Su "
            "nombre quedó unido a unas desigualdades que acotan la probabilidad de que varios sucesos "
            "ocurran a la vez y, sobre todo, a la <b>corrección de Bonferroni</b>: al realizar muchas "
            "pruebas estadísticas simultáneas hay que endurecer el nivel de significación &alpha; para no "
            "acumular falsos positivos.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='formula-box plain'>{F_GOAL}</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Demuéstralo por etapas</div>", unsafe_allow_html=True)

        etapa = st.slider("Etapa de la demostración", 1, 3, 1, 1,
                          key="bonf_stage", label_visibility="collapsed")

        if etapa == 1:
            st.markdown(
                "<div class='content-box'><b>Etapa 1 · Planteamiento.</b><br>"
                "Queremos acotar por debajo la probabilidad de que ocurran todos los sucesos "
                "A<sub>1</sub>, …, A<sub>n</sub> a la vez (su intersección). Ese es el objetivo que "
                "buscamos demostrar.<br><br><i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(F_GOAL)

        elif etapa == 2:
            st.markdown(
                "<div class='content-box'><b>Etapa 2 · Del complementario a la unión.</b><br>"
                "Primero pasamos a complementarios: por las leyes de De Morgan, el complementario de la "
                "intersección es la unión de los complementarios.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(F_DEMOR)
            st.markdown(
                "<div class='content-box'>Y por la regla del complementario, la probabilidad de la "
                "intersección es 1 menos la probabilidad de esa unión.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(F_COMPL)

        else:
            st.markdown(
                "<div class='content-box'><b>Etapa 3 · Acotar y concluir.</b><br>"
                "Acotamos la unión con la desigualdad de Boole: la probabilidad de una unión nunca supera "
                "la suma de las probabilidades.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(F_BOOLE)
            st.markdown(
                "<div class='content-box'>Combinando la regla del complementario con la desigualdad de "
                "Boole obtenemos la desigualdad de Bonferroni.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(F_GOAL + " &#8718;")

# =============================================================================
# 6. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)
    dark = detect_dark_theme()

    c_home, c_title = st.columns([1, 11], gap="small")
    with c_home:
        if st.button("⌂", key="home_btn", use_container_width=True, help="Volver al inicio"):
            try:
                st.switch_page("home.py")
            except Exception:
                st.toast("Ejecuta home.py para ver el índice")
    with c_title:
        st.markdown("<div class='top-bar-title'>C1VIC D4TA · Los axiomas de Kolmogórov</div>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("INTRO", "Introducción", None),
        ("P1", "(I) Encerrando a Venn", "P1_A"),
        ("P2", "(II) Esperando a Kolmogórov", None),
        ("P3", "(III) Corrigiendo con Bonferroni", None),
    ]
    nav_cols = st.columns(4)
    for col, (page_id, label, first_part) in zip(nav_cols, nav):
        is_active = current_page == page_id
        if col.button(label, use_container_width=True,
                      type="primary" if is_active else "secondary",
                      key=f"nav_{page_id}"):
            update = {"page": page_id}
            if first_part:
                update["open_part"] = first_part
            st.session_state.update(update)
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if current_page == "INTRO":
        render_intro()
    elif current_page == "P1":
        render_problem_1(dark)
    elif current_page == "P2":
        render_problem_2(dark)
    elif current_page == "P3":
        render_problem_3(dark)

    st.markdown(
        "<div class='footer-license'>MIT License &nbsp;|&nbsp; CC BY-NC 4.0 &nbsp;|&nbsp; "
        "[AOD, OVG, SPP] 2026</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
