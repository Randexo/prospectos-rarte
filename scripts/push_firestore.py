"""Sube el universo consolidado a Firestore (colección 'empresas', 1 doc por RUC).

Requiere el JSON del service account de Firebase. Se busca en, en este orden:
  1. Variable de entorno FIREBASE_CREDENTIALS_PATH
  2. credentials/firebase_service_account.json (dentro del propio proyecto,
     gitignorado — es una credencial específica de este proyecto, no
     transversal, así que no vive en shared/auth/)
"""

import os

import firebase_admin
import pandas as pd
from firebase_admin import credentials, firestore

CRED_PATH_DEFAULT = os.path.join(
    os.path.dirname(__file__), "..", "credentials", "firebase_service_account.json"
)


def _inicializar():
    if firebase_admin._apps:
        return firestore.client()

    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", CRED_PATH_DEFAULT)
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"No se encontró el service account de Firebase en {cred_path}. "
            "Generarlo en Firebase Console > Configuración del proyecto > Cuentas de servicio."
        )
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()


def subir(universo: pd.DataFrame, coleccion: str = "empresas"):
    db = _inicializar()
    batch = db.batch()
    for i, (_, fila) in enumerate(universo.iterrows(), start=1):
        ref = db.collection(coleccion).document(fila["ruc"])
        batch.set(ref, fila.dropna().to_dict(), merge=True)
        if i % 400 == 0:  # límite de Firestore: 500 escrituras por batch
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f"Subidas {len(universo)} filas a Firestore ({coleccion}).")


if __name__ == "__main__":
    import sys

    df = pd.read_csv(sys.argv[1], dtype=str)
    subir(df)
