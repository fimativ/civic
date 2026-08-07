import streamlit as st
import numpy as np
from bokeh.plotting import figure
from scipy.stats import chi2
import uuid
from streamlit_bokeh import streamlit_bokeh

# =============================================================================
# 1. CONFIGURACIÓN Y CONSTANTES
# =============================================================================

st.set_page_config(layout="wide", page_title="C1VIC D4TA, Covarianza y Componentes Principales")

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

def sigma_from(s1, s2, rho):
    """Matriz de varianzas-covarianzas 2x2 a partir de desviaciones y correlación."""
    c = rho * s1 * s2
    return np.array([[s1 ** 2, c], [c, s2 ** 2]])

def sample_bivariate(s1, s2, rho, n, seed=7):
    """Muestra de una normal bivariante centrada con la Sigma dada."""
    rng = np.random.default_rng(seed)
    Sigma = sigma_from(s1, s2, rho)
    L = np.linalg.cholesky(Sigma + 1e-12 * np.eye(2))
    return rng.standard_normal((n, 2)) @ L.T

def eig_sorted(Sigma):
    """Autovalores en orden decreciente y autovectores asociados."""
    vals, vecs = np.linalg.eigh(Sigma)
    orden = np.argsort(vals)[::-1]
    return vals[orden], vecs[:, orden]

def ellipse_points(Sigma, conf=0.95, n=200):
    """Elipse de nivel {x : xᵀ Σ⁻¹ x = c} con c el cuantil de una chi-cuadrado."""
    c = chi2.ppf(conf, df=2)
    vals, vecs = eig_sorted(Sigma)
    t = np.linspace(0, 2 * np.pi, n)
    semiejes = np.sqrt(np.maximum(vals, 0) * c)
    pts = vecs @ (semiejes[:, None] * np.vstack([np.cos(t), np.sin(t)]))
    return pts[0], pts[1]

def matrix_box(M, label="Σ"):
    """Matriz 2x2 dentro de una formula-box con alineación monoespaciada."""
    a, b, c, d = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return (
        "<div class='formula-box' style=\"font-family: 'Courier New', monospace; "
        "white-space: pre; font-size: 24px;\">"
        f"{label}  =   ⎡ {a:7.3f}   {b:7.3f} ⎤\n"
        f"        ⎣ {c:7.3f}   {d:7.3f} ⎦"
        "</div>"
    )

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
    """Introducción: del vector aleatorio a su estructura de dependencia."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Introducción: Covarianza y Estructura de Dependencia</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Conocer las distribuciones marginales de cada componente de un vector aleatorio no determina "
            "su distribución conjunta: falta la información sobre cómo varían juntas. La covarianza es el "
            "primer resumen de esa información que falta, y la matriz que la organiza contiene toda la "
            "geometría del vector."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("INTRO_A", "Vector Esperanza y Matriz de Varianzas-Covarianzas"):
            st.markdown("<div class='subsection-title'>A) Momentos de un Vector Aleatorio</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Sea <b>X</b> = (X₁, ..., Xₙ) un vector aleatorio. Sus momentos de primer y segundo orden son:<br>"
                "El <b>vector esperanza</b>:<br>"
                "<div class='formula-box'>𝔼[(X₁, ..., Xₙ)] = (𝔼[X₁], ..., 𝔼[Xₙ])</div>"
                "<div class='formula-box'>Σ = 𝔼[(X − μ)(X − μ)<sup>T</sup>]</div>"
                "El elemento genérico de Σ es σ<sub>ij</sub> = Cov(X<sub>i</sub>, X<sub>j</sub>), de modo que la diagonal recoge las varianzas marginales y el resto la "
                "dependencia lineal entre pares."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "El vector esperanza sitúa la nube de puntos y la matriz de varianzas-covarianzas describe su forma. "
                "Trasladar el vector cambia μ pero deja Σ intacta."
            )

        if accordion_step("INTRO_B", "Por qué las Marginales no Bastan"):
            st.markdown("<div class='subsection-title'>B) Marginales frente a Conjunta</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La medibilidad sí se hereda de las componentes: por la equivalencia de medibilidad, "
                "el vector es aleatorio si y sólo si cada componente lo es. "
                "La distribución, en cambio, no se hereda:<br>"
                "<div class='formula-box'>conjunta → marginales &nbsp;&nbsp;✓&nbsp;&nbsp; siempre</div>"
                "<div class='formula-box'>marginales → conjunta &nbsp;&nbsp;✗&nbsp;&nbsp; salvo independencia</div>"
                "Al obtener una marginal se suma o integra sobre la otra componente, y en esa operación se "
                "descarta la información de qué valores se dan simultáneamente. Esa información perdida es "
                "precisamente la dependencia."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("INTRO_C", "Recorrido del Applet"):
            st.markdown("<div class='subsection-title'>C) Contenido de las Tres Secciones</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b style='color: #2b6cb0;'>(I) Covarianza y correlación:</b><br>"
                "El caso escalar. Definición, propiedades y por qué covarianza nula no significa "
                "independencia.<br><br>"
                "<b style='color: #2e7d32;'>(II) La matriz Σ:</b><br>"
                "Simetría, semidefinición positiva y la identidad Var(a<sup>T</sup>X) = a<sup>T</sup>Σa.<br><br>"
                "<b style='color: #E67E22;'>(III) Componentes principales:</b><br>"
                "Diagonalizar Σ para obtener componentes incorreladas ordenadas por varianza."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>📊 Las Mismas Marginales, Distinta Conjunta</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "En las dos nubes X₁ ~ N(0,1) y X₂ ~ N(0,1): las marginales son idénticas. "
            "Lo único que cambia es la covarianza."
            "</small></div>",
            unsafe_allow_html=True
        )

        for rho, color, titulo in [(0.0, BLUE_LINE, "ρ = 0"), (0.9, UBU_RED, "ρ = 0.9")]:
            datos = sample_bivariate(1.0, 1.0, rho, 400, seed=11)
            p = figure(
                title=f"Normal bivariante con {titulo}",
                x_axis_label="X₁", y_axis_label="X₂",
                width=450, height=290, toolbar_location=None, tools="",
                x_range=(-4, 4), y_range=(-4, 4)
            )
            p.scatter(datos[:, 0], datos[:, 1], size=6, color=color, alpha=0.55)
            streamlit_bokeh(style_fig(p))

        st.markdown(
            "<div class='content-box'>"
            "<b>Interpretación:</b> proyecta cualquiera de las dos nubes sobre el eje horizontal y "
            "obtienes la misma N(0,1); proyéctala sobre el vertical y también. La diferencia entre ambas "
            "vive únicamente en cómo se reparte la masa <i>dentro</i> del plano, que es lo que mide Σ."
            "</div>",
            unsafe_allow_html=True
        )

def render_covarianza():
    """Sección I: covarianza y coeficiente de correlación."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(I) Covarianza y Correlación</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "La covarianza mide la variación conjunta de dos componentes alrededor de sus medias. "
            "Su versión normalizada, el coeficiente de correlación, es adimensional y está acotada "
            "en el intervalo [−1, 1]."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P1_A", "A) Definición y Fórmula de Cálculo"):
            st.markdown("<div class='subsection-title'>A) Definición</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Cov(X,Y) = 𝔼[(X − μ<sub>X</sub>)(Y − μ<sub>Y</sub>)]</div>"
                "En la práctica se calcula con la forma equivalente:<br>"
                "<div class='formula-box'>Cov(X,Y) = 𝔼[XY] − 𝔼[X]·𝔼[Y]</div>"
                "<b>Interpretación del signo:</b><br>"
                "• Cov &gt; 0: las desviaciones del mismo signo tienden a coincidir<br>"
                "• Cov &lt; 0: las desviaciones de signo opuesto tienden a coincidir<br>"
                "• Cov = 0: no hay asociación <i>lineal</i><br><br>"
                "La covarianza tiene unidades, el producto de las unidades de X e Y, así que su magnitud "
                "no es comparable entre problemas distintos. Normalizando se obtiene:<br>"
                "<div class='formula-box'>ρ<sub>XY</sub> = Cov(X,Y) / (σ<sub>X</sub>·σ<sub>Y</sub>) ∈ [−1, 1]</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_B", "B) Propiedades"):
            st.markdown("<div class='subsection-title'>B) Propiedades Fundamentales</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<b>1. Caso diagonal:</b><br>"
                "Cov(X,X) = Var(X)<br><br>"
                "<b>2. Simetría:</b><br>"
                "Cov(X,Y) = Cov(Y,X)<br><br>"
                "<b>3. Bilinealidad:</b><br>"
                "Cov(Σ<sub>i</sub> a<sub>i</sub>X<sub>i</sub>, Σ<sub>j</sub> b<sub>j</sub>Y<sub>j</sub>) = "
                "Σ<sub>i</sub> Σ<sub>j</sub> a<sub>i</sub>b<sub>j</sub> Cov(X<sub>i</sub>, Y<sub>j</sub>)<br><br>"
                "<b>4. Escala y origen:</b> la traslación no afecta, la escala sí<br>"
                "Cov(aX + b, cY + d) = ac · Cov(X,Y)<br><br>"
                "<b>5. Varianza de una suma:</b><br>"
                "Var(X ± Y) = Var(X) + Var(Y) ± 2·Cov(X,Y)"
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='content-box'>"
                "<b>6. Cota de la covarianza.</b> De aquí sale que ρ<sub>XY</sub> está acotado, "
                "y el caso de igualdad caracteriza la dependencia lineal "
                "perfecta:<br>"
                "<div class='formula-box'>|Cov(X,Y)| ≤ σ<sub>X</sub>·σ<sub>Y</sub></div>"
                "<div class='formula-box'>|ρ<sub>XY</sub>| = 1 ⟺ Y = aX + b &nbsp; c.s.</div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P1_C", "C) Covarianza Nula no Implica Independencia"):
            st.markdown("<div class='subsection-title'>C) El Recíproco es Falso</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "La implicación entre independencia y covarianza nula sólo se cumple en un sentido:<br>"
                "<div class='formula-box'>X ⊥ Y &nbsp;⟹&nbsp; Cov(X,Y) = 0</div>"
                "Considera X ~ U(−1, 1) e Y = X². Calcula Cov(X,Y) y decide si X e Y son independientes."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Por simetría 𝔼[X] = 0 y 𝔼[XY] = 𝔼[X³] = 0, luego <b>Cov(X,Y) = 0</b>. Pero Y está "
                "completamente determinada por X: conocer X fija Y sin ninguna incertidumbre. "
                "La covarianza solo detecta la componente <b>lineal</b> de la dependencia, y aquí la "
                "relación es puramente cuadrática. Excepción importante: si el vector (X,Y) es normal "
                "bivariante, entonces ρ = 0 sí equivale a independencia."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Nube de Puntos</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Se genera una muestra de una normal bivariante con σ₁ = σ₂ = 1 y la correlación elegida. "
            "Compara el valor teórico con el estimado sobre la muestra."
            "</small></div>",
            unsafe_allow_html=True
        )

        rho = st.slider("ρ: Correlación teórica", -0.99, 0.99, 0.70, 0.01, key="p1_rho")
        n = st.slider("n: Tamaño de la muestra", 50, 2000, 400, 50, key="p1_n")

        datos = sample_bivariate(1.0, 1.0, rho, n, seed=23)
        x, y = datos[:, 0], datos[:, 1]
        cov_emp = float(np.cov(x, y, ddof=1)[0, 1])
        rho_emp = float(np.corrcoef(x, y)[0, 1])

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third metric-a'>Cov muestral<br>{cov_emp:.3f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third metric-b'>ρ muestral<br>{rho_emp:.3f}</div>",
                        unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-c'>ρ teórico<br>{rho:.2f}</div>",
                        unsafe_allow_html=True)

        p = figure(
            title=f"Muestra de tamaño {n} con ρ = {rho:.2f}",
            x_axis_label="X₁", y_axis_label="X₂",
            width=450, height=330, toolbar_location=None, tools=""
        )
        p.scatter(x, y, size=6, color=BLUE_LINE, alpha=0.5, legend_label="Muestra")
        xs = np.array([x.min(), x.max()])
        pendiente = cov_emp / float(np.var(x, ddof=1))
        p.line(xs, pendiente * (xs - x.mean()) + y.mean(), line_width=3,
               color=UBU_RED, legend_label="Ajuste lineal")
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        st.markdown(
            "<div class='content-box'><b>Contraejemplo Y = X²:</b> dependencia total con correlación nula. "
            "La nube tiene una estructura evidente que ρ no puede detectar.</div>",
            unsafe_allow_html=True
        )

        rng = np.random.default_rng(5)
        xu = rng.uniform(-1, 1, 600)
        yu = xu ** 2
        rho_u = float(np.corrcoef(xu, yu)[0, 1])

        p2 = figure(
            title="X ~ U(−1, 1) con Y = X²",
            x_axis_label="X", y_axis_label="Y = X²",
            width=450, height=290, toolbar_location=None, tools=""
        )
        p2.scatter(xu, yu, size=6, color=GREEN_LINE, alpha=0.6)
        streamlit_bokeh(style_fig(p2))

        st.markdown(
            f"<div class='metric-box metric-b'>ρ muestral del contraejemplo<br>{rho_u:.3f}</div>",
            unsafe_allow_html=True
        )

def render_matriz():
    """Sección II: la matriz de varianzas-covarianzas y su forma cuadrática."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(II) La Matriz de Varianzas-Covarianzas Σ</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Toda la información de segundo orden de un vector aleatorio se organiza en una sola matriz. "
            "No es una matriz cualquiera: es simétrica y semidefinida positiva, y esas dos propiedades no "
            "son un accidente algebraico sino consecuencia directa de que las varianzas no pueden ser "
            "negativas."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P2_A", "A) Definición y Estructura"):
            st.markdown("<div class='subsection-title'>A) La Matriz Σ</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Σ = 𝔼[(X − μ)(X − μ)<sup>T</sup>] = "
                "𝔼[XX<sup>T</sup>] − μμ<sup>T</sup></div>"
                "<div class='formula-box' style=\"font-family: 'Courier New', monospace; white-space: pre; "
                "font-size: 22px;\">"
                "     ⎡ σ₁²   σ₁₂  ⋯  σ₁ₙ ⎤\n"
                "Σ =  ⎢ σ₂₁   σ₂²  ⋯  σ₂ₙ ⎥\n"
                "     ⎢  ⋮     ⋮   ⋱   ⋮  ⎥\n"
                "     ⎣ σₙ₁   σₙ₂  ⋯  σₙ² ⎦"
                "</div>"
                "• <b>Diagonal:</b> σ<sub>ii</sub> = Var(X<sub>i</sub>) ≥ 0<br>"
                "• <b>Fuera de la diagonal:</b> σ<sub>ij</sub> = Cov(X<sub>i</sub>, X<sub>j</sub>)<br>"
                "• <b>Simetría:</b> Σ = Σ<sup>T</sup>, porque la covarianza lo es<br>"
                "• <b>Suma de la diagonal:</b> tr(Σ) = Σ<sub>i</sub> Var(X<sub>i</sub>), la varianza total"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_B", "B) Semidefinida Positiva: la Identidad Clave"):
            st.markdown("<div class='subsection-title'>B) Var(a<sup>T</sup>X) = a<sup>T</sup>Σa</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Para cualquier vector de constantes <b>a</b>, la combinación lineal a<sup>T</sup>X es una "
                "variable aleatoria escalar. Su varianza se lee directamente en Σ:<br>"
                "<div class='formula-box'>Var(a<sup>T</sup>X) = a<sup>T</sup>Σa ≥ 0 &nbsp;&nbsp; "
                "∀ a ∈ ℝⁿ</div>"
                "Como una varianza nunca es negativa, la forma cuadrática asociada a Σ es siempre no "
                "negativa: eso <i>es</i> la definición de semidefinida positiva.<br><br>"
                "Esta misma condición se puede escribir como doble sumatorio, "
                "con un vector de constantes τ:<br>"
                "<div class='formula-box'>Σ<sub>i</sub> Σ<sub>j</sub> Cov(X<sub>i</sub>, X<sub>j</sub>) "
                "τ<sub>i</sub> τ<sub>j</sub> ≥ 0</div>"
                "Es exactamente Var(τ<sup>T</sup>X) ≥ 0 desarrollado término a término. "
                "Consecuencia que se usará en la sección (III): todos los autovalores de Σ son ≥ 0."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Si alguna combinación lineal τ<sup>T</sup>X es constante, su varianza es cero y la "
                "desigualdad se cumple con igualdad. Geométricamente la nube de puntos colapsa sobre una "
                "recta: toda la dispersión vive en menos dimensiones de las que aparenta. Es justo la "
                "situación que la sección (III) permite detectar."
            )

        if accordion_step("P2_C", "C) Transformaciones Lineales"):
            st.markdown("<div class='subsection-title'>C) Efecto de Y = AX + b</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Si Y = AX + b con A de tamaño m×n, entonces:<br>"
                "<div class='formula-box'>μ<sub>Y</sub> = Aμ + b</div>"
                "<div class='formula-box'>Σ<sub>Y</sub> = A Σ A<sup>T</sup></div>"
                "La traslación b desaparece de Σ<sub>Y</sub>: la dispersión no depende de dónde situemos el "
                "origen. La identidad a<sup>T</sup>Σa vista antes es el caso particular m = 1.<br><br>"
                "Este resultado es el motor de la sección (III): si elegimos bien A, podemos conseguir que "
                "Σ<sub>Y</sub> sea <b>diagonal</b>."
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P2_D", "D) De Σ al Coeficiente de Correlación"):
            st.markdown("<div class='subsection-title'>D) Versión Adimensional</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Cada elemento de Σ tiene unidades, así que su magnitud no es comparable entre pares de "
                "componentes distintas. Dividiendo por las desviaciones típicas se obtiene el "
                "coeficiente de correlación:<br>"
                "<div class='formula-box'>ρ<sub>XY</sub> = Cov(X, Y) / (σ<sub>X</sub> σ<sub>Y</sub>)</div>"
                "que es adimensional y, por la cota vista antes, está siempre en [−1, 1]. "
                "Es la misma información que Σ pero legible: Σ dice cuánto covarían y ρ dice "
                "<b>cuán fuerte</b> es esa relación en una escala común.<br><br>"
                "<b>Consecuencia práctica para la sección (III):</b> como Σ depende de las unidades, "
                "si una componente se mide en unidades que la hacen mucho más variable que las demás, "
                "dominará el análisis simplemente por su escala y no porque sea más informativa."
                "</div>",
                unsafe_allow_html=True
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Σ y su Forma Cuadrática</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "Construye Σ con los tres primeros deslizadores y gira la dirección a con el cuarto. "
            "La elipse muestra la región que concentra el 95% de la probabilidad."
            "</small></div>",
            unsafe_allow_html=True
        )

        s1 = st.slider("σ₁: Desviación de X₁", 0.2, 3.0, 1.5, 0.1, key="p2_s1")
        s2 = st.slider("σ₂: Desviación de X₂", 0.2, 3.0, 0.8, 0.1, key="p2_s2")
        rho = st.slider("ρ: Correlación", -0.99, 0.99, 0.60, 0.01, key="p2_rho")
        ang = st.slider("θ: Dirección de a en grados", 0, 180, 30, 1, key="p2_ang")

        Sigma = sigma_from(s1, s2, rho)
        theta = np.deg2rad(ang)
        a = np.array([np.cos(theta), np.sin(theta)])
        var_a = float(a @ Sigma @ a)
        vals, vecs = eig_sorted(Sigma)

        st.markdown(matrix_box(Sigma), unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-box metric-third'>tr(Σ)<br>{np.trace(Sigma):.3f}</div>",
                        unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-third'>det(Σ)<br>{np.linalg.det(Sigma):.3f}</div>",
                        unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-box metric-third metric-a'>"
                        f"Var(a<sup>T</sup>X)<br>{var_a:.3f}</div>", unsafe_allow_html=True)

        conf_p2 = st.slider("Nivel de confianza de la elipse", 0.50, 0.99, 0.95, 0.01,
                             key="p2_conf")
        ex, ey = ellipse_points(Sigma, conf=conf_p2)
        lim = max(3.2, 1.25 * float(np.max(np.abs(np.concatenate([ex, ey])))))

        p = figure(
            title=f"Elipse de concentración al {int(conf_p2 * 100)}% y dirección a",
            x_axis_label="X₁", y_axis_label="X₂",
            width=450, height=350, toolbar_location=None, tools="",
            x_range=(-lim, lim), y_range=(-lim, lim)
        )
        p.patch(ex, ey, fill_color=UBU_YELLOW, fill_alpha=0.25,
                line_color=UBU_RED, line_width=3, legend_label=f"Elipse {int(conf_p2*100)}%")
        p.line([0, a[0] * lim * 0.9], [0, a[1] * lim * 0.9], line_width=4,
               color=PANTONE_2727, legend_label="Dirección a")
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        rejilla = np.linspace(0, 180, 361)
        th = np.deg2rad(rejilla)
        A = np.vstack([np.cos(th), np.sin(th)])
        curva = np.einsum("in,ij,jn->n", A, Sigma, A)

        p2 = figure(
            title="a\u1d40Σa en función de θ",
            x_axis_label="θ (grados)", y_axis_label="Var(a\u1d40X)",
            width=450, height=300, toolbar_location=None, tools=""
        )
        p2.line(rejilla, curva, line_width=3, color=PANTONE_2727, legend_label="Var(a\u1d40X)")
        p2.line([0, 180], [vals[0], vals[0]], line_width=2, color=UBU_RED,
                line_dash="dashed", legend_label="λ₁ (máximo)")
        p2.line([0, 180], [vals[1], vals[1]], line_width=2, color=GREEN_LINE,
                line_dash="dashed", legend_label="λ₂ (mínimo)")
        p2.scatter([ang], [var_a], size=12, color=PANTONE_2727)
        p2.legend.location = "top_right"
        p2.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p2))

        st.markdown(
            "<div class='content-box'><b>Interpretación:</b> la curva está acotada entre los dos "
            "autovalores de Σ para cualquier dirección. Ese hecho es exactamente el punto de partida "
            "de la sección (III).</div>",
            unsafe_allow_html=True
        )

def render_pca():
    """Sección III: componentes principales."""
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='bg-left'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>(III) Componentes Principales</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='statement-box'>"
            "Σ es simétrica, así que el teorema espectral garantiza que se puede diagonalizar en una base "
            "ortonormal. Esa base es el conjunto de componentes principales: un giro de los ejes que deja "
            "las componentes incorreladas y ordenadas de mayor a menor varianza."
            "</div>",
            unsafe_allow_html=True
        )

        if accordion_step("P3_A", "A) Teorema Espectral Aplicado a Σ"):
            st.markdown("<div class='subsection-title'>A) Diagonalización Ortogonal</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Σ = U Λ U<sup>T</sup>, &nbsp; U<sup>T</sup>U = I</div>"
                "<div class='formula-box'>Λ = diag(λ₁, ..., λₙ), &nbsp; λ₁ ≥ λ₂ ≥ ... ≥ λₙ ≥ 0</div>"
                "Las columnas u₁, ..., uₙ de U son los autovectores de Σ y forman una base ortonormal. "
                "Que todos los autovalores sean no negativos no es una hipótesis adicional: es la "
                "semidefinición positiva de la sección (II).<br><br>"
                "Además la traza es invariante por giros, de modo que:<br>"
                "<div class='formula-box'>tr(Σ) = Σ<sub>i</sub> σ<sub>i</sub>² = Σ<sub>i</sub> λ<sub>i</sub></div>"
                "</div>",
                unsafe_allow_html=True
            )

        if accordion_step("P3_B", "B) Definición de las Componentes"):
            st.markdown("<div class='subsection-title'>B) El Vector Y de Componentes</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "Se define el vector de componentes principales como el giro que alinea los ejes con los "
                "autovectores:<br>"
                "<div class='formula-box'>Y = U<sup>T</sup>(X − μ), &nbsp; "
                "Y<sub>i</sub> = u<sub>i</sub><sup>T</sup>(X − μ)</div>"
                "Aplicando Σ<sub>Y</sub> = AΣA<sup>T</sup> de (II.C) con A = U<sup>T</sup>:<br>"
                "<div class='formula-box'>Σ<sub>Y</sub> = U<sup>T</sup> Σ U = Λ</div>"
                "Es decir <b>Var(Y<sub>i</sub>) = λ<sub>i</sub></b> y "
                "<b>Cov(Y<sub>i</sub>, Y<sub>j</sub>) = 0</b> para i ≠ j. Hemos eliminado toda la "
                "correlación sin perder varianza total.<br><br>"
                "<b>Propiedad clave:</b> u<sub>1</sub> es además la dirección unitaria que "
                "<b>maximiza</b> Var(a<sup>T</sup>X), y u<sub>2</sub> la que maximiza entre "
                "las ortogonales a u<sub>1</sub>. Por eso la curva de la sección (II) tiene "
                "exactamente λ₁ como techo y λ₂ como suelo."
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Atención al matiz: incorreladas <b>no</b> es lo mismo que independientes. El giro anula "
                "las covarianzas, que son la parte lineal de la dependencia, pero podría quedar dependencia "
                "no lineal. Solo en el caso normal multivariante incorrelación equivale a independencia, "
                "y entonces las componentes principales sí son independientes entre sí."
            )

        if accordion_step("P3_C", "C) Varianza Explicada y Reducción de Dimensión"):
            st.markdown("<div class='subsection-title'>C) Cuánto Aporta cada Componente</div>",
                        unsafe_allow_html=True)
            st.markdown(
                "<div class='content-box'>"
                "<div class='formula-box'>Proporción explicada por Y<sub>i</sub> = "
                "λ<sub>i</sub> / tr(Σ)</div>"
                "Quedarse con las k primeras componentes es la mejor aproximación lineal de dimensión k "
                "en términos de varianza retenida.<br><br>"
                "<b>Pregunta:</b> con σ₁ = σ₂ = 1, ¿qué ocurre cuando ρ tiende a 1?"
                "</div>",
                unsafe_allow_html=True
            )
            spoiler(
                "Con σ₁ = σ₂ = 1 los autovalores son <b>λ₁ = 1 + ρ</b> y <b>λ₂ = 1 − ρ</b>, con "
                "autovectores fijos en las diagonales (1,1)/√2 y (1,−1)/√2. Cuando ρ → 1 se tiene "
                "λ₂ → 0 y det(Σ) → 0: la primera componente explica el 100% de la varianza, la nube "
                "colapsa sobre la recta X₂ = X₁ y el vector pasa a ser degenerado. Reducir de 2 a 1 "
                "dimensión no perdería nada. Con ρ = 0, en cambio, λ₁ = λ₂ = 1: no hay dirección "
                "privilegiada y los autovectores dejan de estar determinados de forma única."
            )

    with col_right:
        st.markdown("<div class='bg-right'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>⚙️ Simulación Interactiva: Giro de los Ejes</b><br>"
            "<small style='color: var(--muted-fg);'>"
            "El primer gráfico muestra la nube original con los autovectores escalados por √λᵢ. "
            "El segundo muestra la misma nube después del giro Y = U\u1d40X."
            "</small></div>",
            unsafe_allow_html=True
        )

        s1 = st.slider("σ₁: Desviación de X₁", 0.2, 3.0, 1.6, 0.1, key="p3_s1")
        s2 = st.slider("σ₂: Desviación de X₂", 0.2, 3.0, 1.0, 0.1, key="p3_s2")
        rho = st.slider("ρ: Correlación", -0.99, 0.99, 0.80, 0.01, key="p3_rho")
        n = st.slider("n: Tamaño de la muestra", 100, 2000, 500, 50, key="p3_n")

        Sigma = sigma_from(s1, s2, rho)
        vals, vecs = eig_sorted(Sigma)
        total = float(np.sum(vals))
        prop = vals / total
        datos = sample_bivariate(s1, s2, rho, n, seed=31)
        Y = datos @ vecs

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"<div class='metric-box metric-a'>λ₁ = {vals[0]:.3f}<br>"
                        f"explica {100 * prop[0]:.1f}%</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-box metric-b'>λ₂ = {vals[1]:.3f}<br>"
                        f"explica {100 * prop[1]:.1f}%</div>", unsafe_allow_html=True)

        # El giro puede ampliar la coordenada máxima hasta un factor √2, así que
        # el encuadre se calcula con ambas nubes y las dos comparten escala.
        lim = 1.15 * float(max(np.max(np.abs(datos)), np.max(np.abs(Y))))

        p = figure(
            title="Nube original con los autovectores de Σ",
            x_axis_label="X₁", y_axis_label="X₂",
            width=450, height=340, toolbar_location=None, tools="",
            x_range=(-lim, lim), y_range=(-lim, lim)
        )
        p.scatter(datos[:, 0], datos[:, 1], size=6, color=BLUE_LINE, alpha=0.45,
                  legend_label="Muestra")
        conf_p3 = st.slider("Nivel de confianza de la elipse", 0.50, 0.99, 0.95, 0.01,
                             key="p3_conf")
        ex, ey = ellipse_points(Sigma, conf=conf_p3)
        p.line(ex, ey, line_width=2, color=ORANGE_ACCENT, line_dash="dashed",
               legend_label=f"Elipse {int(conf_p3*100)}%")
        for i, (color, nombre) in enumerate([(UBU_RED, "u₁"), (GREEN_LINE, "u₂")]):
            v = vecs[:, i] * np.sqrt(vals[i]) * 2.0
            p.line([0, v[0]], [0, v[1]], line_width=5, color=color, legend_label=nombre)
        p.legend.location = "top_left"
        p.legend.label_text_font_size = "12px"
        streamlit_bokeh(style_fig(p))

        p2 = figure(
            title="Tras el giro: componentes incorreladas",
            x_axis_label="Y₁", y_axis_label="Y₂",
            width=450, height=310, toolbar_location=None, tools="",
            x_range=(-lim, lim), y_range=(-lim, lim)
        )
        p2.scatter(Y[:, 0], Y[:, 1], size=6, color=PANTONE_2727, alpha=0.45)
        p2.line([-lim, lim], [0, 0], line_width=3, color=UBU_RED)
        p2.line([0, 0], [-lim, lim], line_width=3, color=GREEN_LINE)
        streamlit_bokeh(style_fig(p2))

        corr_Y = float(np.corrcoef(Y.T)[0, 1])
        st.markdown(matrix_box(np.cov(Y.T, ddof=1), "Σ\u1d67"), unsafe_allow_html=True)
        st.markdown(
            "<div class='content-box'><b>Comprobación numérica:</b> la correlación muestral entre Y₁ e Y₂ "
            f"vale <b>{corr_Y:.4f}</b>, así que el giro ha eliminado la dependencia lineal. Se mira la "
            "correlación y no la covarianza porque esta última escala con las unidades y su magnitud no "
            "sería interpretable por sí sola.<br><br>"
            f"Y la varianza total se conserva: tr(Σ) = {np.trace(Sigma):.3f} = λ₁ + λ₂ = {total:.3f}."
            "</div>",
            unsafe_allow_html=True
        )

# =============================================================================
# 6. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    st.markdown(build_css(), unsafe_allow_html=True)

    st.markdown("<div class='top-bar-title'>C1VIC D4TA · Covarianza, Matriz Σ y Componentes Principales</div>",
                unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    if nav_col1.button("Introducción", use_container_width=True):
        st.session_state.update({"page": "INTRO", "open_step": "INTRO_A"}); st.rerun()
    if nav_col2.button("(I) Covarianza", use_container_width=True):
        st.session_state.update({"page": "P1", "open_step": "P1_A"}); st.rerun()
    if nav_col3.button("(II) Matriz Σ", use_container_width=True):
        st.session_state.update({"page": "P2", "open_step": "P2_A"}); st.rerun()
    if nav_col4.button("(III) Componentes Principales", use_container_width=True):
        st.session_state.update({"page": "P3", "open_step": "P3_A"}); st.rerun()

    paginas = {
        "INTRO": render_intro,
        "P1": render_covarianza,
        "P2": render_matriz,
        "P3": render_pca,
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
