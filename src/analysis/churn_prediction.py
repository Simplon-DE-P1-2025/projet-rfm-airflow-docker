"""
Churn Prediction — Prédiction Légère de Désabonnement Clients
Scoring basé sur Recency (jours depuis dernier achat) et Frequency trend
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
import traceback
from datetime import timedelta

from helpers import setup_paths

setup_paths()
from config import DATABASE_URL


def churn_prediction(truncate=True):
    """Prédiction simple de churn basée sur recency et volatilité"""
    conn = None
    try:
        # 1. Création de la table churn
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if truncate:
            cursor.execute("DROP TABLE IF EXISTS churn_risk;")
            print("🗑️ Table churn_risk supprimée.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS churn_risk (
                customer_id INT PRIMARY KEY,
                recency INT,
                frequency INT,
                days_since_first_purchase INT,
                purchase_frequency_per_month NUMERIC,
                months_active INT,
                churn_score NUMERIC,
                churn_risk VARCHAR(50),
                recommendation VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
        print("✅ Table churn_risk créée.")

        # 2. Calcul du Churn Risk
        print("🚨 Calcul du churn risk...")
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        query = """
            SELECT customer_id, invoice_date
            FROM raw_orders
            WHERE customer_id IS NOT NULL
            ORDER BY invoice_date;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("⚠️ Aucune donnée trouvée pour churn.")

        max_date = df["invoice_date"].max()

        # Par client : recency, frequency, lifecycle
        churn_df = (
            df.groupby("customer_id")
            .agg(
                {
                    "invoice_date": [
                        lambda x: (max_date - x.max()).days,  # Recency
                        "count",  # Frequency
                        "min",  # First purchase
                    ]
                }
            )
            .reset_index()
        )

        churn_df.columns = ["customer_id", "recency", "frequency", "first_purchase"]
        churn_df["days_since_first"] = (
            churn_df["first_purchase"].max() - churn_df["first_purchase"]
        ).dt.days
        churn_df["months_active"] = (churn_df["days_since_first"] / 30).astype(int)

        # Purchase frequency par mois
        churn_df["purchase_freq_per_month"] = churn_df["frequency"] / (
            (churn_df["days_since_first"] / 30).replace(0, 1)
        )

        # Churn score (0-100)
        # Haut recency (>180 jours) = haut risque
        # Basse fréquence (< 1 par mois) = haut risque
        recency_weight = pd.qcut(churn_df["recency"], 5, labels=[20, 40, 60, 80, 95])
        frequency_weight = pd.qcut(
            churn_df["purchase_freq_per_month"],
            5,
            labels=[80, 60, 40, 20, 5],
            duplicates="drop",
        )

        churn_df["recency_weight"] = recency_weight.astype(int)
        churn_df["freq_weight"] = frequency_weight.astype(int)
        churn_df["churn_score"] = (
            churn_df["recency_weight"] * 0.6 + churn_df["freq_weight"] * 0.4
        )

        # Classification
        def classify_risk(score):
            if score >= 80:
                return "🔴 High"
            elif score >= 60:
                return "🟠 Medium"
            elif score >= 40:
                return "🟡 Low"
            else:
                return "🟢 Very Low"

        churn_df["churn_risk"] = churn_df["churn_score"].apply(classify_risk)

        # Recommendations
        def get_recommendation(score, recency, freq):
            if score >= 80:
                return "🎯 Win-back campaign + special offer"
            elif score >= 60:
                return "📧 Engagement email + coupon"
            elif score >= 40:
                return "💌 Regular newsletter"
            else:
                return "🎉 VIP loyalty program"

        churn_df["recommendation"] = churn_df.apply(
            lambda row: get_recommendation(
                row["churn_score"], row["recency"], row["purchase_freq_per_month"]
            ),
            axis=1,
        )

        print(f"📊 Analyse churn de {len(churn_df)} clients.")

        # 3. Insertion
        insert_query = """
            INSERT INTO churn_risk (customer_id, recency, frequency, 
                                   days_since_first_purchase, purchase_frequency_per_month,
                                   months_active, churn_score, churn_risk, recommendation)
            VALUES %s
            ON CONFLICT (customer_id) DO UPDATE SET
                recency = EXCLUDED.recency,
                frequency = EXCLUDED.frequency,
                days_since_first_purchase = EXCLUDED.days_since_first_purchase,
                purchase_frequency_per_month = EXCLUDED.purchase_frequency_per_month,
                months_active = EXCLUDED.months_active,
                churn_score = EXCLUDED.churn_score,
                churn_risk = EXCLUDED.churn_risk,
                recommendation = EXCLUDED.recommendation,
                updated_at = CURRENT_TIMESTAMP;
        """

        values = (
            churn_df[
                [
                    "customer_id",
                    "recency",
                    "frequency",
                    "days_since_first",
                    "purchase_freq_per_month",
                    "months_active",
                    "churn_score",
                    "churn_risk",
                    "recommendation",
                ]
            ]
            .astype(object)
            .values.tolist()
        )

        execute_values(cursor, insert_query, values)
        conn.commit()

        # Stats
        high_risk = len(churn_df[churn_df["churn_score"] >= 80])
        print(f"✅ Churn predictions: {high_risk} clients à haut risque détectés !")

        engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Erreur Churn Prediction : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    churn_prediction()
