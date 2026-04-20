#!/bin/bash
# ============================================================
# Script de Configuración para Machine Learning
# Vision Human Insight - IAGENTEK
# ============================================================

echo "🧠 Configurando sistema de Machine Learning..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado${NC}"

# Navegar al directorio del backend
cd "$(dirname "$0")/../apps/api" || exit

# Instalar dependencias básicas
echo -e "${YELLOW}📦 Instalando dependencias básicas...${NC}"
pip install -r requirements.txt

# Preguntar si instalar dependencias de ML
read -p "¿Instalar dependencias de Machine Learning? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📦 Instalando dependencias de ML (esto puede tardar)...${NC}"
    pip install -r requirements_ml.txt
    echo -e "${GREEN}✅ Dependencias de ML instaladas${NC}"
else
    echo -e "${YELLOW}⚠️  Dependencias de ML omitidas${NC}"
fi

# Crear directorio para modelos
mkdir -p models
mkdir -p datasets

echo -e "${GREEN}✅ Directorios creados${NC}"

# Verificar Supabase
echo -e "${YELLOW}🔍 Verificando configuración de Supabase...${NC}"
if [ -f .env ]; then
    if grep -q "SUPABASE_URL" .env && grep -q "SUPABASE_SERVICE_ROLE_KEY" .env; then
        echo -e "${GREEN}✅ Variables de Supabase configuradas${NC}"
    else
        echo -e "${YELLOW}⚠️  Variables de Supabase no encontradas en .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
fi

# Instrucciones finales
echo ""
echo -e "${GREEN}✅ Configuración completada${NC}"
echo ""
echo "📝 Próximos pasos:"
echo "1. Configura las API keys en .env (UNSPLASH_ACCESS_KEY, PEXELS_API_KEY)"
echo "2. Ejecuta el script SQL: infra/supabase/ml_training_setup.sql"
echo "3. Lee la guía: docs/ML_TRAINING_GUIDE.md"
echo ""

