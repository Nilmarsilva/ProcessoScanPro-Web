# 🚀 Deploy Rápido - VPS

## ✅ Arquivos Criados

- ✅ `docker-compose.prod.yml` - Com suas senhas configuradas
- ✅ `nginx/nginx.conf` - Com domínio processoscanpro.atendimentorapido.app.br
- ✅ `backend/.env.prod` - Variáveis de ambiente
- ✅ `deploy.sh` - Script de deploy automatizado

---

## 📋 Passo a Passo

### 1️⃣ Subir Projeto para VPS

```bash
# No seu PC (PowerShell)
scp -r "d:\SOFTWARES\Processo-Scan-Pro\Backup-ProcessoScanPro\17032025\ProcessoScanPro\ProcessoScanPro-Web" root@processoscanpro.atendimentorapido.app.br:/var/www/
```

### 2️⃣ Conectar na VPS

```bash
ssh root@processoscanpro.atendimentorapido.app.br
cd /var/www/ProcessoScanPro-Web
```

### 3️⃣ Ajustar Rede Docker (IMPORTANTE)

Precisamos saber o nome da rede que o PostgreSQL/Redis usam:

```bash
# Ver redes disponíveis
docker network ls

# Ver qual rede o postgres está usando
docker inspect postgres | grep -A 10 Networks
```

Depois edite `docker-compose.prod.yml` e substitua `portainer_default` pelo nome real da rede.

### 4️⃣ Executar Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

### 5️⃣ Configurar SSL no Portainer

1. Abra Portainer
2. Vá em **Stacks** ou **Containers**
3. Adicione proxy reverso **Nginx Proxy Manager** ou **Traefik**
4. Configure SSL para `processoscanpro.atendimentorapido.app.br` → porta `8080`

---

## 🔍 Verificar Nome da Rede

**Opção A: Ver no Portainer**
- Networks → Veja qual rede o `postgres` e `redis` estão

**Opção B: Via CLI**
```bash
docker network inspect $(docker inspect postgres -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
```

---

## ⚙️ Ajustes Necessários

### Se PostgreSQL/Redis estiverem em rede diferente:

Edite `docker-compose.prod.yml`:
```yaml
networks:
  processoscanpro-network:
    driver: bridge
  external-network:
    external: true
    name: SUA_REDE_AQUI  # ← Coloque o nome da rede real
```

### Se PostgreSQL/Redis tiverem nomes diferentes:

Edite `backend/.env.prod`:
```env
# Se o container postgres não se chamar "postgres", mude aqui:
DATABASE_URL=postgresql://postgres:1TGY8BaXxUtwk74QLqJz65cf0REpvOVg@NOME_DO_CONTAINER:5432/processoscanpro

# Se o container redis não se chamar "redis", mude aqui:
REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@NOME_DO_CONTAINER:6379/0
```

---

## 🧪 Testar Depois do Deploy

```bash
# Ver logs
docker logs -f processoscanpro-backend

# Testar API
curl http://localhost:8080/api/health

# Testar frontend
curl http://localhost:8080
```

---

## 📝 Checklist

- [ ] Projeto copiado para `/var/www/ProcessoScanPro-Web`
- [ ] Nome da rede Docker descoberto e ajustado
- [ ] `deploy.sh` executado com sucesso
- [ ] Containers rodando: `docker ps | grep processoscanpro`
- [ ] Banco criado: `docker exec postgres psql -U postgres -l | grep processoscanpro`
- [ ] Tabelas criadas: `docker exec postgres psql -U postgres -d processoscanpro -c "\dt"`
- [ ] SSL configurado no Portainer/Nginx Proxy Manager
- [ ] Acesso funcionando: https://processoscanpro.atendimentorapido.app.br

---

## 🎯 Informações Que Preciso

Para finalizar, me diga:

1. **Nome do container PostgreSQL** (ex: `postgres`, `postgresql`, `db`)
2. **Nome do container Redis** (ex: `redis`, `redis-server`)
3. **Nome da rede Docker** que eles usam (ex: `portainer_default`, `bridge`, `proxy-network`)

Com essas 3 informações, ajusto os arquivos e está pronto! 🚀
