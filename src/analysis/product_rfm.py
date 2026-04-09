"""
Product-Level RFM Analysis — Analyse RFM par Produit
Identifie les produits stars, orphelins et leurs performances par segment
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
import traceback

from helpers import setup_paths

setup_paths()
from config import DATABASE_URL


def product_rfm_analysis(truncate=True):
    """Calcule RFM au niveau produit (stock_code)"""
    conn = None
    try:
        # 1. Création de la table produit-RFM
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if truncate:
            cursor.execute("DROP TABLE IF EXISTS product_rfm;")
            print("🗑️ Table product_rfm supprimée.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS product_rfm (
                stock_code VARCHAR(50) PRIMARY KEY,
                product_name VARCHAR(500),
                recency INT,
                frequency INT,
                monetary NUMERIC,
                r_score INT,
                f_score INT,
                m_score INT,
                total_customers INT,
                avg_price NUMERIC,
                total_quantity INT,
                performance VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
        print("✅ Table product_rfm créée.")

        # 2. Calcul du Product-RFM
        print("📊 Calcul du RFM par produit...")
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        query = """
            SELECT stock_code, description, price, quantity, invoice_date, customer_id
            FROM raw_orders
            WHERE customer_id IS NOT NULL AND quantity > 0 AND price > 0;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("⚠️ Aucune donnée trouvée pour le RFM produit.")

        # Calculs RFM
        df["amount"] = df["price"] * df["quantity"]
        max_date = df["invoice_date"].max()

        product_rfm = (
            df.groupby("stock_code")
            .agg(
                {
                    "invoice_date": lambda x: (max_date - x.max()).days,  # Recency
                    "customer_id": "nunique",  # Nombre de clients distincts
                    "description": "first",  # Nom produit
                    "amount": "sum",  # Montant total
                    "price": "mean",  # Prix moyen
                    "quantity": "sum",  # Quantité totale
                }
            )
            .reset_index()
        )

        product_rfm.columns = [
            "stock_code",
            "recency",
            "total_customers",
            "product_name",
            "monetary",
            "avg_price",
            "total_quantity",
        ]

        # Scores RFM (1-5)
        product_rfm["r_score"] = pd.qcut(
            product_rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
        ).astype(int)
        product_rfm["f_score"] = pd.qcut(
            product_rfm["total_customers"].rank(method="first"),
            5,
            labels=[1, 2, 3, 4, 5],
        ).astype(int)
        product_rfm["m_score"] = pd.qcut(
            product_rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
        ).astype(int)

        # Classification de performance
        def classify_performance(row):
            """Classifie les produits par performance"""
            r = row["r_score"]
            f = row["f_score"]
            m = row["m_score"]
            avg_score = (r + f + m) / 3
            if avg_score >= 4:
                return "Star"  # Produit vedette
            elif avg_score >= 3:
                return "Strong"  # Produit fort
            elif avg_score >= 2:
                return "Stable"  # Produit stable
            else:
                return "Orphan"  # Produit orphelin

        product_rfm["performance"] = product_rfm.apply(classify_performance, axis=1)

        print(f"🎯 Analyse de {len(product_rfm)} produits terminée.")

        # 3. Insertion en base
        insert_query = """
            INSERT INTO product_rfm (stock_code, product_name, recency, frequency, monetary,
                                    r_score, f_score, m_score, total_customers, avg_price,
                                    total_quantity, performance)
            VALUES %s
            ON CONFLICT (stock_code) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                recency = EXCLUDED.recency,
                frequency = EXCLUDED.frequency,
                monetary = EXCLUDED.monetary,
                r_score = EXCLUDED.r_score,
                f_score = EXCLUDED.f_score,
                m_score = EXCLUDED.m_score,
                total_customers = EXCLUDED.total_customers,
                avg_price = EXCLUDED.avg_price,
                total_quantity = EXCLUDED.total_quantity,
                performance = EXCLUDED.performance,
                updated_at = CURRENT_TIMESTAMP;
        """

        values = (
            product_rfm[
                [
                    "stock_code",
                    "product_name",
                    "recency",
                    "total_customers",
                    "monetary",
                    "r_score",
                    "f_score",
                    "m_score",
                    "total_customers",
                    "avg_price",
                    "total_quantity",
                    "performance",
                ]
            ]
            .astype(object)
            .values.tolist()
        )

        execute_values(cursor, insert_query, values)
        conn.commit()

        engine.dispose()
        print(f"✅ Product-RFM insérés : {len(product_rfm)} produits analysés !")
        return True

    except Exception as e:
        print(f"❌ Erreur Product-RFM : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    product_rfm_analysis()
