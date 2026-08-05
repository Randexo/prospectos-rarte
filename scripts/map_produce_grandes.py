"""Mapeo: PRODUCE - Directorio de Grandes Empresas del sector Manufactura.
Fuente: https://www.datosabiertos.gob.pe/dataset/directorio-de-grandes-empresas-del-sector-manufactura-ministerio-de-la-producci%C3%B3n-produce

Anillo 1, sin filtro adicional de CIIU (ya vienen clasificados como manufactura).
"""

import pandas as pd

from schema import COLUMNAS, limpiar_ruc

FUENTE = "produce_grandes"


def mapear(path_crudo: str, fecha_corte: str) -> pd.DataFrame:
    # Columnas reales (verificadas en produce_grandes_2026-08-04.csv):
    # ruc,razon_social,descripcion_ciiu3,ciiu3,departamento,provincia,distrito,
    # ubigeo,sector,PERIODO,FECHA_PUBLICACION
    df = pd.read_csv(path_crudo, encoding="latin-1", dtype=str)

    out = pd.DataFrame({
        "ruc": df["ruc"].map(limpiar_ruc),
        "razon_social": df["razon_social"],
        "ciiu": df["ciiu3"] + " - " + df["descripcion_ciiu3"],
        "ubigeo": df["ubigeo"],
        "tamano": "grande",
        "anillo": "Anillo 1",
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
