"""
Script para criar usuário admin
"""
from app.db.base import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    
    try:
        # Verifica se usuário já existe
        existing_user = db.query(User).filter(User.email == 'alex.guimaraes@abvat.com.br').first()
        
        if existing_user:
            print('❌ Usuário já existe!')
            return
        
        # Cria admin
        admin = User(
            email='alex.guimaraes@abvat.com.br',
            username='alex.guimaraes',
            full_name='Alex Guimarães',
            hashed_password=get_password_hash('Hoh67552013'),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin)
        db.commit()
        
        print('✓ Admin criado com sucesso!')
        print('Email: alex.guimaraes@abvat.com.br')
        print('Username: alex.guimaraes')
        print('Senha: Hoh67552013')
        
    except Exception as e:
        print(f'❌ Erro ao criar admin: {str(e)}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()
