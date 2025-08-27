# 🔍 Análise de Arquivos Duplicados - CRMIA-VR

## 📁 Estrutura Atual do Diretório

Existem arquivos duplicados em diferentes níveis do diretório `CRMIA-VR`:

### 1. **Arquivos na Raiz (D:\Dados\Sites\Cursor\CRMIA-VR\)**

Estes arquivos parecem ser do projeto original de **Análise de Notas Fiscais**:

- ❌ `app.py` - Aplicação de análise de notas fiscais (DIFERENTE do vale refeição)
- ❌ `app_original.py` - Versão com LlamaIndex do projeto de notas fiscais
- ❌ `requirements.txt` - Dependências do projeto de notas fiscais
- ❌ `cloudbuild.yaml` - Deploy do projeto de notas fiscais
- ❌ `deploy.ps1` - Script de deploy antigo
- ❌ `Dockerfile` - Docker do projeto antigo
- ❌ `Dockerfile.complex` - Versão complexa do Docker
- ❌ `docs/` - Documentação do projeto de notas fiscais
- ❌ `aindo` - Arquivo desconhecido (possivelmente erro de digitação)
- ❌ `tatus` - Arquivo desconhecido (possivelmente erro de digitação de "status")
- ❌ `h origin docker-support` - Comando git incompleto

### 2. **Pasta CRM-IA-VR/**

Esta parece ser uma cópia/backup do projeto original:
- ❌ Contém os mesmos arquivos do projeto de notas fiscais
- ❌ Tem uma subpasta `vale-refeicao-ia` mas com estrutura incompleta

### 3. **Pasta vale-refeicao-ia/** ✅

Esta é a pasta do projeto atual e está completa:
- ✅ Todos os arquivos do sistema de vale refeição
- ✅ Estrutura correta com agentes LlamaIndex
- ✅ Documentação específica do projeto

## 🗑️ Recomendação: Arquivos que PODEM ser apagados

### Arquivos na raiz que podem ser removidos:
```
D:\Dados\Sites\Cursor\CRMIA-VR\app.py
D:\Dados\Sites\Cursor\CRMIA-VR\app_original.py
D:\Dados\Sites\Cursor\CRMIA-VR\requirements.txt
D:\Dados\Sites\Cursor\CRMIA-VR\cloudbuild.yaml
D:\Dados\Sites\Cursor\CRMIA-VR\deploy.ps1
D:\Dados\Sites\Cursor\CRMIA-VR\Dockerfile
D:\Dados\Sites\Cursor\CRMIA-VR\Dockerfile.complex
D:\Dados\Sites\Cursor\CRMIA-VR\aindo
D:\Dados\Sites\Cursor\CRMIA-VR\tatus
D:\Dados\Sites\Cursor\CRMIA-VR\h origin docker-support
```

### Pasta que pode ser removida (se for backup):
```
D:\Dados\Sites\Cursor\CRMIA-VR\CRM-IA-VR\
```

### Pasta docs (se for do projeto antigo):
```
D:\Dados\Sites\Cursor\CRMIA-VR\docs\
```

## ⚠️ IMPORTANTE: Antes de apagar

1. **Faça backup** se houver dúvida sobre algum arquivo
2. **Verifique** se não há código útil nos arquivos antigos
3. **Confirme** que o projeto `vale-refeicao-ia` está completo

## 📊 Resumo

- **Projeto Atual**: `D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia\`
- **Arquivos Antigos**: Relacionados ao projeto de análise de notas fiscais
- **Recomendação**: Limpar arquivos duplicados para evitar confusão

## 🧹 Comando para Limpeza (PowerShell)

```powershell
# CUIDADO: Este comando remove os arquivos!
# Faça backup antes se necessário

# Remover arquivos da raiz
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\app.py
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\app_original.py
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\requirements.txt
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\cloudbuild.yaml
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\deploy.ps1
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\Dockerfile*
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\aindo -ErrorAction SilentlyContinue
Remove-Item D:\Dados\Sites\Cursor\CRMIA-VR\tatus -ErrorAction SilentlyContinue
Remove-Item "D:\Dados\Sites\Cursor\CRMIA-VR\h origin docker-support" -ErrorAction SilentlyContinue

# Remover pasta CRM-IA-VR (se confirmar que é backup)
# Remove-Item -Recurse -Force D:\Dados\Sites\Cursor\CRMIA-VR\CRM-IA-VR\

# Remover pasta docs antiga (se confirmar que é do projeto antigo)
# Remove-Item -Recurse -Force D:\Dados\Sites\Cursor\CRMIA-VR\docs\
```
