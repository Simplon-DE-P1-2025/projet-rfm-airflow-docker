"""
CLV Forecast — Prévision de la Valeur à Vie Clientèle
Projette revenue future basée sur historique et segment de client
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


def clv_forecast(truncate=True):
    """Prévision CLV (Customer Lifetime Value) pour 12 mois"""
    conn = None
    try:
        # 1. Création de la table clv
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if truncate:
            cursor.execute("DROP TABLE IF EXISTS clv_forecast;")
            print("🗑️ Table clv_forecast supprimée.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clv_forecast (
                customer_id INT PRIMARY KEY,
                segment VARCHAR(50),
                historical_value NUMERIC,
                avg_monthly_value NUMERIC,
                clv_12months NUMERIC,
                clv_24months NUMERIC,
                growth_rate NUMERIC,
                forecast_confidence VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
        print("✅ Table clv_forecast créée.")

        # 2. Calcul CLV
        print("💰 Calcul du CLV forecast...")
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        # Récupère données clients + segment
        query = """
            SELECT c.customer_id, c.segment, c.monetary, c.recency, c.frequency,
                   o.invoice_date, o.price, o.quantity
            FROM rfm_analysis c
            JOIN raw_orders o ON c.customer_id = o.customer_id
            WHERE o.customer_id IS NOT NULL AND o.quantity > 0 AND o.price > 0;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("⚠️ Aucune donnée CLV trouvée.")

        df["amount"] = df["price"] * df["quantity"]
        max_date = df["invoice_date"].max()

        # Grouper par client
        clv_df = (
            df.groupby("customer_id")
            .agg(
                {
                    "segment": "first",
                    "amount": "sum",  # Lifetime value to date
                    "invoice_date": ["min", "max"],  # First and last purchase
                }
            )
            .reset_index()
        )

        clv_df.columns = [
            "customer_id",
            "segment",
            "historical_value",
            "first_purchase",
            "last_purchase",
        ]

        # Calcul fréquence par mois
        clv_df["months_active"] = (
            (clv_df["last_purchase"] - clv_df["first_purchase"]).dt.days / 30
        ).clip(lower=1)
        clv_df["avg_monthly_value"] = (
            clv_df["historical_value"] / clv_df["months_active"]
        )

        # Ajustement par segment (facteurs croissance)
        segment_factors = {
            "Champions": 1.15,  # +15% growth
            "Clients Fidèles": 1.10,  # +10%
            "Nouveaux Clients": 1.20,  # +20% (nouveaux = croissance potentielle)
            "Clients Potentiels": 1.08,  # +8%
            "À Risque": 0.85,  # -15% (risque de perte)
            "Perdus": 0.50,  # -50% (très peu de chance)
            "À Réactiver": 1.05,  # +5% (réactivation)
            "Moyens": 1.00,  # Stable
        }

        clv_df["growth_rate"] = clv_df["segment"].map(segment_factors).fillna(1.0)

        # Prévisions (12 et 24 mois)
        clv_df["clv_12months"] = (
            clv_df["avg_monthly_value"] * 12 * clv_df["growth_rate"]
        )
        clv_df["clv_24months"] = (
            clv_df["avg_monthly_value"] * 24 * clv_df["growth_rate"]
        )

        # Confiance basée sur recency et historique
        def get_confidence(months_active, historical_value):
            if historical_value < 100:
                return "🟡 Low"
            elif months_active < 3:
                return "🟡 Medium"
            elif months_active >= 12:
                return "🟢 High"
            else:
                return "🟡 Medium"

        clv_df["forecast_confidence"] = clv_df.apply(
            lambda row: get_confidence(row["months_active"], row["historical_value"]),
            axis=1,
        )

        print(f"📊 Prévisions CLV pour {len(clv_df)} clients calculées.")

        # 3. Insertion
        insert_query = """
            INSERT INTO clv_forecast (customer_id, segment, historical_value,
                                     avg_monthly_value, clv_12months, clv_24months,
                                     growth_rate, forecast_confidence)
            VALUES %s
            ON CONFLICT (customer_id) DO UPDATE SET
                segment = EXCLUDED.segment,
                historical_value = EXCLUDED.historical_value,
                avg_monthly_value = EXCLUDED.avg_monthly_value,
                clv_12months = EXCLUDED.clv_12months,
                clv_24months = EXCLUDED.clv_24months,
                growth_rate = EXCLUDED.growth_rate,
                forecast_confidence = EXCLUDED.forecast_confidence,
                updated_at = CURRENT_TIMESTAMP;
        """

        values = (
            clv_df[
                [
                    "customer_id",
                    "segment",
                    "historical_value",
                    "avg_monthly_value",
                    "clv_12months",
                    "clv_24months",
                    "growth_rate",
                    "forecast_confidence",
                ]
            ]
            .astype(object)
            .values.tolist()
        )

        execute_values(cursor, insert_query, values)
        conn.commit()

        # Stats
        avg_clv_12 = clv_df["clv_12months"].mean()
        total_clv_24 = clv_df["clv_24months"].sum()
        print(f"✅ CLV Forecast: €{total_clv_24:,.0f} expected revenue (24 months) !")

        engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Erreur CLV Forecast : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    clv_forecast()
