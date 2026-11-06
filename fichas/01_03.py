#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 3: la probabilidad clásica de Laplace.

Parejas en una mano de mus (baraja de Fournier), la aguja de Buffon como
método de Montecarlo para estimar π y los regalos de los Reyes Magos
(inclusión-exclusión por etapas).
"""

from __future__ import annotations

from math import comb

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "La probabilidad clásica"
SYMBOL = "#A/#Ω"
PAGE = "01_03"

HAND = 4          # cartas por mano en el mus
VALUES = 10       # 1 al 7, sota, caballo y rey
SUITS = 4         # oros, copas, espadas y bastos


def initial_values():
    return {"needle": round(20 * ui.dfloat(0.80, 0.40, 1.00, "needle")) / 20}


def init_session_state():
    ui.init_state({
        "page": "INTRO",
        "open_part": "P1_A",
        "cards_res": None,
        "buffon_res": None,
    })


# =============================================================================
# 1. CARTAS DE FOURNIER (baraja española de 40)
# =============================================================================

def deal_hands(n_sims: int, rng) -> dict:
    """Reparte n_sims manos de 4 cartas y cuenta cuántos valores aparecen repetidos."""
    cards = rng.random((n_sims, VALUES * SUITS)).argsort(axis=1)[:, :HAND]
    vals = np.sort(cards // SUITS, axis=1)
    eq = vals[:, 1:] == vals[:, :-1]
    pairs = eq[:, 0].astype(int) + (eq[:, 1] & ~eq[:, 0]) + (eq[:, 2] & ~eq[:, 1])
    return {"n": n_sims, "n0": int((pairs == 0).sum()), "n1": int((pairs == 1).sum()),
            "n2": int((pairs == 2).sum())}


def cards_theory() -> dict:
    total = comb(VALUES * SUITS, HAND)
    without = comb(VALUES, HAND) * SUITS ** HAND
    return {"total": total, "sin": without, "p_sin": without / total, "p_al_menos": 1 - without / total}


def cards_histogram(dark, res):
    labels = ["0 parejas", "1 pareja", "2 parejas"]
    n = res["n"]
    pcts = [res["n0"] / n * 100, res["n1"] / n * 100, res["n2"] / n * 100]
    p = ui.new_figure(dark, height=300, x_range=labels, y_axis_label="% de las simulaciones",
                      y_range=(0, max(pcts) * 1.15 + 1))
    p.vbar(x=labels, top=pcts, width=0.7, fill_color=[ui.UBU_YELLOW, ui.BLUE_LINE, ui.UBU_RED],
           line_color=None)
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "16px"
    return p


# =============================================================================
# 2. AGUJA DE BUFFON (Montecarlo para π)
# =============================================================================

FIELD = 8   # número de franjas del suelo; las juntas están en los enteros (d = 1)


def drop_needles(n: int, ell: float, rng) -> dict:
    xc = rng.uniform(0.4, FIELD - 0.4, n)
    yc = rng.uniform(0.0, FIELD, n)
    theta = rng.uniform(0.0, np.pi, n)
    dy = (ell / 2.0) * np.sin(theta)
    crosses = np.floor(yc - dy) != np.floor(yc + dy)
    ncross = int(crosses.sum())
    pi_est = (2.0 * ell * n) / ncross if ncross > 0 else float("nan")
    return dict(xc=xc, yc=yc, th=theta, ell=ell, crosses=crosses, ncross=ncross, n=n, pi_est=pi_est)


def needles_chart(dark, sim, max_draw: int = 250):
    ell = sim["ell"]
    p = ui.new_figure(dark, height=420, x_range=(0, FIELD), y_range=(0, FIELD), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    floor = "#5a5a62" if dark else "#c2c2c2"
    for y in range(FIELD + 1):
        p.line([0, FIELD], [y, y], line_color=floor, line_width=2)
    m = min(sim["n"], max_draw)
    xc, yc, ang, cr = sim["xc"][:m], sim["yc"][:m], sim["th"][:m], sim["crosses"][:m]
    dx, dy = (ell / 2.0) * np.cos(ang), (ell / 2.0) * np.sin(ang)
    hit = np.where(cr)[0]
    miss = np.where(~cr)[0]
    p.multi_line([[xc[i] - dx[i], xc[i] + dx[i]] for i in miss],
                 [[yc[i] - dy[i], yc[i] + dy[i]] for i in miss],
                 line_color=floor, line_width=2, line_alpha=0.6)
    p.multi_line([[xc[i] - dx[i], xc[i] + dx[i]] for i in hit],
                 [[yc[i] - dy[i], yc[i] + dy[i]] for i in hit],
                 line_color=ui.GREEN_LINE, line_width=3, line_alpha=0.95)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es la probabilidad clásica?</b>")
        ui.content(
            "Como ya introdujimos, durante siglos el azar se jugó sin medirse. Fue Pierre-Simon Laplace "
            "quien, recogiendo el trabajo de Pascal, Fermat y Bernoulli, quiso reducir la probabilidad "
            "a algo que se pudiera <b>contar</b>: enumerar todos los resultados posibles de un "
            "experimento y ver cuántos son favorables al suceso que nos interesa. A esta idea se la "
            "llama <b>probabilidad clásica</b> porque es la definición histórica, la de Laplace, y coincide "
            "además con la noción intuitiva que "
            "todos tenemos (casos favorables entre casos totales) cuando los resultados son igual de "
            "verosímiles, como en la lotería o en los juegos de cartas (al menos en principio).<br><br>"
            "<i>Antes de mirar la fórmula, trata de deducir tú mismo su expresión.</i>"
        )
        ui.formula_hidden(
            "&#8473;(A) = <sup>casos favorables</sup>&frasl;<sub>casos posibles</sub> = |A| &frasl; |&Omega;|",
            hint="Pulsa para revelar la definición",
        )
        ui.section("Condiciones necesarias")
        ui.content("<b>Finitud.</b> El espacio muestral &Omega; debe ser finito, para así lidiar con "
                   "números y no con infinitos.")
        ui.content("<b>Equiprobabilidad.</b> Todos los resultados deben ser igual de probables, para que "
                   "contar cardinales (casos) sea equivalente a contar probabilidades.")
        ui.content("<b>Aplicación.</b> Bajo esas condiciones, cada suceso elemental {&omega;} tiene "
                   "probabilidad 1/|&Omega;|. Es la herramienta ideal para juegos de azar simétricos: "
                   "dados, cartas o loterías.")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Jugando a las cartas de Fournier</b><br>"
            "<i>Pon a prueba tu intuición antes de tu siguiente apuesta al mus.</i><br><br>"
            "<b>II. El nido de agujas de Buffon</b><br>"
            "<i>Explora con Buffon (1707-1788) un poco más el método de Montecarlo, esta vez para "
            "obtener el número &pi;.</i><br><br>"
            "<b>III. Un problema navideño: regalos mágicos</b><br>"
            "<i>Ayuda a Sus Majestades de Oriente a recibir cada uno su propio regalo.</i>"
        )


def render_problem_1(dark):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Jugando a las cartas de Fournier</b><br><br>"
            "Una baraja española tiene <b>40 cartas</b>: 10 valores (1 al 7, sota, caballo y rey), cada "
            "uno en 4 palos (oros, copas, espadas y bastos). En el mus recibes 4 cartas. ¿Cuál es la "
            "probabilidad de que te salga <b>al menos una pareja</b> (dos cartas del mismo valor)?"
        )

        if ui.accordion_step("P1_A", "(A) Planteamiento"):
            ui.content(
                "&bull; La baraja tiene 40 cartas: 10 valores (1 al 7, sota, caballo, rey).<br>"
                "&bull; Cada valor aparece en 4 palos distintos (oros, copas, espadas, bastos).<br>"
                "&bull; Se extraen 4 cartas <b>sin reemplazamiento</b> (una carta sacada ya no vuelve a "
                "la baraja).<br>"
                "&bull; Buscamos P(al menos una pareja del mismo valor)."
            )

        if ui.accordion_step("P1_B", "(B) Cálculo teórico"):
            ui.content(
                "Es más cómodo calcular el <b>complementario</b>: la probabilidad de NO obtener ninguna "
                "pareja (las 4 cartas con valores todos distintos) y restarla de 1. Para no tener pareja "
                "elegimos 4 valores diferentes de los 10 y, para cada uno, uno de sus 4 palos.<br><br>"
                "<i>Trata de escribir las fórmulas antes de revelarlas.</i>"
            )
            t = cards_theory()
            ui.formula_hidden(
                f"Casos totales = C(40, 4) = {ui.fmt_int(t['total'])}<br>"
                f"Sin pareja = C(10, 4) &middot; 4<sup>4</sup> = {ui.fmt_int(t['sin'])}<br>"
                f"P(sin pareja) = {t['p_sin']:.4f}<br>"
                f"P(&ge; 1 pareja) = 1 &minus; P(sin pareja) = {t['p_al_menos']:.4f}",
                hint="Pulsa para revelar el cálculo",
            )

        if ui.accordion_step("P1_C", "(C) Montecarlo al rescate"):
            ui.content(
                "En problemas sencillos como este es posible obtener el resultado analíticamente. Pero, "
                "¿qué ocurre si el problema es lo suficientemente complejo como para no poder resolverlo "
                "con lápiz y papel? El <b>método de Montecarlo</b> repite el experimento al azar "
                "muchísimas veces y estima la probabilidad como la frecuencia relativa observada. "
                "Experimenta con él en la parte derecha: reparte manos una y otra vez y observa qué "
                "fracción tiene al menos una pareja."
            )

    with col_right:
        ui.right_panel()
        ui.section("Simulación de Montecarlo")
        n_sims = st.slider("Número de manos repartidas", 1000, 100000, 5000, 1000, key="n_cards")
        if st.button("Repartir las manos", key="deal", width="stretch", type="primary"):
            st.session_state["cards_res"] = deal_hands(n_sims, np.random.default_rng())

        res = st.session_state["cards_res"]
        if res is None:
            ui.footer_bar("Pulsa el botón para lanzar la simulación.")
            return
        n = res["n"]
        ui.metrics([
            (f"0 parejas: {res['n0'] / n * 100:.2f}%", "metric-a"),
            (f"&ge; 1 pareja: {(res['n1'] + res['n2']) / n * 100:.2f}%", "metric-c"),
        ])
        ui.show(cards_histogram(dark, res), key="fig_cards")
        ui.footer_bar(
            f"Con {ui.fmt_int(n)} manos. ¿Se parecen los resultados al cálculo teórico? ¿Cuántas "
            "simulaciones crees que serán suficientes?"
        )


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>El nido de agujas de Buffon</b><br><br>"
            "El conde de Buffon (1707-1788) calculó la probabilidad de que una aguja lanzada sobre un suelo "
            "de tablas paralelas cruce una junta; Laplace advirtió después que el experimento sirve para "
            "estimar el número &pi;, con el mismo espíritu de Montecarlo del problema anterior. En nuestro suelo las "
            f"juntas están a distancia d = 1 y las agujas miden &#8467; = {v['needle']:.2f}."
        )

        if ui.accordion_step("P2_A", "(A) La descripción geométrica"):
            ui.content(
                "Imagina un suelo con líneas paralelas separadas una distancia d. Dejamos caer una aguja "
                "de longitud &#8467; (con &#8467; &le; d). Su posición queda descrita por la distancia de "
                "su centro a la línea más cercana y por el ángulo &theta; que forma con las líneas.<br><br>"
                "<i>Dibuja tú mismo el suelo, una aguja inclinada y marca cuándo cruzaría una línea. "
                "Después compruébalo.</i>"
            )
            ui.formula_hidden(
                "La aguja cruza una línea &hArr; dist(centro, línea) &le; (&#8467;&frasl;2) &middot; sin&theta;",
                hint="Pulsa para revelar cuándo cruza",
            )

        if ui.accordion_step("P2_B", "(B) Lanzando probabilidades"):
            ui.content(
                "Modelamos el lanzamiento suponiendo que el ángulo &theta; es uniforme en [0, &pi;] y que "
                "el centro cae uniformemente entre dos líneas. Integrando sobre todos los casos posibles "
                "se obtiene la probabilidad de que una aguja cruce una línea.<br><br>"
                "<i>Trata de escribir esa probabilidad y, despejando, una fórmula para &pi;.</i>"
            )
            ui.formula_hidden(
                "P(cruce) = <sup>2&#8467;</sup>&frasl;<sub>&pi;d</sub> &nbsp;&rArr;&nbsp; "
                "&pi; &asymp; <sup>2&#8467;N</sup>&frasl;<sub>d&middot;C</sub> &nbsp;(C cruces de N lanzamientos)"
            )

        if ui.accordion_step("P2_C", "(C) Hora de lanzar agujas"):
            ui.content(
                "Como en el problema anterior, simulamos: lanzamos muchas agujas al azar y contamos "
                "cruces. El método de Montecarlo va aún más lejos: si lanzamos muchos <b>puntos</b> al "
                "azar sobre una región y contamos cuántos caen dentro de una forma complicada, la "
                "fracción que la toca aproxima su área.<br><br><i>Trata de escribir esa aproximación.</i>"
            )
            ui.formula_hidden(
                "<sup>casos que tocan</sup>&frasl;<sub>casos lanzados</sub> &asymp; "
                "<sup>área de la forma</sup>&frasl;<sub>área total</sub>",
                hint="Pulsa para revelar la aproximación",
            )

    with col_right:
        ui.right_panel()
        ui.section("Simulación: estimando &pi;")
        n = st.slider("Número de agujas", 200, 50000, 2000, 200, key="n_needles")
        ell = st.slider("Longitud de la aguja ℓ", 0.10, 1.00, v["needle"], 0.05,
                        key=ui.wkey(PAGE, "needle"))
        if st.button("Lanzar las agujas", key="drop", width="stretch", type="primary"):
            st.session_state["buffon_res"] = drop_needles(n, ell, np.random.default_rng())

        sim = st.session_state["buffon_res"]
        if sim is None:
            ui.footer_bar("Pulsa el botón para lanzar las agujas.")
            return
        ui.badge(f"&pi; &asymp; {sim['pi_est']:.4f} &nbsp;|&nbsp; {ui.fmt_int(sim['ncross'])} cruces "
                 f"de {ui.fmt_int(sim['n'])} agujas (&#8467; = {sim['ell']:.2f})")
        ui.show(needles_chart(dark, sim), key="fig_buffon")
        err = abs(sim["pi_est"] - np.pi) / np.pi * 100
        ui.footer_bar(f"Valor real &pi; = 3.1416 (error del {err:.2f}%). Solo se dibujan las primeras "
                      "250 agujas. ¿Cuántas crees que hacen falta para acercarte de verdad?")


def render_problem_3():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Regalos mágicos · Tres sabios de Oriente</b><br><br>"
            "Guiados por una estrella (quizá el rastro de un cometa que cruzó el cielo) tres sabios de "
            "Oriente, Melchor, Gaspar y Baltasar, llegan cargados de regalos etiquetados con el nombre de "
            "su destinatario. Pero en el ajetreo de la noche los regalos se mezclan y se reparten al "
            "azar. ¿Cuál es la probabilidad de que <b>al menos uno</b> de los tres reciba su propio "
            "regalo?"
        )

        if ui.accordion_step("P3_A", "(A) El principio de inclusión-exclusión"):
            ui.content(
                "Para contar en cuántos repartos acierta al menos uno, sumamos los casos de cada uno, "
                "pero al hacerlo contamos de más los repartos donde aciertan dos o más a la vez. El "
                "<b>principio de inclusión-exclusión</b> corrige ese exceso sumando y restando "
                "alternativamente las intersecciones."
            )
            ui.formula(
                "&#8473;(&#8899;<sub>i</sub> A<sub>i</sub>) = &sum;<sub>i</sub> &#8473;(A<sub>i</sub>) "
                "&minus; &sum;<sub>i&lt;j</sub> &#8473;(A<sub>i</sub>&cap;A<sub>j</sub>) + &hellip; + "
                "(&minus;1)<sup>n+1</sup> &#8473;(&#8898;<sub>i</sub> A<sub>i</sub>)"
            )

        if ui.accordion_step("P3_B", "(B) Tres Reyes"):
            ui.content(
                "Con n = 3, sea A<sub>i</sub> el suceso «el Rey i recibe su regalo». Cada uno acierta "
                "con probabilidad 1/3; cada pareja, con 1/(3&middot;2); y los tres a la vez, con "
                "1/(3&middot;2&middot;1).<br><br><i>Trata de calcular la probabilidad.</i>"
            )
            ui.formula_hidden(
                "P(al menos uno) = 1 &minus; <sup>1</sup>&frasl;<sub>2!</sub> + "
                "<sup>1</sup>&frasl;<sub>3!</sub> = 1 &minus; <sup>1</sup>&frasl;<sub>2</sub> + "
                "<sup>1</sup>&frasl;<sub>6</sub> = <sup>2</sup>&frasl;<sub>3</sub> &asymp; 0.667",
                hint="Pulsa para revelar el resultado",
            )

        if ui.accordion_step("P3_C", "(C) n Reyes"):
            ui.content(
                "Para n Reyes cualesquiera, la intersección de k sucesos concretos tiene probabilidad "
                "(n&minus;k)!/n!, y hay C(n, k) de ellas. El principio de inclusión-exclusión deja una "
                "suma alternada muy elegante que, sorprendentemente, casi no depende de n.<br><br>"
                "<i>Trata de escribir la fórmula general y su límite.</i>"
            )
            ui.formula_hidden(
                "P(al menos uno) = &sum;<sub>k=1</sub><sup>n</sup> (&minus;1)<sup>k+1</sup> "
                "<sup>1</sup>&frasl;<sub>k!</sub> &nbsp;&xrarr;&nbsp; 1 &minus; "
                "<sup>1</sup>&frasl;<sub>e</sub> &asymp; 0.632",
                hint="Pulsa para revelar la fórmula general",
            )

    with col_right:
        ui.right_panel()
        ui.section("Demuéstralo por etapas")
        etapa = ui.stage("ie_stage", 3)

        if etapa == 1:
            ui.content(
                "<b>Etapa 1 · Inclusión.</b><br>"
                "Sumamos las probabilidades individuales: cada uno de los n Reyes acierta su propio "
                "regalo con probabilidad 1/n.<br><br><i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden("&sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub>) = "
                              "n &middot; <sup>1</sup>&frasl;<sub>n</sub> = 1")
            ui.content("El resultado es 1 (certeza absoluta), lo cual es absurdo: hemos contado varias "
                       "veces los repartos en que aciertan dos o más Reyes a la vez.")
        elif etapa == 2:
            ui.content(
                "<b>Etapa 2 · Exclusión.</b><br>"
                "Restamos las parejas: que dos Reyes concretos acierten a la vez tiene probabilidad "
                "(n&minus;2)!/n!, y hay C(n, 2) parejas posibles.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(
                "&minus; &sum;<sub>i&lt;j</sub> &#8473;(A<sub>i</sub>&cap;A<sub>j</sub>) = "
                "&minus; C(n,2) &middot; <sup>(n&minus;2)!</sup>&frasl;<sub>n!</sub> = "
                "&minus; <sup>1</sup>&frasl;<sub>2!</sub>"
            )
            ui.content("Con los tríos volveríamos a sumar, con los cuartetos a restar, y así "
                       "sucesivamente: el signo se va alternando.")
        else:
            ui.content(
                "<b>Etapa 3 · Generalización y conclusión.</b><br>"
                "Cada intersección de k sucesos aporta un término (&minus;1)<sup>k+1</sup>/k!. "
                "Sumándolos todos obtenemos la probabilidad de que al menos un Rey acierte.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden("&#8473;(&#8899;<sub>i</sub> A<sub>i</sub>) = "
                              "&sum;<sub>k=1</sub><sup>n</sup> (&minus;1)<sup>k+1</sup> "
                              "<sup>1</sup>&frasl;<sub>k!</sub>")
            ui.content("Y cuando el número de Reyes crece, esta suma converge a un valor notable, casi "
                       "independiente de n.")
            ui.formula_hidden(
                "&#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) &xrarr; "
                "1 &minus; <sup>1</sup>&frasl;<sub>e</sub> &asymp; 0.632 &#8718;",
                hint="Pulsa para revelar el límite",
            )


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Cartas de Fournier", "P1_A"),
        ("P2", "(II) La aguja de Buffon", "P2_A"),
        ("P3", "(III) Regalos mágicos", "P3_A"),
    ])

    if current == "INTRO":
        render_intro()
    elif current == "P1":
        render_problem_1(dark)
    elif current == "P2":
        render_problem_2(dark, v)
    elif current == "P3":
        render_problem_3()

    ui.footer()


main()
