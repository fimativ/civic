#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 4: el arte de contar.

Calculadora combinatoria (orden, repetición, todos los elementos), tres
problemas que se resuelven mirándolos desde el otro lado al estilo de Pólya,
la paradoja del cumpleaños y dos monedas cargadas.
"""

from __future__ import annotations

from math import comb, factorial, perm

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "El arte de contar"
SYMBOL = "n!"
PAGE = "01_04"

COMBI_INFO = {
    "V":  ("Variaciones sin repetición", "V<sub>m</sub><sup>n</sup> = m! / (m&minus;n)!",
           "Medallas de oro, plata y bronce entre 10 atletas."),
    "VR": ("Variaciones con repetición", "VR<sub>m</sub><sup>n</sup> = m<sup>n</sup>",
           "Un candado de 3 ruedas del 0 al 9."),
    "P":  ("Permutaciones sin repetición", "P<sub>m</sub> = m!",
           "El orden de llegada de m corredores a meta."),
    "PR": ("Permutaciones con repetición",
           "PR = m! / (n<sub>1</sub>! &middot; n<sub>2</sub>! &middot; &hellip;)",
           "Ordenar las letras de BANANA: 6!/(3!·2!·1!) = 60."),
    "C":  ("Combinaciones sin repetición", "C<sub>m</sub><sup>n</sup> = ( m sobre n )",
           "Elegir un comité de n personas entre m."),
    "CR": ("Combinaciones con repetición", "CR<sub>m</sub><sup>n</sup> = ( m+n&minus;1 sobre n )",
           "n bolas de helado eligiendo entre m sabores."),
    "DEG": ("Caso degenerado", "1",
            "Sin orden y usando todos los elementos, solo hay una agrupación: el propio conjunto."),
}


def initial_values():
    p1 = ui.dfloat(0.40, 0.20, 0.60, "p1", 2)
    p2 = ui.dfloat(0.70, 0.40, 0.85, "p2", 2)
    return {
        "white": ui.dint(5, 1, 10, "white"),
        "people": ui.dint(23, 10, 60, "people"),
        "p1": round(p1 * 20) / 20,
        "p2": round(p2 * 20) / 20,
        "throws": ui.dchoice(100, [50, 60, 80, 100, 120, 150], "throws"),
        "threshold": ui.dchoice(60, [55, 60, 65, 70, 75, 80], "threshold"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "U_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def combi_kind(orden: bool, repeticion: bool, todos: bool) -> str:
    if orden and todos:
        return "PR" if repeticion else "P"
    if orden:
        return "VR" if repeticion else "V"
    if not todos:
        return "CR" if repeticion else "C"
    return "DEG"


def combi_value(kind: str, m: int, n: int):
    if kind == "V":
        return perm(m, n)
    if kind == "VR":
        return m ** n
    if kind == "P":
        return factorial(m)
    if kind == "C":
        return comb(m, n)
    if kind == "CR":
        return comb(m + n - 1, n)
    if kind == "DEG":
        return 1
    return None   # PR: depende de las multiplicidades


def probability_all_different(n: int) -> float:
    if n > 365:
        return 0.0
    p = 1.0
    for i in range(n):
        p *= (365 - i) / 365
    return p


# =============================================================================
# 2. FIGURAS
# =============================================================================

def draw_urn(white: int, black: int, dark) -> str:
    """Urna en SVG con las bolas apiladas por filas desde el fondo."""
    stroke = ui.UBU_RED
    fg = "#e6e6e6" if dark else "#333333"
    w_fill, w_stroke = "#ffffff", "#333333"
    b_fill, b_stroke = ("#0c0c0c", "#9a9aa2") if dark else ("#1a1a1a", "#666666")
    order = []
    w, b = white, black
    while w or b:          # alternar colores para que la urna se vea mezclada
        if w:
            order.append("w"); w -= 1
        if b:
            order.append("b"); b -= 1
    balls = ""
    for i, colour in enumerate(order):
        row, col = divmod(i, 5)
        x = 102 + 24 * col + (12 if row % 2 else 0)
        y = 172 - 25 * row
        fill, edge = (w_fill, w_stroke) if colour == "w" else (b_fill, b_stroke)
        balls += f'<circle cx="{x}" cy="{y}" r="11" fill="{fill}" stroke="{edge}" stroke-width="2"/>'
    return (
        '<svg viewBox="0 0 300 280" width="100%" style="max-width:260px" '
        'xmlns="http://www.w3.org/2000/svg">'
        f'<ellipse cx="150" cy="70" rx="80" ry="24" fill="none" stroke="{stroke}" stroke-width="3"/>'
        f'<path d="M 70 70 L 70 190" stroke="{stroke}" stroke-width="3" fill="none"/>'
        f'<path d="M 230 70 L 230 190" stroke="{stroke}" stroke-width="3" fill="none"/>'
        f'<ellipse cx="150" cy="190" rx="80" ry="24" fill="none" stroke="{stroke}" stroke-width="3"/>'
        f'{balls}'
        f'<text x="150" y="240" text-anchor="middle" font-size="16" fill="{fg}">'
        f'{white} blancas · {black} negras</text>'
        f'<text x="150" y="264" text-anchor="middle" font-size="14" fill="{fg}">'
        f'Total: {white + black} bolas</text></svg>'
    )


def birthday_chart(dark, n_cur: int):
    ns = list(range(1, 81))
    ps = [1 - probability_all_different(k) for k in ns]
    p = ui.new_figure(dark, height=310, x_axis_label="nº de personas (n)",
                      y_axis_label="P(coincidencia)", x_range=(1, 100), y_range=(0, 1.03))
    p.line(ns, ps, line_width=5, color=ui.BLUE_LINE)
    p.add_layout(Span(location=0.5, dimension="width", line_color=ui.GREY_LINE,
                      line_dash="dashed", line_width=1))
    p.add_layout(Span(location=23, dimension="height", line_color=ui.GREY_LINE,
                      line_dash="dotted", line_width=1))
    p.scatter([n_cur], [1 - probability_all_different(n_cur)], size=16, color=ui.UBU_RED,
              line_color="white", line_width=2)
    return p


def binomial_chart(dark, n: int, p_ok: float, kmin: int):
    ks = np.arange(0, n + 1)
    pmf = stats.binom.pmf(ks, n, p_ok)
    colours = [ui.UBU_RED if k >= kmin else ui.BLUE_LINE for k in ks]
    p = ui.new_figure(dark, height=310, x_axis_label="k (nº de éxitos)", y_axis_label="P(X = k)")
    p.vbar(x=ks, top=pmf, width=0.92, fill_color=colours, line_color=None)
    p.add_layout(Span(location=kmin - 0.5, dimension="height", line_color=ui.GREY_LINE,
                      line_dash="dashed", line_width=2))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>El arte de contar</b>")
        ui.content(
            "Antes que el álgebra o el cálculo estuvo la aritmética, y antes que medir estuvo "
            "<b>contar</b>. La combinatoria es precisamente el arte de contar sin escribir una a una "
            "todas las posibilidades: nos dice cuántas hay. Sus orígenes son muy antiguos (los "
            "matemáticos de la India, como Pingala, ya contaban métricas y combinaciones), y hoy sabemos "
            "que el cardinal de un conjunto puede dispararse de forma vertiginosa: Ronald Graham hizo "
            "célebre un número tan colosal (el número de Graham) que ni todo el universo bastaría para "
            "escribir sus cifras. Contar bien es, por tanto, imprescindible."
        )
        ui.content(
            "Seguramente ya lo trataste en Matemática Discreta, pero conviene recordar que todo se "
            "reduce a tres ideas fundamentales: <b>¿importa el orden?</b>, <b>¿puede haber "
            "repetición?</b> y <b>¿se usan todos los elementos?</b>. Juega con las tres respuestas y con "
            "los deslizadores para descubrir de qué agrupación se trata."
        )

        ui.section("Calculadora combinatoria")
        cs1, cs2 = st.columns(2)
        m = cs1.slider("Total de elementos (m)", 1, 20, 10, key="slider_m")
        n = cs2.slider("Elementos a tomar (n)", 1, 20, 3, key="slider_n")
        q1, q2, q3 = st.columns(3)
        orden = q1.radio("¿Importa el orden?", ["Sí", "No"], key="q_orden", horizontal=True) == "Sí"
        rep = q2.radio("¿Hay repetición?", ["Sí", "No"], index=1, key="q_rep", horizontal=True) == "Sí"
        todos = q3.radio("¿Todos los elementos?", ["Sí", "No"], index=1, key="q_todos",
                         horizontal=True) == "Sí"

        kind = combi_kind(orden, rep, todos)
        name, expr, example = COMBI_INFO[kind]
        val = combi_value(kind, m, n)
        ui.content(f"<b>{name}.</b><br>Ejemplo: {example}")
        ui.formula(expr + (f" = <b>{ui.fmt_int(val)}</b>" if val is not None else ""))

        ui.section("Ahora inténtalo tú")
        if val is not None:
            ui.content(f"Si tuvieras <b>un elemento más</b> en el total (m + 1 = {m + 1}), ¿cuántas "
                       "agrupaciones de este mismo tipo habría?")
            ui.spoiler(f"Habría <b>{ui.fmt_int(combi_value(kind, m + 1, n))}</b> agrupaciones.")
        else:
            ui.content("¿Cuántas ordenaciones distintas tiene la palabra <b>PROBABILIDAD</b>? (12 letras, "
                       "con la B, la A, la I y la D repetidas dos veces cada una).")
            word = factorial(12) // factorial(2) ** 4
            ui.spoiler(f"12! / (2!·2!·2!·2!) = <b>{ui.fmt_int(word)}</b> ordenaciones.")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Pensar al revés, con Pólya</b><br>"
            "<i>Resuelve con George Pólya (1887-1985) tres problemas que se vuelven sencillos cuando "
            "se miran desde el otro lado: una urna, dos vasos y unas oposiciones.</i><br><br>"
            "<b>II. La paradoja del cumpleaños</b><br>"
            "<i>Descubre si dos personas de la clase cumplen años el mismo día, con un pequeño sistema "
            "digital.</i><br><br>"
            "<b>III. Monedas cargadas</b><br>"
            "<i>Adéntrate en una isla desierta y consigue una probabilidad perfecta con monedas "
            "imperfectas.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el número de <u>bolas blancas W</u>")
        w_balls = st.slider("Bolas blancas iniciales (W)", 1, 10, v["white"], key=ui.wkey(PAGE, "white"),
                            label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Pensar al revés, con Pólya</b><br><br>"
            "George Pólya (1887-1985) dedicó su libro <i>Cómo plantear y resolver problemas</i> (1945) a "
            "las preguntas que conviene hacerse ante un problema difícil. Una de sus favoritas: "
            "<i>¿puedes resolver el problema contrario?</i> Pruébalo con esta urna, que contiene W bolas "
            "blancas y 4 negras. Se extrae una bola al azar y resulta ser <b>negra</b>; después se eligen "
            "3 de las bolas restantes para formar una segunda urna. ¿Cuál es la probabilidad de que entre "
            "esas 3 haya <b>al menos una blanca</b>?"
        )

        if ui.accordion_step("U_A", "(A) Dos colores, una decisión"):
            ui.content(
                "Tras sacar la primera bola negra, en la urna quedan W blancas y 3 negras. Formamos la "
                "segunda urna eligiendo 3 de esas bolas al azar. Es más cómodo calcular el "
                "<b>complementario</b>: que las 3 elegidas sean todas negras.<br><br>"
                "<i>Trata de escribir la probabilidad antes de revelarla.</i>"
            )
            total_rest = w_balls + 3
            casos = comb(total_rest, 3)
            ui.spoiler(
                f"<div class='formula-box'>P(al menos 1 blanca) = 1 &minus; "
                f"<sup>1</sup>&frasl;<sub>C({total_rest},3)</sub> = 1 &minus; "
                f"<sup>1</sup>&frasl;<sub>{casos}</sub> = {1 - 1 / casos:.4f}</div>",
                hint="Pulsa para revelar el cálculo",
            )

        if ui.accordion_step("U_B", "(B) Cucharas engañosas"):
            ui.content(
                "Tienes un vaso de agua y un vaso de aceite. Coges una cucharada del de agua y la echas "
                "en el de aceite; agitas bien. Luego coges una cucharada de esa mezcla y la devuelves al "
                "vaso de agua. ¿Dónde es mayor la proporción de intruso: aceite en el agua, o agua en el "
                "aceite?<br><br><i>Piénsalo antes de mirar la respuesta.</i>"
            )
            ui.spoiler(
                "Son <b>exactamente iguales</b>. Como el volumen final de cada vaso vuelve a ser el de "
                "partida, todo el aceite que falta en su vaso ha sido reemplazado por agua, y viceversa: "
                "la cantidad de agua en el aceite es igual a la de aceite en el agua. Es otro consejo de "
                "Pólya: en lugar de seguir el proceso paso a paso, fíjate en lo que no cambia."
            )

        if ui.accordion_step("U_C", "(C) Más que estudiar, opositar"):
            ui.content(
                "En unas oposiciones hay 90 temas. En el examen se sortean 5 al azar y debes desarrollar "
                "1 de ellos. ¿Cuántos temas necesitas llevar preparados para asegurarte <b>siempre</b> un "
                "10 (es decir, que al menos uno de los 5 sorteados lo tengas estudiado)?<br><br>"
                "<i>Piensa en el peor caso posible.</i>"
            )
            ui.spoiler(
                "En el peor caso, los 5 temas sorteados serían justo de los que no llevas. Para que eso "
                "sea imposible, los no estudiados deben ser como mucho 4: 90 &minus; 4 = <b>86 temas</b>. "
                "Con 86 preparados, cualquier grupo de 5 contiene al menos uno tuyo: es el principio del "
                "palomar de Dirichlet."
            )

    with col_right:
        ui.right_panel()
        ui.section("Las urnas, paso a paso")
        total_rest = w_balls + 3
        casos = comb(total_rest, 3)
        u1, u2 = st.columns(2)
        with u1:
            ui.caption("Urna inicial")
            ui.svg(draw_urn(w_balls, 4, dark))
        with u2:
            ui.caption("Tras sacar una negra")
            ui.svg(draw_urn(w_balls, 3, dark))
        ui.comment(f"Con W = {w_balls}: quedan {total_rest} bolas y hay C({total_rest}, 3) = {casos} "
                   "formas de elegir 3. Solo una de ellas es «todas negras».")
        ui.badge(f"P(al menos 1 blanca) &asymp; {(1 - 1 / casos) * 100:.2f}%")
        ui.footer_bar("¿Qué le ocurre a la probabilidad cuando aumentas el número de bolas blancas W? "
                      "¿Tiende a algo?")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de personas n</u>")
        n_people = st.slider("Número de personas (n)", 2, 100, v["people"], key=ui.wkey(PAGE, "people"),
                             label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La paradoja del cumpleaños</b><br><br>"
            "Antes de calcular nada: <b>¿cuántas personas crees que hacen falta para que la probabilidad "
            "de que al menos dos cumplan años el mismo día supere el 50 %?</b> Anota tu estimación y "
            "compruébala con el deslizador."
        )

        if ui.accordion_step("D_A", "(A) Pasando la pelota en baloncesto"):
            ui.content(
                "Imagina 5 jugadores que se pasan la pelota: cada <b>pareja</b> es una oportunidad de "
                "coincidencia, y hay más parejas de las que parece. Calculémoslo explícitamente para "
                "n = 5. La probabilidad de que los 5 cumplan en días distintos es:<br><br>"
                "<i>Trata de escribirla antes de revelarla.</i>"
            )
            p5 = probability_all_different(5)
            ui.spoiler(
                "<div class='formula-box'>P(distintos) = "
                "<sup>365·364·363·362·361</sup>&frasl;<sub>365<sup>5</sup></sub> = "
                f"{p5:.4f}</div>"
                f"Luego P(coincidencia) = 1 &minus; {p5:.4f} = <b>{1 - p5:.4f}</b>, y hay "
                f"C(5,2) = {comb(5, 2)} parejas posibles."
            )

        if ui.accordion_step("D_B", "(B) El caso general de la clase"):
            ui.content(
                "Para n personas, los casos posibles son 365<sup>n</sup> (variaciones con repetición) y "
                "los favorables a que nadie coincida son 365·364·&hellip;·(365&minus;n+1) (variaciones "
                "ordinarias). El gráfico de la derecha muestra cómo se dispara la probabilidad.<br><br>"
                "<i>Trata de escribir la fórmula general.</i>"
            )
            ui.spoiler(
                "<div class='formula-box'>P(coinciden) = 1 &minus; "
                "<sup>365 · 364 · &hellip; · (365&minus;n+1)</sup>&frasl;<sub>365<sup>n</sup></sub></div>"
                "El crecimiento tan rápido se debe a que con n personas hay C(n,2) = n(n&minus;1)/2 "
                "parejas, no n."
            )

        if ui.accordion_step("D_C", "(C) Se nos va de las manos"):
            ui.content(
                "Puedes comprobar este sorprendente resultado en clase usando solo tus manos. Con la "
                "<b>mano derecha en binario</b> codifica el día del mes (dedo arriba = 1, dedo abajo = 0: "
                "con 5 dedos llegas hasta 31). Con la <b>mano izquierda</b> usa las falanges para señalar "
                "el mes. Que cada persona muestre su fecha a la vez y buscad coincidencias: casi siempre "
                "aparece alguna. Eso sí, ¡cuidado con enseñar el día <i>may the force</i> (4 de mayo)!"
            )

    with col_right:
        ui.right_panel()
        ui.section("Cómo evoluciona la probabilidad")
        p_coin = 1 - probability_all_different(n_people)
        ui.badge(f"Con {n_people} personas: P(coincidencia) = {p_coin * 100:.2f}%")
        ui.show(birthday_chart(dark, n_people), key="fig_birthday")
        ui.footer_bar(f"Hay {ui.fmt_int(comb(n_people, 2))} parejas posibles entre {n_people} personas. "
                      "Las líneas marcan el 50 % y las 23 personas.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("ajusta las <u>monedas y el umbral</u>")
        cs1, cs2 = st.columns(2)
        p1 = cs1.slider("Moneda 1: P(cara)", 0.0, 1.0, v["p1"], 0.05, key=ui.wkey(PAGE, "p1"))
        p2 = cs2.slider("Moneda 2: P(cara)", 0.0, 1.0, v["p2"], 0.05, key=ui.wkey(PAGE, "p2"))
        cs3, cs4 = st.columns(2)
        n_throws = cs3.slider("Nº de lanzamientos (n)", 10, 200, v["throws"], 10,
                              key=ui.wkey(PAGE, "throws"))
        threshold = cs4.slider("Más del X% de éxitos", 10, 90, v["threshold"], 5,
                               key=ui.wkey(PAGE, "threshold"))
        p_ok = 1 - (1 - p1) * (1 - p2)
        kmin = threshold * n_throws // 100 + 1

        ui.planteamiento()
        ui.statement(
            "<b>Monedas cargadas</b><br><br>"
            f"Dos monedas parecen idénticas, pero están trucadas: una da cara con probabilidad "
            f"{v['p1']:.2f} y la otra con {v['p2']:.2f}. Se lanzan a la vez {v['throws']} veces y "
            "contamos como «éxito» que salga <b>al menos una cara</b>. ¿Cuál es la probabilidad de "
            f"obtener éxito en más del {v['threshold']}% de los lanzamientos?"
        )

        if ui.accordion_step("C_A", "(A) Planteamiento y fórmula"):
            ui.content(
                "Sea X el número de éxitos en n lanzamientos independientes. X sigue una distribución "
                "<b>binomial</b> B(n, p), donde p es la probabilidad de éxito en un lanzamiento. Como "
                "éxito = «al menos una cara», p = 1 &minus; P(las dos cruces).<br><br>"
                "<i>Trata de escribir p y la probabilidad pedida.</i>"
            )
            q1, q2 = 1 - v["p1"], 1 - v["p2"]
            k0 = v["threshold"] * v["throws"] // 100 + 1
            pv = 1 - q1 * q2
            ui.spoiler(
                f"<div class='formula-box'>p = 1 &minus; ({q1:.2f} &middot; {q2:.2f}) = {pv:.4f}</div>"
                f"<div class='formula-box'>P(X &ge; {k0}) = &sum;<sub>k={k0}</sub><sup>{v['throws']}</sup> "
                f"( {v['throws']} sobre k ) p<sup>k</sup> (1 &minus; p)<sup>{v['throws']}&minus;k</sup></div>",
                hint="Pulsa para revelar p y la fórmula",
            )

        if ui.accordion_step("C_B", "(B) La isla desierta"):
            ui.content(
                "Pablo y Adriana están en una isla desierta y solo tienen una moneda gastada que "
                "favorece las caras. ¿Cómo decidir de forma justa sin conocer su sesgo? El truco (de von "
                "Neumann): lanzarla <b>dos veces</b>. Se descartan CARA-CARA y CRUZ-CRUZ; si sale "
                "CARA-CRUZ gana Pablo y si sale CRUZ-CARA gana Adriana.<br><br>"
                "<i>¿Por qué es justo aunque la moneda esté trucada?</i>"
            )
            ui.spoiler(
                "<div class='formula-box'>P(C,X) = p(1&minus;p) = (1&minus;p)p = P(X,C)</div>"
                "El orden de los factores no altera el producto: ambas secuencias tienen exactamente la "
                "misma probabilidad, sea cual sea el valor desconocido de p. ¡Moneda imperfecta, decisión "
                "perfecta!"
            )

        if ui.accordion_step("C_C", "(C) De la binomial a la campana"):
            ui.content(
                "Cuando n es grande, calcular la suma binomial a mano es inviable. El teorema de De "
                "Moivre-Laplace nos dice que la binomial se parece cada vez más a una <b>campana de "
                "Gauss</b> de media &mu; = np y desviación &sigma; = &radic;(np(1&minus;p)). Fíjate en el "
                "histograma de la derecha: su silueta es ya casi una normal.<br><br>"
                "<i>Trata de escribir &mu; y &sigma;.</i>"
            )
            ui.spoiler(
                "<div class='formula-box'>&mu; = n·p &nbsp;&nbsp; &sigma; = &radic;(n·p·(1&minus;p))</div>"
                "Así P(X &gt; k) se aproxima con el área de la cola de esa campana."
            )

    with col_right:
        ui.right_panel()
        ui.section("Distribución de X = nº de éxitos")
        p_exact = float(stats.binom.sf(kmin - 1, n_throws, p_ok))
        mu = n_throws * p_ok
        sigma = (n_throws * p_ok * (1 - p_ok)) ** 0.5
        ui.comment(f"p = 1 &minus; ({1 - p1:.2f}·{1 - p2:.2f}) = <b>{p_ok:.4f}</b>. Buscamos "
                   f"P(X &ge; {kmin}) en B({n_throws}, {p_ok:.2f}). &mu; = {mu:.1f}, &sigma; = {sigma:.2f}.")
        ui.badge(f"P(X &ge; {kmin}) &asymp; {p_exact * 100:.2f}%")
        ui.show(binomial_chart(dark, n_throws, p_ok, kmin), key="fig_binomial")
        ui.footer_bar(f"En rojo, la cola k &ge; {kmin} que suma la probabilidad pedida. ¿Cómo cambia al "
                      "mover el umbral o el sesgo de las monedas?")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Pensar al revés, con Pólya", "U_A"),
        ("P2", "(II) La paradoja del cumpleaños", "D_A"),
        ("P3", "(III) Monedas cargadas", "C_A"),
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
