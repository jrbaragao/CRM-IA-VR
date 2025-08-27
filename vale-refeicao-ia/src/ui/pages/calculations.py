"""
Página de cálculos com agentes autônomos baseados em prompts
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json

from ..components import render_alert
from ...data.database import get_db_manager
from ...agents.log_utils import log_agent_action

def render():
    """Renderiza página de cálculos com agentes autônomos"""
    st.header("🧮 Cálculos Inteligentes com IA")
    st.caption("Sistema de cálculos baseado em agentes autônomos configuráveis")
    
    # Obter gerenciador de banco
    db = get_db_manager()
    
    # Verificar se há tabelas de dados (excluir tabelas do sistema)
    system_tables = ['importacoes', 'agent_logs', 'calculation_configs']
    all_tables = db.list_tables()
    data_tables = [table for table in all_tables if table not in system_tables]
    
    if not data_tables:
        render_alert(
            "⚠️ Nenhuma tabela de dados encontrada. Processe arquivos primeiro na seção 'Processamento de Dados'.",
            "warning"
        )
        return
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs([
        "⚙️ Configurar Cálculos",
        "🚀 Executar Cálculos", 
        "📊 Histórico de Cálculos"
    ])
    
    with tab1:
        render_calculation_config_tab(db, data_tables)
    
    with tab2:
        render_calculation_execution_tab(db, data_tables)
    
    with tab3:
        render_calculation_history_tab(db)

def render_calculation_config_tab(db, data_tables):
    """Renderiza aba de configuração de cálculos"""
    
    st.markdown("### ⚙️ Configuração de Cálculos Inteligentes")
    st.caption("Configure prompts e ferramentas para agentes autônomos de cálculo")
    
    # Informações sobre o sistema
    with st.expander("ℹ️ Como funciona o Sistema de Cálculos Inteligentes", expanded=False):
        st.markdown("""
        **🧠 Sistema Revolucionário de Cálculos:**
        
        **🎯 Baseado em Prompts:**
        - Defina o que você quer calcular em linguagem natural
        - O agente interpreta e executa automaticamente
        - Sem código fixo - totalmente flexível
        
        **🛠️ Ferramentas Selecionáveis:**
        - Escolha quais ferramentas o agente pode usar
        - SQL queries, análises estatísticas, correlações
        - **📊 Exportação automática para Excel/CSV/JSON**
        - Controle total sobre as capacidades do agente
        
        **🔄 Processo Autônomo:**
        - Agente planeja e executa múltiplas etapas
        - Adapta-se aos dados disponíveis
        - Gera relatórios completos automaticamente
        """)
    
    # Formulário de configuração
    st.markdown("### 📝 Nova Configuração de Cálculo")
    
    with st.form("calculation_config_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            config_name = st.text_input(
                "📛 Nome da Configuração",
                placeholder="Ex: Cálculo Vale Refeição Padrão",
                help="Nome único para identificar esta configuração"
            )
            
            config_description = st.text_area(
                "📝 Descrição",
                placeholder="Descreva o objetivo desta configuração de cálculo...",
                height=80,
                help="Descrição detalhada do que esta configuração faz"
            )
        
        with col2:
            st.markdown("**📊 Tabelas Disponíveis:**")
            for table in data_tables:
                table_info = db.get_table_info(table)
                if table_info:
                    st.caption(f"• **{table}** ({table_info['total_rows']} registros)")
        
        # Prompt principal
        st.markdown("### 🎯 Prompt de Cálculo")
        calculation_prompt = st.text_area(
            "Descreva o que o agente deve calcular:",
            placeholder="""Exemplo (Vale Refeição):
Atue como um especialista de RH e calculista de vale refeições no Brasil.

A tabela ativos indica a lista geral de colaboradores e se relaciona com as demais pela coluna MATRICULA.

Gere uma planilha com os colaboradores ativos que tenham direito a vale refeição.

Não se paga vale refeição para colaboradores de férias, que são aprendizes, com afastamentos, que estão no exterior ou desligados.

Considere um mês de 22 dias úteis.

Use a ferramenta 'Cálculo de Vale Refeição' para executar a lógica de negócio e depois exporte para Excel.""",
            height=200,
            help="Seja específico sobre regras, condições e formato do resultado desejado"
        )
        
        # Seleção de ferramentas
        st.markdown("### 🛠️ Ferramentas Disponíveis para o Agente")
        
        available_tools = get_available_tools()
        selected_tools = []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔍 Análise de Dados:**")
            for tool in available_tools['data_analysis']:
                if st.checkbox(f"{tool['icon']} {tool['name']}", key=f"tool_{tool['id']}"):
                    selected_tools.append(tool['id'])
        
        with col2:
            st.markdown("**🧮 Cálculos:**")
            for tool in available_tools['calculations']:
                if st.checkbox(f"{tool['icon']} {tool['name']}", key=f"tool_{tool['id']}"):
                    selected_tools.append(tool['id'])
        
        with col3:
            st.markdown("**📊 Exportação:**")
            for tool in available_tools['export_tools']:
                if st.checkbox(f"{tool['icon']} {tool['name']}", key=f"tool_{tool['id']}"):
                    selected_tools.append(tool['id'])
        
        # Configurações do agente
        col1, col2 = st.columns(2)
        
        with col1:
            max_iterations = st.slider("🔄 Max Iterações", 1, 15, 8)
            exploration_depth = st.selectbox("🔍 Profundidade", ["Básica", "Intermediária", "Avançada"], index=2)
        
        with col2:
            include_insights = st.checkbox("💡 Incluir Insights", True)
            show_reasoning = st.checkbox("🧠 Mostrar Raciocínio", True)
        
        # Botão de salvar
        submitted = st.form_submit_button("💾 Salvar Configuração", type="primary")
        
        if submitted:
            if not config_name.strip():
                st.error("❌ Nome da configuração é obrigatório!")
            elif not calculation_prompt.strip():
                st.error("❌ Prompt de cálculo é obrigatório!")
            elif not selected_tools:
                st.error("❌ Selecione pelo menos uma ferramenta!")
            else:
                config = {
                    'max_iterations': max_iterations,
                    'exploration_depth': exploration_depth,
                    'include_insights': include_insights,
                    'show_reasoning': show_reasoning
                }
                
                success = db.save_calculation_config(
                    config_name.strip(),
                    config_description.strip(),
                    calculation_prompt.strip(),
                    selected_tools,
                    config
                )
                
                if success:
                    st.success("✅ Configuração salva com sucesso!")
                    st.rerun()
    
    # Lista de configurações existentes
    st.markdown("---")
    st.markdown("### 📋 Configurações Existentes")
    
    configs = db.get_calculation_configs()
    
    if configs:
        for config in configs:
            with st.expander(f"⚙️ {config['name']}", expanded=False):
                st.markdown(f"**Descrição:** {config['description']}")
                st.markdown(f"**Ferramentas:** {len(config['available_tools'])} selecionadas")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar", key=f"edit_{config['id']}"):
                        st.info("🚧 Em desenvolvimento")
                with col2:
                    if st.button("🗑️ Remover", key=f"delete_{config['id']}"):
                        if db.delete_calculation_config(config['name']):
                            st.success("✅ Removido!")
                            st.rerun()
    else:
        st.info("📝 Nenhuma configuração criada ainda.")

def render_calculation_execution_tab(db, data_tables):
    """Renderiza aba de execução de cálculos"""
    
    st.markdown("### 🚀 Executar Cálculos Inteligentes")
    
    configs = db.get_calculation_configs()
    
    if not configs:
        st.warning("⚠️ Nenhuma configuração disponível.")
        st.info("💡 Crie uma configuração na aba 'Configurar Cálculos' primeiro.")
        return
    
    # Seleção de configuração
    config_options = {config['name']: config for config in configs}
    selected_config_name = st.selectbox(
        "Escolha a configuração:",
        options=list(config_options.keys())
    )
    
    if selected_config_name:
        selected_config = config_options[selected_config_name]
        
        with st.expander("ℹ️ Detalhes da Configuração", expanded=True):
            st.markdown(f"**📝 Descrição:** {selected_config['description']}")
            st.markdown(f"**🛠️ Ferramentas:** {len(selected_config['available_tools'])}")
            st.code(selected_config['prompt'], language='text')
        
        if st.button("🚀 Iniciar Cálculo Autônomo", type="primary"):
            execution_container = st.empty()
            execute_autonomous_calculation(db, data_tables, selected_config, execution_container)

def render_calculation_history_tab(db):
    """Renderiza aba de histórico"""
    
    st.markdown("### 📊 Histórico de Cálculos")
    
    if 'calculation_history' in st.session_state and st.session_state['calculation_history']:
        history = st.session_state['calculation_history']
        
        for i, calc in enumerate(reversed(history[-5:])):
            with st.expander(f"🧮 {calc['config_name']} - {calc['timestamp']}", expanded=False):
                st.markdown(f"**Status:** {calc.get('status', 'Concluído')}")
                st.markdown(f"**Iterações:** {calc.get('iterations', 'N/A')}")
    else:
        st.info("📝 Nenhum cálculo executado ainda.")

def get_available_tools():
    """Retorna ferramentas disponíveis"""
    return {
        'data_analysis': [
            {'id': 'sql_query', 'name': 'Consultas SQL', 'icon': '🔍'},
            {'id': 'data_exploration', 'name': 'Exploração de Dados', 'icon': '📊'},
            {'id': 'data_correlation', 'name': 'Correlações', 'icon': '🔗'},
            {'id': 'data_quality', 'name': 'Qualidade dos Dados', 'icon': '✅'}
        ],
        'calculations': [
            {'id': 'calculo_vale_refeicao', 'name': '🍽️ Cálculo de Vale Refeição', 'icon': '💰'},
            {'id': 'mathematical_operations', 'name': 'Operações Matemáticas', 'icon': '🧮'},
            {'id': 'conditional_logic', 'name': 'Lógica Condicional', 'icon': '🔀'},
            {'id': 'aggregations', 'name': 'Agregações', 'icon': '📈'},
            {'id': 'report_generation', 'name': 'Relatórios', 'icon': '📄'}
        ],
        'export_tools': [
            {'id': 'excel_export', 'name': 'Exportar para Excel', 'icon': '📊'},
            {'id': 'csv_export', 'name': 'Exportar para CSV', 'icon': '📄'},
            {'id': 'json_export', 'name': 'Exportar para JSON', 'icon': '🔗'}
        ]
    }

def execute_autonomous_calculation(db, data_tables, config, container):
    """Executa cálculo usando agente autônomo"""
    
    from .database_viewer import execute_autonomous_agent
    from ...agents.log_utils import log_agent_action
    
    with container.container():
        st.markdown("## 🧮 Agente de Cálculo em Ação")
        st.markdown(f"**Configuração:** {config['name']}")
        
        # Debug: Log da configuração recebida
        log_agent_action(
            "calculation_debug",
            "🔧 Configuração carregada",
            {
                "config_name": config['name'],
                "available_tools": config.get('available_tools', []),
                "tools_count": len(config.get('available_tools', [])),
                "prompt_length": len(config.get('prompt', ''))
            }
        )
        
        # Exibir ferramentas selecionadas para o usuário
        st.markdown("### 🛠️ Ferramentas Selecionadas:")
        if config.get('available_tools'):
            for tool in config['available_tools']:
                st.markdown(f"• ✅ {tool}")
        else:
            st.warning("⚠️ Nenhuma ferramenta selecionada!")
        
        calculation_prompt = f"""
        CONTEXTO: Você é um agente especializado em cálculos de benefícios e análises de RH.
        
        OBJETIVO: {config['prompt']}
        
        FERRAMENTAS DISPONÍVEIS: {', '.join(config['available_tools'])}
        
        INSTRUÇÕES:
        1. Analise os dados disponíveis nas tabelas
        2. Aplique as regras de cálculo especificadas
        3. Gere resultados detalhados e organizados
        4. Forneça relatórios com totais e estatísticas
        
        Execute o cálculo de forma autônoma.
        """
        
        success = execute_autonomous_agent(db, data_tables, calculation_prompt, config, container)
        
        if success:
            if 'calculation_history' not in st.session_state:
                st.session_state['calculation_history'] = []
            
            calculation_record = {
                'config_name': config['name'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Concluído'
            }
            
            st.session_state['calculation_history'].append(calculation_record)
            
            log_agent_action(
                "calculation_agent",
                "✅ Cálculo autônomo concluído",
                {"configuracao": config['name']}
            )
