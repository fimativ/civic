#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 3: la distribución muestral de un estadístico.

La proporción muestral en muestras grandes (los nacimientos de París que
estudió Laplace), la diferencia de medias de dos poblaciones normales (dos
abonos en Rothamsted) y la varianza muestral (Helmert, la ji cuadrado y la
independencia de media y varianza, que solo se da en la normal).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Distribución muestral"
PAGE = "00_03"

BOYS, GIRLS = 251527, 241945
REPS = 2000
POPULATIONS = {"normal": "Normal", "exponential": "Exponencial", "uniform": "Uniforme"}


def initial_values():
    return {
        "n_prop": ui.dchoice(50, [10, 20, 50, 200, 1000], "n_prop"),
        "p": ui.dfloat(0.10, 0.02, 0.5, "p"),
        "delta": round(2 * ui.dfloat(2.0, 0.0, 5.0, "delta", 1)) / 2,
        "n1": ui.dint(10, 4, 40, "n1"),
        "n2": ui.dint(10, 4, 40, "n2"),
        "s1": round(2 * ui.dfloat(4.0, 1.0, 8.0, "s1", 1)) / 2,
        "s2": round(2 * ui.dfloat(4.0, 1.0, 8.0, "s2", 1)) / 2,
        "n_var": ui.dchoice(10, [3, 5, 10, 30], "n_var"),
        "pop": ui.dchoice("normal", list(POPULATIONS), "pop"),
        "seed": int(ui.r("muestral") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "pop": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def draw(pop: str, size, rng):
    """Muestras con media 0 y varianza 1 de la población elegida."""
    if pop == "normal":
        return rng.standard_normal(size)
    if pop == "exponential":
        return rng.exponential(1.0, size) - 1.0
    return (rng.random(size) - 0.5) * np.sqrt(12)


EXCESS_KURTOSIS = {"normal": 0.0, "exponential": 6.0, "uniform": -1.2}


# =============================================================================
# 2. FIGURAS
# =============================================================================

def proportion_chart(dark, n, p):
    k = np.arange(n + 1)
    pmf = stats.binom.pmf(k, n, p)
    keep = pmf > 1e-6
    xs = k[keep] / n
    p_fig = ui.new_figure(dark, height=300, x_axis_label="proporción muestral p̂", y_axis_label="densidad")
    p_fig.vbar(x=xs, top=pmf[keep] * n, width=0.8 / n, color=ui.BLUE_LINE, alpha=0.6, legend_label="binomial exacta")
    se = np.sqrt(p * (1 - p) / n)
    grid = np.linspace(min(xs.min(), p - 4 * se), max(xs.max(), p + 4 * se), 300)
    p_fig.line(grid, stats.norm.pdf(grid, p, se), line_width=3, color=ui.UBU_RED, legend_label="aproximación normal")
    p_fig.add_layout(Span(location=0, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed"))
    return ui.style_legend(p_fig, dark, "top_right")


def difference_chart(dark, vals, mean, sd):
    edges = np.linspace(mean - 4.5 * sd, mean + 4.5 * sd, 45)
    h, _ = np.histogram(vals, bins=edges)
    p = ui.new_figure(dark, height=300, x_axis_label="X̄₁ − X̄₂ (kg por parcela)", y_axis_label="densidad")
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / (len(vals) * (edges[1] - edges[0])),
           fill_color=ui.BLUE_LINE, fill_alpha=0.5, line_color=ui.BLUE_LINE, legend_label="simulación")
    grid = np.linspace(edges[0], edges[-1], 300)
    p.line(grid, stats.norm.pdf(grid, mean, sd), line_width=3, color=ui.UBU_RED, legend_label="normal teórica")
    neg = grid[grid < 0]
    if neg.size:
        p.varea(x=neg, y1=0, y2=stats.norm.pdf(neg, mean, sd), fill_color=ui.ORANGE_LINE, fill_alpha=0.45)
    p.add_layout(Span(location=0, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed"))
    return ui.style_legend(p, dark, "top_left")


def scatter_chart(dark, means, sds):
    p = ui.new_figure(dark, height=280, x_axis_label="media X̄", y_axis_label="desviación S")
    p.scatter(means, sds, size=4, color=ui.BLUE_LINE, alpha=0.35)
    return p


def chi2_chart(dark, q, n):
    hi = np.percentile(q, 99.5)
    edges = np.linspace(0, hi, 40)
    h, _ = np.histogram(q, bins=edges)
    p = ui.new_figure(dark, height=260, x_axis_label="(n − 1) S² / σ²", y_axis_label="densidad")
    p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=h / (len(q) * (edges[1] - edges[0])),
           fill_color=ui.GREEN_LINE, fill_alpha=0.5, line_color=ui.GREEN_LINE, legend_label="simulación")
    grid = np.linspace(0.01, hi, 300)
    p.line(grid, stats.chi2.pdf(grid, n - 1), line_width=3, color=ui.UBU_RED, legend_label=f"ji cuadrado, {n - 1} g.l.")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se distribuye un estadístico?</b>")
        ui.content(
            "La <b>distribución muestral</b> de un estadístico T es su distribución como variable aleatoria: la que se "
            "observaría si se repitiera el muestreo muchas veces. De ella sale todo lo demás: el error típico de una "
            "estimación, los intervalos de confianza, los p-valores. A veces se conoce exactamente, como en las "
            "poblaciones normales; otras, solo en el límite, gracias al teorema central del límite. <i>¿Qué dice ese "
            "teorema de la media muestral?</i>"
        )
        ui.formula_hidden("<sup>X̄ &minus; &mu;</sup>&frasl;<sub>&sigma;/&radic;n</sub> &rarr; N(0, 1) en distribución")
        ui.content(
            "Las tres situaciones recorren los casos que más se usan: una proporción con muestras grandes, la diferencia "
            "de dos medias en poblaciones normales y la varianza muestral, que esconde una sorpresa."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los niños de París (1781)</b><br>"
            "<i>Decide con Laplace si nacen más niños que niñas a partir de casi medio millón de bautizos.</i><br><br>"
            "<b>II. Dos abonos en Rothamsted (1919)</b><br>"
            "<i>Compara dos fertilizantes como en la estación agrícola donde trabajó Fisher, y calcula la probabilidad "
            "de que el peor parezca el mejor.</i><br><br>"
            "<b>III. Helmert y la varianza (1876)</b><br>"
            "<i>Descubre la ji cuadrado escondida en S<sup>2</sup> y una propiedad que solo tiene la normal.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>proporción p</u> y el <u>tamaño n</u>")
        p = st.slider("Proporción de la población p", 0.01, 0.99, v["p"], 0.01, key=ui.wkey(PAGE, "p"))
        n = st.select_slider("Tamaño de la muestra n", options=[10, 20, 50, 200, 1000], value=v["n_prop"],
                             key=ui.wkey(PAGE, "n_prop"))

        ui.planteamiento()
        n_tot = BOYS + GIRLS
        ui.statement(
            "<b>Los niños de París (1781)</b><br><br>"
            f"Pierre-Simon Laplace reunió los bautizos de París entre 1745 y 1770: {ui.fmt_int(BOYS)} niños y "
            f"{ui.fmt_int(GIRLS)} niñas, {ui.fmt_int(n_tot)} en total. La proporción de niños, {BOYS / n_tot:.4f}, "
            "supera la mitad. ¿Puede ser casualidad? Para responder hace falta saber cómo varía la proporción muestral "
            "p̂ cuando la proporción real es p."
        )

        if ui.accordion_step("P1_A", "(A) La distribución de p̂"):
            ui.content(
                "n&middot;p̂ cuenta los éxitos de n pruebas independientes. ¿Cuáles son la esperanza y la varianza de p̂? "
                "¿A qué distribución se acerca cuando n es grande?"
            )
            ui.spoiler(
                "n&middot;p̂ es binomial de parámetros n y p, así que E[p̂] = p y &#120141;(p̂) = p(1 &minus; p)/n. Por el "
                "teorema de De Moivre-Laplace, el caso binomial del teorema central del límite:"
                "<div class='formula-box'>p̂ &asymp; N( p, <sup>p(1 &minus; p)</sup>&frasl;<sub>n</sub> )</div>"
            )

        if ui.accordion_step("P1_B", "(B) La respuesta a Laplace"):
            ui.content(
                "Si nacieran niños y niñas con la misma probabilidad, p = 1/2. ¿A cuántos errores típicos de 1/2 está la "
                "proporción observada?"
            )
            ui.spoiler(
                f"El error típico es &radic;(0.25/{ui.fmt_int(n_tot)}) &asymp; 0.00071, y la proporción observada está a "
                "más de trece errores típicos de 1/2. Bajo la normal, una desviación así tiene una probabilidad de orden "
                "10<sup>&minus;42</sup>. Laplace concluyó que nacen más niños que niñas, y la razón de unos 105 niños por cada "
                "100 niñas se sigue observando hoy."
            )

        if ui.accordion_step("P1_C", "(C) Cuándo falla"):
            ui.content(
                "Pon p = 0.02 y n = 50. ¿Se parece la binomial a la campana? ¿Qué regla práctica decide si la "
                "aproximación es aceptable?"
            )
            ui.spoiler(
                "Con n&middot;p = 1 la binomial es muy asimétrica y la normal da probabilidad positiva a proporciones "
                "negativas. La regla habitual pide n&middot;p &ge; 5 y n&middot;(1 &minus; p) &ge; 5. Para sucesos raros es "
                "mejor la aproximación de Poisson, o trabajar con la binomial exacta."
            )

    with col_right:
        ui.right_panel()
        se = np.sqrt(p * (1 - p) / n)
        ok = n * p >= 5 and n * (1 - p) >= 5
        ui.metrics([(f"E[p̂] = {p:.2f}", "metric-a"), (f"Error típico: {se:.4f}", "metric-b"),
                    (f"n&middot;p = {n * p:.1f}", "metric-c")])
        ui.check(ok, "La aproximación normal es razonable" if ok else "n&middot;p o n&middot;(1 &minus; p) por debajo de 5")
        ui.show(proportion_chart(dark, n, p), key="fig_prop")
        ui.footer_bar("Barras: la distribución exacta de p̂ (binomial dividida entre n). Curva roja: la normal con la "
                      "misma media y la misma varianza.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>diferencia real</u>, las <u>desviaciones</u> y los <u>tamaños</u>")
        delta = st.slider("Diferencia real μ₁ − μ₂ (kg)", 0.0, 6.0, v["delta"], 0.5, key=ui.wkey(PAGE, "delta"))
        c1, c2 = st.columns(2)
        with c1:
            n1 = st.slider("Parcelas con el abono 1", 2, 40, v["n1"], 1, key=ui.wkey(PAGE, "n1"))
            s1 = st.slider("σ₁ (kg)", 1.0, 8.0, v["s1"], 0.5, key=ui.wkey(PAGE, "s1"))
        with c2:
            n2 = st.slider("Parcelas con el abono 2", 2, 40, v["n2"], 1, key=ui.wkey(PAGE, "n2"))
            s2 = st.slider("σ₂ (kg)", 1.0, 8.0, v["s2"], 0.5, key=ui.wkey(PAGE, "s2"))

        ui.planteamiento()
        ui.statement(
            "<b>Dos abonos en Rothamsted (1919)</b><br><br>"
            "En 1919 Ronald Fisher entró en la estación agrícola de Rothamsted, en Inglaterra, que llevaba más de setenta "
            "años abonando parcelas de trigo de formas distintas. Comparamos dos abonos: la cosecha de cada parcela es "
            "normal, de media &mu;<sub>1</sub> o &mu;<sub>2</sub> y desviación &sigma;<sub>1</sub> o &sigma;<sub>2</sub>, y "
            "se compara la media de las parcelas de cada abono."
        )

        if ui.accordion_step("P2_A", "(A) La distribución de la diferencia"):
            ui.content("¿Qué distribución tiene X̄<sub>1</sub> &minus; X̄<sub>2</sub>? ¿Por qué se suman las varianzas aunque se resten las medias?")
            ui.spoiler(
                "Cada media es normal, y las dos son independientes. Por la propiedad reproductiva de la normal, cualquier "
                "combinación lineal de normales independientes es normal; la varianza de una diferencia es la suma de "
                "las varianzas, porque &#120141;(&minus;Y) = &#120141;(Y):"
                "<div class='formula-box'>X̄<sub>1</sub> &minus; X̄<sub>2</sub> ~ N( &mu;<sub>1</sub> &minus; &mu;<sub>2</sub>, "
                "<sup>&sigma;<sub>1</sub><sup>2</sup></sup>&frasl;<sub>n<sub>1</sub></sub> + "
                "<sup>&sigma;<sub>2</sub><sup>2</sup></sup>&frasl;<sub>n<sub>2</sub></sub> )</div>"
            )

        if ui.accordion_step("P2_B", "(B) El peor parece el mejor"):
            ui.content(
                "El abono 1 es mejor, pero en un experimento concreto puede salir X̄<sub>1</sub> &lt; X̄<sub>2</sub>. ¿Con "
                "qué probabilidad? Con un total de parcelas fijo, ¿cómo conviene repartirlas?"
            )
            ui.spoiler(
                "Tipificando, &#8473;(X̄<sub>1</sub> &lt; X̄<sub>2</sub>) = &Phi;( &minus;(&mu;<sub>1</sub> &minus; "
                "&mu;<sub>2</sub>) / &radic;(&sigma;<sub>1</sub><sup>2</sup>/n<sub>1</sub> + "
                "&sigma;<sub>2</sub><sup>2</sup>/n<sub>2</sub>) ): el área naranja. Con n<sub>1</sub> + n<sub>2</sub> fijo, "
                "la varianza es mínima cuando n<sub>1</sub>/n<sub>2</sub> = &sigma;<sub>1</sub>/&sigma;<sub>2</sub>: más "
                "parcelas para el abono más irregular, la misma idea que el reparto de Neyman en el muestreo "
                "estratificado."
            )

        if ui.accordion_step("P2_C", "(C) Sin conocer las desviaciones"):
            ui.content(
                "En la práctica &sigma;<sub>1</sub> y &sigma;<sub>2</sub> son desconocidas y se sustituyen por S<sub>1</sub> y "
                "S<sub>2</sub>. ¿Sigue siendo normal el cociente tipificado?"
            )
            ui.spoiler(
                "No: pasa a ser una t de Student. Si las dos varianzas son iguales, la varianza combinada da una t exacta "
                "con n<sub>1</sub> + n<sub>2</sub> &minus; 2 grados de libertad. Si son distintas no hay solución exacta "
                "sencilla, el llamado problema de Behrens-Fisher, y se usa la aproximación de Welch, con unos grados de "
                "libertad calculados a partir de los datos."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + n1 * 41 + n2)
        sd = np.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
        x1 = rng.normal(delta, s1, (REPS, n1)).mean(axis=1)
        x2 = rng.normal(0, s2, (REPS, n2)).mean(axis=1)
        wrong = stats.norm.cdf(-delta / sd)
        ui.metrics([(f"Error típico: {sd:.2f} kg", "metric-a"), (f"&#8473;(X̄₁ &lt; X̄₂) = {wrong:.3f}", "metric-b"),
                    (f"Simulado: {(x1 < x2).mean():.3f}", "metric-c")])
        ui.show(difference_chart(dark, x1 - x2, delta, sd), key="fig_diff")
        total = n1 + n2
        best = round(total * s1 / (s1 + s2))
        ui.footer_bar(f"{REPS} experimentos simulados. Con {total} parcelas en total, el reparto que minimiza el error "
                      f"típico es de unas {best} y {total - best}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>población</u> y el <u>tamaño n</u>")
        if st.session_state["pop"] is None:
            st.session_state["pop"] = v["pop"]
        ui.choice_buttons(list(POPULATIONS), "pop", labels=POPULATIONS, per_row=3)
        n = st.select_slider("Tamaño de cada muestra", options=[3, 5, 10, 30], value=v["n_var"],
                             key=ui.wkey(PAGE, "n_var"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Helmert y la varianza (1876)</b><br><br>"
            "El geodesta alemán Friedrich Helmert estudiaba los errores de las medidas de triangulación. En 1876 encontró "
            "la distribución de la suma de cuadrados de los residuos de una muestra normal, la que hoy llamamos "
            "<b>ji cuadrado</b>. Tomamos muchas muestras de tamaño n, todas con varianza &sigma;<sup>2</sup> = 1, y "
            "comparamos tres poblaciones."
        )

        if ui.accordion_step("P3_A", "(A) La ji cuadrado"):
            ui.content(
                "Con la población normal, ¿qué distribución sigue (n &minus; 1)S<sup>2</sup>/&sigma;<sup>2</sup>? ¿Por qué "
                "se pierde un grado de libertad?"
            )
            ui.spoiler(
                "Sigue una ji cuadrado con n &minus; 1 grados de libertad, la suma de n &minus; 1 cuadrados de normales "
                "tipificadas independientes. Los n residuos X<sub>i</sub> &minus; X̄ suman cero, así que solo n &minus; 1 "
                "son libres. Por eso E[S<sup>2</sup>] = &sigma;<sup>2</sup> exactamente al dividir entre n &minus; 1."
            )

        if ui.accordion_step("P3_B", "(B) Media y desviación independientes"):
            ui.content(
                "La nube de la derecha enfrenta la media y la desviación de cada muestra. Compara la forma de la nube en las "
                "tres poblaciones. ¿En cuál son independientes?"
            )
            ui.spoiler(
                "Solo en la normal. Allí X̄ y S<sup>2</sup> son independientes, el resultado que permite que la t de Student "
                "tenga una distribución exacta. Es una caracterización: si X̄ y S<sup>2</sup> son independientes, la "
                "población es normal (Geary, 1936; Lukacs, 1942). En la exponencial, las muestras con media alta tienen "
                "desviación alta; en la uniforme la correlación es nula y aun así la nube no es independiente: las "
                "medias extremas solo aparecen con desviaciones pequeñas."
            )

        if ui.accordion_step("P3_C", "(C) Fuera de la normal"):
            ui.content(
                "Con la exponencial, el histograma verde se separa de la curva. ¿De qué depende la varianza de "
                "S<sup>2</sup> en general?"
            )
            ui.spoiler(
                "De la curtosis de la población. Con &kappa; el exceso de curtosis (0 en la normal):"
                "<div class='formula-box'>&#120141;(S<sup>2</sup>) = &sigma;<sup>4</sup>( <sup>2</sup>&frasl;<sub>n &minus; 1</sub> + "
                "<sup>&kappa;</sup>&frasl;<sub>n</sub> )</div>"
                "La exponencial tiene &kappa; = 6, y S<sup>2</sup> varía mucho más de lo que predice la ji cuadrado. Los "
                "intervalos y tests para varianzas basados en la normal son muy sensibles a esta hipótesis, mucho más "
                "que los de medias."
            )

    with col_right:
        ui.right_panel()
        pop = st.session_state["pop"]
        rng = np.random.default_rng(v["seed"] + 3 * n)
        x = draw(pop, (REPS, n), rng)
        means, sds = x.mean(axis=1), x.std(axis=1, ddof=1)
        rho = np.corrcoef(means, sds)[0, 1]
        var_s2 = 2 / (n - 1) + EXCESS_KURTOSIS[pop] / n
        ui.metrics([(f"Correlación X̄, S: {rho:.2f}", "metric-a"),
                    (f"&#120141;(S²) simulada: {np.var(sds ** 2):.2f}", "metric-b"),
                    (f"Fórmula: {var_s2:.2f}", "metric-c")])
        ui.show(scatter_chart(dark, means, sds), key="fig_scatter")
        ui.show(chi2_chart(dark, (n - 1) * sds ** 2, n), key="fig_chi2")
        ui.footer_bar(f"{REPS} muestras de tamaño {n} de la población {POPULATIONS[pop].lower()}, con media 0 y varianza 1. "
                      "Arriba, la media y la desviación de cada muestra; abajo, la varianza escalada frente a la ji cuadrado.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los niños de París", "P1_A"),
        ("P2", "(II) Dos abonos en Rothamsted", "P2_A"),
        ("P3", "(III) Helmert y la varianza", "P3_A"),
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
