# 🚀 Build e Deploy - Swarm Mode

## ⚠️ Problema Identificado

Seu Portainer está em **modo Swarm**, que NÃO suporta `build` no docker-compose.

## ✅ Solução: Build Local + Push para Registry

### **Opção 1: Usar Docker Hub (Recomendado)**

#### 1. Login no Docker Hub
```bash
docker login
# Username: nilmarsilva
# Password: seu-token-docker-hub
```

#### 2. Build e Push das Imagens
```bash
# Na VPS (via SSH)
cd /caminho/do/projeto

# Build Backend
docker build -t nilmarsilva/processoscanpro-backend:latest ./backend
docker push nilmarsilva/processoscanpro-backend:latest

# Build Frontend
docker build -t nilmarsilva/processoscanpro-frontend:latest \
  --build-arg VITE_API_URL=https://processoscanpro.atendimentorapido.app.br \
  ./frontend
docker push nilmarsilva/processoscanpro-frontend:latest
```

#### 3. Deploy no Portainer
Use `docker-compose.portainer.yml` (já configurado com as imagens)

---

### **Opção 2: Registry Local (Mais Rápido)**

#### 1. Criar Registry Local
```bash
docker service create --name registry --publish 5000:5000 registry:2
```

#### 2. Build e Push Local
```bash
cd /caminho/do/projeto

# Build e Push Backend
docker build -t localhost:5000/processoscanpro-backend:latest ./backend
docker push localhost:5000/processoscanpro-backend:latest

# Build e Push Frontend  
docker build -t localhost:5000/processoscanpro-frontend:latest \
  --build-arg VITE_API_URL=https://processoscanpro.atendimentorapido.app.br \
  ./frontend
docker push localhost:5000/processoscanpro-frontend:latest
```

#### 3. Usar compose com registry local
Crie `docker-compose.registry.yml`

---

### **Opção 3: Deploy Direto via CLI (Mais Simples)**

```bash
# SSH na VPS
ssh root@processoscanpro.atendimentorapido.app.br

# Clone o repo
cd /opt
git clone https://github.com/Nilmarsilva/ProcessoScanPro-Web.git
cd ProcessoScanPro-Web

# Build localmente (não via Swarm)
docker-compose -f docker-compose.standalone.yml build

# Converte para Swarm e deploy
docker stack deploy -c docker-compose.standalone.yml processoscanpro
```

⚠️ Mas o Swarm vai ignorar o `build`, então precisa buildar antes!

---

## 🎯 **Recomendação: Desabilitar Swarm**

Se você não está usando os recursos do Swarm (alta disponibilidade, múltiplos nodes), **desabilite**:

```bash
# Remover todas as stacks
docker stack rm processoscanpro
docker stack rm portainer
# ... remova todas

# Desabilitar Swarm
docker swarm leave --force

# Agora use docker-compose normal
docker-compose -f docker-compose.standalone.yml up -d
```

**No Portainer:**
- Após desabilitar Swarm, ele vai funcionar em modo **standalone**
- Aí você pode usar `build` normalmente!

---

## 📝 Qual você prefere?

1. **Build e push para Docker Hub** (funciona com Swarm)
2. **Registry local** (mais rápido, funciona com Swarm)  
3. **Desabilitar Swarm** (mais simples, mas perde features Swarm)

Me diga qual você prefere e eu ajusto os arquivos!
