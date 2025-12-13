"""
Controller para endpoints de Transação.
"""
import os
from flask import request
from flask_restx import Resource, Namespace, fields
from app.services.transacao_service import TransacaoService
from app.services.solana_service import SolanaService
from app.schemas.transacao_schema import (
    transacao_create_schema,
    transacao_update_schema,
    transacao_response_schema,
    transacoes_response_schema
)
from app.utils.exceptions import ValidationError

# Cria namespace para Swagger
ns = Namespace('transacoes', description='Operações de transação')

# Modelos para documentação Swagger
transacao_create_model = ns.model('TransacaoCreate', {
    'carteira': fields.String(required=True, description='Carteira de origem'),
    'senha': fields.String(required=True, description='Senha da carteira'),
    'transacao': fields.String(required=True, description='Tipo de transação (send)'),
    'valor': fields.Float(required=True, description='Valor da transação'),
    'carteira_destino': fields.String(required=True, description='Carteira de destino')
})

transacao_update_model = ns.model('TransacaoUpdate', {
    'status': fields.String(description='Status da transação'),
    'valor': fields.Float(description='Valor da transação')
})

transacao_response_model = ns.model('TransacaoResponse', {
    'id': fields.Integer(description='ID da transação'),
    'carteira_origem': fields.String(description='Carteira de origem'),
    'carteira_destino': fields.String(description='Carteira de destino'),
    'valor': fields.Float(description='Valor da transação'),
    'tipo_transacao': fields.String(description='Tipo de transação'),
    'status': fields.String(description='Status da transação'),
    'data_criacao': fields.DateTime(description='Data de criação'),
    'data_atualizacao': fields.DateTime(description='Data de atualização'),
    'signature': fields.String(description='Assinatura da transação na blockchain'),
    'block_slot': fields.Integer(description='Slot do bloco'),
    'confirmation_status': fields.String(description='Status de confirmação (pending/confirmed/finalized)'),
    'network': fields.String(description='Rede Solana (devnet/mainnet)'),
    'fee': fields.Float(description='Taxa da transação em SOL')
})


@ns.route('')
class TransacaoList(Resource):
    """Endpoint para listar e criar transações."""
    
    @ns.doc('list_transacoes')
    @ns.marshal_list_with(transacao_response_model)
    @ns.param('carteira_origem', 'Filtrar por carteira de origem')
    @ns.param('carteira_destino', 'Filtrar por carteira de destino')
    @ns.param('status', 'Filtrar por status')
    def get(self):
        """
        Lista todas as transações.
        
        Query parameters opcionais:
        - carteira_origem: Filtrar por carteira de origem
        - carteira_destino: Filtrar por carteira de destino
        - status: Filtrar por status
        """
        filtros = {}
        if request.args.get('carteira_origem'):
            filtros['carteira_origem'] = request.args.get('carteira_origem')
        if request.args.get('carteira_destino'):
            filtros['carteira_destino'] = request.args.get('carteira_destino')
        if request.args.get('status'):
            filtros['status'] = request.args.get('status')
        
        transacoes = TransacaoService.listar_transacoes(filtros)
        return transacoes_response_schema.dump(transacoes), 200
    
    @ns.doc('create_transacao')
    @ns.expect(transacao_create_model)
    @ns.marshal_with(transacao_response_model, code=201)
    @ns.response(400, 'Erro de validação')
    def post(self):
        """
        Cria uma nova transação.
        
        Campos obrigatórios:
        - carteira: Carteira de origem
        - senha: Senha da carteira
        - transacao: Tipo de transação (deve ser "send")
        - valor: Valor da transação (deve ser positivo)
        - carteira_destino: Carteira de destino
        """
        try:
            # Valida dados de entrada
            dados_validados = transacao_create_schema.load(request.json)
            
            # Cria transação
            transacao = TransacaoService.criar_transacao(dados_validados)
            
            return transacao_response_schema.dump(transacao), 201
        except ValidationError as e:
            ns.abort(400, message=str(e))
        except Exception as e:
            ns.abort(500, message=f'Erro ao criar transação: {str(e)}')


@ns.route('/<int:transacao_id>')
@ns.param('transacao_id', 'ID da transação')
class TransacaoDetail(Resource):
    """Endpoint para operações em transação específica."""
    
    @ns.doc('get_transacao')
    @ns.marshal_with(transacao_response_model)
    @ns.response(404, 'Transação não encontrada')
    def get(self, transacao_id):
        """
        Busca uma transação por ID.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
            return transacao_response_schema.dump(transacao), 200
        except Exception as e:
            ns.abort(404, message=str(e))
    
    @ns.doc('update_transacao')
    @ns.expect(transacao_update_model)
    @ns.marshal_with(transacao_response_model)
    @ns.response(400, 'Erro de validação')
    @ns.response(404, 'Transação não encontrada')
    def put(self, transacao_id):
        """
        Atualiza uma transação.
        
        Campos opcionais:
        - status: Status da transação (pendente, processada, cancelada, falhou)
        - valor: Novo valor da transação
        
        Args:
            transacao_id: ID da transação
        """
        try:
            # Valida dados de entrada
            dados_validados = transacao_update_schema.load(request.json)
            
            # Atualiza transação
            transacao = TransacaoService.atualizar_transacao(transacao_id, dados_validados)
            
            return transacao_response_schema.dump(transacao), 200
        except ValidationError as e:
            ns.abort(400, message=str(e))
        except Exception as e:
            ns.abort(404, message=str(e))
    
    @ns.doc('delete_transacao')
    @ns.response(204, 'Transação deletada com sucesso')
    @ns.response(404, 'Transação não encontrada')
    def delete(self, transacao_id):
        """
        Deleta uma transação.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            TransacaoService.deletar_transacao(transacao_id)
            return None, 204
        except Exception as e:
            ns.abort(404, message=str(e))


@ns.route('/<int:transacao_id>/processar')
@ns.param('transacao_id', 'ID da transação')
class TransacaoProcessar(Resource):
    """Endpoint para processar transação na blockchain."""
    
    @ns.doc('processar_transacao')
    @ns.marshal_with(transacao_response_model)
    @ns.response(400, 'Erro de validação')
    @ns.response(404, 'Transação não encontrada')
    def post(self, transacao_id):
        """
        Processa uma transação pendente na blockchain.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            transacao = TransacaoService.processar_transacao_na_blockchain(transacao_id)
            return transacao_response_schema.dump(transacao), 200
        except Exception as e:
            ns.abort(400, message=str(e))


@ns.route('/<int:transacao_id>/status')
@ns.param('transacao_id', 'ID da transação')
class TransacaoStatus(Resource):
    """Endpoint para consultar status na blockchain."""
    
    @ns.doc('status_transacao')
    @ns.marshal_with(transacao_response_model)
    @ns.response(404, 'Transação não encontrada')
    def get(self, transacao_id):
        """
        Consulta e atualiza status de uma transação na blockchain.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            transacao = TransacaoService.atualizar_status_blockchain(transacao_id)
            return transacao_response_schema.dump(transacao), 200
        except Exception as e:
            ns.abort(404, message=str(e))


# Namespace para carteiras
ns_carteiras = Namespace('carteiras', description='Operações de carteira Solana')

@ns_carteiras.route('/<string:address>/saldo')
@ns_carteiras.param('address', 'Endereço da carteira Solana')
class CarteiraSaldo(Resource):
    """Endpoint para consultar saldo de carteira."""
    
    @ns_carteiras.doc('get_saldo')
    @ns_carteiras.response(400, 'Endereço inválido')
    @ns_carteiras.response(503, 'Erro de conexão Solana')
    def get(self, address):
        """
        Consulta saldo de uma carteira Solana.
        
        Args:
            address: Endereço da carteira Solana
        """
        try:
            saldo = SolanaService.obter_saldo(address)
            return {
                'carteira': address,
                'saldo': saldo,
                'saldo_lamports': SolanaService.converter_sol_para_lamports(saldo),
                'network': os.environ.get('SOLANA_NETWORK', 'devnet')
            }, 200
        except Exception as e:
            ns_carteiras.abort(400, message=str(e))
    
    @ns.doc('processar_transacao')
    @ns.marshal_with(transacao_response_model)
    @ns.response(400, 'Erro de validação')
    @ns.response(404, 'Transação não encontrada')
    def post_processar(self, transacao_id):
        """
        Processa uma transação pendente na blockchain.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            transacao = TransacaoService.processar_transacao_na_blockchain(transacao_id)
            return transacao_response_schema.dump(transacao), 200
        except Exception as e:
            ns.abort(400, message=str(e))
    
    @ns.doc('status_transacao')
    @ns.marshal_with(transacao_response_model)
    @ns.response(404, 'Transação não encontrada')
    def get_status(self, transacao_id):
        """
        Consulta e atualiza status de uma transação na blockchain.
        
        Args:
            transacao_id: ID da transação
        """
        try:
            transacao = TransacaoService.atualizar_status_blockchain(transacao_id)
            return transacao_response_schema.dump(transacao), 200
        except Exception as e:
            ns.abort(404, message=str(e))




