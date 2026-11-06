#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 5: el estimador consistente.

Las cien medidas de la velocidad de la luz de Michelson (consistencia de la
media y errores sistemáticos), la media y la mediana de una muestra de Cauchy
(la ley de los grandes números necesita esperanza) y la paradoja de Neyman y
Scott (un máximo verosímil que no es consistente).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Estimador consistente"
PAGE = "00_05"

C_TRUE = 299734.5            # km/s, valor actual en sus condiciones (en aire), según Stigler (1977)
MICHELSON_MEAN = 299852.4    # media de sus 100 medidas de 1879
MICHELSON_SD = 79.0
MAX_N = 5000
PATHS = 6
LAWS = {"normal": "Normal", "cauchy": "Cauchy"}


def initial_values():
    return {
        "n": ui.dchoice(100, [10, 25, 100, 400, 1600], "n"),
        "eps": ui.dfloat(20.0, 5.0, 40.0, "eps", 0),
        "law": ui.dchoice("cauchy", list(LAWS), "law"),
        "patients": ui.dchoice(500, [10, 50, 200, 500, 2000], "patients"),
        "seed": int(ui.r("consistente") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "law": None, "draws": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def running(x: np.ndarray) -> np.ndarray:
    """Medias acumuladas por filas."""
    return np.cumsum(x, axis=1) / np.arange(1, x.shape[1] + 1)


def running_median(x: np.ndarray, checkpoints: np.ndarray) -> np.ndarray:
    return np.array([np.median(x[:, :m], axis=1) for m in checkpoints]).T


def neyman_scott(m: int, sigma: float, rng):
    """Dos medidas por paciente con media propia; devuelve los dos estimadores acumulados."""
    mu = rng.normal(120, 15, m)
    x = mu[:, None] + rng.normal(0, sigma, (m, 2))
    d2 = (x[:, 0] - x[:, 1]) ** 2
    k = np.arange(1, m + 1)
    return np.cumsum(d2) / (4 * k), np.cumsum(d2) / (2 * k)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def probability_chart(dark, eps, n_now):
    n = np.unique(np.geomspace(2, 4000, 120).astype(int))
    exact = 2 * stats.norm.sf(eps * np.sqrt(n) / MICHELSON_SD)
    cheb = np.minimum(1, MICHELSON_SD ** 2 / (n * eps ** 2))
    p = ui.new_figure(dark, height=280, x_axis_label="número de medidas n", y_axis_label="ℙ(|X̄ − μ| > ε)",
                      x_axis_type="log", y_range=(0, 1.02))
    p.line(n, cheb, line_width=3, color=ui.ORANGE_LINE, legend_label="cota de Chebyshev")
    p.line(n, exact, line_width=3, color=ui.BLUE_LINE, legend_label="valor exacto (normal)")
    p.add_layout(Span(location=n_now, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed"))
    return ui.style_legend(p, dark, "top_right")


def paths_chart(dark, paths, n_now, target, label, y_range, extra=None, x_label="número de observaciones"):
    n = np.arange(1, paths.shape[1] + 1)
    p = ui.new_figure(dark, height=300, x_axis_label=x_label, y_axis_label=label,
                      x_axis_type="log", y_range=y_range)
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.GREY_LINE, ui.UBU_RED]
    for row, colour in zip(paths, palette):
        p.line(n, row, line_width=1.8, color=colour, alpha=0.85)
    p.add_layout(Span(location=target, dimension="width", line_color=ui.UBU_RED, line_width=2.5))
    if extra is not None:
        p.add_layout(Span(location=extra, dimension="width", line_color=ui.GREY_LINE, line_width=2, line_dash="dashed"))
    p.add_layout(Span(location=n_now, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted"))
    return p


def median_chart(dark, checkpoints, medians):
    p = ui.new_figure(dark, height=240, x_axis_label="número de observaciones", y_axis_label="mediana muestral",
                      x_axis_type="log", y_range=(-3, 3))
    palette = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.GREY_LINE, ui.UBU_RED]
    for row, colour in zip(medians, palette):
        p.line(checkpoints, row, line_width=1.8, color=colour, alpha=0.85)
    p.add_layout(Span(location=0, dimension="width", line_color=ui.UBU_RED, line_width=2.5))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Mejora un estimador con más datos?</b>")
        ui.content(
            "Un estimador T<sub>n</sub>, calculado con n observaciones, es <b>consistente</b> para &theta; si se acerca "
            "a &theta; en probabilidad cuando n crece: la probabilidad de equivocarse en más de una cantidad fija tiende a "
            "cero, por pequeña que sea esa cantidad. <i>¿Cómo se escribe?</i>"
        )
        ui.formula_hidden("para todo &epsilon; &gt; 0: &nbsp; &#8473;( |T<sub>n</sub> &minus; &theta;| &gt; &epsilon; ) &rarr; 0")
        ui.content(
            "Insesgadez y consistencia son propiedades distintas: la primera habla del promedio con n fijo, la segunda "
            "del comportamiento cuando n crece. Hay estimadores insesgados que no son consistentes, consistentes con "
            "sesgo, y alguno de los métodos más respetados que falla en las dos."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La velocidad de la luz (1879)</b><br>"
            "<i>Promedia las medidas de Albert Michelson y comprueba que la media converge&hellip; aunque no al valor "
            "correcto.</i><br><br>"
            "<b>II. La media que no converge (1853)</b><br>"
            "<i>Revive la discusión entre Cauchy y Bienaymé con una distribución para la que la ley de los grandes "
            "números no funciona.</i><br><br>"
            "<b>III. La paradoja de Neyman y Scott (1948)</b><br>"
            "<i>Mide dos veces la tensión de muchos pacientes y descubre un estimador de máxima verosimilitud que "
            "nunca acierta.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de medidas n</u> y la <u>tolerancia &epsilon;</u>")
        n = st.select_slider("Número de medidas n", options=[10, 25, 100, 400, 1600], value=v["n"],
                             key=ui.wkey(PAGE, "n"))
        eps = st.slider("Tolerancia ε (km/s)", 5.0, 40.0, v["eps"], 1.0, key=ui.wkey(PAGE, "eps"))

        ui.planteamiento()
        ui.statement(
            "<b>La velocidad de la luz (1879)</b><br><br>"
            "En la Academia Naval de Annapolis, Albert Michelson midió la velocidad de la luz con espejos giratorios. Hizo "
            "cien medidas en aire, con una dispersión de unos 80 km/s, y calculó su media. Modelamos cada medida como una normal "
            "de media &mu; y desviación &sigma; &asymp; 80 km/s, y estimamos &mu; con la media muestral X̄<sub>n</sub>."
        )

        if ui.accordion_step("P1_A", "(A) Una condición suficiente"):
            ui.content(
                "Aplica la desigualdad de Chebyshev a X̄<sub>n</sub>. ¿Qué condición sobre el error cuadrático medio "
                "garantiza la consistencia de cualquier estimador?"
            )
            ui.spoiler(
                "Por la desigualdad de Markov aplicada a (T<sub>n</sub> &minus; &theta;)<sup>2</sup>:"
                "<div class='formula-box'>&#8473;( |T<sub>n</sub> &minus; &theta;| &gt; &epsilon; ) &le; "
                "<sup>ECM(T<sub>n</sub>)</sup>&frasl;<sub>&epsilon;<sup>2</sup></sub></div>"
                "Si el error cuadrático medio tiende a cero, el estimador es consistente. Para la media, "
                "ECM = &sigma;<sup>2</sup>/n: es la ley débil de los grandes números."
            )

        if ui.accordion_step("P1_B", "(B) Cota y valor exacto"):
            ui.content("Compara las dos curvas de la gráfica de arriba. ¿Cuántas medidas garantizan, según cada una, un error menor que &epsilon; con probabilidad 0.95?")
            ui.spoiler(
                "Chebyshev pide &sigma;<sup>2</sup>/(n&epsilon;<sup>2</sup>) &le; 0.05, es decir, n &ge; "
                "20&sigma;<sup>2</sup>/&epsilon;<sup>2</sup>. La normal pide solo n &ge; (1.96&sigma;/&epsilon;)<sup>2</sup>, "
                "unas cinco veces menos. La cota de Chebyshev sirve para cualquier distribución con varianza, y ese es su "
                "precio."
            )

        if ui.accordion_step("P1_C", "(C) Consistente, ¿para qué?"):
            ui.content(
                f"La media de sus cien medidas fue {ui.fmt_int(int(MICHELSON_MEAN))}.4 km/s; el valor que hoy "
                f"corresponde a sus mismas condiciones, en aire, es unos {ui.fmt_int(int(C_TRUE))}.5 km/s. ¿Qué "
                "habría pasado si hubiera hecho cien mil medidas?"
            )
            ui.spoiler(
                "La media es consistente para &mu;, la media de las medidas, no para la velocidad de la luz. Si el aparato "
                "tiene un error sistemático, &mu; no coincide con c y más medidas solo convergen con más firmeza al valor "
                "equivocado: unos 118 km/s de más, cerca de quince errores típicos de su propia media. El error estadístico "
                "baja con n, el sistemático no."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + st.session_state["draws"])
        x = rng.normal(MICHELSON_MEAN, MICHELSON_SD, (PATHS, 1600))
        paths = running(x)
        exact = 2 * stats.norm.sf(eps * np.sqrt(n) / MICHELSON_SD)
        ui.metrics([(f"&#8473;(|X̄ &minus; &mu;| &gt; &epsilon;) = {exact:.3f}", "metric-a"),
                    (f"Chebyshev: &le; {min(1.0, MICHELSON_SD ** 2 / (n * eps ** 2)):.3f}", "metric-b"),
                    (f"Error típico: {MICHELSON_SD / np.sqrt(n):.1f} km/s", "metric-c")])
        ui.show(probability_chart(dark, eps, n), key="fig_prob")
        ui.show(paths_chart(dark, paths, n, MICHELSON_MEAN, "media acumulada (km/s)",
                            (MICHELSON_MEAN - 150, MICHELSON_MEAN + 150), extra=C_TRUE), key="fig_michelson")
        ui.footer_bar("Abajo, seis series simuladas de medidas: la media acumulada converge a la línea roja, la media del "
                      "aparato. La línea discontinua es el valor actual de la velocidad de la luz en aire.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>distribución</u> y saca <u>otras series</u>")
        if st.session_state["law"] is None:
            st.session_state["law"] = v["law"]
        ui.choice_buttons(list(LAWS), "law", labels=LAWS, per_row=2)
        if st.button("Otras seis series", key="new_paths", width="stretch"):
            st.session_state["draws"] += 1

        ui.planteamiento()
        ui.statement(
            "<b>La media que no converge (1853)</b><br><br>"
            "Siméon Denis Poisson ya había observado en 1824 que la densidad 1/(&pi;(1 + x<sup>2</sup>)) escapaba a los "
            "teoremas de su época. En 1853 Augustin Cauchy e Irénée-Jules Bienaymé discutieron en la Academia de Ciencias "
            "de París sobre el método de mínimos cuadrados, y la distribución tomó el nombre de Cauchy. Estimamos su "
            "centro, &theta; = 0, con la media y con la mediana."
        )

        if ui.accordion_step("P2_A", "(A) La media de Cauchy"):
            ui.content(
                "Elige Cauchy. ¿Converge la media acumulada? ¿Qué distribución tiene X̄<sub>n</sub> cuando los datos son "
                "de Cauchy?"
            )
            ui.spoiler(
                "No converge: cada cierto tiempo un dato enorme la desplaza. Con funciones características se prueba que "
                "X̄<sub>n</sub> es otra vez una Cauchy estándar, la misma distribución que un solo dato. Promediar mil "
                "observaciones no mejora nada: la media no es consistente. La ley de los grandes números exige que exista "
                "la esperanza, E|X| &lt; &infin;, y aquí no existe."
            )

        if ui.accordion_step("P2_B", "(B) La mediana sí"):
            ui.content("Mira la gráfica de la mediana. ¿Es consistente? ¿Con qué varianza aproximada?")
            ui.spoiler(
                "Sí. La mediana muestral es consistente para la mediana de la población siempre que la densidad sea "
                "positiva en ella, y su varianza es aproximadamente 1/(4nf(&theta;)<sup>2</sup>). En la Cauchy estándar "
                "f(0) = 1/&pi;, así que la varianza es &pi;<sup>2</sup>/(4n): disminuye como la de una media normal."
            )

        if ui.accordion_step("P2_C", "(C) La normal"):
            ui.content("Elige Normal. ¿Qué estimador converge más deprisa ahora?")
            ui.spoiler(
                "Los dos son consistentes, pero la media converge más deprisa: su varianza es 1/n frente a "
                "&pi;/(2n) de la mediana. Ningún estimador es el mejor para todas las distribuciones: la media es "
                "óptima en la normal y desastrosa en la Cauchy, y la mediana es una opción robusta para las dos."
            )

    with col_right:
        ui.right_panel()
        law = st.session_state["law"]
        rng = np.random.default_rng(v["seed"] + 101 + st.session_state["draws"])
        x = rng.standard_cauchy((PATHS, MAX_N)) if law == "cauchy" else rng.standard_normal((PATHS, MAX_N))
        paths = running(x)
        checkpoints = np.unique(np.geomspace(1, MAX_N, 60).astype(int))
        medians = running_median(x, checkpoints)
        ui.metrics([(f"Media final: {np.abs(paths[:, -1]).max():.2f} (peor serie)", "metric-a"),
                    (f"Mediana final: {np.abs(medians[:, -1]).max():.3f} (peor serie)", "metric-b")])
        ui.show(paths_chart(dark, paths, MAX_N, 0, "media acumulada", (-3, 3)), key="fig_mean_paths")
        ui.show(median_chart(dark, checkpoints, medians), key="fig_median_paths")
        ui.footer_bar(f"Seis series de {ui.fmt_int(MAX_N)} datos de una {'normal' if law == 'normal' else 'Cauchy'} estándar. Arriba, la media acumulada; abajo, la "
                      "mediana acumulada. Las métricas dan la mayor distancia al centro entre las seis series.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de pacientes</u>")
        m = st.select_slider("Pacientes", options=[10, 50, 200, 500, 2000], value=v["patients"],
                             key=ui.wkey(PAGE, "patients"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La paradoja de Neyman y Scott (1948)</b><br><br>"
            "Jerzy Neyman y Elizabeth Scott publicaron un ejemplo que inquietó a los defensores de la máxima verosimilitud. "
            "Medimos dos veces la tensión arterial de cada paciente. Cada uno tiene su propia tensión media "
            "&mu;<sub>i</sub>, y el aparato añade un error normal de varianza &sigma;<sup>2</sup> = 25, igual para todos. "
            "Queremos estimar &sigma;<sup>2</sup>, la precisión del aparato."
        )

        if ui.accordion_step("P3_A", "(A) El máximo verosímil"):
            ui.content(
                "Maximiza la verosimilitud en los &mu;<sub>i</sub> y en &sigma;<sup>2</sup>. Escribe el resultado con las "
                "diferencias d<sub>i</sub> entre las dos medidas de cada paciente."
            )
            ui.spoiler(
                "Cada &mu;<sub>i</sub> se estima con la media de sus dos medidas, y cada paciente aporta dos residuos "
                "&plusmn;d<sub>i</sub>/2. Con n pacientes:"
                "<div class='formula-box'>σ̂<sup>2</sup> = <sup>1</sup>&frasl;<sub>2n</sub> &sum; 2(d<sub>i</sub>/2)<sup>2</sup> = "
                "<sup>1</sup>&frasl;<sub>4n</sub> &sum; d<sub>i</sub><sup>2</sup></div>"
            )

        if ui.accordion_step("P3_B", "(B) Converge a la mitad"):
            ui.content(
                "Cada d<sub>i</sub> es normal de media 0 y varianza 2&sigma;<sup>2</sup>. ¿A qué valor converge el "
                "estimador cuando hay muchos pacientes?"
            )
            ui.spoiler(
                "Por la ley de los grandes números, (1/n)&sum; d<sub>i</sub><sup>2</sup> &rarr; 2&sigma;<sup>2</sup>, así que "
                "el máximo verosímil converge a &sigma;<sup>2</sup>/2: no es consistente. El problema es que el número de "
                "parámetros crece con los datos: cada paciente nuevo trae dos medidas y un &mu;<sub>i</sub> nuevo, y los "
                "teoremas de consistencia de la máxima verosimilitud suponen un número fijo de parámetros."
            )

        if ui.accordion_step("P3_C", "(C) Sesgo y consistencia"):
            ui.content(
                "Corrige el estimador para que sea consistente. ¿Puedes dar, en general, un estimador insesgado que no sea "
                "consistente, y uno sesgado que sí lo sea?"
            )
            ui.spoiler(
                "Dividiendo entre 2n en lugar de 4n, (1/2n)&sum; d<sub>i</sub><sup>2</sup> es insesgado y consistente: es "
                "la curva verde. En general son propiedades independientes: X<sub>1</sub>, el primer dato, es insesgado "
                "para &mu; y nunca mejora con n; X̄<sub>n</sub> + 1/n tiene sesgo y es consistente. La varianza con "
                "divisor n es sesgada y consistente."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + 7)
        mle, fixed = neyman_scott(2000, 5.0, rng)
        ui.metrics([(f"Máximo verosímil con {m}: {mle[m - 1]:.1f}", "metric-a"),
                    (f"Corregido: {fixed[m - 1]:.1f}", "metric-b"), ("Valor real: 25", "metric-c")])
        both = np.vstack([mle, fixed])
        p = paths_chart(dark, both, m, 25.0, "estimación de σ²", (0, 50), extra=12.5, x_label="número de pacientes")
        ui.show(p, key="fig_neyman_scott")
        ui.footer_bar("Línea roja: &sigma;<sup>2</sup> = 25. Línea discontinua: &sigma;<sup>2</sup>/2, el límite del máximo "
                      "verosímil (azul). La curva verde divide entre 2n y converge al valor correcto.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La velocidad de la luz", "P1_A"),
        ("P2", "(II) La media que no converge", "P2_A"),
        ("P3", "(III) Neyman y Scott", "P3_A"),
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
