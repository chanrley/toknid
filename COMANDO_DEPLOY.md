# Comando Correto para Deploy

## Problema Identificado

O Docker Compose está interpretando os caracteres `$j4` e `$twyaz` na SECRET_KEY como variáveis de ambiente.

## Solução 1: Escapar a SECRET_KEY no .env

No arquivo `.env`, a SECRET_KEY precisa ter os `$` escapados ou estar entre aspas:

```env
SECRET_KEY="r&8%fly9d7vo6r%y=uxis1u6-&0rgba6\$j4^(etm9o)\$twyaz\$"
```

OU (mais simples):

```env
SECRET_KEY='r&8%fly9d7vo6r%y=uxis1u6-&0rgba6$j4^(etm9o)$twyaz$'
```

## Comando Correto para Deploy

```bash
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

**Importante:** Use `docker compose` (sem hífen) se estiver usando Docker Compose V2, ou `docker-compose` (com hífen) se for V1.

## Verificar Versão do Docker Compose

```bash
docker compose version
# ou
docker-compose --version
```

## Passos Completos

1. **Corrigir o arquivo .env** (escapar ou colocar entre aspas a SECRET_KEY)
2. **Executar o comando:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build --force-recreate
   ```
3. **Verificar se os containers subiram:**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```
4. **Executar migrations:**
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```
5. **Coletar static files:**
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```
