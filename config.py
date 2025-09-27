from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# Zona horaria
TZ = ZoneInfo("America/Argentina/Buenos_Aires")


# Persistencia simple
COUNTER_PATH = DATA_DIR / "reclamos_counter.json"
LOG_PATH = DATA_DIR / "reclamos_log.jsonl"


# Layout etiqueta (80mm)
LABEL_WIDTH = 576 # dots @203dpi
LABEL_HEIGHT = 900 # ajustar según contenido
WITH_LOGO = True
