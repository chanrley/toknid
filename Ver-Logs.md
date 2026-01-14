# Ver Logs - Toknid D2

Guia completo para consultar os logs do Gunicorn, Nginx e Django em produção.

## 📋 Logs do Gunicorn

O Gunicorn está configurado para enviar logs para stdout/stderr do container. Para ver:

```bash
# Logs em tempo real (follow)
docker compose -f docker-compose.prod.yml logs -f web

# Últimas 100 linhas
docker compose -f docker-compose.prod.yml logs --tail=100 web

# Apenas erros
docker compose -f docker-compose.prod.yml logs web | grep -i error

# Logs desde um tempo específico (últimas 10 minutos)
docker compose -f docker-compose.prod.yml logs --since 10m web
```

## 🌐 Logs do Nginx

O Nginx está configurado para escrever em `/var/log/nginx/` dentro do container:

```bash
# Logs em tempo real do container Nginx
docker compose -f docker-compose.prod.yml logs -f nginx

# Últimas 100 linhas
docker compose -f docker-compose.prod.yml logs --tail=100 nginx

# Ver logs de acesso dentro do container
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/toknid_access.log

# Ver logs de erro dentro do container
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/toknid_error.log

# Ver logs de erro em tempo real
docker compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/toknid_error.log

# Ver logs de acesso em tempo real
docker compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/toknid_access.log

# Últimas 50 linhas de erro
docker compose -f docker-compose.prod.yml exec nginx tail -n 50 /var/log/nginx/toknid_error.log
```

## 🐍 Logs do Django

Os logs do Django estão salvos em arquivo:

```bash
# Ver logs do Django (dentro do container)
docker compose -f docker-compose.prod.yml exec web cat /app/logs/django.log

# Ver logs em tempo real
docker compose -f docker-compose.prod.yml exec web tail -f /app/logs/django.log

# Últimas 100 linhas
docker compose -f docker-compose.prod.yml exec web tail -n 100 /app/logs/django.log

# Ou diretamente no servidor (se o volume estiver mapeado)
tail -f logs/django.log

# Ver apenas erros no log do Django
docker compose -f docker-compose.prod.yml exec web grep -i error /app/logs/django.log
```

## 🔍 Ver todos os logs juntos

```bash
# Todos os serviços em tempo real
docker compose -f docker-compose.prod.yml logs -f

# Apenas web e nginx
docker compose -f docker-compose.prod.yml logs -f web nginx

# Últimas 200 linhas de todos os serviços
docker compose -f docker-compose.prod.yml logs --tail=200
```

## 📊 Comandos Úteis Adicionais

```bash
# Ver status dos containers
docker compose -f docker-compose.prod.yml ps

# Ver uso de recursos
docker stats

# Ver logs de um container específico por nome
docker logs -f toknid-d2-web
docker logs -f toknid-d2-nginx

# Filtrar logs por palavra-chave
docker compose -f docker-compose.prod.yml logs web | grep -i "error\|exception\|traceback"

# Salvar logs em arquivo
docker compose -f docker-compose.prod.yml logs web > logs_gunicorn.txt
docker compose -f docker-compose.prod.yml logs nginx > logs_nginx.txt
```

## 🎯 Resumo Rápido

| Serviço | Comando Principal | Localização no Container |
|---------|-------------------|--------------------------|
| **Gunicorn** | `docker compose logs -f web` | stdout/stderr |
| **Nginx** | `docker compose logs -f nginx` | `/var/log/nginx/` |
| **Django** | `docker compose exec web tail -f /app/logs/django.log` | `/app/logs/django.log` |

## 💡 Dicas

- Use `-f` para seguir os logs em tempo real (como `tail -f`)
- Use `--tail=N` para ver apenas as últimas N linhas
- Use `--since` para ver logs desde um tempo específico (ex: `--since 10m`, `--since 1h`)
- Combine com `grep` para filtrar por palavras-chave
- Para parar o follow, pressione `Ctrl+C`

## 🚨 Troubleshooting

Se os logs não aparecerem:

1. Verifique se os containers estão rodando:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

2. Verifique se os volumes estão mapeados corretamente

3. Para logs do Nginx dentro do container, certifique-se de que o diretório existe:
   ```bash
   docker compose -f docker-compose.prod.yml exec nginx ls -la /var/log/nginx/
   ```

4. Para logs do Django, verifique se o diretório `logs` existe:
   ```bash
   docker compose -f docker-compose.prod.yml exec web ls -la /app/logs/
   ```
