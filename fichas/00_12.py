#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 12: el concepto de correlación.

Las co-relaciones de Galton (el coeficiente como covarianza de variables
tipificadas), lo que el coeficiente de Pearson no ve (dependencias no
lineales, atípicos y grupos, frente al de Spearman) y la inferencia sobre ρ
con las estaturas de padres e hijos de Pearson y Lee.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from scipy import stats

import civic_ui as ui

TITLE = "Correlación"
PAGE = "00_12"

SHAPES = {"line": "Recta", "parabola": "Parábola", "circle": "Círculo", "outlier": "Un atípico", "clusters": "Dos grupos"}
PEARSON_LEE = 1078


def initial_values():
    return {
        "rho": round(20 * ui.dfloat(0.6, -0.9, 0.9, "rho")) / 20,
        "n": ui.dchoice(100, [10, 30, 100, 300, 1000], "n"),
        "shape": ui.dchoice("parabola", list(SHAPES), "shape"),
        "n_inf": ui.dchoice(PEARSON_LEE, [10, 30, 100, 300, PEARSON_LEE], "n_inf"),
        "r_obs": round(100 * ui.dfloat(0.50, 0.05, 0.80, "r_obs")) / 100,
        "seed": int(ui.r("correlacion") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "shape": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def bivariate(rho: float, n: int, rng):
    x = rng.standard_normal(n)
    y = rho * x + np.sqrt(1 - rho ** 2) * rng.standard_normal(n)
    return x, y


def shape_data(shape: str, rng, n: int = 60):
    x = rng.uniform(-2, 2, n)
    if shape == "line":
        return x, 0.8 * x + rng.normal(0, 0.5, n)
    if shape == "parabola":
        return x, x ** 2 + rng.normal(0, 0.25, n)
    if shape == "circle":
        t = rng.uniform(0, 2 * np.pi, n)
        return 2 * np.cos(t) + rng.normal(0, 0.08, n), 2 * np.sin(t) + rng.normal(0, 0.08, n)
    if shape == "outlier":
        y = rng.normal(0, 1, n)
        y = y - np.polyval(np.polyfit(x, y, 1), x) + y.mean()      # nube sin ninguna correlación
        x[0], y[0] = 9.0, 9.0
        return x, y
    g = rng.random(n) < 0.5
    x = np.where(g, rng.normal(-2, 0.5, n), rng.normal(2, 0.5, n))
    y = np.where(g, rng.normal(-2, 0.5, n), rng.normal(2, 0.5, n)) - 0.6 * (x - np.where(g, -2, 2))
    return x, y


# =============================================================================
# 2. FIGURAS
# =============================================================================

def scatter_chart(dark, x, y, x_label="x", y_label="y", fit=True):
    lim = max(np.abs(x).max(), np.abs(y).max()) * 1.08
    p = ui.new_figure(dark, height=330, x_axis_label=x_label, y_axis_label=y_label, x_range=(-lim, lim),
                      y_range=(-lim, lim), match_aspect=True)
    p.scatter(x, y, size=6, color=ui.BLUE_LINE, alpha=0.55)
    if fit and np.std(x) > 0:
        b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
        xs = np.array([-lim, lim])
        p.line(xs, y.mean() + b * (xs - x.mean()), line_width=3, color=ui.UBU_RED)
    return p


def fisher_chart(dark, r, n):
    small = max(5, n // 10)
    zc = np.arctanh(r)
    zs = np.linspace(zc - 4 / np.sqrt(small - 3), zc + 4 / np.sqrt(small - 3), 500)
    p = ui.new_figure(dark, height=260, x_axis_label="r", y_axis_label="densidad aproximada")
    for nn, colour in ((small, ui.GREY_LINE), (n, ui.BLUE_LINE)):
        rho_grid = np.tanh(zs)
        dens = stats.norm.pdf(zs, np.arctanh(r), 1 / np.sqrt(nn - 3)) / (1 - rho_grid ** 2)
        p.line(rho_grid, dens, line_width=3 if nn == n else 2, color=colour, legend_label=f"n = {nn}")
    return ui.style_legend(p, dark, "top_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuánto se mueven juntas dos variables?</b>")
        ui.content(
            "La <b>covarianza</b> de dos variables es positiva si tienden a estar a la vez por encima o por debajo de su "
            "media, y negativa si cuando una sube la otra baja. Pero depende de las unidades. El <b>coeficiente de "
            "correlación</b> la divide entre las dos desviaciones típicas y la deja sin unidades. <i>¿Cómo se define el "
            "coeficiente muestral de Pearson?</i>"
        )
        ui.formula_hidden("r = <sup>S<sub>xy</sub></sup>&frasl;<sub>S<sub>x</sub>S<sub>y</sub></sub> = "
                          "<sup>&sum;(x<sub>i</sub> &minus; x̄)(y<sub>i</sub> &minus; ȳ)</sup>&frasl;<sub>&radic;&sum;(x<sub>i</sub> "
                          "&minus; x̄)<sup>2</sup> &sum;(y<sub>i</sub> &minus; ȳ)<sup>2</sup></sub>")
        ui.content(
            "Es la versión muestral de &rho; = Cov(X, Y)/(&sigma;<sub>X</sub>&sigma;<sub>Y</sub>), que ya apareció en el "
            "tema de vectores aleatorios. Mide la intensidad de la relación <b>lineal</b>, y solo esa."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las co-relaciones de Galton (1888)</b><br>"
            "<i>Genera nubes de puntos con distintas correlaciones y aprende a leer r a ojo.</i><br><br>"
            "<b>II. Lo que r no ve</b><br>"
            "<i>Descubre relaciones perfectas con r = 0 y correlaciones altas fabricadas por un solo punto.</i><br><br>"
            "<b>III. Padres e hijos (1903)</b><br>"
            "<i>Contrasta si una correlación es distinta de cero y calcula su intervalo con la transformación de "
            "Fisher.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>correlación de la población &rho;</u> y el <u>tamaño n</u>")
        rho = st.slider("Correlación de la población ρ", -1.0, 1.0, v["rho"], 0.05, key=ui.wkey(PAGE, "rho"))
        n = st.select_slider("Número de personas n", options=[10, 30, 100, 300, 1000], value=v["n"], key=ui.wkey(PAGE, "n"))

        ui.planteamiento()
        ui.statement(
            "<b>Las co-relaciones de Galton (1888)</b><br><br>"
            "Francis Galton buscaba una medida de cuánto se parecen dos medidas del cuerpo, como la estatura y la longitud "
            "del antebrazo. Su idea fue tipificar las dos variables, para que no importaran las unidades, y ver cuánto "
            "cambia una cuando la otra cambia una desviación típica. Simulamos n personas con dos medidas tipificadas de "
            "correlación &rho;."
        )

        if ui.accordion_step("P1_A", "(A) Covarianza de tipificadas"):
            ui.content("Escribe r en función de las variables tipificadas u<sub>i</sub> = (x<sub>i</sub> &minus; x̄)/S<sub>x</sub> y v<sub>i</sub>. ¿Qué cambia si medimos en pulgadas en vez de en centímetros?")
            ui.spoiler(
                "r = &sum;u<sub>i</sub>v<sub>i</sub>/(n &minus; 1): la covarianza de las variables tipificadas, el "
                "producto medio de las desviaciones medidas en desviaciones típicas. Por eso r no cambia al cambiar de "
                "unidades ni de origen: si x' = a + bx con b &gt; 0, r es el mismo, y si b &lt; 0 solo cambia de signo."
            )

        if ui.accordion_step("P1_B", "(B) Entre &minus;1 y 1"):
            ui.content("¿Por qué |r| &le; 1? ¿Cuándo vale exactamente 1?")
            ui.spoiler(
                "Por la desigualdad de Cauchy-Schwarz, (&sum;u<sub>i</sub>v<sub>i</sub>)<sup>2</sup> &le; "
                "&sum;u<sub>i</sub><sup>2</sup>&sum;v<sub>i</sub><sup>2</sup> = (n &minus; 1)<sup>2</sup>. La igualdad se da "
                "solo si v es proporcional a u, es decir, si los puntos están sobre una recta. Pon &rho; = 1 y lo verás."
            )

        if ui.accordion_step("P1_C", "(C) La pendiente es r"):
            ui.content("En variables tipificadas, ¿cuál es la pendiente de la recta de regresión de v sobre u? ¿Qué tiene que ver con la regresión a la media?")
            ui.spoiler(
                "La pendiente es exactamente r. Una persona una desviación típica por encima en x está, en promedio, solo "
                "r desviaciones por encima en y: más cerca de la media. Es la <b>regresión a la media</b> que Galton "
                "observó en las estaturas de padres e hijos y que dio nombre a la regresión."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + n)
        x, y = bivariate(rho, n, rng)
        r = np.corrcoef(x, y)[0, 1]
        ui.metrics([(f"&rho; = {rho:.2f}", "metric-c"), (f"r = {r:.3f}", "metric-a"),
                    (f"r<sup>2</sup> = {r ** 2:.3f}", "metric-b")])
        ui.show(scatter_chart(dark, x, y, "estatura tipificada", "antebrazo tipificado"), key="fig_galton")
        ui.footer_bar(f"{n} personas simuladas. La recta roja es la de regresión, con pendiente r en variables tipificadas. "
                      "Con muestras pequeñas, r puede alejarse bastante de &rho;.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>forma de la nube</u>")
        if st.session_state["shape"] is None:
            st.session_state["shape"] = v["shape"]
        ui.choice_buttons(list(SHAPES), "shape", labels=SHAPES, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>Lo que r no ve</b><br><br>"
            "Cinco nubes de puntos con cinco historias distintas. Para cada una calculamos el coeficiente de Pearson y el "
            "de <b>Spearman</b>, propuesto por el psicólogo Charles Spearman en 1904: la correlación de Pearson calculada "
            "sobre los rangos, es decir, sobre las posiciones de cada dato al ordenarlos."
        )

        if ui.accordion_step("P2_A", "(A) Relaciones perfectas con r = 0"):
            ui.content("Elige Parábola y Círculo. ¿Son independientes x e y? ¿Por qué r vale casi cero?")
            ui.spoiler(
                "No son independientes: en la parábola y está determinada por x salvo un ruido pequeño. Pero la relación no "
                "es lineal, y los productos positivos de un lado se cancelan con los negativos del otro. La independencia "
                "implica correlación nula; el recíproco es falso. El coeficiente de Spearman tampoco lo ve, porque la "
                "relación no es monótona."
            )

        if ui.accordion_step("P2_B", "(B) Un solo punto"):
            ui.content("Elige Un atípico. Sin él no hay relación. ¿Cuánto vale r con él? ¿Y el de Spearman?")
            ui.spoiler(
                "Un solo punto muy alejado en las dos variables domina las sumas de productos y crea una correlación "
                "importante donde no la hay. El de Spearman lo trata como un dato más, el último en las dos ordenaciones, "
                "y apenas cambia: es <b>robusto</b>. Antes de interpretar un coeficiente hay que dibujar la nube."
            )

        if ui.accordion_step("P2_C", "(C) Dos grupos"):
            ui.content("Elige Dos grupos. ¿Cómo es la relación dentro de cada grupo? ¿Y en el conjunto?")
            ui.spoiler(
                "Dentro de cada grupo la relación es negativa, pero los dos grupos están en esquinas opuestas y la "
                "correlación total es positiva y alta. Mezclar poblaciones distintas puede crear, ocultar o invertir una "
                "correlación, el mismo fenómeno que la paradoja de Simpson. La herramienta de correlaciones espurias "
                "vuelve sobre esto."
            )

    with col_right:
        ui.right_panel()
        shape = st.session_state["shape"]
        rng = np.random.default_rng(v["seed"] + len(shape))
        x, y = shape_data(shape, rng)
        r = np.corrcoef(x, y)[0, 1]
        rs = stats.spearmanr(x, y).statistic
        ui.metrics([(f"Pearson r = {r:.3f}", "metric-a"), (f"Spearman = {rs:.3f}", "metric-b")])
        ui.show(scatter_chart(dark, x, y), key="fig_shapes")
        extra = ""
        if shape == "outlier":
            r0 = np.corrcoef(x[1:], y[1:])[0, 1]
            extra = f" Sin el punto atípico, r = {r0:.3f}."
        ui.footer_bar(f"{len(x)} puntos. La recta roja es la de mínimos cuadrados, la que resume la relación lineal.{extra}")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>correlación observada r</u> y el <u>tamaño n</u>")
        r = st.slider("Correlación observada r", 0.01, 0.95, v["r_obs"], 0.01, key=ui.wkey(PAGE, "r_obs"))
        n = st.select_slider("Pares de padre e hijo n", options=[10, 30, 100, 300, PEARSON_LEE], value=v["n_inf"],
                             key=ui.wkey(PAGE, "n_inf"))

        ui.planteamiento()
        ui.statement(
            "<b>Padres e hijos (1903)</b><br><br>"
            f"Karl Pearson y Alice Lee midieron la estatura de {ui.fmt_int(PEARSON_LEE)} padres y de sus hijos adultos, y "
            "obtuvieron una correlación cercana a 0.5. ¿Qué podemos decir de la correlación &rho; de la población? "
            "Suponemos que las dos estaturas siguen una normal bivariante."
        )

        if ui.accordion_step("P3_A", "(A) ¿Es distinta de cero?"):
            ui.content("Para contrastar H<sub>0</sub>: &rho; = 0 se usa un estadístico t. ¿Cuál, y con qué grados de libertad?")
            ui.spoiler(
                "<div class='formula-box'>t = <sup>r&radic;(n &minus; 2)</sup>&frasl;<sub>&radic;(1 &minus; r<sup>2</sup>)</sub> "
                "~ t<sub>n &minus; 2</sub></div>"
                "Es el mismo test que el de la pendiente en la regresión lineal simple: &rho; = 0 equivale a que la recta sea "
                "horizontal. Con los datos de Pearson y Lee, t pasa de 18 y el p-valor es despreciable."
            )

        if ui.accordion_step("P3_B", "(B) La transformación de Fisher"):
            ui.content(
                "La distribución de r es asimétrica cuando &rho; está lejos de 0, y no sirve para construir un intervalo "
                "sumando y restando. ¿Qué propuso Fisher en 1921?"
            )
            ui.spoiler(
                "Transformar con la arcotangente hiperbólica:"
                "<div class='formula-box'>z = arctanh(r) = &frac12; log <sup>1 + r</sup>&frasl;<sub>1 &minus; r</sub> "
                "&asymp; N( arctanh(&rho;), <sup>1</sup>&frasl;<sub>n &minus; 3</sub> )</div>"
                "Se construye el intervalo para arctanh(&rho;) y se deshace la transformación con tanh. El intervalo para "
                "&rho; queda asimétrico, más corto hacia 1."
            )

        if ui.accordion_step("P3_C", "(C) Significativa pero débil"):
            ui.content("Pon r = 0.10 y n = 1078. ¿Es significativa? ¿Qué proporción de la variabilidad del hijo explica el padre?")
            ui.spoiler(
                "Con n tan grande, r = 0.10 es significativa al 1 %: es casi seguro que &rho; no es cero. Pero r<sup>2</sup> "
                "= 0.01: la relación lineal explica un 1 % de la varianza. Como en el ANOVA, significativo no quiere decir "
                "importante, y al revés, con n = 10 una correlación de 0.5 puede no ser significativa."
            )

    with col_right:
        ui.right_panel()
        t = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
        pval = 2 * stats.t.sf(abs(t), n - 2)
        zc = np.arctanh(r)
        h = 1.96 / np.sqrt(n - 3)
        lo, hi = np.tanh(zc - h), np.tanh(zc + h)
        ui.metrics([(f"t = {t:.2f}", "metric-c"), (f"p-valor: {ui.fmt_sci(pval, 2)}", "metric-a"),
                    (f"IC 95 % para &rho;: [{lo:.3f}, {hi:.3f}]", "metric-b")])
        ui.check(pval < 0.05, "&rho; distinta de 0 al 5 %" if pval < 0.05 else "No se puede descartar &rho; = 0")
        ui.show(fisher_chart(dark, r, n), key="fig_fisher")
        ui.footer_bar("Distribución aproximada de r, según la transformación de Fisher, si &rho; valiera lo que la r observada: "
                      "para tu n y para uno diez veces menor. Al crecer n se estrecha y se vuelve simétrica.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Las co-relaciones de Galton", "P1_A"),
        ("P2", "(II) Lo que r no ve", "P2_A"),
        ("P3", "(III) Padres e hijos", "P3_A"),
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
