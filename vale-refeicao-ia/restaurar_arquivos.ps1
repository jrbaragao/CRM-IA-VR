# Script para restaurar arquivos deletados do Git

Write-Host "🔄 Restaurando arquivos do projeto..." -ForegroundColor Green

# Verificar se estamos em um repositório Git
if (!(Test-Path .git)) {
    Write-Host "❌ Erro: Não é um repositório Git!" -ForegroundColor Red
    exit 1
}

# Listar arquivos deletados
Write-Host "`n📋 Arquivos que serão restaurados:" -ForegroundColor Yellow

# Obter lista de arquivos deletados
$deletedFiles = git ls-files --deleted

if ($deletedFiles) {
    $deletedFiles | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Cyan
    }
    
    Write-Host "`n🔄 Restaurando arquivos..." -ForegroundColor Green
    
    # Restaurar cada arquivo
    $deletedFiles | ForEach-Object {
        git checkout HEAD -- $_
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Restaurado: $_" -ForegroundColor Green
        } else {
            Write-Host "❌ Erro ao restaurar: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "ℹ️ Nenhum arquivo deletado encontrado." -ForegroundColor Yellow
}

# Verificar se há arquivos não commitados no último commit
Write-Host "`n🔍 Verificando arquivos do último commit..." -ForegroundColor Yellow

# Listar todos os arquivos que estavam no commit anterior
$filesInLastCommit = git ls-tree -r HEAD~1 --name-only

Write-Host "`n📦 Restaurando estrutura completa do commit anterior..." -ForegroundColor Cyan

# Criar diretórios necessários
$directories = @(
    ".streamlit",
    "src",
    "src\agents",
    "src\config",
    "src\data",
    "src\ui",
    "src\ui\pages",
    "src\ui\components",
    "src\utils",
    "prompts",
    "tests",
    "docs"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Criado diretório: $dir" -ForegroundColor Green
    }
}

# Restaurar todos os arquivos do commit anterior
Write-Host "`n🔄 Restaurando todos os arquivos..." -ForegroundColor Yellow

git checkout HEAD~1 -- app.py 2>$null
git checkout HEAD~1 -- .gitignore 2>$null
git checkout HEAD~1 -- LICENSE 2>$null
git checkout HEAD~1 -- README.md 2>$null
git checkout HEAD~1 -- CONTRIBUTING.md 2>$null
git checkout HEAD~1 -- DEPLOY.md 2>$null
git checkout HEAD~1 -- pyproject.toml 2>$null
git checkout HEAD~1 -- .streamlit/config.toml 2>$null
git checkout HEAD~1 -- src/ 2>$null
git checkout HEAD~1 -- prompts/ 2>$null

Write-Host "`n✅ Processo de restauração concluído!" -ForegroundColor Green

# Verificar status
Write-Host "`n📊 Status atual:" -ForegroundColor Yellow
git status --short

Write-Host "`n💡 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Verifique os arquivos restaurados"
Write-Host "2. Execute: pip install -r requirements.txt"
Write-Host "3. Configure o .env baseado no .env.example"
Write-Host "4. Execute: streamlit run app.py"
