# Plano de Deploy em Produção - Toknid D2

## 📋 Visão Geral
Este documento descreve o plano completo para deploy do projeto Toknid D2 em ambiente de produção.

**Tecnologias:**
- Django 6.0.1
- Python 3.12
- Gunicorn (WSGI Server)
- Nginx (Reverse Proxy)
- Docker & Docker Compose
- SQLite (atual) → **Recomendado: PostgreSQL para PRD**

---

## 🔍 1. PRÉ-REQUISITOS E CHECKLIST PRÉ-DEPLOY

### 1.1 Infraestrutura
- [ ] Servidor com Docker e Docker Compose instalados
- [ ] Domínio configurado e apontando para o servidor
- [ ] Certificado SSL/TLS (Let's Encrypt recomendado)
- [ ] Firewall configurado (portas 80, 443 abertas)
- [ ] Backup do banco de dados atual (se houver)

### 1.2 Segurança
- [ ] Gerar nova `SECRET_KEY` para produção
- [ ] Configurar variáveis de ambiente sensíveis
- [ ] Revisar `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`
- [ ] Configurar HTTPS obrigatório
- [ ] Revisar permissões de arquivos e diretórios

### 1.3 Banco de Dados
- [ ] **CRÍTICO:** Migrar de SQLite para PostgreSQL
- [ ] Criar banco de dados PostgreSQL
- [ ] Configurar backup automático do banco
- [ ] Testar migração de dados (se houver)

### 1.4 Código
- [ ] Todas as migrations aplicadas
- [ ] Testes executados e passando
- [ ] Static files coletados
- [ ] Código revisado e sem credenciais hardcoded
- [ ] Versão do código marcada (tag Git)

---

## 🗄️ 2. CONFIGURAÇÃO DO BANCO DE DADOS

### 2.1 Estrutura Recomendada para PostgreSQL

**Tabela:** `toknid_d2_prd`

**Configurações:**
- Encoding: UTF-8
- Collation: pt_BR.UTF-8
- Usuário: `toknid_user` (com permissões limitadas)
- Senha: (armazenar em variável de ambiente)

### 2.2 Alterações Necessárias em `settings/settings.py`

```python
# Substituir configuração de DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'toknid_d2_prd'),
        'USER': os.environ.get('DB_USER', 'toknid_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### 2.3 Dependências
Adicionar ao `requirements.txt`:
```
psycopg2-binary>=2.9.9
```

---

## 🔐 3. VARIÁVEIS DE AMBIENTE (.env)

Criar arquivo `.env` na raiz do projeto com:

```env
# Django
SECRET_KEY=<gerar_nova_chave_secreta>
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Database
DB_NAME=toknid_d2_prd
DB_USER=toknid_user
DB_PASSWORD=<senha_forte>
DB_HOST=db
DB_PORT=5432

# Django Settings
DJANGO_SETTINGS_MODULE=settings.settings
PYTHONUNBUFFERED=1
```

**⚠️ IMPORTANTE:**
- Nunca commitar o arquivo `.env` no Git
- Usar gerenciador de secrets (AWS Secrets Manager, HashiCorp Vault, etc.) em produção
- Rotacionar `SECRET_KEY` periodicamente

---

## 🐳 4. CONFIGURAÇÃO DOCKER

### 4.1 Atualizar `docker-compose.yml` para Produção

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: toknid-d2-db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - toknid_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: toknid-d2-web
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - settings.wsgi:application
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=settings.settings
      - PYTHONUNBUFFERED=1
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - toknid_network

  nginx:
    image: nginx:alpine
    container_name: toknid-d2-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - toknid_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  toknid_network:
    driver: bridge
```

### 4.2 Atualizar `Dockerfile` (Otimizações)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar e instalar dependências Node
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Copiar código do projeto
COPY . .

# Coletar static files
RUN python manage.py collectstatic --noinput

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "settings.wsgi:application"]
```

---

## 🌐 5. CONFIGURAÇÃO NGINX COM SSL

### 5.1 Atualizar `nginx/nginx.conf`

```nginx
upstream django {
    server web:8000;
    keepalive 32;
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 100M;
    client_body_timeout 60s;

    # Logs
    access_log /var/log/nginx/toknid_access.log;
    error_log /var/log/nginx/toknid_error.log;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

### 5.2 Obter Certificado SSL (Let's Encrypt)

```bash
# Instalar certbot
sudo apt-get update
sudo apt-get install certbot

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Copiar certificados para pasta do projeto
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ./nginx/ssl/
sudo chmod 644 ./nginx/ssl/*.pem
```

---

## 📦 6. PROCESSO DE DEPLOY

### 6.1 Preparação no Servidor

```bash
# 1. Conectar ao servidor
ssh usuario@servidor-prd

# 2. Criar diretório do projeto
mkdir -p /opt/toknid-d2
cd /opt/toknid-d2

# 3. Clonar repositório (ou fazer upload do código)
git clone <repo-url> .
# OU fazer upload via SCP/SFTP

# 4. Criar arquivo .env
nano .env
# (colar conteúdo do .env preparado)

# 5. Criar diretórios necessários
mkdir -p nginx/ssl
mkdir -p media
chmod 755 media
```

### 6.2 Build e Deploy

```bash
# 1. Parar containers existentes (se houver)
docker-compose down

# 2. Fazer backup do banco atual (se migrando)
# (se houver SQLite, fazer backup do db.sqlite3)

# 3. Build das imagens
docker-compose build --no-cache

# 4. Subir serviços
docker-compose up -d

# 5. Executar migrations
docker-compose exec web python manage.py migrate

# 6. Criar superusuário (se necessário)
docker-compose exec web python manage.py createsuperuser

# 7. Verificar logs
docker-compose logs -f web
docker-compose logs -f nginx
```

### 6.3 Verificações Pós-Deploy

```bash
# 1. Verificar status dos containers
docker-compose ps

# 2. Verificar saúde do banco
docker-compose exec db pg_isready -U toknid_user

# 3. Testar aplicação
curl -I https://seu-dominio.com

# 4. Verificar static files
curl -I https://seu-dominio.com/static/app/css/

# 5. Verificar logs de erro
docker-compose logs web | grep ERROR
docker-compose logs nginx | grep error
```

---

## 🔄 7. SCRIPTS DE AUTOMAÇÃO

### 7.1 Script de Deploy (`deploy.sh`)

```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy..."

# Pull latest code
git pull origin main

# Build
docker-compose build

# Migrations
docker-compose exec -T web python manage.py migrate --noinput

# Collect static
docker-compose exec -T web python manage.py collectstatic --noinput

# Restart services
docker-compose up -d

# Health check
sleep 5
curl -f http://localhost:8000/admin/ || exit 1

echo "✅ Deploy concluído com sucesso!"
```

### 7.2 Script de Backup (`backup.sh`)

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/toknid-d2"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco
docker-compose exec -T db pg_dump -U toknid_user toknid_d2_prd > $BACKUP_DIR/db_$DATE.sql

# Backup de media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /opt/toknid-d2/media

# Manter apenas últimos 7 dias
find $BACKUP_DIR -type f -mtime +7 -delete

echo "✅ Backup criado: $BACKUP_DIR"
```

---

## 📊 8. MONITORAMENTO E LOGS

### 8.1 Configuração de Logs

Adicionar em `settings/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 8.2 Monitoramento Recomendado

- [ ] Configurar alertas de uptime (UptimeRobot, Pingdom)
- [ ] Monitorar uso de recursos (CPU, RAM, Disco)
- [ ] Configurar alertas de logs de erro
- [ ] Monitorar performance do banco de dados
- [ ] Configurar backup automático diário

---

## 🔒 9. SEGURANÇA ADICIONAL

### 9.1 Configurações Django

Adicionar em `settings/settings.py` (se não existir):

```python
# Security settings (já parcialmente implementado)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 9.2 Firewall (UFW)

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 🚨 10. ROLLBACK PLAN

### 10.1 Procedimento de Rollback

```bash
# 1. Parar containers atuais
docker-compose down

# 2. Voltar para versão anterior (Git)
git checkout <tag-ou-commit-anterior>

# 3. Restaurar backup do banco (se necessário)
docker-compose exec -T db psql -U toknid_user toknid_d2_prd < backup.sql

# 4. Subir versão anterior
docker-compose up -d
```

---

## ✅ 11. CHECKLIST FINAL PRÉ-GO-LIVE

- [ ] Todas as variáveis de ambiente configuradas
- [ ] Banco de dados PostgreSQL criado e testado
- [ ] Migrations aplicadas
- [ ] Static files coletados
- [ ] SSL/TLS configurado e funcionando
- [ ] Nginx configurado corretamente
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Monitoramento configurado
- [ ] Testes de carga realizados
- [ ] Documentação atualizada
- [ ] Equipe treinada no processo de deploy
- [ ] Plano de rollback documentado

---

## 📝 12. NOTAS IMPORTANTES

1. **SQLite → PostgreSQL:** Migração obrigatória para produção
2. **SECRET_KEY:** Gerar nova chave usando: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
3. **Workers Gunicorn:** Ajustar número de workers baseado em CPU cores: `(2 * CPU cores) + 1`
4. **Backup:** Configurar backup automático diário do banco
5. **Logs:** Revisar logs regularmente para identificar problemas
6. **Atualizações:** Manter dependências atualizadas e testadas

---

## 📞 13. CONTATOS E SUPORTE

- **Responsável pelo Deploy:** [Nome]
- **Equipe de Infraestrutura:** [Contato]
- **Horário de Deploy Recomendado:** [Horário de menor tráfego]

---

**Última atualização:** [Data]
**Versão do Plano:** 1.0
