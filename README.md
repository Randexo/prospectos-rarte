# Universo de Prospectos RAR TE — Fase 1 (Anillo 1 y Anillo 2)

Base de datos consolidada de empresas candidatas para outreach, cruzando
PRODUCE (Anillo 1), MINEM/DGM (Anillo 2) y SUNAT Padrón RUC (enriquecimiento),
por RUC.

Datos en vivo: https://randexo.github.io/prospectos-rarte/
Hoja fuente: https://docs.google.com/spreadsheets/d/1zsVGF4jk-yeiwO_P1wG8yvvcYQBOZOegWVwiZtwmFdI

## Estructura

```
raw/          archivos crudos tal cual se descargan, sin transformar
              (nombre: <fuente>_YYYY-MM-DD.csv)
scripts/      ETL: 4 scripts de mapeo + orquestador + subida a Google Sheets
output/       universo_consolidado_YYYY-MM-DD.csv, uno por corrida
docs/         página estática (GitHub Pages) que lee el CSV publicado de la
              hoja de Google Sheets — sin backend propio
credentials/  gitignorado — apps_script_config.json (url + secreto del
              Web App que recibe las subidas)
```

## Arquitectura de la base de datos

El dato vive en una Google Sheet. Se escribe desde `scripts/push_sheets.py`,
que le manda los datos a un **Web App de Apps Script** vinculado a esa hoja
(no una API de Google Cloud ni una cuenta de servicio — ver por qué en el
docstring de `push_sheets.py`). El frontend en `docs/` lee la hoja publicada
como CSV (`.../export?format=csv&gid=0`) y filtra en el navegador.

Para replicar el Web App de Apps Script en una hoja nueva: `Extensiones →
Apps Script` en la hoja, pegar el código de `push_sheets.py` (ver
`SECRETO`/`doPost`), implementar como Aplicación Web con acceso "Cualquier
usuario", y guardar la URL + secreto en `credentials/apps_script_config.json`
como `{"url": ..., "secreto": ...}`.

## Pendiente antes de correr desde cero

1. Descargar los 4 archivos fuente a `raw/` con el nombre `<fuente>_<fecha>.csv`:
   `produce_grandes`, `produce_mipyme`, `minem_dgm`, `sunat_padron`.
2. Crear `credentials/apps_script_config.json` (ver arriba).
3. La hoja de Google Sheets y el Web App de Apps Script ya deben existir
   (no se crean automáticamente desde el script).

## Correr

```bash
pip install -r requirements.txt
python scripts/main.py --fecha-corte 2026-08-04 --subir-sheets
```

Sin `--subir-sheets` solo genera el CSV en `output/`.
