"""
Script de test - Vérifier la connexion et ingérer les données
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.ingest import ingest_data

if __name__ == "__main__":
    print("🚀 Démarrage de l'ingestion des données...")
    print("=" * 50)

    try:
        success = ingest_data()

        if success:
            print("\n" + "=" * 50)
            print("✅ Ingestion terminée avec succès !")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("❌ Ingestion échouée")
            print("=" * 50)
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)
