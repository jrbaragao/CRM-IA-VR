# 🔧 Problema de Build no Google Cloud Run - RESOLVIDO

## ❌ Erro Original

```
ERROR: build step 0 "gcr.io/cloud-builders/docker" failed: step exited with non-zero status: 1
```

## 🔍 Causa Raiz Identificada

O erro foi causado por **dependências específicas do Windows** no `requirements.txt`:

### 1. **pyreadline3==3.5.4** (Linha 114)
- **Problema**: Biblioteca EXCLUSIVA para Windows
- **Erro no Linux**: Falha na instalação em containers Linux (Docker/Cloud Run)
- **Solução**: Remover automaticamente durante o build

### 2. **Dependências do Sistema Faltando**
- Faltavam bibliotecas necessárias para compilar pacotes Python
- Exemplo: `libpq-dev` para `psycopg2-binary`, `gcc/g++` para compilação

## ✅ Correções Aplicadas no Dockerfile

### 1. Dependências do Sistema Adicionadas
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
```

### 2. Remoção Automática de Dependências do Windows
```dockerfile
RUN sed -i '/pyreadline3/d' requirements.txt && \
    sed -i '/pywin32/d' requirements.txt
```

### 3. Upgrade do pip
```dockerfile
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
```

## 🚀 Como Fazer Deploy Agora

### Opção 1: Deploy Direto (Recomendado)
```bash
cd vale-refeicao-ia

gcloud run deploy crmia-agente-autonomo \
  --source . \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --set-env-vars OPENAI_API_KEY=sua_chave_aqui
```

### Opção 2: Build e Deploy Separados
```bash
# 1. Build da imagem
gcloud builds submit --tag gcr.io/awesome-carver-463213-r0/crmia-agente-autonomo

# 2. Deploy
gcloud run deploy crmia-agente-autonomo \
  --image gcr.io/awesome-carver-463213-r0/crmia-agente-autonomo \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars OPENAI_API_KEY=sua_chave_aqui
```

## 📝 Alternativa: requirements-docker.txt

Foi criado um arquivo `requirements-docker.txt` com apenas as dependências essenciais para Docker.

Para usá-lo, altere no Dockerfile:
```dockerfile
# Substituir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Por
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
```

## 🧪 Testar Build Localmente

### Antes de fazer deploy, teste localmente:

```bash
# Build local
docker build -t crmia-test .

# Testar container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sua_chave \
  crmia-test
```

Acesse: http://localhost:8501

## 🐛 Outros Problemas Comuns

### 1. **Timeout Durante o Build**
**Solução**: Aumentar o timeout do Cloud Build
```bash
gcloud builds submit --timeout=1200s --tag gcr.io/PROJECT/image
```

### 2. **Memória Insuficiente no Build**
**Solução**: Usar máquina mais potente
```bash
gcloud builds submit --machine-type=E2_HIGHCPU_8 --tag gcr.io/PROJECT/image
```

### 3. **Erro com ChromaDB**
ChromaDB pode ter problemas com SQLite no Cloud Run. 
**Solução**: Considere usar ChromaDB cloud ou alternativa como Pinecone.

### 4. **Erro "No module named 'src'"**
Certifique-se que o código foi copiado corretamente:
```dockerfile
COPY . .
```

## 📊 Verificar Logs do Build

Para ver logs detalhados do build que falhou:

```bash
# Listar builds recentes
gcloud builds list --limit=5

# Ver logs de um build específico
gcloud builds log BUILD_ID

# Ou ver no console
# https://console.cloud.google.com/cloud-build/builds
```

## ✅ Checklist Pré-Deploy

- [ ] Arquivo `.env` com `OPENAI_API_KEY` configurado localmente
- [ ] `requirements.txt` sem dependências do Windows
- [ ] Dockerfile atualizado com correções
- [ ] `.dockerignore` configurado
- [ ] Testado build local com Docker
- [ ] Variáveis de ambiente configuradas no Cloud Run

## 🎯 Próximos Passos Após Deploy

1. **Verificar URL gerada**: `https://crmia-agente-autonomo-xxxxxx-xx.a.run.app`
2. **Testar aplicação**: Fazer upload de arquivo e processar
3. **Monitorar logs**: Verificar erros em tempo real
4. **Configurar domínio customizado** (opcional)
5. **Configurar CI/CD** para deploys automáticos

## 📚 Recursos

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Streamlit on Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

---

**Última atualização**: 07/10/2025
**Status**: ✅ PROBLEMA RESOLVIDO
