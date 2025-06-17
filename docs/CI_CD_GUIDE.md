# 🚀 Guia de Deploy Automático (CI/CD) para Google Cloud Run

Este guia mostra como configurar deploy automático sempre que você alterar o código.

## 📋 Opções Disponíveis

### 1. **GitHub + Cloud Build (Recomendado)**
### 2. **GitLab CI/CD**
### 3. **GitHub Actions**
### 4. **Cloud Source Repositories**

---

## 🔧 Opção 1: GitHub + Cloud Build (Mais Fácil)

### Passo 1: Conectar GitHub ao Cloud Build

```powershell
# No PowerShell, execute:
gcloud builds connections create github minha-conexao-github --region=us-central1
```

Ou via Console:
1. Acesse: https://console.cloud.google.com/cloud-build/triggers
2. Clique em "Connect Repository"
3. Selecione "GitHub" e autorize o acesso
4. Selecione seu repositório

### Passo 2: Criar Trigger de Build

```powershell
# Criar trigger para branch main/master
gcloud builds triggers create github `
  --repo-name=seu-repositorio `
  --repo-owner=seu-usuario-github `
  --branch-pattern="^main$" `
  --build-config=cloudbuild.yaml `
  --name="deploy-analise-nf"
```

### Passo 3: Configurar Permissões

```powershell
# Dar permissão ao Cloud Build para fazer deploy no Cloud Run
gcloud projects add-iam-policy-binding SEU-PROJECT-ID `
  --member="serviceAccount:SEU-PROJECT-NUMBER@cloudbuild.gserviceaccount.com" `
  --role="roles/run.admin"

gcloud iam service-accounts add-iam-policy-binding `
  SEU-PROJECT-NUMBER-compute@developer.gserviceaccount.com `
  --member="serviceAccount:SEU-PROJECT-NUMBER@cloudbuild.gserviceaccount.com" `
  --role="roles/iam.serviceAccountUser"
```

---

## 🔧 Opção 2: GitHub Actions

### Passo 1: Criar Workflow

Crie o arquivo `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_ID: SEU-PROJECT-ID
  SERVICE: analise-nf
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Google Auth
      id: auth
      uses: 'google-github-actions/auth@v1'
      with:
        credentials_json: '${{ secrets.GCP_SA_KEY }}'

    - name: Set up Cloud SDK
      uses: 'google-github-actions/setup-gcloud@v1'

    - name: Configure Docker
      run: |
        gcloud auth configure-docker

    - name: Build and Push Container
      run: |
        docker build -t gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE }}:${{ github.sha }} .
        docker push gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE }}:${{ github.sha }}

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy ${{ env.SERVICE }} \
          --image gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE }}:${{ github.sha }} \
          --platform managed \
          --region ${{ env.REGION }} \
          --allow-unauthenticated \
          --memory 2Gi \
          --cpu 2 \
          --timeout 3600
```

### Passo 2: Configurar Service Account

```powershell
# Criar service account para GitHub Actions
gcloud iam service-accounts create github-actions `
  --display-name="GitHub Actions Deploy"

# Dar permissões necessárias
gcloud projects add-iam-policy-binding SEU-PROJECT-ID `
  --member="serviceAccount:github-actions@SEU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding SEU-PROJECT-ID `
  --member="serviceAccount:github-actions@SEU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding SEU-PROJECT-ID `
  --member="serviceAccount:github-actions@SEU-PROJECT-ID.iam.gserviceaccount.com" `
  --role="roles/iam.serviceAccountUser"

# Criar chave JSON
gcloud iam service-accounts keys create github-actions-key.json `
  --iam-account=github-actions@SEU-PROJECT-ID.iam.gserviceaccount.com
```

### Passo 3: Adicionar Secret no GitHub

1. Vá para Settings > Secrets and variables > Actions no seu repositório
2. Clique em "New repository secret"
3. Nome: `GCP_SA_KEY`
4. Valor: Conteúdo do arquivo `github-actions-key.json`

---

## 🔧 Opção 3: Deploy Manual com Script

Crie um arquivo `deploy.ps1` para Windows PowerShell:

```powershell
# deploy.ps1
param(
    [string]$message = "Update deployment"
)

Write-Host "🚀 Iniciando deploy..." -ForegroundColor Green

# Commit e push das alterações
git add .
git commit -m $message
git push origin main

# Deploy para Cloud Run
Write-Host "📦 Fazendo build e deploy..." -ForegroundColor Yellow
gcloud run deploy analise-nf `
    --source . `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 3600

Write-Host "✅ Deploy concluído!" -ForegroundColor Green
```

Uso:
```powershell
.\deploy.ps1 -message "Adicionar nova funcionalidade"
```

---

## 🔧 Opção 4: Cloud Source Repositories

### Passo 1: Criar Repositório

```powershell
# Criar repositório no Cloud Source
gcloud source repos create analise-nf

# Clonar repositório existente
gcloud source repos clone analise-nf --project=SEU-PROJECT-ID
```

### Passo 2: Configurar Trigger Automático

```powershell
# Criar trigger
gcloud builds triggers create cloud-source-repositories `
  --repo=analise-nf `
  --branch-pattern="^main$" `
  --build-config=cloudbuild.yaml
```

---

## 📝 Arquivo cloudbuild.yaml Otimizado

Atualize seu `cloudbuild.yaml` para melhor performance:

```yaml
steps:
  # Build da imagem Docker
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/analise-nf:$COMMIT_SHA', '.']
    
  # Push da imagem
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/analise-nf:$COMMIT_SHA']
    
  # Deploy para Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'analise-nf'
      - '--image'
      - 'gcr.io/$PROJECT_ID/analise-nf:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--timeout'
      - '3600'
      - '--set-env-vars'
      - 'STREAMLIT_SERVER_HEADLESS=true'

# Cache de imagens para builds mais rápidos
options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

timeout: 1200s

images:
  - 'gcr.io/$PROJECT_ID/analise-nf:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/analise-nf:latest'
```

---

## 🎯 Fluxo de Trabalho Recomendado

### 1. Desenvolvimento Local
```powershell
# Testar localmente
streamlit run app.py

# Verificar alterações
git status
```

### 2. Commit e Push
```powershell
# Adicionar alterações
git add .

# Commit com mensagem descritiva
git commit -m "feat: adicionar nova funcionalidade X"

# Push para o repositório
git push origin main
```

### 3. Deploy Automático
- Se configurou CI/CD: O deploy acontece automaticamente
- Se não: Execute `gcloud run deploy analise-nf --source .`

---

## 📊 Monitoramento de Deploys

### Ver status dos builds
```powershell
# Listar últimos builds
gcloud builds list --limit=5

# Ver logs de um build específico
gcloud builds log BUILD-ID

# Acompanhar build em tempo real
gcloud builds log BUILD-ID --stream
```

### Dashboard do Cloud Build
Acesse: https://console.cloud.google.com/cloud-build/builds

---

## 🔒 Boas Práticas de Segurança

1. **Use branches protegidas**
   - Configure o branch `main` como protegido
   - Exija pull request reviews

2. **Ambientes separados**
   ```yaml
   # cloudbuild-dev.yaml para desenvolvimento
   # cloudbuild-prod.yaml para produção
   ```

3. **Secrets no Secret Manager**
   ```powershell
   # Nunca commite secrets no código
   gcloud secrets create api-key --data-file=api-key.txt
   ```

---

## 🚨 Solução de Problemas

### Build falha com "permission denied"
```powershell
# Verificar permissões do Cloud Build
gcloud projects get-iam-policy SEU-PROJECT-ID
```

### Deploy falha com "quota exceeded"
- Verifique limites em: https://console.cloud.google.com/iam-admin/quotas
- Solicite aumento se necessário

### Build muito lento
- Use cache de Docker layers
- Otimize o Dockerfile
- Use máquinas maiores no Cloud Build

---

## 📚 Links Úteis

- [Cloud Build Triggers](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)
- [GitHub Actions para GCP](https://github.com/google-github-actions)
- [Cloud Run CI/CD](https://cloud.google.com/run/docs/continuous-deployment)
- [Best Practices](https://cloud.google.com/build/docs/best-practices) 