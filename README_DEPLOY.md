# Guia Rápido de Deploy - Toknid D2

## 🚀 Deploy Rápido

### 1. Preparação Inicial

```bash
# Copiar arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Editar .env com valores reais
nano .env
```

### 2. Configurar SSL

```bash
# Instalar certbot
sudo apt-get install certbot

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ./nginx/ssl/
sudo chmod 644 ./nginx/ssl/*.pem
```

### 3. Deploy

**IMPORTANTE:** Antes de executar o deploy, corrija a SECRET_KEY no arquivo `.env` (veja `CORRECAO_ENV.md`).

```bash
# Dar permissão de execução aos scripts
chmod +x deploy.sh backup.sh rollback.sh fix-env-secret.sh

# Corrigir SECRET_KEY (se necessário)
./fix-env-secret.sh

# Executar deploy
docker compose -f docker-compose.prod.yml up -d --build --force-recreate

# OU usar o script automatizado
./deploy.sh
```

### 4. Verificar

```bash
# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f web
```

## 📋 Comandos Úteis

### Backup
```bash
./backup.sh
```

### Rollback
```bash
./rollback.sh v1.0.0
```

### Ver logs
```bash
docker compose -f docker-compose.prod.yml logs -f
# ou (se usar Docker Compose V1)
docker-compose -f docker-compose.prod.yml logs -f
```

### Reiniciar serviços
```bash
docker compose -f docker-compose.prod.yml restart
# ou
docker-compose -f docker-compose.prod.yml restart
```

### Executar migrations manualmente
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
# ou
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Criar superusuário
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
# ou
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## ⚠️ Importante

- Sempre fazer backup antes de deploy
- Testar em ambiente de staging primeiro
- Revisar variáveis de ambiente antes de cada deploy
- Manter logs monitorados

Para mais detalhes, consulte `PLANO_DEPLOY_PRD.md`.
