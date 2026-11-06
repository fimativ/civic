#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 2: transformaciones de vectores aleatorios.

El método de Box y Muller (dos uniformes se convierten en dos normales
independientes mediante un cambio de variable), la ley de Newcomb y Benford
(la primera cifra de un producto de variables) y el faro de Cauchy (una
distribución sin media).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Transformaciones"
SYMBOL = "g(X)"
PAGE = "05_02"

SOURCES = {"product": "Productos de factores al azar", "uniform": "Uniformes entre 1 y 999",
           "lognormal": "Poblaciones de municipios (modelo)"}


def initial_values():
    return {
        "factors": ui.dint(6, 2, 12, "factors"),
        "source": ui.dchoice("product", list(SOURCES), "source"),
        "spread": ui.dchoice(1.0, [0.5, 1.0, 2.0], "spread"),
        "seed": int(ui.r("transform") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "source": None, "bm_round": 0, "benford_round": 0,
                   "cauchy_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def box_muller(n: int, seed: int):
    rng = np.random.default_rng(seed)
    u1, u2 = rng.uniform(1e-12, 1, n), rng.uniform(0, 1, n)
    r = np.sqrt(-2 * np.log(u1))
    theta = 2 * np.pi * u2
    return u1, u2, r * np.cos(theta), r * np.sin(theta)


def first_digit(x):
    x = np.abs(x[x > 0])
    return (x / 10 ** np.floor(np.log10(x))).astype(int)


def benford_sample(source: str, factors: int, seed: int, n: int = 20000):
    rng = np.random.default_rng(seed)
    if source == "product":
        return rng.uniform(1, 10, (n, factors)).prod(axis=1)
    if source == "uniform":
        return rng.uniform(1, 999, n)
    return rng.lognormal(8, 1.6, n)


def lighthouse(n: int, spread: float, seed: int):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-np.pi / 2, np.pi / 2, n)
    return spread * np.tan(theta)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def bm_charts(dark, u1, u2, x, y):
    show = 1500
    p = ui.new_figure(dark, height=240, x_axis_label="U₁", y_axis_label="U₂", x_range=(0, 1), y_range=(0, 1),
                      match_aspect=True)
    p.scatter(u1[:show], u2[:show], size=3, color=ui.GREY_LINE, alpha=0.6)
    q = ui.new_figure(dark, height=300, x_axis_label="X", y_axis_label="Y", x_range=(-4, 4), y_range=(-4, 4),
                      match_aspect=True)
    q.scatter(x[:show], y[:show], size=3, color=ui.BLUE_LINE, alpha=0.6)
    for rad in (1, 2, 3):
        q.circle(x=[0], y=[0], radius=rad, fill_alpha=0, line_color=ui.UBU_RED, line_dash="dotted", line_width=1.5)
    xs = np.linspace(-4, 4, 300)
    edges = np.linspace(-4, 4, 33)
    hist, _ = np.histogram(x, bins=edges)
    h = ui.new_figure(dark, height=200, x_axis_label="X", y_axis_label="densidad", x_range=(-4, 4))
    h.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(x) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None)
    h.line(xs, stats.norm.pdf(xs), line_width=4, color=ui.BLUE_LINE)
    return p, q, h


def benford_chart(dark, digits):
    ds = np.arange(1, 10)
    freq = np.array([(digits == d).mean() for d in ds])
    p = ui.new_figure(dark, height=300, x_axis_label="primera cifra", y_axis_label="frecuencia", x_range=(0.4, 9.6),
                      y_range=(0, max(0.35, freq.max() * 1.15)))
    p.vbar(x=ds, top=freq, width=0.7, color=ui.BLUE_LINE, alpha=0.8, legend_label="datos simulados")
    p.scatter(ds, np.log10(1 + 1 / ds), size=14, marker="diamond", color=ui.UBU_RED, legend_label="log₁₀(1 + 1/d)")
    p.xaxis.ticker = list(ds)
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


def running_chart(dark, sample, spread):
    n = np.arange(1, len(sample) + 1)
    normal = np.random.default_rng(len(sample)).normal(0, spread, len(sample))
    p = ui.new_figure(dark, height=300, x_axis_type="log", x_axis_label="destellos observados",
                      y_axis_label="estimación de la posición", y_range=(-6 * spread, 6 * spread))
    p.line(n, np.cumsum(sample) / n, line_width=3, color=ui.RED_LINE, legend_label="media (Cauchy)")
    medians = np.array([np.median(sample[:k]) for k in n[::25]])
    p.line(n[::25], medians, line_width=3, color=ui.GREEN_LINE, legend_label="mediana (Cauchy)")
    p.line(n, np.cumsum(normal) / n, line_width=2, color=ui.GREY_LINE, line_dash="dashed", legend_label="media (normal)")
    p.add_layout(Span(location=0, dimension="width", line_color=ui.BLUE_LINE, line_dash="dotted", line_width=2))
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué distribución tiene una función de un vector aleatorio?</b>")
        ui.content(
            "Si (X<sub>1</sub>, &hellip;, X<sub>k</sub>) es un vector aleatorio y g una función razonable, "
            "Y = g(X<sub>1</sub>, &hellip;, X<sub>k</sub>) es otro vector aleatorio. En el caso discreto basta sumar "
            "las probabilidades de los puntos que van a parar al mismo valor. En el caso continuo, si g es "
            "invertible con derivadas continuas, la densidad se transforma con el determinante jacobiano de la "
            "inversa. <i>Escribe la fórmula del cambio de variable.</i>"
        )
        ui.formula_hidden("h(y) = f(g<sup>&minus;1</sup>(y))&middot;|J|, &nbsp; J = det(&part;g<sup>&minus;1</sup>/&part;y)")
        ui.content(
            "Para calcular solo la esperanza de g no hace falta la distribución de Y: basta integrar g contra la "
            "densidad conjunta, como en el caso de una variable."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El método de Box y Muller (1958)</b><br>"
            "<i>Convierte con George Box y Mervin Muller dos números uniformes en dos normales "
            "independientes.</i><br><br>"
            "<b>II. La primera cifra (1881)</b><br>"
            "<i>¿Por qué los libros de logaritmos que consultaba Simon Newcomb estaban más gastados al principio? Una "
            "transformación lo explica.</i><br><br>"
            "<b>III. El faro de Cauchy (1853)</b><br>"
            "<i>Un faro gira al azar frente a la costa: la posición de sus destellos no tiene media.</i>"
        )


def render_problem_1(dark):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>El método de Box y Muller (1958)</b><br><br>"
            "Para simular una normal con el método de la inversa haría falta invertir &Phi;, que no tiene expresión "
            "cerrada. George Box y Mervin Muller encontraron un atajo: tomar dos uniformes independientes "
            "U<sub>1</sub>, U<sub>2</sub> en (0, 1) y transformarlas en"
            "<div class='formula-box plain'>X = &radic;(&minus;2 ln U<sub>1</sub>)&middot;cos(2&pi;U<sub>2</sub>), &nbsp; "
            "Y = &radic;(&minus;2 ln U<sub>1</sub>)&middot;sen(2&pi;U<sub>2</sub>)</div>"
            "¿Por qué X e Y resultan ser dos normales típicas independientes?"
        )

        if ui.accordion_step("P1_A", "(A) La normal en coordenadas polares"):
            ui.content(
                "Escribe la densidad conjunta de dos normales típicas independientes y pásala a polares, x = r cos&theta;, "
                "y = r sen&theta;. ¿Cuánto vale el jacobiano? ¿Qué se observa en la densidad resultante?"
            )
            ui.spoiler(
                "<div class='formula-box'>f(x, y) = <sup>1</sup>&frasl;<sub>2&pi;</sub> e<sup>&minus;(x<sup>2</sup> + y<sup>2</sup>)/2</sup> "
                "&nbsp;&rArr;&nbsp; h(r, &theta;) = <sup>1</sup>&frasl;<sub>2&pi;</sub> e<sup>&minus;r<sup>2</sup>/2</sup>&middot;r</div>"
                "El jacobiano de las polares es r. La densidad factoriza en una función de r por una constante en "
                "&theta;: el radio y el ángulo son independientes, el ángulo es uniforme en [0, 2&pi;) y el radio "
                "tiene densidad r e<sup>&minus;r<sup>2</sup>/2</sup>."
            )

        if ui.accordion_step("P1_B", "(B) Fabricar el radio y el ángulo"):
            ui.content(
                "Calcula &#8473;(R &gt; r) para ese radio y comprueba que R = &radic;(&minus;2 ln U<sub>1</sub>) tiene esa "
                "distribución. ¿Y el ángulo 2&pi;U<sub>2</sub>?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(R &gt; r) = e<sup>&minus;r<sup>2</sup>/2</sup> = &#8473;(&radic;(&minus;2 ln U<sub>1</sub>) &gt; r)</div>"
                "porque &radic;(&minus;2 ln U) &gt; r si y solo si U &lt; e<sup>&minus;r<sup>2</sup>/2</sup>. Es el método de la "
                "inversa aplicado al radio. El ángulo 2&pi;U<sub>2</sub> es uniforme en [0, 2&pi;), y al venir de "
                "uniformes independientes, radio y ángulo son independientes."
            )

        if ui.accordion_step("P1_C", "(C) De vuelta a cartesianas"):
            ui.content(
                "Con el radio y el ángulo correctos, deshaz el cambio a polares. ¿Por qué X e Y salen independientes, "
                "si las dos se fabrican con el mismo radio?"
            )
            ui.spoiler(
                "Como el par (R, &Theta;) tiene exactamente la distribución de las polares de dos normales típicas "
                "independientes, al volver a cartesianas se recupera la densidad conjunta e<sup>&minus;(x<sup>2</sup>+y<sup>2</sup>)/2</sup>/(2&pi;), "
                "que factoriza: X e Y son independientes aunque compartan R. A la derecha, los puntos forman una nube "
                "redonda, sin dirección privilegiada, y el histograma de X es la campana."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otras 20 000 parejas", key="bm_new", width="stretch"):
            st.session_state["bm_round"] += 1
        u1, u2, x, y = box_muller(20000, 1234 + st.session_state["bm_round"])
        ui.metrics([(f"Media y varianza de X: {x.mean():+.3f}, {x.var():.3f}", "metric-a"),
                    (f"Correlación de X e Y: {np.corrcoef(x, y)[0, 1]:+.3f}", "metric-c")])
        p, q, h = bm_charts(dark, u1, u2, x, y)
        ui.show(p, key="fig_bm_u")
        ui.show(q, key="fig_bm_xy")
        ui.show(h, key="fig_bm_hist")
        ui.footer_bar("Arriba, las parejas de uniformes; en medio, las mismas parejas transformadas, con círculos de "
                      "radio 1, 2 y 3; abajo, el histograma de X frente a la densidad normal típica.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>origen de los números</u> y el <u>número de factores</u>")
        if st.session_state["source"] is None:
            st.session_state["source"] = v["source"]
        ui.choice_buttons(list(SOURCES), "source", labels=SOURCES, per_row=3)
        factors = st.slider("Factores multiplicados", 1, 15, v["factors"], 1, key=ui.wkey(PAGE, "factors"))

        ui.planteamiento()
        ui.statement(
            "<b>La primera cifra (1881)</b><br><br>"
            "El astrónomo Simon Newcomb notó que las primeras páginas de los libros de logaritmos, las de los "
            "números que empiezan por 1, estaban mucho más gastadas que las últimas. Lo publicó en 1881 y nadie le "
            "hizo caso; en 1938 el físico Frank Benford lo redescubrió con miles de datos: superficies de ríos, "
            "constantes físicas, direcciones postales. La primera cifra significativa no es uniforme: el 1 aparece "
            "algo más del 30 % de las veces y el 9, menos del 5 %."
        )

        if ui.accordion_step("P2_A", "(A) La primera cifra como transformación"):
            ui.content(
                "La primera cifra de X depende solo de la parte fraccionaria U de log<sub>10</sub> X. Si U fuera "
                "uniforme en [0, 1), ¿con qué probabilidad sería d la primera cifra?"
            )
            ui.spoiler(
                "La primera cifra es d exactamente cuando log<sub>10</sub> d &le; U &lt; log<sub>10</sub>(d + 1). Con U "
                "uniforme:"
                "<div class='formula-box'>&#8473;(D = d) = log<sub>10</sub>(d + 1) &minus; log<sub>10</sub> d = "
                "log<sub>10</sub>(1 + 1/d)</div>"
                "Es la ley de Benford: un 30.1 % para el 1, un 17.6 % para el 2&hellip; y un 4.6 % para el 9."
            )

        if ui.accordion_step("P2_B", "(B) Por qué los productos la cumplen"):
            ui.content(
                "Multiplica varios factores al azar y mira la primera cifra del producto. ¿Qué le pasa al logaritmo "
                "de un producto? ¿Por qué cuantos más factores, mejor se cumple la ley?"
            )
            ui.spoiler(
                "El logaritmo de un producto es la suma de los logaritmos. Al sumar muchas variables independientes, "
                "la suma se extiende sobre muchas unidades, y su parte fraccionaria se reparte casi uniformemente "
                "en [0, 1): es lo que exige el apartado anterior. Muchas magnitudes reales, como las poblaciones o "
                "las cuentas de una empresa, crecen multiplicativamente, y por eso cumplen la ley. Los números "
                "uniformes entre 1 y 999, en cambio, no la cumplen."
            )

        if ui.accordion_step("P2_C", "(C) Cazar cuentas falsas"):
            ui.content(
                "En los años noventa, el contable Mark Nigrini empezó a usar la ley de Benford para detectar fraudes. "
                "¿Por qué crees que funciona? ¿Qué datos no deberían cumplirla aunque sean honestos?"
            )
            ui.spoiler(
                "Quien inventa cifras tiende a repartir las primeras cifras de forma bastante uniforme, porque cree "
                "que eso parece azar; las cuentas reales, producto de muchos factores, siguen la ley. Una desviación "
                "fuerte es una señal para mirar más de cerca, no una prueba. No deben cumplirla los datos acotados "
                "o asignados: alturas de personas, números de teléfono o precios fijados en 9.99."
            )

    with col_right:
        ui.right_panel()
        source = st.session_state["source"]
        if st.button("Otros 20 000 números", key="benford_new", width="stretch"):
            st.session_state["benford_round"] += 1
        sample = benford_sample(source, factors, v["seed"] + st.session_state["benford_round"])
        digits = first_digit(sample)
        dev = np.abs(np.array([(digits == d).mean() for d in range(1, 10)]) - np.log10(1 + 1 / np.arange(1, 10))).sum()
        ui.metrics([(f"Frecuencia del 1: {(digits == 1).mean():.3f}", "metric-a"),
                    (f"Desviación total de Benford: {dev:.3f}", "metric-c")])
        ui.show(benford_chart(dark, digits), key="fig_benford")
        ui.footer_bar(f"Datos: {SOURCES[source].lower()}. Los rombos rojos marcan la ley de Benford.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>distancia del faro a la costa</u>")
        spread = st.select_slider("Distancia del faro a la costa (km)", options=[0.5, 1.0, 2.0, 3.0], value=v["spread"],
                                  key=ui.wkey(PAGE, "spread"))

        ui.planteamiento()
        ui.statement(
            "<b>El faro de Cauchy (1853)</b><br><br>"
            "En una polémica con Irénée-Jules Bienaymé sobre el método de los mínimos cuadrados, Augustin Cauchy "
            "presentó una distribución que desbarataba los argumentos basados en promedios. Una forma de verla: un "
            "faro está en el mar, a una distancia b de una costa recta, enfrente del punto 0. Emite destellos en "
            "direcciones al azar, con ángulo uniforme en (&minus;&pi;/2, &pi;/2), y en la costa se anota dónde "
            "llega cada destello: X = b&middot;tan &Theta;. ¿Cómo se estima la posición del faro?"
        )

        if ui.accordion_step("P3_A", "(A) La densidad de los destellos"):
            ui.content(
                "&Theta; es uniforme y X = b&middot;tan &Theta; es una transformación invertible. Calcula la densidad de X "
                "con el cambio de variable."
            )
            ui.spoiler(
                "Con &theta; = arctan(x/b), la derivada es b/(b<sup>2</sup> + x<sup>2</sup>), y la densidad de &Theta; es 1/&pi;:"
                "<div class='formula-box'>f(x) = <sup>1</sup>&frasl;<sub>&pi;</sub>&middot;<sup>b</sup>&frasl;<sub>b<sup>2</sup> + x<sup>2</sup></sub></div>"
                "Es la distribución de Cauchy. Parece una campana, pero sus colas caen solo como 1/x<sup>2</sup>, "
                "mucho más despacio que las de la normal."
            )

        if ui.accordion_step("P3_B", "(B) Una esperanza que no existe"):
            ui.content(
                "Intenta calcular &#120124;[|X|]. ¿Converge la integral? Mira a la derecha cómo evoluciona la media de "
                "los destellos al aumentar su número, comparada con la de datos normales."
            )
            ui.spoiler(
                "&int; |x| b/(&pi;(b<sup>2</sup> + x<sup>2</sup>)) dx crece como un logaritmo y diverge: la Cauchy no tiene "
                "media, y menos aún varianza. Por eso la media de los destellos no se estabiliza: de vez en cuando "
                "llega un destello casi paralelo a la costa, enorme, que la desplaza de golpe. Más aún, la media de "
                "n destellos tiene exactamente la misma distribución de Cauchy que uno solo: promediar no sirve de "
                "nada."
            )

        if ui.accordion_step("P3_C", "(C) La mediana sí funciona"):
            ui.content(
                "Mira la curva verde, la mediana de los destellos. ¿Por qué se estabiliza aunque la media no lo haga? "
                "¿Qué otra forma de obtener la Cauchy conoces?"
            )
            ui.spoiler(
                "La mediana solo depende del orden de los datos, y un destello lejanísimo pesa lo mismo que uno "
                "cercano: es robusta, como en la fuente del pueblo. La mediana de la Cauchy es la posición del faro, "
                "y la mediana muestral converge a ella. La Cauchy aparece también como cociente de dos normales "
                "típicas independientes: el cambio de variable Z = X/Y, W = Y, con jacobiano |w|, da la misma "
                "densidad con b = 1."
            )

    with col_right:
        ui.right_panel()
        if st.button("Otros 5000 destellos", key="cauchy_new", width="stretch"):
            st.session_state["cauchy_round"] += 1
        sample = lighthouse(5000, spread, v["seed"] + st.session_state["cauchy_round"])
        ui.metrics([(f"Media de los destellos: {sample.mean():+.3f}", "result-no"),
                    (f"Mediana: {np.median(sample):+.3f}", "result-yes")])
        ui.show(running_chart(dark, sample, spread), key="fig_cauchy")
        ui.footer_bar(f"El faro está enfrente del 0. Destello más lejano de esta tanda: {np.abs(sample).max():,.0f} km "
                      "del punto 0 de la costa.".replace(",", " "))


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Box y Muller", "P1_A"),
        ("P2", "(II) La primera cifra", "P2_A"),
        ("P3", "(III) El faro de Cauchy", "P3_A"),
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
