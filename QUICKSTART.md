# 🚀 Guia de Início Rápido - ProcessoScanPro Web

## ⚡ Começar em 3 Passos

### 1️⃣ Instalar Docker Desktop

Baixe e instale: https://www.docker.com/products/docker-desktop/

### 2️⃣ Configurar Variáveis de Ambiente

```bash
cd backend
copy .env.docker .env
```

Edite `backend\.env` e configure:

```env
# OBRIGATÓRIO: Gere uma chave segura
SECRET_KEY=cole-aqui-uma-chave-gerada

# OBRIGATÓRIO: Suas API Keys
JUDIT_API_KEY=sua-api-key-judit
ESCAVADOR_API_TOKEN=seu-token-escavador
```

**Gerar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3️⃣ Iniciar

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
docker-compose up -d
```

## 🎉 Pronto!

Acesse: **http://localhost:3000**

### Credenciais Iniciais

Você precisará criar uma conta na primeira vez:
1. Acesse http://localhost:3000
2. Clique em "Registre-se"
3. Preencha os dados
4. Faça login

## 📊 Serviços Disponíveis

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:3000 | Interface do usuário |
| **Backend** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Documentação Swagger |
| **pgAdmin** | http://localhost:5050 | Gerenciar banco de dados |

### pgAdmin (Opcional)

- **Email**: admin@processoscanpro.com
- **Senha**: admin

## 🛠️ Comandos Úteis

### Ver logs
```bash
docker-compose logs -f
```

### Parar
```bash
docker-compose down
# Ou: stop.bat
```

### Reiniciar
```bash
docker-compose restart
```

### Reconstruir
```bash
docker-compose build
docker-compose up -d
```

## ❓ Problemas Comuns

### Docker não está rodando
```
[ERRO] Docker Desktop nao esta rodando!
```
**Solução**: Abra o Docker Desktop e aguarde iniciar

### Porta já em uso
```
Error: port is already allocated
```
**Solução**: Edite `docker-compose.yml` e mude as portas:
```yaml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

### Erro ao conectar ao banco
**Solução**: Aguarde alguns segundos para o PostgreSQL iniciar completamente

### Mudanças no código não aparecem
**Solução**: 
```bash
docker-compose restart backend
docker-compose restart frontend
```

## 📖 Documentação Completa

- [README.md](./README.md) - Visão geral
- [DOCKER.md](./DOCKER.md) - Guia Docker completo
- [backend/README.md](./backend/README.md) - Backend
- [frontend/README.md](./frontend/README.md) - Frontend

## 🎯 Próximos Passos

1. ✅ Criar sua conta
2. ✅ Fazer login
3. ✅ Explorar o dashboard
4. 📝 Aguardar novas funcionalidades!

## 💡 Dicas

- **Hot Reload**: Edite os arquivos localmente, as mudanças aparecem automaticamente
- **Logs**: Use `docker-compose logs -f` para debug
- **Banco**: Use pgAdmin para visualizar dados
- **API**: Teste endpoints em http://localhost:8000/docs

## 🆘 Precisa de Ajuda?

1. Verifique os logs: `docker-compose logs -f`
2. Veja o status: `docker-compose ps`
3. Leia [DOCKER.md](./DOCKER.md) para troubleshooting detalhado

---

**Desenvolvido com ❤️ para ProcessoScanPro**
