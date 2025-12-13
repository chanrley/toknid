"""
Testes para endpoints de transação.
"""
import json
import pytest
from app import db
from app.models.transacao_model import Transacao


class TestTransacaoCreate:
    """Testes para criação de transações."""
    
    def test_create_transacao_success(self, client):
        """Testa criação de transação com sucesso."""
        dados = {
            'carteira': 'carteira_origem_123',
            'senha': 'senha123',
            'transacao': 'send',
            'valor': 100.50,
            'carteira_destino': 'carteira_destino_456'
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['carteira_origem'] == 'carteira_origem_123'
        assert data['carteira_destino'] == 'carteira_destino_456'
        assert float(data['valor']) == 100.50
        assert data['tipo_transacao'] == 'send'
        assert data['status'] == 'pendente'
        assert 'id' in data
        assert 'data_criacao' in data
    
    def test_create_transacao_missing_fields(self, client):
        """Testa criação de transação com campos faltando."""
        dados = {
            'carteira': 'carteira_origem_123',
            'valor': 100.50
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_transacao_same_wallets(self, client):
        """Testa criação de transação com carteiras iguais."""
        dados = {
            'carteira': 'carteira_123',
            'senha': 'senha123',
            'transacao': 'send',
            'valor': 100.50,
            'carteira_destino': 'carteira_123'
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_transacao_invalid_transaction_type(self, client):
        """Testa criação de transação com tipo inválido."""
        dados = {
            'carteira': 'carteira_origem_123',
            'senha': 'senha123',
            'transacao': 'receive',
            'valor': 100.50,
            'carteira_destino': 'carteira_destino_456'
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_transacao_negative_value(self, client):
        """Testa criação de transação com valor negativo."""
        dados = {
            'carteira': 'carteira_origem_123',
            'senha': 'senha123',
            'transacao': 'send',
            'valor': -100.50,
            'carteira_destino': 'carteira_destino_456'
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_transacao_short_password(self, client):
        """Testa criação de transação com senha muito curta."""
        dados = {
            'carteira': 'carteira_origem_123',
            'senha': '123',
            'transacao': 'send',
            'valor': 100.50,
            'carteira_destino': 'carteira_destino_456'
        }
        
        response = client.post(
            '/api/transacoes',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestTransacaoList:
    """Testes para listagem de transações."""
    
    def test_list_transacoes_empty(self, client):
        """Testa listagem quando não há transações."""
        response = client.get('/api/transacoes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_list_transacoes_with_data(self, client):
        """Testa listagem com transações existentes."""
        # Cria transações de teste
        transacao1 = Transacao(
            carteira_origem='carteira_1',
            carteira_destino='carteira_2',
            valor=100.00,
            tipo_transacao='send',
            senha_hash='hash1',
            status='pendente'
        )
        transacao2 = Transacao(
            carteira_origem='carteira_3',
            carteira_destino='carteira_4',
            valor=200.00,
            tipo_transacao='send',
            senha_hash='hash2',
            status='processada'
        )
        
        with client.application.app_context():
            db.session.add(transacao1)
            db.session.add(transacao2)
            db.session.commit()
        
        response = client.get('/api/transacoes')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
    
    def test_list_transacoes_filter_by_status(self, client):
        """Testa listagem filtrada por status."""
        # Cria transações de teste
        transacao1 = Transacao(
            carteira_origem='carteira_1',
            carteira_destino='carteira_2',
            valor=100.00,
            tipo_transacao='send',
            senha_hash='hash1',
            status='pendente'
        )
        transacao2 = Transacao(
            carteira_origem='carteira_3',
            carteira_destino='carteira_4',
            valor=200.00,
            tipo_transacao='send',
            senha_hash='hash2',
            status='processada'
        )
        
        with client.application.app_context():
            db.session.add(transacao1)
            db.session.add(transacao2)
            db.session.commit()
        
        response = client.get('/api/transacoes?status=pendente')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['status'] == 'pendente'


class TestTransacaoDetail:
    """Testes para operações em transação específica."""
    
    def test_get_transacao_success(self, client):
        """Testa busca de transação por ID."""
        transacao = Transacao(
            carteira_origem='carteira_1',
            carteira_destino='carteira_2',
            valor=100.00,
            tipo_transacao='send',
            senha_hash='hash1',
            status='pendente'
        )
        
        with client.application.app_context():
            db.session.add(transacao)
            db.session.commit()
            transacao_id = transacao.id
        
        response = client.get(f'/api/transacoes/{transacao_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == transacao_id
        assert data['carteira_origem'] == 'carteira_1'
    
    def test_get_transacao_not_found(self, client):
        """Testa busca de transação inexistente."""
        response = client.get('/api/transacoes/999')
        
        assert response.status_code == 404
    
    def test_update_transacao_success(self, client):
        """Testa atualização de transação."""
        transacao = Transacao(
            carteira_origem='carteira_1',
            carteira_destino='carteira_2',
            valor=100.00,
            tipo_transacao='send',
            senha_hash='hash1',
            status='pendente'
        )
        
        with client.application.app_context():
            db.session.add(transacao)
            db.session.commit()
            transacao_id = transacao.id
        
        dados_update = {
            'status': 'processada'
        }
        
        response = client.put(
            f'/api/transacoes/{transacao_id}',
            data=json.dumps(dados_update),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'processada'
    
    def test_update_transacao_not_found(self, client):
        """Testa atualização de transação inexistente."""
        dados_update = {
            'status': 'processada'
        }
        
        response = client.put(
            '/api/transacoes/999',
            data=json.dumps(dados_update),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_delete_transacao_success(self, client):
        """Testa deleção de transação."""
        transacao = Transacao(
            carteira_origem='carteira_1',
            carteira_destino='carteira_2',
            valor=100.00,
            tipo_transacao='send',
            senha_hash='hash1',
            status='pendente'
        )
        
        with client.application.app_context():
            db.session.add(transacao)
            db.session.commit()
            transacao_id = transacao.id
        
        response = client.delete(f'/api/transacoes/{transacao_id}')
        
        assert response.status_code == 204
        
        # Verifica que foi deletada
        response_get = client.get(f'/api/transacoes/{transacao_id}')
        assert response_get.status_code == 404
    
    def test_delete_transacao_not_found(self, client):
        """Testa deleção de transação inexistente."""
        response = client.delete('/api/transacoes/999')
        
        assert response.status_code == 404




