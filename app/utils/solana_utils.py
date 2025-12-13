"""
Utilitários para integração com Solana.
"""
import base58
from app.utils.exceptions import InvalidAddressError

# Constantes Solana
LAMPORTS_PER_SOL = 1_000_000_000  # 1 SOL = 1 bilhão de lamports
MIN_TRANSACTION_FEE = 5000  # Taxa mínima em lamports
SOLANA_ADDRESS_LENGTH = 32  # Tamanho do endereço em bytes (base58)


def validar_endereco_solana(address: str) -> bool:
    """
    Valida se um endereço Solana é válido.
    
    Args:
        address: Endereço Solana em formato string
    
    Returns:
        bool: True se o endereço é válido, False caso contrário
    
    Raises:
        InvalidAddressError: Se o endereço for inválido
    """
    if not address or not isinstance(address, str):
        raise InvalidAddressError('Endereço não pode ser vazio')
    
    if len(address) < 32 or len(address) > 44:
        raise InvalidAddressError('Endereço Solana deve ter entre 32 e 44 caracteres')
    
    try:
        # Tenta decodificar o endereço base58
        decoded = base58.b58decode(address)
        if len(decoded) != SOLANA_ADDRESS_LENGTH:
            raise InvalidAddressError('Endereço decodificado tem tamanho inválido')
        return True
    except Exception as e:
        raise InvalidAddressError(f'Endereço Solana inválido: {str(e)}')


def converter_sol_para_lamports(valor_sol: float) -> int:
    """
    Converte valor de SOL para lamports.
    
    Args:
        valor_sol: Valor em SOL
    
    Returns:
        int: Valor em lamports
    """
    return int(valor_sol * LAMPORTS_PER_SOL)


def converter_lamports_para_sol(lamports: int) -> float:
    """
    Converte valor de lamports para SOL.
    
    Args:
        lamports: Valor em lamports
    
    Returns:
        float: Valor em SOL
    """
    return lamports / LAMPORTS_PER_SOL


def calcular_taxa_transacao() -> int:
    """
    Retorna a taxa estimada de uma transação.
    
    Returns:
        int: Taxa em lamports
    """
    return MIN_TRANSACTION_FEE


def formatar_erro_solana(erro: Exception) -> str:
    """
    Formata erros do Solana para mensagens amigáveis.
    
    Args:
        erro: Exceção do Solana
    
    Returns:
        str: Mensagem de erro formatada
    """
    mensagem = str(erro)
    
    # Mapeia erros comuns
    if 'insufficient funds' in mensagem.lower():
        return 'Saldo insuficiente na carteira'
    elif 'invalid account' in mensagem.lower():
        return 'Carteira inválida'
    elif 'transaction failed' in mensagem.lower():
        return 'Transação falhou na blockchain'
    elif 'network' in mensagem.lower() or 'connection' in mensagem.lower():
        return 'Erro de conexão com a rede Solana'
    else:
        return f'Erro Solana: {mensagem}'

