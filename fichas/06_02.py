#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 6, ficha 2: la convergencia en probabilidad.

La ley débil de Chebyshev (la probabilidad de alejarse de la media tiende a
cero), las agujas de Lazzarini (transformaciones continuas de un estimador)
y el teorema de Slutsky con la t de Student.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import BoxAnnotation, Span
from scipy import stats

import civic_ui as ui

TITLE = "Convergencia en probabilidad"
SYMBOL = "→ᴾ"
PAGE = "06_02"

LAWS = {"die": "Un dado", "coin": "Moneda con p = 0.3", "exp": "Exponencial de media 1"}
LAW_MOMENTS = {"die": (3.5, 35 / 12), "coin": (0.3, 0.21), "exp": (1.0, 1.0)}
N_MAX = 400
PATHS = 200
RATIO = 5 / 6          # longitud de la aguja entre la distancia de las líneas, como en el experimento de 1901


def initial_values():
    return {
        "law": ui.dchoice("die", list(LAWS), "law"),
        "eps": ui.dchoice(0.3, [0.1, 0.2, 0.3, 0.5], "eps"),
        "needles": ui.dchoice(3408, [100, 500, 1000, 3408, 10000], "needles"),
        "n_t": ui.dint(5, 3, 15, "n_t"),
        "seed": int(ui.r("chebyshev") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "law": None, "t_law": "normal", "law_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def draw(law: str, size, rng):
    if law == "die":
        return rng.integers(1, 7, size).astype(float)
    if law == "coin":
        return (rng.random(size) < 0.3).astype(float)
    return rng.exponential(1.0, size)


def running_means(law: str, seed: int):
    rng = np.random.default_rng(seed)
    x = draw(law, (PATHS, N_MAX), rng)
    return np.cumsum(x, axis=1) / np.arange(1, N_MAX + 1)


def buffon_estimates(n: int, reps: int, seed: int):
    p = 2 * RATIO / np.pi
    crossings = np.random.default_rng(seed).binomial(n, p, reps)
    crossings = np.maximum(crossings, 1)
    return 2 * RATIO * n / crossings


def t_statistics(law: str, n: int, reps: int, seed: int):
    rng = np.random.default_rng(seed)
    if law == "normal":
        x = rng.standard_normal((reps, n))
        mu = 0.0
    else:
        x = rng.exponential(1.0, (reps, n))
        mu = 1.0
    return (x.mean(axis=1) - mu) / (x.std(axis=1, ddof=1) / np.sqrt(n))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def paths_chart(dark, means, mu: float, eps: float):
    ns = np.arange(1, N_MAX + 1)
    p = ui.new_figure(dark, height=260, x_axis_label="n", y_axis_label="media de las n primeras", x_range=(1, N_MAX),
                      y_range=(mu - 4 * eps, mu + 4 * eps))
    p.add_layout(BoxAnnotation(bottom=mu - eps, top=mu + eps, fill_color=ui.GREEN_LINE, fill_alpha=0.12))
    p.multi_line([ns.tolist()] * 40, [m.tolist() for m in means[:40]], line_color=ui.BLUE_LINE, line_alpha=0.25,
                 line_width=1)
    p.add_layout(Span(location=mu, dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    return p


def outside_chart(dark, means, mu: float, var: float, eps: float):
    ns = np.arange(1, N_MAX + 1)
    frac = (np.abs(means - mu) >= eps).mean(axis=0)
    p = ui.new_figure(dark, height=230, x_axis_label="n", y_axis_label="ℙ(|media − μ| ≥ ε)", x_range=(1, N_MAX),
                      y_range=(0, 1.02))
    p.line(ns, frac, line_width=3, color=ui.BLUE_LINE, legend_label="fracción de trayectorias fuera")
    p.line(ns, np.minimum(1, var / (ns * eps ** 2)), line_width=3, color=ui.UBU_RED, line_dash="dashed",
           legend_label="cota de Chebyshev σ²/(nε²)")
    return ui.style_legend(p, dark, "top_right")


def buffon_chart(dark, estimates, n: int):
    lo, hi = np.pi - 0.6, np.pi + 0.6
    edges = np.linspace(lo, hi, 61)
    hist, _ = np.histogram(estimates, bins=edges)
    p = ui.new_figure(dark, height=280, x_axis_label=f"estimación de π con {n} agujas", y_axis_label="densidad",
                      x_range=(lo, hi))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(estimates) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.7, line_color=None)
    p.add_layout(Span(location=np.pi, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return p


def t_chart(dark, tvals, n: int):
    xs = np.linspace(-5, 5, 400)
    edges = np.linspace(-5, 5, 51)
    hist, _ = np.histogram(tvals, bins=edges)
    p = ui.new_figure(dark, height=300, x_axis_label="(media − μ) / (S/√n)", y_axis_label="densidad", x_range=(-5, 5),
                      y_range=(0, 0.48))
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(tvals) * (edges[1] - edges[0])),
           fill_color=ui.UBU_YELLOW, fill_alpha=0.6, line_color=None, legend_label="simulación")
    p.line(xs, stats.norm.pdf(xs), line_width=4, color=ui.BLUE_LINE, legend_label="N(0, 1)")
    p.line(xs, stats.t.pdf(xs, n - 1), line_width=3, color=ui.UBU_RED, line_dash="dashed",
           legend_label=f"t de Student con {n - 1} g.l.")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuándo está X<sub>n</sub> cerca de X con probabilidad cada vez mayor?</b>")
        ui.content(
            "La convergencia en distribución no dice que los valores de X<sub>n</sub> se acerquen a los de X, solo que se "
            "parecen sus distribuciones. Si las variables viven en el mismo espacio, se puede pedir más: que la "
            "probabilidad de que estén lejos sea cada vez más pequeña. <i>Escribe la definición.</i>"
        )
        ui.formula_hidden("X<sub>n</sub> &rarr; X en probabilidad &nbsp;&hArr;&nbsp; &#8473;(|X<sub>n</sub> &minus; X| &ge; &epsilon;) "
                          "&rarr; 0 &nbsp; para todo &epsilon; &gt; 0")
        ui.content(
            "Es más fuerte que la convergencia en distribución, y equivalente a ella cuando el límite es una "
            "constante. Se conserva al aplicar funciones continuas y al hacer operaciones con otras sucesiones que "
            "también convergen en probabilidad."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La ley débil de Chebyshev (1867)</b><br>"
            "<i>Mira cómo doscientas medias de datos al azar se meten en una banda alrededor de la media "
            "verdadera.</i><br><br>"
            "<b>II. Las agujas de Lazzarini (1901)</b><br>"
            "<i>Un experimento de Buffon con un resultado demasiado bueno, y por qué la estimación de &pi; "
            "converge.</i><br><br>"
            "<b>III. Slutsky y Student</b><br>"
            "<i>Sustituye la desviación desconocida por la de la muestra y descubre por qué funciona para muestras "
            "grandes.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>distribución</u> y la <u>anchura de la banda &epsilon;</u>")
        if st.session_state["law"] is None:
            st.session_state["law"] = v["law"]
        ui.choice_buttons(list(LAWS), "law", labels=LAWS, per_row=3)
        eps = st.select_slider("ε", options=[0.05, 0.1, 0.2, 0.3, 0.5, 1.0], value=v["eps"], key=ui.wkey(PAGE, "eps"))

        ui.planteamiento()
        ui.statement(
            "<b>La ley débil de Chebyshev (1867)</b><br><br>"
            "El teorema áureo de Bernoulli hablaba de frecuencias en una urna. Chebyshev, con su desigualdad, lo "
            "extendió en 1867 a medias de cualquier variable con varianza finita. Tomamos doscientas sucesiones "
            "independientes de datos con la misma distribución y seguimos la media de los n primeros en cada una."
        )

        if ui.accordion_step("P1_A", "(A) Media y varianza de la media"):
            ui.content(
                "Si X<sub>1</sub>, &hellip;, X<sub>n</sub> son independientes con media &mu; y varianza &sigma;<sup>2</sup>, calcula la "
                "media y la varianza de X̄<sub>n</sub>."
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124;[X̄<sub>n</sub>] = &mu; &nbsp;&nbsp; &#120141;(X̄<sub>n</sub>) = <sup>&sigma;<sup>2</sup></sup>&frasl;<sub>n</sub></div>"
                "Basta con que las variables sean incorreladas para que se sumen las varianzas."
            )

        if ui.accordion_step("P1_B", "(B) La ley débil"):
            ui.content(
                "Aplica la desigualdad de Chebyshev a X̄<sub>n</sub>. ¿Qué concluyes cuando n &rarr; &infin;? Compara la cota "
                "con la fracción de trayectorias que están fuera de la banda."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(|X̄<sub>n</sub> &minus; &mu;| &ge; &epsilon;) &le; <sup>&sigma;<sup>2</sup></sup>&frasl;<sub>n&epsilon;<sup>2</sup></sub> "
                "&rarr; 0</div>"
                "La media muestral converge en probabilidad a &mu;: es la ley débil de los grandes números. La versión "
                "general solo pide que la suma de las varianzas dividida entre n<sup>2</sup> tienda a cero. La cota, "
                "como siempre con Chebyshev, es mucho más pesimista que la realidad."
            )

        if ui.accordion_step("P1_C", "(C) Lo que la ley débil no dice"):
            ui.content(
                "Mira una sola trayectoria. ¿Garantiza la ley débil que, a partir de cierto n, se quede para siempre dentro "
                "de la banda?"
            )
            ui.spoiler(
                "No. Dice que, para cada n grande, la mayoría de las trayectorias está dentro; no impide que una "
                "trayectoria concreta se salga de vez en cuando, cada vez en un n distinto. Que cada trayectoria acabe "
                "dentro para siempre es una afirmación más fuerte, la ley fuerte, que pertenece a la convergencia casi "
                "segura y llegará dos fichas más adelante."
            )

    with col_right:
        ui.right_panel()
        law = st.session_state["law"]
        mu, var = LAW_MOMENTS[law]
        if st.button("Otras 200 trayectorias", key="law_new", width="stretch"):
            st.session_state["law_round"] += 1
        means = running_means(law, v["seed"] + st.session_state["law_round"])
        out = (np.abs(means[:, -1] - mu) >= eps).mean()
        ui.metrics([(f"Fuera de la banda con n = {N_MAX}: {out:.3f}", "metric-a"),
                    (f"Cota de Chebyshev: {min(1, var / (N_MAX * eps ** 2)):.3f}", "metric-c")])
        ui.show(paths_chart(dark, means, mu, eps), key="fig_weak_paths")
        ui.show(outside_chart(dark, means, mu, var, eps), key="fig_weak_frac")
        ui.footer_bar(f"{LAWS[law]}: &mu; = {mu:g}, &sigma;<sup>2</sup> = {var:.3f}. Arriba, cuarenta de las doscientas trayectorias "
                      "y la banda &mu; &plusmn; &epsilon;; abajo, la fracción de trayectorias fuera de la banda en cada n.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de agujas n</u>")
        n = st.select_slider("Agujas lanzadas n", options=[50, 100, 500, 1000, 3408, 10000, 50000], value=v["needles"],
                             key=ui.wkey(PAGE, "needles"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las agujas de Lazzarini (1901)</b><br><br>"
            "En la ficha de Laplace estimaste &pi; con la aguja de Buffon. En 1901 el italiano Mario Lazzarini "
            "publicó que, con agujas de 2.5 cm sobre líneas separadas 3 cm, había obtenido 1808 cruces en 3408 "
            "lanzamientos, lo que daba &pi; &asymp; 3.1415929, con seis decimales correctos. Aquí repetimos el experimento "
            "muchas veces para cada n y miramos cómo se reparten las estimaciones."
        )

        if ui.accordion_step("P2_A", "(A) La frecuencia converge"):
            ui.content(
                "Sea f<sub>n</sub> la frecuencia de cruces en n lanzamientos. ¿A qué converge en probabilidad, y por qué?"
            )
            ui.spoiler(
                "f<sub>n</sub> es la media de n indicatrices independientes de media p = 2&#8467;/(&pi;d). Por la ley débil, "
                "f<sub>n</sub> &rarr; p en probabilidad. Con &#8467;/d = 5/6, p = 5/(3&pi;) &asymp; 0.53."
            )

        if ui.accordion_step("P2_B", "(B) Una función continua de la frecuencia"):
            ui.content(
                "El estimador es &pi;̂<sub>n</sub> = 2&#8467;/(d&middot;f<sub>n</sub>). ¿Por qué converge en probabilidad a &pi;, si "
                "lo que sabemos es que f<sub>n</sub> converge a p?"
            )
            ui.spoiler(
                "Porque &pi;̂<sub>n</sub> = g(f<sub>n</sub>) con g(x) = 2&#8467;/(dx), continua en p &gt; 0, y la convergencia en "
                "probabilidad se conserva al aplicar funciones continuas: g(f<sub>n</sub>) &rarr; g(p) = &pi;. El histograma de "
                "la derecha se estrecha alrededor de &pi;, con una anchura que decrece como 1/&radic;n."
            )

        if ui.accordion_step("P2_C", "(C) ¿Demasiado bueno?"):
            ui.content(
                "Con 3408 agujas, ¿qué precisión cabe esperar? ¿Cuál es la probabilidad de obtener exactamente 1808 cruces? "
                "¿Qué te hace sospechar del resultado de Lazzarini?"
            )
            ui.spoiler(
                "Con 3408 agujas las estimaciones se reparten con una desviación de unas cinco centésimas: acertar seis "
                "decimales es puro azar. Obtener exactamente 1808 cruces tiene una probabilidad de en torno al 1.4 %, no "
                "despreciable. Lo sospechoso es otra cosa: con &#8467;/d = 5/6, el estimador vale (5/3)&middot;3408/C, y 3408 "
                "es justo un número de lanzamientos para el que 355/113, la célebre aproximación de &pi;, es alcanzable. "
                "Todo apunta a que Lazzarini eligió cuándo parar. La convergencia en probabilidad promete acercarse, no "
                "acertar a la primera."
            )

    with col_right:
        ui.right_panel()
        est = buffon_estimates(n, 20000, v["seed"])
        p = 2 * RATIO / np.pi
        ui.metrics([(f"&sigma; de las estimaciones: {est.std():.4f}", "metric-a"),
                    (f"&#8473;(|&pi;̂ &minus; &pi;| &gt; 0.01) = {(np.abs(est - np.pi) > 0.01).mean():.3f}", "metric-c")])
        ui.show(buffon_chart(dark, est, n), key="fig_lazzarini")
        ui.footer_bar(f"20 000 repeticiones del experimento con {n} agujas. Con 3408, &#8473;(1808 cruces) = "
                      f"{stats.binom.pmf(1808, 3408, p):.4f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra n</u> y la <u>distribución de los datos</u>")
        n = st.slider("Tamaño de la muestra n", 2, 60, v["n_t"], 1, key=ui.wkey(PAGE, "n_t"))
        laws = {"normal": "Datos normales", "exp": "Datos exponenciales"}
        ui.choice_buttons(list(laws), "t_law", labels=laws, per_row=2)

        ui.planteamiento()
        ui.statement(
            "<b>Slutsky y Student</b><br><br>"
            "William Gosset, químico de la cervecería Guinness en Dublín, trabajaba con muestras muy pequeñas de cebada "
            "y no conocía la desviación típica &sigma;. Publicó en 1908, con el seudónimo Student, la distribución de "
            "(X̄ &minus; &mu;)/(S/&radic;n), donde S es la desviación de la muestra. Para muestras grandes, el economista "
            "ruso Evgeni Slutsky demostró en 1925 por qué se puede tratar S como si fuera &sigma;."
        )

        if ui.accordion_step("P3_A", "(A) S converge a &sigma;"):
            ui.content(
                "La varianza muestral S<sup>2</sup> es, salvo un factor que tiende a 1, la media de los (X<sub>i</sub> &minus; X̄)<sup>2</sup>. "
                "¿A qué converge en probabilidad? ¿Y S?"
            )
            ui.spoiler(
                "Por la ley débil aplicada a los X<sub>i</sub><sup>2</sup> y a los X<sub>i</sub>, S<sup>2</sup> &rarr; &#120124;[X<sup>2</sup>] &minus; "
                "&mu;<sup>2</sup> = &sigma;<sup>2</sup> en probabilidad. La raíz es continua, así que S &rarr; &sigma;."
            )

        if ui.accordion_step("P3_B", "(B) El teorema de Slutsky"):
            ui.content(
                "Por el teorema central del límite, &radic;n(X̄ &minus; &mu;)/&sigma; converge en distribución a una normal típica. "
                "¿Qué le pasa al cociente si se sustituye &sigma; por S?"
            )
            ui.spoiler(
                "Slutsky: si U<sub>n</sub> &rarr; U en distribución y V<sub>n</sub> &rarr; c &ne; 0 en probabilidad, entonces "
                "U<sub>n</sub>/V<sub>n</sub> &rarr; U/c en distribución, y lo mismo con sumas y productos. Con U<sub>n</sub> = "
                "&radic;n(X̄ &minus; &mu;) y V<sub>n</sub> = S:"
                "<div class='formula-box'><sup>X̄ &minus; &mu;</sup>&frasl;<sub>S/&radic;n</sub> &rarr; N(0, 1) en distribución</div>"
                "Es justo el caso que fallaba en la ficha anterior: aquí uno de los dos factores tiende a una constante."
            )

        if ui.accordion_step("P3_C", "(C) Muestras pequeñas"):
            ui.content(
                "Con n pequeño y datos normales, compara el histograma con la normal y con la t de Student. ¿Qué ocurre en "
                "las colas? ¿Y con datos exponenciales?"
            )
            ui.spoiler(
                "Con datos normales el cociente sigue exactamente una t de Student con n &minus; 1 grados de libertad, de "
                "colas más gruesas que la normal: S también es aleatoria y a veces sale pequeña, inflando el cociente. "
                "Al crecer n la t se confunde con la normal, como asegura Slutsky. Con datos exponenciales no hay "
                "fórmula exacta: la distribución es asimétrica para n pequeño y solo el límite está garantizado."
            )

    with col_right:
        ui.right_panel()
        tvals = t_statistics(st.session_state["t_law"], n, 20000, v["seed"])
        crit = stats.norm.ppf(0.975)
        ui.metrics([(f"&#8473;(|T| &gt; 1.96) simulada: {(np.abs(tvals) > crit).mean():.4f}", "metric-a"),
                    ("Con la normal: 0.0500", "metric-c")])
        ui.show(t_chart(dark, tvals, n), key="fig_student")
        ui.footer_bar(f"Con n = {n}, la t de Student da &#8473;(|T| &gt; 1.96) = {2 * stats.t.sf(crit, n - 1):.4f}: usar la "
                      "normal con muestras pequeñas subestima las colas.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La ley débil de Chebyshev", "P1_A"),
        ("P2", "(II) Las agujas de Lazzarini", "P2_A"),
        ("P3", "(III) Slutsky y Student", "P3_A"),
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
