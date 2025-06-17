# Script de Deploy para Google Cloud Run
# Uso: .\deploy.ps1 -message "Sua mensagem de commit"

param(
    [string]$message = "Update deployment",
    [switch]$skipGit = $false,
    [switch]$production = $false
)

# Cores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-Host "Deploy Automatico para Google Cloud Run" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
try {
    $gcloudVersion = gcloud version --format=json 2>$null | ConvertFrom-Json
    Write-Host "[OK] Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Google Cloud SDK nao esta instalado!" -ForegroundColor Red
    Write-Host "   Baixe em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Mostrar projeto atual
$currentProject = gcloud config get-value project 2>$null
Write-Host "Projeto atual: $currentProject" -ForegroundColor Yellow

# Git operations (se não for skipGit)
if (-not $skipGit) {
    Write-Host ""
    Write-Host "Preparando alteracoes do Git..." -ForegroundColor Yellow
    
    # Verificar status do git
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "   Arquivos modificados encontrados" -ForegroundColor Gray
        
        # Adicionar todos os arquivos
        git add .
        
        # Fazer commit
        git commit -m $message
        Write-Host "[OK] Commit realizado: $message" -ForegroundColor Green
        
        # Push para o repositório
        Write-Host "   Enviando para o repositorio..." -ForegroundColor Gray
        git push origin main
        Write-Host "[OK] Push concluido" -ForegroundColor Green
    } else {
        Write-Host "   Nenhuma alteracao para commit" -ForegroundColor Gray
    }
}

# Configurar nome do serviço baseado no ambiente
$serviceName = if ($production) { "analise-nf-prod" } else { "analise-nf" }
$memory = if ($production) { "4Gi" } else { "2Gi" }
$cpu = if ($production) { "4" } else { "2" }

Write-Host ""
Write-Host "Iniciando build e deploy..." -ForegroundColor Yellow
Write-Host "   Servico: $serviceName" -ForegroundColor Gray
Write-Host "   Memoria: $memory" -ForegroundColor Gray
Write-Host "   CPU: $cpu" -ForegroundColor Gray

# Deploy para Cloud Run
try {
    $deployResult = gcloud run deploy $serviceName `
        --source . `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --memory $memory `
        --cpu $cpu `
        --timeout 3600 `
        --min-instances 0 `
        --max-instances 10 `
        2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Deploy concluido com sucesso!" -ForegroundColor Green
        
        # Obter URL do serviço
        $serviceUrl = gcloud run services describe $serviceName `
            --platform managed `
            --region us-central1 `
            --format "value(status.url)" `
            2>$null
            
        if ($serviceUrl) {
            Write-Host ""
            Write-Host "URL do servico:" -ForegroundColor Cyan
            Write-Host "   $serviceUrl" -ForegroundColor White
            Write-Host ""
            
            # Perguntar se quer abrir no navegador
            $openBrowser = Read-Host "Deseja abrir no navegador? (S/N)"
            if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
                Start-Process $serviceUrl
            }
        }
    } else {
        Write-Host "[ERRO] Erro durante o deploy" -ForegroundColor Red
        Write-Host $deployResult -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERRO] Erro durante o deploy: $_" -ForegroundColor Red
    exit 1
}

# Mostrar comandos úteis
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Cyan
Write-Host "   Ver logs:        gcloud run services logs read $serviceName --limit 50" -ForegroundColor Gray
Write-Host "   Ver logs live:   gcloud run services logs tail $serviceName" -ForegroundColor Gray
Write-Host "   Ver metricas:    https://console.cloud.google.com/run/detail/us-central1/$serviceName/metrics" -ForegroundColor Gray
Write-Host ""

# Verificar se há builds em andamento
$builds = gcloud builds list --ongoing --limit 1 --format=json 2>$null | ConvertFrom-Json
if ($builds.Count -gt 0) {
    Write-Host "Build em andamento..." -ForegroundColor Yellow
    Write-Host "   ID: $($builds[0].id)" -ForegroundColor Gray
    Write-Host "   Use 'gcloud builds log $($builds[0].id) --stream' para acompanhar" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Deploy finalizado!" -ForegroundColor Green
Write-Host "" 