"""
Script de test - Exécuter la transformation RFM
"""

import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.transform import transform_rfm

if __name__ == "__main__":
    print("🚀 Démarrage de la transformation RFM...")
    print("=" * 50)

    try:
        transform_rfm()

        print("\n" + "=" * 50)
        print("✅ Transformation terminée avec succès !")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)
