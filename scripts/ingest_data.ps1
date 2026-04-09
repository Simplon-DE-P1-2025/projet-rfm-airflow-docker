# Script pour démarrer PostgreSQL seul et ingérer les données
# Usage: .\ingest_data.ps1

param(
    [switch]$Down = $false
)

Write-Host "📊 Gestion de l'ingestion des données RFM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Down) {
    Write-Host "🛑 Arrêt de PostgreSQL..." -ForegroundColor Yellow
    docker-compose -f docker-compose.postgres-only.yml down
    exit
}

# Démarrer PostgreSQL
Write-Host "🚀 Démarrage de PostgreSQL..." -ForegroundColor Yellow
docker-compose -f docker-compose.postgres-only.yml up -d

# Attendre le démarrage
Write-Host "⏳ Attente du démarrage de PostgreSQL..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "✅ PostgreSQL démarré !" -ForegroundColor Green
Write-Host "`n📝 Ingestion en cours..." -ForegroundColor Yellow

# Exécuter le script d'ingestion en local
python test_ingest.py

Write-Host "`n✅ Opération terminée !" -ForegroundColor Green
Write-Host "`n💾 PostgreSQL disponible sur : localhost:5432" -ForegroundColor Cyan
Write-Host "  • Utilisateur : rfm_user" -ForegroundColor White
Write-Host "  • Mot de passe : rfm_password" -ForegroundColor White
Write-Host "  • Base de données : rfm_db`n" -ForegroundColor White

Write-Host "Pour arrêter PostgreSQL : .\ingest_data.ps1 -Down`n" -ForegroundColor Gray
