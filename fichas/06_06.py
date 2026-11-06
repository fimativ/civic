#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 6: aplicaciones del teorema central del límite.

La sobreventa de billetes de avión (cuántas plazas vender de más), el paseo
aleatorio de Pearson (el teorema en dos dimensiones) y el error del método de
Montecarlo (por qué cada cifra exacta cuesta cien veces más).
"""

from __future__ import annotations

from math import erf, pi, sqrt

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Aplicaciones del TCL"
SYMBOL = "Φ(z)"
PAGE = "06_06"

SEATS = 100
EXACT = sqrt(pi) / 2 * erf(1)      # ∫₀¹ e^(−x²) dx


def initial_values():
    return {
        "sold": ui.dint(105, 100, 115, "sold"),
        "show": ui.dchoice(0.90, [0.85, 0.88, 0.90, 0.92, 0.95], "show"),
        "fare": ui.dchoice(100, [80, 100, 150], "fare"),
        "comp": ui.dchoice(400, [200, 300, 400, 600, 800], "comp"),
        "steps": ui.dchoice(100, [10, 25, 100, 400, 1000], "steps"),
        "samples": ui.dchoice(100, [10, 100, 1000, 10000], "samples"),
        "seed": int(ui.r("pearson") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "walk_round": 0, "mc_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def overbooking(n: int, p: float, fare: float, comp: float):
    k = np.arange(0, n + 1)
    pmf = stats.binom.pmf(k, n, p)
    bumped = np.maximum(k - SEATS, 0)
    p_over = float(pmf[k > SEATS].sum())
    clt = float(stats.norm.sf((SEATS + 0.5 - n * p) / np.sqrt(n * p * (1 - p))))
    profit = n * fare - comp * float((bumped * pmf).sum())
    return p_over, clt, profit


def best_sales(p: float, fare: float, comp: float):
    ns = np.arange(SEATS, SEATS + 40)
    profits = [overbooking(int(n), p, fare, comp)[2] for n in ns]
    return int(ns[int(np.argmax(profits))]), ns, np.array(profits)


def walks(n: int, walkers: int, seed: int):
    rng = np.random.default_rng(seed)
    angles = rng.uniform(0, 2 * np.pi, (walkers, n))
    x = np.cumsum(np.cos(angles), axis=1)
    y = np.cumsum(np.sin(angles), axis=1)
    return x, y


def mc_estimates(n: int, reps: int, seed: int):
    u = np.random.default_rng(seed).uniform(0, 1, (reps, n))
    g = np.exp(-u ** 2)
    return g.mean(axis=1), g.std(axis=1, ddof=1)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def booking_charts(dark, n: int, p: float, ns, profits):
    k = np.arange(80, n + 1)
    pmf = stats.binom.pmf(k, n, p)
    fig = ui.new_figure(dark, height=250, x_axis_label="pasajeros que se presentan", y_axis_label="probabilidad",
                        x_range=(80, max(n, SEATS + 5) + 1))
    fig.vbar(x=k, top=pmf, width=0.85, fill_color=[ui.RED_LINE if kk > SEATS else ui.BLUE_LINE for kk in k],
             line_color=None)
    xs = np.linspace(80, n + 1, 300)
    fig.line(xs, stats.norm.pdf(xs, n * p, np.sqrt(n * p * (1 - p))), line_width=3, color=ui.UBU_YELLOW)
    fig.add_layout(Span(location=SEATS + 0.5, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed", line_width=2))
    g = ui.new_figure(dark, height=200, x_axis_label="billetes vendidos", y_axis_label="ingreso esperado",
                      x_range=(ns[0], ns[-1]))
    g.line(ns, profits, line_width=3, color=ui.GREEN_LINE)
    g.add_layout(Span(location=n, dimension="height", line_color=ui.UBU_RED, line_width=2))
    return fig, g


def walk_charts(dark, x, y, n: int):
    lim = 3 * np.sqrt(n)
    fig = ui.new_figure(dark, height=300, x_range=(-lim, lim), y_range=(-lim, lim), match_aspect=True)
    fig.grid.visible = False
    fig.scatter(x[:, -1], y[:, -1], size=3, color=ui.GREY_LINE, alpha=0.4)
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE]
    for i in range(3):
        fig.line(np.concatenate(([0], x[i])), np.concatenate(([0], y[i])), line_width=2, color=palette[i])
    fig.circle(x=[0], y=[0], radius=np.sqrt(n), fill_alpha=0, line_color=ui.UBU_RED, line_dash="dashed", line_width=2)
    r = np.hypot(x[:, -1], y[:, -1])
    rs = np.linspace(0, lim, 300)
    edges = np.linspace(0, lim, 41)
    h, _ = np.histogram(r, bins=edges)
    g = ui.new_figure(dark, height=220, x_axis_label="distancia al punto de partida", y_axis_label="densidad",
                      x_range=(0, lim))
    g.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / (len(r) * (edges[1] - edges[0])), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.6, line_color=None, legend_label="caminantes simulados")
    g.line(rs, 2 * rs / n * np.exp(-rs ** 2 / n), line_width=3, color=ui.BLUE_LINE, legend_label="(2r/n)e^(−r²/n)")
    ui.style_legend(g, dark, "top_right")
    return fig, g


def mc_charts(dark, est, n: int):
    sigma = float(np.sqrt(sqrt(pi / 8) * erf(sqrt(2)) - EXACT ** 2))
    sd = sigma / np.sqrt(n)
    lo, hi = EXACT - 5 * sd, EXACT + 5 * sd
    edges = np.linspace(lo, hi, 41)
    h, _ = np.histogram(est, bins=edges)
    fig = ui.new_figure(dark, height=250, x_axis_label=f"estimación con {n} puntos", y_axis_label="densidad",
                        x_range=(lo, hi))
    fig.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / (len(est) * (edges[1] - edges[0])),
             fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None)
    xs = np.linspace(lo, hi, 300)
    fig.line(xs, stats.norm.pdf(xs, EXACT, sd), line_width=3, color=ui.BLUE_LINE)
    fig.add_layout(Span(location=EXACT, dimension="height", line_color=ui.UBU_RED, line_width=2))
    ns = np.array([10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000])
    g = ui.new_figure(dark, height=200, x_axis_type="log", y_axis_type="log", x_axis_label="puntos n",
                      y_axis_label="error típico σ/√n", x_range=(10, 100000))
    g.line(ns, sigma / np.sqrt(ns), line_width=3, color=ui.ORANGE_LINE)
    g.scatter([n], [sd], size=12, color=ui.UBU_RED)
    return fig, g, sigma


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Para qué sirve el teorema central del límite?</b>")
        ui.content(
            "Su utilidad práctica es enorme: permite calcular probabilidades sobre sumas y medias de muchas variables "
            "sin conocer la distribución exacta, con solo su media y su varianza. <i>Escribe la aproximación que se usa "
            "en la práctica.</i>"
        )
        ui.formula_hidden("&#8473;(S<sub>n</sub> &le; s) &asymp; &Phi;(<sup>s &minus; n&mu;</sup>&frasl;<sub>&sigma;&radic;n</sub>)")
        ui.content(
            "En esta ficha se aplica a tres problemas: cuántos billetes vender en un avión, dónde acaba quien camina al "
            "azar y cuánto se equivoca una simulación. El último es también el que da la medida de todas las "
            "simulaciones de esta aplicación."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La sobreventa de billetes (1972)</b><br>"
            "<i>Una aerolínea vende más plazas de las que tiene, y un pasajero muy conocido se queda en tierra.</i>"
            "<br><br>"
            "<b>II. El paseo de Pearson (1905)</b><br>"
            "<i>Karl Pearson preguntó en una revista dónde acaba alguien que camina sin rumbo. Lord Rayleigh ya tenía la "
            "respuesta.</i><br><br>"
            "<b>III. El error de Montecarlo (1948)</b><br>"
            "<i>Calcula una integral con puntos al azar y descubre cuánto cuesta cada cifra exacta.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>billetes vendidos</u>, la <u>probabilidad de presentarse</u> y la <u>compensación</u>")
        n = st.slider("Billetes vendidos para 100 plazas", 100, 125, v["sold"], 1, key=ui.wkey(PAGE, "sold"))
        c1, c2, c3 = st.columns(3)
        p = c1.select_slider("Se presenta", options=[0.80, 0.85, 0.88, 0.90, 0.92, 0.95, 0.98], value=v["show"],
                             key=ui.wkey(PAGE, "show"))
        fare = c2.select_slider("Billete (tharni)", options=[80, 100, 150], value=v["fare"], key=ui.wkey(PAGE, "fare"))
        comp = c3.select_slider("Compensación (tharni)", options=[200, 300, 400, 600, 800], value=v["comp"],
                                key=ui.wkey(PAGE, "comp"))

        ui.planteamiento()
        ui.statement(
            "<b>La sobreventa de billetes (1972)</b><br><br>"
            "En 1972 la aerolínea Allegheny dejó en tierra a Ralph Nader, el abogado defensor de los consumidores, porque "
            "había vendido más billetes que plazas. Nader demandó y el caso llegó al Tribunal Supremo de Estados Unidos. "
            "Las aerolíneas venden de más porque una parte de los viajeros no se presenta. Nuestro avión tiene 100 "
            "plazas y cada viajero se presenta con probabilidad p, independientemente de los demás. A quien se queda en "
            "tierra hay que compensarle."
        )

        if ui.accordion_step("P1_A", "(A) Cuántos se presentan"):
            ui.content(
                "Si se venden n billetes, ¿qué distribución tiene el número X de viajeros que se presentan? Aproxímala con "
                "el teorema central del límite y calcula &#8473;(X &gt; 100)."
            )
            ui.spoiler(
                "X es binomial B(n, p), suma de n Bernoulli independientes. Por De Moivre-Laplace, con corrección de "
                "continuidad:"
                "<div class='formula-box'>&#8473;(X &gt; 100) &asymp; 1 &minus; &Phi;(<sup>100.5 &minus; np</sup>&frasl;<sub>&radic;(np(1 &minus; p))</sub>)</div>"
                "La aproximación da el orden de magnitud correcto, pero con p cerca de 1 la binomial es asimétrica y la "
                "normal exagera un poco la cola derecha: compara a la derecha la probabilidad exacta y la aproximada."
            )

        if ui.accordion_step("P1_B", "(B) Cuántos billetes vender"):
            ui.content(
                "La aerolínea quiere que el avión salga sobrevendido como mucho un 5 % de las veces. ¿Cuántos billetes "
                "puede vender? Resuelve la desigualdad con la normal."
            )
            ui.spoiler(
                "Hace falta np + 1.645&radic;(np(1 &minus; p)) &le; 100.5. Con p = 0.9 sale n = 106: vender seis billetes de "
                "más deja el riesgo justo por debajo del 5 %, y la binomial exacta confirma que es aún menor. Al aumentar n, la media np crece como n y la dispersión "
                "solo como &radic;n, así que el margen de seguridad necesario es relativamente pequeño."
            )

        if ui.accordion_step("P1_C", "(C) El precio de equivocarse"):
            ui.content(
                "Con la compensación por viajero en tierra, calcula el ingreso esperado para cada número de billetes. "
                "¿Dónde está el óptimo? ¿Qué cambió tras el caso Nader?"
            )
            ui.spoiler(
                "El ingreso esperado es n&middot;billete &minus; compensación&middot;&#120124;[(X &minus; 100)<sup>+</sup>], y la curva verde de "
                "la derecha tiene un máximo: vender de más compensa mientras el coste esperado de las compensaciones "
                "crezca más despacio que los ingresos. Tras la sentencia, las aerolíneas tuvieron que informar de la "
                "práctica, y acabó imponiéndose una idea del economista Julian Simon: en lugar de elegir a quién dejar "
                "en tierra, subastar la compensación entre voluntarios."
            )

    with col_right:
        ui.right_panel()
        p_over, clt, profit = overbooking(n, p, fare, comp)
        best, ns, profits = best_sales(p, fare, comp)
        ui.metrics([(f"&#8473;(sobreventa) = {p_over:.4f}", "result-no" if p_over > 0.05 else "result-yes"),
                    (f"Con la normal: {clt:.4f}", "metric-c"),
                    (f"Óptimo: {best} billetes", "metric-a")])
        fig, g = booking_charts(dark, n, p, ns, profits)
        ui.show(fig, key="fig_booking")
        ui.show(g, key="fig_booking_profit")
        ui.footer_bar(f"Arriba, la distribución de los que se presentan (en rojo, más de 100) con la campana encima. "
                      f"Abajo, el ingreso esperado: {profit:,.0f} tharni con {n} billetes.".replace(",", " "))


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de pasos n</u>")
        n = st.select_slider("Pasos", options=[5, 10, 25, 50, 100, 400, 1000], value=v["steps"], key=ui.wkey(PAGE, "steps"),
                             label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El paseo de Pearson (1905)</b><br><br>"
            "En 1905 Karl Pearson pidió ayuda en la revista <i>Nature</i>: un hombre camina n tramos de un metro, cada uno en "
            "una dirección al azar; ¿a qué distancia del punto de partida acaba? Lord Rayleigh contestó a la semana "
            "siguiente: lo había resuelto en 1880 estudiando la suma de vibraciones de fases aleatorias. Pearson "
            "concluyó, con humor, que el mejor sitio para buscar a un borracho que todavía se tiene en pie es cerca de donde "
            "empezó."
        )

        if ui.accordion_step("P2_A", "(A) Un paso"):
            ui.content(
                "Un paso es el vector (cos&Theta;, sen&Theta;) con &Theta; uniforme. Calcula la media y la matriz de covarianzas "
                "de sus dos componentes."
            )
            ui.spoiler(
                "Por simetría, las dos medias son cero. &#120124;[cos<sup>2</sup>&Theta;] = &#120124;[sen<sup>2</sup>&Theta;] = 1/2 y "
                "&#120124;[cos&Theta; sen&Theta;] = 0: la matriz de covarianzas es (1/2)I. Las componentes son incorreladas, "
                "aunque no independientes."
            )

        if ui.accordion_step("P2_B", "(B) El teorema en el plano"):
            ui.content(
                "La posición final es la suma de n pasos independientes. ¿Qué distribución tiene aproximadamente? ¿Cómo "
                "crece la distancia típica al origen?"
            )
            ui.spoiler(
                "Por la versión vectorial del teorema central del límite, la posición final es aproximadamente normal "
                "bidimensional con media 0 y matriz de covarianzas (n/2)I. La distancia típica crece como &radic;n, no como n: "
                "cien pasos alejan unos diez metros. El círculo rojo tiene radio &radic;n."
            )

        if ui.accordion_step("P2_C", "(C) Cerca del principio, pero no en él"):
            ui.content(
                "La densidad de la posición final es máxima en el origen. ¿Significa eso que lo más probable es acabar a "
                "distancia casi cero? Mira el histograma de distancias."
            )
            ui.spoiler(
                "No. La distancia R a una normal bidimensional de varianza n/2 por componente tiene la densidad de Rayleigh"
                "<div class='formula-box'>f(r) = <sup>2r</sup>&frasl;<sub>n</sub> e<sup>&minus;r<sup>2</sup>/n</sup></div>"
                "que vale cero en r = 0 y es máxima en r = &radic;(n/2). La posición más probable es el origen, pero hay muy "
                "poco sitio cerca del origen y mucho anillo lejos de él: es la misma idea del jacobiano r de las "
                "coordenadas polares de Box y Muller. La ocurrencia de Pearson era, a medias, cierta."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otros 2000 caminantes", key="walk_new", width="stretch"):
            st.session_state["walk_round"] += 1
        x, y = walks(n, 2000, v["seed"] + st.session_state["walk_round"])
        r = np.hypot(x[:, -1], y[:, -1])
        ui.metrics([(f"Distancia media: {r.mean():.2f}", "metric-a"), (f"Teoría &radic;(&pi;n)/2 = {np.sqrt(np.pi * n) / 2:.2f}", "metric-c")])
        fig, g = walk_charts(dark, x, y, n)
        ui.show(fig, key="fig_walk")
        ui.show(g, key="fig_walk_r")
        ui.footer_bar(f"Arriba, tres paseos de {n} pasos y el punto final de 2000 caminantes. Abajo, la distancia final frente "
                      "a la densidad de Rayleigh.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de puntos n</u>")
        n = st.select_slider("Puntos al azar", options=[10, 30, 100, 300, 1000, 3000, 10000], value=v["samples"],
                             key=ui.wkey(PAGE, "samples"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El error de Montecarlo (1948)</b><br><br>"
            "En la primavera de 1948, el ENIAC, uno de los primeros ordenadores, ejecutó en Aberdeen (Maryland), por encargo de Los Álamos, las "
            "primeras simulaciones de Montecarlo de la difusión de neutrones, programadas por Klára Dán von Neumann. Un año "
            "después, Nicholas Metropolis y Stanisław Ulam publicaron el método. Su idea más sencilla: para calcular "
            "I = &int;<sub>0</sub><sup>1</sup> g(x) dx, se toman n puntos U<sub>i</sub> al azar y se promedia g(U<sub>i</sub>). Probamos con "
            "g(x) = e<sup>&minus;x<sup>2</sup></sup>, que no tiene primitiva elemental."
        )

        if ui.accordion_step("P3_A", "(A) Por qué funciona"):
            ui.content("¿Cuál es la esperanza de g(U) con U uniforme en (0, 1)? ¿A qué converge el promedio?")
            ui.spoiler(
                "Por la ley del estadístico inconsciente, &#120124;[g(U)] = &int;<sub>0</sub><sup>1</sup> g(x) dx = I. Por la ley fuerte, el "
                "promedio de las g(U<sub>i</sub>) converge casi seguro a I: el método de Montecarlo es una ley de los "
                "grandes números convertida en algoritmo."
            )

        if ui.accordion_step("P3_B", "(B) El tamaño del error"):
            ui.content(
                "Con el teorema central del límite, describe el error del promedio. ¿Cómo se construye un intervalo que "
                "contenga a I con un 95 % de probabilidad?"
            )
            ui.spoiler(
                "El error es aproximadamente normal con media 0 y desviación &sigma;/&radic;n, donde &sigma;<sup>2</sup> = &#120141;(g(U)). "
                "Sustituyendo &sigma; por la desviación de la muestra, que por Slutsky no cambia el límite:"
                "<div class='formula-box'>I &isin; promedio &plusmn; 1.96&middot;<sup>S</sup>&frasl;<sub>&radic;n</sub> &nbsp; con probabilidad &asymp; 0.95</div>"
                "Es el primer intervalo de confianza que aparece en la asignatura."
            )

        if ui.accordion_step("P3_C", "(C) Cien veces más por cada cifra"):
            ui.content(
                "¿Cuántos puntos hay que añadir para ganar una cifra decimal exacta? ¿Por qué, aun así, Montecarlo es el "
                "método preferido para integrales en muchas dimensiones?"
            )
            ui.spoiler(
                "El error cae como 1/&radic;n: para dividirlo por diez hace falta multiplicar n por cien. Es lento, pero esa "
                "velocidad no depende de la dimensión: el error sigue cayendo como 1/&radic;n en cien variables igual que en una, mientras que "
                "las reglas de cuadratura en una rejilla se vuelven imposibles. Por eso la física de partículas, las "
                "finanzas y esta misma aplicación confían en él."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otras 2000 estimaciones", key="mc_new", width="stretch"):
            st.session_state["mc_round"] += 1
        est, sds = mc_estimates(n, 2000, v["seed"] + st.session_state["mc_round"])
        fig, g, sigma = mc_charts(dark, est, n)
        cover = float((np.abs(est - EXACT) <= 1.96 * sds / np.sqrt(n)).mean())
        ui.metrics([(f"Error típico: {sigma / np.sqrt(n):.5f}", "metric-a"),
                    (f"Intervalos que contienen I: {cover:.3f}", "metric-c")])
        ui.show(fig, key="fig_mc")
        ui.show(g, key="fig_mc_rate")
        ui.footer_bar(f"I = {EXACT:.6f}. Arriba, 2000 estimaciones con {n} puntos cada una frente a la normal del teorema "
                      "central; abajo, el error típico en función de n.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La sobreventa de billetes", "P1_A"),
        ("P2", "(II) El paseo de Pearson", "P2_A"),
        ("P3", "(III) El error de Montecarlo", "P3_A"),
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
