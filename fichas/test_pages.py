#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Recorre cada ficha sin navegador y pulsa todos sus botones de navegación.

    pip install pytest
    pytest -q fichas/test_pages.py -k 03_

Las figuras de Bokeh se serializan como lo haría el componente, de modo que un
error al construir una gráfica también hace fallar la prueba.
"""

from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

import pytest
from bokeh.embed import json_item

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# El componente necesita el servidor de Streamlit; aquí basta con serializar la figura.
_fake = types.ModuleType("streamlit_bokeh")
_fake.streamlit_bokeh = lambda fig, **kwargs: json_item(fig)
sys.modules["streamlit_bokeh"] = _fake

from streamlit.testing.v1 import AppTest  # noqa: E402

SHEETS = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "fichas").glob("[0-9][0-9]_*.py"))
CODES = [None, "Ubu7", "#árbol 2!"]
ACTION_PREFIXES = ("nav_", "acc_", "ch_")


def _assert_clean(at, where):
    assert not at.exception, f"{where}: {at.exception[0].value}"
    warnings = [w.value for w in at.warning]
    assert not warnings, f"{where}: {warnings}"


def _keys(at, prefixes):
    return [b.key for b in at.button if b.key and b.key.startswith(prefixes) and not b.disabled]


def _fresh(sheet, code):
    at = AppTest.from_file(str(ROOT / sheet), default_timeout=60)
    if code:
        at.query_params["c"] = code
    return at.run()


@pytest.mark.parametrize("code", CODES)
@pytest.mark.parametrize("sheet", SHEETS)
def test_sheet(sheet, code):
    at = _fresh(sheet, code)
    _assert_clean(at, f"{sheet} inicio")
    for nav in _keys(at, ("nav_",)):
        at.button(key=nav).click().run()
        _assert_clean(at, f"{sheet} {nav}")
        seen = set()
        for _ in range(12):
            pending = [k for k in _keys(at, ("acc_", "ch_")) if k not in seen]
            if not pending:
                break
            key = pending[0]
            seen.add(key)
            at.button(key=key).click().run()
            _assert_clean(at, f"{sheet} {nav} {key}")
        for key in [b.key for b in at.button if b.key and not b.key.startswith(ACTION_PREFIXES)
                    and b.key not in ("home_btn",) and not b.disabled]:
            at.button(key=key).click().run()
            _assert_clean(at, f"{sheet} {nav} {key}")
        for skey in [s.key for s in at.slider if s.key and s.key.endswith("_stage")]:
            top = int(at.slider(key=skey).max)
            for value in range(1, top + 1):
                at.slider(key=skey).set_value(value).run()
                _assert_clean(at, f"{sheet} {skey}={value}")


def test_landing():
    at = AppTest.from_file(str(ROOT / "home.py"), default_timeout=60).run()
    _assert_clean(at, "portada")
    assert at.query_params["c"] in (["UBU-GMAyC"], "UBU-GMAyC")
    assert not any(b.disabled for b in at.button if b.key and b.key.startswith("cell_"))
    at.text_input(key="home_code_input").input("Ubu7").run()
    _assert_clean(at, "portada con código")
    assert at.query_params["c"] == ["Ubu7"] or at.query_params["c"] == "Ubu7"


def _load_sheet(sheet):
    """Ejecuta la ficha sin su llamada final a main() y devuelve su espacio de nombres."""
    source = (ROOT / sheet).read_text(encoding="utf-8").replace("\nmain()\n", "\n")
    namespace = {"__name__": Path(sheet).stem}
    exec(compile(source, sheet, "exec"), namespace)
    return namespace


def _literal(node, namespace):
    return eval(compile(ast.Expression(node), "<widget>", "eval"), namespace)


@pytest.mark.parametrize("sheet", SHEETS)
def test_defaults_fit_widgets(sheet, monkeypatch):
    """Con cualquier código, cada valor inicial cae dentro de su deslizador y en un paso válido."""
    ns = _load_sheet(sheet)
    ui = ns["ui"]
    values = []
    for i in range(201):
        monkeypatch.setattr(ui, "session_code", (lambda i=i: f"grupo{i}") if i else (lambda: ""))
        values.append(ns["initial_values"]())
    tree = ast.parse((ROOT / sheet).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("slider", "select_slider")):
            continue
        kw = {k.arg: k.value for k in node.keywords}
        value = node.args[3] if node.func.attr == "slider" and len(node.args) > 3 else kw.get("value")
        if not (isinstance(value, ast.Subscript) and getattr(value.value, "id", "") == "v"):
            continue
        key = ast.literal_eval(value.slice)
        if node.func.attr == "select_slider":
            options = list(_literal(kw["options"], ns))
            bad = {v[key] for v in values if v[key] not in options}
        else:
            lo, hi = (_literal(node.args[i], ns) for i in (1, 2))
            step = _literal(node.args[4], ns) if len(node.args) > 4 else None
            bad = {v[key] for v in values
                   if not lo <= v[key] <= hi
                   or (step and abs(round((v[key] - lo) / step) * step - (v[key] - lo)) > 1e-9)}
        assert not bad, f"{sheet} línea {node.lineno}, {key}: {sorted(bad)[:5]}"
