"""
Configuração de testes com pytest.
"""
import pytest
from app import create_app, db


@pytest.fixture
def app():
    """
    Cria uma instância da aplicação para testes.
    
    Returns:
        Flask: Aplicação Flask configurada para testes
    """
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Cria um cliente de teste.
    
    Args:
        app: Aplicação Flask
    
    Returns:
        FlaskClient: Cliente de teste
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Cria um runner de comandos CLI.
    
    Args:
        app: Aplicação Flask
    
    Returns:
        FlaskCliRunner: Runner de comandos
    """
    return app.test_cli_runner()




