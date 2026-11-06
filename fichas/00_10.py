#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 10: intervalos de confianza.

Qué significa el 95 % (cien intervalos de Neyman), la relación inversa entre
precisión y fiabilidad con un tamaño de muestra fijo, y los intervalos para
una proporción: el de Wald, que falla más de lo que promete, y el de Wilson.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Intervalos de confianza"
PAGE = "00_10"

MU, SIGMA = 50.0, 12.0
INTERVALS = 100


def initial_values():
    return {
        "conf": ui.dchoice(0.95, [0.80, 0.90, 0.95, 0.99], "conf"),
        "n": ui.dchoice(16, [4, 9, 16, 36, 100], "n"),
        "conf2": round(ui.dfloat(0.95, 0.50, 0.995, "conf2", 3) * 200) / 200,
        "n2": ui.dchoice(25, [4, 25, 100, 400], "n2"),
        "n3": ui.dint(30, 10, 150, "n3"),
        "seed": int(ui.r("intervalos") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "draws": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def zq(conf: float) -> float:
    return stats.norm.ppf(1 - (1 - conf) / 2)


def wald(k, n, z):
    p = k / n
    h = z * np.sqrt(p * (1 - p) / n)
    return p - h, p + h


def wilson(k, n, z):
    p = k / n
    centre = (p + z ** 2 / (2 * n)) / (1 + z ** 2 / n)
    h = z / (1 + z ** 2 / n) * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return centre - h, centre + h


def coverage(method, n, z, ps):
    k = np.arange(n + 1)
    lo, hi = method(k, n, z)
    pmf = stats.binom.pmf(k[None, :], n, ps[:, None])
    inside = (lo[None, :] <= ps[:, None]) & (ps[:, None] <= hi[None, :])
    return (pmf * inside).sum(axis=1)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def intervals_chart(dark, lo, hi):
    ys = np.arange(1, len(lo) + 1)
    hit = (lo <= MU) & (MU <= hi)
    p = ui.new_figure(dark, height=420, x_axis_label="intervalo para μ", y_axis_label="muestra",
                      x_range=(MU - 30, MU + 30), y_range=(0, len(lo) + 1))
    p.segment(x0=lo[hit], x1=hi[hit], y0=ys[hit], y1=ys[hit], line_width=2, color=ui.BLUE_LINE, alpha=0.8)
    p.segment(x0=lo[~hit], x1=hi[~hit], y0=ys[~hit], y1=ys[~hit], line_width=3.5, color=ui.UBU_RED)
    p.scatter((lo + hi) / 2, ys, size=3, color=ui.GREY_LINE)
    p.add_layout(Span(location=MU, dimension="height", line_color=ui.GREEN_LINE, line_width=2.5))
    return p


def tradeoff_chart(dark, conf, n):
    cs = np.linspace(0.5, 0.999, 300)
    p = ui.new_figure(dark, height=300, x_axis_label="nivel de confianza (fiabilidad)",
                      y_axis_label="anchura del intervalo (precisión)", y_range=(0, 45))
    for nn, colour in ((4, ui.ORANGE_LINE), (25, ui.BLUE_LINE), (100, ui.GREEN_LINE), (400, ui.PURPLE_LINE)):
        p.line(cs, 2 * zq(cs) * SIGMA / np.sqrt(nn), line_width=3 if nn == n else 1.8, color=colour,
               alpha=1 if nn == n else 0.6, legend_label=f"n = {nn}")
    p.scatter([conf], [2 * zq(conf) * SIGMA / np.sqrt(n)], size=13, color=ui.UBU_RED)
    return ui.style_legend(p, dark, "top_left")


def coverage_chart(dark, n, conf):
    ps = np.linspace(0.005, 0.995, 600)
    z = zq(conf)
    p = ui.new_figure(dark, height=320, x_axis_label="proporción real p", y_axis_label="cobertura real",
                      y_range=(max(0.0, conf - 0.45), 1.0))
    p.line(ps, coverage(wald, n, z, ps), line_width=1.8, color=ui.ORANGE_LINE, legend_label="Wald")
    p.line(ps, coverage(wilson, n, z, ps), line_width=1.8, color=ui.BLUE_LINE, legend_label="Wilson")
    p.add_layout(Span(location=conf, dimension="width", line_color=ui.UBU_RED, line_width=2, line_dash="dashed"))
    return ui.style_legend(p, dark, "bottom_center")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Entre qué valores está el parámetro?</b>")
        ui.content(
            "Un <b>intervalo de confianza</b> de nivel 1 &minus; &alpha; es un par de estadísticos (L, U) que contiene al "
            "parámetro con probabilidad 1 &minus; &alpha;, sea cual sea su valor. Se construye con una cantidad pivotal: "
            "una expresión cuya distribución no depende del parámetro. <i>¿Cuál es el intervalo para la media de una "
            "normal con &sigma; conocida?</i>"
        )
        ui.formula_hidden("x̄ &plusmn; z<sub>&alpha;/2</sub> <sup>&sigma;</sup>&frasl;<sub>&radic;n</sub>")
        ui.content(
            "La probabilidad se refiere al procedimiento, no a un intervalo concreto: antes de tomar la muestra, L y U "
            "son aleatorios; después, el intervalo calculado contiene o no al parámetro. Las tres situaciones muestran "
            "qué significa la confianza, cuánto cuesta y qué pasa cuando la aproximación normal no es buena."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Cien intervalos de Neyman (1937)</b><br>"
            "<i>Calcula cien intervalos con cien muestras y cuenta cuántos fallan.</i><br><br>"
            "<b>II. Precisión contra fiabilidad</b><br>"
            "<i>Comprueba que, con los mismos datos, un intervalo más fiable es siempre menos preciso.</i><br><br>"
            "<b>III. El intervalo de Wilson (1927)</b><br>"
            "<i>Descubre que el intervalo de los libros para una proporción promete un 95 % y a menudo no lo "
            "cumple.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>confianza</u>, el <u>tamaño n</u> y saca <u>otras cien muestras</u>")
        conf = st.select_slider("Nivel de confianza", options=[0.80, 0.90, 0.95, 0.99], value=v["conf"],
                                format_func=lambda c: f"{ui.fmt_pct(c, 0)}", key=ui.wkey(PAGE, "conf"))
        n = st.select_slider("Tamaño de cada muestra", options=[4, 9, 16, 36, 100], value=v["n"], key=ui.wkey(PAGE, "n"))
        if st.button("Otras cien muestras", key="new_intervals", width="stretch"):
            st.session_state["draws"] += 1

        ui.planteamiento()
        ui.statement(
            "<b>Cien intervalos de Neyman (1937)</b><br><br>"
            "Jerzy Neyman dio en 1937 la definición de intervalo de confianza que usamos hoy. Tomamos cien muestras de "
            f"una población normal de media &mu; = {MU:.0f} y desviación &sigma; = {SIGMA:.0f} conocida, y con cada una "
            "calculamos un intervalo para &mu;. En la gráfica, la línea verde es el valor real y los intervalos rojos son "
            "los que no lo contienen."
        )

        if ui.accordion_step("P1_A", "(A) La construcción"):
            ui.content(
                "Parte de que (X̄ &minus; &mu;)/(&sigma;/&radic;n) es una normal estándar. Despeja &mu; de la desigualdad "
                "que se cumple con probabilidad 1 &minus; &alpha;."
            )
            ui.spoiler(
                "&#8473;( &minus;z<sub>&alpha;/2</sub> &le; (X̄ &minus; &mu;)&radic;n/&sigma; &le; z<sub>&alpha;/2</sub> ) = "
                "1 &minus; &alpha;, y despejando &mu;:"
                "<div class='formula-box'>&#8473;( X̄ &minus; z<sub>&alpha;/2</sub>&sigma;/&radic;n &le; &mu; &le; "
                "X̄ + z<sub>&alpha;/2</sub>&sigma;/&radic;n ) = 1 &minus; &alpha;</div>"
                "Lo aleatorio son los extremos, no &mu;."
            )

        if ui.accordion_step("P1_B", "(B) La interpretación"):
            ui.content(
                "Un estudio publica el intervalo [46.1, 57.9] al 95 %. ¿Es correcto decir que &mu; está ahí con "
                "probabilidad 0.95?"
            )
            ui.spoiler(
                "No, en sentido estricto. &mu; es un número fijo y el intervalo calculado lo contiene o no. El 95 % es la "
                "proporción de aciertos del método a la larga: de cada cien intervalos calculados así, unos 95 contienen "
                "a &mu;. La frase «con probabilidad 0.95» solo tiene sentido en el marco bayesiano, donde &mu; tiene "
                "distribución, y entonces se habla de intervalos de credibilidad."
            )

        if ui.accordion_step("P1_C", "(C) Contar los fallos"):
            ui.content("¿Qué distribución tiene el número de intervalos rojos? ¿Es raro ver 9 fallos con el 95 %?")
            ui.spoiler(
                "Las cien muestras son independientes, así que el número de fallos es binomial de parámetros 100 y "
                "&alpha;. Con el 95 %, la media es 5 y la desviación &radic;4.75 &asymp; 2.2; ver 9 o más fallos tiene "
                f"probabilidad {stats.binom.sf(8, 100, 0.05):.3f}. Ocurre de vez en cuando."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + st.session_state["draws"] * 101 + n)
        xbar = rng.normal(MU, SIGMA / np.sqrt(n), INTERVALS)
        h = zq(conf) * SIGMA / np.sqrt(n)
        lo, hi = xbar - h, xbar + h
        misses = int(np.sum((lo > MU) | (hi < MU)))
        ui.metrics([(f"Fallos: {misses} de {INTERVALS}", "result-no" if misses > INTERVALS * (1 - conf) + 2 * np.sqrt(
            INTERVALS * conf * (1 - conf)) else "metric-a"),
                    (f"Esperados: {INTERVALS * (1 - conf):.0f}", "metric-c"), (f"Semiancho: {h:.2f}", "metric-b")])
        ui.show(intervals_chart(dark, lo, hi), key="fig_intervals")
        ui.footer_bar(f"Cien intervalos al {ui.fmt_pct(conf, 0)} con muestras de {n} datos. Todos tienen la misma anchura porque &sigma; es "
                      "conocida; con &sigma; estimada cada uno tendría la suya.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>confianza</u> y el <u>tamaño n</u>")
        conf = st.slider("Nivel de confianza", 0.50, 0.995, v["conf2"], 0.005, key=ui.wkey(PAGE, "conf2"),
                         format="%.3f")
        n = st.select_slider("Tamaño de la muestra", options=[4, 25, 100, 400], value=v["n2"], key=ui.wkey(PAGE, "n2"))

        ui.planteamiento()
        ui.statement(
            "<b>Precisión contra fiabilidad</b><br><br>"
            "Un ayuntamiento quiere estimar el gasto semanal medio de los hogares en tharni, con una desviación conocida de "
            f"&sigma; = {SIGMA:.0f}. Al publicar el intervalo debe elegir el nivel de confianza. Llamamos "
            "<b>fiabilidad</b> al nivel 1 &minus; &alpha; y <b>precisión</b> a lo estrecho que es el intervalo."
        )

        if ui.accordion_step("P2_A", "(A) La anchura"):
            ui.content("Escribe la anchura del intervalo. ¿Cómo cambia al subir la confianza con n fijo?")
            ui.spoiler(
                "<div class='formula-box'>anchura = 2z<sub>&alpha;/2</sub><sup>&sigma;</sup>&frasl;<sub>&radic;n</sub></div>"
                "Al subir la confianza, z<sub>&alpha;/2</sub> crece, y sin límite: un intervalo al 100 % sería toda la "
                "recta real. Con los mismos datos, más fiabilidad significa menos precisión. Es la relación inversa que "
                "muestra cada curva de la gráfica."
            )

        if ui.accordion_step("P2_B", "(B) Cuánto cuesta cada nueve"):
            ui.content("Compara las anchuras al 90 %, 99 % y 99.9 % con el mismo n. ¿Qué crece más deprisa?")
            ui.spoiler(
                "Los cuantiles son 1.645, 2.576 y 3.291: del 90 % al 99 % la anchura crece un 57 %, y del 99 % al 99.9 % "
                "otro 28 %. Las colas de la normal decrecen tan deprisa que cada «nueve» extra cuesta menos anchura que el "
                "anterior, pero nunca es gratis. Por eso el 95 % es un compromiso habitual, no una ley."
            )

        if ui.accordion_step("P2_C", "(C) Las dos cosas a la vez"):
            ui.content("¿Cómo se consigue un intervalo más fiable y, a la vez, igual de estrecho? Salta de una curva a otra.")
            ui.spoiler(
                "Solo con más datos. La anchura baja como 1/&radic;n: con cuatro veces más datos, el intervalo al 99 % de "
                "n = 100 es más estrecho que el del 95 % de n = 25. La relación inversa entre precisión y fiabilidad vale "
                "para un tamaño fijo; el tamaño muestral es lo que permite mejorar las dos."
            )

    with col_right:
        ui.right_panel()
        width = 2 * zq(conf) * SIGMA / np.sqrt(n)
        ui.metrics([(f"Fiabilidad: {ui.fmt_pct(conf, 1)}", "metric-a"), (f"Anchura: {width:.2f} tharni", "metric-b"),
                    (f"z = {zq(conf):.3f}", "metric-c")])
        ui.show(tradeoff_chart(dark, conf, n), key="fig_tradeoff")
        ui.footer_bar("Cada curva es un tamaño de muestra: moverse por ella cambia fiabilidad por precisión. El punto rojo es "
                      "tu elección.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño n</u> de la muestra")
        n = st.slider("Tamaño de la muestra", 10, 200, v["n3"], 1, key=ui.wkey(PAGE, "n3"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El intervalo de Wilson (1927)</b><br><br>"
            "El intervalo más enseñado para una proporción es el de Wald, p̂ &plusmn; z&radic;(p̂(1 &minus; p̂)/n). En 1927 el "
            "matemático Edwin Bidwell Wilson propuso otro, que tardó décadas en llegar a los manuales. Calculamos "
            "exactamente, con la binomial, la probabilidad real de que cada intervalo al 95 % contenga a p."
        )

        if ui.accordion_step("P3_A", "(A) Los fallos de Wald"):
            ui.content("¿Qué intervalo de Wald sale si en la muestra no hay ningún éxito? ¿Qué pasa con la cobertura cerca de p = 0?")
            ui.spoiler(
                "Con p̂ = 0, la desviación estimada es cero y el intervalo es el punto {0}: afirma con un 95 % de confianza "
                "que p = 0 exactamente. Para p pequeño ese caso es frecuente, y la cobertura real cae muy por debajo de lo "
                "prometido. El fallo viene de estimar la varianza con p̂ en lugar de con p."
            )

        if ui.accordion_step("P3_B", "(B) La idea de Wilson"):
            ui.content(
                "En lugar de sustituir p por p̂ en la raíz, busca todos los p que cumplen |p̂ &minus; p| &le; "
                "z&radic;(p(1 &minus; p)/n). ¿Qué intervalo sale?"
            )
            ui.spoiler(
                "Elevando al cuadrado queda una ecuación de segundo grado en p, cuyas raíces son los extremos:"
                "<div class='formula-box'><sup>p̂ + z<sup>2</sup>/(2n)</sup>&frasl;<sub>1 + z<sup>2</sup>/n</sub> &plusmn; "
                "<sup>z</sup>&frasl;<sub>1 + z<sup>2</sup>/n</sub>&radic;( <sup>p̂(1 &minus; p̂)</sup>&frasl;<sub>n</sub> + "
                "<sup>z<sup>2</sup></sup>&frasl;<sub>4n<sup>2</sup></sub> )</div>"
                "Es el conjunto de valores de p que un test de nivel &alpha; no rechazaría: la dualidad entre intervalos y "
                "tests. Su centro se desplaza hacia 1/2, y nunca degenera en un punto."
            )

        if ui.accordion_step("P3_C", "(C) La cobertura oscila"):
            ui.content("¿Por qué las curvas tienen dientes? ¿Mejora Wald al aumentar n?")
            ui.spoiler(
                "Como el número de éxitos es entero, al mover p un poco algún valor posible de p̂ entra o sale del intervalo "
                "y la cobertura salta. Wald mejora con n, pero de forma irregular, y sigue fallando cerca de los extremos "
                "incluso con n grande. Lawrence Brown, Tony Cai y Anirban DasGupta lo documentaron en 2001 y recomendaron "
                "Wilson, o la regla de Agresti-Coull: sumar dos éxitos y dos fracasos antes de aplicar Wald."
            )

    with col_right:
        ui.right_panel()
        ps = np.linspace(0.005, 0.995, 600)
        z = zq(0.95)
        cw, cs = coverage(wald, n, z, ps), coverage(wilson, n, z, ps)
        ui.metrics([(f"Wald, peor cobertura: {cw.min():.3f}", "result-no"), (f"Wilson, peor: {cs.min():.3f}", "metric-a"),
                    (f"Media Wald: {cw.mean():.3f} &middot; Wilson: {cs.mean():.3f}", "metric-c")])
        ui.show(coverage_chart(dark, n, 0.95), key="fig_coverage")
        ui.footer_bar(f"Probabilidad exacta de que el intervalo al 95 % contenga a p, con n = {n}. La línea discontinua es el "
                      "95 % prometido.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Cien intervalos de Neyman", "P1_A"),
        ("P2", "(II) Precisión contra fiabilidad", "P2_A"),
        ("P3", "(III) El intervalo de Wilson", "P3_A"),
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
