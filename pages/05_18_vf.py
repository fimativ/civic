import streamlit as st
import numpy as np
from bokeh.plotting import figure
from scipy.stats import binom, poisson, norm
from scipy.special import comb
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Reproductividad y Familias de Distribuciones")

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
# 4. UTILIDADES MATEMÁTICAS
# =============================================================================

def pmf_suma(pmf1, pmf2):
    """Distribución exacta de la suma de dos variables independientes no negativas."""
    return np.convolve(pmf1, pmf2)

def vandermonde_terminos(n, m, s):
    """Términos C(n,k)·C(m,s−k) de la identidad de Vandermonde."""
    ks = np.arange(max(0, s - m), min(n, s) + 1)
    return ks, np.array([comb(n, k, exact=True) * comb(m, s - k, exact=True) for k in ks])

def cdf_base(nombre, x, par):
    """Función de distribución de la familia base elegida."""
    if nombre == "Uniforme U(0,1)":
        return np.clip(x, 0, 1)
    if nombre == "Exponencial Exp(λ)":
        return np.where(x > 0, 1 - np.exp(-par * np.maximum(x, 0)), 0.0)
    return norm.cdf(x)

def pdf_base(nombre, x, par):
    """Función de densidad de la familia base elegida."""
    if nombre == "Uniforme U(0,1)":
        return np.where((x >= 0) & (x <= 1), 1.0, 0.0)
    if nombre == "Exponencial Exp(λ)":
        return np.where(x > 0, par * np.exp(-par * np.maximum(x, 0)), 0.0)
    return norm.pdf(x)

def muestra_base(nombre, par, forma, seed):
    """Muestra de la familia base con la forma pedida."""
    rng = np.random.default_rng(seed)
    if nombre == "Uniforme U(0,1)":
        return rng.uniform(0, 1, forma)
    if nombre == "Exponencial Exp(λ)":
        return rng.exponential(1 / par, forma)
    return rng.standard_normal(forma)

def rango_base(nombre, par):
    """Rejilla de representación adecuada a cada familia."""
    if nombre == "Uniforme U(0,1)":
        return np.linspace(-0.1, 1.1, 400)
    if nombre == "Exponencial Exp(λ)":
        return np.linspace(0, 6 / par, 400)
    return np.linspace(-4, 4, 400)

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
    """Introducción: reproductividad de familias de distribuciones."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: Reproductividad y Familias de Distribuciones</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Una familia de distribuciones es <b>reproductiva</b> si la suma de variables independientes de "
            "esa familia sigue perteneciendo a la misma familia, con los parámetros combinados de forma "
            "natural. No es una propiedad automática: la mayoría de las familias no la tienen, y cuando "
            "aparece es porque hay una estructura detrás que la explica."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "A) Qué significa que una familia sea reproductiva"):
            st.markdown("<div class='subsection-title'>A) Definición</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Una familia de distribuciones es "
                "<b>reproductiva respecto a un parámetro τ</b> si la suma de variables independientes de "
                "esa misma familia resulta en otra variable de la familia cuyo parámetro es la suma de "
                "los originales:<br>"
                "<div class='formula-box'>X ~ F<sub>τ₁</sub>, &nbsp; Y ~ F<sub>τ₂</sub>, &nbsp; X ⊥ Y "
                "&nbsp;⟹&nbsp; X + Y ~ F<sub>τ₁ + τ₂</sub></div>"
                "Dos condiciones son imprescindibles y suele olvidarse la segunda:<br>"
                "• <b>Independencia</b> entre los sumandos<br>"
                "• Que <b>compartan</b> los parámetros que no se suman (por ejemplo la misma p en la "
                "binomial)"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Sin independencia todo se rompe: si Y = X con X ~ B(n, p), entonces X + Y = 2X solo toma "
                "valores pares y no puede ser una B(2n, p). Y sin compartir p, la suma de B(n, p₁) y "
                "B(m, p₂) con p₁ ≠ p₂ tampoco es binomial, como se verá en la sección (I)."
            )

        if accordion_step("INTRO_B", "B) Catálogo de familias y por qué algunas fallan"):
            st.markdown("<div class='subsection-title'>B) Qué Familias Reproducen</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b style='color: #2e7d32;'>Reproductivas bajo la suma:</b><br>"
                "• <b>Binomial</b>, reproductiva en n: &nbsp; B(n₁, p) + B(n₂, p) = B(n₁ + n₂, p)<br>"
                "• <b>Poisson</b>, reproductiva en λ: &nbsp; 𝒫(λ₁) + 𝒫(λ₂) = 𝒫(λ₁ + λ₂)<br>"
                "• <b>Binomial negativa</b>, reproductiva en n: &nbsp; "
                "NB(n₁, p) + NB(n₂, p) = NB(n₁ + n₂, p)<br>"
                "• <b>Gamma</b>, reproductiva en p: &nbsp; γ(p₁, a) + γ(p₂, a) = γ(p₁ + p₂, a)<br>"
                "• <b>Normal</b>, reproductiva en μ y σ²: &nbsp; "
                "𝒩(μ₁, σ₁) + 𝒩(μ₂, σ₂) = 𝒩(μ₁ + μ₂, √(σ₁² + σ₂²))<br><br>"
                "Todas exigen independencia y que los <b>parámetros secundarios</b> coincidan: "
                "la misma p en la binomial y en la binomial negativa, la misma a en la gamma.<br><br>"
                "<b style='color: #d32f2f;'>No reproductivas:</b><br>"
                "• U(0,1) + U(0,1) es triangular, no uniforme<br>"
                "• B(n, p₁) + B(m, p₂) con p₁ ≠ p₂ no es binomial"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>El patrón.</b> Las familias que reproducen tienen un parámetro que <b>cuenta</b> algo "
                "aditivo:<br>"
                "• Binomial: número de ensayos<br>"
                "• Poisson: tasa de ocurrencias<br>"
                "• Gamma: número de etapas<br>"
                "• Binomial negativa: número de éxitos que se esperan<br><br>"
                "Cuando ese parámetro existe, sumar variables equivale a juntar los contadores y la familia "
                "se conserva. La uniforme no cuenta nada: no hay ningún parámetro que pueda absorber la "
                "suma, y por eso aparece una familia nueva."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "La exponencial no reproduce bajo la suma, pero sí bajo el <b>mínimo</b>: el mínimo de "
                "exponenciales independientes vuelve a ser exponencial. Ese es el puente entre las dos "
                "mitades de este applet y se desarrolla en la sección (III)."
            )

        if accordion_step("INTRO_C", "C) Las dos formas de combinar de este Applet"):
            st.markdown("<div class='subsection-title'>C) Sumar frente a Ordenar</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>Sumar</b> (sección I): se agregan las variables y la pregunta es qué familia resulta. "
                "La herramienta es el cálculo directo de la distribución de la suma, y el caso estrella es la "
                "binomial, cuya demostración combinatoria conduce a la identidad de Vandermonde.<br><br>"
                "<b>Ordenar</b> (secciones II y III): no se agregan valores, se selecciona el mayor o el "
                "menor. La herramienta ya no es el cálculo directo sino la <b>función de distribución</b>, "
                "porque un máximo o un mínimo se traducen directamente en sucesos sobre todas las "
                "componentes a la vez.<br><br>"
                "Son dos operaciones distintas y cada una tiene sus propias familias reproductivas. "
                "La exponencial es el ejemplo de que una familia puede fallar en la primera y funcionar "
                "en la segunda."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: ¿Reproduce esta familia?</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Se obtiene la distribución exacta de X + Y y se compara con la candidata " 
            "de la misma familia. Si coinciden, la familia reproduce."
            "</small></div>",
            unsafe_allow_html=True
        )

        familia = st.radio(
            "Familia de partida:",
            ["Binomial con la misma p", "Poisson", "Binomial con p distintas"],
            key="intro_fam"
        )

        if familia == "Poisson":
            lam1 = st.slider("λ₁: Tasa de la primera Poisson", 0.5, 8.0, 3.0, 0.5, key="intro_l1")
            lam2 = st.slider("λ₂: Tasa de la segunda Poisson", 0.5, 8.0, 2.0, 0.5, key="intro_l2")
            kmax = int(lam1 + lam2 + 6 * np.sqrt(lam1 + lam2)) + 2
            ks = np.arange(kmax + 1)
            pmf = pmf_suma(poisson.pmf(ks, lam1), poisson.pmf(ks, lam2))[:kmax + 1]
            teorica = poisson.pmf(ks, lam1 + lam2)
            nombre_teorica = f"𝒫({lam1 + lam2:g})"
        elif familia == "Binomial con la misma p":
            n1 = st.slider("n: Ensayos de la primera binomial", 1, 30, 8, 1, key="intro_n1")
            n2 = st.slider("m: Ensayos de la segunda binomial", 1, 30, 12, 1, key="intro_n2")
            pp = st.slider("p: Probabilidad de éxito común", 0.05, 0.95, 0.4, 0.05, key="intro_p")
            ks = np.arange(n1 + n2 + 1)
            pmf = pmf_suma(binom.pmf(np.arange(n1 + 1), n1, pp),
                           binom.pmf(np.arange(n2 + 1), n2, pp))
            teorica = binom.pmf(ks, n1 + n2, pp)
            nombre_teorica = f"B({n1 + n2}, {pp:g})"
        else:
            n1 = st.slider("n: Ensayos de la primera binomial", 1, 30, 10, 1, key="intro_n1b")
            n2 = st.slider("m: Ensayos de la segunda binomial", 1, 30, 10, 1, key="intro_n2b")
            p_a = st.slider("p₁: Probabilidad de la primera", 0.05, 0.95, 0.15, 0.05, key="intro_pa")
            p_b = st.slider("p₂: Probabilidad de la segunda", 0.05, 0.95, 0.85, 0.05, key="intro_pb")
            ks = np.arange(n1 + n2 + 1)
            pmf = pmf_suma(binom.pmf(np.arange(n1 + 1), n1, p_a),
                           binom.pmf(np.arange(n2 + 1), n2, p_b))
            p_media = (n1 * p_a + n2 * p_b) / (n1 + n2)
            teorica = binom.pmf(ks, n1 + n2, p_media)
            nombre_teorica = f"B({n1 + n2}, {p_media:.3f}) ajustada por la media"

        error = float(np.max(np.abs(pmf - teorica)))

        p = figure(
            title="Distribución exacta de X + Y frente a la candidata",
            x_axis_label="s", y_axis_label="P(X + Y = s)",
            width=450, height=330, toolbar_location=None, tools=""
        )
        p.vbar(x=ks, top=pmf, width=0.7, fill_color=BLUE_LINE, line_color="white",
               alpha=0.75, legend_label="Distribución de X + Y")
        p.scatter(ks, teorica, size=9, color=UBU_RED, legend_label=nombre_teorica)
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        clase = "result-likely" if error < 1e-10 else "result-unlikely"
        veredicto = "Coinciden: la familia reproduce" if error < 1e-10 else "No coinciden: no reproduce"
        st.markdown(
            f"<div class='metric-box {clase}'>{veredicto}<br>"
            f"discrepancia máxima = {error:.2e}</div>",
            unsafe_allow_html=True
        )

        if familia == "Binomial con p distintas":
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> por muy bien que se elija la p de la "
                "binomial candidata, incluso igualando la media, las dos distribuciones no coinciden. "
                "La suma tiene una forma que ninguna binomial puede reproducir. Cuanto más separadas "
                "estén p₁ y p₂, mayor la discrepancia: la reproductividad exige compartir p.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> los puntos rojos caen exactamente sobre "
                "las barras para todos los valores de s y para cualquier combinación de parámetros. "
                "La discrepancia es del orden del error de redondeo, no una aproximación.</div>",
                unsafe_allow_html=True
            )

def render_vandermonde():
    """Sección II: Problema 058, la suma de binomiales y la identidad de Vandermonde."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Problema 058: Vandermonde en Bernoulli</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Supongamos que X ∼ B(n, p) y Y ∼ B(m, p). ¿Cuál es la distribución de X + Y?"
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Argumento directo: contar ensayos de Bernoulli"):
            st.markdown("<div class='subsection-title'>A) La Demostración de una línea</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Una B(n, p) es, por construcción, el número de éxitos en n ensayos de Bernoulli "
                "independientes con probabilidad p:<br>"
                "Al ser X e Y independientes, los n + m ensayos son todos independientes entre sí y todos "
                "tienen la misma probabilidad de éxito p. Por tanto X + Y cuenta los éxitos de n + m "
                "ensayos de Bernoulli independientes con parámetro p:<br>"
                "<div class='formula-box'>X + Y ~ B(n + m, p)</div>"
                "Aquí se ve con claridad por qué la p debe ser común: si no lo fuera, los n + m ensayos no "
                "serían idénticamente distribuidos y el recuento no sería binomial."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "B) Demostración directa: Aparece Vandermonde"):
            st.markdown("<div class='subsection-title'>B) La Vía Combinatoria</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "El suceso {X + Y = s} se descompone en los sucesos disjuntos {X = k, Y = s − k}, "
                "así que por independencia P(X + Y = s) = Σ<sub>k</sub> P(X = k)·P(Y = s − k). Aplicándolo "
                "a las dos funciones de masa binomiales:<br>"
                "<div class='formula-box'>P(X + Y = s) = Σ<sub>k</sub> "
                "C(n,k) p<sup>k</sup>(1−p)<sup>n−k</sup> · "
                "C(m,s−k) p<sup>s−k</sup>(1−p)<sup>m−s+k</sup></div>"
                "Los exponentes de p suman siempre s y los de (1−p) suman siempre n + m − s, "
                "independientemente de k. Eso permite <b>sacar factor común</b>:<br>"
                "<div class='formula-box'>P(X + Y = s) = p<sup>s</sup>(1−p)<sup>n+m−s</sup> · "
                "Σ<sub>k</sub> C(n,k)·C(m,s−k)</div>"
                "El resultado ya tiene la forma de una binomial salvo el coeficiente. Y ese sumatorio es "
                "exactamente la <b>identidad de Vandermonde</b>."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Que la p pueda salir de factor común es <b>toda</b> la demostración. Si las "
                "probabilidades fuesen p₁ ≠ p₂, los exponentes serían p₁<sup>k</sup>p₂<sup>s−k</sup>, que "
                "depende de k y no se puede extraer del sumatorio. La estructura se desmorona exactamente "
                "en ese paso, y de ahí que la suma deje de ser binomial."
            )

        if accordion_step("P1_C", "C) La Identidad de Vandermonde"):
            st.markdown("<div class='subsection-title'>C) Enunciado y Argumento Combinatorio</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Σ<sub>k</sub> C(n,k)·C(m,s−k) = C(n+m,s)</div>"
                "<b>Demostración: </b> Se quiere elegir un comité de s personas de un "
                "grupo con n hombres y m mujeres.<br><br>"
                "• <b>Contando de golpe:</b> hay n + m personas y se eligen s, es decir C(n+m,s) formas.<br>"
                "• <b>Contando por casos:</b> si el comité tiene k hombres, hay C(n,k) formas de elegirlos "
                "y C(m,s−k) de completar con mujeres. Sumando sobre todos los k posibles se obtiene el "
                "miembro izquierdo.<br><br>"
                "Ambos recuentos cuentan lo mismo, así que son iguales. Sustituyendo en el apartado B):<br>"
                "<div class='formula-box'>P(X + Y = s) = C(n+m,s) p<sup>s</sup>(1−p)<sup>n+m−s</sup></div>"
                "que es la función de masa de una B(n + m, p)."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Verificar Vandermonde</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Se comparan el cálculo exacto, una simulación de X + Y y la B(n+m, p) teórica. "
            "Abajo se desglosa el sumatorio de Vandermonde término a término."
            "</small></div>",
            unsafe_allow_html=True
        )

        n = st.slider("n: Ensayos de X ~ B(n, p)", 1, 25, 6, 1, key="p1_n")
        m = st.slider("m: Ensayos de Y ~ B(m, p)", 1, 25, 9, 1, key="p1_m")
        pp = st.slider("p: Probabilidad de éxito común", 0.05, 0.95, 0.45, 0.05, key="p1_p")
        n_sim = st.slider("Número de repeticiones de la simulación", 1000, 50000, 20000, 1000,
                          key="p1_sim")

        ks = np.arange(n + m + 1)
        pmf = pmf_suma(binom.pmf(np.arange(n + 1), n, pp),
                       binom.pmf(np.arange(m + 1), m, pp))
        teorica = binom.pmf(ks, n + m, pp)

        rng = np.random.default_rng(4)
        sim = rng.binomial(n, pp, n_sim) + rng.binomial(m, pp, n_sim)
        frec = np.bincount(sim, minlength=n + m + 1)[:n + m + 1] / n_sim

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third metric-a'>𝔼[X+Y] = (n+m)p<br>"
                        f"{(n + m) * pp:.2f}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third metric-b'>Var = (n+m)p(1−p)<br>"
                        f"{(n + m) * pp * (1 - pp):.2f}</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-c'>Media simulada<br>"
                        f"{sim.mean():.2f}</div>", unsafe_allow_html=True)

        p = figure(
            title=f"X + Y con X ~ B({n}, {pp:g}) e Y ~ B({m}, {pp:g})",
            x_axis_label="s", y_axis_label="P(X + Y = s)",
            width=450, height=330, toolbar_location=None, tools=""
        )
        p.vbar(x=ks, top=frec, width=0.7, fill_color=BLUE_LINE, line_color="white",
               alpha=0.6, legend_label="Simulación")
        p.line(ks, pmf, line_width=3, color=GREEN_LINE, legend_label="Cálculo exacto")
        p.scatter(ks, teorica, size=9, color=UBU_RED, legend_label=f"B({n + m}, {pp:g})")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        err_pmf = float(np.max(np.abs(pmf - teorica)))
        st.markdown(
            f"<div class='metric-box result-likely'>X + Y = B({n + m}, {pp:g})<br>"
            f"discrepancia máxima = {err_pmf:.2e}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='subsection-title'>Desglose de la Identidad</div>",
                    unsafe_allow_html=True)
        s_sel = st.slider("s: Valor en el que verificar la identidad", 0, n + m,
                          min(n, (n + m) // 2), 1, key="p1_s")

        kk, terminos = vandermonde_terminos(n, m, s_sel)
        total = int(terminos.sum())
        objetivo = int(comb(n + m, s_sel, exact=True))

        filas = "<br>".join(
            f"k = {k}: &nbsp; C({n},{k})·C({m},{s_sel - k}) = "
            f"{comb(n, k, exact=True)} · {comb(m, s_sel - k, exact=True)} = {t}"
            for k, t in zip(kk, terminos)
        )
        st.markdown(
            f"<div class='content-box'>{filas}<br><br>"
            f"<b>Suma = {total}</b> &nbsp;&nbsp; y &nbsp;&nbsp; <b>C({n + m},{s_sel}) = {objetivo}</b>"
            f"</div>",
            unsafe_allow_html=True
        )

        p2 = figure(
            title=f"Términos del sumatorio para s = {s_sel}",
            x_axis_label="k (éxitos aportados por X)", y_axis_label="C(n,k)·C(m,s−k)",
            width=450, height=280, toolbar_location=None, tools=""
        )
        p2.vbar(x=kk, top=terminos.astype(float), width=0.7,
                fill_color=ORANGE_ACCENT, line_color="white", alpha=0.85)
        streamlit_bokeh(style_fig(p2))

        clase = "result-likely" if total == objetivo else "result-unlikely"
        st.markdown(
            f"<div class='metric-box {clase}'>Identidad de Vandermonde<br>"
            f"{total} = {objetivo} &nbsp; {'✓' if total == objetivo else '✗'}</div>",
            unsafe_allow_html=True
        )

def render_max_min():
    """Sección III: Problema 087, distribuciones del máximo y del mínimo."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) Problema 087: Máximo y Mínimo</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Sean X₁, . . . , Xₙ variables aleatorias independientes e idénticamente distribuidas. "
            "Obtener la distribución de máx{X₁, . . . , Xₙ}."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Demostración del Máximo"):
            st.markdown("<div class='subsection-title'>A) Demostración</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea Y = máx{X₁, . . . , Xₙ}.<br>"
                "<div class='formula-box'>F<sub>Y</sub>(y) = P(Y ≤ y) = "
                "P(máx{X₁, . . . , Xₙ} ≤ y)</div>"
                "Dado que el máximo es menor que y si y sólo si todas lo son:<br>"
                "<div class='formula-box'>F<sub>Y</sub>(y) = P(X₁ ≤ y, . . . , Xₙ ≤ y)</div>"
                "Por independencia:<br>"
                "<div class='formula-box'>F<sub>Y</sub>(y) = P(X₁ ≤ y) · · · P(Xₙ ≤ y)</div>"
                "Al ser idénticamente distribuidas con función F<sub>X</sub>(y):<br>"
                "<div class='formula-box'>F<sub>Y</sub>(y) = [F<sub>X</sub>(y)]<sup>n</sup></div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) El Mínimo: usando el complementario"):
            st.markdown("<div class='subsection-title'>B) Distribución del Mínimo</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea Z = mín{X₁, . . . , Xₙ}. Aquí no funciona condicionar sobre {Z ≤ z}, porque para que "
                "el mínimo sea pequeño basta que <b>una</b> componente lo sea, y eso no factoriza. "
                "Se pasa al complementario:<br>"
                "<div class='formula-box'>P(Z &gt; z) = P(X₁ &gt; z, . . . , Xₙ &gt; z) = "
                "[1 − F<sub>X</sub>(z)]<sup>n</sup></div>"
                "porque el mínimo es mayor que z si y sólo si todas lo son. Y de ahí:<br>"
                "<div class='formula-box'>F<sub>Z</sub>(z) = 1 − [1 − F<sub>X</sub>(z)]<sup>n</sup></div>"
                "<b>Simetría:</b> el máximo se ataca con la función de distribución y el mínimo con el "
                "complementario. Son la misma idea vista desde los dos extremos."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_C", "C) Densidades por Derivación"):
            st.markdown("<div class='subsection-title'>C) Caso Continuo</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Derivando las dos funciones de distribución mediante la regla de la cadena:<br>"
                "<div class='formula-box'>f<sub>máx</sub>(y) = n·[F<sub>X</sub>(y)]<sup>n−1</sup>·"
                "f<sub>X</sub>(y)</div>"
                "<div class='formula-box'>f<sub>mín</sub>(z) = n·[1 − F<sub>X</sub>(z)]<sup>n−1</sup>·"
                "f<sub>X</sub>(z)</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_D", "D) Comportamiento Asintótico"):
            st.markdown("<div class='subsection-title'>D) Qué Ocurre al Crecer n</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Como F<sub>X</sub>(y) ∈ [0,1], elevar a la n hace que F<sub>máx</sub> se aplaste contra "
                "cero salvo cerca del extremo superior del soporte:<br>"
                "<div class='formula-box'>F<sub>X</sub>(y) &lt; 1 &nbsp;⟹&nbsp; "
                "[F<sub>X</sub>(y)]<sup>n</sup> → 0</div>"
                "Es decir, el máximo <b>se desplaza hacia el extremo superior</b> del soporte y el mínimo "
                "hacia el inferior. Con soporte acotado convergen a los extremos; con soporte no acotado "
                "el máximo diverge.<br><br>"
                "<b>Ejercicio:</b> sea Y = máx{X<sub>1</sub>, ..., X<sub>n</sub>} con X<sub>i</sub> ~ "
                "U(0,1). Usa el resultado F<sub>Y</sub>(y) = [F<sub>X</sub>(y)]<sup>n</sup> del "
                "apartado A) para calcular 𝔼[máx]. ¿Qué le ocurre cuando n → ∞?"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Para la U(0,1) se tiene F<sub>X</sub>(y) = y, así que por el apartado A): "
                "F<sub>Y</sub>(y) = y<sup>n</sup> en [0,1]. Derivando, "
                "f<sub>Y</sub>(y) = n·y<sup>n−1</sup>. "
                "Aplicando la definición de esperanza:<br><br>"
                "𝔼[máx] = ∫<sub>0</sub><sup>1</sup> y · n·y<sup>n−1</sup> dy = "
                "n · [y<sup>n+1</sup>/(n+1)]<sub>0</sub><sup>1</sup> = <b>n/(n+1)</b><br><br>"
                "Cuando n → ∞, 𝔼[máx] → 1: el máximo se acerca cada vez más al extremo del "
                "intervalo. Por simetría de la U(0,1), 𝔼[mín] = <b>1/(n+1)</b> → 0."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Máximo y Mínimo</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Elige la distribución de partida y el tamaño de la muestra. Se comparan las curvas teóricas "
            "con los histogramas de una simulación."
            "</small></div>",
            unsafe_allow_html=True
        )

        base = st.radio("Distribución de partida:",
                        ["Uniforme U(0,1)", "Exponencial Exp(λ)", "Normal N(0,1)"], key="p2_base")
        par = 1.0
        if base == "Exponencial Exp(λ)":
            par = st.slider("λ: Parámetro de la exponencial", 0.2, 3.0, 1.0, 0.1, key="p2_lam")
        n = st.slider("n: Tamaño de la muestra", 1, 50, 5, 1, key="p2_n")

        x = rango_base(base, par)
        F = cdf_base(base, x, par)
        f = pdf_base(base, x, par)
        F_max = F ** n
        F_min = 1 - (1 - F) ** n
        f_max = n * F ** (n - 1) * f
        f_min = n * (1 - F) ** (n - 1) * f

        p = figure(
            title=f"Funciones de distribución con n = {n}",
            x_axis_label="y", y_axis_label="F(y)",
            width=450, height=300, toolbar_location=None, tools=""
        )
        p.line(x, F, line_width=3, color=UBU_DARK, line_dash="dashed",
               legend_label="F(y) de partida")
        p.line(x, F_max, line_width=4, color=UBU_RED, legend_label="F(y)ⁿ del máximo")
        p.line(x, F_min, line_width=4, color=GREEN_LINE, legend_label="1−(1−F)ⁿ del mínimo")
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        muestras = muestra_base(base, par, (20000, n), seed=29)
        maximos = muestras.max(axis=1)
        minimos = muestras.min(axis=1)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>Media del máximo<br>{maximos.mean():.3f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>Media del mínimo<br>{minimos.mean():.3f}</div>",
                        unsafe_allow_html=True)

        p2 = figure(
            title="Densidades del máximo y del mínimo",
            x_axis_label="y", y_axis_label="densidad",
            width=450, height=310, toolbar_location=None, tools=""
        )
        hmax, bmax = np.histogram(maximos, bins=50, density=True)
        hmin, bmin = np.histogram(minimos, bins=50, density=True)
        p2.quad(top=hmax, bottom=0, left=bmax[:-1], right=bmax[1:],
                fill_color=UBU_RED, line_color=None, alpha=0.25)
        p2.quad(top=hmin, bottom=0, left=bmin[:-1], right=bmin[1:],
                fill_color=GREEN_LINE, line_color=None, alpha=0.25)
        p2.line(x, f_max, line_width=4, color=UBU_RED, legend_label="f del máximo")
        p2.line(x, f_min, line_width=4, color=GREEN_LINE, legend_label="f del mínimo")
        p2.legend.location = "top_right"
        p2.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p2))

        if base == "Uniforme U(0,1)":
            st.markdown(
                f"<div class='content-box'><b>Comprobación teórica:</b> para la U(0,1) se espera "
                f"𝔼[máx] = n/(n+1) = {n / (n + 1):.4f} y 𝔼[mín] = 1/(n+1) = {1 / (n + 1):.4f}. "
                f"La simulación da {maximos.mean():.4f} y {minimos.mean():.4f}.</div>",
                unsafe_allow_html=True
            )
        elif base == "Exponencial Exp(λ)":
            st.markdown(
                f"<div class='content-box'><b>Comprobación teórica:</b> el mínimo de n exponenciales "
                f"independientes es Exp(nλ), con media 1/(nλ) = {1 / (n * par):.4f}. La simulación da "
                f"{minimos.mean():.4f}. El máximo, en cambio, <b>no</b> es exponencial: la familia "
                f"exponencial reproduce con el mínimo pero no con el máximo.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='content-box'><b>Interpretación:</b> con soporte no acotado el máximo crece "
                "indefinidamente al aumentar n, aunque cada vez más despacio. Las dos densidades son "
                "simétricas entre sí respecto del origen porque la 𝒩(0,1) lo es.</div>",
                unsafe_allow_html=True
            )

def render_generalizaciones():
    """Sección III: aplicaciones del problema 087 a uniformes, exponenciales y el rango."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) Aplicaciones del Problema 087</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Los resultados del problema 087, F<sub>máx</sub>(y) = [F<sub>X</sub>(y)]<sup>n</sup> y "
            "F<sub>mín</sub>(z) = 1 − [1 − F<sub>X</sub>(z)]<sup>n</sup>, permiten calcular de forma "
            "directa la distribución y la esperanza del máximo y del mínimo para cualquier familia. "
            "Se aplican aquí a dos casos concretos."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Máximo y Mínimo de Uniformes U(0,1)"):
            st.markdown("<div class='subsection-title'>A) Caso Uniforme</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea X<sub>i</sub> ~ U(0,1), con F<sub>X</sub>(y) = y y f<sub>X</sub>(y) = 1 en [0,1]. "
                "Aplicando el problema 087:<br>"
                "<div class='formula-box'>F<sub>máx</sub>(y) = y<sup>n</sup> &nbsp;&nbsp; "
                "f<sub>máx</sub>(y) = n·y<sup>n−1</sup></div>"
                "<div class='formula-box'>F<sub>mín</sub>(y) = 1 − (1−y)<sup>n</sup> &nbsp;&nbsp; "
                "f<sub>mín</sub>(y) = n·(1−y)<sup>n−1</sup></div>"
                "Integrando cada densidad se obtienen las esperanzas:<br>"
                "<div class='formula-box'>𝔼[máx] = n/(n+1) &nbsp;&nbsp;&nbsp; 𝔼[mín] = 1/(n+1)</div>"
                "Los dos valores están siempre a distancia 1/(n+1) de sus respectivos extremos. "
                "Con n = 1 ambos valen 1/2, como corresponde a una sola U(0,1)."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Cálculo de 𝔼[máx]:</b><br>"
                "𝔼[máx] = ∫<sub>0</sub><sup>1</sup> y · n·y<sup>n−1</sup> dy = "
                "n · [y<sup>n+1</sup>/(n+1)]<sub>0</sub><sup>1</sup> = <b>n/(n+1)</b><br><br>"
                "<b>Cálculo de 𝔼[mín]:</b><br>"
                "𝔼[mín] = ∫<sub>0</sub><sup>1</sup> y · n·(1−y)<sup>n−1</sup> dy. "
                "Con el cambio u = 1 − y se convierte en "
                "∫<sub>0</sub><sup>1</sup> (1−u) · n·u<sup>n−1</sup> du = 1 − n/(n+1) = <b>1/(n+1)</b>."
            )

        if accordion_step("P3_B", "B) Mínimo de Exponenciales Exp(λ)"):
            st.markdown("<div class='subsection-title'>B) La Exponencial Reproduce en el Mínimo</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea X<sub>i</sub> ~ Exp(λ), con F<sub>X</sub>(z) = 1 − e<sup>−λz</sup> para z &gt; 0. "
                "Aplicando la fórmula del mínimo:<br>"
                "<div class='formula-box'>F<sub>mín</sub>(z) = 1 − [1 − F<sub>X</sub>(z)]<sup>n</sup> = "
                "1 − e<sup>−nλz</sup></div>"
                "Eso es la función de distribución de una <b>Exp(nλ)</b>. La familia exponencial "
                "<b>sí reproduce respecto del mínimo</b>: la tasa se multiplica por n.<br><br>"
                "La esperanza del mínimo vale:<br>"
                "<div class='formula-box'>𝔼[mín] = 1/(nλ)</div>"
                "Al doblar el número de variables la esperanza se reduce a la mitad: "
                "cuantas más componentes haya, antes ocurre el primer suceso."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Comparación con la suma: Exp(λ) + Exp(λ) <b>no</b> es Exp(2λ) sino Gamma(2, λ), "
                "una distribución distinta. La familia exponencial <b>no</b> reproduce respecto de la suma "
                "pero <b>sí</b> respecto del mínimo. Son dos operaciones distintas y cada una tiene sus "
                "propias familias reproductivas."
            )

        if accordion_step("P3_C", "C) El Rango"):
            st.markdown("<div class='subsection-title'>C) Combinando los Dos Extremos</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Dados los resultados del apartado A), se puede calcular la esperanza del rango "
                "sin necesidad de conocer su distribución. Por la linealidad de la esperanza "
                "(apartado <b>5.8.1</b>):<br>"
                "<div class='formula-box'>R = máx − mín</div>"
                "<div class='formula-box'>𝔼[R] = 𝔼[máx] − 𝔼[mín] = "
                "n/(n+1) − 1/(n+1) = (n−1)/(n+1)</div>"
                "Con n = 1 el rango vale cero (hay un solo punto). Con n = 2 vale 1/3. "
                "Cuando n → ∞ el rango tiende a 1: el máximo y el mínimo se acercan a los dos extremos.<br><br>"
                "<b>Atención:</b> que la esperanza de la diferencia sea la diferencia de las esperanzas "
                "es siempre cierto por linealidad, <b>aunque el máximo y el mínimo no sean independientes</b>. "
                "Y de hecho no lo son: si el mínimo es grande, el máximo no puede ser pequeño."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "<b>Ejercicio:</b> con n = 3 uniformes U(0,1), calcula 𝔼[máx], 𝔼[mín] y 𝔼[R].<br><br>"
                "𝔼[máx] = 3/4, &nbsp; 𝔼[mín] = 1/4, &nbsp; 𝔼[R] = 3/4 − 1/4 = <b>1/2</b>.<br><br>"
                "Intuitivamente: tres puntos al azar en [0,1] dividen el intervalo en cuatro trozos de "
                "longitud media 1/4 cada uno. El mayor está en media a 3/4 del origen y el menor a 1/4, "
                "así que entre ellos cubren exactamente la mitad del intervalo."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Apartados A), B) y C)</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Mueve n para ver cómo cambian máx, mín y rango. Compara las densidades teóricas con "
            "el histograma simulado y verifica las esperanzas."
            "</small></div>",
            unsafe_allow_html=True
        )

        familia_p3 = st.radio("Distribución de partida:",
                              ["Uniforme U(0,1)", "Exponencial Exp(λ)"], key="p3_fam")
        par_p3 = 1.0
        if familia_p3 == "Exponencial Exp(λ)":
            par_p3 = st.slider("λ: Parámetro de la exponencial", 0.2, 3.0, 1.0, 0.1, key="p3_lam")
        n_p3 = st.slider("n: Número de variables", 1, 20, 4, 1, key="p3_n")

        x_p3 = rango_base(familia_p3, par_p3)
        F_p3 = cdf_base(familia_p3, x_p3, par_p3)
        f_p3 = pdf_base(familia_p3, x_p3, par_p3)
        f_max_p3 = n_p3 * F_p3 ** (n_p3 - 1) * f_p3
        f_min_p3 = n_p3 * (1 - F_p3) ** (n_p3 - 1) * f_p3

        muestras_p3 = muestra_base(familia_p3, par_p3, (20000, n_p3), seed=29)
        maximos_p3 = muestras_p3.max(axis=1)
        minimos_p3 = muestras_p3.min(axis=1)
        rango_p3   = maximos_p3 - minimos_p3

        p = figure(
            title=f"Densidades del máximo y del mínimo (n = {n_p3})",
            x_axis_label="y", y_axis_label="densidad",
            width=450, height=320, toolbar_location=None, tools=""
        )
        h_max, b_max = np.histogram(maximos_p3, bins=50, density=True)
        h_min, b_min = np.histogram(minimos_p3, bins=50, density=True)
        p.quad(top=h_max, bottom=0, left=b_max[:-1], right=b_max[1:],
               fill_color=UBU_RED, line_color=None, alpha=0.25)
        p.quad(top=h_min, bottom=0, left=b_min[:-1], right=b_min[1:],
               fill_color=GREEN_LINE, line_color=None, alpha=0.25)
        p.line(x_p3, f_max_p3, line_width=4, color=UBU_RED, legend_label="f del máximo")
        p.line(x_p3, f_min_p3, line_width=4, color=GREEN_LINE, legend_label="f del mínimo")
        p.legend.location = "top_right"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        if familia_p3 == "Uniforme U(0,1)":
            e_max_teo = n_p3 / (n_p3 + 1)
            e_min_teo = 1 / (n_p3 + 1)
            e_r_teo   = (n_p3 - 1) / (n_p3 + 1)
        else:
            e_min_teo = 1 / (n_p3 * par_p3)
            e_max_teo = float(np.sum(1 / np.arange(1, n_p3 + 1)) / par_p3)
            e_r_teo   = e_max_teo - e_min_teo

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third metric-a'>"
                        f"𝔼[máx] teórica<br>{e_max_teo:.4f}<br>"
                        f"<span style='font-size:18px;color:var(--muted-fg)'>simulada: {maximos_p3.mean():.4f}</span>"
                        f"</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third metric-b'>"
                        f"𝔼[mín] teórica<br>{e_min_teo:.4f}<br>"
                        f"<span style='font-size:18px;color:var(--muted-fg)'>simulada: {minimos_p3.mean():.4f}</span>"
                        f"</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-c'>"
                        f"𝔼[R] teórica<br>{e_r_teo:.4f}<br>"
                        f"<span style='font-size:18px;color:var(--muted-fg)'>simulada: {rango_p3.mean():.4f}</span>"
                        f"</div>", unsafe_allow_html=True)

        if familia_p3 == "Uniforme U(0,1)":
            st.markdown(
                f"<div class='content-box'><b>Comprobación apartado A):</b> con n = {n_p3} uniformes, "
                f"𝔼[máx] = {n_p3}/{n_p3+1} = {e_max_teo:.4f} y "
                f"𝔼[mín] = 1/{n_p3+1} = {e_min_teo:.4f}.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='content-box'><b>Comprobación apartado B):</b> el mínimo de {n_p3} "
                f"Exp({par_p3:g}) sigue una Exp({n_p3 * par_p3:g}), con 𝔼[mín] = "
                f"1/({n_p3}·{par_p3:g}) = {e_min_teo:.4f}.</div>",
                unsafe_allow_html=True
            )

# =============================================================================
# 6. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Reproductividad y Familias de Distribuciones</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO", "open_step": "INTRO_A"}); st.rerun()
    if nav_col2.button("(I) 058: Vandermonde", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) 087: Máximo y Mínimo", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Aplicaciones", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_vandermonde,
        "P2": render_max_min,
        "P3": render_generalizaciones,
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
