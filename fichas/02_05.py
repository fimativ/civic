#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 5: redes y fiabilidad.

Relés en serie y en paralelo (independencia de los complementarios), el
puente de Moore y Shannon (probabilidad total sobre el relé central) y el
planeador de Gimli (una causa común rompe la independencia).
"""

from __future__ import annotations

from math import ceil, log

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "Redes y fiabilidad"
SYMBOL = "R(p)"
PAGE = "02_05"

F_OPTIONS = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01]
Q_OPTIONS = [0.0, 0.0000001, 0.000001, 0.00001, 0.0001, 0.001]


def initial_values():
    return {
        "p_relay": ui.dchoice(0.90, [0.70, 0.75, 0.80, 0.85, 0.90, 0.95], "p_relay"),
        "blocks": ui.dint(3, 2, 4, "blocks"),
        "parallel": ui.dint(2, 2, 4, "parallel"),
        "p_bridge": ui.dchoice(0.60, [0.55, 0.60, 0.65, 0.70, 0.75], "p_bridge"),
        "f": ui.dchoice(0.001, F_OPTIONS[1:6], "f"),
        "q": ui.dchoice(0.00001, Q_OPTIONS[2:5], "q"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "bridge_level": 1})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def series_parallel(p, blocks: int, parallel: int):
    """m bloques en serie, cada uno con r relés en paralelo."""
    return (1 - (1 - p) ** parallel) ** blocks


def bridge(p):
    """Puente de cinco relés: probabilidad total sobre el relé central."""
    closed = (1 - (1 - p) ** 2) ** 2
    opened = 1 - (1 - p ** 2) ** 2
    return p * closed + (1 - p) * opened


def bridge_level(p, level: int):
    for _ in range(level):
        p = bridge(p)
    return p


def engines(f: float, q: float):
    p_one = q + (1 - q) * f
    p_both = q + (1 - q) * f ** 2
    return p_one, p_both


# =============================================================================
# 2. FIGURAS Y ESQUEMAS
# =============================================================================

def network_svg(dark, blocks: int, parallel: int) -> str:
    fg = "#e6e6e6" if dark else "#333333"
    width = 70 + blocks * 90
    height = 30 + parallel * 34
    mid = height / 2
    parts = [f'<line x1="10" y1="{mid}" x2="40" y2="{mid}" stroke="{fg}" stroke-width="2"/>',
             f'<line x1="{width - 40}" y1="{mid}" x2="{width - 10}" y2="{mid}" stroke="{fg}" stroke-width="2"/>']
    for b in range(blocks):
        x0 = 40 + b * 90
        top, bottom = 15 + 17, 15 + 17 + (parallel - 1) * 34
        parts.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{bottom}" stroke="{fg}" stroke-width="2"/>')
        parts.append(f'<line x1="{x0 + 90}" y1="{top}" x2="{x0 + 90}" y2="{bottom}" stroke="{fg}" stroke-width="2"/>')
        for r in range(parallel):
            y = 15 + 17 + r * 34
            parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + 90}" y2="{y}" stroke="{fg}" stroke-width="2"/>')
            parts.append(f'<rect x="{x0 + 27}" y="{y - 10}" width="36" height="20" rx="4" fill="{ui.BLUE_LINE}"/>')
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def bridge_svg(dark) -> str:
    fg = "#e6e6e6" if dark else "#333333"
    s, t, x, y = (30, 90), (370, 90), (200, 30), (200, 150)

    def relay(p1, p2, label, colour):
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        return (f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="{fg}" stroke-width="2.5"/>'
                f'<rect x="{mx - 18}" y="{my - 12}" width="36" height="24" rx="5" fill="{colour}"/>'
                f'<text x="{mx}" y="{my + 6}" text-anchor="middle" font-size="16" fill="#ffffff">{label}</text>')

    nodes = "".join(f'<circle cx="{px}" cy="{py}" r="7" fill="{fg}"/>' for px, py in (s, t, x, y))
    labels = (f'<text x="{s[0] - 4}" y="{s[1] + 28}" font-size="16" fill="{fg}">s</text>'
              f'<text x="{t[0] - 4}" y="{t[1] + 28}" font-size="16" fill="{fg}">t</text>')
    body = (relay(s, x, "a", ui.BLUE_LINE) + relay(x, t, "b", ui.BLUE_LINE) + relay(s, y, "c", ui.BLUE_LINE)
            + relay(y, t, "d", ui.BLUE_LINE) + relay(x, y, "e", ui.UBU_RED))
    return f'<svg viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg">{body}{nodes}{labels}</svg>'


def reliability_chart(dark, p, blocks: int, parallel: int):
    ps = np.linspace(0, 1, 201)
    total = blocks * parallel
    fig = ui.new_figure(dark, height=300, x_axis_label="fiabilidad de cada relé p",
                        y_axis_label="fiabilidad de la red", x_range=(0, 1), y_range=(0, 1.02))
    fig.line(ps, ps ** total, line_width=3, color=ui.RED_LINE, line_dash="dashed",
             legend_label=f"{total} en serie")
    fig.line(ps, 1 - (1 - ps) ** total, line_width=3, color=ui.GREEN_LINE, line_dash="dashed",
             legend_label=f"{total} en paralelo")
    fig.line(ps, series_parallel(ps, blocks, parallel), line_width=5, color=ui.BLUE_LINE,
             legend_label=f"{blocks} bloques de {parallel}")
    fig.scatter([p], [series_parallel(p, blocks, parallel)], size=16, color=ui.BLUE_LINE,
                line_color="white", line_width=2)
    return ui.style_legend(fig, dark, "top_left")


def bridge_chart(dark, p, level: int):
    ps = np.linspace(0, 1, 201)
    fig = ui.new_figure(dark, height=320, x_axis_label="fiabilidad de cada relé p",
                        y_axis_label="fiabilidad de la red", x_range=(0, 1), y_range=(0, 1.02))
    fig.line(ps, ps, line_width=2, color=ui.GREY_LINE, line_dash="dotted", legend_label="un solo relé")
    colours = [ui.BLUE_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE]
    for lv in range(1, 4):
        fig.line(ps, bridge_level(ps, lv), line_width=5 if lv == level else 2.5, color=colours[lv - 1],
                 alpha=1.0 if lv == level else 0.5, legend_label=f"nivel {lv} ({5 ** lv} relés)")
    fig.scatter([p], [bridge_level(p, level)], size=16, color=colours[level - 1], line_color="white",
                line_width=2)
    return ui.style_legend(fig, dark, "top_left")


def engines_chart(dark, f: float, q: float):
    p_one, p_both = engines(f, q)
    labels = ["si fueran independientes", "con causa común", "producto P(A₁)P(A₂)"]
    values = [f ** 2, p_both, p_one ** 2]
    fig = ui.new_figure(dark, height=320, x_range=labels, y_axis_type="log",
                        y_range=(1e-11, 1e-1), y_axis_label="probabilidad (escala logarítmica)")
    fig.vbar(x=labels, bottom=1e-12, top=values, width=0.6,
             fill_color=[ui.GREEN_LINE, ui.RED_LINE, ui.ORANGE_LINE], line_color=None)
    fig.xgrid.grid_line_color = None
    fig.xaxis.major_label_text_font_size = "13px"
    return fig


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se construye algo fiable con piezas que fallan?</b>")
        ui.content(
            "Un avión, una red eléctrica o un circuito están hechos de componentes que pueden fallar. "
            "Si los fallos de unos no influyen en los de otros, la independencia permite calcular la "
            "fiabilidad del conjunto a partir de la de cada pieza. Para n sucesos mutuamente "
            "independientes, la probabilidad de que ocurran todos es el producto.<br><br>"
            "<i>Trata de escribir la probabilidad de que ocurra al menos uno, pasando al "
            "complementario.</i>"
        )
        ui.formula_hidden(
            "&#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) = 1 &minus; "
            "&#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>) = 1 &minus; "
            "&prod;<sub>i=1</sub><sup>n</sup> (1 &minus; &#8473;(A<sub>i</sub>))",
            hint="Pulsa para revelar la fórmula",
        )
        ui.content(
            "La cuenta usa dos ingredientes de los temas anteriores: las leyes de De Morgan, que "
            "convierten <i>al menos uno</i> en <i>ninguno falla</i>, y el hecho de que los "
            "complementarios de sucesos independientes siguen siendo independientes. Toda la ficha "
            "descansa sobre la hipótesis de independencia, y el último problema muestra qué pasa cuando "
            "falla."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los relés de Shannon (1938)</b><br>"
            "<i>Descubre con Claude Shannon que un circuito de relés es un diagrama de Venn con "
            "cables.</i><br><br>"
            "<b>II. El puente de Moore y Shannon (1956)</b><br>"
            "<i>Cinco relés, una pregunta a la probabilidad total y una curva en S que convierte piezas "
            "mediocres en circuitos casi perfectos.</i><br><br>"
            "<b>III. El planeador de Gimli (1983)</b><br>"
            "<i>Dos motores no son el doble de seguros si comparten el mismo depósito.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>fiabilidad p</u> y la <u>forma de la red</u>")
        p = st.slider("Fiabilidad de cada relé p", 0.50, 0.99, v["p_relay"], 0.01, key=ui.wkey(PAGE, "p_relay"))
        c1, c2 = st.columns(2)
        blocks = c1.slider("Bloques en serie m", 1, 6, v["blocks"], 1, key=ui.wkey(PAGE, "blocks"))
        parallel = c2.slider("Relés en paralelo por bloque r", 1, 6, v["parallel"], 1,
                             key=ui.wkey(PAGE, "parallel"))

        ui.planteamiento()
        ui.statement(
            "<b>Los relés de Shannon (1938)</b><br><br>"
            "Con veintiún años, Claude Shannon (1916-2001) escribió en el MIT una tesis de máster (publicada en 1938) que "
            "mostraba que los circuitos de relés de las centralitas telefónicas obedecen al álgebra de "
            "Boole: dos relés en serie dejan pasar la corriente si ambos están cerrados (intersección); "
            "dos en paralelo, si lo está alguno (unión). Supongamos que cada relé funciona con "
            f"probabilidad p = {v['p_relay']:.2f}, independientemente de los demás, y montamos una red de "
            f"{v['blocks']} bloques en serie, cada uno con {v['parallel']} relés en paralelo."
        )

        if ui.accordion_step("P1_A", "(A) En serie"):
            ui.content(
                "Con n relés en serie, la red funciona si funcionan todos. ¿Qué probabilidad tiene? ¿Qué "
                "le pasa al crecer n?"
            )
            ui.spoiler(
                "Por la independencia mutua, la probabilidad de la intersección es el producto:"
                "<div class='formula-box'>&#8473;(serie) = p<sup>n</sup></div>"
                "Decrece exponencialmente con n: una cadena de cien eslabones muy fiables (p = 0.99) solo "
                "funciona en torno a un tercio de las veces."
            )

        if ui.accordion_step("P1_B", "(B) En paralelo"):
            ui.content(
                "Con n relés en paralelo, la red funciona si funciona al menos uno. Pasa al complementario "
                "y justifica cada paso."
            )
            ui.spoiler(
                "La red falla si fallan todos. Por las leyes de De Morgan y la independencia de los "
                "complementarios:"
                "<div class='formula-box'>&#8473;(paralelo) = 1 &minus; (1 &minus; p)<sup>n</sup></div>"
                "Para m bloques de r relés en paralelo puestos en serie basta combinar las dos fórmulas: "
                "1 &minus; (1 &minus; p)<sup>r</sup> por bloque, elevado a m."
            )

        if ui.accordion_step("P1_C", "(C) Cuánta redundancia"):
            ui.content(
                "¿Cuántos relés en paralelo hacen falta para que un bloque funcione con probabilidad al "
                "menos 0.999? ¿Por qué no se ponen siempre muchísimos relés en paralelo?"
            )
            ui.spoiler(
                "Basta que (1 &minus; p)<sup>r</sup> &le; 0.001, es decir, r &ge; ln(0.001)&frasl;ln(1 &minus; p). "
                "Pero un relé también puede fallar quedándose pegado, cerrado cuando debería abrirse: "
                "con ese fallo el paralelo es el peor diseño y la serie el mejor. Proteger contra los dos "
                "fallos a la vez exige redes más ingeniosas, como la del problema siguiente."
            )

    with col_right:
        ui.right_panel()
        rel = float(series_parallel(p, blocks, parallel))
        need = ceil(log(0.001) / log(1 - p))
        ui.metrics([
            (f"Fiabilidad de la red: {rel:.4f}", "metric-a"),
            (f"Relés en paralelo para 0.999: {need}", "metric-c"),
        ])
        ui.svg(network_svg(dark, blocks, parallel))
        ui.show(reliability_chart(dark, p, blocks, parallel), key="fig_relays")
        ui.footer_bar(f"Con los mismos {blocks * parallel} relés, todos en serie darían {p ** (blocks * parallel):.4f} "
                      f"y todos en paralelo {1 - (1 - p) ** (blocks * parallel):.6f}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>fiabilidad p</u> y el <u>nivel de anidamiento</u>")
        p = st.slider("Fiabilidad de cada relé p", 0.30, 0.95, v["p_bridge"], 0.01, key=ui.wkey(PAGE, "p_bridge"))
        level = st.slider("Nivel (cada relé se sustituye por un puente)", 1, 3, 1, 1, key="bridge_level")

        ui.planteamiento()
        ui.statement(
            "<b>El puente de Moore y Shannon (1956)</b><br><br>"
            "Edward Moore y Claude Shannon publicaron en 1956 un artículo con un título que es todo un "
            "programa: <i>circuitos fiables con relés menos fiables</i>. Una de las redes que estudiaron "
            "es el puente de la derecha: cinco relés, cada uno cerrado con probabilidad p y de forma "
            "independiente. La corriente pasa de s a t si hay algún camino de relés cerrados. El relé "
            "central e es el que complica la cuenta: no está ni en serie ni en paralelo con nadie."
        )

        if ui.accordion_step("P2_A", "(A) Preguntar al relé central"):
            ui.content(
                "Los sucesos <i>e cerrado</i> y <i>e abierto</i> forman una partición. ¿En qué se "
                "convierte el puente en cada caso? Aplica el teorema de la probabilidad total."
            )
            ui.spoiler(
                "Con e cerrado, los nodos de arriba y abajo se funden: quedan (a &#8741; c) en serie con "
                "(b &#8741; d). Con e abierto, quedan dos caminos en paralelo, a&ndash;b y c&ndash;d:"
                "<div class='formula-box'>R(p) = p&middot;[1 &minus; (1 &minus; p)<sup>2</sup>]<sup>2</sup> + "
                "(1 &minus; p)&middot;[1 &minus; (1 &minus; p<sup>2</sup>)<sup>2</sup>]</div>"
                "Desarrollando, R(p) = 2p<sup>2</sup> + 2p<sup>3</sup> &minus; 5p<sup>4</sup> + 2p<sup>5</sup>."
            )

        if ui.accordion_step("P2_B", "(B) La curva en S"):
            ui.content(
                "Compara en la figura la curva del puente con la diagonal (un solo relé). ¿Dónde se "
                "cortan? ¿Cuándo es el puente mejor que un relé suelto, y cuándo peor?"
            )
            ui.spoiler(
                "Se cortan en p = 1/2 (además de en 0 y 1): el puente es <i>autodual</i>, R(1 &minus; p) = "
                "1 &minus; R(p). Para p &gt; 1/2 el puente es más fiable que un relé, y para p &lt; 1/2 "
                "menos. Si fallar cerrado y fallar abierto se modelan como los dos lados de p, la red "
                "empuja la probabilidad de acertar hacia los extremos: es un amplificador."
            )

        if ui.accordion_step("P2_C", "(C) Circuitos fiables con relés mediocres"):
            ui.content(
                "Sube el nivel: cada relé del puente se sustituye por otro puente, y así sucesivamente. "
                "¿Qué le ocurre a la fiabilidad con relés de p = 0.6? ¿Cuál es el precio?"
            )
            ui.spoiler(
                "Cada nivel aplica otra vez R, y como R(p) &gt; p por encima de un medio, la fiabilidad "
                "se acerca a 1 a gran velocidad: es la idea de Moore y Shannon. El precio es el número de "
                "relés, que se multiplica por cinco en cada nivel: 5, 25, 125&hellip; La redundancia "
                "compra fiabilidad, y la independencia de los fallos es lo que permite calcularla."
            )

    with col_right:
        ui.right_panel()
        rel = float(bridge_level(p, level))
        ui.metrics([
            (f"R<sub>{level}</sub>(p) = {rel:.4f}", "metric-a"),
            (f"Un solo relé: {p:.4f}", "metric-c"),
        ])
        ui.svg(bridge_svg(dark))
        ui.show(bridge_chart(dark, p, level), key="fig_bridge")
        ui.footer_bar(f"Con relés de fiabilidad {p:.2f} y {5 ** level} relés en total, la red funciona con "
                      f"probabilidad {rel:.4f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>probabilidad de fallo f</u> de cada motor y la de una <u>causa común q</u>")
        f = st.select_slider("Fallo de cada motor por vuelo, f", options=F_OPTIONS, value=v["f"],
                             key=ui.wkey(PAGE, "f"))
        q = st.select_slider("Fallo de causa común por vuelo, q", options=Q_OPTIONS, value=v["q"],
                             key=ui.wkey(PAGE, "q"))

        ui.planteamiento()
        ui.statement(
            "<b>El planeador de Gimli (1983)</b><br><br>"
            "El 23 de julio de 1983 un Boeing 767 de Air Canada se quedó sin combustible a unos 12 500 "
            "metros de altura, sobre el noroeste de Ontario: al calcular la carga, en pleno cambio al sistema métrico, se "
            "habían confundido libras con kilogramos. Los dos motores se pararon a la vez. El comandante, "
            "piloto de planeadores en sus ratos libres, llevó el avión planeando hasta una antigua base "
            "aérea en Gimli, y nadie murió. Los aviones bimotores se certifican suponiendo que un motor "
            "puede fallar; lo que no se espera es que fallen los dos."
        )

        if ui.accordion_step("P3_A", "(A) Si los motores fueran independientes"):
            ui.content(
                "Sea A<sub>i</sub> el suceso <i>el motor i falla en un vuelo</i>, con probabilidad f. Si "
                "A<sub>1</sub> y A<sub>2</sub> fueran independientes, ¿con qué probabilidad fallarían los "
                "dos?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(A<sub>1</sub> &cap; A<sub>2</sub>) = f<sup>2</sup></div>"
                "Con f del orden de una milésima, f<sup>2</sup> es una millonésima: es el argumento que hace "
                "tan atractiva la redundancia."
            )

        if ui.accordion_step("P3_B", "(B) Una causa común"):
            ui.content(
                "Supón ahora que, con probabilidad q, ocurre algo que para los dos motores a la vez (sin "
                "combustible, una nube de ceniza volcánica, una bandada de aves); si no ocurre, cada "
                "motor falla por su cuenta con probabilidad f. Calcula &#8473;(A<sub>1</sub> &cap; "
                "A<sub>2</sub>) condicionando a la causa común."
            )
            ui.spoiler(
                "Con C = <i>ocurre la causa común</i>, el teorema de la probabilidad total sobre "
                "{C, C<sup>c</sup>} da"
                "<div class='formula-box'>&#8473;(A<sub>1</sub> &cap; A<sub>2</sub>) = 1&middot;q + "
                "f<sup>2</sup>&middot;(1 &minus; q)</div>"
                "Aunque q sea pequeñísima, en cuanto supera a f<sup>2</sup> domina la suma: la fiabilidad "
                "de la redundancia queda limitada por la causa común, no por los motores."
            )

        if ui.accordion_step("P3_C", "(C) ¿Independientes o no?"):
            ui.content(
                "Calcula &#8473;(A<sub>1</sub>) con el mismo modelo y compara &#8473;(A<sub>1</sub> &cap; "
                "A<sub>2</sub>) con &#8473;(A<sub>1</sub>)&#8473;(A<sub>2</sub>). Dentro de C y dentro de "
                "C<sup>c</sup>, ¿son independientes los fallos?"
            )
            ui.spoiler(
                "&#8473;(A<sub>1</sub>) = q + (1 &minus; q)f, y su cuadrado es menor que "
                "q + (1 &minus; q)f<sup>2</sup> siempre que 0 &lt; q &lt; 1 y f &lt; 1: los fallos no son "
                "independientes. Sin embargo, sabiendo que ha ocurrido C fallan los dos seguro, y sabiendo "
                "que no ha ocurrido fallan cada uno por su cuenta: son <b>condicionalmente "
                "independientes</b> dada la causa común. Mezclar dos situaciones con independencia "
                "produce dependencia."
            )

    with col_right:
        ui.right_panel()
        p_one, p_both = engines(f, q)
        ui.metrics([
            (f"&#8473;(A<sub>1</sub> &cap; A<sub>2</sub>) = {ui.fmt_sci(p_both)}", "metric-a"),
            (f"Si fueran independientes: {ui.fmt_sci(f ** 2)}", "metric-b"),
        ])
        ui.show(engines_chart(dark, f, q), key="fig_engines")
        ratio = p_both / f ** 2
        ui.footer_bar(f"La causa común multiplica por {ratio:,.1f} la probabilidad de perder los dos motores. "
                      f"El producto &#8473;(A<sub>1</sub>)&#8473;(A<sub>2</sub>) = {ui.fmt_sci(p_one ** 2)} no "
                      "coincide con la intersección: no hay independencia.".replace(",", " "))


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los relés de Shannon", "P1_A"),
        ("P2", "(II) El puente de Moore y Shannon", "P2_A"),
        ("P3", "(III) El planeador de Gimli", "P3_A"),
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
