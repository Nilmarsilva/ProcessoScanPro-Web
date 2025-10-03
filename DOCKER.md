# ProcessoScanPro - Docker Setup

Guia completo para executar o ProcessoScanPro usando Docker Desktop.

## 📋 Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Git** (opcional, para clonar o repositório)

## 🚀 Início Rápido

### 1. Configurar Variáveis de Ambiente

```bash
# Backend
cd backend
copy .env.docker .env
```

**IMPORTANTE**: Edite o arquivo `.env` e configure:
- `SECRET_KEY` - Gere uma chave segura (veja abaixo)
- `JUDIT_API_KEY` - Sua API key da Judit
- `ESCAVADOR_API_TOKEN` - Seu token do Escavador

#### Gerar SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Iniciar Todos os Serviços

Na raiz do projeto (onde está o `docker-compose.yml`):

```bash
docker-compose up -d
```

Isso irá iniciar:
- ✅ Backend (FastAPI) - `http://localhost:8000`
- ✅ Frontend (React) - `http://localhost:3000`
- ✅ PostgreSQL - `localhost:5432`
- ✅ Redis - `localhost:6379`
- ✅ pgAdmin - `http://localhost:5050`

### 3. Verificar Status

```bash
docker-compose ps
```

### 4. Acessar a Aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050
  - Email: `admin@processoscanpro.com`
  - Senha: `admin`

## 📦 Serviços

### Backend (FastAPI)
- **Container**: `processoscanpro-backend`
- **Porta**: 8000
- **Tecnologia**: Python 3.11, FastAPI, SQLAlchemy
- **Banco**: PostgreSQL

### Frontend (React)
- **Container**: `processoscanpro-frontend`
- **Porta**: 3000
- **Tecnologia**: Node 18, React, Vite, TailwindCSS

### PostgreSQL
- **Container**: `processoscanpro-db`
- **Porta**: 5432
- **Usuário**: `postgres`
- **Senha**: `postgres`
- **Database**: `processoscanpro`

### Redis
- **Container**: `processoscanpro-redis`
- **Porta**: 6379
- **Uso**: Cache e fila de tarefas

### pgAdmin (Opcional)
- **Container**: `processoscanpro-pgadmin`
- **Porta**: 5050
- **Interface web** para gerenciar PostgreSQL

## 🛠️ Comandos Úteis

### Iniciar serviços
```bash
docker-compose up -d
```

### Parar serviços
```bash
docker-compose down
```

### Ver logs
```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas frontend
docker-compose logs -f frontend
```

### Reiniciar um serviço
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Reconstruir imagens
```bash
docker-compose build
docker-compose up -d
```

### Limpar tudo (CUIDADO: apaga dados)
```bash
docker-compose down -v
```

### Acessar shell de um container
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Database
docker-compose exec db psql -U postgres -d processoscanpro
```

## 🔄 Desenvolvimento

### Hot Reload

Ambos backend e frontend estão configurados com hot reload:
- **Backend**: Mudanças em `.py` recarregam automaticamente
- **Frontend**: Mudanças em `.jsx` recarregam automaticamente

### Volumes

Os diretórios estão montados como volumes:
- `./backend` → `/app` (backend)
- `./frontend` → `/app` (frontend)

Isso significa que você pode editar os arquivos localmente e as mudanças serão refletidas nos containers.

## 🗄️ Banco de Dados

### Conectar ao PostgreSQL

**Via pgAdmin:**
1. Acesse http://localhost:5050
2. Login: `admin@processoscanpro.com` / `admin`
3. Add New Server:
   - Name: `ProcessoScanPro`
   - Host: `db`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`

**Via linha de comando:**
```bash
docker-compose exec db psql -U postgres -d processoscanpro
```

### Migrations (quando implementadas)

```bash
docker-compose exec backend alembic upgrade head
```

## 🐛 Troubleshooting

### Porta já em uso
Se alguma porta já estiver em uso, edite o `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Mude 8000 para 8001
```

### Erro de permissão (Linux/Mac)
```bash
sudo chown -R $USER:$USER .
```

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs backend

# Reconstruir
docker-compose build --no-cache backend
docker-compose up -d
```

### Limpar cache do Docker
```bash
docker system prune -a
docker volume prune
```

### Backend não conecta ao banco
Verifique se o `DATABASE_URL` no `.env` está correto:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/processoscanpro
```

## 📊 Monitoramento

### Ver uso de recursos
```bash
docker stats
```

### Ver processos
```bash
docker-compose top
```

## 🔐 Segurança

### Produção

Para produção, altere:

1. **Senhas do banco**:
```yaml
environment:
  - POSTGRES_PASSWORD=senha-forte-aqui
```

2. **SECRET_KEY**: Use uma chave forte

3. **DEBUG**: Mude para `False`

4. **CORS**: Restrinja origens permitidas

## 📝 Estrutura de Rede

```
processoscanpro-network (bridge)
├── backend (processoscanpro-backend)
├── frontend (processoscanpro-frontend)
├── db (processoscanpro-db)
├── redis (processoscanpro-redis)
└── pgadmin (processoscanpro-pgadmin)
```

Todos os containers estão na mesma rede e podem se comunicar usando os nomes dos serviços.

## 🚢 Deploy

Para deploy em produção, considere:
- Usar Docker Swarm ou Kubernetes
- Configurar HTTPS com Nginx
- Usar secrets do Docker
- Configurar backups automáticos do banco
- Implementar monitoring (Prometheus, Grafana)

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs -f`
2. Verifique se todos os serviços estão rodando: `docker-compose ps`
3. Tente reconstruir: `docker-compose build --no-cache`
