# 💳 Sistema de Vale Refeição com IA

Sistema inteligente para cálculo e gestão de vale refeição usando Streamlit e LlamaIndex, com agentes de IA especializados para processamento de dados de RH.

## 🌟 Funcionalidades

- **📤 Upload Inteligente**: Processamento de múltiplas planilhas Excel/CSV
- **🤖 Agentes IA Especializados**:
  - **Extraction Agent**: Extração e limpeza automática de dados
  - **Calculation Agent**: Cálculo inteligente de vale refeição
  - **Report Agent**: Geração de relatórios e insights
- **🔗 Unificação por Matrícula**: Integração automática de dados usando MATRICULA como chave
- **💾 Armazenamento Persistente**: PostgreSQL + ChromaDB para dados e conhecimento
- **📊 Visualizações Interativas**: Dashboards e gráficos com Plotly
- **📄 Exportação**: Relatórios em PDF e Excel

## 🏗️ Arquitetura

```mermaid
graph TB
    subgraph "Frontend"
        UI[Streamlit UI]
    end
    
    subgraph "Agentes LlamaIndex"
        EA[Extraction Agent]
        CA[Calculation Agent]
        RA[Report Agent]
    end
    
    subgraph "Storage"
        DB[(PostgreSQL)]
        VS[ChromaDB]
    end
    
    UI --> EA
    EA --> DB
    DB --> CA
    CA --> RA
    EA --> VS
    CA --> VS
```

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+
- PostgreSQL
- OpenAI API Key

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/vale-refeicao-ia.git
cd vale-refeicao-ia
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute a aplicação:
```bash
streamlit run app.py
```

## 📁 Estrutura do Projeto

```
vale-refeicao-ia/
├── app.py                    # Aplicação principal
├── src/
│   ├── agents/              # Agentes LlamaIndex
│   ├── data/                # Modelos e schemas
│   ├── ui/                  # Interface Streamlit
│   └── utils/               # Utilidades
├── prompts/                 # Prompts dos agentes
├── tests/                   # Testes
└── docs/                    # Documentação
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/vale_refeicao

# OpenAI
OPENAI_API_KEY=sk-...

# Configurações de VR
VALOR_DIA_UTIL=35.00
DESCONTO_FUNCIONARIO_PCT=0.20
```

### Banco de Dados

Execute as migrações para criar as tabelas:

```bash
alembic upgrade head
```

## 📊 Uso

### 1. Upload de Dados

- Faça upload das planilhas de RH
- O sistema identificará automaticamente as colunas
- Use MATRICULA como chave de unificação

### 2. Processamento

- O Extraction Agent limpa e normaliza os dados
- Validação automática de CPF, datas, valores
- Detecção de inconsistências

### 3. Cálculo

- O Calculation Agent aplica as regras de negócio
- Cálculo proporcional para admissões/demissões
- Desconto de faltas automático

### 4. Relatórios

- Visualize resultados por departamento
- Exporte para PDF ou Excel
- Insights gerados por IA

## 🤖 Agentes IA

### Extraction Agent

Responsável por:
- Detectar e mapear colunas automaticamente
- Limpar e normalizar dados
- Validar informações
- Aprender padrões para melhorar processamentos futuros

### Calculation Agent

Responsável por:
- Aplicar regras de elegibilidade
- Calcular valores de VR
- Aplicar descontos e ajustes
- Validar cálculos

### Report Agent

Responsável por:
- Gerar relatórios executivos
- Criar visualizações
- Identificar anomalias
- Sugerir otimizações

## 📈 Monitoramento

O sistema registra todas as ações dos agentes para auditoria e melhoria contínua:

- Logs detalhados de processamento
- Métricas de performance
- Histórico de cálculos
- Aprendizados armazenados

## 🔐 Segurança

- Dados sensíveis criptografados
- Autenticação de usuários
- Logs de auditoria
- Backup automático

## 🐳 Docker

Para executar com Docker:

```bash
docker-compose up
```

## 📚 Documentação

Documentação completa disponível em `docs/`:

- [Guia de Instalação](docs/INSTALL.md)
- [Manual do Usuário](docs/USER_GUIDE.md)
- [API Reference](docs/API.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Sistema desenvolvido com ❤️ usando Streamlit e LlamaIndex

## 🙏 Agradecimentos

- OpenAI pela API GPT-4
- Streamlit pela excelente framework
- LlamaIndex pela abstração de agentes IA
