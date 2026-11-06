#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 3: convergencia en media cuadrática y casi segura.

El premio que se escapa (converge casi seguro pero no en media cuadrática),
la máquina de escribir (converge en media cuadrática pero no casi seguro) y
los números normales de Borel (la ley fuerte en las cifras de un número).
"""

from __future__ import annotations

from math import isqrt

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Cuatro modos de converger"
SYMBOL = "c.s.⇒P⇒d"
PAGE = "06_03"

SPECIAL = {"rand": "Un número al azar", "third": "1/3", "half": "1/2", "sqrt2": "√2 − 1"}
DIGITS = 2000


def initial_values():
    return {
        "u": ui.dfloat(0.03, 0.005, 0.2, "u", 3),
        "u_tw": ui.dfloat(0.37, 0.05, 0.95, "u_tw", 2),
        "n_tw": ui.dint(40, 10, 120, "n_tw"),
        "seed": int(ui.r("borel") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "number": "rand", "borel_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def typewriter_interval(n: int):
    k = int(np.floor(np.log2(n)))
    j = n - 2 ** k
    return j / 2 ** k, (j + 1) / 2 ** k


def typewriter_path(u: float, n_max: int):
    out = []
    for n in range(1, n_max + 1):
        a, b = typewriter_interval(n)
        out.append(1 if a <= u < b else 0)
    return np.array(out)


def binary_digits(kind: str, seed: int):
    if kind == "rand":
        return np.random.default_rng(seed).integers(0, 2, DIGITS)
    if kind == "third":
        return np.array([i % 2 for i in range(DIGITS)])            # 0.010101...
    if kind == "half":
        return np.array([1] + [0] * (DIGITS - 1))                    # 0.1000...
    root = isqrt(2 << (2 * DIGITS)) - (1 << DIGITS)                  # ⌊(√2 − 1)·2^DIGITS⌋, exacto
    return np.array([int(c) for c in format(root, f"0{DIGITS}b")])


# =============================================================================
# 2. FIGURAS
# =============================================================================

def prize_chart(dark, u: float):
    ns = np.arange(1, 201)
    x = np.where(u < 1 / ns, ns, 0)
    p = ui.new_figure(dark, height=250, x_axis_label="n", y_axis_label="Xₙ(u)", x_range=(0, 201),
                      y_range=(-2, max(10, x.max() * 1.1)))
    p.vbar(x=ns, top=x, width=0.8, color=ui.UBU_RED)
    p.add_layout(Span(location=1 / u, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    q = ui.new_figure(dark, height=230, x_axis_label="n", y_axis_type="log", y_range=(1e-3, 300),
                      y_axis_label="escala logarítmica", x_range=(1, 200))
    q.line(ns, 1 / ns, line_width=3, color=ui.BLUE_LINE, legend_label="ℙ(Xₙ ≠ 0) = 1/n")
    q.line(ns, np.ones_like(ns, dtype=float), line_width=3, color=ui.GREEN_LINE, legend_label="𝔼[Xₙ] = 1")
    q.line(ns, ns.astype(float), line_width=3, color=ui.UBU_RED, legend_label="𝔼[Xₙ²] = n")
    ui.style_legend(q, dark, "center_right")
    return p, q


def typewriter_charts(dark, u: float, n: int):
    path = typewriter_path(u, 255)
    ns = np.arange(1, 256)
    p = ui.new_figure(dark, height=240, x_axis_label="n", y_axis_label="Xₙ(u)", x_range=(0, 256), y_range=(-0.1, 1.2))
    p.vbar(x=ns, top=path, width=0.8, color=ui.UBU_RED)
    p.add_layout(Span(location=n, dimension="height", line_color=ui.BLUE_LINE, line_width=2))
    a, b = typewriter_interval(n)
    q = ui.new_figure(dark, height=130, x_axis_label="ω ∈ [0, 1]", x_range=(0, 1), y_range=(0, 1))
    q.yaxis.visible = False
    q.ygrid.grid_line_color = None
    q.quad(left=a, right=b, bottom=0.2, top=0.8, fill_color=ui.UBU_YELLOW, line_color=ui.UBU_DARK)
    q.add_layout(Span(location=u, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return p, q


def borel_chart(dark, digits):
    ns = np.arange(1, len(digits) + 1)
    freq = np.cumsum(digits) / ns
    p = ui.new_figure(dark, height=300, x_axis_type="log", x_axis_label="cifras binarias leídas",
                      y_axis_label="frecuencia de unos", x_range=(1, len(digits)), y_range=(0, 1))
    p.line(ns, freq, line_width=3, color=ui.BLUE_LINE)
    p.add_layout(Span(location=0.5, dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿De cuántas maneras puede converger una sucesión de variables?</b>")
        ui.content(
            "Además de la convergencia en distribución y en probabilidad hay otras dos. La <b>media cuadrática</b> pide "
            "que el error cuadrático medio tienda a cero; la <b>casi segura</b>, que la sucesión numérica "
            "X<sub>n</sub>(&omega;) converja para todos los resultados &omega;, salvo un conjunto de probabilidad cero. "
            "<i>Escribe las dos definiciones.</i>"
        )
        ui.formula_hidden("&#120124;[(X<sub>n</sub> &minus; X)<sup>2</sup>] &rarr; 0 &nbsp;&nbsp;&nbsp; "
                          "&#8473;({&omega; : X<sub>n</sub>(&omega;) &rarr; X(&omega;)}) = 1")
        ui.content(
            "Las dos implican la convergencia en probabilidad, que implica la convergencia en distribución. Pero "
            "entre ellas no hay relación: hay sucesiones que convergen casi seguro y no en media cuadrática, y al "
            "revés. Los dos primeros problemas son esos contraejemplos; el tercero, la convergencia casi segura más "
            "famosa."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El premio que se escapa</b><br>"
            "<i>Un premio cada vez mayor y cada vez menos probable: desaparece, pero su media no.</i><br><br>"
            "<b>II. La máquina de escribir</b><br>"
            "<i>Un carro que barre el intervalo una y otra vez: el error medio se anula, pero ningún punto se libra.</i>"
            "<br><br>"
            "<b>III. Los números normales de Borel (1909)</b><br>"
            "<i>Escribe un número al azar en binario y cuenta sus unos con Émile Borel.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número u</u> que sale del sorteo")
        u = st.slider("u", 0.001, 0.3, v["u"], 0.001, format="%.3f", key=ui.wkey(PAGE, "u"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El premio que se escapa</b><br><br>"
            "Se sortea un único número U, uniforme en (0, 1). Después, en la jornada n se paga un premio de n tharni si "
            "U &lt; 1/n, y nada en otro caso: X<sub>n</sub> = n&middot;1<sub>{U &lt; 1/n}</sub>. El premio crece, pero cada vez es más "
            "difícil cobrarlo. ¿Converge X<sub>n</sub> a 0? ¿En qué sentido?"
        )

        if ui.accordion_step("P1_A", "(A) Casi seguro"):
            ui.content(
                "Fija el valor u &gt; 0 que ha salido en el sorteo. ¿Qué le pasa a la sucesión de números X<sub>n</sub>(u)? ¿Para "
                "qué valores de u no converge a 0?"
            )
            ui.spoiler(
                "En cuanto n &gt; 1/u, se tiene u &ge; 1/n y X<sub>n</sub>(u) = 0 para siempre: la sucesión converge a 0. Solo "
                "falla para u = 0, que tiene probabilidad cero. Luego X<sub>n</sub> &rarr; 0 casi seguro, y por tanto también "
                "en probabilidad y en distribución."
            )

        if ui.accordion_step("P1_B", "(B) Pero no en media cuadrática"):
            ui.content("Calcula &#120124;[X<sub>n</sub>] y &#120124;[X<sub>n</sub><sup>2</sup>]. ¿Tienden a 0?")
            ui.spoiler(
                "<div class='formula-box'>&#120124;[X<sub>n</sub>] = n&middot;<sup>1</sup>&frasl;<sub>n</sub> = 1 &nbsp;&nbsp; "
                "&#120124;[X<sub>n</sub><sup>2</sup>] = n<sup>2</sup>&middot;<sup>1</sup>&frasl;<sub>n</sub> = n &rarr; &infin;</div>"
                "No hay convergencia en media cuadrática. Y la esperanza se queda en 1 aunque el límite sea 0: la "
                "convergencia casi segura no garantiza que converjan la media y el momento de segundo orden; la media cuadrática sí."
            )

        if ui.accordion_step("P1_C", "(C) Moraleja para estimadores"):
            ui.content(
                "Imagina un estimador que casi siempre acierta y muy de vez en cuando comete un error enorme. ¿Qué dirían "
                "de él la convergencia casi segura y el error cuadrático medio?"
            )
            ui.spoiler(
                "Converge casi seguro, pero su error cuadrático medio puede no bajar nunca, porque los errores raros y "
                "enormes pesan mucho en la media. En estadística el error cuadrático medio es el criterio habitual "
                "para comparar estimadores, y este ejemplo muestra que es más exigente que acabar acertando."
            )

    with col_right:
        ui.right_panel()
        last = int(np.floor(1 / u - 1e-12))
        ui.metrics([(f"Último premio cobrado: jornada {last}", "metric-a"), ("&#120124;[X<sub>n</sub>] = 1 para todo n", "metric-c")])
        p, q = prize_chart(dark, u)
        ui.show(p, key="fig_prize_path")
        ui.show(q, key="fig_prize_moments")
        ui.footer_bar("Arriba, la sucesión X<sub>n</sub>(u) para el número sorteado: se apaga a partir de n = 1/u. Abajo, "
                      "la probabilidad de premio baja, la media se queda en 1 y el segundo momento crece.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>punto &omega;</u> y la <u>posición n</u> del carro")
        u = st.slider("ω", 0.0, 0.999, v["u_tw"], 0.001, key=ui.wkey(PAGE, "u_tw"))
        n = st.slider("n", 1, 255, v["n_tw"], 1, key=ui.wkey(PAGE, "n_tw"))

        ui.planteamiento()
        ui.statement(
            "<b>La máquina de escribir</b><br><br>"
            "Sea &Omega; = [0, 1) con la probabilidad uniforme. El carro de una máquina de escribir recorre el intervalo: "
            "primero de una pasada, después en dos mitades, luego en cuatro cuartos, en ocho octavos&hellip; Si n = 2<sup>k</sup> "
            "+ j con 0 &le; j &lt; 2<sup>k</sup>, X<sub>n</sub> vale 1 en el tramo [j/2<sup>k</sup>, (j + 1)/2<sup>k</sup>) y 0 fuera. El "
            "carro es cada vez más estrecho, pero sigue pasando por todas partes."
        )

        if ui.accordion_step("P2_A", "(A) En media cuadrática"):
            ui.content("Calcula &#120124;[X<sub>n</sub><sup>2</sup>]. ¿Converge X<sub>n</sub> a 0 en media cuadrática? ¿Y en probabilidad?")
            ui.spoiler(
                "X<sub>n</sub><sup>2</sup> = X<sub>n</sub>, y su esperanza es la anchura del tramo, 2<sup>&minus;k</sup> &rarr; 0: hay "
                "convergencia en media cuadrática a 0, y por la desigualdad de Márkov también en probabilidad."
            )

        if ui.accordion_step("P2_B", "(B) Pero no casi seguro"):
            ui.content(
                "Fija un punto &omega; y mira la sucesión X<sub>n</sub>(&omega;) a la derecha. ¿Converge? ¿Para qué puntos?"
            )
            ui.spoiler(
                "En cada pasada el carro cubre todo [0, 1), así que X<sub>n</sub>(&omega;) = 1 una vez en cada bloque de n entre "
                "2<sup>k</sup> y 2<sup>k+1</sup>, e infinitas veces en total, y vale 0 el resto. La sucesión oscila entre 0 y 1 y no "
                "converge para ningún &omega;: el error de estimación viaja por el espacio muestral sin detenerse."
            )

        if ui.accordion_step("P2_C", "(C) Con independencia"):
            ui.content(
                "Otro ejemplo del mismo tipo: Y<sub>n</sub> vale 1 con probabilidad 1/n y 0 en otro caso, todas independientes. "
                "¿Converge en probabilidad? ¿Y casi seguro? Piensa en la serie &sum; 1/n."
            )
            ui.spoiler(
                "&#8473;(Y<sub>n</sub> = 1) = 1/n &rarr; 0: converge en probabilidad y en media cuadrática. Pero como la serie de "
                "las probabilidades diverge y los sucesos son independientes, el segundo lema de Borel-Cantelli asegura "
                "que Y<sub>n</sub> = 1 infinitas veces casi seguro: no converge casi seguro. Si la serie convergiera, por "
                "ejemplo con probabilidades 1/n<sup>2</sup>, el primer lema daría convergencia casi segura."
            )

    with col_right:
        ui.right_panel()
        a, b = typewriter_interval(n)
        path = typewriter_path(u, 255)
        ui.metrics([(f"&#120124;[X<sub>{n}</sub><sup>2</sup>] = {b - a:.4f}", "metric-a"),
                    (f"Veces que X<sub>n</sub>(&omega;) = 1 hasta 255: {path.sum()}", "metric-c")])
        p, q = typewriter_charts(dark, u, n)
        ui.show(p, key="fig_typewriter_path")
        ui.show(q, key="fig_typewriter_interval")
        ui.footer_bar(f"Arriba, la sucesión X<sub>n</sub>(&omega;) para &omega; = {u:.3f}: un uno en cada pasada del carro. Abajo, "
                      f"el tramo de X<sub>{n}</sub> y el punto &omega; en rojo.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>número</u> cuyas cifras se leen")
        ui.choice_buttons(list(SPECIAL), "number", labels=SPECIAL, per_row=4)

        ui.planteamiento()
        ui.statement(
            "<b>Los números normales de Borel (1909)</b><br><br>"
            "Émile Borel se preguntó cómo son las cifras de un número real elegido al azar en [0, 1). En binario, ¿qué "
            "fracción de sus cifras son unos? Su respuesta, publicada en 1909, fue la primera ley fuerte de los grandes "
            "números: casi todos los números son <i>normales</i>: cada bloque de k cifras aparece con frecuencia 1/2<sup>k</sup>; en particular, unos y ceros en proporción 1/2. Y sin "
            "embargo, es muy difícil señalar uno concreto que lo sea."
        )

        if ui.accordion_step("P3_A", "(A) Las cifras de un número al azar"):
            ui.content(
                "Si U es uniforme en [0, 1), ¿qué distribución tiene su primera cifra binaria? ¿Y las siguientes? ¿Son "
                "independientes?"
            )
            ui.spoiler(
                "La primera cifra es 1 si U &ge; 1/2: probabilidad 1/2. Fijar las k primeras cifras confina U a un tramo de "
                "longitud 2<sup>&minus;k</sup>, así que cada combinación tiene probabilidad 2<sup>&minus;k</sup>: las cifras son variables "
                "de Bernoulli de parámetro 1/2 independientes. Un número al azar es una sucesión infinita de lanzamientos "
                "de moneda."
            )

        if ui.accordion_step("P3_B", "(B) La ley fuerte"):
            ui.content(
                "Aplica a las cifras la ley fuerte de los grandes números. ¿Qué dice de la frecuencia de unos de cada número?"
            )
            ui.spoiler(
                "La frecuencia de unos entre las n primeras cifras converge a 1/2 casi seguro: el conjunto de números de "
                "[0, 1) cuya frecuencia no tiende a 1/2 tiene probabilidad cero. La curva azul de un número al azar se "
                "estabiliza en 1/2 y ya no se separa, una afirmación sobre cada trayectoria, más fuerte que la de la ley "
                "débil."
            )

        if ui.accordion_step("P3_C", "(C) Las excepciones"):
            ui.content(
                "Prueba con 1/3 y con 1/2. ¿Cumplen la ley? ¿Cuántos números hay como ellos? ¿Contradice eso la ley fuerte?"
            )
            ui.spoiler(
                "1/2 = 0.1000&hellip; tiene frecuencia de unos que tiende a 0, y 1/3 = 0.0101&hellip; sí tiende a 1/2, pero no es "
                "normal: la pareja 11 nunca aparece. Hay infinitos números excepcionales, incluso una "
                "cantidad no numerable, y aun así el conjunto que forman tiene probabilidad cero. <i>Casi seguro</i> no "
                "significa <i>seguro</i>: significa fuera de un conjunto de medida nula, como en la ficha de los relojes "
                "de Carroll. Se cree que &radic;2 &minus; 1 es normal, pero nadie lo ha demostrado."
            )

    with col_right:
        ui.right_panel()
        kind = st.session_state["number"]
        if st.button("Otro número al azar", key="borel_new", width="stretch"):
            st.session_state["borel_round"] += 1
        digits = binary_digits(kind, v["seed"] + st.session_state["borel_round"])
        pairs = "".join(map(str, digits[:400]))
        ui.metrics([(f"Frecuencia de unos: {digits.mean():.4f}", "metric-a"),
                    (f"Pareja «11» en las 400 primeras: {sum(pairs[i:i + 2] == '11' for i in range(399))} veces", "metric-c")])
        ui.show(borel_chart(dark, digits), key="fig_borel")
        shown = "".join(map(str, digits[:48]))
        ui.footer_bar(f"{SPECIAL[kind]} = 0.{shown}&hellip; (en binario). La línea roja marca 1/2.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El premio que se escapa", "P1_A"),
        ("P2", "(II) La máquina de escribir", "P2_A"),
        ("P3", "(III) Los números de Borel", "P3_A"),
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
