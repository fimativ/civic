#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 5: la normal bidimensional.

Los errores de tiro de Bravais (elipses de densidad y probabilidad dentro de
ellas), la regresión hacia la media de Galton (la normal condicionada) y dos
normales que no forman una normal (incorrelación sin independencia).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "La normal bidimensional"
SYMBOL = "N₂(μ,Σ)"
PAGE = "05_05"

MU_H, SD_H = 172.0, 7.0   # talla media y desviación de padres e hijos (cm)
BUILDS = {"sign": "Signo al azar", "cut": "Reflejar las colas"}
CUT = 1.5381


def initial_values():
    return {
        "sx": ui.dchoice(2.0, [1.0, 1.5, 2.0, 3.0], "sx"),
        "sy": ui.dchoice(1.0, [1.0, 1.5, 2.0], "sy"),
        "rho": ui.dfloat(0.5, -0.8, 0.8, "rho", 1),
        "k": ui.dchoice(2.0, [1.0, 1.5, 2.0, 2.5], "k"),
        "father": ui.dint(186, 160, 190, "father"),
        "rho_g": ui.dchoice(0.5, [0.3, 0.4, 0.5, 0.6, 0.7], "rho_g"),
        "seed": int(ui.r("bravais") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "build": "sign", "normal_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def bivariate_sample(sx, sy, rho, n, seed):
    rng = np.random.default_rng(seed)
    cov = [[sx ** 2, rho * sx * sy], [rho * sx * sy, sy ** 2]]
    return rng.multivariate_normal([0, 0], cov, n)


def ellipse(sx, sy, rho, k, n=200):
    cov = np.array([[sx ** 2, rho * sx * sy], [rho * sx * sy, sy ** 2]])
    vals, vecs = np.linalg.eigh(cov)
    t = np.linspace(0, 2 * np.pi, n)
    circle = np.vstack((np.cos(t), np.sin(t)))
    pts = vecs @ (np.sqrt(vals)[:, None] * circle) * k
    return pts[0], pts[1]


def inside_fraction(pts, sx, sy, rho, k):
    cov = np.array([[sx ** 2, rho * sx * sy], [rho * sx * sy, sy ** 2]])
    inv = np.linalg.inv(cov)
    d2 = np.einsum("ij,jk,ik->i", pts, inv, pts)
    return float((d2 <= k ** 2).mean())


def build_pair(kind: str, n: int, seed: int):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    if kind == "sign":
        y = rng.choice([-1, 1], n) * x
    else:
        y = np.where(np.abs(x) <= CUT, x, -x)
    return x, y


# =============================================================================
# 2. FIGURAS
# =============================================================================

def bravais_chart(dark, pts, sx, sy, rho, k):
    lim = 3.5 * max(sx, sy)
    p = ui.new_figure(dark, height=340, x_range=(-lim, lim), y_range=(-lim, lim), match_aspect=True,
                      x_axis_label="desviación horizontal", y_axis_label="desviación vertical")
    p.scatter(pts[:, 0], pts[:, 1], size=3, color=ui.BLUE_LINE, alpha=0.4)
    for level, colour, width in ((1, ui.GREY_LINE, 1.5), (2, ui.GREY_LINE, 1.5), (3, ui.GREY_LINE, 1.5)):
        ex, ey = ellipse(sx, sy, rho, level)
        p.line(ex, ey, line_color=colour, line_dash="dotted", line_width=width)
    ex, ey = ellipse(sx, sy, rho, k)
    p.line(ex, ey, line_color=ui.UBU_RED, line_width=3)
    return p


def galton_chart(dark, father, rho):
    xs = np.linspace(MU_H - 4 * SD_H, MU_H + 4 * SD_H, 400)
    cond_mean = MU_H + rho * (father - MU_H)
    cond_sd = SD_H * np.sqrt(1 - rho ** 2)
    p = ui.new_figure(dark, height=270, x_axis_label="talla del hijo (cm)", y_axis_label="densidad",
                      x_range=(xs[0], xs[-1]))
    p.line(xs, stats.norm.pdf(xs, MU_H, SD_H), line_width=3, color=ui.GREY_LINE, line_dash="dashed",
           legend_label="todos los hijos")
    p.line(xs, stats.norm.pdf(xs, cond_mean, cond_sd), line_width=4, color=ui.BLUE_LINE,
           legend_label=f"hijos de padres de {father} cm")
    p.add_layout(Span(location=father, dimension="height", line_color=ui.UBU_RED, line_width=2))
    p.add_layout(Span(location=cond_mean, dimension="height", line_color=ui.BLUE_LINE, line_dash="dotted", line_width=2))
    return ui.style_legend(p, dark, "top_left")


def regression_chart(dark, rho, seed):
    pts = bivariate_sample(SD_H, SD_H, rho, 1500, seed) + MU_H
    xs = np.linspace(145, 200, 2)
    p = ui.new_figure(dark, height=300, x_axis_label="talla del padre (cm)", y_axis_label="talla del hijo (cm)",
                      x_range=(145, 200), y_range=(145, 200), match_aspect=True)
    p.scatter(pts[:, 0], pts[:, 1], size=3, color=ui.GREY_LINE, alpha=0.45)
    p.line(xs, xs, line_color=ui.GREY_LINE, line_dash="dotted", line_width=2, legend_label="hijo = padre")
    p.line(xs, MU_H + rho * (xs - MU_H), line_color=ui.BLUE_LINE, line_width=4, legend_label="𝔼[hijo | padre]")
    p.line(MU_H + rho * (xs - MU_H), xs, line_color=ui.ORANGE_LINE, line_width=3, line_dash="dashed",
           legend_label="𝔼[padre | hijo]")
    return ui.style_legend(p, dark, "top_left")


def pair_charts(dark, x, y):
    p = ui.new_figure(dark, height=280, x_range=(-4, 4), y_range=(-4, 4), match_aspect=True, x_axis_label="X",
                      y_axis_label="Y")
    p.scatter(x[:2000], y[:2000], size=3, color=ui.BLUE_LINE, alpha=0.5)
    edges = np.linspace(-6, 6, 49)
    s = x + y
    hist, _ = np.histogram(s, bins=edges)
    w = edges[1] - edges[0]
    q = ui.new_figure(dark, height=220, x_axis_label="X + Y", y_axis_label="densidad", x_range=(-6, 6))
    q.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(s) * w), fill_color=ui.UBU_YELLOW,
           fill_alpha=0.65, line_color=None, legend_label="X + Y")
    xs = np.linspace(-6, 6, 300)
    q.line(xs, stats.norm.pdf(xs, 0, np.sqrt(2)), line_width=3, color=ui.RED_LINE, line_dash="dashed",
           legend_label="lo que daría una normal conjunta")
    ui.style_legend(q, dark, "top_right")
    return p, q


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo es una campana en dos dimensiones?</b>")
        ui.content(
            "Un vector (X, Y) es normal bidimensional si tiene una densidad de una forma concreta, determinada por las dos "
            "medias, las dos desviaciones típicas y el coeficiente de correlación &rho;. <i>Escribe la densidad con las variables "
            "tipificadas u = (x &minus; &mu;<sub>X</sub>)/&sigma;<sub>X</sub> y v = (y &minus; &mu;<sub>Y</sub>)/&sigma;<sub>Y</sub>.</i>"
        )
        ui.formula_hidden(
            "f(x, y) = <sup>1</sup>&frasl;<sub>2&pi;&sigma;<sub>X</sub>&sigma;<sub>Y</sub>&radic;(1 &minus; &rho;<sup>2</sup>)</sub> "
            "exp[&minus;<sup>u<sup>2</sup> &minus; 2&rho;uv + v<sup>2</sup></sup>&frasl;<sub>2(1 &minus; &rho;<sup>2</sup>)</sub>]"
        )
        ui.content(
            "En forma matricial, con el vector de medias &mu; y la matriz de covarianzas &Sigma;, la misma fórmula "
            "vale en cualquier dimensión k. Sus curvas de nivel son elipses, sus marginales son normales y sus "
            "condicionadas también. Y tiene una propiedad que casi ninguna otra distribución comparte: si &rho; = 0, "
            "las componentes son independientes."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los errores de Bravais (1846)</b><br>"
            "<i>Estudia con Auguste Bravais dónde caen los disparos alrededor del blanco.</i><br><br>"
            "<b>II. La regresión hacia la media (1886)</b><br>"
            "<i>¿Por qué los hijos de padres muy altos son, de media, menos altos que ellos? Francis Galton lo "
            "llamó regresión.</i><br><br>"
            "<b>III. Dos normales que no forman una normal</b><br>"
            "<i>Dos variables normales, incorreladas y, aun así, dependientes.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>desviaciones</u>, la <u>correlación &rho;</u> y la <u>elipse k</u>")
        c1, c2 = st.columns(2)
        sx = c1.select_slider("σ horizontal", options=[0.5, 1.0, 1.5, 2.0, 3.0], value=v["sx"], key=ui.wkey(PAGE, "sx"))
        sy = c2.select_slider("σ vertical", options=[0.5, 1.0, 1.5, 2.0, 3.0], value=v["sy"], key=ui.wkey(PAGE, "sy"))
        c3, c4 = st.columns(2)
        rho = c3.slider("Correlación ρ", -0.95, 0.95, v["rho"], 0.05, key=ui.wkey(PAGE, "rho"))
        k = c4.slider("Elipse de k desviaciones", 0.5, 3.5, v["k"], 0.1, key=ui.wkey(PAGE, "k"))

        ui.planteamiento()
        ui.statement(
            "<b>Los errores de Bravais (1846)</b><br><br>"
            "Auguste Bravais, físico y explorador de las regiones árticas, publicó un estudio sobre los errores "
            "cometidos al situar un punto en el plano, como el impacto de un proyectil alrededor del blanco. "
            "Las desviaciones horizontal y vertical pueden tener distinta precisión y estar relacionadas: si el "
            "viento empuja el disparo hacia un lado, puede elevarlo a la vez. Bravais escribió la densidad normal "
            "de dos variables con un término de correlación."
        )

        if ui.accordion_step("P1_A", "(A) Las elipses de densidad"):
            ui.content(
                "Las curvas de nivel de la densidad son los puntos donde el exponente es constante. ¿Qué figuras son? "
                "¿Cómo cambian con &rho; y con las desviaciones?"
            )
            ui.spoiler(
                "u<sup>2</sup> &minus; 2&rho;uv + v<sup>2</sup> = constante es una elipse centrada en las medias. Con &rho; = 0 "
                "sus ejes son paralelos a los de coordenadas, alargados en la dirección de mayor desviación; con "
                "&rho; &ne; 0 se inclinan, hacia la diagonal si &rho; &gt; 0 y hacia la antidiagonal si &rho; &lt; 0. "
                "Cuando |&rho;| se acerca a 1, la elipse se aplasta sobre una recta."
            )

        if ui.accordion_step("P1_B", "(B) Las marginales"):
            ui.content("Integra la densidad conjunta en y. ¿Qué distribución tiene la desviación horizontal por sí sola?")
            ui.spoiler(
                "Completando el cuadrado en v, la integral en y es la de una normal y vale una constante, y queda"
                "<div class='formula-box'>f<sub>1</sub>(x) = <sup>1</sup>&frasl;<sub>&sigma;<sub>X</sub>&radic;(2&pi;)</sub> "
                "e<sup>&minus;(x &minus; &mu;<sub>X</sub>)<sup>2</sup>/(2&sigma;<sub>X</sub><sup>2</sup>)</sup></div>"
                "Las marginales de una normal bidimensional son normales, y no dependen de &rho;: la correlación solo "
                "vive en la conjunta."
            )

        if ui.accordion_step("P1_C", "(C) ¿Cuántos disparos caen dentro?"):
            ui.content(
                "La elipse roja contiene los puntos a menos de k <i>desviaciones</i> del centro, medidas con la forma "
                "cuadrática. ¿Qué probabilidad encierra? ¿Coincide con el 68-95-99.7 de una dimensión?"
            )
            ui.spoiler(
                "La forma cuadrática de un vector normal bidimensional es una ji-dos con dos grados de libertad, es "
                "decir, una exponencial de media 2:"
                "<div class='formula-box'>&#8473;(dentro de la elipse k) = 1 &minus; e<sup>&minus;k<sup>2</sup>/2</sup></div>"
                "Con k = 1 encierra solo un 39 %, y con k = 2 un 86 %, mucho menos que en una dimensión: en el plano "
                "hay más sitio por el que escaparse. No depende de &rho; ni de las desviaciones, porque la elipse se "
                "adapta a ellas."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otros 3000 disparos", key="normal_new", width="stretch"):
            st.session_state["normal_round"] += 1
        pts = bivariate_sample(sx, sy, rho, 3000, v["seed"] + st.session_state["normal_round"])
        frac = inside_fraction(pts, sx, sy, rho, k)
        ui.metrics([(f"Teoría: 1 &minus; e<sup>&minus;k&sup2;/2</sup> = {1 - np.exp(-k ** 2 / 2):.4f}", "metric-a"),
                    (f"Dentro de la elipse: {frac:.4f}", "metric-c")])
        ui.show(bravais_chart(dark, pts, sx, sy, rho, k), key="fig_bravais")
        ui.footer_bar(f"Elipse roja: k = {k:.1f}. Punteadas: k = 1, 2 y 3. Correlación muestral de los disparos: "
                      f"{np.corrcoef(pts[:, 0], pts[:, 1])[0, 1]:+.3f}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>talla del padre</u> y la <u>correlación</u>")
        father = st.slider("Talla del padre (cm)", 150, 200, v["father"], 1, key=ui.wkey(PAGE, "father"))
        rho = st.slider("Correlación entre padres e hijos ρ", 0.0, 0.95, v["rho_g"], 0.05, key=ui.wkey(PAGE, "rho_g"))

        ui.planteamiento()
        ui.statement(
            "<b>La regresión hacia la media (1886)</b><br><br>"
            "Francis Galton reunió las tallas de cientos de familias y observó algo que le pareció inquietante: los "
            "hijos de padres muy altos eran altos, pero, de media, menos que sus padres; y los de padres muy bajos, "
            "menos bajos. Lo llamó regresión hacia la mediocridad. En nuestro modelo, la talla del padre y la del "
            f"hijo forman una normal bidimensional con medias {MU_H:g} cm, desviaciones {SD_H:g} cm y correlación "
            f"&rho; = {v['rho_g']}."
        )

        if ui.accordion_step("P2_A", "(A) La condicionada"):
            ui.content(
                "Divide la densidad conjunta entre la marginal del padre. ¿Qué distribución tiene la talla del hijo "
                "sabiendo que el padre mide x?"
            )
            ui.spoiler(
                "Completando el cuadrado en y, la condicionada vuelve a ser normal:"
                "<div class='formula-box'>Y | X = x ~ N(&mu;<sub>Y</sub> + &rho;<sup>&sigma;<sub>Y</sub></sup>&frasl;<sub>&sigma;<sub>X</sub></sub>(x &minus; &mu;<sub>X</sub>), "
                "&nbsp;&sigma;<sub>Y</sub>&radic;(1 &minus; &rho;<sup>2</sup>))</div>"
                "La media condicionada es una recta en x, la recta de regresión, y la varianza condicionada no depende "
                "de x: conocer al padre reduce la incertidumbre sobre el hijo en el factor &radic;(1 &minus; &rho;<sup>2</sup>)."
            )

        if ui.accordion_step("P2_B", "(B) Por qué hay regresión"):
            ui.content(
                f"Con desviaciones iguales, ¿cuánto mide de media el hijo de un padre de {v['father']} cm? ¿Por qué queda "
                "entre la talla del padre y la media?"
            )
            ui.spoiler(
                "La media condicionada es &mu; + &rho;(x &minus; &mu;): el hijo hereda solo una fracción &rho; de la "
                "desviación del padre respecto a la media. Con 0 &lt; &rho; &lt; 1 queda siempre entre la media y el padre. "
                "La talla del padre combina factores que se heredan con suerte que no se hereda, y la parte de suerte "
                "no se repite en el hijo."
            )

        if ui.accordion_step("P2_C", "(C) Dos rectas, ninguna fuerza misteriosa"):
            ui.content(
                "Mira la recta naranja: la media de la talla del padre sabiendo la del hijo. ¿También regresa? ¿Significa "
                "eso que las tallas de la población se van igualando con las generaciones?"
            )
            ui.spoiler(
                "Sí: los padres de hijos muy altos son, de media, menos altos que sus hijos. Las dos rectas de regresión "
                "no son inversas una de otra y ninguna es la diagonal. Pero la población no se iguala: las dos "
                "marginales tienen la misma desviación. La regresión hacia la media es una consecuencia de que "
                "&rho; &lt; 1, no una fuerza. Ignorarla lleva a errores frecuentes, como atribuir a un castigo la mejora de "
                "quien acaba de tener un día excepcionalmente malo."
            )

    with col_right:
        ui.right_panel()
        cond_mean = MU_H + rho * (father - MU_H)
        cond_sd = SD_H * np.sqrt(1 - rho ** 2)
        ui.metrics([(f"&#120124;[hijo | padre = {father}] = {cond_mean:.1f} cm", "metric-a"),
                    (f"&sigma; condicionada = {cond_sd:.2f} cm", "metric-c")])
        ui.show(galton_chart(dark, father, rho), key="fig_galton_cond")
        ui.show(regression_chart(dark, rho, v["seed"]), key="fig_galton_lines")
        ui.footer_bar(f"El padre se aparta {father - MU_H:+.0f} cm de la media; su hijo, de media, {cond_mean - MU_H:+.1f} cm.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>construcción</u> de Y a partir de X")
        ui.choice_buttons(list(BUILDS), "build", labels=BUILDS, per_row=2)

        ui.planteamiento()
        ui.statement(
            "<b>Dos normales que no forman una normal</b><br><br>"
            "Sea X una normal típica. Construimos Y de dos maneras. Con <i>signo al azar</i>, Y = S&middot;X, donde S "
            "vale 1 o &minus;1 con probabilidad 1/2, independiente de X. Con <i>reflejar las colas</i>, Y = X si "
            f"|X| &le; c e Y = &minus;X si |X| &gt; c, con c &asymp; {CUT}. En los dos casos, ¿qué distribución tiene Y? "
            "¿Están correladas? ¿Son independientes?"
        )

        if ui.accordion_step("P3_A", "(A) Las marginales"):
            ui.content("Calcula &#8473;(Y &le; y) en cada construcción. Usa la simetría de la normal.")
            ui.spoiler(
                "Como &minus;X tiene la misma distribución que X, cambiarle el signo a X, al azar o según su tamaño, no "
                "altera la distribución: en los dos casos Y es normal típica. Las dos marginales son normales."
            )

        if ui.accordion_step("P3_B", "(B) Incorreladas pero dependientes"):
            ui.content(
                "Calcula Cov(X, Y) en la primera construcción. ¿Son X e Y independientes? Mira la nube de puntos."
            )
            ui.spoiler(
                "Cov(X, SX) = &#120124;[S]&#120124;[X<sup>2</sup>] = 0&middot;1 = 0: incorreladas. Pero |Y| = |X| siempre, así que "
                "conocer X determina Y salvo el signo: son muy dependientes. Los puntos viven en las dos diagonales. "
                "En la segunda construcción, el valor de c se elige precisamente para que la covarianza se anule."
            )

        if ui.accordion_step("P3_C", "(C) Lo que se pierde"):
            ui.content(
                "En una normal bidimensional, &rho; = 0 implica independencia. ¿Por qué no se aplica aquí? ¿Es normal "
                "X + Y?"
            )
            ui.spoiler(
                "Porque (X, Y) no es normal bidimensional, aunque cada componente lo sea: tener marginales normales no "
                "basta. En una normal bidimensional con &rho; = 0 la densidad factoriza en el producto de marginales, y "
                "de ahí la independencia; aquí no hay densidad conjunta en el plano. Y la suma lo delata: con signo "
                "al azar, X + Y vale exactamente 0 la mitad de las veces, un pico imposible para una normal. Muchos "
                "resultados de estadística piden normalidad <i>conjunta</i>, no solo de cada variable."
            )

    with col_right:
        ui.right_panel()
        x, y = build_pair(st.session_state["build"], 20000, v["seed"])
        ui.metrics([(f"Correlación: {np.corrcoef(x, y)[0, 1]:+.3f}", "metric-a"),
                    (f"Correlación de |X| y |Y|: {np.corrcoef(np.abs(x), np.abs(y))[0, 1]:+.3f}", "metric-c")])
        p, q = pair_charts(dark, x, y)
        ui.show(p, key="fig_pair")
        ui.show(q, key="fig_pair_sum")
        ui.footer_bar("Arriba, la nube de (X, Y): dos normales sin forma de elipse. Abajo, la suma X + Y frente a la "
                      "normal que tendría si el vector fuera normal bidimensional.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los errores de Bravais", "P1_A"),
        ("P2", "(II) La regresión hacia la media", "P2_A"),
        ("P3", "(III) Dos normales sin normal", "P3_A"),
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
