# Análise de Notas Fiscais - Aplicação Streamlit para Google Cloud Run

Este projeto é uma aplicação Streamlit para análise inteligente de notas fiscais com IA, containerizada e pronta para ser implantada no Google Cloud Run.

## 📁 Estrutura do Projeto

```
seu-projeto/
│
├── app.py               # Aplicação Streamlit principal
├── requirements.txt     # Dependências Python
├── Dockerfile          # Configuração do container
├── .dockerignore       # Arquivos ignorados na construção do Docker
├── .gcloudignore       # Arquivos ignorados pelo Google Cloud Build
├── .streamlit/         # Configurações do Streamlit
│   └── config.toml     # Arquivo de configuração
└── README.md           # Este arquivo
```

## 🚀 Como Executar Localmente

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação
```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 🐳 Docker

### Construir a imagem
```bash
docker build -t analise-nf:latest .
```

### Executar o container localmente
```bash
docker run -p 8080:8080 -e PORT=8080 analise-nf:latest
```

## ☁️ Deploy no Google Cloud Run

### Pré-requisitos
- Conta no Google Cloud Platform
- Google Cloud CLI instalado (`gcloud`)
- Projeto configurado no GCP

### Passos para o deploy

1. **Autenticar no Google Cloud**
```bash
gcloud auth login
```

2. **Configurar o projeto**
```bash
gcloud config set project SEU_PROJECT_ID
```

3. **Habilitar as APIs necessárias**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

4. **Construir e enviar a imagem para o Google Container Registry**
```bash
# Configurar o Docker para usar o gcloud como auxiliar de credencial
gcloud auth configure-docker

# Construir e enviar a imagem
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/analise-nf
```

5. **Fazer o deploy no Cloud Run**
```bash
gcloud run deploy analise-nf \
  --image gcr.io/SEU_PROJECT_ID/analise-nf \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

### Deploy alternativo usando o Cloud Build

Você também pode usar o Cloud Build diretamente:

```bash
gcloud run deploy analise-nf \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

**Nota**: Configuramos mais memória (2Gi) e CPU (2) porque aplicações Streamlit com processamento de dados precisam de mais recursos.

## 🚀 Funcionalidades da Aplicação

- **Upload de Arquivos CSV**: Carregamento de cabeçalhos e itens de notas fiscais
- **Análise com IA**: Chat inteligente usando GPT-4o para análise dos dados
- **Consultas SQL**: Geração automática de queries SQL baseadas em perguntas em português
- **Visualizações**: Gráficos e métricas dos dados carregados
- **Interface Intuitiva**: UI moderna e responsiva com Streamlit

## 🔧 Variáveis de Ambiente

O Google Cloud Run define automaticamente:
- `PORT` - A porta onde a aplicação deve escutar (padrão: 8080)

Variáveis importantes para a aplicação:
- `OPENAI_API_KEY` - Chave da API OpenAI (pode ser configurada na interface)

Para adicionar variáveis de ambiente no Cloud Run:

```bash
gcloud run services update analise-nf \
  --update-env-vars OPENAI_API_KEY=sua-chave-aqui
```

**Nota**: Por segurança, é recomendado usar o Google Secret Manager para armazenar a API key.

## 📊 Monitoramento

Após o deploy, você pode:
- Ver logs: `gcloud run services logs read analise-nf`
- Obter a URL do serviço: `gcloud run services describe analise-nf --format 'value(status.url)'`
- Monitorar métricas no Console do Google Cloud
- Verificar o uso de memória e CPU (importante para aplicações Streamlit)

## 🛡️ Segurança

- A aplicação roda com um usuário não-root no container
- Use `--no-allow-unauthenticated` se quiser exigir autenticação
- Configure o Cloud IAM para controlar o acesso

## 💡 Dicas Específicas para Streamlit

1. **Performance**: 
   - Use cache do Streamlit (`@st.cache_data`) para operações pesadas
   - Configure recursos adequados (mínimo 2Gi RAM para aplicações com IA)

2. **Uploads de Arquivo**:
   - O limite padrão é 200MB (configurável)
   - Arquivos temporários são limpos automaticamente

3. **Sessões**:
   - O Streamlit mantém estado por sessão
   - Use `st.session_state` para persistir dados entre interações

4. **Otimização de custos**: 
   - Configure auto-scaling mínimo para 0 instâncias
   - Use timeouts apropriados para sua aplicação

## 📚 Recursos Adicionais

- [Documentação do Google Cloud Run](https://cloud.google.com/run/docs)
- [Melhores práticas para containers](https://cloud.google.com/run/docs/tips)
- [Preços do Cloud Run](https://cloud.google.com/run/pricing) 