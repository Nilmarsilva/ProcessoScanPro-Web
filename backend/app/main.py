"""
Aplicação principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import engine, Base
from app.api.routes import auth
from app.routers import dados, pipedrive, judit

# Cria tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dados.router)
app.include_router(pipedrive.router)
app.include_router(judit.router)


@app.get("/")
def root():
    """Rota raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}
