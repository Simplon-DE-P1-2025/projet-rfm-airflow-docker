# 📋 ÉTAPE 3 - Orchestration Airflow

## Statut :  ✅ À LANCER

Vous avez complété :
- ✅ Ingestion (ingest.py)
- ✅ Transformation RFM (transform.py)
- ✅ Chargement (load.py)
- ✅ DAG Airflow (rfm_pipeline_dag.py)
- ✅ Docker Compose configuré

---

## Architecture du Pipeline

```
📂 Data (CSV brut)
    ↓
🔄 [TASK 1] ingest_raw_data
    ↓
🐘 PostgreSQL (table raw_data)
    ↓
🔄 [TASK 2] transform_rfm
    ↓
📊 Fichier RFM (data/processed/rfm_results.csv)
    ↓
🔄 [TASK 3] load_rfm_results
    ↓
🐘 PostgreSQL (table rfm_results)
```

---

## 📁 Structure des Fichiers

```
src/
├── dags/
│   ├── __init__.py
│   └── rfm_pipeline_dag.py        ← DAG Airflow (3 tâches)
└── etl/
    ├── __init__.py
    ├── helpers.py                 ← Gestion des imports
    ├── ingest.py                  ← Tâche 1 : Ingestion
    ├── transform.py               ← Tâche 2 : Transformation RFM
    └── load.py                    ← Tâche 3 : Chargement
```

---

## 🚀 COMMENT LANCER

### Option 1 : Avec Docker Compose (RECOMMANDÉ)

```powershell
# 1. Démarrer les conteneurs
docker-compose up -d

# 2. Attendre que Airflow démarre (2-3 minutes)
Start-Sleep -Seconds 180

# 3. Accéder à Airflow UI
# URL : http://localhost:8080
# Identifiants :
#   - Username : admin
#   - Password : admin

# 4. Dans l'UI Airflow :
#    - Chercher le DAG : rfm_pipeline
#    - Activer le toggle (bouton ON)
#    - Cliquer sur "Trigger DAG" pour une exécution manuelle
#    - Vérifier les logs

# 5. Arrêter les conteneurs
docker-compose down
```

---

## 📊 Vérification du Succès

Après l'exécution du DAG :

```sql
-- Vérifier les données brutes chargées
SELECT COUNT(*) FROM raw_data;

-- Vérifier les résultats RFM
SELECT COUNT(*) FROM rfm_results;

-- Consulter un client RFM
SELECT * FROM rfm_results LIMIT 5;
```

---

## ⚠️ Troubleshooting

### Les DAGs ne sont pas visibles dans Airflow
- Vérifier que `./src/dags` est bien monté dans docker-compose
- Les fichiers `.py` dans `src/dags/` doivent avoir des fonctions avec `@dag` ou être en tant que DAG

### Erreurs de connexion PostgreSQL
- Attendre que PostgreSQL soit complètement prêt (10-15 secondes)
- Vérifier que les variables d'environnement sont correctes dans `.env`

### Les tasks échouent
- Vérifier les logs : `docker-compose logs airflow-scheduler`
- Vérifier que les chemins `/airflow/etl`, `/airflow/config` sont corrects

---

## ✅ Checklist pour l'Étape 3

- [ ] Docker et Docker Compose installés
- [ ] `.env` configuré avec DB_HOST=postgres (pour Docker)
- [ ] `docker-compose up -d` lancé avec succès
- [ ] Airflow accessible sur http://localhost:8080
- [ ] DAG `rfm_pipeline` visible
- [ ] Exécution manuelle réussie
- [ ] Tables PostgreSQL remplies (raw_data, rfm_results)

---

## Prochaines Étapes (Étape 4)

Une fois validée :
- Documenter le README
- Tester l'exécution complète
- Préparer la présentation
