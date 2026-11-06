#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 2: el concepto de estadístico.

Qué expresiones de una muestra son estadísticos (Fisher, 1922), el
experimento de Student con 750 muestras de cuatro fichas (un estadístico es
una variable aleatoria) y la función de distribución empírica, el estadístico
que lo resume todo (Glivenko, Cantelli y Kolmogórov).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Concepto de estadístico"
PAGE = "00_02"

MU, SIGMA = 166.0, 6.5           # estaturas en cm, parecidas a las de las fichas de Macdonell
STUDENT_SAMPLES = 750

EXPRESSIONS = {
    "mean": "X̄",
    "max": "máx X<sub>i</sub>",
    "s2": "S<sup>2</sup>",
    "x1": "X<sub>1</sub>",
    "centred": "X̄ &minus; &mu;",
    "pivot": "(X̄ &minus; &mu;)/(S/&radic;n)",
}
EXPR_LABELS = {"mean": "X̄", "max": "máx Xᵢ", "s2": "S²", "x1": "X₁", "centred": "X̄ − μ", "pivot": "(X̄ − μ)/(S/√n)"}
STATS = {"mean": "Media", "median": "Mediana", "range": "Recorrido", "sd": "Desviación S"}
STATS_THE = {"mean": "la media", "median": "la mediana", "range": "el recorrido", "sd": "la desviación S"}


def initial_values():
    return {
        "n_student": ui.dchoice(4, [2, 4, 8, 16, 30], "n_student"),
        "stat": ui.dchoice("mean", list(STATS), "stat"),
        "n_ecdf": ui.dchoice(20, [10, 20, 50, 100, 500, 2000], "n_ecdf"),
        "seed": int(ui.r("estadistico") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "expr": "mean", "stat": None, "draws": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def statistic(name: str, x: np.ndarray) -> np.ndarray:
    """Calcula el estadístico por filas: cada fila es una muestra."""
    if name == "mean":
        return x.mean(axis=1)
    if name == "median":
        return np.median(x, axis=1)
    if name == "range":
        return x.max(axis=1) - x.min(axis=1)
    return x.std(axis=1, ddof=1)


def evaluate(expr: str, x: np.ndarray):
    """Valor de la expresión en la muestra, o None si necesita el parámetro desconocido."""
    values = {"mean": x.mean(), "max": x.max(), "s2": x.var(ddof=1), "x1": x[0]}
    return values.get(expr)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def sample_chart(dark, x):
    p = ui.new_figure(dark, height=220, x_axis_label="estatura (cm)", x_range=(MU - 4 * SIGMA, MU + 4 * SIGMA),
                      y_range=(-0.5, 1.5))
    p.yaxis.visible = False
    p.ygrid.visible = False
    p.scatter(x, np.zeros_like(x), size=16, color=ui.BLUE_LINE, alpha=0.8)
    for xi, k in zip(x, range(1, len(x) + 1)):
        p.text([xi], [0.35], text=[f"X{k}"], text_align="center", text_font_size="13px",
               text_color="#e6e6e6" if dark else "#333333")
    p.add_layout(Span(location=x.mean(), dimension="height", line_color=ui.UBU_RED, line_width=2))
    return p


def histogram_chart(dark, vals, x_label, overlay=None):
    lo, hi = np.percentile(vals, [0.2, 99.8])
    edges = np.linspace(lo, hi, 36)
    h, _ = np.histogram(vals, bins=edges)
    p = ui.new_figure(dark, height=300, x_axis_label=x_label, y_axis_label="densidad")
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / (len(vals) * (edges[1] - edges[0])),
           fill_color=ui.BLUE_LINE, fill_alpha=0.55, line_color=ui.BLUE_LINE)
    if overlay is not None:
        xs = np.linspace(lo, hi, 300)
        p.line(xs, overlay(xs), line_width=3, color=ui.UBU_RED, legend_label="distribución exacta")
        ui.style_legend(p, dark, "top_right")
    return p


def ecdf_chart(dark, x):
    xs = np.sort(x)
    n = len(xs)
    grid = np.linspace(MU - 4 * SIGMA, MU + 4 * SIGMA, 400)
    p = ui.new_figure(dark, height=320, x_axis_label="estatura (cm)", y_axis_label="probabilidad acumulada",
                      y_range=(-0.02, 1.02))
    step_x = np.concatenate(([grid[0]], np.repeat(xs, 2), [grid[-1]]))
    step_y = np.concatenate(([0, 0], np.repeat(np.arange(1, n) / n, 2), [1, 1]))
    p.line(step_x, step_y, line_width=2.5, color=ui.BLUE_LINE, legend_label="Fₙ (empírica)")
    p.line(grid, stats.norm.cdf(grid, MU, SIGMA), line_width=3, color=ui.UBU_RED, legend_label="F (población)")
    return ui.style_legend(p, dark, "top_left")


def ks_distance(x):
    xs = np.sort(x)
    n = len(xs)
    F = stats.norm.cdf(xs, MU, SIGMA)
    i = np.arange(1, n + 1)
    return max((i / n - F).max(), (F - (i - 1) / n).max())


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es un estadístico?</b>")
        ui.content(
            "Una <b>muestra aleatoria simple</b> de tamaño n es un vector (X<sub>1</sub>, &hellip;, X<sub>n</sub>) de "
            "variables independientes con la misma distribución que la población. Un <b>estadístico</b> es cualquier "
            "función de la muestra que no dependa de parámetros desconocidos: se puede calcular en cuanto se tienen los "
            "datos. <i>¿Cómo se escribe la definición?</i>"
        )
        ui.formula_hidden("T = T(X<sub>1</sub>, &hellip;, X<sub>n</sub>), &nbsp; sin &theta; en la expresión")
        ui.content(
            "Como depende de variables aleatorias, un estadístico es a su vez una <b>variable aleatoria</b>: antes de "
            "tomar la muestra no sabemos cuánto valdrá, pero sí podemos estudiar su distribución. Esa idea, que hoy "
            "parece evidente, ordenó toda la estadística del siglo XX."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los fundamentos de Fisher (1922)</b><br>"
            "<i>Decide qué expresiones son estadísticos y cuáles necesitan algo que no sabemos.</i><br><br>"
            "<b>II. Las fichas de Student (1908)</b><br>"
            "<i>Repite el experimento de William Gosset con 3000 fichas de estaturas y descubre que la media también "
            "tiene distribución.</i><br><br>"
            "<b>III. La empírica lo sabe todo (1933)</b><br>"
            "<i>Comprueba con Glivenko y Cantelli que un solo estadístico reconstruye la población entera.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige una <u>expresión</u> y saca <u>otra muestra</u>")
        ui.choice_buttons(list(EXPRESSIONS), "expr", labels=EXPR_LABELS, per_row=3)
        if st.button("Otra muestra de cinco", key="new_sample", width="stretch"):
            st.session_state["draws"] += 1

        ui.planteamiento()
        ui.statement(
            "<b>Los fundamentos de Fisher (1922)</b><br><br>"
            "En «Sobre los fundamentos matemáticos de la estadística teórica», Ronald Fisher separó por primera vez con "
            "nitidez la población, descrita por unos <b>parámetros</b>, de la muestra, resumida por unos "
            "<b>estadísticos</b>, y les dio esos nombres. Medimos la estatura de cinco personas de una población normal "
            "de media &mu; y desviación &sigma; desconocidas."
        )

        if ui.accordion_step("P1_A", "(A) ¿Se puede calcular?"):
            ui.content(
                "Para cada expresión de los botones, ¿puedes calcular su valor con los cinco números de la derecha? "
                "¿Cuáles son estadísticos?"
            )
            ui.spoiler(
                "X̄, el máximo, S<sup>2</sup> y X<sub>1</sub> son estadísticos: solo usan los datos. X̄ &minus; &mu; y "
                "(X̄ &minus; &mu;)/(S/&radic;n) no lo son, porque contienen &mu;. Que un estadístico sea tonto, como "
                "X<sub>1</sub>, que tira cuatro datos, no le quita la condición de estadístico: la definición no pide "
                "que sea útil."
            )

        if ui.accordion_step("P1_B", "(B) Los que no son estadísticos"):
            ui.content(
                "La expresión (X̄ &minus; &mu;)/(S/&radic;n) no se puede calcular. ¿Para qué sirve entonces? ¿Qué tiene "
                "de especial su distribución?"
            )
            ui.spoiler(
                "Es una <b>cantidad pivotal</b>: depende del parámetro, pero su distribución no. En poblaciones normales "
                "sigue una t de Student con n &minus; 1 grados de libertad sea cual sea &mu;. Por eso sirve para construir "
                "intervalos de confianza: se despeja &mu; de una desigualdad cuya probabilidad conocemos."
            )

        if ui.accordion_step("P1_C", "(C) Resumir sin perder"):
            ui.content(
                "Un estadístico resume n números en uno (o en unos pocos). ¿Qué estadístico de los botones crees que "
                "conserva toda la información sobre &mu;? ¿Y sobre &sigma;?"
            )
            ui.spoiler(
                "En una población normal, el par (X̄, S<sup>2</sup>) contiene toda la información que la muestra trae "
                "sobre (&mu;, &sigma;): dos números sustituyen a n sin pérdida. Fisher lo llamó <b>suficiencia</b>, y se "
                "estudia en su propia herramienta. El máximo, en cambio, sería el estadístico ideal si la población "
                "fuera uniforme en [0, &theta;], no aquí."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + st.session_state["draws"])
        x = rng.normal(MU, SIGMA, 5)
        expr = st.session_state["expr"]
        value = evaluate(expr, x)
        ui.metrics([(" &nbsp; ".join(f"{xi:.1f}" for xi in x), "metric-a")])
        if value is None:
            ui.check(False, f"{EXPRESSIONS[expr]}: no se puede calcular sin conocer &mu;")
        else:
            ui.check(True, f"{EXPRESSIONS[expr]} = {value:.2f}")
        ui.show(sample_chart(dark, x), key="fig_sample")
        ui.footer_bar("Los cinco datos de la muestra, en centímetros; la línea roja es su media. Cada vez que pulsas el "
                      "botón cambia la muestra y con ella el valor de cualquier estadístico.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>estadístico</u> y el <u>tamaño de cada muestra</u>")
        if st.session_state["stat"] is None:
            st.session_state["stat"] = v["stat"]
        ui.choice_buttons(list(STATS), "stat", labels=STATS, per_row=4)
        n = st.select_slider("Fichas por muestra", options=[2, 4, 8, 16, 30], value=v["n_student"],
                             key=ui.wkey(PAGE, "n_student"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las fichas de Student (1908)</b><br><br>"
            "William Gosset trabajaba en la cervecería Guinness de Dublín y firmaba como Student. Para comprobar su "
            "distribución de la media en muestras pequeñas escribió en 3000 fichas la estatura de 3000 presos, "
            "medidos por el antropólogo William Macdonell, las barajó y formó 750 muestras de cuatro. En cada muestra "
            "calculó la media y la desviación. Repetimos el experimento con una población parecida."
        )

        if ui.accordion_step("P2_A", "(A) Una distribución por estadístico"):
            ui.content(
                "El histograma recoge el valor del estadístico en las 750 muestras. ¿Qué distribución tiene la media? "
                "¿Cómo cambia al aumentar n?"
            )
            ui.spoiler(
                "Si la población es normal, la media de n datos es exactamente normal, con media &mu; y desviación "
                "&sigma;/&radic;n: la curva roja. Al cuadruplicar n la anchura se reduce a la mitad. Esta distribución "
                "del estadístico, la que se ve al repetir el muestreo, es su <b>distribución muestral</b>."
            )

        if ui.accordion_step("P2_B", "(B) Media o mediana"):
            ui.content(
                "Las dos se centran en &mu;, porque la población es simétrica. Compara sus desviaciones en la métrica. "
                "¿Cuál concentra más, y qué pasa cuando n crece?"
            )
            ui.spoiler(
                "La media concentra más. Para muestras grandes de una normal, la varianza de la mediana es "
                "&pi;&sigma;<sup>2</sup>/(2n), un 57 % mayor que la de la media: la mediana necesita unos "
                "&pi;/2 &asymp; 1.57 datos por cada dato que usa la media para ser igual de precisa. En muestras "
                "pequeñas la diferencia es menor, y en poblaciones con colas pesadas la mediana gana."
            )

        if ui.accordion_step("P2_C", "(C) El recorrido"):
            ui.content(
                "El recorrido máx &minus; mín también estima la dispersión, y es mucho más fácil de calcular a mano que S. "
                "Con n = 4, ¿cuánto vale su media dividida entre &sigma;?"
            )
            ui.spoiler(
                "Con n = 4 la media del recorrido es unas 2.06 veces &sigma;. Ese factor, que depende solo de n, permite "
                "estimar &sigma; dividiendo el recorrido entre él. Los gráficos de control de calidad de Walter Shewhart lo "
                "usaron durante décadas en las fábricas, donde cada operario calculaba un recorrido en segundos."
            )

    with col_right:
        ui.right_panel()
        name = st.session_state["stat"]
        rng = np.random.default_rng(v["seed"] + 31 * n)
        samples = rng.normal(MU, SIGMA, (STUDENT_SAMPLES, n))
        vals = statistic(name, samples)
        overlay = None
        if name == "mean":
            overlay = lambda t: stats.norm.pdf(t, MU, SIGMA / np.sqrt(n))      # noqa: E731
        elif name == "sd":
            overlay = lambda t: stats.chi.pdf(t * np.sqrt(n - 1) / SIGMA, n - 1) * np.sqrt(n - 1) / SIGMA  # noqa: E731
        ui.metrics([(f"Promedio de {STATS_THE[name]}: {vals.mean():.2f}", "metric-a"),
                    (f"Desviación: {vals.std():.2f}", "metric-b")])
        ui.show(histogram_chart(dark, vals, f"{STATS_THE[name]} de cada muestra (cm)", overlay), key="fig_student")
        ui.footer_bar(f"{STUDENT_SAMPLES} muestras de {n} estaturas de una población normal con &mu; = {MU:.0f} cm y "
                      f"&sigma; = {SIGMA} cm. La curva roja, cuando aparece, es la distribución exacta del estadístico.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra n</u>")
        n = st.select_slider("Tamaño de la muestra", options=[10, 20, 50, 100, 500, 2000], value=v["n_ecdf"],
                             key=ui.wkey(PAGE, "n_ecdf"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La empírica lo sabe todo (1933)</b><br><br>"
            "La <b>función de distribución empírica</b> F<sub>n</sub>(x) es la proporción de datos de la muestra que no "
            "pasan de x. Es un estadístico, aunque su valor no sea un número sino una función entera. En 1933 Valeri "
            "Glivenko y Francesco Cantelli probaron que reconstruye la población, y Andréi Kolmogórov midió a qué "
            "velocidad."
        )

        if ui.accordion_step("P3_A", "(A) Un punto fijo"):
            ui.content(
                "Fija un valor x. ¿Qué distribución tiene n&middot;F<sub>n</sub>(x)? ¿Cuál es la esperanza y la varianza de "
                "F<sub>n</sub>(x)?"
            )
            ui.spoiler(
                "Cada dato cae por debajo de x con probabilidad F(x), de forma independiente, así que "
                "n&middot;F<sub>n</sub>(x) es binomial de parámetros n y F(x):"
                "<div class='formula-box'>E[F<sub>n</sub>(x)] = F(x) &nbsp;&nbsp; &#120141;(F<sub>n</sub>(x)) = "
                "<sup>F(x)(1 &minus; F(x))</sup>&frasl;<sub>n</sub></div>"
                "Por la ley fuerte de los grandes números, F<sub>n</sub>(x) converge a F(x) casi seguro en cada punto."
            )

        if ui.accordion_step("P3_B", "(B) Todos los puntos a la vez"):
            ui.content(
                "La convergencia en cada punto no garantiza que la curva azul se pegue a la roja en todas partes al mismo "
                "tiempo. ¿Qué afirma el teorema de Glivenko-Cantelli?"
            )
            ui.spoiler(
                "Que la mayor distancia vertical entre las dos curvas tiende a cero casi seguro:"
                "<div class='formula-box'>D<sub>n</sub> = sup<sub>x</sub> |F<sub>n</sub>(x) &minus; F(x)| &rarr; 0</div>"
                "Por eso se le llama a veces el teorema fundamental de la estadística: con datos suficientes, la muestra "
                "revela la distribución completa, no solo su media."
            )

        if ui.accordion_step("P3_C", "(C) La escala de Kolmogórov"):
            ui.content(
                "Mira cómo cambia D<sub>n</sub> al multiplicar n por 100. ¿A qué velocidad decrece? ¿Qué umbral supera "
                "&radic;n&middot;D<sub>n</sub> solo un 5 % de las veces?"
            )
            ui.spoiler(
                "D<sub>n</sub> decrece como 1/&radic;n, igual que el error de una media. Kolmogórov encontró la "
                "distribución límite de &radic;n&middot;D<sub>n</sub>, que no depende de F si F es continua: supera 1.36 "
                "con probabilidad 0.05. Es la base del test de Kolmogórov-Smirnov para comprobar si unos datos siguen una "
                "distribución dada."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + n)
        x = rng.normal(MU, SIGMA, n)
        d = ks_distance(x)
        scaled = np.sqrt(n) * d
        ui.metrics([(f"D<sub>n</sub> = {d:.3f}", "metric-a"), (f"&radic;n&middot;D<sub>n</sub> = {scaled:.2f}", "metric-b")])
        ui.check(scaled <= 1.36, "&radic;n&middot;D<sub>n</sub> por debajo de 1.36" if scaled <= 1.36
                 else "&radic;n&middot;D<sub>n</sub> por encima de 1.36: muestra rara")
        ui.show(ecdf_chart(dark, x), key="fig_ecdf")
        ui.footer_bar(f"La escalera azul sube 1/{n} en cada dato de la muestra; la curva roja es la distribución normal de "
                      "la población. D<sub>n</sub> es la mayor separación vertical entre las dos.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los fundamentos de Fisher", "P1_A"),
        ("P2", "(II) Las fichas de Student", "P2_A"),
        ("P3", "(III) La empírica lo sabe todo", "P3_A"),
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
