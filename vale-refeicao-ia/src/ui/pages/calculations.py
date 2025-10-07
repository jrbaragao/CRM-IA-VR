"""
Página de cálculos com agentes autônomos baseados em prompts
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
from sqlalchemy import text

from ..components import render_alert
from ...data.database import get_db_manager
from ...agents.log_utils import log_agent_action

def render():
    """Renderiza página de agentes de IA"""
    st.header("🤖 Agentes de IA")
    st.caption("Configure e execute agentes autônomos para análises, cálculos e explorações de dados")
    
    # Obter gerenciador de banco
    db = get_db_manager()
    
    # Verificar se há tabelas de dados (excluir tabelas do sistema)
    system_tables = ['importacoes', 'agent_logs', 'calculation_configs']
    all_tables = db.list_tables()
    data_tables = [table for table in all_tables if table not in system_tables]
    
    if not data_tables:
        render_alert(
            "⚠️ Nenhuma tabela de dados encontrada. Processe arquivos primeiro na seção 'Preparação de Dados'.",
            "warning"
        )
        return
    
    # Inicializar estado da tab se não existir
    if 'calculation_active_tab' not in st.session_state:
        st.session_state.calculation_active_tab = 1  # Default para "Executar Cálculos"
    
    # Tabs principais
    tabs = st.tabs([
        "⚙️ Configurar Cálculos",
        "🚀 Executar Cálculos", 
        "📊 Histórico de Cálculos",
        "💬 Chat com IA"
    ])
    
    # Renderizar conteúdo baseado na tab ativa
    for idx, tab in enumerate(tabs):
        with tab:
            if idx == 0:
                render_calculation_config_tab(db, data_tables)
            elif idx == 1:
                render_calculation_execution_tab(db, data_tables)
            elif idx == 2:
                render_calculation_history_tab(db)
            elif idx == 3:
                render_chat_tab(db, data_tables)

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
    
    # Verificar nomes existentes antes do formulário
    existing_configs = db.get_calculation_configs()
    existing_names = [config['name'].lower() for config in existing_configs]
    
    # Container para mensagens de validação
    validation_container = st.empty()
    
    # Mostrar aviso se houver muitas configurações com nomes similares
    if existing_configs:
        st.caption(f"📋 {len(existing_configs)} configurações já existentes")
    
    with st.form("calculation_config_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            config_name = st.text_input(
                "📛 Nome da Configuração",
                placeholder="Ex: Análise de Vendas Mensais",
                help="Nome único para identificar esta configuração",
                key="config_name_input"
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
            placeholder="""Exemplo:
Analise os dados de vendas e identifique os padrões de comportamento do cliente.

Considere as seguintes métricas:
- Volume de vendas por categoria
- Tendências temporais
- Produtos mais vendidos
- Análise de sazonalidade

Gere um relatório com insights e recomendações estratégicas.""",
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
            # Usar o container fora do form para mostrar mensagens
            with validation_container.container():
                if not config_name.strip():
                    st.error("❌ Nome da configuração é obrigatório!")
                    st.stop()
                elif not calculation_prompt.strip():
                    st.error("❌ Prompt de cálculo é obrigatório!")
                    st.stop()
                elif not selected_tools:
                    st.error("❌ Selecione pelo menos uma ferramenta!")
                    st.stop()
                elif config_name.strip().lower() in existing_names:
                    st.error(f"❌ Já existe uma configuração com o nome '{config_name}'!")
                    
                    # Sugerir nomes alternativos
                    from datetime import datetime
                    suggestions = [
                        f"{config_name} - v2",
                        f"{config_name} ({datetime.now().strftime('%Y-%m-%d')})",
                        f"{config_name} - Cópia",
                        f"{config_name} - {datetime.now().strftime('%H:%M')}"
                    ]
                    
                    st.info("💡 Sugestões de nomes únicos:")
                    for sugg in suggestions[:3]:
                        st.caption(f"• {sugg}")
                    
                    # Mostrar a configuração existente
                    for config in existing_configs:
                        if config['name'].lower() == config_name.strip().lower():
                            with st.expander("📋 Configuração existente com este nome:", expanded=True):
                                st.write(f"**Nome:** {config['name']}")
                                st.write(f"**Descrição:** {config['description']}")
                                st.write(f"**Criada em:** {config['created_at']}")
                            break
                    st.stop()
                else:
                    config = {
                        'max_iterations': max_iterations,
                        'exploration_depth': exploration_depth,
                        'include_insights': include_insights,
                        'show_reasoning': show_reasoning
                    }
                    
                    # Debug - mostrar o que está sendo salvo
                    st.info(f"💾 Salvando configuração '{config_name}'...")
                    st.caption(f"Ferramentas selecionadas: {len(selected_tools)}")
                    st.caption(f"Ferramentas: {', '.join(selected_tools[:3])}{'...' if len(selected_tools) > 3 else ''}")
                    
                    try:
                        success = db.save_calculation_config(
                            config_name.strip(),
                            config_description.strip(),
                            calculation_prompt.strip(),
                            selected_tools,
                            config
                        )
                        
                        if success:
                            st.success("✅ Configuração salva com sucesso!")
                            # Aguardar um momento antes de recarregar
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar configuração. Verifique os logs.")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
    
    # Lista de configurações existentes
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📋 Configurações Existentes")
    with col2:
        if st.button("🔄 Atualizar Lista", use_container_width=True):
            st.rerun()
    
    # Sempre buscar configs do banco
    configs = db.get_calculation_configs()
    
    # Debug - mostrar quantas configurações existem
    st.caption(f"Total de configurações: {len(configs) if configs else 0}")
    
    # Debug - listar todas as tabelas
    with st.expander("🔍 Debug: Tabelas no banco", expanded=False):
        all_tables = db.list_tables()
        st.write("Tabelas encontradas:")
        for table in all_tables:
            st.write(f"- {table}")
        
        # Verificar se calculation_configs está na lista
        if 'calculation_configs' in all_tables:
            st.success("✅ Tabela calculation_configs encontrada!")
            # Fazer query direta
            try:
                with db.engine.connect() as conn:
                    # Contar registros
                    result = conn.execute(text("SELECT COUNT(*) FROM calculation_configs"))
                    count = result.scalar()
                    st.info(f"📊 Total de registros na tabela: {count}")
                    
                    # Listar registros
                    if count > 0:
                        st.write("**Registros existentes:**")
                        result = conn.execute(text("SELECT id, name, created_at FROM calculation_configs ORDER BY id"))
                        for row in result:
                            st.write(f"- ID: {row[0]}, Nome: {row[1]}, Criado: {row[2]}")
                    else:
                        st.warning("⚠️ Nenhum registro encontrado na tabela")
                        
                    # Verificar estrutura da tabela
                    st.write("**📋 Estrutura da tabela:**")
                    try:
                        # SQLite pragma para ver estrutura
                        result = conn.execute(text("PRAGMA table_info(calculation_configs)"))
                        for col in result:
                            st.caption(f"- {col[1]} ({col[2]})")
                    except Exception as e:
                        st.error(f"Erro ao ver estrutura: {str(e)}")
                        
                    # Mostrar botão de ativar apenas se houver registros inativos
                    inactive_count = count - len(configs)
                    if inactive_count > 0:
                        st.warning(f"⚠️ {inactive_count} configurações inativas encontradas")
                        if st.button("✅ Ativar Todos os Registros", key="activate_all"):
                            try:
                                with db.engine.begin() as activate_conn:
                                    activate_sql = "UPDATE calculation_configs SET is_active = 1 WHERE is_active IS NULL OR is_active = 0"
                                    activate_conn.execute(text(activate_sql))
                                st.success("✅ Todos os registros foram ativados!")
                                st.rerun()
                            except Exception as act_e:
                                st.error(f"❌ Erro ao ativar registros: {str(act_e)}")
                    
                    # Teste manual de inserção (sempre disponível)
                    if st.button("🧪 Testar Inserção Manual", key="test_insert"):
                            import time
                            unique_name = f"Teste Manual {int(time.time())}"
                            test_sql = f"""
                            INSERT INTO calculation_configs 
                            (name, description, prompt, available_tools, max_iterations,
                             exploration_depth, include_insights, show_reasoning, is_active)
                            VALUES ('{unique_name}', 'Teste de inserção manual', 'Prompt teste', 
                                    '["sql_queries"]', 5, 'Básica', 1, 1, 1)
                            """
                            try:
                                with db.engine.begin() as test_conn:
                                    test_conn.execute(text(test_sql))
                                st.success("✅ Inserção manual bem sucedida!")
                                st.rerun()
                            except Exception as test_e:
                                st.error(f"❌ Erro na inserção manual: {str(test_e)}")
                                
            except Exception as e:
                st.error(f"Erro ao consultar tabela: {str(e)}")
        else:
            st.error("❌ Tabela calculation_configs NÃO encontrada!")
            if st.button("🔨 Criar Tabela Manualmente"):
                db._create_calculation_configs_table()
                st.rerun()
    
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
        
        # Container para o resultado do cálculo
        result_container = st.container()
        
        if st.button("🚀 Iniciar Cálculo Autônomo", type="primary", key="exec_calc_btn"):
            # Executar no container dedicado para evitar mudança de tab
            with result_container:
                st.markdown("---")
                execute_autonomous_calculation(db, data_tables, selected_config, result_container)

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
    """Retorna ferramentas disponíveis (apenas as implementadas)"""
    return {
        'data_analysis': [
            {'id': 'sql_query', 'name': 'Consultas SQL', 'icon': '🔍'},
            {'id': 'eda_analysis', 'name': 'Análise Exploratória (EDA)', 'icon': '📊'}
        ],
        'calculations': [
            {'id': 'calculo_vale_refeicao', 'name': '🍽️ Cálculo de Vale Refeição', 'icon': '💰'}
        ],
        'export_tools': [
            {'id': 'excel_export', 'name': 'Exportar para Excel', 'icon': '📊'}
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
        CONTEXTO: Você é um agente autônomo inteligente para análise de dados.
        
        OBJETIVO: {config['prompt']}
        
        FERRAMENTAS DISPONÍVEIS: {', '.join(config['available_tools'])}
        
        INSTRUÇÕES:
        1. Analise os dados disponíveis nas tabelas
        2. Execute as operações solicitadas
        3. Gere resultados detalhados e organizados
        4. Forneça relatórios claros e informativos
        
        Execute de forma autônoma.
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

def render_chat_tab(db, data_tables):
    """Renderiza aba de chat interativo com IA"""
    
    st.markdown("### 💬 Chat Interativo com IA")
    st.caption("Converse com o agente inteligente e explore seus dados de forma interativa")
    
    # Inicializar histórico de chat se não existir
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = {
            'findings': [],
            'previous_queries': [],
            'data_explored': []
        }
    
    # Container para configurações
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🛠️ Ferramentas Disponíveis")
            
            # Seleção de ferramentas
            available_tools = [
                "sql_query",
                "eda_analysis", 
                "excel_export",
                "correlation_analysis",
                "statistical_summary"
            ]
            
            selected_tools = st.multiselect(
                "Selecione as ferramentas que o agente pode usar:",
                options=available_tools,
                default=["sql_query", "eda_analysis"],
                help="Escolha quais ferramentas o agente pode utilizar durante a conversa"
            )
        
        with col2:
            st.markdown("#### ⚙️ Configurações")
            
            # Opções de configuração
            show_reasoning = st.checkbox("Mostrar raciocínio do agente", value=False)
            max_iterations = st.slider("Máximo de iterações por pergunta", 1, 10, 5)
            
            # Botão para limpar chat
            if st.button("🗑️ Limpar Conversa", type="secondary"):
                st.session_state.chat_messages = []
                st.session_state.chat_context = {
                    'findings': [],
                    'previous_queries': [],
                    'data_explored': []
                }
                st.rerun()
    
    st.markdown("---")
    
    # Exibir histórico de chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"], avatar=message.get("avatar")):
                if message["role"] == "user":
                    st.markdown(message["content"])
                else:
                    # Para mensagens do assistant, renderizar conteúdo complexo
                    if isinstance(message["content"], dict):
                        # Texto principal
                        if "text" in message["content"]:
                            st.markdown(message["content"]["text"])
                        
                        # Gráficos
                        if "plots" in message["content"] and message["content"]["plots"]:
                            for plot in message["content"]["plots"]:
                                st.image(f"data:image/png;base64,{plot['image']}", 
                                       caption=plot.get('title', 'Gráfico'))
                        
                        # Tabelas
                        if "tables" in message["content"] and message["content"]["tables"]:
                            for table in message["content"]["tables"]:
                                st.dataframe(table["data"])
                        
                        # Insights
                        if "insights" in message["content"] and message["content"]["insights"]:
                            with st.expander("💡 Insights Descobertos", expanded=True):
                                for insight in message["content"]["insights"]:
                                    st.write(f"• {insight}")
                    else:
                        st.markdown(message["content"])
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua pergunta sobre os dados..."):
        # Adicionar mensagem do usuário
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt,
            "avatar": "🧑‍💻"
        })
        
        # Adicionar à lista de queries anteriores
        st.session_state.chat_context['previous_queries'].append(prompt)
        
        # Rerun para mostrar a mensagem do usuário
        st.rerun()
    
    # Processar resposta se houver nova mensagem
    if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analisando sua pergunta..."):
                # Container para a resposta
                response_container = st.container()
                
                # Executar análise
                response = execute_chat_analysis(
                    db, 
                    data_tables, 
                    st.session_state.chat_messages[-1]["content"],
                    selected_tools,
                    st.session_state.chat_context,
                    show_reasoning,
                    max_iterations,
                    response_container
                )
                
                # Adicionar resposta ao histórico
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response,
                    "avatar": "🤖"
                })

def execute_chat_analysis(db, data_tables, query, tools, context, show_reasoning, max_iterations, container):
    """Executa análise para o chat interativo"""
    
    from .database_viewer import execute_autonomous_agent
    import json
    
    # Construir prompt com contexto
    context_summary = ""
    if context['previous_queries']:
        context_summary = f"\nCONTEXTO DA CONVERSA:\n"
        for i, prev_query in enumerate(context['previous_queries'][-5:], 1):  # Últimas 5 perguntas
            context_summary += f"{i}. {prev_query}\n"
    
    if context['findings']:
        context_summary += f"\nDESCOBERTAS ANTERIORES:\n"
        for finding in context['findings'][-3:]:  # Últimas 3 descobertas
            context_summary += f"- {finding}\n"
    
    # Prompt aprimorado para o agente
    enhanced_prompt = f"""
    CONTEXTO: Você é um assistente de análise de dados conversacional e inteligente.
    {context_summary}
    
    PERGUNTA ATUAL: {query}
    
    INSTRUÇÕES:
    1. Responda de forma clara e direta
    2. Use as ferramentas disponíveis para obter dados precisos
    3. Se gráficos forem solicitados, gere-os usando Python/matplotlib
    4. Mantenha o contexto da conversa em mente
    5. Seja conciso mas completo
    
    FERRAMENTAS DISPONÍVEIS: {', '.join(tools)}
    """
    
    # Configuração para o agente
    config = {
        'available_tools': tools,
        'show_reasoning': show_reasoning,
        'max_iterations': max_iterations,
        'enable_ai': True,
        'max_turn_limit': max_iterations,
        'exploration_depth': 'Intermediária',  # Valor padrão para profundidade
        'include_insights': True,
        'analysis_approach': 'comprehensive'
    }
    
    # Container temporário para capturar a saída
    # Limpar análises anteriores
    if 'agent_analyses' in st.session_state:
        prev_count = len(st.session_state.agent_analyses)
    else:
        prev_count = 0
    
    with container:
        success = execute_autonomous_agent(db, data_tables, enhanced_prompt, config, container)
    
    # Processar resultado
    if success and 'agent_analyses' in st.session_state and len(st.session_state.agent_analyses) > prev_count:
        # Pegar a última análise
        results = st.session_state.agent_analyses[-1]
        
        # Extrair componentes da resposta
        response_content = {
            "text": "",
            "plots": [],
            "tables": [],
            "insights": []
        }
        
        # Extrair resposta final
        final_step = None
        for step in results.get('steps', []):
            if step.get('action') == 'Síntese Final':
                final_step = step
                break
        
        if final_step and 'result' in final_step:
            response_content['text'] = final_step['result'].get('final_answer', 'Análise concluída.')
        
        # Extrair gráficos e insights de todas as etapas
        for step in results.get('steps', []):
            if isinstance(step, dict) and 'result' in step:
                result = step['result']
                if isinstance(result, dict):
                    # Extrair plots
                    if result.get('plots'):
                        response_content['plots'].extend(result['plots'])
                    
                    # Extrair insights
                    if result.get('insights'):
                        for insight in result['insights']:
                            if isinstance(insight, str):
                                response_content['insights'].append(insight)
                            elif isinstance(insight, dict) and 'text' in insight:
                                response_content['insights'].append(insight['text'])
                    
                    # Extrair tabelas de resultados SQL
                    if result.get('query_result') and isinstance(result['query_result'], list):
                        response_content['tables'].append({
                            'data': pd.DataFrame(result['query_result']),
                            'title': result.get('target_table', 'Resultado SQL')
                        })
        
        # Atualizar contexto
        context['findings'].append(response_content['text'])
        
        return response_content
    else:
        return {
            "text": "Desculpe, não consegui processar sua pergunta. Por favor, tente reformulá-la.",
            "plots": [],
            "tables": [],
            "insights": []
        }
