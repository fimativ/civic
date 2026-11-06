#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 2: los axiomas de Kolmogórov.

Sucesos sobre tres lanzamientos de una moneda (Venn), candidatos a medida de
probabilidad (el impostor) y la desigualdad de Bonferroni por etapas.
"""

from __future__ import annotations

import streamlit as st
from bokeh.plotting import figure

import civic_ui as ui

TITLE = "Los axiomas de Kolmogórov"
SYMBOL = "P(Ω)=1"
PAGE = "01_02"

# =============================================================================
# 1. DATOS
# =============================================================================

# Espacio muestral: tres lanzamientos de una moneda (C = cara, X = cruz)
OMEGA = ["CCC", "CCX", "CXC", "XCC", "CXX", "XCX", "XXC", "XXX"]

EVENTS = {
    "E":    ("E", "hay exactamente dos cruces", ["CXX", "XCX", "XXC"]),
    "F":    ("F", "hay al menos dos cruces", ["CXX", "XCX", "XXC", "XXX"]),
    "G":    ("G", "no aparece cruz antes que la primera cara", ["CCC", "CCX", "CXC", "CXX"]),
    "H":    ("H", "el primer lanzamiento es cruz", ["XCC", "XCX", "XXC", "XXX"]),
    "Ec":   ("E<sup>c</sup>", "NO hay exactamente dos cruces",
             [x for x in OMEGA if x not in ["CXX", "XCX", "XXC"]]),
    "FmE":  ("F \\ E", "está en F pero no en E", ["XXX"]),
    "EuGH": ("E &cup; (G &cap; H)", "como G &cap; H = &empty;, el resultado es E", ["CXX", "XCX", "XXC"]),
    "EiHc": ("E &cap; H<sup>c</sup>", "está en E pero no en H", ["CXX"]),
}
PART_A_KEYS = ["E", "F", "G", "H"]
PART_B_KEYS = ["Ec", "FmE", "EuGH", "EiHc"]
PART_B_LABELS = {"Ec": "Eᶜ", "FmE": "F\\E", "EuGH": "E∪(G∩H)", "EiHc": "E∩Hᶜ"}

CANDIDATOS = [
    {
        "label": "P(A) = 0 si A es finito, 1 si A es infinito",
        "ax": [True, True, False],
        "why": [
            "Solo toma los valores 0 y 1, ambos &ge; 0.",
            "&Omega; es infinito, luego P(&Omega;) = 1.",
            "Contraejemplo: &Omega; = &#8469; = &#8899; {n}, cada {n} finito con P = 0, "
            "pero P(&Omega;) = 1 &ne; &sum; 0 = 0.",
        ],
    },
    {
        "label": "P(A) = a si A &ne; &empty;, 0 si A = &empty; (con a constante)",
        "ax": [True, False, False],
        "why": [
            "Si a &ge; 0, P(A) &ge; 0.",
            "P(&Omega;) = a: no cumple salvo que a = 1.",
            "Si A y B son disjuntos y no vacíos: P(A&cup;B) = a, pero P(A)+P(B) = 2a &ne; a.",
        ],
    },
    {
        "label": "Probabilidad clásica o de Laplace: P(A) = |A| / |&Omega;|",
        "ax": [True, True, True],
        "why": [
            "|A| / |&Omega;| &ge; 0 siempre.",
            "P(&Omega;) = |&Omega;| / |&Omega;| = 1.",
            "Si A &cap; B = &empty;, entonces |A&cup;B| = |A| + |B|, luego P(A&cup;B) = P(A) + P(B).",
        ],
    },
]
AXIOM_NAMES = ["(I) No negatividad", "(II) Normalización", "(III) Aditividad"]

F_GOAL = ("&#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) &ge; "
          "1 &minus; &sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub><sup>c</sup>)")
F_DEMOR = ("(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>)<sup>c</sup> = "
           "&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>")
F_COMPL = ("&#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) = "
           "1 &minus; &#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>)")
F_BOOLE = ("&#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub><sup>c</sup>) &le; "
           "&sum;<sub>i=1</sub><sup>n</sup> &#8473;(A<sub>i</sub><sup>c</sup>)")


def initial_values():
    return {"p_cruz": ui.dfloat(0.50, 0.20, 0.80, "p_cruz")}


def init_session_state():
    ui.init_state({
        "page": "INTRO",
        "open_part": "P1_A",
        "sel_a": "E",
        "sel_b": "Ec",
        "sel_c": "XXX",
        "sel_cand": 0,
    })


# =============================================================================
# 2. DIAGRAMA EN ÁRBOL DEL ESPACIO MUESTRAL
# =============================================================================

def tree_diagram(highlighted, dark):
    hi = ui.GREEN_LINE
    if dark:
        fill_def, line_def, text_def, text_leaf, hi_fill = "#24242b", "#5a5a62", "#cfcfcf", "#9a9aa2", "#1f3d27"
    else:
        fill_def, line_def, text_def, text_leaf, hi_fill = "#ffffff", "#c2c2c2", "#555555", "#888888", "#dff0df"

    nodes = {
        "root": (0.0, 3.0),
        "C": (-3.0, 2.0), "X": (3.0, 2.0),
        "CC": (-4.5, 1.0), "CX": (-1.5, 1.0), "XC": (1.5, 1.0), "XX": (4.5, 1.0),
        "CCC": (-5.25, 0.0), "CCX": (-3.75, 0.0), "CXC": (-2.25, 0.0), "CXX": (-0.75, 0.0),
        "XCC": (0.75, 0.0), "XCX": (2.25, 0.0), "XXC": (3.75, 0.0), "XXX": (5.25, 0.0),
    }
    children = {
        "root": ["C", "X"],
        "C": ["CC", "CX"], "X": ["XC", "XX"],
        "CC": ["CCC", "CCX"], "CX": ["CXC", "CXX"],
        "XC": ["XCC", "XCX"], "XX": ["XXC", "XXX"],
    }

    def active(name):
        return any(h.startswith(name) for h in highlighted)

    p = figure(height=340, sizing_mode="stretch_width", x_range=(-6.2, 6.2), y_range=(-0.5, 3.5),
               toolbar_location=None)
    p.background_fill_alpha = 0
    p.border_fill_alpha = 0
    p.outline_line_color = None
    p.grid.visible = False
    p.axis.visible = False

    for parent, chs in children.items():
        x0, y0 = nodes[parent]
        for c in chs:
            x1, y1 = nodes[c]
            on = active(c)
            p.line([x0, x1], [y0, y1], line_color=hi if on else line_def, line_width=6 if on else 2.5)

    for name, (x, y) in nodes.items():
        if name == "root":
            p.scatter([x], [y], size=42, marker="circle", fill_color=fill_def,
                      line_color=ui.UBU_RED, line_width=4)
            p.text([x], [y], text=["Ω"], text_align="center", text_baseline="middle",
                   text_font_size="22px", text_color=ui.UBU_RED)
            continue
        is_leaf = len(name) == 3
        on = active(name)
        p.scatter([x], [y], size=44 if is_leaf else 38, marker="circle",
                  fill_color=hi_fill if name in highlighted else fill_def,
                  line_color=hi if on else line_def, line_width=5 if on else 2.5)
        p.text([x], [y], text=[name], text_align="center", text_baseline="middle",
               text_font_size="18px" if is_leaf else "17px",
               text_color=hi if on else (text_leaf if is_leaf else text_def))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué es la probabilidad?</b>")
        ui.content(
            "A lo largo de la historia la probabilidad ha recibido cuatro grandes definiciones, y todas "
            "conviven hoy. La <b>clásica</b> (o de Laplace) cuenta casos favorables entre casos "
            "posibles cuando todos son igual de verosímiles; la <b>frecuentista</b> la entiende como el "
            "límite de la frecuencia relativa al repetir un experimento muchísimas veces; la "
            "<b>bayesiana</b> la interpreta como un grado de creencia que se actualiza con la evidencia; "
            "y la <b>axiomática</b> de Kolmogórov no dice qué <i>es</i> la probabilidad, sino qué reglas "
            "debe cumplir. Iremos detallando cada una en otros temas: aquí nos quedamos con esta última, "
            "la que puso los cimientos de todas."
        )
        ui.content(
            "Andréi Kolmogórov (1903-1987) fue tan aficionado al deporte como a las matemáticas: se "
            "cuenta que esquiaba y nadaba durante los crudos inviernos rusos, a veces ligero de ropa "
            "bajo el sol helado, convencido de que el cuerpo y la mente se entrenan igual. En 1933, con "
            "apenas unas páginas, hizo por el azar lo que Maxwell había hecho por la electricidad y el "
            "magnetismo: así como cuatro ecuaciones bastaban para describir todo campo electromagnético, "
            "Kolmogórov buscó las leyes mínimas que gobernaran <i>cualquier</i> sistema regido por la "
            "incertidumbre. Y las encontró en apenas <b>tres axiomas</b>, sobre los que se levanta toda "
            "la teoría moderna de la probabilidad."
        )

        ui.section("Los tres axiomas de Kolmogórov")
        ui.content("<b>(I) No negatividad.</b> La probabilidad de cualquier suceso nunca es negativa."
                   "<br><br><i>Prueba ahora a escribir esto matemáticamente.</i>")
        ui.formula_hidden("&#8473;(A) &ge; 0")
        ui.content("<b>(II) Normalización.</b> La probabilidad del suceso seguro (todo el espacio "
                   "muestral &Omega;) es 1.<br><br><i>Prueba ahora a escribir esto matemáticamente.</i>")
        ui.formula_hidden("&#8473;(&Omega;) = 1")
        ui.content("<b>(III) Aditividad numerable.</b> Para sucesos incompatibles (disjuntos), la "
                   "probabilidad de su unión es la suma de sus probabilidades.<br><br>"
                   "<i>Prueba ahora a escribir esto matemáticamente.</i>")
        ui.formula_hidden(
            "A<sub>i</sub> &cap; A<sub>j</sub> = &empty; &rArr; "
            "&#8473;(&#8899;<sub>i=1</sub><sup>&infin;</sup> A<sub>i</sub>) = "
            "&sum;<sub>i=1</sub><sup>&infin;</sup> &#8473;(A<sub>i</sub>)"
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Encerrando a Venn</b><br>"
            "<i>Ayuda a John Venn (1834-1923) a convencer a la London Mathematical Society de la "
            "utilidad de sus diagramas.</i><br><br>"
            "<b>II. Esperando a Kolmogórov (descubre al impostor)</b><br>"
            "<i>Varios compañeros del primer curso del grado del año pasado intentaron describir su "
            "propia definición de probabilidad. Descubre cuáles lo serían también para "
            "Kolmogórov.</i><br><br>"
            "<b>III. Corrigiendo con Bonferroni</b><br>"
            "<i>Comprueba junto con Carlo Emilio Bonferroni (1892-1960) que es necesario corregir el "
            "nivel de significación (&alpha;; no te preocupes, lo verás en Estadística Univariante) "
            "para evitar falsos positivos al hacer pruebas simultáneas.</i>"
        )


def event_panel(key, dark):
    label, desc, hi = EVENTS[key]
    ui.comment(f"<b>{label}</b>: {desc}. Cardinalidad |{label}| = {len(hi)} de {len(OMEGA)}.")
    ui.badge(f"{label} = {{ {', '.join(hi)} }}")
    ui.show(tree_diagram(hi, dark), key=f"fig_tree_{key}")
    ui.footer_bar(
        "Si todos los resultados son equiprobables, la probabilidad de un suceso es su nº de casos "
        f"favorables entre 8. Aquí: P = {len(hi)}/8 = {len(hi) / len(OMEGA):.3f}."
    )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Encerrando a Venn</b><br><br>"
            "Llamamos C a cara y X a cruz. Al lanzar una moneda una sola vez, el conjunto de todos los "
            "resultados posibles es &Omega; = {C, X}. Si la lanzamos tres veces, ese conjunto crece hasta "
            "los 2<sup>3</sup> = 8 resultados:<br><br>"
            "&Omega; = {CCC, CCX, CXC, XCC, CXX, XCX, XXC, XXX}"
        )

        if ui.accordion_step("P1_A", "(A) Primeros sucesos"):
            ui.content(
                "Escribe el conjunto de resultados de cada suceso:<br><br>"
                "<b>E:</b> exactamente dos cruces.<br>"
                "<b>F:</b> al menos dos cruces.<br>"
                "<b>G:</b> no aparece cruz antes que la primera cara.<br>"
                "<b>H:</b> el primer lanzamiento es cruz.<br><br>"
                "Pulsa cada suceso para verlo resaltado en el árbol de la derecha."
            )
            ui.choice_buttons(PART_A_KEYS, "sel_a")
            ui.spoiler(
                "E = {CXX, XCX, XXC}<br>"
                "F = {CXX, XCX, XXC, XXX}<br>"
                "G = {CCC, CCX, CXC, CXX}<br>"
                "H = {XCC, XCX, XXC, XXX}"
            )

        if ui.accordion_step("P1_B", "(B) Eventos compuestos"):
            ui.content(
                "Ahora consideramos la unión, intersección o diferencia de varios de los anteriores. "
                "¿Cómo podrías describir estos sucesos?<br><br>"
                "E<sup>c</sup>, &nbsp; F \\ E, &nbsp; E &cup; (G &cap; H), &nbsp; E &cap; H<sup>c</sup>"
            )
            ui.choice_buttons(PART_B_KEYS, "sel_b", labels=PART_B_LABELS)
            ui.spoiler(
                "E<sup>c</sup> = {CCC, CCX, CXC, XCC, XXX}<br>"
                "F \\ E = {XXX}<br>"
                "E &cup; (G &cap; H) = E &cup; &empty; = {CXX, XCX, XXC}<br>"
                "E &cap; H<sup>c</sup> = {CXX}"
            )

        if ui.accordion_step("P1_C", "(C) Monedas sospechosas"):
            ui.content(
                "En principio la probabilidad de cara o cruz es idéntica e igual a un medio. Definamos "
                "ahora la probabilidad de <b>cruz</b> con p.<br><br>"
                "Un amigo te ha propuesto jugaros quién hace la tarea con una moneda que sacó de su "
                "bolsillo. Sospechosamente, ha dicho que se pide cruz. ¿Cómo se modifica la probabilidad "
                "de cada resultado? Elige un resultado en los botones de abajo y mueve el deslizador p de "
                "la derecha."
            )
            ui.choice_buttons(OMEGA, "sel_c")
            ui.formula_hidden(
                "P(resultado) = p<sup>&#8203;(nº de cruces)</sup> (1&minus;p)<sup>&#8203;(nº de caras)</sup>",
                hint="Pulsa para revelar la fórmula general",
            )

    with col_right:
        ui.right_panel()
        ui.section("El espacio muestral en árbol")
        open_part = st.session_state["open_part"]

        if open_part == "P1_B":
            event_panel(st.session_state["sel_b"], dark)
        elif open_part == "P1_C":
            p_cruz = st.slider("p (probabilidad de cruz)", 0.0, 1.0, v["p_cruz"], 0.01,
                               key=ui.wkey(PAGE, "p_cruz"), label_visibility="collapsed")
            outcome = st.session_state["sel_c"]
            n_x, n_c = outcome.count("X"), outcome.count("C")
            prob = p_cruz ** n_x * (1 - p_cruz) ** n_c
            ui.comment(f"Con p = {p_cruz:.2f}, el resultado <b>{outcome}</b> tiene {n_x} cruces y "
                       f"{n_c} caras.")
            ui.badge(f"P({outcome}) = {p_cruz:.2f}<sup>{n_x}</sup> · {1 - p_cruz:.2f}<sup>{n_c}</sup> "
                     f"= {prob:.3f}")
            ui.show(tree_diagram([outcome], dark), key="fig_tree_coin")
            ui.footer_bar("Cuando la moneda no es justa los ocho resultados dejan de ser equiprobables: "
                          "cada uno pesa según cuántas cruces y caras contiene.")
        else:
            event_panel(st.session_state["sel_a"], dark)


def render_problem_2():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Esperando a Kolmogórov · Descubre al impostor</b><br><br>"
            "Varios compañeros del primer curso del grado del año pasado intentaron inventar su propia "
            "definición de probabilidad. Cada una es un <i>candidato</i> a función de probabilidad, pero "
            "solo será válida si cumple los <b>tres axiomas</b> de Kolmogórov. Estos fueron sus "
            "candidatos:"
        )
        ui.content(
            "<b>1.</b> P(A) = 0 si A es finito, 1 si A es infinito.<br><br>"
            "<b>2.</b> P(A) = a si A &ne; &empty;, 0 si A = &empty; (con a constante).<br><br>"
            "<b>3.</b> Probabilidad clásica o de Laplace: P(A) = |A| / |&Omega;|."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.choice_buttons([0, 1, 2], "sel_cand", labels={i: f"Candidato {i + 1}" for i in range(3)},
                          per_row=3)
        c = CANDIDATOS[st.session_state["sel_cand"]]
        ui.comment(c["label"])
        for i, name in enumerate(AXIOM_NAMES):
            ok = c["ax"][i]
            ui.check(ok, f"<b>{name}: {'cumple' if ok else 'no cumple'}.</b><br>{c['why'][i]}")
        if all(c["ax"]):
            ui.metric("Es una medida de probabilidad válida", "result-yes")
        else:
            ui.metric("No es una medida de probabilidad válida", "result-no")


def render_problem_3():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement(
            "<b>Corrigiendo con Bonferroni</b><br><br>"
            "Carlo Emilio Bonferroni (1892-1960) fue un matemático italiano que trabajó en Bari y "
            "Florencia sobre cálculo de probabilidades y matemática actuarial (la de los seguros). Su "
            "nombre quedó unido a unas desigualdades que acotan la probabilidad de que varios sucesos "
            "ocurran a la vez y, sobre todo, a la <b>corrección de Bonferroni</b>: al realizar muchas "
            "pruebas estadísticas simultáneas hay que endurecer el nivel de significación &alpha; para no "
            "acumular falsos positivos."
        )
        ui.formula(F_GOAL)

    with col_right:
        ui.right_panel()
        ui.section("Demuéstralo por etapas")
        etapa = ui.stage("bonf_stage", 3)

        if etapa == 1:
            ui.content(
                "<b>Etapa 1 · Planteamiento.</b><br>"
                "Queremos acotar por debajo la probabilidad de que ocurran todos los sucesos "
                "A<sub>1</sub>, …, A<sub>n</sub> a la vez (su intersección). Ese es el objetivo que "
                "buscamos demostrar.<br><br><i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(F_GOAL)
        elif etapa == 2:
            ui.content(
                "<b>Etapa 2 · Del complementario a la unión.</b><br>"
                "Primero pasamos a complementarios: por las leyes de De Morgan, el complementario de la "
                "intersección es la unión de los complementarios.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(F_DEMOR)
            ui.content(
                "Y por la regla del complementario, la probabilidad de la intersección es 1 menos la "
                "probabilidad de esa unión.<br><br><i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(F_COMPL)
        else:
            ui.content(
                "<b>Etapa 3 · Acotar y concluir.</b><br>"
                "Acotamos la unión con la desigualdad de Boole: la probabilidad de una unión nunca "
                "supera la suma de las probabilidades.<br><br>"
                "<i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(F_BOOLE)
            ui.content(
                "Combinando la regla del complementario con la desigualdad de Boole obtenemos la "
                "desigualdad de Bonferroni.<br><br><i>Trata de escribirlo de manera matemática.</i>"
            )
            ui.formula_hidden(F_GOAL + " &#8718;")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Encerrando a Venn", "P1_A"),
        ("P2", "(II) Esperando a Kolmogórov", None),
        ("P3", "(III) Corrigiendo con Bonferroni", None),
    ])

    if current == "INTRO":
        render_intro()
    elif current == "P1":
        render_problem_1(dark, v)
    elif current == "P2":
        render_problem_2()
    elif current == "P3":
        render_problem_3()

    ui.footer()


main()
