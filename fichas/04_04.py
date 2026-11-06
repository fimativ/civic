#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 4: la distribución exponencial.

Las partículas alfa de Rutherford y Geiger (de los recuentos de Poisson a las
esperas exponenciales), la datación por radiocarbono (semivida y falta de
memoria) y la paradoja del autobús (por qué se espera más de lo que parece).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "La distribución exponencial"
SYMBOL = "Exp(λ)"
PAGE = "04_04"

# Rutherford y Geiger (1910): partículas alfa contadas en 2608 intervalos de 7.5 segundos.
ALPHA = {0: 57, 1: 203, 2: 383, 3: 525, 4: 532, 5: 408, 6: 273, 7: 139, 8: 45, 9: 27, 10: 10, 11: 4, 12: 0,
         13: 1, 14: 1}
INTERVAL = 7.5
HALF_LIFE = 5730
REGULARITY = {"poisson": "Al azar (Poisson)", "gamma": "Algo regulares", "regular": "Puntuales"}


def initial_values():
    return {
        "remaining": ui.dchoice(25, [10, 20, 25, 40, 50, 60], "remaining"),
        "survived": 100 * round(ui.dint(3000, 1000, 10000, "survived") / 100),
        "headway": ui.dchoice(10, [5, 8, 10, 12, 15, 20], "headway"),
        "regularity": ui.dchoice("poisson", list(REGULARITY), "regularity"),
        "seed": int(ui.r("alpha") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "regularity": None, "alpha_round": 0, "bus_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def alpha_rate():
    k = np.array(list(ALPHA), dtype=float)
    n = np.array(list(ALPHA.values()), dtype=float)
    mean = float((k * n).sum() / n.sum())
    return mean, mean / INTERVAL


def bus_intervals(kind: str, headway: float, n: int, rng):
    if kind == "poisson":
        return rng.exponential(headway, n)
    if kind == "gamma":
        return rng.gamma(4, headway / 4, n)
    return np.full(n, float(headway))


def waits(intervals, passengers: int, rng):
    arrivals = np.cumsum(intervals)
    t = rng.uniform(0, arrivals[-1] * 0.98, passengers)
    idx = np.searchsorted(arrivals, t)
    gap = intervals[idx]
    return arrivals[idx] - t, gap


# =============================================================================
# 2. FIGURAS
# =============================================================================

def alpha_charts(dark, rate: float, seed: int):
    rng = np.random.default_rng(seed)
    gaps = rng.exponential(1 / rate, 4000)
    times = np.cumsum(gaps)
    top = 5 / rate
    xs = np.linspace(0, top, 300)
    edges = np.linspace(0, top, 31)
    hist, _ = np.histogram(gaps, bins=edges)
    width = edges[1] - edges[0]
    p = ui.new_figure(dark, height=260, x_axis_label="segundos entre dos partículas", y_axis_label="densidad",
                      x_range=(0, top))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(gaps) * width), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.6, line_color=None, legend_label="esperas simuladas")
    p.line(xs, rate * np.exp(-rate * xs), line_width=4, color=ui.BLUE_LINE, legend_label="λe^(−λt)")
    ui.style_legend(p, dark, "top_right")
    window = times[times < 60]
    q = ui.new_figure(dark, height=110, x_axis_label="tiempo (s)", x_range=(0, 60), y_range=(-1, 1))
    q.yaxis.visible = False
    q.ygrid.grid_line_color = None
    q.segment(x0=window, y0=-0.7, x1=window, y1=0.7, line_color=ui.UBU_RED, line_width=2)
    for edge in np.arange(INTERVAL, 60, INTERVAL):
        q.add_layout(Span(location=edge, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted"))
    return p, q


def counts_chart(dark, mean: float):
    k = np.array(list(ALPHA))
    n = np.array(list(ALPHA.values()))
    p = ui.new_figure(dark, height=240, x_axis_label="partículas en 7.5 s", y_axis_label="intervalos",
                      x_range=(-0.6, 14.6))
    p.vbar(x=k - 0.18, top=n, width=0.34, color=ui.BLUE_LINE, legend_label="Rutherford y Geiger")
    p.vbar(x=k + 0.18, top=n.sum() * stats.poisson.pmf(k, mean), width=0.34, color=ui.ORANGE_LINE,
           legend_label="Poisson")
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


def decay_chart(dark, survived: float):
    lam = np.log(2) / HALF_LIFE
    ts = np.linspace(0, 6 * HALF_LIFE, 400)
    p = ui.new_figure(dark, height=300, x_axis_label="años", y_axis_label="fracción que sobrevive",
                      x_range=(0, 6 * HALF_LIFE), y_range=(0, 1.05))
    p.line(ts, np.exp(-lam * ts), line_width=4, color=ui.BLUE_LINE, legend_label="desde el principio")
    later = ts[ts >= survived]
    p.line(later, np.exp(-lam * (later - survived)), line_width=3, color=ui.UBU_RED, line_dash="dashed",
           legend_label=f"sabiendo que sobrevivió {int(survived)} años")
    for h in range(1, 6):
        p.add_layout(Span(location=h * HALF_LIFE, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted"))
    return ui.style_legend(p, dark, "top_right")


def waits_chart(dark, wait, headway: float):
    top = 4 * headway
    edges = np.linspace(0, top, 41)
    hist, _ = np.histogram(wait, bins=edges)
    width = edges[1] - edges[0]
    p = ui.new_figure(dark, height=300, x_axis_label="minutos de espera", y_axis_label="densidad", x_range=(0, top))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(wait) * width), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.65, line_color=None)
    p.add_layout(Span(location=wait.mean(), dimension="height", line_color=ui.UBU_RED, line_width=3))
    p.add_layout(Span(location=headway / 2, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed",
                      line_width=2))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuánto hay que esperar a que ocurra algo?</b>")
        ui.content(
            "La distribución exponencial es el modelo natural para la espera hasta un suceso que puede ocurrir "
            "en cualquier momento con la misma intensidad: la próxima llamada, la próxima desintegración, el "
            "próximo autobús que pasa al azar. Tiene un parámetro &lambda; &gt; 0, el número medio de sucesos "
            "por unidad de tiempo. <i>Escribe su densidad y su función de distribución.</i>"
        )
        ui.formula_hidden("f(t) = &lambda;e<sup>&minus;&lambda;t</sup> &nbsp;&nbsp; F(t) = 1 &minus; e<sup>&minus;&lambda;t"
                          "</sup>, &nbsp; t &gt; 0")
        ui.content("<i>Integrando por partes, calcula su media y su varianza.</i>")
        ui.formula_hidden("&#120124;[T] = 1/&lambda; &nbsp;&nbsp; &#120141;(T) = 1/&lambda;<sup>2</sup>")
        ui.content(
            "Es la versión continua de la geométrica, y hereda de ella la propiedad más sorprendente: no tiene "
            "memoria. Esperar ya un rato no acerca el suceso."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las partículas de Rutherford y Geiger (1910)</b><br>"
            "<i>Cuenta destellos con Ernest Rutherford y Hans Geiger y descubre la exponencial escondida en "
            "una Poisson.</i><br><br>"
            "<b>II. El reloj del radiocarbono (1949)</b><br>"
            "<i>Data un resto antiguo con Willard Libby, sabiendo que los átomos no envejecen.</i><br><br>"
            "<b>III. La paradoja del autobús</b><br>"
            "<i>Pasa un autobús cada diez minutos de media. ¿Por qué esperas diez y no cinco?</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>Las partículas de Rutherford y Geiger (1910)</b><br><br>"
            "En Mánchester, Ernest Rutherford y Hans Geiger contaron, a oscuras y mirando por un microscopio, "
            "los destellos que producían las partículas alfa de una muestra de polonio sobre una pantalla. "
            "Anotaron cuántas llegaban en 2608 intervalos de 7.5 segundos, y el matemático Harry Bateman "
            "comprobó que los recuentos seguían una Poisson. Si los recuentos son de Poisson, ¿cómo es la "
            "espera entre una partícula y la siguiente?"
        )

        if ui.accordion_step("P1_A", "(A) De los recuentos a las esperas"):
            ui.content(
                "Si el número de partículas en un tiempo t es Poisson de media &lambda;t, ¿qué suceso equivale a "
                "<i>la primera partícula tarda más de t segundos</i>? Obtén la función de distribución de esa "
                "espera T y deriva para tener la densidad."
            )
            ui.spoiler(
                "Esperar más de t es que no llegue ninguna partícula en [0, t]:"
                "<div class='formula-box'>&#8473;(T &gt; t) = &#8473;(N<sub>t</sub> = 0) = e<sup>&minus;&lambda;t</sup> "
                "&nbsp;&rArr;&nbsp; F(t) = 1 &minus; e<sup>&minus;&lambda;t</sup>, &nbsp; f(t) = &lambda;e<sup>&minus;&lambda;t</sup></div>"
                "Recuentos de Poisson y esperas exponenciales son dos caras del mismo fenómeno: llegadas que "
                "ocurren al azar con intensidad constante."
            )

        if ui.accordion_step("P1_B", "(B) Estimar &lambda;"):
            mean, rate = alpha_rate()
            ui.content(
                "Calcula con la tabla de la derecha el número medio de partículas por intervalo y, de ahí, &lambda; "
                "en partículas por segundo. ¿Cuánto se espera de media entre dos partículas?"
            )
            ui.spoiler(
                f"Se contaron 10 097 partículas en 2608 intervalos: {mean:.2f} por intervalo, es decir, "
                f"&lambda; = {mean:.2f}/7.5 &asymp; {rate:.3f} partículas por segundo. La espera media es "
                f"1/&lambda; &asymp; {1 / rate:.2f} segundos, y su desviación típica, también 1/&lambda;: en la "
                "exponencial la media y la desviación coinciden."
            )

        if ui.accordion_step("P1_C", "(C) Cambiar de unidades"):
            ui.content(
                "Si T es la espera en segundos, ¿qué distribución tiene la espera en minutos, T/60? ¿Y aT para "
                "cualquier a &gt; 0?"
            )
            ui.spoiler(
                "&#8473;(aT &gt; t) = &#8473;(T &gt; t/a) = e<sup>&minus;(&lambda;/a)t</sup>: aT es exponencial de "
                "parámetro &lambda;/a. Medir en minutos multiplica la intensidad por 60. Eligiendo a = &lambda; "
                "cualquier exponencial se reduce a la de parámetro 1, igual que la tipificación con la normal, "
                "aunque aquí no hace falta tabla: la función de distribución es explícita."
            )

    with col_right:
        ui.right_panel()
        mean, rate = alpha_rate()
        ui.metrics([(f"&lambda; = {rate:.3f} partículas/s", "metric-a"), (f"Espera media = {1 / rate:.2f} s", "metric-c")])
        if st.button("Otra simulación", key="alpha_new", width="stretch"):
            st.session_state["alpha_round"] += 1
        hist, line = alpha_charts(dark, rate, v["seed"] + st.session_state["alpha_round"])
        ui.show(counts_chart(dark, mean), key="fig_alpha_counts")
        ui.show(line, key="fig_alpha_line")
        ui.show(hist, key="fig_alpha_gaps")
        ui.footer_bar("Arriba, la tabla original frente a la Poisson. En medio, un minuto de llegadas simuladas con la "
                      "misma intensidad, con los intervalos de 7.5 s. Abajo, las esperas entre llegadas frente a la "
                      "densidad exponencial.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>carbono 14 que queda</u> y los <u>años ya sobrevividos</u>")
        remaining = st.slider("Porcentaje de carbono 14 que queda", 1, 99, v["remaining"], 1,
                              key=ui.wkey(PAGE, "remaining"))
        survived = st.slider("Años que ya ha sobrevivido un átomo", 0, 20000, v["survived"], 100,
                             key=ui.wkey(PAGE, "survived"))

        ui.planteamiento()
        ui.statement(
            "<b>El reloj del radiocarbono (1949)</b><br><br>"
            "Willard Libby se dio cuenta de que los seres vivos incorporan carbono 14 en la misma proporción que "
            "la atmósfera y que, al morir, dejan de reponerlo. Cada átomo de carbono 14 se desintegra tras un "
            "tiempo exponencial, independientemente de los demás, y la mitad desaparece en unos 5730 años. "
            "Midiendo cuánto queda en un resto se sabe cuándo murió. Recibió el Nobel de Química en 1960."
        )

        if ui.accordion_step("P2_A", "(A) La semivida"):
            ui.content(
                "La semivida es el tiempo en que se desintegra la mitad de los átomos, es decir, la mediana de la "
                "exponencial. Exprésala en función de &lambda;. ¿Cuánto vale &lambda; para el carbono 14?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(T &gt; t<sub>1/2</sub>) = e<sup>&minus;&lambda;t<sub>1/2</sub></sup> = "
                "<sup>1</sup>&frasl;<sub>2</sub> &nbsp;&rArr;&nbsp; t<sub>1/2</sub> = <sup>ln 2</sup>&frasl;<sub>&lambda;</sub></div>"
                "Para el carbono 14, &lambda; = ln 2/5730 &asymp; 1.21&middot;10<sup>&minus;4</sup> por año. La "
                "mediana es menor que la media 1/&lambda; &asymp; 8270 años: la cola larga de la exponencial "
                "tira de la media hacia la derecha."
            )

        if ui.accordion_step("P2_B", "(B) Los átomos no envejecen"):
            ui.content(
                "Un átomo ha sobrevivido ya s años. ¿Qué probabilidad tiene de sobrevivir t años más? Compáralo "
                "con la de un átomo recién formado."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(T &gt; s + t | T &gt; s) = <sup>e<sup>&minus;&lambda;(s+t)</sup></sup>"
                "&frasl;<sub>e<sup>&minus;&lambda;s</sup></sub> = e<sup>&minus;&lambda;t</sup> = &#8473;(T &gt; t)</div>"
                "Es la falta de memoria, como en la geométrica del 53 de Venecia: un átomo viejo es "
                "indistinguible de uno nuevo. La curva roja de la derecha es la azul trasladada: empieza de "
                "nuevo en el momento en que sabemos que el átomo seguía ahí. La exponencial es la única "
                "distribución continua con esta propiedad."
            )

        if ui.accordion_step("P2_C", "(C) Datar un resto"):
            ui.content(
                "Un trozo de carbón conserva una fracción R del carbono 14 que tenía al morir el árbol. Con "
                "muchísimos átomos, esa fracción es prácticamente la probabilidad de supervivencia de cada uno. "
                "¿Qué edad tiene?"
            )
            ui.spoiler(
                "<div class='formula-box'>R = e<sup>&minus;&lambda;t</sup> &nbsp;&rArr;&nbsp; t = <sup>t<sub>1/2</sub></sup>"
                "&frasl;<sub>ln 2</sub>&middot;ln(1/R)</div>"
                "Con un 25 % quedan dos semividas, unos 11 460 años. Que la fracción observada sea la probabilidad "
                "se debe a que hay billones de átomos independientes: es otra vez la ley de los grandes números."
            )

    with col_right:
        ui.right_panel()
        lam = np.log(2) / HALF_LIFE
        age = np.log(100 / remaining) / lam
        ui.metrics([(f"Edad estimada: {age:,.0f} años".replace(",", " "), "metric-a"),
                    (f"&#8473;(otros 5730 años | sobrevivió {survived}) = 0.5", "metric-c")])
        ui.show(decay_chart(dark, survived), key="fig_decay")
        ui.footer_bar("Las líneas punteadas marcan semividas sucesivas. La curva roja, que parte del momento en que "
                      "el átomo seguía vivo, es una copia exacta de la azul.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>intervalo medio</u> y la <u>regularidad</u> de los autobuses")
        headway = st.select_slider("Intervalo medio entre autobuses (minutos)", options=[5, 8, 10, 12, 15, 20],
                                   value=v["headway"], key=ui.wkey(PAGE, "headway"))
        if st.session_state["regularity"] is None:
            st.session_state["regularity"] = v["regularity"]
        ui.choice_buttons(list(REGULARITY), "regularity", labels=REGULARITY, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>La paradoja del autobús</b><br><br>"
            "William Feller, en el segundo volumen de su célebre tratado de probabilidad, dedicó un apartado a "
            f"lo que llamó la paradoja del tiempo de espera. Por una parada pasan autobuses cada {v['headway']} "
            "minutos de media, en instantes que forman un proceso de Poisson. Llegas a la parada en un "
            "momento cualquiera. ¿Cuánto esperas de media? La intuición dice que la mitad del intervalo."
        )

        if ui.accordion_step("P3_A", "(A) La falta de memoria responde"):
            ui.content(
                "Si los intervalos entre autobuses son exponenciales, ¿qué distribución tiene tu espera, contada "
                "desde que llegas? Usa la falta de memoria."
            )
            ui.spoiler(
                "Desde el instante en que llegas, el tiempo hasta el siguiente autobús es otra exponencial con la "
                "misma media: el proceso no recuerda cuándo pasó el último. Esperas de media el intervalo "
                "entero, no la mitad. Es la línea roja de la derecha, frente a la gris discontinua."
            )

        if ui.accordion_step("P3_B", "(B) ¿Dónde está el truco?"):
            ui.content(
                "La intuición falla porque los intervalos no son todos igual de probables de contener tu llegada. "
                "¿Cuáles tienen más probabilidad de contenerla? ¿Cuánto mide de media el intervalo en que caes?"
            )
            ui.spoiler(
                "Es más probable caer en un intervalo largo que en uno corto, en proporción a su longitud. El "
                "intervalo que te toca no es un intervalo típico, sino uno elegido con un sesgo hacia los "
                "largos:"
                "<div class='formula-box'>&#120124;[espera] = <sup>&#120124;[I<sup>2</sup>]</sup>&frasl;<sub>2&#120124;[I]</sub> "
                "= <sup>&#120124;[I]</sup>&frasl;<sub>2</sub> + <sup>&#120141;(I)</sup>&frasl;<sub>2&#120124;[I]</sub></div>"
                "Con intervalos exponenciales, &#120141;(I) = &#120124;[I]<sup>2</sup> y la espera media es "
                "&#120124;[I]; el intervalo en que caes mide, de media, el doble del típico."
            )

        if ui.accordion_step("P3_C", "(C) Autobuses puntuales"):
            ui.content(
                "Elige autobuses puntuales y después algo regulares. ¿Cuánto esperas en cada caso? ¿Qué le "
                "conviene más a quien llega sin mirar el horario: un servicio más frecuente o uno más regular?"
            )
            ui.spoiler(
                "Con autobuses exactamente cada T minutos la espera es uniforme en [0, T], de media T/2, porque "
                "la varianza de los intervalos es cero. Entre ambos extremos, la espera media crece con la "
                "varianza de los intervalos. Los autobuses que se apelotonan castigan dos veces: llegan juntos y "
                "dejan huecos largos, y es en los huecos largos donde caen casi todos los viajeros."
            )

    with col_right:
        ui.right_panel()
        kind = st.session_state["regularity"]
        if st.button("Otro día de servicio", key="bus_new", width="stretch"):
            st.session_state["bus_round"] += 1
        rng = np.random.default_rng(v["seed"] + 11 * st.session_state["bus_round"])
        intervals = bus_intervals(kind, headway, 3000, rng)
        wait, gap = waits(intervals, 5000, rng)
        ui.metrics([(f"Espera media: {wait.mean():.2f} min", "metric-a"),
                    (f"Intervalo en que caes: {gap.mean():.2f} min", "metric-c")])
        ui.show(waits_chart(dark, wait, headway), key="fig_bus")
        ui.footer_bar(f"Autobuses {REGULARITY[kind].lower()}, cada {headway} minutos de media. Línea roja: espera media "
                      "de 5000 viajeros simulados. Línea gris: la mitad del intervalo medio, lo que dice la intuición.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Rutherford y Geiger", "P1_A"),
        ("P2", "(II) El reloj del radiocarbono", "P2_A"),
        ("P3", "(III) La paradoja del autobús", "P3_A"),
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
