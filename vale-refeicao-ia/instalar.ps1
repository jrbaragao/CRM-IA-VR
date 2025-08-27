# Script de Instalação - Vale Refeição IA
# PowerShell Script com verificações e instalação automatizada

Write-Host @"
====================================================
  Sistema de Vale Refeição IA - Instalação
====================================================
"@ -ForegroundColor Cyan

# Função para verificar comandos
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# 1. Verificar Python
Write-Host "`n[1/8] Verificando Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
    
    # Verificar versão mínima (3.11)
    $version = [version]($pythonVersion -replace 'Python ', '')
    if ($version -lt [version]"3.11.0") {
        Write-Host "⚠️  Aviso: Recomenda-se Python 3.11 ou superior" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale Python 3.11+ de: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# 2. Criar ambiente virtual
Write-Host "`n[2/8] Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✅ Ambiente virtual já existe" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✅ Ambiente virtual criado!" -ForegroundColor Green
}

# 3. Ativar ambiente virtual
Write-Host "`n[3/8] Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Ambiente ativado!" -ForegroundColor Green

# 4. Atualizar pip
Write-Host "`n[4/8] Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip atualizado!" -ForegroundColor Green

# 5. Instalar dependências
Write-Host "`n[5/8] Instalando dependências (pode demorar alguns minutos)..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao instalar dependências!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# 6. Criar arquivo .env
Write-Host "`n[6/8] Configurando ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    $envContent = @"
# Banco de Dados
DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao

# OpenAI - IMPORTANTE: Adicione sua chave aqui!
OPENAI_API_KEY=sk-...

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

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
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua chave OpenAI!" -ForegroundColor Yellow
    
    # Abrir .env no notepad
    Start-Process notepad.exe ".env"
} else {
    Write-Host "✅ Arquivo .env já existe!" -ForegroundColor Green
}

# 7. Verificar Docker
Write-Host "`n[7/8] Verificando Docker..." -ForegroundColor Yellow
if (Test-Command docker) {
    $dockerVersion = docker --version
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
    
    # Perguntar se deseja iniciar serviços
    $response = Read-Host "`nDeseja iniciar PostgreSQL e ChromaDB via Docker? (S/N)"
    if ($response -eq 'S' -or $response -eq 's') {
        Write-Host "Iniciando serviços Docker..." -ForegroundColor Yellow
        docker-compose up -d
        Start-Sleep -Seconds 5
        docker ps
        Write-Host "✅ Serviços Docker iniciados!" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Docker não encontrado!" -ForegroundColor Yellow
    Write-Host "Para usar PostgreSQL via Docker, instale em: https://www.docker.com/" -ForegroundColor Yellow
    Write-Host "Você pode instalar PostgreSQL manualmente se preferir." -ForegroundColor Yellow
}

# 8. Criar script de inicialização
Write-Host "`n[8/8] Criando scripts de inicialização..." -ForegroundColor Yellow
$startScript = @"
@echo off
echo Iniciando Vale Refeicao IA...
call venv\Scripts\activate.bat
streamlit run app.py
"@
$startScript | Out-File -FilePath "iniciar.bat" -Encoding ASCII
Write-Host "✅ Script 'iniciar.bat' criado!" -ForegroundColor Green

# Resumo final
Write-Host @"

====================================================
  ✅ Instalação Concluída!
====================================================

📋 Checklist:
"@ -ForegroundColor Green

Write-Host "✅ Python instalado e verificado" -ForegroundColor Green
Write-Host "✅ Ambiente virtual criado" -ForegroundColor Green
Write-Host "✅ Dependências instaladas" -ForegroundColor Green
Write-Host "✅ Arquivo .env criado" -ForegroundColor Green

if (Test-Command docker) {
    Write-Host "✅ Docker disponível" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker não instalado (opcional)" -ForegroundColor Yellow
}

Write-Host @"

🚀 Próximos Passos:
1. Edite o arquivo .env com sua chave OpenAI
2. Configure o PostgreSQL (se não usou Docker)
3. Execute: iniciar.bat ou streamlit run app.py

📝 Documentação:
- README.md - Visão geral do projeto
- INSTALACAO_E_TESTE.md - Guia detalhado
- DEPLOY.md - Instruções de deploy

"@ -ForegroundColor Cyan

$response = Read-Host "Deseja iniciar a aplicação agora? (S/N)"
if ($response -eq 'S' -or $response -eq 's') {
    Write-Host "`nIniciando aplicação..." -ForegroundColor Yellow
    streamlit run app.py
} else {
    Write-Host "`nPara iniciar mais tarde, execute: streamlit run app.py" -ForegroundColor Yellow
    Write-Host "ou use o script: iniciar.bat" -ForegroundColor Yellow
}

Read-Host "`nPressione Enter para finalizar"
