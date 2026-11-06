#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 4: el estimador insesgado.

Los números de serie de los tanques alemanes (tres estimadores del total, con
y sin sesgo), el divisor de la varianza muestral (sesgo frente a error
cuadrático medio) y un caso en el que el único estimador insesgado es absurdo.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Estimador insesgado"
PAGE = "00_04"

REPS = 3000
TANK_ESTIMATORS = {"max": "máximo M", "mean": "2X̄ − 1", "umvu": "M(1 + 1/k) − 1"}


def initial_values():
    return {
        "N": 10 * round(ui.dint(300, 100, 900, "N") / 10),
        "k": ui.dint(5, 2, 20, "k"),
        "n_var": ui.dint(10, 2, 40, "n_var"),
        "lam": round(20 * ui.dfloat(0.70, 0.10, 2.50, "lam")) / 20,
        "seed": int(ui.r("insesgado") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def tank_samples(N: int, k: int, rng):
    """REPS muestras sin reemplazamiento de k números de serie entre 1 y N."""
    return np.argsort(rng.random((REPS, N)), axis=1)[:, :k] + 1


def tank_estimates(s: np.ndarray, k: int):
    m = s.max(axis=1)
    return {"max": m, "mean": 2 * s.mean(axis=1) - 1, "umvu": m * (1 + 1 / k) - 1}


def divisor_mse(n: np.ndarray, c: np.ndarray):
    """Sesgo y ECM de SS/c como estimador de σ² = 1 en una normal (SS ~ χ² con n − 1 g.l.)."""
    bias = (n - 1) / c - 1
    var = 2 * (n - 1) / c ** 2
    return bias, var, var + bias ** 2


# =============================================================================
# 2. FIGURAS
# =============================================================================

def tank_chart(dark, est, N):
    vals = np.concatenate(list(est.values()))
    edges = np.linspace(np.percentile(vals, 0.5), np.percentile(vals, 99.5), 50)
    p = ui.new_figure(dark, height=320, x_axis_label="estimación del número total de tanques", y_axis_label="densidad")
    centres = (edges[:-1] + edges[1:]) / 2
    for (name, e), colour in zip(est.items(), (ui.ORANGE_LINE, ui.BLUE_LINE, ui.GREEN_LINE)):
        h, _ = np.histogram(e, bins=edges)
        p.line(centres, h / (len(e) * (edges[1] - edges[0])), line_width=3, color=colour,
               legend_label=TANK_ESTIMATORS[name])
    p.add_layout(Span(location=N, dimension="height", line_color=ui.UBU_RED, line_width=2))
    return ui.style_legend(p, dark, "top_left")


def divisor_chart(dark, n_now):
    n = np.arange(2, 41)
    p = ui.new_figure(dark, height=300, x_axis_label="tamaño de la muestra n", y_axis_label="error cuadrático medio / σ⁴",
                      y_axis_type="log")
    for shift, label, colour in ((-1, "divisor n − 1", ui.BLUE_LINE), (0, "divisor n", ui.GREEN_LINE),
                                 (1, "divisor n + 1", ui.ORANGE_LINE)):
        _, _, mse = divisor_mse(n, n + shift)
        p.line(n, mse, line_width=3, color=colour, legend_label=label)
    p.add_layout(Span(location=n_now, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed"))
    return ui.style_legend(p, dark, "top_right")


def poisson_chart(dark, lam):
    lams = np.linspace(0.02, 3, 200)
    p = ui.new_figure(dark, height=300, x_axis_label="λ (llamadas por minuto)", y_axis_label="error cuadrático medio")
    mse_unb = 1 - np.exp(-4 * lams)
    mse_mle = np.exp(lams * (np.exp(-4) - 1)) - 2 * np.exp(-2 * lams) * np.exp(lams * (np.exp(-2) - 1)) + np.exp(-4 * lams)
    p.line(lams, mse_unb, line_width=3, color=ui.ORANGE_LINE, legend_label="(−1)ˣ, insesgado")
    p.line(lams, mse_mle, line_width=3, color=ui.BLUE_LINE, legend_label="e⁻²ˣ, sesgado")
    p.add_layout(Span(location=lam, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed"))
    return ui.style_legend(p, dark, "center_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Acierta un estimador en promedio?</b>")
        ui.content(
            "Un <b>estimador</b> de un parámetro &theta; es un estadístico T que usamos para aproximarlo. Su "
            "<b>sesgo</b> es la diferencia entre lo que vale en promedio y lo que quiere estimar, y el estimador es "
            "<b>insesgado</b> si esa diferencia es cero para todos los valores posibles de &theta;. <i>¿Cómo se "
            "escriben el sesgo y el error cuadrático medio?</i>"
        )
        ui.formula_hidden("b(&theta;) = E<sub>&theta;</sub>[T] &minus; &theta; &nbsp;&nbsp; ECM(T) = E<sub>&theta;</sub>[(T &minus; &theta;)<sup>2</sup>] "
                          "= &#120141;<sub>&theta;</sub>(T) + b(&theta;)<sup>2</sup>")
        ui.content(
            "El error cuadrático medio reparte el error en dos partes: la dispersión y el sesgo. Ser insesgado es una "
            "virtud, pero no la única. Las tres situaciones muestran estimadores insesgados mejores y peores, uno "
            "sesgado que gana a uno insesgado, y un insesgado que no tiene sentido."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los tanques alemanes (1943)</b><br>"
            "<i>Estima cuántos tanques fabrica el enemigo a partir de los números de serie de los capturados, como los "
            "estadísticos aliados.</i><br><br>"
            "<b>II. La corrección de Bessel</b><br>"
            "<i>Divide la suma de cuadrados entre n &minus; 1, n o n + 1 y decide qué importa más, el sesgo o el "
            "error.</i><br><br>"
            "<b>III. Un insesgado absurdo</b><br>"
            "<i>Estima la probabilidad de que una centralita no reciba llamadas, y descubre el único estimador "
            "insesgado posible.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>total real N</u> y los <u>tanques capturados k</u>")
        N = st.slider("Tanques fabricados N", 50, 1000, v["N"], 10, key=ui.wkey(PAGE, "N"))
        k = st.slider("Tanques capturados k", 2, 30, v["k"], 1, key=ui.wkey(PAGE, "k"))

        ui.planteamiento()
        ui.statement(
            "<b>Los tanques alemanes (1943)</b><br><br>"
            "Durante la Segunda Guerra Mundial, los estadísticos aliados estimaron la producción alemana de tanques a "
            "partir de los números de serie de las piezas de los vehículos capturados. Tras la guerra, los registros de "
            "las fábricas mostraron que sus estimaciones habían sido mucho más precisas que las de los servicios de "
            "inteligencia. Si los números van de 1 a N y se capturan k tanques al azar, ¿cómo estimar N?"
        )

        if ui.accordion_step("P1_A", "(A) El máximo"):
            ui.content(
                "El número más alto capturado, M, nunca puede pasar de N. ¿Tiene sesgo? Calcula su esperanza contando las "
                "muestras en las que el máximo vale m."
            )
            ui.spoiler(
                "&#8473;(M = m) = C(m &minus; 1, k &minus; 1)/C(N, k), y sumando con la identidad del palo de hockey:"
                "<div class='formula-box'>E[M] = <sup>k(N + 1)</sup>&frasl;<sub>k + 1</sub> &lt; N</div>"
                "El máximo subestima siempre: tiene un sesgo negativo. La curva naranja queda a la izquierda de la línea "
                "roja."
            )

        if ui.accordion_step("P1_B", "(B) Dos correcciones insesgadas"):
            ui.content(
                "Despeja N de la esperanza del máximo y de la esperanza de la media muestral X̄. ¿Qué dos estimadores "
                "insesgados salen?"
            )
            ui.spoiler(
                "De E[M] sale M(1 + 1/k) &minus; 1: el máximo más el hueco medio entre dos números capturados. De "
                "E[X̄] = (N + 1)/2, por linealidad, sale 2X̄ &minus; 1. Los dos son insesgados, pero el primero tiene "
                "mucha menos varianza: aprovecha mejor la información, porque el máximo es suficiente para N."
            )

        if ui.accordion_step("P1_C", "(C) El que gana"):
            ui.content("Compara los errores cuadráticos medios de la derecha. ¿Basta con ser insesgado? ¿Gana siempre un insesgado a uno sesgado?")
            ui.spoiler(
                "No basta: 2X̄ &minus; 1 es insesgado y aun así tiene más error cuadrático medio que el máximo sin corregir. "
                "Entre los insesgados, M(1 + 1/k) &minus; 1 tiene la menor varianza posible: es el estimador insesgado de "
                "varianza uniformemente mínima, como garantizan los teoremas de Rao-Blackwell y Lehmann-Scheffé."
            )

    with col_right:
        ui.right_panel()
        k = min(k, N)
        rng = np.random.default_rng(v["seed"] + N * 37 + k)
        est = tank_estimates(tank_samples(N, k, rng), k)
        rows = [(f"{TANK_ESTIMATORS[name]}: sesgo {e.mean() - N:+.0f}, ECM {ui.fmt_int(np.mean((e - N) ** 2))}",
                 cls) for (name, e), cls in zip(est.items(), ("metric-c", "metric-a", "metric-b"))]
        ui.metrics(rows)
        ui.show(tank_chart(dark, est, N), key="fig_tanks")
        ui.footer_bar(f"{REPS} capturas simuladas de {k} tanques entre {ui.fmt_int(N)}. La línea roja marca el total real. "
                      f"La esperanza del máximo es k(N + 1)/(k + 1) = {k * (N + 1) / (k + 1):.1f}.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra n</u>")
        n = st.slider("Tamaño de la muestra", 2, 40, v["n_var"], 1, key=ui.wkey(PAGE, "n_var"),
                      label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La corrección de Bessel</b><br><br>"
            "La varianza muestral divide la suma de cuadrados SS = &sum;(X<sub>i</sub> &minus; X̄)<sup>2</sup> entre "
            "n &minus; 1, y no entre n; el cambio se llama corrección de Bessel, por el astrónomo Friedrich Bessel, que "
            "estudió los errores de observación. Comparamos los tres divisores n &minus; 1, n y n + 1 en una población "
            "normal."
        )

        if ui.accordion_step("P2_A", "(A) El sesgo"):
            ui.content("Usa que E[SS] = (n &minus; 1)&sigma;<sup>2</sup>. ¿Cuál es el sesgo de SS/c para cada divisor c?")
            ui.spoiler(
                "E[SS/c] = (n &minus; 1)&sigma;<sup>2</sup>/c, así que solo c = n &minus; 1 da un estimador insesgado. "
                "Con c = n el sesgo es &minus;&sigma;<sup>2</sup>/n: se subestima, porque los residuos se miden respecto a "
                "X̄, que está más cerca de los datos que la verdadera &mu;."
            )

        if ui.accordion_step("P2_B", "(B) El error cuadrático medio"):
            ui.content(
                "En la normal, SS/&sigma;<sup>2</sup> es una ji cuadrado con n &minus; 1 grados de libertad, de varianza "
                "2(n &minus; 1). Calcula el error cuadrático medio de SS/c. ¿Qué divisor lo minimiza?"
            )
            ui.spoiler(
                "<div class='formula-box'>ECM(SS/c) = &sigma;<sup>4</sup>[ <sup>2(n &minus; 1)</sup>&frasl;<sub>c<sup>2</sup></sub> + "
                "( <sup>n &minus; 1</sup>&frasl;<sub>c</sub> &minus; 1 )<sup>2</sup> ]</div>"
                "Derivando respecto a c, el mínimo está en c = n + 1. El divisor n + 1 introduce más sesgo, pero reduce la "
                "varianza lo suficiente para ganar. Un poco de sesgo puede compensar."
            )

        if ui.accordion_step("P2_C", "(C) Y la desviación típica"):
            ui.content("Si S<sup>2</sup> es insesgado para &sigma;<sup>2</sup>, ¿lo es S para &sigma;?")
            ui.spoiler(
                "No. La raíz es una función cóncava, y por la desigualdad de Jensen E[S] &le; &radic;E[S<sup>2</sup>] = "
                "&sigma;, con igualdad solo si S es constante. La insesgadez no se conserva al transformar el estimador. "
                "Con n = 10, por ejemplo, E[S] es aproximadamente 0.973&sigma;."
            )

    with col_right:
        ui.right_panel()
        rows = []
        for c, label, cls in ((n - 1, "n − 1", "metric-a"), (n, "n", "metric-b"), (n + 1, "n + 1", "metric-c")):
            bias, _, mse = divisor_mse(np.array(n), np.array(c))
            rows.append((f"Divisor {label}: sesgo {float(bias):+.3f}, ECM {float(mse):.3f}", cls))
        ui.metrics(rows)
        rng = np.random.default_rng(v["seed"] + n)
        x = rng.standard_normal((REPS, n))
        ss = ((x - x.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
        ui.show(divisor_chart(dark, n), key="fig_divisor")
        ui.footer_bar(f"Valores en unidades de &sigma;<sup>2</sup> = 1. Con {REPS} muestras simuladas de tamaño {n}, el "
                      f"ECM del divisor n &minus; 1 es {np.mean((ss / (n - 1) - 1) ** 2):.3f} y el de n + 1, "
                      f"{np.mean((ss / (n + 1) - 1) ** 2):.3f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>intensidad de llamadas λ</u>")
        lam = st.slider("Llamadas por minuto λ", 0.1, 3.0, v["lam"], 0.05, key=ui.wkey(PAGE, "lam"),
                        label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Un insesgado absurdo</b><br><br>"
            "En 1909 el ingeniero danés Agner Erlang mostró que las llamadas que llegan a una centralita telefónica en un "
            "minuto siguen una distribución de Poisson de parámetro &lambda;. Contamos las llamadas X de un solo minuto y "
            "queremos estimar la probabilidad de que la centralita pase dos minutos seguidos sin ninguna, que vale "
            "e<sup>&minus;2&lambda;</sup>."
        )

        if ui.accordion_step("P3_A", "(A) Buscar un estimador insesgado"):
            ui.content(
                "Un estimador es una función T(X). Escribe E[T(X)] como serie de potencias de &lambda; e iguálala a "
                "e<sup>&minus;2&lambda;</sup> para todo &lambda;. ¿Qué T sale?"
            )
            ui.spoiler(
                "E[T(X)] = e<sup>&minus;&lambda;</sup>&sum; T(x)&lambda;<sup>x</sup>/x! debe ser e<sup>&minus;2&lambda;</sup>, es "
                "decir, &sum; T(x)&lambda;<sup>x</sup>/x! = e<sup>&minus;&lambda;</sup> = &sum; (&minus;1)<sup>x</sup>&lambda;<sup>x</sup>/x!. "
                "Por la unicidad del desarrollo en serie de potencias, la única solución es"
                "<div class='formula-box'>T(X) = (&minus;1)<sup>X</sup></div>"
            )

        if ui.accordion_step("P3_B", "(B) Por qué es absurdo"):
            ui.content("¿Qué valores toma T? ¿Qué estima cuando la centralita recibe una sola llamada?")
            ui.spoiler(
                "Solo vale 1 o &minus;1. Con un número impar de llamadas estima una probabilidad negativa, y con uno par "
                "estima que es seguro no recibir llamadas, aunque acabe de recibir varias. En promedio acierta, y aun así "
                "cada estimación concreta es disparatada."
            )

        if ui.accordion_step("P3_C", "(C) Un sesgado razonable"):
            ui.content(
                "Compara con e<sup>&minus;2X</sup>, que sustituye &lambda; por su estimación X. ¿Tiene sesgo? ¿Qué error "
                "cuadrático medio tiene frente al insesgado?"
            )
            ui.spoiler(
                "Sí tiene sesgo, pero siempre está entre 0 y 1 y su error cuadrático medio es mucho menor para todos los "
                "valores de &lambda;: el insesgado es <b>inadmisible</b>. La lección de las tres situaciones: el sesgo es "
                "solo una parte del error, y el criterio importante es el error cuadrático medio."
            )

    with col_right:
        ui.right_panel()
        target = np.exp(-2 * lam)
        rng = np.random.default_rng(v["seed"] + int(lam * 100))
        x = rng.poisson(lam, REPS)
        t = (-1.0) ** x
        ui.metrics([(f"Objetivo e<sup>&minus;2&lambda;</sup> = {target:.3f}", "metric-c"),
                    (f"Media de (&minus;1)<sup>X</sup>: {t.mean():.3f}", "metric-a"),
                    (f"Media de e<sup>&minus;2X</sup>: {np.exp(-2 * x).mean():.3f}", "metric-b")])
        ui.show(poisson_chart(dark, lam), key="fig_poisson")
        ui.footer_bar(f"Error cuadrático medio exacto de los dos estimadores en función de &lambda;. En {REPS} minutos "
                      f"simulados, (&minus;1)<sup>X</sup> dio una estimación negativa {np.mean(t < 0) * 100:.0f} % de las veces.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los tanques alemanes", "P1_A"),
        ("P2", "(II) La corrección de Bessel", "P2_A"),
        ("P3", "(III) Un insesgado absurdo", "P3_A"),
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
