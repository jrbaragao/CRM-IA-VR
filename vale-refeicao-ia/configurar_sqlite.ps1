#!/usr/bin/env pwsh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CONFIGURAÇÃO SQLITE - VALE REFEIÇÃO" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env já existe
if (Test-Path ".env") {
    Write-Host "⚠️  Arquivo .env já existe!" -ForegroundColor Yellow
    Write-Host ""
    $resposta = Read-Host "Sobrescrever arquivo .env existente? (s/N)"
    if ($resposta -ne "s" -and $resposta -ne "S") {
        Write-Host "Operação cancelada." -ForegroundColor Yellow
        exit
    }
}

# Criar arquivo .env
Write-Host "📝 Criando arquivo .env..." -ForegroundColor Green

$envContent = @"
# ===================================
# CONFIGURAÇÕES DO VALE REFEIÇÃO IA - MODO SQLITE
# ===================================

# Banco de Dados - Usando SQLite para testes/curso
DATABASE_URL=sqlite:///./vale_refeicao.db

# OpenAI API - OBRIGATÓRIO!
# Obtenha sua chave em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# ChromaDB (Vector Store) - Modo local/memória para testes
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST=False
CHROMA_COLLECTION=vale_refeicao_collection

# Configurações de Vale Refeição
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
DIAS_UTEIS_MES=22

# Ambiente
ENVIRONMENT=development
DEBUG=True

# Configurações de Upload
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ Arquivo .env criado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua chave OpenAI!" -ForegroundColor Yellow
Write-Host "   Substitua 'sk-...' pela sua chave real da OpenAI" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 Para obter sua chave OpenAI:" -ForegroundColor Cyan
Write-Host "   1. Acesse: https://platform.openai.com/api-keys"
Write-Host "   2. Faça login ou crie uma conta"
Write-Host "   3. Clique em 'Create new secret key'"
Write-Host "   4. Copie a chave e cole no arquivo .env"
Write-Host ""

# Abrir arquivo .env para edição
$abrir = Read-Host "Abrir arquivo .env para edição agora? (S/n)"
if ($abrir -ne "n" -and $abrir -ne "N") {
    if (Get-Command "code" -ErrorAction SilentlyContinue) {
        code .env
    } elseif (Get-Command "notepad" -ErrorAction SilentlyContinue) {
        notepad .env
    } else {
        Write-Host "Abra manualmente o arquivo .env para edição" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🧪 Testando configuração..." -ForegroundColor Cyan

# Testar configuração
try {
    if (Test-Path ".env") {
        Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
        
        # Ler arquivo .env
        $envVars = Get-Content ".env" | Where-Object { $_ -match "^[^#].*=" }
        
        $dbUrl = ($envVars | Where-Object { $_ -match "^DATABASE_URL=" }) -replace "DATABASE_URL=", ""
        if ($dbUrl -and $dbUrl -match "sqlite") {
            Write-Host "✅ Configuração SQLite OK" -ForegroundColor Green
        } else {
            Write-Host "❌ DATABASE_URL não configurado corretamente" -ForegroundColor Red
        }
        
        $apiKey = ($envVars | Where-Object { $_ -match "^OPENAI_API_KEY=" }) -replace "OPENAI_API_KEY=", ""
        if ($apiKey -and $apiKey -ne "sk-..." -and $apiKey.Length -gt 20) {
            Write-Host "✅ Chave OpenAI configurada" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Configure sua chave OpenAI no arquivo .env" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Arquivo .env não encontrado" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erro ao testar configuração: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "   1. Edite o arquivo .env e adicione sua chave OpenAI"
Write-Host "   2. Execute: .\venv\Scripts\Activate.ps1"
Write-Host "   3. Execute: streamlit run app.py"
Write-Host "   4. Acesse: http://localhost:8501"
Write-Host ""

# Perguntar se quer executar agora
$executar = Read-Host "Executar aplicação agora? (s/N)"
if ($executar -eq "s" -or $executar -eq "S") {
    Write-Host "🚀 Iniciando aplicação..." -ForegroundColor Green
    
    # Ativar ambiente virtual se existir
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
        & .\venv\Scripts\Activate.ps1
    }
    
    # Executar Streamlit
    streamlit run app.py
}

Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
