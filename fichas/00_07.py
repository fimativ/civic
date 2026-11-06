#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 7: estimación por máxima verosimilitud.

La curva de log-verosimilitud de cuatro familias (Bernoulli, Poisson,
exponencial y geométrica) con su curvatura e información de Fisher, la normal
con dos parámetros (el argumento de Gauss) y la captura-recaptura de Petersen,
donde el parámetro es un entero y no se puede derivar.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span
from scipy import stats
from scipy.special import gammaln

import civic_ui as ui

TITLE = "Máxima verosimilitud"
PAGE = "00_07"

FAMILIES = {"bernoulli": "Bernoulli", "poisson": "Poisson", "exponential": "Exponencial", "geometric": "Geométrica"}
TRUE = {"bernoulli": 0.3, "poisson": 2.5, "exponential": 0.8, "geometric": 0.25}
SYMBOL = {"bernoulli": "p", "poisson": "λ", "exponential": "λ", "geometric": "p"}
MU_TRUE, SIGMA_TRUE = 10.0, 2.0


def initial_values():
    return {
        "family": ui.dchoice("poisson", list(FAMILIES), "family"),
        "n": ui.dchoice(20, [5, 20, 80, 320], "n"),
        "n_gauss": ui.dchoice(10, [3, 5, 10, 30, 100], "n_gauss"),
        "M": ui.dint(50, 20, 100, "M"),
        "c2": ui.dint(60, 20, 100, "c2"),
        "m": ui.dint(7, 1, 20, "m"),
        "seed": int(ui.r("verosimilitud") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "family": None})


# =============================================================================
# 1. CÁLCULOS
# =============================================================================

def sample(family: str, n: int, rng):
    t = TRUE[family]
    if family == "bernoulli":
        return (rng.random(n) < t).astype(float)
    if family == "poisson":
        return rng.poisson(t, n).astype(float)
    if family == "exponential":
        return rng.exponential(1 / t, n)
    return rng.geometric(t, n).astype(float)


def loglik(family: str, x: np.ndarray, th: np.ndarray) -> np.ndarray:
    n, s = len(x), x.sum()
    if family == "bernoulli":
        return s * np.log(th) + (n - s) * np.log1p(-th)
    if family == "poisson":
        return s * np.log(th) - n * th
    if family == "exponential":
        return n * np.log(th) - th * s
    return n * np.log(th) + (s - n) * np.log1p(-th)


def mle(family: str, x: np.ndarray) -> float:
    m = x.mean()
    return m if family in ("bernoulli", "poisson") else 1 / m


def fisher_info(family: str, th: float) -> float:
    return {"bernoulli": 1 / (th * (1 - th)), "poisson": 1 / th, "exponential": 1 / th ** 2,
            "geometric": 1 / (th ** 2 * (1 - th))}[family]


def grid_for(family: str):
    if family in ("bernoulli", "geometric"):
        return np.linspace(0.005, 0.995, 600)
    return np.linspace(0.02, 3 * TRUE[family], 600)


def capture_loglik(N: np.ndarray, M: int, n: int, m: int) -> np.ndarray:
    """log C(M, m) C(N − M, n − m) / C(N, n), sin el término constante."""
    return (gammaln(N - M + 1) - gammaln(N - M - n + m + 1)
            - gammaln(N + 1) + gammaln(N - n + 1))


# =============================================================================
# 2. FIGURAS
# =============================================================================

def loglik_chart(dark, family, x):
    th = grid_for(family)
    ll = loglik(family, x, th)
    ll = ll - np.nanmax(ll)
    hat = mle(family, x)
    hat_c = min(max(hat, th[0]), th[-1])
    se = 1 / np.sqrt(len(x) * fisher_info(family, hat_c))
    p = ui.new_figure(dark, height=320, x_axis_label=SYMBOL[family], y_axis_label="ℓ(θ) − ℓ(θ̂)", y_range=(-6, 0.5))
    p.line(th, ll, line_width=3, color=ui.BLUE_LINE, legend_label="log-verosimilitud")
    p.line(th, -(th - hat_c) ** 2 / (2 * se ** 2), line_width=2, color=ui.ORANGE_LINE, line_dash="dashed",
           legend_label="aproximación cuadrática")
    p.add_layout(Span(location=hat_c, dimension="height", line_color=ui.UBU_RED, line_width=2))
    p.add_layout(Span(location=TRUE[family], dimension="height", line_color=ui.GREY_LINE, line_dash="dotted", line_width=2))
    p.add_layout(Span(location=-1.92, dimension="width", line_color=ui.GREEN_LINE, line_dash="dotted"))
    return ui.style_legend(p, dark, "bottom_right")


def gauss_chart(dark, x):
    mu = np.linspace(MU_TRUE - 3.5, MU_TRUE + 3.5, 160)
    sg = np.linspace(0.5, 5.0, 160)
    M, S = np.meshgrid(mu, sg)
    n = len(x)
    ll = -n * np.log(S) - ((x[None, None, :] - M[..., None]) ** 2).sum(axis=-1) / (2 * S ** 2)
    ll = np.maximum(ll - ll.max(), -12)
    p = ui.new_figure(dark, height=340, x_axis_label="μ", y_axis_label="σ", x_range=(mu[0], mu[-1]), y_range=(sg[0], sg[-1]))
    p.grid.visible = False
    p.image(image=[ll], x=mu[0], y=sg[0], dw=mu[-1] - mu[0], dh=sg[-1] - sg[0], palette="Viridis256")
    s_hat = np.sqrt(np.mean((x - x.mean()) ** 2))
    p.scatter([x.mean()], [s_hat], size=14, marker="x", line_width=3, color="#ffffff")
    p.scatter([MU_TRUE], [SIGMA_TRUE], size=12, marker="circle", fill_alpha=0, line_width=2.5, color=ui.UBU_RED)
    return p


def capture_chart(dark, M, n, m):
    lo = M + n - m
    hi = max(lo + 50, int(6 * M * n / m))
    N = np.unique(np.linspace(lo, hi, 700).astype(int)).astype(float)
    ll = capture_loglik(N, M, n, m)
    L = np.exp(ll - ll.max())
    p = ui.new_figure(dark, height=300, x_axis_label="tamaño de la población N", y_axis_label="verosimilitud (máximo = 1)")
    p.varea(x=N, y1=0, y2=L, fill_color=ui.BLUE_LINE, fill_alpha=0.35)
    p.line(N, L, line_width=2.5, color=ui.BLUE_LINE)
    p.add_layout(Span(location=M * n / m, dimension="height", line_color=ui.UBU_RED, line_width=2, line_dash="dashed"))
    return p


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Qué parámetro explica mejor los datos?</b>")
        ui.content(
            "Una vez observada la muestra x, la función de probabilidad o de densidad conjunta se puede leer como función "
            "del parámetro: es la <b>verosimilitud</b> L(&theta;). El estimador de <b>máxima verosimilitud</b> &theta;̂ es "
            "el valor que la hace máxima, el que daba más probabilidad a lo que de hecho ocurrió. <i>¿Cómo se calcula "
            "casi siempre?</i>"
        )
        ui.formula_hidden("&ell;(&theta;) = &sum; log f(x<sub>i</sub>; &theta;), &nbsp;&nbsp; "
                          "<sup>d&ell;</sup>&frasl;<sub>d&theta;</sub>(&theta;̂) = 0")
        ui.content(
            "Se maximiza el logaritmo, que convierte el producto en suma y tiene el mismo máximo. Las tres situaciones "
            "recorren el caso de un parámetro con cuatro familias, el de dos parámetros con la normal y uno en el que la "
            "derivada no sirve porque el parámetro es un número entero."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. Un criterio absoluto (1912)</b><br>"
            "<i>Dibuja la log-verosimilitud de cuatro familias, como propuso un Ronald Fisher de veintidós años, y mide "
            "su curvatura.</i><br><br>"
            "<b>II. El argumento de Gauss (1809)</b><br>"
            "<i>Busca el máximo en el plano (&mu;, &sigma;) y descubre por qué la media aritmética lleva a la "
            "normal.</i><br><br>"
            "<b>III. Peces marcados (1896)</b><br>"
            "<i>Cuenta los peces de un lago con el método de captura-recaptura de Carl Petersen, sin derivar.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("elige la <u>familia</u> y el <u>tamaño n</u>")
        if st.session_state["family"] is None:
            st.session_state["family"] = v["family"]
        ui.choice_buttons(list(FAMILIES), "family", labels=FAMILIES, per_row=4)
        n = st.select_slider("Tamaño de la muestra", options=[5, 20, 80, 320], value=v["n"], key=ui.wkey(PAGE, "n"),
                             label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Un criterio absoluto (1912)</b><br><br>"
            "Siendo aún estudiante en Cambridge, Ronald Fisher publicó «Sobre un criterio absoluto para ajustar curvas de "
            "frecuencias», donde proponía elegir los parámetros que maximizan la probabilidad de los datos observados. "
            "Diez años después lo llamó máxima verosimilitud. Tomamos una muestra de la familia elegida y dibujamos su "
            "log-verosimilitud."
        )

        if ui.accordion_step("P1_A", "(A) Las cuatro fórmulas"):
            ui.content(
                "Escribe &ell;(&theta;) para cada familia, deriva e iguala a cero. La geométrica cuenta el número de "
                "intentos hasta el primer éxito."
            )
            ui.spoiler(
                "<table><tr><th>familia</th><th>&ell;(&theta;)</th><th>&theta;̂</th></tr>"
                "<tr><td>Bernoulli(p)</td><td>&sum;x log p + (n &minus; &sum;x) log(1 &minus; p)</td><td>x̄</td></tr>"
                "<tr><td>Poisson(&lambda;)</td><td>&sum;x log &lambda; &minus; n&lambda;</td><td>x̄</td></tr>"
                "<tr><td>Exponencial(&lambda;)</td><td>n log &lambda; &minus; &lambda;&sum;x</td><td>1/x̄</td></tr>"
                "<tr><td>Geométrica(p)</td><td>n log p + (&sum;x &minus; n) log(1 &minus; p)</td><td>1/x̄</td></tr></table>"
                "En las cuatro la segunda derivada es negativa, así que el punto crítico es un máximo."
            )

        if ui.accordion_step("P1_B", "(B) La curvatura"):
            ui.content(
                "Aumenta n y mira cómo se estrecha la curva. ¿Qué mide la curvatura en el máximo? ¿Qué relación tiene con "
                "la varianza del estimador?"
            )
            ui.spoiler(
                "Cerca del máximo, &ell; se parece a una parábola (la línea naranja) cuya curvatura es n&middot;I(&theta;), "
                "con I la <b>información de Fisher</b> de una observación. Bajo condiciones de regularidad, &theta;̂ es "
                "asintóticamente normal:"
                "<div class='formula-box'>&theta;̂ &asymp; N( &theta;, <sup>1</sup>&frasl;<sub>n I(&theta;)</sub> )</div>"
                "y alcanza en el límite la cota de Cramér-Rao. Una curva más puntiaguda significa un estimador más preciso."
            )

        if ui.accordion_step("P1_C", "(C) Un intervalo con la curva"):
            ui.content(
                "La línea verde está a 1.92 unidades por debajo del máximo. ¿Qué intervalo forman los valores de &theta; "
                "que quedan por encima?"
            )
            ui.spoiler(
                "Por el teorema de Wilks, 2(&ell;(&theta;̂) &minus; &ell;(&theta;)) es aproximadamente una ji cuadrado con un "
                "grado de libertad, cuyo cuantil 0.95 es 3.84 = 2 &times; 1.92. Los valores de &theta; por encima de la línea "
                "forman un intervalo de confianza del 95 % basado en la verosimilitud. Con n pequeño no es simétrico, y "
                "suele funcionar mejor que &theta;̂ &plusmn; 1.96 errores típicos."
            )

    with col_right:
        ui.right_panel()
        family = st.session_state["family"]
        rng = np.random.default_rng(v["seed"] + n * 5 + len(family))
        x = sample(family, n, rng)
        hat = mle(family, x)
        se = 1 / np.sqrt(n * fisher_info(family, min(max(hat, 0.005), 0.995) if family in ("bernoulli", "geometric") else hat))
        ui.metrics([(f"{SYMBOL[family]} real: {TRUE[family]}", "metric-c"),
                    (f"Máximo verosímil: {hat:.3f}", "metric-a"), (f"Error típico: {se:.3f}", "metric-b")])
        ui.show(loglik_chart(dark, family, x), key="fig_loglik")
        ui.footer_bar(f"Muestra de {n} datos de una {FAMILIES[family].lower()}. Línea roja: el máximo; punteada gris: el valor "
                      "real; naranja: la parábola con curvatura n&middot;I(&theta;̂).")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>número de observaciones n</u>")
        n = st.select_slider("Observaciones", options=[3, 5, 10, 30, 100], value=v["n_gauss"],
                             key=ui.wkey(PAGE, "n_gauss"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El argumento de Gauss (1809)</b><br><br>"
            "En su «Teoría del movimiento de los cuerpos celestes», Carl Friedrich Gauss buscó la ley de los errores de "
            "observación. Partió de que la media aritmética de varias medidas debía ser el valor más probable, y dedujo "
            "que la ley tenía que ser la normal. Ahora vamos al revés: con medidas normales de media &mu; y desviación "
            "&sigma;, buscamos el máximo de la verosimilitud en el plano."
        )

        if ui.accordion_step("P2_A", "(A) Las dos derivadas"):
            ui.content("Escribe &ell;(&mu;, &sigma;), iguala a cero sus dos derivadas parciales y resuelve.")
            ui.spoiler(
                "&ell;(&mu;, &sigma;) = &minus;n log &sigma; &minus; &sum;(x<sub>i</sub> &minus; &mu;)<sup>2</sup>/(2&sigma;<sup>2</sup>) "
                "+ cte. La derivada en &mu; se anula en &mu;̂ = x̄, sea cual sea &sigma;; sustituyendo, la de &sigma; da"
                "<div class='formula-box'>&sigma;̂<sup>2</sup> = <sup>1</sup>&frasl;<sub>n</sub> &sum;(x<sub>i</sub> &minus; x̄)<sup>2</sup></div>"
                "con divisor n: el máximo verosímil de la varianza es sesgado, aunque consistente."
            )

        if ui.accordion_step("P2_B", "(B) La forma de la colina"):
            ui.content(
                "El aspa blanca es el máximo y el círculo rojo el valor real. ¿Por qué la colina es asimétrica en "
                "&sigma;? ¿Qué pasa con n = 3?"
            )
            ui.spoiler(
                "Hacia &sigma; pequeño la verosimilitud cae muy deprisa, porque los datos se vuelven imposibles de explicar; "
                "hacia &sigma; grande cae despacio. Con n = 3 la colina es enorme y el máximo puede quedar lejos del valor "
                "real. Al crecer n, la colina se estrecha y se vuelve simétrica, como predice la normalidad asintótica."
            )

        if ui.accordion_step("P2_C", "(C) La propiedad de invariancia"):
            ui.content(
                "¿Cuál es el máximo verosímil de &sigma;? ¿Y de la probabilidad de que una medida pase de 12?"
            )
            ui.spoiler(
                "Si &theta;̂ maximiza la verosimilitud, g(&theta;̂) es el máximo verosímil de g(&theta;): basta con sustituir. "
                "Así &sigma;̂ = &radic;&sigma;̂<sup>2</sup> y &#8473;̂(X &gt; 12) = 1 &minus; &Phi;((12 &minus; x̄)/&sigma;̂). La "
                "insesgadez no se conserva al transformar, pero la máxima verosimilitud sí."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + 3 * n)
        x = rng.normal(MU_TRUE, SIGMA_TRUE, n)
        s_hat = np.sqrt(np.mean((x - x.mean()) ** 2))
        ui.metrics([(f"&mu;̂ = {x.mean():.2f}", "metric-a"), (f"&sigma;̂ = {s_hat:.2f}", "metric-b"),
                    (f"&#8473;̂(X &gt; 12) = {stats.norm.sf(12, x.mean(), s_hat):.3f}", "metric-c")])
        ui.show(gauss_chart(dark, x), key="fig_gauss")
        ui.footer_bar(f"Log-verosimilitud de {n} medidas con &mu; = {MU_TRUE:.0f} y &sigma; = {SIGMA_TRUE:.0f}: el amarillo es la "
                      f"cima. El valor real de &#8473;(X &gt; 12) es {stats.norm.sf(12, MU_TRUE, SIGMA_TRUE):.3f}.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.try_it("cambia los <u>marcados</u>, la <u>segunda captura</u> y los <u>recapturados</u>")
        M = st.slider("Peces marcados en la primera captura M", 10, 150, v["M"], 1, key=ui.wkey(PAGE, "M"))
        c2 = st.slider("Peces de la segunda captura n", 10, 150, v["c2"], 1, key=ui.wkey(PAGE, "c2"))
        m = st.slider("Marcados en la segunda captura m", 1, 30, v["m"], 1, key=ui.wkey(PAGE, "m"))

        ui.planteamiento()
        ui.statement(
            "<b>Peces marcados (1896)</b><br><br>"
            "El biólogo danés Carl Petersen estudiaba las platijas de los fiordos. Se capturan M peces, se marcan y se "
            "devuelven al agua. Días después se pescan n y se cuentan los m que llevan marca. El número de marcados en la "
            "segunda captura es hipergeométrico, y queremos el máximo verosímil del tamaño N de la población."
        )

        if ui.accordion_step("P3_A", "(A) Sin derivadas"):
            ui.content(
                "N es un número entero. En lugar de derivar, estudia el cociente L(N)/L(N &minus; 1). ¿Cuándo es mayor que 1?"
            )
            ui.spoiler(
                "<div class='formula-box'><sup>L(N)</sup>&frasl;<sub>L(N &minus; 1)</sub> = "
                "<sup>(N &minus; M)(N &minus; n)</sup>&frasl;<sub>N(N &minus; M &minus; n + m)</sub></div>"
                "Es mayor o igual que 1 exactamente cuando N &le; Mn/m. La verosimilitud crece hasta ahí y luego decrece: el "
                "máximo es el mayor entero que no pasa de Mn/m (si Mn/m es entero, empatan él y el anterior)."
            )

        if ui.accordion_step("P3_B", "(B) La intuición"):
            ui.content("¿Por qué tiene sentido el estimador de Lincoln-Petersen N̂ &asymp; Mn/m?")
            ui.spoiler(
                "La proporción de marcados en la segunda captura, m/n, estima la proporción en el lago, M/N. Igualando y "
                "despejando sale N &asymp; Mn/m. Pierre-Simon Laplace usó la misma proporción en 1802 para estimar la "
                "población de Francia, con los nacimientos registrados haciendo el papel de peces marcados."
            )

        if ui.accordion_step("P3_C", "(C) Si no se recaptura ninguno"):
            ui.content("Baja m hasta 1. ¿Qué le pasa a la verosimilitud? ¿Qué ocurriría con m = 0?")
            ui.spoiler(
                "Con m pequeño la verosimilitud es muy plana a la derecha: muchos tamaños explican casi igual de bien los "
                "datos. Con m = 0 crece siempre con N, sin alcanzar nunca un máximo, y el máximo verosímil es infinito. Por eso se usa a menudo la "
                "corrección de Chapman, (M + 1)(n + 1)/(m + 1) &minus; 1, que siempre es finita y tiene mucho menos "
                "sesgo."
            )

    with col_right:
        ui.right_panel()
        m = min(m, M, c2)
        hat = int(np.floor(M * c2 / m))
        chapman = (M + 1) * (c2 + 1) / (m + 1) - 1
        ui.metrics([(f"Máximo verosímil: {ui.fmt_int(hat)}", "metric-a"), (f"Chapman: {chapman:.0f}", "metric-b"),
                    (f"Mínimo posible: {M + c2 - m}", "metric-c")])
        ui.show(capture_chart(dark, M, c2, m), key="fig_capture")
        ui.footer_bar(f"Verosimilitud de cada tamaño N con M = {M}, n = {c2} y m = {m}. La línea roja discontinua es Mn/m = "
                      f"{M * c2 / m:.1f}. La población no puede tener menos de M + n &minus; m peces distintos.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) Un criterio absoluto", "P1_A"),
        ("P2", "(II) El argumento de Gauss", "P2_A"),
        ("P3", "(III) Peces marcados", "P3_A"),
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
