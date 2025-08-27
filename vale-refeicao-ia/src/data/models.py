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

# MODELO REMOVIDO: Empresa
# Agora usamos tabelas dinâmicas e configurações via prompts de agentes autônomos
# class Empresa(Base):
#     """Modelo para empresas/clientes - DESCONTINUADO"""
#     __tablename__ = 'empresas'

# MODELO REMOVIDO: Funcionario
# Agora usamos tabelas dinâmicas criadas automaticamente a partir dos uploads
# class Funcionario(Base):
#     """Modelo para funcionários - DESCONTINUADO"""
#     __tablename__ = 'funcionarios'

# MODELO REMOVIDO: CalculoValeRefeicao  
# Agora os cálculos são feitos por agentes autônomos baseados em prompts
# Os resultados podem ser salvos em tabelas dinâmicas conforme necessário
# class CalculoValeRefeicao(Base):
#     """Modelo para cálculos mensais de VR - DESCONTINUADO"""
#     __tablename__ = 'calculos_vr'

# MODELO REMOVIDO: FuncionarioVR
# Agora os resultados de cálculos são gerados dinamicamente pelos agentes
# class FuncionarioVR(Base):
#     """Modelo para VR individual por funcionário - DESCONTINUADO"""
#     __tablename__ = 'funcionarios_vr'

class ImportacaoArquivo(Base):
    """Modelo para controle de importações"""
    __tablename__ = 'importacoes'
    
    id = Column(Integer, primary_key=True)
    # empresa_id removido - agora usamos tabelas dinâmicas
    
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

# MODELO REMOVIDO: RegraCalculoVR
# Agora as regras são definidas via prompts nos agentes autônomos
# class RegraCalculoVR(Base):
#     """Modelo para regras customizadas de cálculo - DESCONTINUADO"""
#     __tablename__ = 'regras_calculo_vr'

class AgentLog(Base):
    """Modelo para logs dos agentes IA"""
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    
    # Contexto - removidas referências às tabelas antigas
    # empresa_id e calculo_id removidos - agora usamos sistema dinâmico
    
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
