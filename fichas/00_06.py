#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 6: el estimador suficiente.

El orden de las caras de una moneda no dice nada de p una vez que se sabe
cuántas salieron, el teorema de factorización con muestras distintas y la
misma verosimilitud (la discusión de Fisher con Eddington) y la mejora de
Rao-Blackwell con las coces de caballo de Bortkiewicz.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Estimador suficiente"
PAGE = "00_06"

TOSSES = 5
SIMS = 200_000
FAMILIES = {"poisson": "Poisson", "normal": "Normal", "uniform": "Uniforme"}
CORPS_YEARS, DEATHS = 200, 122


def initial_values():
    return {
        "p": round(20 * ui.dfloat(0.30, 0.10, 0.90, "p")) / 20,
        "k": ui.dint(2, 1, TOSSES - 1, "k"),
        "family": ui.dchoice("normal", list(FAMILIES), "family"),
        "lam": ui.dfloat(0.61, 0.20, 2.00, "lam"),
        "n_rb": ui.dchoice(20, [5, 10, 20, 50, 200], "n_rb"),
        "seed": int(ui.r("suficiente") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "family": None, "pairs": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def sequences_with(k: int):
    """Las secuencias de TOSSES lanzamientos con k caras, como cadenas C/X."""
    out = []
    for heads in combinations(range(TOSSES), k):
        out.append("".join("C" if i in heads else "X" for i in range(TOSSES)))
    return out


def conditional_frequencies(p: float, k: int, rng):
    x = rng.random((SIMS, TOSSES)) < p
    keep = x[x.sum(axis=1) == k]
    codes = keep @ (1 << np.arange(TOSSES))
    seqs = sequences_with(k)
    seq_codes = [sum(1 << i for i, c in enumerate(s) if c == "C") for s in seqs]
    counts = np.array([(codes == c).sum() for c in seq_codes])
    return seqs, counts / max(len(keep), 1), len(keep)


def twin_samples(family: str, rng, n: int = 8):
    """Dos muestras distintas con el mismo estadístico suficiente."""
    if family == "poisson":
        a = rng.poisson(2.0, n)
        b = rng.multinomial(a.sum(), np.ones(n) / n)
        return a.astype(float), b.astype(float), f"&sum;x = {int(a.sum())}"
    if family == "normal":
        a = rng.normal(0, 2.0, n)
        z = rng.standard_normal(n)
        b = z / np.linalg.norm(z) * np.linalg.norm(a)
        return a, b, f"&sum;x<sup>2</sup> = {np.sum(a ** 2):.2f}"
    a = rng.uniform(0, 5.0, n)
    b = np.concatenate(([a.max()], rng.uniform(0, a.max(), n - 1)))
    rng.shuffle(b)
    return a, b, f"máx x = {a.max():.2f}"


def likelihood(family: str, x: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Verosimilitud normalizada a máximo 1 sobre la rejilla."""
    if family == "poisson":
        ll = x.sum() * np.log(grid) - len(x) * grid
    elif family == "normal":
        ll = -len(x) * np.log(grid) - np.sum(x ** 2) / (2 * grid ** 2)
    else:
        ll = np.where(grid >= x.max(), -len(x) * np.log(grid), -np.inf)
    return np.exp(ll - ll.max())


GRIDS = {"poisson": (0.3, 5.0, "λ"), "normal": (0.5, 5.0, "σ"), "uniform": (2.0, 9.0, "θ")}


# =============================================================================
# 2. FIGURAS
# =============================================================================

def sequences_chart(dark, seqs, freqs):
    p = ui.new_figure(dark, height=300, x_range=seqs, y_axis_label="frecuencia condicionada",
                      y_range=(0, max(freqs.max(), 1 / len(seqs)) * 1.35))
    p.vbar(x=seqs, top=freqs, width=0.7, color=ui.BLUE_LINE, alpha=0.7)
    p.add_layout(Span(location=1 / len(seqs), dimension="width", line_color=ui.UBU_RED, line_width=2.5))
    p.xaxis.major_label_orientation = 0.9
    return p


def likelihood_chart(dark, family, a, b):
    lo, hi, name = GRIDS[family]
    grid = np.linspace(lo, hi, 500)
    p = ui.new_figure(dark, height=280, x_axis_label=name, y_axis_label="verosimilitud (máximo = 1)")
    p.line(grid, likelihood(family, a, grid), line_width=6, color=ui.BLUE_LINE, alpha=0.5, legend_label="muestra A")
    p.line(grid, likelihood(family, b, grid), line_width=2.5, color=ui.UBU_RED, line_dash="dashed", legend_label="muestra B")
    return ui.style_legend(p, dark, "top_right")


def samples_chart(dark, a, b):
    lo = min(a.min(), b.min()) - 0.5
    hi = max(a.max(), b.max()) + 0.5
    p = ui.new_figure(dark, height=170, x_range=(lo, hi), y_range=["B", "A"])
    p.scatter(a, ["A"] * len(a), size=13, color=ui.BLUE_LINE, alpha=0.75)
    p.scatter(b, ["B"] * len(b), size=13, color=ui.UBU_RED, alpha=0.75)
    return p


def rb_chart(dark, p0, rb, target):
    vals = np.concatenate([p0, rb])
    edges = np.linspace(np.percentile(vals, 0.3), np.percentile(vals, 99.7), 45)
    centres = (edges[:-1] + edges[1:]) / 2
    p = ui.new_figure(dark, height=300, x_axis_label="estimación de ℙ(X = 0)", y_axis_label="densidad")
    for vals_, label, colour in ((p0, "proporción de ceros", ui.ORANGE_LINE), (rb, "Rao-Blackwell", ui.BLUE_LINE)):
        h, _ = np.histogram(vals_, bins=edges)
        p.line(centres, h / (len(vals_) * (edges[1] - edges[0])), line_width=3, color=colour, legend_label=label)
    p.add_layout(Span(location=target, dimension="height", line_color=ui.UBU_RED, line_width=2))
    return ui.style_legend(p, dark, "top_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuándo un resumen no pierde nada?</b>")
        ui.content(
            "Un estadístico T es <b>suficiente</b> para &theta; si, una vez conocido su valor, la muestra no aporta "
            "ninguna información adicional sobre &theta;: la distribución condicionada de la muestra dada T no depende de "
            "&theta;. En la práctica se reconoce con el <b>teorema de factorización</b> de Fisher y Neyman. <i>¿Qué "
            "dice?</i>"
        )
        ui.formula_hidden("f(x<sub>1</sub>, &hellip;, x<sub>n</sub>; &theta;) = g( T(x), &theta; ) &middot; h(x<sub>1</sub>, &hellip;, x<sub>n</sub>)")
        ui.content(
            "La verosimilitud depende de los datos solo a través de T, salvo un factor h que no contiene &theta;. Las tres "
            "situaciones muestran qué significa la definición, cómo se usa la factorización y para qué sirve: un "
            "estimador mejora siempre al condicionarlo a un estadístico suficiente."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El orden de las caras</b><br>"
            "<i>Lanza cinco veces una moneda sesgada y comprueba que, sabiendo cuántas caras salieron, el orden ya no "
            "dice nada.</i><br><br>"
            "<b>II. Fisher contra Eddington (1920)</b><br>"
            "<i>Fabrica muestras distintas con la misma verosimilitud y entiende la discusión sobre cómo medir la "
            "precisión de un astrónomo.</i><br><br>"
            "<b>III. Las coces de Bortkiewicz</b><br>"
            "<i>Mejora un estimador razonable con el teorema de Rao-Blackwell, usando los datos más famosos de la "
            "Poisson.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>probabilidad de cara p</u> y el <u>número de caras k</u>")
        p = st.slider("Probabilidad de cara p", 0.05, 0.95, v["p"], 0.05, key=ui.wkey(PAGE, "p"))
        k = st.slider("Caras en los cinco lanzamientos", 1, TOSSES - 1, v["k"], 1, key=ui.wkey(PAGE, "k"))

        ui.planteamiento()
        ui.statement(
            "<b>El orden de las caras</b><br><br>"
            "Lanzamos cinco veces una moneda con probabilidad de cara p desconocida y anotamos la secuencia, por ejemplo "
            "CXXCX. Simulamos doscientas mil secuencias, nos quedamos con las que tienen exactamente k caras y contamos "
            "cuántas veces aparece cada orden posible."
        )

        if ui.accordion_step("P1_A", "(A) La distribución condicionada"):
            ui.content("Calcula &#8473;(secuencia | T = k), donde T es el número de caras. ¿Depende de p?")
            ui.spoiler(
                "Cada secuencia con k caras tiene probabilidad p<sup>k</sup>(1 &minus; p)<sup>5 &minus; k</sup>, y T = k "
                "tiene probabilidad C(5, k)p<sup>k</sup>(1 &minus; p)<sup>5 &minus; k</sup>. Al dividir, p desaparece:"
                "<div class='formula-box'>&#8473;(secuencia | T = k) = <sup>1</sup>&frasl;<sub>C(5, k)</sub></div>"
                "Todas las ordenaciones son igual de probables. T es suficiente para p."
            )

        if ui.accordion_step("P1_B", "(B) Lo que no dice el orden"):
            ui.content(
                "Mueve p con k fijo. Las barras cambian un poco por el azar, pero no se inclinan. ¿Qué significa en la "
                "práctica?"
            )
            ui.spoiler(
                "Que una vez contadas las caras, el orden es puro ruido: se podría generar de nuevo con un sorteo sin "
                "conocer p. Cualquier estimador que use el orden, como «la proporción de caras en los dos primeros "
                "lanzamientos», añade azar sin añadir información. Dos investigadores con la misma T deberían llegar a la "
                "misma conclusión sobre p."
            )

        if ui.accordion_step("P1_C", "(C) Con la factorización"):
            ui.content("Escribe la función de probabilidad conjunta de los cinco lanzamientos y factorízala.")
            ui.spoiler(
                "f(x; p) = p<sup>&sum;x<sub>i</sub></sup>(1 &minus; p)<sup>5 &minus; &sum;x<sub>i</sub></sup>, que ya es "
                "g(T, p) con h = 1. El teorema de factorización confirma, sin calcular ninguna condicionada, que "
                "T = &sum;x<sub>i</sub> es suficiente."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + int(p * 100) * 7 + k)
        seqs, freqs, kept = conditional_frequencies(p, k, rng)
        spread = freqs.max() - freqs.min()
        ui.metrics([(f"Secuencias con {k} caras: {ui.fmt_int(kept)}", "metric-a"),
                    (f"1/C(5, {k}) = {1 / len(seqs):.3f}", "metric-c"),
                    (f"Máx &minus; mín: {spread:.3f}", "metric-b")])
        ui.show(sequences_chart(dark, seqs, freqs), key="fig_sequences")
        ui.footer_bar(f"Frecuencia de cada orden entre las {ui.fmt_int(kept)} secuencias simuladas con {k} caras. La línea "
                      "roja es 1/C(5, k), el mismo valor para cualquier p.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>familia</u> y fabrica <u>otro par de muestras</u>")
        if st.session_state["family"] is None:
            st.session_state["family"] = v["family"]
        ui.choice_buttons(list(FAMILIES), "family", labels=FAMILIES, per_row=3)
        if st.button("Otro par de muestras", key="new_pair", width="stretch"):
            st.session_state["pairs"] += 1

        ui.planteamiento()
        ui.statement(
            "<b>Fisher contra Eddington (1920)</b><br><br>"
            "El astrónomo Arthur Eddington sostenía que la precisión de un observador se mide mejor con la desviación "
            "media &sum;|x<sub>i</sub>|/n que con la desviación típica. Ronald Fisher le contestó en 1920 que, en una normal, "
            "la suma de cuadrados contiene toda la información sobre &sigma; y la desviación media no añade nada. Fabricamos "
            "dos muestras de ocho datos distintas, A y B, con el mismo estadístico suficiente, y dibujamos sus "
            "verosimilitudes."
        )

        if ui.accordion_step("P2_A", "(A) Factorizar las tres familias"):
            ui.content(
                "Escribe la verosimilitud de una Poisson(&lambda;), de una normal de media 0 y desviación &sigma;, y de una "
                "uniforme en [0, &theta;]. ¿Qué estadístico suficiente sale en cada caso?"
            )
            ui.spoiler(
                "Poisson: e<sup>&minus;n&lambda;</sup>&lambda;<sup>&sum;x<sub>i</sub></sup> &middot; 1/&prod;x<sub>i</sub>!, "
                "con T = &sum;x<sub>i</sub>. Normal: &sigma;<sup>&minus;n</sup>e<sup>&minus;&sum;x<sub>i</sub><sup>2</sup>/(2&sigma;<sup>2</sup>)</sup> "
                "&middot; (2&pi;)<sup>&minus;n/2</sup>, con T = &sum;x<sub>i</sub><sup>2</sup>. Uniforme: "
                "&theta;<sup>&minus;n</sup>&middot;1{máx x<sub>i</sub> &le; &theta;}, con T = máx x<sub>i</sub>; en este "
                "caso la indicatriz forma parte de g, porque depende de &theta;."
            )

        if ui.accordion_step("P2_B", "(B) Dos muestras, una verosimilitud"):
            ui.content(
                "Las muestras A y B son distintas, pero las curvas coinciden. ¿Por qué? ¿Qué conclusión sacarían de ellas "
                "dos estadísticos que razonan con la verosimilitud?"
            )
            ui.spoiler(
                "Por la factorización, la verosimilitud es g(T, &theta;) por un factor que no depende de &theta;; al "
                "normalizar, ese factor desaparece. Dos muestras con la misma T dan la misma curva y, por tanto, la misma "
                "estimación de máxima verosimilitud, los mismos intervalos y las mismas decisiones."
            )

        if ui.accordion_step("P2_C", "(C) La respuesta a Eddington"):
            ui.content("Compara la desviación media &sum;|x<sub>i</sub>|/n de las dos muestras normales. ¿Qué demuestra?")
            ui.spoiler(
                "Las dos muestras tienen la misma suma de cuadrados y desviaciones medias distintas, y sin embargo cuentan "
                "exactamente lo mismo sobre &sigma;. La diferencia en la desviación media es ruido. Fisher calculó además "
                "que, para igualar la precisión de la desviación típica, la desviación media necesita un 14 % más de "
                "observaciones. En su artículo de 1922 llamó a esta propiedad <b>suficiencia</b>."
            )

    with col_right:
        ui.right_panel()
        family = st.session_state["family"]
        rng = np.random.default_rng(v["seed"] + 17 * st.session_state["pairs"] + len(family))
        a, b, t_label = twin_samples(family, rng)
        mad_a, mad_b = np.mean(np.abs(a)), np.mean(np.abs(b))
        ui.metrics([(f"Las dos: {t_label}", "metric-c"),
                    (f"Desviación media A: {mad_a:.2f}", "metric-a"), (f"Desviación media B: {mad_b:.2f}", "metric-b")])
        ui.show(samples_chart(dark, a, b), key="fig_twins")
        ui.show(likelihood_chart(dark, family, a, b), key="fig_likelihoods")
        ui.footer_bar(f"Arriba, las dos muestras de la familia {FAMILIES[family].lower()}; abajo, sus verosimilitudes, "
                      "normalizadas para que el máximo valga 1. La curva discontinua cae exactamente sobre la gruesa.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>intensidad &lambda;</u> y el <u>número de observaciones n</u>")
        lam = st.slider("Muertes por cuerpo y año λ", 0.2, 2.0, v["lam"], 0.01, key=ui.wkey(PAGE, "lam"))
        n = st.select_slider("Cuerpos-año observados n", options=[5, 10, 20, 50, 200], value=v["n_rb"],
                             key=ui.wkey(PAGE, "n_rb"))

        ui.planteamiento()
        ui.statement(
            "<b>Las coces de Bortkiewicz</b><br><br>"
            f"Ladislaus von Bortkiewicz contó los soldados prusianos muertos por coces de caballo en diez cuerpos de "
            f"caballería durante veinte años: {DEATHS} muertes en {CORPS_YEARS} cuerpos-año, y 109 cuerpos-año sin "
            "ninguna. Queremos estimar &#8473;(X = 0) = e<sup>&minus;&lambda;</sup>, la probabilidad de un año sin "
            "muertes. El estimador natural es la proporción de ceros."
        )

        if ui.accordion_step("P3_A", "(A) El estimador de partida"):
            ui.content("¿Es insesgada la proporción de ceros? ¿Usa toda la información de la muestra?")
            ui.spoiler(
                "Es insesgada, porque cada indicatriz 1{X<sub>i</sub> = 0} tiene esperanza e<sup>&minus;&lambda;</sup>, y su "
                "varianza es e<sup>&minus;&lambda;</sup>(1 &minus; e<sup>&minus;&lambda;</sup>)/n. Pero no es función de "
                "T = &sum;X<sub>i</sub>, el estadístico suficiente: trata igual un año con una muerte y uno con tres, "
                "aunque esa diferencia sí informa sobre &lambda;."
            )

        if ui.accordion_step("P3_B", "(B) Condicionar a T"):
            ui.content(
                "Calcula E[1{X<sub>1</sub> = 0} | T = t]. Pista: dada la suma, cada una de las t muertes cae en un "
                "cuerpo-año al azar."
            )
            ui.spoiler(
                "Dada T = t, las muertes se reparten como una multinomial con n casillas iguales, así que el primer "
                "cuerpo-año queda vacío con probabilidad ((n &minus; 1)/n)<sup>t</sup>:"
                "<div class='formula-box'>T* = ( <sup>n &minus; 1</sup>&frasl;<sub>n</sub> )<sup>T</sup></div>"
                f"Con los datos de Bortkiewicz, (199/200)<sup>122</sup> = {(199 / 200) ** 122:.3f}, frente a la proporción "
                f"observada 109/200 = {109 / 200:.3f}."
            )

        if ui.accordion_step("P3_C", "(C) El teorema de Rao-Blackwell"):
            ui.content("Compara las varianzas de la derecha. ¿Qué garantiza el teorema? ¿Hay algún estimador insesgado mejor que T*?")
            ui.spoiler(
                "Rao (1945) y Blackwell (1947) probaron que condicionar un estimador insesgado a un estadístico suficiente "
                "da otro estimador insesgado con varianza menor o igual, por la ley de la varianza total. Como T es "
                "además completo, el teorema de Lehmann-Scheffé asegura que T* es el insesgado de varianza mínima. Su "
                "varianza, e<sup>&minus;2&lambda;</sup>(e<sup>&lambda;/n</sup> &minus; 1), roza la cota de Cramér-Rao "
                "&lambda;e<sup>&minus;2&lambda;</sup>/n sin alcanzarla."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + n + int(lam * 100))
        x = rng.poisson(lam, (4000, n))
        p0 = (x == 0).mean(axis=1)
        rb = ((n - 1) / n) ** x.sum(axis=1)
        target = np.exp(-lam)
        var_p0 = target * (1 - target) / n
        var_rb = np.exp(-2 * lam) * (np.exp(lam / n) - 1)
        cr = lam * np.exp(-2 * lam) / n
        ui.metrics([(f"&#120141; proporción: {ui.fmt_sci(var_p0, 2)}", "metric-c"),
                    (f"&#120141; Rao-Blackwell: {ui.fmt_sci(var_rb, 2)}", "metric-a"),
                    (f"Cota de Cramér-Rao: {ui.fmt_sci(cr, 2)}", "metric-b")])
        ui.show(rb_chart(dark, p0, rb, target), key="fig_rb")
        ui.footer_bar(f"4000 muestras simuladas de {n} cuerpos-año con &lambda; = {lam:.2f}. La línea roja es "
                      f"e<sup>&minus;&lambda;</sup> = {target:.3f}. La proporción de ceros solo toma {n + 1} valores; T* "
                      "aprovecha cada muerte.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El orden de las caras", "P1_A"),
        ("P2", "(II) Fisher contra Eddington", "P2_A"),
        ("P3", "(III) Las coces de Bortkiewicz", "P3_A"),
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
