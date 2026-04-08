# Script de gestion Airflow pour Windows
# Usage: .\manage-airflow.ps1 [start|stop|init|logs|shell]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "init", "logs", "shell", "webui")]
    [string]$Action
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Start-Services {
    Write-Header "🚀 Démarrage des services Docker"
    
    Write-Host "📦 Démarrage de PostgreSQL et Airflow..."
    docker-compose up -d
    
    Write-Host "`n⏳ Attente du démarrage de PostgreSQL (10 secondes)..."
    Start-Sleep -Seconds 10
    
    Write-Host "`n📊 État des conteneurs :"
    docker-compose ps
    
    Write-Host "`n✅ Services démarrés !" -ForegroundColor Green
    Write-Host "   📍 Airflow UI : http://localhost:8080"
    Write-Host "   🔐 Identifiants : admin / admin" -ForegroundColor Yellow
}

function Stop-Services {
    Write-Header "🛑 Arrêt des services Docker"
    
    Write-Host "Arrêt des conteneurs..."
    docker-compose down
    
    Write-Host "`n✅ Services arrêtés" -ForegroundColor Green
}

function Init-Airflow {
    Write-Header "🔧 Initialisation d'Airflow"
    
    Write-Host "1️⃣ Démarrage de PostgreSQL..."
    docker-compose up -d postgres
    
    Write-Host "2️⃣ Attente de PostgreSQL..."
    Start-Sleep -Seconds 10
    
    Write-Host "3️⃣ Initialisation de la base Airflow..."
    docker-compose run --rm airflow-webserver airflow db migrate
    
    Write-Host "4️⃣ Création de l'utilisateur admin..."
    docker-compose run --rm airflow-webserver airflow users create `
        --username admin `
        --password admin `
        --firstname Admin `
        --lastname User `
        --role Admin `
        --email admin@example.com | Out-Null
    
    Write-Host "`n✅ Initialisation terminée" -ForegroundColor Green
    Write-Host "   Vous pouvez maintenant lancer : .\manage-airflow.ps1 start`n" -ForegroundColor Yellow
}

function Show-Logs {
    Write-Header "📋 Logs Airflow Webserver"
    
    Write-Host "Affichage des logs en direct (Ctrl+C pour quitter)`n"
    docker-compose logs -f airflow-webserver
}

function Open-Shell {
    Write-Header "🐚 Shell Airflow Webserver"
    
    Write-Host "Accès au shell du conteneur Airflow`n"
    docker-compose exec airflow-webserver bash
}

function Open-WebUI {
    Write-Header "🌐 Ouverture d'Airflow UI"
    
    Write-Host "Ouverture de http://localhost:8080..."
    Start-Process "http://localhost:8080"
}

# Exécuter l'action
switch ($Action) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "init" { Init-Airflow }
    "logs" { Show-Logs }
    "shell" { Open-Shell }
    "webui" { Open-WebUI }
}

Write-Host ""
