# scripts/test_all.ps1
$ErrorActionPreference = "Stop"

Write-Host "== Running unit tests (auth-service) ==" -ForegroundColor Cyan
Push-Location auth-service
python -m pip install -r requirements.txt | Out-Null
python -m pytest -v
Pop-Location

Write-Host "== Running unit tests (file-service) ==" -ForegroundColor Cyan
Push-Location file-service
python -m pip install -r requirements.txt | Out-Null
python -m pytest -v
Pop-Location

Write-Host "== Running system tests (docker compose) ==" -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --build
Start-Sleep -Seconds 15

Push-Location system-tests/auth
npm install | Out-Null
npm test
Pop-Location

Push-Location system-tests/dashboard
npm install | Out-Null
npm test
Pop-Location

Write-Host "== Done. Stopping containers ==" -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v
