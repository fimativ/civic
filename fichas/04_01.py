#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 1: las variables aleatorias continuas.

Los dos relojes de Lewis Carroll (un punto tiene probabilidad cero), la mesa
de billar de Bayes (la constante de normalización) y las llamadas de Erlang
(de la función de distribución a la densidad y del histograma a la densidad).
"""

from __future__ import annotations

from math import comb, cos, pi, sin

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Variables continuas"
SYMBOL = "∫f(x)dx"
PAGE = "04_01"

DIAL = 720   # minutos en una vuelta de la esfera


def initial_values():
    return {
        "stopped": ui.dint(260, 0, DIAL - 1, "stopped"),
        "eps": ui.dchoice(5, [1, 2, 5, 10, 15], "eps"),
        "n": ui.dint(3, 3, 12, "n"),
        "k": ui.dint(2, 1, 3, "k"),
        "mean": ui.dchoice(6, [3, 4, 5, 6, 8], "mean"),
        "a": ui.dchoice(3.0, [1.0, 2.0, 3.0, 4.0], "a"),
        "b": ui.dchoice(6.0, [6.0, 8.0, 10.0], "b"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "calls": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def billiard_constant(n: int, k: int) -> int:
    return (n + 1) * comb(n, k)


def billiard_density(xs, n: int, k: int):
    return billiard_constant(n, k) * xs ** k * (1 - xs) ** (n - k)


def billiard_cdf(x: float, n: int, k: int) -> float:
    return float(stats.beta.cdf(x, k + 1, n - k + 1))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def clock_svg(dark, stopped: int, eps: float) -> str:
    fg = "#e6e6e6" if dark else "#333333"
    cx, cy, r = 120, 120, 100

    def point(minutes, radius):
        ang = 2 * pi * minutes / DIAL - pi / 2
        return cx + radius * cos(ang), cy + radius * sin(ang)

    x0, y0 = point(stopped - eps, r)
    x1, y1 = point(stopped + eps, r)
    large = 1 if 2 * eps > DIAL / 2 else 0
    wedge = (f'<path d="M {cx} {cy} L {x0:.2f} {y0:.2f} A {r} {r} 0 {large} 1 {x1:.2f} {y1:.2f} Z" '
             f'fill="{ui.UBU_YELLOW}" fill-opacity="0.55"/>')
    ticks = "".join(
        f'<line x1="{point(h * 60, r - 10)[0]:.1f}" y1="{point(h * 60, r - 10)[1]:.1f}" '
        f'x2="{point(h * 60, r)[0]:.1f}" y2="{point(h * 60, r)[1]:.1f}" stroke="{fg}" stroke-width="3"/>'
        for h in range(12))
    hx, hy = point(stopped, 55)
    mx, my = point((stopped % 60) * 12, 85)
    return (f'<svg viewBox="0 0 240 240" width="100%" style="max-width:260px" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{fg}" stroke-width="3"/>{wedge}{ticks}'
            f'<line x1="{cx}" y1="{cy}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{ui.UBU_RED}" stroke-width="6" '
            f'stroke-linecap="round"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{mx:.1f}" y2="{my:.1f}" stroke="{fg}" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="{fg}"/></svg>')


def uniform_cdf_chart(dark, stopped: int, eps: float):
    xs = np.array([-60, 0, DIAL, DIAL + 60])
    ys = np.array([0, 0, 1, 1])
    p = ui.new_figure(dark, height=230, x_axis_label="minutos desde las 12:00", y_axis_label="F(x)",
                      x_range=(-60, DIAL + 60), y_range=(-0.05, 1.05))
    p.line(xs, ys, line_width=4, color=ui.BLUE_LINE)
    lo, hi = max(0, stopped - eps), min(DIAL, stopped + eps)
    p.varea(x=[lo, hi], y1=[0, 0], y2=[lo / DIAL, hi / DIAL], color=ui.UBU_YELLOW, alpha=0.6)
    p.add_layout(Span(location=stopped, dimension="height", line_color=ui.UBU_RED, line_width=2))
    return p


def billiard_chart(dark, n: int, k: int, a: float, b: float):
    xs = np.linspace(0, 1, 401)
    ys = billiard_density(xs, n, k)
    p = ui.new_figure(dark, height=300, x_axis_label="posición p de la bola blanca",
                      y_axis_label="densidad", x_range=(0, 1), y_range=(0, ys.max() * 1.15))
    mask = (xs >= a) & (xs <= b)
    p.varea(x=xs[mask], y1=0, y2=ys[mask], color=ui.UBU_YELLOW, alpha=0.6)
    p.line(xs, ys, line_width=4, color=ui.BLUE_LINE)
    return p


def calls_chart(dark, mean: float, sample, width: float, a: float, b: float):
    top = 6 * mean
    xs = np.linspace(0, top, 400)
    dens = np.exp(-xs / mean) / mean
    p = ui.new_figure(dark, height=300, x_axis_label="duración de la llamada (minutos)", y_axis_label="densidad",
                      x_range=(0, top), y_range=(0, 1.25 / mean))
    if sample is not None:
        edges = np.arange(0, top + width, width)
        hist, _ = np.histogram(sample, bins=edges)
        heights = hist / (len(sample) * width)
        p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=heights, fill_color=ui.UBU_YELLOW, fill_alpha=0.6,
               line_color=None, legend_label="histograma (frecuencia / anchura)")
    mask = (xs >= a) & (xs <= b)
    p.varea(x=xs[mask], y1=0, y2=dens[mask], color=ui.UBU_RED, alpha=0.25)
    p.line(xs, dens, line_width=4, color=ui.BLUE_LINE, legend_label="densidad f(x)")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se reparte la probabilidad en un continuo?</b>")
        ui.content(
            "Longitudes, pesos, tiempos y ángulos toman infinitos valores no numerables. Si cada valor tuviera "
            "una probabilidad positiva, la suma se dispararía; así que la probabilidad no se reparte entre "
            "puntos, sino entre intervalos. Una variable es <b>continua</b> si su función de distribución es "
            "la integral de una función de densidad f. <i>Escribe esa relación y las dos condiciones que debe "
            "cumplir f.</i>"
        )
        ui.formula_hidden("F(x) = &#8473;(X &le; x) = &int;<sub>&minus;&infin;</sub><sup>x</sup> f(u) du &nbsp;;&nbsp; "
                          "f &ge; 0 &nbsp;;&nbsp; &int;<sub>&minus;&infin;</sub><sup>&infin;</sup> f(u) du = 1")
        ui.content(
            "Por el teorema fundamental del cálculo, la densidad es la derivada de la función de distribución "
            "allí donde esta es derivable. Las sumas se convierten en integrales, y las probabilidades en "
            "áreas bajo la curva. <i>Escribe la probabilidad de un intervalo.</i>"
        )
        ui.formula_hidden("&#8473;(a &lt; X &le; b) = F(b) &minus; F(a) = &int;<sub>a</sub><sup>b</sup> f(u) du")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los dos relojes de Lewis Carroll</b><br>"
            "<i>¿Qué reloj es mejor, el que da la hora exacta dos veces al día o el que solo acierta una vez "
            "cada dos años?</i><br><br>"
            "<b>II. La mesa de billar de Bayes (1763)</b><br>"
            "<i>Lanza bolas sobre la mesa de Thomas Bayes y calcula la constante que convierte una curva en "
            "una densidad.</i><br><br>"
            "<b>III. Las llamadas de Erlang (1909)</b><br>"
            "<i>Mide con Agner Erlang la duración de las conferencias telefónicas y mira cómo un histograma "
            "se convierte en una densidad.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>hora del reloj parado</u> y el <u>margen &epsilon;</u>")
        c1, c2 = st.columns(2)
        stopped = c1.slider("Hora del reloj parado (minutos desde las 12)", 0, DIAL - 1, v["stopped"], 1,
                            key=ui.wkey(PAGE, "stopped"))
        eps = c2.slider("Margen ε (minutos)", 0.0, 60.0, float(v["eps"]), 0.5, key=ui.wkey(PAGE, "eps"))

        ui.planteamiento()
        ui.statement(
            "<b>Los dos relojes de Lewis Carroll</b><br><br>"
            "Charles Dodgson, el profesor de matemáticas de Oxford que firmaba como Lewis Carroll, planteó "
            "este acertijo: ¿qué reloj es mejor, uno que da la hora exacta una vez cada dos años o uno que la "
            "da dos veces al día? El segundo, responde todo el mundo. Pero el segundo es un reloj parado, y el "
            "primero uno que atrasa un minuto al día. Miramos un reloj parado en un instante elegido al azar: "
            "la hora real X es uniforme en una vuelta de la esfera, 720 minutos."
        )

        if ui.accordion_step("P1_A", "(A) Un instante no pesa"):
            ui.content(
                "¿Cuál es la probabilidad de que, al mirarlo, el reloj parado marque <i>exactamente</i> la hora "
                "real? Calcula primero la de que esté a menos de &epsilon; minutos y haz tender &epsilon; a cero."
            )
            ui.spoiler(
                "La densidad es constante, f = 1/720 en [0, 720). La probabilidad de estar a menos de &epsilon; "
                "es el área de un rectángulo de base 2&epsilon;:"
                "<div class='formula-box'>&#8473;(|X &minus; x<sub>0</sub>| &le; &epsilon;) = <sup>2&epsilon;</sup>"
                "&frasl;<sub>720</sub> &xrarr; 0 &nbsp; cuando &epsilon; &rarr; 0</div>"
                "En una variable continua, &#8473;(X = x) = 0 para todo x: los puntos no tienen masa, aunque "
                "alguno de ellos ocurra seguro. Probabilidad cero no es lo mismo que imposible."
            )

        if ui.accordion_step("P1_B", "(B) La función de distribución"):
            ui.content(
                "Escribe la función de distribución de la hora X. ¿Por qué da igual escribir &#8473;(a &lt; X "
                "&lt; b) que &#8473;(a &le; X &le; b)?"
            )
            ui.spoiler(
                "<div class='formula-box'>F(x) = 0 si x &lt; 0; &nbsp; F(x) = x/720 si 0 &le; x &lt; 720; "
                "&nbsp; F(x) = 1 si x &ge; 720</div>"
                "Es continua y crece linealmente. Como los extremos tienen probabilidad cero, añadirlos o "
                "quitarlos no cambia nada: todas las versiones del intervalo valen F(b) &minus; F(a)."
            )

        if ui.accordion_step("P1_C", "(C) El acertijo"):
            ui.content(
                "El reloj que atrasa un minuto al día tiene que acumular 720 minutos para volver a coincidir: "
                "¿cada cuánto acierta? Si los miras a los dos en un instante al azar, ¿cuál tiene más "
                "probabilidad de estar a menos de un minuto de la hora real?"
            )
            ui.spoiler(
                "El que atrasa vuelve a acertar cada 720 días, casi dos años; el parado acierta dos veces al "
                "día. Pero acertar en un instante tiene probabilidad cero en los dos casos. Lo que cuenta es "
                "estar cerca, y ahí empatan: el parado está a menos de un minuto con probabilidad 2/720, y el que "
                "atrasa también, porque su error crece un minuto al día y solo pasa dos días de cada 720 a menos de "
                "un minuto. La diferencia está en otra parte: el error del que atrasa es predecible y cambia "
                "despacio. Carroll jugaba con la diferencia entre contar instantes y medir intervalos."
            )

    with col_right:
        ui.right_panel()
        prob = min(1.0, 2 * eps / DIAL)
        hours, minutes = divmod(stopped, 60)
        ui.metrics([(f"Reloj parado en las {hours or 12}:{minutes:02d}", "metric-c"),
                    (f"&#8473;(a menos de {eps:g} min) = {prob:.4f}", "metric-a")])
        ui.svg(clock_svg(dark, stopped, eps))
        ui.show(uniform_cdf_chart(dark, stopped, eps), key="fig_clock_cdf")
        ui.footer_bar("La cuña amarilla es el conjunto de horas reales a menos de &epsilon; del reloj parado; su "
                      "probabilidad es el incremento de F en ese tramo. Con &epsilon; = 0 la cuña desaparece.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>bolas lanzadas n</u>, las que caen a la <u>izquierda k</u> y el <u>intervalo</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Bolas lanzadas n", 1, 20, v["n"], 1, key=ui.wkey(PAGE, "n"))
        k = c2.slider("A la izquierda de la blanca k", 0, n, min(v["k"], n), 1, key=ui.wkey(PAGE, f"k{n}"))
        a, b = st.slider("Intervalo [a, b]", 0.0, 1.0, (0.50, 0.90), 0.01, key="billiard_ab")

        ui.planteamiento()
        ui.statement(
            "<b>La mesa de billar de Bayes (1763)</b><br><br>"
            "En su ensayo póstumo, Thomas Bayes imaginó una mesa de billar de longitud 1. Se lanza una bola "
            "blanca, que se detiene en una posición p uniforme. Después se lanzan otras n bolas y se anota "
            "cuántas, k, quedan a la izquierda de la blanca, sin mirar dónde está esta. Sabiendo k, la "
            "posición de la blanca tiene una densidad proporcional a p<sup>k</sup>(1 &minus; p)<sup>n&minus;k</sup>. "
            f"En nuestra mesa, n = {v['n']} y k = {min(v['k'], v['n'])}."
        )

        if ui.accordion_step("P2_A", "(A) La constante de normalización"):
            ui.content(
                "Con n = 3 y k = 2 la densidad es f(x) = c&middot;x<sup>2</sup>(1 &minus; x) en [0, 1]. ¿Cuánto "
                "debe valer c para que f sea una densidad? ¿Y en general?"
            )
            ui.spoiler(
                "Debe integrar 1: c&middot;&int;<sub>0</sub><sup>1</sup> (x<sup>2</sup> &minus; x<sup>3</sup>) dx = "
                "c(1/3 &minus; 1/4) = c/12 = 1, luego c = 12. En general la integral es la función beta de Euler:"
                "<div class='formula-box'>c = <sup>1</sup>&frasl;<sub>B(k + 1, n &minus; k + 1)</sub> = "
                "(n + 1)&middot;( <sup>n</sup>&frasl;<sub>k</sub> )</div>"
                "Es la densidad de una beta de parámetros k + 1 y n &minus; k + 1."
            )

        if ui.accordion_step("P2_B", "(B) La función de distribución"):
            ui.content(
                "Para n = 3 y k = 2, integra la densidad para obtener F(x) en (0, 1). Con ella, calcula la "
                "probabilidad de que la blanca esté en la mitad derecha de la mesa."
            )
            ui.spoiler(
                "<div class='formula-box'>F(x) = &int;<sub>0</sub><sup>x</sup> 12u<sup>2</sup>(1 &minus; u) du = "
                "4x<sup>3</sup> &minus; 3x<sup>4</sup></div>"
                "&#8473;(p &gt; 1/2) = 1 &minus; F(1/2) = 1 &minus; 4/8 + 3/16 = 11/16. Mueve el intervalo de la "
                "derecha a [0.5, 1] para comprobarlo."
            )

        if ui.accordion_step("P2_C", "(C) ¿Dónde está la bola blanca?"):
            ui.content(
                "Busca el máximo de la densidad y calcula su media. ¿Por qué no coinciden? ¿Qué pasa con la "
                "curva al lanzar muchas bolas con la misma proporción k/n?"
            )
            ui.spoiler(
                "El máximo está en k/n, la proporción observada; la media es (k + 1)/(n + 2), un poco más cerca "
                "del centro. Con muchas bolas la curva se estrecha alrededor de k/n: cuanta más información, "
                "menos incertidumbre sobre p. La media (k + 1)/(n + 2) reaparecerá con Laplace como la regla de "
                "sucesión."
            )

    with col_right:
        ui.right_panel()
        a, b = min(a, b), max(a, b)
        prob = billiard_cdf(b, n, k) - billiard_cdf(a, n, k)
        ui.metrics([(f"c = {billiard_constant(n, k)}", "metric-c"),
                    (f"&#8473;({a:.2f} &le; p &le; {b:.2f}) = {prob:.4f}", "metric-a")])
        ui.show(billiard_chart(dark, n, k, a, b), key="fig_billiard")
        ui.footer_bar(f"Densidad c&middot;p<sup>{k}</sup>(1 &minus; p)<sup>{n - k}</sup>: moda {k / n:.3f}, media "
                      f"{(k + 1) / (n + 2):.3f}. El área amarilla es la probabilidad del intervalo.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>duración media</u>, el <u>intervalo</u> y la <u>anchura de las barras</u>")
        mean = st.select_slider("Duración media (minutos)", options=[2, 3, 4, 5, 6, 8, 10], value=v["mean"],
                                key=ui.wkey(PAGE, "mean"))
        a, b = st.slider("Intervalo [a, b] (minutos)", 0.0, 6.0 * mean, (min(v["a"], 6.0 * mean),
                         min(v["b"], 6.0 * mean)), 0.5, key=ui.wkey(PAGE, f"ab{mean}"))
        width = st.select_slider("Anchura de las barras (minutos)", options=[4.0, 2.0, 1.0, 0.5, 0.25],
                                 value=1.0, key="calls_width")

        ui.planteamiento()
        ui.statement(
            "<b>Las llamadas de Erlang (1909)</b><br><br>"
            "Agner Krarup Erlang, ingeniero de la compañía telefónica de Copenhague, quería saber cuántas "
            "líneas hacían falta para que casi nadie encontrara la centralita ocupada. Para ello necesitaba "
            "modelar la duración de las conferencias. Supongamos que una llamada dura X minutos, con función "
            f"de distribución F(x) = 1 &minus; e<sup>&minus;x/{v['mean']}</sup> para x &ge; 0."
        )

        if ui.accordion_step("P3_A", "(A) De la distribución a la densidad"):
            ui.content(
                "Deriva F para obtener la densidad. Comprueba que es no negativa y que integra 1. ¿Cuánto vale "
                "&#8473;(X &gt; x)?"
            )
            ui.spoiler(
                f"<div class='formula-box'>f(x) = F'(x) = <sup>1</sup>&frasl;<sub>{v['mean']}</sub> "
                f"e<sup>&minus;x/{v['mean']}</sup>, &nbsp; x &ge; 0</div>"
                f"Es positiva e integra [&minus;e<sup>&minus;x/{v['mean']}</sup>]<sub>0</sub><sup>&infin;</sup> = 1. "
                f"La cola es &#8473;(X &gt; x) = 1 &minus; F(x) = e<sup>&minus;x/{v['mean']}</sup>: la "
                "distribución exponencial, que tendrá su propia ficha."
            )

        if ui.accordion_step("P3_B", "(B) Probabilidades como áreas"):
            ui.content(
                f"Calcula la probabilidad de que una llamada dure entre {v['a']:g} y {v['b']:g} minutos de dos formas: "
                "integrando la densidad y restando valores de F. Compara con el área roja de la derecha."
            )
            ui.spoiler(
                f"<div class='formula-box'>&#8473;({v['a']:g} &le; X &le; {v['b']:g}) = F({v['b']:g}) &minus; "
                f"F({v['a']:g}) = e<sup>&minus;{v['a']:g}/{v['mean']}</sup> &minus; e<sup>&minus;{v['b']:g}/{v['mean']}</sup> "
                f"= {np.exp(-v['a'] / v['mean']) - np.exp(-v['b'] / v['mean']):.4f}</div>"
                "Las dos cuentas coinciden por el teorema fundamental del cálculo: la integral de la densidad "
                "entre a y b es el incremento de su primitiva."
            )

        if ui.accordion_step("P3_C", "(C) Del histograma a la densidad"):
            ui.content(
                "Simula llamadas y estrecha las barras del histograma. ¿Por qué se divide la frecuencia de "
                "cada barra entre su anchura? ¿Qué pasa con pocas llamadas y barras muy estrechas?"
            )
            ui.spoiler(
                "La proporción de llamadas en una barra estima la probabilidad del intervalo, que es "
                "aproximadamente f(x) por la anchura; dividiendo por la anchura se estima la densidad. Con "
                "muchas llamadas y barras cada vez más estrechas, el borde del histograma tiende a la curva "
                "f. Si hay pocas llamadas, las barras estrechas quedan casi vacías y el histograma se vuelve "
                "ruidoso: estrechar solo compensa si crece también el número de datos."
            )

        n_calls = st.select_slider("Llamadas simuladas", options=[100, 1000, 10000, 100000], value=1000,
                                   key="calls_n")
        if st.button("Simular llamadas", key="calls_play", width="stretch", type="primary"):
            st.session_state["calls"] = (mean, np.random.default_rng().exponential(mean, n_calls))

    with col_right:
        ui.right_panel()
        a, b = min(a, b), max(a, b)
        prob = float(np.exp(-a / mean) - np.exp(-b / mean))
        sim = st.session_state.get("calls")
        sample = sim[1] if sim and sim[0] == mean else None
        items = [(f"&#8473;({a:g} &le; X &le; {b:g}) = {prob:.4f}", "metric-a")]
        if sample is not None:
            items.append((f"Frecuencia simulada: {((sample >= a) & (sample <= b)).mean():.4f}", "metric-c"))
        ui.metrics(items)
        ui.show(calls_chart(dark, mean, sample, width, a, b), key="fig_calls")
        ui.footer_bar("El área roja bajo la densidad es la probabilidad del intervalo. Simula llamadas para "
                      "superponer el histograma.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los dos relojes de Carroll", "P1_A"),
        ("P2", "(II) La mesa de billar de Bayes", "P2_A"),
        ("P3", "(III) Las llamadas de Erlang", "P3_A"),
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
