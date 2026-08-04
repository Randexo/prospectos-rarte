"""Esquema común del universo consolidado y helpers de validación compartidos
por los 4 scripts de mapeo."""

import re

COLUMNAS = [
    "ruc",
    "razon_social",
    "ciiu",
    "ubigeo",
    "tamano",
    "anillo",
    "fuente",
    "fecha_corte",
]

RUC_RE = re.compile(r"^\d{11}$")


def limpiar_ruc(valor) -> str | None:
    """Normaliza un RUC a string de 11 dígitos. Devuelve None si no calza el formato."""
    if valor is None:
        return None
    ruc = re.sub(r"\D", "", str(valor))
    return ruc if RUC_RE.match(ruc) else None


def dataframe_vacio():
    import pandas as pd

    return pd.DataFrame(columns=COLUMNAS)
