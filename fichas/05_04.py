#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 5, ficha 4: covarianza y matriz de covarianzas.

La cartera de Markowitz (varianza de una combinación lineal), la matriz de
Spearman (no toda tabla de correlaciones es posible) y la varianza de los
patos alcanzados (covarianzas negativas entre indicatrices).
"""

from __future__ import annotations

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "Covarianza"
SYMBOL = "Cov(X,Y)"
PAGE = "05_04"

SUBJECTS = ["Clásicas", "Francés", "Inglés"]


def initial_values():
    return {
        "rho": ui.dfloat(0.2, -0.6, 0.6, "rho", 1),
        "weight": ui.dfloat(0.5, 0.2, 0.8, "weight", 2),
        "r12": ui.dfloat(0.83, 0.5, 0.9, "r12", 2),
        "r13": ui.dfloat(0.78, 0.5, 0.9, "r13", 2),
        "r23": ui.dfloat(0.67, -0.6, 0.9, "r23", 2),
        "hunters": ui.dint(10, 5, 30, "hunters"),
        "ducks": ui.dint(10, 5, 30, "ducks"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "duck_var_sim": None})


ASSETS = {"X": (8.0, 20.0), "Y": (4.0, 10.0)}   # rentabilidad media y desviación, en % anual


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def portfolio(a, rho):
    (m1, s1), (m2, s2) = ASSETS["X"], ASSETS["Y"]
    a = np.asarray(a, dtype=float)
    mean = a * m1 + (1 - a) * m2
    var = a ** 2 * s1 ** 2 + (1 - a) ** 2 * s2 ** 2 + 2 * a * (1 - a) * rho * s1 * s2
    return mean, np.sqrt(np.maximum(var, 0))


def min_variance_weight(rho: float) -> float:
    (_, s1), (_, s2) = ASSETS["X"], ASSETS["Y"]
    den = s1 ** 2 + s2 ** 2 - 2 * rho * s1 * s2
    return float(np.clip((s2 ** 2 - rho * s1 * s2) / den, 0, 1)) if den > 0 else 0.0


def ducks_moments(n: int, m: int):
    survive = (1 - 1 / m) ** n
    h = 1 - survive
    both_hit = 1 - 2 * survive + (1 - 2 / m) ** n
    cov = both_hit - h ** 2
    var = m * h * (1 - h) + m * (m - 1) * cov
    return h, cov, var, m * h * (1 - h)


def hunt(n: int, m: int, trials: int, rng):
    shots = rng.integers(m, size=(trials, n))
    hit = np.zeros((trials, m), dtype=bool)
    hit[np.arange(trials)[:, None], shots] = True
    return hit.sum(axis=1)


# =============================================================================
# 2. FIGURAS
# =============================================================================

def frontier_chart(dark, rho: float, a: float):
    ws = np.linspace(0, 1, 201)
    p = ui.new_figure(dark, height=320, x_axis_label="riesgo: desviación típica (%)", y_axis_label="rentabilidad media (%)",
                      x_range=(0, 22), y_range=(3, 9))
    for r, colour, dash in ((-1.0, ui.GREEN_LINE, "dashed"), (1.0, ui.RED_LINE, "dashed")):
        m, s = portfolio(ws, r)
        p.line(s, m, line_width=2, color=colour, line_dash=dash, legend_label=f"ρ = {r:+.0f}")
    m, s = portfolio(ws, rho)
    p.line(s, m, line_width=4, color=ui.BLUE_LINE, legend_label=f"ρ = {rho:+.2f}")
    ma, sa = portfolio(a, rho)
    p.scatter([sa], [ma], size=16, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK, line_width=2)
    w = min_variance_weight(rho)
    mw, sw = portfolio(w, rho)
    p.scatter([sw], [mw], size=12, marker="diamond", color=ui.UBU_RED, legend_label="mínima varianza")
    return ui.style_legend(p, dark, "bottom_right")


def eigen_chart(dark, eig):
    labels = ["λ₁", "λ₂", "λ₃"]
    p = ui.new_figure(dark, height=240, x_range=labels, y_axis_label="autovalor", y_range=(min(-0.3, eig.min() - 0.1), 3))
    p.vbar(x=labels, top=eig, width=0.6, fill_color=[ui.GREEN_LINE if e >= -1e-9 else ui.RED_LINE for e in eig],
           line_color=None)
    p.xgrid.grid_line_color = None
    return p


def feasible_chart(dark, r12: float, r13: float, r23: float):
    g = np.linspace(-1, 1, 161)
    A, B = np.meshgrid(g, g)
    det = 1 - r12 ** 2 - A ** 2 - B ** 2 + 2 * r12 * A * B
    ok = det >= 0
    p = ui.new_figure(dark, height=300, x_axis_label="r(Clásicas, Inglés)", y_axis_label="r(Francés, Inglés)",
                      x_range=(-1, 1), y_range=(-1, 1), match_aspect=True)
    p.scatter(A[ok].ravel()[::3], B[ok].ravel()[::3], size=3, color=ui.GREEN_LINE, alpha=0.35)
    p.scatter([r13], [r23], size=16, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK, line_width=2)
    return p


def ducks_chart(dark, n: int, m: int, sample):
    ks = np.arange(0, m + 1)
    _, _, var, var_ind = ducks_moments(n, m)
    mean = m * (1 - (1 - 1 / m) ** n)
    from scipy import stats
    p = ui.new_figure(dark, height=300, x_axis_label="patos alcanzados", y_axis_label="probabilidad", x_range=(-0.6, m + 0.6))
    if sample is not None:
        freq = np.bincount(sample, minlength=m + 1)[: m + 1] / len(sample)
        p.vbar(x=ks, top=freq, width=0.8, color=ui.UBU_YELLOW, alpha=0.75, legend_label="simulación")
    xs = np.linspace(0, m, 300)
    p.line(xs, stats.norm.pdf(xs, mean, np.sqrt(var)), line_width=3, color=ui.BLUE_LINE,
           legend_label="campana con la varianza correcta")
    p.line(xs, stats.norm.pdf(xs, mean, np.sqrt(var_ind)), line_width=3, color=ui.RED_LINE, line_dash="dashed",
           legend_label="campana olvidando las covarianzas")
    return ui.style_legend(p, dark, "top_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo varían dos variables juntas?</b>")
        ui.content(
            "La varianza mide cómo se aleja una variable de su media; la <b>covarianza</b> mide si dos variables se "
            "alejan de sus medias en el mismo sentido. <i>Escribe su definición y la fórmula abreviada.</i>"
        )
        ui.formula_hidden("Cov(X, Y) = &#120124;[(X &minus; &#120124;X)(Y &minus; &#120124;Y)] = &#120124;[XY] &minus; &#120124;[X]&#120124;[Y]")
        ui.content(
            "Si X e Y son independientes, &#120124;[XY] = &#120124;[X]&#120124;[Y] y la covarianza es cero; el recíproco es "
            "falso, como mostraron las gotas de Ulam. Dividiendo por las desviaciones típicas se obtiene el "
            "coeficiente de correlación &rho;, entre &minus;1 y 1. Para un vector, las covarianzas forman la "
            "<b>matriz de covarianzas</b> &Sigma;, simétrica y con las varianzas en la diagonal. <i>¿Qué da la "
            "varianza de una combinación lineal?</i>"
        )
        ui.formula_hidden("&#120141;(aX + bY) = a<sup>2</sup>&#120141;(X) + b<sup>2</sup>&#120141;(Y) + 2ab&middot;Cov(X, Y)")

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. La cartera de Markowitz (1952)</b><br>"
            "<i>Reparte cien tharni entre dos inversiones con Harry Markowitz y descubre por qué diversificar "
            "reduce el riesgo.</i><br><br>"
            "<b>II. La matriz de Spearman (1904)</b><br>"
            "<i>Las notas de tres asignaturas, sus correlaciones y una tabla que ningún colegio podría "
            "producir.</i><br><br>"
            "<b>III. Los patos, otra vez</b><br>"
            "<i>La varianza que quedó pendiente: cuánto fluctúa el número de patos alcanzados.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia la <u>correlación &rho;</u> y la <u>fracción invertida en X</u>")
        c1, c2 = st.columns(2)
        rho = c1.slider("Correlación ρ entre X e Y", -1.0, 1.0, v["rho"], 0.05, key=ui.wkey(PAGE, "rho"))
        a = c2.slider("Fracción invertida en X", 0.0, 1.0, v["weight"], 0.01, key=ui.wkey(PAGE, "weight"))

        ui.planteamiento()
        ui.statement(
            "<b>La cartera de Markowitz (1952)</b><br><br>"
            "Harry Markowitz, todavía estudiante de doctorado, publicó un artículo breve que le valió "
            "el Nobel de Economía de 1990. Su idea: un inversor no debe mirar solo la rentabilidad media, sino "
            "también el riesgo, medido por la desviación típica, y el riesgo de una cartera depende de las "
            "covarianzas. Tienes cien tharni para repartir entre X, una inversión arriesgada (rentabilidad media "
            "8 %, desviación 20 %), e Y, una prudente (4 % y 10 %)."
        )

        if ui.accordion_step("P1_A", "(A) La varianza de la cartera"):
            ui.content(
                "Si inviertes una fracción a en X y el resto en Y, la rentabilidad es aX + (1 &minus; a)Y. Calcula su "
                "media y su varianza. ¿Qué papel juega &rho;?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120124; = 8a + 4(1 &minus; a) &nbsp;&nbsp; &#120141; = 400a<sup>2</sup> + 100(1 &minus; a)<sup>2</sup> + "
                "2a(1 &minus; a)&middot;&rho;&middot;20&middot;10</div>"
                "La media es una media ponderada de las medias; la varianza, no: el término cruzado, "
                "proporcional a la covarianza &rho;&sigma;<sub>X</sub>&sigma;<sub>Y</sub>, puede sumar o restar riesgo."
            )

        if ui.accordion_step("P1_B", "(B) Diversificar"):
            ui.content(
                "Compara la curva azul con las rectas discontinuas de &rho; = &plusmn;1. ¿Cuándo es el riesgo de la cartera "
                "menor que la media ponderada de los riesgos? ¿Y con &rho; = &minus;1?"
            )
            ui.spoiler(
                "Con &rho; = 1 la desviación de la cartera es exactamente la media ponderada de las desviaciones: no hay "
                "ganancia. Con &rho; &lt; 1 la curva se dobla hacia la izquierda: mismo rendimiento medio con menos "
                "riesgo. Con &rho; = &minus;1 los dos activos se compensan perfectamente y existe una cartera sin riesgo "
                "alguno. Diversificar funciona porque las inversiones no suben y bajan a la vez."
            )

        if ui.accordion_step("P1_C", "(C) La cartera de mínima varianza"):
            ui.content(
                "Deriva la varianza respecto de a e iguala a cero. ¿Qué fracción minimiza el riesgo? Compruébalo con el "
                "rombo rojo."
            )
            ui.spoiler(
                "<div class='formula-box'>a* = <sup>&sigma;<sub>Y</sub><sup>2</sup> &minus; &rho;&sigma;<sub>X</sub>&sigma;<sub>Y</sub></sup>&frasl;"
                "<sub>&sigma;<sub>X</sub><sup>2</sup> + &sigma;<sub>Y</sub><sup>2</sup> &minus; 2&rho;&sigma;<sub>X</sub>&sigma;<sub>Y</sub></sub></div>"
                "La inversión arriesgada entra en la cartera de mínimo riesgo siempre que &rho; &lt; "
                "&sigma;<sub>Y</sub>/&sigma;<sub>X</sub>, aquí 0.5: no hace falta que las dos sean independientes. Por encima de ese punto, la curva es la frontera eficiente: no hay "
                "forma de ganar más de media sin aceptar más riesgo."
            )

    with col_right:
        ui.right_panel()
        mean, sd = portfolio(a, rho)
        w = min_variance_weight(rho)
        _, sw = portfolio(w, rho)
        ui.metrics([(f"Media: {float(mean):.2f} %", "metric-a"), (f"Riesgo: {float(sd):.2f} %", "metric-c")])
        ui.show(frontier_chart(dark, rho, a), key="fig_markowitz")
        ui.footer_bar(f"Con {a * 100:.0f} tharni en X y {100 - a * 100:.0f} en Y. La cartera de mínimo riesgo invierte "
                      f"{w * 100:.0f} tharni en X, con una desviación de {float(sw):.2f} %.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia las <u>tres correlaciones</u>")
        r12 = st.slider("r(Clásicas, Francés)", -1.0, 1.0, v["r12"], 0.01, key=ui.wkey(PAGE, "r12"))
        r13 = st.slider("r(Clásicas, Inglés)", -1.0, 1.0, v["r13"], 0.01, key=ui.wkey(PAGE, "r13"))
        r23 = st.slider("r(Francés, Inglés)", -1.0, 1.0, v["r23"], 0.01, key=ui.wkey(PAGE, "r23"))

        ui.planteamiento()
        ui.statement(
            "<b>La matriz de Spearman (1904)</b><br><br>"
            "Charles Spearman, oficial del ejército británico reconvertido en psicólogo, recogió las notas de los "
            "alumnos de una escuela en varias asignaturas y calculó sus correlaciones. Todas eran positivas, y "
            "seguían un patrón tan ordenado que propuso una única capacidad general detrás de todas, el factor g. "
            "Antes de interpretar una tabla de correlaciones conviene saber si puede existir: ¿vale cualquier "
            "elección de tres números entre &minus;1 y 1?"
        )

        if ui.accordion_step("P2_A", "(A) La matriz no puede ser cualquiera"):
            ui.content(
                "Sea &Sigma; la matriz de covarianzas de (X<sub>1</sub>, X<sub>2</sub>, X<sub>3</sub>) y &tau; un vector de "
                "números. Calcula la varianza de &tau;<sub>1</sub>X<sub>1</sub> + &tau;<sub>2</sub>X<sub>2</sub> + "
                "&tau;<sub>3</sub>X<sub>3</sub>. ¿Qué condición impone eso a &Sigma;?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120141;(&sum; &tau;<sub>i</sub>X<sub>i</sub>) = &sum;<sub>i</sub>&sum;<sub>j</sub> "
                "&tau;<sub>i</sub>&tau;<sub>j</sub>Cov(X<sub>i</sub>, X<sub>j</sub>) = &tau;&Sigma;&tau;<sup>t</sup> &ge; 0</div>"
                "Una varianza nunca es negativa, así que &Sigma; debe ser <b>semidefinida positiva</b>: todos sus "
                "autovalores mayores o iguales que cero. Lo mismo vale para la matriz de correlaciones."
            )

        if ui.accordion_step("P2_B", "(B) Una tabla imposible"):
            ui.content(
                "Pon r(Clásicas, Francés) = 0.9, r(Clásicas, Inglés) = 0.9 y r(Francés, Inglés) = &minus;0.9. ¿Qué dicen "
                "los autovalores? ¿Por qué es intuitivamente absurdo?"
            )
            ui.spoiler(
                "Aparece un autovalor negativo: ninguna población de alumnos puede tener esas correlaciones. Si las "
                "Clásicas van muy de la mano del Francés y del Inglés, el Francés y el Inglés no pueden ir en "
                "direcciones opuestas. Para tres variables la condición es"
                "<div class='formula-box'>1 &minus; r<sub>12</sub><sup>2</sup> &minus; r<sub>13</sub><sup>2</sup> &minus; r<sub>23</sub><sup>2</sup> + "
                "2r<sub>12</sub>r<sub>13</sub>r<sub>23</sub> &ge; 0</div>"
                "La región verde de la derecha es el conjunto de valores posibles de las otras dos correlaciones una "
                "vez fijada la primera."
            )

        if ui.accordion_step("P2_C", "(C) El factor g"):
            ui.content(
                "Supón que cada nota es X<sub>i</sub> = &lambda;<sub>i</sub>G + E<sub>i</sub>, con un factor común G y "
                "errores propios independientes, todo tipificado. ¿Cuánto vale r<sub>ij</sub>? ¿Qué patrón predice "
                "en la tabla?"
            )
            ui.spoiler(
                "Por la bilinealidad de la covarianza, r<sub>ij</sub> = &lambda;<sub>i</sub>&lambda;<sub>j</sub> para i &ne; j: cada "
                "correlación es el producto de las cargas de las dos asignaturas. Una matriz así es siempre "
                "semidefinida positiva, porque viene de variables que existen. Spearman comprobó que sus tablas casi "
                "cumplían ese patrón, y de ahí nació el análisis factorial."
            )

    with col_right:
        ui.right_panel()
        R = np.array([[1, r12, r13], [r12, 1, r23], [r13, r23, 1]])
        eig = np.sort(np.linalg.eigvalsh(R))[::-1]
        det = float(np.linalg.det(R))
        ok = eig.min() >= -1e-9
        ui.metric("La tabla es posible" if ok else "Ninguna población tiene estas correlaciones",
                  "result-yes" if ok else "result-no")
        ui.show(eigen_chart(dark, eig), key="fig_eigen")
        ui.show(feasible_chart(dark, r12, r13, r23), key="fig_feasible")
        ui.footer_bar(f"Autovalores {eig[0]:.3f}, {eig[1]:.3f}, {eig[2]:.3f}; determinante {det:.3f}. Abajo, en verde, "
                      "los pares posibles para las dos últimas correlaciones con la primera fijada; el punto es tu elección.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>cazadores n</u> y los <u>patos m</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Cazadores n", 1, 60, v["hunters"], 1, key=ui.wkey(PAGE, "hunters"))
        m = c2.slider("Patos m", 2, 60, v["ducks"], 1, key=ui.wkey(PAGE, "ducks"))

        ui.planteamiento()
        ui.statement(
            "<b>Los patos, otra vez</b><br><br>"
            "En la ficha de esperanza condicionada calculamos cuántos patos alcanzan de media n cazadores que eligen "
            "al azar entre m patos: m[1 &minus; (1 &minus; 1/m)<sup>n</sup>], sumando indicatrices. Quedó pendiente la "
            "varianza, porque las indicatrices no son independientes. Ahora tenemos la herramienta: la varianza de "
            "una suma con covarianzas."
        )

        if ui.accordion_step("P3_A", "(A) Varianzas y covarianzas de las indicatrices"):
            ui.content(
                "Sea I<sub>j</sub> la indicatriz de que el pato j es alcanzado, con probabilidad h. ¿Cuánto vale su "
                "varianza? Para dos patos distintos, calcula la probabilidad de que los dos sean alcanzados con la "
                "fórmula de inclusión-exclusión, y de ahí su covarianza."
            )
            ui.spoiler(
                "&#120141;(I<sub>j</sub>) = h(1 &minus; h), como cualquier Bernoulli. Los dos se salvan con probabilidad "
                "(1 &minus; 2/m)<sup>n</sup>, así que"
                "<div class='formula-box'>&#8473;(ambos alcanzados) = 1 &minus; 2(1 &minus; 1/m)<sup>n</sup> + (1 &minus; 2/m)<sup>n</sup></div>"
                "y Cov(I<sub>j</sub>, I<sub>k</sub>) = &#8473;(ambos) &minus; h<sup>2</sup>, que resulta negativa: si un pato "
                "atrae disparos, quedan menos para los demás."
            )

        if ui.accordion_step("P3_B", "(B) La varianza de la suma"):
            ui.content("Escribe la varianza del número de patos alcanzados con las varianzas y las covarianzas.")
            ui.spoiler(
                "<div class='formula-box'>&#120141;(&sum; I<sub>j</sub>) = m&middot;h(1 &minus; h) + m(m &minus; 1)&middot;Cov(I<sub>1</sub>, I<sub>2</sub>)</div>"
                "Hay m términos diagonales y m(m &minus; 1) cruzados en la matriz de covarianzas. Todos los cruzados "
                "son iguales por simetría."
            )

        if ui.accordion_step("P3_C", "(C) Olvidar las covarianzas"):
            ui.content(
                "Compara la varianza correcta con la que saldría tratando las indicatrices como independientes. "
                "Simula cacerías para ver cuál acierta."
            )
            ui.spoiler(
                "Con covarianzas negativas, la varianza real es bastante menor que la que supone independencia: el "
                "número de patos alcanzados es más estable de lo que parece, porque los disparos repetidos sobre un "
                "pato se compensan con patos libres. La campana azul se ajusta a la simulación; la roja, no. La "
                "linealidad de la esperanza perdona la dependencia; la varianza, no."
            )

        if st.button("Simular 10 000 cacerías", key="duck_var_play", width="stretch", type="primary"):
            st.session_state["duck_var_sim"] = (n, m, hunt(n, m, 10000, np.random.default_rng()))

    with col_right:
        ui.right_panel()
        h, cov, var, var_ind = ducks_moments(n, m)
        sim = st.session_state.get("duck_var_sim")
        sample = sim[2] if sim and sim[:2] == (n, m) else None
        items = [(f"&#120141; correcta = {var:.3f}", "metric-a"), (f"Sin covarianzas: {var_ind:.3f}", "result-no")]
        if sample is not None:
            items.append((f"Simulada: {sample.var():.3f}", "metric-c"))
        ui.metrics(items)
        ui.show(ducks_chart(dark, n, m, sample), key="fig_duck_var")
        ui.footer_bar(f"Cov(I<sub>1</sub>, I<sub>2</sub>) = {cov:+.5f}. Con {m} patos hay {m * (m - 1)} covarianzas cruzadas, "
                      "y entre todas restan mucha varianza.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) La cartera de Markowitz", "P1_A"),
        ("P2", "(II) La matriz de Spearman", "P2_A"),
        ("P3", "(III) Los patos, otra vez", "P3_A"),
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
