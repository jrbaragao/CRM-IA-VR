# 🔑 Configurar Service Account Key para Signed URL

## 🎯 Objetivo

Configurar uma chave de conta de serviço (Service Account Key JSON) como variável de ambiente secreta no Cloud Run para permitir geração de Signed URLs.

Esta é a **solução mais simples e confiável** para o erro 413 em uploads grandes.

---

## 📌 Variáveis de Ambiente Necessárias

Para o sistema funcionar completamente, você precisa ter estas variáveis configuradas no Cloud Run:

### Variáveis Obrigatórias:
1. **`OPENAI_API_KEY`** → Token da API do LLM (OpenAI)
   - Exemplo: `sk-proj-xxxxxxxxxxxxx`
   - Configure via: Secret Manager ou variável de ambiente

2. **`GCS_SERVICE_ACCOUNT_KEY_JSON`** → Chave JSON para Signed URLs (este guia)
   - Exemplo: `{"type":"service_account","project_id":"...","private_key":"..."}`
   - Configure via: Secret Manager (recomendado)

### Variáveis Opcionais:
- `OPENAI_MODEL` → Modelo a usar (padrão: `gpt-4-turbo-preview`)
- `AGENT_TEMPERATURE` → Criatividade do agente (padrão: `0.3`)
- `MAX_FILE_SIZE_MB` → Tamanho máximo de arquivo (padrão: `500`)
- `DEBUG` → Modo debug (padrão: `False`)

⚠️ **Este guia adiciona apenas `GCS_SERVICE_ACCOUNT_KEY_JSON` - as outras devem estar já configuradas!**

---

## 🎨 Guia Rápido Visual (Console Web)

Se você está fazendo pelo painel do Google Cloud, siga esta sequência:

### 1️⃣ **Secret Manager** (criar secret)
```
https://console.cloud.google.com/security/secret-manager
↓
[+ CREATE SECRET]
↓
Name: gcs-service-account-key
Secret value: [Upload arquivo key.json]
↓
[CREATE SECRET]
```

### 2️⃣ **Secret Manager** (dar permissão)
```
Clique na secret que você criou
↓
Aba [PERMISSIONS]
↓
[+ GRANT ACCESS]
↓
Principal: xxxxx-compute@developer.gserviceaccount.com
Role: Secret Manager Secret Accessor
↓
[SAVE]
```

### 3️⃣ **Cloud Run** (adicionar secret)
```
https://console.cloud.google.com/run
↓
Clique em: crmia-agente-autonomo
↓
[EDIT & DEPLOY NEW REVISION]
↓
Container → Variables & Secrets
↓
Aba [SECRETS] → [+ REFERENCE A SECRET]
↓
Secret: gcs-service-account-key
Method: Exposed as environment variable
Variable: GCS_SERVICE_ACCOUNT_KEY_JSON
Version: latest
↓
[DONE]
↓
⚠️ Verificar aba [VARIABLES] → OPENAI_API_KEY ainda está lá?
↓
[DEPLOY] (aguardar 2-3 min)
```

### ✅ Pronto!
Acesse a URL do Cloud Run → Upload de Dados → Deve aparecer "✅ Upload direto habilitado!"

---

## 🔧 Configurar OPENAI_API_KEY (se ainda não tiver)

Se você ainda não configurou a `OPENAI_API_KEY`, faça isso primeiro:

### Opção 1: Via Secret Manager (Recomendado)

```bash
export PROJECT_ID="awesome-carver-463213-r0"

# 1. Criar secret com seu token da OpenAI
gcloud secrets create openai-api-key \
  --data-file=- <<EOF
sk-proj-seu-token-aqui
EOF

# 2. Dar acesso ao Cloud Run
export CLOUD_RUN_SA=$(gcloud run services describe crmia-agente-autonomo \
  --region=southamerica-east1 \
  --format="value(spec.template.spec.serviceAccountName)" \
  --project=$PROJECT_ID)

gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:$CLOUD_RUN_SA" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

# 3. Montar no Cloud Run
gcloud run services update crmia-agente-autonomo \
  --region=southamerica-east1 \
  --update-secrets=OPENAI_API_KEY=openai-api-key:latest \
  --project=$PROJECT_ID
```

### Opção 2: Via Variável de Ambiente

```bash
gcloud run services update crmia-agente-autonomo \
  --region=southamerica-east1 \
  --update-env-vars="OPENAI_API_KEY=sk-proj-seu-token-aqui" \
  --project=awesome-carver-463213-r0
```

---

## 📋 Passo a Passo (GCS Service Account Key)

Esta seção configura especificamente a `GCS_SERVICE_ACCOUNT_KEY_JSON` para uploads grandes.

### **1. Criar Service Account (se não existir)**

#### Via Console Web:
1. Acesse [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Clique **"+ Create Service Account"**
3. Preencha:
   - **Name**: `gcs-upload-signer`
   - **Description**: `Service Account para gerar Signed URLs no Cloud Run`
4. Clique **"Create and Continue"**
5. Em **"Grant this service account access to project"**:
   - Adicione papel: **Storage Admin** (`roles/storage.admin`)
6. Clique **"Continue"** → **"Done"**

#### Via gcloud CLI:
```bash
export PROJECT_ID="awesome-carver-463213-r0"

# Criar service account
gcloud iam service-accounts create gcs-upload-signer \
  --display-name="GCS Upload Signer" \
  --description="Service Account para gerar Signed URLs" \
  --project=$PROJECT_ID

# Conceder papel Storage Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

---

### **2. Criar e Baixar a Chave JSON**

#### Via Console Web:
1. Acesse [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Clique na service account `gcs-upload-signer`
3. Aba **"Keys"** (Chaves)
4. Clique **"Add Key"** → **"Create new key"**
5. Escolha **JSON**
6. Clique **"Create"**
7. A chave será baixada automaticamente (ex: `awesome-carver-463213-r0-abc123.json`)

⚠️ **IMPORTANTE**: Guarde este arquivo com segurança! Ele não pode ser recuperado depois.

#### Via gcloud CLI:
```bash
export PROJECT_ID="awesome-carver-463213-r0"
export SA_EMAIL="gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com"

# Criar e baixar chave
gcloud iam service-accounts keys create key.json \
  --iam-account=$SA_EMAIL \
  --project=$PROJECT_ID

# Exibir conteúdo (para copiar)
cat key.json
```

---

### **3. Configurar como Secret no Cloud Run**

⚠️ **IMPORTANTE**: Esta etapa **adiciona** a nova secret sem remover as variáveis existentes (como `OPENAI_API_KEY`).

---

**📍 Resumo do que você vai fazer:**

```
Etapa 3.1: Secret Manager → Criar secret "gcs-service-account-key" com o arquivo key.json
                ↓
Etapa 3.2: Secret Manager → Dar permissão para o Cloud Run acessar
                ↓
Etapa 3.3: Cloud Run → Adicionar secret como variável GCS_SERVICE_ACCOUNT_KEY_JSON
                ↓
            ✅ Deploy!
```

---

#### Opção A: Via Console Web (Mais Fácil) 🖱️

##### **3.1. Criar Secret no Secret Manager**

1. **Acesse o Secret Manager:**
   - Vá para: https://console.cloud.google.com/security/secret-manager
   - Ou busque "Secret Manager" na barra de pesquisa do Cloud Console

2. **Criar novo Secret:**
   - Clique no botão **"+ CREATE SECRET"** (topo da página)
   
3. **Configurar o Secret:**
   - **Name**: `gcs-service-account-key`
   - **Secret value**: 
     - Clique em **"Browse"** e selecione o arquivo `key.json` que você baixou
     - OU copie e cole o conteúdo completo do arquivo JSON
   - **Regions**: Deixe "Automatic" (replicação automática)
   - Clique **"CREATE SECRET"**

##### **3.2. Dar Permissão para o Cloud Run acessar o Secret**

1. **Na tela do Secret que você acabou de criar:**
   - Clique na aba **"PERMISSIONS"**
   - Clique **"+ GRANT ACCESS"**

2. **Adicionar permissão:**
   - **New principals**: Digite o email da service account do Cloud Run
     - Formato: `123456789-compute@developer.gserviceaccount.com`
     - Para descobrir qual é, veja na próxima etapa 3.3
   - **Role**: Selecione `Secret Manager Secret Accessor`
   - Clique **"SAVE"**

##### **3.3. Adicionar Secret ao Cloud Run**

1. **Acesse seu serviço no Cloud Run:**
   - Vá para: https://console.cloud.google.com/run
   - Clique no serviço **`crmia-agente-autonomo`**

2. **Editar e Deploy nova revisão:**
   - Clique no botão **"EDIT & DEPLOY NEW REVISION"** (topo da página)

3. **Navegar até as Variáveis:**
   - Role até a seção **"Container, Networking, Security"**
   - Clique em **"Variables & Secrets"** para expandir

4. **Adicionar a Secret:**
   - Vá para a aba **"SECRETS"**
   - Clique **"+ REFERENCE A SECRET"**
   
5. **Configurar a Secret:**
   - **Secret**: Selecione `gcs-service-account-key` (que você criou)
   - **Reference method**: Selecione "Exposed as environment variable"
   - **Environment variable name**: Digite `GCS_SERVICE_ACCOUNT_KEY_JSON`
   - **Version**: Selecione `latest` (ou `1`)
   - Clique **"DONE"**

6. **Verificar variáveis existentes:**
   - ⚠️ **IMPORTANTE**: Role para cima até a aba **"VARIABLES"**
   - Confirme que você ainda vê **`OPENAI_API_KEY`** e outras variáveis existentes
   - Se não estiver, adicione novamente antes de fazer deploy!

7. **Deploy:**
   - Role até o fim e clique **"DEPLOY"**
   - Aguarde 2-3 minutos enquanto o Cloud Run faz o deploy

##### **3.4. Descobrir qual é a Service Account do Cloud Run** (se precisar)

Se você não sabe qual é o email da service account:

1. No Cloud Run, clique no serviço **`crmia-agente-autonomo`**
2. Role até a seção **"Service details"** (detalhes do serviço)
3. Procure por **"Service account"**
4. Copie o email (formato: `xxxxx-compute@developer.gserviceaccount.com`)

---

#### Opção B: Via Linha de Comando (gcloud CLI) 💻

Se você preferir usar o terminal:

1. **Criar Secret:**
   ```bash
   # Criar secret a partir do arquivo
   gcloud secrets create gcs-service-account-key \
     --data-file=key.json \
     --replication-policy="automatic" \
     --project=$PROJECT_ID
   ```

2. **Conceder acesso à service account do Cloud Run:**
   ```bash
   export CLOUD_RUN_SA="123456789-compute@developer.gserviceaccount.com"
   
   gcloud secrets add-iam-policy-binding gcs-service-account-key \
     --member="serviceAccount:$CLOUD_RUN_SA" \
     --role="roles/secretmanager.secretAccessor" \
     --project=$PROJECT_ID
   ```

3. **Montar secret no Cloud Run:**
   ```bash
   # Usa --update-secrets para adicionar/atualizar apenas esta secret
   # Isso NÃO remove variáveis de ambiente existentes como OPENAI_API_KEY
   gcloud run services update crmia-agente-autonomo \
     --region=southamerica-east1 \
     --update-secrets=GCS_SERVICE_ACCOUNT_KEY_JSON=gcs-service-account-key:latest \
     --project=$PROJECT_ID
   ```

4. **Verificar que todas as variáveis estão configuradas:**
   ```bash
   # Listar variáveis de ambiente
   gcloud run services describe crmia-agente-autonomo \
     --region=southamerica-east1 \
     --format="yaml(spec.template.spec.containers[0].env)" \
     --project=$PROJECT_ID
   
   # Listar secrets montados
   gcloud run services describe crmia-agente-autonomo \
     --region=southamerica-east1 \
     --format="yaml(spec.template.spec.containers[0].env)" \
     --project=$PROJECT_ID | grep -A 2 "secretKeyRef"
   ```
   
   ✅ **Você deve ver:**
   - `OPENAI_API_KEY` (secret ou env var)
   - `GCS_SERVICE_ACCOUNT_KEY_JSON` (secret)
   - Outras variáveis que já tinha configurado

---

#### Opção C: Via Variável de Ambiente (NÃO recomendado) ⚠️

⚠️ **Não recomendado para produção** (chave fica visível no console)

```bash
# Converter JSON para string única (remover quebras de linha)
export KEY_JSON=$(cat key.json | jq -c .)

# Definir como variável de ambiente
# IMPORTANTE: Use --update-env-vars (não --set-env-vars) para manter as existentes
gcloud run services update crmia-agente-autonomo \
  --region=southamerica-east1 \
  --update-env-vars="GCS_SERVICE_ACCOUNT_KEY_JSON=$KEY_JSON" \
  --project=$PROJECT_ID
```

**Diferença importante:**
- `--set-env-vars` → **substitui todas** as variáveis (❌ remove OPENAI_API_KEY)
- `--update-env-vars` → **adiciona/atualiza** apenas a especificada (✅ mantém OPENAI_API_KEY)

---

#### ✅ Checklist Final - Configuração da Secret

Após concluir o Passo 3, verifique se você tem:

**No Secret Manager:**
- [ ] Secret `gcs-service-account-key` criado com o conteúdo do `key.json`
- [ ] Permissão concedida para a service account do Cloud Run (role: Secret Manager Secret Accessor)

**No Cloud Run (aba Variables & Secrets):**
- [ ] **SECRETS tab**: `GCS_SERVICE_ACCOUNT_KEY_JSON` apontando para `gcs-service-account-key:latest`
- [ ] **VARIABLES tab**: `OPENAI_API_KEY` ainda está lá (não foi removida)
- [ ] Deploy realizado com sucesso

**Como verificar pelo Console:**
1. Acesse: https://console.cloud.google.com/run/detail/southamerica-east1/crmia-agente-autonomo/revisions
2. Clique na revisão mais recente (última deployada)
3. Role até "Variables & Secrets"
4. Você deve ver AMBAS: `OPENAI_API_KEY` + `GCS_SERVICE_ACCOUNT_KEY_JSON`

---

### **4. Atualizar Código (já feito!)**

O código já está preparado para usar a variável `GCS_SERVICE_ACCOUNT_KEY_JSON`:

```python
# Em cloud_storage.py
if self.service_account_key_json:
    key_data = json.loads(self.service_account_key_json)
    credentials = service_account.Credentials.from_service_account_info(key_data)
    self.client = storage.Client(project=self.project_id, credentials=credentials)
```

---

### **5. Deploy e Teste**

```bash
# Deploy (se usou Secret Manager, não precisa passar variáveis)
gcloud run deploy crmia-agente-autonomo \
  --source . \
  --region southamerica-east1 \
  --project=$PROJECT_ID

# Verificar variáveis
gcloud run services describe crmia-agente-autonomo \
  --region=southamerica-east1 \
  --format="value(spec.template.spec.containers[0].env)"
```

**Teste:**
1. Acesse a URL do Cloud Run
2. Vá em "📤 Upload de Dados"
3. Role até "☁️ Upload Direto ao Google Cloud Storage"
4. Deve aparecer: **"✅ Upload direto habilitado!"**
5. Teste com arquivo >30MB

---

## 🔧 Troubleshooting - Problemas Comuns pelo Console

### Problema 1: "Não vejo a secret `gcs-service-account-key` na lista"
**Solução:**
- Verifique se você está no projeto correto (topo do console)
- Certifique-se de ter criado a secret no Secret Manager primeiro (Passo 3.1)
- Recarregue a página do Cloud Run

### Problema 2: "Erro de permissão ao tentar acessar a secret"
**Solução:**
- Você esqueceu o Passo 3.2 (dar permissão)
- Vá para Secret Manager → `gcs-service-account-key` → aba PERMISSIONS
- Adicione a service account do Cloud Run com role `Secret Manager Secret Accessor`

### Problema 3: "Deploy falha com erro de secret"
**Possíveis causas:**
- A secret não existe ou foi deletada
- Você digitou o nome errado da variável (deve ser `GCS_SERVICE_ACCOUNT_KEY_JSON` exato)
- A service account do Cloud Run não tem permissão

### Problema 4: "Minha `OPENAI_API_KEY` sumiu após o deploy"
**O que aconteceu:**
- Você provavelmente usou `--set-env-vars` no CLI ao invés de `--update-env-vars`
- Ou no console, você apagou sem querer

**Solução:**
1. Vá em Cloud Run → `crmia-agente-autonomo` → EDIT & DEPLOY NEW REVISION
2. Em Variables & Secrets → VARIABLES
3. Clique **"+ ADD VARIABLE"**
4. Nome: `OPENAI_API_KEY`, Valor: `sk-proj-seu-token`
5. Deploy novamente

### Problema 5: "Upload ainda dá erro 413"
**Verifique:**
1. A secret está montada? (verificar no checklist acima)
2. O deploy foi feito após adicionar a secret?
3. Na página de Upload, aparece "✅ Upload direto habilitado!"?

**Se não aparecer:**
- Veja os logs: Cloud Run → `crmia-agente-autonomo` → LOGS
- Procure por erros relacionados a `GCS_SERVICE_ACCOUNT_KEY_JSON`

---

## 🔐 Segurança

### ✅ **Boas Práticas:**

1. **Use Secret Manager** (não variável de ambiente)
2. **Rotacione chaves** periodicamente
3. **Limite permissões** (use `Storage Object Creator` em vez de `Storage Admin`)
4. **Delete chaves antigas** após rotação

### 🗑️ **Deletar chave antiga:**

```bash
# Listar chaves
gcloud iam service-accounts keys list \
  --iam-account=gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com

# Deletar chave específica
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com
```

---

## 📊 Comparação: IAM API vs Service Account Key

| Método | Segurança | Complexidade | Funciona? |
|--------|-----------|--------------|-----------|
| **IAM Credentials API** | ⭐⭐⭐⭐⭐ Excelente | 🔴 Alta | ❌ Scope insuficiente |
| **Service Account Key** | ⭐⭐⭐ Boa | 🟢 Baixa | ✅ Funciona |

**Recomendação**: Use Service Account Key com Secret Manager.

---

## 🚀 Comando Completo (Copy & Paste)

⚠️ **Antes de executar**: Certifique-se que você já tem `OPENAI_API_KEY` configurado no Cloud Run!

Para verificar:
```bash
gcloud run services describe crmia-agente-autonomo \
  --region=southamerica-east1 \
  --format="get(spec.template.spec.containers[0].env)" \
  --project=awesome-carver-463213-r0 | grep OPENAI_API_KEY
```

Se não aparecer nada, configure primeiro o `OPENAI_API_KEY` antes de prosseguir.

### Script Completo:

```bash
# Definir variáveis
export PROJECT_ID="awesome-carver-463213-r0"
export REGION="southamerica-east1"
export SERVICE_NAME="crmia-agente-autonomo"

# 1. Criar Service Account
gcloud iam service-accounts create gcs-upload-signer \
  --display-name="GCS Upload Signer" \
  --project=$PROJECT_ID

# 2. Conceder permissão no bucket
gsutil iam ch \
  serviceAccount:gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectCreator \
  gs://crmia-uploads-files

# 3. Criar chave
gcloud iam service-accounts keys create key.json \
  --iam-account=gcs-upload-signer@${PROJECT_ID}.iam.gserviceaccount.com \
  --project=$PROJECT_ID

# 4. Criar secret
gcloud secrets create gcs-service-account-key \
  --data-file=key.json \
  --replication-policy="automatic" \
  --project=$PROJECT_ID

# 5. Conceder acesso ao secret
export CLOUD_RUN_SA=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format="value(spec.template.spec.serviceAccountName)" \
  --project=$PROJECT_ID)

gcloud secrets add-iam-policy-binding gcs-service-account-key \
  --member="serviceAccount:$CLOUD_RUN_SA" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

# 6. Montar secret no Cloud Run
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --update-secrets=GCS_SERVICE_ACCOUNT_KEY_JSON=gcs-service-account-key:latest \
  --project=$PROJECT_ID

# 7. Deletar arquivo local da chave (segurança)
rm key.json

echo "✅ Configuração concluída! Faça deploy e teste."
```

---

**Tempo estimado**: 5-10 minutos

**Última atualização**: 08/10/2025

