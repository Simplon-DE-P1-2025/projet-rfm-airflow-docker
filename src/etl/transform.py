import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
from config.config import DATABASE_URL
import traceback


def transform_rfm(truncate=True):
    """Calcule le RFM et charge les données dans la table Silver rfm_analysis"""
    conn = None
    try:
        # 1. Préparation de la table avec psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rfm_analysis (
                customer_id INT PRIMARY KEY,
                recency INT,
                frequency INT,
                monetary NUMERIC
            );
        """
        )

        if truncate:
            cursor.execute("TRUNCATE TABLE rfm_analysis;")
            print("⟳ Table rfm_analysis vidée.")

        conn.commit()

        # 2. Lecture des données avec SQLAlchemy (pour éviter le UserWarning)
        print("📖 Lecture des données depuis PostgreSQL...")
        # On remplace postgres:// par postgresql:// pour SQLAlchemy si nécessaire
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        query = """
            SELECT customer_id, invoice, invoice_date, price, quantity 
            FROM raw_orders 
            WHERE customer_id IS NOT NULL;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            print("⚠️ Aucune donnée trouvée pour le calcul RFM.")
            return False

        # 3. Calculs RFM
        print("🧪 Calcul des scores RFM...")

        # Montant total par ligne
        df["amount"] = df["price"] * df["quantity"]

        # Date de référence pour la récence
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

        # Nettoyage des montants négatifs ou nuls
        rfm = rfm[rfm["monetary"] > 0]

        # 4. Insertion par batch (CORRECTION DU BUG NUMPY)
        print(f"⏳ Insertion de {len(rfm)} profils clients...")

        insert_query = """
            INSERT INTO rfm_analysis (customer_id, recency, frequency, monetary)
            VALUES %s
            ON CONFLICT (customer_id) DO UPDATE SET
                recency = EXCLUDED.recency,
                frequency = EXCLUDED.frequency,
                monetary = EXCLUDED.monetary;
        """

        # SOLUTION : Conversion en types Python natifs pour éviter l'erreur "schema np"
        # .astype(object) transforme les types numpy en types python lors du passage en liste
        values = rfm.astype(object).values.tolist()

        # On utilise le cursor ouvert au début
        execute_values(cursor, insert_query, values)
        conn.commit()

        cursor.close()
        print(f"✅ Analyse RFM terminée : {len(rfm)} clients stockés.")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la transformation RFM : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    transform_rfm()
