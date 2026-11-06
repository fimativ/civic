#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 3: sumas de variables independientes y reproductividad.

Los goles de un partido (Poisson se reproduce al sumar), la medida del metro
(errores normales que se acumulan como una raíz cuadrada) y la suma de
uniformes de Irwin y Hall (una familia que no se reproduce).
"""

from __future__ import annotations

from math import comb, factorial, floor

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Sumas y reproductividad"
SYMBOL = "X + Y"
PAGE = "05_03"


def initial_values():
    return {
        "home": ui.dfloat(1.5, 0.8, 2.4, "home", 1),
        "away": ui.dfloat(1.1, 0.5, 1.8, "away", 1),
        "segments": ui.dint(90, 30, 150, "segments"),
        "sigma": ui.dchoice(0.5, [0.2, 0.3, 0.5, 0.8, 1.0], "sigma"),
        "n": ui.dint(2, 2, 6, "n"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "uniform_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def score_grid(l1: float, l2: float, top: int = 7):
    k = np.arange(top + 1)
    return np.outer(stats.poisson.pmf(k, l1), stats.poisson.pmf(k, l2))


def outcome_probs(l1: float, l2: float):
    grid = score_grid(l1, l2, 25)
    home = float(np.tril(grid, -1).sum())
    draw = float(np.trace(grid))
    return home, draw, 1 - home - draw


def irwin_hall_pdf(x, n: int):
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    for i, xv in enumerate(x):
        if 0 <= xv <= n:
            out[i] = sum((-1) ** k * comb(n, k) * (xv - k) ** (n - 1) for k in range(floor(xv) + 1)) / factorial(n - 1)
    return out


# =============================================================================
# 2. FIGURAS
# =============================================================================

def grid_chart(dark, l1: float, l2: float):
    top = 6
    grid = score_grid(l1, l2, top)
    xs, ys, colours, alphas, texts = [], [], [], [], []
    peak = grid.max()
    for i in range(top + 1):
        for j in range(top + 1):
            xs.append(j)
            ys.append(i)
            colours.append(ui.GREEN_LINE if i > j else (ui.GREY_LINE if i == j else ui.RED_LINE))
            alphas.append(0.15 + 0.85 * grid[i, j] / peak)
            texts.append(f"{100 * grid[i, j]:.1f}")
    p = ui.new_figure(dark, height=320, x_range=(-0.5, top + 0.5), y_range=(-0.5, top + 0.5), match_aspect=True,
                      x_axis_label="goles del visitante", y_axis_label="goles del local")
    p.rect(x=xs, y=ys, width=0.94, height=0.94, fill_color=colours, fill_alpha=alphas, line_color=None)
    p.text(x=xs, y=ys, text=texts, text_align="center", text_baseline="middle", text_font_size="11px",
           text_color="#ffffff" if dark else "#1a1a1a")
    p.xaxis.ticker = list(range(top + 1))
    p.yaxis.ticker = list(range(top + 1))
    p.grid.visible = False
    return p


def total_chart(dark, l1: float, l2: float):
    k = np.arange(0, 11)
    grid = score_grid(l1, l2, 25)
    conv = np.array([sum(grid[i, t - i] for i in range(t + 1)) for t in k])
    p = ui.new_figure(dark, height=230, x_axis_label="goles totales", y_axis_label="probabilidad", x_range=(-0.6, 10.6))
    p.vbar(x=k, top=conv, width=0.7, color=ui.BLUE_LINE, alpha=0.75, legend_label="suma de las diagonales")
    p.scatter(k, stats.poisson.pmf(k, l1 + l2), size=11, marker="diamond", color=ui.UBU_RED,
              legend_label=f"Poisson({l1 + l2:.1f})")
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


def meridian_chart(dark, n: int, sigma: float):
    sd = sigma * np.sqrt(n)
    top = max(4 * sd, 4 * sigma)
    xs = np.linspace(-top, top, 400)
    p = ui.new_figure(dark, height=300, x_axis_label="error total (toesas)", y_axis_label="densidad", x_range=(-top, top))
    p.line(xs, stats.norm.pdf(xs, 0, sigma), line_width=3, color=ui.GREY_LINE, line_dash="dashed",
           legend_label=f"un tramo: N(0, {sigma:g})")
    p.line(xs, stats.norm.pdf(xs, 0, sd), line_width=4, color=ui.BLUE_LINE, legend_label=f"{n} tramos: N(0, {sd:.2f})")
    p.add_layout(Span(location=n * sigma / 10, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return ui.style_legend(p, dark, "top_right")


def irwin_chart(dark, n: int, sample):
    xs = np.linspace(0, n, 400)
    p = ui.new_figure(dark, height=300, x_axis_label=f"U₁ + … + U{n}".replace(f"U{n}", "Uₙ"), y_axis_label="densidad",
                      x_range=(0, n))
    if sample is not None:
        edges = np.linspace(0, n, 41)
        hist, _ = np.histogram(sample, bins=edges)
        p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(sample) * (edges[1] - edges[0])),
               fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None, legend_label="simulación")
    p.line(xs, irwin_hall_pdf(xs, n), line_width=4, color=ui.BLUE_LINE, legend_label="densidad de Irwin y Hall")
    p.line(xs, stats.norm.pdf(xs, n / 2, np.sqrt(n / 12)), line_width=2, color=ui.UBU_RED, line_dash="dashed",
           legend_label="normal con la misma media y varianza")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué distribución tiene una suma?</b>")
        ui.content(
            "La esperanza de una suma es siempre la suma de las esperanzas, y si los sumandos son independientes "
            "también se suman las varianzas. Para conocer la distribución entera hay una herramienta más potente: "
            "la función generatriz de momentos. <i>¿Cuál es la de una suma de variables independientes?</i>"
        )
        ui.formula_hidden("G<sub>X+Y</sub>(t) = &#120124;[e<sup>t(X+Y)</sup>] = &#120124;[e<sup>tX</sup>]&#120124;[e<sup>tY</sup>] = "
                          "G<sub>X</sub>(t)&middot;G<sub>Y</sub>(t)")
        ui.content(
            "Como la función generatriz, si existe, caracteriza la distribución, basta reconocer el producto. Una "
            "familia es <b>reproductiva</b> respecto a un parámetro si al sumar variables independientes de la "
            "familia se obtiene otra de la familia con los parámetros sumados: la binomial en n, la Poisson en "
            "&lambda;, la binomial negativa en n, la gamma en p y la normal en la media y la varianza."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los goles de un partido (1982)</b><br>"
            "<i>Predice un resultado de fútbol con dos variables de Poisson, como propuso Mike Maher.</i><br><br>"
            "<b>II. La medida del metro (1792)</b><br>"
            "<i>Mide el meridiano con Delambre y Méchain, tramo a tramo, y descubre cómo se acumulan los "
            "errores.</i><br><br>"
            "<b>III. La suma de uniformes (1927)</b><br>"
            "<i>Suma números al azar con Joseph Irwin y Philip Hall: el resultado ya no es uniforme.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>goles medios</u> de cada equipo")
        c1, c2 = st.columns(2)
        l1 = c1.slider("Goles medios del local", 0.2, 3.5, v["home"], 0.1, key=ui.wkey(PAGE, "home"))
        l2 = c2.slider("Goles medios del visitante", 0.2, 3.5, v["away"], 0.1, key=ui.wkey(PAGE, "away"))

        ui.planteamiento()
        ui.statement(
            "<b>Los goles de un partido (1982)</b><br><br>"
            "El estadístico británico Mike Maher propuso modelar los goles de cada equipo en un partido como dos "
            "variables de Poisson independientes, con medias que dependen del ataque de uno y la defensa del otro. "
            "El modelo, con retoques, sigue en el corazón de las casas de apuestas. Sea X el número de goles del "
            f"equipo local, de media {v['home']}, e Y el del visitante, de media {v['away']}."
        )

        if ui.accordion_step("P1_A", "(A) El marcador"):
            ui.content(
                "Escribe la probabilidad de un marcador concreto (i, j). ¿Cómo se calculan con la cuadrícula de la "
                "derecha la probabilidad de victoria local, de empate y de victoria visitante?"
            )
            ui.spoiler(
                "Por la independencia, la función de probabilidad conjunta es el producto de las marginales:"
                "<div class='formula-box'>&#8473;(X = i, Y = j) = e<sup>&minus;&lambda;<sub>1</sub></sup><sup>&lambda;<sub>1</sub><sup>i</sup></sup>"
                "&frasl;<sub>i!</sub>&middot;e<sup>&minus;&lambda;<sub>2</sub></sup><sup>&lambda;<sub>2</sub><sup>j</sup></sup>&frasl;<sub>j!</sub></div>"
                "La victoria local es la suma de las casillas en que el local marca más (en verde), el empate la "
                "diagonal (en gris) y la victoria visitante el resto: la probabilidad de un suceso del vector es la "
                "suma sobre los puntos favorables."
            )

        if ui.accordion_step("P1_B", "(B) Los goles totales"):
            ui.content(
                "El total X + Y = n se obtiene sumando una diagonal de la cuadrícula. Calcula esa suma con el "
                "binomio de Newton, o con funciones generatrices. ¿Qué distribución sale?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(X + Y = n) = &sum;<sub>i=0</sub><sup>n</sup> e<sup>&minus;(&lambda;<sub>1</sub>+&lambda;<sub>2</sub>)</sup>"
                "<sup>&lambda;<sub>1</sub><sup>i</sup>&lambda;<sub>2</sub><sup>n&minus;i</sup></sup>&frasl;<sub>i!(n &minus; i)!</sub> = "
                "e<sup>&minus;(&lambda;<sub>1</sub>+&lambda;<sub>2</sub>)</sup><sup>(&lambda;<sub>1</sub> + &lambda;<sub>2</sub>)<sup>n</sup></sup>&frasl;<sub>n!</sub></div>"
                "Una Poisson de media &lambda;<sub>1</sub> + &lambda;<sub>2</sub>. Con generatrices es inmediato: "
                "e<sup>&lambda;<sub>1</sub>(e<sup>t</sup>&minus;1)</sup>&middot;e<sup>&lambda;<sub>2</sub>(e<sup>t</sup>&minus;1)</sup> = "
                "e<sup>(&lambda;<sub>1</sub>+&lambda;<sub>2</sub>)(e<sup>t</sup>&minus;1)</sup>. La Poisson es reproductiva en &lambda;."
            )

        if ui.accordion_step("P1_C", "(C) Sabiendo el total"):
            ui.content(
                "Si te dicen que el partido acabó con n goles en total, ¿qué distribución tienen los del local? ¿Y la "
                "diferencia X &minus; Y, es de Poisson?"
            )
            ui.spoiler(
                "Condicionando a X + Y = n, los goles del local son binomiales B(n, &lambda;<sub>1</sub>/(&lambda;<sub>1</sub> + "
                "&lambda;<sub>2</sub>)): cada gol es del local con probabilidad proporcional a su media. La diferencia, "
                "en cambio, no es de Poisson: puede ser negativa. La reproductividad habla de sumas de variables "
                "independientes de la misma familia, y de nada más."
            )

    with col_right:
        ui.right_panel()
        home, draw, away = outcome_probs(l1, l2)
        ui.metrics([(f"Local: {home:.3f}", "result-yes"), (f"Empate: {draw:.3f}", "metric-c"),
                    (f"Visitante: {away:.3f}", "result-no")])
        ui.show(grid_chart(dark, l1, l2), key="fig_scores")
        ui.show(total_chart(dark, l1, l2), key="fig_total")
        ui.footer_bar("Arriba, la probabilidad (en %) de cada marcador. Abajo, la suma de cada diagonal frente a una "
                      "Poisson con la media total.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de tramos n</u> y el <u>error de cada tramo &sigma;</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Tramos medidos n", 1, 200, v["segments"], 1, key=ui.wkey(PAGE, "segments"))
        sigma = c2.select_slider("Error típico por tramo σ (toesas)", options=[0.2, 0.3, 0.5, 0.8, 1.0],
                                 value=v["sigma"], key=ui.wkey(PAGE, "sigma"))

        ui.planteamiento()
        ui.statement(
            "<b>La medida del metro (1792)</b><br><br>"
            "La Revolución francesa quiso una unidad de longitud para todos los pueblos: la diezmillonésima parte "
            "de la distancia del polo al ecuador. Jean-Baptiste Delambre midió el meridiano de París desde "
            "Dunkerque hasta Rodez, y Pierre Méchain desde Rodez hasta Barcelona, encadenando triángulos. La "
            "longitud total es la suma de muchos tramos, cada uno medido con un pequeño error. Supongamos que los "
            "errores son normales, de media cero y desviación &sigma;, e independientes entre tramos."
        )

        if ui.accordion_step("P2_A", "(A) La suma de normales"):
            ui.content(
                "Calcula la función generatriz de la suma de dos normales independientes. ¿Qué distribución tiene el "
                "error total de n tramos?"
            )
            ui.spoiler(
                "<div class='formula-box'>e<sup>&mu;<sub>1</sub>t + &sigma;<sub>1</sub><sup>2</sup>t<sup>2</sup>/2</sup>&middot;"
                "e<sup>&mu;<sub>2</sub>t + &sigma;<sub>2</sub><sup>2</sup>t<sup>2</sup>/2</sup> = e<sup>(&mu;<sub>1</sub>+&mu;<sub>2</sub>)t + "
                "(&sigma;<sub>1</sub><sup>2</sup>+&sigma;<sub>2</sub><sup>2</sup>)t<sup>2</sup>/2</sup></div>"
                "La suma es normal con media &mu;<sub>1</sub> + &mu;<sub>2</sub> y desviación &radic;(&sigma;<sub>1</sub><sup>2</sup> + "
                "&sigma;<sub>2</sub><sup>2</sup>). Con n tramos iguales, el error total es N(0, &sigma;&radic;n): se suman las "
                "varianzas, no las desviaciones."
            )

        if ui.accordion_step("P2_B", "(B) La raíz cuadrada salva la medida"):
            ui.content(
                "Si cada tramo tiene un error de &sigma; toesas, ¿cuánto error se acumula en n tramos? Compáralo con lo "
                "que pasaría si todos los errores tuvieran el mismo signo, por ejemplo por un instrumento mal "
                "calibrado. La línea roja de la derecha marca un sesgo de &sigma;/10 por tramo."
            )
            ui.spoiler(
                "Con errores independientes y centrados, el error total crece como &sigma;&radic;n: con cien tramos, solo "
                "diez veces el de uno. Un error sistemático, en cambio, crece como n y acaba dominando, igual que el "
                "truncamiento de la bolsa de Vancouver. Por eso los geodestas, además de repetir cada ángulo muchas "
                "veces con el círculo repetidor de Borda, invertían tanto esfuerzo en calibrar sus instrumentos: "
                "repetir no corrige un sesgo."
            )

        if ui.accordion_step("P2_C", "(C) El error de Méchain"):
            ui.content(
                "Méchain midió la latitud de Barcelona desde dos lugares distintos de la ciudad y obtuvo una "
                "discrepancia de unos pocos segundos de arco que no supo explicar. Atormentado, la ocultó durante "
                "años. ¿Por qué promediar muchas medidas repetidas no la habría eliminado?"
            )
            ui.spoiler(
                "Promediar n medidas independientes divide la desviación típica por &radic;n, pero solo reduce el error "
                "aleatorio. La discrepancia de Méchain venía, según se supo después, de efectos sistemáticos de su "
                "instrumento y de la refracción, que afectaban a todas sus medidas por igual. Contra un sesgo común, "
                "la independencia que hace funcionar los promedios no existe."
            )

    with col_right:
        ui.right_panel()
        sd = sigma * np.sqrt(n)
        ui.metrics([(f"&sigma; del error total = {sd:.2f}", "metric-a"),
                    (f"Con sesgo &sigma;/10 por tramo: {n * sigma / 10:.2f}", "result-no")])
        ui.show(meridian_chart(dark, n, sigma), key="fig_meridian")
        ui.footer_bar(f"El error aleatorio de {n} tramos crece como la raíz de n: {sd:.2f} toesas. Un sesgo pequeño y "
                      "constante crece como n: la línea roja.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de uniformes n</u>")
        n = st.slider("Uniformes sumadas n", 1, 12, v["n"], 1, key=ui.wkey(PAGE, "n"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La suma de uniformes (1927)</b><br><br>"
            "En el mismo número de la revista <i>Biometrika</i>, Joseph Irwin y Philip Hall publicaron por separado la "
            "distribución de la suma de n variables uniformes independientes en (0, 1). ¿Es otra uniforme? ¿Qué "
            "forma tiene?"
        )

        if ui.accordion_step("P3_A", "(A) Dos uniformes"):
            ui.content(
                "Calcula la densidad de U<sub>1</sub> + U<sub>2</sub> integrando la densidad conjunta, que vale 1 en el "
                "cuadrado unidad, sobre la recta u<sub>1</sub> + u<sub>2</sub> = s, o calculando el área bajo esa recta."
            )
            ui.spoiler(
                "&#8473;(U<sub>1</sub> + U<sub>2</sub> &le; s) es el área del triángulo bajo la recta: s<sup>2</sup>/2 si s &le; 1 y "
                "1 &minus; (2 &minus; s)<sup>2</sup>/2 si s &ge; 1. Derivando:"
                "<div class='formula-box'>f(s) = s si 0 &le; s &le; 1; &nbsp; f(s) = 2 &minus; s si 1 &le; s &le; 2</div>"
                "Un triángulo, como la suma de dos dados de Catán. La uniforme no es reproductiva."
            )

        if ui.accordion_step("P3_B", "(B) La generatriz lo confirma"):
            ui.content(
                "Calcula la función generatriz de una uniforme en (0, 1) y la de la suma de n. ¿Es la generatriz de "
                "una uniforme?"
            )
            ui.spoiler(
                "<div class='formula-box'>G<sub>U</sub>(t) = <sup>e<sup>t</sup> &minus; 1</sup>&frasl;<sub>t</sub> &nbsp;&rArr;&nbsp; "
                "G<sub>U<sub>1</sub>+&ctdot;+U<sub>n</sub></sub>(t) = (<sup>e<sup>t</sup> &minus; 1</sup>&frasl;<sub>t</sub>)<sup>n</sup></div>"
                "La uniforme en (0, n) tendría generatriz (e<sup>nt</sup> &minus; 1)/(nt), que es otra cosa. La densidad "
                "exacta es un polinomio a trozos de grado n &minus; 1, la fórmula de Irwin y Hall que dibuja la curva "
                "azul."
            )

        if ui.accordion_step("P3_C", "(C) Doce uniformes, menos seis"):
            ui.content(
                "Sube n hasta 12. La suma tiene media 6 y varianza 1. ¿Qué parece? Los primeros ordenadores usaban "
                "este truco para generar normales: ¿qué inconveniente tiene?"
            )
            ui.spoiler(
                "La media de cada uniforme es 1/2 y su varianza 1/12; con doce, media 6 y varianza 1. La curva azul y "
                "la normal discontinua casi se confunden: es el teorema central del límite en acción. El "
                "inconveniente es que la suma nunca sale de [0, 12], así que la normal aproximada nunca supera 6 "
                "desviaciones: inofensivo para casi todo, salvo para estudiar sucesos rarísimos en las colas."
            )

        if st.button("Simular 20 000 sumas", key="uniform_play", width="stretch", type="primary"):
            st.session_state["uniform_sim"] = (n, np.random.default_rng().uniform(0, 1, (20000, n)).sum(axis=1))

    with col_right:
        ui.right_panel()
        sim = st.session_state.get("uniform_sim")
        sample = sim[1] if sim and sim[0] == n else None
        ui.metrics([(f"Media = {n / 2:g}", "metric-a"), (f"Varianza = {n}/12 = {n / 12:.3f}", "metric-b")])
        ui.show(irwin_chart(dark, n, sample), key="fig_irwin")
        ui.footer_bar(f"La suma de {n} uniformes: con n = 1 es plana, con 2 un triángulo y a partir de ahí una campana "
                      "cada vez más parecida a la normal.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los goles de un partido", "P1_A"),
        ("P2", "(II) La medida del metro", "P2_A"),
        ("P3", "(III) La suma de uniformes", "P3_A"),
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
