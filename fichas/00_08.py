#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 8: el test de hipótesis.

El primer p-valor publicado (los bautizos de Londres de Arbuthnot), el nivel
de significación en una prueba discreta (la dama que probaba el té) y la
potencia de un test con las dos hipótesis de Neyman y Pearson.
"""

from __future__ import annotations

from math import comb

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Test de hipótesis"
PAGE = "00_08"

YEARS = 82
MU0, SIGMA = 100.0, 15.0


def initial_values():
    return {
        "k": ui.dint(82, 41, 82, "k"),
        "alpha": ui.dchoice(0.05, [0.01, 0.05, 0.10], "alpha"),
        "cups": ui.dchoice(8, [6, 8, 10, 12], "cups"),
        "right": ui.dint(4, 0, 4, "right"),
        "delta": round(ui.dfloat(5.0, 2.0, 8.0, "delta", 1)),
        "n": ui.dint(25, 4, 100, "n"),
        "alpha_np": ui.dchoice(0.05, [0.01, 0.05, 0.10], "alpha_np"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def tea_pmf(cups: int):
    """Aciertos de la dama entre las tazas con la leche primero, si adivina al azar."""
    h = cups // 2
    return np.array([comb(h, k) * comb(h, h - k) / comb(cups, h) for k in range(h + 1)])


def power(delta, n, alpha):
    z = stats.norm.isf(alpha)
    return stats.norm.sf(z - delta * np.sqrt(n) / SIGMA)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def binomial_chart(dark, k):
    xs = np.arange(20, YEARS + 1)
    pmf = stats.binom.pmf(xs, YEARS, 0.5)
    colours = [ui.UBU_RED if x >= k else ui.BLUE_LINE for x in xs]
    p = ui.new_figure(dark, height=280, x_axis_label="años con más niños que niñas (de 82)", y_axis_label="probabilidad")
    p.vbar(x=xs, top=pmf, width=0.8, color=colours, alpha=0.75)
    p.add_layout(Span(location=k - 0.5, dimension="height", line_color=ui.UBU_RED, line_dash="dashed"))
    return p


def tea_chart(dark, pmf, right):
    xs = [str(k) for k in range(len(pmf))]
    colours = [ui.UBU_RED if k >= right else ui.BLUE_LINE for k in range(len(pmf))]
    p = ui.new_figure(dark, height=270, x_range=xs, x_axis_label="tazas con la leche primero acertadas",
                      y_axis_label="probabilidad si adivina")
    p.vbar(x=xs, top=pmf, width=0.7, color=colours, alpha=0.75)
    return p


def power_chart(dark, delta, n, alpha):
    se = SIGMA / np.sqrt(n)
    crit = MU0 + stats.norm.isf(alpha) * se
    lo, hi = MU0 - 4 * se, MU0 + delta + 4 * se
    xs = np.linspace(lo, hi, 500)
    f0 = stats.norm.pdf(xs, MU0, se)
    f1 = stats.norm.pdf(xs, MU0 + delta, se)
    p = ui.new_figure(dark, height=300, x_axis_label="media muestral X̄", y_axis_label="densidad")
    right = xs >= crit
    p.varea(x=xs[right], y1=0, y2=f0[right], fill_color=ui.UBU_RED, fill_alpha=0.5, legend_label="α: rechazar H₀ siendo cierta")
    p.varea(x=xs[~right], y1=0, y2=f1[~right], fill_color=ui.ORANGE_LINE, fill_alpha=0.45, legend_label="β: no rechazar H₀ siendo falsa")
    p.line(xs, f0, line_width=3, color=ui.BLUE_LINE, legend_label="bajo H₀")
    p.line(xs, f1, line_width=3, color=ui.GREEN_LINE, legend_label="bajo H₁")
    p.add_layout(Span(location=crit, dimension="height", line_color=ui.GREY_LINE, line_width=2, line_dash="dashed"))
    return ui.style_legend(p, dark, "top_left")


def power_curve_chart(dark, delta, n, alpha):
    ds = np.linspace(0, 12, 200)
    p = ui.new_figure(dark, height=240, x_axis_label="mejora real δ (puntos)", y_axis_label="potencia 1 − β",
                      y_range=(0, 1.02))
    for nn, colour in ((n // 4 if n >= 8 else 2, ui.GREY_LINE), (n, ui.BLUE_LINE), (4 * n, ui.GREEN_LINE)):
        p.line(ds, power(ds, nn, alpha), line_width=3, color=colour, legend_label=f"n = {nn}")
    p.add_layout(Span(location=delta, dimension="height", line_color=ui.UBU_RED, line_dash="dashed"))
    p.add_layout(Span(location=alpha, dimension="width", line_color=ui.GREY_LINE, line_dash="dotted"))
    return ui.style_legend(p, dark, "bottom_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Pueden los datos contradecir una hipótesis?</b>")
        ui.content(
            "Un <b>test de hipótesis</b> enfrenta una hipótesis nula H<sub>0</sub>, la que se mantiene salvo prueba en "
            "contra, con una alternativa H<sub>1</sub>. Se elige un estadístico T cuya distribución bajo H<sub>0</sub> se "
            "conoce, y se mide cuán extremo es el valor observado t con el <b>p-valor</b>. <i>¿Cómo se define?</i>"
        )
        ui.formula_hidden("p = &#8473;<sub>H<sub>0</sub></sub>( T &ge; t ), &nbsp; la probabilidad de un resultado al menos "
                          "tan extremo como el observado si H<sub>0</sub> es cierta")
        ui.content(
            "Si el p-valor es menor que un umbral &alpha; fijado de antemano, el <b>nivel de significación</b>, se rechaza "
            "H<sub>0</sub>. Al decidir se pueden cometer dos errores, y la <b>potencia</b> 1 &minus; &beta; mide la "
            "capacidad del test para detectar que H<sub>0</sub> es falsa."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los bautizos de Londres (1710)</b><br>"
            "<i>Calcula con John Arbuthnot el primer p-valor de la historia y decide si nacen más niños por "
            "azar.</i><br><br>"
            "<b>II. La dama que probaba el té (1935)</b><br>"
            "<i>Diseña con Fisher una prueba para saber si alguien distingue el orden de la leche y del té, y descubre "
            "que &alpha; = 0.05 no siempre es posible.</i><br><br>"
            "<b>III. Neyman y Pearson (1933)</b><br>"
            "<i>Añade la hipótesis alternativa y calcula la potencia: cuántos alumnos hacen falta para detectar una "
            "mejora.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>años con más niños</u> y el <u>nivel &alpha;</u>")
        k = st.slider("Años con más niños que niñas", 41, YEARS, v["k"], 1, key=ui.wkey(PAGE, "k"))
        alpha = st.select_slider("Nivel de significación α", options=[0.01, 0.05, 0.10], value=v["alpha"],
                                 key=ui.wkey(PAGE, "alpha"))

        ui.planteamiento()
        ui.statement(
            "<b>Los bautizos de Londres (1710)</b><br><br>"
            "John Arbuthnot, médico de la reina Ana, revisó los registros de bautizos de Londres de 1629 a 1710: en los "
            "82 años habían nacido más niños que niñas. Si cada año el sexo mayoritario se decidiera a cara o cruz, "
            "¿qué probabilidad tendría un resultado así? Con el deslizador puedes probar qué habría concluido con "
            "menos años favorables."
        )

        if ui.accordion_step("P1_A", "(A) La hipótesis y el estadístico"):
            ui.content("Formula H<sub>0</sub>. ¿Qué distribución tiene el número de años con más niños si H<sub>0</sub> es cierta?")
            ui.spoiler(
                "H<sub>0</sub>: cada año es igual de probable que haya más niños o más niñas, de forma independiente. El "
                "número X de años con más niños es entonces binomial de parámetros 82 y 1/2, y el p-valor de k años es "
                "&#8473;(X &ge; k), las barras rojas. Para k = 82:"
                f"<div class='formula-box'>p = (1/2)<sup>82</sup> &asymp; {ui.fmt_sci(0.5 ** 82, 1)}</div>"
                "Es lo que hoy se llama un test de signos."
            )

        if ui.accordion_step("P1_B", "(B) Lo que no es un p-valor"):
            ui.content("Arbuthnot concluyó que el reparto de sexos no era cosa del azar. ¿Es el p-valor la probabilidad de que H<sub>0</sub> sea cierta?")
            ui.spoiler(
                "No. El p-valor es una probabilidad calculada <b>suponiendo</b> H<sub>0</sub> cierta, &#8473;(datos tan "
                "extremos | H<sub>0</sub>), no &#8473;(H<sub>0</sub> | datos). Para la segunda haría falta el teorema de "
                "Bayes y una probabilidad a priori. Arbuthnot añadió una conclusión teológica que los datos no "
                "justifican: rechazar el azar no prueba ninguna explicación concreta."
            )

        if ui.accordion_step("P1_C", "(C) Una cola o dos"):
            ui.content(
                "Antes de ver los datos, ¿por qué contar solo los años con más niños, y no también los resultados extremos "
                "a favor de las niñas?"
            )
            ui.spoiler(
                "Depende de la alternativa. Si H<sub>1</sub> es «nacen más niños», el test es unilateral y el p-valor suma "
                "solo la cola derecha. Si H<sub>1</sub> es «no nacen igual», es bilateral y hay que sumar las dos colas: "
                "aquí, por simetría, el doble. La alternativa se elige antes de mirar los datos; elegirla después para "
                "conseguir un p-valor menor es hacer trampa."
            )

    with col_right:
        ui.right_panel()
        pval = stats.binom.sf(k - 1, YEARS, 0.5)
        reject = pval < alpha
        ui.metrics([(f"p-valor unilateral: {ui.fmt_sci(pval, 2)}", "metric-a"), (f"Bilateral: {ui.fmt_sci(min(1, 2 * pval), 2)}", "metric-b")])
        ui.check(reject, f"Se rechaza H<sub>0</sub> al nivel {alpha}" if reject else f"No se rechaza H<sub>0</sub> al nivel {alpha}")
        ui.show(binomial_chart(dark, k), key="fig_arbuthnot")
        crit = int(stats.binom.isf(alpha, YEARS, 0.5)) + 1
        ui.footer_bar(f"Distribución del número de años con más niños bajo H<sub>0</sub>. En rojo, los resultados al menos tan "
                      f"extremos como {k}. Al nivel {alpha} bastarían {crit} años de 82.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de tazas</u> y los <u>aciertos</u>")
        cups = st.select_slider("Tazas en la prueba", options=[6, 8, 10, 12], value=v["cups"], key=ui.wkey(PAGE, "cups"))
        half = cups // 2
        right = st.slider("Aciertos entre las tazas con la leche primero", 0, half, min(v["right"], half), 1,
                          key=ui.wkey(PAGE, f"right_{cups}"))

        ui.planteamiento()
        ui.statement(
            "<b>La dama que probaba el té (1935)</b><br><br>"
            "En Rothamsted, la bióloga Muriel Bristol aseguraba que notaba si en su taza se había echado primero la leche o "
            "el té. Fisher diseñó la prueba en su libro «El diseño de experimentos»: ocho tazas, cuatro de cada clase, "
            "servidas en orden aleatorio, y ella debe señalar las cuatro con la leche primero. Si no distingue nada, "
            "elige cuatro tazas al azar."
        )

        if ui.accordion_step("P2_A", "(A) La distribución de los aciertos"):
            ui.content("¿Qué distribución tiene el número de aciertos si H<sub>0</sub> es cierta? ¿Cuál es el p-valor de acertar las cuatro?")
            ui.spoiler(
                "Elegir 4 de 8 tazas al azar da una hipergeométrica: &#8473;(k aciertos) = C(4, k)C(4, 4 &minus; k)/C(8, 4). "
                "Acertar las cuatro solo ocurre en uno de los C(8, 4) = 70 repartos posibles:"
                "<div class='formula-box'>p = 1/70 &asymp; 0.014</div>"
                "Es el <b>test exacto de Fisher</b>. Según se cuenta, ella acertó las ocho tazas."
            )

        if ui.accordion_step("P2_B", "(B) El nivel de significación"):
            ui.content(
                "La región de rechazo se fija antes del experimento. Con ocho tazas, ¿qué regiones son posibles y qué "
                "probabilidad de error tiene cada una? ¿Se puede conseguir &alpha; = 0.05 exactamente?"
            )
            ui.spoiler(
                "Rechazar solo con 4 aciertos da &alpha; = 1/70 &asymp; 0.014. Rechazar con 3 o 4 da "
                "17/70 &asymp; 0.243, demasiado. Entre esos dos no hay nada: con un estadístico discreto, el nivel exacto "
                "solo toma ciertos valores. &alpha; es la probabilidad de rechazar H<sub>0</sub> cuando es cierta: el "
                "<b>error de tipo I</b>, que se fija al diseñar la prueba."
            )

        if ui.accordion_step("P2_C", "(C) Diseñar una prueba mejor"):
            ui.content("Aumenta el número de tazas. ¿Cuántas hacen falta para que fallar una taza siga siendo significativo al 5 %?")
            ui.spoiler(
                "Con 10 tazas, acertar 4 de 5 tiene p-valor 26/252 &asymp; 0.103, que no basta. Con 12 tazas, acertar 5 de "
                "6 tiene p-valor 37/924 &asymp; 0.040, por debajo de 0.05. Más tazas permiten tolerar un error sin perder "
                "la significación: el diseño del experimento decide de antemano qué puede llegar a demostrar."
            )

    with col_right:
        ui.right_panel()
        pmf = tea_pmf(cups)
        pval = pmf[right:].sum()
        ui.metrics([(f"Repartos posibles: C({cups}, {half}) = {comb(cups, half)}", "metric-c"),
                    (f"p-valor: {pval:.4f}", "metric-a")])
        ui.check(pval < 0.05, "Significativo al 5 %" if pval < 0.05 else "No significativo al 5 %")
        ui.show(tea_chart(dark, pmf, right), key="fig_tea")
        levels = ", ".join(f"{pmf[j:].sum():.3f}" for j in range(half, 0, -1))
        ui.footer_bar(f"Distribución de los aciertos si la dama adivina. Niveles exactos posibles, rechazando a partir de "
                      f"{half}, {half - 1}, &hellip; aciertos: {levels}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>mejora real</u>, el <u>número de alumnos</u> y el <u>nivel &alpha;</u>")
        delta = st.slider("Mejora real δ (puntos)", 0, 12, int(v["delta"]), 1, key=ui.wkey(PAGE, "delta"))
        n = st.slider("Alumnos n", 4, 200, v["n"], 1, key=ui.wkey(PAGE, "n"))
        alpha = st.select_slider("Nivel α", options=[0.01, 0.05, 0.10], value=v["alpha_np"], key=ui.wkey(PAGE, "alpha_np"))

        ui.planteamiento()
        ui.statement(
            "<b>Neyman y Pearson (1933)</b><br><br>"
            "Jerzy Neyman y Egon Pearson completaron la idea de Fisher: un test debe compararse con una hipótesis "
            "alternativa concreta. Un colegio prueba un método de lectura. Con el método antiguo, las puntuaciones son "
            f"normales de media {MU0:.0f} y desviación {SIGMA:.0f}. Contrastamos H<sub>0</sub>: &mu; = {MU0:.0f} frente a "
            "H<sub>1</sub>: &mu; &gt; 100 con la media de n alumnos, y suponemos que la mejora real es &delta;."
        )

        if ui.accordion_step("P3_A", "(A) Dos errores"):
            ui.content("Identifica en la gráfica las dos áreas sombreadas. ¿Qué error representa cada una?")
            ui.spoiler(
                "La roja es &alpha;, la probabilidad de rechazar H<sub>0</sub> siendo cierta: el <b>error de tipo I</b>, "
                "adoptar un método que no mejora nada. La naranja es &beta;, la probabilidad de no rechazar H<sub>0</sub> "
                "cuando la mejora es &delta;: el <b>error de tipo II</b>, dejar pasar un método que sí funciona. La "
                "<b>potencia</b> es 1 &minus; &beta;."
            )

        if ui.accordion_step("P3_B", "(B) La fórmula de la potencia"):
            ui.content("Se rechaza si X̄ supera &mu;<sub>0</sub> + z<sub>&alpha;</sub>&sigma;/&radic;n. Calcula la probabilidad de rechazar cuando &mu; = &mu;<sub>0</sub> + &delta;.")
            ui.spoiler(
                "Tipificando con la media verdadera:"
                "<div class='formula-box'>1 &minus; &beta; = 1 &minus; &Phi;( z<sub>&alpha;</sub> &minus; "
                "<sup>&delta;&radic;n</sup>&frasl;<sub>&sigma;</sub> )</div>"
                "La potencia crece con la mejora &delta;, con n y con &alpha;, y decrece con &sigma;. Con &delta; = 0 vale "
                "exactamente &alpha;."
            )

        if ui.accordion_step("P3_C", "(C) El equilibrio"):
            ui.content(
                "Con n fijo, baja &alpha; de 0.10 a 0.01. ¿Qué le pasa a &beta;? ¿Qué test elige el lema de Neyman-Pearson?"
            )
            ui.spoiler(
                "Al bajar &alpha;, la línea crítica se desplaza a la derecha y &beta; aumenta: con n fijo no se pueden "
                "reducir los dos errores a la vez. La única forma de bajar ambos es aumentar n. El lema de Neyman-Pearson "
                "dice que, para un &alpha; dado, el test más potente rechaza cuando el cociente de verosimilitudes "
                "f<sub>1</sub>/f<sub>0</sub> es grande, que aquí equivale a rechazar cuando X̄ es grande."
            )

    with col_right:
        ui.right_panel()
        pw = power(delta, n, alpha)
        crit = MU0 + stats.norm.isf(alpha) * SIGMA / np.sqrt(n)
        ui.metrics([(f"Valor crítico: {crit:.2f}", "metric-c"), (f"&beta; = {1 - pw:.3f}", "metric-b"),
                    (f"Potencia: {pw:.3f}", "result-yes" if pw >= 0.8 else "metric-a")])
        ui.show(power_chart(dark, max(delta, 0.5), n, alpha), key="fig_power")
        ui.show(power_curve_chart(dark, delta, n, alpha), key="fig_power_curve")
        ui.footer_bar("Arriba, la distribución de X̄ bajo cada hipótesis; la línea discontinua es el valor crítico. Abajo, la "
                      "potencia frente a la mejora real para tres tamaños de muestra.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los bautizos de Londres", "P1_A"),
        ("P2", "(II) La dama que probaba el té", "P2_A"),
        ("P3", "(III) Neyman y Pearson", "P3_A"),
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
