# 🚀 Setup Rápido - Integração Judit.io

## 📦 Instalação

### 1. Backend - Instalar Dependências

```bash
cd backend
pip install motor httpx
```

### 2. MongoDB - Iniciar

```bash
# Opção A: Docker (Recomendado)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Opção B: Docker Compose (adicione ao docker-compose.yml)
# mongodb:
#   image: mongo:latest
#   ports:
#     - "27017:27017"
#   volumes:
#     - mongodb_data:/data/db
```

### 3. Configurar .env

```bash
# Copie e edite o .env
cp backend/.env.example backend/.env
```

Edite as variáveis:
```env
JUDIT_API_KEY=sua-chave-api-judit
JUDIT_WEBHOOK_URL=http://localhost:8000/api/judit/webhook  # Para dev local
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=processo_scan
```

### 4. Webhook Público (Desenvolvimento)

Para receber webhooks em desenvolvimento local, use **ngrok**:

```bash
# Instalar: https://ngrok.com/download
ngrok http 8000

# Copie a URL gerada e atualize no .env:
# JUDIT_WEBHOOK_URL=https://abc123.ngrok.io/api/judit/webhook
```

## 🎯 Como Usar

### 1. Pipedrive → Processar Judit

1. **Carregar Dados:**
   - Vá em "Pipedrive"
   - Carregue negócios com CPF/CNPJ
   - Clique em "Enviar para Processar"

2. **Processar:**
   - Será redirecionado para "Processar Judit"
   - Dados carregados automaticamente
   - Clique em "Processar"

3. **Escolher Tipo:**
   - **🔵 Busca em Tempo Real**: Consulta tribunais (mais demorado, atualizado)
   - **🟢 Banco de Dados**: Consulta base Judit (rápido, até 30 dias defasagem)

4. **Monitorar:**
   - Veja logs em tempo real
   - Status atualiza automaticamente (polling 3s)
   - Resultados aparecem quando concluído

### 2. Upload Excel → Processar

1. Faça upload de planilha Excel
2. Sistema detecta colunas automaticamente
3. Confirme mapeamento (Título, Pessoa, CPF, CNPJ)
4. Clique em "Processar"
5. Escolha tipo de busca

## 🧪 Testar Integração

### Teste 1: Backend Funcionando

```bash
curl http://localhost:8000/health
# Resposta: {"status": "healthy"}
```

### Teste 2: MongoDB Conectado

```bash
# Conectar ao MongoDB
docker exec -it mongodb mongosh

# No shell MongoDB:
use processo_scan
db.judit_batches.find().pretty()
```

### Teste 3: Processar Teste

```bash
curl -X POST http://localhost:8000/api/judit/processar \
  -H "Content-Type: application/json" \
  -d '{
    "dados": [
      {
        "CPF": "12345678900",
        "Título": "Teste Silva",
        "Organização": "Empresa Teste"
      }
    ],
    "on_demand": false,
    "with_attachments": true
  }'

# Resposta esperada:
# {
#   "success": true,
#   "batch_id": "abc-123-def",
#   "message": "Processamento iniciado com 1 registros",
#   "on_demand": false
# }
```

### Teste 4: Verificar Status

```bash
# Substitua {batch_id} pelo retornado no teste anterior
curl http://localhost:8000/api/judit/status/{batch_id}
```

## 📊 Estrutura Criada

### Backend

```
backend/
├── app/
│   ├── routers/
│   │   └── judit.py              # Endpoints da API
│   ├── services/
│   │   └── judit_service.py      # Lógica de processamento
│   └── database/
│       └── mongo_client.py       # Cliente MongoDB
├── requirements.txt              # Dependências atualizadas
└── .env.example                  # Variáveis de ambiente
```

### Frontend

```
frontend/
└── src/
    ├── services/
    │   └── juditService.js       # Cliente API
    └── pages/
        └── ProcessarJuditPage.jsx # Interface atualizada
```

## 🔧 Endpoints Criados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/judit/processar` | Inicia processamento |
| GET | `/api/judit/status/{batch_id}` | Consulta status |
| POST | `/api/judit/webhook` | Recebe callbacks Judit |
| GET | `/api/judit/resultados/{batch_id}` | Obtém resultados |

## 🎨 Fluxo Completo

```
┌─────────────┐
│  Pipedrive  │
│  (Carregar) │
└──────┬──────┘
       │ Enviar para Processar
       ↓
┌─────────────────────┐
│  Processar Judit    │
│  (Dados carregados) │
└──────┬──────────────┘
       │ Clicar "Processar"
       ↓
┌─────────────────────┐
│  Modal de Seleção   │
│  ┌───────────────┐  │
│  │ Tempo Real    │  │
│  │ (on-demand)   │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Banco Dados   │  │
│  │ (rápido)      │  │
│  └───────────────┘  │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  Backend (FastAPI)  │
│  - Cria batch       │
│  - Envia para Judit │
│  - Salva MongoDB    │
└──────┬──────────────┘
       │
       ├─→ on-demand=true ──→ Judit API ──→ Webhook ─┐
       │                                               │
       └─→ on-demand=false ─→ Judit API ──→ Resposta │
                                                       │
                                                       ↓
                                            ┌──────────────────┐
                                            │  MongoDB         │
                                            │  (judit_batches) │
                                            └────────┬─────────┘
                                                     │
                                                     ↓
                                            ┌──────────────────┐
                                            │  Frontend        │
                                            │  (Polling 3s)    │
                                            │  Atualiza Status │
                                            └──────────────────┘
```

## ⚡ Comandos Úteis

```bash
# Reiniciar backend
docker-compose restart backend

# Reiniciar frontend
docker-compose restart frontend

# Ver logs backend
docker-compose logs -f backend

# Ver logs MongoDB
docker-compose logs -f mongodb

# Limpar dados MongoDB
docker exec -it mongodb mongosh
> use processo_scan
> db.judit_batches.deleteMany({})

# Parar tudo
docker-compose down

# Iniciar tudo
docker-compose up -d
```

## 🐛 Resolução de Problemas

### Erro: "JUDIT_API_KEY not found"
- Configure a variável no `.env`
- Reinicie o backend

### Erro: "MongoDB connection failed"
- Verifique se MongoDB está rodando: `docker ps`
- Teste conexão: `docker exec -it mongodb mongosh`

### Webhook não recebe resposta
- Em desenvolvimento, use **ngrok**
- Verifique `JUDIT_WEBHOOK_URL` está correto e público
- Teste manualmente: `curl http://localhost:8000/api/judit/webhook`

### Frontend não atualiza
- Abra DevTools (F12) → Network
- Verifique se polling está funcionando
- Veja erros no console

## ✅ Checklist

- [ ] MongoDB rodando
- [ ] Backend rodando
- [ ] Frontend rodando
- [ ] .env configurado com `JUDIT_API_KEY`
- [ ] .env configurado com `MONGODB_URI`
- [ ] Para dev: ngrok rodando (webhook público)
- [ ] Testar: Carregar dados do Pipedrive
- [ ] Testar: Clicar "Enviar para Processar"
- [ ] Testar: Escolher tipo de busca
- [ ] Testar: Ver logs em tempo real
- [ ] Testar: Ver resultados quando concluído

## 📚 Documentação

- [Judit.io API](https://docs.judit.io/)
- [Webhook Callbacks](https://docs.judit.io/webhook/callbacks)
- [JUDIT_INTEGRATION.md](./JUDIT_INTEGRATION.md) - Documentação completa

---

**Pronto para usar! 🎉**
