#!/bin/bash
# Script Bash para configurar o repositório Git (Linux/Mac)
# Execute este script para criar um novo repositório independente

echo -e "\033[32m🚀 Configurando repositório do Sistema de Vale Refeição IA\033[0m"

# Verificar se já existe um repositório git
if [ -d .git ]; then
    echo -e "\033[33m⚠️  Já existe um repositório Git neste diretório!\033[0m"
    read -p "Deseja remover e criar um novo? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf .git
        echo -e "\033[32m✅ Repositório anterior removido\033[0m"
    else
        echo -e "\033[31m❌ Operação cancelada\033[0m"
        exit 1
    fi
fi

# Inicializar novo repositório
echo -e "\n\033[36m📁 Inicializando repositório Git...\033[0m"
git init

# Criar branch main
git checkout -b main

# Adicionar todos os arquivos
echo -e "\n\033[36m📝 Adicionando arquivos ao repositório...\033[0m"
git add .

# Primeiro commit
echo -e "\n\033[36m💾 Criando commit inicial...\033[0m"
git commit -m "feat: commit inicial - Sistema de Vale Refeição com IA

- Estrutura base do projeto com Streamlit e LlamaIndex
- Agentes IA para extração, cálculo e relatórios
- Interface web moderna
- Integração com PostgreSQL e ChromaDB
- Processamento inteligente de planilhas de RH"

# Configurar remote (opcional)
echo -e "\n\033[33m🌐 Configuração do repositório remoto (GitHub/GitLab)\033[0m"
echo "Para adicionar um repositório remoto, use um dos comandos abaixo:"
echo ""
echo -e "\033[36mGitHub:\033[0m"
echo "  git remote add origin https://github.com/SEU_USUARIO/vale-refeicao-ia.git"
echo "  git push -u origin main"
echo ""
echo -e "\033[36mGitLab:\033[0m"
echo "  git remote add origin https://gitlab.com/SEU_USUARIO/vale-refeicao-ia.git"
echo "  git push -u origin main"

echo -e "\n\033[32m✅ Repositório local criado com sucesso!\033[0m"
echo ""

# Mostrar status
echo -e "\033[36m📊 Status do repositório:\033[0m"
git status

echo -e "\n\033[33m📋 Próximos passos:\033[0m"
echo "1. Crie um repositório no GitHub/GitLab"
echo "2. Adicione o remote origin com o comando apropriado acima"
echo "3. Faça push do código com: git push -u origin main"
echo "4. Configure CI/CD se necessário"

# Tornar o script executável
chmod +x setup_repository.sh
