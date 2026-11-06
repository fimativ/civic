#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 6: condicionar al primer paso.

La ruina del jugador (recurrencia de la probabilidad total), la tarjeta de
embarque perdida (una respuesta que no depende del número de pasajeros) y el
juego de Penney (un sistema de ecuaciones y un juego no transitivo).
"""

from __future__ import annotations

from itertools import product

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "Condicionar al primer paso"
SYMBOL = "↺ pₖ"
PAGE = "02_06"

P_OPTIONS = {"Justo (1/2)": 0.5, "Ruleta al rojo (18/37)": 18 / 37, "Ligera ventaja (0.52)": 0.52,
             "Desventaja (0.45)": 0.45}
SEQUENCES = ["".join(s) for s in product("CX", repeat=3)]
STATES = ["", "C", "X", "CC", "CX", "XC", "XX"]


def initial_values():
    n_target = ui.dchoice(30, [20, 25, 30, 40], "target")
    return {
        "capital": ui.dint(10, 3, n_target - 3, "capital") if ui.has_code() else 10,
        "target": n_target,
        "odds": ui.dchoice("Justo (1/2)", list(P_OPTIONS), "odds"),
        "passengers": ui.dchoice(100, [10, 20, 50, 100, 150, 200], "passengers"),
        "seq_a": ui.dchoice("CCX", SEQUENCES, "seq_a"),
        "seq_b": ui.dchoice("XCC", SEQUENCES, "seq_b"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "ruin_sim": None, "plane_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def ruin_probability(k: int, n: int, p: float) -> float:
    if abs(p - 0.5) < 1e-12:
        return 1 - k / n
    rho = (1 - p) / p
    return (rho ** k - rho ** n) / (1 - rho ** n)


def play_ruin(k: int, n: int, p: float, games: int, rng, keep: int = 12):
    capital = np.full(games, k)
    alive = np.ones(games, dtype=bool)
    paths = [[k] for _ in range(keep)]
    steps = 0
    while alive.any() and steps < 200000:
        steps += 1
        moves = np.where(rng.random(games) < p, 1, -1)
        capital = np.where(alive, capital + moves, capital)
        alive = (capital > 0) & (capital < n)
        for i in range(keep):
            if paths[i][-1] not in (0, n):
                paths[i].append(int(capital[i]))
    return float((capital == 0).mean()), paths


def board(n: int, flights: int, rng):
    """Simula vuelos: cuenta cuántas veces cada pasajero acaba en su asiento."""
    own = np.zeros(n)
    for _ in range(flights):
        displaced = []
        cur = int(rng.integers(n))
        if cur != 0:
            displaced.append(0)
        while cur not in (0, n - 1):
            displaced.append(cur)
            u = int(rng.integers(n - cur))
            cur = 0 if u == 0 else cur + u
        if cur == n - 1:
            displaced.append(n - 1)
        hits = np.ones(n)
        hits[displaced] = 0
        own += hits
    return own / flights


def penney(a: str, b: str, p: float) -> float:
    """P(a aparece antes que b) resolviendo el sistema del primer paso."""
    if a == b:
        return float("nan")
    q = 1 - p
    index = {s: i for i, s in enumerate(STATES)}
    mat = np.eye(len(STATES))
    rhs = np.zeros(len(STATES))
    for s in STATES:
        i = index[s]
        for toss, prob in (("C", p), ("X", q)):
            w = s + toss
            if len(w) == 3:
                if w == a:
                    rhs[i] += prob
                    continue
                if w == b:
                    continue
                w = w[1:]
            mat[i, index[w]] -= prob
    return float(np.linalg.solve(mat, rhs)[index[""]])


def conway_reply(a: str) -> str:
    """Regla de Conway: la mejor respuesta con una moneda justa."""
    flip = {"C": "X", "X": "C"}
    return flip[a[1]] + a[0] + a[1]


def best_reply(a: str, p: float) -> str:
    """La secuencia que más veces gana a la de A con esta moneda."""
    return max((s for s in SEQUENCES if s != a), key=lambda s: 1 - penney(a, s, p))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def ruin_chart(dark, k: int, n: int, p: float):
    ks = list(range(n + 1))
    fig = ui.new_figure(dark, height=280, x_axis_label="capital inicial (tharni)",
                        y_axis_label="probabilidad de ruina", x_range=(0, n), y_range=(0, 1.02))
    fig.line(ks, [1 - x / n for x in ks], line_width=2, color=ui.GREY_LINE, line_dash="dotted",
             legend_label="juego justo")
    fig.line(ks, [ruin_probability(x, n, p) for x in ks], line_width=5, color=ui.RED_LINE,
             legend_label="este juego")
    fig.scatter([k], [ruin_probability(k, n, p)], size=16, color=ui.RED_LINE, line_color="white", line_width=2)
    return ui.style_legend(fig, dark, "top_right")


def paths_chart(dark, paths, n: int):
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.RED_LINE, "#00838f"]
    longest = max(len(path) for path in paths)
    fig = ui.new_figure(dark, height=260, x_axis_label="ronda", y_axis_label="capital (tharni)",
                        x_range=(0, longest), y_range=(-0.5, n + 0.5))
    fig.line([0, longest], [n, n], line_color=ui.GREEN_LINE, line_dash="dashed", line_width=2)
    fig.line([0, longest], [0, 0], line_color=ui.RED_LINE, line_dash="dashed", line_width=2)
    for i, path in enumerate(paths):
        fig.line(list(range(len(path))), path, line_width=2, color=palette[i % len(palette)], alpha=0.85)
    return fig


def plane_chart(dark, n: int, simulated):
    js = list(range(2, n + 1))
    theory = [(n - j + 1) / (n - j + 2) for j in js]
    fig = ui.new_figure(dark, height=300, x_axis_label="pasajero j (orden de embarque)",
                        y_axis_label="P(se sienta en su asiento)", x_range=(1, n + 1), y_range=(0.4, 1.02))
    fig.line(js, theory, line_width=4, color=ui.BLUE_LINE, legend_label="(n − j + 1)/(n − j + 2)")
    if simulated is not None:
        fig.scatter(js, list(simulated[1:]), size=7, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK,
                    legend_label="simulación")
    return ui.style_legend(fig, dark, "bottom_left")


def penney_chart(dark, a: str, b: str, p: float):
    xs, ys, values, colours, texts = [], [], [], [], []
    n = len(SEQUENCES)
    for i, row in enumerate(SEQUENCES):
        for j, col in enumerate(SEQUENCES):
            val = penney(row, col, p)
            xs.append(j)
            ys.append(n - 1 - i)
            values.append(val)
            if np.isnan(val):
                colours.append(ui.GREY_LINE); texts.append("")
            else:
                colours.append(ui.GREEN_LINE if val > 0.5 else ui.RED_LINE)
                texts.append(f"{val:.2f}")
    alphas = [0.15 if np.isnan(v) else 0.25 + 0.75 * abs(v - 0.5) * 2 for v in values]
    fig = ui.new_figure(dark, height=380, x_range=(-0.5, n - 0.5), y_range=(-0.5, n - 0.5),
                        x_axis_label="secuencia de B", y_axis_label="secuencia de A")
    fig.rect(x=xs, y=ys, width=0.94, height=0.94, fill_color=colours, fill_alpha=alphas, line_color=None)
    fig.text(x=xs, y=ys, text=texts, text_align="center", text_baseline="middle", text_font_size="11px",
             text_color="#ffffff" if dark else "#1a1a1a")
    ia, ib = SEQUENCES.index(a), SEQUENCES.index(b)
    fig.rect(x=[ib], y=[n - 1 - ia], width=0.98, height=0.98, fill_alpha=0, line_color=ui.UBU_YELLOW,
             line_width=4)
    fig.xaxis.ticker = list(range(n))
    fig.yaxis.ticker = list(range(n))
    fig.xaxis.major_label_overrides = {j: s for j, s in enumerate(SEQUENCES)}
    fig.yaxis.major_label_overrides = {n - 1 - i: s for i, s in enumerate(SEQUENCES)}
    fig.xaxis.major_label_orientation = 0.8
    fig.grid.visible = False
    return fig


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Y si el problema se parece a sí mismo?</b>")
        ui.content(
            "El teorema de la probabilidad total pide una partición del espacio muestral. En los "
            "problemas que avanzan paso a paso hay una partición natural: lo que ocurre en el <b>primer "
            "paso</b>. Condicionando a él, muchas veces lo que queda es el mismo problema con otros "
            "datos de partida, y la probabilidad buscada aparece a los dos lados de la ecuación.<br><br>"
            "<i>Trata de escribir la idea con la probabilidad total.</i>"
        )
        ui.formula_hidden(
            "&#8473;(A) = &sum;<sub>i</sub> &#8473;(A | primer paso = i)&middot;&#8473;(primer paso = i)",
            hint="Pulsa para revelar la descomposición",
        )
        ui.content(
            "Si &#8473;(A | primer paso = i) es la misma probabilidad pero empezando en otro estado, se "
            "obtiene una ecuación en recurrencia o un sistema lineal. Es la herramienta con la que "
            "Pascal, Fermat y Huygens resolvieron el problema más antiguo de esta ficha, y la que se usa "
            "hoy para analizar cualquier cadena de Markov."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La ruina del jugador (1656)</b><br>"
            "<i>Calcula con Pascal y Huygens la probabilidad de arruinarse apostando tharni a tharni.</i>"
            "<br><br>"
            "<b>II. La tarjeta de embarque perdida</b><br>"
            "<i>Cien pasajeros, un despistado y una respuesta que no depende de cuántos sean.</i><br><br>"
            "<b>III. El juego de Penney (1969)</b><br>"
            "<i>Elige una secuencia de caras y cruces; tu rival siempre podrá elegir una mejor.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>capital inicial k</u>, la <u>meta N</u> y el <u>juego</u>")
        c1, c2 = st.columns(2)
        n = c2.slider("Meta N (tharni)", 5, 60, v["target"], 1, key=ui.wkey(PAGE, "target"))
        k = c1.slider("Capital inicial k (tharni)", 1, n - 1, min(v["capital"], n - 1), 1,
                      key=ui.wkey(PAGE, f"capital{n}"))
        odds = st.radio("Probabilidad de ganar cada ronda", list(P_OPTIONS),
                        index=list(P_OPTIONS).index(v["odds"]), horizontal=True, key=ui.wkey(PAGE, "odds"))
        p = P_OPTIONS[odds]

        ui.planteamiento()
        ui.statement(
            "<b>La ruina del jugador (1656)</b><br><br>"
            "Pascal planteó a Fermat este problema en 1656, y Huygens lo incluyó al año siguiente como el "
            "último de su tratado sobre los juegos de azar, el primero que se imprimió. En nuestra "
            f"versión un jugador entra en el casino con k = {v['capital']} tharni y apuesta un tharni en "
            "cada ronda, que gana con probabilidad p. Se marcha cuando reúne "
            f"N = {v['target']} tharni o cuando se arruina. ¿Qué probabilidad tiene de salir con los "
            "bolsillos vacíos?"
        )

        if ui.accordion_step("P1_A", "(A) El primer paso"):
            ui.content(
                "Llama P<sub>k</sub> a la probabilidad de ruina empezando con k tharni. Condiciona al "
                "resultado de la primera ronda y escribe una ecuación para P<sub>k</sub>. ¿Cuánto valen "
                "P<sub>0</sub> y P<sub>N</sub>?"
            )
            ui.spoiler(
                "Si gana la primera ronda, el problema empieza de nuevo con k + 1 tharni; si la pierde, "
                "con k &minus; 1. Por el teorema de la probabilidad total, con q = 1 &minus; p:"
                "<div class='formula-box'>P<sub>k</sub> = p&middot;P<sub>k+1</sub> + q&middot;P<sub>k&minus;1</sub>, "
                "&nbsp; P<sub>0</sub> = 1, &nbsp; P<sub>N</sub> = 0</div>"
                "Una recurrencia lineal con dos condiciones de contorno."
            )

        if ui.accordion_step("P1_B", "(B) Resolver la recurrencia"):
            ui.content(
                "Resuelve la recurrencia en el caso justo (p = q = 1/2) y en el caso general. Pista: en el "
                "caso justo las diferencias P<sub>k+1</sub> &minus; P<sub>k</sub> son todas iguales."
            )
            ui.spoiler(
                "En el juego justo P<sub>k</sub> es lineal en k y las condiciones de contorno dan "
                "P<sub>k</sub> = 1 &minus; k&frasl;N. En general, con &rho; = q&frasl;p:"
                "<div class='formula-box'>P<sub>k</sub> = <sup>&rho;<sup>k</sup> &minus; &rho;<sup>N</sup></sup>"
                "&frasl;<sub>1 &minus; &rho;<sup>N</sup></sub></div>"
                "La curva roja de la derecha es esta fórmula para cada capital inicial."
            )

        if ui.accordion_step("P1_C", "(C) Contra la banca"):
            ui.content(
                "Elige la ruleta (apostar al rojo, p = 18/37) y compara con el juego justo. ¿Cuánto cambia "
                "una desventaja tan pequeña? ¿Qué pasa si la meta N es muy grande?"
            )
            ui.spoiler(
                "Una desventaja de apenas un 2.7 % por ronda se acumula: con k = 10 y N = 30 la ruina pasa "
                "de dos tercios a más del 80 %. Y si N crece sin límite con p &lt; 1/2, &rho;<sup>N</sup> se "
                "dispara y P<sub>k</sub> tiende a 1: quien juega contra la banca sin un objetivo para "
                "retirarse acaba arruinado con probabilidad uno. Ni siquiera el juego justo salva a quien "
                "no se retira: 1 &minus; k&frasl;N también tiende a 1."
            )

    with col_right:
        ui.right_panel()
        ruin = ruin_probability(k, n, p)
        ui.metrics([
            (f"&#8473;(ruina) = {ruin:.4f}", "result-no" if ruin > 0.5 else "result-yes"),
            (f"&#8473;(llegar a {n}) = {1 - ruin:.4f}", "metric-a"),
        ])
        ui.show(ruin_chart(dark, k, n, p), key="fig_ruin")
        if st.button("Jugar 2000 partidas", key="ruin_play", width="stretch", type="primary"):
            freq, paths = play_ruin(k, n, p, 2000, np.random.default_rng())
            st.session_state["ruin_sim"] = (k, n, p, freq, paths)
        sim = st.session_state.get("ruin_sim")
        if sim and sim[:3] == (k, n, p):
            ui.show(paths_chart(dark, sim[4], n), key="fig_ruin_paths")
            ui.footer_bar(f"En 2000 partidas simuladas el jugador se arruinó con frecuencia {sim[3]:.4f}. Las "
                          "líneas muestran doce de ellas, hasta que tocan 0 o N.")
        else:
            ui.footer_bar("Pulsa el botón para jugar muchas partidas y comparar con la fórmula.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de pasajeros n</u>")
        n = st.select_slider("Pasajeros n", options=[3, 5, 10, 20, 50, 100, 150, 200], value=v["passengers"],
                             key=ui.wkey(PAGE, "passengers"))

        ui.planteamiento()
        ui.statement(
            "<b>La tarjeta de embarque perdida</b><br><br>"
            "Peter Winkler recogió en 2004 este acertijo en su colección de problemas para conocedores, y "
            "desde entonces circula por las entrevistas de trabajo. Un avión tiene n asientos y n "
            f"pasajeros con billete numerado (en nuestro vuelo, n = {v['passengers']}). El primero en "
            "embarcar ha perdido la tarjeta y se sienta en un asiento al azar. Cada uno de los siguientes "
            "se sienta en el suyo si está libre, y si no, en uno libre al azar. ¿Qué probabilidad tiene el "
            "último pasajero de encontrar libre su asiento?"
        )

        if ui.accordion_step("P2_A", "(A) Con tres pasajeros"):
            ui.content(
                "Haz el árbol con n = 3. El primero elige su propio asiento, el del segundo o el del "
                "tercero, cada uno con probabilidad 1/3. ¿Qué ocurre en cada rama?"
            )
            ui.spoiler(
                "Si elige el suyo, todos se sientan bien. Si elige el del tercero, el tercero pierde. Si "
                "elige el del segundo, este elige al azar entre los dos libres, el del primero y el del "
                "tercero. Por la probabilidad total:"
                "<div class='formula-box'>&#8473; = <sup>1</sup>&frasl;<sub>3</sub>&middot;1 + "
                "<sup>1</sup>&frasl;<sub>3</sub>&middot;<sup>1</sup>&frasl;<sub>2</sub> + "
                "<sup>1</sup>&frasl;<sub>3</sub>&middot;0 = <sup>1</sup>&frasl;<sub>2</sub></div>"
            )

        if ui.accordion_step("P2_B", "(B) El primer paso, en general"):
            ui.content(
                "Con n pasajeros, condiciona a la elección del primero. ¿Qué pasa si elige su asiento, el "
                "del último o el de otro pasajero i? Fíjate en qué dos asientos quedan siempre en juego."
            )
            ui.spoiler(
                "Si el primero elige su asiento, el último gana; si elige el del último, pierde. Si elige "
                "el de un pasajero i intermedio, todos hasta i se sientan bien y el pasajero i queda en la "
                "misma situación que el primero, con menos asientos. En cada momento el asiento del "
                "primero y el del último se tratan exactamente igual, y el proceso acaba cuando alguien "
                "ocupa uno de los dos: por simetría,"
                "<div class='formula-box'>&#8473;(el último se sienta en su asiento) = <sup>1</sup>&frasl;<sub>2</sub></div>"
                "para cualquier n &ge; 2."
            )

        if ui.accordion_step("P2_C", "(C) ¿Y los demás pasajeros?"):
            ui.content(
                "¿Qué probabilidad tiene el pasajero j de sentarse en su asiento? Usa el mismo argumento "
                "de simetría con los asientos que quedan cuando le toca embarcar."
            )
            ui.spoiler(
                "Cuando embarca el pasajero j, su asiento está ocupado solo si el desplazamiento ha "
                "llegado hasta él. Repitiendo el argumento con los asientos 1, j, j + 1, &hellip;, n, que "
                "son equivalentes hasta ese momento:"
                "<div class='formula-box'>&#8473;(el pasajero j se sienta en su asiento) = "
                "<sup>n &minus; j + 1</sup>&frasl;<sub>n &minus; j + 2</sub>, &nbsp; j &ge; 2</div>"
                "Casi todos se sientan bien; el riesgo se concentra en los últimos en embarcar."
            )

    with col_right:
        ui.right_panel()
        ui.metric("&#8473;(el último en su asiento) = 0.5000", "metric-a")
        if st.button("Simular 2000 vuelos", key="plane_play", width="stretch", type="primary"):
            st.session_state["plane_sim"] = (n, board(n, 2000, np.random.default_rng()))
        sim = st.session_state.get("plane_sim")
        simulated = sim[1] if sim and sim[0] == n else None
        ui.show(plane_chart(dark, n, simulated), key="fig_plane")
        if simulated is not None:
            ui.footer_bar(f"En 2000 vuelos simulados el último pasajero encontró su asiento con frecuencia "
                          f"{simulated[-1]:.4f}.")
        else:
            ui.footer_bar("Pulsa el botón para simular vuelos y comparar con la curva teórica.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige las <u>secuencias de A y de B</u> y la <u>moneda</u>")
        c1, c2 = st.columns(2)
        a = c1.selectbox("Secuencia de A", SEQUENCES, index=SEQUENCES.index(v["seq_a"]), key=ui.wkey(PAGE, "seq_a"))
        b = c2.selectbox("Secuencia de B", SEQUENCES, index=SEQUENCES.index(v["seq_b"]), key=ui.wkey(PAGE, "seq_b"))
        p = st.slider("Probabilidad de cara p", 0.30, 0.70, 0.50, 0.01, key="penney_p")

        ui.planteamiento()
        ui.statement(
            "<b>El juego de Penney (1969)</b><br><br>"
            "Walter Penney propuso en una revista de matemática recreativa un juego para dos: cada "
            "jugador elige una secuencia de tres lanzamientos de moneda (C cara, X cruz), se lanza la "
            "moneda una y otra vez, y gana aquel cuya secuencia aparece antes. Apuestan un tharni. Parece "
            "que, con una moneda justa, todas las secuencias deberían valer lo mismo. Martin Gardner lo "
            "popularizó unos años después, y John Conway encontró una regla para elegir siempre la mejor respuesta."
        )

        if ui.accordion_step("P3_A", "(A) Las ecuaciones del primer paso"):
            ui.content(
                "Para saber quién gana solo importan los dos últimos lanzamientos. Llama x<sub>s</sub> a la "
                "probabilidad de que gane A si los últimos lanzamientos son s (s vacío al principio, o C, X, "
                "CC, CX, XC, XX). Condiciona al siguiente lanzamiento y escribe una ecuación para cada "
                "estado."
            )
            ui.spoiler(
                "Para cada estado s, por la probabilidad total sobre el siguiente lanzamiento:"
                "<div class='formula-box'>x<sub>s</sub> = p&middot;x<sub>s&#8226;C</sub> + "
                "(1 &minus; p)&middot;x<sub>s&#8226;X</sub></div>"
                "donde s&#8226;C son los dos últimos lanzamientos tras añadir C, salvo que los tres últimos "
                "formen la secuencia de A (entonces vale 1) o la de B (entonces vale 0). Son siete "
                "ecuaciones lineales con siete incógnitas; la aplicación las resuelve y la respuesta es "
                "x<sub>&empty;</sub>."
            )

        if ui.accordion_step("P3_B", "(B) La respuesta de Conway"):
            ui.content(
                "Mira la fila de A en la tabla de la derecha. ¿Hay alguna secuencia que pierda contra "
                "todas las demás, o que gane a todas? Para cada elección de A, busca la mejor respuesta de B."
            )
            ui.spoiler(
                "Si A elige a<sub>1</sub>a<sub>2</sub>a<sub>3</sub>, la mejor respuesta es "
                "(contrario de a<sub>2</sub>)&nbsp;a<sub>1</sub>&nbsp;a<sub>2</sub>: termina justo como empieza "
                "la secuencia de A, de modo que casi siempre que A está a punto de aparecer, la de B ya ha "
                "aparecido un lanzamiento antes. Con moneda justa esta respuesta gana al menos dos de cada "
                "tres veces, y contra CCC o XXX gana siete de cada ocho."
            )

        if ui.accordion_step("P3_C", "(C) Un juego no transitivo"):
            ui.content(
                "Encadena respuestas: a CCX la vence XCC, a XCC la vence XXC, a XXC la vence CXX, ¿y a CXX? "
                "¿Qué tiene esto de raro? ¿Quién debe elegir primero si se juegan tharni?"
            )
            ui.spoiler(
                "Se cierra el ciclo: a CXX la vence CCX. Como en piedra, papel o tijera, la relación "
                "<i>vence a</i> no es transitiva, así que no existe una secuencia mejor que todas. Quien "
                "elige en segundo lugar siempre puede quedarse con ventaja: si te proponen este juego, "
                "deja elegir primero al otro."
            )

    with col_right:
        ui.right_panel()
        if a == b:
            ui.comment("Elige dos secuencias distintas.")
            return
        prob = penney(a, b, p)
        best = best_reply(a, p)
        ui.metrics([
            (f"&#8473;(gana A) = {prob:.4f}", "result-yes" if prob > 0.5 else "result-no"),
            (f"Mejor respuesta a {a}: {best} ({1 - penney(a, best, p):.3f})", "metric-c"),
        ])
        ui.show(penney_chart(dark, a, b, p), key="fig_penney")
        ui.footer_bar(f"Cada casilla es la probabilidad de que la secuencia de su fila aparezca antes que la de "
                      f"su columna. Ganancia media de A apostando un tharni: {2 * prob - 1:+.4f} tharni.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La ruina del jugador", "P1_A"),
        ("P2", "(II) La tarjeta de embarque", "P2_A"),
        ("P3", "(III) El juego de Penney", "P3_A"),
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
