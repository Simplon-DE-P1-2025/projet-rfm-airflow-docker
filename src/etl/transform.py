import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
import traceback

from helpers import setup_paths

setup_paths()
from config import DATABASE_URL, DATA_PROCESSED_PATH


def transform_rfm(truncate=True):
    """Calcule le RFM, génère les scores et exporte le résultat"""
    conn = None
    try:
        # 1. Préparation de la table intermédiaire (Silver)
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if truncate:
            cursor.execute("DROP TABLE IF EXISTS rfm_analysis CASCADE;")
            cursor.execute("DROP TYPE IF EXISTS rfm_analysis CASCADE;")
            print("🗑️ Table et Type rfm_analysis supprimés.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rfm_analysis (
                customer_id INT PRIMARY KEY,
                recency INT,
                frequency INT,
                monetary NUMERIC,
                r_score INT,
                f_score INT,
                m_score INT,
                rfm_score VARCHAR(10),
                segment VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()

        # 2. Lecture des données brutes
        print("📖 Lecture des données depuis PostgreSQL...")
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        query = """
            SELECT customer_id, invoice, invoice_date, price, quantity 
            FROM raw_orders 
            WHERE customer_id IS NOT NULL;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("⚠️ Aucune donnée trouvée pour le calcul RFM.")

        # 3. Calculs des métriques RFM brutes
        print("🧪 Calcul des métriques RFM...")
        df["amount"] = df["price"] * df["quantity"]
        max_date = df["invoice_date"].max()

        rfm = (
            df.groupby("customer_id")
            .agg(
                {
                    "invoice_date": lambda x: (max_date - x.max()).days,  # Recency
                    "invoice": "nunique",  # Frequency
                    "amount": "sum",  # Monetary
                }
            )
            .reset_index()
        )
        rfm.columns = ["customer_id", "recency", "frequency", "monetary"]

        rfm = rfm[rfm["monetary"] > 0].copy()

        print("🎯 Attribution des scores de 1 à 5...")

        rfm["r_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)

        rfm["f_score"] = pd.qcut(
            rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
        ).astype(int)
        rfm["m_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

        rfm["rfm_score"] = (
            rfm["r_score"].astype(str)
            + rfm["f_score"].astype(str)
            + rfm["m_score"].astype(str)
        )

        def assign_segment(row):
            """Assigne un segment marketing basé sur les scores RFM."""
            r = row["r_score"]
            f = row["f_score"]
            m = row["m_score"]
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif r >= 3 and f >= 3 and m >= 3:
                return "Clients Fidèles"
            elif r >= 4 and f <= 2:
                return "Nouveaux Clients"
            elif r >= 3 and f >= 1 and m >= 2:
                return "Clients Potentiels"
            elif r <= 2 and f >= 3:
                return "À Risque"
            elif r <= 2 and f <= 2 and m <= 2:
                return "Perdus"
            elif r <= 2 and f <= 2 and m >= 3:
                return "À Réactiver"
            else:
                return "Moyens"

        rfm["segment"] = rfm.apply(assign_segment, axis=1)

        print(f"⏳ Insertion de {len(rfm)} profils clients dans rfm_analysis...")
        insert_query = """
            INSERT INTO rfm_analysis (customer_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_score, segment)
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
        values_analysis = (
            rfm[
                [
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
            ]
            .astype(object)
            .values.tolist()
        )
        execute_values(cursor, insert_query, values_analysis)
        conn.commit()

        # 7. EXPORT CSV POUR LE LOAD
        csv_path = os.path.join(DATA_PROCESSED_PATH, "rfm_results.csv")
        rfm.to_csv(csv_path, index=False)
        print(f"💾 Sauvegarde du CSV réussie avec les scores : {csv_path}")

        cursor.close()
        print(f"✅ Transformation RFM terminée avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la transformation RFM : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise e  # Fait remonter l'erreur pour qu'Airflow la détecte
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    transform_rfm()
