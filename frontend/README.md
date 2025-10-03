# ProcessoScanPro - Frontend

Frontend da aplicação ProcessoScanPro desenvolvido com React, Vite e TailwindCSS.

## 🚀 Tecnologias

- **React 18** - Biblioteca UI
- **Vite** - Build tool moderna e rápida
- **TailwindCSS** - Framework CSS utility-first
- **React Router** - Roteamento
- **Zustand** - Gerenciamento de estado
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones modernos
- **shadcn/ui** - Componentes UI

## 📋 Pré-requisitos

- Node.js 18+
- npm ou yarn

## 🔧 Instalação

1. **Instalar dependências:**
```bash
npm install
```

2. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:
```
VITE_API_URL=http://localhost:8000
```

## 🎯 Executar

### Modo Desenvolvimento
```bash
npm run dev
```

O aplicativo estará disponível em: `http://localhost:3000`

### Build para Produção
```bash
npm run build
```

### Preview da Build
```bash
npm run preview
```

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/
│   │   └── ui/              # Componentes UI (Button, Input, etc)
│   ├── pages/
│   │   ├── Login.jsx        # Página de login
│   │   ├── Register.jsx     # Página de registro
│   │   └── Dashboard.jsx    # Dashboard principal
│   ├── services/
│   │   └── api.js           # Configuração Axios e API
│   ├── store/
│   │   └── authStore.js     # Store de autenticação (Zustand)
│   ├── lib/
│   │   └── utils.js         # Utilitários
│   ├── App.jsx              # Componente principal
│   ├── main.jsx             # Entry point
│   └── index.css            # Estilos globais
├── index.html               # HTML template
├── package.json             # Dependências
├── vite.config.js           # Configuração Vite
├── tailwind.config.js       # Configuração TailwindCSS
└── postcss.config.js        # Configuração PostCSS
```

## 🎨 Componentes UI

O projeto usa componentes baseados em shadcn/ui:

- **Button** - Botões com variantes
- **Input** - Campos de entrada
- **Label** - Labels para formulários

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação:

1. **Login**: Usuário faz login e recebe `access_token` e `refresh_token`
2. **Tokens**: Armazenados no `localStorage`
3. **Interceptor**: Axios adiciona token automaticamente em todas as requisições
4. **Refresh**: Token é renovado automaticamente quando expira
5. **Logout**: Tokens são removidos e usuário é redirecionado

## 🛣️ Rotas

- `/login` - Página de login
- `/register` - Página de registro
- `/dashboard` - Dashboard (protegida)
- `/` - Redireciona para dashboard

## 🎨 Temas

O projeto suporta tema claro e escuro (configurado no TailwindCSS).

## 📦 Build

Para fazer build da aplicação:

```bash
npm run build
```

Os arquivos otimizados estarão em `dist/`.

## 🐳 Docker (Opcional)

```bash
docker build -t processoscanpro-frontend .
docker run -p 3000:3000 processoscanpro-frontend
```

## 🔄 Integração com Backend

O frontend se comunica com o backend através de:

- **Base URL**: Configurada em `.env` (`VITE_API_URL`)
- **Proxy**: Vite proxy configurado para `/api`
- **CORS**: Backend deve permitir origem do frontend

## 📝 Próximas Funcionalidades

- [ ] Upload de planilhas
- [ ] Consulta individual de processos
- [ ] Visualização de resultados
- [ ] Exportação de relatórios
- [ ] Histórico de consultas
- [ ] Notificações em tempo real (WebSocket)
