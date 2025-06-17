# 🔧 Solução de Problemas - Cloud Run Deployment

## ❌ Erro: Container failed to start and listen on PORT=8080

### Causas Comuns e Soluções:

## 1. 🔍 Diagnosticar o Problema

### Ver logs detalhados do Cloud Run:
```bash
# Ver logs da última revisão
gcloud run services describe analise-nf --region=us-central1 --format="value(status.latestReadyRevisionName)"

# Ver logs específicos da revisão com problema
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.revision_name=analise-nf-00001-pdk" --limit=50
```

## 2. 🛠️ Soluções Rápidas

### Solução 1: Aumentar o Timeout de Inicialização
```bash
gcloud run services update analise-nf \
  --region=us-central1 \
  --timeout=600 \
  --cpu-boost
```

### Solução 2: Testar com Aplicação Simplificada
```bash
# Temporariamente, renomeie app.py
mv app.py app_original.py
mv app_simple.py app.py

# Faça o deploy
gcloud run deploy analise-nf --source . --memory 1Gi

# Se funcionar, o problema está nas dependências pesadas
```

### Solução 3: Deploy com Mais Recursos
```bash
gcloud run deploy analise-nf \
  --source . \
  --memory=4Gi \
  --cpu=4 \
  --timeout=900 \
  --min-instances=1 \
  --max-instances=10 \
  --region=us-central1
```

## 3. 📦 Otimizar Dependências

### Criar requirements_minimal.txt:
```txt
streamlit==1.29.0
pandas==2.1.4
numpy==1.26.2
```

### Testar com dependências mínimas:
```bash
# Backup do requirements original
cp requirements.txt requirements_full.txt
cp requirements_minimal.txt requirements.txt

# Deploy
gcloud run deploy analise-nf --source .
```

## 4. 🐳 Dockerfile Alternativo (Mais Leve)

Crie `Dockerfile.simple`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Apenas o essencial
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
```

## 5. 🔄 Deploy Passo a Passo

### Passo 1: Limpar builds anteriores
```bash
# Listar serviços
gcloud run services list

# Deletar serviço com problema
gcloud run services delete analise-nf --region=us-central1
```

### Passo 2: Deploy com configurações específicas
```bash
gcloud run deploy analise-nf \
  --source . \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=4Gi \
  --cpu=4 \
  --timeout=900 \
  --set-env-vars="STREAMLIT_SERVER_PORT=8080,STREAMLIT_SERVER_ADDRESS=0.0.0.0,STREAMLIT_SERVER_HEADLESS=true" \
  --min-instances=0 \
  --max-instances=10 \
  --cpu-boost
```

## 6. 🧪 Testar Localmente Primeiro

### Com Docker:
```bash
# Build
docker build -t test-app .

# Run
docker run -p 8080:8080 -e PORT=8080 test-app

# Em outro terminal, testar
curl http://localhost:8080
```

### Sem Docker:
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py --server.port=8080
```

## 7. 📊 Monitorar Deploy

### Durante o deploy:
```bash
# Em tempo real
gcloud run deploy analise-nf --source . 2>&1 | tee deploy.log

# Ver progresso do build
gcloud builds list --ongoing
```

## 8. 🚨 Se Nada Funcionar

### Opção 1: Use Cloud Run Jobs (para processamento batch)
### Opção 2: Use App Engine (mais flexível para apps complexas)
### Opção 3: Use Compute Engine com container

## 9. 📝 Checklist de Verificação

- [ ] Dockerfile especifica porta 8080?
- [ ] Streamlit está configurado para porta 8080?
- [ ] Dependências estão instalando corretamente?
- [ ] Memória suficiente (mínimo 2Gi para apps com IA)?
- [ ] Timeout suficiente (mínimo 300s)?
- [ ] Logs mostram algum erro específico?

## 10. 🆘 Comando de Emergência

Se precisar fazer deploy rápido de uma versão que funciona:
```bash
# Criar app mínima
echo 'import streamlit as st; st.write("Hello Cloud Run!")' > app_minimal.py

# Deploy mínimo
gcloud run deploy analise-nf-test \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi
```

## Links Úteis
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Container Runtime Contract](https://cloud.google.com/run/docs/container-contract) 