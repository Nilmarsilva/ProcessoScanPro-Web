# ProcessoScanPro - Web

Versão web do ProcessoScanPro com arquitetura moderna e autenticação JWT.

## 🏗️ Arquitetura

```
ProcessoScanPro-Web/
├── backend/          # API FastAPI com JWT
└── frontend/         # React + Vite + TailwindCSS
```

## 🚀 Início Rápido

### Opção 1: Docker (Recomendado)

**Pré-requisito**: Docker Desktop instalado e rodando

```bash
# 1. Configurar .env
cd backend
copy .env.docker .env
# Edite .env e configure SECRET_KEY, JUDIT_API_KEY, etc

# 2. Voltar para raiz e iniciar
cd ..
docker-compose up -d

# Ou use o script (Windows)
start.bat
```

**Acessar:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

**Parar:**
```bash
docker-compose down
# Ou use: stop.bat
```

📖 **Documentação completa**: [DOCKER.md](./DOCKER.md)

---

### Opção 2: Manual (Desenvolvimento)

#### 1. Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Edite o .env e configure SECRET_KEY e DATABASE_URL

# Executar
python run.py
```

Backend estará em: `http://localhost:8000`
Documentação: `http://localhost:8000/docs`

#### 2. Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar .env
cp .env.example .env

# Executar
npm run dev
```

Frontend estará em: `http://localhost:3000`

## 📚 Documentação

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens):

1. **Registro**: `POST /api/auth/register`
2. **Login**: `POST /api/auth/login`
3. **Refresh**: `POST /api/auth/refresh`

## 🎯 Funcionalidades Implementadas

### ✅ Backend
- [x] Autenticação JWT completa
- [x] Registro de usuários
- [x] Login com refresh token
- [x] Proteção de rotas
- [x] SQLAlchemy ORM
- [x] Documentação Swagger

### ✅ Frontend
- [x] Página de Login moderna
- [x] Página de Registro
- [x] Dashboard básico
- [x] Gerenciamento de estado (Zustand)
- [x] Rotas protegidas
- [x] Interceptor Axios com refresh automático
- [x] Design responsivo com TailwindCSS

## 🔄 Próximas Etapas

### Backend
- [ ] Endpoint para upload de planilhas
- [ ] Integração com API Judit
- [ ] Webhook para receber callbacks
- [ ] Fila de tarefas (Celery)
- [ ] WebSocket para notificações

### Frontend
- [ ] Página de upload de planilhas
- [ ] Visualização de processos
- [ ] Filtros e busca
- [ ] Exportação de relatórios
- [ ] Notificações em tempo real

## 🛠️ Stack Tecnológica

### Backend
- FastAPI
- SQLAlchemy
- JWT (python-jose)
- Bcrypt
- Uvicorn

### Frontend
- React 18
- Vite
- TailwindCSS
- React Router
- Zustand
- Axios
- Lucide Icons

## 📦 Deploy

### Backend (Docker)
```bash
cd backend
docker build -t processoscanpro-backend .
docker run -p 8000:8000 processoscanpro-backend
```

### Frontend (Docker)
```bash
cd frontend
docker build -t processoscanpro-frontend .
docker run -p 3000:3000 processoscanpro-frontend
```

## 🔑 Gerar SECRET_KEY

Para gerar uma chave secreta segura para o backend:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📝 Licença

© 2025 ProcessoScanPro. Todos os direitos reservados.
