#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 14: correlaciones espurias.

Las correlaciones sin sentido entre series temporales de Yule (dos paseos
aleatorios independientes), la causa común de las cigüeñas y los nacimientos
(correlación parcial) y la correlación espuria de los cocientes de Pearson.
"""

from __future__ import annotations

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "Correlaciones espurias"
PAGE = "00_14"

PAIRS = 2000
COUNTRIES = 17
CV_XY = 0.10


def initial_values():
    return {
        "T": ui.dchoice(50, [10, 25, 50, 100, 250, 500], "T"),
        "a": round(ui.dfloat(1.5, 0.0, 3.0, "a", 1) * 10) / 10,
        "cvz": round(ui.dfloat(0.25, 0.0, 0.5, "cvz", 2) * 100) / 100,
        "seed": int(ui.r("espurias") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "walks": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def corr_rows(x, y):
    xc = x - x.mean(axis=1, keepdims=True)
    yc = y - y.mean(axis=1, keepdims=True)
    return (xc * yc).sum(axis=1) / np.sqrt((xc ** 2).sum(axis=1) * (yc ** 2).sum(axis=1))


def partial(rxy, rxz, ryz):
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def pearson_ratio(cvz):
    return cvz ** 2 / (CV_XY ** 2 + cvz ** 2)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def series_chart(dark, a, b):
    t = np.arange(len(a))
    p = ui.new_figure(dark, height=230, x_axis_label="año", y_axis_label="valor")
    p.line(t, a, line_width=2.5, color=ui.BLUE_LINE, legend_label="serie 1")
    p.line(t, b, line_width=2.5, color=ui.ORANGE_LINE, legend_label="serie 2")
    return ui.style_legend(p, dark, "top_left")


def r_hist_chart(dark, r_walk, r_iid, r_diff):
    edges = np.linspace(-1, 1, 51)
    centres = (edges[:-1] + edges[1:]) / 2
    p = ui.new_figure(dark, height=260, x_axis_label="correlación r entre dos series independientes",
                      y_axis_label="densidad", x_range=(-1, 1))
    for vals, label, colour in ((r_walk, "paseos aleatorios", ui.UBU_RED), (r_iid, "ruido independiente", ui.BLUE_LINE),
                                (r_diff, "paseos diferenciados", ui.GREEN_LINE)):
        h, _ = np.histogram(vals, bins=edges)
        p.line(centres, h / (len(vals) * (edges[1] - edges[0])), line_width=3, color=colour, legend_label=label)
    return ui.style_legend(p, dark, "top_left")


def storks_chart(dark, x, y, z):
    p = ui.new_figure(dark, height=300, x_axis_label="parejas de cigüeñas (tipificado)",
                      y_axis_label="nacimientos al año (tipificado)")
    shade = (z - z.min()) / (z.max() - z.min() + 1e-12)
    colours = [f"rgb({int(60 + 180 * s)}, {int(110 - 40 * s)}, {int(200 - 160 * s)})" for s in shade]
    p.scatter(x, y, size=13, color=colours, alpha=0.85, line_color="#ffffff" if dark else "#333333", line_width=0.5)
    return p


def ratio_chart(dark, rx, ry):
    p = ui.new_figure(dark, height=300, x_axis_label="X/Z", y_axis_label="Y/Z")
    p.scatter(rx, ry, size=5, color=ui.PURPLE_LINE, alpha=0.45)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuándo engaña una correlación?</b>")
        ui.content(
            "Una correlación es <b>espuria</b> cuando no refleja ninguna relación directa entre las dos variables, sino algo "
            "externo a ellas: una tendencia común en el tiempo, una tercera variable que influye en las dos, o la forma en "
            "que se han construido los datos. El coeficiente de Pearson se calcula igual en todos los casos; lo que "
            "cambia es lo que significa. <i>¿Qué supone el test de correlación sobre las observaciones?</i>"
        )
        ui.formula_hidden("pares (X<sub>i</sub>, Y<sub>i</sub>) independientes y con la misma distribución, i = 1, &hellip;, n")
        ui.content(
            "Las tres situaciones son tres mecanismos clásicos, cada uno con su protagonista: George Udny Yule, una "
            "bandada de cigüeñas y Karl Pearson."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Correlaciones sin sentido (1926)</b><br>"
            "<i>Comprueba con Yule que dos series que no tienen nada que ver se correlacionan a menudo con fuerza.</i><br><br>"
            "<b>II. Las cigüeñas traen a los niños</b><br>"
            "<i>Explica por qué los países con más cigüeñas tienen más nacimientos, y haz desaparecer la correlación.</i><br><br>"
            "<b>III. Los cocientes de Pearson (1897)</b><br>"
            "<i>Fabrica una correlación de la nada dividiendo dos variables independientes por una tercera.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>longitud de las series</u> y genera <u>otro par</u>")
        T = st.select_slider("Años observados", options=[10, 25, 50, 100, 250, 500], value=v["T"], key=ui.wkey(PAGE, "T"),
                             label_visibility="collapsed")
        if st.button("Otro par de series", key="new_walks", width="stretch"):
            st.session_state["walks"] += 1

        ui.planteamiento()
        ui.statement(
            "<b>Correlaciones sin sentido (1926)</b><br><br>"
            "En su discurso como presidente de la Royal Statistical Society, George Udny Yule mostró una correlación de 0.95 "
            "entre la proporción de bodas por la Iglesia de Inglaterra y la mortalidad, de 1866 a 1911. Nadie creía que "
            "una causara la otra. Simulamos dos <b>paseos aleatorios</b> independientes, series en las que cada año se suma "
            "un cambio al azar al valor del anterior, como hacen muchos indicadores económicos y sociales."
        )

        if ui.accordion_step("P1_A", "(A) ¿Qué falla?"):
            ui.content("Las dos series son independientes. ¿Por qué el coeficiente sale tan a menudo cerca de 1 o de &minus;1?")
            ui.spoiler(
                "Las observaciones de un paseo aleatorio no son independientes: el valor de cada año es casi el del "
                "anterior. Las dos series tienen tendencias largas, y dos tendencias cualesquiera, al compararse, van en el "
                "mismo sentido o en el contrario durante buena parte del tiempo. El test de correlación supone pares "
                "independientes, y aquí cada serie es en realidad un solo dato con muchas repeticiones."
            )

        if ui.accordion_step("P1_B", "(B) Más años no arreglan nada"):
            ui.content("Aumenta la longitud. Con ruido independiente, el histograma azul se estrecha. ¿Y el rojo?")
            ui.spoiler(
                "El rojo no se estrecha: la distribución de r entre paseos independientes no se concentra en cero aunque "
                "las series sean muy largas. Clive Granger y Paul Newbold mostraron en 1974 que las regresiones entre series "
                "así dan relaciones «significativas» con mucha frecuencia: la <b>regresión espuria</b>."
            )

        if ui.accordion_step("P1_C", "(C) Diferenciar"):
            ui.content("La curva verde usa los cambios de cada año en lugar de los valores. ¿Por qué funciona?")
            ui.spoiler(
                "Los cambios de un paseo aleatorio son independientes, así que sus correlaciones se comportan como las del "
                "ruido. Antes de correlacionar series temporales conviene quitarles la tendencia o diferenciarlas. Cuando "
                "dos series comparten de verdad una tendencia de largo plazo se habla de <b>cointegración</b>, y hay "
                "métodos específicos para contrastarla."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + T)
        steps = rng.standard_normal((2, PAIRS, T))
        walks = np.cumsum(steps, axis=2)
        r_walk = corr_rows(walks[0], walks[1])
        r_iid = corr_rows(steps[0], steps[1])
        r_diff = corr_rows(np.diff(walks[0], axis=1), np.diff(walks[1], axis=1))
        k = st.session_state["walks"] % PAIRS
        ui.metrics([(f"r de este par: {r_walk[k]:.3f}", "metric-a"),
                    (f"|r| &gt; 0.5: {ui.fmt_pct(np.mean(np.abs(r_walk) > 0.5), 0)} de los pares", "result-no"),
                    (f"Con ruido: {ui.fmt_pct(np.mean(np.abs(r_iid) > 0.5), 1)}", "metric-c")])
        ui.show(series_chart(dark, walks[0, k], walks[1, k]), key="fig_walks")
        ui.show(r_hist_chart(dark, r_walk, r_iid, r_diff), key="fig_rhist")
        ui.footer_bar(f"Arriba, un par de paseos aleatorios independientes de {T} años. Abajo, la correlación en "
                      f"{ui.fmt_int(PAIRS)} pares de cada tipo.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>influencia de la superficie</u> del país")
        a = st.slider("Influencia de la superficie en las dos variables", 0.0, 3.0, v["a"], 0.1, key=ui.wkey(PAGE, "a"),
                      label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las cigüeñas traen a los niños</b><br><br>"
            f"En el año 2000 Robert Matthews publicó, como ejemplo para profesores, una correlación de 0.62 entre el número "
            f"de parejas de cigüeñas y los nacimientos en {COUNTRIES} países europeos, con un p-valor de 0.008. Simulamos "
            "países en los que las cigüeñas no influyen en los nacimientos ni al revés, pero la <b>superficie</b> del país "
            "Z influye en las dos: más territorio, más nidos y más habitantes. El color de cada punto indica la superficie."
        )

        if ui.accordion_step("P2_A", "(A) La causa común"):
            ui.content("Si X = aZ + ruido e Y = aZ + ruido, con ruidos independientes de varianza 1, ¿cuánto vale la correlación entre X e Y?")
            ui.spoiler(
                "Cov(X, Y) = a<sup>2</sup>&#120141;(Z) y cada variable tiene varianza a<sup>2</sup>&#120141;(Z) + 1. Con "
                "&#120141;(Z) = 1:"
                "<div class='formula-box'>&rho;<sub>XY</sub> = <sup>a<sup>2</sup></sup>&frasl;<sub>a<sup>2</sup> + 1</sub></div>"
                "Una variable que influye en las dos basta para producir una correlación tan alta como se quiera sin ninguna "
                "relación causal entre ellas. Hans Reichenbach lo formuló en 1956 como principio de la causa común."
            )

        if ui.accordion_step("P2_B", "(B) La correlación parcial"):
            ui.content("¿Cómo se mide la relación entre X e Y una vez descontado el efecto de Z?")
            ui.spoiler(
                "Con la <b>correlación parcial</b>, la correlación entre los residuos de X e Y tras quitarles la parte "
                "lineal explicada por Z:"
                "<div class='formula-box'>r<sub>XY&middot;Z</sub> = <sup>r<sub>XY</sub> &minus; r<sub>XZ</sub>r<sub>YZ</sub></sup>&frasl;"
                "<sub>&radic;((1 &minus; r<sub>XZ</sub><sup>2</sup>)(1 &minus; r<sub>YZ</sub><sup>2</sup>))</sub></div>"
                "Aquí se queda cerca de cero: a igual superficie, las cigüeñas no dicen nada de los nacimientos."
            )

        if ui.accordion_step("P2_C", "(C) Correlación y causalidad"):
            ui.content("Controlar por Z ha funcionado porque sabíamos que existía. ¿Qué pasa si hay una causa común que nadie ha medido?")
            ui.spoiler(
                "Entonces la correlación parcial no puede descontarla, y ningún cálculo con los datos observados la "
                "detecta. Por eso la prueba más fuerte de causalidad es el experimento aleatorizado: si es el azar el que "
                "decide quién recibe el tratamiento, ninguna causa común puede estar asociada a él. Sin experimento, la "
                "causalidad se defiende acumulando indicios, como en los criterios que Austin Bradford Hill propuso en 1965 "
                "para el tabaco y el cáncer de pulmón."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + 3)
        z = rng.standard_normal(COUNTRIES)
        x = a * z + rng.standard_normal(COUNTRIES)
        y = a * z + rng.standard_normal(COUNTRIES)
        rxy, rxz, ryz = np.corrcoef(x, y)[0, 1], np.corrcoef(x, z)[0, 1], np.corrcoef(y, z)[0, 1]
        ui.metrics([(f"r<sub>XY</sub> = {rxy:.3f}", "result-no" if rxy > 0.5 else "metric-a"),
                    (f"Teórica: {a ** 2 / (a ** 2 + 1):.3f}", "metric-c"),
                    (f"Parcial dada Z: {partial(rxy, rxz, ryz):.3f}", "metric-b")])
        ui.show(storks_chart(dark, (x - x.mean()) / x.std(), (y - y.mean()) / y.std(), z), key="fig_storks")
        ui.footer_bar(f"{COUNTRIES} países simulados; los de color más cálido son los más extensos. La correlación aparece "
                      "porque los países grandes están arriba a la derecha y los pequeños abajo a la izquierda.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>variabilidad del divisor Z</u>")
        cvz = st.slider("Coeficiente de variación de Z", 0.0, 0.5, v["cvz"], 0.01, key=ui.wkey(PAGE, "cvz"),
                        label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Los cocientes de Pearson (1897)</b><br><br>"
            "Karl Pearson advirtió a los biólogos que comparaban índices, medidas de órganos divididas por la longitud "
            "total del cuerpo, de que los cocientes podían correlacionarse aunque las medidas no lo hicieran. Pasa también "
            "con las tasas por habitante. Generamos tres variables independientes X, Y y Z, con X e Y de coeficiente de "
            f"variación {CV_XY}, y correlacionamos X/Z con Y/Z."
        )

        if ui.accordion_step("P3_A", "(A) De dónde sale"):
            ui.content("X, Y y Z son independientes. ¿Por qué X/Z e Y/Z no lo son?")
            ui.spoiler(
                "Comparten el denominador: cuando Z es pequeño, los dos cocientes son grandes a la vez, y cuando Z es grande, "
                "los dos son pequeños. La variabilidad de Z pasa a los dos cocientes en el mismo sentido y crea una "
                "correlación positiva aunque X e Y no tengan nada que ver."
            )

        if ui.accordion_step("P3_B", "(B) La fórmula de Pearson"):
            ui.content(
                "Con coeficientes de variación v<sub>X</sub>, v<sub>Y</sub>, v<sub>Z</sub> pequeños, aproxima log(X/Z) = "
                "log X &minus; log Z. ¿Qué correlación sale?"
            )
            ui.spoiler(
                "Por el método delta, log X &asymp; log &mu;<sub>X</sub> + (X &minus; &mu;<sub>X</sub>)/&mu;<sub>X</sub>, con "
                "varianza v<sub>X</sub><sup>2</sup>. Los dos logaritmos de los cocientes comparten &minus;log Z:"
                "<div class='formula-box'>r &asymp; <sup>v<sub>Z</sub><sup>2</sup></sup>&frasl;<sub>&radic;((v<sub>X</sub><sup>2</sup> + "
                "v<sub>Z</sub><sup>2</sup>)(v<sub>Y</sub><sup>2</sup> + v<sub>Z</sub><sup>2</sup>))</sub></div>"
                "Con v<sub>Z</sub> = v<sub>X</sub> = v<sub>Y</sub> sale 0.5. Cuando Z varía mucho, la aproximación pierde "
                "precisión pero la correlación sigue creciendo hacia 1."
            )

        if ui.accordion_step("P3_C", "(C) Correlaciones fabricadas por la selección"):
            ui.content("Hay otra forma de fabricar correlaciones sin dividir: elegir qué casos se miran. ¿Se te ocurre un ejemplo?")
            ui.spoiler(
                "Joseph Berkson observó en 1946 que dos enfermedades independientes en la población aparecen asociadas "
                "entre los pacientes de un hospital, porque tener cualquiera de las dos aumenta la probabilidad de estar "
                "ingresado. Es la <b>paradoja de Berkson</b>: la selección de la muestra, y no la naturaleza, crea la "
                "relación. Igual que con los cocientes, el problema no está en el cálculo de r sino en de dónde salen los "
                "datos."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + 11)
        n = 1500
        X = rng.normal(10, 10 * CV_XY, n)
        Y = rng.normal(10, 10 * CV_XY, n)
        Z = np.maximum(rng.normal(10, 10 * cvz, n), 1.0)
        rx, ry = X / Z, Y / Z
        ui.metrics([(f"r(X, Y) = {np.corrcoef(X, Y)[0, 1]:.3f}", "metric-c"),
                    (f"r(X/Z, Y/Z) = {np.corrcoef(rx, ry)[0, 1]:.3f}", "result-no" if np.corrcoef(rx, ry)[0, 1] > 0.3 else "metric-a"),
                    (f"Fórmula de Pearson: {pearson_ratio(cvz):.3f}", "metric-b")])
        ui.show(ratio_chart(dark, rx, ry), key="fig_ratios")
        ui.footer_bar(f"{ui.fmt_int(n)} individuos simulados con X, Y y Z independientes. Z se trunca en 1 para que no se "
                      "anule el denominador.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Correlaciones sin sentido", "P1_A"),
        ("P2", "(II) Las cigüeñas", "P2_A"),
        ("P3", "(III) Los cocientes de Pearson", "P3_A"),
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
