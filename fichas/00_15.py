#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 15: modelos de regresión lineal no válidos.

El cuarteto de Anscombe (cuatro conjuntos con los mismos resúmenes y modelos
muy distintos), la extrapolación de una curva de crecimiento y la ley de
Moore, donde la recta solo es válida después de tomar logaritmos.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats
from scipy.interpolate import PchipInterpolator

import civic_ui as ui

TITLE = "Modelos no válidos"
PAGE = "00_15"

ANSCOMBE_X = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ANSCOMBE = {
    "I": (ANSCOMBE_X, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II": (ANSCOMBE_X, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III": (ANSCOMBE_X, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV": ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}
GROWTH_AGES = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 25, 40]
GROWTH_CM = [50, 87, 103, 116, 128, 138, 149, 162, 170, 174, 175, 175]
SCALES = {"linear": "Escala lineal", "log": "Escala logarítmica"}


def initial_values():
    return {
        "set": ui.dchoice("II", list(ANSCOMBE), "set"),
        "age": ui.dint(40, 20, 40, "age"),
        "scale": ui.dchoice("linear", list(SCALES), "scale"),
        "seed": int(ui.r("no_validos") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "set": None, "scale": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b1 = ((x - xm) * (y - ym)).sum() / sxx
    b0 = ym - b1 * xm
    e = y - b0 - b1 * x
    s2 = (e ** 2).sum() / (len(x) - 2)
    h = 1 / len(x) + (x - xm) ** 2 / sxx
    return b0, b1, e, s2, sxx, xm, h


def growth_sample(seed):
    rng = np.random.default_rng(seed)
    curve = PchipInterpolator(GROWTH_AGES, GROWTH_CM)
    ages = np.repeat(np.arange(2, 11), 3).astype(float) + rng.uniform(-0.4, 0.4, 27)
    return ages, curve(ages) + rng.normal(0, 3.5, ages.size), curve


def moore_sample(seed):
    rng = np.random.default_rng(seed)
    years = np.sort(rng.uniform(1971, 2011, 45))
    log2n = np.log2(2300) + (years - 1971) / 2 + rng.normal(0, 0.8, years.size)
    return years, 2 ** log2n


# =============================================================================
# 2. FIGURAS
# =============================================================================

def anscombe_chart(dark, x, y, b0, b1):
    p = ui.new_figure(dark, height=300, x_axis_label="x", y_axis_label="y", x_range=(2, 20), y_range=(2, 14))
    p.scatter(x, y, size=11, color=ui.BLUE_LINE, alpha=0.8)
    xs = np.array([2, 20])
    p.line(xs, b0 + b1 * xs, line_width=3, color=ui.UBU_RED)
    return p


def residuals_chart(dark, fitted, e, x_label="valor ajustado ŷ", height=220):
    p = ui.new_figure(dark, height=height, x_axis_label=x_label, y_axis_label="residuo")
    p.scatter(fitted, e, size=8, color=ui.PURPLE_LINE, alpha=0.8)
    p.add_layout(Span(location=0, dimension="width", line_color=ui.UBU_RED, line_width=2))
    return p


def growth_chart(dark, ages, h, curve, fit, age0):
    b0, b1, _, s2, sxx, xm, _ = fit
    n = len(ages)
    xs = np.linspace(0, 40, 300)
    tq = stats.t.isf(0.025, n - 2)
    half = tq * np.sqrt(s2 * (1 + 1 / n + (xs - xm) ** 2 / sxx))
    p = ui.new_figure(dark, height=330, x_axis_label="edad (años)", y_axis_label="estatura (cm)", y_range=(40, 360))
    p.varea(x=xs, y1=b0 + b1 * xs - half, y2=b0 + b1 * xs + half, fill_color=ui.UBU_RED, fill_alpha=0.15,
            legend_label="intervalo de predicción 95 %")
    p.line(xs, b0 + b1 * xs, line_width=3, color=ui.UBU_RED, legend_label="recta ajustada")
    p.line(xs, curve(xs), line_width=3, color=ui.GREEN_LINE, line_dash="dashed", legend_label="crecimiento real")
    p.scatter(ages, h, size=7, color=ui.BLUE_LINE, alpha=0.8, legend_label="datos de 2 a 10 años")
    p.add_layout(Span(location=age0, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    return ui.style_legend(p, dark, "top_left")


def moore_chart(dark, years, n, scale, fit):
    b0, b1 = fit[0], fit[1]
    log = scale == "log"
    p = ui.new_figure(dark, height=300, x_axis_label="año", y_axis_label="log₂ transistores" if log else "transistores")
    yv = np.log2(n) if log else n
    p.scatter(years, yv, size=8, color=ui.BLUE_LINE, alpha=0.75)
    xs = np.array([1970, 2012])
    p.line(xs, b0 + b1 * xs, line_width=3, color=ui.UBU_RED)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuándo no vale una recta?</b>")
        ui.content(
            "Un modelo de regresión lineal es válido cuando sus hipótesis se cumplen razonablemente: la relación es "
            "lineal en el rango de interés, los errores son independientes, de varianza constante y aproximadamente "
            "normales, y ningún punto aislado decide el resultado. La recta de mínimos cuadrados se puede calcular "
            "siempre, se cumplan o no. <i>¿Qué datos hacen falta para calcularla?</i>"
        )
        ui.formula_hidden("solo x̄, ȳ, S<sub>xx</sub> y S<sub>xy</sub>: &nbsp; b<sub>1</sub> = S<sub>xy</sub>/S<sub>xx</sub>, "
                          "b<sub>0</sub> = ȳ &minus; b<sub>1</sub>x̄")
        ui.content(
            "Como la recta solo depende de unos pocos resúmenes, conjuntos de datos muy diferentes dan exactamente la misma "
            "recta. Las tres situaciones muestran tres maneras de que un modelo lineal no sirva: por la forma de los "
            "datos, por usarlo fuera de su rango y por aplicarlo a la escala equivocada."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El cuarteto de Anscombe (1973)</b><br>"
            "<i>Cuatro conjuntos de datos con la misma media, varianza, correlación y recta. Descubre cuál merece esa "
            "recta.</i><br><br>"
            "<b>II. Un gigante de tres metros</b><br>"
            "<i>Ajusta la estatura de un niño entre los 2 y los 10 años y predice la que tendrá de adulto.</i><br><br>"
            "<b>III. La ley de Moore (1965)</b><br>"
            "<i>Ajusta una recta al número de transistores de los procesadores, y descubre en qué escala hay que "
            "hacerlo.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>conjunto de datos</u>")
        if st.session_state["set"] is None:
            st.session_state["set"] = v["set"]
        ui.choice_buttons(list(ANSCOMBE), "set", per_row=4)

        ui.planteamiento()
        ui.statement(
            "<b>El cuarteto de Anscombe (1973)</b><br><br>"
            "Francis Anscombe publicó cuatro conjuntos de once puntos para defender una idea que entonces no era obvia: "
            "los gráficos son parte esencial del análisis, no un adorno. Los cuatro tienen, con dos decimales, la misma "
            "media y varianza de x y de y, la misma correlación y la misma recta de regresión."
        )

        if ui.accordion_step("P1_A", "(A) Los mismos números"):
            ui.content("Recorre los cuatro conjuntos y compara las métricas. ¿Hay algún número que los distinga?")
            ui.spoiler(
                "Ninguno de los habituales: x̄ = 9, ȳ &asymp; 7.50, S<sub>x</sub><sup>2</sup> = 11, S<sub>y</sub><sup>2</sup> "
                "&asymp; 4.12, r &asymp; 0.816 y la recta ŷ = 3 + 0.5x en los cuatro. También coinciden R<sup>2</sup>, los "
                "errores típicos y el test de la pendiente. Un informe que solo diera la tabla de regresión no permitiría "
                "distinguirlos."
            )

        if ui.accordion_step("P1_B", "(B) El diagnóstico de cada uno"):
            ui.content("Mira los datos y los residuos. ¿Qué modelo sería adecuado en cada conjunto?")
            ui.spoiler(
                "I: la recta es razonable y los residuos no tienen estructura. II: la relación es una curva perfecta; hace "
                "falta un término cuadrático. III: es una recta casi exacta salvo un punto atípico en y, que inclina el "
                "ajuste. IV: todos los puntos tienen x = 8 menos uno, y ese punto solo determina la pendiente: sin él, la "
                "pendiente ni siquiera se podría calcular."
            )

        if ui.accordion_step("P1_C", "(C) La lección"):
            ui.content("¿Qué hay que hacer antes de creerse una recta?")
            ui.spoiler(
                "Dibujar los datos y los residuos. Alberto Cairo dibujó un dinosaurio con puntos, el «Datasaurus», y en 2017 "
                "Justin Matejka y George Fitzmaurice generaron otros doce conjuntos con sus mismos resúmenes estadísticos y "
                "formas completamente distintas. Los resúmenes comprimen la información, y lo que tiran puede ser justo lo importante."
            )

    with col_right:
        ui.right_panel()
        key = st.session_state["set"]
        x, y = (np.array(a, float) for a in ANSCOMBE[key])
        b0, b1, e, s2, sxx, xm, h = ols(x, y)
        r = np.corrcoef(x, y)[0, 1]
        ui.metrics([(f"x̄ = {x.mean():.2f}, ȳ = {y.mean():.2f}", "metric-c"),
                    (f"S<sub>x</sub><sup>2</sup> = {x.var(ddof=1):.2f}, S<sub>y</sub><sup>2</sup> = {y.var(ddof=1):.2f}", "metric-c"),
                    (f"r = {r:.3f}, ŷ = {b0:.2f} + {b1:.3f}x", "metric-a")])
        ui.show(anscombe_chart(dark, x, y, b0, b1), key="fig_anscombe")
        ui.show(residuals_chart(dark, b0 + b1 * x, e), key="fig_anscombe_resid")
        ui.footer_bar(f"Conjunto {key} del cuarteto. Arriba, los once puntos y la recta; abajo, los residuos frente a los "
                      f"valores ajustados. El mayor apalancamiento es h = {h.max():.2f}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()
    ages, heights, curve = growth_sample(v["seed"])
    fit = ols(ages, heights)
    b0, b1, _, s2, sxx, xm, _ = fit

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>edad</u> para la que predecir")
        age0 = st.slider("Edad (años)", 2, 40, v["age"], 1, key=ui.wkey(PAGE, "age"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Un gigante de tres metros</b><br><br>"
            "En una revisión pediátrica se mide la estatura de 27 niños de entre 2 y 10 años. En ese rango el crecimiento "
            "es casi lineal, de unos seis centímetros por año, y la recta ajusta muy bien. La curva verde es una curva de "
            "crecimiento aproximada, la verdad que el modelo no conoce."
        )

        if ui.accordion_step("P2_A", "(A) El intervalo de predicción"):
            ui.content("Para predecir la estatura de un niño concreto con edad x<sub>0</sub>, ¿qué intervalo se usa? ¿Por qué se ensancha lejos de x̄?")
            ui.spoiler(
                "<div class='formula-box'>ŷ<sub>0</sub> &plusmn; t<sub>n &minus; 2, 0.025</sub> s "
                "&radic;( 1 + <sup>1</sup>&frasl;<sub>n</sub> + <sup>(x<sub>0</sub> &minus; x̄)<sup>2</sup></sup>&frasl;<sub>S<sub>xx</sub></sub> )</div>"
                "El 1 recoge la variabilidad del niño, y los otros dos términos la incertidumbre de la recta. Lejos de x̄, "
                "un error pequeño en la pendiente se multiplica por la distancia, y el intervalo crece."
            )

        if ui.accordion_step("P2_B", "(B) Extrapolar"):
            ui.content("Lleva la edad a 30 años. ¿Qué predice el modelo? ¿Contiene el intervalo la estatura real?")
            ui.spoiler(
                "La recta predice un adulto de más de dos metros y medio, y el intervalo de predicción, aunque más ancho, no se acerca "
                "a la estatura real. El intervalo solo mide la incertidumbre <b>dentro</b> del modelo; si la relación deja de "
                "ser lineal fuera del rango observado, ninguna fórmula lo avisa. Extrapolar es suponer que el modelo sigue "
                "siendo válido donde no hay datos que lo comprueben."
            )

        if ui.accordion_step("P2_C", "(C) Extrapolaciones famosas"):
            ui.content("¿Se te ocurren predicciones que fallarían por la misma razón?")
            ui.spoiler(
                "En 2004 un artículo en Nature ajustó rectas a los tiempos olímpicos de los 100 metros y predijo que las "
                "mujeres correrían más deprisa que los hombres en los Juegos de 2156. Las mismas rectas predicen que, mucho "
                "después, la carrera se correría en tiempo negativo. Toda recta sale del rango de valores posibles si se "
                "prolonga lo suficiente."
            )

    with col_right:
        ui.right_panel()
        n = len(ages)
        pred = b0 + b1 * age0
        half = stats.t.isf(0.025, n - 2) * np.sqrt(s2 * (1 + 1 / n + (age0 - xm) ** 2 / sxx))
        real = float(curve(age0))
        inside = pred - half <= real <= pred + half
        ui.metrics([(f"Predicción: {pred:.0f} &plusmn; {half:.0f} cm", "metric-a"),
                    (f"Estatura real: {real:.0f} cm", "metric-c")])
        ui.check(inside, "La estatura real está dentro del intervalo" if inside else "La estatura real queda fuera del intervalo")
        ui.show(growth_chart(dark, ages, heights, curve, fit, age0), key="fig_growth")
        ui.footer_bar(f"Recta ajustada con niños de 2 a 10 años: {b0:.1f} + {b1:.2f}&middot;edad. La banda roja es el intervalo "
                      "de predicción al 95 %; la línea verde, el crecimiento real.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()
    years, n = moore_sample(v["seed"])

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>escala</u> en la que ajustar la recta")
        if st.session_state["scale"] is None:
            st.session_state["scale"] = v["scale"]
        ui.choice_buttons(list(SCALES), "scale", labels=SCALES, per_row=2)

        ui.planteamiento()
        ui.statement(
            "<b>La ley de Moore (1965)</b><br><br>"
            "Gordon Moore, que después cofundaría Intel, observó que el número de componentes de un circuito integrado se "
            "duplicaba a un ritmo regular; en 1975 fijó el periodo en unos dos años. El primer microprocesador comercial, "
            "de 1971, tenía 2300 transistores. Simulamos 45 procesadores hasta 2011 que siguen esa ley con algo de ruido, y "
            "ajustamos una recta."
        )

        if ui.accordion_step("P3_A", "(A) En escala lineal"):
            ui.content("Con la escala lineal, ¿qué dicen los residuos? ¿Qué hipótesis fallan?")
            ui.spoiler(
                "Los residuos forman una curva, porque el crecimiento es exponencial, y además su dispersión crece "
                "enormemente con el año. Fallan la linealidad y la homocedasticidad a la vez, y la recta predice números "
                "negativos de transistores para los primeros años. El R<sup>2</sup> puede ser aceptable y el modelo, inútil."
            )

        if ui.accordion_step("P3_B", "(B) En escala logarítmica"):
            ui.content("Toma logaritmos en base 2. ¿Qué modelo lineal resulta? ¿Qué significa la pendiente?")
            ui.spoiler(
                "Si N = N<sub>0</sub>&middot;2<sup>(t &minus; t<sub>0</sub>)/T</sup>, entonces log<sub>2</sub> N = "
                "log<sub>2</sub> N<sub>0</sub> + (t &minus; t<sub>0</sub>)/T: una recta en t. La pendiente es 1/T, la "
                "inversa del tiempo de duplicación, y los residuos tienen ahora varianza constante, porque el ruido era "
                "multiplicativo. El modelo es lineal en los parámetros después de transformar, y eso es lo que pide la "
                "regresión lineal."
            )

        if ui.accordion_step("P3_C", "(C) Volver a la escala original"):
            ui.content("Si ajustas en logaritmos, ¿qué estimas al deshacer la transformación: la media de N o otra cosa?")
            ui.spoiler(
                "Deshacer el logaritmo da la <b>mediana</b> de N para cada año, no la media: por la desigualdad de Jensen, "
                "E[N] es mayor que 2<sup>E[log<sub>2</sub> N]</sup>. Para errores normales en el logaritmo hay una "
                "corrección explícita. George Box y David Cox (1964) propusieron una familia de transformaciones de la "
                "respuesta, que incluye el logaritmo, para elegir la escala en la que el modelo lineal es válido."
            )

    with col_right:
        ui.right_panel()
        scale = st.session_state["scale"]
        yv = np.log2(n) if scale == "log" else n
        fit = ols(years, yv)
        b0, b1, e = fit[0], fit[1], fit[2]
        r2 = 1 - (e ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
        if scale == "log":
            ui.metrics([(f"R<sup>2</sup> = {r2:.3f}", "metric-a"), (f"Duplicación cada {1 / b1:.2f} años", "metric-b")])
        else:
            ui.metrics([(f"R<sup>2</sup> = {r2:.3f}", "metric-a"),
                        (f"Predicción para 1971: {ui.fmt_sci(b0 + b1 * 1971, 2)} transistores", "result-no")])
        ui.show(moore_chart(dark, years, n, scale, fit), key="fig_moore")
        ui.show(residuals_chart(dark, years, e, x_label="año"), key="fig_moore_resid")
        ui.footer_bar(f"{SCALES[scale]}. Arriba, los procesadores simulados y la recta; abajo, los residuos frente al año.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El cuarteto de Anscombe", "P1_A"),
        ("P2", "(II) Un gigante de tres metros", "P2_A"),
        ("P3", "(III) La ley de Moore", "P3_A"),
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
