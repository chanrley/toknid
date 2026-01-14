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

```bash
# Dar permissão de execução aos scripts
chmod +x deploy.sh backup.sh rollback.sh

# Executar deploy
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
docker-compose -f docker-compose.prod.yml logs -f
```

### Reiniciar serviços
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Executar migrations manualmente
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Criar superusuário
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## ⚠️ Importante

- Sempre fazer backup antes de deploy
- Testar em ambiente de staging primeiro
- Revisar variáveis de ambiente antes de cada deploy
- Manter logs monitorados

Para mais detalhes, consulte `PLANO_DEPLOY_PRD.md`.
