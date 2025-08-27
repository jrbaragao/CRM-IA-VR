@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo   Sistema de Vale Refeicao IA - Instalacao
echo ====================================================
echo.

REM Verifica Python
echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! Por favor, instale Python 3.11+
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

REM Cria ambiente virtual
echo.
echo [2/7] Criando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe, pulando...
) else (
    python -m venv venv
    echo Ambiente virtual criado!
)

REM Ativa ambiente virtual
echo.
echo [3/7] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualiza pip
echo.
echo [4/7] Atualizando pip...
python -m pip install --upgrade pip

REM Instala dependencias
echo.
echo [5/7] Instalando dependencias...
pip install -r requirements.txt

REM Cria arquivo .env se nao existir
echo.
echo [6/7] Configurando ambiente...
if not exist .env (
    echo Criando arquivo .env...
    (
        echo # Banco de Dados
        echo DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao
        echo.
        echo # OpenAI - IMPORTANTE: Adicione sua chave aqui!
        echo OPENAI_API_KEY=sk-...
        echo.
        echo # ChromaDB
        echo CHROMA_HOST=localhost
        echo CHROMA_PORT=8000
        echo.
        echo # Configuracoes de Vale Refeicao
        echo VALOR_DIA_UTIL=35.00
        echo DESCONTO_FUNCIONARIO_PCT=0.20
        echo DIAS_UTEIS_MES=22
        echo.
        echo # Ambiente
        echo ENVIRONMENT=development
        echo DEBUG=True
    ) > .env
    echo.
    echo IMPORTANTE: Edite o arquivo .env e adicione sua chave OpenAI!
    notepad .env
) else (
    echo Arquivo .env ja existe!
)

REM Verifica Docker
echo.
echo [7/7] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Docker nao encontrado!
    echo Para usar PostgreSQL via Docker, instale em: https://www.docker.com/
    echo Voce pode instalar PostgreSQL manualmente se preferir.
) else (
    docker --version
    echo.
    choice /C YN /M "Deseja iniciar PostgreSQL e ChromaDB via Docker"
    if !errorlevel! equ 1 (
        echo Iniciando servicos Docker...
        docker-compose up -d
        timeout /t 5 >nul
        docker ps
    )
)

echo.
echo ====================================================
echo   Instalacao Concluida!
echo ====================================================
echo.
echo Proximos passos:
echo 1. Edite o arquivo .env com sua chave OpenAI
echo 2. Configure o PostgreSQL (se nao usou Docker)
echo 3. Execute: streamlit run app.py
echo.
echo Para iniciar a aplicacao agora, digite: streamlit run app.py
echo.
pause
