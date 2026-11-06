# C1VIC D4TA

Fichas interactivas para un primer curso de probabilidad y estadística
univariante, construidas con [Streamlit](https://streamlit.io). Cada ficha
arranca con un breve contexto histórico, plantea tres preguntas en boca de un
protagonista de la época, esconde las soluciones tras cajas difuminadas hasta
que el lector decide mirar, y acompaña el texto con una figura que responde a
los controles.

La versión en inglés de este fichero es `README.md`.

## Estructura

```
home.py          punto de entrada: descubre las fichas y enruta entre ellas
inicio.py        portada: código de sesión, dados, cuadrícula 6 x 6, herramientas
civic_ui.py      estilos, cajas de texto, spoilers, navegación y utilidades Bokeh
fichas/
  TT_KK.py       ejercicio KK del tema TT de probabilidad (TT = 01 ... 06)
  00_KK.py       herramienta KK del bloque de estadística univariante
  test_pages.py  ejecución sin navegador de todas las fichas
.streamlit/      configuración del tema y del servidor
```

Cada ficha declara una constante `TITLE` y, las de probabilidad, también un
`SYMBOL`; la portada lee los dos para dibujar su casilla. El nombre del fichero
decide la posición: `03_04.py` es la cuarta ficha del tema 3. La carpeta se
llama `fichas/` y no `pages/` a propósito: si junto al script de entrada hay
una carpeta `pages/`, Streamlit se salta el enrutador y monta su propio menú a
partir de los nombres de fichero.

## Código de sesión

La portada pide un código: cualquier palabra o combinación de letras, cifras y
símbolos (por ejemplo, el repartido a cada grupo). No importan las mayúsculas
ni los espacios de los extremos. El código fija un número r en [0, 1), y los
valores iniciales de cada problema se calculan a partir de él, con el mismo
espíritu que las hojas de problemas parametrizadas de la asignatura. Dos
lectores con códigos distintos ven datos distintos; el mismo código reproduce
siempre las mismas fichas. Una sesión nueva empieza con el código `UBU-GMAyC`;
si se borra el código, las fichas usan los valores clásicos de los enunciados.

El código viaja en la dirección como `?c=...`, de modo que una recarga o un
enlace compartido lo conservan: `https://<servidor>/t2-3?c=grupo4` abre la
ficha de Bayes del tema 2 con los datos de ese grupo.

## Puesta en marcha

```
pip install -r requirements.txt
streamlit run home.py
```

La maquetación se adapta a móviles y tabletas (una sola columna por debajo de
640 px) y sigue el tema claro u oscuro del navegador.

Para comprobar que todas las fichas se ejecutan, recorriendo todos sus
problemas con y sin código:

```
pip install pytest
pytest -q fichas/test_pages.py -k 03_
```

Cada ficha arranca su propia sesión de Streamlit, así que conviene ejecutar un
bloque cada vez (`-k 00_`, `-k 01_`, ...); `-k defaults` comprueba en unos
segundos que cualquier código de sesión da valores iniciales válidos.

## Temario

| Bloque | Contenido |
|--------|-----------|
| 1 | Orígenes de la probabilidad, axiomas de Kolmogórov, probabilidad clásica, combinatoria, inclusión-exclusión, álgebra de sucesos |
| 2 | Probabilidad condicionada, independencia, Bayes, regla del producto, fiabilidad de redes, análisis del primer paso |
| 3 | Variables aleatorias, esperanza y varianza, desigualdades de Markov y Chebyshev, modelos de Bernoulli, Poisson, esperanza condicionada |
| 4 | Variables continuas, uniforme, normal, exponencial, gamma y ji-dos, beta |
| 5 | Vectores aleatorios, transformaciones, sumas y reproductividad, covarianza, normal bidimensional, multinomial |
| 6 | Modos de convergencia, leyes de los grandes números, teorema central del límite y sus aplicaciones |
| Estadística | Tipos de muestreo, estadísticos y distribuciones muestrales, estimadores insesgados, consistentes y suficientes, máxima verosimilitud, tests de hipótesis y potencia, tamaño muestral, intervalos de confianza, ANOVA de un factor, correlación, regresión lineal simple y su validación, correlaciones espurias, modelos lineales no válidos |

## Licencia

Código: MIT (`LICENSE`). Textos y figuras: CC BY-SA 4.0 (`LICENSE-CONTENT.md`).

Autores: Adriana Ortega (AOD), Olga Valencia García (OVG), Sinuhé Perea (SPP).
Universidad de Burgos, 2026.
