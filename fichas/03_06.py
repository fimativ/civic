#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 6: esperanza condicionada.

El revisor del tren (esperanza total y mezclas), los patos y los cazadores
(indicatrices y linealidad sin independencia) y el 53 de Venecia (la
geométrica no tiene memoria).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats

import civic_ui as ui

TITLE = "Esperanza condicionada"
SYMBOL = "E[X|Y]"
PAGE = "03_06"

P53 = 5 / 90


def initial_values():
    return {
        "lam": ui.dint(20, 8, 30, "lam"),
        "works": ui.dchoice(0.90, [0.5, 0.6, 0.7, 0.8, 0.9], "works"),
        "fine": ui.dchoice(50, [20, 30, 50, 80, 100], "fine"),
        "hunters": ui.dint(10, 5, 40, "hunters"),
        "ducks": ui.dint(10, 5, 40, "ducks"),
        "waited": ui.dint(100, 20, 182, "waited"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "duck_sim": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def inspector(lam: float, works: float):
    ks = np.arange(0, int(lam + 6 * np.sqrt(lam)) + 1)
    pmf = works * stats.poisson.pmf(ks, lam)
    pmf[0] += 1 - works
    mean = works * lam
    var = works * lam + lam ** 2 * works * (1 - works)
    return ks, pmf, mean, var


def ducks_expected(n: int, m: int) -> float:
    return m * (1 - (1 - 1 / m) ** n)


def hunt(n: int, m: int, trials: int, rng):
    shots = rng.integers(m, size=(trials, n))
    hit = np.zeros((trials, m), dtype=bool)
    hit[np.arange(trials)[:, None], shots] = True
    return hit.sum(axis=1)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def inspector_chart(dark, ks, pmf, lam, works):
    p = ui.new_figure(dark, height=320, x_axis_label="pasajeros pillados sin billete", y_axis_label="probabilidad",
                      x_range=(-1, ks[-1] + 1), y_range=(0, max(pmf) * 1.15))
    colours = [ui.UBU_RED if k == 0 else ui.BLUE_LINE for k in ks]
    p.vbar(x=ks, top=pmf, width=0.8, fill_color=colours, line_color=None)
    p.add_layout(Span(location=works * lam, dimension="height", line_color=ui.ORANGE_LINE, line_dash="dashed",
                      line_width=2))
    p.xgrid.grid_line_color = None
    return p


def ducks_chart(dark, n: int, m: int, sample):
    ks = np.arange(0, m + 1)
    p = ui.new_figure(dark, height=300, x_axis_label="patos alcanzados", y_axis_label="proporción",
                      x_range=(-0.6, m + 0.6))
    if sample is not None:
        freq = np.bincount(sample, minlength=m + 1)[: m + 1] / len(sample)
        p.vbar(x=ks, top=freq, width=0.8, color=ui.UBU_YELLOW, alpha=0.8, legend_label="simulación")
    p.add_layout(Span(location=ducks_expected(n, m), dimension="height", line_color=ui.UBU_RED, line_width=3))
    if sample is not None:
        ui.style_legend(p, dark, "top_left")
    return p


def waiting_chart(dark, waited: int):
    ls = np.arange(1, 80)
    base = (1 - P53) ** (ls - 1) * P53
    p = ui.new_figure(dark, height=320, x_axis_label="sorteos adicionales hasta que sale el 53",
                      y_axis_label="probabilidad", x_range=(0, 80), y_range=(0, P53 * 1.25))
    p.vbar(x=ls, top=base, width=0.8, color=ui.BLUE_LINE, alpha=0.55, legend_label="sin saber nada")
    p.scatter(ls, base, size=7, color=ui.UBU_RED, legend_label=f"sabiendo que lleva {waited} sin salir")
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cuánto se espera, sabiendo algo?</b>")
        ui.content(
            "Si conocemos que ha ocurrido un suceso B, la distribución de una variable cambia: se calcula "
            "con probabilidades condicionadas, y con ella la <b>esperanza condicionada</b>. <i>Escríbela.</i>"
        )
        ui.formula_hidden("&#120124;[X | B] = &sum;<sub>k</sub> k&middot;&#8473;(X = k | B)")
        ui.content(
            "Si {B<sub>i</sub>} es una partición, la esperanza se reparte entre los casos igual que la "
            "probabilidad en el teorema de la probabilidad total: divide y vencerás. <i>Escribe el teorema "
            "de la esperanza total.</i>"
        )
        ui.formula_hidden("&#120124;[X] = &sum;<sub>i</sub> &#120124;[X | B<sub>i</sub>]&middot;&#8473;(B<sub>i</sub>)")
        ui.content(
            "La otra gran herramienta de la ficha es la linealidad: la esperanza de una suma es la suma de "
            "las esperanzas, sean o no independientes los sumandos. Combinada con las indicatrices, cuya "
            "esperanza es la probabilidad del suceso, permite contar de media sin conocer la distribución."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El revisor del tren</b><br>"
            "<i>Una máquina de multas que a veces falla: calcula cuántos tharni recauda el revisor por "
            "trayecto.</i><br><br>"
            "<b>II. Los patos y los cazadores</b><br>"
            "<i>Cada cazador dispara a un pato al azar, con puntería perfecta. ¿Cuántos patos cenan?</i>"
            "<br><br>"
            "<b>III. El 53 de Venecia (2005)</b><br>"
            "<i>Un número que no salía nunca, un país entero apostando por él y una distribución sin "
            "memoria.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>viajeros sin billete &lambda;</u>, la <u>fiabilidad</u> y la <u>multa</u>")
        lam = st.slider("Media de viajeros sin billete por trayecto λ", 2, 40, v["lam"], 1, key=ui.wkey(PAGE, "lam"))
        c1, c2 = st.columns(2)
        works = c1.slider("Probabilidad de que funcione la máquina", 0.0, 1.0, v["works"], 0.05,
                          key=ui.wkey(PAGE, "works"))
        fine = c2.select_slider("Multa (tharni)", options=[20, 30, 50, 80, 100], value=v["fine"],
                                key=ui.wkey(PAGE, "fine"))

        ui.planteamiento()
        ui.statement(
            "<b>El revisor del tren</b><br><br>"
            "En un tren de cercanías, el número de viajeros sin billete en cada trayecto sigue una Poisson "
            f"de media &lambda; = {v['lam']}. El revisor lleva una máquina de multas que funciona en un trayecto "
            f"con probabilidad {v['works']:.2f}, independientemente de cuántos viajeros vayan sin billete: si "
            "funciona, multa a todos; si falla, a ninguno. Llamemos X al número de viajeros multados en un "
            f"trayecto. Cada multa son {v['fine']} tharni."
        )

        if ui.accordion_step("P1_A", "(A) Condicionar a la máquina"):
            ui.content(
                "Sea B el suceso <i>la máquina funciona</i>. ¿Qué distribución tiene X sabiendo B? ¿Y sabiendo "
                "B<sup>c</sup>? Calcula &#8473;(X = 0) con la probabilidad total."
            )
            ui.spoiler(
                "Si funciona, X es la Poisson completa; si falla, X = 0 con certeza:"
                "<div class='formula-box'>&#8473;(X = 0) = e<sup>&minus;&lambda;</sup>&middot;&#8473;(B) + "
                "1&middot;&#8473;(B<sup>c</sup>)</div>"
                f"Con &lambda; = {v['lam']}, que la Poisson valga 0 tiene probabilidad e<sup>&minus;{v['lam']}</sup>; "
                "cuando &lambda; es grande, casi toda esa probabilidad viene de los fallos de la máquina. Es la barra "
                "roja de la derecha."
            )

        if ui.accordion_step("P1_B", "(B) La esperanza total"):
            ui.content(
                "Calcular &#120124;[X] sumando k&middot;&#8473;(X = k) es farragoso. Hazlo por casos con el teorema "
                "de la esperanza total. ¿Cuántos tharni recauda de media el revisor por trayecto?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124;[X] = &#120124;[X | B]&#8473;(B) + &#120124;[X | B<sup>c</sup>]"
                "&#8473;(B<sup>c</sup>) = &lambda;&middot;&#8473;(B)</div>"
                "La recaudación media es la multa por esa cantidad, por la linealidad: &#120124;[multa&middot;X] = "
                "multa&middot;&#120124;[X]."
            )

        if ui.accordion_step("P1_C", "(C) Una mezcla más dispersa"):
            ui.content(
                "Calcula la varianza de X condicionando también: &#120141;(X) = &#120124;[&#120141;(X | B)] + "
                "&#120141;(&#120124;[X | B]), donde la media y la varianza de fuera se toman sobre B. ¿Cuánto vale "
                "el índice de Fano? Compáralo con el de una Poisson."
            )
            ui.spoiler(
                "<div class='formula-box'>&#120141;(X) = &lambda;&#8473;(B) + &lambda;<sup>2</sup>&#8473;(B)"
                "(1 &minus; &#8473;(B)) &nbsp;&rArr;&nbsp; D = 1 + &lambda;(1 &minus; &#8473;(B))</div>"
                "Es mayor que 1: mezclar una Poisson con el cero produce una variable super-Poisson, "
                "agrupada. Es lo mismo que buscaba Clarke en Londres: la heterogeneidad entre situaciones "
                "infla la varianza."
            )

    with col_right:
        ui.right_panel()
        ks, pmf, mean, var = inspector(lam, works)
        ui.metrics([
            (f"&#120124;[X] = {mean:.2f}", "metric-a"),
            (f"Recaudación media: {mean * fine:.0f} tharni", "metric-b"),
            (f"D = {var / mean:.2f}" if mean > 0 else "D sin definir", "metric-c"),
        ])
        ui.show(inspector_chart(dark, ks, pmf, lam, works), key="fig_inspector")
        ui.footer_bar(f"&#8473;(X = 0) = {pmf[0]:.4f}. La línea discontinua marca la media; la barra roja recoge los "
                      "trayectos sin multas: los fallos de la máquina más los trayectos sin nadie que viaje sin billete.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>cazadores n</u> y los <u>patos m</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Cazadores n", 1, 60, v["hunters"], 1, key=ui.wkey(PAGE, "hunters"))
        m = c2.slider("Patos m", 2, 60, v["ducks"], 1, key=ui.wkey(PAGE, "ducks"))

        ui.planteamiento()
        ui.statement(
            "<b>Los patos y los cazadores</b><br><br>"
            f"En un lago hay m = {v['ducks']} patos y en la orilla n = {v['hunters']} cazadores. A la señal, "
            "cada cazador elige un pato al azar, sin ponerse de acuerdo con los demás, y le acierta seguro. Dos "
            "cazadores pueden haber elegido el mismo pato. ¿Cuántos patos esperan cenar?"
        )

        if ui.accordion_step("P2_A", "(A) Un pato cada vez"):
            ui.content(
                "La distribución del número de patos alcanzados es complicada. Fíjate en uno solo: define la "
                "indicatriz I<sub>j</sub> del suceso <i>el pato j es alcanzado</i>. ¿Cuánto vale "
                "&#120124;[I<sub>j</sub>]?"
            )
            ui.spoiler(
                "El pato j se salva si los n cazadores eligen otros patos, cada uno con probabilidad "
                "1 &minus; 1/m y de forma independiente:"
                "<div class='formula-box'>&#120124;[I<sub>j</sub>] = &#8473;(alcanzado) = 1 &minus; "
                "(1 &minus; 1/m)<sup>n</sup></div>"
            )

        if ui.accordion_step("P2_B", "(B) Linealidad sin independencia"):
            ui.content(
                "El número de patos alcanzados es la suma de las m indicatrices. ¿Son independientes? ¿Importa "
                "para calcular la media?"
            )
            ui.spoiler(
                "No lo son: si un pato es alcanzado, quedan menos disparos para los demás. Pero la esperanza de "
                "una suma es la suma de las esperanzas siempre:"
                "<div class='formula-box'>&#120124;[patos alcanzados] = m&middot;[1 &minus; (1 &minus; 1/m)"
                "<sup>n</sup>]</div>"
                "Para la varianza, en cambio, la dependencia sí cuenta: harían falta las covarianzas entre las "
                "indicatrices, que verás en el tema de vectores aleatorios."
            )

        if ui.accordion_step("P2_C", "(C) Tantos cazadores como patos"):
            ui.content(
                "Pon n = m y haz crecer el número. ¿Qué fracción de los patos acaba alcanzada? ¿Dónde has visto "
                "antes ese número?"
            )
            ui.spoiler(
                "(1 &minus; 1/m)<sup>m</sup> tiende a e<sup>&minus;1</sup>, así que la fracción alcanzada tiende a "
                "1 &minus; 1/e &asymp; 63 %: más de un tercio de los disparos se desperdicia en patos repetidos. "
                "Es el mismo número que el de los regalos de los Reyes Magos y el del álbum de cromos."
            )

    with col_right:
        ui.right_panel()
        expected = ducks_expected(n, m)
        ui.metrics([(f"&#120124;[alcanzados] = {expected:.3f}", "metric-a"),
                    (f"Fracción: {expected / m:.3f}", "metric-c")])
        if st.button("Repetir la cacería 5000 veces", key="duck_play", width="stretch", type="primary"):
            st.session_state["duck_sim"] = (n, m, hunt(n, m, 5000, np.random.default_rng()))
        sim = st.session_state.get("duck_sim")
        sample = sim[2] if sim and sim[:2] == (n, m) else None
        ui.show(ducks_chart(dark, n, m, sample), key="fig_ducks")
        if sample is not None:
            ui.footer_bar(f"Media simulada: {sample.mean():.3f} patos. La línea roja marca la esperanza calculada "
                          f"con indicatrices; con n = m el límite es 1 &minus; 1/e &asymp; {1 - np.exp(-1):.3f}.")
        else:
            ui.footer_bar("La línea roja marca la esperanza calculada con indicatrices. Pulsa el botón para "
                          "compararla con cacerías simuladas.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>sorteos que lleva sin salir</u>")
        waited = st.slider("Sorteos seguidos sin salir el 53", 0, 200, v["waited"], 1, key=ui.wkey(PAGE, "waited"),
                           label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El 53 de Venecia (2005)</b><br><br>"
            "En el lotto italiano, en cada sorteo salen 5 números de 90 en cada una de varias ruedas con "
            "nombre de ciudad. En la rueda de Venecia, el 53 dejó de salir en mayo de 2003 y no volvió a "
            "hacerlo hasta febrero de 2005, después de 182 sorteos. Durante esos meses medio país apostó por "
            "él, cada vez más fuerte, convencido de que estaba a punto de salir. Llamemos G al sorteo en que "
            "aparece el 53, contando desde uno cualquiera."
        )

        if ui.accordion_step("P3_A", "(A) La espera es geométrica"):
            ui.content(
                "¿Con qué probabilidad sale el 53 en un sorteo? Escribe &#8473;(G = k) y &#8473;(G &gt; m). "
                "¿Cuál es la espera media?"
            )
            ui.spoiler(
                "En cada sorteo el 53 está entre los 5 elegidos con probabilidad p = 5/90 = 1/18, y los sorteos "
                "son independientes:"
                "<div class='formula-box'>&#8473;(G = k) = (1 &minus; p)<sup>k&minus;1</sup>p &nbsp;&nbsp; "
                "&#8473;(G &gt; m) = (1 &minus; p)<sup>m</sup> &nbsp;&nbsp; &#120124;[G] = 1/p = 18</div>"
            )

        if ui.accordion_step("P3_B", "(B) Sin memoria"):
            ui.content(
                "Sabiendo que ya han pasado m sorteos sin el 53, calcula la probabilidad de que salga en el "
                "sorteo m + l. Compárala con &#8473;(G = l). ¿Cuánto hay que esperar de media a partir de ahora?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#8473;(G = m + l | G &gt; m) = <sup>(1 &minus; p)<sup>m+l&minus;1</sup>p"
                "</sup>&frasl;<sub>(1 &minus; p)<sup>m</sup></sub> = (1 &minus; p)<sup>l&minus;1</sup>p = "
                "&#8473;(G = l)</div>"
                "La distribución de lo que falta es la misma que al principio: la geométrica olvida los fracasos "
                "pasados, y &#120124;[G | G &gt; m] = m + 18. Tras 182 sorteos sin salir, al 53 le faltaban, de "
                "media, los mismos 18 sorteos que a cualquier otro número. En la figura, los puntos rojos caen "
                "exactamente sobre las barras azules."
            )

        if ui.accordion_step("P3_C", "(C) ¿Tan raro era?"):
            ui.content(
                "Calcula la probabilidad de que un número concreto pase 182 sorteos sin salir en una rueda. "
                "¿Cambia la impresión si piensas en todos los números de todas las ruedas a lo largo de los años?"
            )
            ui.spoiler(
                "Para un número fijado de antemano, (17/18)<sup>182</sup> es del orden de tres entre cien mil. "
                "Pero había 90 números en cada una de diez ruedas y décadas de sorteos: que <i>alguno</i> "
                "acumulara una sequía así en algún momento era mucho menos sorprendente. La rareza de un "
                "suceso hay que medirla antes de mirar los datos, no después."
            )

    with col_right:
        ui.right_panel()
        p_drought = (1 - P53) ** waited
        ui.metrics([
            (f"&#8473;(G &gt; {waited}) = {ui.fmt_sci(p_drought)}", "metric-c"),
            (f"&#120124;[G | G &gt; {waited}] = {waited} + 18", "metric-a"),
        ])
        ui.show(waiting_chart(dark, waited), key="fig_venice")
        ui.footer_bar("La distribución de los sorteos que faltan no depende de cuántos lleve sin salir: haber "
                      "esperado no acerca el premio.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El revisor del tren", "P1_A"),
        ("P2", "(II) Los patos y los cazadores", "P2_A"),
        ("P3", "(III) El 53 de Venecia", "P3_A"),
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
