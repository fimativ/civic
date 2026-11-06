#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 2: esperanza y varianza.

La paradoja de San Petersburgo (una esperanza infinita y una banca finita),
el café de Lloyd (varianza de una suma de riesgos independientes) y la
fuente del pueblo (la media minimiza el error cuadrático y la mediana el
absoluto).
"""

from __future__ import annotations

from math import floor, log2

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Esperanza y varianza"
SYMBOL = "E[X]"
PAGE = "03_02"

BANKS = [10 ** e for e in range(2, 13)]
HOUSES = np.array([1, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8])


def initial_values():
    return {
        "bank": ui.dchoice(10 ** 6, BANKS[2:9], "bank"),
        "ships": ui.dint(20, 5, 60, "ships"),
        "loss": ui.dchoice(0.05, [0.02, 0.04, 0.05, 0.08, 0.10], "loss"),
        "loading": ui.dchoice(0.20, [0.05, 0.10, 0.20, 0.30, 0.50], "loading"),
        "farm": ui.dint(20, 12, 40, "farm"),
        "c": ui.dfloat(4.0, 2.0, 8.0, "c", 1),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "stp_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def truncated_value(bank: float) -> float:
    """Esperanza del juego si la banca no puede pagar más de `bank` tharni."""
    k0 = floor(log2(bank))
    return k0 + bank / 2 ** k0


def play_stp(games: int, bank: float, rng):
    tosses = rng.geometric(0.5, size=games)
    payout = np.minimum(2.0 ** tosses, bank)
    return np.cumsum(payout) / np.arange(1, games + 1)


def lloyd(n: int, p: float, value: float, loading: float):
    premium = (1 + loading) * p * value
    ks = np.arange(n + 1)
    pmf = stats.binom.pmf(ks, n, p)
    profit = n * premium - ks * value
    p_loss = float(pmf[profit < 0].sum())
    return premium, profit, pmf, p_loss


def village(farm: int):
    positions = np.concatenate((HOUSES, [farm]))
    values, counts = np.unique(positions, return_counts=True)
    probs = counts / counts.sum()
    mean = float((values * probs).sum())
    cdf = np.cumsum(probs)
    median_lo = float(values[np.searchsorted(cdf, 0.5 - 1e-12)])
    median_hi = float(values[np.searchsorted(cdf, 0.5 + 1e-12)])
    mode = float(values[np.argmax(probs)])
    return values, probs, mean, (median_lo, median_hi), mode


def losses(values, probs, cs):
    sq = np.array([(probs * (values - c) ** 2).sum() for c in cs])
    ab = np.array([(probs * np.abs(values - c)).sum() for c in cs])
    return sq, ab


# =============================================================================
# 2. FIGURAS
# =============================================================================

def stp_chart(dark, running, bank):
    xs = np.arange(1, len(running) + 1)
    p = ui.new_figure(dark, height=300, x_axis_type="log", x_axis_label="partidas jugadas",
                      y_axis_label="ganancia media (tharni)")
    p.line(xs, running, line_width=3, color=ui.BLUE_LINE, legend_label="media de la simulación")
    p.add_layout(Span(location=truncated_value(bank), dimension="width", line_color=ui.UBU_RED,
                      line_dash="dashed", line_width=2))
    return ui.style_legend(p, dark, "top_left")


def lloyd_chart(dark, profit, pmf):
    keep = pmf > 1e-5
    colours = [ui.RED_LINE if x < 0 else ui.GREEN_LINE for x in profit[keep]]
    width = abs(profit[1] - profit[0]) * 0.8 if len(profit) > 1 else 1
    p = ui.new_figure(dark, height=300, x_axis_label="beneficio del asegurador (tharni)",
                      y_axis_label="probabilidad")
    p.vbar(x=profit[keep], top=pmf[keep], width=width, fill_color=colours, line_color=None)
    p.add_layout(Span(location=0, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed", line_width=2))
    return p


def village_chart(dark, values, probs, c, mean, median):
    cs = np.linspace(0, max(values) + 2, 400)
    sq, ab = losses(values, probs, cs)
    p = ui.new_figure(dark, height=330, x_axis_label="posición de la fuente c (km)",
                      y_axis_label="coste medio", x_range=(0, max(values) + 2),
                      y_range=(0, float(min(sq.max(), 4 * sq.min() + 20))))
    p.vbar(x=values, top=probs * float(sq.min()) * 2.5, width=0.5, color=ui.GREY_LINE, alpha=0.5,
           legend_label="casas (escala libre)")
    p.line(cs, sq, line_width=4, color=ui.BLUE_LINE, legend_label="𝔼[(X − c)²]")
    p.line(cs, ab * 4, line_width=4, color=ui.GREEN_LINE, line_dash="dashed", legend_label="4·𝔼|X − c|")
    p.add_layout(Span(location=mean, dimension="height", line_color=ui.BLUE_LINE, line_dash="dotted", line_width=2))
    p.add_layout(Span(location=median[0], dimension="height", line_color=ui.GREEN_LINE, line_dash="dotted",
                      line_width=2))
    p.add_layout(Span(location=c, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuánto vale, de media, una variable aleatoria?</b>")
        ui.content(
            "La <b>esperanza</b> de una variable discreta pondera cada valor por su probabilidad: es el "
            "centro de gravedad de la masa de probabilidad, y el promedio al que se acercan las "
            "repeticiones del experimento. <i>Prueba a escribirla.</i>"
        )
        ui.formula_hidden("&#120124;[X] = &sum;<sub>i</sub> x<sub>i</sub> &#8473;(X = x<sub>i</sub>) = &mu;")
        ui.content(
            "Es un operador lineal: &#120124;[aX + b] = a&#120124;[X] + b, y para calcular la esperanza de "
            "una función g(X) no hace falta la distribución de g(X): basta sumar g(x<sub>i</sub>) "
            "ponderado por &#8473;(X = x<sub>i</sub>), la llamada ley del estadístico inconsciente."
        )
        ui.content(
            "Dos variables pueden tener la misma media y comportarse de forma muy distinta. La "
            "<b>varianza</b> mide cuánto se alejan los valores de la media. <i>Escribe su definición y la "
            "fórmula abreviada que se usa para calcularla.</i>"
        )
        ui.formula_hidden("&#120141;(X) = &#120124;[(X &minus; &mu;)<sup>2</sup>] = &#120124;[X<sup>2</sup>] &minus; "
                          "(&#120124;[X])<sup>2</sup> = &sigma;<sup>2</sup>")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La paradoja de San Petersburgo (1738)</b><br>"
            "<i>¿Cuántos tharni pagarías por jugar a un juego cuya ganancia esperada es infinita? "
            "Pregúntaselo a los Bernoulli.</i><br><br>"
            "<b>II. El café de Lloyd (1688)</b><br>"
            "<i>Asegura barcos con los comerciantes de Londres y descubre por qué un asegurador quiere "
            "muchos clientes.</i><br><br>"
            "<b>III. La fuente del pueblo (1774)</b><br>"
            "<i>Decide con Laplace y con Gauss dónde poner la fuente: media, mediana y una masía "
            "lejana.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>capital de la banca</u>")
        bank = st.select_slider("Capital de la banca (tharni)", options=BANKS, value=v["bank"],
                                format_func=lambda x: f"10^{int(round(np.log10(x)))}", key=ui.wkey(PAGE, "bank"))

        ui.planteamiento()
        ui.statement(
            "<b>La paradoja de San Petersburgo (1738)</b><br><br>"
            "En 1713 Nicolaus Bernoulli propuso a Montmort un juego en apariencia inocente: se lanza una "
            "moneda hasta que sale cara; si sale en el lanzamiento k, la banca paga 2<sup>k</sup> tharni. "
            "Su primo Daniel lo estudió en un artículo publicado por la Academia de San Petersburgo, que "
            "dio nombre a la paradoja. ¿Cuánto sería razonable pagar por jugar una partida?"
        )

        if ui.accordion_step("P1_A", "(A) La distribución de la ganancia"):
            ui.content(
                "Sea K el lanzamiento en que sale la primera cara. ¿Cuál es &#8473;(K = k)? ¿Y la función de "
                "probabilidad de la ganancia G = 2<sup>K</sup>?"
            )
            ui.spoiler(
                "Salen k &minus; 1 cruces y luego una cara, de forma independiente: &#8473;(K = k) = "
                "(1/2)<sup>k</sup>. Así, G vale 2, 4, 8, &hellip; con probabilidades 1/2, 1/4, 1/8, &hellip; "
                "Es una función de probabilidad legítima: sus valores suman 1."
            )

        if ui.accordion_step("P1_B", "(B) Una esperanza infinita"):
            ui.content("Calcula &#120124;[G]. ¿Qué precio haría justo el juego en el sentido de Casanova?")
            ui.spoiler(
                "<div class='formula-box'>&#120124;[G] = &sum;<sub>k=1</sub><sup>&infin;</sup> 2<sup>k</sup>"
                "&middot;(1/2)<sup>k</sup> = 1 + 1 + 1 + &hellip; = &infin;</div>"
                "Ningún precio finito haría el juego desfavorable al jugador. Sin embargo, casi nadie "
                "pagaría más de unas decenas de tharni por jugar: la mitad de las veces se cobran solo 2."
            )

        if ui.accordion_step("P1_C", "(C) La banca no es infinita"):
            ui.content(
                "Ninguna banca puede pagar más que su capital C. Si la ganancia es min(2<sup>K</sup>, C), "
                "¿cuánto vale ahora la esperanza? Daniel Bernoulli propuso otra salida: valorar el dinero por "
                "su logaritmo. ¿Cuánto vale &#120124;[log<sub>2</sub> G]?"
            )
            ui.spoiler(
                "Con k<sub>0</sub> = &lfloor;log<sub>2</sub> C&rfloor;, cada uno de los primeros k<sub>0</sub> "
                "términos aporta 1 y la cola aporta C&middot;2<sup>&minus;k<sub>0</sub></sup>:"
                "<div class='formula-box'>&#120124;[min(2<sup>K</sup>, C)] = k<sub>0</sub> + "
                "C&middot;2<sup>&minus;k<sub>0</sub></sup> &asymp; log<sub>2</sub> C + 1</div>"
                "Una banca con un billón de tharni solo justifica pagar unos 41. Y con la utilidad "
                "logarítmica de Daniel, &#120124;[log<sub>2</sub> G] = &sum; k/2<sup>k</sup> = 2: el juego "
                "vale lo mismo que 2<sup>2</sup> = 4 tharni seguros."
            )

    with col_right:
        ui.right_panel()
        value = truncated_value(bank)
        ui.metrics([
            (f"Esperanza con la banca limitada: {value:.2f} tharni", "metric-a"),
            ("Esperanza sin límite: &infin;", "metric-c"),
        ])
        if st.button("Jugar 100 000 partidas", key="stp_play", width="stretch", type="primary"):
            st.session_state["stp_sim"] = (bank, play_stp(100000, bank, np.random.default_rng()))
        sim = st.session_state.get("stp_sim")
        if sim and sim[0] == bank:
            ui.show(stp_chart(dark, sim[1], bank), key="fig_stp")
            ui.footer_bar(f"Tras 100 000 partidas la ganancia media es {sim[1][-1]:.2f} tharni. La línea roja "
                          "marca la esperanza con la banca limitada. Repite: la media salta cada vez que aparece "
                          "una racha larga de cruces.")
        else:
            ui.footer_bar("Pulsa el botón para jugar y seguir la ganancia media partida a partida.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>barcos asegurados n</u>, el <u>riesgo p</u> y el <u>recargo</u>")
        n = st.slider("Barcos asegurados n", 1, 200, v["ships"], 1, key=ui.wkey(PAGE, "ships"))
        c1, c2 = st.columns(2)
        p = c1.select_slider("Probabilidad de naufragio p", options=[0.02, 0.04, 0.05, 0.08, 0.10],
                             value=v["loss"], key=ui.wkey(PAGE, "loss"))
        loading = c2.select_slider("Recargo sobre la prima justa", options=[0.0, 0.05, 0.10, 0.20, 0.30, 0.50],
                                   value=v["loading"], format_func=lambda x: f"{int(round(x * 100))}%",
                                   key=ui.wkey(PAGE, "loading"))

        ui.planteamiento()
        ui.statement(
            "<b>El café de Lloyd (1688)</b><br><br>"
            "En el café de Edward Lloyd, junto al puerto de Londres, se reunían capitanes, armadores y "
            "comerciantes dispuestos a cubrir con su dinero el riesgo de los barcos: los suscriptores. "
            "Cada barco vale 1000 tharni y naufraga en un viaje con probabilidad p, de forma independiente "
            "de los demás. El suscriptor cobra a cada armador una prima y paga el valor del barco si se "
            "hunde."
        )

        if ui.accordion_step("P2_A", "(A) Un solo barco"):
            ui.content(
                "Sea X la indemnización por un barco: 1000 tharni con probabilidad p y 0 si llega a puerto. "
                "Calcula &#120124;[X] y &#120141;(X). ¿Cuál es la prima justa?"
            )
            ui.spoiler(
                "X = 1000&middot;B con B de Bernoulli de parámetro p. Por la linealidad de la esperanza y "
                "porque &#120141;(aX) = a<sup>2</sup>&#120141;(X):"
                "<div class='formula-box'>&#120124;[X] = 1000p &nbsp;&nbsp; &#120141;(X) = 1000<sup>2</sup>"
                "&middot;p(1 &minus; p)</div>"
                "La prima justa es 1000p tharni. Con un solo barco, el suscriptor gana la prima casi siempre "
                "y de vez en cuando lo pierde casi todo: la desviación típica es mucho mayor que la media."
            )

        if ui.accordion_step("P2_B", "(B) Muchos barcos"):
            ui.content(
                "Con n barcos independientes, la indemnización total es la suma de n variables como la "
                "anterior. ¿Cómo crecen su media y su desviación típica? ¿Y las de la indemnización por barco?"
            )
            ui.spoiler(
                "La esperanza de una suma es siempre la suma de las esperanzas, y la varianza de una suma de "
                "variables independientes es la suma de las varianzas:"
                "<div class='formula-box'>&#120124;[S<sub>n</sub>] = 1000np &nbsp;&nbsp; "
                "&sigma;(S<sub>n</sub>) = 1000&radic;(np(1 &minus; p))</div>"
                "La media crece como n y la desviación como &radic;n: por barco, el riesgo cae como "
                "1/&radic;n. Ese es todo el negocio del seguro: agrupar riesgos independientes."
            )

        if ui.accordion_step("P2_C", "(C) El recargo"):
            ui.content(
                "Con la prima justa, ¿qué probabilidad tiene el suscriptor de perder dinero? Añade un "
                "recargo sobre la prima justa y aumenta n. ¿Qué ocurre?"
            )
            ui.spoiler(
                "Con la prima justa el beneficio tiene media cero y la probabilidad de pérdida no tiende a "
                "cero por muchos barcos que se aseguren: al crecer n se acerca a un medio. Con un recargo, el beneficio medio "
                "crece como n mientras su desviación crece como &radic;n, y la probabilidad de pérdida cae "
                "hacia cero: la desigualdad de Chebyshev, en la ficha siguiente, lo convierte en una cota. "
                "La condición, otra vez, es la independencia: una tormenta que hunda a la vez muchos barcos "
                "de la misma flota rompe el cálculo."
            )

    with col_right:
        ui.right_panel()
        premium, profit, pmf, p_loss = lloyd(n, p, 1000, loading)
        mean_profit = n * (premium - 1000 * p)
        sd_profit = 1000 * np.sqrt(n * p * (1 - p))
        ui.metrics([
            (f"&#8473;(pérdida) = {p_loss:.4f}", "result-no" if p_loss > 0.1 else "result-yes"),
            (f"Beneficio: media {mean_profit:.0f}, &sigma; {sd_profit:.0f}", "metric-a"),
        ])
        ui.show(lloyd_chart(dark, profit, pmf), key="fig_lloyd")
        ui.footer_bar(f"Prima por barco: {premium:.1f} tharni. Riesgo por barco (&sigma;/n): "
                      f"{sd_profit / n:.1f} tharni. En rojo, los resultados con pérdidas.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("mueve la <u>fuente c</u> y la <u>masía</u>")
        c = st.slider("Posición de la fuente c (km)", 0.0, 42.0, v["c"], 0.1, key=ui.wkey(PAGE, "c"))
        farm = st.slider("Posición de la masía (km)", 8, 40, v["farm"], 1, key=ui.wkey(PAGE, "farm"))

        ui.planteamiento()
        ui.statement(
            "<b>La fuente del pueblo (1774)</b><br><br>"
            "Un pueblo se extiende a lo largo de un camino. Hay doce casas en los primeros kilómetros y "
            f"una masía apartada, a {v['farm']} km del inicio. Una vecina elegida al azar vive en la posición "
            "X. ¿Dónde poner la única fuente? Laplace propuso en 1774 resolver estos problemas minimizando "
            "el error absoluto medio; Gauss, en 1809, el error cuadrático medio. No dan lo mismo."
        )

        if ui.accordion_step("P3_A", "(A) El error cuadrático"):
            ui.content(
                "Si el coste es el cuadrado de la distancia a la fuente, calcula &#120124;[(X &minus; c)<sup>2</sup>] "
                "sumando y restando &mu; dentro del paréntesis. ¿Dónde es mínimo?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124;[(X &minus; c)<sup>2</sup>] = &#120141;(X) + (&mu; &minus; "
                "c)<sup>2</sup></div>"
                "El término cruzado se anula porque &#120124;[X &minus; &mu;] = 0. La varianza no depende de "
                "c, así que el mínimo está en c = &mu;, y su valor es precisamente la varianza: la media es "
                "el valor que minimiza el error cuadrático medio."
            )

        if ui.accordion_step("P3_B", "(B) El error absoluto"):
            ui.content(
                "Si el coste es la distancia, ¿qué ocurre con &#120124;|X &minus; c| al mover la fuente un poco "
                "hacia la derecha? Piensa en cuántas vecinas quedan a cada lado."
            )
            ui.spoiler(
                "Al desplazar c una pequeña distancia h hacia la derecha, las vecinas a su izquierda se alejan "
                "h y las de su derecha se acercan h: el coste cambia en h&middot;[&#8473;(X &le; c) &minus; "
                "&#8473;(X &gt; c)]. Deja de compensar moverse cuando hay la misma masa a cada lado, es decir, "
                "en la <b>mediana</b>: un valor Me con &#8473;(X &le; Me) &ge; 1/2 y &#8473;(X &ge; Me) &ge; "
                "1/2. Puede no ser única: con un número par de casas cualquier punto entre las dos centrales "
                "sirve."
            )

        if ui.accordion_step("P3_C", "(C) La masía lejana"):
            ui.content(
                "Aleja la masía con el deslizador. ¿Qué le pasa a la media? ¿Y a la mediana? ¿Y a la moda, "
                "el valor más frecuente?"
            )
            ui.spoiler(
                "La media se desplaza hacia la masía en proporción a su distancia: una sola casa lejana "
                "arrastra la fuente lejos de todas las demás. La mediana y la moda no se mueven, porque solo "
                "dependen de cuántas casas hay a cada lado o de dónde se concentran. Por eso la mediana es "
                "<i>robusta</i> y la media no, algo que volverá a aparecer en estadística."
            )

    with col_right:
        ui.right_panel()
        values, probs, mean, median, mode = village(farm)
        sq, ab = losses(values, probs, [c])
        med = f"{median[0]:.0f}" if median[0] == median[1] else f"[{median[0]:.0f}, {median[1]:.0f}]"
        ui.metrics([
            (f"Media &mu; = {mean:.2f}", "metric-a"),
            (f"Mediana = {med}", "metric-b"),
            (f"Moda = {mode:.0f}", "metric-c"),
        ])
        ui.show(village_chart(dark, values, probs, c, mean, median), key="fig_village")
        ui.footer_bar(f"Con la fuente en c = {c:.1f}: error cuadrático medio {sq[0]:.2f} y error absoluto medio "
                      f"{ab[0]:.2f} km. Las líneas punteadas marcan la media (azul) y la mediana (verde).")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La paradoja de San Petersburgo", "P1_A"),
        ("P2", "(II) El café de Lloyd", "P2_A"),
        ("P3", "(III) La fuente del pueblo", "P3_A"),
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
