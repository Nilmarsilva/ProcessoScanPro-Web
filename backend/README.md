# ProcessoScanPro - Backend

Backend da aplicação ProcessoScanPro desenvolvido com FastAPI.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **JWT** - Autenticação com JSON Web Tokens
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## 📋 Pré-requisitos

- Python 3.10+
- pip

## 🔧 Instalação

1. **Criar ambiente virtual:**
```bash
python -m venv venv
```

2. **Ativar ambiente virtual:**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

3. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

4. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:
- `SECRET_KEY` - Chave secreta para JWT (gere uma aleatória)
- `DATABASE_URL` - URL do banco de dados
- `JUDIT_API_KEY` - Sua API key da Judit

## 🎯 Executar

```bash
python run.py
```

O servidor estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

Após iniciar o servidor, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Autenticação

### Registrar novo usuário
```bash
POST /api/auth/register
{
  "email": "usuario@email.com",
  "username": "usuario",
  "password": "senha123",
  "full_name": "Nome Completo"
}
```

### Login
```bash
POST /api/auth/login
{
  "username": "usuario",
  "password": "senha123"
}
```

Retorna:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Usar token
Adicione o header em todas as requisições protegidas:
```
Authorization: Bearer {access_token}
```

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependências da API
│   │   └── routes/
│   │       └── auth.py      # Rotas de autenticação
│   ├── core/
│   │   ├── config.py        # Configurações
│   │   └── security.py      # Funções de segurança
│   ├── db/
│   │   └── base.py          # Configuração do banco
│   ├── models/
│   │   └── user.py          # Modelo de usuário
│   ├── schemas/
│   │   └── user.py          # Schemas Pydantic
│   └── main.py              # Aplicação principal
├── .env.example             # Exemplo de variáveis de ambiente
├── requirements.txt         # Dependências
└── run.py                   # Script de inicialização
```

## 🔑 Gerar SECRET_KEY

Para gerar uma chave secreta segura:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🐳 Docker (Opcional)

```bash
docker build -t processoscanpro-backend .
docker run -p 8000:8000 processoscanpro-backend
```
