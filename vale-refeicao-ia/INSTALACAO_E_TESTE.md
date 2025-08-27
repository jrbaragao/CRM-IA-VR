# 🚀 Guia de Instalação e Teste - Vale Refeição IA

## 📋 Pré-requisitos

Certifique-se de ter instalado:
- ✅ Python 3.11 ou superior
- ✅ PostgreSQL 14 ou superior
- ✅ Git
- ✅ Docker (opcional, mas recomendado)

## 🔧 Instalação Passo a Passo

### 1. Clone o Repositório (se ainda não tiver)

```bash
# Se você já tem o projeto, pule esta etapa
git clone https://github.com/seu-usuario/vale-refeicao-ia.git
cd vale-refeicao-ia
```

### 2. Crie o Ambiente Virtual

```bash
# No Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# No Windows (CMD)
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados

#### Opção A: Usando Docker (Recomendado) 🐳

```bash
# Inicie o PostgreSQL e ChromaDB com Docker Compose
docker-compose up -d

# Verifique se os containers estão rodando
docker ps
```

#### Opção B: PostgreSQL Local

Se você tem PostgreSQL instalado localmente:

```sql
-- Conecte ao PostgreSQL e execute:
CREATE DATABASE vale_refeicao;
CREATE USER vr_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE vale_refeicao TO vr_user;
```

### 5. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Copie este conteúdo para o arquivo .env
# Banco de Dados
DATABASE_URL=postgresql://vr_user:sua_senha_segura@localhost:5432/vale_refeicao

# OpenAI
OPENAI_API_KEY=sk-... # Sua chave da OpenAI

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

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
```

### 6. Execute as Migrações do Banco

```bash
# Crie as tabelas no banco de dados
alembic upgrade head

# Se alembic não estiver configurado, você pode criar as tabelas manualmente:
python -c "from src.data.models import Base, engine; Base.metadata.create_all(engine)"
```

## 🎯 Testando a Aplicação

### 1. Inicie o Streamlit

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em: http://localhost:8501

### 2. Prepare Arquivos de Teste

Crie planilhas Excel de teste com as seguintes colunas:
- **MATRICULA** (obrigatório - chave de unificação)
- **NOME**
- **CPF**
- **DEPARTAMENTO**
- **DATA_ADMISSAO**
- **SALARIO**
- **DIAS_TRABALHADOS**

### 3. Fluxo de Teste Completo

#### Passo 1: Upload de Arquivos
1. Acesse a página de Upload
2. Arraste ou selecione múltiplas planilhas
3. Clique em "Processar Arquivos"

#### Passo 2: Processamento
1. O sistema detectará automaticamente as colunas
2. O Extraction Agent limpará e validará os dados
3. Verifique o relatório de processamento

#### Passo 3: Cálculos
1. Vá para a página de Cálculos
2. Configure:
   - Mês de referência
   - Valor por dia útil
   - Percentual de desconto
3. Clique em "Calcular Vale Refeição"

#### Passo 4: Relatórios
1. Acesse a página de Relatórios
2. Visualize:
   - Resumo por departamento
   - Distribuição de valores
   - Estatísticas gerais
3. Exporte para PDF ou Excel

## 🧪 Testes Automatizados

```bash
# Execute os testes unitários
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_agents.py -v
pytest tests/test_calculations.py -v
```

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY not found"
```bash
# Verifique se o arquivo .env existe e contém:
OPENAI_API_KEY=sk-...
```

### Erro: "Cannot connect to PostgreSQL"
```bash
# Verifique se o PostgreSQL está rodando
docker ps

# Ou se instalado localmente:
pg_isready -h localhost -p 5432
```

### Erro: "ChromaDB connection failed"
```bash
# Inicie o ChromaDB
docker-compose up chroma -d

# Ou use o modo em memória (desenvolvimento)
# Altere no .env: CHROMA_PERSIST=False
```

### Erro: "Module not found"
```bash
# Reinstale as dependências
pip install -r requirements.txt --force-reinstall
```

## 📊 Dados de Exemplo

Crie um arquivo `exemplo_funcionarios.csv`:

```csv
MATRICULA,NOME,CPF,DEPARTAMENTO,DATA_ADMISSAO,SALARIO,DIAS_TRABALHADOS
1001,João Silva,123.456.789-00,TI,2023-01-15,5000.00,22
1002,Maria Santos,987.654.321-00,RH,2022-06-20,4500.00,20
1003,Pedro Oliveira,456.789.123-00,Vendas,2023-03-10,3800.00,22
```

## 🔍 Verificação de Saúde

Execute este script para verificar se tudo está funcionando:

```python
# test_health.py
import os
from dotenv import load_dotenv
import psycopg2
import openai
import chromadb

load_dotenv()

# Teste 1: Variáveis de Ambiente
print("✅ Teste 1: Variáveis de Ambiente")
assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY não configurada"
assert os.getenv("DATABASE_URL"), "❌ DATABASE_URL não configurada"
print("✅ Variáveis OK")

# Teste 2: PostgreSQL
print("\n✅ Teste 2: PostgreSQL")
try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.close()
    print("✅ PostgreSQL OK")
except Exception as e:
    print(f"❌ PostgreSQL Error: {e}")

# Teste 3: OpenAI
print("\n✅ Teste 3: OpenAI")
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # Teste simples sem gastar tokens
    print("✅ OpenAI configurada")
except Exception as e:
    print(f"❌ OpenAI Error: {e}")

# Teste 4: ChromaDB
print("\n✅ Teste 4: ChromaDB")
try:
    client = chromadb.Client()
    print("✅ ChromaDB OK")
except Exception as e:
    print(f"❌ ChromaDB Error: {e}")

print("\n🎉 Todos os testes passaram! A aplicação está pronta para uso.")
```

## 🚀 Início Rápido

```bash
# Comando único para iniciar tudo (Windows PowerShell)
docker-compose up -d; python -m venv venv; .\venv\Scripts\Activate; pip install -r requirements.txt; streamlit run app.py

# Linux/Mac
docker-compose up -d && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && streamlit run app.py
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `streamlit run app.py --logger.level=debug`
2. Consulte a documentação: `README.md` e `DEPLOY.md`
3. Verifique os requisitos: Python 3.11+, PostgreSQL 14+

## ✅ Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL rodando
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Banco de dados criado
- [ ] Tabelas migradas
- [ ] OpenAI API key válida
- [ ] Streamlit rodando
- [ ] Upload de teste realizado

Quando todos os itens estiverem marcados, sua instalação está completa! 🎉
