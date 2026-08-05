"""Mapeo: MINEM/DGM - Registro de Empresas Contratistas Mineras.
Fuente: https://datosabiertos.gob.pe/dataset/minem-contratistas-mineros

Anillo 2, sin filtro adicional (la inscripción ya es el filtro).

Archivo real (.xlsx): 5 filas de título repetido, encabezado en la fila 6:
REGISTRO, R.D, FECHA R.D, CONTRATISTA, RUC, DOMICILIO, DISTRITO, PROVINCIA,
DEPARTAMENTO, TELEFONO, REPRESENTANTE, EXPLORACION, EXPLOTACION, DESARROLLO,
BENEFICIO. No trae CIIU ni ubigeo (código) — quedan vacíos y los rellena el
enriquecimiento de SUNAT en el orquestador.
"""

import pandas as pd

from schema import COLUMNAS, limpiar_ruc

FUENTE = "minem_dgm"


def mapear(path_crudo: str, fecha_corte: str) -> pd.DataFrame:
    df = pd.read_excel(path_crudo, skiprows=5, dtype=str)

    out = pd.DataFrame({
        "ruc": df["RUC"].map(limpiar_ruc),
        "razon_social": df["CONTRATISTA"],
        "ciiu": None,
        "ubigeo": None,
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
