# 🎯 Integração com Judit.io - Webhook

## 📋 Visão Geral

Sistema completo de integração com API Judit.io usando **webhook** para consultas em tempo real.

## 🔧 Configuração

### 1. Variáveis de Ambiente (.env)

```env
# API Judit.io
JUDIT_API_KEY=sua-chave-api-aqui
JUDIT_WEBHOOK_URL=https://seu-dominio.com/api/judit/webhook

# MongoDB (rastreamento de requisições)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=processo_scan
```

### 2. Instalar Dependências

```bash
cd backend
pip install motor httpx
```

### 3. MongoDB (Docker ou Local)

```bash
# Via Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Ou instalar localmente
# https://www.mongodb.com/try/download/community
```

## 🚀 Como Funciona

### 1. Fluxo com Webhook (on-demand = true)

```
Frontend → Backend → Judit API (com callback_url)
                        ↓
            Backend recebe webhook ← Judit API
                        ↓
            MongoDB (salva resultado)
                        ↓
            Frontend polling (verifica status)
```

**Vantagens:**
- ✅ Dados em tempo real dos tribunais
- ✅ Mais atualizado
- ⚠️ Mais demorado (minutos)

### 2. Fluxo sem Webhook (on-demand = false)

```
Frontend → Backend → Judit API (resposta síncrona)
                        ↓
            MongoDB (salva resultado)
                        ↓
            Frontend polling (verifica status)
```

**Vantagens:**
- ✅ Resposta rápida (segundos)
- ✅ Consulta no banco Judit
- ⚠️ Até 30 dias de defasagem

## 📡 Endpoints Criados

### Backend (FastAPI)

1. **POST /api/judit/processar**
   - Inicia processamento em lote
   - Payload: `{ dados: [], on_demand: bool, with_attachments: bool }`
   - Retorna: `{ success: true, batch_id: "uuid" }`

2. **GET /api/judit/status/{batch_id}**
   - Consulta status do processamento
   - Retorna contadores: total, processados, sucesso, erro

3. **POST /api/judit/webhook**
   - Recebe callbacks da Judit.io
   - Processa automaticamente as respostas

4. **GET /api/judit/resultados/{batch_id}**
   - Obtém resultados finais do lote

### Frontend (React)

Serviço: `juditService.js`
```javascript
// Processar dados
await juditService.processar(dados, onDemand, withAttachments)

// Verificar status
await juditService.obterStatus(batchId)

// Obter resultados
await juditService.obterResultados(batchId)
```

## 🗄️ Estrutura MongoDB

### Collection: `judit_batches`

```json
{
  "batch_id": "uuid",
  "total": 10,
  "processados": 5,
  "sucesso": 4,
  "erro": 1,
  "on_demand": true,
  "status": "processando",
  "created_at": "2025-10-03T12:00:00Z",
  "requisicoes": [
    {
      "request_id": "uuid-interno",
      "judit_request_id": "uuid-judit",
      "documento": "12345678900",
      "doc_type": "cpf",
      "nome": "João Silva",
      "empresa": "Empresa XYZ",
      "status": "aguardando",
      "created_at": "2025-10-03T12:00:00Z"
    }
  ],
  "resultados": [
    {
      "documento": "12345678900",
      "doc_type": "cpf",
      "nome": "João Silva",
      "status": "sucesso",
      "qtd_processos": 3,
      "processos": [ /* dados dos processos */ ],
      "processado_at": "2025-10-03T12:05:00Z"
    }
  ]
}
```

## 🔐 Webhook Público

Para receber webhooks da Judit.io em **desenvolvimento local**:

### Opção 1: ngrok (Recomendado)

```bash
# Instalar ngrok: https://ngrok.com/
ngrok http 8000

# Copie a URL gerada (ex: https://abc123.ngrok.io)
# Adicione no .env:
JUDIT_WEBHOOK_URL=https://abc123.ngrok.io/api/judit/webhook
```

### Opção 2: Produção

```bash
# Em produção, use seu domínio real:
JUDIT_WEBHOOK_URL=https://api.seusistema.com/api/judit/webhook
```

## 📊 Testando a Integração

### 1. Via Interface (Processar Judit)

1. Carregue dados do Pipedrive ou Excel
2. Clique em "Processar"
3. Escolha **"Busca em Tempo Real"** ou **"Banco de Dados"**
4. Aguarde processamento
5. Veja logs em tempo real
6. Resultados aparecem automaticamente

### 2. Via API (Postman/cURL)

```bash
# Iniciar processamento
curl -X POST http://localhost:8000/api/judit/processar \
  -H "Content-Type: application/json" \
  -d '{
    "dados": [
      {"CPF": "12345678900", "Título": "João Silva"}
    ],
    "on_demand": true,
    "with_attachments": true
  }'

# Verificar status
curl http://localhost:8000/api/judit/status/{batch_id}

# Ver resultados
curl http://localhost:8000/api/judit/resultados/{batch_id}
```

## 🎨 Interface do Usuário

### Modal de Seleção

Ao clicar em "Processar", o usuário escolhe:

1. **🔵 Busca em Tempo Real**
   - Consulta direto nos tribunais
   - Mais demorado
   - Dados atualizados

2. **🟢 Banco de Dados**
   - Consulta banco Judit
   - Mais rápido
   - Até 30 dias defasagem

### Sistema de Logs

```
[12:00:00] Iniciando busca em TEMPO REAL (on-demand)...
[12:00:01] ⚠️ Esse processo pode demorar alguns minutos
[12:00:02] ✓ Batch iniciado: abc-123-def
[12:00:03] Aguardando respostas via webhook...
[12:00:05] Status: 2/10 processados (2 sucesso, 0 erros)
[12:00:08] Status: 5/10 processados (4 sucesso, 1 erros)
[12:00:15] ✓ Processamento concluído! Total: 9 sucessos, 1 erros
[12:00:16] Resultados carregados: 9 registros
```

## 🔍 Monitoramento

### Logs Backend

```python
print("[JUDIT] Requisição enviada: 12345678900 - ID: abc-123")
print("[WEBHOOK] Recebido: reference_id=abc-123, event_type=response_created")
print("[WEBHOOK] Resultado salvo: 12345678900 - 3 processos")
```

### Collection MongoDB

```javascript
// Verificar batches no MongoDB
db.judit_batches.find().pretty()

// Ver apenas em processamento
db.judit_batches.find({ status: "processando" })

// Contar sucessos/erros
db.judit_batches.aggregate([
  { $project: { sucesso: 1, erro: 1 } }
])
```

## ⚡ Performance

- **Banco de Dados**: ~2-5 segundos por CPF/CNPJ
- **Tempo Real**: ~30-120 segundos por CPF/CNPJ
- **Webhook**: Resposta assíncrona (pode levar minutos)
- **Polling**: Verifica status a cada 3 segundos

## 🐛 Troubleshooting

### Webhook não está sendo recebido

1. Verificar URL pública acessível
2. Testar webhook manualmente
3. Verificar logs do backend
4. Confirmar JUDIT_WEBHOOK_URL está correto

### MongoDB não conecta

1. Verificar se MongoDB está rodando: `docker ps`
2. Testar conexão: `mongo --eval "db.version()"`
3. Verificar MONGODB_URI no .env

### Polling não atualiza

1. Abrir console do navegador (F12)
2. Verificar erros de rede
3. Confirmar batch_id está correto
4. Ver logs do backend

## 🎯 Próximos Passos

- [ ] Adicionar retry automático para requisições falhadas
- [ ] Sistema de notificação quando processamento concluir
- [ ] Exportar resultados em Excel/PDF
- [ ] Dashboard com estatísticas de processamento
- [ ] Histórico de processamentos anteriores

## 📝 Estrutura de Resposta Judit.io

Ver documentação completa: https://docs.judit.io/webhook/callbacks

**response_type:**
- `lawsuit`: Processo encontrado
- `application_info`: Requisição completada (code: 600)
- `application_error`: Erro (ex: LAWSUIT_NOT_FOUND)

**cached_response:**
- `false`: Veio direto do tribunal (tempo real)
- `true`: Veio do banco Judit
