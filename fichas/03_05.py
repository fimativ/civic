#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 3, ficha 5: Poisson y los sucesos raros.

Las coces de caballo en el ejército prusiano (ajuste de una Poisson a datos
reales), el paso al límite desde la binomial y las bombas volantes sobre
Londres (el índice de Fano como prueba de agrupamiento).
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from scipy import stats

import civic_ui as ui

TITLE = "Poisson y los sucesos raros"
SYMBOL = "P(λ)"
PAGE = "03_05"

# Bortkiewicz (1898): muertes por coz de caballo en 10 cuerpos del ejército prusiano, 1875-1894.
KICKS = {0: 109, 1: 65, 2: 22, 3: 3, 4: 1}
# Clarke (1946): impactos de bombas volantes en 576 cuadrículas del sur de Londres.
BOMBS = {0: 229, 1: 211, 2: 93, 3: 35, 4: 7, 7: 1}
GRID = 24
PATTERNS = {"rand": "Al azar", "target": "Apuntando a objetivos", "even": "Repartidas"}


def initial_values():
    return {
        "lam_fit": ui.dfloat(0.61, 0.30, 1.10, "lam_fit"),
        "lam": ui.dchoice(2.0, [1.0, 1.5, 2.0, 3.0, 4.0], "lam"),
        "n": ui.dchoice(20, [10, 20, 30, 50], "n"),
        "pattern": ui.dchoice("rand", list(PATTERNS), "pattern"),
        "seed": int(ui.r("bombs") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "pattern": None, "bomb_round": 0})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def table_stats(table: dict):
    values = np.array(list(table.keys()), dtype=float)
    counts = np.array(list(table.values()), dtype=float)
    total = counts.sum()
    mean = float((values * counts).sum() / total)
    var = float(((values - mean) ** 2 * counts).sum() / (total - 1))
    return mean, var, int(total)


def tv_distance(n: int, lam: float) -> float:
    ks = np.arange(0, n + 1)
    b = stats.binom.pmf(ks, n, lam / n)
    po = stats.poisson.pmf(ks, lam)
    tail = stats.poisson.sf(n, lam)
    return float(0.5 * (np.abs(b - po).sum() + tail))


def drop_bombs(pattern: str, seed: int, bombs: int = 537):
    rng = np.random.default_rng(seed)
    if pattern == "rand":
        x, y = rng.integers(GRID, size=bombs), rng.integers(GRID, size=bombs)
    elif pattern == "target":
        centres = rng.uniform(2, GRID - 2, size=(6, 2))
        pick = rng.integers(6, size=bombs)
        pts = centres[pick] + rng.normal(0, 2.2, size=(bombs, 2))
        pts = np.clip(pts, 0, GRID - 1e-6)
        x, y = pts[:, 0].astype(int), pts[:, 1].astype(int)
    else:
        cells = rng.permutation(GRID * GRID)
        extra = rng.integers(GRID * GRID, size=max(0, bombs - GRID * GRID))
        flat = np.concatenate((cells[: min(bombs, GRID * GRID)], extra)).astype(int)
        x, y = flat % GRID, flat // GRID
    counts = np.zeros((GRID, GRID), dtype=int)
    np.add.at(counts, (y, x), 1)
    return counts


# =============================================================================
# 2. FIGURAS
# =============================================================================

def fit_chart(dark, table: dict, lam: float):
    total = sum(table.values())
    ks = np.arange(0, max(table) + 1)
    observed = np.array([table.get(k, 0) for k in ks])
    expected = total * stats.poisson.pmf(ks, lam)
    p = ui.new_figure(dark, height=320, x_axis_label="número de sucesos por unidad",
                      y_axis_label="frecuencia", x_range=(-0.6, ks[-1] + 0.6),
                      y_range=(0, max(observed.max(), expected.max()) * 1.15))
    p.vbar(x=ks - 0.18, top=observed, width=0.34, color=ui.BLUE_LINE, legend_label="observado")
    p.vbar(x=ks + 0.18, top=expected, width=0.34, color=ui.ORANGE_LINE, legend_label=f"Poisson (λ = {lam:.2f})")
    p.xaxis.ticker = list(ks)
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


def limit_chart(dark, n: int, lam: float):
    top = int(max(10, lam + 5 * np.sqrt(lam)))
    ks = np.arange(0, top + 1)
    p = ui.new_figure(dark, height=320, x_axis_label="k", y_axis_label="probabilidad", x_range=(-0.6, top + 0.6))
    p.vbar(x=ks - 0.18, top=stats.binom.pmf(ks, n, lam / n), width=0.34, color=ui.BLUE_LINE,
           legend_label=f"B({n}, λ/{n})")
    p.vbar(x=ks + 0.18, top=stats.poisson.pmf(ks, lam), width=0.34, color=ui.ORANGE_LINE, legend_label=f"Poisson ({lam})")
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


def map_chart(dark, counts):
    ys, xs = np.mgrid[0:GRID, 0:GRID]
    flat = counts.ravel()
    palette = ["#f2f2f2" if not dark else "#26262e", "#f6c9c9", "#e57373", "#c62828", "#7f0000"]
    colours = [palette[min(int(c), 4)] for c in flat]
    p = ui.new_figure(dark, height=330, x_range=(-0.5, GRID - 0.5), y_range=(-0.5, GRID - 0.5), match_aspect=True)
    p.rect(x=xs.ravel(), y=ys.ravel(), width=0.95, height=0.95, fill_color=colours, line_color=None)
    p.grid.visible = False
    p.axis.visible = False
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se cuentan los sucesos raros?</b>")
        ui.content(
            "Erratas por página, llamadas a una centralita en un minuto, accidentes en un cruce en un año: "
            "sucesos que tienen muchísimas oportunidades de ocurrir y una probabilidad pequeñísima en cada "
            "una. Su número sigue la distribución de <b>Poisson</b>, también llamada ley de los sucesos "
            "raros, con un único parámetro &lambda;, el número medio de sucesos. <i>Escribe su función de "
            "probabilidad.</i>"
        )
        ui.formula_hidden("&#8473;(X = k) = e<sup>&minus;&lambda;</sup> <sup>&lambda;<sup>k</sup></sup>&frasl;"
                          "<sub>k!</sub>, &nbsp; k = 0, 1, 2, &hellip;")
        ui.content(
            "Su media y su varianza coinciden: las dos valen &lambda;. Por eso el cociente "
            "D = &#120141;(X)/&#120124;[X], el <b>índice de Fano</b>, vale exactamente 1 para una Poisson, y "
            "sirve de referencia: D &lt; 1 indica datos más regulares que el azar puro (sub-Poisson) y D &gt; 1, "
            "datos agrupados o contagiosos (super-Poisson)."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las coces de los caballos prusianos (1898)</b><br>"
            "<i>Ajusta con Ladislaus Bortkiewicz una Poisson a veinte años de muertes en la "
            "caballería.</i><br><br>"
            "<b>II. Juicios y jurados (1837)</b><br>"
            "<i>Lleva con Siméon Denis Poisson la binomial al límite y descubre cuándo se puede "
            "cambiar una por otra.</i><br><br>"
            "<b>III. Las bombas sobre Londres (1946)</b><br>"
            "<i>¿Apuntaban o caían al azar? Responde con el actuario R. D. Clarke y el índice de "
            "Fano.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("ajusta el <u>parámetro &lambda;</u> a los datos")
        lam = st.slider("λ", 0.10, 1.50, v["lam_fit"], 0.01, key=ui.wkey(PAGE, "lam_fit"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Las coces de los caballos prusianos (1898)</b><br><br>"
            "Ladislaus Bortkiewicz (1868-1931), economista y estadístico ruso de origen polaco, publicó un librito titulado "
            "<i>La ley de los números pequeños</i>. Su ejemplo más famoso: los soldados muertos por la coz "
            "de un caballo en diez cuerpos del ejército prusiano durante veinte años, de 1875 a 1894. Son "
            "200 observaciones (un cuerpo en un año), y en 109 de ellas no murió nadie. ¿Sigue el número de "
            "muertes una distribución de Poisson?"
        )
        ui.content("<table><tr><th>muertes</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th></tr>"
                   "<tr><td>cuerpos-año</td>" + "".join(f"<td>{c}</td>" for c in KICKS.values()) + "</tr></table>")

        if ui.accordion_step("P1_A", "(A) ¿Por qué Poisson?"):
            ui.content(
                "Cada día, cada soldado de un cuerpo tiene una probabilidad diminuta de recibir una coz mortal, "
                "y hay miles de soldados y cientos de días. ¿Qué modelo sale de contar éxitos en tantos ensayos "
                "tan improbables? ¿Qué propiedad de la media y la varianza deberían reflejar los datos?"
            )
            ui.spoiler(
                "El número de muertes es binomial con n enorme y p diminuta, y por el límite que verás en el "
                "problema siguiente se comporta como una Poisson de parámetro &lambda; = np. Si el modelo es "
                "bueno, la media y la varianza de los datos deberían parecerse, porque en una Poisson "
                "&#120124;[X] = &#120141;(X) = &lambda;."
            )

        if ui.accordion_step("P1_B", "(B) Ajustar &lambda;"):
            ui.content(
                "Mueve &lambda; hasta que las barras naranjas (lo que predice la Poisson para 200 observaciones) "
                "se parezcan a las azules. ¿Qué valor eliges? Calcula la media de los datos."
            )
            ui.spoiler(
                "La media de los datos es 122/200 = 0.61 muertes por cuerpo y año, y es justamente el valor de "
                "&lambda; que mejor ajusta: igualar la media teórica a la observada es el método de los "
                "momentos, y en la Poisson coincide con el de máxima verosimilitud, que verás en estadística. "
                "Con &lambda; = 0.61 la Poisson predice unas 108.7, 66.3, 20.2, 4.1 y 0.6 observaciones."
            )

        if ui.accordion_step("P1_C", "(C) El índice de Fano"):
            ui.content(
                "Calcula la varianza de los datos y el cociente D = varianza/media. ¿Qué dice sobre el modelo? "
                "¿Qué significaría un D muy superior a 1?"
            )
            ui.spoiler(
                "La varianza muestral sale en torno a 0.61, casi igual que la media, y D &asymp; 1: los datos "
                "son compatibles con muertes independientes y raras. Un D claramente mayor que 1 indicaría "
                "agrupamiento, por ejemplo cuerpos con caballos especialmente peligrosos o años malos para "
                "todos, y una sola Poisson no bastaría."
            )

    with col_right:
        ui.right_panel()
        mean, var, total = table_stats(KICKS)
        ui.metrics([(f"Media = {mean:.3f}", "metric-a"), (f"Varianza = {var:.3f}", "metric-b"),
                    (f"D = {var / mean:.3f}", "metric-c")])
        ui.show(fit_chart(dark, KICKS, lam), key="fig_kicks")
        ks = np.arange(0, 5)
        observed = np.array([KICKS[k] for k in ks])
        expected = total * stats.poisson.pmf(ks, lam)
        ui.footer_bar(f"Con &lambda; = {lam:.2f}, la suma de diferencias absolutas entre observado y esperado es "
                      f"{np.abs(observed - expected).sum():.1f}. Busca el &lambda; que la hace mínima.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>media &lambda;</u> y el <u>número de ensayos n</u>")
        c1, c2 = st.columns(2)
        lam = c1.select_slider("Media λ", options=[0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0], value=v["lam"],
                               key=ui.wkey(PAGE, "lam"))
        n = c2.select_slider("Ensayos n", options=[5, 10, 20, 30, 50, 100, 200, 500, 1000], value=v["n"],
                             key=ui.wkey(PAGE, "n"))
        n = max(n, int(np.ceil(lam)) + 1)

        ui.planteamiento()
        ui.statement(
            "<b>Juicios y jurados (1837)</b><br><br>"
            "Siméon Denis Poisson (1781-1840) quería saber con qué probabilidad un jurado se equivoca al "
            "condenar, y en su libro sobre la probabilidad de los juicios obtuvo, casi de pasada, la "
            "distribución que lleva su nombre. Su idea: un número muy grande n de ensayos con una "
            f"probabilidad muy pequeña p de éxito, de modo que la media np = &lambda; = {v['lam']} se mantenga. "
            "¿En qué se convierte la binomial?"
        )

        if ui.accordion_step("P2_A", "(A) El paso al límite"):
            ui.content(
                "Escribe la función de probabilidad de la binomial con p = &lambda;/n y haz tender n a "
                "infinito con k fijo. ¿Qué límite conocido aparece?"
            )
            ui.spoiler(
                "<div class='formula-box'>( <sup>n</sup>&frasl;<sub>k</sub> ) (&lambda;/n)<sup>k</sup> "
                "(1 &minus; &lambda;/n)<sup>n&minus;k</sup> = <sup>&lambda;<sup>k</sup></sup>&frasl;<sub>k!</sub>"
                "&middot;<sup>n(n &minus; 1)&ctdot;(n &minus; k + 1)</sup>&frasl;<sub>n<sup>k</sup></sub>&middot;"
                "(1 &minus; &lambda;/n)<sup>n</sup>(1 &minus; &lambda;/n)<sup>&minus;k</sup> &rarr; e<sup>&minus;&lambda;</sup>"
                "<sup>&lambda;<sup>k</sup></sup>&frasl;<sub>k!</sub></div>"
                "El cociente central y el último factor tienden a 1, y (1 &minus; &lambda;/n)<sup>n</sup> tiende "
                "a e<sup>&minus;&lambda;</sup>, el mismo límite que el del interés compuesto."
            )

        if ui.accordion_step("P2_B", "(B) ¿Cuándo se puede usar?"):
            ui.content(
                "La distancia de la derecha mide cuánto difieren las dos distribuciones: la mayor diferencia "
                "posible entre las probabilidades que asignan a un mismo suceso. ¿Cómo disminuye al aumentar "
                "n? ¿Y si &lambda; es grande?"
            )
            ui.spoiler(
                "Disminuye aproximadamente como 1/n: una desigualdad de Lucien Le Cam la acota por "
                "np<sup>2</sup> = &lambda;<sup>2</sup>/n. La aproximación es buena cuando n es grande y p "
                "pequeña; con &lambda; grande hace falta un n mayor para que p = &lambda;/n sea pequeña."
            )

        if ui.accordion_step("P2_C", "(C) Media y varianza"):
            ui.content(
                "Calcula la media y la varianza de la Poisson pasando al límite en las de la binomial. ¿Por qué "
                "el índice de Fano de la binomial, 1 &minus; p, tiende a 1?"
            )
            ui.spoiler(
                "La binomial tiene media np = &lambda; y varianza np(1 &minus; p) = &lambda;(1 &minus; &lambda;/n), "
                "que tiende a &lambda;. Su índice de Fano 1 &minus; p tiende a 1 porque, cuando p es pequeña, "
                "el tope de n éxitos deja de notarse: la Poisson es la frontera entre lo regular y lo agrupado."
            )

    with col_right:
        ui.right_panel()
        tv = tv_distance(n, lam)
        ui.metrics([(f"Distancia = {tv:.4f}", "metric-a"), (f"Cota de Le Cam = {min(1.0, lam ** 2 / n):.4f}", "metric-c")])
        ui.show(limit_chart(dark, n, lam), key="fig_limit")
        ui.footer_bar(f"Con n = {n} ensayos y p = {lam / n:.4f}, la binomial y la Poisson de media {lam} asignan "
                      f"probabilidades que difieren como mucho en {tv:.4f} a cualquier suceso.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>Las bombas sobre Londres (1946)</b><br><br>"
            "En 1944 cayeron sobre Londres miles de bombas volantes V-1. Los londinenses estaban convencidos "
            "de que apuntaban: había barrios castigados una y otra vez y otros intactos. Al acabar la guerra, "
            "el actuario R. D. Clarke dividió una zona del sur de la ciudad en 576 cuadrículas de un cuarto "
            "de kilómetro cuadrado y contó los impactos en cada una: 537 en total. ¿Apuntaban o caían al azar?"
        )
        ui.content("<table><tr><th>impactos</th><th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>7</th></tr>"
                   "<tr><td>cuadrículas</td>" + "".join(f"<td>{c}</td>" for c in BOMBS.values()) + "</tr></table>")

        if ui.accordion_step("P3_A", "(A) Si cayeran al azar"):
            ui.content(
                "Supón que cada bomba cae en una cuadrícula elegida al azar, independientemente de las demás. "
                "¿Qué distribución tiene el número de impactos en una cuadrícula concreta? ¿Con qué parámetro?"
            )
            ui.spoiler(
                "Cada una de las 537 bombas cae en la cuadrícula con probabilidad 1/576: el número de impactos "
                "es binomial B(537, 1/576), prácticamente una Poisson de parámetro &lambda; = 537/576 &asymp; "
                "0.93. Multiplicando por 576 se obtiene cuántas cuadrículas deberían tener 0, 1, 2&hellip; "
                "impactos."
            )

        if ui.accordion_step("P3_B", "(B) El índice de Fano"):
            ui.content(
                "Compara a la derecha los datos de Clarke con la Poisson y calcula D. Después genera mapas "
                "simulados: bombas al azar, apuntando a unos pocos objetivos o repartidas a propósito. ¿Qué "
                "valor de D da cada patrón?"
            )
            ui.spoiler(
                "Los datos de Clarke dan D muy cerca de 1 y un ajuste a la Poisson excelente: no hay rastro de "
                "puntería. Las bombas que apuntan a objetivos concentran impactos y vacían otras zonas, y dan "
                "D &gt; 1 (super-Poisson); las repartidas a propósito dan D &lt; 1 (sub-Poisson)."
            )

        if ui.accordion_step("P3_C", "(C) Por qué parecía que apuntaban"):
            ui.content(
                "Mira un mapa simulado con bombas al azar. ¿Ves barrios castigados y zonas intactas? ¿Por qué "
                "el azar puro produce racimos?"
            )
            ui.spoiler(
                "Con una media de casi un impacto por cuadrícula, la Poisson predice que en torno al 40 % de las "
                "cuadrículas quedan intactas y que alguna recibe cuatro o más. El azar no reparte de forma "
                "uniforme: produce huecos y racimos, y la mente los interpreta como intención. Para afirmar que "
                "hay agrupamiento hay que compararlo con lo que daría el azar, y el índice de Fano es la forma "
                "más sencilla de hacerlo."
            )

    with col_right:
        ui.right_panel()
        mean, var, total = table_stats(BOMBS)
        ui.metrics([(f"&lambda; = {mean:.3f}", "metric-a"), (f"D (Clarke) = {var / mean:.3f}", "metric-c")])
        ui.show(fit_chart(dark, BOMBS, mean), key="fig_clarke")
        current = st.session_state["pattern"] or v["pattern"]
        st.session_state["pattern"] = current
        ui.choice_buttons(list(PATTERNS), "pattern", labels=PATTERNS, per_row=3)
        if st.button("Otro mapa", key="bombs_new", width="stretch"):
            st.session_state["bomb_round"] += 1
        counts = drop_bombs(st.session_state["pattern"], v["seed"] + st.session_state["bomb_round"])
        flat = counts.ravel()
        d_sim = flat.var(ddof=1) / flat.mean()
        ui.show(map_chart(dark, counts), key="fig_map")
        ui.footer_bar(f"Mapa simulado ({PATTERNS[st.session_state['pattern']].lower()}): {(flat == 0).sum()} "
                      f"cuadrículas intactas y un máximo de {flat.max()} impactos; índice de Fano D = {d_sim:.2f}.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Las coces de los caballos", "P1_A"),
        ("P2", "(II) Juicios y jurados", "P2_A"),
        ("P3", "(III) Las bombas sobre Londres", "P3_A"),
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
