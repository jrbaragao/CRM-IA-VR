# 🚀 Guia de Instalação e Teste - Vale Refeição IA

## 📋 Pré-requisitos

Certifique-se de ter instalado:
- ✅ Python 3.11 ou superior
- ✅ SQLite (incluído no Python) ou PostgreSQL 14+
- ✅ Git
- ✅ Até 2GB de RAM disponível para análises grandes

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
# Instale todas as dependências incluindo bibliotecas de visualização
pip install -r requirements.txt

# Ou se preferir instalar individualmente:
pip install streamlit pandas numpy sqlalchemy
pip install openai llama-index matplotlib seaborn
pip install xlsxwriter openpyxl
```

### 4. Configure o Banco de Dados

#### Opção A: SQLite (Recomendado para Teste) 📦

```bash
# Windows PowerShell
.\configurar_sqlite.ps1

# Windows CMD
configurar_sqlite.bat

# Ou crie manualmente o arquivo .env:
echo "DATABASE_URL=sqlite:///./vale_refeicao.db" > .env
echo "OPENAI_API_KEY=sk-sua-chave-aqui" >> .env
```

#### Opção B: Usando Docker (PostgreSQL) 🐳

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
# Certifique-se que o ambiente virtual está ativo
streamlit run app.py
```

A aplicação abrirá automaticamente em: http://localhost:8501

#### 🔄 Como Reiniciar Após Mudanças:
```bash
# 1. No terminal onde o Streamlit está rodando:
Ctrl + C  # Para o servidor

# 2. Inicie novamente:
streamlit run app.py

# Ou use auto-reload para desenvolvimento:
streamlit run app.py --server.runOnSave true
```

### 2. Prepare Arquivos de Teste

#### Para Vale Refeição:
Crie planilhas Excel/CSV com colunas como:
- **MATRICULA** (ou escolha outra coluna como índice)
- **NOME**
- **SINDICATO**
- **DATA_ADMISSAO**
- **STATUS**

#### Para Análise Exploratória (Qualquer Dataset):
- **Vendas**: produto, quantidade, preço, data, categoria
- **Clientes**: id, idade, cidade, renda, score
- **Estoque**: sku, quantidade, custo, fornecedor
- **Qualquer CSV**: O sistema se adapta automaticamente

### 3. Fluxo de Teste Completo

#### ⚠️ IMPORTANTE: O sistema tem 2 etapas separadas!

1. **Upload** → Apenas carrega arquivos na memória
2. **Preparação de Dados** → Salva no banco de dados

#### Passo 1: Upload de Arquivos
1. Acesse a página "📤 Upload"
2. Arraste ou selecione arquivos (até 500MB)
3. Para cada arquivo:
   - Marque "Definir coluna de indexação" (opcional)
   - Escolha a coluna desejada como chave primária
4. **IMPORTANTE**: Após upload, vá para "🔄 Preparação de Dados" no menu lateral

#### Passo 2: Preparação de Dados (OBRIGATÓRIO!)
1. Acesse a página "🔄 Preparação de Dados" 
2. Clique em "Iniciar Processamento"
3. Aguarde o agente:
   - Limpar dados
   - Criar tabelas no banco
   - Salvar registros
4. Só após isso os dados estarão disponíveis

#### Passo 3: Análise Exploratória de Dados (NOVO!)
1. Vá para "Banco de Dados" → "Buscas (Query)"
2. Na aba "Agente Autônomo", digite:
   - "Faça uma análise exploratória completa dos dados"
   - "Identifique outliers e correlações"
   - "Mostre estatísticas e distribuições"
3. Visualize os resultados em 5 abas:
   - 📈 Estatísticas
   - 📊 Distribuições
   - 🔗 Correlações
   - 🎯 Outliers
   - 💡 Insights

#### Passo 4: Agentes de IA
1. Vá para "Agentes de IA"
2. Configure uma nova análise:
   - Nome: "Análise Completa EDA"
   - Ferramentas: Marque "📊 Análise Exploratória (EDA)"
   - Prompt: Descreva sua análise desejada
3. Execute e acompanhe em tempo real

#### Passo 5: Exportação e Relatórios
1. Os resultados incluem:
   - Estatísticas completas
   - Gráficos (quando solicitados)
   - Recomendações automáticas
2. Exporte para Excel com todas as análises
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

## 🆕 Novos Recursos de Análise Exploratória

### 📊 Análises Disponíveis

1. **Estatísticas Descritivas**
   - Média, mediana, desvio padrão
   - Quartis e percentis
   - Valores mínimos e máximos

2. **Análise de Distribuições**
   - Detecção de normalidade
   - Assimetria (skewness) e curtose
   - Recomendações de transformação

3. **Detecção de Outliers**
   - Método IQR automático
   - Contagem e percentual por coluna
   - Valores específicos identificados

4. **Análise de Correlações**
   - Matriz completa de correlações
   - Identificação de pares fortemente correlacionados
   - Visualização em heatmap (quando solicitado)

5. **Valores Ausentes**
   - Contagem por coluna
   - Padrões de ausência
   - Recomendações de tratamento

### 🎯 Exemplos de Perguntas para o Agente

```
"Análise completa da tabela vendas"
"Quais colunas têm outliers?"
"Mostre as correlações entre preço e quantidade"
"Identifique padrões temporais nos dados"
"Quais variáveis têm distribuição normal?"
"Detecte anomalias no dataset"
```

## 🔍 Verificação de Saúde

Execute este script para verificar se tudo está funcionando:

```python
# test_health.py
import os
from dotenv import load_dotenv
import sqlalchemy
import openai
import pandas as pd
import matplotlib
import seaborn

load_dotenv()

# Teste 1: Variáveis de Ambiente
print("✅ Teste 1: Variáveis de Ambiente")
assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY não configurada"
assert os.getenv("DATABASE_URL"), "❌ DATABASE_URL não configurada"
print("✅ Variáveis OK")

# Teste 2: Banco de Dados
print("\n✅ Teste 2: Banco de Dados")
try:
    engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL"))
    engine.connect()
    print("✅ Banco de Dados OK")
except Exception as e:
    print(f"❌ Database Error: {e}")

# Teste 3: OpenAI
print("\n✅ Teste 3: OpenAI")
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print("✅ OpenAI configurada")
except Exception as e:
    print(f"❌ OpenAI Error: {e}")

# Teste 4: Bibliotecas de Análise
print("\n✅ Teste 4: Bibliotecas de Análise")
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("✅ Matplotlib e Seaborn OK")
except Exception as e:
    print(f"❌ Visualization Error: {e}")

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
