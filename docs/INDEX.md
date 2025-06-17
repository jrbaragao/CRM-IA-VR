# 📚 Índice da Documentação

## 🚀 Deploy e Configuração

### [README.md](README.md)
Documentação principal do projeto com visão geral e instruções básicas.

### [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
Guia completo para fazer deploy no Google Cloud Run, incluindo instalação do SDK.

### [deploy-production.txt](deploy-production.txt)
Comandos prontos para deploy em produção.

### [update-deployment.txt](update-deployment.txt)
Comandos para atualizar deployments existentes.

## 🔧 CI/CD e Automação

### [CI_CD_GUIDE.md](CI_CD_GUIDE.md)
Guia completo de integração contínua e deploy contínuo com várias opções:
- GitHub Actions
- Cloud Build
- Scripts locais

## 🛠️ Solução de Problemas

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Guia de solução de problemas comuns, incluindo:
- Erros de porta
- Problemas de timeout
- Configurações de memória

### [STREAMLIT_CONFIG_INFO.md](STREAMLIT_CONFIG_INFO.md)
Referência de configurações válidas e depreciadas do Streamlit.

## 📁 Estrutura Recomendada

```
seu-projeto/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências Python
├── Dockerfile               # Configuração do container
├── .dockerignore           # Arquivos ignorados pelo Docker
├── .gcloudignore          # Arquivos ignorados pelo gcloud
├── .streamlit/            # Configurações do Streamlit
│   └── config.toml
├── .github/               # GitHub Actions (se usar)
│   └── workflows/
│       └── deploy.yml
├── deploy.ps1             # Script de deploy local
├── cloudbuild.yaml        # Configuração do Cloud Build
└── docs/                  # Documentação
    ├── INDEX.md           # Este arquivo
    ├── README.md
    ├── DEPLOY_GUIDE.md
    ├── CI_CD_GUIDE.md
    ├── TROUBLESHOOTING.md
    └── ...
```

## 🔍 Acesso Rápido

- **Primeiro Deploy?** → Comece com [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- **Problemas?** → Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Automação?** → Configure com [CI_CD_GUIDE.md](CI_CD_GUIDE.md)
- **Atualizar?** → Use [update-deployment.txt](update-deployment.txt) 