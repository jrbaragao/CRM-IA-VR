# 📚 Guia Completo de Deploy no Google Cloud Run

Este guia mostra como fazer deploy da aplicação no Google Cloud Run sem precisar do Docker instalado localmente.

## 📋 Pré-requisitos

1. **Conta no Google Cloud Platform**
   - Se não tem, crie em: https://cloud.google.com/
   - Novos usuários ganham $300 em créditos gratuitos

2. **Projeto no Google Cloud**
   - Crie um novo projeto ou use um existente

## 🔧 Passo 1: Instalar Google Cloud SDK

### Para Windows:

1. Baixe o instalador: https://cloud.google.com/sdk/docs/install#windows
2. Execute o instalador e siga as instruções
3. Durante a instalação, marque a opção "Run gcloud init"

### Alternativa: Use o Google Cloud Shell (Navegador)

Se preferir não instalar nada localmente:
1. Acesse: https://console.cloud.google.com/
2. Clique no ícone do terminal no topo (Cloud Shell)
3. Faça upload dos arquivos do projeto

## 🚀 Passo 2: Configuração Inicial

Abra o PowerShell e execute:

```powershell
# 1. Fazer login no Google Cloud
gcloud auth login

# 2. Listar seus projetos
gcloud projects list

# 3. Configurar o projeto (substitua YOUR-PROJECT-ID)
gcloud config set project YOUR-PROJECT-ID

# 4. Configurar a região padrão
gcloud config set run/region us-central1

# 5. Habilitar as APIs necessárias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## 🏗️ Passo 3: Deploy da Aplicação

### Opção A: Deploy Direto do Código (Mais Fácil)

O Google Cloud Build criará a imagem Docker automaticamente:

```powershell
# Navegue até a pasta do projeto
cd C:\Dados\Sites\Cursor\CRMIA

# Faça o deploy (substitua com um nome único)
gcloud run deploy analise-nf-seu-nome `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --timeout 3600 `
  --min-instances 0 `
  --max-instances 10
```

### Opção B: Usando Cloud Build (CI/CD)

Se você quiser usar o arquivo `cloudbuild.yaml`:

```powershell
# Submeter para build e deploy
gcloud builds submit --config cloudbuild.yaml
```

## 🔐 Passo 4: Configurar Variáveis de Ambiente (Opcional)

Se quiser configurar a API Key da OpenAI como variável de ambiente:

```powershell
gcloud run services update analise-nf-seu-nome `
  --update-env-vars OPENAI_API_KEY=sk-sua-chave-aqui
```

### Usando Secret Manager (Mais Seguro)

```powershell
# 1. Criar o secret
echo -n "sk-sua-chave-aqui" | gcloud secrets create openai-api-key --data-file=-

# 2. Dar permissão ao Cloud Run
gcloud secrets add-iam-policy-binding openai-api-key `
  --member=serviceAccount:YOUR-PROJECT-NUMBER-compute@developer.gserviceaccount.com `
  --role=roles/secretmanager.secretAccessor

# 3. Atualizar o serviço para usar o secret
gcloud run services update analise-nf-seu-nome `
  --update-secrets=OPENAI_API_KEY=openai-api-key:latest
```

## 📊 Passo 5: Acessar a Aplicação

Após o deploy bem-sucedido:

```powershell
# Obter a URL da aplicação
gcloud run services describe analise-nf-seu-nome --format 'value(status.url)'
```

## 🔍 Monitoramento e Logs

```powershell
# Ver logs em tempo real
gcloud run services logs tail analise-nf-seu-nome

# Ver logs das últimas 24 horas
gcloud run services logs read analise-nf-seu-nome --limit 50

# Abrir o console do Cloud Run
gcloud run services describe analise-nf-seu-nome --format export | Out-String
```

## 💰 Otimização de Custos

1. **Configurar auto-scaling mínimo para 0**:
   ```powershell
   gcloud run services update analise-nf-seu-nome --min-instances 0
   ```

2. **Configurar concorrência máxima**:
   ```powershell
   gcloud run services update analise-nf-seu-nome --concurrency 80
   ```

## 🚨 Solução de Problemas

### Erro: "Quota exceeded"
- Verifique suas cotas em: https://console.cloud.google.com/iam-admin/quotas
- Solicite aumento se necessário

### Erro: "Build failed"
- Verifique os logs do Cloud Build:
  ```powershell
  gcloud builds list --limit 5
  gcloud builds log BUILD-ID
  ```

### Aplicação lenta
- Aumente a memória/CPU:
  ```powershell
  gcloud run services update analise-nf-seu-nome --memory 4Gi --cpu 4
  ```

## 📝 Comandos Úteis

```powershell
# Listar todos os serviços Cloud Run
gcloud run services list

# Deletar um serviço
gcloud run services delete analise-nf-seu-nome

# Ver detalhes do serviço
gcloud run services describe analise-nf-seu-nome

# Atualizar configurações
gcloud run services update analise-nf-seu-nome --memory 4Gi

# Ver revisões
gcloud run revisions list --service analise-nf-seu-nome
```

## 🎯 Próximos Passos

1. Configure um domínio personalizado
2. Configure CI/CD com GitHub Actions
3. Adicione monitoramento com Google Cloud Monitoring
4. Configure alertas para erros

## 📚 Links Úteis

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Preços Cloud Run](https://cloud.google.com/run/pricing)
- [Melhores Práticas](https://cloud.google.com/run/docs/tips)
- [Streamlit no Cloud Run](https://docs.streamlit.io/knowledge-base/tutorials/deploy/google-cloud-run) 