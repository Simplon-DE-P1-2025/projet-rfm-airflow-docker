# 📊 Pipeline RFM - Airflow & Docker

## ⚙️ Prérequis

- Docker Desktop (installé & en cours d'exécution)
- PowerShell

---

## 🚀 DÉMARRAGE RAPIDE

### Étape 1 : Initialiser Airflow (une seule fois)

```powershell
cd "d:\data eng\projet-rfm-airflow-docker"
docker-compose up -d postgres
Start-Sleep -Seconds 10
docker-compose run --rm airflow-webserver airflow db migrate
docker-compose run --rm airflow-webserver airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

### Étape 2 : Démarrer les services

```powershell
docker-compose up -d
```

Attendez 30 secondes.

### Étape 3 : Accéder à Airflow

http://localhost:8080

**Identifiants :**
- Username : `admin`
- Password : `admin`

---

## 📋 COMMANDES ESSENTIELLES

**Démarrer tout**
```powershell
docker-compose up -d
```

**Arrêter tout**
```powershell
docker-compose down
```

**Voir l'état des conteneurs**
```powershell
docker-compose ps
```

**Voir les logs**
```powershell
docker-compose logs -f airflow-webserver
```

**Reset complet**
```powershell
docker-compose down -v
docker-compose up -d postgres
Start-Sleep -Seconds 10
docker-compose run --rm airflow-webserver airflow db migrate
docker-compose run --rm airflow-webserver airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
docker-compose up -d
```

---

## ✅ VÉRIFICATION

Dans http://localhost:8080 :

1. Cherchez le DAG : `rfm_pipeline`
2. Activez le toggle (ON)
3. Cliquez sur "Trigger DAG"
4. Vérifiez que les 3 tâches deviennent vertes :
   - `ingest_raw_data`
   - `transform_rfm` 
   - `load_rfm_results`

---

## 📊 Pipeline

```
CSV (data/raw/)
     ↓
[Ingestion] → PostgreSQL (raw_data)
     ↓
[Transformation RFM] → Fichier (data/processed/rfm_results.csv)
     ↓
[Chargement] → PostgreSQL (rfm_results)
```

---

## 🐛 Problèmes

**Les DAGs ne s'affichent pas**
```powershell
docker-compose logs airflow-webserver
```

**Erreur PostgreSQL**
```powershell
docker-compose restart postgres
Start-Sleep -Seconds 10
docker-compose up -d
```

**Conteneur crash**
```powershell
docker-compose down -v
docker-compose up -d postgres
Start-Sleep -Seconds 10
docker-compose run --rm airflow-webserver airflow db migrate
docker-compose up -d
```

---

**C'est tout ! Juste des commandes docker-compose. 🚀**
