# Universo de Prospectos RAR TE — Fase 1 (Anillo 1 y Anillo 2)

Base de datos consolidada de empresas candidatas para outreach, cruzando
PRODUCE (Anillo 1), MINEM/DGM (Anillo 2) y SUNAT Padrón RUC (enriquecimiento),
por RUC.

## Estructura

```
raw/          archivos crudos tal cual se descargan, sin transformar
              (nombre: <fuente>_YYYY-MM-DD.csv)
scripts/      ETL: 4 scripts de mapeo + orquestador + subida a Firestore
output/       universo_consolidado_YYYY-MM-DD.csv, uno por corrida
docs/         página estática que consulta Firestore directo (sin backend propio),
              servida vía GitHub Pages desde esta carpeta
credentials/  service account de Firebase (gitignorado, específico de este proyecto)
```

## Pendiente antes de correr

1. Descargar los 4 archivos fuente a `raw/` con el nombre `<fuente>_<fecha>.csv`:
   `produce_grandes`, `produce_mipyme`, `minem_dgm`, `sunat_padron`.
2. Abrir cada archivo una vez y ajustar los TODO de columnas en
   `scripts/map_*.py` (los nombres reales de columna varían por fuente).
3. Crear el proyecto Firebase (ver guía aparte) y colocar el service account
   en `credentials/firebase_service_account.json`.
4. `firebaseConfig` en `docs/index.html` ya está completo con los datos de la Web App.

## Correr

```bash
pip install -r requirements.txt
python scripts/main.py --fecha-corte 2026-08-04 --subir-firestore
```

Sin `--subir-firestore` solo genera el CSV en `output/`.
