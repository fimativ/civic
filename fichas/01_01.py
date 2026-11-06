#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 1: los orígenes de la probabilidad.

El problema de los puntos de Pascal y Fermat, la lotería de Casanova y el
valor esperado, y las tablas de mortalidad de John Graunt.
"""

from __future__ import annotations

from math import comb

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Orígenes de la probabilidad"
SYMBOL = "½"
PAGE = "01_01"

# =============================================================================
# 1. VALORES INICIALES (dependen del código de sesión)
# =============================================================================

def initial_values():
    meta = ui.dint(10, 6, 10, "meta")
    return {
        "p": ui.dfloat(0.50, 0.30, 0.70, "p"),
        "meta": meta,
        "wins_a": ui.dint(8, 2, meta - 1, "wa"),
        "wins_b": ui.dint(7, 2, meta - 1, "wb"),
        "players": ui.dint(10, 4, 60, "players"),
        "prize": ui.dint(10, 3, 40, "prize"),
        "mortality": ui.dfloat(0.20, 0.08, 0.35, "mortality"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_1"})


# =============================================================================
# 2. CÁLCULOS
# =============================================================================

def prob_a_gana(need_a: int, need_b: int, p: float) -> float:
    if need_a <= 0:
        return 1.0
    if need_b <= 0:
        return 0.0
    max_rounds = need_a + need_b - 1
    return sum(comb(max_rounds, k) * p ** k * (1 - p) ** (max_rounds - k)
               for k in range(need_a, max_rounds + 1))


def survival_data(mortality: float):
    edades_mid = [5, 15, 25, 35, 45, 55, 65, 75, 85]
    edades_plot = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    superv = [1.0]
    for _ in edades_mid:
        superv.append(superv[-1] * (1 - mortality))
    superv = np.array(superv)
    p_muerte = superv[:-1] - superv[1:]
    ev = float(sum(e * pm for e, pm in zip(edades_mid, p_muerte)) + 95 * superv[-1])     # quien llega a 90 cuenta con 95
    return edades_plot, superv, ev


# =============================================================================
# 3. FIGURAS
# =============================================================================

def probability_curve(dark, need_a, need_b, p_cara, p_a, p_b):
    xs = np.linspace(0, 1, 200)
    pa_vals = np.array([prob_a_gana(need_a, need_b, x) for x in xs])
    p = ui.new_figure(dark, height=300, x_axis_label="p (prob. de que A gane cada ronda)",
                      y_axis_label="prob. de ganar", x_range=(0, 1), y_range=(0, 1))
    p.line(xs, pa_vals, line_width=5, color=ui.BLUE_LINE, legend_label="gana A")
    p.line(xs, 1 - pa_vals, line_width=5, color=ui.GREEN_LINE, line_dash="dashed",
           legend_label="gana B")
    p.add_layout(Span(location=0.5, dimension="height", line_color=ui.GREY_LINE,
                      line_dash="dotted", line_width=1))
    p.scatter([p_cara], [p_a], size=16, color=ui.BLUE_LINE, line_color="white", line_width=2)
    p.scatter([p_cara], [p_b], size=16, color=ui.GREEN_LINE, line_color="white", line_width=2)
    return ui.style_legend(p, dark, "center_right")


def expectation_chart(dark, premio, a, ev):
    xs = np.linspace(0.001, 0.5, 300)
    ev_vals = xs * premio
    top = max(float(ev_vals.max()), 2.0)
    p = ui.new_figure(dark, height=300, x_axis_label="probabilidad de ganar p",
                      y_axis_label="esperanza (tharni)", x_range=(0, 0.5), y_range=(0, top))
    p.quad(top=top, bottom=1, left=0, right=0.5, fill_color=ui.GREEN_LINE, fill_alpha=0.12,
           line_color=None)
    p.quad(top=1, bottom=0, left=0, right=0.5, fill_color=ui.RED_LINE, fill_alpha=0.10,
           line_color=None)
    p.line(xs, ev_vals, line_width=5, color=ui.BLUE_LINE)
    p.add_layout(Span(location=1, dimension="width", line_color=ui.GREY_LINE,
                      line_dash="dashed", line_width=1))
    p.scatter([a], [min(ev, top)], size=18, color=ui.BLUE_LINE, line_color="white", line_width=2)
    return p


def survival_chart(dark, edades_plot, superv):
    p = ui.new_figure(dark, height=300, x_axis_label="edad (años)",
                      y_axis_label="supervivencia S(t)", x_range=(0, 90), y_range=(0, 1.05))
    p.varea(x=edades_plot, y1=0, y2=superv, color=ui.BLUE_LINE, alpha=0.10)
    p.line(edades_plot, superv, line_width=5, color=ui.BLUE_LINE)
    p.scatter(edades_plot, superv, size=12, color=ui.BLUE_LINE, line_color="white", line_width=2)
    return p


# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿De dónde surge la probabilidad?</b>")
        ui.content(
            "En Europa, el azar acompañó durante siglos a tabernas y cortes en forma de dados, cartas "
            "y apuestas, pero nadie lo consideraba un objeto digno de estudio: era cosa de la fortuna "
            "o de la providencia. Fue en el Renacimiento, con jugadores tan variopintos como el "
            "algebrista Gerolamo Cardano, quien también trató el problema de resolver las ecuaciones "
            "cúbicas y escribió el primer tratado sobre juegos de azar, cuando se empezó a sospechar que "
            "detrás de los dados había regularidades que podían contarse y, por tanto, calcularse."
        )
        ui.content(
            "Mucho antes, en Asia ya se había convivido de forma sofisticada con la incertidumbre. En "
            "China, el I Ching (traducido, el libro de las mutaciones) organizaba el azar de los "
            "tallos de milenrama en 64 hexagramas, un catálogo sistemático de resultados posibles. En "
            "la India, el épico relato del Mahabharata, en donde los cinco legendarios hermanos "
            "Pándavas libran la gran batalla contra los Kauravas, describe expertos capaces de estimar "
            "cantidades enormes a partir de pequeñas muestras (contar las hojas de un árbol contando "
            "una sola rama), y los matemáticos del subcontinente desarrollaron la combinatoria, la "
            "aritmética de contar casos, siglos antes de que llegara a Europa."
        )
        ui.content(
            "Las ideas matemáticas de fondo son sorprendentemente pocas: enumerar todos los casos "
            "posibles y tratarlos como igual de verosímiles (equiprobabilidad), observar con qué "
            "frecuencia ocurre algo cuando se repite muchas veces (frecuencia relativa) y ponderar cada "
            "resultado por lo que vale (valor esperado). Sobre estos tres pilares, formalizados mucho "
            "después por Laplace y finalmente axiomatizados por Kolmogórov, se levanta toda la teoría "
            "moderna de la probabilidad, que trataremos de desentrañar aquí."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Problema de los puntos (1654)</b><br>"
            "<i>Ayuda a Pascal y Fermat a realizar el reparto de su apuesta</i><br><br>"
            "<b>II. Un fraude en la Lotería (1757)</b><br>"
            "<i>Sé un Casanova y descubre cómo saber si una lotería es injusta mediante el valor "
            "esperado</i><br><br>"
            "<b>III. Estadísticas y estado (1662)</b><br>"
            "<i>Analiza junto con el inglés John Graunt los boletines parroquiales de Londres</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica el valor de <u>la probabilidad p</u>")
        p_cara = st.slider("Probabilidad p (que A gane cada ronda)", 0.0, 1.0, v["p"], 0.01,
                           key=ui.wkey(PAGE, "p"), label_visibility="collapsed")
        c1, c2, c3 = st.columns(3)
        wins_a = c1.number_input("Victorias A", 0, 9, v["wins_a"], key=ui.wkey(PAGE, "wa"))
        wins_b = c2.number_input("Victorias B", 0, 9, v["wins_b"], key=ui.wkey(PAGE, "wb"))
        meta = c3.number_input("Meta", 2, 10, v["meta"], key=ui.wkey(PAGE, "meta"))

        ui.planteamiento()
        ui.statement(
            "<b>El nacimiento de la probabilidad (1654)</b><br><br>"
            "Podemos encontrar los primeros pasos de la discusión entre los matemáticos franceses "
            "Blaise Pascal y Pierre de Fermat, quienes trataban de cuantificar numéricamente eventos "
            "complejos. En particular, se interesaron en varios problemas sobre apuestas y desafíos."
        )

        if ui.accordion_step("P1_1", "(A) El problema de los puntos"):
            ui.content(
                "La formulación clásica del problema habla de dos caballeros A y B, quienes compiten "
                "apostando un tharni (la unidad monetaria que utilizaremos en este entorno, y que "
                "permite adquirir un googol de épsilones) hasta que uno de ellos obtenga "
                f"{v['meta']} victorias. En cada ronda A puede ganar con una probabilidad p. Comienzan "
                f"a jugar y, cuando el jugador A lleva {v['wins_a']} victorias y el jugador B por su "
                f"parte otras {v['wins_b']}, el rey les manda a palacio. La pregunta es, ¿cómo deben "
                "repartirse justamente el premio de su apuesta?"
            )

        if ui.accordion_step("P1_2", "(B) La discusión probabilística"):
            ui.content(
                "Fermat imaginó que el juego continuaba de todas formas durante un número fijo de rondas "
                "(una menos que el total de victorias que faltaban entre los dos jugadores), y enumeró "
                "todos los escenarios posibles. Con p = 1/2 todos son equiprobables y basta contar; con p "
                "cualquiera hay que pesar cada escenario, como en (C). Pascal llegó al mismo resultado por "
                "otro camino, razonando hacia atrás desde el final de la partida. Este fue el primer uso "
                "riguroso de la probabilidad, y se vería luego reflejado en la definición (clásica) de "
                "Laplace.<br><br>"
                "<b>El método (algoritmo) de Fermat, con p = 1/2:</b><br>"
                "1. Enumera todos los escenarios equiprobables hasta que uno de los dos jugadores gane "
                "(casos totales)<br>"
                "2. Cuenta cuántos casos de los anteriores favorecen a A (favorables)<br>"
                "3. El valor asociado de la probabilidad de que A gane será: casos favorables / casos "
                "totales<br><br>"
                "Observa cómo varían estos valores dependiendo de cuál es el valor de p (la probabilidad "
                "de que A gane). ¿Observas alguna relación entre la probabilidad de que gane A y la de "
                "que gane B?"
            )
            ui.spoiler("Ambas probabilidades suman uno (son eventos complementarios: o gana A, o gana B).")

        if ui.accordion_step("P1_3", "(C) La fórmula general"):
            ui.content(
                "En general, si para ganar se requieren n partidas, si A necesita a victorias para "
                "llegar a la meta y B necesita b victorias, el juego termina en un máximo de (a+b−1) "
                "rondas. El conjunto de todos los resultados posibles (espacio muestral, &Omega;) tiene "
                "2<sup>a+b−1</sup> resultados. A gana si, en esas rondas, obtiene al menos a victorias."
            )
            ui.spoiler(
                "<div class='formula-box'>"
                "&#8473;(A gana) = &sum;<sub>k=a</sub><sup>a+b−1</sup> "
                "( <sup>a+b−1</sup>&frasl;<sub>k</sub> ) "
                "p<sup>k</sup> (1−p)<sup>a+b−1−k</sup>"
                "</div>"
                "Prueba a sustituir los valores del problema para comprobar que obtienes los mismos "
                "valores que en el panel de la derecha."
            )

    with col_right:
        ui.right_panel()
        need_a = meta - wins_a
        need_b = meta - wins_b
        p_a = prob_a_gana(need_a, need_b, p_cara)
        p_b = 1 - p_a
        ui.metrics([
            (f"&#8473;(A gana) = {p_a:.4f}", "metric-a"),
            (f"&#8473;(B gana) = {p_b:.4f}", "metric-b"),
        ])
        ui.show(probability_curve(dark, need_a, need_b, p_cara, p_a, p_b), key="fig_points")
        ui.footer_bar(
            f"Con p = {p_cara:.2f}, A necesita {max(need_a, 0)} victorias, B necesita "
            f"{max(need_b, 0)}. Reparto de tharni: {p_a * 100:.1f}% para A, {p_b * 100:.1f}% para B."
        )


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica el <u>valor del premio Q</u>, y el <u>número de jugadores</u> 1/p")
        n_jugadores = st.slider("Número de jugadores (1/p)", 2, 100, v["players"], 1,
                                key=ui.wkey(PAGE, "players"))
        premio = st.slider("Premio Q (tharni)", 1, 50, v["prize"], 1, key=ui.wkey(PAGE, "prize"))

        ui.planteamiento()
        ui.statement(
            "El veneciano Giacomo Casanova (sí, este aventurero tuvo una faceta matemática, así como "
            "literaria, diplomática, o de libre pensador dialogando con Voltaire, Rousseau o Federico II) "
            "promovió en 1757, junto a los hermanos Calzabigi, la lotería de la École militaire de París, "
            "con la que el Estado francés llenaba sus arcas a costa de jugadores de toda condición."
        )

        if ui.accordion_step("P2_1", "(A) Un nuevo concepto: valor esperado"):
            ui.content(
                "El mero concepto de equiprobable del problema anterior no es suficiente para que un "
                "juego sea justo (es decir, que ninguno de sus participantes tenga ventaja sobre otro). "
                "Lo que determina si un juego nos favorece, nos perjudica o es justo es su valor esperado o "
                "esperanza, que se corresponde con el resultado que se obtendría en promedio, tras jugar "
                "un número elevado de partidas (cuántas, lo veremos en un tema más avanzado)."
            )

        if ui.accordion_step("P2_2", "(B) La tabla de decisión"):
            ui.content(
                "Si en un juego de azar como la lotería compras un billete de 1 tharni, ganando un "
                "premio Q con probabilidad p, entonces ¿cuándo te interesaría jugar al juego?"
            )
            ui.spoiler(
                "Para calcular la esperanza se aglutinan todos los casos posibles junto con su "
                "probabilidad correspondiente:"
                "<div class='formula-box'>"
                "&#120124;[lotería] = P[ganar]&middot;Q + P[perder]&middot;0 = p&middot;Q"
                "</div>"
                "Y entonces:<br>"
                "Si &#120124;[lotería] &gt; 1 tharni: el juego es favorable al jugador.<br>"
                "Si &#120124;[lotería] = 1 tharni: el juego es matemáticamente justo.<br>"
                "Si &#120124;[lotería] &lt; 1 tharni: el juego es favorable a «la casa»."
            )

        if ui.accordion_step("P2_3", "(C) En la mesa y en el juego se conoce al caballero"):
            ui.content(
                "Un jugador astuto solo compraría en loterías en las que pQ &gt; 1 (y recuerda que p, la "
                "probabilidad, es sencillamente el inverso del número de billetes). Por ejemplo, el "
                "Sorteo de Navidad de la Lotería Nacional española (que se celebra desde 1812 y cantan los "
                "niños de San Ildefonso) tiene 100\u202f000 números, cada uno con varias series y cada "
                "billete con diez fracciones (cada fracción es un décimo)... ¿cuánto tendría que ser el "
                "primer premio (asumiendo que no hubiera más) para "
                "que se tratara de un juego justo, suponiendo que cada décimo cuesta 20 tharni?"
            )
            ui.spoiler(
                "Resuélvelo numéricamente: en un juego justo p&middot;Q = precio del billete. La "
                "probabilidad de que tu número sea premiado es p = 1/100\u202f000, y cada décimo cuesta 20 "
                f"tharni, luego el premio justo por décimo sería Q = 20 &middot; 100\u202f000 = "
                f"{ui.fmt_int(20 * 100_000)} tharni."
            )

    with col_right:
        ui.right_panel()
        a = 1.0 / n_jugadores
        ev = a * premio
        if abs(ev - 1) < 0.001:
            resultado, clase = "Juego justo", "result-yes"
        elif ev > 1:
            resultado, clase = "Favorable al jugador", "result-gold"
        else:
            resultado, clase = "Favorable a la banca", "result-no"
        ui.metrics([
            (f"&#120124;[X] = {ev:.4f} tharni", ""),
            (f"Resultado: {resultado}", clase),
        ])
        ui.show(expectation_chart(dark, premio, a, ev), key="fig_lottery")
        ui.footer_bar(f"Con p = {a:.3f} y el premio = {premio} tharni: &#120124;[X] = {ev:.4f} tharni")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica la <u>tasa de mortalidad M</u> de cada franja")
        mortality = st.slider("M: tasa de mortalidad por franja", 0.01, 0.60, v["mortality"], 0.01,
                              format="%.2f", key=ui.wkey(PAGE, "mortality"),
                              label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "En 1662, mientras Londres convivía con la peste, un mercero llamado John Graunt tuvo una "
            "idea revolucionaria: en lugar de especular sobre la muerte, decidió contarla. Con los "
            "boletines parroquiales de la ciudad construyó la primera tabla de mortalidad de la "
            "historia, fundando de paso la estadística demográfica."
        )

        if ui.accordion_step("P3_1", "(A) Los boletines parroquiales de Londres"):
            ui.content(
                "Cada semana, las parroquias londinenses publicaban los Bills of Mortality: listados de "
                "bautizos y entierros con sus causas (peste, viruela, «dientes», e incluso "
                "«planeta»: si fuiste maldecido, tuviste una mala influencia planetaria, o una "
                "afección paranormal te afectó demasiado). Nadie los usaba más que para saber si "
                "convenía huir de la ciudad. Graunt los recopiló durante décadas y descubrió "
                "regularidades asombrosas: nacen ligeramente más niños que niñas, la mortalidad urbana "
                "supera a la rural, y ciertas causas de muerte mantienen proporciones estables año tras "
                "año. ¿Qué tiene esto que ver con la probabilidad?"
            )
            ui.spoiler(
                "Que los datos masivos convierten el azar individual (nadie sabe cuándo morirá) en "
                "regularidad colectiva: las proporciones estables son, en el fondo, probabilidades."
            )

        if ui.accordion_step("P3_2", "(B) La definición frecuentista"):
            ui.content(
                "Graunt no usó nunca la palabra probabilidad, pero su método es el germen de la segunda "
                "gran definición de la misma:<br><br>"
                "1. Cuenta los casos observados en los registros (n<sub>A</sub> de un total de n)<br>"
                "2. Calcula la proporción n<sub>A</sub>/n<br>"
                "3. Asume que las proporciones pasadas predicen el futuro<br><br>"
                "¿Cómo se formaliza esta idea matemáticamente?"
            )
            ui.spoiler(
                "Es la definición frecuentista de la probabilidad:"
                "<div class='formula-box'>&#8473;(A) = lim<sub>n&rarr;&infin;</sub> n<sub>A</sub>/n</div>"
                "La probabilidad de un suceso es el límite de su frecuencia relativa cuando el número "
                "de observaciones crece indefinidamente."
            )

        if ui.accordion_step("P3_3", "(C) La curva de supervivencia"):
            ui.content(
                "La curva de supervivencia S(t) indica qué fracción de la población inicial sigue viva a "
                "la edad t. Si la tasa de mortalidad en cada franja de edad es M (igual para todas, como "
                "supuso Graunt en su tabla), la supervivencia decrece en cada etapa: "
                "S(t<sub>k+1</sub>) = S(t<sub>k</sub>)&middot;(1−M).<br><br>"
                "¿Cómo se calcula entonces la esperanza de vida?"
            )
            ui.spoiler(
                "La esperanza de vida es el promedio de las edades de muerte ponderado por su "
                "probabilidad:"
                "<div class='formula-box'>&#120124;[edad] = &sum;<sub>k</sub> edad<sub>k</sub> "
                "&middot; &#8473;(morir en la franja k)</div>"
                "Exactamente la misma idea de valor esperado que usó Casanova con la lotería, ahora "
                "aplicada a la vida humana. Sobre esta base nacieron los seguros de vida modernos."
            )

    with col_right:
        ui.right_panel()
        edades_plot, superv, ev = survival_data(mortality)
        ui.metrics([
            (f"<b>Esperanza de vida:</b><br>{ev:.1f} años", ""),
            (f"<b>Superv. a los 40:</b><br>{superv[4] * 100:.1f}%", ""),
            (f"<b>Superv. a los 70:</b><br>{superv[7] * 100:.1f}%", ""),
        ])
        ui.show(survival_chart(dark, edades_plot, superv), key="fig_graunt")
        ui.footer_bar(f"Con tasa de mortalidad M = {mortality:.2f} por franja: esperanza de vida = "
                      f"{ev:.1f} años")


# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Otra apuesta de Pascal", "P1_1"),
        ("P2", "(II) Una lotería justa", "P2_1"),
        ("P3", "(III) Con estadística y a lo loco", "P3_1"),
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
