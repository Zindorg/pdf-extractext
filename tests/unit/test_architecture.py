"""Regla de dependencias: el núcleo no conoce frameworks, drivers ni config.

Analiza los imports de cada módulo (sin ejecutarlos) y falla si una capa
interna depende de una externa.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "app"

FORBIDDEN = {
    "domain": ("fastapi", "pydantic", "pymongo", "bson", "pypdf", "app.config",
               "app.api", "app.routes", "app.schemas", "app.dependencies",
               "app.infrastructure", "app.use_cases"),
    "use_cases": ("fastapi", "pydantic", "pymongo", "bson", "pypdf", "app.config",
                  "app.api", "app.routes", "app.schemas", "app.dependencies",
                  "app.infrastructure"),
}


def _imports(module: Path) -> set[str]:
    tree = ast.parse(module.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("layer", FORBIDDEN)
def test_layer_does_not_depend_on_outer_layers(layer):
    violations = [
        f"{module.relative_to(APP)} -> {name}"
        for module in sorted((APP / layer).rglob("*.py"))
        for name in _imports(module)
        if any(name == banned or name.startswith(banned + ".") for banned in FORBIDDEN[layer])
    ]

    assert violations == []
