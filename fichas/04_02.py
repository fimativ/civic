#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 2: la distribución uniforme.

Los dígitos aleatorios de Tippett (simular cualquier distribución con una
uniforme), el índice de la bolsa de Vancouver (errores de truncamiento
uniformes que se acumulan) y la cuerda de Bertrand (qué significa «al azar»).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Band, ColumnDataSource

import civic_ui as ui

TITLE = "La distribución uniforme"
SYMBOL = "U(a,b)"
PAGE = "04_02"

TARGETS = {"exp": "Exponencial", "billiard": "Bola de Bayes", "unif": "Uniforme [a, b]"}
METHODS = {"ends": "Extremos al azar", "radius": "Distancia al centro", "mid": "Punto medio"}
THEORY = {"ends": 1 / 3, "radius": 1 / 2, "mid": 1 / 4}
SIDE = np.sqrt(3)


def initial_values():
    return {
        "target": ui.dchoice("exp", list(TARGETS), "target"),
        "per_day": ui.dchoice(3000, [1000, 2000, 3000, 4000], "per_day"),
        "days": 10 * round(ui.dint(460, 100, 600, "days") / 10),
        "method": ui.dchoice("ends", list(METHODS), "method"),
        "seed": int(ui.r("chords") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "target": None, "method": None, "chord_round": 0,
                   "tippett_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def billiard_inverse(u):
    xs = np.linspace(0, 1, 2001)
    cdf = 4 * xs ** 3 - 3 * xs ** 4
    return np.interp(u, cdf, xs)


def transform(target: str, u):
    if target == "exp":
        return -np.log(1 - u)
    if target == "billiard":
        return billiard_inverse(u)
    return 2 + 3 * u


def target_density(target: str, xs):
    if target == "exp":
        return np.where(xs >= 0, np.exp(-xs), 0.0)
    if target == "billiard":
        return np.where((xs >= 0) & (xs <= 1), 12 * xs ** 2 * (1 - xs), 0.0)
    return np.where((xs >= 2) & (xs <= 5), 1 / 3, 0.0)


def target_range(target: str):
    return {"exp": (0, 6), "billiard": (0, 1), "unif": (1, 6)}[target]


def draw_chords(method: str, n: int, rng):
    if method == "ends":
        t1, t2 = rng.uniform(0, 2 * np.pi, n), rng.uniform(0, 2 * np.pi, n)
        x0, y0, x1, y1 = np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)
    else:
        if method == "radius":
            phi = rng.uniform(0, 2 * np.pi, n)
            d = rng.uniform(0, 1, n)
        else:
            phi = rng.uniform(0, 2 * np.pi, n)
            d = np.sqrt(rng.uniform(0, 1, n))
        half = np.sqrt(1 - d ** 2)
        mx, my = d * np.cos(phi), d * np.sin(phi)
        x0, y0 = mx - half * np.sin(phi), my + half * np.cos(phi)
        x1, y1 = mx + half * np.sin(phi), my - half * np.cos(phi)
    length = np.hypot(x1 - x0, y1 - y0)
    return x0, y0, x1, y1, length


# =============================================================================
# 2. FIGURAS
# =============================================================================

def tippett_chart(dark, target: str, sample):
    lo, hi = target_range(target)
    xs = np.linspace(lo, hi, 400)
    dens = target_density(target, xs)
    p = ui.new_figure(dark, height=300, x_axis_label="x = F⁻¹(U)", y_axis_label="densidad", x_range=(lo, hi),
                      y_range=(0, dens.max() * 1.3))
    edges = np.linspace(lo, hi, 41)
    hist, _ = np.histogram(sample, bins=edges)
    width = edges[1] - edges[0]
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(sample) * width), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.6, line_color=None, legend_label="F⁻¹ de dígitos uniformes")
    p.line(xs, dens, line_width=4, color=ui.BLUE_LINE, legend_label="densidad objetivo")
    return ui.style_legend(p, dark, "top_right")


def drift_chart(dark, per_day: int, days: int, rng):
    d = np.arange(0, days + 1)
    n = d * per_day
    step = 0.001
    p = ui.new_figure(dark, height=320, x_axis_label="días de cotización", y_axis_label="error acumulado (puntos)",
                      x_range=(0, days))
    trunc_mean = n * step / 2
    sd = np.sqrt(n / 12) * step
    src = ColumnDataSource(dict(x=d, lo=trunc_mean - 2 * sd, hi=trunc_mean + 2 * sd))
    p.add_layout(Band(base="x", lower="lo", upper="hi", source=src, fill_color=ui.RED_LINE, fill_alpha=0.15))
    p.line(d, trunc_mean, line_width=4, color=ui.RED_LINE, legend_label="truncando: media")
    daily_round = rng.normal(0, np.sqrt(per_day / 12) * step, days)
    p.line(d, np.concatenate(([0], np.cumsum(daily_round))), line_width=3, color=ui.GREEN_LINE,
           legend_label="redondeando: una trayectoria")
    return ui.style_legend(p, dark, "top_left")


def chords_chart(dark, x0, y0, x1, y1, length, show: int = 160):
    p = ui.new_figure(dark, height=340, x_range=(-1.1, 1.1), y_range=(-1.1, 1.1), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    fg = "#e6e6e6" if dark else "#333333"
    p.circle(x=[0], y=[0], radius=1, fill_alpha=0, line_color=fg, line_width=2)
    long = length[:show] > SIDE
    for mask, colour, alpha in ((~long, ui.GREY_LINE, 0.35), (long, ui.UBU_RED, 0.75)):
        idx = np.where(mask)[0]
        p.multi_line([[x0[i], x1[i]] for i in idx], [[y0[i], y1[i]] for i in idx], line_color=colour,
                     line_alpha=alpha, line_width=1.5)
    tri = np.array([np.pi / 2, np.pi / 2 + 2 * np.pi / 3, np.pi / 2 + 4 * np.pi / 3, np.pi / 2])
    p.line(np.cos(tri), np.sin(tri), line_color=ui.BLUE_LINE, line_width=3)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué significa «al azar» en un intervalo?</b>")
        ui.content(
            "La distribución uniforme en [a, b] es la idealización de una variable que se sabe que está entre "
            "dos límites y de la que no hay motivo para pensar que unos valores sean más frecuentes que otros: "
            "todos los subintervalos de la misma longitud tienen la misma probabilidad. <i>Escribe su "
            "densidad.</i>"
        )
        ui.formula_hidden("f(x) = <sup>1</sup>&frasl;<sub>b &minus; a</sub> si x &isin; [a, b], &nbsp; 0 en el resto")
        ui.content("<i>Calcula su media y su varianza integrando.</i>")
        ui.formula_hidden("&#120124;[X] = <sup>a + b</sup>&frasl;<sub>2</sub> &nbsp;&nbsp; &#120141;(X) = "
                          "<sup>(b &minus; a)<sup>2</sup></sup>&frasl;<sub>12</sub>")
        ui.content(
            "La uniforme en [0, 1] tiene un papel especial: a partir de ella se puede simular cualquier otra "
            "distribución, y por eso los ordenadores dedican tanto esfuerzo a producir números que lo parezcan."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los dígitos de Tippett (1927)</b><br>"
            "<i>Convierte con Leonard Tippett una lista de cifras al azar en cualquier distribución que "
            "quieras.</i><br><br>"
            "<b>II. La bolsa de Vancouver (1982)</b><br>"
            "<i>Un índice que perdía puntos sin que nadie vendiera nada, por culpa de una uniforme mal "
            "centrada.</i><br><br>"
            "<b>III. La cuerda de Bertrand (1889)</b><br>"
            "<i>Traza una cuerda al azar en un círculo y obtén tres respuestas distintas a la misma "
            "pregunta.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>distribución objetivo</u>")
        if st.session_state["target"] is None:
            st.session_state["target"] = v["target"]
        ui.choice_buttons(list(TARGETS), "target", labels=TARGETS, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>Los dígitos de Tippett (1927)</b><br><br>"
            "Leonard Tippett, estadístico de la industria textil, necesitaba números al azar para sus "
            "experimentos de muestreo. Karl Pearson le sugirió tomar cifras de los informes del censo, y así "
            "nació la primera tabla publicada de dígitos aleatorios: 41 600 cifras. Agrupando cuatro cifras "
            "seguidas se obtiene un número U = 0.dddd prácticamente uniforme en [0, 1]. ¿Cómo se fabrica con él "
            "una duración exponencial, o la posición de la bola de Bayes?"
        )

        if ui.accordion_step("P1_A", "(A) La uniforme"):
            ui.content(
                "Calcula la media y la varianza de una uniforme en [a, b]. ¿Qué distribución tiene a + (b &minus; "
                "a)U si U es uniforme en [0, 1]?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124;[X] = &int;<sub>a</sub><sup>b</sup> <sup>x</sup>&frasl;<sub>b &minus; a</sub> dx = "
                "<sup>a + b</sup>&frasl;<sub>2</sub> &nbsp;&nbsp; &#120124;[X<sup>2</sup>] = <sup>a<sup>2</sup> + ab + "
                "b<sup>2</sup></sup>&frasl;<sub>3</sub> &nbsp;&rArr;&nbsp; &#120141;(X) = <sup>(b &minus; a)<sup>2</sup></sup>"
                "&frasl;<sub>12</sub></div>"
                "Una transformación lineal estira y desplaza el intervalo sin cambiar la forma: a + (b &minus; a)U "
                "es uniforme en [a, b]. Es la opción <i>Uniforme [a, b]</i>, con a = 2 y b = 5."
            )

        if ui.accordion_step("P1_B", "(B) El método de la inversa"):
            ui.content(
                "Sea F una función de distribución continua y estrictamente creciente, y X = F<sup>&minus;1</sup>(U). "
                "Calcula &#8473;(X &le; x). ¿Qué fórmula da una exponencial de media 1?"
            )
            ui.spoiler(
                "Como F es creciente, {F<sup>&minus;1</sup>(U) &le; x} = {U &le; F(x)}, y para una uniforme en "
                "[0, 1] esa probabilidad es F(x):"
                "<div class='formula-box'>&#8473;(F<sup>&minus;1</sup>(U) &le; x) = &#8473;(U &le; F(x)) = F(x)</div>"
                "Para la exponencial, F(x) = 1 &minus; e<sup>&minus;x</sup> y X = &minus;ln(1 &minus; U). Para la bola "
                "de Bayes, F(x) = 4x<sup>3</sup> &minus; 3x<sup>4</sup> no se invierte a mano, y la aplicación lo "
                "hace numéricamente."
            )

        if ui.accordion_step("P1_C", "(C) ¿De dónde sale el azar?"):
            ui.content(
                "Las cifras del censo no se diseñaron para ser aleatorias. ¿Qué tendría que cumplir una tabla "
                "para servir? ¿Y los números que produce un ordenador, que sigue instrucciones fijas?"
            )
            ui.spoiler(
                "Cada cifra debería aparecer con frecuencia 1/10, cada pareja con frecuencia 1/100, y así "
                "sucesivamente, sin dependencias entre cifras cercanas: Kendall y Babington Smith propusieron "
                "pruebas para comprobarlo poco después. Los ordenadores usan fórmulas deterministas cuyos "
                "resultados superan esas pruebas: números <i>pseudoaleatorios</i>. Toda simulación de esta "
                "aplicación empieza con ellos y termina, a menudo, con el método de la inversa."
            )

    with col_right:
        ui.right_panel()
        target = st.session_state["target"]
        if st.button("Otros 4000 números", key="tippett_new", width="stretch"):
            st.session_state["tippett_round"] += 1
        rng = np.random.default_rng(v["seed"] + 7 * st.session_state["tippett_round"])
        digits = rng.integers(0, 10, size=(4000, 4))
        u = (digits * np.array([1e-1, 1e-2, 1e-3, 1e-4])).sum(axis=1) + 5e-5
        sample = transform(target, u)
        ui.metrics([(f"Media de U = {u.mean():.4f}", "metric-c"),
                    (f"Media de F<sup>&minus;1</sup>(U) = {sample.mean():.4f}", "metric-a")])
        ui.show(tippett_chart(dark, target, sample), key="fig_tippett")
        first = " ".join("".join(map(str, row)) for row in digits[:6])
        ui.footer_bar(f"Primeros grupos de cuatro cifras: {first}&hellip; Cada grupo es un U; el histograma muestra "
                      f"F<sup>&minus;1</sup>(U) para la distribución {TARGETS[target].lower()}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>actualizaciones por día</u> y los <u>días</u>")
        c1, c2 = st.columns(2)
        per_day = c1.select_slider("Actualizaciones por día", options=[500, 1000, 2000, 3000, 4000], value=v["per_day"],
                                   key=ui.wkey(PAGE, "per_day"))
        days = c2.slider("Días de cotización", 20, 600, v["days"], 10, key=ui.wkey(PAGE, "days"))

        ui.planteamiento()
        ui.statement(
            "<b>La bolsa de Vancouver (1982)</b><br><br>"
            "En enero de 1982 la bolsa de Vancouver estrenó un índice que valía 1000. Se recalculaba con cada "
            "operación, unas tres mil veces al día, y en cada recálculo se conservaban tres decimales "
            "<i>cortando</i> los demás en lugar de redondear. En noviembre de 1983 el índice marcaba 524.811, "
            "aunque el mercado no había caído: recalculado correctamente, valía 1098.892. ¿Adónde fueron los "
            "puntos?"
        )

        if ui.accordion_step("P2_A", "(A) El error de un corte"):
            ui.content(
                "Al cortar en la tercera cifra decimal se pierde la parte que sigue, un número entre 0 y 0.001. "
                "Si esas cifras descartadas son como cifras al azar, ¿qué distribución tiene el error E? Calcula "
                "su media y su varianza."
            )
            ui.spoiler(
                "E es uniforme en [0, 0.001):"
                "<div class='formula-box'>&#120124;[E] = 0.0005 &nbsp;&nbsp; &#120141;(E) = <sup>0.001<sup>2</sup></sup>"
                "&frasl;<sub>12</sub></div>"
                "Un error minúsculo y, sobre todo, siempre del mismo signo: cortar nunca suma, solo resta."
            )

        if ui.accordion_step("P2_B", "(B) Miles de cortes"):
            ui.content(
                "Tras n recálculos el error acumulado es la suma de n errores independientes como el anterior. "
                "¿Cómo crecen su media y su desviación típica? ¿Qué domina?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124;[&sum; E<sub>i</sub>] = 0.0005&middot;n &nbsp;&nbsp; "
                "&sigma;(&sum; E<sub>i</sub>) = 0.001&middot;&radic;(n/12)</div>"
                "La media crece como n y la dispersión solo como &radic;n: el sesgo domina por completo. Con "
                "tres mil recálculos al día se pierde punto y medio diario, y en los aproximadamente 460 días "
                "de cotización transcurridos el modelo predice una pérdida del mismo orden que la observada."
            )

        if ui.accordion_step("P2_C", "(C) Redondear"):
            ui.content(
                "Si se redondea en lugar de cortar, el error es uniforme en [&minus;0.0005, 0.0005). ¿Cómo cambian "
                "la media y la varianza del error acumulado? Compara las dos curvas de la derecha."
            )
            ui.spoiler(
                "La varianza es la misma, pero la media pasa a ser cero: el error acumulado ya no deriva, solo "
                "fluctúa, y en el peor de los casos razonables se aleja del orden de 0.001&middot;&radic;(n/12), "
                "unas décimas de punto tras años de cotización. El problema de Vancouver no era la "
                "imprecisión, sino una uniforme mal centrada."
            )

    with col_right:
        ui.right_panel()
        n = per_day * days
        mean_loss = 0.0005 * n
        sd = 0.001 * np.sqrt(n / 12)
        ui.metrics([(f"Pérdida media truncando: {mean_loss:.1f} puntos", "result-no"),
                    (f"&sigma; del error redondeando: {sd:.3f}", "result-yes")])
        ui.show(drift_chart(dark, per_day, days, np.random.default_rng(v["seed"])), key="fig_vancouver")
        ui.footer_bar(f"Tras {ui.fmt_int(n)} recálculos, cortar resta de media {mean_loss:.1f} puntos (banda roja: "
                      "media &plusmn; 2&sigma;); redondear deja un error que oscila alrededor de cero.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>método para trazar la cuerda</u>")
        if st.session_state["method"] is None:
            st.session_state["method"] = v["method"]
        ui.choice_buttons(list(METHODS), "method", labels=METHODS, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>La cuerda de Bertrand (1889)</b><br><br>"
            "En el mismo libro de la caja de las monedas, Joseph Bertrand propuso este problema: se traza una "
            "cuerda al azar en un círculo. ¿Qué probabilidad hay de que sea más larga que el lado del "
            "triángulo equilátero inscrito? Bertrand dio tres razonamientos, todos aparentemente "
            "impecables, con tres respuestas distintas."
        )

        if ui.accordion_step("P3_A", "(A) Extremos al azar"):
            ui.content(
                "Elige los dos extremos de la cuerda con ángulos uniformes e independientes en la circunferencia. "
                "Fija el primero en un vértice del triángulo: ¿dónde tiene que caer el segundo?"
            )
            ui.spoiler(
                "La cuerda es más larga que el lado si el segundo extremo cae en el arco opuesto al vértice, que "
                "es un tercio de la circunferencia. Por la uniformidad del ángulo: &#8473; = 1/3."
            )

        if ui.accordion_step("P3_B", "(B) Distancia al centro uniforme"):
            ui.content(
                "Elige un radio al azar y, sobre él, la distancia d del punto medio de la cuerda al centro, uniforme "
                "en [0, 1]. ¿Para qué valores de d es la cuerda más larga que el lado?"
            )
            ui.spoiler(
                "El lado del triángulo está a distancia 1/2 del centro, y una cuerda es más larga si está más "
                "cerca: d &lt; 1/2. Con d uniforme en [0, 1], &#8473; = 1/2."
            )

        if ui.accordion_step("P3_C", "(C) Punto medio uniforme en el círculo"):
            ui.content(
                "Elige el punto medio de la cuerda uniformemente en el círculo, con probabilidad proporcional al "
                "área. ¿Qué región corresponde a las cuerdas largas? ¿Cuál de las tres respuestas es la buena?"
            )
            ui.spoiler(
                "Las cuerdas largas tienen el punto medio en el círculo concéntrico de radio 1/2, de área un "
                "cuarto de la total: &#8473; = 1/4. No hay respuesta buena: <i>al azar</i> no significa nada "
                "hasta que se fija la distribución, y cada método la reparte de una forma. Edwin Jaynes defendió "
                "en 1973 que, si el problema no debe depender de la posición ni del tamaño del círculo, solo el "
                "segundo método es coherente; pero esa es una hipótesis más, no una consecuencia de la palabra."
            )

    with col_right:
        ui.right_panel()
        method = st.session_state["method"]
        if st.button("Trazar otras 3000 cuerdas", key="chord_new", width="stretch"):
            st.session_state["chord_round"] += 1
        rng = np.random.default_rng(v["seed"] + st.session_state["chord_round"])
        x0, y0, x1, y1, length = draw_chords(method, 3000, rng)
        freq = float((length > SIDE).mean())
        ui.metrics([(f"Frecuencia de cuerdas largas: {freq:.4f}", "metric-a"),
                    (f"Teoría: {THEORY[method]:.4f}", "metric-c")])
        ui.show(chords_chart(dark, x0, y0, x1, y1, length), key="fig_chords")
        ui.footer_bar(f"Método «{METHODS[method].lower()}»: en rojo, las cuerdas más largas que el lado del triángulo. "
                      "Se dibujan 160 de las 3000 simuladas.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los dígitos de Tippett", "P1_A"),
        ("P2", "(II) La bolsa de Vancouver", "P2_A"),
        ("P3", "(III) La cuerda de Bertrand", "P3_A"),
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
