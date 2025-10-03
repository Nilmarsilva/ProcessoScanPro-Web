"""
Script para criar tabelas Judit no banco de dados
Executa diretamente via SQLAlchemy
"""
from app.db.base import engine, Base
from app.models.judit import JuditBatch, JuditRequest, JuditResult

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("Criando tabelas Judit...")
    
    try:
        # Cria todas as tabelas definidas nos models
        Base.metadata.create_all(bind=engine)
        print("✓ Tabelas criadas com sucesso!")
        print("  - judit_batches")
        print("  - judit_requests")
        print("  - judit_results")
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        raise

if __name__ == "__main__":
    create_tables()
