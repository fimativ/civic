#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 5: el teorema central del límite.

De Moivre y la binomial (la primera versión, con la corrección de
continuidad), Lindeberg y Lévy (cualquier distribución con varianza finita) y
Berry y Esseen (a qué velocidad y por qué la regla de los treinta datos falla).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from scipy import stats

import civic_ui as ui

TITLE = "El teorema central del límite"
SYMBOL = "→ N(0,1)"
PAGE = "06_05"

BASES = {"unif": "Uniforme", "exp": "Exponencial", "die": "Un dado", "rare": "Bernoulli p = 0.1",
         "bimodal": "Dos picos"}
BERRY_ESSEEN = 0.4748


def initial_values():
    return {
        "n_bin": ui.dint(30, 10, 80, "n_bin"),
        "p_bin": ui.dchoice(0.5, [0.2, 0.3, 0.4, 0.5], "p_bin"),
        "base": ui.dchoice("exp", list(BASES), "base"),
        "n_sum": ui.dint(5, 2, 30, "n_sum"),
        "p_be": ui.dchoice(0.05, [0.01, 0.02, 0.05, 0.1, 0.3], "p_be"),
        "seed": int(ui.r("clt") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "base": None, "clt_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def base_sample(base: str, size, rng):
    if base == "unif":
        return rng.uniform(0, 1, size), 0.5, 1 / 12
    if base == "exp":
        return rng.exponential(1, size), 1.0, 1.0
    if base == "die":
        return rng.integers(1, 7, size).astype(float), 3.5, 35 / 12
    if base == "rare":
        return (rng.random(size) < 0.1).astype(float), 0.1, 0.09
    mix = rng.random(size) < 0.5
    return np.where(mix, rng.normal(-2, 0.5, size), rng.normal(2, 0.5, size)), 0.0, 4.25


def kolmogorov_distance(n: int, p: float) -> float:
    """sup_x |F_n(x) − Φ(x)| para la binomial tipificada."""
    k = np.arange(0, n + 1)
    mu, sd = n * p, np.sqrt(n * p * (1 - p))
    z = (k - mu) / sd
    cdf = stats.binom.cdf(k, n, p)
    left = np.concatenate(([0.0], cdf[:-1]))
    phi = stats.norm.cdf(z)
    return float(max(np.abs(cdf - phi).max(), np.abs(left - phi).max()))


def berry_esseen_bound(n: int, p: float) -> float:
    q = 1 - p
    rho = p * q * (p ** 2 + q ** 2)
    return BERRY_ESSEEN * rho / ((p * q) ** 1.5 * np.sqrt(n))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def demoivre_chart(dark, n: int, p: float, a: int, b: int):
    k = np.arange(0, n + 1)
    pmf = stats.binom.pmf(k, n, p)
    mu, sd = n * p, np.sqrt(n * p * (1 - p))
    lo, hi = max(0, mu - 5 * sd), min(n, mu + 5 * sd)
    xs = np.linspace(lo, hi, 400)
    colours = [ui.UBU_RED if a <= kk <= b else ui.BLUE_LINE for kk in k]
    fig = ui.new_figure(dark, height=300, x_axis_label="éxitos k", y_axis_label="probabilidad", x_range=(lo - 1, hi + 1))
    fig.vbar(x=k, top=pmf, width=0.9, fill_color=colours, fill_alpha=0.7, line_color=None)
    fig.line(xs, stats.norm.pdf(xs, mu, sd), line_width=4, color=ui.UBU_DARK if not dark else "#ffffff",
             legend_label=f"N({mu:.1f}, {sd:.2f})")
    return ui.style_legend(fig, dark, "top_right")


def clt_charts(dark, base: str, n: int, seed: int):
    rng = np.random.default_rng(seed)
    one, mu, var = base_sample(base, 20000, rng)
    sums, _, _ = base_sample(base, (20000, n), rng)
    z = (sums.sum(axis=1) - n * mu) / np.sqrt(n * var)
    p = ui.new_figure(dark, height=180, x_axis_label="una observación", y_axis_label="frecuencia")
    edges = np.histogram_bin_edges(one, bins=30)
    h, _ = np.histogram(one, bins=edges)
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / h.sum(), fill_color=ui.GREY_LINE, fill_alpha=0.6,
           line_color=None)
    xs = np.linspace(-4, 4, 300)
    q = ui.new_figure(dark, height=300, x_axis_label=f"suma tipificada de {n}", y_axis_label="densidad",
                      x_range=(-4, 4), y_range=(0, 0.6))
    e2 = np.linspace(-4, 4, 41)
    h2, _ = np.histogram(z, bins=e2)
    q.quad(left=e2[:-1], right=e2[1:], bottom=0, top=h2 / (len(z) * (e2[1] - e2[0])), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.7, line_color=None, legend_label="simulación")
    q.line(xs, stats.norm.pdf(xs), line_width=4, color=ui.BLUE_LINE, legend_label="N(0, 1)")
    ui.style_legend(q, dark, "top_right")
    return p, q, z


def rate_chart(dark, p: float, n_cur: int):
    ns = np.unique(np.logspace(0, 3.3, 60).astype(int))
    dist = [kolmogorov_distance(int(n), p) for n in ns]
    bound = [min(1, berry_esseen_bound(int(n), p)) for n in ns]
    fig = ui.new_figure(dark, height=300, x_axis_type="log", y_axis_type="log", x_axis_label="n",
                        y_axis_label="sup |Fₙ − Φ|", x_range=(1, ns[-1]), y_range=(1e-3, 1.2))
    fig.line(ns, dist, line_width=4, color=ui.BLUE_LINE, legend_label="distancia real")
    fig.line(ns, bound, line_width=3, color=ui.UBU_RED, line_dash="dashed", legend_label="cota de Berry-Esseen")
    fig.scatter([n_cur], [kolmogorov_distance(n_cur, p)], size=14, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK)
    return ui.style_legend(fig, dark, "bottom_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Por qué la campana aparece en todas partes?</b>")
        ui.content(
            "Las leyes de los grandes números dicen hacia dónde va la media; el <b>teorema central del límite</b> dice "
            "cómo fluctúa a su alrededor. Si las variables son independientes, con la misma distribución, media &mu; y "
            "varianza finita &sigma;<sup>2</sup>, la suma tipificada se parece cada vez más a una normal típica, sea cual sea "
            "la distribución de partida. <i>Escribe el teorema de Lindeberg-Lévy.</i>"
        )
        ui.formula_hidden("<sup>S<sub>n</sub> &minus; n&mu;</sup>&frasl;<sub>&sigma;&radic;n</sub> = <sup>X̄<sub>n</sub> &minus; &mu;</sup>&frasl;"
                          "<sub>&sigma;/&radic;n</sub> &rarr; N(0, 1) en distribución")
        ui.content(
            "Es la explicación de todas las campanas que han ido apareciendo: los dados de Galileo, la máquina de Galton, "
            "la gamma con forma grande, la suma de uniformes. Y es el pilar de la inferencia estadística: permite "
            "calcular probabilidades sobre medias sin conocer la distribución de los datos."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. De Moivre y la binomial (1733)</b><br>"
            "<i>La primera aparición de la campana, en un breve folleto sobre la binomial.</i><br><br>"
            "<b>II. Lindeberg y Lévy (1922)</b><br>"
            "<i>Elige la distribución más rara que se te ocurra y súmala muchas veces.</i><br><br>"
            "<b>III. Berry y Esseen (1941)</b><br>"
            "<i>¿Basta con treinta datos? Depende de lo asimétricos que sean.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>ensayos n</u>, la <u>probabilidad p</u> y el <u>intervalo de éxitos</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Ensayos n", 5, 200, v["n_bin"], 1, key=ui.wkey(PAGE, "n_bin"))
        p = c2.slider("Probabilidad p", 0.02, 0.98, v["p_bin"], 0.01, key=ui.wkey(PAGE, "p_bin"))
        mu = n * p
        sd = np.sqrt(n * p * (1 - p))
        default = (int(max(0, round(mu - sd))), int(min(n, round(mu + sd))))
        a, b = st.slider("Éxitos entre a y b", 0, n, default, 1, key=ui.wkey(PAGE, f"ab{n}{p}"))

        ui.planteamiento()
        ui.statement(
            "<b>De Moivre y la binomial (1733)</b><br><br>"
            "Abraham de Moivre, hugonote exiliado en Londres que se ganaba la vida resolviendo problemas de juego en el "
            "café de Slaughter, quería calcular probabilidades binomiales con n enorme, imposibles de sumar a mano. En un "
            "breve folleto en latín de 1733 encontró que, para p = 1/2, la binomial se aproxima por una curva "
            "exponencial de segundo grado: la campana. Laplace lo extendió a cualquier p en 1812."
        )

        if ui.accordion_step("P1_A", "(A) Tipificar la binomial"):
            ui.content(
                "La binomial es la suma de n Bernoulli independientes. ¿Qué dice el teorema central del límite de "
                "(X &minus; np)/&radic;(np(1 &minus; p))?"
            )
            ui.spoiler(
                "Con &mu; = p y &sigma;<sup>2</sup> = p(1 &minus; p) por ensayo:"
                "<div class='formula-box'><sup>X &minus; np</sup>&frasl;<sub>&radic;(np(1 &minus; p))</sub> &rarr; N(0, 1)</div>"
                "Es el teorema de De Moivre-Laplace, la primera versión histórica del teorema central del límite. Para n "
                "grande, la binomial se aproxima por N(np, &radic;(np(1 &minus; p)))."
            )

        if ui.accordion_step("P1_B", "(B) La corrección de continuidad"):
            ui.content(
                "La binomial pone su probabilidad en enteros; la normal la reparte en un continuo. ¿Qué intervalo de la "
                "normal corresponde mejor a &#8473;(a &le; X &le; b)? Compara las dos aproximaciones de la derecha."
            )
            ui.spoiler(
                "Cada barra de la binomial ocupa [k &minus; 1/2, k + 1/2], así que conviene extender el intervalo media unidad "
                "por cada lado:"
                "<div class='formula-box'>&#8473;(a &le; X &le; b) &asymp; &Phi;(<sup>b + 1/2 &minus; np</sup>&frasl;<sub>&sigma;</sub>) &minus; "
                "&Phi;(<sup>a &minus; 1/2 &minus; np</sup>&frasl;<sub>&sigma;</sub>)</div>"
                "Con n moderado, la corrección reduce mucho el error."
            )

        if ui.accordion_step("P1_C", "(C) Cuándo vale"):
            ui.content(
                "Pon p = 0.05 y n = 30. ¿Se parece la binomial a la campana? ¿Qué condición práctica falla?"
            )
            ui.spoiler(
                "Con np = 1.5 la binomial está pegada a cero y es muy asimétrica: la normal le asigna incluso probabilidad a "
                "valores negativos. Las condiciones orientativas de los apuntes piden n &ge; 30, np &ge; 5 y p no demasiado "
                "extremo; cuando np es pequeño, la buena aproximación es la de Poisson."
            )

    with col_right:
        ui.right_panel()
        exact = float(stats.binom.cdf(b, n, p) - stats.binom.cdf(a - 1, n, p))
        plain = float(stats.norm.cdf((b - mu) / sd) - stats.norm.cdf((a - mu) / sd))
        cc = float(stats.norm.cdf((b + 0.5 - mu) / sd) - stats.norm.cdf((a - 0.5 - mu) / sd))
        ui.metrics([(f"Exacta: {exact:.4f}", "metric-a"), (f"Normal: {plain:.4f}", "metric-c"),
                    (f"Con corrección: {cc:.4f}", "metric-b")])
        ui.show(demoivre_chart(dark, n, p, a, b), key="fig_demoivre")
        ui.footer_bar(f"En rojo, las barras de {a} a {b} éxitos. Error de la normal: {abs(plain - exact):.4f}; con corrección "
                      f"de continuidad: {abs(cc - exact):.4f}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>distribución de partida</u> y el <u>número de sumandos n</u>")
        if st.session_state["base"] is None:
            st.session_state["base"] = v["base"]
        ui.choice_buttons(list(BASES), "base", labels=BASES, per_row=3)
        n = st.slider("Sumandos n", 1, 100, v["n_sum"], 1, key=ui.wkey(PAGE, "n_sum"))

        ui.planteamiento()
        ui.statement(
            "<b>Lindeberg y Lévy (1922)</b><br><br>"
            "Jarl Lindeberg, matemático finlandés que dividía su tiempo entre la universidad y su granja, dio en 1922 "
            "una demostración rigurosa y muy general del teorema; Paul Lévy, con las funciones características, lo "
            "dejó en la forma que se enseña hoy. La sorpresa es la universalidad: la distribución de partida puede "
            "ser plana, asimétrica, discreta o con dos picos. Pruébalo."
        )

        if ui.accordion_step("P2_A", "(A) La suma tipificada"):
            ui.content(
                "Para cada distribución, la suma de n observaciones tiene media n&mu; y desviación &sigma;&radic;n. ¿Por qué se "
                "tipifica antes de comparar con la normal?"
            )
            ui.spoiler(
                "Sin tipificar, la suma se desplaza hacia n&mu; y se ensancha como &radic;n, y no converge a nada. Restar n&mu; "
                "y dividir por &sigma;&radic;n la mantiene centrada en 0 con varianza 1, y entonces sí tiene un límite, el "
                "mismo para todas las distribuciones con varianza finita: la normal típica."
            )

        if ui.accordion_step("P2_B", "(B) Qué se pierde al sumar"):
            ui.content(
                "Compara la rapidez con que se acercan a la normal la uniforme, el dado, la exponencial y la Bernoulli con "
                "p = 0.1. ¿Qué rasgo de la distribución de partida tarda más en desaparecer?"
            )
            ui.spoiler(
                "Las simétricas, como la uniforme o el dado, se parecen a la normal con muy pocos sumandos. Las asimétricas "
                "conservan durante más tiempo una cola más larga hacia un lado: la asimetría de la suma decrece como "
                "1/&radic;n. Con dos picos, la suma se vuelve multimodal, con un pico por cada número posible de sumandos de la derecha, "
                "y solo hacia n = 20 los picos se funden en una campana. La forma se olvida; solo sobreviven la "
                "media y la varianza."
            )

        if ui.accordion_step("P2_C", "(C) Cuando falla"):
            ui.content("¿Qué hipótesis del teorema no cumple la distribución de Cauchy? ¿Qué le pasa a su media?")
            ui.spoiler(
                "No tiene varianza, ni siquiera media. La media de n variables de Cauchy independientes vuelve a ser una "
                "Cauchy con el mismo parámetro: no se concentra ni se vuelve normal. El teorema central del límite exige "
                "varianza finita, y sin ella existen otros límites, las distribuciones estables, que estudió el propio Lévy."
            )

    with col_right:
        ui.right_panel()
        base = st.session_state["base"]
        if st.button("Otra simulación", key="clt_new", width="stretch"):
            st.session_state["clt_round"] += 1
        p, q, z = clt_charts(dark, base, n, v["seed"] + st.session_state["clt_round"])
        skew = float(stats.skew(z))
        ui.metrics([(f"Asimetría de la suma: {skew:+.3f}", "metric-a"),
                    (f"&#8473;(|Z| &gt; 1.96): {(np.abs(z) > 1.96).mean():.4f}", "metric-c")])
        ui.show(p, key="fig_clt_base")
        ui.show(q, key="fig_clt_sum")
        ui.footer_bar(f"Arriba, la distribución de una observación ({BASES[base].lower()}). Abajo, 20 000 sumas de {n} "
                      "observaciones, tipificadas, frente a la normal típica.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>probabilidad p</u> de la Bernoulli y el <u>tamaño n</u>")
        c1, c2 = st.columns(2)
        p = c1.select_slider("Probabilidad p", options=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5], value=v["p_be"],
                             key=ui.wkey(PAGE, "p_be"))
        n = c2.select_slider("Tamaño n", options=[10, 30, 100, 300, 1000, 2000], value=30, key="be_n")

        ui.planteamiento()
        ui.statement(
            "<b>Berry y Esseen (1941)</b><br><br>"
            "En muchos libros se lee que con treinta datos ya se puede usar la normal. Andrew Berry en 1941 y Carl-Gustav "
            "Esseen en 1942 demostraron, cada uno por su lado, cuánto se separa la distribución de la suma tipificada de "
            "la normal, y de qué depende. Lo comprobamos con la binomial, suma de n Bernoulli de parámetro p."
        )

        if ui.accordion_step("P3_A", "(A) La velocidad"):
            ui.content(
                "La desigualdad de Berry-Esseen acota la mayor diferencia entre F<sub>n</sub>, la distribución de la suma "
                "tipificada, y &Phi;. Escríbela con &rho; = &#120124;|X &minus; &mu;|<sup>3</sup>. ¿A qué ritmo decrece?"
            )
            ui.spoiler(
                "<div class='formula-box'>sup<sub>x</sub> |F<sub>n</sub>(x) &minus; &Phi;(x)| &le; C<sup>&rho;</sup>&frasl;<sub>&sigma;<sup>3</sup>&radic;n</sub></div>"
                "con una constante C menor que 0.48. El error decrece como 1/&radic;n: para dividirlo por diez hay que "
                "multiplicar los datos por cien. En la figura, las dos curvas son rectas de pendiente &minus;1/2 en escala "
                "doble logarítmica."
            )

        if ui.accordion_step("P3_B", "(B) La asimetría manda"):
            ui.content(
                "Para una Bernoulli, calcula &rho;/&sigma;<sup>3</sup>. ¿Cómo se comporta cuando p se acerca a 0?"
            )
            ui.spoiler(
                "Con q = 1 &minus; p, &rho; = pq(p<sup>2</sup> + q<sup>2</sup>) y &sigma;<sup>3</sup> = (pq)<sup>3/2</sup>, así que "
                "&rho;/&sigma;<sup>3</sup> = (p<sup>2</sup> + q<sup>2</sup>)/&radic;(pq), que crece sin límite cuando p &rarr; 0. Cuanto más "
                "raro es el suceso, más asimétrica la Bernoulli y más datos hacen falta para que la normal sirva."
            )

        if ui.accordion_step("P3_C", "(C) La regla de los treinta"):
            ui.content("Con p = 0.01 y n = 30, ¿cuánto se separa la binomial de la normal? ¿Y con p = 0.5?")
            ui.spoiler(
                "Con p = 0.5 y treinta datos, la distancia ronda las siete centésimas, casi toda debida a los saltos de la "
                "binomial, que la corrección de continuidad compensa. Con p = 0.01 "
                "supera el 0.4: la normal no se parece en nada, porque el número esperado de éxitos es 0.3. Ninguna "
                "regla fija vale para todas las distribuciones: el número de datos necesario depende de la asimetría, y "
                "por eso los apuntes añaden np &ge; 5 a la regla de n &ge; 30."
            )

    with col_right:
        ui.right_panel()
        dist = kolmogorov_distance(n, p)
        bound = berry_esseen_bound(n, p)
        ui.metrics([(f"sup |F<sub>{n}</sub> &minus; &Phi;| = {dist:.4f}", "metric-a"),
                    (f"Cota de Berry-Esseen: {min(bound, 1):.4f}", "metric-c")])
        ui.show(rate_chart(dark, p, n), key="fig_berry")
        ui.footer_bar(f"Con p = {p} y n = {n}: np = {n * p:.2f}. La distancia real siempre queda bajo la cota, y las dos "
                      "caen como 1/&radic;n.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) De Moivre y la binomial", "P1_A"),
        ("P2", "(II) Lindeberg y Lévy", "P2_A"),
        ("P3", "(III) Berry y Esseen", "P3_A"),
    ])

    if current == "INTRO":
        render_intro()
    elif current == "P1":
        render_problem_1(dark, v)
    elif current == "P2":
        render_problem_2(dark, v)
    elif current == "P3":
        render_problem_3(dark, v)

    ui.footer()


main()
