# Script PowerShell para buscar e clonar o projeto do GitHub

Write-Host "🔍 Assistente para Buscar e Clonar Projeto do GitHub" -ForegroundColor Green
Write-Host "=" * 50

# Perguntar informações
$usuario = Read-Host "`nQual seu usuário do GitHub? (ou pressione Enter se não souber)"
$nomeRepo = Read-Host "Qual o nome do repositório? (padrão: vale-refeicao-ia)"

if ([string]::IsNullOrWhiteSpace($nomeRepo)) {
    $nomeRepo = "vale-refeicao-ia"
}

# Opções de busca
Write-Host "`n📋 O que você quer fazer?" -ForegroundColor Yellow
Write-Host "1. Buscar o repositório no GitHub"
Write-Host "2. Clonar se já sei a URL"
Write-Host "3. Ver meus repositórios"
Write-Host "4. Buscar em organizações"

$opcao = Read-Host "`nEscolha (1-4)"

switch ($opcao) {
    "1" {
        Write-Host "`n🔍 Abrindo buscas no navegador..." -ForegroundColor Cyan
        
        # Abrir várias buscas
        $searchQueries = @(
            "https://github.com/search?q=$nomeRepo&type=repositories",
            "https://github.com/search?q=vale+refeicao+streamlit&type=repositories",
            "https://github.com/search?q=vale+refeição+ia&type=repositories"
        )
        
        foreach ($query in $searchQueries) {
            Start-Process $query
            Start-Sleep -Milliseconds 500
        }
        
        Write-Host "✅ Buscas abertas no navegador!" -ForegroundColor Green
        Write-Host "`nQuando encontrar, copie a URL e execute este script novamente escolhendo opção 2" -ForegroundColor Yellow
    }
    
    "2" {
        $repoUrl = Read-Host "`nCole a URL completa do repositório"
        
        if ($repoUrl -match "github.com") {
            Write-Host "`n📥 Clonando repositório..." -ForegroundColor Cyan
            
            # Remover .git se existir no final
            $repoUrl = $repoUrl -replace "\.git$", ""
            
            # Adicionar .git
            $cloneUrl = "$repoUrl.git"
            
            # Executar clone
            $cloneCommand = "git clone $cloneUrl"
            Write-Host "Executando: $cloneCommand" -ForegroundColor White
            
            Invoke-Expression $cloneCommand
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "`n✅ Repositório clonado com sucesso!" -ForegroundColor Green
                
                # Extrair nome do repo da URL
                $repoName = $repoUrl.Split('/')[-1]
                
                Write-Host "`n📁 Entrando no diretório..." -ForegroundColor Cyan
                Set-Location $repoName
                
                Write-Host "`n📋 Conteúdo do repositório:" -ForegroundColor Yellow
                Get-ChildItem | Format-Table Name, Mode, LastWriteTime -AutoSize
            } else {
                Write-Host "`n❌ Erro ao clonar. Verifique:" -ForegroundColor Red
                Write-Host "- A URL está correta?"
                Write-Host "- O repositório é privado? (precisa de autenticação)"
                Write-Host "- Você tem permissão de acesso?"
            }
        } else {
            Write-Host "❌ URL inválida. Deve conter 'github.com'" -ForegroundColor Red
        }
    }
    
    "3" {
        if (![string]::IsNullOrWhiteSpace($usuario)) {
            Write-Host "`n🔍 Abrindo seus repositórios..." -ForegroundColor Cyan
            Start-Process "https://github.com/$usuario?tab=repositories"
            Start-Process "https://github.com/$usuario?tab=stars"
        } else {
            Write-Host "❌ Usuário não informado" -ForegroundColor Red
        }
    }
    
    "4" {
        $org = Read-Host "`nQual o nome da organização?"
        if (![string]::IsNullOrWhiteSpace($org)) {
            Start-Process "https://github.com/orgs/$org/repositories"
        }
    }
}

Write-Host "`n💡 Dicas:" -ForegroundColor Yellow
Write-Host "- Se o repositório for privado, configure suas credenciais Git primeiro"
Write-Host "- Use 'git config --global credential.helper wincred' no Windows"
Write-Host "- Para SSH: ssh-keygen -t rsa -b 4096 -C 'seu-email@example.com'"

Write-Host "`n📌 Próximos passos após clonar:" -ForegroundColor Cyan
Write-Host "1. cd $nomeRepo"
Write-Host "2. pip install -r requirements.txt"
Write-Host "3. cp .env.example .env"
Write-Host "4. streamlit run app.py"

