# 🔧 Parâmetros de Configuração - Vale Refeição IA

## 📋 Parâmetros Obrigatórios

### 1. **OPENAI_API_KEY** ⭐ (ESSENCIAL)
- **Tipo**: String
- **Exemplo**: `sk-proj-abc123...`
- **Onde obter**: https://platform.openai.com/api-keys
- **Descrição**: Chave de API da OpenAI para funcionamento dos agentes IA

### 2. **DATABASE_URL** ⭐ (ESSENCIAL)
- **Tipo**: String (URL de conexão)
- **Exemplo**: `postgresql://vr_user:senha123@localhost:5432/vale_refeicao`
- **Formato**: `postgresql://[usuário]:[senha]@[host]:[porta]/[banco]`
- **Descrição**: URL de conexão com o banco PostgreSQL

## 📋 Parâmetros de Configuração do Vale Refeição

### 3. **VALOR_DIA_UTIL**
- **Tipo**: Float
- **Padrão**: `35.00`
- **Exemplo**: `42.50`
- **Descrição**: Valor do vale refeição por dia útil trabalhado

### 4. **DESCONTO_FUNCIONARIO_PCT**
- **Tipo**: Float (0.0 a 1.0)
- **Padrão**: `0.20` (20%)
- **Exemplo**: `0.15` (15%)
- **Descrição**: Percentual de desconto do funcionário sobre o valor total

### 5. **DIAS_UTEIS_MES_PADRAO**
- **Tipo**: Integer
- **Padrão**: `22`
- **Exemplo**: `20`
- **Descrição**: Número padrão de dias úteis no mês

## 📋 Parâmetros de IA/LlamaIndex

### 6. **OPENAI_MODEL**
- **Tipo**: String
- **Padrão**: `gpt-4-turbo-preview`
- **Opções**: `gpt-4`, `gpt-4-turbo-preview`, `gpt-3.5-turbo`
- **Descrição**: Modelo da OpenAI a ser usado

### 7. **AGENT_TEMPERATURE**
- **Tipo**: Float (0.0 a 2.0)
- **Padrão**: `0.1`
- **Exemplo**: `0.7`
- **Descrição**: Criatividade das respostas (0=determinístico, 2=criativo)

### 8. **AGENT_MAX_RETRIES**
- **Tipo**: Integer
- **Padrão**: `3`
- **Descrição**: Número máximo de tentativas em caso de erro

## 📋 Parâmetros do ChromaDB (Vector Store)

### 9. **CHROMA_HOST**
- **Tipo**: String
- **Padrão**: `localhost`
- **Exemplo**: `192.168.1.100`
- **Descrição**: Host do servidor ChromaDB

### 10. **CHROMA_PORT**
- **Tipo**: Integer
- **Padrão**: `8000`
- **Descrição**: Porta do servidor ChromaDB

### 11. **CHROMA_PERSIST**
- **Tipo**: Boolean
- **Padrão**: `True`
- **Descrição**: Se deve persistir dados no disco

### 12. **CHROMA_PERSIST_DIR**
- **Tipo**: String (caminho)
- **Padrão**: `./chroma_db`
- **Descrição**: Diretório para persistência do ChromaDB

### 13. **CHROMA_COLLECTION**
- **Tipo**: String
- **Padrão**: `vale_refeicao_collection`
- **Descrição**: Nome da coleção no ChromaDB

## 📋 Parâmetros de Upload/Processamento

### 14. **MAX_FILE_SIZE_MB**
- **Tipo**: Integer
- **Padrão**: `50`
- **Exemplo**: `100`
- **Descrição**: Tamanho máximo de arquivo em MB

### 15. **ALLOWED_EXTENSIONS**
- **Tipo**: String (lista separada por vírgula)
- **Padrão**: `csv,xlsx,xls`
- **Exemplo**: `csv,xlsx,xls,xlsm`
- **Descrição**: Extensões de arquivo permitidas

## 📋 Parâmetros de Sistema

### 16. **ENVIRONMENT**
- **Tipo**: String
- **Padrão**: `development`
- **Opções**: `development`, `staging`, `production`
- **Descrição**: Ambiente de execução

### 17. **DEBUG**
- **Tipo**: Boolean
- **Padrão**: `True` (desenvolvimento), `False` (produção)
- **Descrição**: Modo debug (mais logs e informações)

### 18. **LOG_LEVEL**
- **Tipo**: String
- **Padrão**: `INFO`
- **Opções**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Descrição**: Nível de detalhamento dos logs

### 19. **LOG_FILE**
- **Tipo**: String (caminho)
- **Padrão**: `logs/app.log`
- **Descrição**: Arquivo para salvar logs

## 📋 Parâmetros de Segurança

### 20. **SECRET_KEY**
- **Tipo**: String
- **Padrão**: Gerado automaticamente
- **Exemplo**: `sua-chave-secreta-muito-segura-aqui`
- **Descrição**: Chave para criptografia de sessões

### 21. **SESSION_TIMEOUT**
- **Tipo**: Integer (segundos)
- **Padrão**: `3600` (1 hora)
- **Descrição**: Tempo de expiração da sessão

## 📋 Parâmetros de Diretórios

### 22. **UPLOAD_DIR**
- **Tipo**: String (caminho)
- **Padrão**: `./uploads`
- **Descrição**: Diretório para arquivos enviados

### 23. **EXPORT_DIR**
- **Tipo**: String (caminho)
- **Padrão**: `./exports`
- **Descrição**: Diretório para arquivos exportados

### 24. **PROMPTS_DIR**
- **Tipo**: String (caminho)
- **Padrão**: `./prompts`
- **Descrição**: Diretório com prompts dos agentes

## 📝 Exemplo de Arquivo .env Completo

```env
# === CONFIGURAÇÕES OBRIGATÓRIAS ===
OPENAI_API_KEY=sk-proj-suachaveaqui123...
DATABASE_URL=postgresql://vr_user:senha123@localhost:5432/vale_refeicao

# === CONFIGURAÇÕES DO VALE REFEIÇÃO ===
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
DIAS_UTEIS_MES_PADRAO=22

# === CONFIGURAÇÕES DE IA ===
OPENAI_MODEL=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.1
AGENT_MAX_RETRIES=3

# === CHROMADB ===
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST=True
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION=vale_refeicao_collection

# === UPLOAD/PROCESSAMENTO ===
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls

# === SISTEMA ===
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# === SEGURANÇA ===
SECRET_KEY=minha-chave-secreta-super-segura-2024
SESSION_TIMEOUT=3600

# === DIRETÓRIOS ===
UPLOAD_DIR=./uploads
EXPORT_DIR=./exports
PROMPTS_DIR=./prompts
```

## 🚀 Configuração Mínima para Funcionar

Para uma configuração mínima funcional, você precisa apenas:

```env
# Arquivo .env mínimo
OPENAI_API_KEY=sk-proj-suachaveaqui...
DATABASE_URL=postgresql://vr_user:senha@localhost:5432/vale_refeicao
```

Os demais parâmetros usarão valores padrão definidos no código.

## 💡 Dicas

1. **Desenvolvimento Local**: Use SQLite temporariamente:
   ```env
   DATABASE_URL=sqlite:///./vale_refeicao.db
   ```

2. **Docker Compose**: O database_url padrão funciona com o docker-compose.yml:
   ```env
   DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao
   ```

3. **Produção**: Sempre defina:
   - `DEBUG=False`
   - `ENVIRONMENT=production`
   - Use senhas fortes
   - Configure logs apropriadamente

4. **Testes**: Para testes rápidos sem ChromaDB persistente:
   ```env
   CHROMA_PERSIST=False
   ```
