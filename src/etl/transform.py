import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from config.config import DATABASE_URL

def transform_rfm():
    # Connexion
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Création de la table RFM
    create_rfm_table = """
    CREATE TABLE IF NOT EXISTS rfm_analysis (
        customer_id INT PRIMARY KEY,
        recency INT,
        frequency INT,
        monetary NUMERIC
    );
    """
    cursor.execute(create_rfm_table)
    conn.commit()

    # Lecture des données brutes depuis PostgreSQL
    query = "SELECT customer_id, invoice_date, price, quantity FROM raw_orders WHERE customer_id IS NOT NULL;"
    df = pd.read_sql(query, conn)

    # Fermer la connexion initiale pour la lecture
    conn.close()

    # Calcul RFM
    # Recency: Dernier achat (différence avec la date max du dataset)
    max_date = df['invoice_date'].max()
    df['recency_days'] = (max_date - df['invoice_date']).dt.days
    
    # Calcul du montant total par ligne (price * quantity)
    df['amount'] = df['price'] * df['quantity']
    
    # Agrégation par client
    rfm = df.groupby('customer_id').agg({
        'recency_days': 'min',      # Moins de jours = plus récent
        'invoice_date': 'count',    # Fréquence (nombre de transactions)
        'amount': 'sum'             # Montant total (Monetary)
    }).reset_index()
    
    # Renommage
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Nettoyage des valeurs négatives (annulations) si nécessaire
    rfm = rfm[rfm['monetary'] > 0]

    # Reconnexion pour l'insertion
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Insertion dans la table RFM (méthode rapide par batch)
    insert_query = """
    INSERT INTO rfm_analysis (customer_id, recency, frequency, monetary)
    VALUES %s
    ON CONFLICT (customer_id) DO UPDATE SET
        recency = EXCLUDED.recency,
        frequency = EXCLUDED.frequency,
        monetary = EXCLUDED.monetary;
    """
    
    # Conversion manuelle en types Python natifs pour éviter les types numpy
    values = []
    for idx, row in rfm.iterrows():
        values.append((
            int(row['customer_id']),
            int(row['recency']),
            int(row['frequency']),
            float(row['monetary'])
        ))
    if values:
        execute_values(cursor, insert_query, values)
        conn.commit()

    cursor.close()
    conn.close()
    print(f"✅ Analyse RFM terminée : {len(rfm)} clients traités et stockés dans rfm_analysis.")

if __name__ == "__main__":
    transform_rfm()