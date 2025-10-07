FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

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
