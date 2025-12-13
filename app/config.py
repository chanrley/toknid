"""
Configurações da aplicação Flask.
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.parent
instance_path = basedir / 'instance'


class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        f'sqlite:///{instance_path / "database.db"}'
    
    # Flask-RESTX
    RESTX_MASK_SWAGGER = False
    
    # Solana Configuration
    SOLANA_NETWORK = os.environ.get('SOLANA_NETWORK', 'devnet')
    SOLANA_RPC_URL = os.environ.get('SOLANA_RPC_URL') or \
        ('https://api.devnet.solana.com' if os.environ.get('SOLANA_NETWORK', 'devnet') == 'devnet' 
         else 'https://api.mainnet-beta.solana.com')
    SOLANA_COMMITMENT = os.environ.get('SOLANA_COMMITMENT', 'confirmed')
    SOLANA_PRIVATE_KEY = os.environ.get('SOLANA_PRIVATE_KEY', None)


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}




