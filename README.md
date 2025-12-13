# API REST Flask - Sistema de Transações

API RESTful desenvolvida em Flask para gerenciamento de transações entre carteiras.

## Estrutura do Projeto

```
toknid-chan/
├── app/
│   ├── __init__.py              # Factory do Flask app
│   ├── config.py                # Configurações
│   ├── controllers/             # Endpoints REST
│   ├── models/                  # Modelos SQLAlchemy
│   ├── services/                   # Lógica de negócio
│   ├── schemas/                 # Validação Marshmallow
│   └── utils/                   # Utilitários e exceções
├── tests/                       # Testes unitários
├── instance/                    # Banco de dados SQLite
└── run.py                       # Script de inicialização
```

## Instalação

1. Ative o ambiente virtual:
```bash
.\.venv\Scripts\Activate.ps1
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):
```bash
cp .env.example .env
```

## Execução

### Opção 1: Usando o script run.py
```bash
python run.py
```

### Opção 2: Usando Flask CLI (recomendado)
Certifique-se de que o ambiente virtual está ativado e use:

**PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m flask run
```

**Ou use o script auxiliar:**
```powershell
.\flask_run.ps1
```

**CMD/Batch:**
```cmd
.\.venv\Scripts\python.exe -m flask run
```

**Ou use o script auxiliar:**
```cmd
flask_run.bat
```

**Nota:** O arquivo `.flaskenv` já está configurado com `FLASK_APP=app:create_app`, então o Flask CLI sabe qual aplicação usar.

A API estará disponível em `http://localhost:5000`

## Documentação Swagger

Acesse a documentação interativa em:
```
http://localhost:5000/api/docs
```

## Integração com Solana Devnet

A aplicação está integrada com a blockchain Solana usando Devnet para testes gratuitos.

### Configuração

Configure as variáveis no arquivo `.env`:

```env
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_COMMITMENT=confirmed
SOLANA_PRIVATE_KEY=sua_chave_privada_base58  # Opcional
```

### Obter SOL de Teste

1. Configure a Phantom Wallet para Devnet:
   - Settings → Developer Mode → ON
   - Settings → Networks → Change Network → Devnet

2. Use um faucet para obter SOL de teste:
   - https://faucet.solana.com/
   - https://solfaucet.com/
   - https://faucet.quicknode.com/solana/devnet

## Endpoints

### POST /api/transacoes
Cria uma nova transação e processa na blockchain Solana.

**Body:**
```json
{
  "carteira": "EndereçoSolanaOrigem...",
  "senha": "senha123",
  "transacao": "send",
  "valor": 0.1,
  "carteira_destino": "EndereçoSolanaDestino..."
}
```

**Resposta inclui:**
- `signature`: Assinatura da transação na blockchain
- `confirmation_status`: Status de confirmação (pending/confirmed/finalized)
- `block_slot`: Slot do bloco
- `network`: Rede usada (devnet/mainnet)
- `fee`: Taxa da transação

### GET /api/transacoes
Lista todas as transações.

**Query Parameters (opcionais):**
- `carteira_origem`: Filtrar por carteira de origem
- `carteira_destino`: Filtrar por carteira de destino
- `status`: Filtrar por status

### GET /api/transacoes/{id}
Busca uma transação por ID.

### PUT /api/transacoes/{id}
Atualiza uma transação.

**Body:**
```json
{
  "status": "processada",
  "valor": 150.00
}
```

### DELETE /api/transacoes/{id}
Deleta uma transação.

### POST /api/transacoes/{id}/processar
Força o processamento de uma transação pendente na blockchain.

### GET /api/transacoes/{id}/status
Consulta e atualiza o status de uma transação na blockchain.

### GET /api/carteiras/{address}/saldo
Consulta o saldo de uma carteira Solana.

**Resposta:**
```json
{
  "carteira": "EndereçoSolana...",
  "saldo": 1.5,
  "saldo_lamports": 1500000000,
  "network": "devnet"
}
```

## Testes

Execute os testes com:
```bash
pytest
```

## Tecnologias

- Flask 3.0
- Flask-SQLAlchemy
- Flask-Marshmallow
- Flask-RESTX (Swagger)
- SQLite
- pytest
- Solana Python SDK (solana, solders)
- base58

## Funcionalidades Solana

- ✅ Validação de endereços Solana
- ✅ Consulta de saldo em tempo real
- ✅ Verificação de saldo suficiente antes de transacionar
- ✅ Criação e envio de transações na blockchain
- ✅ Consulta de status de transações
- ✅ Suporte a Devnet (testes) e Mainnet
- ✅ Conversão automática SOL ↔ Lamports
- ✅ Tratamento de erros específicos da blockchain

