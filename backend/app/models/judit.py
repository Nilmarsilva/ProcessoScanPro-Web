from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..db.base import Base

class JuditBatch(Base):
    """Lote de processamento Judit.io"""
    __tablename__ = "judit_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), unique=True, index=True, nullable=False)
    total = Column(Integer, default=0)
    processados = Column(Integer, default=0)
    sucesso = Column(Integer, default=0)
    erro = Column(Integer, default=0)
    on_demand = Column(Boolean, default=False)
    status = Column(String(50), default="processando")  # processando, aguardando_webhooks, concluído, erro
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class JuditRequest(Base):
    """Requisição individual para Judit.io"""
    __tablename__ = "judit_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), index=True, nullable=False)
    request_id = Column(String(100), unique=True, index=True)
    judit_request_id = Column(String(100), index=True)
    documento = Column(String(20))
    doc_type = Column(String(10))  # cpf, cnpj
    nome = Column(String(255))
    empresa = Column(String(255))
    status = Column(String(50), default="aguardando")  # aguardando, processando, concluído, erro
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class JuditResult(Base):
    """Resultado do processamento"""
    __tablename__ = "judit_results"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), index=True, nullable=False)
    request_id = Column(String(100), index=True)
    documento = Column(String(20))
    doc_type = Column(String(10))
    nome = Column(String(255))
    empresa = Column(String(255))
    status = Column(String(50))  # sucesso, erro
    qtd_processos = Column(Integer, default=0)
    processos = Column(JSON)  # Dados completos em JSON
    erro = Column(Text, nullable=True)
    processado_at = Column(DateTime(timezone=True), server_default=func.now())
