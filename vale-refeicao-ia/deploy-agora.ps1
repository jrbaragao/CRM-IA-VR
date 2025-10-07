# Script de Deploy Rápido para Cloud Run
# Execute: .\deploy-agora.ps1

param(
    [string]$OpenAIKey = "",
    [string]$Method = "direct"
)

Write-Host "🚀 Deploy Rápido - Cloud Run" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Erro: Execute este script a partir do diretório vale-refeicao-ia" -ForegroundColor Red
    Write-Host "   cd vale-refeicao-ia" -ForegroundColor Yellow
    exit 1
}

# Verificar gcloud
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "❌ gcloud CLI não encontrado" -ForegroundColor Red
    Write-Host "   Instale: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Solicitar chave da OpenAI se não foi fornecida
if ([string]::IsNullOrWhiteSpace($OpenAIKey)) {
    Write-Host "🔑 Digite sua chave da OpenAI:" -ForegroundColor Yellow
    $OpenAIKey = Read-Host "   OPENAI_API_KEY"
    
    if ([string]::IsNullOrWhiteSpace($OpenAIKey)) {
        Write-Host ""
        Write-Host "⚠️ Nenhuma chave fornecida. Deploy será feito sem OPENAI_API_KEY." -ForegroundColor Yellow
        $confirm = Read-Host "   Continuar? (s/n)"
        if ($confirm -ne "s" -and $confirm -ne "S") {
            Write-Host "Deploy cancelado." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "📋 Configuração do Deploy:" -ForegroundColor Cyan
Write-Host "   Projeto: awesome-carver-463213-r0" -ForegroundColor White
Write-Host "   Região: southamerica-east1" -ForegroundColor White
Write-Host "   Serviço: crmia-agente-autonomo" -ForegroundColor White
Write-Host "   Memória: 2Gi" -ForegroundColor White
Write-Host "   CPU: 2" -ForegroundColor White
Write-Host "   Timeout: 600s" -ForegroundColor White
if (-not [string]::IsNullOrWhiteSpace($OpenAIKey)) {
    $maskedKey = $OpenAIKey.Substring(0, [Math]::Min(7, $OpenAIKey.Length)) + "..." + $OpenAIKey.Substring([Math]::Max($OpenAIKey.Length - 4, 7))
    Write-Host "   OpenAI Key: $maskedKey" -ForegroundColor White
}
Write-Host ""

$confirm = Read-Host "Iniciar deploy? (s/n)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "Deploy cancelado." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔨 Iniciando deploy..." -ForegroundColor Yellow
Write-Host "   (Isso pode levar 5-10 minutos)" -ForegroundColor Gray
Write-Host ""

# Construir comando de deploy
$deployCmd = "gcloud run deploy crmia-agente-autonomo --source . --platform managed --region southamerica-east1 --allow-unauthenticated --memory 2Gi --cpu 2 --timeout 600"

if (-not [string]::IsNullOrWhiteSpace($OpenAIKey)) {
    $deployCmd += " --set-env-vars OPENAI_API_KEY=$OpenAIKey"
}

# Executar deploy
Write-Host "Executando: $deployCmd" -ForegroundColor Gray
Write-Host ""

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Para obter a URL do serviço:" -ForegroundColor Cyan
    Write-Host "   gcloud run services describe crmia-agente-autonomo --region southamerica-east1 --format='value(status.url)'" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Para ver logs:" -ForegroundColor Cyan
    Write-Host "   gcloud run services logs read crmia-agente-autonomo --region southamerica-east1 --limit 50" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "❌ DEPLOY FALHOU" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para ver logs do erro:" -ForegroundColor Yellow
    Write-Host "   .\ver-logs-build.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Para testar localmente:" -ForegroundColor Yellow
    Write-Host "   .\testar-build.ps1" -ForegroundColor White
    Write-Host ""
}
