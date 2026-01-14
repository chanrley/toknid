#!/bin/bash
# Script de deploy automatizado para produção
# Uso: ./deploy.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do Toknid D2..."

# Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: docker-compose.yml não encontrado. Execute este script na raiz do projeto."
    exit 1
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado. Certifique-se de configurá-lo antes do deploy."
    exit 1
fi

# Pull latest code (se usando Git)
if [ -d ".git" ]; then
    echo "📥 Atualizando código do repositório..."
    git pull origin main || git pull origin master
fi

# Build das imagens
echo "🔨 Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# Subir serviços
echo "⬆️  Subindo serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 5

# Executar migrations
echo "🔄 Executando migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Coletar static files
echo "📦 Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Reiniciar web para aplicar mudanças
echo "🔄 Reiniciando serviço web..."
docker-compose -f docker-compose.prod.yml restart web

# Health check
echo "🏥 Verificando saúde da aplicação..."
sleep 5

if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Deploy concluído com sucesso!"
    echo "📊 Status dos containers:"
    docker-compose -f docker-compose.prod.yml ps
else
    echo "❌ Erro: Aplicação não está respondendo corretamente."
    echo "📋 Verifique os logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 web
    exit 1
fi
