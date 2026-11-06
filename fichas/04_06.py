#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 6: la distribución beta.

La salida del sol de Laplace (la regla de sucesión con una beta a priori),
la subasta de Vickrey (el máximo y el segundo mayor de varias uniformes) y el
dilema de Thompson (decidir aprendiendo con posteriores beta).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "La distribución beta"
SYMBOL = "β(a,b)"
PAGE = "04_06"

PATIENTS = 300


def initial_values():
    return {
        "n": ui.dint(10, 5, 40, "n"),
        "k": ui.dint(10, 3, 10, "k"),
        "a": ui.dchoice(1.0, [0.5, 1.0, 2.0], "a"),
        "b": ui.dchoice(1.0, [0.5, 1.0, 2.0], "b"),
        "bidders": ui.dint(5, 2, 12, "bidders"),
        "pA": ui.dchoice(0.45, [0.30, 0.40, 0.45, 0.50], "pA"),
        "pB": ui.dchoice(0.60, [0.55, 0.60, 0.65, 0.70], "pB"),
        "seed": int(ui.r("thompson") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "auctions": None, "trial_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def simulate_auctions(n: int, trials: int, rng):
    values = np.sort(rng.uniform(0, 1, (trials, n)), axis=1)
    return values[:, -1], values[:, -2]


def thompson_trial(pA: float, pB: float, seed: int, adaptive: bool):
    rng = np.random.default_rng(seed)
    succ, fail = np.zeros(2), np.zeros(2)
    choices = []
    for i in range(PATIENTS):
        if adaptive:
            draws = rng.beta(1 + succ, 1 + fail)
            arm = int(np.argmax(draws))
        else:
            arm = i % 2
        ok = rng.random() < (pA, pB)[arm]
        succ[arm] += ok
        fail[arm] += 1 - ok
        choices.append(arm)
    return succ, fail, np.array(choices)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def posterior_chart(dark, a: float, b: float, n: int, k: int):
    xs = np.linspace(0.001, 0.999, 400)
    prior = stats.beta.pdf(xs, a, b)
    post = stats.beta.pdf(xs, a + k, b + n - k)
    cap = float(min(max(post.max(), prior.max()), 40)) * 1.1
    p = ui.new_figure(dark, height=300, x_axis_label="probabilidad p de que salga el sol", y_axis_label="densidad",
                      x_range=(0, 1), y_range=(0, cap))
    p.line(xs, np.minimum(prior, cap), line_width=3, color=ui.GREY_LINE, line_dash="dashed", legend_label="a priori")
    p.line(xs, np.minimum(post, cap), line_width=4, color=ui.ORANGE_LINE,
           legend_label=f"a posteriori β({a + k:g}, {b + n - k:g})")
    p.add_layout(Span(location=(a + k) / (a + b + n), dimension="height", line_color=ui.UBU_RED, line_width=2))
    return ui.style_legend(p, dark, "top_left")


def auction_chart(dark, n: int, sample):
    xs = np.linspace(0, 1, 400)
    p = ui.new_figure(dark, height=300, x_axis_label="valoración (miles de tharni)", y_axis_label="densidad",
                      x_range=(0, 1))
    if sample is not None:
        edges = np.linspace(0, 1, 41)
        h2, _ = np.histogram(sample[1], bins=edges)
        p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h2 / (len(sample[1]) * 0.025),
               fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None, legend_label="segunda puja simulada")
    p.line(xs, stats.beta.pdf(xs, n, 1), line_width=4, color=ui.BLUE_LINE, legend_label=f"máximo: β({n}, 1)")
    p.line(xs, stats.beta.pdf(xs, n - 1, 2), line_width=4, color=ui.UBU_RED, legend_label=f"segunda: β({n - 1}, 2)")
    return ui.style_legend(p, dark, "top_left")


def thompson_chart(dark, succ, fail):
    xs = np.linspace(0.001, 0.999, 400)
    p = ui.new_figure(dark, height=280, x_axis_label="probabilidad de curación", y_axis_label="densidad a posteriori",
                      x_range=(0, 1))
    for arm, colour, label in ((0, ui.BLUE_LINE, "tratamiento A"), (1, ui.GREEN_LINE, "tratamiento B")):
        p.line(xs, stats.beta.pdf(xs, 1 + succ[arm], 1 + fail[arm]), line_width=4, color=colour,
               legend_label=f"{label}: β({1 + succ[arm]:.0f}, {1 + fail[arm]:.0f})")
    return ui.style_legend(p, dark, "top_left")


def allocation_chart(dark, choices):
    idx = np.arange(1, len(choices) + 1)
    share = np.cumsum(choices) / idx
    p = ui.new_figure(dark, height=200, x_axis_label="pacientes", y_axis_label="fracción con B",
                      x_range=(0, len(choices)), y_range=(0, 1))
    p.line(idx, share, line_width=3, color=ui.GREEN_LINE)
    p.add_layout(Span(location=0.5, dimension="width", line_color=ui.GREY_LINE, line_dash="dotted"))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué distribución describe una proporción desconocida?</b>")
        ui.content(
            "La distribución beta vive en el intervalo (0, 1) y es el modelo natural para una proporción o una "
            "probabilidad desconocida. Depende de dos parámetros positivos p y q que controlan su forma. "
            "<i>Escribe su densidad.</i>"
        )
        ui.formula_hidden("f(x) = <sup>1</sup>&frasl;<sub>B(p, q)</sub> x<sup>p&minus;1</sup>(1 &minus; x)<sup>q&minus;1</sup>, "
                          "&nbsp; B(p, q) = <sup>&Gamma;(p)&Gamma;(q)</sup>&frasl;<sub>&Gamma;(p + q)</sub>")
        ui.content(
            "Su media es p/(p + q). Con p = q = 1 es la uniforme en (0, 1); ya apareció en la mesa de billar de "
            "Bayes. Tiene dos propiedades que la hacen omnipresente: si la proporción tiene una distribución beta "
            "y se observan ensayos de Bernoulli, la distribución actualizada sigue siendo beta; y el k-ésimo "
            "menor de n números uniformes al azar también es una beta."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La salida del sol (1814)</b><br>"
            "<i>¿Qué probabilidad hay de que mañana salga el sol? Pierre-Simon Laplace se atrevió a dar un "
            "número.</i><br><br>"
            "<b>II. La subasta de Vickrey (1961)</b><br>"
            "<i>Vende un cuadro al mejor postor cobrando la segunda puja, y calcula con William Vickrey cuánto "
            "ingresas.</i><br><br>"
            "<b>III. El dilema de Thompson (1933)</b><br>"
            "<i>Dos tratamientos, pacientes que llegan uno a uno y una forma de aprender sin dejar de curar.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>días observados n</u>, los <u>éxitos k</u> y la <u>distribución a priori</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Días observados n", 0, 60, v["n"], 1, key=ui.wkey(PAGE, "n"))
        k = c2.slider("Días en que salió el sol k", 0, n, min(v["k"], n), 1, key=ui.wkey(PAGE, f"k{n}"))
        c3, c4 = st.columns(2)
        a = c3.select_slider("A priori: a", options=[0.5, 1.0, 2.0, 5.0], value=v["a"], key=ui.wkey(PAGE, "a"))
        b = c4.select_slider("A priori: b", options=[0.5, 1.0, 2.0, 5.0], value=v["b"], key=ui.wkey(PAGE, "b"))

        ui.planteamiento()
        ui.statement(
            "<b>La salida del sol (1814)</b><br><br>"
            "En su <i>Ensayo filosófico sobre las probabilidades</i>, Laplace planteó una pregunta provocadora: si "
            "el sol ha salido todos los días desde que hay registros, ¿qué probabilidad hay de que salga mañana? "
            "Su modelo: cada día el sol sale con una probabilidad p desconocida, de forma independiente, y antes "
            "de mirar no hay motivo para preferir ningún valor de p, así que se toma uniforme. Tras observar n "
            "días con k salidas, ¿qué se sabe de p?"
        )

        if ui.accordion_step("P1_A", "(A) De la a priori a la a posteriori"):
            ui.content(
                "Aplica el teorema de Bayes a la densidad de p: la a posteriori es proporcional a la a priori por la "
                "verosimilitud de lo observado. Si la a priori es β(a, b), ¿qué distribución tiene la a posteriori "
                "tras k éxitos en n ensayos?"
            )
            ui.spoiler(
                "<div class='formula-box'>f(p | datos) &prop; p<sup>a&minus;1</sup>(1 &minus; p)<sup>b&minus;1</sup>&middot;"
                "p<sup>k</sup>(1 &minus; p)<sup>n&minus;k</sup> = p<sup>a+k&minus;1</sup>(1 &minus; p)<sup>b+n&minus;k&minus;1</sup></div>"
                "Es otra beta, de parámetros a + k y b + n &minus; k: los éxitos se suman a un parámetro y los "
                "fracasos al otro. Que la a priori y la a posteriori sean de la misma familia es lo que hace a la "
                "beta tan cómoda."
            )

        if ui.accordion_step("P1_B", "(B) La regla de sucesión"):
            ui.content(
                "La probabilidad de éxito en el ensayo siguiente es la media de la a posteriori. Calcúlala con la "
                "a priori uniforme. ¿Qué da con k = n, todo éxitos?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(éxito mañana | k de n) = <sup>k + 1</sup>&frasl;<sub>n + 2</sub></div>"
                "Es la regla de sucesión de Laplace: como si a los datos se añadieran un éxito y un fracaso "
                "imaginarios. Con todo éxitos da (n + 1)/(n + 2), que nunca llega a 1: ninguna cantidad finita de "
                "observaciones da certeza."
            )

        if ui.accordion_step("P1_C", "(C) Cinco mil años de amaneceres"):
            ui.content(
                "Laplace tomó 5000 años de historia, 1 826 213 días con sol. ¿Qué probabilidad da la regla? ¿Qué le "
                "reprocharías al modelo?"
            )
            ui.spoiler(
                "Da unas apuestas de 1 826 214 contra 1 a favor de que salga mañana, la cifra que publicó Laplace. "
                "Él mismo advirtió que quien conoce las leyes de la mecánica celeste tiene una certeza mucho mayor: "
                "el modelo trata los amaneceres como extracciones independientes de una urna y la a priori uniforme "
                "como si no supiéramos nada. Una a priori distinta cambia la respuesta, sobre todo con pocos datos: "
                "pruébalo con los deslizadores."
            )

    with col_right:
        ui.right_panel()
        mean = (a + k) / (a + b + n)
        ui.metrics([(f"&#8473;(sale mañana) = {mean:.4f}", "metric-a"),
                    (f"Laplace con a priori uniforme: {(k + 1) / (n + 2):.4f}", "metric-c")])
        ui.show(posterior_chart(dark, a, b, n, k), key="fig_sunrise")
        ui.footer_bar(f"A posteriori β({a + k:g}, {b + n - k:g}); la línea roja es su media, la probabilidad de éxito "
                      "en el ensayo siguiente.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de pujadores n</u>")
        n = st.slider("Pujadores n", 2, 20, v["bidders"], 1, key=ui.wkey(PAGE, "bidders"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La subasta de Vickrey (1961)</b><br><br>"
            "William Vickrey, premio Nobel de Economía en 1996, analizó una subasta en sobre cerrado en la que "
            "gana la puja más alta pero se paga la segunda. Con esa regla a nadie le conviene mentir: lo mejor es "
            "pujar exactamente lo que vale el objeto para uno. Subastamos un cuadro ante n pujadores cuyas "
            "valoraciones, en miles de tharni, son uniformes en (0, 1) e independientes. ¿Cuánto ingresa el "
            "vendedor?"
        )

        if ui.accordion_step("P2_A", "(A) La puja más alta"):
            ui.content(
                "Calcula la función de distribución del máximo de n uniformes, como hiciste con los dados del "
                "Risk, y deriva. ¿Qué beta es? ¿Cuál es su media?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(M &le; x) = x<sup>n</sup> &nbsp;&rArr;&nbsp; f(x) = nx<sup>n&minus;1</sup></div>"
                "Es la β(n, 1), de media n/(n + 1): con muchos pujadores, el que más valora el cuadro lo valora "
                "casi en el máximo."
            )

        if ui.accordion_step("P2_B", "(B) La segunda puja"):
            ui.content(
                "El vendedor cobra la segunda valoración más alta. Para que caiga en (x, x + dx), una valoración debe "
                "caer ahí, otra por encima y las n &minus; 2 restantes por debajo. Cuenta las formas y escribe la "
                "densidad."
            )
            ui.spoiler(
                "Hay n formas de elegir la que cae en x y n &minus; 1 de elegir la que queda por encima:"
                "<div class='formula-box'>f(x) = n(n &minus; 1)x<sup>n&minus;2</sup>(1 &minus; x)</div>"
                "Es la β(n &minus; 1, 2), y el ingreso medio es (n &minus; 1)/(n + 1) miles de tharni. En general, el "
                "k-ésimo menor de n uniformes es una β(k, n &minus; k + 1): los estadísticos ordenados de la uniforme "
                "son betas."
            )

        if ui.accordion_step("P2_C", "(C) ¿Pierde dinero el vendedor?"):
            ui.content(
                "Cobrando la segunda puja parece que el vendedor regala la diferencia. En una subasta en la que se "
                "paga la propia puja, cada pujador puja por debajo de su valoración: con valoraciones uniformes, lo "
                "óptimo es pujar (n &minus; 1)/n de ella. ¿Cuánto ingresa entonces de media?"
            )
            ui.spoiler(
                "El ganador paga (n &minus; 1)/n por la valoración máxima, de media (n &minus; 1)/n &middot; n/(n + 1) = "
                "(n &minus; 1)/(n + 1): exactamente lo mismo. Es un caso del teorema de equivalencia de ingresos: "
                "con pujadores racionales, muchas reglas de subasta distintas dan el mismo ingreso esperado."
            )

        if st.button("Celebrar 5000 subastas", key="auction_play", width="stretch", type="primary"):
            st.session_state["auctions"] = (n, simulate_auctions(n, 5000, np.random.default_rng()))

    with col_right:
        ui.right_panel()
        sim = st.session_state.get("auctions")
        sample = sim[1] if sim and sim[0] == n else None
        items = [(f"&#120124;[ingreso] = {(n - 1) / (n + 1):.4f} miles de tharni", "metric-a")]
        if sample is not None:
            items.append((f"Simulado: {sample[1].mean():.4f}", "metric-c"))
        ui.metrics(items)
        ui.show(auction_chart(dark, n, sample), key="fig_vickrey")
        ui.footer_bar(f"Con {n} pujadores, la valoración máxima tiene media {n / (n + 1):.3f} y la segunda, que es lo que "
                      f"se cobra, {(n - 1) / (n + 1):.3f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>tasas de curación reales</u> de los dos tratamientos")
        c1, c2 = st.columns(2)
        pA = c1.slider("Tratamiento A", 0.05, 0.95, v["pA"], 0.05, key=ui.wkey(PAGE, "pA"))
        pB = c2.slider("Tratamiento B", 0.05, 0.95, v["pB"], 0.05, key=ui.wkey(PAGE, "pB"))
        adaptive = st.toggle("Asignar con la regla de Thompson (si no, alternar A y B)", value=True, key="thompson_on")

        ui.planteamiento()
        ui.statement(
            "<b>El dilema de Thompson (1933)</b><br><br>"
            "William R. Thompson, patólogo en Yale, se preguntó cómo repartir a los pacientes entre dos "
            "tratamientos cuando no se sabe cuál es mejor. Si se reparte a partes iguales, la mitad de los "
            "pacientes recibe el peor durante todo el ensayo; si se elige pronto el que parece mejor, se puede "
            f"elegir mal. En nuestro ensayo llegan {PATIENTS} pacientes, uno a uno, y cada tratamiento cura con una "
            "probabilidad que el médico desconoce."
        )

        if ui.accordion_step("P3_A", "(A) Lo que se sabe de cada tratamiento"):
            ui.content(
                "Con una a priori uniforme para la tasa de curación de cada tratamiento, ¿qué distribución tiene "
                "después de s curaciones y f fracasos? ¿Qué pasa con su anchura a medida que se trata a más "
                "pacientes?"
            )
            ui.spoiler(
                "Como en el problema de Laplace, la a posteriori es una β(1 + s, 1 + f). Su varianza decrece como "
                "1/(s + f): cuantos más pacientes recibe un tratamiento, más estrecha es su curva y mejor se conoce "
                "su eficacia."
            )

        if ui.accordion_step("P3_B", "(B) La regla de Thompson"):
            ui.content(
                "Thompson propuso dar a cada paciente el tratamiento A con una probabilidad igual a la probabilidad, "
                "según lo observado hasta entonces, de que A sea el mejor. Se consigue sacando un valor al azar de "
                "cada a posteriori y eligiendo el mayor. ¿Por qué funciona?"
            )
            ui.spoiler(
                "Si las dos curvas se solapan mucho, los dos tratamientos se eligen a menudo y se sigue aprendiendo. "
                "Si una curva está claramente a la derecha de la otra, su tratamiento gana casi siempre el sorteo y "
                "recibe a casi todos los pacientes. La regla equilibra sola explorar (aprender cuál es mejor) y "
                "explotar (usar el que parece mejor)."
            )

        if ui.accordion_step("P3_C", "(C) Comparar con repartir a medias"):
            ui.content(
                "Desactiva la regla para alternar A y B. ¿Cuántos pacientes más se curan con la regla de Thompson? "
                "¿Qué se pierde a cambio?"
            )
            ui.spoiler(
                "Con la regla, la mayoría de los pacientes acaba recibiendo el mejor tratamiento y se curan más. A "
                "cambio, el peor tratamiento se prueba en pocos pacientes y su eficacia queda peor estimada: su curva "
                "es más ancha. El método quedó olvidado décadas y renació con internet, donde se usa para decidir "
                "qué versión de una página mostrar a cada visitante."
            )

    with col_right:
        ui.right_panel()
        if st.button("Repetir el ensayo", key="trial_new", width="stretch"):
            st.session_state["trial_round"] += 1
        seed = v["seed"] + st.session_state["trial_round"]
        succ, fail, choices = thompson_trial(pA, pB, seed, adaptive)
        better = 1 if pB >= pA else 0
        ui.metrics([(f"Curados: {int(succ.sum())} de {PATIENTS}", "metric-a"),
                    (f"Con el mejor tratamiento: {ui.fmt_pct((choices == better).mean(), 0)}", "metric-c")])
        ui.show(thompson_chart(dark, succ, fail), key="fig_thompson")
        ui.show(allocation_chart(dark, choices), key="fig_allocation")
        ui.footer_bar(f"Curados esperables si todos recibieran el mejor: {PATIENTS * max(pA, pB):.0f}; repartiendo a "
                      f"medias: {PATIENTS * (pA + pB) / 2:.0f}.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La salida del sol", "P1_A"),
        ("P2", "(II) La subasta de Vickrey", "P2_A"),
        ("P3", "(III) El dilema de Thompson", "P3_A"),
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
