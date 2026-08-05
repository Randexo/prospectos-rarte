"""Sube el universo consolidado a Google Sheets vía un Web App de Apps Script
vinculado a la hoja de destino.

Por qué así y no con la API de Google directo: un script de Apps Script
vinculado a la hoja ya tiene permiso nativo de escritura sobre ella — no
requiere cuenta de servicio, ni habilitar ninguna API de Google Cloud, ni
sufrir demoras de propagación de permisos.

Requiere credentials/apps_script_config.json con {"url": ..., "secreto": ...}
(url del despliegue del Web App, secreto compartido definido en el propio
script de Apps Script para que no cualquiera pueda escribir en la hoja).
"""

import json
import os

import pandas as pd
import requests

CONFIG_PATH_DEFAULT = os.path.join(
    os.path.dirname(__file__), "..", "credentials", "apps_script_config.json"
)


def _config():
    config_path = os.environ.get("APPS_SCRIPT_CONFIG_PATH", CONFIG_PATH_DEFAULT)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No se encontró la configuración del Web App en {config_path}.")
    with open(config_path) as f:
        return json.load(f)


def subir(universo: pd.DataFrame, lote: int = 20_000, reanudar_desde: int = 0):
    """reanudar_desde: índice (0-based, incluye el header en la posición 0)
    desde donde continuar si una corrida anterior se cortó a medio camino.
    Cuando es 0 (default), limpia la hoja antes de escribir; si es mayor a 0,
    NO limpia y sigue escribiendo desde ahí."""
    cfg = _config()
    universo = universo.fillna("")
    filas = [universo.columns.tolist()] + universo.values.tolist()

    for inicio in range(reanudar_desde, len(filas), lote):
        bloque = filas[inicio : inicio + lote]
        resp = requests.post(
            cfg["url"],
            json={
                "secreto": cfg["secreto"],
                "limpiar": inicio == 0,
                "filaInicio": inicio + 1,
                "filas": bloque,
            },
            timeout=300,
        )
        resp.raise_for_status()
        resultado = resp.json()
        if not resultado.get("ok"):
            raise RuntimeError(f"El Web App rechazó el lote: {resultado}")
        print(f"  Lote desde fila {inicio + 1}: {resultado['filas']} filas escritas.")

    print(f"Subidas {len(universo)} filas a Google Sheets vía Apps Script.")


if __name__ == "__main__":
    import sys

    df = pd.read_csv(sys.argv[1], dtype=str)
    subir(df)
