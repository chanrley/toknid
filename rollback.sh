#!/bin/bash
# Script de rollback para versão anterior
# Uso: ./rollback.sh [tag-ou-commit]

set -e

if [ -z "$1" ]; then
    echo "❌ Erro: Especifique a tag ou commit para fazer rollback."
    echo "Uso: ./rollback.sh <tag-ou-commit>"
    echo "Exemplo: ./rollback.sh v1.0.0"
    exit 1
fi

TARGET_VERSION=$1
BACKUP_DIR="/opt/backups/toknid-d2"

echo "⏪ Iniciando rollback para versão: $TARGET_VERSION"

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: docker-compose.yml não encontrado."
    exit 1
fi

# Fazer backup antes do rollback
echo "💾 Criando backup antes do rollback..."
if [ -f "backup.sh" ]; then
    bash backup.sh
fi

# Parar containers
echo "🛑 Parando containers..."
docker-compose -f docker-compose.prod.yml down

# Voltar para versão anterior (Git)
if [ -d ".git" ]; then
    echo "📥 Voltando código para versão $TARGET_VERSION..."
    git fetch origin
    git checkout "$TARGET_VERSION"
else
    echo "⚠️  Aviso: Diretório não é um repositório Git. Rollback manual necessário."
fi

# Rebuild das imagens
echo "🔨 Reconstruindo imagens..."
docker-compose -f docker-compose.prod.yml build

# Subir serviços
echo "⬆️  Subindo serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Executar migrations (pode ser necessário reverter algumas)
echo "🔄 Verificando migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Health check
echo "🏥 Verificando saúde da aplicação..."
sleep 5

if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Rollback concluído com sucesso!"
    echo "📊 Status dos containers:"
    docker-compose -f docker-compose.prod.yml ps
else
    echo "❌ Erro: Aplicação não está respondendo após rollback."
    echo "📋 Verifique os logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 web
    exit 1
fi
