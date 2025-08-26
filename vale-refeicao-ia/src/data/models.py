"""
Modelos de dados usando SQLAlchemy
"""

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, 
    Boolean, ForeignKey, Text, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Empresa(Base):
    """Modelo para empresas/clientes"""
    __tablename__ = 'empresas'
    
    id = Column(Integer, primary_key=True)
    cnpj = Column(String(18), unique=True, nullable=False)
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    endereco = Column(String(500))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(9))
    
    # Configurações de VR
    valor_dia_util = Column(Float, default=35.00)
    desconto_funcionario_pct = Column(Float, default=0.20)
    
    # Relacionamentos
    funcionarios = relationship("Funcionario", back_populates="empresa")
    calculos = relationship("CalculoValeRefeicao", back_populates="empresa")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Funcionario(Base):
    """Modelo para funcionários"""
    __tablename__ = 'funcionarios'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    matricula = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14))
    rg = Column(String(20))
    data_nascimento = Column(Date)
    
    # Dados profissionais
    cargo = Column(String(100))
    departamento = Column(String(100))
    centro_custo = Column(String(50))
    data_admissao = Column(Date)
    data_demissao = Column(Date)
    tipo_contrato = Column(String(50))  # CLT, PJ, Estagiário, etc
    salario = Column(Float)
    status = Column(String(50))  # Ativo, Afastado, Férias, etc
    
    # Contato
    email = Column(String(200))
    telefone = Column(String(20))
    endereco = Column(Text)
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(9))
    
    # Dados bancários
    banco = Column(String(50))
    agencia = Column(String(10))
    conta = Column(String(20))
    
    # Metadados
    dados_complementares = Column(JSON)  # Para campos adicionais não mapeados
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="funcionarios")
    vr_funcionario = relationship("FuncionarioVR", back_populates="funcionario")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para performance
    __table_args__ = (
        Index('idx_funcionario_empresa_matricula', 'empresa_id', 'matricula', unique=True),
        Index('idx_funcionario_cpf', 'cpf'),
        Index('idx_funcionario_nome', 'nome'),
    )

class CalculoValeRefeicao(Base):
    """Modelo para cálculos mensais de VR"""
    __tablename__ = 'calculos_vr'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    mes_referencia = Column(String(7), nullable=False)  # YYYY-MM
    
    # Parâmetros utilizados
    valor_dia_util = Column(Float, nullable=False)
    desconto_funcionario_pct = Column(Float, nullable=False)
    dias_uteis_mes = Column(Integer, nullable=False)
    
    # Totais
    total_funcionarios = Column(Integer, default=0)
    funcionarios_elegiveis = Column(Integer, default=0)
    valor_total_vr = Column(Float, default=0.0)
    total_desconto_funcionario = Column(Float, default=0.0)
    total_liquido_empresa = Column(Float, default=0.0)
    
    # Status e processamento
    status = Column(String(50), default='pendente')  # pendente, processando, concluido, erro
    processado_por = Column(String(100))
    observacoes = Column(Text)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="calculos")
    funcionarios_vr = relationship("FuncionarioVR", back_populates="calculo")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Índices
    __table_args__ = (
        Index('idx_calculo_empresa_mes', 'empresa_id', 'mes_referencia', unique=True),
    )

class FuncionarioVR(Base):
    """Modelo para VR individual por funcionário"""
    __tablename__ = 'funcionarios_vr'
    
    id = Column(Integer, primary_key=True)
    calculo_id = Column(Integer, ForeignKey('calculos_vr.id'), nullable=False)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Dados do cálculo
    elegivel = Column(Boolean, default=True)
    dias_trabalhados = Column(Integer, default=0)
    dias_desconto = Column(Integer, default=0)
    faltas = Column(Integer, default=0)
    
    # Valores
    valor_total_vr = Column(Float, default=0.0)
    desconto_funcionario = Column(Float, default=0.0)
    valor_liquido_empresa = Column(Float, default=0.0)
    
    # Observações e ajustes
    observacoes = Column(Text)
    ajuste_manual = Column(Float, default=0.0)
    motivo_ajuste = Column(String(200))
    
    # Relacionamentos
    calculo = relationship("CalculoValeRefeicao", back_populates="funcionarios_vr")
    funcionario = relationship("Funcionario", back_populates="vr_funcionario")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_funcionario_vr_calculo', 'calculo_id', 'funcionario_id', unique=True),
    )

class ImportacaoArquivo(Base):
    """Modelo para controle de importações"""
    __tablename__ = 'importacoes'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    
    # Informações do arquivo
    nome_arquivo = Column(String(255), nullable=False)
    tipo_arquivo = Column(String(50))  # principal, complementar, etc
    formato = Column(String(10))  # csv, xlsx, xls
    tamanho_bytes = Column(Integer)
    
    # Processamento
    status = Column(String(50), default='pendente')
    total_linhas = Column(Integer, default=0)
    linhas_processadas = Column(Integer, default=0)
    linhas_erro = Column(Integer, default=0)
    
    # Mapeamento de colunas (JSON)
    mapeamento_colunas = Column(JSON)
    
    # Log e erros
    log_processamento = Column(Text)
    erros = Column(JSON)
    
    # Agente que processou
    agente_processamento = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

class RegraCalculoVR(Base):
    """Modelo para regras customizadas de cálculo"""
    __tablename__ = 'regras_calculo_vr'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    
    nome_regra = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo_regra = Column(String(50))  # eligibilidade, valor, desconto, etc
    
    # Condições e ações em formato JSON
    condicoes = Column(JSON)
    acoes = Column(JSON)
    
    # Prioridade (regras com maior prioridade são aplicadas primeiro)
    prioridade = Column(Integer, default=0)
    ativa = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentLog(Base):
    """Modelo para logs dos agentes IA"""
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    
    # Contexto
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    calculo_id = Column(Integer, ForeignKey('calculos_vr.id'))
    
    # Detalhes
    input_data = Column(JSON)
    output_data = Column(JSON)
    tokens_used = Column(Integer)
    processing_time_ms = Column(Integer)
    
    # Status
    status = Column(String(50))  # success, error, warning
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_agent_log_timestamp', 'created_at'),
        Index('idx_agent_log_agent', 'agent_name'),
    )
