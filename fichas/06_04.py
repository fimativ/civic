#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 4: las leyes de los grandes números.

La moneda de Kerrich (la frecuencia converge, la diferencia no), el casino
siempre gana (la media de las apuestas converge casi seguro) y la condición de
Kolmogórov (qué varianzas permite la ley fuerte).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Band, ColumnDataSource, Span

import civic_ui as ui

TITLE = "Las leyes de los grandes números"
SYMBOL = "X̄ₙ → μ"
PAGE = "06_04"

TOSSES = 10000
EDGE = 1 / 37


def initial_values():
    return {
        "paths": ui.dint(5, 3, 8, "paths"),
        "bets": ui.dchoice(10000, [1000, 5000, 10000, 50000], "bets"),
        "a": ui.dfloat(0.5, 0.0, 0.9, "a", 1),
        "seed": int(ui.r("kerrich") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "coin_round": 0, "casino_round": 0, "kol_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def coin_paths(k: int, seed: int):
    rng = np.random.default_rng(seed)
    flips = rng.integers(0, 2, (k, TOSSES))
    return np.cumsum(flips, axis=1)


def casino_paths(n: int, players: int, seed: int):
    rng = np.random.default_rng(seed)
    gains = np.where(rng.random((players, n)) < 18 / 37, 1.0, -1.0)
    return np.cumsum(gains, axis=1)


def kolmogorov_paths(a: float, n: int, k: int, seed: int):
    rng = np.random.default_rng(seed)
    i = np.arange(1, n + 1)
    signs = rng.choice([-1.0, 1.0], (k, n))
    x = signs * i ** (a / 2)
    return np.cumsum(x, axis=1) / i


# =============================================================================
# 2. FIGURAS
# =============================================================================

def coin_charts(dark, heads):
    ns = np.arange(1, TOSSES + 1)
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.RED_LINE, "#00838f", ui.GREY_LINE, ui.UBU_RED]
    p = ui.new_figure(dark, height=250, x_axis_type="log", x_axis_label="lanzamientos", y_axis_label="frecuencia de caras",
                      x_range=(1, TOSSES), y_range=(0.3, 0.7))
    for i, h in enumerate(heads):
        p.line(ns, h / ns, line_width=2, color=palette[i % len(palette)], alpha=0.85)
    p.add_layout(Span(location=0.5, dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    p.scatter([TOSSES], [0.5067], size=14, marker="diamond", color=ui.UBU_YELLOW, line_color=ui.UBU_DARK)
    q = ui.new_figure(dark, height=230, x_axis_label="lanzamientos", y_axis_label="caras − n/2", x_range=(1, TOSSES))
    src = ColumnDataSource(dict(x=ns, lo=-np.sqrt(ns), hi=np.sqrt(ns)))
    q.add_layout(Band(base="x", lower="lo", upper="hi", source=src, fill_color=ui.GREY_LINE, fill_alpha=0.15))
    for i, h in enumerate(heads):
        q.line(ns, h - ns / 2, line_width=2, color=palette[i % len(palette)], alpha=0.85)
    q.scatter([TOSSES], [67], size=14, marker="diamond", color=ui.UBU_YELLOW, line_color=ui.UBU_DARK)
    return p, q


def casino_chart(dark, totals):
    n = totals.shape[1]
    ns = np.arange(1, n + 1)
    p = ui.new_figure(dark, height=300, x_axis_type="log", x_axis_label="apuestas de un tharni",
                      y_axis_label="ganancia media por apuesta (tharni)", x_range=(1, n), y_range=(-0.4, 0.4))
    for t in totals:
        p.line(ns, t / ns, line_width=1.5, color=ui.BLUE_LINE, alpha=0.35)
    p.add_layout(Span(location=-EDGE, dimension="width", line_color=ui.UBU_RED, line_width=3))
    p.add_layout(Span(location=0, dimension="width", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    return p


def kolmogorov_chart(dark, means, a: float):
    n = means.shape[1]
    ns = np.arange(1, n + 1)
    lim = 3.0
    p = ui.new_figure(dark, height=270, x_axis_type="log", x_axis_label="n", y_axis_label="media de las n primeras",
                      x_range=(1, n), y_range=(-lim, lim))
    for m in means:
        p.line(ns, np.clip(m, -lim, lim), line_width=1.8, color=ui.BLUE_LINE, alpha=0.45)
    p.add_layout(Span(location=0, dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    q = ui.new_figure(dark, height=200, x_axis_type="log", y_axis_type="log", x_axis_label="n",
                      y_axis_label="𝕍(media)", x_range=(1, n))
    var = np.cumsum(ns ** a) / ns ** 2
    q.line(ns, var, line_width=3, color=ui.ORANGE_LINE)
    return p, q


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Por qué la media de muchas observaciones deja de ser aleatoria?</b>")
        ui.content(
            "Las leyes de los grandes números dicen cuándo la media de muchas variables se comporta como un número fijo. "
            "La <b>ley débil</b> afirma que converge en probabilidad; la <b>ley fuerte</b>, que converge casi seguro: cada "
            "sucesión de observaciones, salvo un conjunto de probabilidad cero, acaba estabilizándose en la media. "
            "<i>Escribe la ley fuerte para variables independientes e idénticamente distribuidas.</i>"
        )
        ui.formula_hidden("X<sub>i</sub> i.i.d., &#120124;[X<sub>i</sub>] = &mu; &nbsp;&rArr;&nbsp; "
                          "&#8473;(X̄<sub>n</sub> &rarr; &mu;) = 1")
        ui.content(
            "Para variables independientes con distintas varianzas basta la condición de Kolmogórov: "
            "&sum; &sigma;<sub>n</sub><sup>2</sup>/n<sup>2</sup> &lt; &infin;. La ley fuerte es la que justifica de verdad la definición "
            "frecuentista de la probabilidad que intuyó Graunt: con probabilidad uno, la frecuencia relativa de un suceso "
            "converge a su probabilidad."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La moneda de Kerrich (1946)</b><br>"
            "<i>Diez mil lanzamientos en un campo de internamiento: la frecuencia se estabiliza, la diferencia "
            "no.</i><br><br>"
            "<b>II. El casino siempre gana</b><br>"
            "<i>Por qué un tharni de ventaja en cada treinta y siete basta para que la banca no pierda nunca a largo "
            "plazo.</i><br><br>"
            "<b>III. La condición de Kolmogórov (1930)</b><br>"
            "<i>Variables cada vez más dispersas: ¿hasta dónde aguanta la ley fuerte?</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de trayectorias</u>")
        k = st.slider("Trayectorias simuladas", 1, 8, v["paths"], 1, key=ui.wkey(PAGE, "paths"),
                      label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La moneda de Kerrich (1946)</b><br><br>"
            "John Kerrich, matemático sudafricano, estaba de visita en Copenhague cuando Alemania invadió Dinamarca, y "
            "pasó la guerra internado. Para entretenerse, y con ayuda de otro preso, lanzó una moneda diez mil veces y "
            "anotó cada resultado. Obtuvo 5067 caras. Lo publicó en 1946 como introducción experimental a la "
            "probabilidad. El rombo amarillo marca su resultado."
        )

        if ui.accordion_step("P1_A", "(A) La frecuencia converge"):
            ui.content(
                "La frecuencia de caras tras n lanzamientos es la media de n indicatrices. ¿Qué dice la ley fuerte de cada "
                "una de las trayectorias de arriba?"
            )
            ui.spoiler(
                "Con probabilidad uno, la frecuencia de cada trayectoria converge a 1/2: no solo la mayoría de las "
                "trayectorias está cerca de 1/2 para n grande, como garantizaba la ley débil, sino que cada una acaba "
                "atrapada alrededor de 1/2 y ya no se escapa. Es la definición frecuentista, ahora con demostración."
            )

        if ui.accordion_step("P1_B", "(B) La diferencia no converge"):
            ui.content(
                "Mira el gráfico de abajo, la diferencia entre el número de caras y n/2. ¿Tiende a cero? ¿Cómo crece su "
                "dispersión?"
            )
            ui.spoiler(
                "No: la desviación típica de caras &minus; n/2 es &radic;n/2, así que la diferencia en número absoluto tiende a "
                "crecer, del orden de &radic;n. La frecuencia converge porque esa diferencia se divide entre n, que crece más "
                "deprisa. La ley de los grandes números no iguala las caras y las cruces: diluye la diferencia. Es la "
                "misma confusión que la de los jugadores de Montecarlo."
            )

        if ui.accordion_step("P1_C", "(C) ¿Fue normal el resultado de Kerrich?"):
            ui.content(
                "Kerrich obtuvo 67 caras de más. ¿Cuántas desviaciones típicas son? ¿Es un resultado sospechoso?"
            )
            ui.spoiler(
                "Con n = 10 000, la desviación típica del número de caras es &radic;(10 000/4) = 50. Un exceso de 67 caras son "
                "1.34 desviaciones: perfectamente normal. Su exceso de 67 caras cae dentro de la banda gris del "
                "gráfico de abajo, que marca &plusmn;2 desviaciones (&plusmn;100)."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otras trayectorias", key="coin_new", width="stretch"):
            st.session_state["coin_round"] += 1
        heads = coin_paths(k, v["seed"] + st.session_state["coin_round"])
        final = heads[:, -1]
        ui.metrics([(f"Frecuencias finales: {', '.join(f'{h / TOSSES:.4f}' for h in final[:4])}", "metric-a"),
                    ("Kerrich: 0.5067", "metric-c")])
        p, q = coin_charts(dark, heads)
        ui.show(p, key="fig_kerrich_freq")
        ui.show(q, key="fig_kerrich_diff")
        ui.footer_bar("Arriba, la frecuencia de caras de cada trayectoria. Abajo, el exceso de caras sobre n/2, con la banda "
                      "de &plusmn;&radic;n (dos desviaciones típicas).")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de apuestas</u>")
        n = st.select_slider("Apuestas por jugador", options=[500, 1000, 5000, 10000, 50000], value=v["bets"],
                             key=ui.wkey(PAGE, "bets"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El casino siempre gana</b><br><br>"
            "Un jugador apuesta un tharni al rojo una y otra vez en una ruleta europea: gana un tharni con probabilidad "
            "18/37 y lo pierde con probabilidad 19/37. Cincuenta jugadores hacen lo mismo cada noche. El casino no sabe "
            "quién ganará esta noche, pero sabe perfectamente cuánto ganará él al cabo del año. ¿Por qué?"
        )

        if ui.accordion_step("P2_A", "(A) La ventaja de la banca"):
            ui.content("Calcula la media y la varianza de la ganancia de una apuesta.")
            ui.spoiler(
                "<div class='formula-box'>&#120124;[G] = 1&middot;<sup>18</sup>&frasl;<sub>37</sub> &minus; 1&middot;<sup>19</sup>&frasl;<sub>37</sub> "
                "= &minus;<sup>1</sup>&frasl;<sub>37</sub> &nbsp;&nbsp; &#120141;(G) = 1 &minus; <sup>1</sup>&frasl;<sub>37<sup>2</sup></sub></div>"
                "Una ventaja del 2.7 % por tharni apostado, debida solo al cero."
            )

        if ui.accordion_step("P2_B", "(B) La ley fuerte trabaja para la banca"):
            ui.content(
                "¿A qué converge la ganancia media por apuesta de cada jugador si sigue jugando? ¿Y el beneficio total del "
                "casino, sumando todos los jugadores?"
            )
            ui.spoiler(
                "Por la ley fuerte, la ganancia media de cada jugador converge casi seguro a &minus;1/37: todas las curvas de "
                "la derecha acaban sobre la línea roja. El beneficio del casino tras N apuestas en total es del orden de "
                "N/37 tharni, con una incertidumbre de solo &radic;N: con millones de apuestas, el resultado del año es "
                "casi determinista."
            )

        if ui.accordion_step("P2_C", "(C) ¿Por qué hay ganadores?"):
            ui.content(
                "Hay jugadores que van ganando tras cientos de apuestas. ¿Cuántas apuestas hacen falta para que la "
                "desventaja se imponga a la suerte?"
            )
            ui.spoiler(
                "Tras n apuestas, la ganancia total tiene media &minus;n/37 y desviación del orden de &radic;n. La desventaja "
                "domina cuando n/37 supera a &radic;n, es decir, a partir de unas 37<sup>2</sup> &asymp; 1400 apuestas. Antes, "
                "la suerte puede dar ventaja a cualquiera; después, casi a nadie. El casino, que suma las apuestas de "
                "todos, vive siempre en el segundo régimen."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otra noche", key="casino_new", width="stretch"):
            st.session_state["casino_round"] += 1
        totals = casino_paths(n, 50, v["seed"] + st.session_state["casino_round"])
        winners = (totals[:, -1] > 0).mean()
        ui.metrics([(f"Jugadores en ganancias al final: {ui.fmt_pct(winners, 0)}", "metric-c"),
                    (f"Beneficio del casino: {-totals[:, -1].sum():,.0f} tharni".replace(",", " "), "metric-a")])
        ui.show(casino_chart(dark, totals), key="fig_casino")
        ui.footer_bar(f"Cincuenta jugadores, {ui.fmt_int(n)} apuestas cada uno. Beneficio esperado del casino: "
                      f"{50 * n / 37:,.0f} tharni.".replace(",", " "))


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>exponente a</u> de las varianzas")
        a = st.slider("a", 0.0, 1.8, v["a"], 0.1, key=ui.wkey(PAGE, "a"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La condición de Kolmogórov (1930)</b><br><br>"
            "Andréi Kolmogórov encontró en 1930 condiciones muy generales para la ley fuerte. Pongámosla a prueba con "
            "variables independientes de media cero cada vez más dispersas: X<sub>i</sub> vale &plusmn;i<sup>a/2</sup> con probabilidad "
            "1/2, de modo que &#120141;(X<sub>i</sub>) = i<sup>a</sup>. Con a = 0 son monedas de &plusmn;1. ¿Sigue convergiendo la media a "
            "cero cuando a crece?"
        )

        if ui.accordion_step("P3_A", "(A) La varianza de la media"):
            ui.content("Calcula &#120141;(X̄<sub>n</sub>) aproximando la suma por una integral. ¿Para qué a tiende a cero?")
            ui.spoiler(
                "<div class='formula-box'>&#120141;(X̄<sub>n</sub>) = <sup>1</sup>&frasl;<sub>n<sup>2</sup></sub>&sum;<sub>i=1</sub><sup>n</sup> i<sup>a</sup> "
                "&asymp; <sup>n<sup>a&minus;1</sup></sup>&frasl;<sub>a + 1</sub></div>"
                "Tiende a cero si y solo si a &lt; 1: es la condición de la ley débil para variables incorreladas. Con a = 1 "
                "se estanca y con a &gt; 1 crece: la media no se estabiliza, como muestran las trayectorias."
            )

        if ui.accordion_step("P3_B", "(B) El criterio de Kolmogórov"):
            ui.content("Comprueba si la serie &sum; &sigma;<sub>n</sub><sup>2</sup>/n<sup>2</sup> converge. ¿Coincide la frontera con la del apartado anterior?")
            ui.spoiler(
                "&sum; n<sup>a</sup>/n<sup>2</sup> = &sum; n<sup>a&minus;2</sup> converge si y solo si a &lt; 1. Para a &lt; 1 la media "
                "converge casi seguro a 0: la ley fuerte. En este ejemplo las fronteras de las dos leyes coinciden, pero "
                "en general el criterio de Kolmogórov es más exigente, porque pide algo sobre cada trayectoria."
            )

        if ui.accordion_step("P3_C", "(C) Sin varianza"):
            ui.content(
                "Para variables idénticamente distribuidas, ¿hace falta que tengan varianza finita? ¿Y media?"
            )
            ui.spoiler(
                "Kolmogórov demostró que, para variables i.i.d., la ley fuerte se cumple si y solo si tienen media finita: "
                "la varianza puede ser infinita, aunque entonces la convergencia es más lenta. Sin media no hay ley: la "
                "media de los destellos del faro de Cauchy no converge a nada, como viste en el tema de vectores."
            )

    with col_right:
        ui.right_panel()
        n = 5000
        if st.button("Otras trayectorias", key="kol_new", width="stretch"):
            st.session_state["kol_round"] += 1
        means = kolmogorov_paths(a, n, 12, v["seed"] + st.session_state["kol_round"])
        var_n = float(np.sum(np.arange(1, n + 1) ** a)) / n ** 2
        ui.metrics([(f"&#120141;(X̄<sub>{n}</sub>) = {var_n:.4f}", "metric-a"),
                    ("Ley fuerte: sí" if a < 1 else "Ley fuerte: no", "result-yes" if a < 1 else "result-no")])
        p, q = kolmogorov_chart(dark, means, a)
        ui.show(p, key="fig_kol_paths")
        ui.show(q, key="fig_kol_var")
        ui.footer_bar(f"Con a = {a:.1f}: arriba, doce trayectorias de la media; abajo, su varianza en función de n, en "
                      "escala logarítmica.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La moneda de Kerrich", "P1_A"),
        ("P2", "(II) El casino siempre gana", "P2_A"),
        ("P3", "(III) La condición de Kolmogórov", "P3_A"),
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
