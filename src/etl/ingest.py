"""
Script d'ingestion - Charge les données brutes CSV dans PostgreSQL
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values  # Outil pour l'insertion rapide en lot
from config.config import DATABASE_URL, DATA_RAW_PATH
import os
import glob


def create_raw_table(conn):
    """Crée la table brute dans PostgreSQL"""
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_orders (
        transaction_id SERIAL PRIMARY KEY,
        invoice VARCHAR(50),
        stock_code VARCHAR(50),
        description VARCHAR(255),
        quantity INT,
        invoice_date TIMESTAMP,
        price NUMERIC,
        customer_id INT,
        country VARCHAR(100)
    );
    """

    try:
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Table raw_orders prête")
    except Exception as e:
        print(f"⚠️ Erreur lors de la création de la table : {e}")
        conn.rollback()
    finally:
        cursor.close()


def ingest_data():
    """Ingère les données depuis les fichiers CSV vers PostgreSQL"""

    # 1. Trouver tous les fichiers CSV dans le dossier
    csv_pattern = os.path.join(DATA_RAW_PATH, "*.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        print(f"❌ Aucun fichier CSV trouvé dans : {DATA_RAW_PATH}")
        return False

    print(f"📂 {len(csv_files)} fichier(s) CSV trouvé(s).")

    # 2. Lire et combiner les fichiers
    dataframes = []
    for file in csv_files:
        print(f"   Lecture de : {os.path.basename(file)}")
        try:
            # Encodage défini sur UTF-8 selon votre format
            df_temp = pd.read_csv(file, sep=";", encoding="utf-8", decimal=",")
            dataframes.append(df_temp)
        except Exception as e:
            print(f"❌ Erreur de lecture sur {file} : {e}")
            return False

    # Fusionner tous les tableaux en un seul
    df = pd.concat(dataframes, ignore_index=True)

    # Forcer la conversion de la colonne Price en numérique (sécurité)
    if df["Price"].dtype == object:
        df["Price"] = df["Price"].astype(str).str.replace(",", ".").astype(float)

    # Convertir proprement la date au format PostgreSQL (Année-Mois-Jour)
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], format="%d/%m/%Y %H:%M", errors="coerce"
    )

    # Forcer le tableau en type 'object' pour que Pandas accepte les vrais 'None'
    # (Évite l'erreur 'integer out of range' avec les identifiants clients manquants)
    df = df.astype(object).where(pd.notnull(df), None)

    print(f"📊 Données combinées : {len(df)} lignes prêtes pour l'ingestion.")

    # 3. Connexion et Ingestion
    try:
        conn = psycopg2.connect(DATABASE_URL)
        create_raw_table(conn)
        cursor = conn.cursor()

        print("⏳ Insertion en base en cours (Batch)...")

        # Préparer la requête
        insert_query = """
        INSERT INTO raw_orders (invoice, stock_code, description, quantity, 
                               invoice_date, price, customer_id, country)
        VALUES %s
        """

        # Convertir le DataFrame en une liste de tuples
        columns_to_extract = [
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID",
            "Country",
        ]
        values = [tuple(x) for x in df[columns_to_extract].to_numpy()]

        # Exécuter l'insertion rapide
        execute_values(cursor, insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Succès : {len(df)} lignes insérées dans PostgreSQL !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'insertion en base : {e}")
        return False


if __name__ == "__main__":
    success = ingest_data()
    exit(0 if success else 1)
