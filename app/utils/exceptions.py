"""
Exceções customizadas e handlers de erro.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ValidationError(Exception):
    """Exceção para erros de validação."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Exceção para erros de lógica de negócio."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exceção para recursos não encontrados."""
    def __init__(self, message="Recurso não encontrado", status_code=404):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SolanaConnectionError(Exception):
    """Exceção para erros de conexão com Solana RPC."""
    def __init__(self, message="Erro ao conectar com Solana RPC", status_code=503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InsufficientFundsError(Exception):
    """Exceção para saldo insuficiente."""
    def __init__(self, message="Saldo insuficiente para realizar a transação", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidAddressError(Exception):
    """Exceção para endereço Solana inválido."""
    def __init__(self, message="Endereço Solana inválido", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class TransactionFailedError(Exception):
    """Exceção para falha na transação blockchain."""
    def __init__(self, message="Falha ao processar transação na blockchain", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def register_error_handlers(app):
    """
    Registra handlers de erro na aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handler para erros de validação."""
        return jsonify({
            'error': 'Erro de validação',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_error(error):
        """Handler para erros de lógica de negócio."""
        return jsonify({
            'error': 'Erro de negócio',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """Handler para recursos não encontrados."""
        return jsonify({
            'error': 'Não encontrado',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handler para exceções HTTP."""
        return jsonify({
            'error': error.name,
            'message': error.description
        }), error.code
    
    @app.errorhandler(SolanaConnectionError)
    def handle_solana_connection_error(error):
        """Handler para erros de conexão Solana."""
        return jsonify({
            'error': 'Erro de conexão Solana',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(InsufficientFundsError)
    def handle_insufficient_funds_error(error):
        """Handler para saldo insuficiente."""
        return jsonify({
            'error': 'Saldo insuficiente',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(InvalidAddressError)
    def handle_invalid_address_error(error):
        """Handler para endereço inválido."""
        return jsonify({
            'error': 'Endereço inválido',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(TransactionFailedError)
    def handle_transaction_failed_error(error):
        """Handler para falha na transação."""
        return jsonify({
            'error': 'Falha na transação',
            'message': error.message
        }), error.status_code
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handler para erros internos."""
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado'
        }), 500




