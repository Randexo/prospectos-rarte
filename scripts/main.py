"""Orquestador: arma el universo consolidado a partir de los archivos crudos
en raw/, guarda un CSV versionado en output/ y (opcionalmente) lo sube a
Google Sheets.

Uso:
    python scripts/main.py --fecha-corte 2026-08-04 --subir-sheets
"""

import argparse
import glob
import os
from datetime import date

import pandas as pd

import map_minem_dgm
import map_produce_grandes
import map_produce_mipyme
import map_sunat_padron

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def _ultimo_archivo(prefijo: str) -> str:
    candidatos = sorted(
        p
        for patron in (f"{prefijo}_*.csv", f"{prefijo}_*.xlsx", f"{prefijo}_*.txt")
        for p in glob.glob(os.path.join(RAW_DIR, patron))
        if "diccionario" not in p
    )
    if not candidatos:
        raise FileNotFoundError(f"No se encontró ningún raw/{prefijo}_*.(csv|xlsx)")
    return candidatos[-1]


def construir_universo(fecha_corte: str) -> pd.DataFrame:
    anillo1 = pd.concat([
        map_produce_grandes.mapear(_ultimo_archivo("produce_grandes"), fecha_corte),
        map_produce_mipyme.mapear(_ultimo_archivo("produce_mipyme"), fecha_corte),
    ], ignore_index=True)

    anillo2 = map_minem_dgm.mapear(_ultimo_archivo("minem_dgm"), fecha_corte)

    universo = pd.concat([anillo1, anillo2], ignore_index=True)

    # Dedup por ruc: si aparece en Anillo 1 y Anillo 2, combinar en "Anillo 1+2".
    # PRODUCE/MINEM mandan en tamano/ciiu (SUNAT no los trae).
    def combinar(grupo: pd.DataFrame) -> pd.Series:
        anillos = set(grupo["anillo"])
        anillo_final = "Anillo 1+2" if len(anillos) > 1 else grupo["anillo"].iloc[0]
        primera = grupo.iloc[0].copy()
        primera["anillo"] = anillo_final
        primera["fuente"] = "+".join(sorted(set(grupo["fuente"])))
        for campo in ["tamano", "ciiu", "razon_social", "ubigeo"]:
            no_vacios = grupo[campo].dropna()
            if not no_vacios.empty:
                primera[campo] = no_vacios.iloc[0]
        return primera

    universo = universo.groupby("ruc", as_index=False, group_keys=False).apply(combinar)

    # Enriquecimiento SUNAT: solo para los RUCs que ya tenemos, nunca el padrón completo.
    rucs_objetivo = set(universo["ruc"])
    sunat = map_sunat_padron.enriquecer(_ultimo_archivo("sunat_padron"), rucs_objetivo)
    sunat_idx = sunat.set_index("ruc")

    faltantes_antes = universo[["razon_social", "ubigeo"]].isna().sum()
    for campo in ["razon_social", "ubigeo"]:
        universo[campo] = universo.apply(
            lambda fila: fila[campo] if pd.notna(fila[campo]) else sunat_idx[campo].get(fila["ruc"]),
            axis=1,
        )
    universo["estado"] = universo["ruc"].map(sunat_idx["estado"].to_dict())
    universo["condicion_domicilio"] = universo["ruc"].map(sunat_idx["condicion_domicilio"].to_dict())

    no_matcheados_sunat = len(rucs_objetivo - set(sunat["ruc"]))

    print("=== Resumen ===")
    print(universo["anillo"].value_counts())
    print(f"Anillo 1+2 (traslape): {(universo['anillo'] == 'Anillo 1+2').sum()}")
    print(f"RUCs sin match en SUNAT: {no_matcheados_sunat}")
    print(f"Campos rellenados por SUNAT (razon_social/ubigeo, antes vacíos): {faltantes_antes.to_dict()}")

    return universo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fecha-corte", default=str(date.today()))
    parser.add_argument("--subir-sheets", action="store_true")
    args = parser.parse_args()

    universo = construir_universo(args.fecha_corte)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    salida = os.path.join(OUTPUT_DIR, f"universo_consolidado_{args.fecha_corte}.csv")
    universo.to_csv(salida, index=False)
    print(f"\nGuardado: {salida}")

    if args.subir_sheets:
        import push_sheets

        push_sheets.subir(universo)


if __name__ == "__main__":
    main()
