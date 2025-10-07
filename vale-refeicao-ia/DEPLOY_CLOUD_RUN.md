# Deploy no Google Cloud Run

## Alterações Realizadas no Dockerfile

O Dockerfile foi otimizado para funcionar corretamente no Google Cloud Run:

### Principais Correções:

1. **Removido `EXPOSE $PORT` dinâmico** - Cloud Run não interpreta variáveis de ambiente no EXPOSE em runtime
2. **Mantido apenas `EXPOSE 8501`** - Como documentação (Cloud Run ignora isso e usa sua própria variável PORT)
3. **Adicionadas variáveis de ambiente do Streamlit** - Configurações pré-definidas para evitar conflitos
4. **Permissões adequadas** - Diretórios de upload/export com permissões corretas
5. **Comando simplificado** - Removido wrapper `sh -c` desnecessário

## Comandos para Deploy

### 1. Fazer login no Google Cloud
```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

### 2. Habilitar APIs necessárias
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Build e Deploy (Opção Recomendada)
```bash
# Navegue até o diretório do projeto
cd vale-refeicao-ia

# Deploy direto (Cloud Run faz o build automaticamente)
gcloud run deploy crmia-vale-refeicao \
  --source . \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars OPENAI_API_KEY=sua_chave_aqui
```

### 4. Build Manual e Deploy (Alternativa)
```bash
# Build da imagem
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/crmia-vale-refeicao

# Deploy da imagem
gcloud run deploy crmia-vale-refeicao \
  --image gcr.io/SEU_PROJECT_ID/crmia-vale-refeicao \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars OPENAI_API_KEY=sua_chave_aqui
```

## Variáveis de Ambiente Necessárias

Configure suas variáveis de ambiente sensíveis no Cloud Run:

```bash
gcloud run services update crmia-vale-refeicao \
  --update-env-vars OPENAI_API_KEY=sk-... \
  --region southamerica-east1
```

Ou adicione no arquivo `.env` antes do build (não recomendado para produção):
- `OPENAI_API_KEY`
- Outras variáveis do seu `.env`

## Considerações Importantes

### 1. **Persistência de Dados**
Cloud Run é **stateless**, então:
- Arquivos em `uploads/`, `exports/` e `chroma_db/` são **temporários**
- Para persistência, considere:
  - Google Cloud Storage para arquivos
  - Cloud SQL ou Firestore para banco de dados
  - Cloud Memorystore para ChromaDB (ou use persistência em Cloud Storage)

### 2. **Memória e CPU**
Ajuste conforme necessário:
- Mínimo recomendado: 2Gi de memória, 1 CPU
- Para processamento pesado: 4Gi de memória, 2 CPUs
```bash
--memory 4Gi --cpu 2
```

### 3. **Timeout**
- Padrão: 300 segundos (5 minutos)
- Máximo: 3600 segundos (60 minutos)
```bash
--timeout 3600
```

### 4. **Cold Start**
Para reduzir cold starts:
```bash
--min-instances 1  # Mantém uma instância sempre ativa (gera custo)
```

### 5. **Custo**
Verifique calculadora de preços do Google Cloud Run:
- Cobrado por: tempo de execução, memória, CPU, requisições
- Primeira camada gratuita disponível

## Verificação do Deploy

Após o deploy, o Cloud Run fornecerá uma URL:
```
https://crmia-vale-refeicao-xxxxxx-xx.a.run.app
```

### Testar a aplicação:
```bash
curl https://sua-url.run.app
```

### Ver logs:
```bash
gcloud run services logs read crmia-vale-refeicao \
  --region southamerica-east1 \
  --limit 50
```

## Problemas Comuns e Soluções

### Erro: "Container failed to start"
- Verifique os logs: `gcloud run services logs read`
- Confirme que a aplicação escuta na porta definida por `$PORT`
- Verifique se todas as dependências estão no `requirements.txt`

### Erro: "Memory limit exceeded"
- Aumente a memória: `--memory 4Gi`
- Otimize o uso de memória da aplicação

### Erro: "Timeout"
- Aumente o timeout: `--timeout 600`
- Otimize operações longas

### Erro de permissões
- Execute: `chmod -R 777 uploads exports chroma_db` (já incluído no Dockerfile)

### Banco de dados SQLite não persiste
- SQLite não é recomendado para Cloud Run (storage efêmero)
- Migre para Cloud SQL (PostgreSQL) para produção

## Migração para Persistência (Opcional)

### Para Cloud Storage (arquivos):
```python
from google.cloud import storage

# Substituir salvamento local por Cloud Storage
client = storage.Client()
bucket = client.bucket('seu-bucket')
blob = bucket.blob('caminho/arquivo.csv')
blob.upload_from_filename('local/arquivo.csv')
```

### Para Cloud SQL (banco de dados):
1. Crie uma instância Cloud SQL
2. Configure a conexão no Cloud Run
3. Atualize a string de conexão no código

## Monitoramento

Acesse o console do Google Cloud:
- **Métricas**: CPU, memória, latência, requests
- **Logs**: Todos os prints e erros da aplicação
- **Alertas**: Configure notificações para falhas

## Rollback

Se houver problemas, faça rollback para versão anterior:
```bash
gcloud run services update-traffic crmia-vale-refeicao \
  --to-revisions REVISION_ANTERIOR=100 \
  --region southamerica-east1
```

## Recursos Adicionais

- [Documentação Cloud Run](https://cloud.google.com/run/docs)
- [Streamlit no Cloud Run](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker#cloud-run)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
