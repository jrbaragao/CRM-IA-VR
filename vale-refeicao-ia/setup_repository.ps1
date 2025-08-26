# Script PowerShell para configurar o repositório Git
# Execute este script para criar um novo repositório independente

Write-Host "🚀 Configurando repositório do Sistema de Vale Refeição IA" -ForegroundColor Green

# Verificar se já existe um repositório git
if (Test-Path .git) {
    Write-Host "⚠️  Já existe um repositório Git neste diretório!" -ForegroundColor Yellow
    $response = Read-Host "Deseja remover e criar um novo? (s/n)"
    if ($response -eq 's') {
        Remove-Item -Recurse -Force .git
        Write-Host "✅ Repositório anterior removido" -ForegroundColor Green
    } else {
        Write-Host "❌ Operação cancelada" -ForegroundColor Red
        exit
    }
}

# Inicializar novo repositório
Write-Host "`n📁 Inicializando repositório Git..." -ForegroundColor Cyan
git init

# Criar branch main
git checkout -b main

# Adicionar todos os arquivos
Write-Host "`n📝 Adicionando arquivos ao repositório..." -ForegroundColor Cyan
git add .

# Primeiro commit
Write-Host "`n💾 Criando commit inicial..." -ForegroundColor Cyan
git commit -m "feat: commit inicial - Sistema de Vale Refeição com IA

- Estrutura base do projeto com Streamlit e LlamaIndex
- Agentes IA para extração, cálculo e relatórios
- Interface web moderna
- Integração com PostgreSQL e ChromaDB
- Processamento inteligente de planilhas de RH"

# Configurar remote (opcional)
Write-Host "`n🌐 Configuração do repositório remoto (GitHub/GitLab)" -ForegroundColor Yellow
Write-Host "Para adicionar um repositório remoto, use um dos comandos abaixo:" -ForegroundColor White
Write-Host ""
Write-Host "GitHub:" -ForegroundColor Cyan
Write-Host "  git remote add origin https://github.com/SEU_USUARIO/vale-refeicao-ia.git" -ForegroundColor White
Write-Host "  git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "GitLab:" -ForegroundColor Cyan
Write-Host "  git remote add origin https://gitlab.com/SEU_USUARIO/vale-refeicao-ia.git" -ForegroundColor White
Write-Host "  git push -u origin main" -ForegroundColor White

Write-Host "`n✅ Repositório local criado com sucesso!" -ForegroundColor Green
Write-Host ""

# Mostrar status
Write-Host "📊 Status do repositório:" -ForegroundColor Cyan
git status

Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Crie um repositório no GitHub/GitLab"
Write-Host "2. Adicione o remote origin com o comando apropriado acima"
Write-Host "3. Faça push do código com: git push -u origin main"
Write-Host "4. Configure CI/CD se necessário"
