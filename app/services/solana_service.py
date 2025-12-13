"""
Service layer para integração com Solana blockchain.
"""
import os
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.rpc.responses import GetTransactionResp
from app.config import Config
from app.utils.solana_utils import (
    validar_endereco_solana,
    converter_sol_para_lamports,
    converter_lamports_para_sol,
    calcular_taxa_transacao,
    formatar_erro_solana
)
from app.utils.exceptions import (
    SolanaConnectionError,
    InsufficientFundsError,
    InvalidAddressError,
    TransactionFailedError
)


class SolanaService:
    """
    Service para operações com Solana blockchain.
    
    Gerencia conexão com RPC, validação de carteiras,
    consulta de saldos e envio de transações.
    """
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """
        Retorna cliente Solana RPC (singleton).
        
        Returns:
            Client: Cliente Solana RPC
        """
        if cls._client is None:
            rpc_url = os.environ.get('SOLANA_RPC_URL', Config.SOLANA_RPC_URL)
            try:
                cls._client = Client(rpc_url)
            except Exception as e:
                raise SolanaConnectionError(f'Erro ao conectar com Solana RPC: {str(e)}')
        return cls._client
    
    @staticmethod
    def validar_carteira(address: str) -> bool:
        """
        Valida formato de endereço Solana.
        
        Args:
            address: Endereço Solana
        
        Returns:
            bool: True se válido
        
        Raises:
            InvalidAddressError: Se o endereço for inválido
        """
        return validar_endereco_solana(address)
    
    @staticmethod
    def obter_saldo(carteira: str) -> float:
        """
        Consulta saldo de uma carteira na blockchain.
        
        Args:
            carteira: Endereço da carteira Solana
        
        Returns:
            float: Saldo em SOL
        
        Raises:
            InvalidAddressError: Se a carteira for inválida
            SolanaConnectionError: Se houver erro de conexão
        """
        try:
            SolanaService.validar_carteira(carteira)
            client = SolanaService.get_client()
            pubkey = Pubkey.from_string(carteira)
            
            commitment = Commitment(os.environ.get('SOLANA_COMMITMENT', 'confirmed'))
            response = client.get_balance(pubkey, commitment=commitment)
            
            if response.value is None:
                raise SolanaConnectionError('Não foi possível obter saldo da carteira')
            
            lamports = response.value
            return converter_lamports_para_sol(lamports)
        except InvalidAddressError:
            raise
        except Exception as e:
            if isinstance(e, (SolanaConnectionError, InvalidAddressError)):
                raise
            raise SolanaConnectionError(f'Erro ao consultar saldo: {formatar_erro_solana(e)}')
    
    @staticmethod
    def verificar_saldo_suficiente(carteira: str, valor: float, fee: float = None) -> bool:
        """
        Verifica se a carteira tem saldo suficiente para a transação.
        
        Args:
            carteira: Endereço da carteira
            valor: Valor da transação em SOL
            fee: Taxa da transação em SOL (opcional)
        
        Returns:
            bool: True se há saldo suficiente
        
        Raises:
            InsufficientFundsError: Se o saldo for insuficiente
        """
        if fee is None:
            fee_lamports = calcular_taxa_transacao()
            fee = converter_lamports_para_sol(fee_lamports)
        
        saldo = SolanaService.obter_saldo(carteira)
        valor_total = valor + fee
        
        if saldo < valor_total:
            raise InsufficientFundsError(
                f'Saldo insuficiente. Disponível: {saldo:.9f} SOL, Necessário: {valor_total:.9f} SOL'
            )
        
        return True
    
    @staticmethod
    def criar_transacao(carteira_origem: str, carteira_destino: str, valor: float) -> Transaction:
        """
        Cria uma transação Solana para transferência.
        
        Args:
            carteira_origem: Endereço da carteira de origem
            carteira_destino: Endereço da carteira de destino
            valor: Valor em SOL
        
        Returns:
            Transaction: Transação Solana criada
        
        Raises:
            InvalidAddressError: Se algum endereço for inválido
        """
        SolanaService.validar_carteira(carteira_origem)
        SolanaService.validar_carteira(carteira_destino)
        
        from_pubkey = Pubkey.from_string(carteira_origem)
        to_pubkey = Pubkey.from_string(carteira_destino)
        lamports = converter_sol_para_lamports(valor)
        
        transaction = Transaction()
        transaction.add(transfer(
            TransferParams(
                from_pubkey=from_pubkey,
                to_pubkey=to_pubkey,
                lamports=lamports
            )
        ))
        
        return transaction
    
    @staticmethod
    def enviar_transacao(transaction: Transaction, private_key: str = None) -> str:
        """
        Envia transação para a blockchain Solana.
        
        Args:
            transaction: Transação Solana
            private_key: Chave privada para assinar (opcional, usa SOLANA_PRIVATE_KEY se não fornecido)
        
        Returns:
            str: Signature da transação
        
        Raises:
            TransactionFailedError: Se a transação falhar
            SolanaConnectionError: Se houver erro de conexão
        """
        try:
            client = SolanaService.get_client()
            
            # Obtém chave privada
            if private_key is None:
                private_key = os.environ.get('SOLANA_PRIVATE_KEY')
            
            if not private_key:
                raise TransactionFailedError('Chave privada não fornecida para assinar transação')
            
            # Converte chave privada para Keypair
            try:
                # Se for string base58, decodifica
                if isinstance(private_key, str):
                    import base58
                    key_bytes = base58.b58decode(private_key)
                    keypair = Keypair.from_bytes(key_bytes)
                else:
                    keypair = Keypair.from_bytes(private_key)
            except Exception as e:
                raise TransactionFailedError(f'Erro ao processar chave privada: {str(e)}')
            
            # Envia transação
            commitment = Commitment(os.environ.get('SOLANA_COMMITMENT', 'confirmed'))
            opts = TxOpts(skip_preflight=False, preflight_commitment=commitment)
            
            response = client.send_transaction(transaction, keypair, opts=opts)
            
            if response.value is None:
                raise TransactionFailedError('Transação não foi enviada')
            
            signature = str(response.value)
            return signature
            
        except TransactionFailedError:
            raise
        except Exception as e:
            if isinstance(e, TransactionFailedError):
                raise
            raise TransactionFailedError(f'Erro ao enviar transação: {formatar_erro_solana(e)}')
    
    @staticmethod
    def consultar_transacao(signature: str) -> dict:
        """
        Consulta status de uma transação na blockchain.
        
        Args:
            signature: Signature da transação
        
        Returns:
            dict: Dados da transação com status de confirmação
        
        Raises:
            SolanaConnectionError: Se houver erro de conexão
        """
        try:
            client = SolanaService.get_client()
            commitment = Commitment(os.environ.get('SOLANA_COMMITMENT', 'confirmed'))
            
            response = client.get_transaction(signature, commitment=commitment)
            
            if response.value is None:
                return {
                    'status': 'not_found',
                    'confirmation_status': None,
                    'block_slot': None
                }
            
            tx_data: GetTransactionResp = response.value
            slot = tx_data.slot if hasattr(tx_data, 'slot') else None
            
            # Determina status de confirmação
            if tx_data.meta and hasattr(tx_data.meta, 'err'):
                if tx_data.meta.err is None:
                    confirmation_status = 'confirmed' if commitment == Commitment.Confirmed else 'finalized'
                else:
                    confirmation_status = 'failed'
            else:
                confirmation_status = 'pending'
            
            return {
                'status': 'found',
                'confirmation_status': confirmation_status,
                'block_slot': slot,
                'fee': converter_lamports_para_sol(tx_data.meta.fee) if tx_data.meta and hasattr(tx_data.meta, 'fee') else None
            }
        except Exception as e:
            raise SolanaConnectionError(f'Erro ao consultar transação: {formatar_erro_solana(e)}')
    
    @staticmethod
    def converter_sol_para_lamports(valor_sol: float) -> int:
        """Converte SOL para lamports."""
        return converter_sol_para_lamports(valor_sol)
    
    @staticmethod
    def converter_lamports_para_sol(lamports: int) -> float:
        """Converte lamports para SOL."""
        return converter_lamports_para_sol(lamports)

