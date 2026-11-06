#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 4: la regla del producto.

El sorteo de quintos (el orden de extracción no altera la probabilidad), un as
para cada jugador al repartir la baraja (probabilidad compuesta frente a
contar manos) y la urna de Pólya (secuencias intercambiables y contagio).
"""

from __future__ import annotations

from math import prod

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "La regla del producto"
SYMBOL = "∏ P"
PAGE = "02_04"

DECK = 40
ACES = 4
PLAYER_OPTIONS = [4, 5, 8, 10]
PATHS = 8
DRAWS = 200


def initial_values():
    n = ui.dint(5, 4, 10, "mozos")
    return {
        "mozos": n,
        "plazas": ui.dint(1, 1, max(1, n // 2), "plazas"),
        "turn": ui.dint(5, 1, n, "turn") if ui.has_code() else n,
        "players": ui.dchoice(4, [4, 5, 8], "players"),
        "red": ui.dint(1, 1, 4, "red"),
        "blue": ui.dint(1, 1, 4, "blue"),
        "add": ui.dint(1, 1, 3, "add"),
        "seed": int(ui.r("polya") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "quintos_sim": None, "aces_sim": None,
                   "polya_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def soldier_conditional(n: int, k: int, turn: int) -> float:
    """P(soldado en el turno t | todos los anteriores sacaron libre)."""
    if turn - 1 > n - k:
        return float("nan")
    return k / (n - turn + 1)


def simulate_quintos(n: int, k: int, draws: int, rng):
    slips = np.zeros((draws, n), dtype=bool)
    slips[:, :k] = True
    order = rng.random((draws, n)).argsort(axis=1)
    shuffled = np.take_along_axis(slips, order, axis=1)
    return shuffled.mean(axis=0)


def aces_apart(players: int) -> float:
    """P(los cuatro ases caen en manos distintas) con 40/players cartas por mano."""
    h = DECK // players
    return prod((DECK - i * h) / (DECK - i) for i in range(1, ACES))


def simulate_aces(players: int, deals: int, rng) -> float:
    h = DECK // players
    positions = rng.random((deals, DECK)).argsort(axis=1)[:, :ACES]
    hands = np.sort(positions // h, axis=1)
    return float((np.diff(hands, axis=1) > 0).all(axis=1).mean())


def sequence_probability(seq: str, r: int, b: int, c: int) -> float:
    p, red, blue = 1.0, r, b
    for colour in seq:
        total = red + blue
        if colour == "R":
            p *= red / total
            red += c
        else:
            p *= blue / total
            blue += c
    return p


def polya_paths(r: int, b: int, c: int, seed: int):
    rng = np.random.default_rng(seed)
    paths = []
    for _ in range(PATHS):
        red, blue, frac = r, b, []
        for _ in range(DRAWS):
            if rng.random() < red / (red + blue):
                red += c
            else:
                blue += c
            frac.append(red / (red + blue))
        paths.append(frac)
    return paths


# =============================================================================
# 2. FIGURAS
# =============================================================================

def quintos_chart(dark, n: int, k: int, turn: int, simulated):
    turns = list(range(1, n + 1))
    cond = [soldier_conditional(n, k, t) for t in turns]
    p = ui.new_figure(dark, height=320, x_axis_label="turno de extracción", y_axis_label="probabilidad de soldado",
                      x_range=(0.4, n + 0.6), y_range=(0, 1.05))
    colours = [ui.UBU_RED if t == turn else ui.BLUE_LINE for t in turns]
    p.vbar(x=turns, top=[k / n] * n, width=0.7, fill_color=colours, fill_alpha=0.8, line_color=None,
           legend_label="sin mirar a los demás")
    valid = [(t, c) for t, c in zip(turns, cond) if not np.isnan(c)]
    p.line([t for t, _ in valid], [c for _, c in valid], line_width=3, color=ui.ORANGE_LINE, line_dash="dashed",
           legend_label="si todos los anteriores sacaron libre")
    p.scatter([t for t, _ in valid], [c for _, c in valid], size=10, color=ui.ORANGE_LINE)
    if simulated is not None:
        p.scatter(turns, list(simulated), size=16, marker="diamond", color=ui.UBU_YELLOW, line_color=ui.UBU_DARK,
                  line_width=2, legend_label="frecuencia simulada")
    p.xaxis.ticker = turns
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_left")


def aces_chart(dark, players: int, simulated):
    labels = [f"{n} jugadores" for n in PLAYER_OPTIONS]
    values = [aces_apart(n) for n in PLAYER_OPTIONS]
    colours = [ui.UBU_RED if n == players else ui.BLUE_LINE for n in PLAYER_OPTIONS]
    p = ui.new_figure(dark, height=320, x_range=labels, y_range=(0, 1.0),
                      y_axis_label="P(los ases en manos distintas)")
    p.vbar(x=labels, top=values, width=0.65, fill_color=colours, line_color=None)
    if simulated is not None and simulated[0] == players:
        p.scatter([f"{players} jugadores"], [simulated[1]], size=18, marker="diamond", color=ui.UBU_YELLOW,
                  line_color=ui.UBU_DARK, line_width=2)
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "15px"
    return p


def polya_chart(dark, paths, r: int, b: int):
    xs = list(range(1, DRAWS + 1))
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.RED_LINE, "#00838f",
               ui.GREY_LINE, ui.UBU_RED]
    p = ui.new_figure(dark, height=320, x_axis_label="extracciones", y_axis_label="fracción de bolas rojas",
                      x_range=(0, DRAWS), y_range=(0, 1))
    p.line([0, DRAWS], [r / (r + b)] * 2, line_color=ui.GREY_LINE, line_dash="dashed", line_width=2)
    for path, colour in zip(paths, palette):
        p.line(xs, path, line_width=2.5, color=colour, alpha=0.9)
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se encadenan las probabilidades?</b>")
        ui.content(
            "Muchos experimentos ocurren por etapas: se saca una bola, luego otra; se reparte una carta, "
            "luego la siguiente. Despejando en la definición de probabilidad condicionada se obtiene la "
            "<b>regla de la multiplicación</b>, que da la probabilidad de que ocurran dos sucesos a partir "
            "de la de uno y la del otro sabiendo que ha ocurrido el primero.<br><br>"
            "<i>Trata de escribirla de las dos maneras posibles.</i>"
        )
        ui.formula_hidden("&#8473;(A &cap; B) = &#8473;(A | B)&middot;&#8473;(B) = &#8473;(B | A)&middot;&#8473;(A)",
                          hint="Pulsa para revelar la regla de la multiplicación")
        ui.content(
            "Aplicándola una y otra vez a n sucesos que ocurren en secuencia se llega, por inducción, a la "
            "<b>fórmula de la probabilidad compuesta</b>. En un diagrama de árbol es una regla muy visual: "
            "la probabilidad de un camino es el producto de las etiquetas de sus ramas.<br><br>"
            "<i>Trata de escribirla.</i>"
        )
        ui.formula_hidden(
            "&#8473;(A<sub>1</sub> &cap; &ctdot; &cap; A<sub>n</sub>) = &#8473;(A<sub>1</sub>)&middot;"
            "&#8473;(A<sub>2</sub> | A<sub>1</sub>)&middot;&#8473;(A<sub>3</sub> | A<sub>1</sub> &cap; "
            "A<sub>2</sub>) &ctdot; &#8473;(A<sub>n</sub> | A<sub>1</sub> &cap; &ctdot; &cap; A<sub>n&minus;1</sub>)",
            hint="Pulsa para revelar la fórmula de la probabilidad compuesta",
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El sorteo de quintos (1770)</b><br>"
            "<i>Los mozos del pueblo sacan papeletas de un cántaro. ¿Conviene sacar el primero, o "
            "esperar?</i><br><br>"
            "<b>II. Un as para cada uno</b><br>"
            "<i>Reparte la baraja con Gerolamo Cardano y calcula, carta a carta, la probabilidad de que "
            "los ases queden repartidos.</i><br><br>"
            "<b>III. La urna de Pólya (1923)</b><br>"
            "<i>Una urna que se contagia de su propio pasado: descubre con George Pólya por qué el orden "
            "de los colores no importa.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>mozos n</u>, las <u>plazas k</u> y <u>tu turno</u>")
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Mozos n", 3, 12, v["mozos"], key=ui.wkey(PAGE, "mozos"))
        k = c2.number_input("Plazas k", 1, n - 1, min(v["plazas"], n - 1), key=ui.wkey(PAGE, f"plazas{n}"))
        turn = c3.number_input("Tu turno", 1, n, min(v["turn"], n), key=ui.wkey(PAGE, f"turn{n}"))

        ui.planteamiento()
        ui.statement(
            "<b>El sorteo de quintos (1770)</b><br><br>"
            "Desde la ordenanza de reemplazos de Carlos III, el ejército español se nutrió de mozos "
            "elegidos por sorteo en cada pueblo; se les llamó <i>quintos</i> porque en origen se llevaba "
            "a uno de cada cinco. Quien podía pagaba la redención en metálico (para nosotros, unos "
            "cuantos tharni) y se libraba; los demás sacaban por turno una papeleta de un cántaro. En "
            f"nuestro pueblo hay n = {v['mozos']} mozos y k = {v['plazas']} papeletas de soldado. Tú "
            f"sacas en el turno {min(v['turn'], v['mozos'])}. ¿Te conviene cambiar de turno?"
        )

        if ui.accordion_step("P1_A", "(A) ¿Conviene sacar el primero?"):
            ui.content(
                "Sea S<sub>t</sub> el suceso <i>el mozo del turno t saca soldado</i>. Calcula "
                "&#8473;(S<sub>1</sub>) y, condicionando a lo que sacó el primero, "
                "&#8473;(S<sub>2</sub>)."
            )
            ui.spoiler(
                "&#8473;(S<sub>1</sub>) = k&frasl;n por la regla de Laplace. Para el segundo, "
                "{S<sub>1</sub>, S<sub>1</sub><sup>c</sup>} es una partición, y en cada rama se aplica la "
                "regla de la multiplicación:"
                "<div class='formula-box'>&#8473;(S<sub>2</sub>) = <sup>k&minus;1</sup>&frasl;<sub>n&minus;1</sub>"
                "&middot;<sup>k</sup>&frasl;<sub>n</sub> + <sup>k</sup>&frasl;<sub>n&minus;1</sub>&middot;"
                "<sup>n&minus;k</sup>&frasl;<sub>n</sub> = <sup>k</sup>&frasl;<sub>n</sub></div>"
                "Exactamente lo mismo que el primero."
            )

        if ui.accordion_step("P1_B", "(B) El turno t"):
            ui.content(
                "Con una sola papeleta de soldado (k = 1), escribe con la fórmula de la probabilidad "
                "compuesta la probabilidad de que te toque a ti en el turno t: los t &minus; 1 anteriores "
                "han sacado libre y tú sacas soldado. ¿Qué ocurre al multiplicar?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(S<sub>t</sub>) = <sup>n&minus;1</sup>&frasl;<sub>n</sub>&middot;"
                "<sup>n&minus;2</sup>&frasl;<sub>n&minus;1</sub> &ctdot; <sup>n&minus;t+1</sup>&frasl;"
                "<sub>n&minus;t+2</sub>&middot;<sup>1</sup>&frasl;<sub>n&minus;t+1</sub> = <sup>1</sup>&frasl;"
                "<sub>n</sub></div>"
                "El producto es telescópico: cada numerador se cancela con el denominador siguiente. Con k "
                "papeletas el argumento más corto es de simetría: todos los órdenes de las papeletas en el "
                "cántaro son igual de probables, y la papeleta del turno t tiene la misma probabilidad de "
                "ser de soldado que la del turno 1. El sorteo es justo."
            )

        if ui.accordion_step("P1_C", "(C) Lo que sí cambia con el turno"):
            ui.content(
                "Imagina que esperas tu turno viendo sacar a los demás y todos los anteriores sacan "
                "libre. ¿Cuánto vale ahora la probabilidad de que te toque? Mira la línea naranja de la "
                "derecha."
            )
            ui.spoiler(
                "Sabiendo que los t &minus; 1 anteriores han sacado libre, en el cántaro quedan "
                "n &minus; t + 1 papeletas y siguen todas las de soldado:"
                "<div class='formula-box'>&#8473;(S<sub>t</sub> | S<sub>1</sub><sup>c</sup> &cap; &ctdot; "
                "&cap; S<sub>t&minus;1</sub><sup>c</sup>) = <sup>k</sup>&frasl;<sub>n&minus;t+1</sub></div>"
                "El turno no cambia tu probabilidad mientras no sepas nada; lo que la cambia es la "
                "información que vas acumulando. Por eso el último mozo pasa tan mal rato: su "
                "probabilidad <i>a priori</i> es la de todos, pero la condicionada a lo que ve puede subir "
                "hasta la certeza."
            )

    with col_right:
        ui.right_panel()
        cond = soldier_conditional(n, k, turn)
        ui.metrics([
            (f"&#8473;(S<sub>{turn}</sub>) = {k / n:.4f}", "metric-a"),
            ("Si los anteriores sacan libre: " + ("imposible" if np.isnan(cond) else f"{cond:.4f}"), "metric-c"),
        ])
        if st.button("Repetir el sorteo 5000 veces", key="quintos_play", width="stretch", type="primary"):
            st.session_state["quintos_sim"] = (n, k, simulate_quintos(n, k, 5000, np.random.default_rng()))
        sim = st.session_state.get("quintos_sim")
        simulated = sim[2] if sim and sim[0] == n and sim[1] == k else None
        ui.show(quintos_chart(dark, n, k, turn, simulated), key="fig_quintos")
        ui.footer_bar(f"Con {n} mozos y {k} plazas, todos los turnos tienen probabilidad {k / n:.3f} de soldado. "
                      "La línea naranja crece porque condiciona a una información que solo tiene quien espera.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de jugadores</u>")
        players = st.select_slider("Jugadores", options=PLAYER_OPTIONS, value=v["players"],
                                   key=ui.wkey(PAGE, "players"))

        ui.planteamiento()
        ui.statement(
            "<b>Un as para cada uno</b><br><br>"
            "Gerolamo Cardano (1501-1576), médico, algebrista y jugador incorregible, escribió hacia 1564 "
            "el <i>Libro de los juegos de azar</i>, que no se publicó hasta un siglo después de su muerte. "
            "En él calcula las suertes de la primera, que se jugaba con una baraja de 40 cartas como la "
            f"nuestra. Repartimos la baraja entera entre {v['players']} jugadores, "
            f"{DECK // v['players']} cartas a cada uno{', como en el tute' if v['players'] == 4 else ''}. ¿Qué probabilidad hay de que los "
            "cuatro ases acaben en manos distintas?"
        )

        if ui.accordion_step("P2_A", "(A) Repartir los ases uno a uno"):
            ui.content(
                "Fíjate solo en las posiciones de los cuatro ases en la baraja barajada. El primero cae en "
                "alguna mano. ¿Con qué probabilidad cae el segundo en otra mano distinta? ¿Y el tercero, "
                "sabiendo lo anterior? Encadena con la fórmula de la probabilidad compuesta."
            )
            ui.spoiler(
                "Con h cartas por mano, al segundo as le quedan 39 posiciones, de las que 40 &minus; h están "
                "fuera de la mano del primero; al tercero, 38 posiciones con 40 &minus; 2h libres de las dos "
                "manos ocupadas, y así sucesivamente:"
                "<div class='formula-box'>&#8473; = <sup>40&minus;h</sup>&frasl;<sub>39</sub>&middot;"
                "<sup>40&minus;2h</sup>&frasl;<sub>38</sub>&middot;<sup>40&minus;3h</sup>&frasl;<sub>37</sub></div>"
                "Con cuatro jugadores (h = 10) es la probabilidad de que cada uno reciba exactamente un as."
            )

        if ui.accordion_step("P2_B", "(B) Contando manos"):
            ui.content(
                "Comprueba el resultado con la regla de Laplace para cuatro jugadores: cuenta los repartos "
                "posibles de las 40 cartas en cuatro manos de 10, y los repartos en que cada mano tiene un "
                "as."
            )
            ui.spoiler(
                "Los repartos posibles son 40!&frasl;(10!)<sup>4</sup> (permutaciones con repetición). Los "
                "favorables asignan un as a cada mano (4! formas) y reparten las 36 cartas restantes en "
                "cuatro grupos de 9:"
                "<div class='formula-box'>&#8473; = <sup>4! &middot; 36!&frasl;(9!)<sup>4</sup></sup>&frasl;"
                "<sub>40!&frasl;(10!)<sup>4</sup></sub></div>"
                "que, simplificando, coincide con el producto del apartado anterior. Dos caminos, el "
                "mismo número: contar todo de golpe o encadenar condicionadas."
            )

        if ui.accordion_step("P2_C", "(C) Con más jugadores"):
            ui.content(
                "Con más jugadores las manos son más pequeñas. ¿Es más o menos probable que los ases "
                "queden separados? Compara las barras de la derecha y comprueba con la simulación."
            )
            ui.spoiler(
                "Más probable: con manos más pequeñas, cada as ocupa una mano que se lleva menos posiciones "
                "consigo, y los factores (40 &minus; ih)&frasl;(40 &minus; i) crecen al bajar h. En el límite "
                "de manos de una carta, los ases estarían siempre separados."
            )

    with col_right:
        ui.right_panel()
        exact = aces_apart(players)
        ui.metric(f"&#8473;(ases en manos distintas) = {exact:.4f}", "metric-a")
        if st.button("Repartir 20000 veces", key="aces_play", width="stretch", type="primary"):
            st.session_state["aces_sim"] = (players, simulate_aces(players, 20000, np.random.default_rng()))
        sim = st.session_state.get("aces_sim")
        ui.show(aces_chart(dark, players, sim), key="fig_aces")
        if sim and sim[0] == players:
            ui.footer_bar(f"Frecuencia simulada con {players} jugadores: {sim[1]:.4f}, frente al valor exacto "
                          f"{exact:.4f}.")
        else:
            ui.footer_bar("Pulsa el botón para repartir la baraja muchas veces y comparar con el valor exacto.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>bolas iniciales</u> y las <u>bolas añadidas c</u>")
        c1, c2, c3 = st.columns(3)
        r = c1.number_input("Rojas", 1, 6, v["red"], key=ui.wkey(PAGE, "red"))
        b = c2.number_input("Azules", 1, 6, v["blue"], key=ui.wkey(PAGE, "blue"))
        c = c3.number_input("Añadidas c", 0, 5, v["add"], key=ui.wkey(PAGE, "add"))

        ui.planteamiento()
        ui.statement(
            "<b>La urna de Pólya (1923)</b><br><br>"
            "Florian Eggenberger y George Pólya buscaban en 1923 un modelo sencillo de contagio: cada "
            "caso de una enfermedad hace más probable el siguiente. Su urna empieza con "
            f"{v['red']} bolas rojas y {v['blue']} azules. Se saca una bola al azar, se mira su color y se "
            f"devuelve a la urna junto con {v['add']} {'bola' if v['add'] == 1 else 'bolas'} más del "
            "mismo color. Y se repite. ¿Cuál es la "
            "probabilidad de una secuencia de colores, y qué le pasa a la urna a la larga?"
        )

        if ui.accordion_step("P3_A", "(A) Una secuencia concreta"):
            ui.content(
                "Con la fórmula de la probabilidad compuesta, calcula &#8473;(R, R, A): roja, roja y "
                "azul, en ese orden. Repite la cuenta para (R, A, R) y (A, R, R). ¿Qué observas?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(R, R, A) = <sup>r</sup>&frasl;<sub>r+a</sub>&middot;"
                "<sup>r+c</sup>&frasl;<sub>r+a+c</sub>&middot;<sup>a</sup>&frasl;<sub>r+a+2c</sub></div>"
                "Los otros dos órdenes dan los mismos factores en otro orden: los denominadores no "
                "dependen de los colores, y los numeradores de cada color van r, r + c, r + 2c&hellip; "
                "aparezcan donde aparezcan. La probabilidad de una secuencia solo depende de cuántas rojas "
                "y azules tiene: las extracciones son <b>intercambiables</b>, aunque no independientes."
            )

        if ui.accordion_step("P3_B", "(B) La segunda bola"):
            ui.content(
                "Sin mirar la primera bola, ¿cuál es la probabilidad de que la segunda sea roja? "
                "Condiciona al color de la primera."
            )
            ui.spoiler(
                "Por el teorema de la probabilidad total sobre la partición {R<sub>1</sub>, A<sub>1</sub>}:"
                "<div class='formula-box'>&#8473;(R<sub>2</sub>) = <sup>r+c</sup>&frasl;<sub>r+a+c</sub>&middot;"
                "<sup>r</sup>&frasl;<sub>r+a</sub> + <sup>r</sup>&frasl;<sub>r+a+c</sub>&middot;"
                "<sup>a</sup>&frasl;<sub>r+a</sub> = <sup>r</sup>&frasl;<sub>r+a</sub></div>"
                "La misma que para la primera, como en el sorteo de quintos. Pero R<sub>1</sub> y "
                "R<sub>2</sub> no son independientes si c &gt; 0: saber que la primera fue roja hace más "
                "probable que la segunda también lo sea."
            )

        if ui.accordion_step("P3_C", "(C) El contagio"):
            ui.content(
                "Pulsa <i>Otra tanda</i> a la derecha varias veces. Cada línea es una urna distinta que "
                "evoluciona durante 200 extracciones. ¿Tiende la fracción de rojas a la proporción inicial? "
                "¿Y con c = 0?"
            )
            ui.spoiler(
                "Cada urna se estabiliza, pero cada una en un nivel distinto: las primeras extracciones, "
                "puro azar, se refuerzan a sí mismas y deciden el destino de la urna. La fracción límite es "
                "una variable aleatoria (con distribución beta, que verás más adelante; uniforme cuando se "
                "empieza con una bola de cada color y c = 1). Con c = 0 las extracciones son independientes "
                "y todas las urnas se quedan en la proporción inicial."
            )

    with col_right:
        ui.right_panel()
        rrb = sequence_probability("RRA", r, b, c)
        ui.metrics([
            (f"&#8473;(R<sub>1</sub>) = &#8473;(R<sub>2</sub>) = {r / (r + b):.4f}", "metric-a"),
            (f"&#8473;(R, R, A) = &#8473;(A, R, R) = {rrb:.4f}", "metric-c"),
        ])
        if st.button("Otra tanda", key="polya_new", width="stretch", type="primary"):
            st.session_state["polya_round"] += 1
        paths = polya_paths(r, b, c, v["seed"] + st.session_state["polya_round"])
        ui.show(polya_chart(dark, paths, r, b), key="fig_polya")
        finals = ", ".join(f"{path[-1]:.2f}" for path in paths)
        ui.footer_bar(f"Fracción de rojas tras {DRAWS} extracciones en cada urna: {finals}. La línea "
                      "discontinua marca la proporción inicial.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El sorteo de quintos", "P1_A"),
        ("P2", "(II) Un as para cada uno", "P2_A"),
        ("P3", "(III) La urna de Pólya", "P3_A"),
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
