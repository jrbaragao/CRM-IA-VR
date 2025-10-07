# 🚀 Deploy Rápido - Google Cloud Run

## ⚡ Comandos Prontos para Usar

### 1. Configuração Inicial (primeira vez apenas)

```bash
# Login no Google Cloud
gcloud auth login

# Configurar projeto
gcloud config set project awesome-carver-463213-r0

# Habilitar APIs necessárias
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### 2. Deploy da Aplicação

```bash
# Navegar até o diretório
cd vale-refeicao-ia

# Deploy direto (Cloud Run faz o build automaticamente)
gcloud run deploy crmia-agente-autonomo \
  --source . \
  --platform managed \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --set-env-vars OPENAI_API_KEY=sk-sua-chave-aqui
```

### 3. Atualizar Variáveis de Ambiente (após deploy)

```bash
# Atualizar a chave da OpenAI
gcloud run services update crmia-agente-autonomo \
  --update-env-vars OPENAI_API_KEY=sk-nova-chave \
  --region southamerica-east1
```

### 4. Ver Logs em Tempo Real

```bash
# Últimas 50 linhas
gcloud run services logs read crmia-agente-autonomo \
  --region southamerica-east1 \
  --limit 50

# Seguir logs em tempo real
gcloud run services logs tail crmia-agente-autonomo \
  --region southamerica-east1
```

### 5. Comandos Úteis

```bash
# Listar serviços
gcloud run services list --region southamerica-east1

# Ver detalhes do serviço
gcloud run services describe crmia-agente-autonomo \
  --region southamerica-east1

# Ver URL do serviço
gcloud run services describe crmia-agente-autonomo \
  --region southamerica-east1 \
  --format='value(status.url)'

# Deletar serviço (cuidado!)
gcloud run services delete crmia-agente-autonomo \
  --region southamerica-east1
```

## 🧪 Teste Local Antes do Deploy

### Windows
```powershell
.\testar-build.ps1
```

### Linux/Mac
```bash
chmod +x testar-build.sh
./testar-build.sh
```

### Manualmente
```bash
# Build
docker build -t crmia-test .

# Run
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-sua-chave crmia-test

# Acesse: http://localhost:8501
```

## 🔧 Ajustes de Performance

### Mais Memória e CPU
```bash
gcloud run services update crmia-agente-autonomo \
  --memory 4Gi \
  --cpu 4 \
  --region southamerica-east1
```

### Aumentar Timeout
```bash
gcloud run services update crmia-agente-autonomo \
  --timeout 1800 \
  --region southamerica-east1
```

### Manter Instância Sempre Ativa (evita cold start)
```bash
gcloud run services update crmia-agente-autonomo \
  --min-instances 1 \
  --region southamerica-east1
```

## 📊 Monitoramento

### Console Web
```
https://console.cloud.google.com/run/detail/southamerica-east1/crmia-agente-autonomo
```

### Métricas
- **Latência**: Tempo de resposta
- **Requests**: Número de requisições
- **Memory**: Uso de memória
- **CPU**: Uso de CPU
- **Errors**: Taxa de erros

## 🔄 Rollback (se algo der errado)

```bash
# Listar revisões
gcloud run revisions list \
  --service crmia-agente-autonomo \
  --region southamerica-east1

# Voltar para revisão anterior
gcloud run services update-traffic crmia-agente-autonomo \
  --to-revisions REVISION_ANTERIOR=100 \
  --region southamerica-east1
```

## 💰 Otimização de Custos

```bash
# Configuração econômica (para testes)
gcloud run deploy crmia-agente-autonomo \
  --source . \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --region southamerica-east1

# Configuração performance (para produção)
gcloud run deploy crmia-agente-autonomo \
  --source . \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --region southamerica-east1
```

## ⚠️ Troubleshooting Rápido

### Erro no Build?
```bash
# Ver logs do último build
gcloud builds list --limit 1
gcloud builds log $(gcloud builds list --limit 1 --format='value(id)')
```

### Aplicação não inicia?
```bash
# Ver logs de inicialização
gcloud run services logs read crmia-agente-autonomo \
  --region southamerica-east1 \
  --limit 100
```

### Timeout constante?
```bash
# Aumentar timeout e recursos
gcloud run services update crmia-agente-autonomo \
  --timeout 1200 \
  --memory 4Gi \
  --cpu 2 \
  --region southamerica-east1
```

## 📝 Variáveis de Ambiente Comuns

```bash
# Configurar múltiplas variáveis
gcloud run services update crmia-agente-autonomo \
  --set-env-vars \
    OPENAI_API_KEY=sk-...,\
    DATABASE_URL=postgresql://...,\
    DEBUG=false \
  --region southamerica-east1
```

## 🎯 Checklist Pré-Deploy

- [ ] Testei o build localmente
- [ ] Tenho a chave da OpenAI pronta
- [ ] Configurei o projeto correto no gcloud
- [ ] As APIs estão habilitadas
- [ ] Revisei os recursos (memória/CPU) necessários

## 📚 Documentação Completa

- `PROBLEMA_BUILD_RESOLVIDO.md` - Detalhes do problema que foi corrigido
- `DEPLOY_CLOUD_RUN.md` - Guia completo de deploy
- `RESUMO_CORRECOES.md` - Resumo de todas as correções

---

**Pronto para deploy!** 🎉
