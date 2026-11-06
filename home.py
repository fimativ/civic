#Adriana Ortega 2026 Prácticas Externas UC-C1VIC D4TA

"""Punto de entrada de la aplicación: `streamlit run home.py`.

Descubre las fichas de la carpeta `fichas/`, les asigna una dirección estable y
arranca la navegación. La portada propiamente dicha vive en `inicio.py`.

Nombres de fichero:
    fichas/TT_KK.py   ejercicio KK del tema TT de probabilidad (TT = 01..06)
    fichas/00_KK.py   herramienta KK de estadística univariante
La carpeta no se llama pages/ a propósito: si existe una carpeta con ese nombre
junto a este script, Streamlit ni siquiera lo ejecuta y monta su propio menú.
Cada ficha declara una constante TITLE con el título que se muestra y, las de
probabilidad, una constante SYMBOL con el símbolo de su casilla en la portada.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="C1VIC D4TA",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / "fichas"
PAGE_RE = re.compile(r"^(?P<chapter>\d{2})_(?P<number>\d{2})\.py$")


@dataclass(frozen=True)
class Sheet:
    path: Path
    chapter: int
    number: int
    title: str
    symbol: str = ""

    @property
    def route(self) -> str:
        return f"fichas/{self.path.name}"

    @property
    def url_path(self) -> str:
        return f"e{self.number}" if self.chapter == 0 else f"t{self.chapter}-{self.number}"

    @property
    def is_statistics(self) -> bool:
        return self.chapter == 0


def read_constants(path: Path) -> dict[str, str]:
    """Lee las constantes de texto de una ficha (TITLE, SYMBOL) sin ejecutarla."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    found = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("TITLE", "SYMBOL"):
                    found[target.id] = node.value.value
    return found


@st.cache_resource(show_spinner=False)
def discover_sheets(pages_dir: str, signature: tuple) -> list[Sheet]:
    sheets = []
    for path in sorted(Path(pages_dir).glob("*.py")):
        m = PAGE_RE.match(path.name)
        if m:
            consts = read_constants(path)
            sheets.append(Sheet(path, int(m["chapter"]), int(m["number"]),
                                consts.get("TITLE", path.stem), consts.get("SYMBOL", "")))
    sheets.sort(key=lambda s: (s.chapter, s.number))
    return sheets


def folder_signature(pages_dir: Path) -> tuple:
    """Cambia cuando se añade, quita o edita una ficha (invalida la caché)."""
    return tuple(sorted((p.name, p.stat().st_mtime_ns) for p in pages_dir.glob("*.py")))


SHEETS = discover_sheets(str(PAGES_DIR), folder_signature(PAGES_DIR))
st.session_state["sheets"] = SHEETS

pages = [st.Page("inicio.py", title="Inicio", default=True)]
pages += [st.Page(s.route, title=s.title, url_path=s.url_path) for s in SHEETS]

st.navigation(pages, position="hidden").run()
