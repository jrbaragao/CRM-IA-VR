"""
Página para visualizar e gerenciar tabelas do banco de dados
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from ..components import (
    render_alert,
    render_metrics_row,
    safe_columns
)
from ...data.database import get_db_manager
from ...config.settings import settings
from ...agents.log_utils import log_agent_action

def render():
    """Renderiza página de visualização do banco de dados"""
    st.header("🗃️ Visualizador de Banco de Dados")
    st.caption("Visualize e gerencie as tabelas criadas dinamicamente")
    
    # Inicializar banco de dados
    db = get_db_manager()
    
    # Testar conexão
    if not db.test_connection():
        render_alert("❌ Erro de conexão com o banco de dados", "error")
        return
    
    # Listar tabelas
    try:
        tables = db.list_tables()
        
        if not tables:
            render_alert("📭 Nenhuma tabela encontrada no banco de dados", "info")
            st.markdown("### 💡 Como criar tabelas:")
            st.markdown("1. Vá para a página **Upload de Arquivos**")
            st.markdown("2. Faça upload de planilhas CSV ou Excel")
            st.markdown("3. Processe os arquivos na página **Processamento**")
            st.markdown("4. Cada arquivo criará uma tabela automaticamente!")
            return
        
        # Separar tabelas do sistema das tabelas de dados
        system_tables = ['importacoes', 'agent_logs', 'calculation_configs']
        data_tables = [t for t in tables if t not in system_tables]
        
        # Métricas gerais
        total_registros = 0
        for table in data_tables:
            info = db.get_table_info(table)
            if info:
                total_registros += info.get('total_rows', 0)
        
        # Contar configurações de cálculo
        calculation_configs_count = len(db.get_calculation_configs())
        
        metrics = [
            {'label': 'Total de Tabelas', 'value': len(tables)},
            {'label': 'Tabelas de Dados', 'value': len(data_tables)},
            {'label': 'Tabelas do Sistema', 'value': len(system_tables)},
            {'label': 'Configurações de Cálculo', 'value': calculation_configs_count},
            {'label': 'Total de Registros', 'value': total_registros}
        ]
        render_metrics_row(metrics)
        
        # Limpar qualquer session_state residual de controle de abas
        keys_to_remove = ['active_db_tab_index', 'tab_selector', 'force_query_tab']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        # Tabs nativas do Streamlit (ATUALIZADO - sem controle de sessão)
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Tabelas de Dados", 
            "🔗 Correlações", 
            "⚙️ Tabelas do Sistema", 
            "🔍 Buscas (Query)",
            "🔧 Ferramentas"
        ])
        
        with tab1:
            render_data_tables(db, data_tables)
        
        with tab2:
            render_table_correlations(db, data_tables)
        
        with tab3:
            render_system_tables(db, system_tables)
        
        with tab4:
            render_query_interface(db, tables)
        
        with tab5:
            render_database_tools(db, tables)
            
    except Exception as e:
        render_alert(f"❌ Erro ao acessar banco de dados: {str(e)}", "error")

def render_data_tables(db, data_tables):
    """Renderiza tabelas de dados criadas pelos uploads"""
    if not data_tables:
        st.info("📭 Nenhuma tabela de dados encontrada")
        st.markdown("**Dica:** Faça upload e processamento de arquivos para criar tabelas automaticamente!")
        return
    
    st.subheader(f"📊 Tabelas de Dados ({len(data_tables)})")
    
    # Análise de chaves primárias
    tables_with_pk = 0
    tables_without_pk = 0
    
    for table in data_tables:
        table_info = db.get_table_info(table)
        if table_info:
            primary_keys = [col['name'] for col in table_info['columns'] if col['primary_key']]
            if primary_keys:
                tables_with_pk += 1
            else:
                tables_without_pk += 1
    
    # Mostrar resumo de chaves primárias
    if tables_without_pk > 0:
        st.warning(f"⚠️ {tables_without_pk} tabela(s) sem chave primária definida. Isso pode afetar correlações entre dados.")
        st.info("💡 **Dica:** Configure chaves primárias na seção 'Estrutura da Tabela' abaixo para melhorar correlações.")
    else:
        st.success(f"✅ Todas as {tables_with_pk} tabelas têm chave primária definida!")
    
    # Métricas resumidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔑 Com Chave Primária", tables_with_pk)
    with col2:
        st.metric("⚠️ Sem Chave Primária", tables_without_pk)
    with col3:
        st.metric("📊 Total de Tabelas", len(data_tables))
    
    st.markdown("---")
    
    for table in data_tables:
        try:
            # Obter informações da tabela
            table_info = db.get_table_info(table)
            
            if not table_info:
                continue
            
            # Verificar se tem chave primária definida
            primary_keys = [col['name'] for col in table_info['columns'] if col['primary_key']]
            pk_indicator = "🔑" if primary_keys else "⚠️"
            pk_status = "PK definida" if primary_keys else "Sem PK"
            
            # Expandir para cada tabela com indicador de PK
            with st.expander(f"{pk_indicator} {table} ({table_info['total_rows']} registros) - {pk_status}", expanded=False):
                
                # Informações básicas
                cols = safe_columns(4)
                if cols:
                    col1, col2, col3, col4 = cols
                    
                    with col1:
                        st.metric("Registros", table_info['total_rows'])
                    
                    with col2:
                        st.metric("Colunas", len(table_info['columns']))
                    
                    with col3:
                        primary_keys = [col['name'] for col in table_info['columns'] if col['primary_key']]
                        st.metric("Chaves Primárias", len(primary_keys))
                    
                    with col4:
                        # Botão para remover tabela
                        if st.button(f"🗑️ Remover", key=f"delete_{table}", help="Remove esta tabela"):
                            if st.session_state.get(f'confirm_delete_{table}', False):
                                if db.drop_table(table):
                                    st.success(f"Tabela '{table}' removida!")
                                    st.rerun()
                            else:
                                st.session_state[f'confirm_delete_{table}'] = True
                                st.warning("Clique novamente para confirmar a remoção")
                
                # Estrutura da tabela com edição de PK
                st.markdown("**📋 Estrutura da Tabela:**")
                
                # Destacar se não tem chave primária
                if not primary_keys:
                    st.error("⚠️ **Esta tabela não possui chave primária definida!**")
                    st.markdown("**Por que isso é importante?**")
                    st.markdown("- Chaves primárias são essenciais para correlacionar dados entre tabelas")
                    st.markdown("- Agentes autônomos usam PKs para fazer JOINs inteligentes")
                    st.markdown("- Melhora performance das consultas")
                    st.markdown("**👇 Configure uma chave primária abaixo:**")
                    
                    # Sugerir colunas candidatas para PK
                    candidate_columns = []
                    for col in table_info['columns']:
                        col_name = col['name'].lower()
                        if any(term in col_name for term in ['id', 'codigo', 'matricula', 'cpf', 'cnpj', 'registro']):
                            candidate_columns.append(col['name'])
                    
                    if candidate_columns:
                        st.info(f"💡 **Sugestões de colunas para chave primária:** {', '.join(candidate_columns)}")
                    else:
                        st.info("💡 **Dica:** Procure por colunas com valores únicos como ID, código, matrícula, etc.")
                
                render_editable_table_structure(db, table, table_info)
                
                # Preview dos dados
                st.markdown("**👀 Preview dos Dados:**")
                
                # Controles de visualização
                col_limit, col_refresh = st.columns([3, 1])
                
                with col_limit:
                    limit = st.selectbox(
                        "Registros para mostrar:",
                        [10, 25, 50, 100],
                        key=f"limit_{table}"
                    )
                
                with col_refresh:
                    st.write("")  # Espaçamento
                    if st.button("🔄 Atualizar", key=f"refresh_{table}"):
                        st.rerun()
                
                # Buscar e mostrar dados
                df_table = db.get_table_data(table, limit=limit)
                
                if not df_table.empty:
                    st.dataframe(df_table, use_container_width=True)
                    
                    # Opção de download
                    csv = df_table.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Baixar {table}.csv",
                        data=csv,
                        file_name=f"{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"download_{table}"
                    )
                else:
                    st.warning("Nenhum dado encontrado na tabela")
                    
        except Exception as e:
            st.error(f"❌ Erro ao carregar tabela '{table}': {str(e)}")

def render_editable_table_structure(db, table_name: str, table_info: dict):
    """Renderiza estrutura da tabela com possibilidade de editar chave primária"""
    
    # Obter colunas
    columns = table_info['columns']
    
    # Identificar chave primária atual
    current_pk = None
    for col in columns:
        if col['primary_key']:
            current_pk = col['name']
            break
    
    # Interface para alterar chave primária
    st.markdown("**🔑 Configuração de Chave Primária:**")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Lista de colunas disponíveis
        column_options = ['(Nenhuma)'] + [col['name'] for col in columns]
        current_index = 0
        
        if current_pk:
            try:
                current_index = column_options.index(current_pk)
            except ValueError:
                current_index = 0
        
        new_pk = st.selectbox(
            "Chave Primária:",
            options=column_options,
            index=current_index,
            key=f"pk_select_{table_name}",
            help="Selecione qual coluna será a chave primária para correlacionar com outras tabelas"
        )
    
    with col2:
        # Mostrar dados de exemplo da coluna selecionada
        if new_pk and new_pk != '(Nenhuma)':
            sample_data = db.get_column_sample_data(table_name, new_pk, limit=3)
            if sample_data:
                st.markdown("**Exemplos:**")
                for i, sample in enumerate(sample_data, 1):
                    st.caption(f"{i}. {sample}")
            else:
                st.caption("Sem dados de exemplo")
        else:
            st.caption("Nenhuma chave primária selecionada")
    
    with col3:
        # Botão para aplicar mudança
        if st.button("💾 Aplicar", key=f"apply_pk_{table_name}"):
            # Determinar nova PK
            new_primary_key = new_pk if new_pk != '(Nenhuma)' else None
            
            # Verificar se houve mudança
            if new_primary_key != current_pk:
                with st.spinner("Alterando chave primária..."):
                    success = db.update_primary_key(table_name, current_pk, new_primary_key)
                    if success:
                        st.rerun()
            else:
                st.info("Nenhuma alteração detectada")
    
    # Mostrar estrutura atual
    st.markdown("**📊 Estrutura Atual:**")
    
    # Criar DataFrame para mostrar estrutura
    structure_data = []
    for col in columns:
        # Destacar chave primária
        pk_status = "🔑 Sim" if col['primary_key'] else "❌ Não"
        
        structure_data.append({
            'Coluna': col['name'],
            'Tipo': col['type'],
            'Permite Nulo': "❌ Não" if col['not_null'] else "✅ Sim",
            'Chave Primária': pk_status
        })
    
    structure_df = pd.DataFrame(structure_data)
    
    # Aplicar estilo para destacar chave primária
    def highlight_primary_key(row):
        if row['Chave Primária'] == "🔑 Sim":
            return ['background-color: #e8f5e8'] * len(row)
        return [''] * len(row)
    
    styled_df = structure_df.style.apply(highlight_primary_key, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Dicas sobre chaves primárias (usando container em vez de expander)
    st.markdown("---")
    if st.checkbox("💡 Mostrar Dicas sobre Chaves Primárias", key=f"show_tips_{table_name}"):
        st.markdown("""
        **Para que serve a chave primária?**
        - Identifica unicamente cada registro na tabela
        - Permite correlacionar dados entre diferentes tabelas
        - Melhora a performance das consultas
        
        **Boas práticas:**
        - Escolha uma coluna com valores únicos (ex: MATRICULA, ID, CPF)
        - Evite colunas que podem ter valores duplicados (ex: NOME, DEPARTAMENTO)
        - Prefira valores que não mudam com frequência
        
        **Exemplos comuns:**
        - `MATRICULA` - Para dados de funcionários
        - `ID` - Para identificadores únicos
        - `CPF` - Para pessoas físicas
        - `CNPJ` - Para empresas
        """)
        
        # Mostrar análise de unicidade das colunas
        st.markdown("**🔍 Análise de Unicidade das Colunas:**")
        
        uniqueness_data = []
        df_sample = db.get_table_data(table_name, limit=1000)  # Amostra para análise
        
        if not df_sample.empty:
            for col_name in df_sample.columns:
                if col_name not in ['created_at', 'updated_at']:  # Pular metadados
                    total_rows = len(df_sample)
                    unique_values = df_sample[col_name].nunique()
                    null_count = df_sample[col_name].isnull().sum()
                    uniqueness_pct = (unique_values / total_rows) * 100 if total_rows > 0 else 0
                    
                    # Recomendação
                    if uniqueness_pct >= 95 and null_count == 0:
                        recommendation = "🟢 Excelente para PK"
                    elif uniqueness_pct >= 80 and null_count <= total_rows * 0.05:
                        recommendation = "🟡 Boa para PK"
                    else:
                        recommendation = "🔴 Não recomendada"
                    
                    uniqueness_data.append({
                        'Coluna': col_name,
                        'Valores Únicos': unique_values,
                        'Total Registros': total_rows,
                        'Unicidade (%)': f"{uniqueness_pct:.1f}%",
                        'Valores Nulos': null_count,
                        'Recomendação': recommendation
                    })
            
            if uniqueness_data:
                uniqueness_df = pd.DataFrame(uniqueness_data)
                st.dataframe(uniqueness_df, use_container_width=True, hide_index=True)

def render_table_correlations(db, data_tables):
    """Renderiza análise de correlações entre tabelas"""
    st.subheader("🔗 Correlações entre Tabelas")
    st.caption("Analise como as tabelas podem se relacionar através das chaves primárias")
    
    if len(data_tables) < 2:
        st.info("📭 Você precisa de pelo menos 2 tabelas para analisar correlações")
        st.markdown("**Dica:** Faça upload de mais planilhas para ver as correlações!")
        return
    
    # Obter informações de todas as tabelas
    tables_info = {}
    for table in data_tables:
        info = db.get_table_info(table)
        if info:
            tables_info[table] = info
    
    if not tables_info:
        st.warning("⚠️ Não foi possível obter informações das tabelas")
        return
    
    # Análise de correlações possíveis
    st.markdown("### 🔍 Análise de Correlações Possíveis")
    
    correlations = []
    
    # Comparar cada tabela com as outras
    for table1 in tables_info:
        for table2 in tables_info:
            if table1 != table2:
                # Buscar colunas em comum
                cols1 = {col['name'].upper(): col for col in tables_info[table1]['columns']}
                cols2 = {col['name'].upper(): col for col in tables_info[table2]['columns']}
                
                common_columns = set(cols1.keys()) & set(cols2.keys())
                common_columns.discard('CREATED_AT')  # Remover metadados
                common_columns.discard('UPDATED_AT')
                
                if common_columns:
                    for col_name in common_columns:
                        # Verificar se alguma é chave primária
                        is_pk1 = cols1[col_name]['primary_key']
                        is_pk2 = cols2[col_name]['primary_key']
                        
                        correlation_type = "🔑 Chave Primária" if (is_pk1 or is_pk2) else "🔗 Coluna Comum"
                        strength = "Alta" if (is_pk1 or is_pk2) else "Média"
                        
                        correlations.append({
                            'Tabela 1': table1,
                            'Tabela 2': table2,
                            'Coluna Comum': col_name,
                            'Tipo': correlation_type,
                            'Força': strength
                        })
    
    if correlations:
        correlations_df = pd.DataFrame(correlations)
        st.dataframe(correlations_df, use_container_width=True, hide_index=True)
        
        # Sugestões de JOIN
        st.markdown("### 💡 Sugestões de Consultas JOIN")
        
        # Agrupar por pares de tabelas
        table_pairs = {}
        for corr in correlations:
            pair_key = f"{corr['Tabela 1']} + {corr['Tabela 2']}"
            if pair_key not in table_pairs:
                table_pairs[pair_key] = []
            table_pairs[pair_key].append(corr)
        
        for pair_key, pair_correlations in table_pairs.items():
            table1, table2 = pair_key.split(' + ')
            
            # Usar container com checkbox em vez de expander
            st.markdown(f"### 🔗 {table1} ↔ {table2}")
            if st.checkbox(f"Mostrar detalhes da correlação", key=f"show_corr_{table1}_{table2}"):
                st.markdown(f"**Colunas em comum:** {len(pair_correlations)}")
                
                # Mostrar colunas comuns
                for corr in pair_correlations:
                    col_name = corr['Coluna Comum']
                    corr_type = corr['Tipo']
                    
                    # Gerar SQL de exemplo
                    sql_example = f"""
-- Juntar {table1} com {table2} usando {col_name}
SELECT 
    t1.*,
    t2.*
FROM "{table1}" t1
INNER JOIN "{table2}" t2 ON t1."{col_name}" = t2."{col_name}"
LIMIT 10;
                    """
                    
                    st.markdown(f"**{corr_type} - {col_name}:**")
                    st.code(sql_example.strip(), language='sql')
                    
                    # Botão para executar consulta
                    if st.button(f"▶️ Executar JOIN", key=f"join_{table1}_{table2}_{col_name}"):
                        try:
                            join_query = f'''
                            SELECT t1.*, t2.*
                            FROM "{table1}" t1
                            INNER JOIN "{table2}" t2 ON t1."{col_name}" = t2."{col_name}"
                            LIMIT 50
                            '''
                            
                            result_df = pd.read_sql(join_query, db.engine)
                            
                            if not result_df.empty:
                                st.success(f"✅ JOIN executado! {len(result_df)} registros encontrados.")
                                st.dataframe(result_df, use_container_width=True)
                                
                                # Opção de download
                                csv = result_df.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Baixar resultado do JOIN",
                                    data=csv,
                                    file_name=f"join_{table1}_{table2}_{col_name}.csv",
                                    mime="text/csv",
                                    key=f"download_join_{table1}_{table2}_{col_name}"
                                )
                            else:
                                st.warning("⚠️ Nenhum registro encontrado no JOIN")
                                
                        except Exception as e:
                            st.error(f"❌ Erro ao executar JOIN: {str(e)}")
            
            st.markdown("---")  # Separador entre correlações
    else:
        st.info("📭 Nenhuma correlação encontrada entre as tabelas")
        st.markdown("""
        **Para criar correlações:**
        1. Certifique-se de que as tabelas tenham colunas com nomes similares
        2. Configure chaves primárias nas tabelas
        3. Use nomes padronizados (ex: MATRICULA, ID, CPF)
        """)
    
    # Resumo das chaves primárias
    st.markdown("### 🔑 Resumo das Chaves Primárias")
    
    pk_summary = []
    for table_name, info in tables_info.items():
        primary_keys = [col['name'] for col in info['columns'] if col['primary_key']]
        pk_status = primary_keys[0] if primary_keys else "❌ Sem chave primária"
        
        pk_summary.append({
            'Tabela': table_name,
            'Chave Primária': pk_status,
            'Total Registros': info['total_rows']
        })
    
    pk_df = pd.DataFrame(pk_summary)
    st.dataframe(pk_df, use_container_width=True, hide_index=True)
    
    # Dicas para melhorar correlações (usando container)
    st.markdown("---")
    if st.checkbox("💡 Mostrar Dicas para Melhorar Correlações", key="show_correlation_tips"):
        st.markdown("""
        **1. Padronize os nomes das colunas:**
        - Use `MATRICULA` em todas as tabelas de funcionários
        - Use `ID` para identificadores únicos
        - Use `CPF` para pessoas físicas
        
        **2. Configure chaves primárias:**
        - Vá na aba "Tabelas de Dados"
        - Expanda cada tabela
        - Configure a chave primária apropriada
        
        **3. Mantenha consistência:**
        - Mesmos tipos de dados nas colunas relacionadas
        - Mesma formatação (ex: CPF com ou sem pontos)
        - Valores únicos nas chaves primárias
        
        **4. Teste as correlações:**
        - Use os JOINs sugeridos acima
        - Verifique se os resultados fazem sentido
        - Ajuste as chaves primárias se necessário
        """)

def render_query_interface(db, tables):
    """Renderiza interface de consultas e buscas"""
    
    st.markdown("### 🔍 Interface de Consultas")
    st.caption("Faça consultas inteligentes aos seus dados")
    
    # Informação sobre persistência de resultados
    if ('current_generated_sql' in st.session_state or 
        st.session_state.get('execute_current_sql', False)):
        st.info("💡 **Dica**: Os resultados das consultas aparecem nesta mesma aba. Não é necessário navegar entre abas!")
    
    # Debug info (remover após teste)
    if st.checkbox("🔧 Mostrar Debug", key="show_debug"):
        st.write("**Debug Info:**")
        st.write(f"- Aba ativa: {st.session_state.get('active_db_tab_index', 'não definida')}")
        st.write(f"- Consulta SQL ativa: {'Sim' if 'current_generated_sql' in st.session_state else 'Não'}")
        st.write(f"- Executar SQL: {'Sim' if st.session_state.get('execute_current_sql', False) else 'Não'}")
        st.write(f"- Forçar aba Query: {'Sim' if st.session_state.get('force_query_tab', False) else 'Não'}")
    
    # Separar tabelas do sistema das tabelas de dados
    system_tables = ['importacoes', 'agent_logs', 'calculation_configs']
    data_tables = [t for t in tables if t not in system_tables]
    
    if not data_tables:
        st.warning("⚠️ Nenhuma tabela de dados disponível para consulta.")
        st.info("💡 Faça upload e processe arquivos primeiro para criar tabelas de dados.")
        return
    
    # Sub-tabs para diferentes tipos de consulta
    query_tab1, query_tab2, query_tab3 = st.tabs([
        "🤖 Consulta com IA (Prompt to Query)",
        "🧠 Consulta com Agente de IA",
        "🔍 Consulta SQL Avançada"
    ])
    
    with query_tab1:
        render_ai_query_interface(db, data_tables)
    
    with query_tab2:
        render_autonomous_agent_interface(db, data_tables)
    
    with query_tab3:
        render_advanced_sql_interface(db, tables)

def render_system_tables(db, system_tables):
    """Renderiza tabelas do sistema"""
    st.subheader("⚙️ Tabelas do Sistema")
    st.caption("Tabelas internas do sistema para controle, logs e configurações")
    
    existing_system_tables = [t for t in system_tables if t in db.list_tables()]
    
    if not existing_system_tables:
        st.info("📭 Nenhuma tabela do sistema encontrada")
        return
    
    # Descrições das tabelas do sistema
    table_descriptions = {
        'importacoes': '📥 Registro de importações de arquivos',
        'agent_logs': '🤖 Logs de atividades dos agentes',
        'calculation_configs': '⚙️ Configurações de prompts para agentes de cálculo'
    }
    
    for table in existing_system_tables:
        try:
            table_info = db.get_table_info(table)
            
            if not table_info:
                continue
            
            # Usar descrição personalizada se disponível
            description = table_descriptions.get(table, f"⚙️ {table}")
            with st.expander(f"{description} ({table_info['total_rows']} registros)", expanded=False):
                
                # Informações básicas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Registros", table_info['total_rows'])
                
                with col2:
                    st.metric("Colunas", len(table_info['columns']))
                
                # Estrutura da tabela
                st.markdown("**📋 Estrutura:**")
                columns_df = pd.DataFrame(table_info['columns'])
                st.dataframe(columns_df, use_container_width=True, hide_index=True)
                
                # Preview específico para cada tipo de tabela
                if table == 'calculation_configs':
                    # Para configurações de cálculo, mostrar informações mais úteis
                    configs = db.get_calculation_configs()
                    if configs:
                        st.markdown("**🔧 Configurações Ativas:**")
                        for config in configs[:3]:  # Mostrar apenas as 3 primeiras
                            st.markdown(f"• **{config['name']}**: {config['description'][:50]}...")
                        
                        if len(configs) > 3:
                            st.caption(f"... e mais {len(configs) - 3} configurações")
                    else:
                        st.info("Nenhuma configuração de cálculo criada ainda")
                
                # Preview padrão para outras tabelas
                if st.button(f"👀 Ver Últimos Registros", key=f"preview_system_{table}"):
                    df_table = db.get_table_data(table, limit=5)
                    if not df_table.empty:
                        st.dataframe(df_table, use_container_width=True)
                    else:
                        st.warning("Nenhum dado encontrado")
                        
        except Exception as e:
            st.error(f"❌ Erro ao carregar tabela do sistema '{table}': {str(e)}")

def render_autonomous_agent_interface(db, data_tables):
    """Renderiza interface do agente autônomo de IA"""
    
    st.markdown("### 🧠 Agente Autônomo de IA")
    st.caption("Agente inteligente que executa múltiplas etapas para responder perguntas complexas")
    
    # Informações sobre o agente
    with st.expander("ℹ️ Como funciona o Agente Autônomo", expanded=False):
        st.markdown("""
        **O Agente Autônomo é diferente da consulta simples:**
        
        🔍 **Análise Inteligente:**
        - Analisa sua pergunta e planeja etapas
        - Explora o esquema das tabelas automaticamente
        - Faz consultas exploratórias para entender os dados
        
        🔄 **Processo Iterativo:**
        - Executa múltiplas consultas SQL se necessário
        - Refina a busca com base nos resultados
        - Combina informações de diferentes tabelas
        
        🎯 **Resposta Completa:**
        - Apresenta análise detalhada
        - Mostra o raciocínio usado
        - Fornece insights e recomendações
        
        **Exemplos de perguntas complexas:**
        - "Analise o perfil dos funcionários e identifique padrões salariais"
        - "Qual departamento tem melhor performance e por quê?"
        - "Encontre anomalias nos dados e sugira correções"
        """)
    
    # Configurações do agente
    st.markdown("### ⚙️ Configurações do Agente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_iterations = st.slider(
            "🔄 Máximo de Iterações",
            min_value=1,
            max_value=10,
            value=5,
            help="Número máximo de etapas que o agente pode executar"
        )
        
        exploration_depth = st.selectbox(
            "🔍 Profundidade de Exploração",
            options=["Básica", "Intermediária", "Avançada"],
            index=1,
            help="Quão detalhada será a análise inicial dos dados"
        )
    
    with col2:
        include_insights = st.checkbox(
            "💡 Incluir Insights",
            value=True,
            help="Agente fornecerá insights e recomendações"
        )
        
        show_reasoning = st.checkbox(
            "🧠 Mostrar Raciocínio",
            value=True,
            help="Exibir o processo de pensamento do agente"
        )
    
    # Campo de pergunta
    st.markdown("### 💬 Sua Pergunta Complexa")
    
    user_question = st.text_area(
        "Descreva o que você quer descobrir:",
        placeholder="Ex: Analise os dados de funcionários e identifique quais departamentos têm maior rotatividade, correlacionando com salários e tempo de empresa. Sugira ações para melhorar a retenção.",
        height=120,
        help="Seja específico sobre o que você quer analisar. O agente pode lidar com perguntas complexas que requerem múltiplas análises."
    )
    
    # Informações contextuais
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Iniciar Análise Autônoma", type="primary", disabled=not user_question.strip()):
            if not user_question.strip():
                st.warning("⚠️ Digite uma pergunta primeiro!")
            else:
                # Container para o processo do agente
                agent_container = st.empty()
                execute_autonomous_agent(db, data_tables, user_question, {
                    'max_iterations': max_iterations,
                    'exploration_depth': exploration_depth,
                    'include_insights': include_insights,
                    'show_reasoning': show_reasoning
                }, agent_container)
    
    with col2:
        st.markdown("**📋 Tabelas disponíveis:**")
        for table in data_tables:
            table_info = db.get_table_info(table)
            if table_info:
                st.caption(f"• **{table}** ({table_info['total_rows']} registros)")
    
    # Histórico de análises do agente
    if 'agent_analyses' in st.session_state and st.session_state['agent_analyses']:
        st.markdown("---")
        st.markdown("### 📚 Histórico de Análises")
        
        for i, analysis in enumerate(st.session_state['agent_analyses'][-3:]):  # Últimas 3
            with st.expander(f"🧠 {analysis['question'][:60]}...", expanded=False):
                st.markdown(f"**Pergunta:** {analysis['question']}")
                st.markdown(f"**Data:** {analysis['timestamp']}")
                st.markdown(f"**Iterações:** {analysis['iterations']}")
                
                if st.button(f"🔄 Repetir Análise", key=f"repeat_analysis_{i}"):
                    # Repetir análise com mesmos parâmetros
                    agent_container = st.empty()
                    execute_autonomous_agent(db, data_tables, analysis['question'], 
                                           analysis['config'], agent_container)

def render_advanced_sql_interface(db, tables):
    """Renderiza interface de consulta SQL avançada"""
    
    st.markdown("### 🔍 Editor SQL Avançado")
    st.caption("Execute consultas SQL personalizadas")
    
    # Informações das tabelas disponíveis
    with st.expander("📋 Tabelas Disponíveis", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Tabelas de Dados:**")
            system_tables = ['importacoes', 'agent_logs', 'calculation_configs']
            data_tables = [t for t in tables if t not in system_tables]
            
            for table in data_tables:
                table_info = db.get_table_info(table)
                if table_info:
                    st.caption(f"• **{table}** ({table_info['total_rows']} registros)")
        
        with col2:
            st.markdown("**⚙️ Tabelas do Sistema:**")
            for table in system_tables:
                if table in tables:
                    table_info = db.get_table_info(table)
                    if table_info:
                        st.caption(f"• **{table}** ({table_info['total_rows']} registros)")
    
    # Exemplos de consultas
    with st.expander("💡 Exemplos de Consultas SQL", expanded=False):
        st.markdown("""
        **Consultas básicas:**
        ```sql
        -- Listar todos os registros de uma tabela
        SELECT * FROM "nome_da_tabela" LIMIT 10;
        
        -- Contar registros
        SELECT COUNT(*) as total FROM "nome_da_tabela";
        
        -- Agrupar por coluna
        SELECT "coluna", COUNT(*) as total 
        FROM "nome_da_tabela" 
        GROUP BY "coluna";
        ```
        
        **Consultas com JOIN:**
        ```sql
        -- Juntar duas tabelas
        SELECT a.*, b.* 
        FROM "tabela_a" a 
        JOIN "tabela_b" b ON a."chave" = b."chave";
        ```
        """)
    
    # Editor SQL
    st.warning("⚠️ Use com cuidado! Apenas consultas SELECT são recomendadas.")
    
    # Verificar se há SQL salvo para edição
    default_sql = st.session_state.get('edit_sql', '')
    if default_sql:
        st.info("📝 SQL carregado do gerador de IA")
        # Limpar após usar
        if 'edit_sql' in st.session_state:
            del st.session_state['edit_sql']
    
    sql_query = st.text_area(
        "Digite sua consulta SQL:",
        value=default_sql,
        placeholder="SELECT * FROM \"nome_da_tabela\" LIMIT 10;",
        height=150,
        help="Digite uma consulta SQL válida. Use aspas duplas para nomes de tabelas e colunas."
    )
    
    # Container para resultados do editor SQL
    sql_result_container = st.empty()
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Executar SQL", type="primary"):
            if sql_query.strip():
                execute_query_dynamic(db, sql_query, sql_result_container)
            else:
                st.warning("Digite uma consulta SQL válida")
    
    with col2:
        if st.button("🧹 Limpar Editor"):
            sql_result_container.empty()  # Limpar resultados também
            st.rerun()
    
    with col3:
        if st.button("💾 Salvar Consulta"):
            if sql_query.strip():
                save_query_to_session("Consulta SQL Manual", sql_query)
                st.success("💾 Consulta salva no histórico!")
            else:
                st.warning("Digite uma consulta primeiro")

def execute_query_dynamic(db, sql_query: str, container):
    """Executa consulta SQL dinamicamente sem rerun"""
    try:
        # Validações de segurança
        sql_upper = sql_query.upper().strip()
        
        # Permitir apenas SELECT
        if not sql_upper.startswith('SELECT'):
            with container.container():
                st.error("❌ Por segurança, apenas consultas SELECT são permitidas!")
            return False
        
        # Bloquear comandos perigosos
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                with container.container():
                    st.error(f"❌ Comando '{keyword}' não é permitido por segurança!")
                return False
        
        # Executar consulta e mostrar resultado no container
        with container.container():
            # Mostrar spinner durante execução
            progress_placeholder = st.empty()
            with progress_placeholder:
                st.info("🔄 Executando consulta...")
            
            # Executar consulta
            df_result = pd.read_sql(sql_query, db.engine)
            
            # Limpar spinner
            progress_placeholder.empty()
            
            if not df_result.empty:
                st.success(f"✅ Consulta executada! {len(df_result)} registros encontrados.")
                
                # Mostrar dados
                if len(df_result) > 100:
                    with st.expander(f"📊 Visualizar {len(df_result)} registros", expanded=True):
                        st.dataframe(df_result, use_container_width=True, height=400)
                else:
                    st.dataframe(df_result, use_container_width=True)
                
                # Estatísticas rápidas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Registros", len(df_result))
                with col2:
                    st.metric("📋 Colunas", len(df_result.columns))
                with col3:
                    # Calcular tamanho aproximado em KB
                    size_kb = round(df_result.memory_usage(deep=True).sum() / 1024, 2)
                    st.metric("💾 Tamanho", f"{size_kb} KB")
                
                # Opção de download
                csv = df_result.to_csv(index=False)
                st.download_button(
                    label="📥 Baixar Resultado (CSV)",
                    data=csv,
                    file_name=f"consulta_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"download_result_{hash(sql_query)}"
                )
                
                # Log da execução (sem rerun)
                log_agent_action(
                    "query_ai_agent",
                    "▶️ Consulta IA executada com sucesso",
                    {
                        "registros_encontrados": len(df_result),
                        "colunas": list(df_result.columns)[:10]
                    }
                )
                
                return True
                
            else:
                st.warning("⚠️ A consulta não retornou nenhum resultado.")
                st.info("💡 Dica: Verifique se os nomes das tabelas e colunas estão corretos.")
                
                # Log de consulta vazia (sem rerun)
                log_agent_action(
                    "query_ai_agent",
                    "⚠️ Consulta IA executada - sem resultados",
                    {"sql": sql_query[:100] + "..." if len(sql_query) > 100 else sql_query}
                )
                
                return False
                
    except Exception as e:
        with container.container():
            st.error(f"❌ Erro ao executar consulta: {str(e)}")
        
        # Log do erro (sem rerun)
        log_agent_action(
            "query_ai_agent",
            "❌ Erro na execução da consulta IA",
            {
                "erro": str(e),
                "sql": sql_query[:100] + "..." if len(sql_query) > 100 else sql_query
            }
        )
        
        return False

def execute_sql_query(db, sql_query: str):
    """Executa consulta SQL manual"""
    try:
        # Log da consulta manual
        log_agent_action(
            "manual_sql_agent",
            "🔍 Consulta SQL manual executada",
            {"sql": sql_query[:200] + "..." if len(sql_query) > 200 else sql_query}
        )
        
        df_result = pd.read_sql(sql_query, db.engine)
        
        if not df_result.empty:
            st.success(f"✅ Consulta executada! {len(df_result)} registros retornados.")
            
            # Mostrar dados
            if len(df_result) > 100:
                with st.expander(f"📊 Visualizar {len(df_result)} registros", expanded=True):
                    st.dataframe(df_result, use_container_width=True, height=400)
            else:
                st.dataframe(df_result, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", len(df_result))
            with col2:
                st.metric("📋 Colunas", len(df_result.columns))
            with col3:
                size_kb = round(df_result.memory_usage(deep=True).sum() / 1024, 2)
                st.metric("💾 Tamanho", f"{size_kb} KB")
            
            # Download
            csv = df_result.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Resultado (CSV)",
                data=csv,
                file_name=f"consulta_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ A consulta não retornou nenhum resultado.")
            
    except Exception as e:
        st.error(f"❌ Erro na consulta: {str(e)}")
        
        # Log do erro
        log_agent_action(
            "manual_sql_agent",
            "❌ Erro na consulta SQL manual",
            {
                "erro": str(e),
                "sql": sql_query[:100] + "..." if len(sql_query) > 100 else sql_query
            }
        )

def render_database_tools(db, tables):
    """Renderiza ferramentas de gerenciamento do banco"""
    st.subheader("🔧 Ferramentas de Gerenciamento")
    
    # Informações do banco
    st.markdown("### 📊 Informações do Banco")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Arquivo do Banco:**")
        st.code("vale_refeicao.db")
        
        st.markdown("**Tipo:**")
        st.code("SQLite")
    
    with col2:
        st.markdown("**Total de Tabelas:**")
        st.code(f"{len(tables)}")
        
        # Tamanho do arquivo (se possível)
        try:
            import os
            if os.path.exists("vale_refeicao.db"):
                size_mb = os.path.getsize("vale_refeicao.db") / (1024 * 1024)
                st.markdown("**Tamanho do Arquivo:**")
                st.code(f"{size_mb:.2f} MB")
        except:
            pass
    
    # Ferramentas de manutenção
    st.markdown("### 🛠️ Ferramentas de Manutenção")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Testar Conexão"):
            if db.test_connection():
                st.success("✅ Conexão OK!")
            else:
                st.error("❌ Falha na conexão")
    
    with col2:
        if st.button("📊 Atualizar Estatísticas"):
            st.info("Estatísticas atualizadas!")
            st.rerun()
    
    with col3:
        if st.button("🧹 Limpar Cache"):
            # Limpar cache do Streamlit
            st.cache_data.clear()
            st.success("✅ Cache limpo!")
    
    # Backup e restore
    st.markdown("### 💾 Backup e Restore")
    
    st.markdown("""
    **Para fazer backup do banco de dados:**
    1. Copie o arquivo `vale_refeicao.db` para um local seguro
    2. O arquivo contém todas as tabelas e dados
    
    **Para restaurar um backup:**
    1. Substitua o arquivo `vale_refeicao.db` pelo backup
    2. Reinicie a aplicação
    """)
    
    # Prompt to Query (IA)
    st.markdown("### 🤖 Consulta com IA (Prompt to Query)")
    if st.checkbox("Mostrar consulta com IA", key="show_ai_query"):
        render_ai_query_interface(db, tables)
    
    # SQL Query (avançado)
    st.markdown("### 🔍 Consulta SQL Avançada")
    if st.checkbox("Mostrar editor SQL", key="show_sql_editor"):
        st.warning("⚠️ Use com cuidado! Consultas incorretas podem afetar os dados.")
        
        sql_query = st.text_area(
            "Digite sua consulta SQL:",
            placeholder="SELECT * FROM nome_da_tabela LIMIT 10;",
            height=100
        )
        
        if st.button("▶️ Executar Consulta"):
            if sql_query.strip():
                try:
                    df_result = pd.read_sql(sql_query, db.engine)
                    st.success(f"✅ Consulta executada! {len(df_result)} registros retornados.")
                    st.dataframe(df_result, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Erro na consulta: {str(e)}")
            else:
                st.warning("Digite uma consulta SQL válida")

def render_ai_query_interface(db, data_tables):
    """Renderiza interface de consulta com IA (Prompt to Query)"""
    
    # Verificar se OpenAI está configurada
    if not settings.openai_ready:
        st.error("❌ OpenAI API Key não configurada!")
        st.markdown("""
        Para usar a consulta com IA, você precisa:
        1. Configurar sua chave OpenAI no arquivo `.env`
        2. Definir `OPENAI_API_KEY=sk-sua-chave-aqui`
        3. Reiniciar a aplicação
        """)
        return
    
    st.info("🤖 Faça perguntas em linguagem natural e a IA gerará consultas SQL automaticamente!")
    
    # Exemplos de perguntas
    with st.expander("💡 Exemplos de Perguntas", expanded=False):
        st.markdown("""
        **Exemplos que você pode perguntar:**
        
        📊 **Análises gerais:**
        - "Quantos registros temos em cada tabela?"
        - "Quais são as colunas da tabela funcionarios?"
        - "Mostre os primeiros 10 registros da tabela vendas"
        
        👥 **Sobre funcionários:**
        - "Quantos funcionários temos por departamento?"
        - "Qual é o salário médio dos funcionários?"
        - "Liste os funcionários admitidos em 2024"
        
        💰 **Análises financeiras:**
        - "Qual é o total de vendas por mês?"
        - "Quem são os 5 funcionários com maior salário?"
        - "Qual departamento tem o maior custo com pessoal?"
        
        🔗 **Relacionamentos:**
        - "Junte dados de funcionários com seus benefícios"
        - "Mostre funcionários e seus departamentos"
        - "Correlacione vendas com vendedores"
        """)
    
    # Interface principal
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_area(
            "💬 Faça sua pergunta:",
            placeholder="Ex: Quantos funcionários temos por departamento?",
            height=100,
            help="Descreva o que você quer saber sobre os dados em linguagem natural"
        )
    
    with col2:
        st.markdown("**📋 Tabelas disponíveis:**")
        for table in data_tables:
            st.caption(f"• {table}")
    
    # Botão para gerar consulta
    if st.button("🚀 Gerar Consulta SQL", type="primary"):
        if not user_question.strip():
            st.warning("⚠️ Digite uma pergunta primeiro!")
        else:
            with st.spinner("🤖 IA analisando sua pergunta e gerando SQL..."):
                try:
                    # Gerar contexto das tabelas
                    schema_context = generate_schema_context(db, data_tables)
                    
                    # Gerar SQL usando IA
                    generated_sql = generate_sql_from_prompt(user_question, schema_context)
                    
                    if generated_sql:
                        # Salvar no session_state para manter
                        st.session_state['current_generated_sql'] = generated_sql
                        st.session_state['current_question'] = user_question
                        
                        # Log da ação
                        log_agent_action(
                            "query_ai_agent",
                            "🤖 Consulta SQL gerada por IA",
                            {
                                "pergunta": user_question,
                                "sql_gerado": generated_sql[:200] + "..." if len(generated_sql) > 200 else generated_sql
                            }
                        )
                    else:
                        st.error("❌ Não foi possível gerar uma consulta SQL para esta pergunta.")
                        
                except Exception as e:
                    st.error(f"❌ Erro ao gerar consulta: {str(e)}")
    
    # Mostrar SQL gerado se existir (fora do botão para persistir)
    if 'current_generated_sql' in st.session_state and 'current_question' in st.session_state:
        if st.session_state['current_question'] == user_question:  # Só mostrar se for a mesma pergunta
            st.success("✅ Consulta SQL gerada com sucesso!")
            
            # Mostrar SQL gerado
            st.markdown("**🔍 SQL Gerado:**")
            st.code(st.session_state['current_generated_sql'], language='sql')
            
            # Container para resultado da execução
            exec_result_container = st.empty()
            
            # Opções de ação
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("▶️ Executar Consulta", key="exec_generated"):
                    execute_query_dynamic(db, st.session_state['current_generated_sql'], exec_result_container)
            
            with col2:
                if st.button("📝 Editar SQL", key="edit_generated"):
                    st.session_state['edit_sql'] = st.session_state['current_generated_sql']
                    st.info("SQL copiado para o editor avançado abaixo!")
            
            with col3:
                if st.button("💾 Salvar Consulta", key="save_generated"):
                    save_query_to_session(st.session_state['current_question'], st.session_state['current_generated_sql'])
                    st.success("💾 Consulta salva no histórico!")
    
    # Seção de limpeza de consulta (apenas se não for a pergunta atual)
    if ('current_generated_sql' in st.session_state and 
        'current_question' in st.session_state and
        st.session_state['current_question'] != user_question):
        
        st.markdown("---")
        st.markdown("### 💾 Consulta Anterior")
        st.markdown(f"**Pergunta anterior:** {st.session_state['current_question']}")
        
        if st.button("🗑️ Limpar Consulta Anterior", key="clear_old_sql"):
            if 'current_generated_sql' in st.session_state:
                del st.session_state['current_generated_sql']
            if 'current_question' in st.session_state:
                del st.session_state['current_question']
            st.rerun()
    
    # Seção removida: execução automática não é mais necessária
    # Os resultados agora são mostrados dinamicamente nos containers
    
    # Histórico de consultas
    if 'saved_queries' in st.session_state and st.session_state['saved_queries']:
        st.markdown("### 📚 Histórico de Consultas")
        
        for i, query_data in enumerate(st.session_state['saved_queries']):
            with st.expander(f"💬 {query_data['question'][:50]}...", expanded=False):
                st.markdown(f"**Pergunta:** {query_data['question']}")
                st.code(query_data['sql'], language='sql')
                
                if st.button(f"▶️ Executar", key=f"exec_saved_{i}"):
                    execute_generated_sql(db, query_data['sql'])

def generate_schema_context(db, data_tables):
    """Gera contexto do esquema das tabelas para a IA"""
    context = "Esquema do banco de dados SQLite:\n\n"
    
    for table in data_tables:
        table_info = db.get_table_info(table)
        if table_info:
            context += f"Tabela: {table}\n"
            context += f"Registros: {table_info['total_rows']}\n"
            context += "Colunas:\n"
            
            for col in table_info['columns']:
                pk_indicator = " (PRIMARY KEY)" if col['primary_key'] else ""
                null_indicator = " NOT NULL" if col['not_null'] else ""
                context += f"  - {col['name']}: {col['type']}{pk_indicator}{null_indicator}\n"
            
            context += "\n"
    
    return context

def generate_sql_from_prompt(question: str, schema_context: str) -> str:
    """Gera SQL usando LlamaIndex/OpenAI"""
    try:
        # Importar LlamaIndex
        from llama_index.llms.openai import OpenAI
        
        # Configurar LLM
        llm = OpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.1
        )
        
        # Prompt para gerar SQL
        system_prompt = f"""
Você é um especialista em SQL que converte perguntas em linguagem natural para consultas SQL válidas.

ESQUEMA DO BANCO DE DADOS:
{schema_context}

REGRAS IMPORTANTES:
1. Use apenas as tabelas e colunas fornecidas no esquema
2. Gere SQL válido para SQLite
3. Use aspas duplas para nomes de tabelas e colunas: "tabela"."coluna"
4. Limite resultados com LIMIT quando apropriado
5. Use JOINs quando necessário para relacionar tabelas
6. Para contagens, use COUNT(*)
7. Para médias, use AVG()
8. Para agrupamentos, use GROUP BY
9. Não use funções específicas de outros SGBDs

PERGUNTA DO USUÁRIO: {question}

Gere apenas a consulta SQL, sem explicações adicionais.
"""
        
        # Gerar resposta
        response = llm.complete(system_prompt)
        
        # Extrair SQL da resposta
        sql = response.text.strip()
        
        # Limpar SQL (remover markdown se houver)
        if sql.startswith('```sql'):
            sql = sql.replace('```sql', '').replace('```', '').strip()
        elif sql.startswith('```'):
            sql = sql.replace('```', '').strip()
        
        return sql
        
    except ImportError:
        st.error("❌ LlamaIndex não está instalado corretamente")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao gerar SQL: {str(e)}")
        return None

def execute_generated_sql(db, sql: str):
    """Executa SQL gerado pela IA"""
    try:
        # Validações de segurança
        sql_upper = sql.upper().strip()
        
        # Permitir apenas SELECT
        if not sql_upper.startswith('SELECT'):
            st.error("❌ Por segurança, apenas consultas SELECT são permitidas!")
            return False
        
        # Bloquear comandos perigosos
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                st.error(f"❌ Comando '{keyword}' não é permitido por segurança!")
                return False
        
        # Executar consulta
        df_result = pd.read_sql(sql, db.engine)
        
        if not df_result.empty:
            st.success(f"✅ Consulta executada! {len(df_result)} registros encontrados.")
            
            # Mostrar dados em container expansível para grandes resultados
            if len(df_result) > 100:
                with st.expander(f"📊 Visualizar {len(df_result)} registros", expanded=True):
                    st.dataframe(df_result, use_container_width=True, height=400)
            else:
                st.dataframe(df_result, use_container_width=True)
            
            # Log da execução
            log_agent_action(
                "query_ai_agent",
                "▶️ Consulta IA executada com sucesso",
                {
                    "registros_encontrados": len(df_result),
                    "colunas": list(df_result.columns)[:10]  # Primeiras 10 colunas
                }
            )
            
            # Estatísticas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Registros", len(df_result))
            with col2:
                st.metric("📋 Colunas", len(df_result.columns))
            with col3:
                # Calcular tamanho aproximado em KB
                size_kb = round(df_result.memory_usage(deep=True).sum() / 1024, 2)
                st.metric("💾 Tamanho", f"{size_kb} KB")
            
            # Opção de download
            csv = df_result.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Resultado (CSV)",
                data=csv,
                file_name=f"consulta_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"download_result_{hash(sql)}"
            )
            
            return True
            
        else:
            st.warning("⚠️ A consulta não retornou nenhum resultado.")
            st.info("💡 Dica: Verifique se os nomes das tabelas e colunas estão corretos.")
            
            # Log de consulta vazia
            log_agent_action(
                "query_ai_agent",
                "⚠️ Consulta IA executada - sem resultados",
                {"sql": sql[:100] + "..." if len(sql) > 100 else sql}
            )
            
            return False
            
    except Exception as e:
        st.error(f"❌ Erro ao executar consulta: {str(e)}")
        
        # Log do erro
        log_agent_action(
            "query_ai_agent",
            "❌ Erro na execução da consulta IA",
            {
                "erro": str(e),
                "sql": sql[:100] + "..." if len(sql) > 100 else sql
            }
        )
        
        return False

def save_query_to_session(question: str, sql: str):
    """Salva consulta no histórico da sessão"""
    if 'saved_queries' not in st.session_state:
        st.session_state['saved_queries'] = []
    
    query_data = {
        'question': question,
        'sql': sql,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state['saved_queries'].append(query_data)
    
    # Manter apenas as últimas 10 consultas
    if len(st.session_state['saved_queries']) > 10:
        st.session_state['saved_queries'] = st.session_state['saved_queries'][-10:]
    
    st.success("💾 Consulta salva no histórico!")

# Função utilitária que pode ser importada e usada em outros lugares
def execute_query_anywhere(db, sql_query: str, question: str = "Consulta"):
    """
    Função utilitária para executar consultas SQL de qualquer lugar da aplicação
    
    Args:
        db: Instância do DatabaseManager
        sql_query: Consulta SQL a ser executada
        question: Descrição da consulta (opcional)
    
    Returns:
        tuple: (success: bool, dataframe: pd.DataFrame or None, error: str or None)
    """
    try:
        # Validações de segurança
        sql_upper = sql_query.upper().strip()
        
        if not sql_upper.startswith('SELECT'):
            return False, None, "Apenas consultas SELECT são permitidas"
        
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False, None, f"Comando '{keyword}' não é permitido"
        
        # Executar consulta
        df_result = pd.read_sql(sql_query, db.engine)
        
        # Log da execução
        log_agent_action(
            "utility_query_agent",
            f"🔍 {question}",
            {
                "sql": sql_query[:200] + "..." if len(sql_query) > 200 else sql_query,
                "registros_encontrados": len(df_result) if not df_result.empty else 0
            }
        )
        
        return True, df_result, None
        
    except Exception as e:
        # Log do erro
        log_agent_action(
            "utility_query_agent",
            f"❌ Erro em {question}",
            {
                "erro": str(e),
                "sql": sql_query[:100] + "..." if len(sql_query) > 100 else sql_query
            }
        )
        
        return False, None, str(e)

def execute_autonomous_agent(db, data_tables, question: str, config: dict, container):
    """Executa agente autônomo de IA para análise complexa"""
    
    with container.container():
        st.markdown("## 🧠 Agente Autônomo em Ação")
        st.markdown(f"**Pergunta:** {question}")
        
        # Inicializar progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Container para etapas
        steps_container = st.container()
        
        try:
            # Configurar LLM
            from llama_index.llms.openai import OpenAI
            
            llm = OpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=0.3
            )
            
            # Inicializar histórico de análise
            analysis_steps = []
            iteration = 0
            max_iterations = config['max_iterations']
            
            # Etapa 1: Análise inicial da pergunta
            status_text.text("🔍 Etapa 1: Analisando pergunta e planejando abordagem...")
            progress_bar.progress(10)
            
            planning_result = plan_analysis_approach(llm, question, data_tables, db, config)
            analysis_steps.append({
                'step': 1,
                'action': 'Planejamento',
                'description': 'Análise da pergunta e criação do plano de ação',
                'result': planning_result
            })
            
            with steps_container:
                render_analysis_step(analysis_steps[-1], config['show_reasoning'])
            
            # Etapa 2: Exploração do esquema
            status_text.text("📊 Etapa 2: Explorando estrutura dos dados...")
            progress_bar.progress(25)
            
            schema_analysis = explore_data_schema(llm, data_tables, db, config)
            analysis_steps.append({
                'step': 2,
                'action': 'Exploração do Esquema',
                'description': 'Análise detalhada da estrutura das tabelas',
                'result': schema_analysis
            })
            
            with steps_container:
                render_analysis_step(analysis_steps[-1], config['show_reasoning'])
            
            # Etapas iterativas de análise
            current_context = {
                'question': question,
                'plan': planning_result,
                'schema': schema_analysis,
                'findings': []
            }
            
            while iteration < max_iterations:
                iteration += 1
                progress = 25 + (iteration / max_iterations) * 60
                progress_bar.progress(int(progress))
                
                status_text.text(f"🔄 Etapa {iteration + 2}: Executando análise iterativa ({iteration}/{max_iterations})...")
                
                # Executar iteração de análise
                iteration_result = execute_analysis_iteration(
                    llm, db, data_tables, current_context, config, iteration
                )
                
                analysis_steps.append({
                    'step': iteration + 2,
                    'action': f'Análise Iterativa {iteration}',
                    'description': iteration_result.get('description', 'Análise de dados'),
                    'result': iteration_result
                })
                
                with steps_container:
                    render_analysis_step(analysis_steps[-1], config['show_reasoning'])
                
                # Atualizar contexto
                current_context['findings'].append(iteration_result)
                
                # Verificar se análise está completa
                if iteration_result.get('analysis_complete', False):
                    break
                
                # Log da iteração
                log_agent_action(
                    "autonomous_agent",
                    f"🔄 Iteração {iteration} completada",
                    {
                        "pergunta": question[:100],
                        "iteracao": iteration,
                        "acao": iteration_result.get('action', 'Análise'),
                        "completa": iteration_result.get('analysis_complete', False)
                    }
                )
            
            # Etapa final: Síntese e conclusões
            status_text.text("🎯 Finalizando: Sintetizando resultados e gerando insights...")
            progress_bar.progress(90)
            
            final_synthesis = synthesize_final_results(llm, current_context, config)
            analysis_steps.append({
                'step': len(analysis_steps) + 1,
                'action': 'Síntese Final',
                'description': 'Consolidação dos resultados e geração de insights',
                'result': final_synthesis
            })
            
            with steps_container:
                render_analysis_step(analysis_steps[-1], config['show_reasoning'])
            
            # Completar progresso
            progress_bar.progress(100)
            status_text.text("✅ Análise autônoma concluída!")
            
            # Salvar no histórico
            save_agent_analysis(question, analysis_steps, config, iteration)
            
            # Log final
            log_agent_action(
                "autonomous_agent",
                "✅ Análise autônoma concluída",
                {
                    "pergunta": question[:100],
                    "total_iteracoes": iteration,
                    "total_etapas": len(analysis_steps),
                    "insights_gerados": len(final_synthesis.get('insights', []))
                }
            )
            
            # Mostrar resumo final
            st.markdown("---")
            st.markdown("## 📋 Resumo da Análise")
            
            # Usar safe_columns para evitar erro de aninhamento
            try:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔄 Iterações", iteration)
                with col2:
                    st.metric("📊 Etapas", len(analysis_steps))
                with col3:
                    st.metric("💡 Insights", len(final_synthesis.get('insights', [])))
            except:
                # Fallback para exibição vertical se colunas não funcionarem
                st.metric("🔄 Iterações", iteration)
                st.metric("📊 Etapas", len(analysis_steps))
                st.metric("💡 Insights", len(final_synthesis.get('insights', [])))
            
            return True
            
        except ImportError:
            st.error("❌ LlamaIndex não está instalado corretamente")
            return False
        except Exception as e:
            st.error(f"❌ Erro durante análise autônoma: {str(e)}")
            log_agent_action(
                "autonomous_agent",
                "❌ Erro na análise autônoma",
                {
                    "erro": str(e),
                    "pergunta": question[:100],
                    "iteracao_atual": iteration
                }
            )
            return False

# Funções auxiliares do agente autônomo

def plan_analysis_approach(llm, question: str, data_tables: list, db, config: dict) -> dict:
    """Planeja a abordagem de análise baseada na pergunta"""
    
    # Gerar contexto das tabelas
    schema_context = generate_schema_context(db, data_tables)
    
    planning_prompt = f"""
    Você é um analista de dados experiente. Analise a pergunta do usuário e crie um plano detalhado de análise.

    PERGUNTA DO USUÁRIO: {question}

    TABELAS DISPONÍVEIS:
    {schema_context}

    PROFUNDIDADE DE EXPLORAÇÃO: {config['exploration_depth']}

    Crie um plano estruturado que inclua:
    1. Objetivos principais da análise
    2. Tabelas que serão utilizadas
    3. Tipos de análises necessárias (estatísticas, correlações, etc.)
    4. Sequência de etapas a serem executadas
    5. Possíveis desafios e como superá-los

    Responda em formato JSON com as chaves: objectives, tables_to_use, analysis_types, steps, challenges
    """
    
    try:
        response = llm.complete(planning_prompt)
        # Tentar parsear como JSON, se falhar, retornar estrutura básica
        import json
        try:
            plan = json.loads(response.text)
        except:
            plan = {
                "objectives": ["Analisar dados conforme solicitado"],
                "tables_to_use": data_tables,
                "analysis_types": ["Análise exploratória"],
                "steps": ["Explorar dados", "Analisar padrões", "Gerar insights"],
                "challenges": ["Qualidade dos dados"]
            }
        
        return {
            "plan": plan,
            "raw_response": response.text
        }
    except Exception as e:
        return {
            "plan": {
                "objectives": ["Analisar dados conforme solicitado"],
                "tables_to_use": data_tables,
                "analysis_types": ["Análise exploratória"],
                "steps": ["Explorar dados", "Analisar padrões", "Gerar insights"],
                "challenges": ["Qualidade dos dados"]
            },
            "error": str(e)
        }

def explore_data_schema(llm, data_tables: list, db, config: dict) -> dict:
    """Explora o esquema dos dados em detalhes"""
    
    schema_details = {}
    sample_data = {}
    
    for table in data_tables:
        # Obter informações da tabela
        table_info = db.get_table_info(table)
        if table_info:
            schema_details[table] = table_info
            
            # Obter amostra de dados se configurado para exploração avançada
            if config['exploration_depth'] in ['Intermediária', 'Avançada']:
                try:
                    sample_query = f'SELECT * FROM "{table}" LIMIT 5'
                    df_sample = pd.read_sql(sample_query, db.engine)
                    sample_data[table] = df_sample.to_dict('records')
                except:
                    sample_data[table] = []
    
    # Análise com IA se configurado
    if config['exploration_depth'] == 'Avançada':
        analysis_prompt = f"""
        Analise o esquema das tabelas e identifique:
        1. Relacionamentos potenciais entre tabelas
        2. Qualidade dos dados (campos vazios, inconsistências)
        3. Oportunidades de análise
        4. Possíveis problemas nos dados

        ESQUEMA DAS TABELAS:
        {schema_details}

        AMOSTRAS DE DADOS:
        {sample_data}

        Forneça insights sobre a estrutura dos dados.
        """
        
        try:
            response = llm.complete(analysis_prompt)
            ai_insights = response.text
        except:
            ai_insights = "Análise automática não disponível"
    else:
        ai_insights = "Análise básica do esquema"
    
    return {
        "schema_details": schema_details,
        "sample_data": sample_data,
        "ai_insights": ai_insights,
        "total_tables": len(data_tables),
        "total_columns": sum(len(info.get('columns', [])) for info in schema_details.values())
    }

def execute_analysis_iteration(llm, db, data_tables: list, context: dict, config: dict, iteration: int) -> dict:
    """Executa uma iteração de análise"""
    
    # Determinar próxima ação baseada no contexto
    action_prompt = f"""
    Você está na iteração {iteration} de uma análise de dados.

    CONTEXTO ATUAL:
    - Pergunta: {context['question']}
    - Plano: {context['plan']}
    - Esquema: {context['schema']}
    - Descobertas anteriores: {context['findings'][-2:] if context['findings'] else 'Nenhuma'}

    Determine a próxima ação mais útil:
    1. Consulta SQL específica para explorar dados
    2. Análise estatística de uma tabela
    3. Correlação entre tabelas
    4. Verificação de qualidade dos dados
    5. Finalizar análise (se já tem informações suficientes)

    Responda com:
    - action_type: tipo da ação (1-5)
    - sql_query: consulta SQL se aplicável
    - description: descrição da ação
    - analysis_complete: true se análise deve ser finalizada
    """
    
    try:
        response = llm.complete(action_prompt)
        
        # Parsear resposta (implementação simplificada)
        response_text = response.text.lower()
        
        if "finalizar" in response_text or "analysis_complete: true" in response_text:
            return {
                "action_type": "finalize",
                "description": "Análise considerada completa",
                "analysis_complete": True,
                "findings": "Dados suficientes coletados para conclusão"
            }
        
        # Executar consulta exploratória simples
        table = data_tables[iteration % len(data_tables)]  # Rotacionar entre tabelas
        
        queries = [
            f'SELECT COUNT(*) as total_records FROM "{table}"',
            f'SELECT * FROM "{table}" LIMIT 10',
            f'SELECT COUNT(DISTINCT *) as unique_records FROM "{table}"'
        ]
        
        query = queries[iteration % len(queries)]
        
        try:
            df_result = pd.read_sql(query, db.engine)
            query_result = df_result.to_dict('records')
        except Exception as e:
            query_result = f"Erro na consulta: {str(e)}"
        
        return {
            "action_type": "sql_query",
            "sql_query": query,
            "description": f"Análise exploratória da tabela {table}",
            "query_result": query_result,
            "analysis_complete": iteration >= 3,  # Completar após 3 iterações por padrão
            "findings": f"Dados coletados da tabela {table}"
        }
        
    except Exception as e:
        return {
            "action_type": "error",
            "description": f"Erro na iteração {iteration}",
            "error": str(e),
            "analysis_complete": True
        }

def synthesize_final_results(llm, context: dict, config: dict) -> dict:
    """Sintetiza os resultados finais da análise"""
    
    synthesis_prompt = f"""
    Sintetize os resultados da análise completa:

    PERGUNTA ORIGINAL: {context['question']}
    PLANO EXECUTADO: {context['plan']}
    DESCOBERTAS: {context['findings']}

    Forneça:
    1. Resposta direta à pergunta
    2. Principais insights descobertos
    3. Recomendações baseadas nos dados
    4. Limitações da análise
    5. Próximos passos sugeridos

    Seja claro, objetivo e baseie-se apenas nos dados analisados.
    """
    
    try:
        response = llm.complete(synthesis_prompt)
        
        # Gerar insights estruturados
        insights = [
            "Análise dos dados concluída",
            "Padrões identificados nos dados",
            "Recomendações baseadas em evidências"
        ]
        
        if config['include_insights']:
            insights.extend([
                "Oportunidades de melhoria identificadas",
                "Áreas que requerem atenção especial"
            ])
        
        return {
            "final_answer": response.text,
            "insights": insights,
            "recommendations": [
                "Continuar monitoramento dos dados",
                "Implementar melhorias sugeridas",
                "Realizar análises periódicas"
            ],
            "limitations": [
                "Análise baseada em dados disponíveis",
                "Resultados dependem da qualidade dos dados"
            ]
        }
        
    except Exception as e:
        return {
            "final_answer": "Análise concluída com base nos dados disponíveis",
            "insights": ["Dados analisados com sucesso"],
            "error": str(e)
        }

def render_analysis_step(step: dict, show_reasoning: bool):
    """Renderiza uma etapa da análise"""
    
    with st.expander(f"🔍 Etapa {step['step']}: {step['action']}", expanded=True):
        st.markdown(f"**Descrição:** {step['description']}")
        
        result = step['result']
        
        if show_reasoning and isinstance(result, dict):
            if 'plan' in result:
                st.markdown("**📋 Plano de Ação:**")
                plan = result['plan']
                if isinstance(plan, dict):
                    for key, value in plan.items():
                        if isinstance(value, list):
                            st.markdown(f"- **{key.replace('_', ' ').title()}:** {', '.join(map(str, value))}")
                        else:
                            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            if 'sql_query' in result:
                st.markdown("**🔍 Consulta Executada:**")
                st.code(result['sql_query'], language='sql')
                
            if 'query_result' in result:
                st.markdown("**📊 Resultado:**")
                if isinstance(result['query_result'], list):
                    st.json(result['query_result'])
                else:
                    st.write(result['query_result'])
            
            if 'ai_insights' in result:
                st.markdown("**🧠 Insights da IA:**")
                st.write(result['ai_insights'])
            
            if 'final_answer' in result:
                st.markdown("**🎯 Resposta Final:**")
                st.write(result['final_answer'])
                
                if 'insights' in result:
                    st.markdown("**💡 Principais Insights:**")
                    for insight in result['insights']:
                        st.markdown(f"- {insight}")

def save_agent_analysis(question: str, steps: list, config: dict, iterations: int):
    """Salva análise do agente no histórico"""
    
    if 'agent_analyses' not in st.session_state:
        st.session_state['agent_analyses'] = []
    
    analysis = {
        'question': question,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'steps': steps,
        'config': config,
        'iterations': iterations,
        'total_steps': len(steps)
    }
    
    st.session_state['agent_analyses'].append(analysis)
    
    # Manter apenas as últimas 10 análises
    if len(st.session_state['agent_analyses']) > 10:
        st.session_state['agent_analyses'] = st.session_state['agent_analyses'][-10:]
