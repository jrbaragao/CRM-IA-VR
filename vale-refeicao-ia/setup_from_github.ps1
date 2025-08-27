# Script para configurar projeto baseado em templates do GitHub

Write-Host "🔍 Configurando projeto Vale Refeição IA..." -ForegroundColor Green

# Opção 1: Usar template de Streamlit + LlamaIndex
Write-Host "`n📦 Opções de templates disponíveis:" -ForegroundColor Yellow
Write-Host "1. Streamlit + LlamaIndex Chat Template"
Write-Host "2. Full Stack AI Application Template"
Write-Host "3. Criar estrutura customizada baseada em exemplos"

$option = Read-Host "`nEscolha uma opção (1-3)"

switch ($option) {
    "1" {
        Write-Host "`n📥 Clonando template Streamlit + LlamaIndex..." -ForegroundColor Cyan
        
        # Clone de exemplo de chat com LlamaIndex
        $tempDir = "temp_template"
        git clone https://github.com/streamlit/llm-examples.git $tempDir
        
        # Copiar estrutura relevante
        if (Test-Path $tempDir) {
            Copy-Item -Path "$tempDir\pages\*" -Destination ".\src\ui\pages\" -Recurse -Force
            Remove-Item -Recurse -Force $tempDir
        }
    }
    "2" {
        Write-Host "`n📥 Baixando estrutura de aplicação Full Stack..." -ForegroundColor Cyan
        
        # Criar estrutura baseada em melhores práticas
        $directories = @(
            "src\agents",
            "src\config", 
            "src\data",
            "src\ui\pages",
            "src\ui\components",
            "src\utils",
            "tests\unit",
            "tests\integration",
            "docs",
            "prompts",
            "notebooks"
        )
        
        foreach ($dir in $directories) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        
        Write-Host "✅ Estrutura de diretórios criada" -ForegroundColor Green
    }
    "3" {
        Write-Host "`n🛠️ Criando estrutura customizada..." -ForegroundColor Cyan
        
        # Baixar exemplos específicos
        Write-Host "Baixando exemplos de código..." -ForegroundColor White
        
        # Criar arquivo com links úteis
        @"
# Repositórios de Referência

## Templates Streamlit + IA
- https://github.com/streamlit/llm-examples
- https://github.com/streamlit/example-app-chat-pandas
- https://github.com/jerryjliu/llama_index/tree/main/examples

## Sistemas de RH/Vale Refeição
- https://github.com/pedroaranha/VR-Code
- https://github.com/izabelmcarvalho/calculadora-vr
- https://github.com/akiraTatesawa/valex-ddd

## Exemplos LlamaIndex
- https://github.com/run-llama/llama_index/tree/main/docs/examples
- https://github.com/run-llama/llama-hub
- https://github.com/run-llama/rags

## Componentes Úteis
- Data Processing: https://github.com/streamlit/example-app-csv-wrangler
- Multi-page Apps: https://github.com/streamlit/example-app-multi-page
- Authentication: https://github.com/mkhorasani/Streamlit-Authenticator
"@ | Out-File -FilePath "REFERENCIAS_GITHUB.md" -Encoding utf8
        
        Write-Host "✅ Arquivo de referências criado: REFERENCIAS_GITHUB.md" -ForegroundColor Green
    }
}

Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Revise os arquivos de referência"
Write-Host "2. Adapte o código para suas necessidades"
Write-Host "3. Instale as dependências: pip install -r requirements.txt"
Write-Host "4. Configure o .env baseado no .env.example"

Write-Host "`n💡 Dica: Use os repositórios de referência como inspiração!" -ForegroundColor Cyan

