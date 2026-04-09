# Script pour démarrer les conteneurs Docker
# Usage: .\start.ps1

param(
    [switch]$Build = $false,
    [switch]$Down = $false
)

Write-Host "🐳 Gestion des conteneurs RFM" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if ($Down) {
    Write-Host "🛑 Arrêt des conteneurs..." -ForegroundColor Yellow
    docker-compose down
    exit
}

if ($Build) {
    Write-Host "🏗️ Construction et démarrage des conteneurs..." -ForegroundColor Yellow
    docker-compose up -d --build
} else {
    Write-Host "🚀 Démarrage des conteneurs..." -ForegroundColor Yellow
    docker-compose up -d
}

Write-Host "⏳ Attente du démarrage de PostgreSQL..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "`n✅ Conteneurs démarrés !" -ForegroundColor Green
Write-Host "`n📊 Accès aux services :" -ForegroundColor Cyan
Write-Host "  • Airflow UI : http://localhost:8080" -ForegroundColor White
Write-Host "  • PostgreSQL : localhost:5432" -ForegroundColor White
Write-Host "`n🔐 Identifiants Airflow :" -ForegroundColor Cyan
Write-Host "  • Utilisateur : admin" -ForegroundColor White
Write-Host "  • Mot de passe : admin" -ForegroundColor White
Write-Host "`n💾 Identifiants PostgreSQL :" -ForegroundColor Cyan
Write-Host "  • Utilisateur : rfm_user" -ForegroundColor White
Write-Host "  • Mot de passe : rfm_password" -ForegroundColor White
Write-Host "  • Base de données : rfm_db`n" -ForegroundColor White

Write-Host "Pour afficher les logs : docker-compose logs -f" -ForegroundColor Gray
Write-Host "Pour arrêter : .\start.ps1 -Down`n" -ForegroundColor Gray
