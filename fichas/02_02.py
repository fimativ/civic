#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 2: la independencia.

La independencia como áreas, una demostración por etapas, el tetraedro de
Bernstein y dos dados (independencia dos a dos frente a mutua) y la noche de
Montecarlo de 1913 (la falacia del jugador).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Independencia"
SYMBOL = "A ⊥ B"
PAGE = "02_02"

DICE_CASES = {
    "AB": "A₂ ∩ B₂",
    "AC": "A₂ ∩ C₂",
    "BC": "B₂ ∩ C₂",
    "ABC": "A₂ ∩ B₂ ∩ C₂",
}
MAX_STREAK = 8


def initial_values():
    return {
        "pA": ui.dchoice(0.50, [0.3, 0.4, 0.5, 0.6, 0.7], "pA"),
        "pB": ui.dchoice(0.40, [0.2, 0.3, 0.4, 0.5, 0.6], "pB"),
        "spins": ui.dchoice(100000, [50000, 100000, 200000, 300000], "spins"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P2_A", "dice_case": "AB", "roulette": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def spin_roulette(n: int, rng):
    """Ruleta europea: 0 verde, 18 rojos y 18 negros. Devuelve las frecuencias de
    rojo tras al menos k negros seguidos y la racha negra más larga."""
    pockets = rng.integers(37, size=n)
    red = (pockets >= 1) & (pockets <= 18)
    black = pockets >= 19
    idx = np.arange(n)
    last_break = np.maximum.accumulate(np.where(~black, idx, -1))
    run_end = np.where(black, idx - last_break, 0)
    run_before = np.concatenate(([0], run_end[:-1]))
    freqs, counts = [], []
    for k in range(MAX_STREAK + 1):
        mask = run_before >= k
        counts.append(int(mask.sum()))
        freqs.append(float(red[mask].mean()) if mask.any() else float("nan"))
    return {"n": n, "freqs": freqs, "counts": counts, "longest": int(run_end.max())}


# =============================================================================
# 2. FIGURAS
# =============================================================================

def independence_square(dark, pA, pB):
    p = ui.new_figure(dark, height=360, x_range=(0, 1), y_range=(0, 1), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    p.outline_line_color = ui.GREY_LINE
    p.quad(left=0, right=pA, bottom=0, top=1, fill_color=ui.BLUE_LINE, fill_alpha=0.18, line_color=None)
    p.quad(left=0, right=1, bottom=0, top=pB, fill_color=ui.GREEN_LINE, fill_alpha=0.18, line_color=None)
    p.quad(left=0, right=pA, bottom=0, top=pB, fill_color=ui.UBU_RED, fill_alpha=0.55, line_color=None)
    p.line([pA, pA], [0, 1], line_color=ui.BLUE_LINE, line_width=2)
    p.line([0, 1], [pB, pB], line_color=ui.GREEN_LINE, line_width=2)
    p.text([pA / 2], [0.93], text=["A"], text_color=ui.BLUE_LINE, text_font_size="18px", text_align="center")
    p.text([0.94], [pB / 2], text=["B"], text_color=ui.GREEN_LINE, text_font_size="18px", text_align="center",
           text_baseline="middle")
    p.text([pA / 2], [pB / 2], text=["A∩B"], text_color="#ffffff", text_font_size="15px",
           text_align="center", text_baseline="middle")
    return p


def dice_grid(dark, case: str):
    xs, ys, colours = [], [], []
    off = "#3a3a44" if dark else "#e3e3e3"
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            in_a, in_b, in_c = d1 % 2 == 0, d2 % 2 == 0, (d1 + d2) % 2 == 0
            hit = {"AB": in_a and in_b, "AC": in_a and in_c, "BC": in_b and in_c,
                   "ABC": in_a and in_b and in_c}[case]
            xs.append(d1)
            ys.append(d2)
            colours.append(ui.UBU_RED if hit else off)
    p = ui.new_figure(dark, height=340, x_range=(0.5, 6.5), y_range=(0.5, 6.5), match_aspect=True,
                      x_axis_label="primer dado", y_axis_label="segundo dado")
    p.rect(x=xs, y=ys, width=0.92, height=0.92, fill_color=colours, fill_alpha=0.9, line_color=None)
    p.xaxis.ticker = list(range(1, 7))
    p.yaxis.ticker = list(range(1, 7))
    p.grid.visible = False
    return p


def roulette_chart(dark, res):
    ks = list(range(MAX_STREAK + 1))
    p = ui.new_figure(dark, height=320, x_axis_label="negros seguidos antes de la tirada (al menos k)",
                      y_axis_label="frecuencia de rojo", x_range=(-0.6, MAX_STREAK + 0.6),
                      y_range=(0, 0.8))
    p.vbar(x=ks, top=res["freqs"], width=0.7, color=ui.RED_LINE, alpha=0.85)
    p.add_layout(Span(location=18 / 37, dimension="width", line_color=ui.GREY_LINE, line_dash="dashed",
                      line_width=2))
    p.xaxis.ticker = ks
    p.xgrid.grid_line_color = None
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuándo un suceso no informa sobre otro?</b>")
        ui.content(
            "Dos sucesos A y B son <b>independientes</b> si saber que ocurre uno no cambia la "
            "probabilidad del otro: &#8473;(A | B) = &#8473;(A). Llevando esa igualdad a la regla de la "
            "multiplicación se obtiene una definición que ya no exige que &#8473;(B) sea positiva."
            "<br><br><i>Trata de escribirla.</i>"
        )
        ui.formula_hidden("&#8473;(A &cap; B) = &#8473;(A) &middot; &#8473;(B)",
                          hint="Pulsa para revelar la definición")
        ui.content(
            "Si A no informa sobre B, tampoco debería informar sobre que B <i>no</i> ocurra. <i>Comprueba "
            "que A y B<sup>c</sup> son independientes si lo son A y B.</i>"
        )
        ui.formula_hidden(
            "&#8473;(A &cap; B<sup>c</sup>) = &#8473;(A) &minus; &#8473;(A &cap; B) = &#8473;(A) &minus; "
            "&#8473;(A)&#8473;(B) = &#8473;(A)&#8473;(B<sup>c</sup>)",
            hint="Pulsa para revelar la comprobación",
        )
        ui.content(
            "Lo mismo vale para A<sup>c</sup> y B, y para A<sup>c</sup> y B<sup>c</sup>. Con tres o más "
            "sucesos la cosa se complica: no basta con que sean independientes dos a dos, y lo verás con "
            "Bernstein."
        )
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Una demostración</b><br><i>Fuerza algebraicamente la independencia de dos "
            "sucesos.</i><br><br>"
            "<b>II. El tetraedro de Bernstein</b><br><i>Independencia dos a dos frente a independencia "
            "mutua, con un tetraedro pintado y dos dados.</i><br><br>"
            "<b>III. La noche de Montecarlo (1913)</b><br><i>Veintiséis negros seguidos en la ruleta, y "
            "muchos tharni perdidos por no entender la independencia.</i>"
        )

    with col_right:
        ui.right_panel()
        ui.section("Pruébalo: la independencia como áreas")
        pA = st.slider("P(A)", 0.05, 1.0, v["pA"], 0.05, key=ui.wkey(PAGE, "pA"))
        pB = st.slider("P(B)", 0.05, 1.0, v["pB"], 0.05, key=ui.wkey(PAGE, "pB"))
        ui.metrics([
            (f"&#8473;(A)&middot;&#8473;(B) = {pA * pB:.3f}", "metric-a"),
            (f"Área roja = {pA * pB:.3f}", "metric-b"),
        ])
        ui.show(independence_square(dark, pA, pB), key="fig_square")
        ui.footer_bar(
            "En el cuadrado unidad, A es una franja vertical y B una horizontal. Su intersección, el "
            "rectángulo rojo, tiene exactamente área &#8473;(A)&middot;&#8473;(B): la proporción de A "
            "que cae dentro de B es la misma que la de todo el cuadrado. Eso es la independencia."
        )


def render_problem_1():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Una demostración</b><br><br>"
            "En un espacio (&Omega;, &Ascr;, &#8473;), sean A, B y C sucesos con probabilidad positiva. Si "
            "se cumple que &#8473;(A|B) = &#8473;(A|B&cap;C)&middot;&#8473;(C) + "
            "&#8473;(A|B&cap;C<sup>c</sup>)&middot;&#8473;(C<sup>c</sup>) y además &#8473;(A|B&cap;C) &ne; "
            "&#8473;(A|B), demuestra que B y C son necesariamente independientes."
        )
        ui.content(
            "Sigue la demostración por etapas con el deslizador de la derecha: el texto explica cada paso "
            "y las fórmulas quedan ocultas para que intentes escribirlas primero."
        )
        ui.formula("&#8473;(B &cap; C) = &#8473;(B)&middot;&#8473;(C)")
        ui.content("Ese es el objetivo: llegar a esta igualdad, que es justo la definición de que B y C "
                   "sean independientes.")

    with col_right:
        ui.right_panel()
        ui.section("La demostración por etapas")
        etapa = ui.stage("dem_stage", 3)
        if etapa == 1:
            ui.content(
                "<b>Etapa 1 · Desarrollar los dos lados.</b><br>"
                "Aplicamos la definición de probabilidad condicionada a cada término del lado derecho, para "
                "que aparezcan las intersecciones triples.<br><br><i>Trata de escribirlo.</i>"
            )
            ui.formula_hidden(
                "&#8473;(A|B) = <sup>&#8473;(A&cap;B&cap;C)</sup>&frasl;<sub>&#8473;(B&cap;C)</sub>&middot;"
                "&#8473;(C) + <sup>&#8473;(A&cap;B&cap;C<sup>c</sup>)</sup>&frasl;"
                "<sub>&#8473;(B&cap;C<sup>c</sup>)</sub>&middot;&#8473;(C<sup>c</sup>)"
            )
            ui.content(
                "Y escribimos también el lado izquierdo como una única fracción, partiendo A&cap;B según C "
                "y su complementario (teorema de la probabilidad total).<br><br><i>Trata de escribirlo.</i>"
            )
            ui.formula_hidden(
                "&#8473;(A|B) = <sup>&#8473;(A&cap;B&cap;C) + &#8473;(A&cap;B&cap;C<sup>c</sup>)</sup>&frasl;"
                "<sub>&#8473;(B)</sub>"
            )
        elif etapa == 2:
            ui.content(
                "<b>Etapa 2 · Igualar y factorizar.</b><br>"
                "Igualamos las dos expresiones de &#8473;(A|B), agrupamos por C y C<sup>c</sup> y, tras "
                "operar los denominadores comunes, todo se factoriza en un <b>producto igual a cero</b>."
                "<br><br><i>Trata de escribir ese producto.</i>"
            )
            ui.formula_hidden(
                "[ &#8473;(B&cap;C) &minus; &#8473;(B)&#8473;(C) ] &middot; "
                "[ &#8473;(A|B&cap;C) &minus; &#8473;(A|B&cap;C<sup>c</sup>) ] = 0"
            )
        else:
            ui.content(
                "<b>Etapa 3 · Conclusión.</b><br>"
                "Si un producto es cero, uno de los factores lo es. El segundo no puede anularse: si "
                "&#8473;(A|B&cap;C) = &#8473;(A|B&cap;C<sup>c</sup>), entonces &#8473;(A|B&cap;C) = "
                "&#8473;(A|B), contra la hipótesis. Luego se anula el primero.<br><br>"
                "<i>Trata de escribir la conclusión.</i>"
            )
            ui.formula_hidden(
                "&#8473;(B&cap;C) &minus; &#8473;(B)&#8473;(C) = 0 &nbsp;&rArr;&nbsp; &#8473;(B&cap;C) = "
                "&#8473;(B)&#8473;(C) &nbsp; &#8718; &nbsp; (B y C independientes)",
                hint="Pulsa para revelar la conclusión",
            )


def render_problem_2(dark):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>El tetraedro de Bernstein</b><br><br>"
            "Serguéi Bernstein (1880-1968) propuso en 1917 una de las primeras axiomatizaciones de la "
            "probabilidad, dieciséis años antes que Kolmogórov, y dejó en su manual un ejemplo que todavía "
            "se usa: un tetraedro con una cara roja, otra verde, otra azul y la cuarta pintada con los tres "
            "colores. Nosotros haremos la misma cuenta con dos dados no cargados y los sucesos "
            "A<sub>2</sub> = <i>el primer dado es par</i>, B<sub>2</sub> = <i>el segundo dado es par</i> y "
            "C<sub>2</sub> = <i>la suma es par</i>. El espacio muestral tiene 36 resultados equiprobables."
        )

        if ui.accordion_step("P2_A", "(A) ¿A₂ y B₂ independientes?"):
            ui.content(
                "&#8473;(A<sub>2</sub>) = &#8473;(B<sub>2</sub>) = 1/2. La intersección (ambos pares) tiene "
                "9 casos de 36.<br><br><i>Trata de compararlo con el producto.</i>"
            )
            ui.formula_hidden(
                "&#8473;(A<sub>2</sub>&cap;B<sub>2</sub>) = <sup>9</sup>&frasl;<sub>36</sub> = "
                "<sup>1</sup>&frasl;<sub>4</sub> = &#8473;(A<sub>2</sub>)&middot;&#8473;(B<sub>2</sub>) "
                "&nbsp; &rArr; sí",
                hint="Pulsa para revelar la respuesta",
            )

        if ui.accordion_step("P2_B", "(B) ¿A₂ y C₂ independientes?"):
            ui.content(
                "&#8473;(C<sub>2</sub>) = 1/2 (par más par o impar más impar). La intersección con "
                "A<sub>2</sub> obliga al segundo dado a ser par: 9 casos de 36. ¿Y B<sub>2</sub> con "
                "C<sub>2</sub>?<br><br><i>Compáralo con el producto.</i>"
            )
            ui.formula_hidden(
                "&#8473;(A<sub>2</sub>&cap;C<sub>2</sub>) = &#8473;(B<sub>2</sub>&cap;C<sub>2</sub>) = "
                "<sup>1</sup>&frasl;<sub>4</sub> = &#8473;(A<sub>2</sub>)&middot;&#8473;(C<sub>2</sub>) "
                "&nbsp; &rArr; sí, aunque sorprenda",
                hint="Pulsa para revelar la respuesta",
            )

        if ui.accordion_step("P2_C", "(C) ¿A₂, B₂ y C₂ mutuamente independientes?"):
            ui.content(
                "Si el primer dado es par y el segundo es par, la suma es par forzosamente: la intersección "
                "triple son de nuevo esos 9 casos. Pero el producto de las tres probabilidades es 1/8."
                "<br><br><i>Compáralos, y haz la misma cuenta con el tetraedro de Bernstein.</i>"
            )
            ui.formula_hidden(
                "&#8473;(A<sub>2</sub>&cap;B<sub>2</sub>&cap;C<sub>2</sub>) = <sup>1</sup>&frasl;<sub>4</sub> "
                "&ne; <sup>1</sup>&frasl;<sub>8</sub> = &#8473;(A<sub>2</sub>)&#8473;(B<sub>2</sub>)"
                "&#8473;(C<sub>2</sub>) &nbsp; &rArr; no",
                hint="Pulsa para revelar la respuesta",
            )
            ui.spoiler(
                "En el tetraedro, cada color aparece en dos de las cuatro caras: probabilidad 1/2. Dos "
                "colores a la vez solo en la cara tricolor: 1/4, el producto. Pero los tres colores a la "
                "vez también tienen probabilidad 1/4, no 1/8. La independencia mutua exige la regla del "
                "producto para <i>todas</i> las subcolecciones, no solo para las parejas.",
                hint="Pulsa para revelar el caso del tetraedro",
            )

    with col_right:
        ui.right_panel()
        ui.section("Los 36 resultados")
        case = ui.choice_buttons(list(DICE_CASES), "dice_case", labels=DICE_CASES, per_row=4)
        products = {"AB": "1/4", "AC": "1/4", "BC": "1/4", "ABC": "1/8"}
        verdict = "no son mutuamente independientes" if case == "ABC" else "son independientes"
        ui.badge(f"{DICE_CASES[case]}: 9/36 = 0.250 &nbsp;|&nbsp; producto = {products[case]}")
        ui.show(dice_grid(dark, case), key="fig_dice")
        ui.footer_bar(f"En rojo, los casos de la intersección: los sucesos {verdict}. La independencia dos "
                      "a dos no garantiza la independencia mutua.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>La noche de Montecarlo (1913)</b><br><br>"
            "El 18 de agosto de 1913, en una mesa de ruleta del casino de Montecarlo, la bola cayó en "
            "negro veintiséis veces seguidas. A medida que la racha crecía, los jugadores apostaban "
            "cada vez más fuerte al rojo, convencidos de que <i>le tocaba</i>; cuando la racha terminó, "
            "la banca había ganado una fortuna. La ruleta europea tiene 37 casillas: 18 rojas, "
            "18 negras y el cero, verde. Cada tharni apostado al rojo devuelve dos si sale rojo."
        )

        if ui.accordion_step("P3_A", "(A) La racha"):
            ui.content(
                "Suponiendo que las tiradas son independientes, ¿cuál es la probabilidad de veintiséis "
                "negros seguidos? ¿Qué regla usas?"
            )
            ui.spoiler(
                "Para sucesos mutuamente independientes la probabilidad de la intersección es el producto:"
                "<div class='formula-box'>&#8473;(N<sub>1</sub> &cap; &ctdot; &cap; N<sub>26</sub>) = "
                "(18&frasl;37)<sup>26</sup></div>"
                "un número del orden de 10<sup>&minus;8</sup>. Rarísimo, pero en los casinos del mundo se "
                "hacen tantas tiradas que alguna racha así tenía que aparecer."
            )

        if ui.accordion_step("P3_B", "(B) ¿Le toca al rojo?"):
            ui.content(
                "Tras k negros seguidos, ¿cuál es la probabilidad de que la siguiente tirada sea roja? "
                "Lanza la simulación de la derecha y compara las barras para distintos k."
            )
            ui.spoiler(
                "Si las tiradas son independientes, condicionar a cualquier historia pasada no cambia nada:"
                "<div class='formula-box'>&#8473;(rojo | k negros seguidos) = &#8473;(rojo) = 18&frasl;37</div>"
                "Es literalmente la definición de independencia. La ruleta no tiene memoria, y las barras "
                "solo se separan de la línea discontinua por el ruido de muestreo, mayor cuanto más larga "
                "es la racha y menos veces se ha observado."
            )

        if ui.accordion_step("P3_C", "(C) Compensación o dilución"):
            ui.content(
                "Muchos jugadores justifican su apuesta con la ley de los grandes números: <i>a la larga, "
                "la frecuencia de rojos tiene que acercarse a 18/37, así que ahora deben salir más "
                "rojos</i>. ¿Qué falla? ¿Cuánto gana de media quien apuesta un tharni al rojo después de "
                "una racha negra?"
            )
            ui.spoiler(
                "La frecuencia se acerca a 18/37 por <b>dilución</b>, no por compensación: los veintiséis "
                "negros pesan cada vez menos entre miles de tiradas nuevas que se comportan como siempre. "
                "Y la ganancia media de un tharni al rojo es, después de cualquier racha,"
                "<div class='formula-box'>2 &middot; 18&frasl;37 &minus; 1 = &minus;1&frasl;37 tharni</div>"
                "La única ventaja en la mesa es la del cero, y es de la banca."
            )

    with col_right:
        ui.right_panel()
        n = st.select_slider("Tiradas simuladas", options=[20000, 50000, 100000, 200000, 300000, 500000],
                             value=v["spins"], key=ui.wkey(PAGE, "spins"))
        if st.button("Girar la ruleta", key="spin", width="stretch", type="primary"):
            st.session_state["roulette"] = spin_roulette(n, np.random.default_rng())
        res = st.session_state["roulette"]
        if res is None:
            ui.footer_bar("Pulsa el botón para girar la ruleta. La línea discontinua marcará 18/37.")
            return
        ui.metrics([
            (f"&#8473;(rojo) = {res['freqs'][0]:.4f}", "metric-a"),
            (f"Racha negra más larga: {res['longest']}", "metric-c"),
        ])
        ui.show(roulette_chart(dark, res), key="fig_roulette")
        ui.footer_bar(
            f"En {ui.fmt_int(res['n'])} tiradas hubo {ui.fmt_int(res['counts'][MAX_STREAK])} con al menos "
            f"{MAX_STREAK} negros justo antes; en ellas salió rojo con frecuencia "
            f"{res['freqs'][MAX_STREAK]:.4f}, frente a 18/37 = {18 / 37:.4f}."
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
        ("P1", "(I) Una demostración", None),
        ("P2", "(II) El tetraedro de Bernstein", "P2_A"),
        ("P3", "(III) La noche de Montecarlo", "P3_A"),
    ])

    if current == "INTRO":
        render_intro(dark, v)
    elif current == "P1":
        render_problem_1()
    elif current == "P2":
        render_problem_2(dark)
    elif current == "P3":
        render_problem_3(dark, v)

    ui.footer()


main()
