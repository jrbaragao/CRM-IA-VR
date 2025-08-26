# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o Sistema de Vale Refeição IA! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Como Contribuir

### 1. Reportando Bugs

Antes de criar um novo issue:
- Verifique se o bug já foi reportado
- Use o template de issue para bugs
- Inclua informações detalhadas:
  - Descrição clara do problema
  - Passos para reproduzir
  - Comportamento esperado vs atual
  - Screenshots se aplicável
  - Ambiente (OS, Python version, etc.)

### 2. Sugerindo Melhorias

- Use o template de feature request
- Explique claramente a funcionalidade
- Descreva o problema que resolve
- Forneça exemplos de uso

### 3. Pull Requests

#### Processo de Desenvolvimento

1. **Fork o repositório**
   ```bash
   git clone https://github.com/seu-usuario/vale-refeicao-ia.git
   cd vale-refeicao-ia
   ```

2. **Crie uma branch para sua feature**
   ```bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/nome-do-fix
   ```

3. **Configure o ambiente de desenvolvimento**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dependências de desenvolvimento
   ```

4. **Faça suas mudanças**
   - Siga o estilo de código do projeto
   - Adicione testes quando aplicável
   - Atualize a documentação se necessário

5. **Execute os testes**
   ```bash
   pytest tests/
   flake8 src/
   mypy src/
   ```

6. **Commit suas mudanças**
   ```bash
   git add .
   git commit -m "tipo: descrição concisa
   
   Descrição detalhada do que foi feito e por quê."
   ```

#### Convenção de Commits

Use o formato [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Formatação, ponto e vírgula faltando, etc.
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Tarefas de manutenção

Exemplos:
```
feat: adicionar exportação para Excel
fix: corrigir cálculo de dias úteis
docs: atualizar README com novos exemplos
```

### 4. Estilo de Código

#### Python
- Seguimos PEP 8
- Use type hints quando possível
- Docstrings para todas as funções públicas
- Máximo 88 caracteres por linha (Black formatter)

Exemplo:
```python
def calcular_vale_refeicao(
    funcionario: Dict[str, Any],
    dias_uteis: int,
    valor_dia: float = 35.0
) -> Dict[str, float]:
    """
    Calcula o valor do vale refeição para um funcionário.
    
    Args:
        funcionario: Dados do funcionário
        dias_uteis: Número de dias úteis no mês
        valor_dia: Valor por dia de VR
        
    Returns:
        Dicionário com valores calculados
    """
    # Implementação...
```

#### Streamlit
- Componentes reutilizáveis em `src/ui/components.py`
- Páginas separadas em `src/ui/pages/`
- Use session state para gerenciar estado

### 5. Documentação

- Atualize o README.md se adicionar funcionalidades
- Documente APIs novas em `docs/API.md`
- Adicione exemplos de uso quando relevante

### 6. Testes

- Escreva testes para novas funcionalidades
- Mantenha cobertura de testes > 80%
- Use pytest para testes unitários
- Testes de integração para agentes IA

Estrutura de testes:
```python
def test_extraction_agent_column_mapping():
    """Testa mapeamento de colunas pelo agente de extração"""
    agent = ExtractionAgent()
    df = pd.DataFrame({'Nome Completo': ['João'], 'Matrícula': ['123']})
    
    result = agent._detect_and_map_columns(df)
    
    assert 'NOME' in result.columns
    assert 'MATRICULA' in result.columns
```

## 🔍 Revisão de Código

### O que procuramos em PRs:

- ✅ Código limpo e bem documentado
- ✅ Testes adequados
- ✅ Sem conflitos com a branch main
- ✅ Commits bem organizados
- ✅ Performance considerada
- ✅ Segurança (sem dados sensíveis)

### Processo de Revisão:

1. Automated checks (CI/CD)
2. Revisão de código por maintainers
3. Discussão e iterações se necessário
4. Aprovação e merge

## 🎯 Áreas Prioritárias

Estamos especialmente interessados em contribuições nas seguintes áreas:

- 🧪 Testes (unitários e integração)
- 📚 Documentação e exemplos
- 🎨 Melhorias na UI/UX
- 🔧 Otimização de performance
- 🌐 Internacionalização
- 🔒 Segurança e validação de dados

## 📞 Comunicação

- Use issues para discussões técnicas
- Seja respeitoso e construtivo
- Ajude outros contribuidores
- Celebre as conquistas!

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto.

---

Obrigado por fazer o Sistema de Vale Refeição IA melhor! 🚀
