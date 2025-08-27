# 📋 Guia de Configuração do Arquivo .env

## 📍 Onde Colocar o Arquivo .env

O arquivo `.env` deve ser colocado na **raiz do projeto**, ou seja:
```
D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia\.env
```

### Estrutura de Arquivos:
```
vale-refeicao-ia/
├── .env                 👈 AQUI (na raiz)
├── .gitignore          
├── app.py              
├── requirements.txt    
├── src/                
└── ...                 
```

## 🔒 Segurança - Git/GitHub

### ✅ SIM, está protegido!

O arquivo `.env` **NÃO será enviado** para o Git/GitHub porque:

1. **Está no .gitignore** (linha 106):
   ```gitignore
   # Environments
   .env
   .venv
   env/
   venv/
   ```

2. **Variações também protegidas** (linhas 174-176):
   ```gitignore
   # Local development
   .env.local
   .env.development
   .env.production
   ```

## 📝 Como Criar o Arquivo .env

### Opção 1: Criar Manualmente

1. **No Windows Explorer:**
   - Navegue até `D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia`
   - Clique com botão direito → Novo → Documento de Texto
   - Renomeie para `.env` (sim, começando com ponto)

2. **Via PowerShell:**
   ```powershell
   cd D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia
   New-Item -Path ".env" -ItemType File
   ```

3. **Via CMD:**
   ```cmd
   cd D:\Dados\Sites\Cursor\CRMIA-VR\vale-refeicao-ia
   echo. > .env
   ```

### Opção 2: Copiar do Exemplo

Se existir um arquivo `.env.example`:
```bash
copy .env.example .env
```

## 📄 Conteúdo do Arquivo .env

Adicione este conteúdo ao arquivo `.env`:

```env
# ===================================
# CONFIGURAÇÕES DO VALE REFEIÇÃO IA
# ===================================

# Banco de Dados PostgreSQL
DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao

# OpenAI API - OBRIGATÓRIO!
# Obtenha sua chave em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...  # 👈 SUBSTITUA pela sua chave real

# ChromaDB (Vector Store)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST=True
CHROMA_COLLECTION=vale_refeicao_collection

# Configurações de Vale Refeição
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
DIAS_UTEIS_MES=22

# Ambiente
ENVIRONMENT=development
DEBUG=True

# Configurações de Upload
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls

# Configurações de Segurança (opcional)
SECRET_KEY=sua_chave_secreta_aqui
SESSION_TIMEOUT=3600

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 🔑 Obtendo a Chave OpenAI

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (começa com `sk-`)
5. Cole no lugar de `sk-...` no arquivo `.env`

## ✅ Verificando se Está Funcionando

### 1. Teste de Leitura do .env:
```python
# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

# Verifica se as variáveis foram carregadas
api_key = os.getenv("OPENAI_API_KEY")
if api_key and api_key.startswith("sk-"):
    print("✅ Chave OpenAI configurada!")
else:
    print("❌ Chave OpenAI não encontrada ou inválida")

db_url = os.getenv("DATABASE_URL")
if db_url:
    print("✅ Database URL configurada!")
else:
    print("❌ Database URL não encontrada")
```

### 2. Execute o teste:
```bash
python test_env.py
```

## 🚫 O que NÃO Fazer

1. **NUNCA** commite o arquivo `.env` com dados reais
2. **NUNCA** compartilhe sua chave OpenAI
3. **NUNCA** remova `.env` do `.gitignore`

## 📌 Comandos Git para Segurança

### Verificar se .env está sendo ignorado:
```bash
git status --ignored
```

### Se acidentalmente adicionou .env ao Git:
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### Verificar antes de fazer push:
```bash
git ls-files | grep -i env
```

## 🔄 Boas Práticas

1. **Crie um .env.example**:
   - Copie o `.env` como `.env.example`
   - Remova valores sensíveis
   - Mantenha apenas a estrutura
   - Commite o `.env.example` (este pode ir pro GitHub)

2. **Use valores diferentes por ambiente**:
   - `.env.development` - desenvolvimento local
   - `.env.test` - testes
   - `.env.production` - produção

3. **Documente as variáveis**:
   - Sempre adicione comentários
   - Indique quais são obrigatórias
   - Forneça exemplos de valores

## ✨ Resumo

- 📍 **Local**: Raiz do projeto (`vale-refeicao-ia/.env`)
- 🔒 **Segurança**: Já está no `.gitignore` - não será enviado ao GitHub
- 🔑 **Obrigatório**: Adicionar sua chave OpenAI
- ✅ **Verificação**: Use `git status` para confirmar que não está sendo rastreado
