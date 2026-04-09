"""
Analyse des données CSV raw pour valider l'ETL & Dashboard
"""

import pandas as pd
import os

# Lire juste les 100 premières lignes de chaque fichier
file1 = "data/raw/online_retail_II-2009.csv"
file2 = "data/raw/online_retail_II-2010.csv"

print("=" * 70)
print("📊 ANALYSE DES DONNÉES CSV RAW")
print("=" * 70)

df1 = pd.read_csv(file1, sep=";", decimal=",", nrows=100)
df2 = pd.read_csv(file2, sep=";", decimal=",", nrows=100)

# Fusion
df_all = pd.concat([df1, df2], ignore_index=True)

print("\n✅ STRUCTURE DES DONNÉES:")
print(f"  Colonnes: {list(df1.columns)}")
print(f"  Types:\n{df1.dtypes}")

print(f"\n📈 VOLUME (Sample 200 lignes):")
print(f"  Total: {len(df_all)} lignes")
print(f'  Client IDs uniques: {df_all["Customer ID"].nunique()}')
print(f'  Factures uniques: {df_all["Invoice"].nunique()}')
print(f'  Pays: {df_all["Country"].nunique()}')

print(f"\n🌍 Top 5 Pays:")
for country, count in df_all["Country"].value_counts().head().items():
    print(f"    {country}: {count} transactions")

print(f"\n💰 MONTANTS (Quantity * Price):")
df_all["amount"] = df_all["Quantity"] * df_all["Price"]
print(f'    Min: {df_all["amount"].min():.2f}€')
print(f'    Max: {df_all["amount"].max():.2f}€')
print(f'    Moy: {df_all["amount"].mean():.2f}€')
print(f'    Total: {df_all["amount"].sum():.2f}€')

print(f"\n⚠️ ANOMALIES DÉTECTÉES:")
print(f'    Quantity < 0: {(df_all["Quantity"] < 0).sum()} lignes')
print(f'    Price < 0: {(df_all["Price"] < 0).sum()} lignes')
print(f'    Customer ID NULL: {df_all["Customer ID"].isna().sum()} lignes')
print(f'    Description vide: {df_all["Description"].isna().sum()} lignes')

print(f"\n📋 ÉCHANTILLON DE CLIENTS:")
customers = df_all["Customer ID"].dropna().unique()[:10]
print(f"    {customers}")

print(f"\n📅 PLAGE DE DATES:")
df_all["InvoiceDate"] = pd.to_datetime(df_all["InvoiceDate"], format="%d/%m/%Y %H:%M")
print(f'    Min: {df_all["InvoiceDate"].min()}')
print(f'    Max: {df_all["InvoiceDate"].max()}')
print(
    f'    Durée: {(df_all["InvoiceDate"].max() - df_all["InvoiceDate"].min()).days} jours'
)

print(f"\n📊 DISTRIBUTION PAR CLIENT (Sample):")
client_freq = df_all[df_all["Customer ID"].notna()].groupby("Customer ID").size()
print(f"    Transactions par client - Min: {client_freq.min()}")
print(f"    Transactions par client - Max: {client_freq.max()}")
print(f"    Transactions par client - Moy: {client_freq.mean():.1f}")

print("\n" + "=" * 70)
