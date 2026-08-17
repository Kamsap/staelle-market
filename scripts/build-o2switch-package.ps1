$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$distBrowser = Join-Path $projectRoot "dist\staelle-market\browser"
$deployRoot = Join-Path $projectRoot "deploy\o2switch"
$frontendPackage = Join-Path $deployRoot "frontend"
$backendPackage = Join-Path $deployRoot "backend"

Set-Location $projectRoot

npm run build

if (Test-Path $deployRoot) {
  Remove-Item $deployRoot -Recurse -Force
}

New-Item -ItemType Directory -Force $frontendPackage | Out-Null
New-Item -ItemType Directory -Force $backendPackage | Out-Null

Copy-Item (Join-Path $distBrowser "*") $frontendPackage -Recurse -Force

# Certains outils ignorent les fichiers commençant par un point. On force donc
# la présence du .htaccess dans le package final.
Copy-Item (Join-Path $projectRoot "public\.htaccess") (Join-Path $frontendPackage ".htaccess") -Force

Copy-Item (Join-Path $projectRoot "backend\app") $backendPackage -Recurse -Force
Copy-Item (Join-Path $projectRoot "backend\alembic") $backendPackage -Recurse -Force
Copy-Item (Join-Path $projectRoot "backend\alembic.ini") $backendPackage -Force
Copy-Item (Join-Path $projectRoot "backend\requirements.txt") $backendPackage -Force
Copy-Item (Join-Path $projectRoot "backend\staelle_wsgi.py") $backendPackage -Force
Copy-Item (Join-Path $projectRoot "backend\.env.example") $backendPackage -Force

Get-ChildItem $backendPackage -Directory -Recurse -Filter "__pycache__" |
  Remove-Item -Recurse -Force

Compress-Archive -Path (Join-Path $frontendPackage "*") -DestinationPath (Join-Path $deployRoot "staelle-market-frontend-o2switch.zip") -Force
Compress-Archive -Path (Join-Path $backendPackage "*") -DestinationPath (Join-Path $deployRoot "staelle-market-backend-o2switch.zip") -Force

Write-Host "Packages prêts :"
Write-Host "- $deployRoot\staelle-market-frontend-o2switch.zip"
Write-Host "- $deployRoot\staelle-market-backend-o2switch.zip"
