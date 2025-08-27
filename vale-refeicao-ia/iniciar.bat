@echo off
echo ====================================
echo   Iniciando Vale Refeicao IA
echo ====================================
echo.

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica se o .env existe
if not exist .env (
    echo.
    echo ATENCAO: Arquivo .env nao encontrado!
    echo Copie config_sqlite.txt para .env e adicione sua chave OpenAI
    echo.
    pause
    exit
)

REM Inicia o Streamlit
echo.
echo Iniciando aplicacao...
echo.
echo A aplicacao abrira em: http://localhost:8501
echo.
echo Pressione Ctrl+C para parar
echo.
streamlit run app.py
