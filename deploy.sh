#!/bin/bash

echo "🚀 Deploy ProcessoScanPro - Produção"
echo "====================================="

# Configurações
DOMAIN="processoscanpro.atendimentorapido.app.br"
DB_CONTAINER="processoscanpro-db"
POSTGRES_PASSWORD="ProcessoScan2025!Secure"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "${YELLOW}1. Parando containers antigos (se existirem)...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
echo "${GREEN}✓ Containers parados${NC}"

echo ""
echo "${YELLOW}2. Subindo PostgreSQL dedicado...${NC}"
docker-compose -f docker-compose.prod.yml up -d db
sleep 5
echo "${GREEN}✓ PostgreSQL dedicado iniciado${NC}"

echo ""
echo "${YELLOW}3. Copiando .env de produção...${NC}"
cp backend/.env.prod backend/.env
echo "${GREEN}✓ .env configurado${NC}"

echo ""
echo "${YELLOW}4. Buildando containers...${NC}"
docker-compose -f docker-compose.prod.yml build

echo ""
echo "${YELLOW}5. Subindo aplicação...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "${YELLOW}6. Aguardando backend iniciar...${NC}"
sleep 10

echo ""
echo "${YELLOW}7. Criando tabelas no banco...${NC}"
docker exec processoscanpro-backend python create_tables_docker.py 2>/dev/null || echo "⚠️ Execute manualmente: docker exec processoscanpro-backend python create_tables_docker.py"

echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✓ Deploy concluído com sucesso!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "🌐 Acesse: https://$DOMAIN"
echo "📊 API: https://$DOMAIN/api/health"
echo ""
echo "📋 Comandos úteis:"
echo "  Ver logs backend:  docker logs -f processoscanpro-backend"
echo "  Ver logs frontend: docker logs -f processoscanpro-frontend"
echo "  Ver logs nginx:    docker logs -f processoscanpro-nginx"
echo "  Reiniciar:         docker-compose -f docker-compose.prod.yml restart"
echo "  Parar:             docker-compose -f docker-compose.prod.yml down"
echo ""
