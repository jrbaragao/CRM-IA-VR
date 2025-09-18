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

def get_system_tables():
    """Retorna lista de tabelas do sistema que devem ser excluídas das análises"""
    return ['importacoes', 'agent_logs', 'calculation_configs']

def filter_data_tables(all_tables):
    """Filtra apenas tabelas de dados, excluindo tabelas do sistema"""
    system_tables = get_system_tables()
    return [table for table in all_tables if table not in system_tables]

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
        system_tables = get_system_tables()
        data_tables = filter_data_tables(tables)
        
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
    system_tables = get_system_tables()
    data_tables = filter_data_tables(tables)
    
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
                # LIMPAR COMPLETAMENTE qualquer cache/estado anterior
                keys_to_clear = [
                    'agent_analyses', 'current_generated_sql', 'current_question',
                    'execute_current_sql', 'query_results', 'last_question',
                    'cached_question', 'previous_analysis', 'agent_context'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # Container para o processo do agente
                agent_container = st.empty()
                
                # Garantir que a pergunta atual é passada corretamente
                current_question = user_question.strip()
                
                # Debug: Mostrar a pergunta que será passada
                st.info(f"🔍 **Pergunta que será processada:** '{current_question}'")
                
                execute_autonomous_agent(db, data_tables, current_question, {
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
        
        # Limpar qualquer cache de análises anteriores
        if 'agent_analyses' in st.session_state:
            # Não limpar completamente, mas garantir que não interfira
            pass
            
        # Debug: Mostrar tabelas disponíveis para o agente
        st.markdown("### 📊 Tabelas Disponíveis para Análise:")
        if data_tables:
            for table in data_tables:
                table_info = db.get_table_info(table)
                if table_info:
                    st.markdown(f"• **{table}** ({table_info['total_rows']} registros)")
        else:
            st.warning("⚠️ Nenhuma tabela de dados disponível!")
        
        # Inicializar progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Container para etapas
        steps_container = st.container()
        
        try:
            # Configurar LLM (nova instância para evitar cache)
            from llama_index.llms.openai import OpenAI
            import uuid
            
            llm = OpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=0.3,
                # Forçar nova sessão
                request_timeout=60.0,
                max_retries=3
            )
            
            # Inicializar histórico de análise com ID único
            import uuid
            execution_id = str(uuid.uuid4())[:8]
            
            st.markdown(f"**🆔 ID da Execução:** `{execution_id}`")
            st.markdown(f"**❓ Pergunta Atual:** `{question}`")
            
            # Mostrar o prompt que será enviado para o agente
            with st.expander("🔍 Ver Prompt Enviado para o Agente", expanded=False):
                st.markdown("**Este é o prompt exato que será enviado para o LLM:**")
                
                # Gerar o mesmo prompt que será usado
                tables_list = ', '.join(data_tables) if data_tables else 'Nenhuma'
                
                planning_prompt_preview = f"""
Você é um agente autônomo especializado. Seu objetivo é:

{question}

Tabelas disponíveis: {tables_list}

Crie um plano estruturado em JSON com as chaves:
- objectives: [lista dos objetivos baseados no prompt do usuário]
- tables_to_use: [tabelas que serão utilizadas, se aplicável]
- analysis_types: [tipos de análises necessárias]
- steps: [sequência de etapas para atingir o objetivo]
- challenges: [possíveis desafios]
                """
                
                st.code(planning_prompt_preview, language="text")
            
            analysis_steps = []
            iteration = 0
            max_iterations = config['max_iterations']
            
            # Etapa 1: Análise inicial da pergunta
            status_text.text("🔍 Etapa 1: Analisando pergunta e planejando abordagem...")
            progress_bar.progress(10)
            
            planning_result = plan_analysis_approach(llm, question, data_tables, db, config, execution_id)
            analysis_steps.append({
                'step': 1,
                'action': 'Planejamento',
                'description': 'Análise da pergunta e criação do plano de ação',
                'result': planning_result
            })
            
            with steps_container:
                render_analysis_step(analysis_steps[-1], config['show_reasoning'])
                
                # Mostrar resposta bruta do LLM para debug
                with st.expander("🤖 Resposta Bruta do LLM - Etapa 1 (Debug)", expanded=False):
                    st.markdown("**Resposta original do modelo na etapa de planejamento:**")
                    if 'raw_response' in planning_result:
                        st.code(planning_result['raw_response'], language="text")
                    else:
                        st.code(str(planning_result), language="json")
            
            # Continuar com as etapas normais do agente autônomo
            
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
                'user_objective': question,  # Objetivo original do usuário
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
                
                # Se deve gerar Excel, executar agora - MAS apenas se ainda não foi gerado
                excel_already_generated = any(
                    step.get('result', {}).get('excel_generated', False) or 
                    step.get('action', '') == 'Exportação Excel'
                    for step in analysis_steps
                )
                
                if final_synthesis.get('generate_excel', False) and not excel_already_generated:
                    st.markdown("### 📊 Gerando Planilha Excel...")
                    excel_result = execute_excel_export_action(db, data_tables, current_context, len(analysis_steps))
                    
                    # Adicionar resultado do Excel como etapa adicional
                    analysis_steps.append({
                        'step': len(analysis_steps) + 1,
                        'action': 'Exportação Excel',
                        'description': 'Geração de planilha Excel com todos os dados',
                        'result': excel_result
                    })
                    
                    # Renderizar etapa do Excel
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

def plan_analysis_approach(llm, question: str, data_tables: list, db, config: dict, execution_id: str = None) -> dict:
    """Planeja abordagem usando o prompt do usuário como objetivo principal"""
    
    # Informações básicas das tabelas disponíveis
    tables_list = ', '.join(data_tables) if data_tables else 'Nenhuma'
    
    # Usar o prompt do usuário como objetivo, apenas adicionando contexto mínimo
    planning_prompt = f"""
Você é um agente autônomo especializado. Seu objetivo é:

{question}

Tabelas disponíveis: {tables_list}

Crie um plano estruturado em JSON com as chaves:
- objectives: [lista dos objetivos baseados no prompt do usuário]
- tables_to_use: [tabelas que serão utilizadas, se aplicável]
- analysis_types: [tipos de análises necessárias]
- steps: [sequência de etapas para atingir o objetivo]
- challenges: [possíveis desafios]
    """
    
    try:
        response = llm.complete(planning_prompt)
        
        # Tentar parsear como JSON
        import json
        try:
            plan = json.loads(response.text)
        except:
            # Se falhar, criar estrutura básica baseada no prompt do usuário
            plan = {
                "objectives": [question],
                "tables_to_use": data_tables if data_tables else [],
                "analysis_types": ["Execução do objetivo especificado"],
                "steps": ["Analisar objetivo", "Executar ações necessárias", "Fornecer resultado"],
                "challenges": ["Interpretação correta do objetivo"]
            }
        
        return {
            "plan": plan,
            "raw_response": response.text,
            "user_objective": question
        }
    except Exception as e:
        return {
            "plan": {
                "objectives": [question],
                "tables_to_use": data_tables if data_tables else [],
                "analysis_types": ["Execução do objetivo especificado"],
                "steps": ["Analisar objetivo", "Executar ações necessárias", "Fornecer resultado"],
                "challenges": ["Interpretação correta do objetivo"]
            },
            "error": str(e),
            "user_objective": question
        }

def explore_data_schema(llm, data_tables: list, db, config: dict) -> dict:
    """Explora o esquema dos dados de forma compacta"""
    
    schema_details = {}
    
    # Obter apenas informações essenciais das tabelas (limitado para evitar tokens)
    for table in data_tables[:5]:  # Máximo 5 tabelas para análise de esquema
        table_info = db.get_table_info(table)
        if table_info:
            # Manter apenas informações essenciais
            schema_details[table] = {
                'total_rows': table_info['total_rows'],
                'columns': [col['name'] for col in table_info['columns'][:5]]  # Apenas nomes das primeiras 5 colunas
            }
    
    # Análise simplificada com IA apenas se necessário
    if config['exploration_depth'] == 'Avançada' and len(data_tables) <= 3:
        # Prompt compacto para análise
        analysis_prompt = f"""
Analise rapidamente:
Tabelas: {list(schema_details.keys())}
Identifique relacionamentos básicos.
Resposta em 2-3 frases.
        """
        
        try:
            response = llm.complete(analysis_prompt)
            ai_insights = response.text[:300]  # Limitar resposta
        except:
            ai_insights = "Análise automática não disponível"
    else:
        ai_insights = f"Análise básica de {len(data_tables)} tabelas com relacionamentos por MATRICULA"
    
    return {
        "schema_details": schema_details,
        "ai_insights": ai_insights,
        "total_tables": len(data_tables),
        "total_columns": sum(len(info.get('columns', [])) for info in schema_details.values())
    }

def execute_analysis_iteration(llm, db, data_tables: list, context: dict, config: dict, iteration: int) -> dict:
    """Executa uma iteração de análise usando IA para determinar próxima ação"""
    
    # Obter contexto completo
    plan = context.get('plan', {}).get('plan', {})
    user_question = context.get('user_objective', context.get('question', ''))
    previous_findings = context.get('findings', [])
    schema_info = context.get('schema', {})
    
    # Extrair passos do plano se disponível (DEFINIR PRIMEIRO)
    planned_steps = []
    if isinstance(plan, dict) and 'steps' in plan:
        planned_steps = plan['steps']
    
    # Definir total_steps ANTES de usar
    total_steps = len(planned_steps) if planned_steps else 0
    
    # Debug: Log da iteração
    if 'agent_logs' not in st.session_state:
        st.session_state['agent_logs'] = []
    
    st.session_state['agent_logs'].append({
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'agent': 'analysis_iteration',
        'action': f'🔄 Iteração {iteration}/{total_steps} - IA determinando ação',
        'details': {
            'question': user_question[:50],
            'iteration': iteration,
            'total_steps': total_steps,
            'current_step': 'Calculando...',  # Será atualizado depois
            'previous_steps': len(previous_findings),
            'has_more_steps': iteration < total_steps
        }
    })
    
    # Preparar contexto das tabelas disponíveis (compacto para evitar excesso de tokens)
    tables_context = ""
    for table in data_tables[:8]:  # Máximo 8 tabelas no contexto
        table_info = db.get_table_info(table)
        if table_info:
            columns = [col['name'] for col in table_info['columns'][:4]]  # 4 primeiras colunas
            tables_context += f"- {table}: {table_info['total_rows']} registros\n"
    
    # Resumir descobertas anteriores (limitado para evitar excesso de tokens)
    previous_summary = ""
    if previous_findings:
        for i, finding in enumerate(previous_findings[-1:], 1):  # Apenas última descoberta
            if isinstance(finding, dict):
                action = finding.get('action_type', 'ação')
                findings_text = finding.get('findings', 'sem detalhes')[:100]  # Limitar a 100 chars
                previous_summary += f"{i}. {action}: {findings_text}...\n"
    
    # Determinar qual passo do plano executar
    current_step_info = ""
    
    if planned_steps and iteration <= len(planned_steps):
        step_index = iteration - 1
        if step_index < len(planned_steps):
            current_step = planned_steps[step_index]
            if isinstance(current_step, dict):
                current_step_info = f"PASSO {iteration}/{total_steps}: {current_step.get('description', '')}"
            else:
                current_step_info = f"PASSO {iteration}/{total_steps}: {current_step}"
    
    # Prompt ultra-compacto para evitar excesso de tokens
    # Extrair apenas informações essenciais
    objective_short = user_question[:80] if user_question else "análise"
    step_short = current_step_info.replace("PASSO ATUAL DO PLANO: ", "")[:150] if current_step_info else f"passo {iteration}"
    tables_short = ', '.join(data_tables[:6])
    
    # Verificar se ainda há passos a executar
    has_more_steps = iteration < total_steps
    
    action_prompt = f"""
OBJETIVO: {objective_short}

{current_step_info}

TABELAS: {tables_short}

IMPORTANTE: 
- Você DEVE executar TODOS os {total_steps} passos do plano.
- Escolha apenas a TABELA mais relevante para este passo
- NÃO gere SQL - isso será feito automaticamente

Iteração atual: {iteration}/{total_steps}
{"CONTINUE executando o passo atual. NÃO marque como completo ainda." if has_more_steps else "Este é o ÚLTIMO passo. Pode marcar como completo."}

Responda APENAS JSON:
{{
"action_type": "sql_query",
"target_table": "nome_da_tabela_relevante",
"description": "executando passo {iteration}: [descrição do que está fazendo]",
"analysis_complete": {str(not has_more_steps).lower()}
}}
"""
    
    try:
        # Usar IA para determinar próxima ação
        response = llm.complete(action_prompt)
        
        # Tentar parsear resposta JSON
        import json
        import re
        
        # Log da resposta bruta para debug
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'json_parser',
            'action': f'📝 Resposta LLM Iteração {iteration}',
            'details': {'raw_response': response.text[:200]}
        })
        
        try:
            # Tentar parse direto
            action_plan = json.loads(response.text)
        except:
            try:
                # Tentar extrair JSON de dentro do texto
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    action_plan = json.loads(json_text)
                else:
                    raise ValueError("Nenhum JSON encontrado")
            except:
                # Se ainda falhar, criar plano baseado no passo atual do plano original
                response_text = response.text.lower()
                
                # Verificar se menciona análise completa
                if "analysis_complete" in response_text and "true" in response_text:
                    return {
                        "action_type": "analysis_complete",
                        "description": "Análise considerada completa pela IA",
                        "analysis_complete": True,
                        "findings": "IA determinou que objetivo foi atingido",
                        "ai_reasoning": response.text,
                        "parse_error": "JSON inválido, mas detectou conclusão"
                    }
                
                # Tentar seguir o plano mesmo com erro de JSON
                if planned_steps and iteration <= len(planned_steps):
                    step_index = iteration - 1
                    if step_index < len(planned_steps):
                        current_step = planned_steps[step_index]
                        step_desc = ""
                        if isinstance(current_step, dict):
                            step_desc = current_step.get('description', '')
                        else:
                            step_desc = str(current_step)
                        
                        # Tentar identificar tabela e ação baseado no passo do plano
                        target_table = None
                        sql_query = None
                        
                        # Analisar descrição do passo para extrair tabela e ação
                        step_lower = step_desc.lower()
                        
                        # Identificar tabela mencionada no passo (melhorada)
                        # Primeiro, tentar encontrar tabela mencionada explicitamente
                        for table in data_tables:
                            if table.lower() in step_lower:
                                target_table = table
                                break
                        
                        # Se não encontrou, usar lógica inteligente baseada no passo
                        if not target_table:
                            if iteration == 1 or "ativo" in step_lower or "colaborador" in step_lower:
                                # Passo 1: Priorizar tabela de ativos
                                for table in data_tables:
                                    if "ativo" in table.lower():
                                        target_table = table
                                        break
                            elif iteration == 2 or "consultar" in step_lower:
                                # Passo 2: Continuar com ativos ou primeira tabela disponível
                                for table in data_tables:
                                    if "ativo" in table.lower():
                                        target_table = table
                                        break
                            elif iteration >= 3 and iteration <= 4 and ("excluir" in step_lower or "férias" in step_lower or "afastamento" in step_lower):
                                # Passos 3-4: Priorizar tabelas de exclusão
                                exclusion_tables = ["ferias", "afastamentos", "aprendiz", "estagio", "exterior", "desligados"]
                                for table in data_tables:
                                    if any(excl in table.lower() for excl in exclusion_tables):
                                        target_table = table
                                        break
                            elif iteration >= 5 and ("sindicato" in step_lower or "valor" in step_lower):
                                # Passo 5+: Priorizar tabela de valores
                                for table in data_tables:
                                    if "sindicato" in table.lower() or "valor" in table.lower():
                                        target_table = table
                                        break
                        
                        # Fallback final: usar primeira tabela disponível
                        if not target_table and data_tables:
                            target_table = data_tables[0]
                        
                        # Gerar consulta SQL SEGURA baseada no passo
                        if target_table:
                            # Obter informações da tabela para consultas seguras
                            table_info = db.get_table_info(target_table)
                            available_columns = []
                            if table_info and 'columns' in table_info:
                                available_columns = [col['name'] for col in table_info['columns']]
                            
                            # Consultas SEGURAS que não dependem de colunas específicas
                            if iteration == 1:
                                # Passo 1: Sempre começar explorando a tabela
                                if available_columns and any(col.upper() in ['MATRICULA', 'NOME'] for col in available_columns):
                                    # Se tem MATRICULA e NOME, usar essas colunas
                                    matricula_col = next((col for col in available_columns if col.upper() == 'MATRICULA'), None)
                                    nome_col = next((col for col in available_columns if col.upper() == 'NOME'), None)
                                    if matricula_col and nome_col:
                                        sql_query = f'SELECT "{matricula_col}", "{nome_col}" FROM "{target_table}" LIMIT 100'
                                    else:
                                        sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                                else:
                                    sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                            elif iteration == 2:
                                # Passo 2: Explorar estrutura da tabela
                                sql_query = f'SELECT * FROM "{target_table}" LIMIT 100'
                            elif iteration == 3:
                                # Passo 3: Identificar registros (sem filtros específicos)
                                if available_columns and any(col.upper() == 'MATRICULA' for col in available_columns):
                                    matricula_col = next((col for col in available_columns if col.upper() == 'MATRICULA'), None)
                                    sql_query = f'SELECT "{matricula_col}" FROM "{target_table}" LIMIT 50'
                                else:
                                    sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                            elif iteration == 4:
                                # Passo 4: Contar registros (sempre seguro)
                                sql_query = f'SELECT COUNT(*) as total_registros FROM "{target_table}"'
                            elif iteration == 5:
                                # Passo 5: Explorar dados para valores
                                sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                            elif iteration == 6:
                                # Passo 6: Análise de dados
                                sql_query = f'SELECT * FROM "{target_table}" LIMIT 100'
                            elif iteration == 7:
                                # Passo 7: Preparar relatório
                                sql_query = f'SELECT * FROM "{target_table}" LIMIT 200'
                            elif iteration >= 8:
                                # Passo 8+: Contagem final
                                sql_query = f'SELECT COUNT(*) as total_para_exportacao FROM "{target_table}"'
                            else:
                                # Fallback sempre seguro - sem WHERE com colunas específicas
                                sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                        
                        if not target_table and data_tables:
                            target_table = data_tables[0]
                            sql_query = f'SELECT * FROM "{target_table}" LIMIT 10'
                        
                        # Log detalhado para debug
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'fallback_sql_generator',
                            'action': f'🔧 Fallback - Gerando SQL para passo {iteration}',
                            'details': {
                                'step_desc': step_desc[:100],
                                'target_table': target_table,
                                'sql_query': sql_query[:100] if sql_query else 'None',
                                'iteration': iteration,
                                'total_steps': total_steps
                            }
                        })
                        
                        action_plan = {
                            "action_type": "sql_query",
                            "target_table": target_table,
                            "sql_query": sql_query,
                            "description": f"Executando passo {iteration}/{total_steps}: {step_desc}",
                            "reasoning": f"Seguindo plano original - Passo {iteration}: {step_desc}",
                            "analysis_complete": iteration >= total_steps,  # Só completa quando executar TODOS os passos
                            "parse_error": "JSON inválido, usando plano original"
                        }
                    else:
                        # Sem mais passos no plano
                        action_plan = {
                            "action_type": "analysis_complete",
                            "description": "Todos os passos do plano foram executados",
                            "analysis_complete": True,
                            "reasoning": "Plano original completado",
                            "parse_error": "JSON inválido, mas plano concluído"
                        }
                else:
                    # Fallback final - ação genérica
                    target_table = data_tables[0] if data_tables else None
                    action_plan = {
                        "action_type": "sql_query",
                        "target_table": target_table,
                        "sql_query": f'SELECT * FROM "{target_table}" LIMIT 10' if target_table else None,
                        "description": f"Exploração da tabela {target_table}",
                        "reasoning": "Fallback devido a erro no parse JSON",
                        "analysis_complete": iteration >= 3,
                        "parse_error": "JSON inválido, usando fallback"
                    }
        
        # Executar ação determinada pela IA
        action_type = action_plan.get("action_type", "sql_query")
        
        if action_type == "analysis_complete":
            return {
                "action_type": "analysis_complete",
                "description": action_plan.get("description", "Análise completa"),
                "analysis_complete": True,
                "findings": action_plan.get("reasoning", "Objetivo atingido"),
                "ai_reasoning": action_plan.get("reasoning", "")
            }
        
        elif action_type == "excel_export" and "excel_export" in config.get('available_tools', []):
            return execute_excel_export_action(db, data_tables, context, iteration)
        
        # NOVA TOOL: Cálculo de Vale Refeição
        elif action_type == "calculo_vale_refeicao" and "calculo_vale_refeicao" in config.get('available_tools', []):
            result = calculo_vale_refeicao_tool(db, data_tables)
            
            # Se o cálculo foi bem-sucedido e tem Excel disponível, gerar automaticamente
            if result.get('success', False) and result.get('auto_export_excel', False) and "excel_export" in config.get('available_tools', []):
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'auto_excel_trigger',
                    'action': '📊 Cálculo concluído - Gerando planilha Excel automaticamente',
                    'details': {
                        'elegiveis': result.get('total_records', 0),
                        'valor_total': result.get('findings', '')
                    }
                })
                
                # Adicionar resultado do cálculo ao contexto para a exportação usar
                context['findings'].append(result)
                
                # Gerar Excel automaticamente
                excel_result = execute_excel_export_action(db, data_tables, context, iteration)
                
                # Combinar resultados
                result['excel_generated'] = True
                result['excel_filename'] = excel_result.get('filename', '')
                result['description'] += f" + Planilha Excel gerada: {excel_result.get('filename', 'arquivo.xlsx')}"
            
            return result
        
        # Se a IA menciona cálculo de vale refeição
        elif ("vale refeição" in action_plan.get("description", "").lower() or 
              "calculo" in action_plan.get("description", "").lower() or
              "calcular" in action_plan.get("description", "").lower()):
            if "calculo_vale_refeicao" in config.get('available_tools', []):
                result = calculo_vale_refeicao_tool(db, data_tables)
                
                # Auto-gerar Excel se bem-sucedido
                if result.get('success', False) and result.get('auto_export_excel', False) and "excel_export" in config.get('available_tools', []):
                    context['findings'].append(result)
                    excel_result = execute_excel_export_action(db, data_tables, context, iteration)
                    result['excel_generated'] = True
                    result['excel_filename'] = excel_result.get('filename', '')
                    result['description'] += f" + Planilha Excel gerada: {excel_result.get('filename', 'arquivo.xlsx')}"
                
                return result
        
        # Se a IA menciona exportação mas não especificou o tipo correto
        elif ("excel" in action_plan.get("description", "").lower() or 
              "planilha" in action_plan.get("description", "").lower() or
              "export" in action_plan.get("description", "").lower()):
            return execute_excel_export_action(db, data_tables, context, iteration)
        
        # Se é o último passo e tem ferramenta de Excel, forçar exportação APENAS se todos os passos foram executados
        elif iteration >= total_steps and "excel_export" in config.get('available_tools', []):
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'excel_auto_trigger',
                'action': f'📊 Último passo ({iteration}/{total_steps}) - Forçando geração de planilha final',
                'details': {
                    'iteration': iteration, 
                    'total_steps': total_steps,
                    'all_steps_completed': True
                }
            })
            # Marcar como completo na exportação final
            result = execute_excel_export_action(db, data_tables, context, iteration)
            result["analysis_complete"] = True  # AGORA sim, marcar como completo
            result["final_step"] = True
            return result
        
        elif action_type == "sql_query":
            target_table = action_plan.get("target_table")
            sql_query = action_plan.get("sql_query")
            
            # USAR O SISTEMA TEXT-TO-QUERY EXISTENTE para gerar SQL seguro
            if not target_table and data_tables:
                target_table = data_tables[0]
            
            if target_table:
                # Gerar contexto do esquema para a tabela específica
                schema_context = generate_schema_context(db, [target_table])
                
                # Criar pergunta ESPECÍFICA baseada no passo atual e contexto do vale refeição
                step_description = action_plan.get('description', f'análise passo {iteration}')
                
                # Gerar pergunta mais específica baseada no número do passo e contexto
                if iteration == 1 and "ativo" in target_table.lower():
                    step_question = f"Listar todos os colaboradores ativos da tabela {target_table} com MATRICULA e NOME para identificar quem tem direito ao vale refeição"
                elif iteration == 2 and ("ferias" in target_table.lower() or "afastamento" in target_table.lower()):
                    step_question = f"Identificar MATRICULAS de colaboradores em férias ou afastados na tabela {target_table} que NÃO devem receber vale refeição"
                elif iteration == 3 and ("aprendiz" in target_table.lower() or "estagio" in target_table.lower()):
                    step_question = f"Listar MATRICULAS de aprendizes e estagiários na tabela {target_table} que são excluídos do vale refeição"
                elif iteration == 4 and ("exterior" in target_table.lower() or "desligado" in target_table.lower()):
                    step_question = f"Identificar MATRICULAS de colaboradores no exterior ou desligados na tabela {target_table} para exclusão do vale refeição"
                elif iteration >= 5 and ("sindicato" in target_table.lower() or "valor" in target_table.lower()):
                    step_question = f"Consultar valores de vale refeição por sindicato na tabela {target_table} para calcular o benefício de 22 dias úteis por colaborador"
                elif iteration >= 7:
                    step_question = f"Calcular o valor total de vale refeição multiplicando valor diário por 22 dias para cada colaborador elegível usando dados da tabela {target_table}"
                else:
                    # Fallback com contexto de vale refeição
                    step_question = f"Analisar dados da tabela {target_table} para {step_description} no contexto de cálculo de vale refeição considerando 22 dias úteis"
                
                # Usar a função text-to-query existente que já valida colunas
                try:
                    generated_sql = generate_sql_from_prompt(step_question, schema_context)
                    if generated_sql and generated_sql.strip():
                        sql_query = generated_sql
                        
                        # Log do uso do text-to-query
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'text_to_query_integration',
                            'action': f'🔄 Usando Text-to-Query para passo {iteration}',
                            'details': {
                                'target_table': target_table,
                                'question': step_question[:100],
                                'generated_sql': sql_query[:100],
                                'iteration': iteration
                            }
                        })
                    else:
                        # Fallback se text-to-query falhar
                        sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                except Exception as e:
                    # Fallback seguro se text-to-query falhar
                    sql_query = f'SELECT * FROM "{target_table}" LIMIT 50'
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'text_to_query_fallback',
                        'action': f'⚠️ Text-to-Query falhou, usando fallback',
                        'details': {
                            'error': str(e),
                            'fallback_sql': sql_query,
                            'iteration': iteration
                        }
                    })
            else:
                return {
                    "action_type": "error",
                    "description": "Nenhuma tabela disponível para consulta",
                    "error": "Sem tabelas de dados disponíveis",
                    "analysis_complete": True,
                    "findings": "Erro: Nenhuma tabela de dados encontrada"
                }
            
            # Executar consulta SQL
            try:
                df_result = pd.read_sql(sql_query, db.engine)
                query_result = df_result.to_dict('records')
                
                # Determinar se análise está completa baseado na resposta da IA
                # MAS forçar a continuar se ainda há passos no plano
                # IMPORTANTE: Só marcar como completo se executou TODOS os passos do plano
                ai_says_complete = action_plan.get("analysis_complete", False)
                all_steps_executed = iteration >= total_steps
                analysis_complete = ai_says_complete and all_steps_executed
                
                # Log para debug da decisão de completude
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'completion_logic',
                    'action': f'🎯 Verificando completude - Passo {iteration}/{total_steps}',
                    'details': {
                        'ai_says_complete': ai_says_complete,
                        'all_steps_executed': all_steps_executed,
                        'final_decision': analysis_complete,
                        'iteration': iteration,
                        'total_steps': total_steps
                    }
                })
                
                return {
                    "action_type": "ai_guided_query",
                    "sql_query": sql_query,
                    "description": action_plan.get("description", f"Consulta na tabela {target_table}"),
                    "query_result": query_result,
                    "target_table": target_table,
                    "analysis_complete": analysis_complete,
                    "findings": action_plan.get("reasoning", f"Dados coletados da tabela {target_table}"),
                    "ai_reasoning": action_plan.get("reasoning", ""),
                    "result_count": len(df_result) if not df_result.empty else 0
                }
                
            except Exception as e:
                return {
                    "action_type": "query_error",
                    "description": f"Erro ao executar consulta determinada pela IA",
                    "error": str(e),
                    "sql_query": sql_query,
                    "target_table": target_table,
                    "analysis_complete": True,
                    "findings": f"Erro na consulta: {str(e)}"
                }
        
        else:
            return {
                "action_type": "unknown_action",
                "description": f"Tipo de ação não reconhecido: {action_type}",
                "analysis_complete": True,
                "findings": "IA sugeriu ação não implementada"
            }
            
    except Exception as e:
        return {
            "action_type": "iteration_error",
            "description": f"Erro na iteração {iteration}",
            "error": str(e),
            "analysis_complete": True,
            "findings": f"Erro geral na iteração: {str(e)}"
        }

def calculo_vale_refeicao_tool(db, data_tables: list) -> dict:
    """
    Tool especializada para cálculo de vale refeição
    Implementa a lógica de negócio específica do RH brasileiro
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        # Log do início do cálculo
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': '🧮 Iniciando cálculo de vale refeição',
            'details': {
                'tabelas_disponiveis': data_tables,
                'dias_uteis': 22
            }
        })
        
        # 1. BUSCAR COLABORADORES ATIVOS
        if 'ativos' not in data_tables:
            return {
                "action_type": "calculation_error",
                "description": "Tabela 'ativos' não encontrada",
                "error": "Tabela obrigatória 'ativos' não está disponível",
                "success": False
            }
        
        ativos_df = pd.read_sql('SELECT * FROM "ativos"', db.engine)
        total_ativos = len(ativos_df)
        
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': f'📊 Carregados {total_ativos} colaboradores ativos',
            'details': {'total_ativos': total_ativos}
        })
        
        # 1.1. BUSCAR COLABORADORES DE ADMISSÃO ABRIL (SE EXISTIR)
        admissao_abril_df = pd.DataFrame()
        total_admissao_abril = 0
        
        if 'admissao_abril' in data_tables:
            admissao_abril_df = pd.read_sql('SELECT * FROM "admissao_abril"', db.engine)
            
            # Filtrar apenas colaboradores que NÃO estão na tabela ativos
            if not admissao_abril_df.empty and 'MATRICULA' in admissao_abril_df.columns:
                matriculas_ativos = set(ativos_df['MATRICULA'].astype(str))
                admissao_abril_df['MATRICULA'] = admissao_abril_df['MATRICULA'].astype(str)
                
                # Filtrar apenas os que não estão em ativos
                mask_novos = ~admissao_abril_df['MATRICULA'].isin(matriculas_ativos)
                admissao_abril_df = admissao_abril_df[mask_novos]
                total_admissao_abril = len(admissao_abril_df)
                
                if total_admissao_abril > 0:
                    # Unir com colaboradores ativos
                    ativos_df = pd.concat([ativos_df, admissao_abril_df], ignore_index=True)
                    
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'calculo_vale_refeicao',
                        'action': f'➕ Adicionados {total_admissao_abril} colaboradores de admissão abril',
                        'details': {
                            'total_admissao_abril': total_admissao_abril,
                            'total_combinado': len(ativos_df)
                        }
                    })
        
        # Atualizar total após possível inclusão de admissão abril
        total_final = len(ativos_df)
        
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': f'📋 Total final para processamento: {total_final} colaboradores',
            'details': {
                'ativos_originais': total_ativos,
                'admissao_abril_novos': total_admissao_abril,
                'total_final': total_final
            }
        })
        
        # 2. BUSCAR TABELAS DE EXCLUSÃO
        exclusoes = {}
        tabelas_exclusao = ['ferias', 'afastamentos', 'aprendiz', 'exterior', 'desligados']
        
        for tabela in tabelas_exclusao:
            if tabela in data_tables:
                try:
                    df_exclusao = pd.read_sql(f'SELECT MATRICULA FROM "{tabela}"', db.engine)
                    exclusoes[tabela] = set(df_exclusao['MATRICULA'].astype(str))
                    
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'calculo_vale_refeicao',
                        'action': f'🚫 Exclusões {tabela}: {len(exclusoes[tabela])} registros',
                        'details': {'tabela': tabela, 'total_exclusoes': len(exclusoes[tabela])}
                    })
                except Exception as e:
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'calculo_vale_refeicao',
                        'action': f'⚠️ Erro ao carregar {tabela}: {str(e)}',
                        'details': {'tabela': tabela, 'erro': str(e)}
                    })
        
        # 3. DEFINIR VALORES POR ESTADO (baseado no sindicato)
        valor_sp = 37.50  # São Paulo - sindicatos com "SP" no nome
        valor_outros = 35.00  # Outros estados
        valores_sindicato = {}  # Inicializar dicionário de valores por sindicato
        
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': '💰 Regra de valores por estado definida',
            'details': {
                'regra': 'Sindicatos com "SP" no nome = R$ 37,50 | Outros = R$ 35,00',
                'valor_sp': f'R$ {valor_sp}',
                'valor_outros': f'R$ {valor_outros}',
                'exemplo_sp': 'SINDPD SP - SIND.TRAB.EM PROC DADOS...'
            }
        })
        
        if 'base_sindicato_x_valor' in data_tables:
            try:
                sindicato_df = pd.read_sql('SELECT * FROM "base_sindicato_x_valor"', db.engine)
                
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'calculo_vale_refeicao',
                    'action': f'🔍 Estrutura da tabela sindicato: {list(sindicato_df.columns)}',
                    'details': {'colunas': list(sindicato_df.columns), 'registros': len(sindicato_df)}
                })
                
                # Tentar diferentes combinações de nomes de colunas
                sindicato_col = None
                valor_col = None
                
                # Buscar coluna de sindicato
                for col in sindicato_df.columns:
                    col_lower = col.lower()
                    if any(term in col_lower for term in ['sindicato', 'sindic', 'categoria', 'tipo']):
                        sindicato_col = col
                        break
                
                # Buscar coluna de valor
                for col in sindicato_df.columns:
                    col_lower = col.lower()
                    if any(term in col_lower for term in ['valor', 'preco', 'price', 'amount', 'vr']):
                        valor_col = col
                        break
                
                if sindicato_col and valor_col:
                    for _, row in sindicato_df.iterrows():
                        sindicato_key = str(row[sindicato_col]).strip()
                        valor = float(row[valor_col]) if pd.notna(row[valor_col]) else valor_padrao
                        valores_sindicato[sindicato_key] = valor
                    
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'calculo_vale_refeicao',
                        'action': f'💰 Valores carregados: {len(valores_sindicato)} sindicatos',
                        'details': {
                            'sindicato_col': sindicato_col,
                            'valor_col': valor_col,
                            'valores_encontrados': len(valores_sindicato),
                            'exemplo_valores': dict(list(valores_sindicato.items())[:3])
                        }
                    })
                else:
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'calculo_vale_refeicao',
                        'action': f'⚠️ Colunas não identificadas - usando valor padrão R$ {valor_padrao}',
                        'details': {
                            'colunas_disponiveis': list(sindicato_df.columns),
                            'sindicato_col_encontrada': sindicato_col,
                            'valor_col_encontrada': valor_col
                        }
                    })
                    
            except Exception as e:
                st.session_state['agent_logs'].append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': 'calculo_vale_refeicao',
                    'action': f'⚠️ Erro ao carregar valores de sindicato: {str(e)}',
                    'details': {'erro': str(e)}
                })
        else:
            st.session_state['agent_logs'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'agent': 'calculo_vale_refeicao',
                'action': f'⚠️ Tabela base_sindicato_x_valor não encontrada - usando valor padrão R$ {valor_padrao}',
                'details': {'valor_padrao': valor_padrao}
            })
        
        # 4. LOOP PELOS COLABORADORES ATIVOS - LÓGICA PRINCIPAL
        resultados = []
        total_processados = 0
        total_elegiveis = 0
        total_excluidos = 0
        valor_total_geral = 0
        
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': '🔄 Iniciando loop de cálculo por colaborador',
            'details': {'total_para_processar': total_final}
        })
        
        for index, colaborador in ativos_df.iterrows():
            total_processados += 1
            
            # Obter dados do colaborador
            matricula = str(colaborador.get('MATRICULA', ''))
            nome = str(colaborador.get('NOME', 'Nome não informado'))
            sindicato = str(colaborador.get('SINDICATO', ''))
            
            # VERIFICAR EXCLUSÕES
            motivo_exclusao = None
            
            # Verificar cada tipo de exclusão
            for tipo_exclusao, matriculas_excluidas in exclusoes.items():
                if matricula in matriculas_excluidas:
                    motivo_exclusao = tipo_exclusao
                    break
            
            if motivo_exclusao:
                # COLABORADOR EXCLUÍDO
                total_excluidos += 1
                
                # Determinar estado mesmo para excluídos (para informação)
                sindicato_upper = sindicato.upper().strip()
                if ' SP ' in sindicato_upper or sindicato_upper.startswith('SP ') or sindicato_upper.endswith(' SP') or 'ESTADO DE SP' in sindicato_upper:
                    estado_info = 'SP'
                else:
                    estado_info = 'OUTROS'
                
                resultados.append({
                    'MATRICULA': matricula,
                    'NOME': nome,
                    'SINDICATO': sindicato,
                    'ESTADO': estado_info,
                    'STATUS': 'EXCLUÍDO',
                    'MOTIVO_EXCLUSAO': motivo_exclusao.upper(),
                    'DIAS_ELEGIVEL': 0,
                    'VALOR_DIARIO': 0.0,
                    'VALOR_TOTAL_VR': 0.0
                })
            else:
                # COLABORADOR ELEGÍVEL
                total_elegiveis += 1
                
                # Determinar valor baseado no sindicato (verificar se contém "SP")
                sindicato_upper = sindicato.upper().strip()
                
                if ' SP ' in sindicato_upper or sindicato_upper.startswith('SP ') or sindicato_upper.endswith(' SP') or 'ESTADO DE SP' in sindicato_upper:
                    valor_diario = valor_sp  # R$ 37,50 para São Paulo
                    estado_info = 'SP'
                else:
                    valor_diario = valor_outros  # R$ 35,00 para outros estados
                    estado_info = 'OUTROS'
                
                # Tentar buscar valor específico do sindicato se disponível na tabela (sobrescreve o padrão)
                if sindicato in valores_sindicato and valores_sindicato[sindicato] > 0:
                    valor_diario = valores_sindicato[sindicato]
                    estado_info += f' (Tabela: R$ {valor_diario})'
                
                # Calcular valor total (22 dias úteis)
                dias_elegiveis = 22
                valor_total_vr = valor_diario * dias_elegiveis
                valor_total_geral += valor_total_vr
                
                resultados.append({
                    'MATRICULA': matricula,
                    'NOME': nome,
                    'SINDICATO': sindicato,
                    'ESTADO': estado_info,
                    'STATUS': 'ELEGÍVEL',
                    'MOTIVO_EXCLUSAO': '',
                    'DIAS_ELEGIVEL': dias_elegiveis,
                    'VALOR_DIARIO': valor_diario,
                    'VALOR_TOTAL_VR': valor_total_vr
                })
        
        # 5. GERAR DATAFRAME FINAL
        resultado_df = pd.DataFrame(resultados)
        
        # 6. ESTATÍSTICAS FINAIS (incluindo por estado)
        # Contar por estado
        elegiveis_sp = len([r for r in resultados if r['STATUS'] == 'ELEGÍVEL' and r['ESTADO'] == 'SP'])
        elegiveis_outros = len([r for r in resultados if r['STATUS'] == 'ELEGÍVEL' and r['ESTADO'] == 'OUTROS'])
        valor_total_sp = sum([r['VALOR_TOTAL_VR'] for r in resultados if r['STATUS'] == 'ELEGÍVEL' and r['ESTADO'] == 'SP'])
        valor_total_outros = sum([r['VALOR_TOTAL_VR'] for r in resultados if r['STATUS'] == 'ELEGÍVEL' and r['ESTADO'] == 'OUTROS'])
        
        estatisticas = {
            'total_colaboradores': total_ativos,
            'total_elegiveis': total_elegiveis,
            'total_excluidos': total_excluidos,
            'elegiveis_sp': elegiveis_sp,
            'elegiveis_outros': elegiveis_outros,
            'valor_total_geral': valor_total_geral,
            'valor_total_sp': valor_total_sp,
            'valor_total_outros': valor_total_outros,
            'valor_medio_por_elegivel': valor_total_geral / total_elegiveis if total_elegiveis > 0 else 0,
            'percentual_elegiveis': (total_elegiveis / total_ativos * 100) if total_ativos > 0 else 0,
            'percentual_sp': (elegiveis_sp / total_elegiveis * 100) if total_elegiveis > 0 else 0
        }
        
        # Log final
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': '✅ Cálculo de vale refeição concluído',
            'details': {
                'total_processados': total_processados,
                'elegiveis_total': total_elegiveis,
                'elegiveis_sp': f'{elegiveis_sp} (R$ 37,50/dia)',
                'elegiveis_outros': f'{elegiveis_outros} (R$ 35,00/dia)',
                'excluidos': total_excluidos,
                'valor_total_geral': f'R$ {valor_total_geral:,.2f}',
                'valor_sp': f'R$ {valor_total_sp:,.2f}',
                'valor_outros': f'R$ {valor_total_outros:,.2f}',
                'percentual_elegiveis': f'{estatisticas["percentual_elegiveis"]:.1f}%'
            }
        })
        
        return {
            "action_type": "calculo_vale_refeicao",
            "description": f"Cálculo de vale refeição concluído: {total_elegiveis} elegíveis de {total_ativos} colaboradores",
            "success": True,
            "resultado_df": resultado_df,
            "estatisticas": estatisticas,
            "total_records": len(resultado_df),
            "analysis_complete": True,  # MARCAR COMO COMPLETO - cálculo específico já foi feito
            "findings": f"Processados {total_ativos} colaboradores: {total_elegiveis} elegíveis, {total_excluidos} excluídos. Valor total: R$ {valor_total_geral:,.2f}",
            "auto_export_excel": True  # Sinalizar para exportar automaticamente
        }
        
    except Exception as e:
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'calculo_vale_refeicao',
            'action': f'❌ Erro no cálculo: {str(e)}',
            'details': {'erro': str(e)}
        })
        
        return {
            "action_type": "calculation_error",
            "description": f"Erro no cálculo de vale refeição: {str(e)}",
            "error": str(e),
            "success": False,
            "analysis_complete": True
        }

def execute_excel_export_action(db, data_tables: list, context: dict, iteration: int) -> dict:
    """Executa ação de exportação Excel pelo agente autônomo"""
    
    try:
        # Importar ferramenta de Excel
        from ...utils.excel_generator import execute_excel_export_tool
        
        # Verificar se há resultados de cálculo de vale refeição no contexto
        export_data = {}
        total_records = 0
        
        # PRIORIDADE: Usar resultados de cálculo se disponíveis
        calculo_vr_encontrado = False
        for finding in context.get('findings', []):
            if isinstance(finding, dict) and finding.get('action_type') == 'calculo_vale_refeicao':
                if 'resultado_df' in finding and finding.get('success', False):
                    # Usar resultado do cálculo de vale refeição
                    resultado_df = finding['resultado_df']
                    estatisticas = finding.get('estatisticas', {})
                    
                    export_data['CALCULO_VALE_REFEICAO'] = resultado_df
                    total_records += len(resultado_df)
                    calculo_vr_encontrado = True
                    
                    # Adicionar aba de estatísticas (incluindo por estado)
                    estatisticas_df = pd.DataFrame([{
                        'Métrica': 'Total de Colaboradores',
                        'Valor': estatisticas.get('total_colaboradores', 0)
                    }, {
                        'Métrica': 'Colaboradores Elegíveis - Total',
                        'Valor': estatisticas.get('total_elegiveis', 0)
                    }, {
                        'Métrica': 'Colaboradores Elegíveis - São Paulo (R$ 37,50)',
                        'Valor': estatisticas.get('elegiveis_sp', 0)
                    }, {
                        'Métrica': 'Colaboradores Elegíveis - Outros Estados (R$ 35,00)',
                        'Valor': estatisticas.get('elegiveis_outros', 0)
                    }, {
                        'Métrica': 'Colaboradores Excluídos',
                        'Valor': estatisticas.get('total_excluidos', 0)
                    }, {
                        'Métrica': 'Valor Total Geral (R$)',
                        'Valor': f"R$ {estatisticas.get('valor_total_geral', 0):,.2f}"
                    }, {
                        'Métrica': 'Valor Total - São Paulo (R$)',
                        'Valor': f"R$ {estatisticas.get('valor_total_sp', 0):,.2f}"
                    }, {
                        'Métrica': 'Valor Total - Outros Estados (R$)',
                        'Valor': f"R$ {estatisticas.get('valor_total_outros', 0):,.2f}"
                    }, {
                        'Métrica': 'Valor Médio por Elegível (R$)',
                        'Valor': f"R$ {estatisticas.get('valor_medio_por_elegivel', 0):,.2f}"
                    }, {
                        'Métrica': 'Percentual de Elegíveis (%)',
                        'Valor': f"{estatisticas.get('percentual_elegiveis', 0):.1f}%"
                    }, {
                        'Métrica': 'Percentual São Paulo (%)',
                        'Valor': f"{estatisticas.get('percentual_sp', 0):.1f}%"
                    }])
                    
                    export_data['ESTATISTICAS_VR'] = estatisticas_df
                    
                    # Adicionar aba no formato padrão solicitado
                    formato_padrao_df = pd.DataFrame()
                    
                    # Filtrar apenas colaboradores elegíveis para o formato padrão
                    elegiveis_df = resultado_df[resultado_df['STATUS'] == 'ELEGÍVEL'].copy()
                    
                    if not elegiveis_df.empty:
                        # Criar DataFrame no formato padrão
                        formato_padrao_data = []
                        
                        for _, row in elegiveis_df.iterrows():
                            valor_diario = row['VALOR_DIARIO']
                            total_vr = row['VALOR_TOTAL_VR']
                            
                            # Calcular custo empresa e desconto profissional (80% empresa, 20% funcionário)
                            custo_empresa = total_vr * 0.80  # 80% empresa
                            desconto_profissional = total_vr * 0.20  # 20% funcionário
                            
                            formato_padrao_data.append({
                                'Admissão': '01/05/2024',  # Data padrão - pode ser ajustada
                                'Sindicato do Colaborador': row['SINDICATO'],
                                'Competência': '05/2025',  # Competência padrão - pode ser ajustada
                                'Dias': float(22.00),
                                'VALOR DIÁRIO VR': float(valor_diario),
                                'TOTAL': float(total_vr),
                                'Custo empresa': float(custo_empresa),
                                'Desconto profissional': float(desconto_profissional),
                                'OBS GERAL': f"Matrícula: {row['MATRICULA']} - {row['NOME']} - Estado: {row['ESTADO']}"
                            })
                        
                        formato_padrao_df = pd.DataFrame(formato_padrao_data)
                        export_data['FORMATO_PADRAO_VR'] = formato_padrao_df
                        
                        st.session_state['agent_logs'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'agent': 'formato_padrao',
                            'action': f'📋 Aba formato padrão criada com {len(formato_padrao_df)} registros',
                            'details': {
                                'registros_formato_padrao': len(formato_padrao_df),
                                'custo_empresa_total': f"R$ {formato_padrao_df['Custo empresa'].sum():,.2f}",
                                'desconto_total': f"R$ {formato_padrao_df['Desconto profissional'].sum():,.2f}"
                            }
                        })
                    
                    st.session_state['agent_logs'].append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'agent': 'excel_export',
                        'action': '🎯 Usando resultados do cálculo de vale refeição para Excel',
                        'details': {
                            'registros_calculo': len(resultado_df),
                            'elegiveis': estatisticas.get('total_elegiveis', 0),
                            'valor_total': f"R$ {estatisticas.get('valor_total_geral', 0):,.2f}"
                        }
                    })
                    break
        
        # Se não encontrou cálculo de VR, usar dados das tabelas normalmente
        if not calculo_vr_encontrado:
            for table in data_tables:  # Todas as tabelas sem limitação
                try:
                    # Buscar todos os dados da tabela (sem limitação para exportação completa)
                    df = pd.read_sql(f'SELECT * FROM "{table}"', db.engine)
                    export_data[table] = df
                    total_records += len(df)
                except Exception as e:
                    # Se erro, criar DataFrame com informação do erro
                    export_data[table] = pd.DataFrame({
                        'Erro': [f'Não foi possível acessar dados: {str(e)}']
                    })
        
        # Metadados da exportação
        metadata = {
            'Pergunta Original': context['question'],
            'Iteração': iteration,
            'Total de Tabelas': len(data_tables),
            'Total de Registros': total_records,
            'Gerado em': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Tipo': 'Análise Autônoma - Dados Completos'
        }
        
        # Nome do arquivo baseado na pergunta - extrair apenas o objetivo real
        question_text = context.get('question', 'analise')
        
        # Se o texto começa com "CONTEXTO:", extrair apenas o OBJETIVO
        if "OBJETIVO:" in question_text:
            # Pegar o texto após "OBJETIVO:" até a próxima quebra de linha ou limite
            objetivo_start = question_text.find("OBJETIVO:") + len("OBJETIVO:")
            objetivo_end = question_text.find("\n", objetivo_start)
            if objetivo_end == -1:
                objetivo_end = objetivo_start + 50
            question_clean = question_text[objetivo_start:objetivo_end].strip()[:30]
        else:
            # Caso contrário, usar os primeiros 30 caracteres
            question_clean = question_text[:30]
        
        # Limpar caracteres especiais
        question_clean = question_clean.replace(' ', '_').replace('?', '').replace('/', '_').replace(':', '').replace('\n', '')
        
        # Se ficou vazio ou muito pequeno, usar nome padrão
        if len(question_clean) < 5:
            question_clean = "calculo_vale_refeicao"
            
        filename = f"analise_autonoma_{question_clean}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Usar o ExcelGenerator com as formatações implementadas
        try:
            from ...utils.excel_generator import ExcelGenerator
            
            generator = ExcelGenerator()
            excel_buffer = generator.create_excel_from_data(export_data, filename, metadata)
            
            if excel_buffer is None:
                return {
                    "action_type": "excel_export_error",
                    "description": "Erro ao gerar planilha Excel",
                    "error": "ExcelGenerator retornou None",
                    "analysis_complete": False,
                    "findings": "Falha na geração do Excel"
                }
            
        except Exception as e:
            return {
                "action_type": "excel_export_error",
                "description": f"Erro ao gerar planilha Excel: {str(e)}",
                "error": str(e),
                "analysis_complete": False,
                "findings": f"Falha na geração do Excel: {str(e)}"
            }
        
        # Verificar se o buffer tem dados
        excel_data = excel_buffer.getvalue()
        if len(excel_data) == 0:
            st.error("❌ Arquivo Excel está vazio")
            return {
                "action_type": "excel_export_error",
                "description": "Arquivo Excel vazio",
                "error": "Buffer sem dados",
                "analysis_complete": False,
                "findings": "Excel gerado mas sem conteúdo"
            }
        
        # Armazenar dados no session_state para evitar URLs intermediárias
        excel_key = f"excel_data_{iteration}_{int(datetime.now().timestamp())}"
        st.session_state[excel_key] = {
            'data': excel_data,
            'filename': filename,
            'size': len(excel_data)
        }
        
        # SOLUÇÃO DEFINITIVA: Mostrar informações apenas uma vez
        st.markdown("### 📥 Download da Planilha Excel")
        
        # Exibir informações do arquivo uma única vez
        st.success("✅ Planilha Excel gerada com sucesso!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 **Nome:** {filename}")
            st.info(f"📊 **Tabelas:** {len([k for k, v in export_data.items() if not v.empty])}")
        with col2:
            st.info(f"📊 **Tamanho:** {len(excel_data):,} bytes")
            st.info(f"📈 **Total de registros:** {total_records:,}")
        
        # Usar st.download_button padrão do Streamlit (mais confiável, evita duplicação)
        st.download_button(
            label=f"📥 Baixar Planilha Excel ({len(excel_data)/1024:.1f} KB)",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_download_{iteration}_{int(datetime.now().timestamp())}"
        )
        
        
        success = True
        
        return {
            "action_type": "excel_export",
            "description": f"Planilha Excel gerada com dados de {len(data_tables)} tabelas",
            "export_success": success,
            "filename": filename,
            "total_records": total_records,
            "analysis_complete": False,  # NÃO marcar como completo - deixar o agente decidir
            "findings": f"Dados exportados para Excel: {total_records} registros de {len(data_tables)} tabelas"
        }
        
    except Exception as e:
        return {
            "action_type": "excel_export_error",
            "description": f"Erro ao gerar planilha Excel",
            "error": str(e),
            "analysis_complete": False,
            "findings": f"Falha na exportação: {str(e)}"
        }

def synthesize_final_results(llm, context: dict, config: dict) -> dict:
    """Sintetiza os resultados finais da análise"""
    
    # Verificar se deve gerar Excel baseado nas ferramentas disponíveis
    should_generate_excel = "excel_export" in config.get('available_tools', [])
    
    synthesis_prompt = f"""
    Sintetize os resultados da análise:

    PERGUNTA: {context['question'][:100]}
    DESCOBERTAS: {len(context.get('findings', []))} etapas executadas

    Forneça resposta direta em 2-3 frases.
    {"Mencione que foi gerada planilha Excel." if should_generate_excel else ""}
    """
    
    try:
        response = llm.complete(synthesis_prompt)
        
        # Se deve gerar Excel, retornar indicação
        if should_generate_excel:
            return {
                "final_answer": response.text,
                "insights": ["Análise concluída", "Dados exportados para Excel"],
                "generate_excel": True,  # Sinalizar para gerar Excel
                "recommendations": ["Verificar planilha Excel gerada"]
            }
        else:
            return {
                "final_answer": response.text,
                "insights": ["Análise concluída"],
                "recommendations": ["Revisar resultados obtidos"]
            }
        
    except Exception as e:
        return {
            "final_answer": "Análise concluída com base nos dados disponíveis",
            "insights": ["Dados analisados com sucesso"],
            "error": str(e)
        }

def render_analysis_step(step: dict, show_reasoning: bool):
    """Renderiza uma etapa da análise"""
    
    # Usar container em vez de expander para evitar aninhamento
    with st.container():
        st.markdown(f"### 🔍 Etapa {step['step']}: {step['action']}")
        st.markdown(f"**Descrição:** {step['description']}")
        
        result = step['result']
        
        # Mostrar resposta direta primeiro se existir
        if isinstance(result, dict) and 'direct_answer' in result:
            st.success(f"✅ **Resposta:** {result['direct_answer']}")
        
        # Mostrar resultado numérico destacado para contagens
        if isinstance(result, dict) and 'total_registros' in result:
            st.metric("📊 Total de Registros", result['total_registros'])
        
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
                st.markdown("**📊 Resultado da Consulta:**")
                if isinstance(result['query_result'], list) and len(result['query_result']) <= 5:
                    # Para resultados pequenos, mostrar de forma mais limpa
                    for i, record in enumerate(result['query_result']):
                        if isinstance(record, dict):
                            for key, value in record.items():
                                st.markdown(f"- **{key}:** {value}")
                        else:
                            st.write(f"Registro {i+1}: {record}")
                elif isinstance(result['query_result'], list):
                    # Para resultados grandes, usar checkbox para mostrar/ocultar
                    if st.checkbox(f"Ver dados detalhados ({len(result['query_result'])} registros)", key=f"show_data_{step['step']}"):
                        st.json(result['query_result'])
                else:
                    st.write(result['query_result'])
            
            # Mostrar tabela alvo se especificada
            if 'target_table' in result:
                st.info(f"🎯 **Tabela analisada:** `{result['target_table']}`")
            
            # Mostrar raciocínio da IA se disponível
            if 'ai_reasoning' in result and result['ai_reasoning']:
                st.markdown("**🧠 Raciocínio da IA:**")
                st.write(result['ai_reasoning'])
            
            # Mostrar erro de parse JSON se houver
            if 'parse_error' in result:
                st.warning(f"⚠️ **Aviso de Parse:** {result['parse_error']}")
                
                # Mostrar resposta bruta para debug
                if st.checkbox(f"Ver resposta bruta da IA (Debug)", key=f"show_raw_{step['step']}"):
                    if 'ai_reasoning' in result:
                        st.code(result['ai_reasoning'], language="text")
            
            # Mostrar contagem de resultados se disponível
            if 'result_count' in result:
                st.metric("📊 Registros Retornados", result['result_count'])
            
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
            
            # Mostrar erros se existirem
            if 'error' in result:
                st.error(f"❌ **Erro:** {result['error']}")
            
            # Mostrar findings de forma destacada
            if 'findings' in result and result['findings']:
                st.markdown("**🔍 Descobertas:**")
                st.info(result['findings'])
        
        st.markdown("---")  # Separador entre etapas

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
