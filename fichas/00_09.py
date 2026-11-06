#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 9: el tamaño muestral.

Cuántas entrevistas necesita una encuesta para estimar una media o una
proporción con un margen dado, cuántas parcelas necesitaba Gosset para
detectar una diferencia entre dos cebadas, y por qué el ensayo de la vacuna
de Salk necesitó cientos de miles de niños.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Tamaño muestral"
PAGE = "00_09"

PARAMS = {"prop": "Proporción", "mean": "Media"}
DESIGNS = {"one": "Una muestra", "two": "Dos muestras"}
CONF = [0.90, 0.95, 0.99]
POWERS = [0.80, 0.90, 0.95]


def initial_values():
    return {
        "param": ui.dchoice("prop", list(PARAMS), "param"),
        "conf": ui.dchoice(0.95, CONF, "conf"),
        "E": ui.dchoice(3.0, [1.0, 2.0, 3.0, 4.0, 5.0], "E"),
        "p": round(20 * ui.dfloat(0.50, 0.10, 0.50, "p")) / 20,
        "sigma": ui.dint(15, 5, 30, "sigma"),
        "design": ui.dchoice("two", list(DESIGNS), "design"),
        "alpha": ui.dchoice(0.05, [0.01, 0.05, 0.10], "alpha"),
        "power": ui.dchoice(0.80, POWERS, "power"),
        "d": round(10 * ui.dfloat(0.5, 0.2, 1.0, "d", 1)) / 10,
        "rate": 5 * round(ui.dint(50, 10, 100, "rate") / 5),
        "cut": ui.dchoice(50, [30, 40, 50, 60, 70, 80], "cut"),
        "power_salk": ui.dchoice(0.90, POWERS, "power_salk"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "param": None, "design": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def z(q: float) -> float:
    return stats.norm.ppf(q)


def n_estimate(param: str, conf: float, E: float, p: float, sigma: float) -> float:
    """Tamaño para un margen de error E (en puntos porcentuales o en unidades de la media)."""
    zz = z(1 - (1 - conf) / 2)
    if param == "prop":
        return zz ** 2 * p * (1 - p) / (E / 100) ** 2
    return (zz * sigma / E) ** 2


def n_means(d, alpha, power, design):
    k = 2 if design == "two" else 1
    return k * ((z(1 - alpha / 2) + z(power)) / d) ** 2


def n_props(p1, p2, alpha, power):
    pb = (p1 + p2) / 2
    num = z(1 - alpha / 2) * np.sqrt(2 * pb * (1 - pb)) + z(power) * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return num ** 2 / (p1 - p2) ** 2


# =============================================================================
# 2. FIGURAS
# =============================================================================

def margin_chart(dark, param, conf, E, p, sigma):
    Es = np.linspace(0.5, 8, 200)
    p_fig = ui.new_figure(dark, height=300, x_axis_label="margen de error E" + (" (puntos)" if param == "prop" else ""),
                          y_axis_label="tamaño n", y_axis_type="log")
    for c, colour in zip(CONF, (ui.GREEN_LINE, ui.BLUE_LINE, ui.ORANGE_LINE)):
        p_fig.line(Es, n_estimate(param, c, Es, p, sigma), line_width=3, color=colour, legend_label=f"confianza {ui.fmt_pct(c, 0)}")
    p_fig.scatter([E], [n_estimate(param, conf, E, p, sigma)], size=13, color=ui.UBU_RED)
    return ui.style_legend(p_fig, dark, "top_right")


def effect_chart(dark, d, alpha, power, design):
    ds = np.linspace(0.1, 1.5, 200)
    p = ui.new_figure(dark, height=300, x_axis_label="tamaño del efecto d = δ/σ", y_axis_label="tamaño n por grupo",
                      y_axis_type="log")
    for pw, colour in zip(POWERS, (ui.GREEN_LINE, ui.BLUE_LINE, ui.ORANGE_LINE)):
        p.line(ds, n_means(ds, alpha, pw, design), line_width=3, color=colour, legend_label=f"potencia {ui.fmt_pct(pw, 0)}")
    p.scatter([d], [n_means(d, alpha, power, design)], size=13, color=ui.UBU_RED)
    for x in (0.2, 0.5, 0.8):
        p.add_layout(Span(location=x, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted"))
    return ui.style_legend(p, dark, "top_right")


def salk_chart(dark, rate, cut, power):
    cuts = np.linspace(20, 90, 200)
    p1 = rate / 1e5
    p = ui.new_figure(dark, height=300, x_axis_label="reducción de casos con la vacuna (%)",
                      y_axis_label="niños por grupo", y_axis_type="log")
    for r, colour in ((rate / 2, ui.GREEN_LINE), (rate, ui.BLUE_LINE), (rate * 2, ui.ORANGE_LINE)):
        q = r / 1e5
        p.line(cuts, n_props(q, q * (1 - cuts / 100), 0.05, power), line_width=3, color=colour,
               legend_label=f"{r:.0f} casos por 100\u202f000")
    p.scatter([cut], [n_props(p1, p1 * (1 - cut / 100), 0.05, power)], size=13, color=ui.UBU_RED)
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuántos datos hacen falta?</b>")
        ui.content(
            "El tamaño de la muestra se decide <b>antes</b> de tomarla, y depende de cuatro cosas: el tipo de "
            "parámetro, la variabilidad de la población, el nivel de confianza o de significación, y la precisión que se "
            "quiere, que en un test es la diferencia que se quiere ser capaz de detectar con una potencia dada. Todas las "
            "fórmulas salen de despejar n de una igualdad de la normal. <i>¿Cuál es la más sencilla, para la media?</i>"
        )
        ui.formula_hidden("E = z<sub>&alpha;/2</sub><sup>&sigma;</sup>&frasl;<sub>&radic;n</sub> &nbsp;&rArr;&nbsp; "
                          "n = ( <sup>z<sub>&alpha;/2</sub>&sigma;</sup>&frasl;<sub>E</sub> )<sup>2</sup>")
        ui.content(
            "Como n aparece bajo una raíz, la precisión sale cara: reducir el error a la mitad cuesta cuatro veces más "
            "datos. Las tres situaciones recorren la estimación, la comparación de medias y la de proporciones."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. ¿Por qué mil entrevistas?</b><br>"
            "<i>Calcula cuántas personas necesita una encuesta electoral para un margen de tres puntos, y descubre que "
            "no depende del tamaño del país.</i><br><br>"
            "<b>II. Las cebadas de Gosset (1908)</b><br>"
            "<i>Decide cuántas parcelas sembrar para detectar una diferencia de rendimiento con la potencia "
            "deseada.</i><br><br>"
            "<b>III. La vacuna de Salk (1954)</b><br>"
            "<i>Entiende por qué el ensayo de la vacuna de la polio necesitó a cientos de miles de niños.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>parámetro</u>, la <u>confianza</u> y el <u>margen</u>")
        if st.session_state["param"] is None:
            st.session_state["param"] = v["param"]
        param = ui.choice_buttons(list(PARAMS), "param", labels=PARAMS, per_row=2)
        conf = st.select_slider("Nivel de confianza", options=CONF, value=v["conf"], format_func=lambda c: f"{ui.fmt_pct(c, 0)}",
                                key=ui.wkey(PAGE, "conf"))
        E = st.select_slider("Margen de error E" + (" (puntos porcentuales)" if param == "prop" else ""),
                             options=[1.0, 2.0, 3.0, 4.0, 5.0], value=v["E"], key=ui.wkey(PAGE, "E"))
        if param == "prop":
            p = st.slider("Proporción esperada p", 0.05, 0.95, v["p"], 0.05, key=ui.wkey(PAGE, "p"))
            sigma = v["sigma"]
        else:
            sigma = st.slider("Desviación de la población σ", 5, 30, v["sigma"], 1, key=ui.wkey(PAGE, "sigma"))
            p = v["p"]

        ui.planteamiento()
        ui.statement(
            "<b>¿Por qué mil entrevistas?</b><br><br>"
            "Las encuestas electorales suelen entrevistar a unas mil personas y anunciar un margen de error de unos tres "
            "puntos. Calculamos el tamaño necesario para estimar una proporción, la intención de voto, o una media, "
            "por ejemplo el gasto semanal en tharni, con un margen E y un nivel de confianza dados."
        )

        if ui.accordion_step("P1_A", "(A) Despejar n"):
            ui.content("Escribe el margen de error de la proporción muestral y despeja n. ¿Qué valor de p da el caso más desfavorable?")
            ui.spoiler(
                "Con la aproximación normal, E = z<sub>&alpha;/2</sub>&radic;(p(1 &minus; p)/n), así que"
                "<div class='formula-box'>n = <sup>z<sub>&alpha;/2</sub><sup>2</sup> p(1 &minus; p)</sup>&frasl;<sub>E<sup>2</sup></sub></div>"
                "p(1 &minus; p) es máximo en p = 1/2, donde vale 1/4. Si no se sabe nada de p, se usa ese valor y el "
                "tamaño vale para cualquier proporción. Con 95 % de confianza y E = 3 puntos sale n &asymp; 1068."
            )

        if ui.accordion_step("P1_B", "(B) Confianza y precisión"):
            ui.content("Pasa del 95 % al 99 % sin cambiar E. ¿Cuánto crece n? ¿Y si se quiere E = 1.5 en lugar de 3?")
            ui.spoiler(
                "Del 95 % al 99 %, z pasa de 1.96 a 2.58, y n se multiplica por (2.58/1.96)<sup>2</sup> &asymp; 1.73. "
                "Reducir el margen a la mitad multiplica n por 4. Las dos exigencias tiran en la misma dirección: más "
                "fiabilidad y más precisión a la vez solo se pagan con más datos."
            )

        if ui.accordion_step("P1_C", "(C) El tamaño del país"):
            ui.content("La fórmula no contiene el tamaño N de la población. ¿Cuándo importa? ¿Cómo se corrige?")
            ui.spoiler(
                "Sin reemplazamiento, la varianza lleva el factor 1 &minus; n/N, y el tamaño corregido es "
                "n = n<sub>0</sub>/(1 + n<sub>0</sub>/N), con n<sub>0</sub> el de la fórmula. Para N = 40 millones la "
                "corrección es despreciable; para un pueblo de 2000 habitantes, las 1068 entrevistas bajan a unas 696. "
                "Fuera de poblaciones pequeñas, una encuesta vale lo mismo en Andorra que en la India."
            )

    with col_right:
        ui.right_panel()
        n = n_estimate(param, conf, E, p, sigma)
        n_small = n / (1 + n / 2000)
        ui.metrics([(f"n = {ui.fmt_int(np.ceil(n))}", "metric-a"),
                    (f"z = {z(1 - (1 - conf) / 2):.3f}", "metric-c"),
                    (f"Si N = 2000: {ui.fmt_int(np.ceil(n_small))}", "metric-b")])
        ui.show(margin_chart(dark, param, conf, E, p, sigma), key="fig_margin")
        what = f"p = {p:.2f}" if param == "prop" else f"&sigma; = {sigma}"
        ui.footer_bar(f"Tamaño necesario frente al margen de error, con {what}, para tres niveles de confianza (escala "
                      "logarítmica). El punto rojo es tu elección.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>diseño</u>, el <u>efecto</u>, el <u>nivel &alpha;</u> y la <u>potencia</u>")
        if st.session_state["design"] is None:
            st.session_state["design"] = v["design"]
        design = ui.choice_buttons(list(DESIGNS), "design", labels=DESIGNS, per_row=2)
        d = st.slider("Efecto a detectar d = δ/σ", 0.1, 1.5, v["d"], 0.1, key=ui.wkey(PAGE, "d"))
        alpha = st.select_slider("Nivel α (bilateral)", options=[0.01, 0.05, 0.10], value=v["alpha"],
                                 key=ui.wkey(PAGE, "alpha"))
        power = st.select_slider("Potencia 1 − β", options=POWERS, value=v["power"], format_func=lambda c: f"{ui.fmt_pct(c, 0)}",
                                 key=ui.wkey(PAGE, "power"))

        ui.planteamiento()
        ui.statement(
            "<b>Las cebadas de Gosset (1908)</b><br><br>"
            "En la cervecería Guinness, William Gosset ayudaba a elegir variedades de cebada con ensayos en parcelas, "
            "siempre con pocas parcelas porque cada una costaba una cosecha. Queremos detectar una diferencia de "
            "rendimiento &delta;, medida en desviaciones típicas (d = &delta;/&sigma;), con un test bilateral de nivel "
            "&alpha; y una potencia dada. Con una muestra se compara una variedad con un valor de referencia; con dos, "
            "dos variedades entre sí."
        )

        if ui.accordion_step("P2_A", "(A) La fórmula con potencia"):
            ui.content(
                "El test rechaza cuando |Z| &gt; z<sub>&alpha;/2</sub>. Exige que, con la diferencia &delta;, rechace con "
                "probabilidad 1 &minus; &beta;. ¿Qué n sale?"
            )
            ui.spoiler(
                "Ignorando la cola contraria, la condición es &delta;&radic;n/&sigma; = z<sub>&alpha;/2</sub> + "
                "z<sub>&beta;</sub>. Con dos grupos de n cada uno la varianza de la diferencia es el doble:"
                "<div class='formula-box'>n = k&middot;( <sup>z<sub>&alpha;/2</sub> + z<sub>&beta;</sub></sup>&frasl;<sub>d</sub> )<sup>2</sup>, "
                "&nbsp; k = 1 o 2</div>"
                "Con d = 0.5, &alpha; = 0.05 y potencia 0.80, salen 63 parcelas por variedad."
            )

        if ui.accordion_step("P2_B", "(B) Efectos pequeños"):
            ui.content(
                "Las líneas punteadas marcan los efectos que Jacob Cohen llamó pequeño, mediano y grande: 0.2, 0.5 y 0.8. "
                "¿Cuánto cuesta detectar uno pequeño frente a uno grande?"
            )
            ui.spoiler(
                "Como n &prop; 1/d<sup>2</sup>, pasar de d = 0.8 a d = 0.2 multiplica el tamaño por 16. Los estudios "
                "pequeños solo pueden detectar efectos grandes: si el efecto real es pequeño, un estudio con poca potencia "
                "casi nunca lo encontrará, y cuando lo encuentra suele exagerarlo."
            )

        if ui.accordion_step("P2_C", "(C) Sin conocer &sigma;"):
            ui.content("La fórmula usa la normal y &sigma; conocida. ¿Qué cambia cuando el análisis final será una t de Student?")
            ui.spoiler(
                "La t tiene colas más pesadas, así que hacen falta unas pocas observaciones más; la potencia exacta con la t "
                "es 0.795 en lugar de 0.80 con las 63 parcelas del ejemplo. Más grave es no conocer &sigma;: se "
                "toma de estudios previos o de un estudio piloto, y un &sigma; optimista da un tamaño insuficiente. Por eso "
                "se suele planificar en función de d, que no necesita conocer &sigma; por separado."
            )

    with col_right:
        ui.right_panel()
        n = n_means(d, alpha, power, design)
        ui.metrics([(f"n = {ui.fmt_int(np.ceil(n))}" + (" por grupo" if design == "two" else ""), "metric-a"),
                    (f"Total: {ui.fmt_int(np.ceil(n) * (2 if design == 'two' else 1))}", "metric-b"),
                    (f"z<sub>&alpha;/2</sub> + z<sub>&beta;</sub> = {z(1 - alpha / 2) + z(power):.2f}", "metric-c")])
        ui.show(effect_chart(dark, d, alpha, power, design), key="fig_effect")
        ui.footer_bar(f"Tamaño necesario frente al efecto d para tres potencias, con &alpha; = {alpha} (escala logarítmica). "
                      "Las líneas punteadas son los efectos pequeño, mediano y grande de Cohen.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>incidencia</u>, la <u>reducción</u> y la <u>potencia</u>")
        rate = st.slider("Casos por 100\u202f000 niños sin vacunar", 10, 100, v["rate"], 5, key=ui.wkey(PAGE, "rate"))
        cut = st.select_slider("Reducción de casos con la vacuna (%)", options=[30, 40, 50, 60, 70, 80], value=v["cut"],
                               key=ui.wkey(PAGE, "cut"))
        power = st.select_slider("Potencia", options=POWERS, value=v["power_salk"], format_func=lambda c: f"{ui.fmt_pct(c, 0)}",
                                 key=ui.wkey(PAGE, "power_salk"))

        ui.planteamiento()
        ui.statement(
            "<b>La vacuna de Salk (1954)</b><br><br>"
            "La vacuna de Jonas Salk contra la poliomielitis se probó en uno de los mayores experimentos de la historia de "
            "la medicina. En la parte con placebo, unos doscientos mil niños recibieron la vacuna y otros tantos una "
            "inyección de agua con sal, sin que ellos ni sus médicos supieran cuál. La polio paralítica era temida, pero "
            "afectaba cada año a unas decenas de niños de cada cien mil. Comparamos dos proporciones muy pequeñas."
        )

        if ui.accordion_step("P3_A", "(A) La fórmula para dos proporciones"):
            ui.content(
                "Con p<sub>1</sub> la incidencia sin vacuna y p<sub>2</sub> con ella, y p̄ su media, el tamaño por grupo es "
                "el de la fórmula. ¿De dónde sale cada raíz?"
            )
            ui.spoiler(
                "<div class='formula-box'>n = <sup>[ z<sub>&alpha;/2</sub>&radic;(2p̄(1 &minus; p̄)) + "
                "z<sub>&beta;</sub>&radic;(p<sub>1</sub>q<sub>1</sub> + p<sub>2</sub>q<sub>2</sub>) ]<sup>2</sup></sup>&frasl;"
                "<sub>(p<sub>1</sub> &minus; p<sub>2</sub>)<sup>2</sup></sub></div>"
                "La primera raíz es la desviación de la diferencia bajo H<sub>0</sub>, cuando las dos proporciones son "
                "iguales; la segunda, bajo la alternativa. Es la misma estructura que con medias, con varianzas binomiales."
            )

        if ui.accordion_step("P3_B", "(B) Sucesos raros"):
            ui.content("Fija la reducción y duplica la incidencia. ¿Qué le pasa a n? ¿Por qué hacen falta tantos niños?")
            ui.spoiler(
                "Cuando p es pequeña, p(1 &minus; p) &asymp; p y el numerador crece como p mientras el denominador crece "
                "como p<sup>2</sup>: n es aproximadamente inversamente proporcional a la incidencia. Lo que cuenta no es el "
                "número de niños sino el de casos: mira la métrica de casos esperados, que apenas cambia al mover la "
                "incidencia. Para detectar una reducción a la mitad con potencia 0.90 hacen falta unos 63 casos en el "
                "grupo sin vacuna, y con 50 casos por 100\u202f000 eso supone más de cien mil niños por grupo."
            )

        if ui.accordion_step("P3_C", "(C) Por qué tan grande"):
            ui.content("Con 50 casos por 100\u202f000 y una reducción a la mitad, la fórmula pide unos 126\u202f000 niños por grupo. El "
                       "ensayo usó unos doscientos mil. ¿Por qué más?")
            ui.spoiler(
                "La incidencia variaba mucho de un año y de una región a otra, y nadie sabía cuánto protegería la vacuna: "
                "había que asegurar potencia también en un año flojo de polio o con una vacuna menos eficaz. Además se "
                "querían estimar efectos por subgrupos y detectar efectos secundarios raros. El tamaño se calcula para el "
                "escenario desfavorable que se quiere cubrir, no para el esperado."
            )

    with col_right:
        ui.right_panel()
        p1 = rate / 1e5
        p2 = p1 * (1 - cut / 100)
        n = n_props(p1, p2, 0.05, power)
        ui.metrics([(f"Niños por grupo: {ui.fmt_int(np.ceil(n))}", "metric-a"),
                    (f"Casos esperados sin vacuna: {n * p1:.0f}", "metric-b"),
                    (f"Con vacuna: {n * p2:.0f}", "metric-c")])
        ui.show(salk_chart(dark, rate, cut, power), key="fig_salk")
        ui.footer_bar(f"Tamaño por grupo frente a la reducción de casos, con &alpha; = 0.05 bilateral y potencia {ui.fmt_pct(power, 0)}, "
                      "para tres incidencias (escala logarítmica).")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) ¿Por qué mil entrevistas?", "P1_A"),
        ("P2", "(II) Las cebadas de Gosset", "P2_A"),
        ("P3", "(III) La vacuna de Salk", "P3_A"),
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
