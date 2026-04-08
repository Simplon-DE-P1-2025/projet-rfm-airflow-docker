#!/bin/bash
# Script d'initialisation Airflow
# À exécuter une seule fois avant de démarrer Airflow

set -e

echo "🔄 Initialisation de la base Airflow..."

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
until pg_isready -h postgres -U $DB_USER -d $DB_NAME; do
  sleep 1
done

echo "✅ PostgreSQL est prêt"

# Initialiser la base Airflow
echo "🔧 Initialisation de la base Airflow..."
airflow db migrate

# Créer l'utilisateur admin
echo "👤 Création de l'utilisateur admin..."
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com 2>/dev/null || echo "L'utilisateur admin existe déjà"

echo "✅ Initialisation terminée !"
