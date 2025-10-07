# Script para testar build Docker localmente antes do deploy
# Execute: .\testar-build.ps1

Write-Host "🔧 Testando Build Docker para Cloud Run..." -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
Write-Host "1️⃣ Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "   ✅ Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker não encontrado. Instale o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar se há um .env
Write-Host ""
Write-Host "2️⃣ Verificando variáveis de ambiente..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ Arquivo .env encontrado" -ForegroundColor Green
    $envContent = Get-Content ".env" | Select-String "OPENAI_API_KEY"
    if ($envContent) {
        Write-Host "   ✅ OPENAI_API_KEY configurada" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ OPENAI_API_KEY não encontrada no .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️ Arquivo .env não encontrado (copie do .env.example)" -ForegroundColor Yellow
}

# Build da imagem
Write-Host ""
Write-Host "3️⃣ Fazendo build da imagem Docker..." -ForegroundColor Yellow
Write-Host "   (Isso pode levar alguns minutos...)" -ForegroundColor Gray
$buildResult = docker build -t crmia-test:latest . 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Build concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Build falhou! Verifique os erros acima." -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "- Verifique se todos os arquivos estão presentes" -ForegroundColor White
    Write-Host "- Verifique o Dockerfile" -ForegroundColor White
    Write-Host "- Verifique o requirements.txt" -ForegroundColor White
    exit 1
}

# Perguntar se quer executar
Write-Host ""
$runContainer = Read-Host "4️⃣ Deseja executar o container localmente? (s/n)"

if ($runContainer -eq "s" -or $runContainer -eq "S") {
    Write-Host ""
    Write-Host "   Iniciando container na porta 8501..." -ForegroundColor Yellow
    Write-Host "   Acesse: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "   Pressione Ctrl+C para parar" -ForegroundColor Gray
    Write-Host ""
    
    # Carregar OPENAI_API_KEY do .env se existir
    $openaiKey = ""
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        $keyLine = $envContent | Select-String "OPENAI_API_KEY=" | Select-Object -First 1
        if ($keyLine) {
            $openaiKey = $keyLine.ToString().Split("=")[1].Trim()
        }
    }
    
    if ($openaiKey) {
        docker run -p 8501:8501 -e OPENAI_API_KEY=$openaiKey crmia-test:latest
    } else {
        Write-Host "   ⚠️ OPENAI_API_KEY não encontrada, rodando sem ela" -ForegroundColor Yellow
        docker run -p 8501:8501 crmia-test:latest
    }
} else {
    Write-Host ""
    Write-Host "✅ Build testado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Cyan
    Write-Host "1. Para rodar localmente:" -ForegroundColor White
    Write-Host "   docker run -p 8501:8501 -e OPENAI_API_KEY=sua_chave crmia-test:latest" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Para fazer deploy no Cloud Run:" -ForegroundColor White
    Write-Host "   Consulte o arquivo PROBLEMA_BUILD_RESOLVIDO.md" -ForegroundColor Gray
    Write-Host ""
}
