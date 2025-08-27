# Script PowerShell para limpeza de arquivos duplicados
# Projeto: CRMIA-VR

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host " LIMPEZA DE ARQUIVOS DUPLICADOS"         -ForegroundColor Cyan
Write-Host " Projeto: CRMIA-VR"                      -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório pai
Set-Location -Path "D:\Dados\Sites\Cursor\CRMIA-VR"

Write-Host "[1/3] Removendo arquivos do projeto antigo na raiz..." -ForegroundColor Yellow
Write-Host ""

# Lista de arquivos para remover
$arquivosRemover = @(
    "app.py",
    "app_original.py",
    "requirements.txt",
    "cloudbuild.yaml",
    "deploy.ps1",
    "Dockerfile",
    "Dockerfile.complex",
    "aindo",
    "tatus",
    "h origin docker-support"
)

# Remover cada arquivo
foreach ($arquivo in $arquivosRemover) {
    if (Test-Path $arquivo) {
        Remove-Item $arquivo -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Removido: $arquivo" -ForegroundColor Green
    } else {
        Write-Host "- Não encontrado: $arquivo" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[2/3] Verificando pastas duplicadas..." -ForegroundColor Yellow
Write-Host ""

# Verificar pasta CRM-IA-VR
if (Test-Path "CRM-IA-VR") {
    Write-Host "ATENÇÃO: Encontrada pasta CRM-IA-VR (possível backup)" -ForegroundColor Magenta
    $resposta = Read-Host "Deseja removê-la? (S/N)"
    
    if ($resposta -eq 'S' -or $resposta -eq 's') {
        Write-Host "Removendo pasta CRM-IA-VR..." -ForegroundColor Yellow
        Remove-Item -Path "CRM-IA-VR" -Recurse -Force
        Write-Host "✓ Removido: pasta CRM-IA-VR" -ForegroundColor Green
    } else {
        Write-Host "- Mantida: pasta CRM-IA-VR" -ForegroundColor Gray
    }
}

# Verificar pasta docs
if (Test-Path "docs") {
    Write-Host ""
    Write-Host "ATENÇÃO: Encontrada pasta docs (documentação do projeto antigo)" -ForegroundColor Magenta
    $resposta = Read-Host "Deseja removê-la? (S/N)"
    
    if ($resposta -eq 'S' -or $resposta -eq 's') {
        Write-Host "Removendo pasta docs..." -ForegroundColor Yellow
        Remove-Item -Path "docs" -Recurse -Force
        Write-Host "✓ Removido: pasta docs" -ForegroundColor Green
    } else {
        Write-Host "- Mantida: pasta docs" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[3/3] Limpeza concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " RESUMO:"                                -ForegroundColor Cyan
Write-Host " - Arquivos do projeto antigo removidos" -ForegroundColor White
Write-Host " - Pasta vale-refeicao-ia mantida"       -ForegroundColor White
Write-Host " - Workspace limpo e organizado"         -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar estrutura final
Write-Host "Estrutura final do diretório:" -ForegroundColor Yellow
Get-ChildItem -Name

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
