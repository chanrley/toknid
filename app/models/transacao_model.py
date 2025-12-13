"""
Modelo de Transação.
"""
from datetime import datetime
from app import db


class Transacao(db.Model):
    """
    Modelo de Transação.
    
    Representa uma transação financeira entre carteiras.
    """
    __tablename__ = 'transacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    carteira_origem = db.Column(db.String(100), nullable=False, index=True)
    carteira_destino = db.Column(db.String(100), nullable=False, index=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_transacao = db.Column(db.String(20), nullable=False, default='send')
    senha_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Campos blockchain Solana
    signature = db.Column(db.String(128), nullable=True, index=True)
    block_slot = db.Column(db.BigInteger, nullable=True)
    confirmation_status = db.Column(db.String(20), nullable=True, default='pending')
    network = db.Column(db.String(20), nullable=True, default='devnet')
    fee = db.Column(db.Numeric(10, 2), nullable=True)
    
    def __repr__(self):
        return f'<Transacao {self.id}: {self.carteira_origem} -> {self.carteira_destino} - {self.valor}>'
    
    def to_dict(self):
        """
        Converte o modelo para dicionário.
        
        Returns:
            dict: Dicionário com os dados da transação
        """
        return {
            'id': self.id,
            'carteira_origem': self.carteira_origem,
            'carteira_destino': self.carteira_destino,
            'valor': float(self.valor),
            'tipo_transacao': self.tipo_transacao,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'signature': self.signature,
            'block_slot': self.block_slot,
            'confirmation_status': self.confirmation_status,
            'network': self.network,
            'fee': float(self.fee) if self.fee else None
        }




