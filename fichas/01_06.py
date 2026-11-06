#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 6: el álgebra de los sucesos.

Las leyes del pensamiento de Boole (lógica y conjuntos, De Morgan), los
sucesos que puede decidir un jugador al que solo se le responden ciertas
preguntas (σ-álgebra generada, al estilo de Borel) y la diagonal de Cantor
(conjunto potencia, numerable frente a continuo).
"""

from __future__ import annotations

from itertools import combinations
from math import comb

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "El álgebra de los sucesos"
SYMBOL = "A∩Bᶜ"
PAGE = "01_06"

# =============================================================================
# 1. DATOS
# =============================================================================

EXPRESSIONS = {
    "A ∪ B": lambda a, b, c: a | b,
    "A ∩ B": lambda a, b, c: a & b,
    "Aᶜ": lambda a, b, c: ~a,
    "(A ∪ B)ᶜ": lambda a, b, c: ~(a | b),
    "Aᶜ ∩ Bᶜ": lambda a, b, c: ~a & ~b,
    "(A ∩ B)ᶜ": lambda a, b, c: ~(a & b),
    "Aᶜ ∪ Bᶜ": lambda a, b, c: ~a | ~b,
    "A \\ B": lambda a, b, c: a & ~b,
    "A ∩ Bᶜ": lambda a, b, c: a & ~b,
    "Aᶜ ∪ B": lambda a, b, c: ~a | b,
    "A Δ B": lambda a, b, c: a ^ b,
    "A ∩ (B ∪ C)": lambda a, b, c: a & (b | c),
    "(A ∩ B) ∪ (A ∩ C)": lambda a, b, c: (a & b) | (a & c),
    "A ∪ (B ∩ C)": lambda a, b, c: a | (b & c),
    "(A ∪ B) ∩ (A ∪ C)": lambda a, b, c: (a | b) & (a | c),
    "(A ∪ B ∪ C)ᶜ": lambda a, b, c: ~(a | b | c),
    "Aᶜ ∩ Bᶜ ∩ Cᶜ": lambda a, b, c: ~a & ~b & ~c,
    "A ∩ Aᶜ": lambda a, b, c: a & ~a,
    "A ∪ Aᶜ": lambda a, b, c: a | ~a,
}
EXPR_NAMES = list(EXPRESSIONS)
EXPR_PAIRS = [("(A ∪ B)ᶜ", "Aᶜ ∩ Bᶜ"), ("(A ∩ B)ᶜ", "Aᶜ ∪ Bᶜ"), ("A ∩ (B ∪ C)", "(A ∩ B) ∪ (A ∩ C)"),
              ("A ∪ (B ∩ C)", "(A ∪ B) ∩ (A ∪ C)"), ("A \\ B", "A ∩ Bᶜ"), ("(A ∪ B)ᶜ", "Aᶜ ∪ Bᶜ")]

GENERATORS = {
    "P": ("es par", {2, 4, 6}),
    "G": ("es mayor que 3", {4, 5, 6}),
    "T": ("es múltiplo de 3", {3, 6}),
    "R": ("es primo", {2, 3, 5}),
    "S": ("es un seis", {6}),
    "U": ("es un uno", {1}),
}
GEN_SETS = [("P", "G"), ("P", "T"), ("G", "R"), ("T", "U"), ("P",), ("R", "S")]
ATOM_COLOURS = [ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE, ui.PURPLE_LINE, ui.RED_LINE, "#00838f"]
PIPS = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)],
        4: [(0, 0), (2, 0), (0, 2), (2, 2)], 5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
        6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}

DIAG = 8


def initial_values():
    left, right = ui.dchoice(EXPR_PAIRS[0], EXPR_PAIRS, "pair")
    return {
        "left": left,
        "right": right,
        "gens": ui.dchoice(("P", "G"), GEN_SETS, "gens"),
        "test": ui.dchoice([1, 2], [[1, 2], [4, 5, 6], [2, 4, 6], [3], [1, 3, 5], [5, 6]], "test"),
        "n_set": ui.dint(3, 3, 5, "n_set"),
        "seed": int(ui.r("diag") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "diag_round": 0})


# =============================================================================
# 2. CÁLCULOS
# =============================================================================

def truth_rows():
    a = np.array([bool(i & 4) for i in range(7, -1, -1)])
    b = np.array([bool(i & 2) for i in range(7, -1, -1)])
    c = np.array([bool(i & 1) for i in range(7, -1, -1)])
    return a, b, c


def atoms_of(selected):
    groups = {}
    for face in range(1, 7):
        signature = tuple(face in GENERATORS[g][1] for g in selected)
        groups.setdefault(signature, []).append(face)
    return list(groups.values())


def is_measurable(event, atoms) -> bool:
    return all(set(atom) <= event or not (set(atom) & event) for atom in atoms)


def subset_label(faces) -> str:
    return "&empty;" if not faces else "{" + ", ".join(str(f) for f in sorted(faces)) + "}"


def diagonal_list(seed: int):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(DIAG, DIAG))


# =============================================================================
# 3. FIGURAS
# =============================================================================

def venn(dark, expr: str):
    width, height = 220, 190
    xs = np.linspace(-2.0, 2.0, width)
    ys = np.linspace(-1.75, 1.75, height)
    X, Y = np.meshgrid(xs, ys)
    a = (X + 0.55) ** 2 + (Y - 0.35) ** 2 < 1
    b = (X - 0.55) ** 2 + (Y - 0.35) ** 2 < 1
    c = X ** 2 + (Y + 0.55) ** 2 < 1
    mask = EXPRESSIONS[expr](a, b, c)
    img = np.zeros((height, width), dtype=np.uint32)
    view = img.view(dtype=np.uint8).reshape((height, width, 4))
    view[mask] = (155, 39, 67, 190)
    fg = "#e6e6e6" if dark else "#333333"
    p = ui.new_figure(dark, height=300, x_range=(-2.05, 2.05), y_range=(-1.8, 1.8), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    p.image_rgba(image=[img], x=-2.0, y=-1.75, dw=4.0, dh=3.5)
    p.quad(left=-2.0, right=2.0, bottom=-1.75, top=1.75, fill_alpha=0, line_color=fg, line_width=2)
    p.circle(x=[-0.55, 0.55, 0.0], y=[0.35, 0.35, -0.55], radius=1.0, fill_alpha=0,
             line_color=fg, line_width=2)
    p.text(x=[-1.45, 1.45, 1.05, -1.85], y=[1.25, 1.25, -1.45, 1.45], text=["A", "B", "C", "Ω"],
           text_color=fg, text_font_size="20px", text_align="center", text_baseline="middle")
    return p


def dice_row(dark, atoms) -> str:
    colour_of = {}
    for i, atom in enumerate(atoms):
        for face in atom:
            colour_of[face] = ATOM_COLOURS[i % len(ATOM_COLOURS)]
    pip = "#ffffff"
    parts = []
    for face in range(1, 7):
        x0 = 8 + (face - 1) * 72
        dots = "".join(
            f'<circle cx="{x0 + 14 + gx * 18}" cy="{22 + gy * 18}" r="5.5" fill="{pip}"/>'
            for gx, gy in PIPS[face])
        parts.append(f'<rect x="{x0}" y="8" width="64" height="64" rx="12" fill="{colour_of[face]}"/>'
                     f'{dots}')
    return f'<svg viewBox="0 0 440 80" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def binomial_row(dark, n: int):
    ks = list(range(n + 1))
    counts = [comb(n, k) for k in ks]
    p = ui.new_figure(dark, height=240, x_axis_label="tamaño del subconjunto i",
                      y_axis_label="nº de subconjuntos C(n, i)", x_range=(-0.6, n + 0.6))
    p.vbar(x=ks, top=counts, width=0.8, color=ui.BLUE_LINE, alpha=0.85)
    p.xaxis.ticker = ks
    p.xgrid.grid_line_color = None
    return p


# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es, exactamente, un suceso?</b>")
        ui.content(
            "Hasta ahora hemos tratado los sucesos como subconjuntos del espacio muestral &Omega; y los "
            "hemos combinado con uniones, intersecciones y complementarios. Esa costumbre tiene detrás "
            "una idea de George Boole: el cálculo con conjuntos y el razonamiento lógico son la misma "
            "álgebra con distinto vestido. <i>Llueve y no hace frío</i> es una conjunción con una "
            "negación, y también es la intersección de un suceso con el complementario de otro."
        )
        ui.content(
            "Cuando &Omega; es finito no hay más que pensar: cualquier subconjunto es un suceso y se le "
            "puede asignar una probabilidad. Pero cuando &Omega; es infinito, y sobre todo cuando es tan "
            "grande como la recta real, aparecen conjuntos tan extraños que no admiten ninguna medida "
            "razonable. Por eso Kolmogórov no habla de <i>todos</i> los subconjuntos, sino de una familia "
            "&Ascr; de sucesos de interés, y define el espacio de probabilidad como la terna "
            "(&Omega;, &Ascr;, &#8473;)."
        )
        ui.content(
            "Esa familia no puede ser cualquiera: si sé decidir si ha ocurrido A, también sé decidir si "
            "no ha ocurrido; y si sé decidir cada A<sub>i</sub>, sé decidir si ha ocurrido alguno. "
            "<i>Prueba a escribir las tres condiciones que debe cumplir &Ascr; para ser una "
            "&sigma;-álgebra.</i>"
        )
        ui.formula_hidden(
            "&empty; &isin; &Ascr; &nbsp;;&nbsp; A &isin; &Ascr; &rArr; A<sup>c</sup> &isin; &Ascr; "
            "&nbsp;;&nbsp; A<sub>1</sub>, A<sub>2</sub>, &hellip; &isin; &Ascr; &rArr; "
            "&#8899;<sub>i=1</sub><sup>&infin;</sup> A<sub>i</sub> &isin; &Ascr;",
            hint="Pulsa para revelar la definición de σ-álgebra",
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Las leyes del pensamiento (1854)</b><br>"
            "<i>Traduce con George Boole frases a conjuntos y comprueba las leyes de De Morgan sin "
            "escribir una sola demostración.</i><br><br>"
            "<b>II. Los sucesos de Borel (1898)</b><br>"
            "<i>Un crupier solo responde a ciertas preguntas sobre un dado. Descubre con Émile Borel "
            "qué sucesos puedes decidir y cuáles no.</i><br><br>"
            "<b>III. La diagonal de Cantor (1891)</b><br>"
            "<i>Cuenta subconjuntos con Georg Cantor hasta descubrir que hay infinitos más grandes que "
            "otros.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige <u>dos expresiones</u> y compara sus regiones")
        c1, c2 = st.columns(2)
        left = c1.selectbox("Expresión 1", EXPR_NAMES, index=EXPR_NAMES.index(v["left"]),
                            key=ui.wkey(PAGE, "left"))
        right = c2.selectbox("Expresión 2", EXPR_NAMES, index=EXPR_NAMES.index(v["right"]),
                             key=ui.wkey(PAGE, "right"))

        ui.planteamiento()
        ui.statement(
            "<b>Las leyes del pensamiento (1854)</b><br><br>"
            "George Boole (1815-1864) fue maestro de escuela sin título universitario antes de ocupar la "
            "cátedra de matemáticas del Queen's College de Cork. Su libro más conocido lleva un título "
            "que hoy suena a programa de esta asignatura: <i>Una investigación sobre las leyes del "
            "pensamiento, en las que se fundan las teorías matemáticas de la lógica y las "
            "probabilidades</i>. En él trataba las proposiciones como si fueran números que se suman y "
            "se multiplican. Tomemos tres sucesos A, B y C; ¿cuándo dos expresiones distintas describen "
            "el mismo suceso?"
        )

        if ui.accordion_step("P1_A", "(A) Del lenguaje a los conjuntos"):
            ui.content(
                "Sea A = <i>llueve</i>, B = <i>hace frío</i> y C = <i>hay clase</i>. Escribe como "
                "conjuntos: <i>llueve y no hace frío</i>; <i>ni llueve ni hace frío</i>; <i>si llueve, "
                "hace frío</i>. ¿Qué símbolo de conjuntos corresponde a cada conectiva lógica?"
            )
            ui.spoiler(
                "A &cap; B<sup>c</sup>; &nbsp; A<sup>c</sup> &cap; B<sup>c</sup>; &nbsp; A<sup>c</sup> &cup; B."
                "<br><br>La correspondencia es un isomorfismo entre el álgebra de la lógica y la de los "
                "conjuntos: la negación &sim; es el complementario, la conjunción &and; la intersección, "
                "la disyunción &or; la unión, la implicación la inclusión, la tautología &#8868; el "
                "suceso seguro &Omega; y la contradicción &#8869; el suceso imposible &empty;."
            )

        if ui.accordion_step("P1_B", "(B) Las leyes de De Morgan"):
            ui.content(
                "Elige arriba (A &cup; B)<sup>c</sup> y A<sup>c</sup> &cap; B<sup>c</sup>, y después "
                "(A &cap; B)<sup>c</sup> frente a A<sup>c</sup> &cup; B<sup>c</sup>. ¿Coinciden las "
                "regiones? ¿Y las columnas de la tabla de verdad? ¿Por qué comparar tablas de ocho filas "
                "es una demostración completa?"
            )
            ui.spoiler(
                "Son las leyes de De Morgan:"
                "<div class='formula-box'>(A &cup; B)<sup>c</sup> = A<sup>c</sup> &cap; B<sup>c</sup> "
                "&nbsp;&nbsp; (A &cap; B)<sup>c</sup> = A<sup>c</sup> &cup; B<sup>c</sup></div>"
                "Cada fila de la tabla es una de las ocho regiones en que A, B y C parten &Omega;; dos "
                "expresiones construidas con uniones, intersecciones y complementarios son iguales si y "
                "solo si contienen las mismas regiones. Prueba también las dos propiedades distributivas."
            )

        if ui.accordion_step("P1_C", "(C) Implicación e inclusión"):
            ui.content(
                "Compara A<sup>c</sup> &cup; B con el suceso seguro. ¿Cuándo ocupa A<sup>c</sup> &cup; B "
                "todo &Omega;? ¿Qué ocurre con A &cap; A<sup>c</sup> y con A &cup; A<sup>c</sup>?"
            )
            ui.spoiler(
                "A<sup>c</sup> &cup; B es la traducción de <i>A implica B</i>, y es todo &Omega; "
                "exactamente cuando A &sub; B: la implicación es una tautología si y solo si hay "
                "inclusión. Por eso la monotonía de la probabilidad, A &sub; B &rArr; &#8473;(A) &le; "
                "&#8473;(B), es la versión probabilística de la implicación. Del mismo modo, "
                "A &cap; A<sup>c</sup> = &empty; es la contradicción A &and; &sim;A, y "
                "A &cup; A<sup>c</sup> = &Omega; es el tercio excluso."
            )

    with col_right:
        ui.right_panel()
        a, b, c = truth_rows()
        col_l = EXPRESSIONS[left](a, b, c)
        col_r = EXPRESSIONS[right](a, b, c)
        same = bool((col_l == col_r).all())
        ui.metric("Equivalentes: misma tabla, misma región" if same else "No son equivalentes",
                  "result-yes" if same else "result-no")
        ui.caption(f"Región de la expresión 1: {left}")
        ui.show(venn(dark, left), key="fig_venn")

        def vf(x):
            return "V" if x else "F"

        rows = "".join(
            f"<tr><td>{vf(a[i])}</td><td>{vf(b[i])}</td><td>{vf(c[i])}</td>"
            f"<td><b>{vf(col_l[i])}</b></td><td><b>{vf(col_r[i])}</b></td></tr>"
            for i in range(8))
        ui.content(
            "<table><tr><th>A</th><th>B</th><th>C</th>"
            f"<th>{left}</th><th>{right}</th></tr>{rows}</table>"
        )


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige las <u>preguntas que responde el crupier</u>")
        chosen = []
        cols = st.columns(3)
        for i, (key, (desc, faces)) in enumerate(GENERATORS.items()):
            if cols[i % 3].checkbox(f"¿{desc}?", value=key in v["gens"], key=ui.wkey(PAGE, f"gen_{key}")):
                chosen.append(key)

        ui.planteamiento()
        ui.statement(
            "<b>Los sucesos de Borel (1898)</b><br><br>"
            "Émile Borel (1871-1956) dio en sus lecciones sobre la teoría de funciones la receta para "
            "medir conjuntos de números reales: partir de los intervalos y permitir solo complementarios "
            "y uniones numerables. Los conjuntos que se obtienen así se llaman hoy borelianos, y son los "
            "sucesos con los que Kolmogórov construyó la probabilidad en la recta real. Veamos la idea en "
            "pequeño: un crupier lanza un dado tras una mampara y solo contesta sí o no a ciertas "
            "preguntas. ¿Sobre qué sucesos podrás apostar sabiendo después si has ganado?"
        )

        if ui.accordion_step("P2_A", "(A) Lo que se puede decidir"):
            ui.content(
                "Si el crupier responde a <i>¿es par?</i>, ¿puedes decidir también el suceso <i>es "
                "impar</i>? Y si responde a dos preguntas, ¿puedes decidir <i>una u otra</i>? Razona por "
                "qué la familia de sucesos decidibles cumple las condiciones de una &sigma;-álgebra."
            )
            ui.spoiler(
                "Saber si ha ocurrido A es saber si no ha ocurrido (complementario), y saber si ha "
                "ocurrido cada uno de varios sucesos es saber si ha ocurrido alguno (unión). El suceso "
                "imposible y el seguro se deciden sin preguntar nada. La menor &sigma;-álgebra que "
                "contiene las preguntas del crupier es la <b>&sigma;-álgebra generada</b> por ellas: la "
                "información de la que dispones."
            )

        if ui.accordion_step("P2_B", "(B) Los átomos"):
            ui.content(
                "Agrupa las caras del dado que el crupier no te deja distinguir: las que responden igual "
                "a todas las preguntas. Son los <b>átomos</b>, coloreados a la derecha. ¿Cuántos sucesos "
                "decidibles hay si hay k átomos? ¿Qué preguntas hacen falta para decidirlo todo?"
            )
            ui.spoiler(
                "Un suceso es decidible si y solo si es unión de átomos: con cada átomo dentro o fuera, "
                "la &sigma;-álgebra generada tiene 2<sup>k</sup> elementos. Cuando cada cara es un átomo "
                "se recupera el conjunto potencia &#8472;(&Omega;), con 2<sup>6</sup> = 64 sucesos; con "
                "una sola pregunta trivial solo quedan &empty; y &Omega;."
            )

        if ui.accordion_step("P2_C", "(C) Por qué no basta con todos los subconjuntos"):
            ui.content(
                "En un dado podemos tomar como sucesos todos los subconjuntos. ¿Por qué no hacer lo mismo "
                "cuando &Omega; = [0, 1] y queremos que la probabilidad de un intervalo sea su longitud?"
            )
            ui.spoiler(
                "Porque es imposible. Giuseppe Vitali construyó en 1905 un subconjunto de [0, 1] al que "
                "no se le puede asignar longitud sin contradecir la aditividad numerable y la invariancia "
                "por traslaciones; la paradoja de Banach-Tarski (1924) lleva la extrañeza al espacio "
                "tridimensional. La salida es renunciar a medir todo &#8472;(&#8477;) y quedarse con la "
                "&sigma;-álgebra de Borel, que contiene todos los conjuntos que aparecen en la práctica."
            )

    with col_right:
        ui.right_panel()
        atoms = atoms_of(chosen)
        k = len(atoms)
        ui.metrics([
            (f"Átomos: {k}", "metric-a"),
            (f"|&sigma;(preguntas)| = 2<sup>{k}</sup> = {2 ** k}", "metric-b"),
        ])
        ui.svg(dice_row(dark, atoms))
        ui.caption("Átomos: " + " · ".join(subset_label(atom) for atom in atoms))
        test = st.multiselect("Elige un suceso para apostar", [1, 2, 3, 4, 5, 6], default=v["test"],
                              key=ui.wkey(PAGE, "test"))
        event = set(test)
        ok = is_measurable(event, atoms)
        ui.check(ok, f"<b>{subset_label(event)}</b> " + (
            "es decidible: es unión de átomos." if ok else
            "no es decidible: parte algún átomo, y el crupier no te dejará saber si has ganado."))
        if 2 ** k <= 16:
            family = [set().union(*combo) if combo else set()
                      for r in range(k + 1) for combo in combinations([set(x) for x in atoms], r)]
            ui.footer_bar("&sigma;(preguntas) = { " + ", ".join(subset_label(e) for e in family) + " }")
        else:
            ui.footer_bar(f"Con {k} átomos la &sigma;-álgebra tiene {2 ** k} sucesos: demasiados para "
                          "listarlos aquí.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.planteamiento()
        ui.statement(
            "<b>La diagonal de Cantor (1891)</b><br><br>"
            "Georg Cantor (1845-1918) se atrevió a comparar tamaños de conjuntos infinitos, para "
            "escándalo de su antiguo profesor Leopold Kronecker. En 1874 probó que los números reales "
            "no pueden ponerse en lista, y en 1891 encontró el argumento de la diagonal, tan sencillo "
            "que cabe en una servilleta. David Hilbert diría después que nadie nos expulsaría del "
            "paraíso que Cantor había creado. ¿Cuántos subconjuntos tiene un conjunto, y qué ocurre "
            "cuando el conjunto es infinito?"
        )

        if ui.accordion_step("P3_A", "(A) Contar subconjuntos"):
            ui.content(
                "Un subconjunto de {1, &hellip;, n} queda determinado por una cadena de n ceros y unos "
                "(el elemento i está o no está). ¿Cuántos subconjuntos hay? Agrúpalos por tamaño y "
                "relaciona la cuenta con el binomio de Newton."
            )
            ui.spoiler(
                "Hay 2<sup>n</sup> cadenas, luego |&#8472;(&Omega;)| = 2<sup>n</sup>. Contando por "
                "tamaños, hay C(n, i) subconjuntos de i elementos, y evaluar el binomio de Newton en "
                "x = y = 1 da la misma cuenta:"
                "<div class='formula-box'>&sum;<sub>i=0</sub><sup>n</sup> ( <sup>n</sup>&frasl;<sub>i</sub> ) "
                "= (1 + 1)<sup>n</sup> = 2<sup>n</sup></div>"
            )

        if ui.accordion_step("P3_B", "(B) La diagonal"):
            ui.content(
                "Ahora los subconjuntos de &#8469; son sucesiones infinitas de ceros y unos. Supón que "
                "alguien asegura haberlos puesto todos en una lista s<sub>1</sub>, s<sub>2</sub>, "
                "&hellip; Construye una sucesión que no esté en la lista mirando solo la diagonal. ¿Qué "
                "dice eso del tamaño de &#8472;(&#8469;)?"
            )
            ui.spoiler(
                "Basta cambiar el i-ésimo dígito de s<sub>i</sub>: la sucesión d resultante difiere de "
                "cada s<sub>i</sub> al menos en la posición i, así que no está en la lista. Ninguna lista "
                "agota &#8472;(&#8469;): su cardinal 2<sup>&#8501;<sub>0</sub></sup> es estrictamente "
                "mayor que el numerable &#8501;<sub>0</sub>, y coincide con el de los números reales, el "
                "continuo &#120096;."
            )

        if ui.accordion_step("P3_C", "(C) La hipótesis del continuo"):
            ui.content(
                "¿Existe algún conjunto más grande que &#8469; y más pequeño que &#8477;? Cantor creyó "
                "que no, y pasó años intentando demostrarlo. ¿Qué tiene que ver esta pregunta con la "
                "probabilidad?"
            )
            ui.spoiler(
                "La hipótesis del continuo afirma que no hay cardinales intermedios, "
                "&#8501;<sub>1</sub> = 2<sup>&#8501;<sub>0</sub></sup>. Kurt Gödel probó en 1940 que no "
                "puede refutarse con los axiomas usuales de la teoría de conjuntos, y Paul Cohen en 1963 "
                "que tampoco puede demostrarse: es independiente. Para la probabilidad la frontera "
                "importante es otra: sobre un &Omega; numerable todo subconjunto puede ser suceso, "
                "mientras que sobre el continuo hace falta una &sigma;-álgebra más pequeña, como viste "
                "con Borel."
            )

    with col_right:
        ui.right_panel()
        if st.session_state["open_part"] == "P3_A":
            n = st.slider("Elementos de Ω", 1, 5, v["n_set"], 1, key=ui.wkey(PAGE, "n_set"))
            ui.metric(f"|&#8472;(&Omega;)| = 2<sup>{n}</sup> = {2 ** n}", "metric-a")
            chips = []
            for mask in range(2 ** n):
                members = [i + 1 for i in range(n) if mask >> (n - 1 - i) & 1]
                code = format(mask, f"0{n}b")
                chips.append(f"<span class='mono'>{code}</span> &rarr; {subset_label(members)}")
            ui.content("<br>".join(chips) if n <= 3 else " &nbsp;·&nbsp; ".join(chips))
            ui.show(binomial_row(dark, n), key="fig_powerset")
            return

        if st.button("Otra lista", key="diag_new", width="stretch"):
            st.session_state["diag_round"] += 1
        rows = diagonal_list(v["seed"] + st.session_state["diag_round"])
        diag = 1 - np.diag(rows)
        body = ""
        for i in range(DIAG):
            cells = "".join(
                f"<td style='background:{ui.UBU_YELLOW};color:{ui.UBU_DARK};font-weight:700'>{rows[i, j]}</td>"
                if i == j else f"<td>{rows[i, j]}</td>" for j in range(DIAG))
            body += f"<tr><th>s<sub>{i + 1}</sub></th>{cells}<td>&hellip;</td></tr>"
        d_cells = "".join(
            f"<td style='background:{ui.GREEN_LINE};color:#ffffff;font-weight:700'>{x}</td>" for x in diag)
        body += f"<tr><th>d</th>{d_cells}<td>&hellip;</td></tr>"
        ui.content(f"<table class='mono'>{body}</table>")
        ui.footer_bar(
            "La sucesión d se obtiene cambiando cada dígito amarillo. Difiere de s<sub>1</sub> en la "
            "posición 1, de s<sub>2</sub> en la 2, y así con todas: por mucho que se alargue la lista, d "
            "nunca está en ella."
        )


# =============================================================================
# 5. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Las leyes del pensamiento", "P1_A"),
        ("P2", "(II) Los sucesos de Borel", "P2_A"),
        ("P3", "(III) La diagonal de Cantor", "P3_A"),
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
