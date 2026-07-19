import streamlit as st
import numpy as np
import random
from collections import Counter
from math import comb
from bokeh.plotting import figure
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA · La probabilidad clásica de Laplace",
    initial_sidebar_state="collapsed",
)

# Colores de marca
UBU_RED        = "#9b2743"
UBU_YELLOW     = "#F5C400"
UBU_DARK       = "#1a1a1a"
PANTONE_2727   = "#4169E1"
BLUE_LINE      = "#2b6cb0"
GREEN_LINE     = "#2e7d32"

# Paleta CMYK del histograma: cian + magenta = azul (la suma de dos da el tercero)
COL_CYAN    = "#00AEEF"   # 1 pareja
COL_MAGENTA = "#EC008C"   # 2 parejas
COL_BLUE    = "#3b4cc0"   # >= 1 pareja  (cian + magenta)

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
    margin-bottom: 18px; box-shadow: var(--shadow); text-align: center; width: 100%;
}}

/* ---- Cajas de porcentaje (resultado Montecarlo) ---- */
.pct-box {{
    font-size: clamp(16px, 2.1vw, 24px); font-weight: 700; text-align: center;
    border-radius: 12px; padding: 16px 20px; width: 100%; margin-bottom: 14px;
    box-shadow: var(--shadow);
}}
.pct-zero    {{ background: {UBU_YELLOW}; color: {UBU_DARK}; }}
.pct-atleast {{ background: {COL_BLUE};   color: #ffffff; }}

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
.formula-box.plain {{ color: var(--box-fg); border-color: {UBU_RED}; }}

/* ---- Botones ---- */
button p {{ font-size: clamp(14px, 1.7vw, 21px) !important; line-height: 1.2 !important; }}
div[data-testid="column"] button {{
    padding-top: 14px !important; padding-bottom: 14px !important;
    white-space: normal !important; height: 100%;
}}
/* Botón de "play" en amarillo, solo el símbolo */
.st-key-play_p1 button, .st-key-play_p2 button {{
    background: {UBU_YELLOW} !important; color: {UBU_DARK} !important;
    border: 2px solid {UBU_YELLOW} !important;
}}
.st-key-play_p1 button p, .st-key-play_p2 button p {{
    font-size: clamp(22px, 3vw, 34px) !important; font-weight: 700 !important;
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
# 2. ESTADO DE LA SESIÓN
# =============================================================================

def init_session_state():
    defaults = {
        "page": "INTRO",
        "open_p1": "P1_A",
        "open_p2": "P2_A",
        "open_p3": "P3_A",
        "n_cartas": 5000,
        "cartas_res": None,
        "n_buffon": 2000,
        "buffon_res": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================

def accordion(state_key: str, step_id: str, title: str) -> bool:
    is_open = st.session_state[state_key] == step_id
    if st.button(title, key=f"acc_{state_key}_{step_id}", use_container_width=True,
                 type="primary" if is_open else "secondary"):
        st.session_state[state_key] = step_id if not is_open else None
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

# ---- Tematización de las gráficas ----

def chart_theme(dark):
    if dark is True:
        return dict(fg="#e6e6e6", grid="#3a3a42", axis="#8a8a92", line="#5a5a62")
    if dark is False:
        return dict(fg="#2a2a2a", grid="#e2e2e2", axis="#9a9a9a", line="#c2c2c2")
    return dict(fg="#8a8a8a", grid="#8a8a8a", axis="#8a8a8a", line="#8a8a8a")

def style_axes(p, th, label_size="18px", tick_size="14px"):
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

# =============================================================================
# 4. LÓGICA: CARTAS DE FOURNIER (baraja española de 40)
# =============================================================================

# 10 valores (1..7, sota, caballo, rey), cada uno en 4 palos
def create_deck():
    return [v for v in range(10) for _ in range(4)]

def count_pairs(cards):
    return sum(1 for c in Counter(cards).values() if c >= 2)

def run_cartas(n_sims, seed=42):
    random.seed(seed)
    deck = create_deck()
    res = {"n0": 0, "n1": 0, "n2": 0}
    for _ in range(n_sims):
        drawn = random.sample(deck, 4)
        k = count_pairs(drawn)
        res["n0" if k == 0 else ("n1" if k == 1 else "n2")] += 1
    return res

def cartas_teorico():
    total = comb(40, 4)
    sin = comb(10, 4) * (4 ** 4)
    p_sin = sin / total
    return {"total": total, "sin": sin, "p_sin": p_sin, "p_al_menos": 1 - p_sin}

def histograma_cartas(res, n, th):
    labels = ["0 parejas", "1 pareja", "2 parejas"]
    pcts = [res["n0"] / n * 100, res["n1"] / n * 100, res["n2"] / n * 100]
    p = figure(x_range=labels, height=300, sizing_mode="stretch_width",
               toolbar_location=None, tools="", y_axis_label="% de las simulaciones",
               y_range=(0, max(pcts) * 1.15 + 1))
    p.vbar(x=labels, top=pcts, width=0.7,
           fill_color=[UBU_YELLOW, COL_CYAN, COL_MAGENTA],
           line_color=th["axis"], line_width=1.5)
    return style_axes(p, th)

# =============================================================================
# 5. LÓGICA: AGUJA DE BUFFON (Montecarlo para pi)
# =============================================================================

def run_buffon(n, ell=0.8, field=8, seed=42):
    rng = np.random.default_rng(seed)
    xc = rng.uniform(0.4, field - 0.4, n)
    # yc sobre un número ENTERO de franjas (0..field) para que la estimación sea insesgada
    yc = rng.uniform(0.0, field, n)
    th = rng.uniform(0.0, np.pi, n)
    dy = (ell / 2.0) * np.sin(th)
    crosses = np.floor(yc - dy) != np.floor(yc + dy)   # líneas enteras, d = 1
    ncross = int(crosses.sum())
    pi_est = (2.0 * ell * n) / ncross if ncross > 0 else float("nan")
    return dict(xc=xc, yc=yc, th=th, ell=ell, field=field,
                crosses=crosses, ncross=ncross, n=n, pi_est=pi_est)

def buffon_chart(sim, th, max_draw=250):
    field = sim["field"]
    ell = sim["ell"]
    p = figure(height=420, sizing_mode="stretch_width", toolbar_location=None,
               x_range=(0, field), y_range=(0, field), match_aspect=True)
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    p.grid.visible = False
    p.axis.visible = False
    # Líneas paralelas del suelo
    for y in range(0, field + 1):
        p.line([0, field], [y, y], line_color=th["line"], line_width=2)
    # Agujas (subconjunto para no saturar)
    m = min(sim["n"], max_draw)
    xc, yc, ang, cr = sim["xc"][:m], sim["yc"][:m], sim["th"][:m], sim["crosses"][:m]
    dx = (ell / 2.0) * np.cos(ang)
    dy = (ell / 2.0) * np.sin(ang)
    xs0, xs1 = xc - dx, xc + dx
    ys0, ys1 = yc - dy, yc + dy
    for i in range(m):
        col = GREEN_LINE if cr[i] else th["line"]
        p.line([xs0[i], xs1[i]], [ys0[i], ys1[i]],
               line_color=col, line_width=3 if cr[i] else 2,
               line_alpha=0.95 if cr[i] else 0.55)
    return p

# =============================================================================
# 6. PÁGINAS
# =============================================================================

def render_intro():
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>¿Qué es la probabilidad clásica?</b></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'>Como ya introdujimos, durante siglos el azar se jugó sin medirse. "
            "Fue Pierre-Simon Laplace quien, recogiendo el trabajo de Pascal, Fermat y Bernoulli, quiso "
            "reducir la probabilidad a algo que se pudiera <b>contar</b>: enumerar todos los resultados "
            "posibles de un experimento y ver cuántos son favorables al suceso que nos interesa. A esta "
            "idea se la llama <b>probabilidad clásica</b> precisamente porque coincide con la noción "
            "intuitiva que todos tenemos —casos favorables entre casos totales— cuando los resultados son "
            "igual de verosímiles, como en la lotería o en los juegos de cartas (al menos en "
            "principio).<br><br><i>Antes de mirar la fórmula, trata de deducir tú mismo su "
            "expresión.</i></div>",
            unsafe_allow_html=True
        )
        formula_hidden(
            "&#8473;(A) = "
            "<sup>casos favorables</sup>&frasl;<sub>casos posibles</sub> = "
            "|A| &frasl; |&Omega;|",
            hint="Pulsa para revelar la definición"
        )

        st.markdown("<div class='section-title'>Condiciones necesarias</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>Finitud.</b> El espacio muestral &Omega; debe ser finito, para "
            "así lidiar con números y no con infinitos.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><b>Equiprobabilidad.</b> Todos los resultados deben ser igual de "
            "probables, para que contar cardinales (casos) sea equivalente a contar probabilidades.</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='content-box'><b>Aplicación.</b> Bajo esas condiciones, cada suceso elemental "
            "{&omega;} tiene probabilidad 1/|&Omega;|. Es la herramienta ideal para juegos de azar "
            "simétricos: dados, cartas o loterías.</div>",
            unsafe_allow_html=True
        )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Ahora es tu turno</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'>"
            "<b>I. Jugando a las cartas de Fournier (1870)</b><br>"
            "<i>Pon a prueba tu intuición antes de tu siguiente apuesta al mus.</i><br><br>"
            "<b>II. El nido de agujas de Buffon</b><br>"
            "<i>Explora con Buffon (1707-1788) un poco más el método de Montecarlo, esta vez para "
            "obtener el número &pi;.</i><br><br>"
            "<b>III. Un problema navideño: regalos mágicos</b><br>"
            "<i>Ayuda a Sus Majestades de Oriente a recibir cada uno su propio regalo.</i>"
            "</div>",
            unsafe_allow_html=True
        )

def render_problem_1(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Jugando a las cartas de Fournier (1870)</b><br><br>"
            "Una baraja española tiene <b>40 cartas</b>: 10 valores (1 al 7, sota, caballo y rey), cada "
            "uno en 4 palos (oros, copas, espadas y bastos). En el mus recibes 4 cartas. ¿Cuál es la "
            "probabilidad de que te salga <b>al menos una pareja</b> (dos cartas del mismo valor)?</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p1", "P1_A", "(A) Planteamiento"):
            st.markdown(
                "<div class='content-box'>"
                "&bull; La baraja tiene 40 cartas: 10 valores (1 al 7, sota, caballo, rey).<br>"
                "&bull; Cada valor aparece en 4 palos distintos (oros, copas, espadas, bastos).<br>"
                "&bull; Se extraen 4 cartas <b>sin reemplazamiento</b> (una carta sacada ya no vuelve a la "
                "baraja).<br>"
                "&bull; Buscamos P(al menos una pareja del mismo valor)."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion("open_p1", "P1_B", "(B) Cálculo teórico"):
            st.markdown(
                "<div class='content-box'>Es más cómodo calcular el <b>complementario</b>: la probabilidad "
                "de NO obtener ninguna pareja (las 4 cartas con valores todos distintos) y restarla de 1. "
                "Para no tener pareja elegimos 4 valores diferentes de los 10 y, para cada uno, uno de sus "
                "4 palos.<br><br><i>Trata de escribir las fórmulas antes de revelarlas.</i></div>",
                unsafe_allow_html=True
            )
            t = cartas_teorico()
            formula_hidden(
                "Casos totales = C(40, 4) = " + f"{t['total']:,}".replace(",", ".") + "<br>"
                "Sin pareja = C(10, 4) &middot; 4<sup>4</sup> = " + f"{t['sin']:,}".replace(",", ".") + "<br>"
                "P(sin pareja) = " + f"{t['p_sin']:.4f}" + "<br>"
                "P(&ge; 1 pareja) = 1 &minus; P(sin pareja) = " + f"{t['p_al_menos']:.4f}"
                + f" ({t['p_al_menos']*100:.2f}%)",
                hint="Pulsa para revelar el cálculo"
            )

        if accordion("open_p1", "P1_C", "(C) Montecarlo al rescate"):
            st.markdown(
                "<div class='content-box'>En problemas sencillos como este es posible obtener el resultado "
                "analíticamente. Pero, ¿qué ocurre si el problema es lo suficientemente complejo como para "
                "no poder resolverlo con lápiz y papel? El <b>método de Montecarlo</b> repite el "
                "experimento al azar muchísimas veces y estima la probabilidad como la frecuencia relativa "
                "observada. Experimenta con él en la parte derecha: reparte manos una y otra vez y observa "
                "qué fracción tiene al menos una pareja.</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Simulación de Montecarlo</div>", unsafe_allow_html=True)

        n_sims = st.slider("Número de simulaciones", 1000, 100000,
                           st.session_state["n_cartas"], 1000,
                           key="n_cartas", label_visibility="collapsed")

        with st.container(key="play_p1"):
            if st.button("▶", use_container_width=True, key="btn_play_p1"):
                st.session_state["cartas_res"] = run_cartas(n_sims, seed=42)
                st.rerun()

        res = st.session_state["cartas_res"]
        if res is not None:
            p0 = res["n0"] / n_sims * 100
            pa = (res["n1"] + res["n2"]) / n_sims * 100
            st.markdown(f"<div class='pct-box pct-zero'>0 parejas: {p0:.2f}%</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='pct-box pct-atleast'>&ge; 1 pareja: {pa:.2f}%</div>",
                        unsafe_allow_html=True)
            streamlit_bokeh(histograma_cartas(res, n_sims, chart_theme(dark)),
                            use_container_width=True)
            t = cartas_teorico()
            st.markdown(
                f"<div class='footer-bar'>¿Se parecen los resultados? ¿Cuántas simulaciones crees que "
                f"serán suficientes? (Valor teórico: {t['p_al_menos']*100:.2f}%)</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='footer-bar'>Pulsa el botón para lanzar la simulación.</div>",
                unsafe_allow_html=True
            )

def render_problem_2(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>El nido de agujas de Buffon</b><br><br>"
            "Para explorar un poco más el método de Montecarlo del problema anterior, el conde de Buffon "
            "(1707-1788) ideó un experimento sorprendente: dejar caer agujas sobre un suelo de tablas "
            "paralelas y estimar el número &pi; contando cuántas cruzan una junta.</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p2", "P2_A", "(A) La descripción geométrica"):
            st.markdown(
                "<div class='content-box'>Imagina un suelo con líneas paralelas separadas una distancia d. "
                "Dejamos caer una aguja de longitud &#8467; (con &#8467; &le; d). Su posición queda descrita "
                "por la distancia de su centro a la línea más cercana y por el ángulo &theta; que forma con "
                "las líneas.<br><br><i>Dibuja tú mismo el suelo, una aguja inclinada y marca cuándo "
                "cruzaría una línea. Después compruébalo.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "La aguja cruza una línea &hArr; "
                "dist(centro, línea) &le; (&#8467;&frasl;2) &middot; sin&theta;",
                hint="Pulsa para revelar cuándo cruza"
            )

        if accordion("open_p2", "P2_B", "(B) Lanzando probabilidades"):
            st.markdown(
                "<div class='content-box'>Modelamos el lanzamiento suponiendo que el ángulo &theta; es "
                "uniforme en [0, &pi;] y que el centro cae uniformemente entre dos líneas. Integrando sobre "
                "todos los casos posibles se obtiene la probabilidad de que una aguja cruce una "
                "línea.<br><br><i>Trata de escribir esa probabilidad y, despejando, una fórmula para "
                "&pi;.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(cruce) = "
                "<sup>2&#8467;</sup>&frasl;<sub>&pi;d</sub>"
                " &nbsp;&rArr;&nbsp; "
                "&pi; &asymp; "
                "<sup>2&#8467;N</sup>&frasl;<sub>d&middot;C</sub>"
                " &nbsp;(C cruces de N lanzamientos)"
            )

        if accordion("open_p2", "P2_C", "(C) Hora de lanzar agujas"):
            st.markdown(
                "<div class='content-box'>Como en el problema anterior, simulamos: lanzamos muchas agujas "
                "al azar y contamos cruces. El método de Montecarlo va aún más lejos: si lanzamos muchos "
                "<b>puntos</b> al azar sobre una región y contamos cuántos caen dentro de una forma "
                "complicada, la fracción que la toca aproxima su área.<br><br><i>Trata de escribir esa "
                "aproximación.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "<sup>casos que tocan</sup>&frasl;<sub>casos lanzados</sub> &asymp; "
                "<sup>área de la forma</sup>&frasl;<sub>área total</sub>",
                hint="Pulsa para revelar la aproximación"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Simulación: estimando &pi;</div>", unsafe_allow_html=True)

        n = st.slider("Número de agujas", 200, 50000,
                      st.session_state["n_buffon"], 200,
                      key="n_buffon", label_visibility="collapsed")

        with st.container(key="play_p2"):
            if st.button("▶", use_container_width=True, key="btn_play_p2"):
                st.session_state["buffon_res"] = run_buffon(n, seed=42)
                st.rerun()

        sim = st.session_state["buffon_res"]
        if sim is not None:
            err = abs(sim["pi_est"] - np.pi) / np.pi * 100
            st.markdown(
                f"<div class='result-badge'>&pi; &asymp; {sim['pi_est']:.4f} "
                f"&nbsp;|&nbsp; {sim['ncross']:,} cruces de {sim['n']:,} agujas</div>".replace(",", "."),
                unsafe_allow_html=True
            )
            streamlit_bokeh(buffon_chart(sim, chart_theme(dark)), use_container_width=True)
            st.markdown(
                f"<div class='footer-bar'>Valor real &pi; = 3.1416 (error del {err:.2f}%). "
                f"¿Cuántas agujas crees que hacen falta para acercarte de verdad?</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='footer-bar'>Pulsa el botón para lanzar las agujas.</div>",
                unsafe_allow_html=True
            )

def render_problem_3(dark):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'><b>Regalos mágicos · Tres sabios de Oriente</b><br><br>"
            "Guiados por una estrella —quizá el rastro de un cometa que cruzó el cielo— tres sabios de "
            "Oriente, Melchor, Gaspar y Baltasar, llegan cargados de regalos etiquetados con el nombre de "
            "su destinatario. Pero en el ajetreo de la noche los regalos se mezclan y se reparten al azar. "
            "¿Cuál es la probabilidad de que <b>al menos uno</b> de los tres reciba su propio "
            "regalo?</div>",
            unsafe_allow_html=True
        )

        if accordion("open_p3", "P3_A", "(A) El principio de inclusión-exclusión"):
            st.markdown(
                "<div class='content-box'>Para contar en cuántos repartos acierta al menos uno, sumamos "
                "los casos de cada uno, pero al hacerlo contamos de más los repartos donde aciertan dos o "
                "más a la vez. El <b>principio de inclusión-exclusión</b> corrige ese exceso sumando y "
                "restando alternativamente las intersecciones.</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='formula-box plain'>"
                "&#8473;(&#8899;<sub>i</sub> A<sub>i</sub>) = "
                "&sum;<sub>i</sub> &#8473;(A<sub>i</sub>) &minus; "
                "&sum;<sub>i&lt;j</sub> &#8473;(A<sub>i</sub>&cap;A<sub>j</sub>) + "
                "&hellip; + (&minus;1)<sup>n+1</sup> "
                "&#8473;(&#8898;<sub>i</sub> A<sub>i</sub>)"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion("open_p3", "P3_B", "(B) Tres Reyes"):
            st.markdown(
                "<div class='content-box'>Con n = 3, sea A<sub>i</sub> el suceso \"el Rey i recibe su "
                "regalo\". Cada uno acierta con probabilidad 1/3; cada pareja, con 1/(3&middot;2); y los "
                "tres a la vez, con 1/(3&middot;2&middot;1).<br><br><i>Trata de calcular la "
                "probabilidad.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(al menos uno) = 1 &minus; "
                "<sup>1</sup>&frasl;<sub>2!</sub> + "
                "<sup>1</sup>&frasl;<sub>3!</sub> = "
                "1 &minus; <sup>1</sup>&frasl;<sub>2</sub> + <sup>1</sup>&frasl;<sub>6</sub> = "
                "<sup>2</sup>&frasl;<sub>3</sub> &asymp; 0.667",
                hint="Pulsa para revelar el resultado"
            )

        if accordion("open_p3", "P3_C", "(C) n Reyes"):
            st.markdown(
                "<div class='content-box'>Para n Reyes cualesquiera, la intersección de k sucesos concretos "
                "tiene probabilidad (n&minus;k)!/n!, y hay C(n, k) de ellas. El principio de "
                "inclusión-exclusión deja una suma alternada muy elegante que, sorprendentemente, casi no "
                "depende de n.<br><br><i>Trata de escribir la fórmula general y su límite.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "P(al menos uno) = "
                "&sum;<sub>k=1</sub><sup>n</sup> (&minus;1)<sup>k+1</sup> "
                "<sup>1</sup>&frasl;<sub>k!</sub> "
                "&nbsp;&xrarr;&nbsp; 1 &minus; "
                "<sup>1</sup>&frasl;<sub>e</sub> &asymp; 0.632",
                hint="Pulsa para revelar la fórmula general"
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Demuéstralo por etapas</div>", unsafe_allow_html=True)

        etapa = st.slider("Etapa de la demostración", 1, 3, 1, 1,
                          key="ie_stage", label_visibility="collapsed")

        if etapa == 1:
            st.markdown(
                "<div class='content-box'><b>Etapa 1 · Inclusión.</b><br>"
                "Sumamos las probabilidades individuales: cada uno de los n Reyes acierta su propio regalo "
                "con probabilidad 1/n.<br><br><i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "&sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub>) = "
                "n &middot; <sup>1</sup>&frasl;<sub>n</sub> = 1"
            )
            st.markdown(
                "<div class='content-box'>El resultado es 1 (certeza absoluta), lo cual es absurdo: hemos "
                "contado varias veces los repartos en que aciertan dos o más Reyes a la vez.</div>",
                unsafe_allow_html=True
            )

        elif etapa == 2:
            st.markdown(
                "<div class='content-box'><b>Etapa 2 · Exclusión.</b><br>"
                "Restamos las parejas: que dos Reyes concretos acierten a la vez tiene probabilidad "
                "(n&minus;2)!/n!, y hay C(n, 2) parejas posibles.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "&minus; &sum;<sub>i&lt;j</sub> &#8473;(A<sub>i</sub>&cap;A<sub>j</sub>) = "
                "&minus; C(n,2) &middot; <sup>(n&minus;2)!</sup>&frasl;<sub>n!</sub> = "
                "&minus; <sup>1</sup>&frasl;<sub>2!</sub>"
            )
            st.markdown(
                "<div class='content-box'>Con los tríos volveríamos a sumar, con los cuartetos a restar, y "
                "así sucesivamente: el signo se va alternando.</div>",
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                "<div class='content-box'><b>Etapa 3 · Generalización y conclusión.</b><br>"
                "Cada intersección de k sucesos aporta un término (&minus;1)<sup>k+1</sup>/k!. Sumándolos "
                "todos obtenemos la probabilidad de que al menos un Rey acierte.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i></div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "&#8473;(&#8899;<sub>i</sub> A<sub>i</sub>) = "
                "&sum;<sub>k=1</sub><sup>n</sup> (&minus;1)<sup>k+1</sup> "
                "<sup>1</sup>&frasl;<sub>k!</sub>"
            )
            st.markdown(
                "<div class='content-box'>Y cuando el número de Reyes crece, esta suma converge a un valor "
                "notable, casi independiente de n.</div>",
                unsafe_allow_html=True
            )
            formula_hidden(
                "&#8746; = 1 &minus; <sup>1</sup>&frasl;<sub>e</sub> &asymp; 0.632 &#8718;",
                hint="Pulsa para revelar el límite"
            )

# =============================================================================
# 7. APLICACIÓN PRINCIPAL
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
        st.markdown("<div class='top-bar-title'>C1VIC D4TA · La probabilidad clásica de Laplace</div>",
                    unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    nav = [
        ("INTRO", "Introducción"),
        ("P1", "(I) Cartas de Fournier"),
        ("P2", "(II) La aguja de Buffon"),
        ("P3", "(III) Regalos mágicos"),
    ]
    nav_cols = st.columns(4)
    for col, (page_id, label) in zip(nav_cols, nav):
        is_active = current_page == page_id
        if col.button(label, use_container_width=True,
                      type="primary" if is_active else "secondary",
                      key=f"nav_{page_id}"):
            st.session_state["page"] = page_id
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
