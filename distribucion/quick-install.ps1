# Script de instalación rápida para Windows
# DVD Rental API - Instalador automático

$ErrorActionPreference = "Stop"

# Colores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Clear-Host
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   🎬 DVD Rental API - Instalador Rápido   " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script instalará y configurará:" -ForegroundColor White
Write-Host "  • PostgreSQL 15 con DVD Rental Database" -ForegroundColor Gray
Write-Host "  • API REST de Express.js" -ForegroundColor Gray
Write-Host "  • Todo completamente dockerizado" -ForegroundColor Gray
Write-Host ""

# Verificar Docker
Write-Host "🔍 Verificando requisitos..." -ForegroundColor Yellow
Write-Host ""

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: Docker no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Docker Desktop desde:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Docker instalado" -ForegroundColor Green

# Verificar si Docker está corriendo
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker no está corriendo"
    }
    Write-Host "✅ Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Docker no está corriendo" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor inicia Docker Desktop e intenta nuevamente" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar Docker Compose
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERROR: Docker Compose no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Docker Compose debería venir con Docker Desktop" -ForegroundColor Yellow
    Write-Host "Intenta reinstalar Docker Desktop" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "✅ Docker Compose instalado" -ForegroundColor Green
Write-Host ""

# Preguntar al usuario
Write-Host "¿Deseas continuar con la instalación? (S/N): " -ForegroundColor Yellow -NoNewline
$respuesta = Read-Host

if ($respuesta -ne "S" -and $respuesta -ne "s") {
    Write-Host ""
    Write-Host "Instalación cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   📦 Iniciando instalación...              " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Descargar docker-compose.yml si no existe
if (!(Test-Path "docker-compose.yml")) {
    Write-Host "📥 Descargando configuración..." -ForegroundColor Yellow
    
    try {
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SamuelJJuarez/API_Express-Docker/main/distribucion/docker-compose.yml" -OutFile "docker-compose.yml"
        Write-Host "✅ Configuración descargada" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al descargar configuración" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
} else {
    Write-Host "✅ Configuración encontrada" -ForegroundColor Green
}

Write-Host ""

# Crear archivo .env si no existe
if (!(Test-Path ".env")) {
    Write-Host "📝 Creando archivo de configuración..." -ForegroundColor Yellow
    @"
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=dvdrental
DB_PORT=5432
API_PORT=3000
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "📥 Descargando imágenes de Docker Hub..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar varios minutos)" -ForegroundColor Gray
Write-Host ""

try {
    docker-compose pull
    Write-Host ""
    Write-Host "✅ Imágenes descargadas correctamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al descargar imágenes" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "🚀 Iniciando servicios..." -ForegroundColor Yellow
Write-Host ""

try {
    docker-compose up -d
    Write-Host ""
    Write-Host "✅ Servicios iniciados" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 30-60 segundos)" -ForegroundColor Gray

# Esperar a que la API responda
$maxIntentos = 30
$intento = 0
$apiReady = $false

while ($intento -lt $maxIntentos -and !$apiReady) {
    Start-Sleep -Seconds 2
    $intento++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 2 -UseBasicParsing 2>$null
        if ($response.StatusCode -eq 200) {
            $apiReady = $true
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host ""

if ($apiReady) {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "   ✅ ¡Instalación completada!              " -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 La API está lista y funcionando" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 URLs de acceso:" -ForegroundColor Cyan
    Write-Host "   API:        http://localhost:3000" -ForegroundColor White
    Write-Host "   PostgreSQL: localhost:5432" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Endpoints disponibles:" -ForegroundColor Cyan
    Write-Host "   GET  http://localhost:3000/api/films" -ForegroundColor White
    Write-Host "   GET  http://localhost:3000/api/customers" -ForegroundColor White
    Write-Host "   GET  http://localhost:3000/api/rentals" -ForegroundColor White
    Write-Host "   GET  http://localhost:3000/api/reports/most-rented" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Comandos útiles:" -ForegroundColor Cyan
    Write-Host "   Ver logs:     docker-compose logs -f" -ForegroundColor White
    Write-Host "   Detener:      docker-compose down" -ForegroundColor White
    Write-Host "   Reiniciar:    docker-compose restart" -ForegroundColor White
    Write-Host "   Ver estado:   docker-compose ps" -ForegroundColor White
    Write-Host ""
    
    # Preguntar si quiere abrir en el navegador
    Write-Host "¿Deseas abrir la API en tu navegador? (S/N): " -ForegroundColor Yellow -NoNewline
    $abrir = Read-Host
    
    if ($abrir -eq "S" -or $abrir -eq "s") {
        Start-Process "http://localhost:3000"
    }
    
} else {
    Write-Host "⚠️  Los servicios están iniciando pero aún no responden" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Esto es normal. Espera un minuto más y verifica:" -ForegroundColor White
    Write-Host "   docker-compose logs -f" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "📖 Para más información, visita:" -ForegroundColor Cyan
Write-Host "   https://github.com/SamuelJJuarez/API_Express-Docker" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para salir"