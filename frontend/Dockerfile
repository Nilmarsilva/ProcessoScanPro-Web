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

# Copia config nginx para SPA (rotas React)
RUN echo 'server { \n\
    listen 80; \n\
    location / { \n\
        root /usr/share/nginx/html; \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
