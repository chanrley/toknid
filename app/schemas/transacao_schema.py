"""
Schemas de validação e serialização para Transação.
"""
from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class TransacaoCreateSchema(Schema):
    """
    Schema para criação de transação.
    
    Valida os dados de entrada para criação de uma nova transação.
    """
    carteira = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Carteira de origem é obrigatória'}
    )
    senha = fields.Str(
        required=True,
        validate=validate.Length(min=4, error='Senha deve ter no mínimo 4 caracteres'),
        error_messages={'required': 'Senha é obrigatória'},
        load_only=True
    )
    transacao = fields.Str(
        required=True,
        validate=validate.OneOf(['send'], error='Tipo de transação deve ser "send"'),
        error_messages={'required': 'Tipo de transação é obrigatório'}
    )
    valor = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.01, error='Valor deve ser maior que zero'),
        error_messages={'required': 'Valor é obrigatório'}
    )
    carteira_destino = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Carteira de destino é obrigatória'}
    )
    
    @validates_schema
    def validate_carteiras(self, data, **kwargs):
        """
        Valida que carteira origem e destino são diferentes.
        
        Args:
            data: Dados a validar
            **kwargs: Argumentos adicionais
        """
        if data.get('carteira') == data.get('carteira_destino'):
            raise ValidationError('Carteira de origem e destino não podem ser iguais')


class TransacaoUpdateSchema(Schema):
    """
    Schema para atualização de transação.
    """
    status = fields.Str(
        validate=validate.OneOf(['pendente', 'processada', 'cancelada', 'falhou']),
        allow_none=True
    )
    valor = fields.Decimal(
        validate=validate.Range(min=0.01),
        allow_none=True
    )


class TransacaoResponseSchema(Schema):
    """
    Schema para resposta de transação.
    
    Serializa os dados da transação para resposta da API.
    """
    id = fields.Int(dump_only=True)
    carteira_origem = fields.Str(dump_only=True)
    carteira_destino = fields.Str(dump_only=True)
    valor = fields.Decimal(dump_only=True, places=2)
    tipo_transacao = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    data_criacao = fields.DateTime(dump_only=True)
    data_atualizacao = fields.DateTime(dump_only=True, allow_none=True)
    signature = fields.Str(dump_only=True, allow_none=True)
    block_slot = fields.Int(dump_only=True, allow_none=True)
    confirmation_status = fields.Str(dump_only=True, allow_none=True)
    network = fields.Str(dump_only=True, allow_none=True)
    fee = fields.Decimal(dump_only=True, places=9, allow_none=True)


# Instâncias dos schemas
transacao_create_schema = TransacaoCreateSchema()
transacao_update_schema = TransacaoUpdateSchema()
transacao_response_schema = TransacaoResponseSchema()
transacoes_response_schema = TransacaoResponseSchema(many=True)

