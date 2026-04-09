import sys
import os
from helpers import setup_paths

setup_paths()

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from config import DATABASE_URL, DATA_RAW_PATH
import os
import glob
import traceback


def create_raw_table(conn):
    """Détruit l'ancienne table et recrée une table brute à neuf"""
    cursor = conn.cursor()
    create_table_query = """
    DROP TABLE IF EXISTS raw_orders CASCADE;
    
    CREATE TABLE raw_orders (
        transaction_id SERIAL PRIMARY KEY,
        invoice VARCHAR(50),
        stock_code VARCHAR(50),
        description VARCHAR(500),
        quantity INT,
        invoice_date TIMESTAMP,
        price NUMERIC,
        customer_id INT,
        country VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Table raw_orders prête (recréée à neuf)")
    except Exception as e:
        print(f"⚠️ Erreur création table : {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()


def ingest_data():
    # 1. Trouver et TRIER les fichiers
    csv_pattern = os.path.join(DATA_RAW_PATH, "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))

    if not csv_files:
        print(f"❌ Aucun fichier CSV trouvé dans : {DATA_RAW_PATH}")
        return False

    print(f"📂 {len(csv_files)} fichier(s) trouvé(s).")

    # 2. Lecture et nettoyage
    dataframes = []
    for file in csv_files:
        try:
            # On utilise les noms de colonnes exacts du CSV
            df_temp = pd.read_csv(file, sep=";", encoding="utf-8", decimal=",")
            dataframes.append(df_temp)
        except Exception as e:
            print(f"❌ Erreur lecture {file} : {e}")
            return False

    df = pd.concat(dataframes, ignore_index=True)

    # Nettoyage Price
    if df["Price"].dtype == object:
        df["Price"] = df["Price"].astype(str).str.replace(",", ".").astype(float)

    # Nettoyage Date
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], format="%d/%m/%Y %H:%M", errors="coerce"
    )

    # Conversion en types natifs Python pour PostgreSQL (gère les NaN -> None)
    df = df.astype(object).where(pd.notnull(df), None)

    # 3. Ingestion
    try:
        conn = psycopg2.connect(DATABASE_URL)

        # On passe explicitement le truncate
        create_raw_table(conn)

        cursor = conn.cursor()

        insert_query = """
        INSERT INTO raw_orders (invoice, stock_code, description, quantity, 
                               invoice_date, price, customer_id, country)
        VALUES %s
        """

        # Mapping exact entre colonnes DataFrame et colonnes Table
        columns = [
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID",
            "Country",
        ]

        values = [tuple(x) for x in df[columns].to_numpy()]

        print(f"⏳ Insertion de {len(values)} lignes...")
        execute_values(cursor, insert_query, values)

        conn.commit()
        cursor.close()  # Bonne pratique : fermer le curseur dès qu'on a fini

        print(f"✅ Succès : {len(df)} lignes insérées !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
        traceback.print_exc()
        if "conn" in locals():
            conn.rollback()
        return False
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    success = ingest_data()
    exit(0 if success else 1)
