# 🎓 Configuração com SQLite para Testes/Curso

## ✅ Vantagens do SQLite para Testes

1. **Zero configuração** - Não precisa instalar nada
2. **Arquivo único** - Fácil de compartilhar
3. **Rápido** - Para poucos dados é muito eficiente
4. **Portável** - Funciona em qualquer lugar

## 🚀 Configuração Rápida

### 1. Crie o arquivo `.env`

Crie um arquivo chamado `.env` na raiz do projeto com este conteúdo:

```env
# Banco de Dados - SQLite (arquivo local)
DATABASE_URL=sqlite:///./vale_refeicao.db

# OpenAI API - COLOQUE SUA CHAVE AQUI!
OPENAI_API_KEY=sk-...

# ChromaDB em memória (não precisa instalar)
CHROMA_PERSIST=False
```

**Importante**: Substitua `sk-...` pela sua chave real da OpenAI!

### 2. Execute a Aplicação

```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Execute o Streamlit
streamlit run app.py
```

## 📝 Script Completo de Configuração

Copie e cole no PowerShell:

```powershell
# 1. Criar arquivo .env
@"
DATABASE_URL=sqlite:///./vale_refeicao.db
OPENAI_API_KEY=sk-COLE_SUA_CHAVE_AQUI
CHROMA_PERSIST=False
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
"@ | Out-File -FilePath ".env" -Encoding UTF8

# 2. Mensagem
Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
Write-Host "⚠️  Edite o arquivo .env e adicione sua chave OpenAI!" -ForegroundColor Yellow

# 3. Abrir o arquivo
notepad .env
```

## 🔧 Verificar se Está Funcionando

Crie um arquivo `test_sqlite.py`:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega .env
load_dotenv()

# Testa conexão
try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ SQLite funcionando!")
        
    # Testa OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sk-..." and len(api_key) > 20:
        print("✅ Chave OpenAI configurada!")
    else:
        print("❌ Configure sua chave OpenAI no .env")
        
except Exception as e:
    print(f"❌ Erro: {e}")
```

Execute:
```bash
python test_sqlite.py
```

## 📊 Limitações do SQLite

Para um curso/teste está perfeito, mas saiba que:

1. **Sem múltiplos usuários** - Apenas 1 pessoa por vez
2. **Sem tipos JSON nativos** - Armazena como texto
3. **Queries mais simples** - Sem window functions avançadas
4. **Arquivo pode corromper** - Faça backups

## 🎯 Começar Agora!

1. **Copie o conteúdo de `config_sqlite.txt` para `.env`**
2. **Adicione sua chave OpenAI**
3. **Execute**: `streamlit run app.py`
4. **Teste com os arquivos em `exemplos/`**

## 💡 Dicas para o Curso

### Estrutura Simplificada de Tabelas

```sql
-- SQLite cria automaticamente estas tabelas
CREATE TABLE funcionarios (
    matricula TEXT PRIMARY KEY,
    nome TEXT,
    cpf TEXT,
    departamento TEXT,
    data_admissao DATE,
    salario REAL
);

CREATE TABLE calculos_vr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT,
    mes_referencia TEXT,
    valor_calculado REAL,
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matricula) REFERENCES funcionarios(matricula)
);
```

### Dados de Teste

Use os arquivos em `exemplos/`:
- `funcionarios_teste.csv` - 10 funcionários
- `beneficios_teste.csv` - Benefícios extras

### Resetar Banco

Para começar do zero:
```bash
# Windows
del vale_refeicao.db

# PowerShell
Remove-Item vale_refeicao.db -Force
```

## ✨ Pronto para o Curso!

Com SQLite você pode:
- ✅ Fazer upload de planilhas
- ✅ Ver os agentes IA funcionando
- ✅ Calcular vale refeição
- ✅ Gerar relatórios
- ✅ Aprender o sistema completo

Sem se preocupar com:
- ❌ Instalar PostgreSQL
- ❌ Configurar Docker
- ❌ Gerenciar banco de dados

Perfeito para aprendizado! 🎓
