"""Configuration du projet RFM"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"

# PostgreSQL - Lire depuis variables d'environnement
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "rfm_db")
DB_USER = os.getenv("DB_USER", "rfm_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rfm_password")

# URLs
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Airflow
AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", str(PROJECT_ROOT / "airflow"))

# Dataset
DATASET_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
