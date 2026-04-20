# ============================================================
# Script de Configuración para Machine Learning (PowerShell)
# Vision Human Insight - IAGENTEK
# ============================================================

Write-Host "🧠 Configurando sistema de Machine Learning..." -ForegroundColor Cyan

# Navegar al directorio del backend
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "..\apps\api"
Set-Location $backendPath

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado" -ForegroundColor Red
    exit 1
}

# Instalar dependencias básicas
Write-Host "📦 Instalando dependencias básicas..." -ForegroundColor Yellow
pip install -r requirements.txt

# Preguntar si instalar dependencias de ML
$response = Read-Host "¿Instalar dependencias de Machine Learning? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "📦 Instalando dependencias de ML (esto puede tardar)..." -ForegroundColor Yellow
    pip install -r requirements_ml.txt
    Write-Host "✅ Dependencias de ML instaladas" -ForegroundColor Green
} else {
    Write-Host "⚠️  Dependencias de ML omitidas" -ForegroundColor Yellow
}

# Crear directorios
New-Item -ItemType Directory -Force -Path "models" | Out-Null
New-Item -ItemType Directory -Force -Path "datasets" | Out-Null
Write-Host "✅ Directorios creados" -ForegroundColor Green

# Verificar Supabase
Write-Host "🔍 Verificando configuración de Supabase..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "SUPABASE_URL" -and $envContent -match "SUPABASE_SERVICE_ROLE_KEY") {
        Write-Host "✅ Variables de Supabase configuradas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Variables de Supabase no encontradas en .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
}

# Instrucciones finales
Write-Host ""
Write-Host "✅ Configuración completada" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Configura las API keys en .env (UNSPLASH_ACCESS_KEY, PEXELS_API_KEY)"
Write-Host "2. Ejecuta el script SQL: infra/supabase/ml_training_setup.sql"
Write-Host "3. Lee la guía: docs/ML_TRAINING_GUIDE.md"
Write-Host ""

