FROM node:18-alpine

# Define diretório de trabalho
WORKDIR /app

# Copia package.json e package-lock.json
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia código da aplicação
COPY . .

# Expõe porta
EXPOSE 3000

# Comando para iniciar a aplicação
CMD ["npm", "run", "dev", "--", "--host"]
