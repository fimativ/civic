#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 5: las distribuciones gamma y ji-dos.

El k-ésimo siniestro de Lundberg (la gamma como suma de exponenciales), la
función gamma de Euler (interpolar el factorial) y los dados de Weldon que
analizó Pearson (la ji-dos como suma de cuadrados de normales).
"""

from __future__ import annotations

from math import gamma as gamma_fn, sqrt, pi

import numpy as np
import streamlit as st
from scipy import stats

import civic_ui as ui

TITLE = "Gamma y ji-dos"
SYMBOL = "Γ, χ²"
PAGE = "04_05"

# Weldon (1894): 26 306 lanzamientos de 12 dados, contando los que muestran 5 o 6.
WELDON = np.array([185, 1149, 3265, 5475, 6114, 5194, 3067, 1331, 403, 105, 14, 4, 0])


def initial_values():
    return {
        "k": ui.dint(5, 2, 10, "k"),
        "rate": ui.dchoice(2.0, [1.0, 1.5, 2.0, 3.0, 4.0], "rate"),
        "t": round(2 * ui.dfloat(3.0, 1.0, 6.0, "t", 1)) / 2,
        "p": ui.dfloat(2.5, 0.5, 5.5, "p", 1),
        "df": ui.dint(3, 1, 10, "df"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "claims": None, "squares": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def weldon_test(p: float):
    k = np.arange(13)
    n = WELDON.sum()
    expected = n * stats.binom.pmf(k, 12, p)
    obs = np.r_[WELDON[:11], WELDON[11:].sum()]
    exp_ = np.r_[expected[:11], expected[11:].sum()]
    x2 = float(((obs - exp_) ** 2 / exp_).sum())
    return k, expected, x2


def fitted_p() -> float:
    return float((WELDON * np.arange(13)).sum() / (12 * WELDON.sum()))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def gamma_chart(dark, k: int, rate: float, t: float, sample):
    top = (k + 5 * sqrt(k)) / rate
    xs = np.linspace(0, top, 400)
    dens = stats.gamma.pdf(xs, k, scale=1 / rate)
    p = ui.new_figure(dark, height=300, x_axis_label="días hasta el siniestro k", y_axis_label="densidad",
                      x_range=(0, top), y_range=(0, dens.max() * 1.3))
    if sample is not None:
        edges = np.linspace(0, top, 41)
        hist, _ = np.histogram(sample, bins=edges)
        w = edges[1] - edges[0]
        p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(sample) * w), fill_color=ui.UBU_YELLOW,
               fill_alpha=0.6, line_color=None, legend_label="sumas de exponenciales")
    mask = xs <= t
    p.varea(x=xs[mask], y1=0, y2=dens[mask], color=ui.UBU_RED, alpha=0.2)
    p.line(xs, dens, line_width=4, color=ui.BLUE_LINE, legend_label=f"γ({k}, {rate:g})")
    return ui.style_legend(p, dark, "top_right")


def euler_chart(dark, p_val: float):
    xs = np.linspace(0.15, 6.0, 400)
    gs = np.array([gamma_fn(x) for x in xs])
    fig = ui.new_figure(dark, height=280, x_axis_label="p", y_axis_label="Γ(p)", x_range=(0, 6.2), y_range=(0, 26))
    fig.line(xs, gs, line_width=4, color=ui.BLUE_LINE, legend_label="Γ(p)")
    ns = np.arange(1, 7)
    fig.scatter(ns, [gamma_fn(n) for n in ns], size=12, color=ui.UBU_RED, legend_label="(p − 1)!")
    fig.scatter([0.5], [sqrt(pi)], size=12, marker="diamond", color=ui.GREEN_LINE, legend_label="Γ(1/2) = √π")
    fig.scatter([p_val], [gamma_fn(p_val)], size=16, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK, line_width=2)
    return ui.style_legend(fig, dark, "top_left")


def integrand_chart(dark, p_val: float):
    xs = np.linspace(0.001, 15, 500)
    ys = np.exp(-xs) * xs ** (p_val - 1)
    fig = ui.new_figure(dark, height=220, x_axis_label="x", y_axis_label="e⁻ˣ xᵖ⁻¹", x_range=(0, 15),
                        y_range=(0, min(ys.max(), 5) * 1.15))
    fig.varea(x=xs, y1=0, y2=np.minimum(ys, 50), color=ui.UBU_YELLOW, alpha=0.6)
    fig.line(xs, np.minimum(ys, 50), line_width=3, color=ui.ORANGE_LINE)
    return fig


def chi2_chart(dark, df: int, sample):
    top = df + 6 * sqrt(2 * df) + 2
    xs = np.linspace(0.01, top, 400)
    dens = stats.chi2.pdf(xs, df)
    cap = min(float(dens.max()), 0.6) * 1.3
    p = ui.new_figure(dark, height=300, x_axis_label="suma de cuadrados", y_axis_label="densidad",
                      x_range=(0, top), y_range=(0, cap))
    if sample is not None:
        edges = np.linspace(0, top, 41)
        hist, _ = np.histogram(sample, bins=edges)
        w = edges[1] - edges[0]
        p.quad(left=edges[:-1], right=edges[1:], bottom=0, top=hist / (len(sample) * w), fill_color=ui.UBU_YELLOW,
               fill_alpha=0.6, line_color=None, legend_label="Z₁² + … + Zₙ² simulada")
    p.line(xs, np.minimum(dens, cap), line_width=4, color=ui.BLUE_LINE, legend_label=f"χ² con {df} g.l.")
    return ui.style_legend(p, dark, "top_right")


def weldon_chart(dark, p: float, x2: float):
    k, expected, _ = weldon_test(p)
    fig = ui.new_figure(dark, height=260, x_axis_label="dados con 5 o 6 (de 12)", y_axis_label="tiradas",
                        x_range=(-0.6, 12.6))
    fig.vbar(x=k - 0.18, top=WELDON, width=0.34, color=ui.BLUE_LINE, legend_label="Weldon")
    fig.vbar(x=k + 0.18, top=expected, width=0.34, color=ui.ORANGE_LINE, legend_label=f"B(12, {p:.4f})")
    fig.xgrid.grid_line_color = None
    return ui.style_legend(fig, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué pasa al sumar esperas y al sumar cuadrados?</b>")
        ui.content(
            "La exponencial mide la espera hasta un suceso. La espera hasta el k-ésimo suceso es la suma de k "
            "esperas exponenciales independientes, y su distribución es la <b>gamma</b>, que depende de un "
            "parámetro de forma p y otro a, inverso de la escala. <i>Escribe su densidad.</i>"
        )
        ui.formula_hidden("f(x) = <sup>a<sup>p</sup></sup>&frasl;<sub>&Gamma;(p)</sub> x<sup>p&minus;1</sup> "
                          "e<sup>&minus;ax</sup>, &nbsp; x &gt; 0")
        ui.content(
            "El factor a<sup>p</sup>/&Gamma;(p) es el que hace que integre 1. Su media es p/a y su varianza "
            "p/a<sup>2</sup>; con p = 1 es la exponencial de parámetro a. Un caso particular con nombre propio "
            "es la <b>ji-dos</b> de Pearson con n grados de libertad, la gamma de parámetros n/2 y 1/2, que es "
            "la distribución de la suma de los cuadrados de n normales típicas independientes."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El k-ésimo siniestro (1903)</b><br>"
            "<i>Espera con Filip Lundberg a que una aseguradora reciba su quinto parte de accidente.</i><br><br>"
            "<b>II. La función gamma de Euler (1729)</b><br>"
            "<i>¿Cuánto vale el factorial de un medio? Leonhard Euler encontró la respuesta en una "
            "integral.</i><br><br>"
            "<b>III. Los dados de Weldon (1900)</b><br>"
            "<i>Doce dados lanzados 26 306 veces y la distribución con la que Karl Pearson decidió que "
            "estaban cargados.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de siniestros k</u>, la <u>intensidad &lambda;</u> y el <u>plazo t</u>")
        c1, c2, c3 = st.columns(3)
        k = c1.slider("Siniestro número k", 1, 15, v["k"], 1, key=ui.wkey(PAGE, "k"))
        rate = c2.select_slider("λ (partes/día)", options=[0.5, 1.0, 1.5, 2.0, 3.0, 4.0], value=v["rate"],
                                key=ui.wkey(PAGE, "rate"))
        t = c3.slider("Plazo t (días)", 0.5, 15.0, v["t"], 0.5, key=ui.wkey(PAGE, "t"))

        ui.planteamiento()
        ui.statement(
            "<b>El k-ésimo siniestro (1903)</b><br><br>"
            "Filip Lundberg, actuario sueco, defendió en Upsala una tesis en la que los partes de siniestro "
            "llegan a una aseguradora al azar, como las partículas de Rutherford: un proceso de Poisson. Es el "
            "origen de la teoría matemática del riesgo. Si llegan &lambda; partes al día de media, ¿cuánto "
            "tarda en llegar el parte número k?"
        )

        if ui.accordion_step("P1_A", "(A) Una suma de esperas"):
            ui.content(
                "La espera hasta el siniestro k es la suma de las k esperas entre siniestros consecutivos, "
                "exponenciales e independientes. Calcula su media y su varianza sin conocer su densidad."
            )
            ui.spoiler(
                "Por la linealidad de la esperanza y la suma de varianzas de variables independientes:"
                "<div class='formula-box'>&#120124;[T<sub>k</sub>] = k/&lambda; &nbsp;&nbsp; &#120141;(T<sub>k</sub>) = "
                "k/&lambda;<sup>2</sup></div>"
                "Coinciden con la media p/a y la varianza p/a<sup>2</sup> de una gamma con p = k y a = &lambda;. "
                "Con forma entera se llama también distribución de Erlang."
            )

        if ui.accordion_step("P1_B", "(B) Gamma y Poisson"):
            ui.content(
                "El parte k llega antes del día t si y solo si en [0, t] llegan al menos k partes. Escribe "
                "&#8473;(T<sub>k</sub> &le; t) como una suma de probabilidades de Poisson."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(T<sub>k</sub> &le; t) = &#8473;(N<sub>t</sub> &ge; k) = 1 &minus; "
                "&sum;<sub>j=0</sub><sup>k&minus;1</sup> e<sup>&minus;&lambda;t</sup> <sup>(&lambda;t)<sup>j</sup></sup>"
                "&frasl;<sub>j!</sub></div>"
                "Con k = 1 es la exponencial de siempre. Derivando respecto de t, la suma se telescopa y queda la "
                "densidad gamma &lambda;<sup>k</sup>t<sup>k&minus;1</sup>e<sup>&minus;&lambda;t</sup>/(k &minus; 1)!."
            )

        if ui.accordion_step("P1_C", "(C) La forma de la gamma"):
            ui.content(
                "Aumenta k con &lambda; fija. ¿Cómo cambia la forma de la densidad? ¿Qué le ocurre si se mira la "
                "espera relativa a su media?"
            )
            ui.spoiler(
                "Con k = 1 la densidad es máxima en 0; con k &gt; 1 empieza en 0, sube hasta un máximo en "
                "(k &minus; 1)/&lambda; y baja con una cola a la derecha. Al crecer k la asimetría disminuye y "
                "la curva se parece cada vez más a una normal de media k/&lambda;: una suma de muchas esperas "
                "independientes, otra vez el anuncio del teorema central del límite."
            )

        if st.button("Simular 5000 esperas", key="claims_play", width="stretch", type="primary"):
            st.session_state["claims"] = (k, rate, np.random.default_rng().exponential(1 / rate, (5000, k)).sum(axis=1))

    with col_right:
        ui.right_panel()
        prob = float(stats.gamma.cdf(t, k, scale=1 / rate))
        ui.metrics([(f"&#120124;[T<sub>{k}</sub>] = {k / rate:.2f} días", "metric-a"),
                    (f"&#8473;(T<sub>{k}</sub> &le; {t:g}) = {prob:.4f}", "metric-c")])
        sim = st.session_state.get("claims")
        sample = sim[2] if sim and sim[:2] == (k, rate) else None
        ui.show(gamma_chart(dark, k, rate, t, sample), key="fig_gamma")
        poisson_side = 1 - float(stats.poisson.cdf(k - 1, rate * t))
        ui.footer_bar(f"&#8473;(N<sub>{t:g}</sub> &ge; {k}) = {poisson_side:.4f}, igual que el área roja bajo la gamma: "
                      "esperar menos de t al parte k es recibir al menos k partes antes de t.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>argumento p</u>")
        p_val = st.slider("p", 0.2, 6.0, v["p"], 0.1, key=ui.wkey(PAGE, "p"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>La función gamma de Euler (1729)</b><br><br>"
            "En unas cartas a Christian Goldbach, Leonhard Euler resolvió un problema que parecía capricho: "
            "extender el factorial, definido para enteros, a cualquier número positivo. Su respuesta fue una "
            "integral, &Gamma;(p) = &int;<sub>0</sub><sup>&infin;</sup> e<sup>&minus;x</sup>x<sup>p&minus;1</sup>dx, "
            "el área amarilla de la derecha. Es la constante que hace falta para que la densidad gamma integre 1."
        )

        if ui.accordion_step("P2_A", "(A) La recurrencia"):
            ui.content(
                "Integra por partes &Gamma;(p) para relacionarla con &Gamma;(p &minus; 1). Calcula &Gamma;(1) y deduce "
                "&Gamma;(n) para n natural."
            )
            ui.spoiler(
                "Con u = x<sup>p&minus;1</sup> y dv = e<sup>&minus;x</sup>dx, el término de contorno se anula:"
                "<div class='formula-box'>&Gamma;(p) = (p &minus; 1)&Gamma;(p &minus; 1), &nbsp; &Gamma;(1) = 1 &nbsp;&rArr;&nbsp; "
                "&Gamma;(n) = (n &minus; 1)!</div>"
                "Los puntos rojos de la figura son los factoriales; la curva azul los une de la forma más natural."
            )

        if ui.accordion_step("P2_B", "(B) El factorial de un medio"):
            ui.content(
                "Calcula &Gamma;(1/2) con el cambio x = z<sup>2</sup>/2. ¿Qué integral conocida aparece?"
            )
            ui.spoiler(
                "<div class='formula-box'>&Gamma;(1/2) = &int;<sub>0</sub><sup>&infin;</sup> e<sup>&minus;x</sup>x<sup>&minus;1/2</sup>dx "
                "= &radic;2&int;<sub>0</sub><sup>&infin;</sup> e<sup>&minus;z<sup>2</sup>/2</sup>dz = &radic;&pi;</div>"
                "Aparece la integral de la campana de Gauss, la misma que da el factor 1/&radic;(2&pi;) de la densidad "
                "normal. Con la recurrencia, (1/2)! = &Gamma;(3/2) = &radic;&pi;/2."
            )

        if ui.accordion_step("P2_C", "(C) Normalizar la gamma"):
            ui.content(
                "Usa el cambio y = ax para calcular &int;<sub>0</sub><sup>&infin;</sup> x<sup>p&minus;1</sup>e<sup>&minus;ax</sup>dx. "
                "¿Qué constante debe multiplicar a x<sup>p&minus;1</sup>e<sup>&minus;ax</sup> para tener una densidad?"
            )
            ui.spoiler(
                "<div class='formula-box'>&int;<sub>0</sub><sup>&infin;</sup> x<sup>p&minus;1</sup>e<sup>&minus;ax</sup>dx = "
                "<sup>&Gamma;(p)</sup>&frasl;<sub>a<sup>p</sup></sub></div>"
                "La constante es a<sup>p</sup>/&Gamma;(p). Sin el factor a<sup>p</sup> la función solo sería una "
                "densidad cuando a = 1. Con la misma cuenta se obtiene la media: &#120124;[X] = "
                "<sup>a<sup>p</sup></sup>&frasl;<sub>&Gamma;(p)</sub>&middot;<sup>&Gamma;(p + 1)</sup>&frasl;<sub>a<sup>p+1</sup></sub> = p/a."
            )

    with col_right:
        ui.right_panel()
        ui.metrics([(f"&Gamma;({p_val:.1f}) = {gamma_fn(p_val):.4f}", "metric-a"),
                    (f"({p_val:.1f} &minus; 1)&middot;&Gamma;({p_val - 1:.1f}) = "
                     f"{(p_val - 1) * gamma_fn(p_val - 1):.4f}" if p_val > 1.05 else "Γ(p) explota cuando p → 0",
                     "metric-c")])
        ui.show(euler_chart(dark, p_val), key="fig_euler")
        ui.show(integrand_chart(dark, p_val), key="fig_integrand")
        ui.footer_bar("Arriba, la función gamma con los factoriales en rojo. Abajo, el integrando de Euler: su área "
                      "es &Gamma;(p).")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>grados de libertad n</u>")
        df = st.slider("Grados de libertad n", 1, 20, v["df"], 1, key=ui.wkey(PAGE, "df"))
        use_fit = st.toggle("En los dados de Weldon, usar la p estimada en lugar de 1/3", value=False, key="weldon_fit")

        ui.planteamiento()
        ui.statement(
            "<b>Los dados de Weldon (1900)</b><br><br>"
            "El biólogo Walter Weldon lanzó doce dados 26 306 veces y anotó cuántos "
            "mostraban un 5 o un 6. Si los dados son buenos, ese número es binomial B(12, 1/3). Karl Pearson usó "
            "la tabla para estrenar en 1900 una medida de la discrepancia entre lo observado y lo esperado, cuya "
            "distribución resultó ser una ji-dos. ¿Estaban cargados los dados?"
        )

        if ui.accordion_step("P3_A", "(A) Suma de cuadrados"):
            ui.content(
                "Si Z<sub>1</sub>, &hellip;, Z<sub>n</sub> son normales típicas independientes, calcula la media y la "
                "varianza de Z<sub>1</sub><sup>2</sup> + &ctdot; + Z<sub>n</sub><sup>2</sup>. Compara la simulación con "
                "la densidad ji-dos."
            )
            ui.spoiler(
                "&#120124;[Z<sup>2</sup>] = &#120141;(Z) = 1 y &#120124;[Z<sup>4</sup>] = 3, luego &#120141;(Z<sup>2</sup>) = 2. "
                "Sumando n independientes:"
                "<div class='formula-box'>&#120124;[&chi;<sup>2</sup><sub>n</sub>] = n &nbsp;&nbsp; &#120141;(&chi;<sup>2</sup><sub>n</sub>) = 2n</div>"
                "Coincide con la gamma de parámetros p = n/2 y a = 1/2: media (n/2)/(1/2) = n, varianza "
                "(n/2)/(1/4) = 2n."
            )

        if ui.accordion_step("P3_B", "(B) La medida de Pearson"):
            ui.content(
                "Pearson propuso sumar, en cada casilla, (observado &minus; esperado)<sup>2</sup>/esperado. Si el modelo "
                "es correcto, cada término se parece al cuadrado de una normal típica. ¿Cuánto vale la suma para los "
                "dados de Weldon con p = 1/3?"
            )
            _, _, x2 = weldon_test(1 / 3)
            ui.spoiler(
                "<div class='formula-box'>X<sup>2</sup> = &sum; <sup>(O<sub>i</sub> &minus; E<sub>i</sub>)<sup>2</sup></sup>"
                f"&frasl;<sub>E<sub>i</sub></sub> &asymp; {x2:.1f}</div>"
                "Agrupando las dos últimas casillas, que esperan muy pocos casos, quedan doce casillas y, como los "
                "totales observado y esperado coinciden, once grados de libertad. Una ji-dos con once grados tiene "
                "media 11: el valor observado está muy lejos."
            )

        if ui.accordion_step("P3_C", "(C) El veredicto"):
            ui.content(
                "Calcula con la densidad ji-dos la probabilidad de obtener una discrepancia tan grande si los dados "
                "fueran buenos. Activa después la p estimada a partir de los datos. ¿Qué concluyes?"
            )
            ui.spoiler(
                "Con p = 1/3 esa probabilidad es del orden de 10<sup>&minus;5</sup>: los dados no se comportan como "
                "dados perfectos. La proporción observada de cincos y seises es 0.3377, un poco mayor que 1/3, "
                "quizá porque las caras con más puntos, más vaciadas, pesan menos. Con esa p la discrepancia baja "
                "a unos 13, perfectamente compatible con una ji-dos. Es el primer contraste de bondad del ajuste, "
                "que verás en estadística."
            )

        if st.button("Simular 5000 sumas de cuadrados", key="squares_play", width="stretch", type="primary"):
            st.session_state["squares"] = (df, (np.random.default_rng().standard_normal((5000, df)) ** 2).sum(axis=1))

    with col_right:
        ui.right_panel()
        sim = st.session_state.get("squares")
        sample = sim[1] if sim and sim[0] == df else None
        ui.metrics([(f"&#120124;[&chi;<sup>2</sup><sub>{df}</sub>] = {df}", "metric-a"),
                    (f"&#120141;(&chi;<sup>2</sup><sub>{df}</sub>) = {2 * df}", "metric-b")])
        ui.show(chi2_chart(dark, df, sample), key="fig_chi2")
        p = fitted_p() if use_fit else 1 / 3
        _, _, x2 = weldon_test(p)
        dof = 10 if use_fit else 11
        pval = float(stats.chi2.sf(x2, dof))
        ui.show(weldon_chart(dark, p, x2), key="fig_weldon")
        ui.footer_bar(f"Dados de Weldon con p = {p:.4f}: X<sup>2</sup> = {x2:.2f} con {dof} grados de libertad; "
                      f"&#8473;(&chi;<sup>2</sup><sub>{dof}</sub> &ge; {x2:.2f}) = {ui.fmt_sci(pval)}.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El k-ésimo siniestro", "P1_A"),
        ("P2", "(II) La función gamma de Euler", "P2_A"),
        ("P3", "(III) Los dados de Weldon", "P3_A"),
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
