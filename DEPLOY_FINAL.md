# 🚀 Deploy FINAL - ProcessoScanPro

## ✅ Configuração Completa

### 📋 **Informações Configuradas:**
- ✅ **Domínio:** processoscanpro.atendimentorapido.app.br
- ✅ **Rede Docker:** network_public
- ✅ **PostgreSQL:** Dedicado (processoscanpro-db)
- ✅ **Redis:** Compartilhado (rede network_public)
- ✅ **Porta Nginx:** 8080 (SSL via Portainer)

---

## 🚀 Passo a Passo Deploy

### 1️⃣ Upload para VPS

```bash
# No seu PC (PowerShell)
cd "d:\SOFTWARES\Processo-Scan-Pro\Backup-ProcessoScanPro\17032025\ProcessoScanPro"

# Compactar (opcional, mais rápido)
Compress-Archive -Path ProcessoScanPro-Web -DestinationPath ProcessoScanPro-Web.zip

# Enviar para VPS
scp ProcessoScanPro-Web.zip root@processoscanpro.atendimentorapido.app.br:/var/www/

# Ou enviar pasta direto (mais demorado)
scp -r ProcessoScanPro-Web root@processoscanpro.atendimentorapido.app.br:/var/www/
```

### 2️⃣ Conectar na VPS e Descompactar

```bash
ssh root@processoscanpro.atendimentorapido.app.br

cd /var/www

# Se enviou zip
unzip ProcessoScanPro-Web.zip
cd ProcessoScanPro-Web

# Se enviou pasta direto
cd ProcessoScanPro-Web
```

### 3️⃣ Executar Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

**O script vai:**
- ✅ Parar containers antigos
- ✅ Criar PostgreSQL dedicado
- ✅ Buildar backend e frontend
- ✅ Subir todos containers
- ✅ Criar tabelas no banco

### 4️⃣ Verificar Containers

```bash
docker ps | grep processoscanpro

# Deve mostrar:
# processoscanpro-backend
# processoscanpro-frontend
# processoscanpro-nginx
# processoscanpro-db
```

### 5️⃣ Verificar Logs

```bash
# Backend
docker logs -f processoscanpro-backend

# Frontend
docker logs -f processoscanpro-frontend

# Nginx
docker logs -f processoscanpro-nginx
```

### 6️⃣ Configurar SSL no Portainer

**Opção A: Nginx Proxy Manager (Recomendado)**
1. Acesse Nginx Proxy Manager
2. Add Proxy Host:
   - **Domain:** processoscanpro.atendimentorapido.app.br
   - **Forward Hostname:** processoscanpro-nginx
   - **Forward Port:** 80
   - **SSL:** Request new certificate (Let's Encrypt)

**Opção B: Traefik**
1. Adicione labels no nginx service
2. Configure no Portainer

**Opção C: Cloudflare**
1. Configure proxy no Cloudflare
2. Aponte para IP:8080

### 7️⃣ Testar

```bash
# Teste interno (na VPS)
curl http://localhost:8080/api/health

# Deve retornar: {"status": "healthy"}

# Teste externo (no seu PC)
# Navegador: https://processoscanpro.atendimentorapido.app.br
```

---

## 📦 Estrutura de Containers

```
network_public (rede externa)
  │
  ├─ processoscanpro-db (PostgreSQL dedicado)
  ├─ processoscanpro-backend (FastAPI)
  ├─ processoscanpro-frontend (React)
  ├─ processoscanpro-nginx (Nginx)
  └─ redis (compartilhado - já existente)
```

---

## 🔧 Comandos Úteis

### Ver Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Reiniciar Serviços
```bash
# Backend apenas
docker-compose -f docker-compose.prod.yml restart backend

# Tudo
docker-compose -f docker-compose.prod.yml restart
```

### Ver Logs em Tempo Real
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Entrar no Container
```bash
# Backend
docker exec -it processoscanpro-backend bash

# Banco
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro
```

### Backup do Banco
```bash
# Criar backup
docker exec processoscanpro-db pg_dump -U postgres processoscanpro > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20250103.sql | docker exec -i processoscanpro-db psql -U postgres processoscanpro
```

### Atualizar Código
```bash
cd /var/www/ProcessoScanPro-Web

# Pull código novo (se usar git)
git pull

# Ou fazer upload de novos arquivos via scp

# Rebuild e reiniciar
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🐛 Troubleshooting

### Erro: "network_public not found"
```bash
# Verificar se a rede existe
docker network ls | grep network_public

# Se não existir, criar:
docker network create network_public
```

### Erro: "Cannot connect to Redis"
```bash
# Verificar se redis está na mesma rede
docker inspect redis | grep -A 10 Networks

# Se não estiver, adicionar:
docker network connect network_public redis
```

### Erro: "Port 8080 already in use"
```bash
# Ver o que está usando a porta
netstat -tulpn | grep 8080

# Mudar porta no docker-compose.prod.yml
# De: "8080:80"
# Para: "8081:80"
```

### Tabelas não foram criadas
```bash
# Criar manualmente
docker exec processoscanpro-backend python create_tables_docker.py

# Ou via psql
docker exec -it processoscanpro-db psql -U postgres -d processoscanpro -f /caminho/create_judit_tables.sql
```

---

## ✅ Checklist Final

- [ ] Projeto enviado para `/var/www/ProcessoScanPro-Web`
- [ ] `./deploy.sh` executado com sucesso
- [ ] 4 containers rodando: `docker ps | grep processoscanpro`
- [ ] Logs sem erros: `docker logs processoscanpro-backend`
- [ ] API respondendo: `curl http://localhost:8080/api/health`
- [ ] Tabelas criadas: `docker exec processoscanpro-db psql -U postgres -d processoscanpro -c "\dt"`
- [ ] SSL configurado (Nginx Proxy Manager ou Cloudflare)
- [ ] Frontend acessível: https://processoscanpro.atendimentorapido.app.br
- [ ] Login funcionando
- [ ] Pipedrive carregando
- [ ] **Processar Judit funcionando** (sem erro de DNS!)

---

## 🎯 Senhas e Configs

**PostgreSQL (ProcessoScanPro):**
- Container: `processoscanpro-db`
- User: `postgres`
- Password: `ProcessoScan2025!Secure`
- Database: `processoscanpro`

**Redis (Compartilhado):**
- Password: `DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6`

**Judit API:**
- Key: `42779980-114e-43f1-abfd-05de937ea6f4`

---

## 🎉 Pronto!

Após completar todos os passos, acesse:
**https://processoscanpro.atendimentorapido.app.br**

E teste a integração Judit sem problema de DNS! 🚀
