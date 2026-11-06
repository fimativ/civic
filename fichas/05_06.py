#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 6: la multinomial y la uniforme en un recinto.

Los guisantes de Mendel (multinomial, marginales binomiales y un ajuste
demasiado bueno), la encuesta de Gallup (covarianzas negativas entre
proporciones y el sesgo que ningún tamaño corrige) y el palo roto (un vector
uniforme en un triángulo).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "La multinomial"
SYMBOL = "M(n,p)"
PAGE = "05_06"

PEAS = np.array([315, 108, 101, 32])
PEA_P = np.array([9, 3, 3, 1]) / 16
PEA_LABELS = ["lisa y amarilla", "lisa y verde", "rugosa y amarilla", "rugosa y verde"]
STICKS = {"two": "Dos cortes al azar", "longer": "Cortar el trozo mayor", "random": "Cortar un trozo al azar"}
STICK_THEORY = {"two": 0.25, "longer": 2 * np.log(2) - 1, "random": np.log(2) - 0.5}


def initial_values():
    return {
        "sample": ui.dchoice(1500, [500, 1000, 1500, 3000, 5000], "sample"),
        "roosevelt": ui.dchoice(0.55, [0.51, 0.53, 0.55, 0.58, 0.61], "roosevelt"),
        "landon": ui.dchoice(0.40, [0.36, 0.38, 0.40, 0.43, 0.45], "landon"),
        "stick": ui.dchoice("two", list(STICKS), "stick"),
        "seed": int(ui.r("mendel") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "stick": None, "mendel_round": 0, "poll_round": 0,
                   "stick_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def pearson_x2(counts, probs) -> float:
    expected = counts.sum() * probs
    return float(((counts - expected) ** 2 / expected).sum())


def simulate_mendel(n_exp: int, seed: int):
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(PEAS.sum(), PEA_P, size=n_exp)
    return np.array([pearson_x2(c, PEA_P) for c in counts]), counts[0]


def simulate_polls(n: int, pr: float, pl: float, polls: int, seed: int):
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(n, [pr, pl, 1 - pr - pl], size=polls)
    return counts[:, 0] / n - counts[:, 1] / n


def break_stick(kind: str, n: int, seed: int):
    rng = np.random.default_rng(seed)
    if kind == "two":
        u = np.sort(rng.uniform(0, 1, (n, 2)), axis=1)
        a, b, c = u[:, 0], u[:, 1] - u[:, 0], 1 - u[:, 1]
    else:
        first = rng.uniform(0, 1, n)
        left, right = first, 1 - first
        if kind == "longer":
            choose_left = left >= right
        else:
            choose_left = rng.random(n) < 0.5
        piece = np.where(choose_left, left, right)
        other = np.where(choose_left, right, left)
        cut = rng.uniform(0, 1, n) * piece
        a, b, c = cut, piece - cut, other
    return np.column_stack((a, b, c))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def mendel_chart(dark, x2_sim, observed):
    top = 15
    xs = np.linspace(0.01, top, 300)
    edges = np.linspace(0, top, 46)
    hist, _ = np.histogram(x2_sim, bins=edges)
    p = ui.new_figure(dark, height=280, x_axis_label="discrepancia X² de un experimento", y_axis_label="densidad",
                      x_range=(0, top))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(x2_sim) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None, legend_label="experimentos simulados")
    p.line(xs, stats.chi2.pdf(xs, 3), line_width=4, color=ui.BLUE_LINE, legend_label="χ² con 3 g.l.")
    p.add_layout(Span(location=observed, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return ui.style_legend(p, dark, "top_right")


def peas_chart(dark, counts):
    expected = counts.sum() * PEA_P
    p = ui.new_figure(dark, height=230, x_range=PEA_LABELS, y_axis_label="guisantes")
    p.vbar(x=PEA_LABELS, top=counts, width=0.55, color=ui.GREEN_LINE, alpha=0.8, legend_label="observado")
    p.scatter(PEA_LABELS, expected, size=14, marker="diamond", color=ui.UBU_RED, legend_label="9 : 3 : 3 : 1")
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "12px"
    return ui.style_legend(p, dark, "top_right")


def poll_chart(dark, leads, true_lead, sd_correct, sd_naive):
    lo, hi = true_lead - 5 * sd_correct, true_lead + 5 * sd_correct
    xs = np.linspace(lo, hi, 300)
    edges = np.linspace(lo, hi, 41)
    hist, _ = np.histogram(leads, bins=edges)
    p = ui.new_figure(dark, height=300, x_axis_label="ventaja estimada de Roosevelt", y_axis_label="densidad",
                      x_range=(lo, hi))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(leads) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None, legend_label="encuestas simuladas")
    p.line(xs, stats.norm.pdf(xs, true_lead, sd_correct), line_width=4, color=ui.BLUE_LINE,
           legend_label="con la covarianza")
    p.line(xs, stats.norm.pdf(xs, true_lead, sd_naive), line_width=3, color=ui.RED_LINE, line_dash="dashed",
           legend_label="olvidando la covarianza")
    p.add_layout(Span(location=0, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    return ui.style_legend(p, dark, "top_left")


def simplex_chart(dark, pieces):
    a, b = pieces[:, 0], pieces[:, 1]
    x = b + a / 2
    y = a * np.sqrt(3) / 2
    ok = (pieces < 0.5).all(axis=1)
    show = slice(0, 2500)
    fg = "#e6e6e6" if dark else "#333333"
    p = ui.new_figure(dark, height=320, x_range=(-0.05, 1.05), y_range=(-0.05, 0.92), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    p.patch([0, 1, 0.5, 0], [0, 0, np.sqrt(3) / 2, 0], fill_alpha=0, line_color=fg, line_width=2)
    p.patch([0.5, 0.75, 0.25], [0, np.sqrt(3) / 4, np.sqrt(3) / 4], fill_color=ui.GREEN_LINE, fill_alpha=0.12,
            line_color=ui.GREEN_LINE, line_width=2)
    p.scatter(x[show][~ok[show]], y[show][~ok[show]], size=3, color=ui.GREY_LINE, alpha=0.5)
    p.scatter(x[show][ok[show]], y[show][ok[show]], size=3.5, color=ui.GREEN_LINE, alpha=0.8)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué pasa cuando hay más de dos resultados?</b>")
        ui.content(
            "La binomial cuenta éxitos en n ensayos con dos resultados. Si cada ensayo puede acabar en k "
            "resultados A<sub>1</sub>, &hellip;, A<sub>k</sub> con probabilidades p<sub>1</sub>, &hellip;, p<sub>k</sub>, el "
            "vector de recuentos (X<sub>1</sub>, &hellip;, X<sub>k</sub>) sigue una <b>multinomial</b>. <i>Escribe su función "
            "de probabilidad.</i>"
        )
        ui.formula_hidden("&#8473;(X<sub>1</sub> = x<sub>1</sub>, &hellip;, X<sub>k</sub> = x<sub>k</sub>) = "
                          "<sup>n!</sup>&frasl;<sub>x<sub>1</sub>!&ctdot;x<sub>k</sub>!</sub> p<sub>1</sub><sup>x<sub>1</sub></sup>&ctdot;"
                          "p<sub>k</sub><sup>x<sub>k</sub></sup>, &nbsp; x<sub>1</sub> + &ctdot; + x<sub>k</sub> = n")
        ui.content(
            "Cada recuento por separado es binomial, pero los recuentos no son independientes: suman n, así que si "
            "uno sube los demás tienden a bajar. La otra distribución de la ficha es la <b>uniforme</b> en un recinto "
            "B del plano: densidad constante, inversa del área de B."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los guisantes de Mendel (1866)</b><br>"
            "<i>Cuenta guisantes con Gregor Mendel y comprueba, con Ronald Fisher, si sus datos eran demasiado "
            "buenos.</i><br><br>"
            "<b>II. La encuesta de Gallup (1936)</b><br>"
            "<i>Una encuesta de dos millones de respuestas que falló y otra mucho más pequeña que acertó.</i>"
            "<br><br>"
            "<b>III. El palo roto</b><br>"
            "<i>Rompe un palo en tres trozos al azar: ¿con qué probabilidad forman un triángulo?</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>Los guisantes de Mendel (1866)</b><br><br>"
            "En el huerto de su monasterio de Brno, Gregor Mendel cruzó guisantes de semilla lisa y amarilla con "
            "otros de semilla rugosa y verde. En la segunda generación, su teoría predecía las cuatro combinaciones "
            "en proporción 9 : 3 : 3 : 1. Contó 556 semillas: 315 lisas y amarillas, 108 lisas y verdes, 101 rugosas y "
            "amarillas y 32 rugosas y verdes."
        )
        ui.show(peas_chart(dark, PEAS), key="fig_peas")

        if ui.accordion_step("P1_A", "(A) La multinomial"):
            ui.content(
                "Si cada semilla cae en una de las cuatro clases con probabilidades 9/16, 3/16, 3/16 y 1/16, de forma "
                "independiente, ¿qué distribución tiene el vector de recuentos? ¿Cuántas semillas de cada clase se "
                "esperan?"
            )
            ui.spoiler(
                "Es multinomial M(556; 9/16, 3/16, 3/16, 1/16), y cada recuento tiene media np<sub>i</sub>: 312.75, 104.25, "
                "104.25 y 34.75. Los datos de Mendel están asombrosamente cerca."
            )

        if ui.accordion_step("P1_B", "(B) Marginales y covarianzas"):
            ui.content(
                "¿Qué distribución tiene el número de semillas lisas, sin mirar el color? ¿Y la covarianza entre los "
                "recuentos de dos clases distintas?"
            )
            ui.spoiler(
                "Agrupando clases se obtiene otra multinomial; con dos grupos, una binomial: las lisas son B(556, 3/4). "
                "Escribiendo X<sub>i</sub> como suma de indicatrices de cada semilla, Cov(X<sub>i</sub>, X<sub>j</sub>) = "
                "&minus;np<sub>i</sub>p<sub>j</sub> para i &ne; j: negativa, porque una semilla que cae en una clase no puede "
                "caer en otra. La matriz de covarianzas tiene determinante cero, porque los recuentos suman siempre 556."
            )

        if ui.accordion_step("P1_C", "(C) ¿Demasiado bueno?"):
            ui.content(
                "Calcula la discrepancia de Pearson X<sup>2</sup> de los datos de Mendel. Simula muchos experimentos de 556 "
                "semillas con la teoría correcta: ¿con qué frecuencia sale un ajuste tan bueno o mejor?"
            )
            x2 = pearson_x2(PEAS, PEA_P)
            ui.spoiler(
                f"X<sup>2</sup> = {x2:.2f}, con tres grados de libertad. Un ajuste igual de bueno o mejor solo aparece en "
                f"torno al {100 * stats.chi2.cdf(x2, 3):.0f} % de los experimentos: raro, pero no imposible en uno solo. En "
                "1936 Ronald Fisher repasó todos los experimentos de Mendel y concluyó que, en conjunto, se ajustaban a "
                "la teoría mejor de lo que el azar permite. Si fue un ayudante entusiasta, una selección inconsciente "
                "de los datos o simple suerte se sigue discutiendo."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otros 5000 experimentos", key="mendel_new", width="stretch"):
            st.session_state["mendel_round"] += 1
        x2_sim, first = simulate_mendel(5000, v["seed"] + st.session_state["mendel_round"])
        observed = pearson_x2(PEAS, PEA_P)
        ui.metrics([(f"X<sup>2</sup> de Mendel = {observed:.3f}", "metric-a"),
                    (f"Simulados con X<sup>2</sup> &le; {observed:.2f}: {(x2_sim <= observed).mean():.3f}", "metric-c")])
        ui.show(mendel_chart(dark, x2_sim, observed), key="fig_mendel")
        ui.footer_bar(f"Un experimento simulado: {', '.join(map(str, first))}. La línea roja marca la discrepancia de "
                      "Mendel: casi todos los experimentos simulados quedan a su derecha, con peor ajuste.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra</u> y el <u>apoyo real</u> de cada candidato")
        n = st.select_slider("Personas encuestadas n", options=[100, 300, 500, 1000, 1500, 3000, 5000, 10000],
                             value=v["sample"], key=ui.wkey(PAGE, "sample"))
        c1, c2 = st.columns(2)
        pr = c1.slider("Apoyo real a Roosevelt", 0.30, 0.70, v["roosevelt"], 0.01, key=ui.wkey(PAGE, "roosevelt"))
        pl = c2.slider("Apoyo real a Landon", 0.20, 0.65, v["landon"], 0.01, key=ui.wkey(PAGE, "landon"))
        if pl > 0.99 - pr:
            pl = round(0.99 - pr, 2)
            ui.caption(f"Los dos apoyos no pueden sumar más de 0.99: Landon queda en {pl:.2f}.")

        ui.planteamiento()
        ui.statement(
            "<b>La encuesta de Gallup (1936)</b><br><br>"
            "En las elecciones presidenciales de 1936, la revista <i>Literary Digest</i> envió millones de papeletas a "
            "lectores, propietarios de teléfono y de automóvil, recibió más de dos millones de respuestas y dio como "
            "ganador a Alf Landon. George Gallup, con una muestra mucho menor, elegida para parecerse a todo el "
            "electorado, predijo la victoria de Franklin D. Roosevelt, que ganó por una enorme mayoría. Una "
            "encuesta a n personas elegidas al azar, con tres respuestas posibles (Roosevelt, Landon, otros), es una "
            "multinomial."
        )

        if ui.accordion_step("P2_A", "(A) La ventaja estimada"):
            ui.content(
                "Sea p̂<sub>R</sub> = X<sub>R</sub>/n la proporción de la muestra que apoya a Roosevelt y p̂<sub>L</sub> la de "
                "Landon. Calcula la media y la varianza de cada una y su covarianza."
            )
            ui.spoiler(
                "Cada recuento es binomial y la covarianza de la multinomial es &minus;np<sub>R</sub>p<sub>L</sub>:"
                "<div class='formula-box'>&#120141;(p̂<sub>R</sub>) = <sup>p<sub>R</sub>(1 &minus; p<sub>R</sub>)</sup>&frasl;<sub>n</sub> &nbsp;&nbsp; "
                "Cov(p̂<sub>R</sub>, p̂<sub>L</sub>) = &minus;<sup>p<sub>R</sub>p<sub>L</sub></sup>&frasl;<sub>n</sub></div>"
            )

        if ui.accordion_step("P2_B", "(B) La covarianza cuenta dos veces"):
            ui.content(
                "La ventaja es p̂<sub>R</sub> &minus; p̂<sub>L</sub>. Calcula su varianza. ¿Qué error se comete si se ignora la "
                "covarianza? Compara las dos curvas de la derecha con la simulación."
            )
            ui.spoiler(
                "<div class='formula-box'>&#120141;(p̂<sub>R</sub> &minus; p̂<sub>L</sub>) = <sup>p<sub>R</sub> + p<sub>L</sub> &minus; "
                "(p<sub>R</sub> &minus; p<sub>L</sub>)<sup>2</sup></sup>&frasl;<sub>n</sub></div>"
                "Al restar dos variables con covarianza negativa, el término &minus;2Cov se suma: la ventaja fluctúa más "
                "de lo que sugiere tratar las proporciones como independientes. Cada voto que gana uno lo pierde el "
                "otro, y la ventaja se mueve el doble."
            )

        if ui.accordion_step("P2_C", "(C) Dos millones de respuestas, y falló"):
            ui.content(
                "Con más de dos millones de respuestas, la desviación típica de la ventaja del <i>Literary Digest</i> era "
                "minúscula. ¿Por qué falló? ¿Qué diferencia esa muestra de la de Gallup?"
            )
            ui.spoiler(
                "Todas las fórmulas anteriores suponen que cada persona encuestada se elige al azar entre los votantes, "
                "con las probabilidades reales. Los lectores con teléfono y automóvil en plena Gran Depresión, y "
                "además los que se molestaron en contestar, no eran una muestra al azar del electorado: votaban más a "
                "Landon. Ese sesgo no disminuye al aumentar n. Una muestra pequeña bien elegida vale más que una enorme "
                "mal elegida, la lección fundacional del muestreo."
            )

    with col_right:
        ui.right_panel()
        lead = pr - pl
        sd_c = np.sqrt((pr + pl - lead ** 2) / n)
        sd_n = np.sqrt((pr * (1 - pr) + pl * (1 - pl)) / n)
        if st.button("Otras 4000 encuestas", key="poll_new", width="stretch"):
            st.session_state["poll_round"] += 1
        leads = simulate_polls(n, pr, pl, 4000, v["seed"] + st.session_state["poll_round"])
        ui.metrics([(f"&sigma; de la ventaja: {sd_c:.4f}", "metric-a"),
                    (f"Encuestas con el ganador correcto: {(np.sign(leads) == np.sign(lead)).mean():.3f}", "metric-c")])
        ui.show(poll_chart(dark, leads, lead, sd_c, sd_n), key="fig_gallup")
        ui.footer_bar(f"Ventaja real: {lead:+.3f}. Desviación de la ventaja estimada: {sd_c:.4f} con la covarianza y "
                      f"{sd_n:.4f} si se olvida.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>forma de romper el palo</u>")
        if st.session_state["stick"] is None:
            st.session_state["stick"] = v["stick"]
        ui.choice_buttons(list(STICKS), "stick", labels=STICKS, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>El palo roto</b><br><br>"
            "Un clásico de los manuales del siglo XIX: se rompe un palo de longitud 1 por dos puntos elegidos al azar, "
            "de forma independiente y uniforme. ¿Qué probabilidad hay de que los tres trozos formen un triángulo? Las "
            "longitudes (A, B, C) suman 1, así que viven en un triángulo del espacio, y cada rotura al azar es un "
            "punto de ese triángulo, como los de la figura."
        )

        if ui.accordion_step("P3_A", "(A) La condición del triángulo"):
            ui.content(
                "Tres longitudes que suman 1 forman un triángulo si cada una es menor que la suma de las otras dos. "
                "Reescribe la condición. ¿Qué región del triángulo de la figura le corresponde?"
            )
            ui.spoiler(
                "a &lt; b + c = 1 &minus; a equivale a a &lt; 1/2, y lo mismo con b y c: ningún trozo puede superar la mitad "
                "del palo. En el triángulo de longitudes, es el triángulo central que une los puntos medios de los "
                "lados, en verde."
            )

        if ui.accordion_step("P3_B", "(B) Uniforme en un recinto"):
            ui.content(
                "Con dos cortes al azar, ¿qué distribución tiene el vector de longitudes en su triángulo? ¿Qué fracción "
                "del área ocupa la región verde?"
            )
            ui.spoiler(
                "Los dos puntos de corte son uniformes en el cuadrado unidad, y ordenarlos lleva la mitad del cuadrado "
                "al triángulo de longitudes sin deformar las áreas: el vector es <b>uniforme</b> en el triángulo, con "
                "densidad constante. La probabilidad es el cociente de áreas, y el triángulo central ocupa un cuarto: "
                "&#8473; = 1/4. La longitud de un trozo cualquiera tiene densidad marginal 2(1 &minus; x) en (0, 1)."
            )

        if ui.accordion_step("P3_C", "(C) Otras formas de romper"):
            ui.content(
                "Rompe el palo una vez y después rompe el trozo mayor, o uno de los dos elegido al azar. ¿Cambia la "
                "probabilidad? ¿A qué problema de la ficha de la uniforme te recuerda?"
            )
            ui.spoiler(
                "Cambia: rompiendo el trozo mayor sale 2 ln 2 &minus; 1 &asymp; 0.386, y rompiendo uno al azar, "
                "ln 2 &minus; 1/2 &asymp; 0.193. Los puntos ya no se reparten uniformemente en el triángulo. Como en la "
                "cuerda de Bertrand, <i>romper al azar</i> no está definido hasta que se dice cómo."
            )

    with col_right:
        ui.right_panel()
        kind = st.session_state["stick"]
        if st.button("Romper otros 10 000 palos", key="stick_new", width="stretch"):
            st.session_state["stick_round"] += 1
        pieces = break_stick(kind, 10000, v["seed"] + st.session_state["stick_round"])
        freq = float((pieces < 0.5).all(axis=1).mean())
        ui.metrics([(f"Frecuencia de triángulos: {freq:.4f}", "metric-a"),
                    (f"Teoría: {STICK_THEORY[kind]:.4f}", "metric-c")])
        ui.show(simplex_chart(dark, pieces), key="fig_stick")
        ui.footer_bar("Cada punto es una rotura: su distancia a cada lado del triángulo es proporcional a la longitud de un trozo (las tres suman la altura). En "
                      "verde, las roturas que forman triángulo.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los guisantes de Mendel", "P1_A"),
        ("P2", "(II) La encuesta de Gallup", "P2_A"),
        ("P3", "(III) El palo roto", "P3_A"),
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
