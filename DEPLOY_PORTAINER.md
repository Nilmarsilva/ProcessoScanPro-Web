# 🚀 Deploy via Portainer - Git Repository

## 📋 Passo a Passo Completo

### 1️⃣ Criar Repositório Git (GitHub/GitLab)

```bash
# No seu PC
cd "d:\SOFTWARES\Processo-Scan-Pro\Backup-ProcessoScanPro\17032025\ProcessoScanPro\ProcessoScanPro-Web"

# Inicializar Git (se ainda não tiver)
git init

# Adicionar remote (substitua com seu repo)
git remote add origin https://github.com/hulber/ProcessoScanPro-Web.git

# Adicionar arquivos
git add .

# Commit
git commit -m "Deploy inicial ProcessoScanPro"

# Push para GitHub
git push -u origin main
```

---

### 2️⃣ Acessar Portainer

1. Acesse seu Portainer
2. Vá em **Stacks** → **Add Stack**

---

### 3️⃣ Configurar Stack no Portainer

**Nome da Stack:** `processoscanpro`

**Build method:** Selecione **Repository**

**Repository configuration:**
- **Repository URL:** `https://github.com/hulber/ProcessoScanPro-Web`
- **Repository reference:** `refs/heads/main` (ou `master`)
- **Compose path:** `docker-compose.portainer.yml`
- **Authentication:** Se repo privado, adicione credenciais

---

### 4️⃣ Variáveis de Ambiente (Environment variables)

Clique em **+ Add environment variable** e adicione:

```
POSTGRES_PASSWORD=ProcessoScan2025!Secure
REDIS_PASSWORD=DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6
JUDIT_API_KEY=42779980-114e-43f1-abfd-05de937ea6f4
DOMAIN=processoscanpro.atendimentorapido.app.br
SECRET_KEY=processoscan_2025_production_key_change_this_in_prod_12345678
```

---

### 5️⃣ Deploy

1. Clique em **Deploy the stack**
2. Aguarde o build (pode demorar alguns minutos na primeira vez)
3. Veja os logs em tempo real

---

### 6️⃣ Verificar Containers

Na tela da Stack, você verá:
- ✅ `processoscanpro_db_1` - PostgreSQL
- ✅ `processoscanpro_backend_1` - FastAPI
- ✅ `processoscanpro_frontend_1` - React
- ✅ `processoscanpro_nginx_1` - Nginx

---

### 7️⃣ Criar Tabelas no Banco

No Portainer:
1. Vá na Stack → Container **backend**
2. Clique em **Console**
3. Connect
4. Execute:
```bash
python create_tables_docker.py
```

---

### 8️⃣ Configurar Proxy/SSL

**Se usar Nginx Proxy Manager:**
1. Add Proxy Host
2. **Domain:** processoscanpro.atendimentorapido.app.br
3. **Forward Hostname/IP:** IP da VPS
4. **Forward Port:** 8080
5. **SSL:** Request new certificate
6. Save

**Se usar Traefik:**
- Já está configurado nas labels do nginx
- Traefik vai gerar SSL automaticamente

---

### 9️⃣ Testar

Acesse: **https://processoscanpro.atendimentorapido.app.br**

Deve abrir a tela de login! 🎉

---

## 🔄 Atualizar Deploy (Push novos commits)

```bash
# No seu PC - Após fazer mudanças
git add .
git commit -m "Atualização XYZ"
git push

# No Portainer
# Vá em Stacks → processoscanpro
# Clique em "Update the stack"
# Selecione "Pull latest image" se usar imagens
# Clique em "Update"
```

O Portainer vai:
1. Fazer pull do Git
2. Rebuild containers (se necessário)
3. Restart services
4. Deploy automaticamente

---

## 📊 Estrutura do Repositório

```
ProcessoScanPro-Web/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── create_tables_docker.py
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf
├── docker-compose.portainer.yml  ← Usado pelo Portainer
├── docker-compose.prod.yml       ← Para deploy manual
├── .gitignore
└── README.md
```

---

## 🔐 Segurança - Variáveis Sensíveis

**IMPORTANTE:** Nunca commite senhas!

**Crie `.env` local (não vai pro Git):**
```env
POSTGRES_PASSWORD=ProcessoScan2025!Secure
REDIS_PASSWORD=DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6
JUDIT_API_KEY=42779980-114e-43f1-abfd-05de937ea6f4
SECRET_KEY=processoscan_2025_production_key_change_this_in_prod_12345678
```

**No `docker-compose.portainer.yml`, use:**
```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  JUDIT_API_KEY: ${JUDIT_API_KEY}
```

**No Portainer, configure as variáveis** (passo 4)

---

## 🐛 Troubleshooting

### Stack não inicia
- Veja logs: Stacks → processoscanpro → Logs
- Verifique rede: `network_public` deve existir

### Erro de build
- Veja logs de build no Portainer
- Verifique Dockerfile backend/frontend

### Não acessa pelo domínio
- Verifique porta 8080 acessível
- Verifique SSL/Proxy configurado
- Teste: `curl http://IP:8080/api/health`

### Banco não conecta
- Entre no container backend console
- Teste: `psql -h db -U postgres -d processoscanpro`

---

## 📝 Vantagens Deploy via Git

✅ **Versionamento** - Todo histórico no Git  
✅ **Rollback fácil** - Voltar versão anterior  
✅ **CI/CD simples** - Push = Deploy automático  
✅ **Backup** - Código no GitHub/GitLab  
✅ **Colaboração** - Múltiplos desenvolvedores  
✅ **Portainer gerencia** - Atualiza com 1 clique  

---

## 🎯 Próximo: Configurar CI/CD (Opcional)

Com GitHub Actions, pode fazer:
- Build automático de imagens Docker
- Push para GitHub Container Registry
- Webhook para Portainer fazer pull/deploy automático

Quer que eu crie os arquivos de CI/CD também?
