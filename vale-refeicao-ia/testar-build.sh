#!/bin/bash
# Script para testar build Docker localmente antes do deploy
# Execute: chmod +x testar-build.sh && ./testar-build.sh

echo -e "\033[36m🔧 Testando Build Docker para Cloud Run...\033[0m"
echo ""

# Verificar se Docker está rodando
echo -e "\033[33m1️⃣ Verificando Docker...\033[0m"
if command -v docker &> /dev/null; then
    echo -e "   \033[32m✅ Docker encontrado\033[0m"
else
    echo -e "   \033[31m❌ Docker não encontrado. Instale o Docker.\033[0m"
    exit 1
fi

# Verificar se há um .env
echo ""
echo -e "\033[33m2️⃣ Verificando variáveis de ambiente...\033[0m"
if [ -f ".env" ]; then
    echo -e "   \033[32m✅ Arquivo .env encontrado\033[0m"
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "   \033[32m✅ OPENAI_API_KEY configurada\033[0m"
    else
        echo -e "   \033[33m⚠️ OPENAI_API_KEY não encontrada no .env\033[0m"
    fi
else
    echo -e "   \033[33m⚠️ Arquivo .env não encontrado (copie do .env.example)\033[0m"
fi

# Build da imagem
echo ""
echo -e "\033[33m3️⃣ Fazendo build da imagem Docker...\033[0m"
echo -e "   \033[90m(Isso pode levar alguns minutos...)\033[0m"

if docker build -t crmia-test:latest .; then
    echo -e "   \033[32m✅ Build concluído com sucesso!\033[0m"
else
    echo -e "   \033[31m❌ Build falhou! Verifique os erros acima.\033[0m"
    echo ""
    echo -e "\033[33mPossíveis soluções:\033[0m"
    echo -e "- Verifique se todos os arquivos estão presentes"
    echo -e "- Verifique o Dockerfile"
    echo -e "- Verifique o requirements.txt"
    exit 1
fi

# Perguntar se quer executar
echo ""
read -p "4️⃣ Deseja executar o container localmente? (s/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo -e "   \033[33mIniciando container na porta 8501...\033[0m"
    echo -e "   \033[36mAcesse: http://localhost:8501\033[0m"
    echo -e "   \033[90mPressione Ctrl+C para parar\033[0m"
    echo ""
    
    # Carregar OPENAI_API_KEY do .env se existir
    if [ -f ".env" ]; then
        export $(grep OPENAI_API_KEY .env | xargs)
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        docker run -p 8501:8501 -e OPENAI_API_KEY="$OPENAI_API_KEY" crmia-test:latest
    else
        echo -e "   \033[33m⚠️ OPENAI_API_KEY não encontrada, rodando sem ela\033[0m"
        docker run -p 8501:8501 crmia-test:latest
    fi
else
    echo ""
    echo -e "\033[32m✅ Build testado com sucesso!\033[0m"
    echo ""
    echo -e "\033[36mPróximos passos:\033[0m"
    echo -e "1. Para rodar localmente:"
    echo -e "   \033[90mdocker run -p 8501:8501 -e OPENAI_API_KEY=sua_chave crmia-test:latest\033[0m"
    echo ""
    echo -e "2. Para fazer deploy no Cloud Run:"
    echo -e "   \033[90mConsulte o arquivo PROBLEMA_BUILD_RESOLVIDO.md\033[0m"
    echo ""
fi
