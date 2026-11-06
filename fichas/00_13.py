#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 13: regresión lineal simple y su validación.

El ajuste por mínimos cuadrados de la ley de Hubble (a mano y con las
ecuaciones normales), el diagnóstico gráfico de los residuos con un muelle de
Hooke en cinco escenarios, y los tests formales de falta de ajuste (con
réplicas) y de heterocedasticidad (Breusch-Pagan).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Regresión lineal"
PAGE = "00_13"

GALAXIES = 24
SCENARIOS = {"ok": "Correcto", "curve": "Curvatura", "funnel": "Embudo", "influential": "Atípico influyente",
             "skew": "Errores asimétricos"}
LOADS = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0])
REPLICATES = 4


def initial_values():
    return {
        "b1": 5 * round(ui.dint(450, 200, 800, "b1") / 5),
        "b0": 5 * round(ui.dint(0, -200, 200, "b0") / 5),
        "scenario": ui.dchoice("curve", list(SCENARIOS), "scenario"),
        "curv": round(ui.dfloat(0.08, 0.0, 0.2, "curv", 2) * 100) / 100,
        "het": round(ui.dfloat(0.0, 0.0, 0.2, "het", 2) * 100) / 100,
        "seed": int(ui.r("regresion") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "scenario": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def ols(x, y):
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b1 = ((x - xm) * (y - ym)).sum() / sxx
    b0 = ym - b1 * xm
    fitted = b0 + b1 * x
    e = y - fitted
    n = len(x)
    s2 = (e ** 2).sum() / (n - 2)
    h = 1 / n + (x - xm) ** 2 / sxx
    return {"b0": b0, "b1": b1, "fitted": fitted, "e": e, "s2": s2, "sxx": sxx, "h": h,
            "r2": 1 - (e ** 2).sum() / ((y - ym) ** 2).sum()}


def hubble_data(seed):
    rng = np.random.default_rng(seed)
    d = np.sort(rng.uniform(0.03, 2.0, GALAXIES))
    v = 500 * d + rng.normal(0, 180, GALAXIES)
    return d, v


def spring_data(scenario, seed, n=40):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(0.5, 5, n))
    if scenario == "curve":
        return x, 2 * x + 0.25 * x ** 2 + rng.normal(0, 0.3, n)
    if scenario == "funnel":
        return x, 2 * x + rng.normal(0, 0.12 * x ** 1.3, n)
    if scenario == "influential":
        y = 2 * x + rng.normal(0, 0.3, n)
        x = np.append(x, 12.0)
        return x, np.append(y, 15.0)
    if scenario == "skew":
        return x, 2 * x + rng.exponential(0.5, n) - 0.5
    return x, 2 * x + rng.normal(0, 0.3, n)


def replicate_data(curv, het, seed):
    rng = np.random.default_rng(seed)
    x = np.repeat(LOADS, REPLICATES)
    sd = 0.15 + het * x ** 1.5
    return x, 2 * x + curv * x ** 2 + rng.normal(0, 1, x.size) * sd


def lack_of_fit(x, y, fit):
    levels = np.unique(x)
    ss_pe = sum(((y[x == u] - y[x == u].mean()) ** 2).sum() for u in levels)
    sse = (fit["e"] ** 2).sum()
    ss_lof = sse - ss_pe
    m, N = len(levels), len(x)
    F = (ss_lof / (m - 2)) / (ss_pe / (N - m))
    return F, m - 2, N - m, stats.f.sf(F, m - 2, N - m)


def breusch_pagan(x, fit):
    """Versión studentizada de Koenker: n·R² de la regresión de e² sobre x."""
    e2 = fit["e"] ** 2
    aux = ols(x, e2)
    lm = len(x) * aux["r2"]
    return lm, stats.chi2.sf(lm, 1)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def fit_chart(dark, x, y, lines, x_label, y_label, height=300):
    p = ui.new_figure(dark, height=height, x_axis_label=x_label, y_axis_label=y_label)
    p.scatter(x, y, size=8, color=ui.BLUE_LINE, alpha=0.7)
    xs = np.array([min(0, x.min()), x.max() * 1.05])
    for (b0, b1, label, colour, dash) in lines:
        p.line(xs, b0 + b1 * xs, line_width=3, color=colour, line_dash=dash, legend_label=label)
    return ui.style_legend(p, dark, "top_left")


def residual_chart(dark, fitted, e, height=230):
    p = ui.new_figure(dark, height=height, x_axis_label="valor ajustado ŷ", y_axis_label="residuo e")
    p.scatter(fitted, e, size=7, color=ui.PURPLE_LINE, alpha=0.75)
    p.add_layout(Span(location=0, dimension="width", line_color=ui.UBU_RED, line_width=2))
    return p


def qq_chart(dark, e, height=230):
    z = np.sort((e - e.mean()) / e.std(ddof=1))
    n = len(z)
    q = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    p = ui.new_figure(dark, height=height, x_axis_label="cuantil normal", y_axis_label="residuo tipificado")
    p.scatter(q, z, size=7, color=ui.GREEN_LINE, alpha=0.8)
    lim = max(abs(q).max(), abs(z).max())
    p.line([-lim, lim], [-lim, lim], line_width=2, color=ui.UBU_RED, line_dash="dashed")
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué recta resume mejor una nube de puntos?</b>")
        ui.content(
            "El modelo de <b>regresión lineal simple</b> supone que la respuesta es una recta más un error: "
            "Y<sub>i</sub> = &beta;<sub>0</sub> + &beta;<sub>1</sub>x<sub>i</sub> + &epsilon;<sub>i</sub>, con errores "
            "independientes, de media cero, la misma varianza &sigma;<sup>2</sup> y, para la inferencia, normales. La recta "
            "de <b>mínimos cuadrados</b> minimiza la suma de los cuadrados de los residuos. <i>¿Qué coeficientes da?</i>"
        )
        ui.formula_hidden("b<sub>1</sub> = <sup>S<sub>xy</sub></sup>&frasl;<sub>S<sub>xx</sub></sub>, &nbsp; "
                          "b<sub>0</sub> = ȳ &minus; b<sub>1</sub>x̄")
        ui.content(
            "Calcular la recta siempre es posible; que el modelo sea válido, no. Por eso un ajuste no termina con los "
            "coeficientes: hay que <b>validarlo</b> mirando los residuos, que deben parecerse a los errores que el modelo "
            "supone."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La ley de Hubble (1929)</b><br>"
            "<i>Ajusta a mano la recta entre distancia y velocidad de las galaxias y compárala con la de mínimos "
            "cuadrados.</i><br><br>"
            "<b>II. El muelle de Hooke</b><br>"
            "<i>Lee las gráficas de residuos de cinco experimentos y diagnostica qué falla en cada uno.</i><br><br>"
            "<b>III. Falta de ajuste y homocedasticidad</b><br>"
            "<i>Pon a prueba el modelo con réplicas y con el test de Breusch-Pagan.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()
    d, vel = hubble_data(v["seed"])
    fit = ols(d, vel)

    with col_left:
        ui.left_panel()
        ui.try_it("ajusta a mano la <u>pendiente</u> y la <u>ordenada en el origen</u>")
        b1 = st.slider("Pendiente (km/s por megaparsec)", 200, 800, v["b1"], 5, key=ui.wkey(PAGE, "b1"))
        b0 = st.slider("Ordenada en el origen (km/s)", -300, 300, v["b0"], 5, key=ui.wkey(PAGE, "b0"))

        ui.planteamiento()
        ui.statement(
            "<b>La ley de Hubble (1929)</b><br><br>"
            "Edwin Hubble comparó la distancia de 24 galaxias con la velocidad a la que se alejan, medida por el "
            "desplazamiento al rojo de su luz, y encontró una relación lineal: cuanto más lejos, más deprisa. La pendiente "
            "es la constante de Hubble. Simulamos 24 galaxias con una dispersión parecida a la de sus datos."
        )

        if ui.accordion_step("P1_A", "(A) Las ecuaciones normales"):
            ui.content("Minimiza S(b<sub>0</sub>, b<sub>1</sub>) = &sum;(y<sub>i</sub> &minus; b<sub>0</sub> &minus; b<sub>1</sub>x<sub>i</sub>)<sup>2</sup>. ¿Qué dos ecuaciones salen?")
            ui.spoiler(
                "Igualando a cero las derivadas parciales:"
                "<div class='formula-box'>&sum;e<sub>i</sub> = 0, &nbsp;&nbsp; &sum;x<sub>i</sub>e<sub>i</sub> = 0</div>"
                "con e<sub>i</sub> = y<sub>i</sub> &minus; b<sub>0</sub> &minus; b<sub>1</sub>x<sub>i</sub>. Los residuos suman cero "
                "y no están correlacionados con x. De ahí salen b<sub>1</sub> = S<sub>xy</sub>/S<sub>xx</sub> y "
                "b<sub>0</sub> = ȳ &minus; b<sub>1</sub>x̄: la recta pasa por el punto (x̄, ȳ)."
            )

        if ui.accordion_step("P1_B", "(B) Cuánto explica"):
            ui.content("¿Qué mide R<sup>2</sup>? ¿Qué relación tiene con el coeficiente de correlación?")
            ui.spoiler(
                "La variabilidad total se descompone en la explicada por la recta y la residual: SCT = SCE + SCR. "
                "R<sup>2</sup> = SCE/SCT es la proporción explicada, y en regresión simple coincide con r<sup>2</sup>. Un "
                "R<sup>2</sup> alto no valida el modelo por sí solo: la situación siguiente muestra casos con R<sup>2</sup> "
                "alto y modelo inadecuado."
            )

        if ui.accordion_step("P1_C", "(C) El error de la pendiente"):
            ui.content("¿Cuál es el error típico de b<sub>1</sub>? Construye un intervalo al 95 % para la constante de Hubble.")
            ui.spoiler(
                "Con s<sup>2</sup> = SCR/(n &minus; 2), el error típico es s/&radic;S<sub>xx</sub>, y (b<sub>1</sub> &minus; "
                "&beta;<sub>1</sub>)/(s/&radic;S<sub>xx</sub>) es una t con n &minus; 2 grados de libertad:"
                "<div class='formula-box'>b<sub>1</sub> &plusmn; t<sub>n &minus; 2, 0.025</sub><sup>s</sup>&frasl;<sub>&radic;S<sub>xx</sub></sub></div>"
                "Hubble obtuvo unos 500 km/s por megaparsec, unas siete veces el valor actual: sus distancias estaban mal "
                "calibradas. El intervalo solo recoge el error aleatorio, no el sistemático."
            )

    with col_right:
        ui.right_panel()
        sse_user = ((vel - b0 - b1 * d) ** 2).sum()
        sse_ls = (fit["e"] ** 2).sum()
        se_b1 = np.sqrt(fit["s2"] / fit["sxx"])
        tq = stats.t.isf(0.025, GALAXIES - 2)
        ui.metrics([(f"Tu suma de cuadrados: {ui.fmt_int(sse_user)}", "metric-c"),
                    (f"Mínimos cuadrados: {ui.fmt_int(sse_ls)}", "metric-a"),
                    (f"b<sub>1</sub> = {fit['b1']:.0f} &plusmn; {tq * se_b1:.0f}, R<sup>2</sup> = {fit['r2']:.3f}", "metric-b")])
        ui.show(fit_chart(dark, d, vel, [(b0, b1, "tu recta", ui.ORANGE_LINE, "dashed"),
                                         (fit["b0"], fit["b1"], "mínimos cuadrados", ui.UBU_RED, "solid")],
                          "distancia (megaparsecs)", "velocidad (km/s)"), key="fig_hubble")
        ui.footer_bar(f"24 galaxias simuladas. Tu recta tiene una suma de cuadrados {sse_user / sse_ls:.2f} veces la mínima. "
                      f"b<sub>0</sub> = {fit['b0']:.0f} km/s.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>experimento</u>")
        if st.session_state["scenario"] is None:
            st.session_state["scenario"] = v["scenario"]
        ui.choice_buttons(list(SCENARIOS), "scenario", labels=SCENARIOS, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>El muelle de Hooke</b><br><br>"
            "En 1678 Robert Hooke resumió su ley en latín: <i>ut tensio, sic vis</i>, como la extensión, así la fuerza. "
            "Colgamos pesos de un muelle y medimos cuánto se estira. Cinco laboratorios hacen el experimento, y en cada uno "
            "algo puede salir mal. Ajustamos siempre una recta y miramos tres gráficas: el ajuste, los residuos frente a los "
            "valores ajustados y los residuos frente a los cuantiles de la normal."
        )

        if ui.accordion_step("P2_A", "(A) Residuos frente a ajustados"):
            ui.content("Compara Correcto con Curvatura. ¿Qué forma deberían tener los residuos? ¿Qué indica una sonrisa?")
            ui.spoiler(
                "Si el modelo es correcto, los residuos forman una banda horizontal sin estructura alrededor de cero. Una "
                "forma de U indica <b>falta de ajuste</b>: la relación no es lineal, aquí porque el muelle ha pasado su "
                "límite elástico. Fíjate en que el R<sup>2</sup> sigue siendo altísimo: no detecta el problema. Remedios: un "
                "término cuadrático, una transformación o un modelo físico mejor."
            )

        if ui.accordion_step("P2_B", "(B) El embudo"):
            ui.content("Elige Embudo. ¿Qué hipótesis falla? ¿Siguen siendo válidos los coeficientes y sus errores típicos?")
            ui.spoiler(
                "La dispersión crece con la carga: falla la <b>homocedasticidad</b>. Los coeficientes de mínimos cuadrados "
                "siguen siendo insesgados, pero ya no son los de menor varianza (el teorema de Gauss-Markov exige varianza "
                "constante), y la fórmula s/&radic;S<sub>xx</sub> da errores típicos equivocados. Se corrige con mínimos "
                "cuadrados ponderados, transformando la respuesta o con errores típicos robustos."
            )

        if ui.accordion_step("P2_C", "(C) Atípicos y normalidad"):
            ui.content("Elige Atípico influyente y Errores asimétricos. ¿Qué gráfica delata cada problema?")
            ui.spoiler(
                "El punto de carga 12 está lejos en x, tiene mucho <b>apalancamiento</b> y arrastra la recta hacia él. Su "
                "<b>distancia de Cook</b>, que mide cuánto cambiarían los coeficientes al quitarlo, es muy superior a 1. Los "
                "errores asimétricos se ven en el gráfico de cuantiles, que se curva en un extremo. La normalidad importa "
                "para intervalos y tests con muestras pequeñas; con muestras grandes, el teorema central del límite la "
                "hace menos crítica."
            )

    with col_right:
        ui.right_panel()
        scenario = st.session_state["scenario"]
        x, y = spring_data(scenario, v["seed"] + len(scenario))
        fit = ols(x, y)
        cook = fit["e"] ** 2 / (2 * fit["s2"]) * fit["h"] / (1 - fit["h"]) ** 2
        lm, bp = breusch_pagan(x, fit)
        ui.metrics([(f"R<sup>2</sup> = {fit['r2']:.3f}", "metric-a"), (f"Cook máx: {cook.max():.2f}", "metric-b"),
                    (f"Breusch-Pagan p = {bp:.3f}", "metric-c")])
        ui.show(fit_chart(dark, x, y, [(fit["b0"], fit["b1"], "recta ajustada", ui.UBU_RED, "solid")], "carga (N)",
                          "extensión (cm)", height=260), key="fig_spring")
        ui.show(residual_chart(dark, fit["fitted"], fit["e"]), key="fig_resid")
        ui.show(qq_chart(dark, fit["e"]), key="fig_qq")
        ui.footer_bar(f"Experimento «{SCENARIOS[scenario]}». Arriba, los datos y la recta; en medio, los residuos frente a los "
                      "valores ajustados; abajo, los residuos tipificados frente a los cuantiles normales.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>curvatura</u> y la <u>heterocedasticidad</u> reales")
        curv = st.slider("Curvatura real (término en x²)", 0.0, 0.2, v["curv"], 0.01, key=ui.wkey(PAGE, "curv"))
        het = st.slider("Heterocedasticidad (crecimiento de σ con la carga)", 0.0, 0.2, v["het"], 0.01,
                        key=ui.wkey(PAGE, "het"))

        ui.planteamiento()
        ui.statement(
            "<b>Falta de ajuste y homocedasticidad</b><br><br>"
            f"Repetimos el experimento del muelle con {len(LOADS)} cargas fijas y {REPLICATES} medidas en cada una. Las "
            "<b>réplicas</b> permiten separar el error puro del experimento de la falta de ajuste de la recta. Además "
            "contrastamos si la varianza de los errores cambia con la carga."
        )

        if ui.accordion_step("P3_A", "(A) El test de falta de ajuste"):
            ui.content(
                "La suma de cuadrados residual se descompone en error puro (dentro de cada carga) y falta de ajuste (las "
                "medias de cada carga frente a la recta). ¿Qué estadístico compara las dos?"
            )
            ui.spoiler(
                "Con m cargas distintas y N medidas:"
                "<div class='formula-box'>F = <sup>SC<sub>FA</sub>/(m &minus; 2)</sup>&frasl;<sub>SC<sub>EP</sub>/(N &minus; m)</sub> "
                "~ F<sub>m &minus; 2, N &minus; m</sub></div>"
                "El error puro estima &sigma;<sup>2</sup> pase lo que pase; la falta de ajuste solo lo hace si la recta es "
                "correcta. Un F grande indica que las medias de cada carga no están sobre una recta. Sin réplicas, este test "
                "no es posible."
            )

        if ui.accordion_step("P3_B", "(B) El test de Breusch-Pagan"):
            ui.content("¿Cómo se contrasta si la varianza depende de x, usando solo los residuos?")
            ui.spoiler(
                "Trevor Breusch y Adrian Pagan (1979) propusieron hacer una regresión auxiliar de los residuos al cuadrado "
                "sobre x. Si la varianza es constante, x no debería explicar nada. En la versión de Koenker, el estadístico "
                "n&middot;R<sup>2</sup> de esa regresión auxiliar sigue aproximadamente una ji cuadrado con un grado de "
                "libertad."
            )

        if ui.accordion_step("P3_C", "(C) Tests y gráficas"):
            ui.content("Con curvatura 0.02 el test de falta de ajuste suele no rechazar, aunque la curvatura existe. ¿Está validado el modelo?")
            ui.spoiler(
                "No rechazar no prueba que el modelo sea correcto: con 28 medidas, el test no tiene potencia para "
                "curvaturas pequeñas. Y con miles de datos rechazaría desviaciones sin importancia práctica. Los tests "
                "complementan a las gráficas de residuos, no las sustituyen: la validación es mirar el modelo desde varios "
                "lados y decidir si es útil para lo que se quiere hacer con él."
            )

    with col_right:
        ui.right_panel()
        x, y = replicate_data(curv, het, v["seed"] + int(curv * 100) * 31 + int(het * 100))
        fit = ols(x, y)
        F, d1, d2, p_lof = lack_of_fit(x, y, fit)
        lm, p_bp = breusch_pagan(x, fit)
        ui.metrics([(f"Falta de ajuste: F = {F:.2f}, p = {ui.fmt_sci(p_lof, 2)}", "result-no" if p_lof < 0.05 else "metric-a"),
                    (f"Breusch-Pagan: {lm:.2f}, p = {ui.fmt_sci(p_bp, 2)}", "result-no" if p_bp < 0.05 else "metric-b"),
                    (f"R<sup>2</sup> = {fit['r2']:.4f}", "metric-c")])
        ui.show(fit_chart(dark, x, y, [(fit["b0"], fit["b1"], "recta ajustada", ui.UBU_RED, "solid")], "carga (N)",
                          "extensión (cm)", height=260), key="fig_replicates")
        ui.show(residual_chart(dark, fit["fitted"], fit["e"]), key="fig_resid3")
        ui.footer_bar(f"{len(x)} medidas, {REPLICATES} por carga. En rojo, los tests que rechazan al 5 %. Fíjate en que "
                      "R<sup>2</sup> apenas cambia mientras el modelo falla.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La ley de Hubble", "P1_A"),
        ("P2", "(II) El muelle de Hooke", "P2_A"),
        ("P3", "(III) Falta de ajuste", "P3_A"),
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
