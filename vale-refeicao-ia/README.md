# 🤖 Sistema Inteligente de Análise de Dados com Agentes Autônomos

Sistema revolucionário de análise de dados baseado em **Agentes de IA Autônomos** e **Tabelas Dinâmicas**. Processe qualquer tipo de dados, configure prompts personalizados e deixe os agentes executarem análises complexas automaticamente.

## 🌟 Funcionalidades Revolucionárias

### 🧠 **Agentes de IA Autônomos**
- **🔍 Agente de Consulta**: Converte linguagem natural em SQL inteligente
- **🧮 Agente de Cálculo**: Executa cálculos complexos baseados em prompts configuráveis
- **💰 Tool Vale Refeição**: Cálculo especializado com regras de negócio brasileiras (detalhado abaixo)
- **📊 Agente de Análise**: Realiza análises multi-etapas com raciocínio transparente
- **🔄 Processo Iterativo**: Agentes executam múltiplas etapas até completar objetivos

### 📊 **Tabelas Dinâmicas Inteligentes**
- **🚀 Criação Automática**: Cada arquivo gera sua própria tabela no banco
- **🔗 Correlações Inteligentes**: Agentes identificam relações entre dados via prompts
- **🔑 Chaves Primárias Configuráveis**: Sistema sugere e permite configurar PKs
- **⚡ Performance Otimizada**: Estrutura adaptada aos dados reais

### 🎯 **Prompts Configuráveis**
- **📝 Linguagem Natural**: Defina regras e cálculos em português
- **🛠️ Ferramentas Selecionáveis**: Escolha capacidades específicas para cada agente
- **💾 Persistência**: Configurações salvas no banco para reutilização
- **🔄 Versionamento**: Histórico completo de configurações e execuções

### 🔍 **Sistema de Consultas Avançado**
- **🤖 Prompt to Query**: "Mostre funcionários com salário acima de R$ 5.000"
- **🧠 Consulta Autônoma**: Agente executa múltiplas etapas para responder perguntas complexas
- **📊 SQL Avançado**: Editor completo com validação e execução segura
- **📈 Resultados Dinâmicos**: Visualização sem recarregamento de página

## 🏗️ Nova Arquitetura

```mermaid
graph TB
    subgraph "Interface Streamlit"
        UP[📤 Upload de Dados]
        DB[🗃️ Banco de Dados]
        CALC[🧮 Cálculos IA]
        PROM[🎯 Prompts]
    end
    
    subgraph "Agentes Autônomos"
        QA[🔍 Query Agent]
        CA[🧮 Calculation Agent]
        AA[📊 Analysis Agent]
    end
    
    subgraph "Dados Dinâmicos"
        SQLITE[(SQLite Dinâmico)]
        DT[📊 Tabelas Dinâmicas]
        PC[⚙️ Prompt Configs]
    end
    
    subgraph "IA & Processamento"
        GPT[🧠 OpenAI GPT-4]
        LLAMA[🦙 LlamaIndex]
    end
    
    UP --> DT
    DB --> QA
    CALC --> CA
    PROM --> PC
    
    QA --> GPT
    CA --> GPT
    AA --> GPT
    
    GPT --> LLAMA
    LLAMA --> SQLITE
    
    DT --> SQLITE
    PC --> SQLITE
```

## 🚀 Quick Start

### ⚡ Instalação Rápida (SQLite)

1. **Clone e Configure**:
```bash
git clone https://github.com/seu-usuario/vale-refeicao-ia.git
cd vale-refeicao-ia
```

2. **Configuração Automática** (Windows):
```bash
# PowerShell
.\configurar_sqlite.ps1

# Ou Batch
configurar_sqlite.bat
```

3. **Instalação Manual**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

4. **Configure OpenAI**:
```bash
# Crie .env com sua chave
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > .env
echo "DATABASE_URL=sqlite:///./vale_refeicao.db" >> .env
```

5. **Execute**:
```bash
streamlit run app.py
```

## 📁 Estrutura Revolucionária

```
vale-refeicao-ia/
├── 🚀 app.py                          # App principal com layout inteligente
├── 📊 src/
│   ├── 🤖 agents/                     # Agentes autônomos
│   │   ├── extraction_agent.py        # Processamento de dados
│   │   ├── calculation_agent.py       # Cálculos via prompts
│   │   └── log_utils.py              # Logs em tempo real
│   ├── 💾 data/
│   │   ├── database.py               # Gerenciador dinâmico
│   │   └── models.py                 # Modelos simplificados
│   └── 🎨 ui/
│       ├── components.py             # Componentes reutilizáveis
│       └── pages/                    # Páginas da aplicação
│           ├── upload.py             # Upload unificado
│           ├── processing.py         # Processamento dinâmico
│           ├── database_viewer.py    # Visualizador avançado
│           ├── calculations.py       # Cálculos por IA
│           ├── prompts_manager.py    # Gerenciador de prompts
│           └── agent_monitor.py      # Monitor de agentes
├── ⚙️ configurar_sqlite.ps1          # Setup automático
└── 📚 docs/                          # Documentação
```

## 🎯 Como Usar o Novo Sistema

### 1. 📤 **Upload de Dados** (Simplificado)
```
📤 Upload de Dados
├── 📁 Selecione múltiplos arquivos
├── 🔄 Processamento automático
└── 📊 Cada arquivo = 1 tabela dinâmica
```

### 2. 🗃️ **Banco de Dados** (Inteligente)
```
🗃️ Visualizador de Banco de Dados
├── 📊 Tabelas de Dados (com indicadores de PK)
├── 🔗 Correlações (sugestões automáticas)
├── ⚙️ Tabelas do Sistema
└── 🔍 Buscas (Query)
    ├── 🤖 Prompt to Query
    ├── 🧠 Agente Autônomo
    └── 🔍 SQL Avançado
```

### 3. 🧮 **Cálculos** (Revolucionário)
```
🧮 Cálculos Inteligentes com IA
├── ⚙️ Configurar Cálculos
│   ├── 📝 Prompt em linguagem natural
│   ├── 🛠️ Seleção de ferramentas
│   └── 💾 Salvar configuração
├── 🚀 Executar Cálculos
│   ├── 🤖 Agente autônomo executa
│   ├── 🔄 Múltiplas iterações
│   └── 📊 Resultados detalhados
└── 📊 Histórico de Cálculos
```

### 4. 🎯 **Prompts** (Configurável)
```
🎯 Gerenciar Prompts
├── 📝 Editor de prompts
├── 🔧 Configurações de agentes
└── 📚 Biblioteca de prompts
```

## 💰 Tool Especializada: Cálculo de Vale Refeição

### 🎯 **Funcionalidades da Tool VR**
- **🏢 Regras Brasileiras**: Implementa legislação trabalhista do Brasil
- **🗺️ Valores por Estado**: São Paulo (R$ 37,50) vs Outros (R$ 35,00)
- **🚫 Exclusões Automáticas**: Férias, afastamentos, aprendizes, exterior, desligados
- **📊 Múltiplos Formatos**: Detalhado, estatísticas e formato padrão
- **💼 Divisão de Custos**: 80% empresa / 20% funcionário
- **⚡ Processamento**: Loop otimizado por colaborador

### 📋 **Estrutura de Dados Esperada**
```
📊 Tabelas Necessárias:
├── ativos.xlsx              # Lista de colaboradores ativos
│   ├── MATRICULA           # Chave primária
│   ├── NOME                # Nome do colaborador  
│   └── SINDICATO           # Sindicato (detecta SP automaticamente)
├── admissao_abril.xlsx     # Funcionários contratados em abril (NOVO!)
│   ├── MATRICULA           # Chave primária (validação anti-duplicata)
│   ├── NOME                # Nome do contratado
│   └── SINDICATO           # Sindicato para cálculo de valor
├── ferias.xlsx             # Colaboradores de férias
├── afastamentos.xlsx       # Colaboradores afastados
├── aprendiz.xlsx           # Aprendizes (excluídos)
├── exterior.xlsx           # Colaboradores no exterior
├── desligados.xlsx         # Colaboradores desligados
└── base_sindicato_x_valor.xlsx  # Valores por sindicato (opcional)
```

### 🧮 **Lógica de Cálculo Atualizada**
```python
# 1. Carrega colaboradores ativos
ativos = carregar_tabela("ativos")

# 1.1. Adiciona funcionários contratados (se existir tabela)
if tabela_existe("admissao_abril"):
    contratados_abril = carregar_tabela("admissao_abril")
    # Filtra apenas os que NÃO estão em ativos (evita duplicação)
    novos_contratados = contratados_abril[~contratados_abril.MATRICULA.isin(ativos.MATRICULA)]
    # Combina as listas
    ativos = combinar(ativos, novos_contratados)

# 2. Identifica exclusões
exclusoes = {
    "ferias": carregar_matriculas("ferias"),
    "afastamentos": carregar_matriculas("afastamentos"),
    "aprendiz": carregar_matriculas("aprendiz"),
    "exterior": carregar_matriculas("exterior"),
    "desligados": carregar_matriculas("desligados")
}

# 3. Para cada colaborador ativo:
for colaborador in ativos:
    if colaborador.matricula not in exclusoes:
        # Determina valor por estado
        if "SP" in colaborador.sindicato:
            valor_diario = 37.50  # São Paulo
        else:
            valor_diario = 35.00  # Outros estados
        
        # Calcula valor mensal
        valor_total = valor_diario * 22  # 22 dias úteis
        
        # Divide custos
        custo_empresa = valor_total * 0.80      # 80%
        desconto_funcionario = valor_total * 0.20  # 20%
```

### 📊 **Saídas Geradas**
```
📄 Planilha Excel com 3 abas:

1. 📋 CALCULO_VALE_REFEICAO
   ├── MATRICULA, NOME, SINDICATO, ESTADO
   ├── STATUS (ELEGÍVEL/EXCLUÍDO)
   ├── MOTIVO_EXCLUSAO (se aplicável)
   └── DIAS_ELEGIVEL, VALOR_DIARIO, VALOR_TOTAL_VR

2. 📊 ESTATISTICAS_VR
   ├── Total de Colaboradores: 1.815
   ├── Elegíveis SP: 856 (R$ 37,50/dia)
   ├── Elegíveis Outros: 859 (R$ 35,00/dia)
   ├── Excluídos: 100
   ├── Valor Total Geral: R$ 1.342.385,00
   └── Percentuais e médias

3. 📄 FORMATO_PADRAO_VR
   ├── Admissão, Sindicato do Colaborador, Competência
   ├── Dias (22.00), VALOR DIÁRIO VR, TOTAL
   ├── Custo empresa (80%), Desconto profissional (20%)
   └── OBS GERAL (matrícula, nome, estado)
```

## 💰 Ferramenta "Cálculo de Vale Refeição" - Análise Detalhada

### 🎯 **Objetivo Principal**
A ferramenta "Cálculo de Vale Refeição" é um **agente especializado** que automatiza completamente o processo de cálculo de benefícios alimentação seguindo as **regras brasileiras de RH**, eliminando trabalho manual e garantindo precisão total.

### 🔧 **Funcionalidades Principais**

#### 1. **🔍 Análise Automática de Elegibilidade**
- **Carrega colaboradores ativos** da tabela principal
- **➕ Inclui funcionários contratados** da tabela `admissao_abril` que não estejam em `ativos`
- **🚫 Evita duplicações** através de validação cruzada por MATRÍCULA
- **Identifica exclusões automáticas** através de múltiplas tabelas:
  - ❌ Colaboradores de férias
  - ❌ Afastamentos médicos/licenças
  - ❌ Aprendizes (não elegíveis)
  - ❌ Funcionários no exterior
  - ❌ Desligados do quadro
- **Aplica regras de negócio** específicas do RH brasileiro

#### 2. **💰 Cálculo Inteligente por Estado**
- **São Paulo**: R$ 37,50/dia (detecção automática via campo SINDICATO)
- **Outros Estados**: R$ 35,00/dia
- **Valores customizáveis** via tabela `base_sindicato_x_valor.xlsx`
- **22 dias úteis padrão** (configurável)

#### 3. **📊 Geração de Relatórios Completos**
A ferramenta gera **automaticamente** 3 abas Excel:

**📋 Aba "CALCULO_VALE_REFEICAO":**
- Lista completa com todos os colaboradores
- Status de elegibilidade individual
- Motivos de exclusão detalhados
- Valores calculados por pessoa

**📊 Aba "ESTATISTICAS_VR":**
- Totalizadores gerais e por estado
- Percentuais de elegibilidade
- Médias e análises estatísticas
- Resumo executivo para gestão

**📄 Aba "FORMATO_PADRAO_VR":**
- Layout padrão para folha de pagamento
- Divisão de custos (80% empresa / 20% funcionário)
- Campos prontos para importação em sistemas

#### 4. **🧠 Inteligência Artificial Integrada**
- **Detecção automática** de padrões nos dados
- **Sugestões inteligentes** para correções
- **Validação cruzada** entre tabelas
- **Logs detalhados** de todo o processo

#### 5. **⚡ Performance e Escalabilidade**
- Processa **milhares de registros** em segundos
- **Otimizações SQL** para grandes volumes
- **Cache inteligente** para execuções repetidas
- **Exportação automática** sem intervenção manual

### 🎮 **Como Usar**

1. **📤 Upload dos Arquivos**:
   - `ativos.xlsx` - Lista de colaboradores principais
   - `admissao_abril.xlsx` - Funcionários contratados em abril (opcional)
   - `ferias.xlsx`, `afastamentos.xlsx`, etc. - Exclusões

2. **🔄 Processamento Inteligente**:
   - Sistema carrega colaboradores ativos
   - **Adiciona automaticamente** funcionários de `admissao_abril` que não estejam em `ativos`
   - **Valida e remove duplicatas** por MATRÍCULA
   - Logs detalhados de todo o processo

3. **🚀 Execução Automática**:
   - Selecione a configuração "Vale Refeição Padrão"
   - Clique em "Iniciar Cálculo Autônomo"
   - Aguarde o processamento (30-60 segundos)

4. **📊 Resultados**:
   - Excel completo gerado automaticamente
   - Disponível na aba "Exportações"
   - Logs detalhados do processo com contadores por origem

### 💡 **Vantagens Competitivas**

- **🕐 Economia de Tempo**: Processo que levava horas agora leva minutos
- **🎯 Precisão Total**: Elimina erros humanos de cálculo
- **📋 Conformidade**: Segue rigorosamente a legislação brasileira
- **🔄 Reutilizável**: Configurações salvas para uso mensal
- **📊 Transparência**: Logs completos de todas as decisões
- **🔧 Customizável**: Regras adaptáveis para diferentes empresas

## 🧠 Uso de Agentes de IA na Aplicação

### 🎯 **Onde a IA é Utilizada**

A aplicação utiliza **Inteligência Artificial (OpenAI GPT)** em **duas camadas principais**:

#### **1. 🧮 Agente de Cálculo Autônomo (Orquestração IA)**
**Localização:** `src/ui/pages/calculations.py` → `execute_autonomous_calculation()`

```python
# O usuário define um prompt em linguagem natural:
calculation_prompt = f"""
CONTEXTO: Você é um agente especializado em cálculos de benefícios e análises de RH.

OBJETIVO: {config['prompt']}  # Ex: "Calcule vale refeição para todos os funcionários ativos"

FERRAMENTAS DISPONÍVEIS: {', '.join(config['available_tools'])}

INSTRUÇÕES:
1. Analise os dados disponíveis nas tabelas
2. Aplique as regras de cálculo especificadas
3. Gere resultados detalhados e organizados
4. Forneça relatórios com totais e estatísticas

Execute o cálculo de forma autônoma.
"""
```

**🤖 Como a IA funciona aqui:**
- **Recebe prompt** em linguagem natural do usuário
- **Analisa tabelas** disponíveis no banco de dados
- **Cria um plano** de execução estruturado
- **Executa iterações** até completar o objetivo
- **Decide quais ferramentas** usar em cada etapa
- **Chama a tool específica** (ex: `calculo_vale_refeicao_tool`)

#### **2. 🔄 Agente Autônomo Multi-Iterativo (Decisão IA)**
**Localização:** `src/ui/pages/database_viewer.py` → `execute_autonomous_agent()`

```python
# IA configurada com OpenAI GPT
llm = OpenAI(
    api_key=settings.openai_api_key,
    model=settings.openai_model,  # Ex: gpt-4
    temperature=0.3,
    request_timeout=60.0,
    max_retries=3
)

# IA decide a próxima ação baseada no contexto
action_prompt = f"""
OBJETIVO: {objective}
TABELAS: {tables_available}
PASSO ATUAL: {current_step}

Responda APENAS JSON:
{{
"action_type": "sql_query" | "calculo_vale_refeicao" | "excel_export",
"target_table": "nome_da_tabela",
"description": "o que está fazendo",
"analysis_complete": true/false
}}
"""

# IA responde e sistema executa a ação
response = llm.complete(action_prompt)
action_plan = json.loads(response.text)
```

**🤖 Como a IA funciona aqui:**
- **Planeja estratégia** baseada no objetivo
- **Decide próxima ação** em cada iteração
- **Escolhe tabelas relevantes** para consultar
- **Determina quando usar** ferramentas específicas
- **Adapta-se aos resultados** de etapas anteriores
- **Finaliza quando** objetivo é atingido

#### **3. 💰 Tool de Cálculo Vale Refeição (Lógica Determinística)**
**Localização:** `src/ui/pages/database_viewer.py` → `calculo_vale_refeicao_tool()`

⚠️ **IMPORTANTE:** Esta tool **NÃO usa IA diretamente**. Ela implementa **lógica de negócio determinística**:

```python
def calculo_vale_refeicao_tool(db, data_tables: list) -> dict:
    """
    Tool especializada para cálculo de vale refeição
    Implementa a lógica de negócio específica do RH brasileiro
    """
    # 1. Carrega dados (SEM IA)
    ativos_df = pd.read_sql('SELECT * FROM "ativos"', db.engine)
    
    # 2. Aplica regras fixas (SEM IA)
    if ' SP ' in sindicato_upper:
        valor_diario = 37.50  # São Paulo
    else:
        valor_diario = 35.00  # Outros estados
    
    # 3. Calcula valores (SEM IA)
    valor_total_vr = valor_diario * 22  # 22 dias úteis
    
    # 4. Gera relatório Excel (SEM IA)
    return export_to_excel(resultados)
```

**🔧 Por que não usa IA:**
- **Precisão garantida** - cálculos financeiros devem ser exatos
- **Conformidade legal** - regras trabalhistas são fixas
- **Auditoria** - resultados devem ser reproduzíveis
- **Performance** - processamento rápido de milhares de registros

### 🔄 **Fluxo Completo com IA**

```mermaid
graph TD
    A[👤 Usuário define prompt] --> B[🧠 IA Orquestradora]
    B --> C[🧠 IA Autônoma planeja]
    C --> D[🧠 IA decide próxima ação]
    D --> E{Qual ação?}
    E -->|SQL Query| F[📊 Consulta dados]
    E -->|Cálculo VR| G[💰 Tool determinística]
    E -->|Export Excel| H[📊 Gera relatório]
    F --> I[🧠 IA avalia resultado]
    G --> I
    H --> I
    I --> J{Objetivo completo?}
    J -->|Não| D
    J -->|Sim| K[✅ Finaliza]
```

### 🎯 **Resumo: IA vs Lógica Determinística**

| Componente | Usa IA? | Função da IA | Por que? |
|------------|---------|--------------|----------|
| **Orquestração** | ✅ SIM | Interpreta prompts, planeja execução | Flexibilidade e adaptação |
| **Decisão de Ações** | ✅ SIM | Escolhe próximos passos | Autonomia inteligente |
| **Cálculo VR** | ❌ NÃO | Apenas chama a tool | IA decide QUANDO usar |
| **Tool VR** | ❌ NÃO | Lógica de negócio fixa | Precisão e conformidade |
| **Geração SQL** | ✅ SIM | Cria queries baseadas no contexto | Adaptação aos dados |
| **Exportação** | ❌ NÃO | Formatação padronizada | Consistência de formato |

### 💡 **Vantagens desta Arquitetura**

- **🧠 Inteligência** onde precisa (planejamento, adaptação)
- **🎯 Determinismo** onde importa (cálculos, compliance)
- **🔄 Flexibilidade** para novos cenários
- **⚡ Performance** otimizada
- **🔍 Transparência** total com logs

## 🤖 Exemplos de Uso dos Agentes

### 🔍 **Consulta com IA**
```
Pergunta: "Quantos funcionários ganham mais de R$ 5.000 por departamento?"

Agente:
1. 🔍 Analisa pergunta
2. 📊 Identifica tabelas necessárias
3. 🔍 Gera SQL: SELECT departamento, COUNT(*) FROM funcionarios WHERE salario > 5000 GROUP BY departamento
4. ⚡ Executa e apresenta resultados
```

### 🧮 **Cálculo Autônomo**
```
Prompt: "Atue como especialista de RH e calculista de vale refeições no Brasil.
A tabela ativos indica colaboradores e se relaciona com as demais pela MATRICULA.
Gere planilha com colaboradores ativos que tenham direito a vale refeição.
Não se paga para colaboradores de férias, aprendizes, afastados, no exterior ou desligados.
Considere um mês de 22 dias úteis."

Agente:
1. 📋 Planeja análise (9 etapas específicas)
2. 📊 Carrega colaboradores ativos (1.815 registros)
3. 🚫 Identifica exclusões (100 excluídos)
4. 💰 Aplica valores por estado (SP: R$ 37,50 | Outros: R$ 35,00)
5. 🧮 Calcula valores (22 dias × valor diário)
6. 📊 Gera 3 abas Excel: Cálculo + Estatísticas + Formato Padrão
7. ✅ Total: R$ 1.342.385,00 (1.715 elegíveis)
```

### 🧠 **Análise Complexa**
```
Pergunta: "Analise padrões salariais e identifique anomalias"

Agente:
1. 🔍 Explora estrutura dos dados
2. 📊 Calcula estatísticas descritivas
3. 🔍 Identifica outliers
4. 📈 Analisa distribuições
5. 💡 Gera insights e recomendações
```

## ⚙️ Configuração Avançada

### 🔑 **Variáveis de Ambiente**
```env
# IA
OPENAI_API_KEY=sk-sua-chave-openai
OPENAI_MODEL=gpt-4o

# Banco (SQLite padrão)
DATABASE_URL=sqlite:///./vale_refeicao.db

# Debug
DEBUG=false
```

### 🛠️ **Ferramentas dos Agentes**
```python
Ferramentas Disponíveis:
├── 🔍 Análise de Dados
│   ├── sql_query          # Consultas SQL
│   ├── data_exploration   # Análise exploratória
│   ├── data_correlation   # Correlações
│   └── data_quality       # Qualidade dos dados
├── 🧮 Cálculos
│   ├── calculo_vale_refeicao   # 💰 Cálculo especializado VR
│   ├── mathematical_operations  # Operações matemáticas
│   ├── conditional_logic       # Lógica condicional
│   ├── aggregations           # Agregações
│   └── report_generation      # Relatórios
└── 📊 Exportação
    ├── excel_export       # Planilhas Excel
    ├── csv_export         # Arquivos CSV
    └── json_export        # Dados JSON
```

## 📊 Monitoramento em Tempo Real

### 🔄 **Logs de Agentes**
- **📱 Coluna lateral**: Atividades em tempo real
- **🔍 Detalhamento**: Cada etapa do processo
- **⏱️ Timestamps**: Rastreamento temporal
- **🧹 Limpeza**: Histórico gerenciável

### 📈 **Métricas do Sistema**
- **📊 Tabelas**: Dinâmicas vs Sistema
- **🔑 Chaves Primárias**: Status e sugestões
- **⚙️ Configurações**: Prompts ativos
- **🤖 Agentes**: Execuções e performance

## 🔐 Segurança e Validação

### 🛡️ **SQL Seguro**
- **✅ Apenas SELECT**: Consultas somente leitura
- **🚫 Comandos Perigosos**: Bloqueio automático
- **🔍 Validação**: Sintaxe e segurança
- **📊 Sandbox**: Execução isolada

### 🔒 **Dados Protegidos**
- **💾 SQLite Local**: Dados não saem da máquina
- **🔐 Sem Exposição**: API keys protegidas
- **📝 Logs Auditáveis**: Rastreamento completo
- **🧹 Limpeza Automática**: Remoção de dados antigos

## 🚀 Casos de Uso

### 💼 **RH e Folha de Pagamento**
```
📊 Upload: ativos.xlsx, ferias.xlsx, afastamentos.xlsx, base_sindicato_x_valor.xlsx
🤖 Agente: "Calcule vale refeição seguindo regras brasileiras de RH"
📈 Resultado: 
   ├── 📋 Planilha detalhada (1.815 colaboradores)
   ├── 📊 Estatísticas por estado (SP vs Outros)
   ├── 📄 Formato padrão (80% empresa / 20% funcionário)
   └── 💰 Total: R$ 1.342.385,00
```

### 📈 **Análise Financeira**
```
📊 Upload: vendas.csv, custos.csv, metas.xlsx
🤖 Agente: "Analise performance vs metas por região"
📈 Resultado: Dashboard com recomendações
```

### 🏢 **Gestão Operacional**
```
📊 Upload: producao.xlsx, qualidade.csv, recursos.xlsx
🤖 Agente: "Identifique gargalos e oportunidades"
📈 Resultado: Análise detalhada com plano de ação
```

## 🔄 Roadmap

### 🎯 **Próximas Funcionalidades**
- [ ] 🔗 **Conectores**: APIs externas (ERP, CRM)
- [ ] 📊 **Dashboards**: Visualizações interativas
- [ ] 🤖 **Agentes Especializados**: Por domínio de negócio
- [ ] 🔄 **Automação**: Execução agendada
- [ ] 📱 **Mobile**: Interface responsiva
- [ ] 🌐 **Multi-tenant**: Múltiplas organizações

### 🧠 **IA Avançada**
- [ ] 🎯 **Prompt Engineering**: Templates inteligentes
- [ ] 📚 **Knowledge Base**: Aprendizado contínuo
- [ ] 🔍 **RAG**: Recuperação de contexto
- [ ] 🤖 **Multi-Agent**: Colaboração entre agentes

## 🤝 Contribuindo

### 🛠️ **Como Contribuir**
1. 🍴 Fork o projeto
2. 🌿 Crie sua branch (`git checkout -b feature/NovaFuncionalidade`)
3. 💾 Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. 📤 Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. 🔄 Abra um Pull Request

### 📋 **Diretrizes**
- **🧪 Testes**: Inclua testes para novas funcionalidades
- **📚 Documentação**: Atualize README e docs
- **🎯 Prompts**: Teste com diferentes tipos de dados
- **🤖 Agentes**: Valide comportamento autônomo

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- **🤖 OpenAI**: Pela API GPT-4 que alimenta nossos agentes
- **🦙 LlamaIndex**: Framework para agentes inteligentes
- **🎨 Streamlit**: Interface web intuitiva e poderosa
- **🐍 Python**: Linguagem que torna tudo possível
- **💾 SQLite**: Banco de dados simples e eficiente

---

## 🚀 **Comece Agora!**

```bash
git clone https://github.com/seu-usuario/vale-refeicao-ia.git
cd vale-refeicao-ia
.\configurar_sqlite.ps1  # Windows
streamlit run app.py
```

**Transforme seus dados em insights com o poder dos Agentes de IA Autônomos!** 🤖✨