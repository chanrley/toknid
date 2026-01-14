#!/bin/bash
# Script de backup automatizado
# Uso: ./backup.sh

set -e

BACKUP_DIR="/opt/backups/toknid-d2"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/opt/toknid-d2"

echo "💾 Iniciando backup do Toknid D2..."

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Verificar se docker-compose está rodando
if ! docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "Up"; then
    echo "⚠️  Aviso: Containers não estão rodando. Alguns backups podem falhar."
fi

# Backup do banco de dados SQLite
echo "🗄️  Fazendo backup do banco de dados SQLite..."
if docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "web.*Up"; then
    # Copiar db.sqlite3 do container
    docker-compose -f docker-compose.prod.yml exec -T web cp /app/db.sqlite3 /tmp/db_backup.sqlite3 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml cp web:/app/db.sqlite3 "$BACKUP_DIR/db_$DATE.sqlite3" 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml cp web:/tmp/db_backup.sqlite3 "$BACKUP_DIR/db_$DATE.sqlite3" 2>/dev/null
    
    if [ -f "$BACKUP_DIR/db_$DATE.sqlite3" ] && [ -s "$BACKUP_DIR/db_$DATE.sqlite3" ]; then
        echo "✅ Backup do banco criado: db_$DATE.sqlite3"
        # Comprimir backup do banco
        gzip "$BACKUP_DIR/db_$DATE.sqlite3"
    else
        # Tentar backup direto do volume
        if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
            cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_$DATE.sqlite3"
            gzip "$BACKUP_DIR/db_$DATE.sqlite3"
            echo "✅ Backup do banco criado do volume: db_$DATE.sqlite3.gz"
        else
            echo "⚠️  Aviso: Backup do banco pode ter falhado ou banco não encontrado."
        fi
    fi
else
    # Backup direto do arquivo se container não estiver rodando
    if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
        cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_$DATE.sqlite3"
        gzip "$BACKUP_DIR/db_$DATE.sqlite3"
        echo "✅ Backup do banco criado: db_$DATE.sqlite3.gz"
    else
        echo "⚠️  Aviso: Arquivo db.sqlite3 não encontrado."
    fi
fi

# Backup de arquivos media
echo "📁 Fazendo backup dos arquivos media..."
if [ -d "$PROJECT_DIR/media" ] && [ "$(ls -A $PROJECT_DIR/media 2>/dev/null)" ]; then
    tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" -C "$PROJECT_DIR" media 2>/dev/null
    if [ -f "$BACKUP_DIR/media_$DATE.tar.gz" ]; then
        echo "✅ Backup de media criado: media_$DATE.tar.gz"
    fi
else
    echo "ℹ️  Diretório media vazio ou não existe. Pulando backup de media."
fi

# Backup do arquivo .env (opcional - apenas se autorizado)
# Descomente a linha abaixo se quiser fazer backup do .env
# cp "$PROJECT_DIR/.env" "$BACKUP_DIR/env_$DATE.backup" 2>/dev/null && echo "✅ Backup do .env criado"

# Limpar backups antigos (manter apenas últimos 7 dias)
echo "🧹 Limpando backups antigos (mantendo últimos 7 dias)..."
find "$BACKUP_DIR" -type f -mtime +7 -delete 2>/dev/null || true

# Listar backups criados
echo ""
echo "📋 Backups disponíveis:"
ls -lh "$BACKUP_DIR" | tail -5

echo ""
echo "✅ Backup concluído!"
echo "📂 Localização: $BACKUP_DIR"
