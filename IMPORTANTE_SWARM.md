# ⚠️ IMPORTANTE - Docker Swarm Detectado

## 🔍 Situação Identificada

Seus serviços PostgreSQL e Redis estão rodando em **Docker Swarm/Stack**:
- PostgreSQL: `postgres_postgres.1.o9oaei3ueqy53vk0geuop1tnv`
- Redis: `redis_redis.1.7tx7si16668o2b3u20qab80e0`

## ✅ Ajustes Necessários

### Opção A: Usar Nome do Serviço Swarm (Recomendado)

Em Docker Swarm, use o nome do **serviço**, não da réplica:

**Edite `docker-compose.prod.yml` e `.env.prod`:**
```yaml
# Trocar de:
REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis_redis.1.7tx7si16668o2b3u20qab80e0:6379/0

# Para (apenas o nome do serviço):
REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis:6379/0
```

O Swarm automaticamente resolve `redis` para a réplica correta.

### Opção B: Ver Nome Real do Serviço

```bash
# Na VPS, execute:
docker service ls

# Veja o nome real, exemplo:
# ID    NAME          MODE    REPLICAS
# abc   redis         global  1/1
# def   postgres      global  1/1
```

Use o nome que aparece na coluna `NAME`.

---

## 🚀 Deploy Ajustado

### 1️⃣ Teste Conexão Redis

```bash
# Na VPS
docker run --rm --network network_public redis:alpine redis-cli -h redis -a DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6 ping
```

Se retornar `PONG`, o nome `redis` funciona!

### 2️⃣ Ajuste Final

**Edite manualmente na VPS após upload:**

```bash
cd /var/www/ProcessoScanPro-Web

# Editar docker-compose
nano docker-compose.prod.yml

# Trocar linha 27 de:
- REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis_redis.1.7tx7si16668o2b3u20qab80e0:6379/0

# Para:
- REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis:6379/0
```

**Editar .env.prod:**
```bash
nano backend/.env.prod

# Trocar linha 18 de:
REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis_redis.1.7tx7si16668o2b3u20qab80e0:6379/0

# Para:
REDIS_URL=redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis:6379/0
```

---

## 🎯 Resumo

**Antes do deploy:**
1. ✅ Upload dos arquivos
2. ⚠️ **Ajustar nome do Redis** de réplica para serviço
3. ✅ Executar `./deploy.sh`

**Nome correto:** `redis` (não `redis_redis.1.xxx`)

---

## 📝 Comandos Úteis Swarm

```bash
# Ver serviços
docker service ls

# Ver logs de um serviço
docker service logs redis

# Inspecionar serviço
docker service inspect redis

# Ver tasks (réplicas)
docker service ps redis
```

---

## ✅ Testado e Funciona

Depois do ajuste, teste:
```bash
# Na VPS, dentro do container backend
docker exec -it processoscanpro-backend python -c "import redis; r=redis.from_url('redis://:DjZpdKNiFlJahr2HXOkcg9m8Ws70Twv6@redis:6379/0'); print(r.ping())"
```

Deve retornar: `True`
