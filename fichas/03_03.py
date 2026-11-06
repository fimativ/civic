#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 3: las desigualdades de Márkov y Chebyshev.

La cota de Márkov con solo la media, la cota de Chebyshev en desviaciones
típicas frente a distribuciones concretas (y la que la alcanza) y el teorema
áureo de Bernoulli: cuántos ensayos hacen falta para fiarse de una frecuencia.
"""

from __future__ import annotations

from math import ceil

import numpy as np
import streamlit as st
from bokeh.models import BoxAnnotation, Span
from scipy import stats

import civic_ui as ui

TITLE = "Las desigualdades"
SYMBOL = "≤ 1/k²"
PAGE = "03_03"

SUPPORT = np.arange(0, 61)
FAMILIES = ["Poisson", "Geométrica", "Binomial", "Uniforme", "Dos puntos (extremal)"]
CHEB_FAMILIES = ["Dado", "Binomial", "Poisson", "Geométrica", "Tres puntos (extremal)"]
DELTAS = {"1 entre 20": 0.05, "1 entre 100": 0.01, "1 entre 1001": 1 / 1001}


def initial_values():
    return {
        "mu": ui.dint(3, 2, 6, "mu"),
        "K": ui.dint(12, 8, 24, "K"),
        "family": ui.dchoice("Poisson", FAMILIES[:4], "family"),
        "cheb": ui.dchoice("Binomial", CHEB_FAMILIES[:4], "cheb"),
        "k": ui.dchoice(2.0, [1.5, 2.0, 2.5, 3.0], "k"),
        "p": ui.dchoice(0.60, [0.30, 0.40, 0.50, 0.60, 0.70], "p"),
        "eps": ui.dchoice(0.02, [0.01, 0.02, 0.03, 0.05], "eps"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def markov_pmf(family: str, mu: int, K: int):
    x = SUPPORT
    if family == "Poisson":
        pmf = stats.poisson.pmf(x, mu)
    elif family == "Geométrica":
        p = 1 / (mu + 1)
        pmf = (1 - p) ** x * p
    elif family == "Binomial":
        pmf = stats.binom.pmf(x, 2 * mu, 0.5)
    elif family == "Uniforme":
        pmf = np.where(x <= 2 * mu, 1 / (2 * mu + 1), 0.0)
    else:
        pmf = np.zeros_like(x, dtype=float)
        pmf[0] = 1 - mu / K
        pmf[K] = mu / K
    return x, pmf / pmf.sum()


def cheb_pmf(family: str, k: float):
    if family == "Dado":
        x = np.arange(1, 7)
        pmf = np.full(6, 1 / 6)
    elif family == "Binomial":
        x = np.arange(0, 21)
        pmf = stats.binom.pmf(x, 20, 0.3)
    elif family == "Poisson":
        x = np.arange(0, 25)
        pmf = stats.poisson.pmf(x, 4)
    elif family == "Geométrica":
        x = np.arange(0, 40)
        pmf = 0.75 ** x * 0.25
    else:
        x = np.array([-k, 0.0, k])
        pmf = np.array([1 / (2 * k ** 2), 1 - 1 / k ** 2, 1 / (2 * k ** 2)])
    pmf = pmf / pmf.sum()
    mu = float((x * pmf).sum())
    sigma = float(np.sqrt(((x - mu) ** 2 * pmf).sum()))
    return x, pmf, mu, sigma


def chebyshev_trials(p: float, eps: float, delta: float) -> int:
    return ceil(p * (1 - p) / (delta * eps ** 2))


def exact_trials(p: float, eps: float, delta: float, limit: int = 200000) -> int:
    """Menor n a partir del cual ℙ(|X/n − p| ≥ ε) ≤ δ para X ~ B(n, p)."""
    ns = np.arange(1, limit + 1)
    lo = np.floor(ns * (p - eps) + 1e-9)
    hi = np.ceil(ns * (p + eps) - 1e-9)
    prob = stats.binom.cdf(lo, ns, p) + stats.binom.sf(hi - 1, ns, p)
    bad = np.where(prob > delta)[0]
    return int(ns[bad[-1] + 1]) if len(bad) and bad[-1] + 1 < len(ns) else (1 if not len(bad) else limit)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def markov_chart(dark, x, pmf, mu: int, K: int):
    tail = np.array([pmf[x >= t].sum() for t in x])
    ts = x[1:]
    p = ui.new_figure(dark, height=320, x_axis_label="umbral K", y_axis_label="probabilidad",
                      x_range=(0, 40), y_range=(0, 1.02))
    p.vbar(x=x, top=pmf, width=0.7, color=ui.GREY_LINE, alpha=0.5, legend_label="ℙ(X = x)")
    p.line(ts, np.minimum(1, mu / ts), line_width=4, color=ui.UBU_RED, line_dash="dashed",
           legend_label="cota de Márkov μ/K")
    p.line(ts, tail[1:], line_width=4, color=ui.BLUE_LINE, legend_label="ℙ(X ≥ K)")
    p.add_layout(Span(location=K, dimension="height", line_color=ui.ORANGE_LINE, line_width=2))
    return ui.style_legend(p, dark, "top_right")


def cheb_chart(dark, x, pmf, mu: float, sigma: float, k: float):
    inside = np.abs(x - mu) < k * sigma - 1e-12
    colours = [ui.BLUE_LINE if i else ui.UBU_RED for i in inside]
    span = x.max() - x.min() if len(x) > 1 else 1
    width = 0.7 if len(x) > 3 else span * 0.08
    p = ui.new_figure(dark, height=320, x_axis_label="x", y_axis_label="ℙ(X = x)",
                      x_range=(x.min() - 1.5 * sigma, x.max() + 1.5 * sigma), y_range=(0, pmf.max() * 1.2))
    p.add_layout(BoxAnnotation(left=mu - k * sigma, right=mu + k * sigma, fill_color=ui.GREEN_LINE, fill_alpha=0.1))
    p.vbar(x=x, top=pmf, width=width, fill_color=colours, line_color=None)
    p.add_layout(Span(location=mu, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed", line_width=2))
    return p


def trials_chart(dark, n_cheb: int, n_exact: int):
    labels = ["Chebyshev", "Bernoulli (1713)", "exacto"]
    values = [n_cheb, 25550, n_exact]
    p = ui.new_figure(dark, height=280, x_range=labels, y_axis_type="log", y_range=(10, max(values) * 3),
                      y_axis_label="ensayos (escala logarítmica)")
    p.vbar(x=labels, bottom=1, top=values, width=0.6, fill_color=[ui.RED_LINE, ui.GREY_LINE, ui.GREEN_LINE],
           line_color=None)
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "15px"
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué se puede decir sabiendo solo la media?</b>")
        ui.content(
            "Muchas veces no se conoce la distribución de una variable, pero sí su media o su varianza. "
            "Las desigualdades de esta ficha dan cotas que valen para <b>cualquier</b> distribución: son "
            "universales, y por eso mismo conservadoras. La primera solo pide que la variable no sea "
            "negativa. <i>Prueba a escribirla.</i>"
        )
        ui.formula_hidden("X &ge; 0, &nbsp; K &gt; 0 &nbsp;&rArr;&nbsp; &#8473;(X &ge; K) &le; "
                          "<sup>&#120124;[X]</sup>&frasl;<sub>K</sub>", hint="Pulsa para revelar la desigualdad de Márkov")
        ui.content(
            "Aplicada a la variable (X &minus; &mu;)<sup>2</sup>, que tampoco es negativa, se convierte en "
            "una cota para la probabilidad de alejarse de la media. <i>Escríbela con la varianza.</i>"
        )
        ui.formula_hidden("&#8473;(|X &minus; &mu;| &ge; &epsilon;) &le; <sup>&#120141;(X)</sup>&frasl;<sub>"
                          "&epsilon;<sup>2</sup></sub>", hint="Pulsa para revelar la desigualdad de Chebyshev")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La cota de Márkov</b><br>"
            "<i>Si la renta media de un pueblo es de unos pocos tharni, ¿cuántos vecinos pueden ser "
            "ricos?</i><br><br>"
            "<b>II. Los valores medios de Chebyshev (1867)</b><br>"
            "<i>Mide en desviaciones típicas con Pafnuti Chebyshev y busca la distribución que pone su "
            "cota en apuros.</i><br><br>"
            "<b>III. El teorema áureo de Bernoulli (1713)</b><br>"
            "<i>¿Cuántas extracciones de una urna hacen falta para conocer su composición? Jacob Bernoulli "
            "contestó con un número enorme.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>distribución</u>, la <u>media &mu;</u> y el <u>umbral K</u>")
        family = st.radio("Distribución", FAMILIES, index=FAMILIES.index(v["family"]), horizontal=True,
                          key=ui.wkey(PAGE, "family"))
        c1, c2 = st.columns(2)
        mu = c1.slider("Media μ (tharni)", 1, 8, v["mu"], 1, key=ui.wkey(PAGE, "mu"))
        K = c2.slider("Umbral K (tharni)", mu + 1, 40, max(v["K"], mu + 1), 1, key=ui.wkey(PAGE, f"K{mu}"))

        ui.planteamiento()
        ui.statement(
            "<b>La cota de Márkov</b><br><br>"
            "La desigualdad aparece ya en los trabajos de Pafnuti Chebyshev, pero lleva el nombre de su "
            "alumno más famoso, Andréi Márkov (1856-1922), el de las cadenas. Sirve para preguntas como "
            f"esta: en un pueblo la riqueza media es de {v['mu']} tharni por vecino y nadie tiene deudas. "
            f"Sin saber nada más, ¿qué fracción de los vecinos puede tener {v['K']} tharni o más?"
        )

        if ui.accordion_step("P1_A", "(A) La desigualdad"):
            ui.content(
                "Parte la esperanza en dos sumas: los valores que alcanzan el umbral K y los que no. Acota la "
                "primera por debajo y desprecia la segunda. ¿Qué obtienes?"
            )
            ui.spoiler(
                "Como todos los términos son no negativos, quitar los valores menores que K solo reduce la "
                "suma, y en los que quedan x<sub>i</sub> &ge; K:"
                "<div class='formula-box'>&#120124;[X] &ge; &sum;<sub>x<sub>i</sub> &ge; K</sub> x<sub>i</sub>"
                "&#8473;(X = x<sub>i</sub>) &ge; K&middot;&#8473;(X &ge; K)</div>"
                f"Con media {v['mu']} tharni, a lo sumo un {100 * v['mu'] / v['K']:.0f} % de los vecinos puede "
                f"tener {v['K']} o más: si fueran más, ellos solos ya subirían la media por encima de {v['mu']}."
            )

        if ui.accordion_step("P1_B", "(B) ¿Se puede mejorar?"):
            ui.content(
                "Prueba las distintas distribuciones. ¿Alguna llega a tocar la cota? Elige la de dos puntos "
                "y explica por qué la cota no puede mejorarse sin saber algo más que la media."
            )
            ui.spoiler(
                "La distribución que vale K con probabilidad &mu;/K y 0 en otro caso tiene media &mu; y "
                "&#8473;(X &ge; K) = &mu;/K exactamente: alcanza la cota. Por tanto, ninguna desigualdad que "
                "use solo la media y la no negatividad puede dar algo mejor. Las demás distribuciones quedan "
                "muy por debajo: la cota es universal, pero conservadora."
            )

        if ui.accordion_step("P1_C", "(C) Márkov con otras funciones"):
            ui.content(
                "La desigualdad vale para cualquier función no negativa g(X): &#8473;(g(X) &ge; K) &le; "
                "&#120124;[g(X)]/K. ¿Qué se obtiene con g(X) = (X &minus; &mu;)<sup>2</sup>?"
            )
            ui.spoiler(
                "Con g(X) = (X &minus; &mu;)<sup>2</sup> y K = &epsilon;<sup>2</sup>, la esperanza de g es la "
                "varianza y el suceso {(X &minus; &mu;)<sup>2</sup> &ge; &epsilon;<sup>2</sup>} es "
                "{|X &minus; &mu;| &ge; &epsilon;}: sale la desigualdad de Chebyshev, la del problema "
                "siguiente. Con g(X) = e<sup>tX</sup> salen cotas exponenciales mucho más finas, la base "
                "de buena parte de la probabilidad moderna."
            )

    with col_right:
        ui.right_panel()
        x, pmf = markov_pmf(family, mu, K)
        tail = float(pmf[x >= K].sum())
        ui.metrics([
            (f"&#8473;(X &ge; {K}) = {tail:.4f}", "metric-a"),
            (f"Cota &mu;/K = {mu / K:.4f}", "metric-c"),
        ])
        ui.show(markov_chart(dark, x, pmf, mu, K), key="fig_markov")
        ui.footer_bar(f"Distribución {family.lower()} con media {mu}: la cola real queda "
                      f"{'exactamente en' if abs(tail - mu / K) < 1e-9 else 'por debajo de'} la cota de Márkov.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>distribución</u> y el <u>número de desviaciones k</u>")
        family = st.radio("Distribución", CHEB_FAMILIES, index=CHEB_FAMILIES.index(v["cheb"]), horizontal=True,
                          key=ui.wkey(PAGE, "cheb"))
        k = st.slider("k (desviaciones típicas)", 1.0, 4.0, v["k"], 0.1, key=ui.wkey(PAGE, "k"))

        ui.planteamiento()
        ui.statement(
            "<b>Los valores medios de Chebyshev (1867)</b><br><br>"
            "Pafnuti Chebyshev (1821-1894), fundador de la escuela de San Petersburgo, publicó en 1867 un "
            "artículo sobre los valores medios con una desigualdad que el francés Irénée-Jules Bienaymé "
            "había publicado en 1853. Dice cuánta probabilidad puede quedar lejos de la media, medida "
            "en desviaciones típicas, sea cual sea la distribución."
        )

        if ui.accordion_step("P2_A", "(A) En desviaciones típicas"):
            ui.content(
                "Escribe la desigualdad de Chebyshev con &epsilon; = k&sigma;. ¿Qué garantiza para k = 2? ¿Y para "
                "k = 3? ¿Y para k = 1?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(|X &minus; &mu;| &ge; k&sigma;) &le; <sup>1</sup>&frasl;"
                "<sub>k<sup>2</sup></sub></div>"
                "Con k = 2, al menos el 75 % de la probabilidad está a menos de dos desviaciones de la media; "
                "con k = 3, al menos el 89 %. Con k = 1 la cota vale 1 y no dice nada."
            )

        if ui.accordion_step("P2_B", "(B) La realidad es más amable"):
            ui.content(
                "Compara la probabilidad real fuera de la banda verde con la cota 1/k<sup>2</sup> para un dado, "
                "una binomial, una Poisson y una geométrica. ¿Cuánto se separan? ¿Qué distribución se acerca más?"
            )
            ui.spoiler(
                "Para las distribuciones habituales la probabilidad real es muy inferior a la cota: un dado ni "
                "siquiera tiene valores a dos desviaciones de su media. Las distribuciones asimétricas, con una "
                "cola derecha más pesada, como la geométrica o la Poisson, se acercan más, aunque siguen lejos de la cota. Para una normal, que llegará en el tema siguiente, "
                "fuera de 2&sigma; queda en torno al 5 % y fuera de 3&sigma; un 0.3 %, frente al 25 % y al "
                "11 % que garantiza Chebyshev."
            )

        if ui.accordion_step("P2_C", "(C) El peor caso"):
            ui.content(
                "Elige la distribución de tres puntos: vale &minus;k y k con probabilidad 1/(2k<sup>2</sup>) "
                "cada uno, y 0 en el resto. Calcula su media y su varianza. ¿Qué probabilidad queda a "
                "distancia k&sigma; o más de la media?"
            )
            ui.spoiler(
                "La media es 0 por simetría y la varianza es 2&middot;k<sup>2</sup>&middot;1/(2k<sup>2</sup>) "
                "= 1, así que &sigma; = 1 y los extremos están exactamente a k desviaciones. Quedan fuera "
                "&#8473; = 1/k<sup>2</sup>: la cota se alcanza. Chebyshev no puede mejorarse si solo se "
                "conocen la media y la varianza."
            )

    with col_right:
        ui.right_panel()
        x, pmf, mu, sigma = cheb_pmf(family, k)
        outside = float(pmf[np.abs(x - mu) >= k * sigma - 1e-9].sum())
        ui.metrics([
            (f"&#8473;(|X &minus; &mu;| &ge; {k:.1f}&sigma;) = {outside:.4f}", "metric-a"),
            (f"Cota 1/k<sup>2</sup> = {1 / k ** 2:.4f}", "metric-c"),
        ])
        ui.show(cheb_chart(dark, x, pmf, mu, sigma, k), key="fig_cheb")
        ui.footer_bar(f"&mu; = {mu:.3f}, &sigma; = {sigma:.3f}. En verde la banda &mu; &plusmn; {k:.1f}&sigma;; en rojo, "
                      "los valores que quedan fuera.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>proporción p</u>, la <u>precisión &epsilon;</u> y la <u>certeza</u>")
        c1, c2 = st.columns(2)
        p = c1.select_slider("Proporción de bolas blancas p", options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                             value=v["p"], key=ui.wkey(PAGE, "p"))
        eps = c2.select_slider("Precisión ε", options=[0.01, 0.02, 0.03, 0.05, 0.10], value=v["eps"],
                               key=ui.wkey(PAGE, "eps"))
        label = st.radio("Probabilidad de equivocarse δ", list(DELTAS), index=2, horizontal=True, key="delta")
        delta = DELTAS[label]

        ui.planteamiento()
        ui.statement(
            "<b>El teorema áureo de Bernoulli (1713)</b><br><br>"
            "Jacob Bernoulli trabajó veinte años en lo que llamó su teorema áureo, publicado tras su muerte "
            "en el <i>Arte de la conjetura</i>. Quería justificar que la frecuencia observada en muchas "
            "extracciones de una urna se acerca a la proporción real de bolas. Su ejemplo: una urna con 3000 "
            "bolas blancas y 2000 negras, y la pregunta de cuántas extracciones con devolución hacen falta "
            "para que la frecuencia de blancas quede a menos de 1/50 de 3/5 con una certeza moral de mil "
            "contra uno."
        )

        if ui.accordion_step("P3_A", "(A) La frecuencia es una media"):
            ui.content(
                "Sea X el número de blancas en n extracciones con devolución. ¿Qué distribución tiene? "
                "Calcula la media y la varianza de la frecuencia X/n."
            )
            ui.spoiler(
                "X es binomial B(n, p), con media np y varianza np(1 &minus; p). Por las propiedades de la "
                "esperanza y la varianza:"
                "<div class='formula-box'>&#120124;[X/n] = p &nbsp;&nbsp; &#120141;(X/n) = "
                "<sup>p(1 &minus; p)</sup>&frasl;<sub>n</sub></div>"
                "La frecuencia está centrada en la proporción verdadera y su varianza se hace pequeña al "
                "crecer n."
            )

        if ui.accordion_step("P3_B", "(B) Chebyshev da una respuesta"):
            ui.content(
                "Aplica la desigualdad de Chebyshev a X/n. ¿Cuántas extracciones garantizan que "
                "&#8473;(|X/n &minus; p| &ge; &epsilon;) &le; &delta;? ¿Y si no se conoce p?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(|X/n &minus; p| &ge; &epsilon;) &le; <sup>p(1 &minus; p)</sup>"
                "&frasl;<sub>n&epsilon;<sup>2</sup></sub> &le; &delta; &nbsp;&lArr;&nbsp; n &ge; "
                "<sup>p(1 &minus; p)</sup>&frasl;<sub>&delta;&epsilon;<sup>2</sup></sub></div>"
                "Sin conocer p basta usar p(1 &minus; p) &le; 1/4. Y como la cota tiende a cero al crecer n, "
                "la frecuencia converge en probabilidad a p: es la ley débil de los grandes números, que "
                "volverá en el último tema."
            )

        if ui.accordion_step("P3_C", "(C) Tres respuestas a la misma pregunta"):
            ui.content(
                "Compara a la derecha el número de extracciones que exige Chebyshev, las 25 550 que obtuvo "
                "Bernoulli con su propio argumento y el número exacto calculado con la binomial. ¿Qué te dice "
                "esto sobre las cotas universales?"
            )
            ui.spoiler(
                "Con p = 3/5, &epsilon; = 1/50 y &delta; = 1/1001, Chebyshev pide del orden de seiscientas mil "
                "extracciones; Bernoulli, con una acotación más fina de las colas de la binomial, se quedó en "
                "25 550; y el cálculo exacto da algo más de seis mil. Las cotas universales garantizan, pero "
                "desperdician: para afinar hace falta saber algo más de la distribución, y el teorema central "
                "del límite será esa herramienta."
            )

    with col_right:
        ui.right_panel()
        n_cheb = chebyshev_trials(p, eps, delta)
        n_exact = exact_trials(p, eps, delta)
        ui.metrics([
            (f"Chebyshev: n &ge; {ui.fmt_int(n_cheb)}", "metric-c"),
            (f"Exacto: n &ge; {ui.fmt_int(n_exact)}", "metric-a"),
        ])
        ui.show(trials_chart(dark, n_cheb, n_exact), key="fig_trials")
        ui.footer_bar(f"Para p = {p}, &epsilon; = {eps} y &delta; = {delta:.4g}: Chebyshev exige "
                      f"{n_cheb / n_exact:.0f} veces más extracciones de las necesarias. La barra gris es el "
                      "número de Bernoulli para su urna.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La cota de Márkov", "P1_A"),
        ("P2", "(II) Los valores medios de Chebyshev", "P2_A"),
        ("P3", "(III) El teorema áureo de Bernoulli", "P3_A"),
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
