# Correção do Problema com SECRET_KEY

## Problema

O Docker Compose está interpretando `$j4` e `$twyaz` na sua SECRET_KEY como variáveis de ambiente, gerando os warnings:
```
WARN[0000] The "j4" variable is not set. Defaulting to a blank string.
WARN[0000] The "twyaz" variable is not set. Defaulting to a blank string.
```

## Solução

A SECRET_KEY no arquivo `.env` precisa ter os caracteres `$` escapados ou estar entre aspas.

### Opção 1: Usar Aspas Simples (Recomendado)

No servidor, edite o arquivo `.env`:

```bash
nano .env
```

Altere a linha:
```env
SECRET_KEY=r&8%fly9d7vo6r%y=uxis1u6-&0rgba6$j4^(etm9o)$twyaz$
```

Para:
```env
SECRET_KEY='r&8%fly9d7vo6r%y=uxis1u6-&0rgba6$j4^(etm9o)$twyaz$'
```

### Opção 2: Escapar os Caracteres $

```env
SECRET_KEY="r&8%fly9d7vo6r%y=uxis1u6-&0rgba6\$j4^(etm9o)\$twyaz\$"
```

### Opção 3: Usar Script Automático

No servidor, execute:

```bash
chmod +x fix-env-secret.sh
./fix-env-secret.sh
```

## Comando Correto Após Correção

```bash
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

**Nota:** Use `docker compose` (sem hífen) para Docker Compose V2, ou `docker-compose` (com hífen) para V1.

## Verificar se Funcionou

Após corrigir e executar, você não deve mais ver os warnings sobre `j4` e `twyaz`.
