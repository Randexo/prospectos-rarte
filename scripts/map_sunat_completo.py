"""Enriquecimiento adicional: Padrón RUC completo de SUNAT (distinto al
Padrón Reducido usado en map_sunat_padron.py).

Fuente: https://www.datosabiertos.gob.pe/dataset/padr%C3%B3n-ruc-superintendencia-nacional-de-aduanas-y-de-administraci%C3%B3n-tributaria-sunat

Trae dos señales operacionales que el padrón reducido no tiene:
- NroTrab: número de trabajadores (cifra real, ej. "1573", o "NO DISPONIBLE").
- ComercioExterior: "IMPORTADOR/EXPORTADOR" o "SIN ACTIVIDAD".

No trae razón social (por eso no reemplaza al padrón reducido, se suma).
No trae ingresos/ventas — SUNAT no publica eso por reserva tributaria.

Mismo criterio que map_sunat_padron.py: nunca cargar el archivo completo
(3.5GB+) sin filtrar antes por rucs_objetivo.
"""

import pandas as pd

from schema import limpiar_ruc

FUENTE = "sunat_completo"

COLUMNAS_USADAS = ["RUC", "NroTrab", "ComercioExterior"]


def enriquecer(path_crudo: str, rucs_objetivo: set[str], chunksize: int = 200_000) -> pd.DataFrame:
    filas = []
    for chunk in pd.read_csv(
        path_crudo,
        dtype=str,
        usecols=COLUMNAS_USADAS,
        chunksize=chunksize,
        on_bad_lines="skip",
    ):
        chunk = chunk.rename(columns={
            "RUC": "ruc",
            "NroTrab": "nro_trabajadores",
            "ComercioExterior": "comercio_exterior",
        })
        chunk["ruc"] = chunk["ruc"].map(limpiar_ruc)
        filas.append(chunk[chunk["ruc"].isin(rucs_objetivo)])

    resultado = pd.concat(filas, ignore_index=True) if filas else pd.DataFrame(
        columns=["ruc", "nro_trabajadores", "comercio_exterior"]
    )
    resultado["nro_trabajadores"] = pd.to_numeric(resultado["nro_trabajadores"], errors="coerce")
    return resultado


if __name__ == "__main__":
    import sys

    objetivo = set(sys.argv[2].split(","))
    resultado = enriquecer(sys.argv[1], objetivo)
    print(resultado.head())
    print(f"Filas encontradas: {len(resultado)}")
