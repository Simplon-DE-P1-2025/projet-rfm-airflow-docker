# 📊 Pipeline RFM - Airflow & Docker

Une pipeline de données complète pour analyser le comportement client avec la métrique **RFM** (Recency, Frequency, Monetary) orchestrée par **Apache Airflow** et containerisée avec **Docker**.

---

## 🎯 À Propos

Ce projet implémente une pipeline ETL (Extract, Transform, Load) qui :
- **Ingère** des données de transactions depuis des fichiers CSV
- **Transforme** les données pour calculer les scores RFM par client
- **Charge** les résultats dans PostgreSQL
- **Orchestre** le tout avec Airflow (exécution automatique quotidienne)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE RFM                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CSV (data/raw/)                                             │
│      ↓                                                        │
│  ┌──────────────────────────────────────────────────┐        │
│  │  TÂCHE 1 : INGESTION                             │        │
│  │  • Lecture des fichiers CSV                      │        │
│  │  • Chargement dans PostgreSQL (raw_data)         │        │
│  └──────────────────────────────────────────────────┘        │
│      ↓                                                        │
│  ┌──────────────────────────────────────────────────┐        │
│  │  TÂCHE 2 : TRANSFORMATION RFM                    │        │
│  │  • Calcul Recency (jours depuis dernier achat)   │        │
│  │  • Calcul Frequency (nombre d'achats)            │        │
│  │  • Calcul Monetary (total des dépenses)          │        │
│  │  • Scoring RFM (1-5 pour chaque dimension)       │        │
│  └──────────────────────────────────────────────────┘        │
│      ↓                                                        │
│  ┌──────────────────────────────────────────────────┐        │
│  │  TÂCHE 3 : CHARGEMENT                            │        │
│  │  • Sauvegarde dans PostgreSQL (rfm_results)      │        │
│  │  • Export en CSV (data/processed/)                │        │
│  └──────────────────────────────────────────────────┘        │
│      ↓                                                        │
│  PostgreSQL Database                                        │
│  - Données brutes (raw_data)                                │
│  - Résultats RFM (rfm_results)                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Orchestrateur : Apache Airflow (interface web http://localhost:8080)
Conteneurisation : Docker Compose
Base de données : PostgreSQL 15
```

---

## 📋 Prérequis

| Composant | Version | Installation |
|-----------|---------|--------------|
| **Docker Desktop** | 4.0+ | [Télécharger](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | 1.29+ | Inclus dans Docker Desktop |
| **PowerShell** | 5.0+ | Disponible sur Windows |

**Vérification :**
```powershell
docker --version
docker-compose --version
```

---

## 🚀 Démarrage Rapide

### 1️⃣ Préparation

```powershell
cd "d:\data eng\projet-rfm-airflow-docker"

# Créer les dossiers nécessaires
mkdir -p airflow/logs
mkdir -p data/raw
mkdir -p data/processed
```

### 2️⃣ Initialisation (une seule fois)

```powershell
# Nettoyer les anciens conteneurs
docker-compose down -v

# Lancer PostgreSQL
docker-compose up -d postgres

# Attendre ~15 secondes
Start-Sleep -Seconds 15

# Initialiser la base Airflow
docker-compose run --rm airflow-webserver airflow db migrate

# Créer l'utilisateur administrateur
docker-compose run --rm airflow-webserver airflow users create `
  --username admin `
  --password admin `
  --firstname Admin `
  --lastname User `
  --role Admin `
  --email admin@example.com
```

### 3️⃣ Lancer les Services

```powershell
# Démarrer tous les conteneurs
docker-compose up -d

# Attendre 2-3 minutes pour que Airflow démarre
Start-Sleep -Seconds 180

# Vérifier l'état
docker-compose ps
```

### 4️⃣ Accéder à Airflow

Ouvrez votre navigateur : **http://localhost:8080**

**Identifiants :**
- 👤 Username : `admin`
- 🔐 Password : `admin`

---

## 📖 Utilisation

### Déclencher le DAG manuellement

1. **Dans l'interface Airflow UI :**
   - Cherchez le DAG `rfm_pipeline`
   - Cliquez sur le toggle pour l'**activer** (ON)
   - Cliquez sur **"Trigger DAG"**

2. **Ou en ligne de commande :**
   ```powershell
   docker-compose exec airflow-webserver airflow dags trigger rfm_pipeline
   ```

### Monitoring

- **Logs en direct :**
  ```powershell
  docker-compose logs -f airflow-webserver
  ```

- **État des tâches :**
  Consultez la page "Graph View" dans Airflow UI

- **Résultats :**
  ```powershell
  # Les résultats sont sauvegardés dans
  data/processed/rfm_results.csv
  ```

---

## 📁 Structure du Projet

```
projet-rfm-airflow-docker/
│
├── src/                           # Code source
│   ├── dags/
│   │   └── rfm_pipeline_dag.py    # DAG Airflow (3 tâches)
│   └── etl/
│       ├── ingest.py              # Ingestion CSV → PostgreSQL
│       ├── transform.py           # Calcule les scores RFM
│       ├── load.py                # Charge RFM → PostgreSQL
│       └── helpers.py             # Utilitaires d'import
│
├── data/
│   ├── raw/                       # 📥 CSV brutes à ingérer
│   │   ├── online_retail_II-2009.csv
│   │   └── online_retail_II-2010.csv
│   └── processed/                 # 📤 RFM résultats
│       └── rfm_results.csv
│
├── config/
│   ├── config.py                  # Configuration centralisée
│   └── __init__.py
│
├── docker/
│   └── Dockerfile                 # Image Airflow custom
│
├── airflow/
│   └── logs/                       # 📝 Logs Airflow
│
├── docker-compose.yml             # Orchestration services
├── .env                           # Variables d'environnement
├── requirements.txt               # Dépendances Python
├── .gitignore
└── README.md                      # Ce fichier
```

---

## 🔧 Configuration

### Variables d'environnement (`.env`)

```dotenv
# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=rfm_db
DB_USER=rfm_user
DB_PASSWORD=rfm_password

# Airflow
AIRFLOW_HOME=/airflow
AIRFLOW__CORE__DAGS_FOLDER=/airflow/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

---

## 📊 Vérification du Fonctionnement

### ✅ Checklist après démarrage

- [ ] Tous les conteneurs sont "Up" : `docker-compose ps`
- [ ] http://localhost:8080 accessible
- [ ] Page de login Airflow visible
- [ ] DAG `rfm_pipeline` affiché dans la liste
- [ ] Trois tâches visibles dans le DAG

### ✅ Après exécution du DAG

- [ ] Les 3 tâches deviennent vertes (succès)
- [ ] Fichier `data/processed/rfm_results.csv` créé
- [ ] PostgreSQL contient les tables :
  ```powershell
  # Vérifier les données
  docker-compose exec postgres psql -U rfm_user -d rfm_db -c "SELECT COUNT(*) FROM rfm_results;"
  ```

---

## 📋 Commandes Utiles

| Commande | Action |
|----------|--------|
| `docker-compose up -d` | Démarrer tous les services |
| `docker-compose down` | Arrêter tous les services |
| `docker-compose ps` | État des conteneurs |
| `docker-compose logs -f SERVICE` | Logs en direct d'un service |
| `docker-compose exec SERVICE COMMAND` | Exécuter une commande dans un conteneur |
| `docker volume prune -f` | Nettoyer les volumes Docker orphelins |

---

## 🐛 Troubleshooting

### Le DAG n'apparaît pas dans Airflow

```powershell
# Vérifier que le fichier DAG est au bon endroit
docker-compose exec airflow-webserver ls -la /airflow/dags/

# Redémarrer le scheduler
docker-compose restart airflow-scheduler
```

### Erreur de connexion PostgreSQL

```powershell
# Vérifier que PostgreSQL est prêt
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres
Start-Sleep -Seconds 10
docker-compose up -d
```

### Les conteneurs Airflow crashent

```powershell
# Voir les logs d'erreur
docker-compose logs airflow-webserver | Select-Object -Last 50

# Reset complet
docker-compose down -v
docker volume prune -f
mkdir -p airflow/logs
docker-compose up -d
Start-Sleep -Seconds 300
docker-compose ps
```

### Les fichiers CSV ne sont pas dans `/airflow/data`

```powershell
# Vérifier les permissions
ls -la data/raw/

# Les fichiers doivent être dans :
d:\data eng\projet-rfm-airflow-docker\data\raw\
```

---

## 📈 Étendre le Projet

### Ajouter une nouvelle tâche Airflow

1. Créer un script Python dans `src/etl/`
2. L'importer dans `src/dags/rfm_pipeline_dag.py`
3. Ajouter une tâche PythonOperator
4. Définir les dépendances

### Modifier la fréquence d'exécution

Dans `src/dags/rfm_pipeline_dag.py`, changer `schedule_interval` :
```python
schedule_interval='@daily'     # Quotidien
schedule_interval='@weekly'    # Hebdomadaire
schedule_interval='0 2 * * *'  # Tous les jours à 2h du matin
```

### Ajouter de la visualisation

Integrer Streamlit ou Metabase pour visualiser les résultats RFM.

---

## 📚 Ressources

- **Dataset Original** : [Online Retail II - UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Airflow Docs** : [Apache Airflow](https://airflow.apache.org/)
- **Docker Docs** : [Docker Documentation](https://docs.docker.com/)
- **PostgreSQL** : [PostgreSQL 15](https://www.postgresql.org/)

---

## 📝 Notes

- Les logs Airflow sont sauvegardés dans `airflow/logs/`
- Les données brutes ne sont **jamais supprimées** pendant l'exécution
- Les fichiers RFM sont écrasés à chaque exécution (mode `truncate_insert`)
- L'utilisateur Airflow par défaut est `admin / admin` (à changer en production)

---

## 👥 Auteurs

Développé comme projet pédagogique pour apprendre :
- ETL et data engineering
- Orchestration avec Airflow
- Containerisation avec Docker
- Analyse RFM (segmentation clients)

---

## 📞 Support

Pour les problèmes :

1. **Vérifier les logs :**
   ```powershell
   docker-compose logs SERVICE_NAME
   ```

2. **Consulter la documentation Airflow :**
   http://localhost:8080/documentation

3. **Reset et redémarrage complet :**
   ```powershell
   docker-compose down -v
   docker volume prune -f
   docker-compose up -d
   ```

---

**✨ Bon workflow ! ✨**
