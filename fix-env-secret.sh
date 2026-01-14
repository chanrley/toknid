#!/bin/bash
# Script para corrigir a SECRET_KEY no arquivo .env
# Escapa os caracteres $ que estão causando problemas no Docker Compose

if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

echo "🔧 Corrigindo SECRET_KEY no arquivo .env..."

# Fazer backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Ler o arquivo .env e corrigir a SECRET_KEY
# Opção 1: Colocar entre aspas simples (mais simples)
sed -i.bak "s/^SECRET_KEY=\(.*\)$/SECRET_KEY='\1'/" .env

# Remover arquivo .bak criado pelo sed
rm -f .env.bak

echo "✅ SECRET_KEY corrigida!"
echo "📋 Verifique o arquivo .env e execute novamente:"
echo "   docker compose -f docker-compose.prod.yml up -d --build --force-recreate"
