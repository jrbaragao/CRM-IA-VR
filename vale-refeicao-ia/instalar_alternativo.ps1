
# Script Alternativo de Instalação - Resolve problemas com metadata
Write-Host @"
====================================================
  Instalação Alternativa - Vale Refeição IA
  Resolvendo problemas de metadata
====================================================
"@ -ForegroundColor Cyan

# Ativar ambiente virtual
if (Test-Path "venv") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
}

# Atualizar ferramentas base
Write-Host "`n[1/6] Atualizando ferramentas base..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
Write-Host "✅ Ferramentas atualizadas!" -ForegroundColor Green

# Instalar dependências problemáticas primeiro
Write-Host "`n[2/6] Instalando dependências críticas..." -ForegroundColor Yellow

# Weasyprint requer dependências especiais no Windows
Write-Host "Instalando dependências sem weasyprint..." -ForegroundColor Yellow
pip install streamlit==1.29.0
pip install pandas==2.1.4
pip install numpy==1.26.2
pip install python-dotenv==1.0.0
pip install openai==1.57.2
pip install sqlalchemy==2.0.25
pip install psycopg2-binary==2.9.9
pip install openpyxl==3.1.2
pip install plotly==5.18.0

Write-Host "✅ Dependências básicas instaladas!" -ForegroundColor Green

# Tentar instalar LlamaIndex
Write-Host "`n[3/6] Instalando LlamaIndex (pode demorar)..." -ForegroundColor Yellow
try {
    # Instalar componentes separadamente
    pip install llama-index-core==0.9.48
    pip install llama-index-embeddings-openai==0.1.5
    pip install llama-index-llms-openai==0.1.5
    pip install chromadb==0.4.22
    pip install llama-index-vector-stores-chroma==0.1.4
    
    # Tentar instalar o pacote principal
    pip install llama-index==0.9.48 --no-deps
    
    Write-Host "✅ LlamaIndex instalado!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Aviso: Problema ao instalar LlamaIndex completo" -ForegroundColor Yellow
    Write-Host "Tentando versão alternativa..." -ForegroundColor Yellow
    pip install llama-index
}

# Criar requirements-working.txt com as versões que funcionaram
Write-Host "`n[4/6] Salvando configuração funcional..." -ForegroundColor Yellow
pip freeze > requirements-working.txt
Write-Host "✅ Arquivo requirements-working.txt criado!" -ForegroundColor Green

# Criar arquivo .env se necessário
Write-Host "`n[5/6] Verificando arquivo .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    $envContent = @"
# Banco de Dados
DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao

# OpenAI - IMPORTANTE: Adicione sua chave aqui!
OPENAI_API_KEY=sk-...

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST=False

# Configurações de Vale Refeição
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
DIAS_UTEIS_MES=22

# Ambiente
ENVIRONMENT=development
DEBUG=True
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
}

# Verificar instalação
Write-Host "`n[6/6] Verificando instalação..." -ForegroundColor Yellow
Write-Host "`nMódulos instalados:" -ForegroundColor Cyan

$modules = @(
    @{Name="streamlit"; Display="Streamlit"},
    @{Name="pandas"; Display="Pandas"},
    @{Name="openai"; Display="OpenAI"},
    @{Name="sqlalchemy"; Display="SQLAlchemy"},
    @{Name="llama_index"; Display="LlamaIndex"}
)

$allGood = $true
foreach ($module in $modules) {
    try {
        $result = python -c "import $($module.Name); print($($module.Name).__version__)" 2>$null
        if ($result) {
            Write-Host "✅ $($module.Display) $result" -ForegroundColor Green
        } else {
            Write-Host "✅ $($module.Display) instalado" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ $($module.Display) não instalado" -ForegroundColor Red
        $allGood = $false
    }
}

# Recomendações finais
Write-Host @"

====================================================
  Instalação Concluída!
====================================================
"@ -ForegroundColor Green

if ($allGood) {
    Write-Host "✅ Todos os módulos principais foram instalados!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Alguns módulos não foram instalados corretamente." -ForegroundColor Yellow
    Write-Host "Use requirements-working.txt para futuras instalações:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements-working.txt" -ForegroundColor Cyan
}

Write-Host @"

📝 Próximos passos:
1. Edite .env com sua chave OpenAI
2. Teste a aplicação: streamlit run app.py

💡 Dicas:
- Se houver erros, use: pip install -r requirements-minimal.txt
- Para relatórios PDF, instale weasyprint separadamente
- Use Docker para PostgreSQL (recomendado)

"@ -ForegroundColor Cyan

Read-Host "Pressione Enter para finalizar"
