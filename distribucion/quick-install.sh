#!/bin/bash

# Script de instalación rápida para Linux/Mac
# DVD Rental API - Instalador automático

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}   🎬 DVD Rental API - Instalador Rápido   ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "${NC}Este script instalará y configurará:${NC}"
echo -e "${GRAY}  • PostgreSQL 15 con DVD Rental Database${NC}"
echo -e "${GRAY}  • API REST de Express.js${NC}"
echo -e "${GRAY}  • Todo completamente dockerizado${NC}"
echo ""

# Verificar Docker
echo -e "${YELLOW}🔍 Verificando requisitos...${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker no está instalado${NC}"
    echo ""
    echo -e "${YELLOW}Por favor instala Docker desde:${NC}"
    echo -e "${CYAN}https://docs.docker.com/get-docker/${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Docker instalado${NC}"

# Verificar si Docker está corriendo
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker no está corriendo${NC}"
    echo ""
    echo -e "${YELLOW}Por favor inicia el servicio de Docker e intenta nuevamente${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Docker está corriendo${NC}"

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker Compose no está instalado${NC}"
    echo ""
    echo -e "${YELLOW}Por favor instala Docker Compose${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose instalado${NC}"
echo ""

# Preguntar al usuario
echo -en "${YELLOW}¿Deseas continuar con la instalación? (s/n): ${NC}"
read -r respuesta

if [[ ! "$respuesta" =~ ^[sS]$ ]]; then
    echo ""
    echo -e "${YELLOW}Instalación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}   📦 Iniciando instalación...              ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Descargar docker-compose.yml si no existe
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}📥 Descargando configuración...${NC}"
    
    if command -v curl &> /dev/null; then
        curl -sL -o docker-compose.yml "https://raw.githubusercontent.com/samueljjuarezb/dvdrental-api/main/distribution/docker-compose.yml"
    elif command -v wget &> /dev/null; then
        wget -q -O docker-compose.yml "https://raw.githubusercontent.com/samueljjuarezb/dvdrental-api/main/distribution/docker-compose.yml"
    else
        echo -e "${RED}❌ No se encontró curl ni wget${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Configuración descargada${NC}"
else
    echo -e "${GREEN}✅ Configuración encontrada${NC}"
fi

echo ""

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creando archivo de configuración...${NC}"
    cat > .env << 'EOF'
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=dvdrental
DB_PORT=5432
API_PORT=3000
EOF
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

echo ""
echo -e "${YELLOW}📥 Descargando imágenes de Docker Hub...${NC}"
echo -e "${GRAY}   (Esto puede tomar varios minutos)${NC}"
echo ""

docker-compose pull

echo ""
echo -e "${GREEN}✅ Imágenes descargadas correctamente${NC}"
echo ""
echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
echo ""

docker-compose up -d

echo ""
echo -e "${GREEN}✅ Servicios iniciados${NC}"
echo ""
echo -e "${YELLOW}⏳ Esperando a que los servicios estén listos...${NC}"
echo -e "${GRAY}   (Esto puede tomar 30-60 segundos)${NC}"

# Esperar a que la API responda
max_intentos=30
intento=0
api_ready=false

while [ $intento -lt $max_intentos ] && [ "$api_ready" = false ]; do
    sleep 2
    intento=$((intento + 1))
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        api_ready=true
    else
        echo -n "."
    fi
done

echo ""
echo ""

if [ "$api_ready" = true ]; then
    echo -e "${CYAN}============================================${NC}"
    echo -e "${GREEN}   ✅ ¡Instalación completada!              ${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    echo -e "${GREEN}🎉 La API está lista y funcionando${NC}"
    echo ""
    echo -e "${CYAN}📍 URLs de acceso:${NC}"
    echo -e "${NC}   API:        http://localhost:3000${NC}"
    echo -e "${NC}   PostgreSQL: localhost:5432${NC}"
    echo ""
    echo -e "${CYAN}📚 Endpoints disponibles:${NC}"
    echo -e "${NC}   GET  http://localhost:3000/api/films${NC}"
    echo -e "${NC}   GET  http://localhost:3000/api/customers${NC}"
    echo -e "${NC}   GET  http://localhost:3000/api/rentals${NC}"
    echo -e "${NC}   GET  http://localhost:3000/api/reports/most-rented${NC}"
    echo ""
    echo -e "${CYAN}🔧 Comandos útiles:${NC}"
    echo -e "${NC}   Ver logs:     docker-compose logs -f${NC}"
    echo -e "${NC}   Detener:      docker-compose down${NC}"
    echo -e "${NC}   Reiniciar:    docker-compose restart${NC}"
    echo -e "${NC}   Ver estado:   docker-compose ps${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Los servicios están iniciando pero aún no responden${NC}"
    echo ""
    echo -e "${NC}Esto es normal. Espera un minuto más y verifica:${NC}"
    echo -e "${CYAN}   docker-compose logs -f${NC}"
    echo ""
fi

echo ""
echo -e "${CYAN}📖 Para más información, visita:${NC}"
echo -e "${NC}   https://github.com/samueljjuarezb/dvdrental-api${NC}"
echo ""

chmod +x quick-install.sh