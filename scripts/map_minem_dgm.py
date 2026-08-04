"""Mapeo: MINEM/DGM - Registro de Empresas Contratistas Mineras.
Fuente: https://datosabiertos.gob.pe/dataset/minem-contratistas-mineros

Anillo 2, sin filtro adicional (la inscripción ya es el filtro).
"""

import pandas as pd

from schema import COLUMNAS, limpiar_ruc

FUENTE = "minem_dgm"


def mapear(path_crudo: str, fecha_corte: str) -> pd.DataFrame:
    df = pd.read_csv(path_crudo, encoding="latin-1", sep=None, engine="python")

    # TODO: verificar nombres reales de columnas al bajar el archivo.
    # Placeholder de mapeo — ajustar una vez inspeccionado el archivo real.
    out = pd.DataFrame({
        "ruc": df["ruc"].map(limpiar_ruc),
        "razon_social": df.get("razon_social"),
        "ciiu": df.get("ciiu"),
        "ubigeo": df.get("ubigeo"),
        "tamano": None,
        "anillo": "Anillo 2",
        "fuente": FUENTE,
        "fecha_corte": fecha_corte,
    })

    out = out.dropna(subset=["ruc"])
    return out[COLUMNAS]


if __name__ == "__main__":
    import sys

    resultado = mapear(sys.argv[1], sys.argv[2])
    print(resultado.head())
    print(f"Filas mapeadas: {len(resultado)}")
