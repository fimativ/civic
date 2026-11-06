# C1VIC D4TA

Interactive worksheets for a first course in probability and univariate
statistics, built with [Streamlit](https://streamlit.io). Each worksheet opens
with a short historical setting, poses three questions in the voice of a
protagonist of the time, hides its solutions behind blurred boxes until the
reader decides to look, and pairs the text with a live figure that reacts to
the controls.

The Spanish version of this file is `README.es.md`.

## Structure

```
home.py          entry point: discovers the worksheets and routes between them
inicio.py        landing page: session code, dice, 6 x 6 grid, statistics tools
civic_ui.py      shared styles, text boxes, spoilers, navigation, Bokeh helpers
fichas/
  TT_KK.py       exercise KK of probability topic TT (TT = 01 ... 06)
  00_KK.py       tool KK of the univariate statistics block
  test_pages.py  headless run of every worksheet
.streamlit/      theme and server configuration
```

Every worksheet declares a `TITLE` constant, and the probability ones a
`SYMBOL` too; the landing page reads both to draw its cell in the grid. File
names decide the position: `03_04.py` is the fourth worksheet of topic 3. The
folder is called `fichas/` rather than `pages/` on purpose: when a `pages/`
folder sits next to the entry script, Streamlit skips the router and builds
its own menu from the file names.

## Session code

The landing page asks for a code: any word or combination of letters, digits
and symbols (for instance the one handed out to a group). Case and surrounding
spaces are ignored. The code fixes a number r in [0, 1), and the initial values
of every problem are computed from it, in the same spirit as the parametrised
problem sheets of the course. Two readers with different codes see different
data; the same code always reproduces the same worksheets. A new session
starts with the code `UBU-GMAyC`; if the code is cleared, the worksheets use the
classical values of the problem statements.

The code travels in the address as `?c=...`, so a reload or a shared link
keeps it: `https://<server>/t2-3?c=grupo4` opens the Bayes worksheet of topic 2
with the data of that group.

## Running it

```
pip install -r requirements.txt
streamlit run home.py
```

The layout adapts to phones and tablets (single column below 640 px) and
follows the light or dark theme of the browser.

To check that every worksheet runs, clicking through all its problems with
and without a code:

```
pip install pytest
pytest -q fichas/test_pages.py -k 03_
```

Each worksheet starts its own Streamlit session, so it is better to run one
block at a time (`-k 00_`, `-k 01_`, ...); `-k defaults` checks in a few
seconds that every session code gives valid initial values.

## Topics

| Block | Content |
|-------|---------|
| 1 | Origins of probability, Kolmogorov axioms, classical probability, counting, inclusion-exclusion, algebra of events |
| 2 | Conditional probability, independence, Bayes, product rule, reliability of networks, first-step analysis |
| 3 | Random variables, expectation and variance, Markov and Chebyshev inequalities, Bernoulli models, Poisson, conditional expectation |
| 4 | Continuous random variables, uniform, normal, exponential, gamma and chi-squared, beta |
| 5 | Random vectors, transformations, sums and reproductive families, covariance, bivariate normal, multinomial |
| 6 | Modes of convergence, laws of large numbers, central limit theorem and its applications |
| Statistics | Sampling designs, statistics and sampling distributions, unbiased, consistent and sufficient estimators, maximum likelihood, hypothesis tests and power, sample size, confidence intervals, one-way ANOVA, correlation, simple linear regression and its validation, spurious correlations, invalid linear models |

## Licence

Code: MIT (`LICENSE`). Texts and figures: CC BY-SA 4.0 (`LICENSE-CONTENT.md`).

Authors: Adriana Ortega (AOD), Olga Valencia García (OVG), Sinuhé Perea (SPP).
Universidad de Burgos, 2026.
