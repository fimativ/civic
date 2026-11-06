#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 1: los vectores aleatorios.

Clase y supervivencia en el Titanic (distribución conjunta discreta,
marginales y condicionadas), las gotas de Ulam en un círculo (vector
continuo uniforme) y los cangrejos de Nápoles (vector mixto y Bayes).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Vectores aleatorios"
SYMBOL = "v.a."
PAGE = "05_01"

CLASSES = ["Primera", "Segunda", "Tercera", "Tripulación"]
# Pasajeros y tripulantes del Titanic según clase y supervivencia (2201 personas).
TITANIC = np.array([[122, 203], [167, 118], [528, 178], [673, 212]])


def initial_values():
    return {
        "x0": ui.dfloat(0.5, -0.8, 0.8, "x0", 2),
        "prior": ui.dchoice(0.5, [0.3, 0.4, 0.5, 0.6, 0.7], "prior"),
        "y": ui.dfloat(64.0, 61.0, 67.0, "y", 1),
        "seed": int(ui.r("ulam") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "titanic_view": "class", "ulam_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def titanic_tables():
    joint = TITANIC / TITANIC.sum()
    p_class = joint.sum(axis=1)
    p_surv = joint.sum(axis=0)
    return joint, p_class, p_surv


def ulam_points(n: int, seed: int):
    rng = np.random.default_rng(seed)
    pts = rng.uniform(-1, 1, (n, 2))
    inside = (pts ** 2).sum(axis=1) <= 1
    return pts, inside


CRAB = {"A": (62.5, 1.4), "B": (65.5, 1.6)}


def crab_posterior(y, prior):
    fa = stats.norm.pdf(y, *CRAB["A"])
    fb = stats.norm.pdf(y, *CRAB["B"])
    return prior * fa / (prior * fa + (1 - prior) * fb)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def titanic_chart(dark, view: str):
    joint, p_class, p_surv = titanic_tables()
    if view == "class":
        cond = TITANIC[:, 1] / TITANIC.sum(axis=1)
        p = ui.new_figure(dark, height=300, x_range=CLASSES, y_range=(0, 1), y_axis_label="ℙ(sobrevive | clase)")
        p.vbar(x=CLASSES, top=cond, width=0.6, color=ui.BLUE_LINE)
        p.add_layout(Span(location=p_surv[1], dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    else:
        cond = TITANIC[:, 1] / TITANIC[:, 1].sum()
        p = ui.new_figure(dark, height=300, x_range=CLASSES, y_range=(0, 0.6), y_axis_label="probabilidad")
        p.vbar(x=[c for c in CLASSES], top=p_class, width=0.35, color=ui.GREY_LINE, alpha=0.6,
               legend_label="ℙ(clase)")
        p.scatter(CLASSES, cond, size=16, marker="diamond", color=ui.UBU_RED, legend_label="ℙ(clase | sobrevive)")
        ui.style_legend(p, dark, "top_left")
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "14px"
    return p


def ulam_chart(dark, pts, inside, x0: float):
    band = np.abs(pts[:, 0] - x0) < 0.03
    p = ui.new_figure(dark, height=330, x_range=(-1.05, 1.05), y_range=(-1.05, 1.05), match_aspect=True)
    p.grid.visible = False
    p.scatter(pts[~inside, 0], pts[~inside, 1], size=2.5, color=ui.GREY_LINE, alpha=0.35)
    p.scatter(pts[inside & ~band, 0], pts[inside & ~band, 1], size=3, color=ui.BLUE_LINE, alpha=0.6)
    p.scatter(pts[inside & band, 0], pts[inside & band, 1], size=5, color=ui.UBU_RED)
    p.add_layout(Span(location=x0, dimension="height", line_color=ui.UBU_RED, line_dash="dotted", line_width=2))
    return p


def marginal_chart(dark, pts, inside):
    xs = np.linspace(-1, 1, 300)
    p = ui.new_figure(dark, height=200, x_axis_label="x", y_axis_label="densidad de X", x_range=(-1.05, 1.05),
                      y_range=(0, 0.85))
    edges = np.linspace(-1, 1, 31)
    hist, _ = np.histogram(pts[inside, 0], bins=edges)
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (inside.sum() * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None)
    p.line(xs, 2 / np.pi * np.sqrt(1 - xs ** 2), line_width=4, color=ui.BLUE_LINE)
    return p


def crab_chart(dark, prior: float, y: float):
    xs = np.linspace(57, 71, 400)
    fa = prior * stats.norm.pdf(xs, *CRAB["A"])
    fb = (1 - prior) * stats.norm.pdf(xs, *CRAB["B"])
    p = ui.new_figure(dark, height=280, x_axis_label="anchura de la frente (escala de Weldon)", y_axis_label="densidad",
                      x_range=(57, 71))
    p.varea(x=xs, y1=0, y2=fa, color=ui.BLUE_LINE, alpha=0.3, legend_label="tipo A")
    p.varea(x=xs, y1=fa, y2=fa + fb, color=ui.GREEN_LINE, alpha=0.3, legend_label="tipo B")
    p.line(xs, fa + fb, line_width=3, color=ui.GREY_LINE, legend_label="mezcla")
    p.add_layout(Span(location=y, dimension="height", line_color=ui.UBU_RED, line_width=3))
    ui.style_legend(p, dark, "top_right")
    q = ui.new_figure(dark, height=180, x_axis_label="anchura observada y", y_axis_label="ℙ(A | y)", x_range=(57, 71),
                      y_range=(0, 1.02))
    q.line(xs, crab_posterior(xs, prior), line_width=4, color=ui.BLUE_LINE)
    q.scatter([y], [crab_posterior(y, prior)], size=14, color=ui.UBU_RED)
    return p, q


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se estudian varias magnitudes a la vez?</b>")
        ui.content(
            "Un mismo experimento produce a menudo varios números: la clase del billete y si se sobrevivió, la "
            "altura y el peso, las dos coordenadas de un punto. Un <b>vector aleatorio</b> (X, Y) es una "
            "aplicación de &Omega; en &#8477;<sup>2</sup> cuyas componentes son variables aleatorias. Su "
            "comportamiento conjunto lo recoge la <b>función de distribución conjunta</b>. <i>Escríbela.</i>"
        )
        ui.formula_hidden("F(x, y) = &#8473;(X &le; x, Y &le; y)")
        ui.content(
            "De ella salen las <b>marginales</b>, sumando o integrando la otra variable, y las "
            "<b>condicionadas</b>, dividiendo la conjunta entre la marginal de lo que se conoce. <i>Escribe "
            "ambas para un vector continuo.</i>"
        )
        ui.formula_hidden("f<sub>1</sub>(x) = &int; f(x, y) dy &nbsp;&nbsp; f(y | x) = <sup>f(x, y)</sup>&frasl;"
                          "<sub>f<sub>1</sub>(x)</sub>")
        ui.content("Las componentes son independientes si la conjunta es el producto de las marginales.")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El Titanic (1912)</b><br>"
            "<i>Lee en la tabla de pasajeros la distribución conjunta de la clase y la supervivencia.</i><br><br>"
            "<b>II. Las gotas de Ulam (1946)</b><br>"
            "<i>Lanza puntos al azar con Stanisław Ulam, quédate con los del círculo y estudia sus "
            "coordenadas.</i><br><br>"
            "<b>III. Los cangrejos de Nápoles (1894)</b><br>"
            "<i>Una medida continua y un tipo discreto: decide con Karl Pearson a qué grupo pertenece un "
            "cangrejo.</i>"
        )


def render_problem_1(dark):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>El Titanic (1912)</b><br><br>"
            "La noche del 14 al 15 de abril de 1912 el Titanic chocó con un iceberg y se hundió en menos de tres "
            "horas, con botes salvavidas para poco más de la mitad de las personas a bordo. Las investigaciones "
            "posteriores registraron, para cada una, su clase y si sobrevivió. Elegimos al azar a una de las "
            "2201 personas de la tabla: X es su clase e Y vale 1 si sobrevivió y 0 si no."
        )
        rows = "".join(f"<tr><td>{c}</td><td>{a}</td><td>{b}</td><td>{a + b}</td></tr>"
                       for c, (a, b) in zip(CLASSES, TITANIC))
        ui.content("<table><tr><th>clase</th><th>murió</th><th>sobrevivió</th><th>total</th></tr>" + rows +
                   f"<tr><th>total</th><th>{TITANIC[:, 0].sum()}</th><th>{TITANIC[:, 1].sum()}</th>"
                   f"<th>{TITANIC.sum()}</th></tr></table>")

        if ui.accordion_step("P1_A", "(A) Conjunta y marginales"):
            ui.content(
                "Divide cada casilla entre 2201 para tener la función de probabilidad conjunta. ¿Cómo se obtienen de "
                "ella la distribución de la clase y la de la supervivencia?"
            )
            ui.spoiler(
                "Sumando por filas y por columnas: &#8473;(X = x) = &sum;<sub>y</sub> &#8473;(X = x, Y = y). Por eso se "
                "llaman marginales: aparecen en los márgenes de la tabla. Sobrevivió una de cada tres personas, "
                "711 de 2201, y la tripulación era el grupo más numeroso."
            )

        if ui.accordion_step("P1_B", "(B) Condicionadas"):
            ui.content(
                "Calcula la probabilidad de sobrevivir condicionada a cada clase. Después, la distribución de la "
                "clase entre los supervivientes. Elige la vista a la derecha."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(Y = 1 | X = x) = <sup>&#8473;(X = x, Y = 1)</sup>&frasl;<sub>&#8473;(X = x)</sub></div>"
                "Sobrevivió el 62 % de primera, el 41 % de segunda, el 25 % de tercera y el 24 % de la tripulación. "
                "Y entre los supervivientes, la primera clase está sobrerrepresentada: es el 29 % de ellos, frente "
                "al 15 % del total. Cada condicionada es una distribución completa: suma 1."
            )

        if ui.accordion_step("P1_C", "(C) ¿Independientes?"):
            ui.content(
                "Si la clase y la supervivencia fueran independientes, ¿qué debería cumplir cada casilla de la tabla? "
                "Compruébalo con la primera clase."
            )
            ui.spoiler(
                "Debería cumplirse &#8473;(X = x, Y = y) = &#8473;(X = x)&#8473;(Y = y), o lo que es lo mismo, todas las "
                "condicionadas deberían coincidir con la marginal 711/2201 &asymp; 0.32. Para la primera clase, la "
                "conjunta de sobrevivir es 203/2201 &asymp; 0.092 y el producto de marginales 0.148 &times; 0.323 "
                "&asymp; 0.048: casi el doble. La clase y la supervivencia estuvieron fuertemente asociadas."
            )

    with col_right:
        ui.right_panel()
        views = {"class": "Sobrevivir según la clase", "surv": "Clase de los supervivientes"}
        ui.choice_buttons(list(views), "titanic_view", labels=views, per_row=2)
        joint, p_class, p_surv = titanic_tables()
        ui.metrics([(f"&#8473;(sobrevive) = {p_surv[1]:.3f}", "metric-a"),
                    (f"&#8473;(primera, sobrevive) = {joint[0, 1]:.3f}", "metric-c")])
        ui.show(titanic_chart(dark, st.session_state["titanic_view"]), key="fig_titanic")
        product = np.outer(p_class, p_surv)
        ratio = " · ".join(f"{c}: {joint[i, 1] / product[i, 1]:.2f}" for i, c in enumerate(CLASSES))
        ui.footer_bar("Cociente entre la conjunta y el producto de marginales en la columna de supervivientes (1 si "
                      f"hubiera independencia): {ratio}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("mueve la <u>abscisa x<sub>0</sub></u> en la que se condiciona")
        x0 = st.slider("x₀", -0.95, 0.95, v["x0"], 0.01, key=ui.wkey(PAGE, "x0"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las gotas de Ulam (1946)</b><br><br>"
            "Convaleciente de una enfermedad, Stanisław Ulam jugaba solitarios y se preguntó con qué probabilidad "
            "saldría uno. En lugar de calcularla, pensó, bastaría jugar muchas partidas y contar: así nació, con "
            "John von Neumann, el método de Montecarlo. Hacemos lo mismo con puntos: se lanzan al azar en el "
            "cuadrado [&minus;1, 1]<sup>2</sup> y nos quedamos con los que caen en el círculo unidad. Las "
            "coordenadas (X, Y) de esos puntos forman un vector uniforme en el círculo."
        )

        if ui.accordion_step("P2_A", "(A) La densidad conjunta"):
            ui.content(
                "¿Cuál es la densidad conjunta de un vector uniforme en el círculo? ¿Qué fracción de los puntos del "
                "cuadrado cae dentro, y qué número permite estimar?"
            )
            ui.spoiler(
                "Una densidad constante en el recinto, inversa de su área:"
                "<div class='formula-box'>f(x, y) = 1/&pi; &nbsp; si x<sup>2</sup> + y<sup>2</sup> &le; 1</div>"
                "Cae dentro la fracción &pi;/4 de los puntos del cuadrado, así que cuatro veces la frecuencia "
                "observada estima &pi;, como la aguja de Buffon por otro camino."
            )

        if ui.accordion_step("P2_B", "(B) La marginal"):
            ui.content(
                "Integra la densidad conjunta en y para obtener la densidad de X. ¿Es uniforme? Compárala con el "
                "histograma de la derecha."
            )
            ui.spoiler(
                "Para cada x, y recorre el segmento [&minus;&radic;(1 &minus; x<sup>2</sup>), &radic;(1 &minus; x<sup>2</sup>)]:"
                "<div class='formula-box'>f<sub>1</sub>(x) = &int; <sup>1</sup>&frasl;<sub>&pi;</sub> dy = "
                "<sup>2</sup>&frasl;<sub>&pi;</sub>&radic;(1 &minus; x<sup>2</sup>), &nbsp; |x| &le; 1</div>"
                "No es uniforme: es media elipse, porque las cuerdas verticales del círculo son más largas en el "
                "centro que cerca de los bordes. Un vector uniforme no tiene por qué tener marginales uniformes; "
                "las tiene, por ejemplo, si el recinto es un rectángulo de lados paralelos a los ejes."
            )

        if ui.accordion_step("P2_C", "(C) La condicionada y la dependencia"):
            ui.content(
                "Fija X = x<sub>0</sub>: los puntos rojos son los que tienen esa abscisa. ¿Qué distribución tiene Y "
                "condicionada a X = x<sub>0</sub>? ¿Son X e Y independientes? Calcula su covarianza."
            )
            ui.spoiler(
                "<div class='formula-box'>f(y | x<sub>0</sub>) = <sup>1/&pi;</sup>&frasl;<sub>(2/&pi;)&radic;(1 &minus; "
                "x<sub>0</sub><sup>2</sup>)</sub>, &nbsp; |y| &le; &radic;(1 &minus; x<sub>0</sub><sup>2</sup>)</div>"
                "Uniforme en un segmento cuya longitud depende de x<sub>0</sub>: conocer X cambia lo que se sabe de Y, "
                "así que no son independientes. La conjunta no es el producto de marginales: en (0.9, 0.9) el "
                "producto es positivo y la conjunta vale cero. Sin embargo, por simetría, &#120124;[XY] = 0 y "
                "Cov(X, Y) = 0. Variables incorreladas pueden ser dependientes."
            )

    with col_right:
        ui.right_panel()
        if st.button("Lanzar otros puntos", key="ulam_new", width="stretch"):
            st.session_state["ulam_round"] += 1
        pts, inside = ulam_points(6000, v["seed"] + st.session_state["ulam_round"])
        inner = pts[inside]
        ui.metrics([(f"4&middot;(dentro/total) = {4 * inside.mean():.4f}", "metric-a"),
                    (f"Cov(X, Y) muestral = {np.cov(inner[:, 0], inner[:, 1])[0, 1]:+.4f}", "metric-c")])
        ui.show(ulam_chart(dark, pts, inside, x0), key="fig_ulam")
        ui.show(marginal_chart(dark, pts, inside), key="fig_ulam_marginal")
        half = np.sqrt(max(0.0, 1 - x0 ** 2))
        ui.footer_bar(f"Con X = {x0:.2f}, Y es uniforme en [&minus;{half:.3f}, {half:.3f}]. Abajo, la marginal de X: el "
                      "histograma de los puntos del círculo frente a (2/&pi;)&radic;(1 &minus; x<sup>2</sup>).")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>proporción de tipo A</u> y la <u>medida observada y</u>")
        prior = st.slider("Proporción de cangrejos de tipo A", 0.05, 0.95, v["prior"], 0.05, key=ui.wkey(PAGE, "prior"))
        y = st.slider("Medida observada y", 57.0, 71.0, v["y"], 0.1, key=ui.wkey(PAGE, "y"))

        ui.planteamiento()
        ui.statement(
            "<b>Los cangrejos de Nápoles (1894)</b><br><br>"
            "Walter Weldon midió la anchura de la frente de mil cangrejos de la bahía de Nápoles y obtuvo un "
            "histograma asimétrico, que no encajaba en ninguna normal. Karl Pearson propuso que la población "
            "mezclaba dos tipos, cada uno con su propia normal. En nuestra versión, un cangrejo es de tipo A con "
            "probabilidad &pi; y de tipo B en otro caso, y su medida Y, dado el tipo, es normal con la media y la "
            "desviación de ese tipo. El tipo es discreto y la medida continua: un vector mixto."
        )

        if ui.accordion_step("P3_A", "(A) La densidad de la mezcla"):
            ui.content(
                "Escribe la densidad marginal de la medida Y repartiendo entre los dos tipos. ¿Por qué puede salir "
                "asimétrica o con dos jorobas, aunque cada tipo sea normal?"
            )
            ui.spoiler(
                "Por la probabilidad total aplicada a densidades:"
                "<div class='formula-box'>f(y) = &pi;&middot;f(y | A) + (1 &minus; &pi;)&middot;f(y | B)</div>"
                "La suma ponderada de dos campanas con centros distintos ya no es una campana: si están cerca sale "
                "una curva asimétrica, como la de Weldon; si están lejos, dos jorobas. Pearson tuvo que estimar "
                "cinco parámetros con el método de los momentos, resolviendo a mano un polinomio de grado nueve."
            )

        if ui.accordion_step("P3_B", "(B) Bayes con una medida continua"):
            ui.content(
                "Se mide un cangrejo y su frente vale y. ¿Qué probabilidad hay de que sea de tipo A? Aplica el "
                "teorema de Bayes con densidades en lugar de probabilidades."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(A | y) = <sup>&pi;&middot;f(y | A)</sup>&frasl;<sub>&pi;&middot;f(y | A) + "
                "(1 &minus; &pi;)&middot;f(y | B)</sub></div>"
                "Es la misma fórmula que en el tema 2, con la densidad de la medida en lugar de la probabilidad del "
                "suceso: &#8473;(Y = y) vale cero, pero el cociente de densidades tiene sentido como límite de "
                "intervalos cada vez más pequeños alrededor de y."
            )

        if ui.accordion_step("P3_C", "(C) Dónde está la frontera"):
            ui.content(
                "¿Para qué medida es igual de probable que el cangrejo sea de un tipo que del otro? ¿Cómo se desplaza "
                "esa frontera al cambiar la proporción &pi;?"
            )
            ui.spoiler(
                "La frontera es donde &pi;f(y | A) = (1 &minus; &pi;)f(y | B), el cruce de las dos áreas coloreadas. "
                "Si el tipo A es más frecuente, la frontera se desplaza hacia el lado de B: hace falta una medida "
                "más típica de B para inclinarse por B. Es la tasa base del tema 2 en versión continua."
            )

    with col_right:
        ui.right_panel()
        post = float(crab_posterior(y, prior))
        ui.metrics([(f"&#8473;(A | y = {y:.1f}) = {post:.4f}", "metric-a"),
                    (f"&#8473;(B | y = {y:.1f}) = {1 - post:.4f}", "metric-b")])
        top, bottom = crab_chart(dark, prior, y)
        ui.show(top, key="fig_crabs")
        ui.show(bottom, key="fig_crabs_post")
        ui.footer_bar("Arriba, la densidad de la mezcla repartida entre los dos tipos; la línea roja es la medida "
                      "observada. Abajo, la probabilidad a posteriori del tipo A para cada medida posible.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El Titanic", "P1_A"),
        ("P2", "(II) Las gotas de Ulam", "P2_A"),
        ("P3", "(III) Los cangrejos de Nápoles", "P3_A"),
    ])

    if current == "INTRO":
        render_intro()
    elif current == "P1":
        render_problem_1(dark)
    elif current == "P2":
        render_problem_2(dark, v)
    elif current == "P3":
        render_problem_3(dark, v)

    ui.footer()


main()
