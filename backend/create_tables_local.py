"""
Script para criar tabelas Judit no banco de dados LOCAL (SQLite)
Para desenvolvimento local sem Docker
"""
import os
import sys

# Força usar SQLite local
os.environ['DATABASE_URL'] = 'sqlite:///./processoscanpro.db'

from app.db.base import engine, Base
from app.models.judit import JuditBatch, JuditRequest, JuditResult

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("Criando tabelas Judit no SQLite local...")
    print(f"Banco: {os.environ['DATABASE_URL']}")
    
    try:
        # Cria todas as tabelas definidas nos models
        Base.metadata.create_all(bind=engine)
        print("\n✓ Tabelas criadas com sucesso!")
        print("  - judit_batches")
        print("  - judit_requests")
        print("  - judit_results")
        print("\nArquivo do banco: ./processoscanpro.db")
    except Exception as e:
        print(f"\n✗ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
