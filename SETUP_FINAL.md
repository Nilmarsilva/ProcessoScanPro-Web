# ✅ Setup Final - Integração Judit.io com PostgreSQL

## 🎉 Migração Concluída!

**MongoDB removido** - Usando apenas **PostgreSQL** agora!

## 📦 Instalação Rápida

### 1. Instalar Dependência

```bash
cd backend
pip install httpx
```

### 2. Configurar .env

```bash
cp backend/.env.example backend/.env
```

Edite apenas estas variáveis:
```env
JUDIT_API_KEY=sua-chave-api-judit
JUDIT_WEBHOOK_URL=http://localhost:8000/api/judit/webhook  # Para dev
```

### 3. Criar Tabelas no Banco

```bash
cd backend
alembic revision --autogenerate -m "Add Judit tables"
alembic upgrade head
```

### 4. Webhook Público (Dev)

```bash
# Instalar ngrok: https://ngrok.com/
ngrok http 8000

# Atualizar .env com URL gerada:
# JUDIT_WEBHOOK_URL=https://abc123.ngrok.io/api/judit/webhook
```

## 🗄️ Estrutura PostgreSQL

### Tabelas Criadas

1. **judit_batches** - Lotes de processamento
   - batch_id, total, processados, sucesso, erro, status

2. **judit_requests** - Requisições individuais
   - request_id, judit_request_id, documento, status

3. **judit_results** - Resultados
   - documento, qtd_processos, processos (JSON), erro

## 🚀 Como Usar

### Fluxo Completo

```
1. Pipedrive → Carregar negócios
2. Enviar para Processar → Dados transferidos
3. Processar Judit → Escolher tipo busca
4. Ver resultados em tempo real
```

### Tipos de Busca

**🔵 Tempo Real (on-demand = true)**
- Consulta tribunais diretamente
- Webhook recebe respostas
- Mais demorado, mais atualizado

**🟢 Banco Dados (on-demand = false)**
- Consulta base Judit
- Resposta imediata
- Rápido, até 30 dias defasagem

## 📡 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/judit/processar` | Inicia processamento |
| GET | `/api/judit/status/{batch_id}` | Status em tempo real |
| POST | `/api/judit/webhook` | Recebe callbacks |
| GET | `/api/judit/resultados/{batch_id}` | Resultados finais |

## 🧪 Testar

### 1. Backend Funcionando

```bash
curl http://localhost:8000/health
```

### 2. Processar Teste

```bash
curl -X POST http://localhost:8000/api/judit/processar \
  -H "Content-Type: application/json" \
  -d '{
    "dados": [{"CPF": "12345678900", "Título": "Teste"}],
    "on_demand": false,
    "with_attachments": true
  }'
```

### 3. Ver Status

```bash
curl http://localhost:8000/api/judit/status/{batch_id}
```

## 📊 Arquivos Criados/Modificados

### Backend
- ✅ `app/models/judit.py` - Models PostgreSQL
- ✅ `app/routers/judit.py` - Endpoints API
- ✅ `app/services/judit_service.py` - Lógica processamento
- ✅ `requirements.txt` - Adicionado httpx
- ✅ `.env.example` - Variáveis atualizadas
- ❌ `app/database/mongo_client.py` - REMOVIDO

### Frontend
- ✅ `services/juditService.js` - Cliente API
- ✅ `pages/ProcessarJuditPage.jsx` - Modal + Polling

## ⚡ Comandos Úteis

```bash
# Reiniciar backend
docker-compose restart backend

# Ver logs
docker-compose logs -f backend

# Criar migration
cd backend
alembic revision --autogenerate -m "Sua mensagem"
alembic upgrade head

# Ver tabelas PostgreSQL
docker exec -it postgres_container psql -U usuario -d banco
\dt
SELECT * FROM judit_batches;
```

## 🎯 Checklist Final

- [x] Models PostgreSQL criados
- [x] Router atualizado (sem MongoDB)
- [x] Service usando SQLAlchemy
- [x] MongoDB removido
- [x] requirements.txt atualizado
- [x] .env.example limpo
- [ ] Criar migration Alembic
- [ ] Testar processamento
- [ ] Configurar webhook público (ngrok)

## 🐛 Troubleshooting

### Erro: "JUDIT_API_KEY not found"
```bash
# Configure no .env
JUDIT_API_KEY=sua-chave-aqui
# Reinicie backend
docker-compose restart backend
```

### Erro: "Table doesn't exist"
```bash
# Criar tabelas
cd backend
alembic upgrade head
```

### Webhook não recebe
```bash
# Use ngrok em dev
ngrok http 8000
# Atualize JUDIT_WEBHOOK_URL no .env
```

## 📚 Documentação

- [JUDIT_INTEGRATION.md](./JUDIT_INTEGRATION.md) - Documentação completa
- [POSTGRES_JUDIT.md](./POSTGRES_JUDIT.md) - Detalhes migração
- [Judit.io Docs](https://docs.judit.io/)

---

## ✨ Pronto para Usar!

**Apenas PostgreSQL** - Sem MongoDB, mais simples!

**Próximo passo:** Criar migration Alembic e testar! 🚀
