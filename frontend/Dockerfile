# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copia package files
COPY package*.json ./

# Instala dependências
RUN npm ci

# Copia código
COPY . .

# Argumentos de build
ARG VITE_API_URL=https://processoscanpro.atendimentorapido.app.br
ENV VITE_API_URL=$VITE_API_URL

# Build para produção
RUN npm run build

# Stage 2: Serve com Nginx
FROM nginx:alpine

# Copia build
COPY --from=builder /app/dist /usr/share/nginx/html

# Cria config nginx para SPA (rotas React)
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
