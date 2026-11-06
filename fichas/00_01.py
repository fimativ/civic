#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Estadística, herramienta 1: tipos de muestreo.

Una población de 2000 hogares repartidos en 20 barrios, urbanos y rurales,
sobre la que se comparan el muestreo aleatorio simple, el estratificado (con
reparto proporcional y de Neyman), por conglomerados, por etapas y por cuotas.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
from bokeh.models import Span

import civic_ui as ui

TITLE = "Tipos de muestreo"
PAGE = "00_01"

BARRIOS = 20
URBANOS = 6
HOGARES = 100
REPS = 1500
DESIGNS = {"cluster": "Conglomerados", "stage": "Dos etapas", "quota": "Cuotas"}


def initial_values():
    return {
        "n": ui.dchoice(100, [50, 100, 200], "n"),
        "n_strat": ui.dchoice(100, [60, 100, 150], "n_strat"),
        "design": ui.dchoice("cluster", list(DESIGNS), "design"),
        "seed": int(ui.r("muestreo") * 1e9),
    }


def init_session_state():
    ui.init_state({"page": "INTRO", "open_part": "P1_A", "design": None})


# =============================================================================
# 1. LA POBLACIÓN
# =============================================================================

@st.cache_data(show_spinner=False)
def population(seed: int):
    """Renta (en tharni) de cada hogar, su barrio y su estrato (1 urbano, 0 rural)."""
    rng = np.random.default_rng(seed)
    barrio = np.repeat(np.arange(BARRIOS), HOGARES)
    urbano = (barrio < URBANOS).astype(int)
    media_barrio = np.where(np.arange(BARRIOS) < URBANOS, rng.normal(60, 15, BARRIOS), rng.normal(35, 6, BARRIOS))
    ruido = np.where(urbano == 1, rng.normal(0, 25, barrio.size), rng.normal(0, 9, barrio.size))
    renta = np.clip(media_barrio[barrio] + ruido, 3, None)
    return renta, barrio, urbano


def strata_stats(renta, urbano):
    out = []
    for h in (1, 0):
        y = renta[urbano == h]
        out.append((len(y), y.mean(), y.std(ddof=1)))
    return out


def srs_means(renta, n, reps, rng):
    idx = np.argsort(rng.random((reps, renta.size)), axis=1)[:, :n]
    return renta[idx].mean(axis=1)


def allocation(stats_, n, kind):
    N = np.array([s[0] for s in stats_], dtype=float)
    S = np.array([s[2] for s in stats_])
    w = N * S if kind == "neyman" else N
    alloc = np.maximum(2, np.round(n * w / w.sum())).astype(int)
    alloc[-1] = max(2, n - alloc[:-1].sum())
    return alloc


def stratified_means(renta, urbano, alloc, reps, rng):
    est = np.zeros(reps)
    for h, n_h in zip((1, 0), alloc):
        y = renta[urbano == h]
        W = len(y) / renta.size
        idx = np.argsort(rng.random((reps, len(y))), axis=1)[:, :n_h]
        est += W * y[idx].mean(axis=1)
    return est


def design_means(design, renta, barrio, urbano, reps, rng):
    by_barrio = renta.reshape(BARRIOS, HOGARES)
    if design == "cluster":            # un barrio entero, elegido al azar
        return by_barrio.mean(axis=1)[rng.integers(BARRIOS, size=reps)]
    if design == "stage":              # 5 barrios al azar y 20 hogares al azar en cada uno
        ks = np.argsort(rng.random((reps, BARRIOS)), axis=1)[:, :5]
        idx = np.argsort(rng.random((reps, 5, HOGARES)), axis=2)[:, :, :20]
        return by_barrio[ks[:, :, None], idx].mean(axis=(1, 2))
    # Cuotas: 30 urbanos y 70 rurales, pero el entrevistador prefiere los hogares más acomodados.
    # Muestreo ponderado sin reemplazamiento con claves log(u)/w (Efraimidis y Spirakis).
    out = np.zeros(reps)
    for h, quota in ((1, 30), (0, 70)):
        y = renta[urbano == h]
        keys = np.log(rng.random((reps, len(y)))) / np.exp(0.025 * y)
        picks = np.argsort(-keys, axis=1)[:, :quota]
        out += (quota / 100) * y[picks].mean(axis=1)
    return out


# =============================================================================
# 2. FIGURAS
# =============================================================================

def map_chart(dark, renta, barrio, sample_idx=None):
    xs = (barrio % 5) * 10 + (np.arange(renta.size) % 10)
    ys = (barrio // 5) * 10 + ((np.arange(renta.size) // 10) % 10)
    p = ui.new_figure(dark, height=300, x_range=(-1, 50), y_range=(-1, 40), match_aspect=True)
    p.grid.visible = False
    p.axis.visible = False
    shade = np.clip((renta - 5) / 110, 0, 1)
    colours = [f"rgb({int(40 + 180 * s)}, {int(90 + 60 * (1 - s))}, {int(200 - 150 * s)})" for s in shade]
    p.rect(x=xs, y=ys, width=0.9, height=0.9, fill_color=colours, line_color=None, alpha=0.75)
    for k in range(BARRIOS):
        x0, y0 = (k % 5) * 10 - 0.5, (k // 5) * 10 - 0.5
        p.quad(left=x0, right=x0 + 10, bottom=y0, top=y0 + 10, fill_alpha=0,
               line_color=ui.UBU_RED if k < URBANOS else ui.GREY_LINE, line_width=2.5 if k < URBANOS else 1)
    if sample_idx is not None:
        p.scatter(xs[sample_idx], ys[sample_idx], size=7, marker="x", color="#000000" if not dark else "#ffffff",
                  line_width=2)
    return p


def hist_chart(dark, series, truth):
    allv = np.concatenate([s[1] for s in series])
    half = max(8.0, np.percentile(np.abs(allv - truth), 99.5) * 1.1)
    lo, hi = truth - half, truth + half
    edges = np.linspace(lo, hi, 61)
    p = ui.new_figure(dark, height=300, x_axis_label="media muestral de la renta (tharni)", y_axis_label="densidad",
                      x_range=(lo, hi))
    palette = [ui.GREY_LINE, ui.BLUE_LINE, ui.GREEN_LINE, ui.ORANGE_LINE]
    for (label, vals), colour in zip(series, palette):
        h, _ = np.histogram(vals, bins=edges)
        centres = (edges[:-1] + edges[1:]) / 2
        p.line(centres, h / (len(vals) * (edges[1] - edges[0])), line_width=3, color=colour, legend_label=label)
    p.add_layout(Span(location=truth, dimension="height", line_color=ui.UBU_RED, line_width=2))
    return ui.style_legend(p, dark, "top_left")


# =============================================================================
# 3. PÁGINAS DE CONTENIDO
# =============================================================================

def render_intro():
    col_left, col_right = ui.two_columns()

    with col_left:
        ui.left_panel()
        ui.statement("<b>¿Cómo se elige a quién preguntar?</b>")
        ui.content(
            "La estadística trabaja con una <b>muestra</b> para conocer una <b>población</b>. Todo el edificio de los "
            "temas de probabilidad (esperanzas, varianzas, teoremas límite) solo se puede aplicar si la muestra se "
            "elige con un mecanismo aleatorio conocido. El más sencillo es el <b>muestreo aleatorio simple</b>: todos "
            "los subconjuntos de tamaño n tienen la misma probabilidad de ser elegidos. <i>¿Cuántos hay, y con qué "
            "probabilidad entra en la muestra cada individuo?</i>"
        )
        ui.formula_hidden("C(N, n) muestras posibles; &nbsp; &#8473;(el individuo i está en la muestra) = n/N")
        ui.content(
            "A partir de ahí hay variantes que aprovechan lo que se sabe de la población: dividirla en <b>estratos</b> "
            "homogéneos, elegir grupos enteros o <b>conglomerados</b>, hacerlo en varias <b>etapas</b>&hellip; y una "
            "práctica muy extendida que no es aleatoria, el muestreo por <b>cuotas</b>. Las tres situaciones de esta "
            "herramienta usan la misma población: los 2000 hogares de una comarca imaginaria, en 20 barrios de 100, seis "
            "urbanos y catorce rurales, con su renta mensual en tharni."
        )

    with col_right:
        ui.right_panel()
        ui.section("Ahora es tu turno")
        ui.content(
            "<b>I. El método representativo (1895)</b><br>"
            "<i>Convence con Anders Kiær a un congreso de estadísticos de que no hace falta preguntar a todo el "
            "mundo.</i><br><br>"
            "<b>II. Los estratos de Neyman (1934)</b><br>"
            "<i>Reparte la muestra entre barrios ricos y pobres como propuso Jerzy Neyman, y gana precisión sin "
            "coste.</i><br><br>"
            "<b>III. Dewey derrota a Truman (1948)</b><br>"
            "<i>Barrios enteros, muestras en dos etapas y entrevistadores con cuotas: cuál ahorra, cuál pierde "
            "precisión y cuál engaña.</i>"
        )


def render_problem_1(dark, v):
    col_left, col_right = ui.two_columns()
    renta, barrio, urbano = population(v["seed"])

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra n</u>")
        n = st.select_slider("Hogares encuestados n", options=[10, 25, 50, 100, 200, 500, 1000], value=v["n"],
                             key=ui.wkey(PAGE, "n"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>El método representativo (1895)</b><br><br>"
            "En el congreso del Instituto Internacional de Estadística de Berna, el director de estadística de "
            "Noruega, Anders Kiær, defendió algo que escandalizó a muchos: se puede conocer una población preguntando "
            "solo a una parte bien elegida. La discusión duró décadas. Queremos conocer la renta media de la comarca "
            "con n hogares elegidos por muestreo aleatorio simple, sin reemplazamiento."
        )

        if ui.accordion_step("P1_A", "(A) Una muestra, una estimación"):
            ui.content(
                "La media de la muestra cambia de una muestra a otra. ¿Cuál es su esperanza? ¿Necesita la estimación "
                "que la muestra se parezca a la población en todo?"
            )
            ui.spoiler(
                "Cada hogar entra en la muestra con probabilidad n/N, así que, por la linealidad de la esperanza, la "
                "esperanza de la media muestral es la media de la población: el estimador es insesgado, con indicatrices "
                "como en la Primitiva. No hace falta que la muestra sea una maqueta perfecta de la comarca: basta con "
                "que el azar decida, para que las propiedades de la media muestral se puedan calcular."
            )

        if ui.accordion_step("P1_B", "(B) La precisión"):
            ui.content(
                "Calcula la varianza de la media muestral sin reemplazamiento. ¿Qué papel juega el factor de corrección "
                "por población finita que viste con la hipergeométrica?"
            )
            ui.spoiler(
                "<div class='formula-box'>&#120141;(ȳ) = <sup>S<sup>2</sup></sup>&frasl;<sub>n</sub>&middot;(1 &minus; <sup>n</sup>&frasl;<sub>N</sub>)</div>"
                "donde S<sup>2</sup> es la cuasivarianza de la población (con divisor N &minus; 1). La precisión depende sobre todo de n, no de N: con "
                "muestras pequeñas respecto a la población, el factor 1 &minus; n/N es casi 1. Por eso una encuesta de mil "
                "personas sirve igual para un país de diez millones que para uno de trescientos millones."
            )

        if ui.accordion_step("P1_C", "(C) Lo que cuesta"):
            ui.content(
                "Mira el mapa: la muestra está desperdigada por todos los barrios. ¿Qué problema práctico tiene? ¿Qué "
                "información sobre la comarca no aprovecha?"
            )
            ui.spoiler(
                "Visitar hogares sueltos por toda la comarca es caro, y el muestreo simple no usa nada de lo que ya se "
                "sabe: que los barrios urbanos son más ricos y más desiguales que los rurales. Las dos situaciones "
                "siguientes aprovechan esa información, una para ganar precisión y otra para abaratar el trabajo de "
                "campo."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + n)
        idx = rng.choice(renta.size, n, replace=False)
        means = srs_means(renta, n, REPS, rng)
        S2 = renta.var(ddof=1)
        se = np.sqrt(S2 / n * (1 - n / renta.size))
        ui.metrics([(f"Media real: {renta.mean():.2f}", "metric-c"), (f"Esta muestra: {renta[idx].mean():.2f}", "metric-a"),
                    (f"Error típico: {se:.2f}", "metric-b")])
        ui.show(map_chart(dark, renta, barrio, idx), key="fig_srs_map")
        ui.show(hist_chart(dark, [("muestreo aleatorio simple", means)], renta.mean()), key="fig_srs_hist")
        ui.footer_bar(f"Mapa: cada cuadrado es un hogar, más cálido cuanto más rico; borde rojo, barrios urbanos; cruces, "
                      f"la muestra. Abajo, {REPS} medias muestrales: su desviación es {means.std():.2f}, frente a {se:.2f} "
                      "de la fórmula.")


def render_problem_2(dark, v):
    col_left, col_right = ui.two_columns()
    renta, barrio, urbano = population(v["seed"])
    stats_ = strata_stats(renta, urbano)

    with col_left:
        ui.left_panel()
        ui.try_it("cambia el <u>tamaño de la muestra</u>")
        n = st.select_slider("Hogares encuestados", options=[40, 60, 100, 150, 250], value=v["n_strat"],
                             key=ui.wkey(PAGE, "n_strat"), label_visibility="collapsed")

        ui.planteamiento()
        ui.statement(
            "<b>Los estratos de Neyman (1934)</b><br><br>"
            "En 1934 Jerzy Neyman analizó una muestra del censo italiano que Corrado Gini y Luigi Galvani habían "
            "elegido a mano, escogiendo distritos cuyas medias se parecieran a las de todo el país. Las estimaciones "
            "eran malas. Neyman mostró que había que elegir al azar, pero dentro de grupos homogéneos, los "
            "<b>estratos</b>, y explicó cómo repartir la muestra entre ellos. Nuestros estratos son el urbano y el rural."
        )
        rows = "".join(f"<tr><td>{name}</td><td>{N}</td><td>{m:.1f}</td><td>{s:.1f}</td></tr>"
                       for name, (N, m, s) in zip(("urbano", "rural"), stats_))
        ui.content("<table><tr><th>estrato</th><th>hogares</th><th>media</th><th>desviación</th></tr>" + rows + "</table>")

        if ui.accordion_step("P2_A", "(A) El estimador estratificado"):
            ui.content(
                "Se toma una muestra aleatoria simple dentro de cada estrato. ¿Cómo se combinan las dos medias para "
                "estimar la media de la comarca? ¿Cuál es su varianza?"
            )
            ui.spoiler(
                "Se pondera cada media por el peso W<sub>h</sub> = N<sub>h</sub>/N de su estrato. Como las muestras son "
                "independientes, las varianzas se suman (despreciando la corrección por población finita):"
                "<div class='formula-box'>ȳ<sub>st</sub> = &sum; W<sub>h</sub>ȳ<sub>h</sub> &nbsp;&nbsp; &#120141;(ȳ<sub>st</sub>) = "
                "&sum; W<sub>h</sub><sup>2</sup><sup>S<sub>h</sub><sup>2</sup></sup>&frasl;<sub>n<sub>h</sub></sub></div>"
                "La variación entre estratos desaparece de la fórmula: solo queda la de dentro de cada uno."
            )

        if ui.accordion_step("P2_B", "(B) El reparto de Neyman"):
            ui.content(
                "Con n fijo, ¿cuántos hogares conviene encuestar en cada estrato? Minimiza la varianza con la restricción "
                "&sum; n<sub>h</sub> = n."
            )
            ui.spoiler(
                "Por multiplicadores de Lagrange, o por la desigualdad de Cauchy-Schwarz:"
                "<div class='formula-box'>n<sub>h</sub> &prop; N<sub>h</sub>&middot;S<sub>h</sub></div>"
                "Se encuesta más donde hay más hogares y donde son más distintos entre sí. Aquí el estrato urbano, "
                "pequeño pero muy desigual, recibe muchos más hogares de los que le tocarían en proporción a su tamaño."
            )

        if ui.accordion_step("P2_C", "(C) Comparar los tres diseños"):
            ui.content(
                "Compara a la derecha las distribuciones de la media con el muestreo simple, el estratificado proporcional "
                "y el de Neyman. ¿Cuál gana, y por qué el proporcional nunca puede perder contra el simple?"
            )
            ui.spoiler(
                "El estratificado proporcional elimina la parte de la varianza debida a las diferencias entre las medias "
                "de los estratos, así que no puede ser peor que el simple. El de Neyman además reparte la muestra "
                "donde más rinde, y es el más preciso de los tres. La lección contra Gini y Galvani: el conocimiento "
                "previo se usa para estratificar, no para elegir a mano."
            )

    with col_right:
        ui.right_panel()
        rng = np.random.default_rng(v["seed"] + 7 * n)
        prop = allocation(stats_, n, "prop")
        ney = allocation(stats_, n, "neyman")
        srs = srs_means(renta, n, REPS, rng)
        st_prop = stratified_means(renta, urbano, prop, REPS, rng)
        st_ney = stratified_means(renta, urbano, ney, REPS, rng)
        ui.metrics([(f"Simple: &sigma; = {srs.std():.2f}", "metric-c"),
                    (f"Proporcional {prop[0]}+{prop[1]}: &sigma; = {st_prop.std():.2f}", "metric-a"),
                    (f"Neyman {ney[0]}+{ney[1]}: &sigma; = {st_ney.std():.2f}", "metric-b")])
        ui.show(hist_chart(dark, [("simple", srs), ("estratificado proporcional", st_prop), ("Neyman", st_ney)],
                           renta.mean()), key="fig_strata")
        ui.footer_bar(f"Con {n} hogares, el reparto proporcional encuesta {prop[0]} urbanos y {prop[1]} rurales; el de Neyman, "
                      f"{ney[0]} y {ney[1]}. Para igualar la precisión de Neyman, el muestreo simple necesitaría unos "
                      f"{n * (srs.std() / st_ney.std()) ** 2:.0f} hogares.")


def render_problem_3(dark, v):
    col_left, col_right = ui.two_columns()
    renta, barrio, urbano = population(v["seed"])

    with col_left:
        ui.left_panel()
        ui.try_it("elige el <u>diseño</u>, siempre con 100 hogares")
        if st.session_state["design"] is None:
            st.session_state["design"] = v["design"]
        ui.choice_buttons(list(DESIGNS), "design", labels=DESIGNS, per_row=3)

        ui.planteamiento()
        ui.statement(
            "<b>Dewey derrota a Truman (1948)</b><br><br>"
            "En las elecciones presidenciales de 1948 todas las encuestas daban como ganador a Thomas Dewey, y un "
            "periódico de Chicago llegó a titular su victoria antes del recuento. Ganó Harry Truman. Las encuestas usaban "
            "<b>cuotas</b>: cada entrevistador debía encontrar tantas personas de cada sexo, edad y clase, pero elegía a "
            "quién. Comparamos tres diseños baratos con 100 hogares: un barrio entero (<b>conglomerados</b>), cinco "
            "barrios al azar y veinte hogares al azar en cada uno (<b>dos etapas</b>), y cuotas de 30 urbanos y 70 "
            "rurales elegidos por el entrevistador."
        )

        if ui.accordion_step("P3_A", "(A) Conglomerados"):
            ui.content(
                "Encuestar un barrio entero ahorra desplazamientos. ¿Por qué pierde tanta precisión, si son 100 hogares "
                "igual que en el muestreo simple?"
            )
            ui.spoiler(
                "Los hogares de un mismo barrio se parecen entre sí, así que cien vecinos aportan mucha menos "
                "información que cien hogares independientes. El <b>efecto del diseño</b> mide la pérdida: con m hogares "
                "por conglomerado y una correlación &rho; entre vecinos, la varianza se multiplica por 1 + (m &minus; 1)&rho;. "
                "Con m = 100, una correlación pequeña ya es devastadora."
            )

        if ui.accordion_step("P3_B", "(B) Dos etapas"):
            ui.content("¿Qué gana el diseño en dos etapas respecto al de un solo barrio? ¿Y respecto al muestreo simple?")
            ui.spoiler(
                "Repartir la muestra en varios barrios reduce m y con él el efecto del diseño: se acerca al muestreo "
                "simple sin perder del todo el ahorro de concentrar el trabajo. Las encuestas nacionales reales son casi "
                "siempre así: municipios, después secciones censales, después hogares. Sigue siendo insesgado, porque en "
                "cada etapa decide el azar."
            )

        if ui.accordion_step("P3_C", "(C) Cuotas"):
            ui.content(
                "Las cuotas reproducen exactamente la proporción de urbanos y rurales. ¿Por qué el histograma está "
                "desplazado de la línea roja? ¿Se arregla aumentando la muestra?"
            )
            ui.spoiler(
                "Dentro de cada cuota elige el entrevistador, y tiende a los hogares más accesibles, que aquí son los más "
                "ricos. El estimador tiene un <b>sesgo</b> que no depende del tamaño de la muestra: con más entrevistas el "
                "histograma se estrecha, pero alrededor de un valor equivocado. Eso le pasó a la encuesta de 1948. Una "
                "muestra que se parece a la población en las variables controladas puede ser muy distinta en las demás."
            )

    with col_right:
        ui.right_panel()
        design = st.session_state["design"]
        rng = np.random.default_rng(v["seed"] + 13)
        means = design_means(design, renta, barrio, urbano, REPS, rng)
        srs = srs_means(renta, 100, REPS, rng)
        deff = means.var() / srs.var()
        ui.metrics([(f"Sesgo: {means.mean() - renta.mean():+.2f}", "result-no" if abs(means.mean() - renta.mean()) > 1 else "metric-c"),
                    (f"&sigma;: {means.std():.2f}", "metric-a"), (f"Efecto del diseño: {deff:.1f}", "metric-b")])
        ui.show(hist_chart(dark, [("muestreo simple", srs), (DESIGNS[design].lower(), means)], renta.mean()),
                key="fig_designs")
        if design == "quota":
            ecm = np.mean((means - renta.mean()) ** 2)
            ui.footer_bar(f"Las cuotas dan poca dispersión, pero alrededor de un valor equivocado: el error cuadrático medio es "
                          f"{ecm:.1f}, frente a {srs.var():.1f} del muestreo simple. El efecto del diseño solo mira la "
                          "varianza y aquí engaña.")
        else:
            ui.footer_bar(f"{DESIGNS[design]} frente a muestreo simple, ambos con 100 hogares. Un efecto del diseño de "
                          f"{deff:.1f} significa que esos 100 hogares valen lo que {100 / deff:.0f} elegidos al azar.")


# =============================================================================
# 4. APLICACIÓN PRINCIPAL
# =============================================================================

def main():
    init_session_state()
    dark = ui.page_setup(TITLE)
    v = initial_values()

    current = ui.nav_bar([
        ("INTRO", "Introducción", None),
        ("P1", "(I) El método representativo", "P1_A"),
        ("P2", "(II) Los estratos de Neyman", "P2_A"),
        ("P3", "(III) Dewey derrota a Truman", "P3_A"),
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
