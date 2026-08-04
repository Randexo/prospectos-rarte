"""Mapeo: PRODUCE - Directorio de Grandes Empresas del sector Manufactura.
Fuente: https://www.datosabiertos.gob.pe/dataset/directorio-de-grandes-empresas-del-sector-manufactura-ministerio-de-la-producci%C3%B3n-produce

Anillo 1, sin filtro adicional de CIIU (ya vienen clasificados como manufactura).
"""

import pandas as pd

from schema import COLUMNAS, limpiar_ruc

FUENTE = "produce_grandes"


def mapear(path_crudo: str, fecha_corte: str) -> pd.DataFrame:
    df = pd.read_csv(path_crudo, encoding="latin-1", sep=None, engine="python")

    # TODO: verificar nombres reales de columnas al bajar el archivo.
    # Placeholder de mapeo — ajustar una vez inspeccionado el archivo real.
    out = pd.DataFrame({
        "ruc": df["ruc"].map(limpiar_ruc),
        "razon_social": df.get("razon_social"),
        "ciiu": df.get("ciiu"),
        "ubigeo": df.get("ubigeo"),
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
