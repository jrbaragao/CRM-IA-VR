"""
Executor seguro de código Python para análises de dados
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Tuple
import streamlit as st
from datetime import datetime
import json
import re


class SafePythonExecutor:
    """Executor seguro de código Python com sandbox limitado"""
    
    def __init__(self, data_tables: Dict[str, pd.DataFrame]):
        """
        Inicializa o executor com as tabelas disponíveis
        
        Args:
            data_tables: Dicionário com nome_tabela -> DataFrame
        """
        self.data_tables = data_tables
        self.execution_results = []
        self.plots = []
        self.insights = []
        
        # Configurar matplotlib
        plt.ioff()
        sns.set_style("whitegrid")
        
    def create_safe_globals(self) -> Dict[str, Any]:
        """Cria ambiente global seguro para execução"""
        
        # Funções permitidas
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool,
            'dict': dict, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'int': int, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'print': print,
            'range': range, 'round': round, 'set': set, 'sorted': sorted,
            'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
            'zip': zip,
            '__import__': __import__,  # Necessário para imports
            'isinstance': isinstance,  # Útil para verificação de tipos
            'hasattr': hasattr,  # Útil para verificar atributos
            'getattr': getattr,  # Útil para acessar atributos
            'globals': globals,  # Para acessar variáveis globais
            'locals': locals,  # Para acessar variáveis locais
            # Exceções e tratamento de erros
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
        }
        
        # Ambiente global com bibliotecas e dados
        safe_globals = {
            '__builtins__': safe_builtins,
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'datetime': datetime,
            'json': json,
            'warnings': __import__('warnings'),  # Para suprimir warnings
            # Funções matemáticas adicionais
            'math': __import__('math'),
            'statistics': __import__('statistics'),
            # Adicionar tabelas de dados
            **self.data_tables,
            # Funções auxiliares
            'save_plot': self._save_plot,
            'add_insight': self._add_insight,
            'show_results': self._show_results,
            # Criar uma classe wrapper para a lista de plots
            'PlotsList': self._create_plots_list_class(),
            # Listas para resultados - importante para acesso no código executado
            'execution_results': self.execution_results,
            'plots': self._create_plots_wrapper(),
            'insights': self.insights,
        }
        
        return safe_globals
    
    def _create_plots_list_class(self):
        """Cria uma classe que herda de list mas intercepta append"""
        parent = self
        
        class PlotsList(list):
            def append(self, item):
                # Log de tentativa de adicionar plot
                if 'st' in globals() and hasattr(globals()['st'], 'session_state'):
                    if 'agent_logs' in globals()['st'].session_state:
                        globals()['st'].session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'plots_list',
                            'action': '🎨 Tentando adicionar item à lista de plots',
                            'details': f'Tipo do item: {type(item)}, hasattr savefig: {hasattr(item, "savefig")}'
                        })
                
                # Se for uma figura matplotlib
                if hasattr(item, 'savefig'):
                    try:
                        buffer = io.BytesIO()
                        item.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                        buffer.seek(0)
                        plot_base64 = base64.b64encode(buffer.read()).decode()
                        plt.close(item)
                        
                        super().append({
                            'title': 'Plot',
                            'image': plot_base64,
                            'timestamp': datetime.now()
                        })
                        
                        # Log
                        if 'st' in globals() and hasattr(globals()['st'], 'session_state'):
                            if 'agent_logs' in globals()['st'].session_state:
                                globals()['st'].session_state['agent_logs'].append({
                                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                                    'agent': 'plot_converter',
                                    'action': '✅ PLOT SALVO COM SUCESSO!',
                                    'details': f'Figura matplotlib convertida para base64. Tamanho: {len(plot_base64)} bytes'
                                })
                    except Exception as e:
                        parent.execution_results.append(f"Erro ao converter figura: {str(e)}")
                # Se já for um dicionário válido
                elif isinstance(item, dict) and 'image' in item:
                    super().append(item)
                else:
                    # Tentar tratar como figura
                    try:
                        if hasattr(plt, 'figure') and isinstance(item, plt.Figure):
                            # É uma figura matplotlib
                            buffer = io.BytesIO()
                            item.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                            buffer.seek(0)
                            plot_base64 = base64.b64encode(buffer.read()).decode()
                            plt.close(item)
                            
                            super().append({
                                'title': 'Plot',
                                'image': plot_base64,
                                'timestamp': datetime.now()
                            })
                    except:
                        parent.execution_results.append(f"Aviso: não foi possível adicionar item do tipo {type(item)} aos plots")
        
        return PlotsList
    
    def _create_plots_wrapper(self):
        """Cria um wrapper para a lista de plots que intercepta append"""
        PlotsList = self._create_plots_list_class()
        wrapped_plots = PlotsList()
        # Copiar referência para a lista original
        for item in self.plots:
            wrapped_plots.append(item)
        # Substituir a lista original
        self.plots = wrapped_plots
        return self.plots
    
    def _save_plot(self, title: str = "Plot"):
        """Salva o plot atual"""
        try:
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            self.plots.append({
                'title': title,
                'image': plot_base64,
                'timestamp': datetime.now()
            })
            
            # Log para debug
            if 'st' in globals() and hasattr(globals()['st'], 'session_state'):
                if 'agent_logs' in globals()['st'].session_state:
                    globals()['st'].session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'plot_saver',
                        'action': f'📊 Plot salvo: {title}',
                        'details': f'Tamanho da imagem: {len(plot_base64)} bytes'
                    })
        except Exception as e:
            self.execution_results.append(f"Erro ao salvar plot: {str(e)}")
    
    def _add_insight(self, insight: str, category: str = "geral"):
        """Adiciona um insight à lista"""
        self.insights.append({
            'text': insight,
            'category': category,
            'timestamp': datetime.now()
        })
    
    def _show_results(self, data: Any, title: str = "Resultado"):
        """Adiciona resultado à lista de execução"""
        self.execution_results.append({
            'title': title,
            'data': data,
            'type': type(data).__name__
        })
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Executa código Python de forma segura
        
        Args:
            code: Código Python a ser executado
            
        Returns:
            Dict com resultados da execução
        """
        # Log antes de executar
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'python_executor',
                'action': '🏃 Iniciando execução do código Python',
                'details': f"Código com {len(code)} caracteres, {len(self.data_tables)} tabelas disponíveis: {list(self.data_tables.keys())}"
            })
        
        # Limpar resultados anteriores
        self.execution_results = []
        self.plots = []
        self.insights = []
        
        # Capturar saída
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            # Criar ambiente seguro
            safe_globals = self.create_safe_globals()
            
            # Debug: verificar se as tabelas estão no ambiente
            table_keys = [k for k in safe_globals.keys() if isinstance(safe_globals.get(k), pd.DataFrame)]
            if 'agent_logs' in st.session_state and table_keys:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_executor',
                    'action': '📊 DataFrames no ambiente',
                    'details': f"Tabelas disponíveis: {table_keys}"
                })
            
            # Executar código
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, safe_globals)
            
            # Capturar saídas
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            
            # Capturar resultados do ambiente global após execução
            # Isso é importante caso o código tenha modificado as listas diretamente
            if 'execution_results' in safe_globals:
                # Se é um dicionário, converter para lista de resultados
                exec_results = safe_globals['execution_results']
                if isinstance(exec_results, dict) and exec_results not in self.execution_results:
                    self.execution_results.append(exec_results)
                elif isinstance(exec_results, list):
                    self.execution_results = exec_results
            
            # Log após execução bem-sucedida
            if 'agent_logs' in st.session_state:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_executor',
                    'action': '✅ Execução concluída',
                    'details': f'Plots salvos: {len(self.plots)}, Insights: {len(self.insights)}, Results: {len(self.execution_results)}'
                })
            
            return {
                'success': True,
                'stdout': stdout_output,
                'stderr': stderr_output,
                'results': self.execution_results,
                'plots': self.plots,
                'insights': self.insights
            }
            
        except Exception as e:
            # Capturar erro completo
            error_trace = traceback.format_exc()
            
            # Log de erro detalhado
            if 'agent_logs' in st.session_state:
                # Extrair linha do erro se possível
                error_lines = error_trace.split('\n')
                error_summary = str(e)
                
                # Tentar encontrar a linha específica do erro
                for line in error_lines:
                    if 'line' in line.lower() and '.py' not in line:
                        error_summary += f"\n{line.strip()}"
                        break
                
                # Pegar também o stdout até o erro
                stdout_so_far = stdout_buffer.getvalue()
                stderr_so_far = stderr_buffer.getvalue()
                
                error_details = []
                error_details.append(f"ERRO: {error_summary}")
                error_details.append(f"TIPO: {type(e).__name__}")
                
                if stdout_so_far:
                    error_details.append(f"\nSTDOUT ATÉ O ERRO:\n{stdout_so_far[:200]}...")
                    
                if stderr_so_far:
                    error_details.append(f"\nSTDERR:\n{stderr_so_far[:200]}...")
                    
                error_details.append(f"\nTRACEBACK:\n{error_trace[:500]}")
                
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_executor',
                    'action': '❌ Erro na execução do código',
                    'details': '\n'.join(error_details)
                })
            
            return {
                'success': False,
                'stdout': stdout_buffer.getvalue(),
                'stderr': stderr_buffer.getvalue(),
                'results': self.execution_results,
                'plots': self.plots,
                'insights': self.insights,
                'error': str(e),
                'traceback': error_trace
            }
        finally:
            # Fechar buffers
            stdout_buffer.close()
            stderr_buffer.close()
            # Fechar qualquer plot aberto
            plt.close('all')


def validate_generated_code(code: str) -> Tuple[bool, str]:
    """
    Valida código Python gerado por segurança
    
    Returns:
        (is_safe, error_message)
    """
    # Lista de padrões realmente perigosos com verificação mais específica
    dangerous_patterns = [
        (r'\bexec\s*\(', 'exec'),  # exec( mas não execution_results
        (r'\beval\s*\(', 'eval'),
        (r'__import__\s*\(', '__import__'),
        (r'\bcompile\s*\(', 'compile'),
        (r'\bopen\s*\(', 'open'),
        (r'\bfile\s*\(', 'file'),
        (r'\binput\s*\(', 'input'), 
        (r'os\.system', 'os.system'),
        (r'subprocess', 'subprocess'),
        (r'socket', 'socket'),
        (r'urllib', 'urllib'),
        (r'requests\.', 'requests'),
        (r'sys\.exit', 'sys.exit'),
        (r'__builtins__', '__builtins__'),
        (r'__globals__', '__globals__'),
        (r'__locals__', '__locals__'),
        (r'globals\s*\(\)', 'globals()'),
        (r'locals\s*\(\)', 'locals()'),
    ]
    
    # Verificar padrões perigosos com regex
    import re
    for pattern, name in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Código contém padrão potencialmente perigoso: {name}"
    
    # Verificar se usa apenas as variáveis esperadas
    required_vars = ['df', 'insights', 'plots', 'execution_results', 'pd', 'np', 'plt', 'sns']
    
    # Validação básica de sintaxe
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return False, f"Erro de sintaxe: {str(e)}"
    
    return True, ""

def generate_eda_code_with_llm(question: str, table_info: Dict[str, List[str]], llm=None) -> str:
    """
    Gera código Python usando LLM (GPT-4 ou superior)
    """
    # Se não passou LLM, criar um
    if llm is None:
        from llama_index.llms.openai import OpenAI
        from ..config.settings import Settings
        settings = Settings()
        
        # Usar o modelo mais recente disponível
        model = settings.openai_model
        if "gpt-4" not in model:
            model = "gpt-4-turbo-preview"  # Forçar GPT-4
        
        llm = OpenAI(
            api_key=settings.openai_api_key,
            model=model,
            temperature=0.3
        )
    
    # Preparar informações das tabelas
    table_name = list(table_info.keys())[0] if table_info else 'df'
    columns = table_info.get(table_name, []) if table_info else []
    
    # Prompt para gerar código
    prompt = f"""
Você é um especialista em análise de dados com Python. 
Gere código Python para responder a seguinte pergunta:

PERGUNTA: {question}

DADOS DISPONÍVEIS:
- DataFrame: {table_name}
- Colunas: {', '.join(columns[:20])}{'...' if len(columns) > 20 else ''}

IMPORTANTE: Se a pergunta menciona colunas que não existem exatamente (ex: AMONT ao invés de AMOUNT), 
procure por colunas similares usando busca case-insensitive e correção de digitação.

REQUISITOS DO CÓDIGO:
1. Use apenas: pandas (pd), numpy (np), matplotlib.pyplot (plt), seaborn (sns)
2. O DataFrame já está disponível como '{table_name}'
3. Adicione resultados à lista 'execution_results' como dicionários com 'title' e 'data'
4. Adicione insights textuais à lista 'insights' 
5. IMPORTANTE PARA GRÁFICOS: Após criar um plot com plt, SEMPRE chame:
   plots.append(plt.gcf())  # Adiciona o gráfico atual à lista
   OU
   save_plot("Título do Gráfico")  # Função auxiliar que salva o plot
6. Use print() para debug
7. Trate erros com try/except
8. Para estatísticas, calcule média, mediana, desvio padrão quando relevante
9. Para visualizações, crie gráficos informativos com labels
10. NÃO use: exec, eval, compile, open, __import__, subprocess, os.system
11. NÃO acesse __builtins__, __globals__, __locals__
12. Use APENAS as variáveis e funções mencionadas acima
13. IMPORTANTE: Verifique ortografia dos nomes de colunas (use .columns para ver lista)
14. Para perguntas simples, mantenha o código simples e direto

ESTRUTURA DO CÓDIGO:
```python
# Inicialização (já feita)
# df = {table_name}  # DataFrame já disponível
# insights = []      # Lista para insights
# plots = []         # Lista para gráficos  
# execution_results = []  # Lista para resultados

# Primeiro, verificar colunas disponíveis
print("Colunas disponíveis:", {table_name}.columns.tolist())
print("Tipos de dados:", {table_name}.dtypes.to_dict())

# Seu código aqui

# EXEMPLO de busca inteligente de colunas:
# # Função para encontrar coluna similar
# def find_column(df, nome_procurado):
#     nome_lower = nome_procurado.lower()
#     for col in df.columns:
#         if nome_lower in col.lower() or col.lower() in nome_lower:
#             return col
#     # Se não encontrou, procurar por similaridade
#     for col in df.columns:
#         if any(parte in col.lower() for parte in nome_lower.split('_')):
#             return col
#     return None
# 
# # Exemplo de uso para scatter plot:
# col_amount = find_column(df, 'AMOUNT')
# col_time = find_column(df, 'TIME')
# 
# if col_amount and col_time:
#     # Criar scatter plot
#     plt.figure(figsize=(10, 6))
#     plt.scatter(df[col_time], df[col_amount], alpha=0.5)
#     plt.xlabel(col_time)
#     plt.ylabel(col_amount)
#     plt.title(f'Scatter Plot: {{col_time}} vs {{col_amount}}')
#     plt.grid(True, alpha=0.3)
#     
#     # IMPORTANTE: Salvar o plot
#     plots.append(plt.gcf())  # ou save_plot("Scatter TIME vs AMOUNT")
#     
#     # Calcular correlação
#     correlacao = df[col_amount].corr(df[col_time])
#     execution_results.append({{'title': 'Correlação', 'data': correlacao}})
#     insights.append(f"Correlação entre {{col_amount}} e {{col_time}}: {{correlacao:.4f}}")
```

IMPORTANTE: Sempre verifique se a coluna existe antes de usá-la.
Use try/except para capturar erros e adicionar mensagens úteis.

Gere APENAS o código Python, sem explicações adicionais.
"""
    
    try:
        response = llm.complete(prompt)
        code = response.text.strip()
        
        # Remover marcadores de código se existirem
        if '```python' in code:
            code = code.split('```python')[1].split('```')[0]
        elif '```' in code:
            code = code.split('```')[1].split('```')[0]
        
        # Validar código gerado
        is_safe, error_msg = validate_generated_code(code)
        if not is_safe:
            # Se não for seguro, usar template padrão
            if 'agent_logs' in st.session_state:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'code_generator',
                    'action': '⚠️ Código rejeitado por segurança',
                    'details': f"Motivo: {error_msg}\nUsando template seguro como fallback"
                })
            print(f"Código gerado falhou na validação: {error_msg}")
            return generate_eda_code_fallback(question, table_info)
        
        # Adicionar inicializações se não existirem
        if 'execution_results = []' not in code and 'execution_results =' not in code:
            code = f"execution_results = []\n{code}"
        if 'insights = []' not in code and 'insights =' not in code:
            code = f"insights = []\n{code}" 
        if 'plots = []' not in code and 'plots =' not in code:
            code = f"plots = []\n{code}"
        
        # Adicionar acesso ao DataFrame
        final_code = f"""
# DataFrame disponível
df = {table_name}

{code}

# Garantir que pelo menos um resultado seja retornado
if not execution_results and not insights:
    insights.append("Análise concluída")
"""
        
        # Log do código real gerado pelo LLM
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'code_generator',
                'action': '🎯 Código LLM Gerado (Real) - COMPLETO',
                'details': f"Pergunta: {question}\n\n{code}"  # Mostrar código completo
            })
            
            # Verificar se o código contém comandos de plot
            has_plot_save = ('plots.append' in final_code or 'save_plot' in final_code)
            if 'scatter' in question.lower() or 'plot' in question.lower() or 'gráfico' in question.lower():
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'code_validator',
                    'action': '🔍 Verificação de salvamento de plot',
                    'details': f"Código {'✅ CONTÉM' if has_plot_save else '❌ NÃO CONTÉM'} comando para salvar plot (plots.append ou save_plot)"
                })
        
        return final_code
        
    except Exception as e:
        print(f"Erro ao gerar código com LLM: {str(e)}")
        return generate_eda_code_fallback(question, table_info)

def generate_eda_code_fallback(question: str, table_info: Dict[str, List[str]]) -> str:
    """
    Fallback para geração de código quando LLM falha
    """
    # Código anterior com templates fixos
    question_lower = question.lower()
    table_name = list(table_info.keys())[0] if table_info else 'df'
    columns = table_info.get(table_name, []) if table_info else []
    
    # Verificar se é análise de tendência central específica
    if any(word in question_lower for word in ['mediana', 'média', 'moda', 'tendência central', 'quartil', 'percentil']):
        # Extrair nome da coluna mencionada
        column_name = None
        
        # Primeiro, procurar menção exata na pergunta
        for col in columns:
            if col.lower() in question_lower:
                column_name = col
                break
        
        # Se não encontrou, procurar por palavras-chave comuns
        if not column_name:
            # Mapear palavras comuns para possíveis nomes de colunas
            column_keywords = {
                'amount': ['amount', 'valor', 'value', 'montante', 'total'],
                'value': ['value', 'valor', 'amount', 'price', 'preco'],
                'valores': ['amount', 'value', 'valor', 'total'],
                'coluna': ['amount', 'value']  # genérico
            }
            
            # Procurar palavras-chave na pergunta
            for keyword, possible_cols in column_keywords.items():
                if keyword in question_lower:
                    for col in columns:
                        if any(pc in col.lower() for pc in possible_cols):
                            column_name = col
                            break
                    if column_name:
                        break
        
        if column_name:
            # Template específico para medidas de tendência central
            return f"""
# Análise de Medidas de Tendência Central
print("Calculando medidas de tendência central para coluna {column_name}...")

# Acessar dados
df = {table_name}
insights = []
plots = []
execution_results = []

# Verificar se a coluna existe
if '{column_name}' in df.columns:
    col_data = df['{column_name}'].dropna()
    
    # Calcular estatísticas
    stats = {{
        'Média': col_data.mean(),
        'Mediana': col_data.median(),
        'Moda': col_data.mode().iloc[0] if not col_data.mode().empty else 'N/A',
        'Desvio Padrão': col_data.std(),
        'Mínimo': col_data.min(),
        'Máximo': col_data.max(),
        'Q1 (25%)': col_data.quantile(0.25),
        'Q3 (75%)': col_data.quantile(0.75),
        'IQR': col_data.quantile(0.75) - col_data.quantile(0.25),
        'Valores Únicos': col_data.nunique(),
        'Valores Nulos': df['{column_name}'].isna().sum()
    }}
    
    # Adicionar aos resultados de duas formas para garantir
    execution_results.append({{
        'title': 'Medidas de Tendência Central - {column_name}',
        'data': pd.DataFrame([stats])
    }})
    
    # Adicionar também como dicionário direto para facilitar acesso
    execution_results.append(stats)
    
    # Insights
    insights.append(f"Média: {{stats['Média']:.4f}}")
    insights.append(f"Mediana: {{stats['Mediana']:.4f}}")
    insights.append(f"Desvio Padrão: {{stats['Desvio Padrão']:.4f}}")
    
    if stats['Mediana'] > stats['Média']:
        insights.append("A mediana é maior que a média, indicando distribuição assimétrica à esquerda (cauda esquerda mais longa)")
    elif stats['Mediana'] < stats['Média']:
        insights.append("A mediana é menor que a média, indicando distribuição assimétrica à direita (cauda direita mais longa)")
    else:
        insights.append("Média e mediana são iguais, indicando distribuição simétrica")
    
    # Visualização
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histograma com média e mediana
    ax1.hist(col_data, bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(stats['Média'], color='red', linestyle='--', linewidth=2, label=f"Média: {{stats['Média']:.2f}}")
    ax1.axvline(stats['Mediana'], color='green', linestyle='--', linewidth=2, label=f"Mediana: {{stats['Mediana']:.2f}}")
    ax1.set_xlabel('{column_name}')
    ax1.set_ylabel('Frequência')
    ax1.set_title('Distribuição com Média e Mediana')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Boxplot
    ax2.boxplot(col_data, vert=True)
    ax2.set_ylabel('{column_name}')
    ax2.set_title('Boxplot - Visualização de Quartis')
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores no boxplot
    ax2.text(1.1, stats['Mínimo'], f"Min: {{stats['Mínimo']:.2f}}", fontsize=8)
    ax2.text(1.1, stats['Q1 (25%)'], f"Q1: {{stats['Q1 (25%)']:.2f}}", fontsize=8)
    ax2.text(1.1, stats['Mediana'], f"Mediana: {{stats['Mediana']:.2f}}", fontsize=8)
    ax2.text(1.1, stats['Q3 (75%)'], f"Q3: {{stats['Q3 (75%)']:.2f}}", fontsize=8)
    ax2.text(1.1, stats['Máximo'], f"Max: {{stats['Máximo']:.2f}}", fontsize=8)
    
    plt.tight_layout()
    plots.append(plt.gcf())
    plt.close()
    
    print("Análise de tendência central concluída!")
else:
    print(f"ERRO: Coluna '{column_name}' não encontrada na tabela")
    insights.append(f"Coluna '{column_name}' não encontrada na tabela")
"""
    
    # Renomear função atual para generate_eda_code
    return generate_eda_code_fallback(question, table_info)

def generate_eda_code(question: str, table_info: Dict[str, List[str]]) -> str:
    """
    Função principal que decide entre LLM ou template
    """
    # Tentar primeiro com LLM
    try:
        # Verificar se temos API key
        from ..config.settings import Settings
        settings = Settings()
        if settings.openai_api_key:
            # Log de tentativa
            if 'agent_logs' in st.session_state:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'code_generator',
                    'action': '🤖 Gerando código com LLM',
                    'details': f"Modelo: {settings.openai_model}"
                })
            
            code = generate_eda_code_with_llm(question, table_info)
            
            if 'agent_logs' in st.session_state:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'code_generator',
                    'action': '✅ Código gerado com sucesso',
                    'details': f"{len(code.split('\\n'))} linhas de código"
                })
            
            return code
    except Exception as e:
        print(f"Erro ao usar LLM: {str(e)}")
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'code_generator',
                'action': '⚠️ Fallback para templates',
                'details': str(e)
            })
    
    # Fallback para templates
    return generate_eda_code_fallback(question, table_info)

def generate_eda_code_original(question: str, table_info: Dict[str, List[str]]) -> str:
    """
    Função original com templates (mantida para compatibilidade)
    """
    # SEMPRE usar o template otimizado para evitar erros
    # Este template é mais robusto e não tem problemas de escopo
    if True:  # Forçar uso do template otimizado sempre
        # Já temos table_name definido acima
        table_name = list(table_info.keys())[0] if table_info else 'df'
        
        return f"""
# Análise de Tipos de Dados e Distribuições
# Nota: bibliotecas já disponíveis: pd, np, plt, sns, warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

# Inicializar listas globais para resultados
insights = []
plots = []

# Debug inicial
print("Iniciando análise EDA...")
print("Tabela principal: {table_name}")

# Acessar tabela
try:
    # Debug: mostrar o que está disponível
    print("Variáveis disponíveis no ambiente:")
    available_vars = [k for k in globals().keys() if not k.startswith('_')]
    print(available_vars[:20])  # Primeiras 20 variáveis
    
    # Tentar acessar a tabela
    if '{table_name}' in globals():
        df = globals()['{table_name}']
        print("Tabela '{table_name}' carregada via globals()!")
    else:
        df = {table_name}
        print("Tabela '{table_name}' carregada diretamente!")
    
    print("Shape:", df.shape)
    print("Primeiras colunas:", list(df.columns)[:10])
except Exception as e:
    print("ERRO ao carregar tabela '{table_name}':", str(e))
    print("Tipo do erro:", type(e).__name__)
    # Tentar listar o que está disponível
    print("\\nVariáveis disponíveis:")
    for k in list(globals().keys())[:10]:
        if not k.startswith('_'):
            print(f"  - {{k}}: {{type(globals()[k]).__name__}}")
    raise

print("="*50)
print("ANÁLISE: TIPOS DE DADOS E DISTRIBUIÇÕES")
print("Tabela: {table_name}")
print("="*50)

# 1. Informações Gerais
print("\\n1. INFORMAÇÕES GERAIS:")
print("   - Total de registros: {{:,}}".format(len(df)))
print("   - Total de colunas: {{}}".format(len(df.columns)))
print("   - Tamanho em memória: {{:.2f}} MB".format(df.memory_usage(deep=True).sum() / 1024**2))

# 2. Tipos de Dados
print("\\n2. TIPOS DE DADOS POR COLUNA:")
print(df.dtypes.to_string())

# 3. Classificação das Colunas
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

print("\\n3. CLASSIFICAÇÃO DAS COLUNAS:")
print("   - Numéricas ({{}}): {{}}{{}}".format(len(numeric_cols), ', '.join(numeric_cols[:10]), ' ...' if len(numeric_cols) > 10 else ''))
print("   - Categóricas ({{}}): {{}}{{}}".format(len(categorical_cols), ', '.join(categorical_cols[:10]), ' ...' if len(categorical_cols) > 10 else ''))
print("   - Data/Hora ({{}}): {{}}".format(len(datetime_cols), ', '.join(datetime_cols)))

add_insight("A tabela possui {{}} colunas numéricas e {{}} colunas categóricas".format(len(numeric_cols), len(categorical_cols)), "tipos_dados")

# 4. Estatísticas Descritivas
if numeric_cols:
    print("\\n4. ESTATÍSTICAS DESCRITIVAS (COLUNAS NUMÉRICAS):")
    desc_stats = df[numeric_cols].describe()
    print(desc_stats.to_string())
    
    # 5. Distribuições - Análise detalhada das primeiras 5 colunas numéricas
    print("\\n5. ANÁLISE DE DISTRIBUIÇÕES:")
    
    for i, col in enumerate(numeric_cols[:5]):
        try:
            print("\\n   {{}}:".format(col))
            
            # Estatísticas
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            skew_val = df[col].skew()
            kurt_val = df[col].kurtosis()
        except Exception as e:
            print(f"   Erro ao analisar coluna {{col}}: {{e}}")
            continue
        
        print("      - Média: {{:.4f}}".format(mean_val))
        print("      - Mediana: {{:.4f}}".format(median_val))
        print("      - Desvio Padrão: {{:.4f}}".format(std_val))
        print("      - Assimetria (Skewness): {{:.4f}}".format(skew_val))
        print("      - Curtose: {{:.4f}}".format(kurt_val))
        
        # Interpretação da distribuição
        if abs(skew_val) < 0.5:
            dist_type = "aproximadamente simétrica"
        elif skew_val > 0.5:
            dist_type = "assimétrica positiva (cauda à direita)"
        else:
            dist_type = "assimétrica negativa (cauda à esquerda)"
            
        add_insight("{{}}: distribuição {{}} (skewness={{:.2f}})".format(col, dist_type, skew_val), "distribuição")
        
        # Criar visualização
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Histograma
            df[col].hist(bins=50, ax=ax1, edgecolor='black', alpha=0.7)
            ax1.axvline(mean_val, color='red', linestyle='--', label='Média={{:.2f}}'.format(mean_val))
            ax1.axvline(median_val, color='green', linestyle='--', label='Mediana={{:.2f}}'.format(median_val))
            ax1.set_title('Histograma: {{}}'.format(col))
            ax1.set_xlabel(col)
            ax1.set_ylabel('Frequência')
            ax1.legend()
            
            # Boxplot
            df.boxplot(column=col, ax=ax2)
            ax2.set_title('Boxplot: {{}}'.format(col))
            
            plt.tight_layout()
            save_plot('Distribuição de {{}}'.format(col))
            plt.close()
        except Exception as e:
            print(f"   Erro ao criar visualização para {{col}}: {{e}}")
            plt.close('all')  # Fechar qualquer plot aberto

# 6. Valores Missing
print("\\n6. ANÁLISE DE VALORES MISSING:")
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({{'missing_count': missing, 'missing_pct': missing_pct}})
missing_df = missing_df[missing_df['missing_count'] > 0].sort_values('missing_count', ascending=False)

if not missing_df.empty:
    print(missing_df.to_string())
    add_insight("Encontrados valores missing em {{}} colunas".format(len(missing_df)), "qualidade_dados")
else:
    print("   Nenhum valor missing encontrado!")
    add_insight("Dataset completo sem valores missing", "qualidade_dados")

# 7. Resumo Final
print("\\n" + "="*50)
print("ANÁLISE CONCLUÍDA!")
print("Total de insights gerados: {{}}".format(len(insights)))
print("Total de visualizações criadas: {{}}".format(len(plots)))
print("="*50)
"""
    
    # Templates de código para diferentes tipos de análise
    code_parts = []
    
    # Cabeçalho
    code_parts.append("""
# Análise Exploratória de Dados
import warnings
warnings.filterwarnings('ignore')

# Informações sobre as tabelas disponíveis
""")
    
    # Listar tabelas disponíveis
    for table_name, columns in table_info.items():
        code_parts.append(f"# {table_name}: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    
    code_parts.append("\n# Iniciando análise\n")
    
    # Análise de tipos de dados
    if any(term in question_lower for term in ['tipo', 'types', 'dtype', 'categórico', 'numérico']):
        # Gerar código específico para cada tabela
        for table_name in table_info.keys():
            code_parts.append(f"""
# Análise de tipos de dados - {table_name}
df = {table_name}  # Acesso direto à tabela
print(f"\\n=== Análise de tipos de dados: {table_name} ===")
print(f"Total de colunas: {{len(df.columns)}}")
print(f"Total de registros: {{len(df)}}")

# Tipos de dados
print("\\nTipos de dados por coluna:")
print(df.dtypes)

# Classificar colunas
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

print(f"\\nColunas numéricas ({{len(numeric_cols)}}): {{numeric_cols}}")
print(f"Colunas categóricas ({{len(categorical_cols)}}): {{categorical_cols}}")
print(f"Colunas de data ({{len(datetime_cols)}}): {{datetime_cols}}")

add_insight(f"Tabela {table_name}: {{len(numeric_cols)}} numéricas, {{len(categorical_cols)}} categóricas", "tipos_dados")
""")
    
    # Análise de distribuições
    if any(term in question_lower for term in ['distribuição', 'distribution', 'histograma', 'média', 'mediana']):
        for table_name in table_info.keys():
            code_parts.append(f"""
# Análise de distribuições - {table_name}
df = {table_name}  # Acesso direto à tabela
numeric_cols = df.select_dtypes(include=[np.number]).columns

if len(numeric_cols) > 0:
            print(f"\\n=== Estatísticas descritivas: {table_name} ===")
            print(df[numeric_cols].describe())
            
            # Medidas de tendência central
            for col in numeric_cols[:5]:  # Limitar a 5 colunas
                mean_val = df[col].mean()
                median_val = df[col].median()
                std_val = df[col].std()
                
                print(f"\\n{col}:")
                print(f"  Média: {mean_val:.2f}")
                print(f"  Mediana: {median_val:.2f}")
                print(f"  Desvio padrão: {std_val:.2f}")
                print(f"  Assimetria: {df[col].skew():.2f}")
                
                # Criar histograma
                plt.figure(figsize=(8, 5))
                plt.hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
                plt.title(f'Distribuição de {col} ({table_name})')
                plt.xlabel(col)
                plt.ylabel('Frequência')
                plt.grid(True, alpha=0.3)
                save_plot(f"Distribuição {col}")
                
                if abs(df[col].skew()) > 1:
                    add_insight(f"{col} tem distribuição assimétrica (skew={df[col].skew():.2f})", "distribuição")
""")
    
    # Detecção de outliers
    if any(term in question_lower for term in ['outlier', 'anomalia', 'atípico', 'extremo']):
        code_parts.append("""
# Detecção de outliers
for table_name in locals():
    if isinstance(locals()[table_name], pd.DataFrame):
        df = locals()[table_name]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            print(f"\\n=== Análise de outliers: {table_name} ===")
            
            outliers_info = {}
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                outliers_info[col] = len(outliers)
                
                if len(outliers) > 0:
                    print(f"{col}: {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)")
                    add_insight(f"{col} tem {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)", "outliers")
            
            # Boxplot para visualização
            if len(numeric_cols) <= 10:
                plt.figure(figsize=(12, 6))
                df[numeric_cols].boxplot()
                plt.title(f'Detecção de Outliers - {table_name}')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                save_plot(f"Outliers {table_name}")
""")
    
    # Correlações
    if any(term in question_lower for term in ['correlação', 'correlation', 'relação', 'relationship']):
        code_parts.append("""
# Análise de correlações
for table_name in locals():
    if isinstance(locals()[table_name], pd.DataFrame):
        df = locals()[table_name]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            print(f"\\n=== Correlações: {table_name} ===")
            corr_matrix = df[numeric_cols].corr()
            
            # Encontrar correlações fortes
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
                        print(f"{corr_matrix.columns[i]} vs {corr_matrix.columns[j]}: {corr_val:.3f}")
                        add_insight(f"Correlação forte entre {corr_matrix.columns[i]} e {corr_matrix.columns[j]}: {corr_val:.3f}", "correlação")
            
            # Heatmap de correlação
            if len(numeric_cols) <= 20:
                plt.figure(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                           fmt='.2f', square=True, linewidths=1)
                plt.title(f'Matriz de Correlação - {table_name}')
                plt.tight_layout()
                save_plot(f"Correlação {table_name}")
""")
    
    # Padrões e tendências
    if any(term in question_lower for term in ['padrão', 'pattern', 'tendência', 'trend', 'temporal']):
        code_parts.append("""
# Identificação de padrões
for table_name in locals():
    if isinstance(locals()[table_name], pd.DataFrame):
        df = locals()[table_name]
        
        print(f"\\n=== Análise de padrões: {table_name} ===")
        
        # Valores mais frequentes em colunas categóricas
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:5]:  # Limitar a 5 colunas
            value_counts = df[col].value_counts()
            print(f"\\n{col} - Valores mais frequentes:")
            print(value_counts.head(10))
            
            if len(value_counts) > 1:
                # Gráfico de barras
                plt.figure(figsize=(10, 5))
                value_counts.head(10).plot(kind='bar')
                plt.title(f'Top 10 valores - {col} ({table_name})')
                plt.xlabel(col)
                plt.ylabel('Frequência')
                plt.xticks(rotation=45)
                plt.tight_layout()
                save_plot(f"Frequência {col}")
                
                # Detectar concentração
                top_percent = value_counts.head(3).sum() / len(df) * 100
                if top_percent > 50:
                    add_insight(f"{col}: Top 3 valores representam {top_percent:.1f}% dos dados", "padrões")
""")
    
    # Análise geral se não houver tipo específico
    if not any(term in question_lower for term in ['tipo', 'distribuição', 'outlier', 'correlação', 'padrão']):
        code_parts.append("""
# Análise geral dos dados
for table_name in locals():
    if isinstance(locals()[table_name], pd.DataFrame):
        df = locals()[table_name]
        
        print(f"\\n=== Análise geral: {table_name} ===")
        print(f"Dimensões: {df.shape}")
        print(f"\\nInformações gerais:")
        print(df.info())
        
        # Estatísticas básicas
        print("\\nEstatísticas descritivas:")
        print(df.describe(include='all'))
        
        # Valores missing
        missing = df.isnull().sum()
        if missing.any():
            print("\\nValores missing:")
            print(missing[missing > 0])
            add_insight(f"{table_name} tem {missing.sum()} valores missing em {(missing > 0).sum()} colunas", "qualidade")
""")
    
    # Finalização
    code_parts.append("""
# Resumo dos insights
print("\\n=== RESUMO DOS INSIGHTS ===")
for i, insight in enumerate(insights, 1):
    print(f"{i}. [{insight['category']}] {insight['text']}")

show_results({"total_insights": len(insights), "total_plots": len(plots)}, "Resumo da Análise")
""")
    
    return '\n'.join(code_parts)


def execute_python_eda(db, data_tables: list, query: str) -> Dict[str, Any]:
    """
    Executa análise EDA usando código Python gerado dinamicamente
    
    Args:
        db: DatabaseManager
        data_tables: Lista de tabelas disponíveis
        query: Pergunta do usuário
        
    Returns:
        Resultados da análise
    """
    try:
        # Log inicial
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'python_eda',
                'action': '🐍 Iniciando análise Python EDA',
                'details': f"Pergunta: {query[:100]}..."
            })
        
        # Carregar dados das tabelas
        dataframes = {}
        table_info = {}
        
        for table_name in data_tables[:5]:  # Limitar a 5 tabelas
            try:
                df = db.get_table_data(table_name, limit=10000)  # Limitar registros
                if df is not None and not df.empty:
                    dataframes[table_name] = df
                    table_info[table_name] = df.columns.tolist()
                    
                    if 'agent_logs' in st.session_state:
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': f'📊 Tabela {table_name} carregada',
                            'details': f"{len(df)} registros, {len(df.columns)} colunas"
                        })
            except Exception as e:
                st.warning(f"Não foi possível carregar {table_name}: {str(e)}")
        
        if not dataframes:
            return {
                'success': False,
                'error': 'Nenhuma tabela pôde ser carregada'
            }
        
        # Gerar código Python baseado na pergunta
        code = generate_eda_code(query, table_info)
        
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'python_eda',
                'action': '📝 Código Python gerado',
                'details': f"{len(code.split(chr(10)))} linhas de código | Query: {query[:50]}..."
            })
            
            # Log se código foi gerado
            if not code:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_eda',
                    'action': '⚠️ Código vazio!',
                    'details': 'Nenhum código foi gerado'
                })
                return {
                    'action_type': 'python_eda',
                    'success': False,
                    'error': 'Código não foi gerado'
                }
            
            # Mostrar preview do código
            code_lines = code.split('\n')
            code_preview = '\n'.join(code_lines[:20]) + f'\n... ({len(code_lines)} linhas total)'
            
            # Forçar mostrar o código completo nos logs
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'python_eda',
                'action': '💻 Código Final Executado - COMPLETO',
                'details': f"Total: {len(code_lines)} linhas\nPergunta: {query}\n\n{code}"  # Mostrar código completo
            })
            
            # Separar e mostrar a parte específica do código (sem o template)
            # Procurar onde começa o código real após "# Seu código aqui"
            codigo_especifico = ""
            inicio_codigo_real = False
            for i, linha in enumerate(code_lines):
                if "# Seu código aqui" in linha:
                    inicio_codigo_real = True
                    continue
                if inicio_codigo_real and "# Garantir que pelo menos" in linha:
                    break
                if inicio_codigo_real:
                    codigo_especifico += linha + "\n"
            
            if codigo_especifico.strip():
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_eda',
                    'action': '🎯 Código Específico (sem template)',
                    'details': codigo_especifico[:1000]  # Limitar a 1000 caracteres
                })
            
            # Debug: mostrar se está usando o template correto
            if 'tipos de dados' in query.lower() or 'distribuições' in query.lower():
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_eda',
                    'action': '🔍 Usando template de tipos/distribuições',
                    'details': f'Tabela alvo: {list(table_info.keys())[0] if table_info else "nenhuma"}'
                })
        
        # Executar código
        executor = SafePythonExecutor(dataframes)
        
        if 'agent_logs' in st.session_state:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'python_eda',
                'action': '🚀 Executando análise Python',
                'details': 'Gerando estatísticas, gráficos e insights...'
            })
        
        results = executor.execute_code(code)
        
        if 'agent_logs' in st.session_state:
            if results['success']:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_eda',
                    'action': '✅ Análise concluída',
                    'details': f"Gráficos: {len(results.get('plots', []))}, Insights: {len(results.get('insights', []))}"
                })
                
                # Log detalhado dos resultados calculados
                if results.get('results') is not None:
                    exec_results = results['results']
                    results_text = []
                    
                    # Debug: mostrar o que recebemos
                    if 'agent_logs' in st.session_state:
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '🔍 Debug - execution_results recebido',
                            'details': f"Tipo: {type(exec_results)}, Conteúdo: {str(exec_results)[:300]}"
                        })
                    
                    if isinstance(exec_results, dict):
                        # Formatar resultados como string legível
                        for key, value in exec_results.items():
                            if key not in ['plots', 'stdout', 'stderr']:
                                if isinstance(value, (int, float)):
                                    results_text.append(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
                                else:
                                    results_text.append(f"{key}: {value}")
                    elif isinstance(exec_results, list):
                        # Se é uma lista, processar cada item
                        for item in exec_results:
                            if isinstance(item, dict):
                                # Se tem 'title' e 'data' (formato comum do LLM)
                                if 'title' in item and 'data' in item:
                                    value = item['data']
                                    # Se data é um DataFrame, pular
                                    if hasattr(value, 'to_dict'):
                                        continue
                                    # Se é um número, formatar
                                    if isinstance(value, (int, float)):
                                        results_text.append(f"{item['title']}: {value:.2f}" if isinstance(value, float) else f"{item['title']}: {value}")
                                    else:
                                        results_text.append(f"{item['title']}: {value}")
                                # Se tem 'data' com DataFrame, pular
                                elif 'data' in item and hasattr(item.get('data'), 'to_dict'):
                                    continue
                                # Se tem estatísticas específicas, processar
                                elif any(key in item for key in ['Média', 'Mediana', 'Desvio Padrão']):
                                    for key, value in item.items():
                                        if key not in ['title', 'data', 'type']:
                                            if isinstance(value, (int, float)):
                                                results_text.append(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
                                            else:
                                                results_text.append(f"{key}: {value}")
                                # Processar outros formatos
                                else:
                                    if 'title' in item:
                                        results_text.append(f"\n{item['title']}:")
                                    for key, value in item.items():
                                        if key not in ['title', 'data', 'type'] and not key.startswith('_'):
                                            if isinstance(value, (int, float)):
                                                results_text.append(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
                                            else:
                                                results_text.append(f"  {key}: {value}")
                    
                    if results_text:
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '📊 Resultados Calculados',
                            'details': '\n'.join(results_text)
                        })
                    else:
                        # Se não há resultados formatados, mostrar o que temos
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '⚠️ Resultados vazios',
                            'details': f"execution_results: {str(exec_results)[:200]}..."
                        })
                    
                # Log dos insights gerados
                if results.get('insights'):
                    # Processar insights - podem ser strings ou dicionários
                    insights_list = []
                    for insight in results['insights'][:10]:  # Aumentar limite
                        if isinstance(insight, str):
                            insights_list.append(f"• {insight}")
                        elif isinstance(insight, dict) and 'text' in insight:
                            insights_list.append(f"• {insight['text']}")
                        else:
                            insights_list.append(f"• {str(insight)}")
                    
                    insights_text = '\n'.join(insights_list)
                    if insights_text:
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '💡 Insights Gerados',
                            'details': insights_text
                        })
                
                # Log do stdout se tiver saída importante
                if results.get('stdout') and results['stdout'].strip():
                    stdout_lines = results['stdout'].strip().split('\n')
                    # Filtrar linhas relevantes (que contêm números ou resultados)
                    relevant_lines = []
                    for line in stdout_lines[:30]:  # Aumentar limite
                        # Incluir mais tipos de linhas relevantes
                        if any(keyword in line.lower() for keyword in ['média', 'mediana', 'mean', 'median', ':', '=', 'erro', 'error', 'coluna', 'column']) or any(char.isdigit() for char in line):
                            relevant_lines.append(line)
                    
                    if relevant_lines:
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '📋 Saída do Código Python',
                            'details': '\n'.join(relevant_lines)
                        })
                    elif results['stdout'].strip():  # Se não há linhas relevantes mas tem saída
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'python_eda',
                            'action': '📋 Saída Completa do Python',
                            'details': results['stdout'][:500]  # Primeiros 500 caracteres
                        })
                
                # Log específico para plots
                if results.get('plots'):
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'python_eda',
                        'action': f'📊 {len(results["plots"])} gráfico(s) gerado(s)',
                        'details': f"Plots: {[p.get('title', 'Sem título') for p in results['plots']]}"
                    })
                else:
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'python_eda',
                        'action': '⚠️ Nenhum gráfico foi gerado',
                        'details': 'Lista de plots está vazia ou código não salvou o gráfico'
                    })
            else:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'python_eda',
                    'action': '❌ Erro na execução',
                    'details': results.get('error', 'Erro desconhecido')
                })
                
                # Mostrar stdout/stderr para debug
                if results.get('stdout'):
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'python_eda',
                        'action': '📋 Stdout do código',
                        'details': results['stdout'][:200] + '...' if len(results.get('stdout', '')) > 200 else results.get('stdout', '')
                    })
                    
                if results.get('stderr'):
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'python_eda',
                        'action': '⚠️ Stderr do código',
                        'details': results['stderr'][:200] + '...' if len(results.get('stderr', '')) > 200 else results.get('stderr', '')
                    })
        
        # Formatar resultados
        result_dict = {
            'action_type': 'python_eda',
            'success': results['success'],
            'query': query,
            'code': code,
            'stdout': results['stdout'],
            'stderr': results['stderr'],
            'plots': results['plots'],
            'insights': results['insights'],
            'execution_results': results['results'],
            'tables_analyzed': list(dataframes.keys())
        }
        
        # Só incluir error se realmente existir
        if results.get('error'):
            result_dict['error'] = results['error']
            
        return result_dict
        
    except Exception as e:
        return {
            'action_type': 'python_eda',
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
