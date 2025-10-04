"""add cpf cnpj columns

Revision ID: add_cpf_cnpj_001
Revises: 
Create Date: 2025-01-04 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cpf_cnpj_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona colunas CPF e CNPJ na tabela judit_requests
    op.add_column('judit_requests', sa.Column('cpf', sa.String(length=11), nullable=True))
    op.add_column('judit_requests', sa.Column('cnpj', sa.String(length=14), nullable=True))
    
    # Adiciona colunas CPF e CNPJ na tabela judit_results
    op.add_column('judit_results', sa.Column('cpf', sa.String(length=11), nullable=True))
    op.add_column('judit_results', sa.Column('cnpj', sa.String(length=14), nullable=True))


def downgrade():
    # Remove colunas CPF e CNPJ da tabela judit_results
    op.drop_column('judit_results', 'cnpj')
    op.drop_column('judit_results', 'cpf')
    
    # Remove colunas CPF e CNPJ da tabela judit_requests
    op.drop_column('judit_requests', 'cnpj')
    op.drop_column('judit_requests', 'cpf')
