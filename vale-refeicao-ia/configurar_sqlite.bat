@echo off
echo ========================================
echo  CONFIGURACAO SQLITE - VALE REFEICAO
echo ========================================
echo.

REM Verificar se .env ja existe
if exist ".env" (
    echo ⚠️  Arquivo .env ja existe!
    echo.
    choice /C SN /M "Sobrescrever arquivo .env existente? (S/N)"
    if errorlevel 2 goto :fim
)

REM Criar arquivo .env
echo 📝 Criando arquivo .env...
(
echo # ===================================
echo # CONFIGURACOES DO VALE REFEICAO IA - MODO SQLITE
echo # ===================================
echo.
echo # Banco de Dados - Usando SQLite para testes/curso
echo DATABASE_URL=sqlite:///./vale_refeicao.db
echo.
echo # OpenAI API - OBRIGATORIO!
echo # Obtenha sua chave em: https://platform.openai.com/api-keys
echo OPENAI_API_KEY=sk-...
echo.
echo # ChromaDB ^(Vector Store^) - Modo local/memoria para testes
echo CHROMA_HOST=localhost
echo CHROMA_PORT=8000
echo CHROMA_PERSIST=False
echo CHROMA_COLLECTION=vale_refeicao_collection
echo.
echo # Configuracoes de Vale Refeicao
echo VALOR_DIA_UTIL=35.00
echo DESCONTO_FUNCIONARIO_PCT=0.20
echo DIAS_UTEIS_MES=22
echo.
echo # Ambiente
echo ENVIRONMENT=development
echo DEBUG=True
echo.
echo # Configuracoes de Upload
echo MAX_FILE_SIZE_MB=50
echo ALLOWED_EXTENSIONS=csv,xlsx,xls
echo.
echo # Logs
echo LOG_LEVEL=INFO
echo LOG_FILE=logs/app.log
) > .env

echo ✅ Arquivo .env criado com sucesso!
echo.
echo ⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua chave OpenAI!
echo    Substitua "sk-..." pela sua chave real da OpenAI
echo.
echo 📖 Para obter sua chave OpenAI:
echo    1. Acesse: https://platform.openai.com/api-keys
echo    2. Faça login ou crie uma conta
echo    3. Clique em "Create new secret key"
echo    4. Copie a chave e cole no arquivo .env
echo.

REM Abrir arquivo .env para edicao
choice /C SN /M "Abrir arquivo .env para edicao agora? (S/N)"
if errorlevel 2 goto :testar
notepad .env

:testar
echo.
echo 🧪 Testando configuracao...
python -c "
import os
from pathlib import Path

# Verificar se .env existe
if Path('.env').exists():
    print('✅ Arquivo .env encontrado')
    
    # Tentar carregar configuracoes
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        if db_url and 'sqlite' in db_url:
            print('✅ Configuracao SQLite OK')
        else:
            print('❌ DATABASE_URL nao configurado corretamente')
            
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'sk-...' and len(api_key) > 20:
            print('✅ Chave OpenAI configurada')
        else:
            print('⚠️  Configure sua chave OpenAI no arquivo .env')
            
    except ImportError:
        print('⚠️  Instale as dependencias: pip install python-dotenv')
    except Exception as e:
        print(f'❌ Erro: {e}')
else:
    print('❌ Arquivo .env nao encontrado')
"

echo.
echo 🚀 PROXIMOS PASSOS:
echo    1. Edite o arquivo .env e adicione sua chave OpenAI
echo    2. Execute: venv\Scripts\activate
echo    3. Execute: streamlit run app.py
echo    4. Acesse: http://localhost:8501
echo.

:fim
pause
