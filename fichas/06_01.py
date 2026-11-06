#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 1: la convergencia en distribución.

Las crecidas de Gumbel (el máximo normalizado converge a una distribución
límite), la dicotomía de Zenón (por qué se excluyen los puntos de discontinuidad)
y unas sumas que no se comportan (lo que la convergencia débil no garantiza).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Convergencia en distribución"
SYMBOL = "→ᵈ"
PAGE = "06_01"


def initial_values():
    return {
        "days": ui.dchoice(30, [5, 10, 30, 90, 365], "days"),
        "period": ui.dchoice(100, [10, 50, 100, 500], "period"),
        "n_zeno": ui.dint(4, 2, 10, "n_zeno"),
        "n_sum": ui.dint(5, 1, 20, "n_sum"),
        "seed": int(ui.r("gumbel") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "gumbel_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def max_cdf(x, n: int):
    """ℙ(M_n − ln n ≤ x) para el máximo de n exponenciales de media 1."""
    t = np.exp(-x) / n
    return np.where(t < 1, (1 - np.minimum(t, 1)) ** n, 0.0)


def gumbel_cdf(x):
    return np.exp(-np.exp(-x))


def return_level(period: float) -> float:
    return float(-np.log(-np.log(1 - 1 / period)))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def gumbel_chart(dark, n: int, sample, level: float):
    xs = np.linspace(-3, 7, 400)
    p = ui.new_figure(dark, height=300, x_axis_label="máximo anual − ln n", y_axis_label="función de distribución",
                      x_range=(-3, 7), y_range=(0, 1.02))
    if sample is not None:
        srt = np.sort(sample)
        p.line(srt, np.arange(1, len(srt) + 1) / len(srt), line_width=2, color=ui.UBU_YELLOW,
               legend_label="años simulados")
    p.line(xs, max_cdf(xs, n), line_width=4, color=ui.BLUE_LINE, legend_label=f"exacta, n = {n} días")
    p.line(xs, gumbel_cdf(xs), line_width=3, color=ui.UBU_RED, line_dash="dashed", legend_label="Gumbel exp(−e⁻ˣ)")
    p.add_layout(Span(location=level, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    return ui.style_legend(p, dark, "bottom_right")


def zeno_chart(dark, n: int):
    p = ui.new_figure(dark, height=300, x_axis_label="x", y_axis_label="F(x)", x_range=(-0.6, 1.2), y_range=(-0.05, 1.1))
    palette = [ui.GREY_LINE, ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE]
    for i, k in enumerate(range(max(1, n - 4), n + 1)):
        point = 1 / k
        p.line([-0.6, point], [0, 0], line_width=2.5, color=palette[i % len(palette)], alpha=0.8)
        p.line([point, 1.2], [1, 1], line_width=2.5, color=palette[i % len(palette)], alpha=0.8,
               legend_label=f"F de X_{k} = 1/{k}")
        p.scatter([point], [1], size=9, color=palette[i % len(palette)])
        p.scatter([point], [0], size=9, fill_color="white", line_color=palette[i % len(palette)])
    p.line([-0.6, 0], [0, 0], line_width=4, color=ui.UBU_RED, line_dash="dashed")
    p.line([0, 1.2], [1, 1], line_width=4, color=ui.UBU_RED, line_dash="dashed", legend_label="límite: X = 0")
    p.scatter([0], [1], size=12, color=ui.UBU_RED)
    return ui.style_legend(p, dark, "center_right")


def sums_chart(dark, n: int, seed: int):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(20000)
    y = (-1) ** n * z
    s = z + y
    edges = np.linspace(-6, 6, 61)
    p = ui.new_figure(dark, height=300, x_axis_label=f"X_{n} + Y_{n}", y_axis_label="densidad", x_range=(-6, 6),
                      y_range=(0, 1.2))
    hist, _ = np.histogram(s, bins=edges)
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(s) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.7, line_color=None, legend_label=f"n = {n}")
    xs = np.linspace(-6, 6, 300)
    p.line(xs, np.exp(-xs ** 2 / 4) / np.sqrt(4 * np.pi), line_width=3, color=ui.RED_LINE, line_dash="dashed",
           legend_label="N(0, √2), lo que se esperaría")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué significa que una sucesión de variables aleatorias converja?</b>")
        ui.content(
            "Muchos resultados de la probabilidad hablan de lo que ocurre cuando el número de variables crece: la "
            "media de muchas observaciones, el máximo de muchos datos, la binomial con muchos ensayos. Pero las "
            "variables aleatorias son funciones, y hay varias formas de decir que se acercan a un límite. La más "
            "débil solo mira sus distribuciones. <i>Escribe la definición de convergencia en distribución.</i>"
        )
        ui.formula_hidden("X<sub>n</sub> &rarr; X en distribución &nbsp;&hArr;&nbsp; F<sub>n</sub>(x) &rarr; F(x) &nbsp; "
                          "para todo x en el que F es continua")
        ui.content(
            "Las X<sub>n</sub> ni siquiera tienen que estar definidas sobre el mismo espacio: la convergencia solo "
            "compara probabilidades. Ya la usaste sin nombrarla cuando la binomial B(n, &lambda;/n) se convertía en "
            "una Poisson. El límite, si existe, es único."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las crecidas de Gumbel (1941)</b><br>"
            "<i>Calcula con Emil Gumbel la crecida de los cien años a partir del máximo de muchos días.</i><br><br>"
            "<b>II. La dicotomía de Zenón</b><br>"
            "<i>Una flecha que se acerca a su blanco y una definición que tiene que ser cuidadosa.</i><br><br>"
            "<b>III. Sumas que no se comportan</b><br>"
            "<i>Dos sucesiones que convergen en distribución cuya suma no converge a nada.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de días n</u> y el <u>periodo de retorno</u>")
        c1, c2 = st.columns(2)
        n = c1.select_slider("Días por año n", options=[1, 2, 5, 10, 30, 90, 365], value=v["days"],
                             key=ui.wkey(PAGE, "days"))
        period = c2.select_slider("Periodo de retorno (años)", options=[5, 10, 50, 100, 500, 1000], value=v["period"],
                                  key=ui.wkey(PAGE, "period"))

        ui.planteamiento()
        ui.statement(
            "<b>Las crecidas de Gumbel (1941)</b><br><br>"
            "Emil Gumbel, matemático alemán exiliado por su oposición al nazismo, aplicó a los ríos una teoría que "
            "Ronald Fisher y Leonard Tippett habían desarrollado en 1928: la de los valores extremos. Lo que importa "
            "para construir un dique no es el caudal medio, sino el máximo del año. Supongamos que el caudal de cada "
            "día, medido en unidades del caudal medio, es exponencial de media 1 e independiente de los demás. ¿Cómo "
            "se distribuye el máximo de n días cuando n es grande?"
        )

        if ui.accordion_step("P1_A", "(A) La distribución del máximo"):
            ui.content(
                "Calcula &#8473;(M<sub>n</sub> &le; x) para el máximo de n exponenciales independientes, como hiciste con los "
                "dados del Risk. ¿Hacia dónde se va M<sub>n</sub> cuando n crece?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(M<sub>n</sub> &le; x) = (1 &minus; e<sup>&minus;x</sup>)<sup>n</sup></div>"
                "Para cada x fijo, tiende a 0: el máximo crece sin límite, y M<sub>n</sub> no converge en distribución a "
                "nada. Para obtener un límite hay que centrar, igual que para hablar de la media de muchos datos hay "
                "que comparar con algo."
            )

        if ui.accordion_step("P1_B", "(B) Centrar con ln n"):
            ui.content(
                "Calcula &#8473;(M<sub>n</sub> &minus; ln n &le; x) y su límite cuando n &rarr; &infin;. ¿Qué límite clásico del "
                "cálculo aparece?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(M<sub>n</sub> &minus; ln n &le; x) = (1 &minus; <sup>e<sup>&minus;x</sup></sup>&frasl;<sub>n</sub>)"
                "<sup>n</sup> &xrarr; e<sup>&minus;e<sup>&minus;x</sup></sup></div>"
                "El mismo límite (1 &minus; a/n)<sup>n</sup> &rarr; e<sup>&minus;a</sup> que daba la Poisson. La función "
                "exp(&minus;e<sup>&minus;x</sup>) es la distribución de Gumbel: M<sub>n</sub> &minus; ln n converge en distribución "
                "a ella. Con un mes ya se confunde con la exacta."
            )

        if ui.accordion_step("P1_C", "(C) La crecida de los cien años"):
            ui.content(
                "La crecida de T años es el nivel que el máximo anual supera con probabilidad 1/T. Calcúlalo con la "
                "distribución de Gumbel. ¿Cuánto mayor es la de quinientos años que la de cincuenta?"
            )
            ui.spoiler(
                "<div class='formula-box'>e<sup>&minus;e<sup>&minus;x<sub>T</sub></sup></sup> = 1 &minus; 1/T &nbsp;&rArr;&nbsp; "
                "x<sub>T</sub> = &minus;ln(&minus;ln(1 &minus; 1/T)) &asymp; ln T</div>"
                "El nivel crece como el logaritmo del periodo: multiplicar el periodo por diez solo añade ln 10 "
                "&asymp; 2.3 unidades al caudal. Por eso los diques se diseñan para periodos de cientos o miles de "
                "años: el coste de prevenir lo rarísimo no es tan grande."
            )

        if st.button("Simular 3000 años", key="gumbel_play", width="stretch", type="primary"):
            rng = np.random.default_rng()
            st.session_state["gumbel_sim"] = (n, rng.exponential(1, (3000, n)).max(axis=1) - np.log(n))

    with col_right:
        ui.right_panel()
        level = return_level(period)
        sim = st.session_state.get("gumbel_sim")
        sample = sim[1] if sim and sim[0] == n else None
        ui.metrics([(f"Crecida de {period} años: ln n + {level:.2f}", "metric-a"),
                    (f"= {np.log(n) + level:.2f} veces el caudal medio", "metric-c")])
        ui.show(gumbel_chart(dark, n, sample, level), key="fig_gumbel")
        gap = float(np.abs(max_cdf(np.linspace(-3, 7, 400), n) - gumbel_cdf(np.linspace(-3, 7, 400))).max())
        ui.footer_bar(f"Mayor distancia entre la distribución exacta y la de Gumbel: {gap:.4f}. La línea punteada marca el "
                      f"nivel de la crecida de {period} años.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("avanza la <u>flecha</u> con n")
        n = st.slider("n", 1, 40, v["n_zeno"], 1, key=ui.wkey(PAGE, "n_zeno"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La dicotomía de Zenón</b><br><br>"
            "Zenón de Elea sostenía, en su paradoja de la dicotomía, que una flecha nunca llega al blanco: primero debe recorrer la mitad, después la "
            "mitad de lo que falta, y así sin fin. Démosle una versión probabilística sin azar: la variable X<sub>n</sub> "
            "vale 1/n con probabilidad 1. La sucesión de números 1/n tiende a 0, así que cualquier definición razonable "
            "de convergencia debería decir que X<sub>n</sub> converge a la constante 0. ¿Lo dice la definición con "
            "funciones de distribución?"
        )

        if ui.accordion_step("P2_A", "(A) Las funciones de distribución"):
            ui.content("Escribe F<sub>n</sub>, la función de distribución de X<sub>n</sub>, y F, la de la constante 0.")
            ui.spoiler(
                "F<sub>n</sub>(x) = 0 si x &lt; 1/n y 1 si x &ge; 1/n: un escalón en 1/n. F(x) = 0 si x &lt; 0 y 1 si x &ge; 0: "
                "un escalón en 0. Son las escaleras de la derecha."
            )

        if ui.accordion_step("P2_B", "(B) El punto conflictivo"):
            ui.content(
                "¿Converge F<sub>n</sub>(x) a F(x) para cada x? Estudia por separado x &lt; 0, x &gt; 0 y x = 0."
            )
            ui.spoiler(
                "Si x &lt; 0, todas valen 0. Si x &gt; 0, a partir de un n tenemos 1/n &le; x y F<sub>n</sub>(x) = 1 = F(x). Pero "
                "en x = 0, F<sub>n</sub>(0) = 0 para todo n, mientras que F(0) = 1. Si se exigiera convergencia en todos los "
                "puntos, la flecha de Zenón no convergería a su blanco. Por eso la definición solo pide convergencia "
                "donde F es continua, y 0 es justo el punto de salto de F."
            )

        if ui.accordion_step("P2_C", "(C) Probabilidades de intervalos"):
            ui.content(
                "¿Converge &#8473;(X<sub>n</sub> &le; 0) a &#8473;(X &le; 0)? ¿Y &#8473;(X<sub>n</sub> &isin; [&minus;1, 1])? ¿Qué diferencia "
                "hay entre los dos intervalos?"
            )
            ui.spoiler(
                "La primera vale siempre 0 y no converge a 1. La segunda vale siempre 1 = &#8473;(X &isin; [&minus;1, 1]). La "
                "convergencia en distribución garantiza la de las probabilidades de los intervalos cuya frontera no "
                "tiene probabilidad para el límite: {X &le; 0} tiene frontera {0}, que se lleva toda la masa de X. Si el "
                "límite es continuo, el problema desaparece."
            )

    with col_right:
        ui.right_panel()
        ui.metrics([(f"F<sub>{n}</sub>(0) = 0", "result-no"), ("F(0) = 1", "metric-a"),
                    (f"F<sub>{n}</sub>(0.1) = {1 if 1 / n <= 0.1 else 0}", "metric-c")])
        ui.show(zeno_chart(dark, n), key="fig_zeno")
        ui.footer_bar("Escalones de las últimas cinco X<sub>n</sub>, que se acercan al de la constante 0 (en rojo). En "
                      "cualquier x &ne; 0 los escalones acaban coincidiendo; en x = 0, nunca.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia <u>n</u>")
        n = st.slider("n", 1, 30, v["n_sum"], 1, key=ui.wkey(PAGE, "n_sum"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Sumas que no se comportan</b><br><br>"
            "Sea Z una normal típica. Definimos X<sub>n</sub> = Z para todo n, e Y<sub>n</sub> = (&minus;1)<sup>n</sup>Z: alterna "
            "entre Z y &minus;Z. Por la simetría de la normal, todas las X<sub>n</sub> y todas las Y<sub>n</sub> son normales "
            "típicas. Si en el límite tomamos X e Y normales típicas independientes, X + Y sería N(0, &radic;2). ¿Se "
            "parece X<sub>n</sub> + Y<sub>n</sub> a eso?"
        )

        if ui.accordion_step("P3_A", "(A) Cada sucesión converge"):
            ui.content("¿Converge Y<sub>n</sub> en distribución? ¿A qué?")
            ui.spoiler(
                "Sí, trivialmente: todas tienen la misma función de distribución &Phi;, así que F<sub>n</sub> = &Phi; para todo "
                "n y converge a &Phi;. Igual X<sub>n</sub>. La convergencia en distribución no mira cómo se relacionan "
                "las variables entre sí, solo la distribución de cada una."
            )

        if ui.accordion_step("P3_B", "(B) La suma no converge"):
            ui.content("Calcula X<sub>n</sub> + Y<sub>n</sub> para n par y para n impar. ¿Converge en distribución?")
            ui.spoiler(
                "Para n par, X<sub>n</sub> + Y<sub>n</sub> = 2Z, una N(0, 2); para n impar, X<sub>n</sub> + Y<sub>n</sub> = 0. La "
                "sucesión salta entre dos distribuciones distintas y no converge a nada. Saber que cada sumando "
                "converge en distribución no dice nada de la suma, porque la distribución de la suma depende de la "
                "conjunta, y la convergencia débil la ignora."
            )

        if ui.accordion_step("P3_C", "(C) Cuándo sí se puede sumar"):
            ui.content(
                "Si Y<sub>n</sub> converge a una <i>constante</i> c, ¿se puede afirmar que X<sub>n</sub> + Y<sub>n</sub> converge a "
                "X + c? ¿Por qué ese caso es especial?"
            )
            ui.spoiler(
                "Sí: es el teorema de Slutsky, que verás en la ficha siguiente. Una constante no tiene dependencia "
                "con nada, así que la conjunta queda determinada. Sumar una constante, o multiplicar por ella, siempre "
                "conserva la convergencia en distribución; sumar otra sucesión aleatoria, en general, no."
            )

    with col_right:
        ui.right_panel()
        ui.metrics([(f"n = {n}: X<sub>n</sub> + Y<sub>n</sub> = {'2Z' if n % 2 == 0 else '0'}", "metric-a"),
                    (f"Varianza: {'4' if n % 2 == 0 else '0'}", "metric-c")])
        ui.show(sums_chart(dark, n, v["seed"]), key="fig_sums")
        ui.footer_bar("Con n impar la suma es un pico en 0; con n par, una normal ancha. Ninguna de las dos es la curva "
                      "discontinua N(0, √2) que sugeriría el límite de cada sumando.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Las crecidas de Gumbel", "P1_A"),
        ("P2", "(II) La dicotomía de Zenón", "P2_A"),
        ("P3", "(III) Sumas que no se comportan", "P3_A"),
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
