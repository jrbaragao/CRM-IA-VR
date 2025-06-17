# 📊 Análise de Notas Fiscais - Streamlit + Google Cloud Run

Aplicação web para análise inteligente de notas fiscais com IA (GPT-4), desenvolvida em Streamlit e pronta para deploy no Google Cloud Run.

## 🚀 Quick Start

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
streamlit run app.py

# Deploy no Cloud Run
gcloud run deploy analise-nf --source . --memory 4Gi
```

## 📚 Documentação Completa

Toda a documentação detalhada está organizada no diretório `docs/`:

- 📖 **[docs/INDEX.md](docs/INDEX.md)** - Índice completo da documentação
- 🚀 **[docs/DEPLOY_GUIDE.md](docs/DEPLOY_GUIDE.md)** - Guia de deploy passo a passo
- 🔧 **[docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md)** - Configurar deploy automático
- 🛠️ **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solução de problemas

## 🌟 Funcionalidades

- Upload e análise de arquivos CSV de notas fiscais
- Chat inteligente com GPT-4 para análise dos dados
- Conversão automática de perguntas em SQL
- Interface moderna e responsiva
- Pronto para deploy no Google Cloud Run

## 🛠️ Stack Tecnológica

- **Frontend**: Streamlit
- **Backend**: Python, SQLite
- **IA**: OpenAI GPT-4
- **Deploy**: Google Cloud Run, Docker
- **Visualização**: Plotly, Matplotlib, Seaborn

## 📋 Pré-requisitos

- Python 3.11+
- Conta Google Cloud (para deploy)
- API Key da OpenAI (para funcionalidades de IA)

## 🤝 Contribuindo

Veja as diretrizes de contribuição em [docs/README.md](docs/README.md).

## 📄 Licença

Este projeto está sob a licença MIT. 