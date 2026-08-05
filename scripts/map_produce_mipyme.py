"""Mapeo: PRODUCE - Directorio de Empresas MiPyme por sector productivo.
Fuente: https://www.datosabiertos.gob.pe/dataset/directorio-de-empresas-mipyme-por-sector-productivo-ministerio-de-la-producci%C3%B3n-produce

Anillo 1, filtrado a sector=MANUFACTURA. A diferencia del directorio de
Grandes Empresas (100% manufactura), este archivo trae los 3 sectores
productivos de PRODUCE (Comercio, Servicio, Manufactura) — ~2M filas sin
filtrar. Se filtra a Manufactura para mantener consistencia con la
definición de Anillo 1 y por límite práctico de cuota de Firestore.
"""

import pandas as pd

from schema import COLUMNAS, limpiar_ruc

FUENTE = "produce_mipyme"


def mapear(path_crudo: str, fecha_corte: str) -> pd.DataFrame:
    # Mismas columnas que produce_grandes:
    # ruc,razon_social,descripcion_ciiu3,ciiu3,departamento,provincia,distrito,
    # ubigeo,sector,PERIODO,FECHA_PUBLICACION
    #
    # Algunas razones sociales traen comas sin comillas (error del archivo
    # fuente, ej. "DELALPER - INMOBILIARIA Y NEGOCIOS, SOCIEDAD ANONIMA
    # CERRADA"), lo que rompe el conteo de columnas en esas filas puntuales.
    # Se saltan y se reporta cuántas, en vez de fallar todo el parseo.
    with open(path_crudo, encoding="latin-1") as f:
        total_lineas_fuente = sum(1 for _ in f) - 1  # menos encabezado

    df = pd.read_csv(path_crudo, encoding="latin-1", dtype=str, on_bad_lines="skip")

    saltadas = total_lineas_fuente - len(df)
    if saltadas:
        print(f"[map_produce_mipyme] {saltadas} filas saltadas por error de formato en el CSV fuente.")

    df = df[df["sector"] == "MANUFACTURA"]

    out = pd.DataFrame({
        "ruc": df["ruc"].map(limpiar_ruc),
        "razon_social": df["razon_social"],
        "ciiu": df["ciiu3"] + " - " + df["descripcion_ciiu3"],
        "ubigeo": df["ubigeo"],
        "tamano": "mipyme",
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
