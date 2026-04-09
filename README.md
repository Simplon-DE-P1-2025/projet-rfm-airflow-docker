# 📊 Pipeline Data RFM — Orchestration Airflow & Docker

**Projet pédagogique** : Pipeline ETL simple orchestrée avec Airflow, containerisée avec Docker, et visualisée avec Streamlit.

---

## 🎯 Objectifs

Ce projet vise à apprendre les concepts clés du data engineering :

✅ **Ingestion** : Charger des fichiers CSV dans PostgreSQL  
✅ **Transformation** : Calculer les scores RFM (Recency, Frequency, Monetary)  
✅ **Orchestration** : Automatiser la pipeline avec Airflow DAG  
✅ **Containerisation** : Déployer tous les services avec Docker Compose  
✅ **Visualisation** : Explorer les résultats avec Streamlit (bonus)

---

## 🏗️ Architecture Simplifiée

```
                    ETL PIPELINE
                        
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE RFM                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CSV (data/raw/)                                            │
│      ↓                                                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │  TÂCHE 1 : INGESTION (ingest.py)                 │       │
│  │  • Lecture des fichiers CSV                      │       │
│  │  • Chargement dans PostgreSQL (raw_data)         │       │
│  └──────────────────────────────────────────────────┘       │
│      ↓                                                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │  TÂCHE 2 : TRANSFORMATION RFM (transform.py)     │       │
│  │  • Calcul Recency (jours depuis dernier achat)   │       │
│  │  • Calcul Frequency (nombre d'achats)            │       │
│  │  • Calcul Monetary (total des dépenses)          │       │
│  │  • Scoring RFM (1-5 pour chaque dimension)       │       │
│  └──────────────────────────────────────────────────┘       │
│      ↓                                                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │  TÂCHE 3 : CHARGEMENT (load.py)                  │       │
│  │  • Sauvegarde dans PostgreSQL (rfm_results)      │       │
│  └──────────────────────────────────────────────────┘       │
│      ↓                                                      │
│  PostgreSQL Database                                        │
│  - Données brutes (raw_data)                                │
│  - Résultats RFM (rfm_results)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
Orchestrator: Apache Airflow (DAG: rfm_pipeline)
Container: Docker Compose (3 services)
Visualization: Streamlit Dashboard (optional)

```

---

## 📋 Prérequis

| Outil | Version | Vérifier |
|-------|---------|----------|
| Docker Desktop | 4.0+ | `docker --version` |
| Docker Compose | 1.29+ | `docker-compose --version` |
| PowerShell | 5.0+ | Inclus Windows 10+ |

---

## 🚀 Démarrage (3 étapes)

### 1️⃣ Initialisation de la Base de Données

```powershell
cd "d:\data eng\projet-rfm-airflow-docker"

# Démarrer PostgreSQL uniquement
docker-compose up -d postgres
Start-Sleep -Seconds 15

# Initialiser Airflow
docker-compose run --rm airflow-webserver airflow db migrate

# Créer utilisateur admin
docker-compose run --rm airflow-webserver airflow users create `
  --username admin --password admin `
  --firstname Admin --lastname User `
  --role Admin --email admin@example.com
```

### 2️⃣ Lancer Tous les Services

```powershell
# Démarrer la pipeline complète
docker-compose up -d

# Attendre 2-3 minutes pour que Airflow démarre
Start-Sleep -Seconds 180

# Vérifier l'état
docker-compose ps
```

### 3️⃣ Accéder à Airflow

Ouvrir navigateur : **http://localhost:8080**

**Login :**
- Username: `admin`
- Password: `admin`

---

## 📖 Utilisation Simple

### ▶️ Exécuter la Pipeline

1. **Interface Airflow UI** :
   - Chercher le DAG `rfm_pipeline`
   - Cliquer sur le toggle ON
   - Cliquer "Trigger DAG"

2. **Ou ligne de commande** :
   ```powershell
   docker-compose exec airflow-webserver airflow dags trigger rfm_pipeline
   ```

### 📊 Résultats

Après exécution, vérifier les données :

```powershell
# Vérifier dans PostgreSQL
docker-compose exec postgres psql -U rfm_user -d rfm_db -c "SELECT COUNT(*) FROM rfm_results;"

# Visualiser avec Streamlit (si disponible)
# Accès: http://localhost:8501
```

---

## 📁 Structure du Projet

```
projet-rfm-airflow-docker/
│
├── src/
│   ├── dags/
│   │   └── rfm_pipeline_dag.py    ← DAG Airflow (orchestration)
│   ├── etl/
│   │   ├── ingest.py              ← Charge CSV → PostgreSQL
│   │   ├── transform.py           ← Calcule RFM
│   │   ├── load.py                ← Copie → rfm_results
│   │   └── helpers.py             ← Utilitaires
│   ├── analysis/                  ← Analyses avancées (optionnel)
│   └── app/
│       └── main.py                ← Dashboard Streamlit
│
├── data/
│   ├── raw/                       ← 📥 CSV à traiter
│
├── docker/
│   └── Dockerfile                 ← Image custom Airflow
│
├── docker-compose.yml             ← Orchestration services
├── requirements.txt               ← Dépendances Python
├── .env                          ← Configuration env
└── README.md                     ← Ce fichier
```

---

## 🔑 Concepts Clés Expliqués

### 1. Pipeline RFM (étapes ETL)

| Étape | Fonction | Fichier |
|-------|----------|---------|
| **E**xtract | Lire CSV et charger en PostgreSQL (table `raw_orders`) | `ingest.py` |
| **T**ransform | Calculer Recency, Frequency, Monetary + scores 1-5 | `transform.py` |
| **L**oad | Copier résultats dans `rfm_results` | `load.py` |

**Formule RFM Simple :**
- **Recency** = jours depuis dernier achat (moins = mieux)
- **Frequency** = nombre total d'achats (plus = mieux)
- **Monetary** = montant total dépensé (plus = mieux)

Chaque dimension reçoit un score de **1 à 5** (via quartiles).

### 2. Airflow DAG (Orchestration)

**DAG `rfm_pipeline`** :
```
ingest_data 
    ↓
transform_rfm
    ↓
load_rfm_results
    ↓
(+ 4 tâches parallèles d'analyses avancées - optionnel)
```

**Fréquence** : @daily (run quotidien à minuit)  
**Retry** : 1 essai après 5 minutes en cas d'erreur

### 3. Docker Compose (Services)

| Service | Rôle | Port |
|---------|------|------|
| `postgres` | Base de données RFM | 5432 (interne) |
| `airflow-webserver` | Interface Airflow UI | 8080 |
| `airflow-scheduler` | Lance les DAGs (tous les jours) | interne |
| `streamlit` | Dashboard visualisation | 8501 |

---

## ✅ Checklist de Vérification

Après démarrage :

- [ ] `docker-compose ps` → tous les services "Up"
- [ ] http://localhost:8080 → page login Airflow
- [ ] Connexion avec admin/admin ✓
- [ ] DAG `rfm_pipeline` visible en haut
- [ ] Tâches `ingest_data`, `transform_rfm`, `load_rfm_results` apparentes

Après exécution du DAG :

- [ ] Les 3 tâches deviennent **vertes** (success)
- [ ] Pas d'erreurs visibles dans les logs
- [ ] PostgreSQL contient les tables : `raw_orders`, `rfm_analysis`, `rfm_results`

```powershell
# Vérifier les tables
docker-compose exec postgres psql -U rfm_user -d rfm_db -c "\dt"
```

---

## 🛠️ Commandes Essentielles

```powershell
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# État des services
docker-compose ps

# Logs en direct
docker-compose logs -f airflow-webserver

# Reset complet (⚠️ supprime toutes données)
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

---

## 🎓 Choix Techniques Justifiés

### Pourquoi Airflow ?
- **Simple** : DAG Python facile à lire
- **Couramment utilisé** : Standard industrie
- **Interface visuelle** : Monitoring facile

### Pourquoi PostgreSQL ?
- **Robuste** : Base relationnelle SQL standard
- **Conteneurisable** : Image Docker officielle
- **Performant** : Suffit pour données petites/moyennes

### Pourquoi Docker Compose ?
- **Multi-services** : PostgreSQL + Airflow + Streamlit ensemble
- **Reproductible** : Même config partout (dev, prod)
- **Facile** : Une commande `up` pour tout lancer

### Pipeline Optimisée (Sans fichier CSV intermédiaire)
- **Avant** : data → CSV → PostgreSQL (2 I/O)
- **Après** : PostgreSQL → PostgreSQL (SQL direct = plus rapide)
- **Bénéfice** : Source unique de vérité, pas de synchronisation

---

## 📈 Résultats Attendus

Après exécution complète du DAG :

**Table `rfm_results`** : 4000+ clients avec :

```
customer_id | recency | frequency | monetary | r_score | f_score | m_score | segment
     543    |   12    |     8     |  1250.50 |    5    |    4    |    5    | Champions
     789    |   180   |     2     |   200.00 |    1    |    1    |    1    | Perdus
     ...
```

**8 segments de clients** identifiés automatiquement :
- 🏆 Champions (meilleurs clients)
- 💎 Clients Fidèles
- 🌱 Nouveaux Clients
- 📈 Clients Potentiels
- ⚠️ À Risque
- 💤 Perdus
- 🔄 À Réactiver
- ➖ Moyens

---

## 🐛 Dépannage Rapide

| Problème | Solution |
|----------|----------|
| DAG n'apparaît pas | `docker-compose restart airflow-scheduler` |
| Erreur connexion PostgreSQL | `docker-compose logs postgres` |
| Conteneurs ne démarrent pas | `docker-compose down -v` + `up -d` |
| Permission denied | Vérifier `data/raw/` accessible |

---

## 🎯 Prochaines Étapes (Optionnel)

1. **Dashboard Streamlit** : Visualiser les segments
2. **Analyses avancées** : Churn prediction, CLV forecast
3. **Export** : Fichier Excel final
4. **Alertes** : Notifier quand segment "Perdus" augmente

---

## 📚 Ressources

- **Dataset**: [Online Retail II - UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Airflow Docs**: http://localhost:8080/docs (une fois lancé)
- **Docker Docs**: https://docs.docker.com/

---


