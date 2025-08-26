# 🚀 Guia de Deploy - Sistema de Vale Refeição IA

Este guia detalha como fazer deploy da aplicação em diferentes ambientes.

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Docker (opcional)
- Conta em serviço de cloud (AWS, GCP, Azure, Heroku, etc.)

## 🏠 Deploy Local

### 1. Preparação do Ambiente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/vale-refeicao-ia.git
cd vale-refeicao-ia

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração do Banco de Dados

```bash
# Instale PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# MacOS
brew install postgresql

# Windows - baixe o instalador em postgresql.org

# Crie o banco de dados
sudo -u postgres psql
CREATE DATABASE vale_refeicao;
CREATE USER vr_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE vale_refeicao TO vr_user;
\q
```

### 3. Configuração de Variáveis

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env
DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao
OPENAI_API_KEY=sk-...
```

### 4. Executar Aplicação

```bash
streamlit run app.py
```

## 🐳 Deploy com Docker

### 1. Dockerfile

```dockerfile
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

# Criar diretórios necessários
RUN mkdir -p uploads exports chroma_db

# Expor porta
EXPOSE 8501

# Comando para executar
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: vale_refeicao
      POSTGRES_USER: vr_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://vr_user:${DB_PASSWORD}@postgres:5432/vale_refeicao
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads
      - ./exports:/app/exports
      - ./chroma_db:/app/chroma_db

volumes:
  postgres_data:
```

### 3. Executar com Docker Compose

```bash
# Criar arquivo .env com variáveis
echo "DB_PASSWORD=sua_senha_segura" >> .env
echo "OPENAI_API_KEY=sk-..." >> .env

# Construir e executar
docker-compose up --build
```

## ☁️ Deploy na Nuvem

### Heroku

1. **Instalar Heroku CLI**
```bash
# MacOS
brew tap heroku/brew && brew install heroku

# Windows/Linux - baixe do site heroku.com
```

2. **Preparar arquivos**

Crie `Procfile`:
```
web: sh setup.sh && streamlit run app.py
```

Crie `setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"seu-email@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

3. **Deploy**
```bash
heroku create vale-refeicao-ia
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

### Google Cloud Run

1. **Preparar projeto**
```bash
gcloud config set project SEU_PROJECT_ID
gcloud auth configure-docker
```

2. **Build e Push**
```bash
docker build -t gcr.io/SEU_PROJECT_ID/vale-refeicao-ia .
docker push gcr.io/SEU_PROJECT_ID/vale-refeicao-ia
```

3. **Deploy**
```bash
gcloud run deploy vale-refeicao-ia \
  --image gcr.io/SEU_PROJECT_ID/vale-refeicao-ia \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=sk-..." \
  --memory 2Gi
```

### AWS Elastic Beanstalk

1. **Instalar EB CLI**
```bash
pip install awsebcli
```

2. **Configurar aplicação**
```bash
eb init -p python-3.11 vale-refeicao-ia
eb create vale-refeicao-env
```

3. **Configurar variáveis**
```bash
eb setenv OPENAI_API_KEY=sk-...
eb setenv DATABASE_URL=postgresql://...
```

4. **Deploy**
```bash
eb deploy
```

## 🔧 Configurações de Produção

### 1. Banco de Dados

Para produção, use serviços gerenciados:
- **AWS**: RDS PostgreSQL
- **GCP**: Cloud SQL
- **Azure**: Database for PostgreSQL
- **Heroku**: Heroku Postgres

### 2. Armazenamento de Arquivos

Configure buckets para uploads/exports:
- **AWS**: S3
- **GCP**: Cloud Storage
- **Azure**: Blob Storage

### 3. Segurança

```python
# src/config/settings.py - adicione validações
import secrets

class Settings(BaseSettings):
    # ...
    
    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if not v or not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key')
        return v
    
    # Gerar secret key se não existir
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32)
    )
```

### 4. Monitoramento

Configure logging e monitoramento:

```python
# src/utils/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Arquivo rotativo
    handler = RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

### 5. CI/CD com GitHub Actions

`.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "vale-refeicao-ia"
        heroku_email: "seu-email@example.com"
```

## 📊 Escalabilidade

### 1. Cache Redis

Para melhor performance, adicione Redis:

```python
# src/utils/cache.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(os.getenv('REDIS_URL'))

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expiration,
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator
```

### 2. Workers Assíncronos

Para processamento em background:

```python
# src/workers/celery_app.py
from celery import Celery

celery_app = Celery(
    'vale_refeicao',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL')
)

@celery_app.task
def process_large_file(file_path):
    # Processamento assíncrono
    pass
```

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de memória no Streamlit**
   - Aumente o limite: `--server.maxUploadSize 200`
   - Use processamento em chunks para arquivos grandes

2. **Timeout em cloud providers**
   - Configure timeouts maiores
   - Use processamento assíncrono

3. **Erro de conexão com PostgreSQL**
   - Verifique SSL: adicione `?sslmode=require` na URL
   - Configure firewall/security groups

### Logs e Debug

```bash
# Heroku
heroku logs --tail

# Docker
docker logs -f container_name

# Cloud Run
gcloud logging read "resource.type=cloud_run_revision"
```

## 📞 Suporte

Para problemas de deploy:
1. Verifique os logs detalhados
2. Consulte a documentação do provedor
3. Abra uma issue no GitHub com detalhes

---

Boa sorte com o deploy! 🚀
