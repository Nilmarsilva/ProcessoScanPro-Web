# 🚀 Deploy na VPS - Guia Completo

## 📋 Pré-requisitos

- VPS com Ubuntu 20.04+ ou Debian 11+
- Domínio configurado (ex: `processoscan.com.br`)
- Acesso SSH root ou sudo

---

## 🔧 1. Preparar Servidor

```bash
# Conectar via SSH
ssh root@seu-servidor.com

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

---

## 📦 2. Transferir Projeto

### Opção A: Via Git (Recomendado)
```bash
# No servidor
cd /var/www
git clone https://github.com/seu-usuario/ProcessoScanPro.git
cd ProcessoScanPro/ProcessoScanPro-Web
```

### Opção B: Via SCP
```powershell
# No seu PC (PowerShell)
scp -r "d:\SOFTWARES\Processo-Scan-Pro\Backup-ProcessoScanPro\17032025\ProcessoScanPro\ProcessoScanPro-Web" root@seu-servidor:/var/www/
```

---

## 🔐 3. Configurar Variáveis de Ambiente

```bash
# No servidor
cd /var/www/ProcessoScanPro-Web/backend
cp .env.example .env
nano .env
```

**Edite o .env:**
```env
# Servidor
APP_NAME=ProcessoScanPro
DEBUG=False
HOST=0.0.0.0
PORT=8000

# JWT
SECRET_KEY=GERE_UMA_CHAVE_SEGURA_AQUI_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Banco de Dados PostgreSQL
DATABASE_URL=postgresql://postgres:SENHA_FORTE_AQUI@db:5432/processoscanpro

# APIs
JUDIT_API_KEY=42779980-114e-43f1-abfd-05de937ea6f4
JUDIT_WEBHOOK_URL=https://seu-dominio.com.br/api/judit/webhook
ESCAVADOR_API_TOKEN=seu-token-aqui

# CORS
CORS_ORIGINS=["https://seu-dominio.com.br"]
```

---

## 🐳 4. Configurar Docker Compose para Produção

Criar `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: processoscanpro-backend
    restart: always
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/processoscanpro
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ./backend/.env
    depends_on:
      - db
      - redis
    networks:
      - app-network

  frontend:
    build: ./frontend
    container_name: processoscanpro-frontend
    restart: always
    environment:
      - VITE_API_URL=https://seu-dominio.com.br
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    container_name: processoscanpro-db
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=processoscanpro
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    container_name: processoscanpro-redis
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: processoscanpro-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

---

## 🌐 5. Configurar Nginx

```bash
mkdir -p nginx
nano nginx/nginx.conf
```

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name seu-dominio.com.br;

        # Redirecionar HTTP para HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name seu-dominio.com.br;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 🔒 6. Configurar SSL (Certbot/Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com.br

# Copiar certificados para nginx
sudo cp /etc/letsencrypt/live/seu-dominio.com.br/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/seu-dominio.com.br/privkey.pem ./nginx/ssl/
```

---

## 🚀 7. Subir Aplicação

```bash
# Criar tabelas no banco
docker-compose -f docker-compose.prod.yml up -d db
sleep 10
docker-compose -f docker-compose.prod.yml run backend python create_tables_docker.py

# Subir tudo
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## ✅ 8. Testar

```bash
# Testar backend
curl https://seu-dominio.com.br/api/health

# Acessar no navegador
https://seu-dominio.com.br
```

---

## 🔧 Comandos Úteis

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Reiniciar serviço
docker-compose -f docker-compose.prod.yml restart backend

# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Backup banco
docker exec processoscanpro-db pg_dump -U postgres processoscanpro > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i processoscanpro-db psql -U postgres processoscanpro
```

---

## 🎯 **Quer que eu crie os arquivos de deploy agora?**

1. `docker-compose.prod.yml`
2. `nginx/nginx.conf`
3. Script de deploy automatizado
4. Script de backup

**Qual o domínio que vai usar?**
