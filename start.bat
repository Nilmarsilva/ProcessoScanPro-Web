@echo off
echo ========================================
echo ProcessoScanPro - Docker Setup
echo ========================================
echo.

REM Verifica se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker Desktop nao esta rodando!
    echo Por favor, inicie o Docker Desktop e tente novamente.
    pause
    exit /b 1
)

echo [OK] Docker Desktop esta rodando
echo.

REM Verifica se .env existe
if not exist "backend\.env" (
    echo [AVISO] Arquivo .env nao encontrado!
    echo Copiando .env.docker para .env...
    copy "backend\.env.docker" "backend\.env"
    echo.
    echo [IMPORTANTE] Configure o arquivo backend\.env antes de continuar!
    echo - Gere uma SECRET_KEY segura
    echo - Configure JUDIT_API_KEY
    echo - Configure ESCAVADOR_API_TOKEN
    echo.
    pause
)

echo Iniciando servicos Docker...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar os servicos!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Servicos iniciados com sucesso!
echo ========================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo pgAdmin:   http://localhost:5050
echo.
echo Para ver os logs: docker-compose logs -f
echo Para parar:       docker-compose down
echo.
pause
