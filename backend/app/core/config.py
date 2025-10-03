"""
Configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # App
    APP_NAME: str = "ProcessoScanPro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Banco de Dados
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # APIs Externas
    JUDIT_API_KEY: str = ""
    ESCAVADOR_API_TOKEN: str = ""
    
    # Pipedrive
    PIPEDRIVE_API_KEY: str = ""
    PIPEDRIVE_DOMAIN: str = ""
    
    # Assertiva
    ASSERTIVA_CLIENT_ID: str = ""
    ASSERTIVA_CLIENT_SECRET: str = ""
    ASSERTIVA_BASE_URL: str = "https://api.assertivasolucoes.com.br"
    ASSERTIVA_AUTH_URL: str = "https://api.assertivasolucoes.com.br/oauth2/v3/token"
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Converte string JSON para lista"""
        import json
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    
    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite variáveis extras no .env


settings = Settings()
