# 🔐 Configurar IAM para Signed URL no Cloud Run

## 📋 Pré-requisitos

- Projeto Google Cloud com Cloud Run ativo
- Permissão de administrador IAM no projeto
- Service do Cloud Run já deployado

## 🎯 Objetivo

Permitir que o Cloud Run gere Signed URLs para upload direto ao Google Cloud Storage, sem precisar de arquivo de chave privada (Service Account Key JSON).

---

## 📝 Passo a Passo Completo

### **1. Identificar a Service Account do Cloud Run**

#### Opção A: Via Console Web
1. Acesse [Cloud Run Console](https://console.cloud.google.com/run)
2. Clique no seu serviço (ex: `crmia-agente-autonomo`)
3. Aba **"Revisar"** ou **"Revisions"**
4. Procure por **"Service account"**
5. Copie o email (geralmente algo como):
   ```
   PROJECT_NUMBER-compute@developer.gserviceaccount.com
   ```
   ou
   ```
   service-PROJECT_NUMBER@serverless-robot-prod.iam.gserviceaccount.com
   ```

#### Opção B: Via gcloud CLI
```bash
# Liste todos os serviços Cloud Run
gcloud run services list

# Descreva o serviço específico
gcloud run services describe crmia-agente-autonomo \
  --region=southamerica-east1 \
  --format="value(spec.template.spec.serviceAccountName)"
```

---

### **2. Habilitar a API IAM Service Account Credentials**

#### Via Console Web:
1. Acesse [APIs & Services](https://console.cloud.google.com/apis/library)
2. Busque: **"IAM Service Account Credentials API"**
3. Clique em **"Habilitar"** (Enable)

#### Via gcloud CLI:
```bash
gcloud services enable iamcredentials.googleapis.com
```

---

### **3. Conceder Papel `Service Account Token Creator`**

A conta de serviço do Cloud Run precisa ter permissão para **assinar tokens como ela mesma**.

#### Via Console Web:

1. Acesse [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)

2. Localize a service account do Cloud Run (do passo 1)

3. Clique nos **3 pontinhos** (⋮) → **"Manage permissions"**

4. Clique **"Grant Access"** (Conceder acesso)

5. Em **"New principals"** (Novos membros):
   ```
   Cole o email da própria service account
   Exemplo: 123456789-compute@developer.gserviceaccount.com
   ```

6. Em **"Select a role"** (Selecionar função):
   ```
   Service Accounts → Service Account Token Creator
   ```
   
   Ou busque por: `roles/iam.serviceAccountTokenCreator`

7. Clique **"Save"**

#### Via gcloud CLI:

```bash
# Substitua pelos seus valores
export PROJECT_ID="awesome-carver-463213-r0"
export SERVICE_ACCOUNT="123456789-compute@developer.gserviceaccount.com"

# Conceder o papel
gcloud iam service-accounts add-iam-policy-binding \
  $SERVICE_ACCOUNT \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project=$PROJECT_ID
```

---

### **4. Conceder Permissões no Bucket GCS**

A service account também precisa de permissão para criar objetos no bucket.

#### Via Console Web:

1. Acesse [Cloud Storage → Buckets](https://console.cloud.google.com/storage/browser)

2. Clique no bucket (ex: `crmia-uploads-files`)

3. Aba **"Permissions"** (Permissões)

4. Clique **"Grant Access"**

5. Em **"New principals"**:
   ```
   Cole o email da service account
   ```

6. Em **"Select a role"**:
   ```
   Storage Object Creator
   ```
   Ou: `roles/storage.objectCreator`

7. Clique **"Save"**

#### Via gcloud CLI:

```bash
export BUCKET_NAME="crmia-uploads-files"
export SERVICE_ACCOUNT="123456789-compute@developer.gserviceaccount.com"

# Conceder permissão no bucket
gsutil iam ch \
  serviceAccount:$SERVICE_ACCOUNT:roles/storage.objectCreator \
  gs://$BUCKET_NAME
```

---

### **5. Verificar Configuração**

#### Teste via gcloud CLI:

```bash
# Verificar se a service account tem o papel Token Creator
gcloud iam service-accounts get-iam-policy $SERVICE_ACCOUNT

# Deve aparecer algo como:
# bindings:
# - members:
#   - serviceAccount:123456789-compute@developer.gserviceaccount.com
#   role: roles/iam.serviceAccountTokenCreator
```

#### Teste no Cloud Run:

1. Faça um novo deploy (para garantir que as permissões foram aplicadas):
   ```bash
   gcloud run deploy crmia-agente-autonomo \
     --source . \
     --region southamerica-east1
   ```

2. Acesse a página de Upload no app

3. Verifique se aparece:
   ```
   ✅ Upload direto habilitado! Destino: gs://...
   ```

---

## 🔍 Troubleshooting

### ❌ Erro: "you need a private key to sign credentials"

**Causa**: IAM Service Account Credentials API não habilitada OU papel Token Creator não concedido.

**Solução**:
1. Confirme que a API está habilitada (passo 2)
2. Confirme que o papel foi concedido (passo 3)
3. Aguarde 1-2 minutos para propagação
4. Faça redeploy do Cloud Run

### ❌ Erro: "403 Forbidden" ao gerar Signed URL

**Causa**: Service account sem permissão no bucket.

**Solução**:
- Adicione `Storage Object Creator` no bucket (passo 4)

### ❌ Signed URL ainda não funciona

**Causa**: Versão antiga da biblioteca `google-cloud-storage`.

**Solução**:
```bash
# Atualize no requirements.txt
google-cloud-storage>=2.10.0

# Ou instale manualmente
pip install --upgrade google-cloud-storage
```

---

## 📊 Resumo dos Papéis Necessários

| Recurso | Service Account | Papel | Motivo |
|---------|----------------|-------|--------|
| **Própria SA** | Ela mesma | `Service Account Token Creator` | Assinar URLs via IAM |
| **Bucket GCS** | SA do Cloud Run | `Storage Object Creator` | Criar objetos no bucket |
| **Projeto** | - | `IAM Credentials API` | Permitir assinatura via IAM |

---

## ✅ Validação Final

Após configurar tudo, teste:

1. Acesse a página de Upload
2. Deve aparecer: **"✅ Upload direto habilitado!"**
3. Selecione um arquivo >30MB
4. Clique **"🚀 Enviar ao GCS"**
5. Deve mostrar: **"✅ Upload concluído!"**
6. Clique **"🔄 Verificar e processar arquivo do GCS"**
7. Arquivo deve ser processado normalmente

---

## 📚 Referências

- [Cloud Run Service Identity](https://cloud.google.com/run/docs/securing/service-identity)
- [IAM Service Account Credentials API](https://cloud.google.com/iam/docs/reference/credentials/rest)
- [Signed URLs for GCS](https://cloud.google.com/storage/docs/access-control/signed-urls)
- [Service Account Token Creator](https://cloud.google.com/iam/docs/service-account-permissions)

---

**Última atualização**: 08/10/2025

