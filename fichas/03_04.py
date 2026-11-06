#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 4: los modelos de Bernoulli.

La máquina de Galton (binomial), las cajas de cerillas de Banach (binomial
negativa) y la Primitiva (hipergeométrica y su aproximación binomial).
"""

from __future__ import annotations

from math import comb

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Modelos de Bernoulli"
SYMBOL = "B(n,p)"
PAGE = "03_04"


def initial_values():
    return {
        "rows": ui.dint(10, 6, 16, "rows"),
        "bias": ui.dchoice(0.50, [0.40, 0.45, 0.50, 0.55, 0.60], "bias"),
        "matches": ui.dchoice(50, [10, 20, 30, 40, 50, 60], "matches"),
        "N": ui.dchoice(49, [40, 45, 49, 54], "N"),
        "D": ui.dchoice(6, [5, 6, 7], "D"),
        "n": ui.dchoice(6, [5, 6, 7], "n"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "galton_sim": None, "banach_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def drop_balls(rows: int, p: float, balls: int, rng):
    return rng.binomial(rows, p, size=balls)


def banach_pmf(N: int):
    ks = np.arange(N + 1)
    pmf = np.array([comb(2 * N - k, N) / 2 ** (2 * N - k) for k in range(N + 1)], dtype=float)
    return ks, pmf


def simulate_banach(N: int, trials: int, rng):
    """Cada fila es una secuencia de bolsillos; la caja se descubre vacía al
    elegirla por vez N + 1."""
    picks = rng.integers(2, size=(trials, 2 * N + 1))
    left = np.cumsum(picks == 0, axis=1)
    right = np.cumsum(picks == 1, axis=1)
    done = (left == N + 1) | (right == N + 1)
    stop = done.argmax(axis=1)
    rows = np.arange(trials)
    empty_left = left[rows, stop] == N + 1
    return np.where(empty_left, N - right[rows, stop], N - left[rows, stop])


def hyper(N: int, D: int, n: int):
    ks = np.arange(0, min(n, D) + 1)
    pmf = stats.hypergeom.pmf(ks, N, D, n)
    approx = stats.binom.pmf(ks, n, D / N)
    return ks, pmf, approx


# =============================================================================
# 2. FIGURAS
# =============================================================================

def galton_chart(dark, rows: int, p: float, sample):
    ks = np.arange(rows + 1)
    pmf = stats.binom.pmf(ks, rows, p)
    fig = ui.new_figure(dark, height=320, x_axis_label="casilla final (rebotes a la derecha)",
                        y_axis_label="proporción", x_range=(-0.8, rows + 0.8),
                        y_range=(0, max(pmf) * 1.35))
    if sample is not None:
        freq = np.bincount(sample, minlength=rows + 1)[: rows + 1] / len(sample)
        fig.vbar(x=ks, top=freq, width=0.8, color=ui.UBU_YELLOW, alpha=0.75, legend_label="bolas simuladas")
    fig.scatter(ks, pmf, size=11, color=ui.BLUE_LINE, legend_label="B(n, p)")
    fig.line(ks, pmf, line_width=2, color=ui.BLUE_LINE)
    fig.xaxis.ticker = list(ks)
    fig.xgrid.grid_line_color = None
    return ui.style_legend(fig, dark, "top_right")


def banach_chart(dark, N: int, sample):
    ks, pmf = banach_pmf(N)
    fig = ui.new_figure(dark, height=320, x_axis_label="cerillas en la otra caja", y_axis_label="probabilidad",
                        x_range=(-0.8, N + 0.8), y_range=(0, max(pmf) * 1.3))
    if sample is not None:
        freq = np.bincount(sample, minlength=N + 1)[: N + 1] / len(sample)
        fig.vbar(x=ks, top=freq, width=0.8, color=ui.UBU_YELLOW, alpha=0.75, legend_label="simulación")
    fig.scatter(ks, pmf, size=8, color=ui.UBU_RED, legend_label="fórmula de Banach")
    fig.line(ks, pmf, line_width=2, color=ui.UBU_RED)
    mean = float((ks * pmf).sum())
    fig.add_layout(Span(location=mean, dimension="height", line_color=ui.GREY_LINE, line_dash="dashed", line_width=2))
    return ui.style_legend(fig, dark, "top_right")


def lotto_chart(dark, ks, pmf, approx, show_binomial: bool):
    fig = ui.new_figure(dark, height=320, x_axis_label="aciertos", y_axis_type="log",
                        y_range=(max(min(pmf[pmf > 0].min(), approx.min()) * 0.3, 1e-12), 1.5),
                        y_axis_label="probabilidad (escala logarítmica)", x_range=(-0.6, ks[-1] + 0.6))
    fig.vbar(x=ks - (0.18 if show_binomial else 0), bottom=1e-13, top=pmf, width=0.34 if show_binomial else 0.6,
             color=ui.BLUE_LINE, legend_label="hipergeométrica")
    if show_binomial:
        fig.vbar(x=ks + 0.18, bottom=1e-13, top=approx, width=0.34, color=ui.ORANGE_LINE, legend_label="binomial")
    fig.xaxis.ticker = list(ks)
    fig.xgrid.grid_line_color = None
    return ui.style_legend(fig, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué modelos salen de repetir un experimento de dos resultados?</b>")
        ui.content(
            "El ladrillo de la probabilidad discreta es el <b>ensayo de Bernoulli</b>: un experimento con "
            "éxito (1) con probabilidad p y fracaso (0) con probabilidad 1 &minus; p. <i>Escribe su media y "
            "su varianza.</i>"
        )
        ui.formula_hidden("&#120124;[X] = p &nbsp;&nbsp; &#120141;(X) = p(1 &minus; p)")
        ui.content(
            "Repitiendo ensayos independientes salen casi todos los modelos discretos clásicos, según qué se "
            "cuente: el número de éxitos en n ensayos (<b>binomial</b>), los fracasos antes del primer éxito "
            "(<b>geométrica</b>) o antes del n-ésimo (<b>binomial negativa</b>). Si se extrae sin "
            "devolución de una población finita, los ensayos dejan de ser independientes y aparece la "
            "<b>hipergeométrica</b>."
        )
        ui.content("<i>Escribe la función de probabilidad de la binomial y explica qué cuenta el número "
                   "combinatorio.</i>")
        ui.formula_hidden("&#8473;(X = k) = ( <sup>n</sup>&frasl;<sub>k</sub> ) p<sup>k</sup> (1 &minus; p)"
                          "<sup>n&minus;k</sup>, &nbsp; k = 0, 1, &hellip;, n")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La máquina de Galton (1889)</b><br>"
            "<i>Deja caer bolas entre los clavos de Francis Galton y descubre la binomial en cada "
            "rebote.</i><br><br>"
            "<b>II. Las cerillas de Banach</b><br>"
            "<i>Un matemático fumador, dos cajas de cerillas y la binomial negativa.</i><br><br>"
            "<b>III. La Primitiva (1985)</b><br>"
            "<i>Seis números de cuarenta y nueve: cuenta tus aciertos con la hipergeométrica y decide "
            "cuándo basta la binomial.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>filas de clavos n</u> y la <u>inclinación p</u>")
        c1, c2 = st.columns(2)
        rows = c1.slider("Filas de clavos n", 2, 20, v["rows"], 1, key=ui.wkey(PAGE, "rows"))
        p = c2.slider("Probabilidad de rebotar a la derecha p", 0.10, 0.90, v["bias"], 0.05, key=ui.wkey(PAGE, "bias"))

        ui.planteamiento()
        ui.statement(
            "<b>La máquina de Galton (1889)</b><br><br>"
            "Francis Galton (1822-1911), primo de Darwin, mandó construir un tablero de clavos dispuestos en "
            "tresbolillo por el que caen perdigones; lo describió en su libro <i>Herencia natural</i>. En "
            "cada fila, la bola choca con un clavo y sigue a la derecha con probabilidad p o a la izquierda "
            f"con probabilidad 1 &minus; p. Nuestro tablero tiene n = {v['rows']} filas. ¿En qué casilla "
            "acabará una bola?"
        )

        if ui.accordion_step("P1_A", "(A) Un clavo, un ensayo"):
            ui.content(
                "Numera las casillas de abajo por el número de rebotes hacia la derecha. ¿Qué distribución "
                "tiene la casilla final? ¿Cuántos caminos llevan a la casilla k?"
            )
            ui.spoiler(
                "Cada clavo es un ensayo de Bernoulli y los rebotes son independientes, así que la casilla "
                "final es la suma de n Bernoulli: una binomial B(n, p). A la casilla k llegan "
                "( <sup>n</sup>&frasl;<sub>k</sub> ) caminos, tantos como formas de elegir en qué filas se "
                "rebota a la derecha, y todos tienen probabilidad p<sup>k</sup>(1 &minus; p)<sup>n&minus;k</sup>."
            )

        if ui.accordion_step("P1_B", "(B) Media, varianza e índice de Fano"):
            ui.content(
                "Calcula la media y la varianza de la casilla final sin usar la función de probabilidad. "
                "¿Cuánto vale el índice de Fano D = &#120141;(X)/&#120124;[X]?"
            )
            ui.spoiler(
                "La esperanza de la suma es la suma de las esperanzas, y por la independencia la varianza "
                "también se suma:"
                "<div class='formula-box'>&#120124;[X] = np &nbsp;&nbsp; &#120141;(X) = np(1 &minus; p) &nbsp;&nbsp; "
                "D = 1 &minus; p</div>"
                "D &lt; 1: la binomial es menos dispersa que una Poisson de la misma media (sub-Poisson), "
                "porque el número de éxitos no puede pasar de n."
            )

        if ui.accordion_step("P1_C", "(C) La campana"):
            ui.content(
                "Deja caer bolas con muchas filas y p = 0.5. ¿Qué forma tiene el montón? ¿Y si inclinas el "
                "tablero?"
            )
            ui.spoiler(
                "Con muchas filas el montón dibuja una campana centrada en np y de anchura del orden de "
                "&radic;(np(1 &minus; p)), incluso con el tablero inclinado: es el teorema de De Moivre-Laplace, "
                "que convierte la binomial en una normal. Galton usó la máquina para explicar por qué tantas "
                "medidas biológicas, suma de muchas pequeñas causas, se distribuyen así."
            )

    with col_right:
        ui.right_panel()
        mean, var = rows * p, rows * p * (1 - p)
        ui.metrics([(f"&#120124;[X] = {mean:.2f}", "metric-a"), (f"&#120141;(X) = {var:.2f}", "metric-b"),
                    (f"D = {1 - p:.2f}", "metric-c")])
        if st.button("Dejar caer 2000 bolas", key="galton_drop", width="stretch", type="primary"):
            st.session_state["galton_sim"] = (rows, p, drop_balls(rows, p, 2000, np.random.default_rng()))
        sim = st.session_state.get("galton_sim")
        sample = sim[2] if sim and sim[0] == rows and sim[1] == p else None
        ui.show(galton_chart(dark, rows, p, sample), key="fig_galton")
        if sample is not None:
            ui.footer_bar(f"Media de las bolas simuladas: {sample.mean():.2f}; varianza: {sample.var():.2f}.")
        else:
            ui.footer_bar("Pulsa el botón para dejar caer las bolas y compararlas con la binomial.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>cerillas por caja N</u>")
        N = st.slider("Cerillas por caja N", 5, 80, v["matches"], 1, key=ui.wkey(PAGE, "matches"),
                      label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las cerillas de Banach</b><br><br>"
            "En un discurso de homenaje, Hugo Steinhaus contó medio en broma una costumbre que atribuía a su "
            "colega Stefan Banach, gran fumador: llevaba una caja de cerillas en cada bolsillo y, para encender, metía la "
            f"mano en uno de los dos al azar. Cada caja empieza con N = {v['matches']} cerillas. Llega un "
            "momento en que saca una caja y la encuentra vacía. ¿Cuántas cerillas quedan en la otra?"
        )

        if ui.accordion_step("P2_A", "(A) Esperar al éxito número n"):
            ui.content(
                "Repite ensayos de Bernoulli independientes con probabilidad de éxito p. ¿Cuál es la "
                "probabilidad de que antes del n-ésimo éxito haya exactamente k fracasos? ¿Qué pasa con n = 1?"
            )
            ui.spoiler(
                "El último ensayo es forzosamente un éxito, y en los n + k &minus; 1 anteriores hay n &minus; 1 "
                "éxitos colocados de cualquier forma: es la binomial negativa"
                "<div class='formula-box'>&#8473;(X = k) = ( <sup>n + k &minus; 1</sup>&frasl;<sub>k</sub> ) "
                "(1 &minus; p)<sup>k</sup> p<sup>n</sup></div>"
                "Con n = 1 es la geométrica, de media (1 &minus; p)/p, y la binomial negativa es una suma de n "
                "geométricas independientes."
            )

        if ui.accordion_step("P2_B", "(B) Las cerillas"):
            ui.content(
                "Llama éxito a elegir el bolsillo izquierdo. La caja izquierda se descubre vacía cuando se "
                "elige por N + 1 veces. Si en ese momento la derecha conserva k cerillas, ¿cuántas veces se ha "
                "elegido? Escribe &#8473;(K = k) usando la binomial negativa y la simetría entre bolsillos."
            )
            ui.spoiler(
                "La derecha se ha elegido N &minus; k veces antes del éxito número N + 1 del bolsillo "
                "izquierdo, con p = 1/2. Sumando el caso simétrico:"
                "<div class='formula-box'>&#8473;(K = k) = 2&middot;( <sup>2N &minus; k</sup>&frasl;<sub>N &minus; k</sub> )"
                " (1/2)<sup>2N &minus; k + 1</sup> = ( <sup>2N &minus; k</sup>&frasl;<sub>N</sub> ) "
                "(1/2)<sup>2N &minus; k</sup>, &nbsp; k = 0, &hellip;, N</div>"
            )

        if ui.accordion_step("P2_C", "(C) ¿Cuántas quedan de media?"):
            ui.content(
                "Mira la línea discontinua de la derecha y cambia N. ¿Crece la media de K en proporción a N? "
                "¿Por qué es mucho menor que N?"
            )
            ui.spoiler(
                "La media de K crece solo como 2&radic;(N/&pi;) &minus; 1, mucho más despacio que N: con 50 "
                "cerillas por caja quedan unas siete de media en la otra. Para que quedaran muchas, uno de los "
                "bolsillos tendría que haber sido elegido muchas más veces que el otro, y las fluctuaciones "
                "de un paseo al azar de 2N pasos son del orden de &radic;N."
            )

    with col_right:
        ui.right_panel()
        ks, pmf = banach_pmf(N)
        mean = float((ks * pmf).sum())
        ui.metrics([(f"&#120124;[K] = {mean:.3f}", "metric-a"), (f"&#8473;(K = 0) = {pmf[0]:.4f}", "metric-c")])
        if st.button("Simular 3000 cajetillas", key="banach_play", width="stretch", type="primary"):
            st.session_state["banach_sim"] = (N, simulate_banach(N, 3000, np.random.default_rng()))
        sim = st.session_state.get("banach_sim")
        sample = sim[1] if sim and sim[0] == N else None
        ui.show(banach_chart(dark, N, sample), key="fig_banach")
        if sample is not None:
            ui.footer_bar(f"Media simulada: {sample.mean():.3f}, frente a {mean:.3f} de la fórmula. La línea "
                          "discontinua marca la media exacta.")
        else:
            ui.footer_bar("La línea discontinua marca la media exacta. Pulsa el botón para simular.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>números del bombo N</u>, los <u>premiados D</u> y los <u>marcados n</u>")
        c1, c2, c3 = st.columns(3)
        N = c1.number_input("Bombo N", 10, 2000, v["N"], key=ui.wkey(PAGE, "N"))
        D = c2.number_input("Premiados D", 1, min(20, N), min(v["D"], N), key=ui.wkey(PAGE, f"D{N}"))
        n = c3.number_input("Marcados n", 1, min(20, N), min(v["n"], N), key=ui.wkey(PAGE, f"n{N}"))
        show_binomial = st.checkbox("Comparar con la binomial", value=True, key="lotto_binom")

        ui.planteamiento()
        ui.statement(
            "<b>La Primitiva (1985)</b><br><br>"
            "La lotería que Carlos III trajo de Nápoles en 1763 se recuperó en 1985 con el nombre de "
            "Primitiva: el jugador marca 6 números de 49 y del bombo salen 6 sin devolución. Cada apuesta "
            "cuesta un tharni. Llama X al número de aciertos. ¿Qué probabilidad hay de acertar 3, 4, 5 o los "
            "6? ¿Y si el bombo tuviera muchos más números?"
        )

        if ui.accordion_step("P3_A", "(A) Contar boletos"):
            ui.content(
                "Hay ( <sup>N</sup>&frasl;<sub>n</sub> ) combinaciones posibles de los números marcados. "
                "¿Cuántas tienen exactamente k de los D premiados? Escribe la función de probabilidad."
            )
            ui.spoiler(
                "Se eligen k de los D premiados y n &minus; k de los N &minus; D restantes; por la regla de Laplace:"
                "<div class='formula-box'>&#8473;(X = k) = <sup>( <sup>D</sup>&frasl;<sub>k</sub> ) "
                "( <sup>N &minus; D</sup>&frasl;<sub>n &minus; k</sub> )</sup>&frasl;<sub>( <sup>N</sup>&frasl;"
                "<sub>n</sub> )</sub></div>"
                "Es la hipergeométrica. Con N = 49 y n = D = 6, el pleno tiene probabilidad 1 entre "
                "13 983 816."
            )

        if ui.accordion_step("P3_B", "(B) Media con indicatrices"):
            ui.content(
                "Escribe X como suma de indicatrices, una por cada número marcado. ¿Son independientes? "
                "¿Importa para calcular la media? ¿Y para la varianza?"
            )
            ui.spoiler(
                "X = &sum; 1<sub>A<sub>i</sub></sub>, donde A<sub>i</sub> es <i>el número marcado i sale del "
                "bombo</i>, con &#8473;(A<sub>i</sub>) = D/N. La linealidad de la esperanza no necesita "
                "independencia:"
                "<div class='formula-box'>&#120124;[X] = n<sup>D</sup>&frasl;<sub>N</sub> &nbsp;&nbsp; "
                "&#120141;(X) = n<sup>D</sup>&frasl;<sub>N</sub><sup>N &minus; D</sup>&frasl;<sub>N</sub>"
                "<sup>N &minus; n</sup>&frasl;<sub>N &minus; 1</sub></div>"
                "La varianza sí nota la dependencia: el factor (N &minus; n)/(N &minus; 1), la corrección por "
                "población finita, la hace menor que la de la binomial."
            )

        if ui.accordion_step("P3_C", "(C) ¿Cuándo basta la binomial?"):
            ui.content(
                "Si se extrajera con devolución, X sería binomial B(n, D/N). Activa la comparación y aumenta "
                "N manteniendo la proporción de premiados. ¿Cuándo se parecen las dos distribuciones?"
            )
            ui.spoiler(
                "Cuando la población es grande y la muestra pequeña, sacar una bola apenas cambia la "
                "composición del bombo y da casi igual devolverla o no. La regla práctica de los apuntes pide "
                "N &gt; 50 y n &le; 0.1N. En la Primitiva no se cumple, y la binomial sobrestima la "
                "probabilidad del pleno casi cincuenta veces."
            )

    with col_right:
        ui.right_panel()
        ks, pmf, approx = hyper(N, D, n)
        top = ks[-1]
        three = float(pmf[ks >= min(3, top)].sum())
        ui.metrics([
            (f"&#8473;(X = {top}) = 1 entre {ui.fmt_int(round(1 / pmf[-1]))}", "metric-a"),
            (f"&#8473;(X &ge; {min(3, top)}) = {three:.5f}", "metric-c"),
        ])
        ui.show(lotto_chart(dark, ks, pmf, approx, show_binomial), key="fig_lotto")
        mean = n * D / N
        var = mean * (N - D) / N * (N - n) / (N - 1) if N > 1 else 0.0
        ui.footer_bar(f"&#120124;[X] = {mean:.4f}, &#120141;(X) = {var:.4f}; la binomial daría una varianza de "
                      f"{n * D / N * (1 - D / N):.4f}. Con un tharni por apuesta, el pleno sale de media una vez cada "
                      f"{ui.fmt_int(round(1 / pmf[-1]))} tharni jugados.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La máquina de Galton", "P1_A"),
        ("P2", "(II) Las cerillas de Banach", "P2_A"),
        ("P3", "(III) La Primitiva", "P3_A"),
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
