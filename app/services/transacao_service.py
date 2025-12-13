"""
Service layer para Transação.
"""
import os
import bcrypt
from app import db
from app.models.transacao_model import Transacao
from app.services.solana_service import SolanaService
from app.utils.solana_utils import calcular_taxa_transacao, converter_lamports_para_sol
from app.utils.exceptions import (
    ValidationError, NotFoundError, BusinessLogicError,
    SolanaConnectionError, InsufficientFundsError, InvalidAddressError, TransactionFailedError
)


class TransacaoService:
    """
    Service para operações de transação.
    
    Contém a lógica de negócio para criação, leitura, atualização
    e exclusão de transações.
    """
    
    @staticmethod
    def hash_senha(senha):
        """
        Gera hash da senha usando bcrypt.
        
        Args:
            senha: Senha em texto plano
        
        Returns:
            str: Hash da senha
        """
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verificar_senha(senha, senha_hash):
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            senha: Senha em texto plano
            senha_hash: Hash da senha armazenado
        
        Returns:
            bool: True se a senha corresponde, False caso contrário
        """
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
    
    @staticmethod
    def criar_transacao(dados):
        """
        Cria uma nova transação e processa na blockchain Solana.
        
        Args:
            dados: Dicionário com dados da transação (carteira, senha, transacao, valor, carteira_destino)
        
        Returns:
            Transacao: Objeto Transacao criado
        
        Raises:
            ValidationError: Se os dados forem inválidos
            BusinessLogicError: Se houver erro de lógica de negócio
            InvalidAddressError: Se as carteiras forem inválidas
            InsufficientFundsError: Se o saldo for insuficiente
            TransactionFailedError: Se a transação falhar na blockchain
        """
        # Valida que carteira origem e destino são diferentes
        if dados.get('carteira') == dados.get('carteira_destino'):
            raise ValidationError('Carteira de origem e destino não podem ser iguais')
        
        carteira_origem = dados['carteira']
        carteira_destino = dados['carteira_destino']
        valor = dados['valor']
        
        # Valida carteiras Solana
        try:
            SolanaService.validar_carteira(carteira_origem)
            SolanaService.validar_carteira(carteira_destino)
        except InvalidAddressError as e:
            raise ValidationError(str(e))
        
        # Verifica saldo suficiente
        try:
            fee_lamports = calcular_taxa_transacao()
            fee = converter_lamports_para_sol(fee_lamports)
            SolanaService.verificar_saldo_suficiente(carteira_origem, valor, fee)
        except InsufficientFundsError:
            raise
        except Exception as e:
            raise BusinessLogicError(f'Erro ao verificar saldo: {str(e)}')
        
        # Cria hash da senha
        senha_hash = TransacaoService.hash_senha(dados['senha'])
        
        # Obtém network atual
        network = os.environ.get('SOLANA_NETWORK', 'devnet')
        
        # Cria transação no banco
        transacao = Transacao(
            carteira_origem=carteira_origem,
            carteira_destino=carteira_destino,
            valor=valor,
            tipo_transacao=dados.get('transacao', 'send'),
            senha_hash=senha_hash,
            status='pendente',
            network=network,
            fee=fee,
            confirmation_status='pending'
        )
        
        try:
            db.session.add(transacao)
            db.session.flush()  # Para obter o ID
            
            # Processa transação na blockchain
            try:
                solana_transaction = SolanaService.criar_transacao(
                    carteira_origem, carteira_destino, valor
                )
                signature = SolanaService.enviar_transacao(solana_transaction)
                
                # Atualiza transação com dados da blockchain
                transacao.signature = signature
                transacao.status = 'processando'
                transacao.confirmation_status = 'pending'
                
                db.session.commit()
                return transacao
            except (TransactionFailedError, SolanaConnectionError) as e:
                # Se falhar na blockchain, mantém como pendente
                transacao.status = 'falhou'
                db.session.commit()
                raise BusinessLogicError(f'Erro ao processar transação na blockchain: {str(e)}')
        except Exception as e:
            db.session.rollback()
            if isinstance(e, BusinessLogicError):
                raise
            raise BusinessLogicError(f'Erro ao criar transação: {str(e)}')
    
    @staticmethod
    def listar_transacoes(filtros=None):
        """
        Lista todas as transações, opcionalmente filtradas.
        
        Args:
            filtros: Dicionário com filtros opcionais (carteira_origem, carteira_destino, status)
        
        Returns:
            list: Lista de objetos Transacao
        """
        query = Transacao.query
        
        if filtros:
            if 'carteira_origem' in filtros:
                query = query.filter(Transacao.carteira_origem == filtros['carteira_origem'])
            if 'carteira_destino' in filtros:
                query = query.filter(Transacao.carteira_destino == filtros['carteira_destino'])
            if 'status' in filtros:
                query = query.filter(Transacao.status == filtros['status'])
        
        return query.order_by(Transacao.data_criacao.desc()).all()
    
    @staticmethod
    def buscar_transacao_por_id(transacao_id):
        """
        Busca uma transação por ID.
        
        Args:
            transacao_id: ID da transação
        
        Returns:
            Transacao: Objeto Transacao encontrado
        
        Raises:
            NotFoundError: Se a transação não for encontrada
        """
        transacao = Transacao.query.get(transacao_id)
        if not transacao:
            raise NotFoundError(f'Transação com ID {transacao_id} não encontrada')
        return transacao
    
    @staticmethod
    def atualizar_transacao(transacao_id, dados):
        """
        Atualiza uma transação existente.
        
        Args:
            transacao_id: ID da transação
            dados: Dicionário com dados a atualizar
        
        Returns:
            Transacao: Objeto Transacao atualizado
        
        Raises:
            NotFoundError: Se a transação não for encontrada
            ValidationError: Se os dados forem inválidos
        """
        transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
        
        # Atualiza campos permitidos
        if 'status' in dados:
            transacao.status = dados['status']
        if 'valor' in dados:
            if dados['valor'] <= 0:
                raise ValidationError('Valor deve ser maior que zero')
            transacao.valor = dados['valor']
        
        try:
            db.session.commit()
            return transacao
        except Exception as e:
            db.session.rollback()
            raise BusinessLogicError(f'Erro ao atualizar transação: {str(e)}')
    
    @staticmethod
    def deletar_transacao(transacao_id):
        """
        Deleta uma transação.
        
        Args:
            transacao_id: ID da transação
        
        Returns:
            bool: True se deletado com sucesso
        
        Raises:
            NotFoundError: Se a transação não for encontrada
        """
        transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
        
        try:
            db.session.delete(transacao)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise BusinessLogicError(f'Erro ao deletar transação: {str(e)}')
    
    @staticmethod
    def processar_transacao_na_blockchain(transacao_id):
        """
        Processa uma transação pendente na blockchain.
        
        Args:
            transacao_id: ID da transação
        
        Returns:
            Transacao: Transação atualizada
        
        Raises:
            NotFoundError: Se a transação não for encontrada
            BusinessLogicError: Se a transação já foi processada ou falhar
        """
        transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
        
        if transacao.status in ['processada', 'processando']:
            raise BusinessLogicError('Transação já está sendo processada ou foi processada')
        
        if transacao.signature:
            raise BusinessLogicError('Transação já possui signature na blockchain')
        
        try:
            # Cria e envia transação
            solana_transaction = SolanaService.criar_transacao(
                transacao.carteira_origem,
                transacao.carteira_destino,
                float(transacao.valor)
            )
            signature = SolanaService.enviar_transacao(solana_transaction)
            
            # Atualiza transação
            transacao.signature = signature
            transacao.status = 'processando'
            transacao.confirmation_status = 'pending'
            
            db.session.commit()
            return transacao
        except Exception as e:
            db.session.rollback()
            transacao.status = 'falhou'
            db.session.commit()
            raise BusinessLogicError(f'Erro ao processar transação: {str(e)}')
    
    @staticmethod
    def atualizar_status_blockchain(transacao_id):
        """
        Consulta e atualiza status de uma transação na blockchain.
        
        Args:
            transacao_id: ID da transação
        
        Returns:
            Transacao: Transação atualizada
        
        Raises:
            NotFoundError: Se a transação não for encontrada
            BusinessLogicError: Se não houver signature
        """
        transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
        
        if not transacao.signature:
            raise BusinessLogicError('Transação não possui signature para consultar')
        
        try:
            tx_info = SolanaService.consultar_transacao(transacao.signature)
            
            # Atualiza status
            if tx_info['status'] == 'found':
                transacao.confirmation_status = tx_info['confirmation_status']
                transacao.block_slot = tx_info['block_slot']
                
                if tx_info['fee']:
                    transacao.fee = tx_info['fee']
                
                # Atualiza status geral
                if tx_info['confirmation_status'] == 'confirmed':
                    transacao.status = 'processada'
                elif tx_info['confirmation_status'] == 'failed':
                    transacao.status = 'falhou'
                elif tx_info['confirmation_status'] == 'finalized':
                    transacao.status = 'processada'
            else:
                transacao.confirmation_status = 'pending'
            
            db.session.commit()
            return transacao
        except Exception as e:
            db.session.rollback()
            raise BusinessLogicError(f'Erro ao atualizar status: {str(e)}')
    
    @staticmethod
    def cancelar_transacao(transacao_id):
        """
        Cancela uma transação pendente.
        
        Args:
            transacao_id: ID da transação
        
        Returns:
            Transacao: Transação cancelada
        
        Raises:
            NotFoundError: Se a transação não for encontrada
            BusinessLogicError: Se a transação não puder ser cancelada
        """
        transacao = TransacaoService.buscar_transacao_por_id(transacao_id)
        
        if transacao.status in ['processada', 'processando']:
            raise BusinessLogicError('Não é possível cancelar transação já processada ou em processamento')
        
        if transacao.signature:
            raise BusinessLogicError('Não é possível cancelar transação já enviada para blockchain')
        
        try:
            transacao.status = 'cancelada'
            db.session.commit()
            return transacao
        except Exception as e:
            db.session.rollback()
            raise BusinessLogicError(f'Erro ao cancelar transação: {str(e)}')




