#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 11: análisis de la varianza de un factor.

La descomposición de Fisher de la variabilidad en tres abonos para patatas,
cómo influyen en la decisión las diferencias de medias, los tamaños y las
varianzas muestrales, y qué le pasa al test F cuando los grupos tienen
varianzas distintas y tamaños desiguales.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "ANOVA de un factor"
PAGE = "00_11"

GROUPS = ("A", "B", "C")
COLOURS = (ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE)
SIMS = 4000


def initial_values():
    return {
        "mA": ui.dint(20, 15, 25, "mA"),
        "mB": ui.dint(22, 15, 25, "mB"),
        "mC": ui.dint(23, 15, 25, "mC"),
        "n": ui.dint(8, 3, 30, "n"),
        "s": ui.dint(4, 1, 10, "s"),
        "nC": ui.dint(4, 2, 40, "nC"),
        "sC": round(2 * ui.dfloat(3.0, 1.0, 4.0, "sC", 1)) / 2,
        "seed": int(ui.r("anova") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def groups_with(means, sds, ns, seed):
    """Datos con medias y desviaciones muestrales exactamente iguales a las pedidas."""
    rng = np.random.default_rng(seed)
    out = []
    for m, s, n in zip(means, sds, ns):
        z = rng.standard_normal(n)
        z = (z - z.mean()) / z.std(ddof=1)
        out.append(m + s * z)
    return out


def anova(groups):
    ns = np.array([len(g) for g in groups])
    means = np.array([g.mean() for g in groups])
    N, k = ns.sum(), len(groups)
    grand = (ns * means).sum() / N
    ssb = (ns * (means - grand) ** 2).sum()
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    F = (ssb / (k - 1)) / (ssw / (N - k))
    return ssb, ssw, F, k - 1, N - k, stats.f.sf(F, k - 1, N - k)


def type_one_error(ns, sds, rng):
    """Proporción de rechazos al 5 % cuando las tres medias son iguales."""
    gs = [rng.normal(0, s, (SIMS, n)) for n, s in zip(ns, sds)]
    ns = np.array(ns)
    N, k = ns.sum(), len(ns)
    m = np.array([g.mean(axis=1) for g in gs])
    grand = (ns[:, None] * m).sum(axis=0) / N
    ssb = (ns[:, None] * (m - grand) ** 2).sum(axis=0)
    ssw = sum(((g - g.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) for g in gs)
    F = (ssb / (k - 1)) / (ssw / (N - k))
    v = np.array([g.var(axis=1, ddof=1) for g in gs])
    w = ns[:, None] / v
    mw = (w * m).sum(axis=0) / w.sum(axis=0)
    a = ((w * (m - mw) ** 2).sum(axis=0)) / (k - 1)
    lam = (((1 - w / w.sum(axis=0)) ** 2) / (ns[:, None] - 1)).sum(axis=0)
    welch = a / (1 + 2 * (k - 2) * lam / (k ** 2 - 1))
    df2 = (k ** 2 - 1) / (3 * lam)
    return (F > stats.f.isf(0.05, k - 1, N - k)).mean(), (stats.f.sf(welch, k - 1, df2) < 0.05).mean()


# =============================================================================
# 2. FIGURAS
# =============================================================================

def dots_chart(dark, groups, rng_seed):
    rng = np.random.default_rng(rng_seed)
    p = ui.new_figure(dark, height=300, x_range=list(GROUPS), y_axis_label="cosecha por parcela (kg)")
    allv = np.concatenate(groups)
    for name, g, colour in zip(GROUPS, groups, COLOURS):
        jitter = rng.uniform(-0.18, 0.18, len(g))
        p.scatter([(name, j) for j in jitter], g, size=9, color=colour, alpha=0.7)
        p.segment(x0=[(name, -0.3)], x1=[(name, 0.3)], y0=[g.mean()], y1=[g.mean()], line_width=4, color=colour)
    p.add_layout(Span(location=allv.mean(), dimension="width", line_color=ui.UBU_RED, line_dash="dashed", line_width=2))
    return p


def f_chart(dark, F, d1, d2):
    hi = max(stats.f.isf(0.001, d1, d2), F * 1.15)
    xs = np.linspace(0.001, hi, 400)
    pdf = stats.f.pdf(xs, d1, d2)
    crit = stats.f.isf(0.05, d1, d2)
    p = ui.new_figure(dark, height=240, x_axis_label=f"F con ({d1}, {d2}) grados de libertad", y_axis_label="densidad")
    p.line(xs, pdf, line_width=3, color=ui.BLUE_LINE)
    tail = xs >= crit
    p.varea(x=xs[tail], y1=0, y2=pdf[tail], fill_color=ui.UBU_RED, fill_alpha=0.35)
    p.add_layout(Span(location=F, dimension="height", line_color=ui.UBU_RED, line_width=3))
    return p


def f_vs_n_chart(dark, s, n_now):
    ns = np.arange(3, 41)
    means = np.array([20.0, 22.0, 23.0])
    var_m = ((means - means.mean()) ** 2).sum() / 2
    F = ns * var_m / s ** 2
    crit = stats.f.isf(0.05, 2, 3 * ns - 3)
    p = ui.new_figure(dark, height=240, x_axis_label="parcelas por abono n", y_axis_label="F", y_axis_type="log")
    p.line(ns, F, line_width=3, color=ui.BLUE_LINE, legend_label="F observado")
    p.line(ns, crit, line_width=2.5, color=ui.UBU_RED, line_dash="dashed", legend_label="valor crítico 5 %")
    p.add_layout(Span(location=n_now, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted"))
    return ui.style_legend(p, dark, "top_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Son iguales las medias de varios grupos?</b>")
        ui.content(
            "El <b>análisis de la varianza</b> compara las medias de k grupos con un solo test. La idea es descomponer la "
            "variabilidad total de los datos en la que hay <b>entre</b> los grupos y la que hay <b>dentro</b> de cada uno, y "
            "comparar las dos. <i>¿Cómo se escribe la descomposición?</i>"
        )
        ui.formula_hidden("&sum;&sum;(x<sub>ij</sub> &minus; x̄)<sup>2</sup> = &sum; n<sub>i</sub>(x̄<sub>i</sub> &minus; x̄)<sup>2</sup> + "
                          "&sum;&sum;(x<sub>ij</sub> &minus; x̄<sub>i</sub>)<sup>2</sup>, &nbsp; SCT = SCE + SCR")
        ui.content(
            "Si las medias poblacionales son iguales, las dos partes, divididas por sus grados de libertad, estiman la "
            "misma varianza &sigma;<sup>2</sup>, y su cociente sigue una distribución F de Snedecor. Las hipótesis: "
            "grupos independientes, normales y con la misma varianza."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las patatas de Fisher (1923)</b><br>"
            "<i>Mueve las medias de tres abonos y mira cómo cambia la variabilidad entre grupos y el estadístico "
            "F.</i><br><br>"
            "<b>II. Tamaños y varianzas</b><br>"
            "<i>Con las mismas medias, decide si los abonos son distintos según cuántas parcelas haya y cuánto varíen "
            "dentro de cada grupo.</i><br><br>"
            "<b>III. Cuando falla la igualdad de varianzas</b><br>"
            "<i>Descubre con George Box que el test F se equivoca si un grupo pequeño es mucho más irregular.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("mueve las <u>medias muestrales</u> de los tres abonos")
        mA = st.slider("Media del abono A (kg)", 15, 25, v["mA"], 1, key=ui.wkey(PAGE, "mA"))
        mB = st.slider("Media del abono B (kg)", 15, 25, v["mB"], 1, key=ui.wkey(PAGE, "mB"))
        mC = st.slider("Media del abono C (kg)", 15, 25, v["mC"], 1, key=ui.wkey(PAGE, "mC"))

        ui.planteamiento()
        ui.statement(
            "<b>Las patatas de Fisher (1923)</b><br><br>"
            "En un artículo con Winifred Mackenzie sobre la respuesta de distintas variedades de patata a los abonos, "
            "Ronald Fisher publicó la primera tabla de análisis de la varianza. Tenemos ocho parcelas con cada uno de "
            "tres abonos, A, B y C, y una desviación muestral de 4 kg dentro de cada grupo. ¿Son distintos los abonos?"
        )

        if ui.accordion_step("P1_A", "(A) Entre y dentro"):
            ui.content(
                "Mira la gráfica de puntos: las barras gruesas son las medias de cada grupo y la línea discontinua, la media "
                "global. ¿Qué parte de la descomposición cambia al mover las medias? ¿Cuál no?"
            )
            ui.spoiler(
                "Al mover las medias cambia la suma de cuadrados entre grupos, SCE = &sum;n<sub>i</sub>(x̄<sub>i</sub> &minus; "
                "x̄)<sup>2</sup>, que mide lo separadas que están. La suma residual, dentro de los grupos, SCR = "
                "&sum;(n<sub>i</sub> &minus; 1)s<sub>i</sub><sup>2</sup>, no cambia, porque las desviaciones de cada grupo "
                "están fijas."
            )

        if ui.accordion_step("P1_B", "(B) El estadístico F"):
            ui.content("Divide cada suma por sus grados de libertad. ¿Qué distribución tiene el cociente si los tres abonos son iguales?")
            ui.spoiler(
                "<div class='formula-box'>F = <sup>SCE/(k &minus; 1)</sup>&frasl;<sub>SCR/(N &minus; k)</sub> ~ "
                "F<sub>k &minus; 1, N &minus; k</sub></div>"
                "Bajo H<sub>0</sub>, el numerador y el denominador son dos estimaciones independientes de &sigma;<sup>2</sup>, "
                "cada una una ji cuadrado dividida por sus grados de libertad, y su cociente es una F de Snedecor. Si las "
                "medias son distintas, el numerador crece. Se rechaza H<sub>0</sub> cuando F supera el valor crítico."
            )

        if ui.accordion_step("P1_C", "(C) Lo que dice y lo que no dice"):
            ui.content("Pon A = B = 20 y C = 25. El test rechaza. ¿Dice cuál de los abonos es distinto?")
            ui.spoiler(
                "No: H<sub>1</sub> solo afirma que alguna media es distinta. Para saber cuál hacen falta comparaciones "
                "múltiples, por ejemplo las de Tukey, o la corrección de Bonferroni sobre los tests por pares, que "
                "controlan la probabilidad de cometer algún error de tipo I entre todas las comparaciones. Hacer los tres "
                "tests t por separado al 5 % daría muchos más falsos positivos."
            )

    with col_right:
        ui.right_panel()
        groups = groups_with([mA, mB, mC], [4, 4, 4], [8, 8, 8], v["seed"])
        ssb, ssw, F, d1, d2, pval = anova(groups)
        ui.metrics([(f"SCE = {ssb:.1f}", "metric-a"), (f"SCR = {ssw:.1f}", "metric-c"), (f"F = {F:.2f}", "metric-b")])
        ui.check(pval < 0.05, f"p-valor {pval:.4f}: se rechaza que los abonos sean iguales" if pval < 0.05
                 else f"p-valor {pval:.4f}: no hay pruebas de diferencias")
        ui.show(dots_chart(dark, groups, v["seed"]), key="fig_dots")
        ui.show(f_chart(dark, F, d1, d2), key="fig_f")
        ui.footer_bar("Arriba, las 24 parcelas. Abajo, la distribución F bajo H<sub>0</sub>: el área roja es el 5 % de rechazo "
                      "y la línea roja, el F observado.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>parcelas por abono</u> y la <u>desviación dentro de los grupos</u>")
        n = st.slider("Parcelas por abono n", 3, 40, v["n"], 1, key=ui.wkey(PAGE, "n"))
        s = st.slider("Desviación muestral dentro de cada grupo (kg)", 1, 10, v["s"], 1, key=ui.wkey(PAGE, "s"))

        ui.planteamiento()
        ui.statement(
            "<b>Tamaños y varianzas</b><br><br>"
            "Las medias muestrales quedan fijas en 20, 22 y 23 kg. Cambiamos el número de parcelas por abono y la "
            "desviación muestral dentro de cada grupo, igual en los tres. Los datos son distintos en cada caso, pero las "
            "medias son siempre las mismas: ¿es siempre la misma la decisión?"
        )

        if ui.accordion_step("P2_A", "(A) El papel del tamaño"):
            ui.content("Con grupos de igual tamaño n y la misma desviación s, escribe F en función de n, s y la varianza de las medias.")
            ui.spoiler(
                "Con grupos iguales, SCE = n&middot;&sum;(x̄<sub>i</sub> &minus; x̄)<sup>2</sup> y SCR/(N &minus; k) = "
                "s<sup>2</sup>, así que"
                "<div class='formula-box'>F = <sup>n &middot; s<sub>x̄</sub><sup>2</sup></sup>&frasl;<sub>s<sup>2</sup></sub></div>"
                "con s<sub>x̄</sub><sup>2</sup> la varianza de las tres medias. F crece en proporción a n: las mismas "
                "diferencias entre medias acaban siendo significativas con muestras grandes."
            )

        if ui.accordion_step("P2_B", "(B) El papel de la varianza"):
            ui.content("Duplica s. ¿Qué le pasa a F? ¿Cuántas parcelas harían falta para compensar?")
            ui.spoiler(
                "F se divide entre 4, porque depende de s<sup>2</sup>. Para recuperar el mismo F hay que multiplicar n por 4. "
                "Diferencias de medias que destacan con grupos homogéneos se pierden en el ruido cuando cada grupo es "
                "muy irregular. Lo que decide es la señal (diferencias de medias) frente al ruido (varianza dentro), y el "
                "tamaño amplifica la señal."
            )

        if ui.accordion_step("P2_C", "(C) Significativo no es importante"):
            ui.content("Con n = 40 y s = 1, el p-valor es minúsculo. ¿Significa que el abono C es mucho mejor?")
            ui.spoiler(
                "No. El p-valor mide si la diferencia es explicable por azar, no su tamaño. Una diferencia de 3 kg puede "
                "ser irrelevante o decisiva según el precio del abono. Por eso conviene acompañar el test de una medida del "
                "efecto, como &eta;<sup>2</sup> = SCE/SCT, la proporción de variabilidad explicada por el factor, y de "
                "intervalos para las diferencias."
            )

    with col_right:
        ui.right_panel()
        groups = groups_with([20, 22, 23], [s, s, s], [n, n, n], v["seed"] + n)
        ssb, ssw, F, d1, d2, pval = anova(groups)
        ui.metrics([(f"F = {F:.2f}", "metric-b"), (f"p-valor: {ui.fmt_sci(pval, 2)}", "metric-a"),
                    (f"&eta;<sup>2</sup> = {ssb / (ssb + ssw):.3f}", "metric-c")])
        ui.check(pval < 0.05, "Se rechaza H<sub>0</sub> al 5 %" if pval < 0.05 else "No se rechaza H<sub>0</sub> al 5 %")
        ui.show(dots_chart(dark, groups, v["seed"] + 1), key="fig_dots2")
        ui.show(f_vs_n_chart(dark, s, n), key="fig_f_vs_n")
        ui.footer_bar(f"Con s = {s}, la curva azul es el F que dan las mismas medias para cada tamaño. Donde cruza la línea "
                      "roja, la decisión cambia.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño</u> y la <u>desviación</u> del grupo C")
        nC = st.slider("Parcelas con el abono C", 2, 40, v["nC"], 1, key=ui.wkey(PAGE, "nC"))
        sC = st.slider("Desviación de la población C (A y B tienen 1)", 1.0, 4.0, v["sC"], 0.5, key=ui.wkey(PAGE, "sC"))

        ui.planteamiento()
        ui.statement(
            "<b>Cuando falla la igualdad de varianzas</b><br><br>"
            "En 1954 George Box estudió qué le pasa al test F cuando los grupos tienen varianzas distintas. Simulamos "
            f"{ui.fmt_int(SIMS)} experimentos en los que los tres abonos tienen <b>la misma media</b>: H<sub>0</sub> es "
            "cierta. A y B tienen diez parcelas y desviación 1; el grupo C, el tamaño y la desviación que elijas. Un test "
            "correcto al 5 % debería rechazar en el 5 % de los experimentos."
        )

        if ui.accordion_step("P3_A", "(A) Tamaños iguales"):
            ui.content("Pon C con diez parcelas y desviación 3. ¿Se aleja mucho del 5 % la tasa de rechazos?")
            ui.spoiler(
                "Algo, pero poco: con tamaños iguales el test F es bastante <b>robusto</b> a las diferencias de varianza, "
                "y su nivel real se queda cerca del 8 %. Con diseños equilibrados, una violación moderada de la "
                "homocedasticidad apenas importa."
            )

        if ui.accordion_step("P3_B", "(B) El grupo pequeño e irregular"):
            ui.content("Ahora baja C a cuatro parcelas con desviación 3, y después súbelo a cuarenta. ¿Qué pasa en cada caso?")
            ui.spoiler(
                "Con el grupo pequeño e irregular, el denominador de F, que promedia las varianzas pesando por los tamaños, "
                "infravalora la variabilidad de la media de C, y el test rechaza más de un 20 % de las veces: demasiados "
                "falsos positivos. Con el grupo grande e irregular pasa lo contrario: el test casi nunca rechaza y pierde "
                "potencia. Tamaños desiguales y varianzas desiguales juntos son la combinación peligrosa."
            )

        if ui.accordion_step("P3_C", "(C) El remedio de Welch"):
            ui.content("¿Cómo se corrige? Compara la segunda métrica con la primera.")
            ui.spoiler(
                "El ANOVA de Welch (1951) pondera cada media por n<sub>i</sub>/s<sub>i</sub><sup>2</sup>, la inversa de su "
                "varianza estimada, y ajusta los grados de libertad. Su nivel real queda mucho más cerca del 5 %; solo se "
                "desvía cuando un grupo tiene dos o tres parcelas, porque entonces su varianza está muy mal estimada. Antes de aplicar el ANOVA clásico conviene mirar las desviaciones de cada grupo, o usar un test de "
                "homogeneidad como el de Levene."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + nC * 11 + int(sC * 10))
        f_rate, w_rate = type_one_error([10, 10, nC], [1.0, 1.0, sC], rng)
        ui.metrics([(f"Rechazos con F: {ui.fmt_pct(f_rate, 1)}", "result-no" if abs(f_rate - 0.05) > 0.02 else "metric-a"),
                    (f"Con Welch: {ui.fmt_pct(w_rate, 1)}", "metric-b"), ("Nominal: 5.0 %", "metric-c")])
        demo = groups_with([20, 20, 20], [1.0, 1.0, sC], [10, 10, nC], v["seed"] + 5)
        ui.show(dots_chart(dark, demo, v["seed"] + 2), key="fig_dots3")
        ui.footer_bar(f"Un experimento de ejemplo con medias iguales. Las métricas cuentan, en {ui.fmt_int(SIMS)} experimentos "
                      "simulados, cuántas veces cada test rechaza una hipótesis nula que es cierta.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Las patatas de Fisher", "P1_A"),
        ("P2", "(II) Tamaños y varianzas", "P2_A"),
        ("P3", "(III) Varianzas distintas", "P3_A"),
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
