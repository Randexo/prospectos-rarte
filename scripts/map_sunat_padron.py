"""Enriquecimiento: SUNAT - Padrón Reducido RUC.
Fuente: http://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html

No se concatena directo al universo (no tiene anillo propio) — se usa solo
para rellenar campos vacíos (razón social, ubigeo, estado) de los RUCs que
ya aparecen en Anillo 1 / Anillo 2. El padrón completo tiene millones de
filas: nunca cargar completo a memoria sin filtrar primero por rucs_objetivo.

TODO: confirmar el orden/cantidad real de columnas contra el archivo bajado
(el padrón es texto plano delimitado por "|", sin encabezado). El layout de
abajo es el conocido públicamente pero puede variar por versión.
"""

import pandas as pd

from schema import limpiar_ruc

FUENTE = "sunat_padron"

# TODO: confirmar contra archivo real
COLUMNAS_PADRON = [
    "ruc",
    "razon_social",
    "estado",
    "condicion_domicilio",
    "ubigeo",
]


def enriquecer(path_crudo: str, rucs_objetivo: set[str], chunksize: int = 200_000) -> pd.DataFrame:
    """Lee el padrón en chunks y devuelve solo las filas cuyo RUC está en
    rucs_objetivo, ya con columnas normalizadas."""
    filas = []
    for chunk in pd.read_csv(
        path_crudo,
        sep="|",
        header=None,
        encoding="latin-1",
        dtype=str,
        chunksize=chunksize,
    ):
        chunk = chunk.iloc[:, : len(COLUMNAS_PADRON)]
        chunk.columns = COLUMNAS_PADRON
        chunk["ruc"] = chunk["ruc"].map(limpiar_ruc)
        filas.append(chunk[chunk["ruc"].isin(rucs_objetivo)])

    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame(columns=COLUMNAS_PADRON)


if __name__ == "__main__":
    import sys

    objetivo = set(sys.argv[2].split(","))
    resultado = enriquecer(sys.argv[1], objetivo)
    print(resultado.head())
    print(f"Filas encontradas: {len(resultado)}")
