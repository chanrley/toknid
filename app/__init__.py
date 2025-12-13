"""
Factory do Flask Application.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api
from app.config import config
import os

db = SQLAlchemy()
ma = Marshmallow()
api = Api(
    version='1.0',
    title='API de Transações',
    description='API RESTful para gerenciamento de transações',
    doc='/api/docs'
)


def create_app(config_name=None):
    """
    Cria e configura a aplicação Flask.
    
    Args:
        config_name: Nome da configuração a usar (development, production, testing)
    
    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    app = Flask(__name__)
    
    # Carrega configuração
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    ma.init_app(app)
    
    # Registra blueprint da API
    from app.controllers.transacao_controller import ns, ns_carteiras
    api.add_namespace(ns)
    api.add_namespace(ns_carteiras)
    api.init_app(app)
    
    # Cria tabelas do banco
    with app.app_context():
        db.create_all()
    
    # Registra handlers de erro
    from app.utils.exceptions import register_error_handlers
    register_error_handlers(app)
    
    return app

