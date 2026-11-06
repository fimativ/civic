#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 2, ficha 3: el teorema de Bayes.

Tres situaciones: el albacea de Bayes revisa un test de diagnóstico
(probabilidad total e inversión del condicionamiento), las cartas a Marilyn
vos Savant sobre el concurso de las puertas, y la probabilidad de las causas
de Laplace con una urna. Los valores iniciales dependen del código de sesión.
"""

from __future__ import annotations

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "El teorema de Bayes"
SYMBOL = "A|B⇄B|A"
PAGE = "02_03"

PREVALENCES = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]

# =============================================================================
# 1. VALORES INICIALES (dependen del código de sesión)
# =============================================================================

def initial_values():
    return {
        "prev": ui.dchoice(0.02, PREVALENCES[1:7], "prev"),
        "sens": ui.dchoice(0.70, [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95], "sens"),
        "fpos": ui.dchoice(0.10, [0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20], "fpos"),
        "doors": 3 + round(7 * ui.r()) if ui.has_code() else 3,
        "red": ui.dint(3, 1, 6, "red"),
        "green": ui.dint(2, 1, 6, "green"),
        "white": ui.dint(4, 1, 6, "white"),
    }


def init_session_state():
    ui.init_state({
        "page": "INTRO",
        "open_part": "P1_A",
        "mh_games": None,
    })


# =============================================================================
# 2. CÁLCULOS
# =============================================================================

def posterior(prev: float, sens: float, fpos: float, repeats: int = 1) -> float:
    """P(enfermo | positivo en `repeats` tests independientes)."""
    num = prev * sens ** repeats
    den = num + (1 - prev) * fpos ** repeats
    return num / den if den > 0 else 0.0


def monty_probabilities(n_doors: int, k_open: int):
    stay = 1 / n_doors
    switch = (n_doors - 1) / n_doors / (n_doors - 1 - k_open)
    return stay, switch


def play_monty(n_doors: int, k_open: int, games: int, rng):
    """Simula `games` partidas. Si el coche no está en la puerta elegida, queda
    entre las n−1−k cerradas y el cambio acierta con probabilidad 1/(n−1−k)."""
    car_at_chosen = rng.integers(n_doors, size=games) == 0
    win_stay = car_at_chosen.mean()
    switch_hits = rng.integers(n_doors - 1 - k_open, size=games) == 0
    win_switch = (~car_at_chosen & switch_hits).mean()
    return win_stay, win_switch


def urn_posteriors(red: int, green: int, white: int, replace: bool):
    counts = np.array([red, green, white], dtype=float)
    total = counts.sum()
    prior = counts / total
    if replace:
        cond_white = np.full(3, white / total)
    else:
        remaining = np.array([white, white, white - 1], dtype=float)
        cond_white = remaining / (total - 1)
    p_white2 = float((cond_white * prior).sum())
    post = cond_white * prior / p_white2 if p_white2 > 0 else np.full(3, np.nan)
    return prior, cond_white, p_white2, post


# =============================================================================
# 3. FIGURAS
# =============================================================================

def posterior_curve(dark, prev, sens, fpos):
    xs = np.logspace(-3, 0, 300)
    one = np.array([posterior(x, sens, fpos, 1) for x in xs])
    two = np.array([posterior(x, sens, fpos, 2) for x in xs])
    p = ui.new_figure(dark, height=320, x_axis_type="log",
                      x_axis_label="prevalencia π (escala logarítmica)",
                      y_axis_label="P(enfermo | positivo)",
                      x_range=(1e-3, 1), y_range=(0, 1.02))
    p.line(xs, one, line_width=5, color=ui.BLUE_LINE, legend_label="un positivo")
    p.line(xs, two, line_width=4, color=ui.GREEN_LINE, line_dash="dashed",
           legend_label="dos positivos independientes")
    p.line([1e-3, 1], [0.5, 0.5], line_color=ui.GREY_LINE, line_dash="dotted", line_width=1)
    p.scatter([prev], [posterior(prev, sens, fpos, 1)], size=16, color=ui.BLUE_LINE,
              line_color="white", line_width=2)
    p.scatter([prev], [posterior(prev, sens, fpos, 2)], size=16, color=ui.GREEN_LINE,
              line_color="white", line_width=2)
    return ui.style_legend(p, dark, "top_left")


def monty_bars(dark, stay, switch, simulated):
    labels = ["Quedarse", "Cambiar"]
    p = ui.new_figure(dark, height=320, x_range=labels, y_range=(0, 1.05),
                      y_axis_label="probabilidad de ganar el coche")
    p.vbar(x=labels, top=[stay, switch], width=0.55,
           color=[ui.RED_LINE, ui.GREEN_LINE], alpha=0.85, legend_label="teoría")
    if simulated is not None:
        p.scatter(labels, list(simulated), size=18, marker="diamond", color=ui.UBU_YELLOW,
                  line_color=ui.UBU_DARK, line_width=2, legend_label="frecuencia simulada")
    p.xaxis.major_label_text_font_size = "17px"
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_left")


def urn_bars(dark, prior, post):
    colours = ["roja", "verde", "blanca"]
    fills = [ui.RED_LINE, ui.GREEN_LINE, ui.GREY_LINE]
    x_prior = [i - 0.18 for i in range(3)]
    x_post = [i + 0.18 for i in range(3)]
    p = ui.new_figure(dark, height=320, x_range=(-0.6, 2.6), y_range=(0, 1.05),
                      y_axis_label="probabilidad del color de la primera bola")
    p.vbar(x=x_prior, top=list(prior), width=0.34, color=fills, alpha=0.35,
           legend_label="a priori P(C₁)")
    if not np.isnan(post).any():
        p.vbar(x=x_post, top=list(post), width=0.34, color=fills, alpha=0.95,
               legend_label="a posteriori P(C₁ | B₂)")
    p.xaxis.ticker = [0, 1, 2]
    p.xaxis.major_label_overrides = dict(enumerate(colours))
    p.xaxis.major_label_text_font_size = "17px"
    p.xgrid.grid_line_color = None
    return ui.style_legend(p, dark, "top_right")


# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se aprende de la evidencia?</b>")
        ui.content(
            "Thomas Bayes (1701-1761) fue pastor presbiteriano en Tunbridge Wells y miembro de la "
            "Royal Society, aunque en vida publicó poco y nada sobre el resultado que lleva su "
            "nombre. Su ensayo sobre el problema de las probabilidades lo rescató de entre sus "
            "papeles y lo presentó su amigo Richard Price en 1763, dos años después de su muerte. "
            "Price lo leía como una respuesta al escepticismo de Hume: ¿cuánta evidencia hace falta "
            "para creer razonablemente en algo que parecía improbable? Una década más tarde, "
            "Laplace redescubrió la regla por su cuenta, la generalizó y la aplicó a cuanto tenía a "
            "mano: urnas, nacimientos, órbitas de cometas."
        )
        ui.content(
            "La idea es una inversión. Los modelos nos dan la probabilidad de los efectos conocidas "
            "las causas (si el animal está enfermo, el test da positivo con tal frecuencia), pero en "
            "la práctica observamos los efectos y queremos juzgar las causas. Bayes enseña a dar la "
            "vuelta al condicionamiento. Durante siglo y medio el método se llamó "
            "<i>probabilidad inversa</i>; el adjetivo <i>bayesiano</i> es del siglo XX, y durante "
            "buena parte de él se pronunció con recelo en los departamentos de estadística."
        )
        ui.content(
            "La maquinaria es la de este tema: una partición del espacio muestral, el teorema de la "
            "probabilidad total para repartir un suceso entre las ramas de la partición y la "
            "definición de probabilidad condicionada para invertir el orden. Si {B<sub>i</sub>} es "
            "una partición y A un suceso observado, <i>prueba a escribir la probabilidad de la causa "
            "B<sub>k</sub> una vez visto A.</i>"
        )
        ui.formula_hidden(
            "&#8473;(B<sub>k</sub> | A) = &#8473;(A | B<sub>k</sub>) &#8473;(B<sub>k</sub>) &frasl; "
            "&sum;<sub>i</sub> &#8473;(A | B<sub>i</sub>) &#8473;(B<sub>i</sub>)"
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El albacea de Bayes (1763)</b><br>"
            "<i>Acompaña a Richard Price, pastor y pionero de los seguros de vida, mientras decide "
            "cuánto creerse el resultado de un test.</i><br><br>"
            "<b>II. Las cartas a Marilyn (1990)</b><br>"
            "<i>Defiende con Marilyn vos Savant, frente a miles de lectores indignados, que en el "
            "concurso de las puertas conviene cambiar.</i><br><br>"
            "<b>III. La probabilidad de las causas (1774)</b><br>"
            "<i>Razona hacia atrás con el joven Laplace: una urna, dos extracciones y una bola que "
            "nadie miró.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica la <u>prevalencia π</u>, la <u>sensibilidad s</u> y la "
                  "<u>tasa de falsas alarmas f</u>")
        prev = st.select_slider("Prevalencia π", options=PREVALENCES, value=v["prev"],
                                key=ui.wkey(PAGE, "prev"))
        c1, c2 = st.columns(2)
        sens = c1.slider("Sensibilidad s = P(T | Z)", 0.50, 1.00, v["sens"], 0.01,
                         key=ui.wkey(PAGE, "sens"))
        fpos = c2.slider("Falsas alarmas f = P(T | Zᶜ)", 0.00, 0.30, v["fpos"], 0.01,
                         key=ui.wkey(PAGE, "fpos"))

        ui.planteamiento()
        ui.statement(
            "<b>El albacea de Bayes (1763)</b><br><br>"
            "Richard Price, pastor, filósofo y uno de los padres de la ciencia actuarial (sus tablas "
            "de mortalidad de Northampton rigieron durante décadas las primas de la Equitable, la "
            "primera compañía moderna de seguros de vida), encontró entre los papeles de su amigo "
            "Thomas Bayes un ensayo sobre cómo revisar una probabilidad a la luz de la evidencia. Lo "
            "presentó a la Royal Society. Probémoslo nosotros con la clase de problema que un asegurador "
            "entiende bien: ¿cuánto hay que creerse un diagnóstico?"
        )

        if ui.accordion_step("P1_A", "(A) El árbol de la probabilidad total"):
            ui.content(
                f"Una enfermedad del ganado afecta a una fracción π = {v['prev']} de los animales "
                f"(prevalencia). Un test la detecta en una fracción s = {v['sens']:.2f} de los "
                f"enfermos (sensibilidad) y da positivo por error en una fracción f = {v['fpos']:.2f} "
                "de los sanos (falsa alarma). Llamemos Z a <i>estar enfermo</i> y T a <i>dar "
                "positivo</i>. Los sucesos Z y Z<sup>c</sup> forman una partición del espacio "
                "muestral: todo animal está en uno y solo en uno de los dos. ¿Cuál es la "
                "probabilidad de que un animal elegido al azar dé positivo?"
            )
            ui.spoiler(
                "Por el teorema de la probabilidad total, el suceso T se reparte entre las dos "
                "ramas de la partición:"
                "<div class='formula-box'>&#8473;(T) = &#8473;(T | Z) &#8473;(Z) + "
                "&#8473;(T | Z<sup>c</sup>) &#8473;(Z<sup>c</sup>) = s&middot;π + f&middot;(1 &minus; π)</div>"
                "Dos caminos llevan al positivo: estar enfermo y ser detectado, o estar sano y "
                "sufrir una falsa alarma."
            )

        if ui.accordion_step("P1_B", "(B) Invertir la pregunta"):
            ui.content(
                "El fabricante del test conoce &#8473;(T | Z), la probabilidad de positivo cuando hay "
                "enfermedad. Al ganadero le interesa justo lo contrario: la probabilidad de "
                "enfermedad cuando hay positivo, &#8473;(Z | T). Confundir ambas es el error más "
                "frecuente de todo el tema. ¿Cómo se pasa de una a la otra?"
            )
            ui.spoiler(
                "Por la definición de probabilidad condicionada, &#8473;(Z | T) = &#8473;(Z &cap; T) / "
                "&#8473;(T), y la intersección se escribe con la regla de la multiplicación en el "
                "orden que sí conocemos. Es el teorema de Bayes:"
                "<div class='formula-box'>&#8473;(Z | T) = &#8473;(T | Z) &#8473;(Z) &frasl; "
                "[&#8473;(T | Z) &#8473;(Z) + &#8473;(T | Z<sup>c</sup>) &#8473;(Z<sup>c</sup>)]</div>"
                "El numerador es la rama <i>enfermo y positivo</i>; el denominador, la probabilidad "
                "total del positivo que calculaste en (A)."
            )

        if ui.accordion_step("P1_C", "(C) La falacia de la tasa base"):
            ui.content(
                "Deja s y f en valores excelentes y baja la prevalencia hasta donde puedas. ¿Qué le "
                "ocurre a &#8473;(Z | T)? Y si el mismo animal da positivo en un segundo test, "
                "realizado de forma independiente del primero, ¿cómo cambia la probabilidad de que "
                "esté enfermo?"
            )
            ui.spoiler(
                "Cuando la enfermedad es rara, los sanos son tantos que incluso una fracción pequeña "
                "f de falsas alarmas produce más positivos que todos los enfermos juntos: el "
                "denominador lo domina el término f&middot;(1 &minus; π). Ignorar la prevalencia y "
                "quedarse solo con la sensibilidad es la <i>falacia de la tasa base</i>. Para el "
                "segundo test, la probabilidad a posteriori del primero pasa a ser la a priori del "
                "segundo (la a posteriori de hoy es la a priori de mañana) y se aplica Bayes de nuevo; "
                "si los tests son independientes dadas las causas, el resultado es:"
                "<div class='formula-box'>&#8473;(Z | T<sub>1</sub> &cap; T<sub>2</sub>) = "
                "s<sup>2</sup>π &frasl; [s<sup>2</sup>π + f<sup>2</sup>(1 &minus; π)]</div>"
            )

    with col_right:
        ui.right_panel()
        p_test = sens * prev + fpos * (1 - prev)
        post1 = posterior(prev, sens, fpos, 1)
        post2 = posterior(prev, sens, fpos, 2)
        verdict = "result-yes" if post1 > 0.5 else "result-no"
        ui.metrics([
            (f"&#8473;(T) = {p_test:.4f}", "metric-a"),
            (f"&#8473;(Z | T) = {post1:.4f}", verdict),
        ])
        ui.show(posterior_curve(dark, prev, sens, fpos), key="fig_bayes_test")
        per_thousand = round(1000 * post1)
        ui.footer_bar(
            f"Con π = {prev}, s = {sens:.2f} y f = {fpos:.2f}: de cada 1000 positivos, unos "
            f"{per_thousand} corresponden a animales enfermos. Tras dos positivos independientes la "
            f"probabilidad sube a {post2:.4f}."
        )


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica el <u>número de puertas N</u> y las <u>puertas k</u> que abre "
                  "el presentador")
        n_doors = st.slider("Número de puertas N", 3, 10, v["doors"], 1, key=ui.wkey(PAGE, "doors"))
        max_open = n_doors - 2
        if max_open == 1:
            k_open = 1
            st.caption("Con tres puertas el presentador solo puede abrir una, k = 1.")
        else:
            k_open = st.slider("Puertas con cabra que abre el presentador, k", 1, max_open,
                               max_open, 1, key=ui.wkey(PAGE, f"kopen{n_doors}"))

        ui.planteamiento()
        ui.statement(
            "<b>Las cartas a Marilyn (1990)</b><br><br>"
            "Un lector, Craig F. Whitaker, preguntó a Marilyn vos Savant, que firmaba una columna de acertijos en la "
            "revista <i>Parade</i>, si convenía cambiar de puerta en el concurso de Monty Hall. "
            "Marilyn contestó que sí y recibió miles de cartas, muchas de matemáticos con doctorado, "
            "asegurándole que se equivocaba. No se equivocaba. En nuestra versión el concurso tiene "
            f"N = {v['doors']} puertas: tras una hay un coche y tras el resto, cabras. Eliges una; el "
            "presentador, que sabe dónde está el coche, abre k puertas con cabra entre las que no has "
            "elegido y te ofrece cambiar a cualquiera de las que siguen cerradas."
        )

        if ui.accordion_step("P2_A", "(A) Quedarse"):
            ui.content(
                "Si no cambias, ganas solo si acertaste a la primera. ¿Cuál es esa probabilidad, y "
                "por qué no la altera lo que haga después el presentador?"
            )
            ui.spoiler(
                "Por la regla de Laplace, con N puertas igualmente verosímiles:"
                "<div class='formula-box'>&#8473;(ganar sin cambiar) = 1 &frasl; N</div>"
                "El presentador siempre puede abrir k puertas con cabra, hayas acertado o no, así que "
                "el suceso <i>abre k cabras</i> tiene probabilidad uno en las dos ramas de la "
                "partición {A, A<sup>c</sup>}, con A = <i>el coche está en tu puerta</i>. Un suceso "
                "que ocurre seguro en todas las ramas no mueve la probabilidad de ninguna."
            )

        if ui.accordion_step("P2_B", "(B) Cambiar"):
            ui.content(
                "Si cambias, eliges al azar una de las N &minus; 1 &minus; k puertas que siguen "
                "cerradas aparte de la tuya. Condiciona según acertaras o no al principio y aplica el "
                "teorema de la probabilidad total."
            )
            ui.spoiler(
                "Con G = <i>ganar el coche</i>:"
                "<div class='formula-box'>&#8473;(G) = &#8473;(G | A) &#8473;(A) + "
                "&#8473;(G | A<sup>c</sup>) &#8473;(A<sup>c</sup>) = "
                "0 &middot; (1&frasl;N) + [1 &frasl; (N &minus; 1 &minus; k)] &middot; "
                "[(N &minus; 1) &frasl; N]</div>"
                "Si el presentador abre todas las cabras que puede (k = N &minus; 2) solo queda una "
                "puerta a la que cambiar, y la probabilidad de ganar es (N &minus; 1)&frasl;N: el "
                "complementario de haber acertado a la primera."
            )

        if ui.accordion_step("P2_C", "(C) ¿Por qué tantas cartas?"):
            ui.content(
                "El argumento de quienes escribían a Marilyn era: <i>quedan dos puertas, luego es un "
                "50 %</i>. ¿Dónde está el fallo? Imagina ahora un presentador despistado que no sabe "
                "dónde está el coche, abre una puerta al azar y, por suerte, aparece una cabra. ¿Cambia "
                "algo?"
            )
            ui.spoiler(
                "El fallo es tratar como equiprobables dos puertas que no lo son: una fue elegida a "
                "ciegas y la otra sobrevivió a un filtro aplicado por alguien que conoce la "
                "respuesta. Con el presentador despistado, el suceso <i>aparece una cabra</i> sí tiene "
                "probabilidades distintas en cada rama (seguro si tenías el coche, no seguro si no), y "
                "al aplicar el teorema de Bayes todas las puertas cerradas quedan igualadas: cambiar ya "
                "no mejora nada. La información no está en la puerta abierta, sino en quién la abrió."
            )

    with col_right:
        ui.right_panel()
        stay, switch = monty_probabilities(n_doors, k_open)
        ui.metrics([
            (f"Quedarse: {stay:.4f}", "result-no"),
            (f"Cambiar: {switch:.4f}", "result-yes"),
        ])
        b1, b2 = st.columns([2, 1])
        if b1.button("Juega 1000 partidas con cada estrategia", key="mh_play", width="stretch"):
            rng = np.random.default_rng()
            st.session_state["mh_games"] = (n_doors, k_open, *play_monty(n_doors, k_open, 1000, rng))
        if b2.button("Borrar", key="mh_clear", width="stretch"):
            st.session_state["mh_games"] = None
        games = st.session_state.get("mh_games")
        simulated = None
        if games and games[0] == n_doors and games[1] == k_open:
            simulated = games[2:]
        ui.show(monty_bars(dark, stay, switch, simulated), key="fig_monty")
        gain = switch / stay
        text = (f"Con N = {n_doors} y k = {k_open}: cambiar multiplica por {gain:.2f} la "
                "probabilidad de ganar.")
        if simulated is not None:
            text += (f" En la simulación: {simulated[0]:.3f} quedándose y {simulated[1]:.3f} "
                     "cambiando.")
        ui.footer_bar(text)


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica la <u>composición de la urna</u> y decide si hay "
                  "<u>reemplazamiento</u>")
        c1, c2, c3 = st.columns(3)
        red = c1.number_input("Rojas", 0, 12, v["red"], key=ui.wkey(PAGE, "red"))
        green = c2.number_input("Verdes", 0, 12, v["green"], key=ui.wkey(PAGE, "green"))
        white = c3.number_input("Blancas", 0, 12, v["white"], key=ui.wkey(PAGE, "white"))
        replace = st.checkbox("Devolver la primera bola a la urna (con reemplazamiento)",
                              value=False, key=ui.wkey(PAGE, "replace"))

        ui.planteamiento()
        ui.statement(
            "<b>La probabilidad de las causas (1774)</b><br><br>"
            "Con veinticinco años, Pierre-Simon Laplace publicó una memoria sobre la probabilidad de "
            "las causas por los sucesos: sin conocer el ensayo de Bayes, reinventó la regla y la "
            "convirtió en un método general. Sus ejemplos favoritos eran las urnas. En la nuestra hay "
            f"{v['red']} bolas rojas, {v['green']} verdes y {v['white']} blancas; se extraen dos sin "
            "reemplazamiento y la segunda resulta ser blanca. ¿Qué podemos decir de la primera, que "
            "nadie miró?"
        )

        if ui.accordion_step("P3_A", "(A) Hacia delante"):
            ui.content(
                "El color de la primera bola, {R<sub>1</sub>, V<sub>1</sub>, B<sub>1</sub>}, es una "
                "partición del espacio muestral. Calcula la probabilidad de que la segunda bola sea "
                "blanca y compárala con la de que lo sea la primera."
            )
            ui.spoiler(
                "Por el teorema de la probabilidad total:"
                "<div class='formula-box'>&#8473;(B<sub>2</sub>) = &#8473;(B<sub>2</sub> | R<sub>1</sub>) "
                "&#8473;(R<sub>1</sub>) + &#8473;(B<sub>2</sub> | V<sub>1</sub>) &#8473;(V<sub>1</sub>) + "
                "&#8473;(B<sub>2</sub> | B<sub>1</sub>) &#8473;(B<sub>1</sub>)</div>"
                "Cada condicionada sale de la regla de Laplace aplicada a la urna que queda tras la "
                "primera extracción. El resultado es exactamente la proporción inicial de blancas: "
                "mientras nadie mire la primera bola, la segunda extracción es tan <i>fresca</i> como "
                "la primera."
            )

        if ui.accordion_step("P3_B", "(B) Hacia atrás"):
            ui.content(
                "Sabiendo que la segunda bola fue blanca, ¿cuál es la probabilidad de que la primera "
                "fuera roja? ¿Y verde? ¿Y blanca? Observa en la figura cómo la evidencia redistribuye "
                "la probabilidad entre las tres causas."
            )
            ui.spoiler(
                "Es el teorema de Bayes sobre la partición de los colores:"
                "<div class='formula-box'>&#8473;(R<sub>1</sub> | B<sub>2</sub>) = "
                "&#8473;(B<sub>2</sub> | R<sub>1</sub>) &#8473;(R<sub>1</sub>) &frasl; &#8473;(B<sub>2</sub>)</div>"
                "y análogamente para las otras dos. Las tres a posteriori suman uno, porque la "
                "probabilidad condicionada es una medida de probabilidad legítima sobre la partición. "
                "La blanca sale perdiendo: haber sacado una blanca al principio deja menos blancas para "
                "la segunda extracción, así que la evidencia la hace menos verosímil."
            )

        if ui.accordion_step("P3_C", "(C) Con reemplazamiento"):
            ui.content(
                "Marca la casilla de arriba para devolver la primera bola a la urna antes de la "
                "segunda extracción. ¿Qué le pasa ahora a la probabilidad de las causas?"
            )
            ui.spoiler(
                "Con reemplazamiento la segunda urna es idéntica a la primera, luego "
                "&#8473;(B<sub>2</sub> | C<sub>1</sub>) = &#8473;(B<sub>2</sub>) para cualquier color "
                "C<sub>1</sub>: las dos extracciones son sucesos independientes y la fórmula de Bayes "
                "devuelve"
                "<div class='formula-box'>&#8473;(C<sub>1</sub> | B<sub>2</sub>) = &#8473;(C<sub>1</sub>)</div>"
                "La evidencia no informa sobre una causa de la que es independiente: a priori y a "
                "posteriori coinciden, y en la figura las barras claras y oscuras se igualan."
            )

    with col_right:
        ui.right_panel()
        total = red + green + white
        if total < 2 or (white == 0):
            ui.comment("Hacen falta al menos dos bolas y alguna blanca para que el suceso "
                       "<i>la segunda bola es blanca</i> pueda observarse.")
            return
        prior, cond_white, p_white2, post = urn_posteriors(red, green, white, replace)
        ui.metrics([
            (f"&#8473;(B<sub>2</sub>) = {p_white2:.4f}", "metric-a"),
            (f"&#8473;(R<sub>1</sub> | B<sub>2</sub>) = {post[0]:.4f}", "metric-c"),
        ])
        ui.show(urn_bars(dark, prior, post), key="fig_urn")
        mode = "con" if replace else "sin"
        ui.footer_bar(
            f"Urna de {red} rojas, {green} verdes y {white} blancas, {mode} reemplazamiento: "
            f"a posteriori, roja {post[0]:.3f}, verde {post[1]:.3f}, blanca {post[2]:.3f} "
            f"(a priori {prior[0]:.3f}, {prior[1]:.3f}, {prior[2]:.3f})."
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
        ("P1", "(I) El albacea de Bayes", "P1_A"),
        ("P2", "(II) Las cartas a Marilyn", "P2_A"),
        ("P3", "(III) La probabilidad de las causas", "P3_A"),
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
