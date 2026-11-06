#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 1: la probabilidad condicionada.

La lluvia según la estación (restringir el espacio muestral), Linda la cajera
(falacia de la conjunción), la caja de Bertrand (contar monedas y no cajas) y
los hijos del señor Smith (la forma de obtener la información importa).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Probabilidad condicionada"
SYMBOL = "P(A|B)"
PAGE = "02_01"

SEASONS = ["Primavera", "Verano", "Otoño", "Invierno"]
BASE_RAIN = [0.50, 0.15, 0.60, 0.70]

INFOS = {
    "older": "El mayor es niño",
    "some": "Al menos uno es niño",
    "tuesday": "Al menos uno es niño nacido en martes",
}


def initial_values():
    return {
        "humidity": ui.dfloat(1.0, 0.6, 1.3, "humidity", 1),
        "linda": ui.dchoice(60, [30, 40, 50, 60, 70, 80], "linda"),
        "gg": ui.dint(1, 1, 4, "gg"),
        "ss": ui.dint(1, 0, 4, "ss"),
        "gs": ui.dint(1, 1, 4, "gs"),
        "boy": ui.dfloat(0.50, 0.46, 0.54, "boy"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "info": "older", "box_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def bertrand(gg: int, ss: int, gs: int) -> float:
    """P(la otra moneda es de oro | se ha visto una de oro)."""
    gold_faces = 2 * gg + gs
    return 2 * gg / gold_faces if gold_faces else float("nan")


def simulate_boxes(gg: int, ss: int, gs: int, draws: int, rng):
    boxes = np.array([0] * gg + [1] * ss + [2] * gs)
    chosen = boxes[rng.integers(len(boxes), size=draws)]
    coin = rng.integers(2, size=draws)
    seen_gold = (chosen == 0) | ((chosen == 2) & (coin == 0))
    other_gold = chosen == 0
    return int(seen_gold.sum()), int((seen_gold & other_gold).sum())


def children_grid(info: str, p: float):
    """Celdas (mayor, menor) con su peso, si están en la condición y si son dos niños."""
    days = 7 if info == "tuesday" else 1
    kinds = [("niño", d) for d in range(days)] + [("niña", d) for d in range(days)]
    cells = []
    for i, (s1, d1) in enumerate(kinds):
        for j, (s2, d2) in enumerate(kinds):
            w = (p if s1 == "niño" else 1 - p) * (p if s2 == "niño" else 1 - p) / days ** 2
            if info == "older":
                cond = s1 == "niño"
            elif info == "some":
                cond = s1 == "niño" or s2 == "niño"
            else:
                cond = (s1 == "niño" and d1 == 1) or (s2 == "niño" and d2 == 1)
            cells.append((i, j, w, cond, s1 == "niño" and s2 == "niño"))
    return cells, len(kinds)


def children_probability(info: str, p: float) -> float:
    cells, _ = children_grid(info, p)
    den = sum(w for _, _, w, cond, _ in cells if cond)
    num = sum(w for _, _, w, cond, both in cells if cond and both)
    return num / den


# =============================================================================
# 2. FIGURAS
# =============================================================================

def seasons_chart(dark, ps, sel_idx, pa):
    p = ui.new_figure(dark, height=330, x_range=SEASONS, y_range=(0, 1.0), y_axis_label="fracción de días")
    p.vbar(x=SEASONS, top=ps, width=0.8, fill_color=ui.BLUE_LINE, fill_alpha=0.8, line_color=None)
    p.vbar(x=SEASONS, bottom=ps, top=1.0, width=0.8, fill_color=ui.GREY_LINE, fill_alpha=0.25,
           line_color=None)
    p.vbar(x=[SEASONS[sel_idx]], top=1.0, width=0.84, fill_alpha=0, line_color=ui.UBU_RED, line_width=4)
    p.add_layout(Span(location=pa, dimension="width", line_color=ui.GREEN_LINE, line_dash="dashed",
                      line_width=2))
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "15px"
    return p


def linda_bars(dark, p_fc):
    cats = ["Cajeras", "Cajeras y feministas"]
    p = ui.new_figure(dark, height=320, x_range=cats, y_range=(0, 1.05),
                      y_axis_label="proporción respecto a las cajeras")
    p.vbar(x=cats, top=[1.0, p_fc], width=0.6, fill_color=[ui.BLUE_LINE, ui.UBU_RED], line_color=None)
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "15px"
    return p


def boxes_svg(dark, gg: int, ss: int, gs: int) -> str:
    gold, silver = "#d4a017", "#b8bcc6"
    fg = "#e6e6e6" if dark else "#333333"
    boxes = [("O", "O")] * gg + [("P", "P")] * ss + [("O", "P")] * gs
    per_row = 4
    rows = (len(boxes) - 1) // per_row + 1
    parts = []
    for idx, (c1, c2) in enumerate(boxes):
        r, c = divmod(idx, per_row)
        x0, y0 = 10 + c * 105, 10 + r * 70
        parts.append(f'<rect x="{x0}" y="{y0}" width="95" height="56" rx="10" fill="none" '
                     f'stroke="{fg}" stroke-width="2"/>')
        for k, coin in enumerate((c1, c2)):
            cx = x0 + 26 + k * 43
            partner_gold = (c2 if k == 0 else c1) == "O"
            fill = gold if coin == "O" else silver
            ring = ""
            if coin == "O":
                ring_colour = ui.GREEN_LINE if partner_gold else ui.RED_LINE
                ring = (f'<circle cx="{cx}" cy="{y0 + 28}" r="19" fill="none" stroke="{ring_colour}" '
                        f'stroke-width="4"/>')
            parts.append(f'<circle cx="{cx}" cy="{y0 + 28}" r="14" fill="{fill}" stroke="#555" '
                         f'stroke-width="1.5"/>{ring}')
    height = 20 + rows * 70
    return (f'<svg viewBox="0 0 430 {height}" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(parts)}</svg>')


def children_chart(dark, info: str, p: float):
    cells, n = children_grid(info, p)
    xs, ys, colours, alphas = [], [], [], []
    for i, j, w, cond, both in cells:
        xs.append(j)
        ys.append(n - 1 - i)
        if not cond:
            colours.append(ui.GREY_LINE); alphas.append(0.15)
        elif both:
            colours.append(ui.GREEN_LINE); alphas.append(0.85)
        else:
            colours.append(ui.UBU_RED); alphas.append(0.6)
    p = ui.new_figure(dark, height=340, x_range=(-0.5, n - 0.5), y_range=(-0.5, n - 0.5),
                      match_aspect=True, x_axis_label="hijo menor", y_axis_label="hijo mayor")
    p.rect(x=xs, y=ys, width=0.92, height=0.92, fill_color=colours, fill_alpha=alphas, line_color=None)
    p.grid.visible = False
    half = n // 2
    if n == 2:
        p.xaxis.ticker = [0, 1]
        p.yaxis.ticker = [0, 1]
        p.xaxis.major_label_overrides = {0: "niño", 1: "niña"}
        p.yaxis.major_label_overrides = {1: "niño", 0: "niña"}
    else:
        p.xaxis.ticker = [half / 2 - 0.5, half + half / 2 - 0.5]
        p.yaxis.ticker = [half / 2 - 0.5, half + half / 2 - 0.5]
        p.xaxis.major_label_overrides = {half / 2 - 0.5: "niño (L-D)", half + half / 2 - 0.5: "niña (L-D)"}
        p.yaxis.major_label_overrides = {half + half / 2 - 0.5: "niño", half / 2 - 0.5: "niña"}
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es la probabilidad condicionada?</b>")
        ui.content(
            "La probabilidad condicionada es la posibilidad de que ocurra un suceso A <b>sabiendo que ya "
            "ha ocurrido</b> otro suceso B. Si alguien nos pregunta a quién votará una persona elegida al "
            "azar, nuestra respuesta cambia en cuanto nos dicen que es joven, o que preside el club de "
            "fútbol del pueblo. La información previa reduce el espacio de posibilidades: ya no miramos "
            "todo &Omega;, solo la parte compatible con B.<br><br>"
            "<i>En palabras: la probabilidad de A dado B es la parte de B que también está en A, dividida "
            "entre todo B. Prueba a escribirlo.</i>"
        )
        ui.formula_hidden("&#8473;(A | B) = <sup>&#8473;(A &cap; B)</sup>&frasl;<sub>&#8473;(B)</sub>, "
                          "&nbsp; con &#8473;(B) &gt; 0", hint="Pulsa para revelar la definición")
        ui.content(
            "Restringirse a B no rompe nada: la función A &#8614; &#8473;(A | B) vuelve a cumplir los "
            "tres axiomas de Kolmogórov, así que es una probabilidad con todas las de la ley sobre el "
            "nuevo espacio B. <i>Comprueba el axioma de normalización.</i>"
        )
        ui.formula_hidden("&#8473;(&Omega; | B) = <sup>&#8473;(&Omega; &cap; B)</sup>&frasl;"
                          "<sub>&#8473;(B)</sub> = <sup>&#8473;(B)</sup>&frasl;<sub>&#8473;(B)</sub> = 1")
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Linda la cajera (1983)</b><br><i>Descubre por qué la mayoría de la gente se equivoca "
            "con la falacia de la conjunción.</i><br><br>"
            "<b>II. La caja de Bertrand (1889)</b><br><i>Tres cajas, seis monedas y una respuesta que "
            "casi todo el mundo da mal a la primera.</i><br><br>"
            "<b>III. Los hijos del señor Smith (1959)</b><br><i>Con Martin Gardner, comprueba que la "
            "misma frase puede llevar a probabilidades distintas según cómo se haya obtenido.</i>"
        )

    with col_right:
        ui.right_panel()
        ui.section("Pruébalo: &Omega; partido en cuatro estaciones")
        sel = st.radio("¿Qué estación ha ocurrido? (suceso B)", SEASONS, horizontal=True, key="season_sel")
        factor = st.slider("Factor de humedad del año", 0.4, 1.4, v["humidity"], 0.1,
                           key=ui.wkey(PAGE, "humidity"))
        ps = [min(1.0, b * factor) for b in BASE_RAIN]
        sel_idx = SEASONS.index(sel)
        p_a = sum(ps) / 4
        ui.metrics([
            (f"&#8473;(lluvia | {sel}) = {ps[sel_idx]:.2f}", "metric-a"),
            (f"&#8473;(lluvia) = {p_a:.2f}", "metric-b"),
        ])
        ui.show(seasons_chart(dark, ps, sel_idx, p_a), key="fig_seasons")
        ui.footer_bar(
            "A = «día de lluvia» y B = estación del año. La probabilidad de lluvia cambia según la "
            "estación (azul = A dentro de cada B); la línea verde marca &#8473;(A) en todo el año. Saber la "
            "estación lo cambia todo."
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Linda la cajera (1983)</b><br><br>"
            "El problema de «Linda la cajera», diseñado por los psicólogos Daniel Kahneman y Amos "
            "Tversky en 1983, es uno de los recursos más célebres para introducir la probabilidad de la "
            "intersección y la condicionada."
        )

        if ui.accordion_step("P1_A", "(A) Conocer a Linda"):
            ui.content(
                "Linda tiene 31 años, es soltera, franca y muy brillante. Se especializó en Filosofía y de "
                "estudiante le preocupaban la discriminación y la justicia social.<br><br>"
                "<b>¿Qué te parece más probable?</b><br>&bull; Opción A: Linda es cajera de banco.<br>"
                "&bull; Opción B: Linda es cajera de banco <b>y</b> activista feminista."
            )
            ui.spoiler("En los experimentos originales, alrededor del <b>85 %</b> de las personas eligió la "
                       "opción B. Pero, ¿es eso matemáticamente posible?")

        if ui.accordion_step("P1_B", "(B) El error: la falacia de la conjunción"):
            ui.content(
                "Sea C = «ser cajera» y F = «ser feminista». Las cajeras que además son feministas "
                "(C &cap; F) forman un <b>subconjunto</b> de todas las cajeras (C). Por tanto la "
                "intersección nunca puede ser más probable que el todo.<br><br>"
                "<i>Trata de escribir la desigualdad y di qué propiedad de la probabilidad la justifica.</i>"
            )
            ui.formula_hidden("C &cap; F &sub; C &nbsp;&rArr;&nbsp; &#8473;(C &cap; F) &le; &#8473;(C)",
                              hint="Pulsa para revelar la desigualdad")

        if ui.accordion_step("P1_C", "(C) Por qué nos engaña el cerebro"):
            ui.content(
                "El cerebro no calcula la intersección &#8473;(C &cap; F); en su lugar evalúa sin darse "
                "cuenta una <b>condicionada</b>: &#8473;(F | C), lo bien que «encaja» el perfil. "
                "Escribe la intersección con la regla de la multiplicación y explica por qué nunca "
                "supera a &#8473;(C)."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(C &cap; F) = &#8473;(F | C) &middot; &#8473;(C)</div>"
                "Como &#8473;(F | C) es un número entre 0 y 1, al multiplicarlo por &#8473;(C) nunca puede "
                "aumentar la probabilidad. <b>Moraleja:</b> confundimos condicionadas con intersecciones."
            )

    with col_right:
        ui.right_panel()
        ui.section("El experimento original, en una gráfica")
        ui.comment("Muchos colocaron «cajera y feminista» por encima de «cajera», algo imposible: "
                   "mueve el deslizador y verás que la barra roja nunca supera a la azul.")
        p_fc = st.slider("De cada 100 cajeras, ¿cuántas crees que son feministas? (P(F | C), %)",
                         0, 100, v["linda"], 5, key=ui.wkey(PAGE, "linda")) / 100.0
        ui.show(linda_bars(dark, p_fc), key="fig_linda")
        ui.footer_bar(f"&#8473;(cajera y feminista) = &#8473;(F | C)&middot;&#8473;(cajera) = "
                      f"{p_fc:.2f}&middot;&#8473;(cajera) &le; &#8473;(cajera). La conjunción nunca gana.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de cajas</u> de cada tipo")
        c1, c2, c3 = st.columns(3)
        gg = c1.number_input("Oro y oro", 0, 4, v["gg"], key=ui.wkey(PAGE, "gg"))
        ss = c2.number_input("Plata y plata", 0, 4, v["ss"], key=ui.wkey(PAGE, "ss"))
        gs = c3.number_input("Oro y plata", 0, 4, v["gs"], key=ui.wkey(PAGE, "gs"))

        ui.planteamiento()
        ui.statement(
            "<b>La caja de Bertrand (1889)</b><br><br>"
            "Joseph Bertrand (1822-1900), secretario perpetuo de la Academia de Ciencias de París, llenó "
            "su <i>Cálculo de probabilidades</i> de problemas pensados para desconfiar de la intuición. "
            f"En nuestra versión hay {v['gg']} cajas con dos monedas de oro, {v['ss']} con dos de plata y "
            f"{v['gs']} con una de cada metal. Se elige una caja al azar, se saca una de sus dos monedas "
            "sin mirar la otra, y resulta ser de oro. ¿Qué probabilidad hay de que la otra también lo sea?"
        )

        if ui.accordion_step("P2_A", "(A) La respuesta de la intuición"):
            ui.content(
                "En la versión original (una caja de cada tipo) mucha gente razona así: <i>si he visto "
                "oro, la caja no es la de plata; quedan dos cajas posibles, luego la probabilidad es un "
                "medio</i>. ¿Dónde está el error?"
            )
            ui.spoiler(
                "Las dos cajas que quedan no son igual de verosímiles después de ver el oro: la de dos "
                "monedas de oro produce una moneda de oro siempre, y la mixta solo la mitad de las veces. "
                "Contar casos solo funciona si son equiprobables, y aquí los casos equiprobables son las "
                "monedas, no las cajas."
            )

        if ui.accordion_step("P2_B", "(B) Contar monedas, no cajas"):
            ui.content(
                "Sea O = <i>la moneda vista es de oro</i> y D = <i>la caja es de oro y oro</i>. Usa la "
                "definición de probabilidad condicionada, y obtén &#8473;(O) repartiendo entre los tres "
                "tipos de caja."
            )
            ui.spoiler(
                "Como D &sub; O, &#8473;(D &cap; O) = &#8473;(D). Las monedas de oro son todas igual de "
                "probables de ser la vista; hay 2 por cada caja de oro y oro y 1 por cada mixta:"
                "<div class='formula-box'>&#8473;(D | O) = <sup>&#8473;(D)</sup>&frasl;<sub>&#8473;(O)</sub> "
                "= <sup>2&middot;(oro y oro)</sup>&frasl;<sub>2&middot;(oro y oro) + (oro y plata)</sub></div>"
                "Con una caja de cada tipo sale 2/3, no 1/2. Las cajas de plata no influyen en el "
                "resultado: desaparecen al condicionar."
            )

        if ui.accordion_step("P2_C", "(C) Compruébalo sacando monedas"):
            ui.content(
                "Pulsa el botón de la derecha para repetir el experimento muchas veces. Entre las "
                "extracciones en que salió oro, ¿qué fracción tenía oro también en la otra moneda? "
                "¿Por qué la simulación tira a la basura las extracciones en que salió plata?"
            )
            ui.spoiler(
                "Simular una probabilidad condicionada es quedarse solo con las repeticiones en que "
                "ocurre la condición y contar dentro de ellas: es la definición frecuentista de "
                "&#8473;(A | B) como el cociente de las frecuencias de A &cap; B y de B. Bertrand usaba "
                "este ejemplo para avisar de lo peligroso que es el argumento <i>hay dos casos, luego es "
                "un medio</i>."
            )

    with col_right:
        ui.right_panel()
        if 2 * gg + gs == 0:
            ui.comment("Sin monedas de oro el suceso <i>la moneda vista es de oro</i> es imposible: la "
                       "probabilidad condicionada a él no está definida.")
            return
        prob = bertrand(gg, ss, gs)
        ui.metrics([("Intuición: 0.5000", "metric-c"), (f"&#8473;(D | O) = {prob:.4f}", "metric-a")])
        ui.svg(boxes_svg(dark, gg, ss, gs))
        ui.caption("Anillo verde: moneda de oro cuya compañera es de oro. Anillo rojo: compañera de plata.")
        if st.button("Sacar 2000 monedas", key="box_draw", width="stretch", type="primary"):
            st.session_state["box_sim"] = (gg, ss, gs, *simulate_boxes(gg, ss, gs, 2000,
                                                                      np.random.default_rng()))
        sim = st.session_state.get("box_sim")
        if sim and sim[:3] == (gg, ss, gs) and sim[3]:
            ui.footer_bar(f"Salió oro {sim[3]} veces; en {sim[4]} de ellas la otra moneda también era de "
                          f"oro: frecuencia {sim[4] / sim[3]:.4f}.")
        else:
            ui.footer_bar("Pulsa el botón para comprobar el resultado con monedas simuladas.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Los hijos del señor Smith (1959)</b><br><br>"
            "Martin Gardner (1914-2010) escribió durante veinticinco años la columna de juegos "
            "matemáticos de <i>Scientific American</i>. En 1959 propuso a sus lectores dos preguntas "
            "casi idénticas: el señor Jones tiene dos hijos y el mayor es una niña, ¿qué probabilidad hay "
            "de que ambos sean niñas?; el señor Smith tiene dos hijos y al menos uno es niño, ¿qué "
            "probabilidad hay de que ambos sean niños? Aquí lo planteamos con niños en los dos casos, y "
            "con la probabilidad de nacer niño como parámetro."
        )

        if ui.accordion_step("P3_A", "(A) El mayor es niño"):
            ui.content(
                "Toma como espacio muestral los pares (mayor, menor) y supón que el sexo de cada hijo es "
                "independiente del otro. Sabiendo que el mayor es niño, ¿cuál es la probabilidad de que "
                "los dos lo sean? Elige esa información a la derecha y mira qué celdas sobreviven."
            )
            ui.spoiler(
                "La condición deja dos celdas, (niño, niño) y (niño, niña), y su peso relativo solo "
                "depende del menor: por la independencia, &#8473;(dos niños | el mayor es niño) = "
                "&#8473;(el menor es niño) = p. Con p = 1/2 sale un medio, como dice la intuición."
            )

        if ui.accordion_step("P3_B", "(B) Al menos uno es niño"):
            ui.content(
                "Ahora la condición es <i>al menos uno es niño</i>. ¿Cuántas celdas sobreviven y cuánto "
                "pesa cada una? Gardner tuvo que publicar una aclaración: ¿qué cambia si la información "
                "viene de haber visto por la calle a uno de los dos hijos, elegido al azar, y ser niño?"
            )
            ui.spoiler(
                "Sobreviven tres celdas de igual peso cuando p = 1/2, y solo una tiene dos niños:"
                "<div class='formula-box'>&#8473;(dos niños | al menos uno) = "
                "<sup>p<sup>2</sup></sup>&frasl;<sub>1 &minus; (1 &minus; p)<sup>2</sup></sub></div>"
                "que vale 1/3 con p = 1/2. Pero si ves a uno de los hijos al azar y es niño, el suceso "
                "observado es otro: equivale a conocer el sexo de un hijo concreto, y la respuesta "
                "vuelve a ser un medio. La frase es la misma; el suceso por el que se condiciona, no."
            )

        if ui.accordion_step("P3_C", "(C) Un niño nacido en martes"):
            ui.content(
                "En 2010, en un encuentro en homenaje a Gardner, Gary Foshee planteó: <i>tengo dos hijos, "
                "uno es un niño nacido en martes; ¿qué probabilidad hay de que tenga dos niños?</i> "
                "¿Cómo puede importar el día de la semana? Elige esa opción a la derecha."
            )
            ui.spoiler(
                "Con el día de nacimiento la cuadrícula pasa a tener 14 &times; 14 celdas. La condición "
                "deja 27 celdas de igual peso (con p = 1/2) y 13 de ellas tienen dos niños: "
                "&#8473; = 13/27, muy cerca de un medio. Cuanto más rara es la característica "
                "mencionada, más se parece la información a señalar a un hijo concreto, y más se acerca "
                "la respuesta a la del apartado (A)."
            )

    with col_right:
        ui.right_panel()
        ui.choice_buttons(list(INFOS), "info", labels=INFOS, per_row=3)
        p = st.slider("Probabilidad de nacer niño p", 0.30, 0.70, v["boy"], 0.01, key=ui.wkey(PAGE, "boy"))
        info = st.session_state["info"]
        prob = children_probability(info, p)
        ui.metric(f"&#8473;(dos niños | {INFOS[info].lower()}) = {prob:.4f}", "metric-a")
        ui.show(children_chart(dark, info, p), key="fig_children")
        ui.footer_bar("En gris, las parejas descartadas por la información; en rojo, las compatibles; en "
                      "verde, las compatibles con dos niños. La probabilidad condicionada es el peso verde "
                      "dividido entre el peso rojo y verde.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Linda la cajera", "P1_A"),
        ("P2", "(II) La caja de Bertrand", "P2_A"),
        ("P3", "(III) Los hijos del señor Smith", "P3_A"),
    ])

    if current == "INTRO":
        render_intro(dark, v)
    elif current == "P1":
        render_problem_1(dark, v)
    elif current == "P2":
        render_problem_2(dark, v)
    elif current == "P3":
        render_problem_3(dark, v)

    ui.footer()


main()
