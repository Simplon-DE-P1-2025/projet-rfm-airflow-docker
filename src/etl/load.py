"""
Script de chargement - Sauvegarde les résultats RFM dans PostgreSQL (Version Robuste)
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from helpers import setup_paths

setup_paths()
from config import DATABASE_URL, DATA_PROCESSED_PATH


def create_rfm_table(cursor):
    """Crée la table pour les résultats RFM si elle n'existe pas"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS rfm_results (
        id SERIAL PRIMARY KEY,
        customer_id INT UNIQUE,
        recency INT,
        frequency INT,
        monetary NUMERIC(10, 2),
        r_score INT,
        f_score INT,
        m_score INT,
        rfm_score VARCHAR(10),
        segment VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    print("✅ Structure de la table rfm_results vérifiée.")


def load_rfm_results():
    """Charge les résultats RFM dans PostgreSQL"""

    rfm_file = os.path.join(DATA_PROCESSED_PATH, "rfm_results.csv")

    # 1. Validation de l'existence du fichier
    if not os.path.exists(rfm_file):
        raise FileNotFoundError(
            f"❌ Le fichier CSV est introuvable : {rfm_file}\n"
            "Assurez-vous que la tâche 'transform_rfm' l'a bien généré."
        )

    print(f"📂 Lecture du fichier RFM : {os.path.basename(rfm_file)}")

    # 2. Lecture et validation des données
    df = pd.read_csv(rfm_file)

    if df.empty:
        raise ValueError("❌ Le fichier CSV est vide. Rien à charger.")

    expected_columns = [
        "customer_id",
        "recency",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "segment",
    ]
    missing_cols = [col for col in expected_columns if col not in df.columns]

    if missing_cols:
        raise KeyError(
            f"❌ Colonnes manquantes dans le CSV : {missing_cols}\n"
            "Avez-vous bien calculé les scores dans l'étape de transformation ?"
        )

    print(f"📊 {len(df)} clients RFM prêts à être chargés.")

    df = df.astype(object).where(pd.notnull(df), None)

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                print("✅ Connecté à PostgreSQL.")

                create_rfm_table(cursor)

                values = [tuple(x) for x in df[expected_columns].to_numpy()]

                # Requête Upsert
                insert_query = """
                INSERT INTO rfm_results (customer_id, recency, frequency, monetary, 
                                        r_score, f_score, m_score, rfm_score, segment)
                VALUES %s
                ON CONFLICT (customer_id) DO UPDATE SET
                    recency = EXCLUDED.recency,
                    frequency = EXCLUDED.frequency,
                    monetary = EXCLUDED.monetary,
                    r_score = EXCLUDED.r_score,
                    f_score = EXCLUDED.f_score,
                    m_score = EXCLUDED.m_score,
                    rfm_score = EXCLUDED.rfm_score,
                    segment = EXCLUDED.segment,
                    updated_at = CURRENT_TIMESTAMP;
                """

                print(f"⏳ Chargement de {len(values)} lignes en base...")
                # execute_values est optimisé pour les insertions par lots
                execute_values(cursor, insert_query, values, page_size=1000)

        print("=" * 50)
        print(
            f"✅ SUCCÈS : {len(values)} clients RFM mis à jour/insérés dans PostgreSQL !"
        )
        print("=" * 50)

    except Exception as e:
        raise RuntimeError(f"❌ Échec lors de l'insertion en base de données : {e}")


if __name__ == "__main__":
    load_rfm_results()
