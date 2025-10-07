#!/bin/bash
# Script de Deploy Rápido para Cloud Run
# Execute: chmod +x deploy-agora.sh && ./deploy-agora.sh

set -e

echo -e "\033[36m🚀 Deploy Rápido - Cloud Run\033[0m"
echo ""

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo -e "\033[31m❌ Erro: Execute este script a partir do diretório vale-refeicao-ia\033[0m"
    echo -e "\033[33m   cd vale-refeicao-ia\033[0m"
    exit 1
fi

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "\033[31m❌ gcloud CLI não encontrado\033[0m"
    echo -e "\033[33m   Instale: https://cloud.google.com/sdk/docs/install\033[0m"
    exit 1
fi

# Solicitar chave da OpenAI se não foi fornecida
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "\033[33m🔑 Digite sua chave da OpenAI (ou deixe em branco para pular):\033[0m"
    read -r OPENAI_API_KEY
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo ""
        echo -e "\033[33m⚠️ Nenhuma chave fornecida. Deploy será feito sem OPENAI_API_KEY.\033[0m"
        read -p "   Continuar? (s/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
            echo -e "\033[31mDeploy cancelado.\033[0m"
            exit 1
        fi
    fi
fi

echo ""
echo -e "\033[36m📋 Configuração do Deploy:\033[0m"
echo -e "   Projeto: awesome-carver-463213-r0"
echo -e "   Região: southamerica-east1"
echo -e "   Serviço: crmia-agente-autonomo"
echo -e "   Memória: 2Gi"
echo -e "   CPU: 2"
echo -e "   Timeout: 600s"
if [ -n "$OPENAI_API_KEY" ]; then
    MASKED_KEY="${OPENAI_API_KEY:0:7}...${OPENAI_API_KEY: -4}"
    echo -e "   OpenAI Key: $MASKED_KEY"
fi
echo ""

read -p "Iniciar deploy? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo -e "\033[31mDeploy cancelado.\033[0m"
    exit 1
fi

echo ""
echo -e "\033[33m🔨 Iniciando deploy...\033[0m"
echo -e "\033[90m   (Isso pode levar 5-10 minutos)\033[0m"
echo ""

# Construir comando de deploy
DEPLOY_CMD="gcloud run deploy crmia-agente-autonomo \
  --source . \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600"

if [ -n "$OPENAI_API_KEY" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY"
fi

# Executar deploy
echo -e "\033[90mExecutando: $DEPLOY_CMD\033[0m"
echo ""

eval "$DEPLOY_CMD"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "\033[32m============================================\033[0m"
    echo -e "\033[32m✅ DEPLOY CONCLUÍDO COM SUCESSO!\033[0m"
    echo -e "\033[32m============================================\033[0m"
    echo ""
    echo -e "\033[36m🌐 Para obter a URL do serviço:\033[0m"
    echo -e "   gcloud run services describe crmia-agente-autonomo --region southamerica-east1 --format='value(status.url)'"
    echo ""
    echo -e "\033[36m📊 Para ver logs:\033[0m"
    echo -e "   gcloud run services logs read crmia-agente-autonomo --region southamerica-east1 --limit 50"
    echo ""
else
    echo ""
    echo -e "\033[31m============================================\033[0m"
    echo -e "\033[31m❌ DEPLOY FALHOU\033[0m"
    echo -e "\033[31m============================================\033[0m"
    echo ""
    echo -e "\033[33mPara ver logs do erro:\033[0m"
    echo -e "   gcloud builds list --limit=5"
    echo ""
    echo -e "\033[33mPara testar localmente:\033[0m"
    echo -e "   ./testar-build.sh"
    echo ""
    exit 1
fi
