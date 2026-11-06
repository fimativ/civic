#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 1: las variables aleatorias.

La suma de dos dados en Catán (función de probabilidad y de distribución),
el máximo de varios dados en el Risk (la distribución del máximo a través de
la función de distribución) y los tres dados de Galileo (particiones frente a
resultados ordenados).
"""

from __future__ import annotations

from itertools import product

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "Variables aleatorias"
SYMBOL = "Ω → ℝ"
PAGE = "03_01"


def initial_values():
    return {
        "k": ui.dint(8, 2, 12, "k"),
        "attack": ui.dchoice(3, [1, 2, 3], "attack"),
        "defend": ui.dchoice(2, [1, 2], "defend"),
        "dice": ui.dint(3, 2, 5, "dice"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def sum_pmf(n: int):
    """Función de probabilidad de la suma de n dados (convolución)."""
    pmf = np.ones(6) / 6
    dist = np.array([1.0])
    for _ in range(n):
        dist = np.convolve(dist, pmf)
    return np.arange(n, 6 * n + 1), dist


def max_pmf(n: int):
    ks = np.arange(1, 7)
    cdf = (ks / 6) ** n
    return ks, np.diff(np.concatenate(([0.0], cdf))), cdf


def attacker_wins(a: int, d: int) -> float:
    """P(el máximo del atacante supera estrictamente al del defensor)."""
    _, pa, _ = max_pmf(a)
    _, _, cd = max_pmf(d)
    below = np.concatenate(([0.0], cd[:-1]))
    return float((pa * below).sum())


def ordered_counts(n: int, total: int) -> int:
    return sum(1 for roll in product(range(1, 7), repeat=n) if sum(roll) == total)


def partitions(n: int, total: int):
    return sorted({tuple(sorted(r, reverse=True)) for r in product(range(1, 7), repeat=n) if sum(r) == total},
                  reverse=True)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def catan_table(dark, k: int):
    xs, ys, colours, texts = [], [], [], []
    off = "#3a3a44" if dark else "#e8e8ec"
    for i in range(1, 7):
        for j in range(1, 7):
            xs.append(i)
            ys.append(j)
            colours.append(ui.UBU_RED if i + j == k else off)
            texts.append(str(i + j))
    p = ui.new_figure(dark, height=300, x_range=(0.5, 6.5), y_range=(0.5, 6.5), match_aspect=True,
                      x_axis_label="primer dado i", y_axis_label="segundo dado j")
    p.rect(x=xs, y=ys, width=0.92, height=0.92, fill_color=colours, line_color=None)
    p.text(x=xs, y=ys, text=texts, text_align="center", text_baseline="middle", text_font_size="15px",
           text_color=["#ffffff" if i + j == k else ("#dddddd" if dark else "#333333")
                       for i in range(1, 7) for j in range(1, 7)])
    p.xaxis.ticker = list(range(1, 7))
    p.yaxis.ticker = list(range(1, 7))
    p.grid.visible = False
    return p


def pmf_cdf_chart(dark, ks, pmf, k: int):
    cdf = np.cumsum(pmf)
    p = ui.new_figure(dark, height=280, x_axis_label="valor", y_axis_label="probabilidad",
                      x_range=(ks[0] - 1, ks[-1] + 1), y_range=(0, 1.05))
    colours = [ui.UBU_RED if x == k else ui.BLUE_LINE for x in ks]
    p.vbar(x=ks, top=pmf, width=0.7, fill_color=colours, line_color=None, legend_label="ℙ(X = x)")
    xs = np.concatenate(([ks[0] - 1], ks, [ks[-1] + 1]))
    ys = np.concatenate(([0.0], cdf, [1.0]))
    p.step(xs, ys, mode="after", line_width=3, color=ui.ORANGE_LINE, legend_label="F(x) = ℙ(X ≤ x)")
    p.scatter(ks, cdf, size=8, color=ui.ORANGE_LINE)
    p.xaxis.ticker = list(ks)
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_left")


def risk_chart(dark, a: int, d: int):
    ks, pa, _ = max_pmf(a)
    _, pd, _ = max_pmf(d)
    p = ui.new_figure(dark, height=300, x_axis_label="dado más alto", y_axis_label="probabilidad",
                      x_range=(0.4, 6.6), y_range=(0, 0.75))
    p.vbar(x=ks - 0.18, top=pa, width=0.34, color=ui.UBU_RED, alpha=0.85, legend_label=f"atacante ({a} dados)")
    p.vbar(x=ks + 0.18, top=pd, width=0.34, color=ui.BLUE_LINE, alpha=0.85, legend_label=f"defensor ({d} dados)")
    p.xaxis.ticker = list(range(1, 7))
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_left")


def galileo_chart(dark, n: int):
    ks, pmf = sum_pmf(n)
    colours = [ui.UBU_RED if k == 10 else (ui.ORANGE_LINE if k == 9 else ui.BLUE_LINE) for k in ks]
    p = ui.new_figure(dark, height=300, x_axis_label=f"suma de {n} dados", y_axis_label="probabilidad",
                      x_range=(ks[0] - 1, ks[-1] + 1), y_range=(0, max(pmf) * 1.2))
    p.vbar(x=ks, top=pmf, width=0.75, fill_color=colours, line_color=None)
    p.xgrid.grid_line_color = None
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es una variable aleatoria?</b>")
        ui.content(
            "Hasta ahora el modelo de un experimento tenía tres piezas: el espacio muestral &Omega;, los "
            "sucesos de interés &Ascr; y la probabilidad &#8473;. Pero lo que nos interesa casi siempre es "
            "un <b>número</b>: la suma de los dados, el número de caras, el tiempo de espera. Una variable "
            "aleatoria es una función X : &Omega; &rarr; &#8477; que asigna un número a cada resultado. "
            "Es <i>variable</i> porque toma distintos valores y <i>aleatoria</i> porque no se sabe cuál "
            "antes del experimento."
        )
        ui.content(
            "Para poder hablar de la probabilidad de sus valores, hay que exigirle algo: que los conjuntos "
            "de resultados en que X no supera un número sean sucesos. <i>Prueba a escribir esa condición.</i>"
        )
        ui.formula_hidden("{X &le; c} = {&omega; &isin; &Omega; : X(&omega;) &le; c} &isin; &Ascr; "
                          "&nbsp; para todo c &isin; &#8477;", hint="Pulsa para revelar la condición")
        ui.content(
            "Con ella, X traslada la probabilidad de &Omega; a la recta real: la <b>probabilidad "
            "inducida</b> &#8473;<sub>X</sub>(B) = &#8473;(X &isin; B). Si X toma una cantidad finita o "
            "numerable de valores es <b>discreta</b>, y basta con su función de probabilidad. "
            "<i>¿Qué dos propiedades debe cumplir?</i>"
        )
        ui.formula_hidden("&#8473;(X = x<sub>i</sub>) &ge; 0 &nbsp;;&nbsp; &sum;<sub>i</sub> "
                          "&#8473;(X = x<sub>i</sub>) = 1",
                          hint="Pulsa para revelar las propiedades")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los dados de Catán (1995)</b><br>"
            "<i>Descubre con Klaus Teuber por qué el ladrón vive en el siete y dónde conviene "
            "construir.</i><br><br>"
            "<b>II. La conquista del mundo (1957)</b><br>"
            "<i>Ataca y defiende con los dados del juego de Albert Lamorisse y calcula la distribución "
            "del dado más alto.</i><br><br>"
            "<b>III. Los tres dados de Galileo (hacia 1620)</b><br>"
            "<i>Responde con Galileo a la pregunta de un gran duque: ¿por qué sale más el diez que el "
            "nueve?</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige un <u>valor k</u> de la suma")
        k = st.slider("Valor k de la suma", 2, 12, v["k"], 1, key=ui.wkey(PAGE, "k"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Los dados de Catán (1995)</b><br><br>"
            "Klaus Teuber, protésico dental en un pueblo de Hesse, diseñaba juegos de mesa por las noches. "
            "En <i>Los colonos de Catán</i> cada casilla de terreno lleva una ficha numerada del 2 al 12, "
            "y en cada turno se lanzan dos dados: producen las casillas cuyo número coincide con la suma. "
            "Si sale un 7, no produce nadie y aparece el ladrón. ¿Por qué el 7, y dónde conviene fundar "
            "los poblados?"
        )

        if ui.accordion_step("P1_A", "(A) La suma es una función"):
            ui.content(
                "El espacio muestral son los 36 pares (i, j). Define la variable S(i, j) = i + j. ¿Cuál es "
                f"su imagen? ¿Qué resultados forman el suceso {{S = {v['k']}}}? Mira la tabla de la derecha."
            )
            ui.spoiler(
                "La imagen de S es {2, 3, &hellip;, 12}. El suceso {S = k} es la antiimagen "
                "S<sup>&minus;1</sup>(k) = {(i, j) : i + j = k}, una diagonal de la tabla. Como cada par es "
                "equiprobable, su probabilidad es el número de casillas de esa diagonal entre 36."
            )

        if ui.accordion_step("P1_B", "(B) La función de probabilidad"):
            ui.content(
                "Cuenta las casillas de cada diagonal y escribe una fórmula para &#8473;(S = k). ¿Por qué "
                "Teuber puso al ladrón en el 7? Las fichas del juego llevan puntitos debajo del número: "
                "¿qué crees que cuentan?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(S = k) = <sup>6 &minus; |k &minus; 7|</sup>&frasl;"
                "<sub>36</sub>, &nbsp; k = 2, &hellip;, 12</div>"
                "El 7 es la moda: el valor más probable, y por eso el que no produce nada. Los puntitos "
                "son exactamente 36&middot;&#8473;(S = k), el número de casos favorables: el 6 y el 8 "
                "llevan cinco y se imprimen en rojo. Las dos propiedades se cumplen: todo es positivo y "
                "las once probabilidades suman 36/36."
            )

        if ui.accordion_step("P1_C", "(C) La función de distribución"):
            ui.content(
                "La curva naranja es F(x) = &#8473;(S &le; x). ¿Por qué es una escalera? ¿Cuánto mide cada "
                "salto? Calcula con ella la probabilidad de que la suma esté entre 4 y 9, ambos incluidos."
            )
            ui.spoiler(
                "F acumula la función de probabilidad: es constante entre dos valores de la imagen y salta "
                "en cada x<sub>i</sub> exactamente &#8473;(S = x<sub>i</sub>). Es no decreciente, va de 0 a "
                "1 y es continua por la derecha. Para un intervalo basta restar:"
                "<div class='formula-box'>&#8473;(4 &le; S &le; 9) = F(9) &minus; F(3)</div>"
            )

    with col_right:
        ui.right_panel()
        ks, pmf = sum_pmf(2)
        p_k = pmf[k - 2]
        ui.metrics([
            (f"&#8473;(S = {k}) = {round(p_k * 36)}/36 = {p_k:.4f}", "metric-a"),
            (f"F({k}) = {pmf[:k - 1].sum():.4f}", "metric-c"),
        ])
        ui.show(catan_table(dark, k), key="fig_catan_table")
        ui.show(pmf_cdf_chart(dark, ks, pmf, k), key="fig_catan_pmf")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige los <u>dados del atacante</u> y los <u>del defensor</u>")
        c1, c2 = st.columns(2)
        a = c1.radio("Dados del atacante", [1, 2, 3], index=[1, 2, 3].index(v["attack"]), horizontal=True,
                     key=ui.wkey(PAGE, "attack"))
        d = c2.radio("Dados del defensor", [1, 2], index=[1, 2].index(v["defend"]), horizontal=True,
                     key=ui.wkey(PAGE, "defend"))

        ui.planteamiento()
        ui.statement(
            "<b>La conquista del mundo (1957)</b><br><br>"
            "Albert Lamorisse, el cineasta de <i>El globo rojo</i>, inventó un juego de estrategia que "
            "hoy conocemos como Risk. En cada batalla el atacante lanza hasta tres dados y el defensor "
            "hasta dos; se comparan los dados más altos de cada uno, y el empate favorece al defensor. "
            "Nosotros nos fijamos solo en esa primera comparación. La variable clave es el dado más alto, "
            "R = máx de los dados lanzados."
        )

        if ui.accordion_step("P2_A", "(A) El máximo de dos dados"):
            ui.content(
                "Con dos dados, construye la tabla de R(i, j) = máx(i, j) y cuenta cuántas casillas tienen "
                "cada valor. ¿Qué forma tiene la función de probabilidad?"
            )
            ui.spoiler(
                "El valor k aparece en una escuadra de la tabla con 2k &minus; 1 casillas:"
                "<div class='formula-box'>&#8473;(R = k) = <sup>2k &minus; 1</sup>&frasl;<sub>36</sub>, "
                "&nbsp; k = 1, &hellip;, 6</div>"
                "Crece con k: con dos dados es más probable que el más alto sea un 6 que cualquier otro valor."
            )

        if ui.accordion_step("P2_B", "(B) El truco de la función de distribución"):
            ui.content(
                "Con tres dados la tabla tiene 216 casillas. En lugar de contarlas, piensa en el suceso "
                "{R &le; k}: ¿qué tiene que pasar con cada dado? Obtén F(k) y de ella la función de "
                "probabilidad."
            )
            ui.spoiler(
                "El máximo no supera k si y solo si ningún dado lo supera: {R &le; k} = &#8898;<sub>i</sub> "
                "{D<sub>i</sub> &le; k}. Por la independencia de los dados,"
                "<div class='formula-box'>F(k) = (k&frasl;6)<sup>n</sup> &nbsp;&rArr;&nbsp; &#8473;(R = k) "
                "= F(k) &minus; F(k &minus; 1) = <sup>k<sup>n</sup> &minus; (k &minus; 1)<sup>n</sup></sup>"
                "&frasl;<sub>6<sup>n</sup></sub></div>"
                "Es el método estándar para la distribución de un máximo: calcular primero la función de "
                "distribución, que se factoriza, y luego restar."
            )

        if ui.accordion_step("P2_C", "(C) ¿Quién gana la primera comparación?"):
            ui.content(
                "El atacante gana si su máximo supera estrictamente al del defensor. Escribe la probabilidad "
                "condicionando al valor del máximo del atacante."
            )
            ui.spoiler(
                "Por la probabilidad total sobre los valores k del máximo del atacante R<sub>a</sub>, que "
                "es independiente del máximo del defensor R<sub>d</sub>:"
                "<div class='formula-box'>&#8473;(R<sub>a</sub> &gt; R<sub>d</sub>) = &sum;<sub>k=1</sub>"
                "<sup>6</sup> &#8473;(R<sub>a</sub> = k)&middot;F<sub>d</sub>(k &minus; 1)</div>"
                "Tres dados contra uno dan una ventaja clara al atacante; uno contra dos, una clara "
                "desventaja: por eso conviene atacar con muchos ejércitos."
            )

    with col_right:
        ui.right_panel()
        win = attacker_wins(a, d)
        ui.metrics([
            (f"&#8473;(gana el atacante) = {win:.4f}", "result-yes" if win > 0.5 else "result-no"),
            (f"&#8473;(máx. del atacante = 6) = {max_pmf(a)[1][-1]:.4f}", "metric-a"),
        ])
        ui.show(risk_chart(dark, a, d), key="fig_risk")
        ui.footer_bar(f"Con {a} {'dado' if a == 1 else 'dados'} contra {d}, el atacante gana la comparación de los dados más altos con "
                      f"probabilidad {win:.4f}; el defensor, con {1 - win:.4f} (incluye los empates).")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de dados n</u>")
        n = st.slider("Número de dados", 1, 6, v["dice"], 1, key=ui.wkey(PAGE, "dice"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Los tres dados de Galileo (hacia 1620)</b><br><br>"
            "Los jugadores florentinos apostaban a la suma de tres dados, y alguien de la corte del gran "
            "duque de Toscana había notado algo raro: el 10 salía más a menudo que el 9, aunque los dos "
            "números se pueden escribir como suma de tres caras de seis formas cada uno. Galileo Galilei, "
            "matemático de la corte, dedicó a la cuestión un breve escrito, <i>Sobre los descubrimientos de "
            "los dados</i>. ¿Quién tenía razón, la experiencia o la cuenta?"
        )

        if ui.accordion_step("P3_A", "(A) Las seis particiones"):
            ui.content(
                "Escribe las formas de obtener 9 y 10 como suma de tres números del 1 al 6 sin importar el "
                "orden. ¿Por qué el argumento <i>seis formas cada uno, luego igual de probables</i> es "
                "sospechoso?"
            )
            nine = " · ".join("+".join(map(str, t)) for t in partitions(3, 9))
            ten = " · ".join("+".join(map(str, t)) for t in partitions(3, 10))
            ui.spoiler(
                f"9: {nine}<br>10: {ten}<br><br>"
                "Seis cada uno. Pero las particiones no son igual de probables: 3+3+3 solo sale de una "
                "manera, mientras que 6+2+1 sale de seis maneras distintas según qué dado muestra cada cara. "
                "La regla de Laplace solo vale con casos equiprobables."
            )

        if ui.accordion_step("P3_B", "(B) Contar con orden"):
            ui.content(
                "Los casos equiprobables son los 216 resultados ordenados. Cuenta cuántos dan 9 y cuántos "
                "dan 10 sumando las permutaciones de cada partición."
            )
            ui.spoiler(
                f"<div class='formula-box'>&#8473;(S = 9) = {ordered_counts(3, 9)}/216 &nbsp;&nbsp; "
                f"&#8473;(S = 10) = {ordered_counts(3, 10)}/216</div>"
                "Una partición con tres números distintos aporta 3! = 6 órdenes; con dos iguales, 3; con "
                "los tres iguales, 1 (permutaciones con repetición). La diferencia es pequeña, pero los "
                "jugadores, que tiraban miles de veces, la habían detectado."
            )

        if ui.accordion_step("P3_C", "(C) Con más dados"):
            ui.content(
                "Sube el número de dados con el deslizador. ¿Qué forma va tomando la función de probabilidad "
                "de la suma? ¿Dónde está su máximo?"
            )
            ui.spoiler(
                "La suma de n dados toma los valores n, &hellip;, 6n y su función de probabilidad es "
                "simétrica respecto a 3.5n. Con un dado es plana; con dos, un triángulo; con más, se "
                "redondea en forma de campana. Es el primer aviso del teorema central del límite, que "
                "llegará en el último tema."
            )

    with col_right:
        ui.right_panel()
        ks, pmf = sum_pmf(n)
        lookup = dict(zip(ks, pmf))
        ui.metrics([
            (f"&#8473;(S = 9) = {lookup.get(9, 0.0):.4f}", "metric-c"),
            (f"&#8473;(S = 10) = {lookup.get(10, 0.0):.4f}", "metric-a"),
        ])
        ui.show(galileo_chart(dark, n), key="fig_galileo")
        ui.footer_bar(f"Con {n} {'dado' if n == 1 else 'dados'} hay 6<sup>{n}</sup> = {6 ** n} resultados ordenados igual de probables. "
                      "En naranja el 9, en rojo el 10.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los dados de Catán", "P1_A"),
        ("P2", "(II) La conquista del mundo", "P2_A"),
        ("P3", "(III) Los tres dados de Galileo", "P3_A"),
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
