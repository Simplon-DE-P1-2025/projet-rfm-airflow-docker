"""
Script de chargement - Copie les résultats RFM depuis rfm_analysis vers rfm_results
Optimisé : SQL INSERT...SELECT au lieu de fichier CSV
"""

import sys
import psycopg2
from helpers import setup_paths

setup_paths()
from config import DATABASE_URL


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
    """Copie les résultats RFM depuis rfm_analysis vers rfm_results (SQL INSERT...SELECT)"""

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                print("✅ Connecté à PostgreSQL.")

                # 1. Vérifier que rfm_analysis a des données
                cursor.execute("SELECT COUNT(*) FROM rfm_analysis;")
                count = cursor.fetchone()[0]
                if count == 0:
                    raise ValueError(
                        "❌ Aucune donnée dans rfm_analysis. "
                        "Assurez-vous que la tâche 'transform_rfm' s'est bien exécutée."
                    )

                print(f"📊 {count} clients RFM trouvés dans rfm_analysis")

                # 2. Créer rfm_results si besoin
                create_rfm_table(cursor)

                # 3. Copie directe depuis rfm_analysis via UPSERT
                copy_query = """
                INSERT INTO rfm_results (customer_id, recency, frequency, monetary, 
                                        r_score, f_score, m_score, rfm_score, segment)
                SELECT customer_id, recency, frequency, monetary, 
                       r_score, f_score, m_score, rfm_score, segment
                FROM rfm_analysis
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

                print(
                    f"⏳ Copie de {count} lignes depuis rfm_analysis vers rfm_results..."
                )
                cursor.execute(copy_query)
                conn.commit()

                # 4. Vérification
                cursor.execute("SELECT COUNT(*) FROM rfm_results;")
                loaded_count = cursor.fetchone()[0]

                print("=" * 50)
                print(f"✅ SUCCÈS : {loaded_count} clients RFM dans rfm_results !")
                print("=" * 50)

    except Exception as e:
        print(f"❌ Erreur lors du chargement RFM : {e}")
        raise e


if __name__ == "__main__":
    load_rfm_results()
