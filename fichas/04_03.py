#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 4, ficha 3: la distribución normal.

Los soldados escoceses de Quetelet (ajustar una normal a datos reales), Gauss
en el billete de diez marcos (tipificar y usar las tablas) y el gráfico de
control de Shewhart (la regla de las tres sigmas).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import BoxAnnotation, Span
from scipy import stats

import civic_ui as ui

TITLE = "La distribución normal"
SYMBOL = "N(μ,σ)"
PAGE = "04_03"

# Perímetro torácico (pulgadas) de 5738 soldados escoceses, publicado en 1817 y reanalizado por Quetelet.
CHESTS = {33: 3, 34: 18, 35: 81, 36: 185, 37: 420, 38: 749, 39: 1073, 40: 1079, 41: 934, 42: 658,
          43: 370, 44: 92, 45: 50, 46: 21, 47: 4, 48: 1}


def initial_values():
    return {
        "mu_fit": ui.dfloat(39.0, 37.5, 41.5, "mu_fit", 1),
        "sd_fit": ui.dfloat(1.5, 1.0, 3.0, "sd_fit", 1),
        "mu": ui.dint(163, 158, 170, "mu"),
        "sd": ui.dint(6, 4, 9, "sd"),
        "minimum": ui.dint(155, 148, 160, "minimum"),
        "shift": ui.dchoice(1.0, [0.5, 1.0, 1.5, 2.0], "shift"),
        "seed": int(ui.r("shewhart") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "shewhart_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def chest_stats():
    x = np.array(list(CHESTS), dtype=float)
    f = np.array(list(CHESTS.values()), dtype=float)
    n = f.sum()
    mean = float((x * f).sum() / n)
    sd = float(np.sqrt(((x - mean) ** 2 * f).sum() / (n - 1)))
    return x, f, int(n), mean, sd


def within(mean: float, sd: float, k: float) -> float:
    x, f, n, *_ = chest_stats()
    return float(f[np.abs(x - mean) <= k * sd].sum() / n)


def detect_prob(shift: float, k: float) -> float:
    return float(1 - (stats.norm.cdf(k - shift) - stats.norm.cdf(-k - shift)))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def chest_chart(dark, mu: float, sd: float):
    x, f, n, *_ = chest_stats()
    xs = np.linspace(31, 50, 400)
    p = ui.new_figure(dark, height=320, x_axis_label="perímetro torácico (pulgadas)", y_axis_label="soldados",
                      x_range=(31.5, 49.5), y_range=(0, max(f.max(), n * stats.norm.pdf(mu, mu, sd)) * 1.12))
    p.vbar(x=x, top=f, width=0.85, color=ui.BLUE_LINE, alpha=0.75, legend_label="datos (1817)")
    p.line(xs, n * stats.norm.pdf(xs, mu, sd), line_width=4, color=ui.UBU_RED, legend_label=f"normal N({mu:.1f}, {sd:.1f})")
    for s in (-1, 1):
        p.add_layout(Span(location=mu + s * sd, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted",
                          line_width=1))
    return ui.style_legend(p, dark, "top_right")


def standard_chart(dark, mu: float, sd: float, a: float, b: float):
    xs = np.linspace(mu - 4 * sd, mu + 4 * sd, 500)
    dens = stats.norm.pdf(xs, mu, sd)
    p = ui.new_figure(dark, height=300, x_axis_label=f"talla x (cm)   ·   z = (x − {mu:g})/{sd:g}",
                      y_axis_label="densidad", x_range=(xs[0], xs[-1]), y_range=(0, dens.max() * 1.15))
    mask = (xs >= a) & (xs <= b)
    p.varea(x=xs[mask], y1=0, y2=dens[mask], color=ui.UBU_YELLOW, alpha=0.7)
    p.line(xs, dens, line_width=4, color=ui.BLUE_LINE)
    ticks = [mu + k * sd for k in range(-3, 4)]
    p.xaxis.ticker = ticks
    p.xaxis.major_label_overrides = {t: f"{t:g} | {k:+d}" for t, k in zip(ticks, range(-3, 4))}
    p.xaxis.major_label_orientation = 0.5
    return p


def control_chart(dark, shift: float, k: float, seed: int):
    rng = np.random.default_rng(seed)
    n = 60
    z = rng.normal(0, 1, n)
    z[30:] += shift
    idx = np.arange(1, n + 1)
    out = np.abs(z) > k
    p = ui.new_figure(dark, height=320, x_axis_label="muestra", y_axis_label="desviación (en σ)",
                      x_range=(0, n + 1), y_range=(-4.5, 4.5 + shift))
    p.add_layout(BoxAnnotation(bottom=-k, top=k, fill_color=ui.GREEN_LINE, fill_alpha=0.08))
    for s in (-k, k):
        p.add_layout(Span(location=s, dimension="width", line_color=ui.RED_LINE, line_dash="dashed", line_width=2))
    p.add_layout(Span(location=30.5, dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    p.line(idx, z, line_width=2, color=ui.BLUE_LINE)
    p.scatter(idx[~out], z[~out], size=8, color=ui.BLUE_LINE)
    p.scatter(idx[out], z[out], size=13, color=ui.RED_LINE, marker="diamond")
    return p, int(out[:30].sum()), int(out[30:].sum())


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Por qué la campana aparece en todas partes?</b>")
        ui.content(
            "La distribución normal, o de Gauss, es la idealización de un histograma simétrico y en forma de "
            "campana. Depende de dos parámetros: &mu;, el eje de simetría, y &sigma;, la anchura. <i>Escribe su "
            "densidad.</i>"
        )
        ui.formula_hidden("f(x) = <sup>1</sup>&frasl;<sub>&sigma;&radic;(2&pi;)</sub> e<sup>&minus;(x &minus; &mu;)"
                          "<sup>2</sup>/(2&sigma;<sup>2</sup>)</sup>, &nbsp; x &isin; &#8477;")
        ui.content(
            "Su media es &mu; y su varianza &sigma;<sup>2</sup>; la curva cambia de concavidad en &mu; &plusmn; "
            "&sigma;. Aparece tanto porque es el límite de sumas de muchas pequeñas causas independientes, como "
            "anunciaban la máquina de Galton y los dados de Galileo. Su densidad no tiene primitiva elemental, "
            "pero basta una tabla: cualquier normal se reduce a la típica N(0, 1). <i>Escribe la "
            "tipificación.</i>"
        )
        ui.formula_hidden("X ~ N(&mu;, &sigma;) &nbsp;&rArr;&nbsp; Z = <sup>X &minus; &mu;</sup>&frasl;<sub>&sigma;</sub> "
                          "~ N(0, 1), &nbsp; F(c) = &Phi;(<sup>c &minus; &mu;</sup>&frasl;<sub>&sigma;</sub>)")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Los soldados de Quetelet (1846)</b><br>"
            "<i>Ajusta con Adolphe Quetelet una campana al pecho de 5738 soldados escoceses.</i><br><br>"
            "<b>II. Gauss en el billete de diez marcos</b><br>"
            "<i>Tipifica la talla de los quintos y calcula probabilidades con una sola tabla.</i><br><br>"
            "<b>III. El gráfico de Shewhart (1924)</b><br>"
            "<i>Vigila una fábrica con Walter Shewhart y la regla de las tres sigmas.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("ajusta la <u>media &mu;</u> y la <u>desviación &sigma;</u>")
        c1, c2 = st.columns(2)
        mu = c1.slider("μ (pulgadas)", 36.0, 44.0, v["mu_fit"], 0.1, key=ui.wkey(PAGE, "mu_fit"))
        sd = c2.slider("σ (pulgadas)", 0.5, 4.0, v["sd_fit"], 0.1, key=ui.wkey(PAGE, "sd_fit"))

        ui.planteamiento()
        ui.statement(
            "<b>Los soldados de Quetelet (1846)</b><br><br>"
            "Adolphe Quetelet, astrónomo belga, llevó la curva de los errores de los astrónomos a las medidas "
            "humanas. Su ejemplo más célebre fue una tabla publicada en Edimburgo en 1817: el perímetro "
            "torácico de 5738 soldados escoceses, redondeado a la pulgada. Quetelet vio en ella la campana de "
            "Gauss y en su centro al <i>hombre medio</i>. ¿Encaja de verdad una normal?"
        )

        if ui.accordion_step("P1_A", "(A) Ajustar la campana"):
            ui.content(
                "Mueve &mu; y &sigma; hasta que la curva roja se ajuste a las barras. Después calcula la media y la "
                "desviación típica de los datos. ¿Coinciden con lo que has elegido a ojo?"
            )
            _, _, n, mean, sdv = chest_stats()
            ui.spoiler(
                f"La media de los datos es {mean:.2f} pulgadas y la desviación típica {sdv:.2f}. Con esos valores "
                "la normal reproduce la tabla con notable precisión: igualar la media y la varianza teóricas a "
                "las observadas es, otra vez, el método de los momentos."
            )

        if ui.accordion_step("P1_B", "(B) La regla del 68-95-99.7"):
            ui.content(
                "En una normal, ¿qué probabilidad queda a menos de una, dos y tres desviaciones de la media? "
                "Compruébalo con los soldados y compáralo con lo que garantizaba Chebyshev."
            )
            _, _, n, mean, sdv = chest_stats()
            ui.spoiler(
                "<div class='formula-box'>&#8473;(|X &minus; &mu;| &le; k&sigma;) = &Phi;(k) &minus; &Phi;(&minus;k) "
                "&asymp; 0.683, 0.954, 0.997 &nbsp; (k = 1, 2, 3)</div>"
                f"En los datos, las proporciones son {within(mean, sdv, 1):.3f}, {within(mean, sdv, 2):.3f} y "
                f"{within(mean, sdv, 3):.3f} (el redondeo a la pulgada las altera un poco). Chebyshev solo "
                "garantizaba 0, 0.75 y 0.89: conocer la forma de la distribución vale mucho."
            )

        if ui.accordion_step("P1_C", "(C) Concavidad e inflexión"):
            ui.content(
                "Deriva dos veces la densidad normal. ¿Dónde cambia de concavidad? Comprueba en la figura que las "
                "líneas punteadas, en &mu; &plusmn; &sigma;, caen donde la campana deja de curvarse hacia abajo."
            )
            ui.spoiler(
                "<div class='formula-box'>f''(x) = <sup>f(x)</sup>&frasl;<sub>&sigma;<sup>2</sup></sub>"
                "[<sup>(x &minus; &mu;)<sup>2</sup></sup>&frasl;<sub>&sigma;<sup>2</sup></sub> &minus; 1]</div>"
                "Se anula en x = &mu; &plusmn; &sigma;: la campana es cóncava hacia abajo entre esos dos puntos y "
                "hacia arriba fuera. Por eso &sigma; se puede leer a ojo en una gráfica: es la distancia del "
                "centro a los puntos de inflexión."
            )

    with col_right:
        ui.right_panel()
        x, f, n, mean, sdv = chest_stats()
        expected = n * (stats.norm.cdf(x + 0.5, mu, sd) - stats.norm.cdf(x - 0.5, mu, sd))
        ui.metrics([(f"Media de los datos = {mean:.2f}", "metric-a"), (f"&sigma; de los datos = {sdv:.2f}", "metric-b")])
        ui.show(chest_chart(dark, mu, sd), key="fig_chest")
        ui.footer_bar(f"Con &mu; = {mu:.1f} y &sigma; = {sd:.1f}, la suma de diferencias absolutas entre la tabla y la "
                      f"normal es {np.abs(f - expected).sum():.0f} soldados. Acércate a la media y la desviación de "
                      "los datos para minimizarla.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>media</u>, la <u>desviación</u> y el <u>intervalo de tallas</u>")
        c1, c2 = st.columns(2)
        mu = c1.slider("μ (cm)", 150, 180, v["mu"], 1, key=ui.wkey(PAGE, "mu"))
        sd = c2.slider("σ (cm)", 2, 12, v["sd"], 1, key=ui.wkey(PAGE, "sd"))
        a, b = st.slider("Intervalo de tallas [a, b] (cm)", 130.0, 200.0, (float(v["minimum"]), 200.0), 0.5,
                         key=ui.wkey(PAGE, f"ab{mu}{sd}"))

        ui.planteamiento()
        ui.statement(
            "<b>Gauss en el billete de diez marcos</b><br><br>"
            "Durante una década, los alemanes llevaron en la cartera a Carl Friedrich Gauss: su retrato, junto "
            "a la campana y su fórmula, ilustraba el billete de diez marcos. Gauss la había obtenido en 1809 "
            "como ley de los errores de medida en astronomía. Usémosla para la talla de los quintos: en "
            f"nuestro reemplazo es normal con &mu; = {v['mu']} cm y &sigma; = {v['sd']} cm, y no se admitía a "
            f"quien no alcanzaba {v['minimum']} cm. ¿Qué fracción de los mozos quedaba fuera?"
        )

        if ui.accordion_step("P2_A", "(A) Tipificar"):
            ui.content(
                "Escribe &#8473;(X &lt; mínimo) en función de &Phi;, la distribución de la normal típica. ¿Por qué "
                "basta una sola tabla para todas las normales?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(X &lt; m) = &#8473;(<sup>X &minus; &mu;</sup>&frasl;<sub>&sigma;</sub> "
                "&lt; <sup>m &minus; &mu;</sup>&frasl;<sub>&sigma;</sub>) = &Phi;(<sup>m &minus; &mu;</sup>&frasl;"
                "<sub>&sigma;</sub>)</div>"
                "Restar &mu; y dividir por &sigma; convierte cualquier normal en la N(0, 1). La tabla de &Phi; "
                "sirve para todas: solo cambia el punto z = (m &minus; &mu;)/&sigma; en el que se consulta, el "
                "número de desviaciones a que está m de la media. En el eje de la figura se leen a la vez la "
                "talla y ese número."
            )

        if ui.accordion_step("P2_B", "(B) Intervalos y simetría"):
            ui.content(
                "Las tablas solo traen &Phi;(z) para z &ge; 0. ¿Cómo calculas &Phi;(&minus;1.5)? Escribe la "
                "probabilidad de un intervalo [a, b] con &Phi;."
            )
            ui.spoiler(
                "Por la simetría de la campana respecto a 0, &Phi;(&minus;z) = 1 &minus; &Phi;(z). Y para un "
                "intervalo se resta:"
                "<div class='formula-box'>&#8473;(a &le; X &le; b) = &Phi;(<sup>b &minus; &mu;</sup>&frasl;<sub>&sigma;"
                "</sub>) &minus; &Phi;(<sup>a &minus; &mu;</sup>&frasl;<sub>&sigma;</sub>)</div>"
                "Como en toda variable continua, da igual que los extremos estén incluidos o no."
            )

        if ui.accordion_step("P2_C", "(C) Cambiar de unidades"):
            ui.content(
                "Si X es la talla en centímetros, ¿qué distribución tiene la talla en pulgadas, X/2.54? ¿Y en "
                "general aX + b?"
            )
            ui.spoiler(
                "<div class='formula-box'>X ~ N(&mu;, &sigma;) &nbsp;&rArr;&nbsp; aX + b ~ N(a&mu; + b, |a|&sigma;)</div>"
                "Una transformación lineal de una normal es normal: se desplaza el centro y se escala la anchura. "
                "La tipificación es el caso a = 1/&sigma;, b = &minus;&mu;/&sigma;. Las probabilidades no "
                "cambian: los mismos mozos quedan fuera midan en centímetros o en pulgadas."
            )

    with col_right:
        ui.right_panel()
        a, b = min(a, b), max(a, b)
        za, zb = (a - mu) / sd, (b - mu) / sd
        prob = float(stats.norm.cdf(zb) - stats.norm.cdf(za))
        ui.metrics([(f"z<sub>a</sub> = {za:+.2f}, z<sub>b</sub> = {zb:+.2f}", "metric-c"),
                    (f"&#8473;({a:g} &le; X &le; {b:g}) = {prob:.4f}", "metric-a")])
        ui.show(standard_chart(dark, mu, sd, a, b), key="fig_gauss")
        ui.footer_bar(f"&Phi;({zb:+.2f}) &minus; &Phi;({za:+.2f}) = {prob:.4f}. Fuera del intervalo queda "
                      f"{1 - prob:.4f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>desajuste del proceso</u> y los <u>límites de control</u>")
        c1, c2 = st.columns(2)
        shift = c1.slider("Desajuste a partir de la muestra 31 (en σ)", 0.0, 3.0, v["shift"], 0.25,
                          key=ui.wkey(PAGE, "shift"))
        k = c2.select_slider("Límites de control (± k σ)", options=[2.0, 2.5, 3.0, 3.5], value=3.0, key="shewhart_k")

        ui.planteamiento()
        ui.statement(
            "<b>El gráfico de Shewhart (1924)</b><br><br>"
            "El 16 de mayo de 1924 Walter Shewhart, ingeniero de la Western Electric (poco después, de los laboratorios Bell), entregó a su jefe un "
            "memorando de una página con un dibujo: el primer gráfico de control. Una máquina fabrica piezas "
            "cuya medida, con la máquina bien ajustada, es normal; se marca cada muestra en desviaciones "
            "respecto al valor nominal y se da la alarma si se sale de &plusmn;k&sigma;. ¿Dónde poner los "
            "límites?"
        )

        if ui.accordion_step("P3_A", "(A) La regla de las tres sigmas"):
            ui.content(
                "Con la máquina bien ajustada, ¿con qué probabilidad cae una muestra fuera de &plusmn;3&sigma;? "
                "Compáralo con la cota de Chebyshev."
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(|Z| &gt; 3) = 2(1 &minus; &Phi;(3)) &asymp; 0.0027</div>"
                "Unas tres muestras de cada mil dan la alarma sin motivo. Chebyshev solo garantizaba 1/9, más de "
                "cuarenta veces más: el gráfico de Shewhart aprovecha que conoce la forma de la distribución."
            )

        if ui.accordion_step("P3_B", "(B) Falsas alarmas"):
            ui.content(
                "Si las muestras son independientes, ¿cuántas hay que tomar de media hasta la primera falsa "
                "alarma? ¿Qué distribución tiene ese número?"
            )
            ui.spoiler(
                "El número de muestras hasta la primera alarma es geométrico con p = 0.0027, de media 1/p "
                "&asymp; 370: la <i>longitud media de racha</i> de un proceso bajo control. Bajar los límites a "
                "2&sigma; detecta antes los problemas, pero la longitud media cae a unas 22 muestras y la "
                "fábrica se para por nada."
            )

        if ui.accordion_step("P3_C", "(C) Detectar un desajuste"):
            ui.content(
                "Si la media se desplaza &delta; desviaciones, ¿con qué probabilidad sale una muestra de los "
                "límites? ¿Cuántas muestras hacen falta de media para darse cuenta?"
            )
            ui.spoiler(
                "Tras el desajuste, Z &minus; &delta; es normal típica:"
                "<div class='formula-box'>&#8473;(alarma) = 1 &minus; [&Phi;(k &minus; &delta;) &minus; "
                "&Phi;(&minus;k &minus; &delta;)]</div>"
                "Con &delta; = 1 y k = 3 vale en torno a 0.023: hacen falta unas 44 muestras de media para "
                "detectarlo. Desajustes pequeños se escapan mucho tiempo a un gráfico de tres sigmas, y por eso "
                "se añadieron después reglas que miran varias muestras seguidas."
            )

    with col_right:
        ui.right_panel()
        false_alarm = detect_prob(0.0, k)
        detect = detect_prob(shift, k)
        ui.metrics([(f"Falsa alarma: {false_alarm:.4f} (racha media {1 / false_alarm:.0f})", "metric-c"),
                    (f"Detección: {detect:.4f} (racha media {1 / detect:.1f})", "metric-a")])
        if st.button("Otras 60 muestras", key="shewhart_new", width="stretch"):
            st.session_state["shewhart_round"] += 1
        fig, before, after = control_chart(dark, shift, k, v["seed"] + st.session_state["shewhart_round"])
        ui.show(fig, key="fig_shewhart")
        ui.footer_bar(f"Alarmas en las 30 primeras muestras (proceso ajustado): {before}. En las 30 siguientes "
                      f"(desajuste de {shift:g}&sigma;): {after}. La línea punteada marca el desajuste.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Los soldados de Quetelet", "P1_A"),
        ("P2", "(II) Gauss en el billete", "P2_A"),
        ("P3", "(III) El gráfico de Shewhart", "P3_A"),
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
