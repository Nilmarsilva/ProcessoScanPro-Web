"""
Script para criar tabelas Judit no PostgreSQL do Docker
Execute DENTRO do container backend ou via docker exec
"""
import os

# Usa a URL do Docker (já está no environment do container)
# DATABASE_URL=postgresql://postgres:postgres@db:5432/processoscanpro

from app.db.base import engine, Base
from app.models.judit import JuditBatch, JuditRequest, JuditResult

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/processoscanpro')
    print(f"Criando tabelas Judit no PostgreSQL...")
    print(f"Banco: {db_url}")
    
    try:
        # Cria todas as tabelas definidas nos models
        Base.metadata.create_all(bind=engine)
        print("\n✓ Tabelas criadas com sucesso!")
        print("  - judit_batches")
        print("  - judit_requests")
        print("  - judit_results")
    except Exception as e:
        print(f"\n✗ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    create_tables()
