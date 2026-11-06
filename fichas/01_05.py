#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Tema 1, ficha 5: la fórmula de Poincaré (inclusión-exclusión).

Tres situaciones: el álbum de cromos (cuántos hay que comprar para llenarlo y
las cotas de Bonferroni), la criba de Legendre (múltiplos y recuento de
primos) y la apuesta del caballero de Méré (complementario, De Morgan y
binomio de Newton). Los regalos de los Reyes Magos, el otro gran ejemplo de
la fórmula, están en la ficha de Laplace.
Los valores iniciales dependen del código de sesión.
"""

from __future__ import annotations

from itertools import combinations
from fractions import Fraction
from math import comb, log, prod

import numpy as np
import streamlit as st

import civic_ui as ui

TITLE = "La fórmula de Poincaré"
SYMBOL = "∪ Aᵢ"
PAGE = "01_05"

PRIMES = [2, 3, 5, 7]

# =============================================================================
# 1. VALORES INICIALES (dependen del código de sesión)
# =============================================================================

def initial_values():
    return {
        "stickers": ui.dint(20, 10, 40, "stickers"),
        "bought": ui.dint(60, 30, 120, "bought"),
        "limit": ui.dint(30, 20, 100, "limit"),
        "rolls_one": ui.dint(4, 2, 8, "one"),
        "rolls_two": ui.dint(24, 15, 40, "two"),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A"})


# =============================================================================
# 2. CÁLCULOS
# =============================================================================

def p_complete(n: int, m: int) -> float:
    """Probabilidad de completar un álbum de n cromos comprando m sueltos al azar
    (fórmula de Poincaré sobre los sucesos «falta el cromo i», en aritmética exacta)."""
    if m < n:
        return 0.0
    total = sum((-1) ** k * comb(n, k) * (n - k) ** m for k in range(n + 1))
    return float(Fraction(total, n ** m))


def boole_bound(n: int, m: int) -> float:
    """Cota inferior que da la desigualdad de Boole: 1 − n(1 − 1/n)^m."""
    return max(0.0, 1 - n * (1 - 1 / n) ** m)


def bonferroni_terms(n: int, m: int, terms: int = 4):
    """Sumas parciales de la fórmula de Poincaré para P(falta algún cromo)."""
    out, acc = [], 0.0
    for k in range(1, min(n, terms) + 1):
        acc += (-1) ** (k + 1) * comb(n, k) * (1 - k / n) ** m
        out.append(acc)
    return out


def stickers_needed(n: int, target: float) -> int:
    m = n
    while p_complete(n, m) < target:
        m += max(1, n // 10)
    while m > n and p_complete(n, m - 1) >= target:
        m -= 1
    return m


def sieve_count(limit: int, primes) -> tuple[int, int]:
    """Número de enteros en 1..limit divisibles por algún primo de la lista
    (inclusión-exclusión con suelos) y la suma sin corregir Σ⌊N/p⌋."""
    total = 0
    for k in range(1, len(primes) + 1):
        for subset in combinations(primes, k):
            total += (-1) ** (k + 1) * (limit // prod(subset))
    naive = sum(limit // p for p in primes)
    return total, naive


def divisor_counts(limit: int, primes):
    numbers = np.arange(1, limit + 1)
    counts = np.zeros(limit, dtype=int)
    for p in primes:
        counts += (numbers % p == 0)
    return numbers, counts


def at_least_one(p_single: float, rolls: int) -> float:
    return 1 - (1 - p_single) ** rolls


# =============================================================================
# 3. FIGURAS
# =============================================================================

def album_chart(dark, n: int, m: int):
    top = max(int(n * (log(n) + 4)), m + 10)
    ms = list(range(n, top + 1, max(1, (top - n) // 120)))
    exact = [p_complete(n, k) for k in ms]
    bound = [boole_bound(n, k) for k in ms]
    p = ui.new_figure(dark, height=320, x_axis_label="cromos comprados m",
                      y_axis_label="P(álbum completo)", x_range=(0, top), y_range=(0, 1.02))
    p.line([0, top], [0.5, 0.5], line_color=ui.GREY_LINE, line_dash="dotted", line_width=1)
    p.line(ms, exact, line_width=5, color=ui.BLUE_LINE, legend_label="fórmula de Poincaré")
    p.line(ms, bound, line_width=3, color=ui.ORANGE_LINE, line_dash="dashed",
           legend_label="cota de Boole")
    p.scatter([m], [p_complete(n, m)], size=18, color=ui.UBU_YELLOW, line_color=ui.UBU_DARK,
              line_width=2)
    return ui.style_legend(p, dark, "bottom_right")


def sieve_grid(dark, limit: int, primes):
    numbers, counts = divisor_counts(limit, primes)
    per_row = 10
    xs = [(k - 1) % per_row for k in numbers]
    ys = [-((k - 1) // per_row) for k in numbers]
    palette = {0: ("#f4f4f4" if not dark else "#2a2a32"), 1: ui.BLUE_LINE,
               2: ui.ORANGE_LINE, 3: ui.RED_LINE, 4: ui.PURPLE_LINE}
    fills = [palette[min(int(c), 4)] for c in counts]
    text_colour = [("#444444" if not dark else "#dddddd") if c == 0 else "#ffffff" for c in counts]
    rows = (limit - 1) // per_row + 1
    p = ui.new_figure(dark, height=max(220, 34 * rows + 40), x_range=(-0.6, per_row - 0.4),
                      y_range=(-rows + 0.4, 0.6))
    p.grid.visible = False
    p.axis.visible = False
    p.rect(x=xs, y=ys, width=0.92, height=0.92, fill_color=fills, line_color=None)
    p.text(x=xs, y=ys, text=[str(k) for k in numbers], text_align="center",
           text_baseline="middle", text_font_size="13px", text_color=text_colour)
    return p


def mere_curves(dark, n_one: int, n_two: int):
    xs = np.arange(1, 81)
    one = at_least_one(1 / 6, xs)
    two = at_least_one(1 / 36, xs)
    p = ui.new_figure(dark, height=320, x_axis_label="número de tiradas",
                      y_axis_label="probabilidad de al menos un éxito",
                      x_range=(0, 81), y_range=(0, 1.02))
    p.line([0, 81], [0.5, 0.5], line_color=ui.GREY_LINE, line_dash="dotted", line_width=1)
    p.line(xs, one, line_width=4, color=ui.BLUE_LINE, legend_label="un seis con un dado")
    p.line(xs, two, line_width=4, color=ui.GREEN_LINE, legend_label="un doble seis con dos dados")
    p.scatter([n_one], [at_least_one(1 / 6, n_one)], size=16, color=ui.BLUE_LINE,
              line_color="white", line_width=2)
    p.scatter([n_two], [at_least_one(1 / 36, n_two)], size=16, color=ui.GREEN_LINE,
              line_color="white", line_width=2)
    return ui.style_legend(p, dark, "bottom_right")


# =============================================================================
# 4. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se cuenta lo que se solapa?</b>")
        ui.content(
            "Sumar probabilidades de sucesos solo es legítimo cuando son incompatibles: es lo que "
            "dice el tercer axioma de Kolmogórov. Si los sucesos se solapan, la suma cuenta dos veces "
            "la intersección y hay que restarla; con tres sucesos, al restar las tres intersecciones "
            "dobles se ha quitado de más la triple, que hay que volver a sumar. Ese vaivén de sumas y "
            "restas, que generaliza la fórmula de la probabilidad de la unión, es el principio de "
            "inclusión-exclusión."
        )
        ui.content(
            "La idea es antigua. Pierre Rémond de Montmort la empleó en 1708 para resolver el "
            "problema de los encuentros con una baraja (el mismo de los regalos de los Reyes Magos "
            "que viste con Laplace), y Abraham de Moivre escribió la fórmula "
            "general diez años después en su <i>Doctrine of Chances</i>. En combinatoria se la conoce "
            "como fórmula de Da Silva o de Sylvester; en probabilidad la tradición francesa la bautizó "
            "con el nombre de Henri Poincaré, que la recogió en su curso de cálculo de probabilidades "
            "de 1896. Pocas fórmulas tienen tantos padres."
        )
        ui.content(
            "Para dos sucesos la fórmula se dibuja con un diagrama de Venn; para n sucesos "
            "A<sub>1</sub>, …, A<sub>n</sub> alterna sumas de intersecciones de orden creciente. "
            "<i>Prueba a escribir ambas antes de revelarlas.</i>"
        )
        ui.formula_hidden(
            "&#8473;(A &cup; B) = &#8473;(A) + &#8473;(B) &minus; &#8473;(A &cap; B)",
            hint="Pulsa para revelar la fórmula con dos sucesos",
        )
        ui.formula_hidden(
            "&#8473;(&#8899;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>) = "
            "&sum;<sub>i</sub> &#8473;(A<sub>i</sub>) &minus; &sum;<sub>i&lt;j</sub> "
            "&#8473;(A<sub>i</sub> &cap; A<sub>j</sub>) + &sum;<sub>i&lt;j&lt;k</sub> "
            "&#8473;(A<sub>i</sub> &cap; A<sub>j</sub> &cap; A<sub>k</sub>) &minus; &ctdot; + "
            "(&minus;1)<sup>n+1</sup> &#8473;(&#8898;<sub>i=1</sub><sup>n</sup> A<sub>i</sub>)",
            hint="Pulsa para revelar la fórmula de Poincaré",
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El álbum de cromos (1961)</b><br>"
            "<i>Calcula con los hermanos Panini cuántos cromos hay que comprar para llenar un álbum, "
            "y por qué los últimos huecos cuestan tanto.</i><br><br>"
            "<b>II. La criba de Legendre (1808)</b><br>"
            "<i>Tacha múltiplos con Adrien-Marie Legendre sin contar dos veces el mismo número, y "
            "cuenta primos de paso.</i><br><br>"
            "<b>III. La apuesta del caballero de Méré (1654)</b><br>"
            "<i>Averigua con Pascal por qué el caballero ganaba con un dado y perdía con dos.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica los <u>cromos del álbum n</u> y los <u>cromos comprados m</u>")
        c1, c2 = st.columns(2)
        n = c1.slider("Cromos del álbum n", 5, 60, v["stickers"], 1, key=ui.wkey(PAGE, "stickers"))
        m = c2.slider("Cromos comprados m", 5, 400, v["bought"], 1, key=ui.wkey(PAGE, "bought"))

        ui.planteamiento()
        ui.statement(
            "<b>El álbum de cromos (1961)</b><br><br>"
            "Los hermanos Panini regentaban un quiosco de prensa en Módena cuando, en 1961, lanzaron su "
            "primera colección de cromos de futbolistas. El negocio descansa sobre una pregunta tan "
            "antigua como los dados (¿cuántas tiradas hacen falta para ver salir todas las caras?) y "
            f"que aquí planteamos así: un álbum tiene n = {v['stickers']} huecos, cada cromo que compras "
            "es uno de los n al azar, con independencia de los anteriores, y has comprado "
            f"m = {v['bought']}. ¿Qué probabilidad hay de que el álbum esté completo?"
        )

        if ui.accordion_step("P1_A", "(A) Los huecos que faltan"):
            ui.content(
                "Sea A<sub>i</sub> el suceso <i>falta el cromo i</i>. El álbum está completo si no "
                "ocurre ninguno de ellos, así que basta con la probabilidad de la unión de los "
                "A<sub>i</sub>. Calcula, por la regla de Laplace sobre las n<sup>m</sup> secuencias "
                "posibles de compras, &#8473;(A<sub>i</sub>), &#8473;(A<sub>i</sub> &cap; A<sub>j</sub>) y, "
                "en general, la probabilidad de que falten k cromos concretos."
            )
            ui.spoiler(
                "Si faltan k cromos concretos, cada una de las m compras ha caído en los n &minus; k "
                "restantes; por el principio de multiplicación:"
                "<div class='formula-box'>&#8473;(A<sub>i<sub>1</sub></sub> &cap; &ctdot; &cap; "
                "A<sub>i<sub>k</sub></sub>) = (n &minus; k)<sup>m</sup> &frasl; n<sup>m</sup> = "
                "(1 &minus; k&frasl;n)<sup>m</sup></div>"
                "Como en los regalos de los Reyes, solo importa cuántos sucesos se intersecan, no cuáles."
            )

        if ui.accordion_step("P1_B", "(B) Sumar y restar"):
            ui.content(
                "Aplica la fórmula de Poincaré a A<sub>1</sub> &cup; &ctdot; &cup; A<sub>n</sub> y pasa "
                "al complementario para obtener la probabilidad de completar el álbum."
            )
            ui.spoiler(
                "Hay C(n, k) intersecciones de orden k, todas con la misma probabilidad:"
                "<div class='formula-box'>&#8473;(álbum completo) = 1 &minus; &#8473;(&#8899; A<sub>i</sub>) "
                "= &sum;<sub>k=0</sub><sup>n</sup> (&minus;1)<sup>k</sup> "
                "( <sup>n</sup>&frasl;<sub>k</sub> ) (1 &minus; k&frasl;n)<sup>m</sup></div>"
                "La suma tiene signos alternos y términos enormes que se cancelan entre sí; por eso la "
                "aplicación la evalúa con aritmética exacta de enteros."
            )

        if ui.accordion_step("P1_C", "(C) Cotas de Bonferroni"):
            ui.content(
                "Quedarse con el primer término de la fórmula es la desigualdad de Boole. ¿Qué cota da "
                "para la probabilidad de completar el álbum? ¿Y si se corta la suma tras dos, tres o "
                "cuatro términos? Compara en la derecha la curva exacta con la cota."
            )
            ui.spoiler(
                "La desigualdad de Boole acota la unión por la suma: &#8473;(&#8899; A<sub>i</sub>) &le; "
                "n(1 &minus; 1&frasl;n)<sup>m</sup>, luego"
                "<div class='formula-box'>&#8473;(álbum completo) &ge; 1 &minus; n(1 &minus; 1&frasl;n)"
                "<sup>m</sup></div>"
                "Las sumas parciales de la fórmula de Poincaré acotan alternativamente por exceso y por "
                "defecto: son las desigualdades de Bonferroni. Cuando m es grande, ya la primera es casi "
                "exacta, y de ella se deduce que comprar del orden de n&middot;ln(n) cromos basta para "
                "llenar el álbum con alta probabilidad: los últimos huecos son los caros."
            )

    with col_right:
        ui.right_panel()
        prob = p_complete(n, m)
        ui.metrics([
            (f"&#8473;(álbum completo) = {prob:.4f}", "metric-a"),
            (f"Cota de Boole: {boole_bound(n, m):.4f}", "metric-c"),
        ])
        ui.show(album_chart(dark, n, m), key="fig_album")
        partial = bonferroni_terms(n, m)
        bounds = ", ".join(f"{1 - s:.4f}" for s in partial)
        ui.footer_bar(
            f"Con n = {n} cromos hacen falta unos {stickers_needed(n, 0.5)} para tener un 50 % de "
            f"probabilidad de completarlo y {stickers_needed(n, 0.9)} para un 90 %. Cortando la fórmula "
            f"tras 1, 2, 3 y 4 términos: {bounds}."
        )


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica el <u>tope N</u> y elige los <u>primos</u> con los que cribar")
        limit = st.slider("N", 10, 120, v["limit"], 1, key=ui.wkey(PAGE, "limit"),
                          label_visibility="collapsed")
        st.caption("Primos con los que cribar")
        cols = st.columns(4)
        chosen = [p for p, col in zip(PRIMES, cols)
                  if col.checkbox(f"p = {p}", value=(p != 7), key=ui.wkey(PAGE, f"p{p}"))]

        ui.planteamiento()
        ui.statement(
            "<b>La criba de Legendre (1808)</b><br><br>"
            "Adrien-Marie Legendre (1752-1833) quiso contar cuántos primos hay hasta un número N y, "
            "en su <i>Essai sur la théorie des nombres</i>, lo hizo tachando: de la lista 1, 2, …, N "
            "se eliminan los múltiplos de 2, luego los de 3, los de 5… La criba es la de Eratóstenes, "
            "pero contar lo que queda exige no tachar dos veces el mismo número, y ahí entra la "
            f"inclusión-exclusión. Elegimos un número al azar entre 1 y N = {v['limit']}: ¿qué "
            "probabilidad hay de que sea múltiplo de alguno de los primos marcados?"
        )

        if ui.accordion_step("P2_A", "(A) Un número al azar"):
            ui.content(
                "Sea D<sub>p</sub> el suceso <i>el número elegido es múltiplo de p</i>. Calcula "
                "&#8473;(D<sub>p</sub>) con la regla de Laplace. ¿Qué suceso es D<sub>p</sub> &cap; "
                "D<sub>q</sub> cuando p y q son primos distintos?"
            )
            ui.spoiler(
                "Hay &lfloor;N&frasl;p&rfloor; múltiplos de p entre 1 y N, luego"
                "<div class='formula-box'>&#8473;(D<sub>p</sub>) = &lfloor;N&frasl;p&rfloor; &frasl; N</div>"
                "Un número es múltiplo de dos primos distintos si y solo si lo es de su producto "
                "(teorema fundamental de la aritmética), así que D<sub>p</sub> &cap; D<sub>q</sub> = "
                "D<sub>pq</sub>, y lo mismo con tres o más primos."
            )

        if ui.accordion_step("P2_B", "(B) Poincaré con suelos"):
            ui.content(
                "Escribe la probabilidad de la unión de los D<sub>p</sub> para los primos marcados. "
                "¿Por qué no basta con sumar las &#8473;(D<sub>p</sub>)? Compara en el panel de la "
                "derecha el recuento exacto con el que daría la suma sin corregir."
            )
            ui.spoiler(
                "Por la fórmula de Poincaré, con las intersecciones convertidas en múltiplos de "
                "productos:"
                "<div class='formula-box'>&#8473;(&#8899; D<sub>p</sub>) = (1&frasl;N) [ "
                "&sum;<sub>p</sub> &lfloor;N&frasl;p&rfloor; &minus; "
                "&sum;<sub>p&lt;q</sub> &lfloor;N&frasl;pq&rfloor; + "
                "&sum;<sub>p&lt;q&lt;r</sub> &lfloor;N&frasl;pqr&rfloor; &minus; &ctdot; ]</div>"
                "Los números con varios divisores marcados aparecen una vez por cada divisor en la "
                "primera suma; las restas y sumas siguientes dejan a cada uno contado exactamente una "
                "vez. Cuando N crece, &lfloor;N&frasl;m&rfloor;&frasl;N tiende a 1&frasl;m y la "
                "fórmula se convierte en 1 &minus; &prod;<sub>p</sub>(1 &minus; 1&frasl;p): en el "
                "límite, ser múltiplo de un primo no informa sobre serlo de otro."
            )

        if ui.accordion_step("P2_C", "(C) Legendre cuenta primos"):
            ui.content(
                "Si marcas todos los primos menores o iguales que &radic;N, ¿qué números sobreviven a "
                "la criba, aparte del 1? Deduce de ahí una manera de contar los primos hasta N."
            )
            ui.spoiler(
                "Sobreviven los números sin divisores primos pequeños, es decir, todos los primos entre "
                "&radic;N y N, porque un número compuesto siempre tiene un factor primo que no supera "
                "su raíz cuadrada. Si π(x) cuenta los primos hasta x, el número de supervivientes es "
                "π(N) &minus; π(&radic;N) + 1, y la fórmula de inclusión-exclusión lo calcula sin "
                "listar los primos: es la fórmula de Legendre, el primer paso de la teoría de cribas."
            )

    with col_right:
        ui.right_panel()
        if not chosen:
            ui.comment("Marca al menos un primo para cribar.")
            return
        count, naive = sieve_count(limit, chosen)
        ui.metrics([
            (f"Múltiplos de algún primo marcado: {count} de {limit}", "metric-a"),
            (f"&#8473; = {count / limit:.4f}", "metric-b"),
        ])
        ui.show(sieve_grid(dark, limit, chosen), key="fig_sieve")
        limit_value = 1 - prod(1 - 1 / p for p in chosen)
        ui.footer_bar(
            f"La suma sin corregir &sum;&lfloor;N&frasl;p&rfloor; vale {naive}, frente a los {count} "
            f"múltiplos reales: los colores cálidos marcan los números contados de más. Para N grande "
            f"la probabilidad tiende a 1 &minus; &prod;(1 &minus; 1&frasl;p) = {limit_value:.4f}."
        )


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("modifica las <u>tiradas n</u> con un dado y las <u>tiradas m</u> con dos")
        c1, c2 = st.columns(2)
        n_one = c1.slider("Tiradas n con un dado", 1, 40, v["rolls_one"], 1,
                          key=ui.wkey(PAGE, "one"))
        n_two = c2.slider("Tiradas m con dos dados", 1, 80, v["rolls_two"], 1,
                          key=ui.wkey(PAGE, "two"))

        ui.planteamiento()
        ui.statement(
            "<b>La apuesta del caballero de Méré (1654)</b><br><br>"
            "Antoine Gombaud, caballero de Méré (1607-1684), hombre de letras y jugador empedernido, "
            "llevaba años ganando tharni con una apuesta a la par (un tharni contra un tharni): sacar "
            "al menos un seis en cuatro tiradas de un dado. Cuando trasladó la idea a dos dados, al "
            "menos un doble seis en veinticuatro tiradas, empezó a perder, y planteó la cuestión a Pascal, que la discutió con Fermat en la "
            "misma correspondencia que dio origen al problema de los puntos. Aquí eres tú quien elige "
            f"el número de tiradas: n = {v['rolls_one']} con un dado y m = {v['rolls_two']} con dos."
        )

        if ui.accordion_step("P3_A", "(A) Ninguno es más fácil que al menos uno"):
            ui.content(
                "Sea A<sub>i</sub> = <i>sale un seis en la tirada i</i>. La apuesta se gana si ocurre "
                "A<sub>1</sub> &cup; &ctdot; &cup; A<sub>n</sub>. Pasa al complementario: ¿cuántos "
                "resultados, de los 6<sup>n</sup> posibles, no contienen ningún seis?"
            )
            ui.spoiler(
                "Por las leyes de De Morgan, (&#8899; A<sub>i</sub>)<sup>c</sup> = &#8898; "
                "A<sub>i</sub><sup>c</sup>: <i>al menos un seis</i> falla exactamente cuando ocurre "
                "<i>ningún seis</i>. Por el principio de multiplicación hay 5<sup>n</sup> resultados "
                "sin seises, así que la regla de Laplace y la del complementario dan"
                "<div class='formula-box'>&#8473;(al menos un seis) = 1 &minus; 5<sup>n</sup>&frasl;6<sup>n</sup> "
                "= 1 &minus; (5&frasl;6)<sup>n</sup></div>"
                "Para el doble seis con dos dados se cambia 5&frasl;6 por 35&frasl;36."
            )

        if ui.accordion_step("P3_B", "(B) Poincaré llega al mismo sitio"):
            ui.content(
                "Calcula la misma probabilidad con la fórmula de Poincaré: la intersección de k de los "
                "A<sub>i</sub> es <i>seis en k tiradas fijas</i>. ¿Reconoces la suma que aparece?"
            )
            ui.spoiler(
                "Cada intersección de orden k tiene probabilidad (1&frasl;6)<sup>k</sup> y hay C(n, k) "
                "de ellas:"
                "<div class='formula-box'>&sum;<sub>k=1</sub><sup>n</sup> (&minus;1)<sup>k+1</sup> "
                "( <sup>n</sup>&frasl;<sub>k</sub> ) (1&frasl;6)<sup>k</sup> = "
                "1 &minus; (1 &minus; 1&frasl;6)<sup>n</sup></div>"
                "por el binomio de Newton. La fórmula de Poincaré y la regla del complementario son dos "
                "caminos al mismo número, y el segundo es mucho más corto."
            )

        if ui.accordion_step("P3_C", "(C) El error del caballero"):
            ui.content(
                "De Méré razonaba por proporciones: si cuatro tiradas bastan con un dado, que tiene 6 "
                "casos, con dos dados y 36 casos harán falta 4 &middot; 36 &frasl; 6 = 24 tiradas. ¿Por "
                "qué falla el argumento? Encuentra en la figura a partir de qué n y de qué m cada "
                "apuesta pasa a ser favorable (probabilidad mayor que un medio)."
            )
            ui.spoiler(
                "La probabilidad de <i>al menos uno</i> no crece en proporción al número de tiradas, "
                "sino como 1 &minus; (1 &minus; p)<sup>n</sup>, una curva que se va doblando: la regla "
                "de tres solo es buena para n muy pequeño. Para saber desde qué n la apuesta es "
                "favorable basta resolver (5&frasl;6)<sup>n</sup> &lt; 1&frasl;2 tomando logaritmos, y "
                "lo mismo con 35&frasl;36: comprobarás que al caballero le faltaba exactamente una tirada "
                "con los dos dados."
            )

    with col_right:
        ui.right_panel()
        p_one = at_least_one(1 / 6, n_one)
        p_two = at_least_one(1 / 36, n_two)
        ui.metrics([
            (f"Un seis en {n_one} tiradas: {p_one:.4f}", "result-yes" if p_one > 0.5 else "result-no"),
            (f"Doble seis en {n_two} tiradas: {p_two:.4f}", "result-yes" if p_two > 0.5 else "result-no"),
        ])
        ui.show(mere_curves(dark, n_one, n_two), key="fig_mere")
        gain_one = 2 * p_one - 1
        gain_two = 2 * p_two - 1
        ui.footer_bar(
            f"En una apuesta a la par, cada tharni apostado rinde de media 2&#8473; &minus; 1: "
            f"{gain_one:+.4f} tharni con un dado y {gain_two:+.4f} con dos. Con un dado, la fórmula de "
            f"Poincaré da {sum((-1) ** (k + 1) * comb(n_one, k) / 6 ** k for k in range(1, n_one + 1)):.4f}, "
            "igual que el complementario."
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
        ("P1", "(I) El álbum de cromos", "P1_A"),
        ("P2", "(II) La criba de Legendre", "P2_A"),
        ("P3", "(III) La apuesta del caballero de Méré", "P3_A"),
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
