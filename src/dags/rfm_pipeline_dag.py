"""
DAG Airflow - Pipeline RFM
Orchestre : Ingestion → Transformation → Chargement
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Ajouter les chemins pour importer les scripts ETL et Analysis
module_paths = [
    "/airflow/etl",  # Docker - ETL core scripts
    "/airflow/analysis",  # Docker - Advanced analytics scripts
    os.path.join(os.path.dirname(__file__), "..", "etl"),  # Local - etl/
    os.path.join(os.path.dirname(__file__), "..", "analysis"),  # Local - analysis/
]

for path in module_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Importer le helper de configuration
from helpers import setup_paths

setup_paths()

try:
    from ingest import ingest_data
    from transform import transform_rfm
    from load import load_rfm_results
    from product_rfm import product_rfm_analysis
    from churn_prediction import churn_prediction
    from geographic_analysis import geographic_analysis
    from clv_forecast import clv_forecast
except ImportError as e:
    print(f"⚠️ Erreur d'import : {e}")
    raise

# Configuration du DAG
default_args = {
    "owner": "data-engineer",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="rfm_pipeline",
    default_args=default_args,
    description="Pipeline RFM : Ingestion → Transformation → Chargement",
    schedule_interval="@daily",  # Exécution quotidienne
    catchup=False,
) as dag:

    # Tâche 1 : Ingestion
    task_ingest = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=ingest_data,
        doc="Charge les fichiers CSV bruts dans PostgreSQL (table raw_data)",
    )

    # Tâche 2 : Transformation RFM
    task_transform = PythonOperator(
        task_id="transform_rfm",
        python_callable=transform_rfm,
        doc="Calcule les scores RFM (Recency, Frequency, Monetary)",
    )

    # Tâche 3 : Chargement
    task_load = PythonOperator(
        task_id="load_rfm_results",
        python_callable=load_rfm_results,
        doc="Charge les résultats RFM dans PostgreSQL (table rfm_results)",
    )

    # ─────────────────────────────────────────────────────────
    # Tâches Avancées (Priority 3) - Exécutées en parallèle
    # ─────────────────────────────────────────────────────────
    task_product = PythonOperator(
        task_id="product_rfm_analysis",
        python_callable=product_rfm_analysis,
        doc="Analyse RFM au niveau produit (Stars vs Orphelins)",
    )

    task_churn = PythonOperator(
        task_id="churn_prediction",
        python_callable=churn_prediction,
        doc="Prédiction de churn (0-100 score) avec recommendations",
    )

    task_geo = PythonOperator(
        task_id="geographic_analysis",
        python_callable=geographic_analysis,
        doc="Analyse géographique (opportunités expansion par pays)",
    )

    task_clv = PythonOperator(
        task_id="clv_forecast",
        python_callable=clv_forecast,
        doc="Prévision CLV 12-24 mois par client/segment",
    )

    # Définir les dépendances
    (
        task_ingest
        >> task_transform
        >> task_load
        >> [task_product, task_churn, task_geo, task_clv]
    )
