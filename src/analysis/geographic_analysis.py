"""
Geographic Drill-Down Analysis — Expansion géographique par pays
Identifie opportunités de marché et performance par région
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


def geographic_analysis(truncate=True):
    """Analyse RFM au niveau géographique (pays)"""
    conn = None
    try:
        # 1. Création de la table géographique
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if truncate:
            cursor.execute("DROP TABLE IF EXISTS geographic_analysis;")
            print("🗑️ Table geographic_analysis supprimée.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS geographic_analysis (
                country VARCHAR(100) PRIMARY KEY,
                total_customers INT,
                total_orders INT,
                total_revenue NUMERIC,
                avg_order_value NUMERIC,
                avg_customer_value NUMERIC,
                recency_avg INT,
                frequency_avg NUMERIC,
                monetary_avg NUMERIC,
                market_growth_potential VARCHAR(50),
                priority_rank INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
        print("✅ Table geographic_analysis créée.")

        # 2. Calcul géographique
        print("🌍 Analyse géographique...")
        engine_url = DATABASE_URL.replace("postgres://", "postgresql://")
        engine = create_engine(engine_url)

        query = """
            SELECT country, customer_id, invoice, invoice_date, price, quantity
            FROM raw_orders
            WHERE customer_id IS NOT NULL AND quantity > 0 AND price > 0;
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            raise ValueError("⚠️ Aucune donnée géographique trouvée.")

        df["amount"] = df["price"] * df["quantity"]
        max_date = df["invoice_date"].max()

        # Agrégation par pays
        geo_df = (
            df.groupby("country")
            .agg(
                {
                    "customer_id": "nunique",  # Total customers
                    "invoice": "nunique",  # Total orders
                    "amount": "sum",  # Total revenue
                }
            )
            .reset_index()
        )

        geo_df.columns = ["country", "total_customers", "total_orders", "total_revenue"]

        # Métriques additionnelles
        geo_df["avg_order_value"] = geo_df["total_revenue"] / geo_df["total_orders"]
        geo_df["avg_customer_value"] = (
            geo_df["total_revenue"] / geo_df["total_customers"]
        )

        # RFM par pays
        for country in geo_df["country"]:
            country_data = df[df["country"] == country]
            recency_avg = (
                max_date - country_data.groupby("customer_id")["invoice_date"].max()
            ).dt.days.mean()
            frequency_avg = (
                country_data.groupby("customer_id")["invoice"].nunique().mean()
            )
            monetary_avg = country_data.groupby("customer_id")["amount"].sum().mean()

            idx = geo_df[geo_df["country"] == country].index[0]
            geo_df.loc[idx, "recency_avg"] = int(recency_avg)
            geo_df.loc[idx, "frequency_avg"] = frequency_avg
            geo_df.loc[idx, "monetary_avg"] = monetary_avg

        # Classification d'opportunité
        def classify_market(row):
            """Classification du potentiel de marché"""
            revenue = row["total_revenue"]
            customers = row["total_customers"]
            recency = row["recency_avg"]

            # Haut revenue + basse recency = etabli
            # Bas revenue + basse recency = opportunité croissante
            # Haut revenue + haute recency = déclin
            # Bas revenue + haute recency = stagnant

            if revenue >= geo_df["total_revenue"].quantile(0.75):
                if recency <= geo_df["recency_avg"].quantile(0.25):
                    return "🟢 Established Leader"
                else:
                    return "🟠 Declining"
            else:
                if recency <= geo_df["recency_avg"].quantile(0.50):
                    return "🟡 Growing Opportunity"
                else:
                    return "🔴 Emerging Market"

        geo_df["market_growth_potential"] = geo_df.apply(classify_market, axis=1)

        # Ranking
        geo_df = geo_df.sort_values("total_revenue", ascending=False).reset_index(
            drop=True
        )
        geo_df["priority_rank"] = range(1, len(geo_df) + 1)

        print(f"🌐 Analyse de {len(geo_df)} pays terminée.")

        # 3. Insertion
        insert_query = """
            INSERT INTO geographic_analysis (country, total_customers, total_orders, total_revenue,
                                            avg_order_value, avg_customer_value,
                                            recency_avg, frequency_avg, monetary_avg,
                                            market_growth_potential, priority_rank)
            VALUES %s
            ON CONFLICT (country) DO UPDATE SET
                total_customers = EXCLUDED.total_customers,
                total_orders = EXCLUDED.total_orders,
                total_revenue = EXCLUDED.total_revenue,
                avg_order_value = EXCLUDED.avg_order_value,
                avg_customer_value = EXCLUDED.avg_customer_value,
                recency_avg = EXCLUDED.recency_avg,
                frequency_avg = EXCLUDED.frequency_avg,
                monetary_avg = EXCLUDED.monetary_avg,
                market_growth_potential = EXCLUDED.market_growth_potential,
                priority_rank = EXCLUDED.priority_rank,
                updated_at = CURRENT_TIMESTAMP;
        """

        values = (
            geo_df[
                [
                    "country",
                    "total_customers",
                    "total_orders",
                    "total_revenue",
                    "avg_order_value",
                    "avg_customer_value",
                    "recency_avg",
                    "frequency_avg",
                    "monetary_avg",
                    "market_growth_potential",
                    "priority_rank",
                ]
            ]
            .astype(object)
            .values.tolist()
        )

        execute_values(cursor, insert_query, values)
        conn.commit()

        print(
            f"✅ Geographic analysis: Top 3 pays = {geo_df.head(3)['country'].tolist()} !"
        )

        engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Erreur Geographic Analysis : {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    geographic_analysis()
