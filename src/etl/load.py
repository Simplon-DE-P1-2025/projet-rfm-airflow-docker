"""
Script de chargement - Sauvegarde les résultats RFM dans PostgreSQL
"""

import sys
import os
from helpers import setup_paths

setup_paths()

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from config import DATABASE_URL, DATA_PROCESSED_PATH
import os


def create_rfm_table(conn):
    """Crée la table pour les résultats RFM"""
    cursor = conn.cursor()

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Table rfm_results créée")
        return True
    except Exception as e:
        print(f"❌ Erreur création table : {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def load_rfm_results():
    """Charge les résultats RFM dans PostgreSQL"""

    # 1. Lire le fichier RFM
    rfm_file = os.path.join(DATA_PROCESSED_PATH, "rfm_results.csv")

    if not os.path.exists(rfm_file):
        print(f"❌ Fichier RFM non trouvé : {rfm_file}")
        return False

    print(f"📂 Lecture du fichier RFM : {os.path.basename(rfm_file)}")

    try:
        df = pd.read_csv(rfm_file)
        print(f"📊 {len(df)} clients RFM à charger")
    except Exception as e:
        print(f"❌ Erreur lecture fichier : {e}")
        return False

    # 2. Connexion et insertion
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connecté à PostgreSQL\n")

        if not create_rfm_table(conn):
            return False

        cursor = conn.cursor()

        # Préparer les données
        columns = [
            "customer_id",
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "rfm_score",
        ]

        values = [tuple(x) for x in df[columns].to_numpy()]

        # Insérer avec upsert (UPDATE si existe, INSERT sinon)
        insert_query = """
        INSERT INTO rfm_results (customer_id, recency, frequency, monetary, 
                                r_score, f_score, m_score, rfm_score)
        VALUES %s
        ON CONFLICT (customer_id) DO UPDATE SET
            recency = EXCLUDED.recency,
            frequency = EXCLUDED.frequency,
            monetary = EXCLUDED.monetary,
            r_score = EXCLUDED.r_score,
            f_score = EXCLUDED.f_score,
            m_score = EXCLUDED.m_score,
            rfm_score = EXCLUDED.rfm_score
        """

        print(f"⏳ Chargement de {len(values)} clients RFM...")
        execute_values(cursor, insert_query, values)
        conn.commit()

        cursor.close()
        conn.close()

        print("=" * 50)
        print(f"✅ {len(values)} clients RFM chargés !")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = load_rfm_results()
    exit(0 if success else 1)
