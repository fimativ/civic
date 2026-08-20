#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

import streamlit as st
import numpy as np
from bokeh.plotting import figure
from scipy.stats import binom, norm
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Convergencia y Teoremas Límite")

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
        st.session_state["page"] = "INTRO"
    if "open_step" not in st.session_state:
        st.session_state["open_step"] = "INTRO_A"
    if "ldgn_seed" not in st.session_state:
        st.session_state["ldgn_seed"] = 7

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
# 4. UTILIDADES MATEMÁTICAS
# =============================================================================

def muestra_ldgn(nombre, size, seed):
    """Muestra iid de la distribución elegida para la sección I (LDGN)."""
    rng = np.random.default_rng(seed)
    if nombre.startswith("Moneda"):
        return rng.binomial(1, 0.5, size).astype(float)
    if nombre.startswith("Dado"):
        return rng.integers(1, 7, size).astype(float)
    if nombre.startswith("Uniforme"):
        return rng.uniform(0, 1, size)
    return rng.exponential(1.0, size)  # Exponencial(1)

def mu_ldgn(nombre):
    """Media teórica μ de cada distribución de la sección I."""
    if nombre.startswith("Moneda"):
        return 0.5
    if nombre.startswith("Dado"):
        return 3.5
    if nombre.startswith("Uniforme"):
        return 0.5
    return 1.0

def muestra_gen(nombre, size, seed):
    """Muestra iid de la distribución elegida para la sección III (generalidad del TLC)."""
    rng = np.random.default_rng(seed)
    if nombre.startswith("Uniforme"):
        return rng.uniform(0, 1, size)
    if nombre.startswith("Exponencial"):
        return rng.exponential(1.0, size)
    if nombre.startswith("Bernoulli"):
        return rng.binomial(1, 0.1, size).astype(float)
    # Mezcla bimodal: dos picos separados, cada uno con probabilidad 1/2
    u = rng.uniform(size=size)
    izq = rng.uniform(0.0, 0.6, size)
    der = rng.uniform(4.0, 4.6, size)
    return np.where(u < 0.5, izq, der)

def momentos_gen(nombre):
    """Media μ y desviación típica σ teóricas de cada distribución de la sección III."""
    if nombre.startswith("Uniforme"):
        return 0.5, float(np.sqrt(1 / 12))
    if nombre.startswith("Exponencial"):
        return 1.0, 1.0
    if nombre.startswith("Bernoulli"):
        return 0.1, float(np.sqrt(0.1 * 0.9))
    return 2.3, float(np.sqrt(4.03))  # bimodal

def style_fig(p):
    """Tipografía uniforme de las figuras, igual que en el resto de la serie."""
    p.title.text_font_size = "16px"
    p.xaxis.axis_label_text_font_size = "14px"
    p.yaxis.axis_label_text_font_size = "14px"
    return p

# =============================================================================
# 5. PÁGINAS
# =============================================================================

def render_intro():
    """Introducción: las cuatro convergencias de sucesiones de variables aleatorias."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: Cuatro Maneras de Converger</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Cualquier noción de convergencia de variables aleatorias debe incluir, como caso particular, "
            "la convergencia habitual de números reales. A partir de ahí la Probabilidad distingue cuatro "
            "nociones, cada una con su propio grado de exigencia, y relacionadas entre sí por una jerarquía "
            "de implicaciones que no siempre es total."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "A) Las Cuatro Convergencias"):
            st.markdown("<div class='subsection-title'>A) Definiciones</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Débil o en distribución</b> (Xₙ →D X):<br>"
                "<div class='formula-box'>Fₙ(x) → F(x) &nbsp; en todo punto de continuidad de F</div>"
                "Solo depende de las distribuciones, ni siquiera exige el mismo espacio de probabilidad."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>En probabilidad</b> (Xₙ →P X):<br>"
                "<div class='formula-box'>∀ε&gt;0, &nbsp; P(|Xₙ − X| ≤ ε) → 1</div>"
                "<b>En media cuadrática</b> (Xₙ →m.c. X):<br>"
                "<div class='formula-box'>E[(Xₙ − X)²] → 0</div>"
                "<b>Casi seguro</b> (Xₙ →c.s. X):<br>"
                "<div class='formula-box'>P({ω : Xₙ(ω) → X(ω)}) = 1</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("INTRO_B", "B) Jerarquía e Implicaciones"):
            st.markdown("<div class='subsection-title'>B) Cómo se Relacionan</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Xₙ →c.s. X &nbsp;⟹&nbsp; Xₙ →P X</div>"
                "<div class='formula-box'>Xₙ →m.c. X &nbsp;⟹&nbsp; Xₙ →P X</div>"
                "<div class='formula-box'>Xₙ →P X &nbsp;⟹&nbsp; Xₙ →D X</div>"
                "<b>Casi seguro y media cuadrática no son comparables entre sí:</b> ninguna implica la otra "
                "en general. Cada flecha es estrictamente unidireccional salvo un caso especial."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Cuando el límite X es una <b>constante</b> c ∈ ℝ, converger en probabilidad y converger "
                "en distribución son <b>equivalentes</b>. Es justo lo que necesitan las leyes de los grandes "
                "números: su límite es la esperanza μ, un número, no una variable aleatoria. Por eso la "
                "sección (I) puede hablar indistintamente de \"converger a μ\" sin más matices, "
                "mientras que en la sección (II) el límite es una Normal — ya no una constante — y ahí sí "
                "importa qué tipo de convergencia se usa."
            )

        if accordion_step("INTRO_C", "C) Recorrido del Applet"):
            st.markdown("<div class='subsection-title'>C) Contenido de las Tres Secciones</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                f"<b style='color: {BLUE_LINE};'>(I) Ley débil de los grandes números:</b><br>"
                "¿Hacia dónde va la media muestral X̄ₙ? Convergencia en probabilidad a μ.<br><br>"
                f"<b style='color: {GREEN_LINE};'>(II) Teorema del Límite Central:</b><br>"
                "¿Cómo fluctúa X̄ₙ alrededor de μ? Convergencia en distribución a una Normal, con la "
                "Binomial como caso particular (De Moivre–Laplace).<br><br>"
                f"<b style='color: {ORANGE_ACCENT};'>(III) El TLC para cualquier distribución:</b><br>"
                "¿Es un resultado general? Sí: no depende de la forma de partida, solo de que haya "
                "varianza finita."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Adelanto: Dos Preguntas, Dos Convergencias</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "La misma sucesión X̄ₙ admite dos lecturas asintóticas distintas: hacia dónde va (un número) "
            "y cómo fluctúa a su alrededor (una curva). Ambas aparecen a la vez en esta gráfica."
            "</small></div>",
            unsafe_allow_html=True
        )

        n_prev = st.slider("n: tamaño de la muestra", 1, 400, 60, 1, key="intro_n")
        rng = np.random.default_rng(3)
        datos = rng.uniform(0, 1, (4000, n_prev))
        xbar = datos.mean(axis=1)
        mu, sigma = 0.5, float(np.sqrt(1 / 12))
        z = (xbar - mu) / (sigma / np.sqrt(n_prev))

        p = figure(
            title=f"Distribución de X̄ₙ tipificada (n = {n_prev}), Xᵢ ~ U(0,1)",
            x_axis_label="(X̄ₙ − μ) / (σ/√n)", y_axis_label="densidad",
            width=480, height=340, toolbar_location=None, tools="", x_range=(-4.5, 4.5)
        )
        hist, edges = np.histogram(z, bins=40, density=True, range=(-4.5, 4.5))
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", alpha=0.65, legend_label="Simulación")
        xs = np.linspace(-4.5, 4.5, 300)
        p.line(xs, norm.pdf(xs), line_width=3, color=UBU_RED, legend_label="𝒩(0,1)")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        st.markdown(
            "<div class='content-box'><b>Interpretación:</b> el centrado (restar μ) es la pregunta de la "
            "sección (I); el reescalado por √n y la forma de campana resultante son la pregunta de la "
            "sección (II). Mueve n y observa cómo la campana se ajusta cada vez mejor a 𝒩(0,1).</div>",
            unsafe_allow_html=True
        )

def render_ldgn():
    """Sección I: Ley débil de los grandes números."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Ley Débil de los Grandes Números</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Dada una sucesión de variables aleatorias, llamamos media muestral a X̄ₙ = (X₁+···+Xₙ)/n. "
            "La ley débil de los grandes números dice hacia dónde va esa media cuando n crece: se estabiliza, "
            "de forma no aleatoria, alrededor de su valor esperado."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Enunciado General"):
            st.markdown("<div class='subsection-title'>A) Ley Débil de los Grandes Números</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si las Xₙ están incorrelacionadas, con E[Xₙ] = μₙ y Var(Xₙ) = σₙ², y la varianza media "
                "tiende a cero:<br>"
                "<div class='formula-box'>(1/n²) Σᵢ σᵢ² → 0</div>"
                "entonces la media muestral converge <b>en probabilidad</b> a la media teórica:<br>"
                "<div class='formula-box'>X̄ₙ − (1/n)Σᵢ μᵢ &nbsp;→P&nbsp; 0</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "B) Corolario i.i.d. y Teorema de Bernoulli"):
            st.markdown("<div class='subsection-title'>B) El Caso Idénticamente Distribuido</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si además μₙ ≡ μ y σₙ² ≡ σ² (finita), la fórmula se simplifica a lo que se conoce como la "
                "LDGN:<br>"
                "<div class='formula-box'>X̄ₙ &nbsp;→P&nbsp; μ</div>"
                "<b>Teorema de Bernoulli (1713):</b> si Xᵢ son indicadores de un suceso A "
                "en ensayos independientes, X̄ₙ es la proporción muestral de éxitos y μ = P(A). El teorema "
                "afirma que esa proporción converge en probabilidad a la probabilidad teórica del suceso; "
                "el fundamento de interpretar la probabilidad como frecuencia relativa a largo plazo."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_C", "C) Por Qué Funciona: la Desigualdad de Chebyshev"):
            st.markdown("<div class='subsection-title'>C) El Argumento (Caso i.i.d.)</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Como en el <b>Tema 4</b>, la desigualdad de Chebyshev acota la probabilidad de alejarse de "
                "la media usando solo la varianza. Aplicada a X̄ₙ, cuya varianza es Var(X̄ₙ) = σ²/n:<br>"
                "<div class='formula-box'>P(|X̄ₙ − μ| ≥ ε) &nbsp;≤&nbsp; σ² / (nε²)</div>"
                "El miembro derecho tiende a 0 cuando n → ∞ para cualquier ε &gt; 0 fijo, que es exactamente "
                "la definición de X̄ₙ →P μ."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Este mismo argumento explica por qué en la simulación de la derecha la anchura típica de "
                "la trayectoria decrece como 1/√n en vez de como 1/n: la desigualdad acota la <b>probabilidad</b> "
                "de un error dado, no el error en sí. La sección (II) precisa exactamente cuál es esa forma "
                "de fluctuación."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación: Evolución de la Media Muestral</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Se genera una trayectoria de X̄ₙ frente a n. Observa cómo se estabiliza alrededor de μ aunque "
            "nunca deje de oscilar."
            "</small></div>",
            unsafe_allow_html=True
        )

        dist_ldgn = st.radio(
            "Distribución de cada Xᵢ:",
            ["Moneda: Bernoulli(0.5)", "Dado: uniforme discreta {1..6}", "Uniforme(0,1)", "Exponencial(λ=1)"],
            key="ldgn_dist"
        )
        n_max = st.slider("n máximo de la trayectoria", 10, 2000, 500, 10, key="ldgn_nmax")
        if st.button("🎲 Nueva simulación", key="ldgn_reroll"):
            st.session_state["ldgn_seed"] += 1

        seed = st.session_state["ldgn_seed"]
        muestras = muestra_ldgn(dist_ldgn, n_max, seed)
        xbar_traj = np.cumsum(muestras) / np.arange(1, n_max + 1)
        mu = mu_ldgn(dist_ldgn)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third metric-a'>X̄ₙ final<br>{xbar_traj[-1]:.4f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third metric-c'>μ (límite)<br>{mu:.4f}</div>",
                        unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-b'>|X̄ₙ − μ|<br>{abs(xbar_traj[-1]-mu):.4f}</div>",
                        unsafe_allow_html=True)

        p = figure(
            title=f"Trayectoria de X̄ₙ, n = 1..{n_max}",
            x_axis_label="n", y_axis_label="X̄ₙ",
            width=480, height=340, toolbar_location=None, tools="", x_axis_type="log"
        )
        ns = np.arange(1, n_max + 1)
        p.line(ns, xbar_traj, line_width=2, color=BLUE_LINE, legend_label="Trayectoria de X̄ₙ")
        p.line([1, n_max], [mu, mu], line_width=2.5, color=UBU_RED, line_dash="dashed",
               legend_label="μ (límite)")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        st.markdown(
            "<div class='content-box'><b>Interpretación:</b> el eje n está en escala logarítmica para que "
            "se aprecien tanto las primeras oscilaciones (grandes) como el aplanamiento final (pequeño). "
            "Pulsa \"Nueva simulación\" para comprobar que, aunque la trayectoria concreta cambia, el destino "
            "μ es siempre el mismo.</div>",
            unsafe_allow_html=True
        )

def render_tlc():
    """Sección II: Teorema Central del Límite (Normal y Binomial)."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) Teorema Central del Límite</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La LDGN dice hacia dónde va X̄ₙ, pero no de qué tamaño ni de qué forma es el error. El TLC "
            "responde: si en vez de dividir por n se divide por √n, el resultado no se derrumba a 0 ni "
            "diverge — converge en distribución a una Normal."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Teorema de Lindeberg–Lévy"):
            st.markdown("<div class='subsection-title'>A) Enunciado</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si Xₙ son i.i.d. con esperanza μ y varianza finita σ² &gt; 0, la media tipificada converge "
                "en distribución a la Normal estándar:<br>"
                "<div class='formula-box'>(X̄ₙ − μ) / (σ/√n) &nbsp;→D&nbsp; 𝒩(0,1)</div>"
                "En la práctica se usa como aproximación cuando <b>n ≥ 30</b>:<br>"
                "<div class='formula-box'>P(Sₙ ≤ x) &nbsp;≃&nbsp; Φ( (x − nμ) / (σ√n) )</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) De Moivre–Laplace: la Binomial como caso particular"):
            st.markdown("<div class='subsection-title'>B) Por qué la Binomial encaja aquí</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Una B(n, p) es, por construcción, la suma de n Bernoulli(p) independientes. Aplicando "
                "Lindeberg–Lévy con μ = p y σ² = p(1−p):<br>"
                "<div class='formula-box'>(X − np) / √(np(1−p)) &nbsp;→D&nbsp; 𝒩(0,1)</div>"
                "La aproximación se considera aceptable cuando <b>np ≥ 5</b> y <b>n(1−p) ≥ 5</b>. Cuanto "
                "más cerca esté p de 0 o de 1, más ensayos hacen falta para que la campana sea una buena "
                "aproximación de los escalones de la binomial."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Con p muy pequeña y n moderado la binomial es muy asimétrica y la aproximación normal falla "
                "visiblemente cerca de 0; en ese régimen conviene la aproximación de Poisson en su lugar. "
                "El TLC normal y la aproximación de Poisson cubren regímenes distintos del mismo objeto: la "
                "binomial."
            )

        if accordion_step("P2_C", "C) Uso Práctico: la Función Φ"):
            st.markdown("<div class='subsection-title'>C) Calcular sin Conocer la Distribución Exacta</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El TLC permite aproximar probabilidades de sumas de variables aleatorias sin calcular su "
                "distribución exacta, con solo conocer μ y σ. Usa la calculadora de la derecha para "
                "comprobar cómo z = (x − nμ)/(σ√n) determina Φ(z)."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación: Binomial(n,p) frente a Normal</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Compara la función de masa exacta de B(n,p) con la densidad Normal que predice De Moivre–Laplace."
            "</small></div>",
            unsafe_allow_html=True
        )

        n = st.slider("n: número de ensayos", 2, 300, 40, 1, key="tlc_n")
        pp = st.slider("p: probabilidad de éxito", 0.02, 0.98, 0.30, 0.01, key="tlc_p")

        mu_b, sigma_b = n * pp, float(np.sqrt(n * pp * (1 - pp)))
        lo = max(0, int(np.floor(mu_b - 4 * sigma_b)))
        hi = min(n, int(np.ceil(mu_b + 4 * sigma_b)))
        ks = np.arange(lo, hi + 1)
        pmf = binom.pmf(ks, n, pp)
        xs = np.linspace(lo, hi, 300)

        p = figure(
            title=f"B({n}, {pp:g}) ; μ = {mu_b:.2f}, σ = {sigma_b:.2f}",
            x_axis_label="k", y_axis_label="P(X = k) / densidad",
            width=480, height=320, toolbar_location=None, tools=""
        )
        p.vbar(x=ks, top=pmf, width=0.75, fill_color=BLUE_LINE, line_color="white",
               alpha=0.75, legend_label="P(X = k), Binomial")
        p.line(xs, norm.pdf(xs, mu_b, sigma_b), line_width=3, color=UBU_RED,
               legend_label="Densidad 𝒩(np, √np(1−p))")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        cond1 = n >= 30
        cond2 = n * pp >= 5
        cond3 = n * (1 - pp) >= 5
        c1, c2, c3 = st.columns(3)
        with c1:
            cls = "result-likely" if cond1 else "result-unlikely"
            st.markdown(f"<div class='metric-box metric-third {cls}'>n ≥ 30<br>n = {n}</div>", unsafe_allow_html=True)
        with c2:
            cls = "result-likely" if cond2 else "result-unlikely"
            st.markdown(f"<div class='metric-box metric-third {cls}'>np ≥ 5<br>np = {mu_b:.1f}</div>", unsafe_allow_html=True)
        with c3:
            cls = "result-likely" if cond3 else "result-unlikely"
            st.markdown(f"<div class='metric-box metric-third {cls}'>n(1−p) ≥ 5<br>= {n*(1-pp):.1f}</div>", unsafe_allow_html=True)

        st.markdown("<div class='subsection-title'>Calculadora: P(Sₙ ≤ x) ≈ Φ(z)</div>", unsafe_allow_html=True)
        n_c = st.slider("n", 1, 500, 50, 1, key="calc_n")
        mu_c = st.slider("μ", -5.0, 5.0, 0.0, 0.1, key="calc_mu")
        sigma_c = st.slider("σ", 0.1, 5.0, 1.0, 0.1, key="calc_sigma")
        x_c = st.slider("x", -20.0, 20.0, 2.0, 0.1, key="calc_x")

        z = (x_c - n_c * mu_c) / (sigma_c * np.sqrt(n_c))
        prob = float(norm.cdf(z))
        st.markdown(
            f"<div class='formula-box'>P(S<sub>{n_c}</sub> ≤ {x_c:.1f}) ≃ Φ({z:.3f}) = "
            f"<b style='color:{UBU_RED};'>{prob:.4f}</b></div>",
            unsafe_allow_html=True
        )

def render_general():
    """Sección III: el TLC para cualquier distribución de partida."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) El TLC para cualquier distribución</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "El teorema de Lindeberg–Lévy no menciona en ningún momento la forma de la distribución de "
            "partida: solo pide independencia, idéntica distribución y varianza finita. Da igual si cada "
            "Xᵢ es simétrica, muy asimétrica o incluso bimodal, la media tipificada siempre termina "
            "pareciéndose a una campana."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Las hipótesis (y lo que NO se pide)"):
            st.markdown("<div class='subsection-title'>A) Solo tres condiciones</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Se exige:</b><br>"
                "• Independencia entre las Xᵢ<br>"
                "• Idéntica distribución (o, en la versión de Lindeberg, una condición más débil sobre los "
                "momentos)<br>"
                "• Varianza σ² finita<br><br>"
                "<b>No se exige</b> ninguna forma concreta para la distribución de cada Xᵢ: puede ser "
                "discreta o continua, simétrica o no, acotada o no. El límite 𝒩(0,1) es siempre el mismo."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_B", "B) Catálogo: de lo feo a la campana"):
            st.markdown("<div class='subsection-title'>B) Ejemplos con formas muy distintas</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "• <b>Uniforme(0,1):</b> simétrica y acotada<br>"
                "• <b>Exponencial(1):</b> muy asimétrica, cola larga a la derecha<br>"
                "• <b>Bernoulli(0.1):</b> casi degenerada, solo dos valores posibles y muy desequilibrados<br>"
                "• <b>Mezcla bimodal:</b> dos picos separados, ni siquiera unimodal<br><br>"
                "Con n = 1 el histograma de la derecha reproduce fielmente cada una de estas formas. "
                "Aumenta n y observa cómo todas convergen al mismo límite."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_C", "C) Por qué importa: Inferencia sin conocer la población"):
            st.markdown(
                "<div class='content-box'>"
                "Como el límite no depende de la forma de partida, no hace falta conocer la distribución "
                "exacta de la población para aproximar el comportamiento de una media muestral grande: "
                "basta con μ y σ. Esto es lo que convierte al TLC en la herramienta central de la Inferencia "
                "Estadística,intervalos de confianza y contrastes de hipótesis para la media se apoyan "
                "en él sin necesidad de suponer normalidad de los datos originales."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Encaje con la introducción: la LDGN usa convergencia <b>en probabilidad</b> (el destino, "
                "un número); el TLC usa convergencia <b>en distribución</b> (la forma de la fluctuación, "
                "una curva). Son necesariamente convergencias distintas: el límite del TLC, la Normal, no "
                "es una constante, así que aquí probabilidad y distribución ya no son equivalentes."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación: de cualquier forma a la campana</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Elige una distribución de partida y aumenta n para ver cómo se olvida su forma original."
            "</small></div>",
            unsafe_allow_html=True
        )

        dist_gen = st.radio(
            "Distribución de cada Xᵢ:",
            ["Uniforme(0,1): simétrica", "Exponencial(1): muy asimétrica",
             "Bernoulli(0.1): casi degenerada", "Mezcla bimodal: dos picos separados"],
            key="gen_dist"
        )
        n_gen = st.slider("n: tamaño de la muestra en cada media", 1, 60, 2, 1, key="gen_n")

        mu_g, sigma_g = momentos_gen(dist_gen)
        base = muestra_gen(dist_gen, 4000, seed=17)

        p_base = figure(
            title="Forma de una única Xᵢ",
            x_axis_label="valor", y_axis_label="densidad",
            width=480, height=180, toolbar_location=None, tools=""
        )
        h0, e0 = np.histogram(base, bins=40, density=True)
        p_base.quad(top=h0, bottom=0, left=e0[:-1], right=e0[1:],
                    fill_color=ORANGE_ACCENT, line_color="white", alpha=0.75)
        streamlit_bokeh(style_fig(p_base))

        M = 3000
        muestras = muestra_gen(dist_gen, (M, n_gen), seed=23)
        xbar = muestras.mean(axis=1)
        z = (xbar - mu_g) / (sigma_g / np.sqrt(n_gen))

        p = figure(
            title=f"(X̄ₙ − μ)/(σ/√n) sobre {M} repeticiones, n = {n_gen}",
            x_axis_label="z", y_axis_label="densidad",
            width=480, height=320, toolbar_location=None, tools="", x_range=(-4.5, 4.5)
        )
        hist, edges = np.histogram(z, bins=36, density=True, range=(-4.5, 4.5))
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color=BLUE_LINE, line_color="white", alpha=0.65, legend_label="Medias tipificadas")
        xs = np.linspace(-4.5, 4.5, 300)
        p.line(xs, norm.pdf(xs), line_width=3, color=UBU_RED, legend_label="𝒩(0,1), el límite universal")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        st.markdown(
            "<div class='content-box'><b>Interpretación:</b> con n = 1 el histograma azul coincide con la "
            "forma de partida (arriba), por asimétrica o extraña que sea. A medida que n crece, esa forma "
            "se olvida y solo queda 𝒩(0,1), el mismo límite para las cuatro distribuciones del menú.</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 6. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Convergencia de sucesiones y Teoremas Límite</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO", "open_step": "INTRO_A"}); st.rerun()
    if nav_col2.button("(I) LDGN", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) TLC", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) ¿Es general?", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_ldgn,
        "P2": render_tlc,
        "P3": render_general,
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
