# 🐳 Comandos Docker - Setup Judit.io

## 🚀 Setup Completo

### 1️⃣ Subir containers
```powershell
docker-compose up -d
```

### 2️⃣ Criar tabelas Judit no PostgreSQL
```powershell
docker exec -it processoscanpro-backend python create_tables_docker.py
```

### 3️⃣ Verificar tabelas criadas
```powershell
# Via pgAdmin (navegador)
# Acesse: http://localhost:5050
# Email: admin@processoscanpro.com
# Senha: admin

# Ou via linha de comando:
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro -c "\dt"
```

### 4️⃣ Ver dados das tabelas
```powershell
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro -c "SELECT * FROM judit_batches;"
```

---

## 🔧 Comandos Úteis

### Ver logs do backend
```powershell
docker logs -f processoscanpro-backend
```

### Reiniciar backend
```powershell
docker-compose restart backend
```

### Entrar no container backend
```powershell
docker exec -it processoscanpro-backend bash
```

### Entrar no PostgreSQL
```powershell
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro
```

### Parar tudo
```powershell
docker-compose down
```

### Rebuild (após mudanças no código)
```powershell
docker-compose up -d --build
```

---

## 📊 Acessar Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| Frontend | http://localhost:3000 | - |
| pgAdmin | http://localhost:5050 | admin@processoscanpro.com / admin |
| PostgreSQL | localhost:5432 | postgres / postgres |

---

## ✅ Checklist Setup

- [ ] `docker-compose up -d`
- [ ] `docker exec -it processoscanpro-backend python create_tables_docker.py`
- [ ] Configurar `.env` com `JUDIT_API_KEY`
- [ ] Testar: http://localhost:8000/health
- [ ] Acessar frontend: http://localhost:3000

---

## 🎯 Testar Integração Judit

1. Acesse: http://localhost:3000
2. Vá em **Pipedrive** → Carregar negócios
3. Clique em **"Enviar para Processar"**
4. Escolha tipo de busca
5. Veja logs em tempo real!

---

## 🐛 Troubleshooting

### Container não sobe
```powershell
docker-compose logs backend
docker-compose logs db
```

### Erro de conexão com banco
```powershell
# Verificar se PostgreSQL está rodando
docker ps | findstr processoscanpro-db

# Testar conexão
docker exec -it processoscanpro-db psql -U postgres -c "SELECT 1"
```

### Tabelas não foram criadas
```powershell
# Executar novamente
docker exec -it processoscanpro-backend python create_tables_docker.py

# Verificar
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro -c "\dt"
```

---

## 📝 Estrutura PostgreSQL

**Container:** `processoscanpro-db`
**Database:** `processoscanpro`
**User:** `postgres`
**Password:** `postgres`
**Port:** `5432`

**Tabelas Judit:**
- `judit_batches` - Lotes de processamento
- `judit_requests` - Requisições individuais  
- `judit_results` - Resultados com processos

---

## 🎉 Pronto!

Agora pode usar a integração Judit.io completa! 🚀
