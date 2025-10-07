# Dockerfile Proxy
# Este arquivo redireciona o build para o diretório vale-refeicao-ia
# Necessário porque o trigger do Cloud Build procura Dockerfile na raiz

FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos do subdiretório
COPY vale-refeicao-ia/requirements.txt .

# Remover dependências específicas do Windows que causam falha no Linux
RUN sed -i '/pyreadline3/d' requirements.txt && \
    sed -i '/pywin32/d' requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação do subdiretório
COPY vale-refeicao-ia/ .

# Criar diretórios necessários com permissões adequadas
RUN mkdir -p uploads exports chroma_db && \
    chmod -R 777 uploads exports chroma_db

# Expor porta padrão (Cloud Run usa a variável de ambiente PORT)
EXPOSE 8501

# Configurar variáveis de ambiente do Streamlit
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Comando para executar a aplicação
# Cloud Run define PORT automaticamente, usamos 8501 como fallback
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
