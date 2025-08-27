"""
Componentes reutilizáveis da interface Streamlit
"""

import streamlit as st
from typing import Optional, List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_header():
    """Renderiza o header principal da aplicação"""
    st.markdown("""
    <div class="main-header">
        <h1>💳 Sistema de Vale Refeição com IA</h1>
        <p>Processamento inteligente de dados de RH com LlamaIndex</p>
    </div>
    """, unsafe_allow_html=True)

def safe_columns(ratios):
    """
    Cria colunas de forma segura, evitando erro de aninhamento
    Retorna None se não conseguir criar colunas
    """
    try:
        return st.columns(ratios)
    except Exception:
        return None

def render_realtime_logs():
    """Renderiza coluna de logs em tempo real"""
    st.markdown("""
    <style>
    .log-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        height: calc(100vh - 200px);
        overflow-y: auto;
    }
    .log-entry {
        background: white;
        border-radius: 4px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #667eea;
        font-size: 0.85rem;
    }
    .log-time {
        color: #666;
        font-size: 0.75rem;
    }
    .log-agent {
        font-weight: bold;
        color: #667eea;
    }
    .log-action {
        color: #333;
        margin: 0.2rem 0;
    }
    .log-detail {
        color: #666;
        font-size: 0.8rem;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📡 Atividade dos Agentes")
    st.caption("Logs em tempo real")
    
    # Container para os logs
    log_container = st.container()
    
    with log_container:
        # Obter logs da sessão
        logs = st.session_state.get('agent_logs', [])
        
        # Mostrar contador de logs
        if logs:
            st.caption(f"📊 {len(logs)} atividades registradas")
        
        if not logs:
            st.info("🔍 Aguardando atividade dos agentes...")
        else:
            # Mostrar os últimos 20 logs (mais recentes primeiro)
            recent_logs = list(reversed(logs[-20:]))
            
            for log in recent_logs:
                # Formatar timestamp
                try:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    time_str = timestamp.strftime("%H:%M:%S")
                except:
                    time_str = "--:--:--"
                
                # Identificar agente
                agent_icons = {
                    'extraction_agent': '🔍',
                    'calculation_agent': '🧮',
                    'report_agent': '📊'
                }
                agent_icon = agent_icons.get(log.get('agent', ''), '🤖')
                agent_name = log.get('agent', 'unknown').replace('_', ' ').title()
                
                # Criar entrada de log
                with st.container():
                    st.markdown(f"""
                    <div class="log-entry">
                        <div class="log-time">{time_str}</div>
                        <div class="log-agent">{agent_icon} {agent_name}</div>
                        <div class="log-action">{log.get('action', 'Ação desconhecida')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar detalhes se existirem
                    if log.get('details'):
                        details = log['details']
                        if isinstance(details, dict):
                            for key, value in details.items():
                                st.caption(f"└─ {key}: {value}")
    
    # Botão para limpar logs
    if st.button("🗑️ Limpar Logs", key="clear_logs_sidebar"):
        st.session_state['agent_logs'] = []
        st.rerun()
    
    # Auto-refresh
    if st.checkbox("🔄 Auto-atualizar", key="auto_refresh_logs", value=True):
        # Atualizar a cada 2 segundos se habilitado
        import time
        time.sleep(0.1)  # Pequeno delay para não sobrecarregar

def render_sidebar() -> str:
    """Renderiza sidebar com navegação e retorna página selecionada"""
    use_custom_layout = st.session_state.get('use_custom_layout', True)
    
    if use_custom_layout:
        # Renderizar em coluna customizada
        st.header("🧭 Navegação")
        
        # Botão para alternar para sidebar padrão
        if st.button("📱 Recolher Menu", help="Usar sidebar padrão para mais espaço"):
            st.session_state['use_custom_layout'] = False
            st.rerun()
            
        return _render_navigation_content()
    else:
        # Renderizar na sidebar padrão
        with st.sidebar:
            st.header("🧭 Navegação")
            
            # Botão para voltar ao layout customizado
            if st.button("📱 Expandir Menu", help="Voltar ao layout com 3 colunas"):
                st.session_state['use_custom_layout'] = True
                st.rerun()
                
            return _render_navigation_content()

def _render_navigation_content() -> str:
    """Renderiza o conteúdo da navegação"""
    
    # Menu de navegação
    pages = {
        'upload': '📤 Upload de Dados',
        'processing': '🔄 Processamento',
        'database': '🗃️ Banco de Dados',
        'calculations': '🧮 Cálculos VR',
        'reports': '📊 Relatórios',
        'prompts': '🎯 Gerenciar Prompts',
        'monitor': '🤖 Monitor de Agentes'
    }
    
    # Seleção de página
    selected_page = st.radio(
        "Selecione uma página:",
        options=list(pages.keys()),
        format_func=lambda x: pages[x],
        key='navigation'
    )
    
    st.divider()
    
    # Status dos agentes
    st.header("🤖 Status dos Agentes")
    
    # Extraction Agent
    extraction_status = st.session_state.get('extraction_status', 'idle')
    render_agent_status("Agente de Extração", extraction_status)
    
    # Calculation Agent
    calculation_status = st.session_state.get('calculation_status', 'idle')
    render_agent_status("Agente de Cálculo", calculation_status)
    
    # Report Agent
    report_status = st.session_state.get('report_status', 'idle')
    render_agent_status("Agente de Relatórios", report_status)
    
    st.divider()
    
    # Configurações
    st.header("⚙️ Configurações")
    
    # API Key
    api_key = st.text_input(
        "OpenAI API Key:",
        type="password",
        help="Necessária para funcionamento dos agentes IA"
    )
    
    if api_key:
        st.session_state['openai_api_key'] = api_key
        st.success("✅ API Key configurada!")
    
    return selected_page

def render_agent_status(agent_name: str, status: str):
    """Renderiza status de um agente"""
    status_colors = {
        'idle': '⚪',
        'running': '🟡',
        'completed': '🟢',
        'error': '🔴'
    }
    
    status_texts = {
        'idle': 'Inativo',
        'running': 'Executando',
        'completed': 'Concluído',
        'error': 'Erro'
    }
    
    icon = status_colors.get(status, '⚪')
    text = status_texts.get(status, 'Desconhecido')
    
    st.markdown(f"{icon} **{agent_name}**: {text}")

def render_metrics_row(metrics: List[Dict[str, Any]]):
    """Renderiza uma linha de métricas"""
    # Tentar layout horizontal usando função segura
    cols = safe_columns(len(metrics))
    
    if cols:
        # Layout horizontal (funciona fora de colunas)
        for col, metric in zip(cols, metrics):
            with col:
                st.metric(
                    label=metric['label'],
                    value=metric['value'],
                    delta=metric.get('delta'),
                    delta_color=metric.get('delta_color', 'normal')
                )
    else:
        # Fallback: layout vertical (funciona dentro de colunas)
        st.markdown("### 📊 Métricas")
        for metric in metrics:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta'),
                delta_color=metric.get('delta_color', 'normal')
            )

def render_data_preview(df: pd.DataFrame, title: str = "Preview dos Dados"):
    """Renderiza preview de um DataFrame"""
    st.subheader(title)
    
    # Informações básicas
    col1, col2, col3 = safe_columns(3) or [st.container(), st.container(), st.container()]
    
    with col1:
        st.metric("Linhas", len(df))
    with col2:
        st.metric("Colunas", len(df.columns))
    with col3:
        st.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # Preview dos dados
    st.dataframe(df.head(10), use_container_width=True)
    
    # Informações das colunas
    with st.expander("📋 Informações das Colunas"):
        col_info = []
        for col in df.columns:
            col_info.append({
                'Coluna': col,
                'Tipo': str(df[col].dtype),
                'Não-nulos': df[col].count(),
                'Nulos': df[col].isnull().sum(),
                'Únicos': df[col].nunique()
            })
        
        st.dataframe(pd.DataFrame(col_info), use_container_width=True, hide_index=True)

def render_progress_bar(current: int, total: int, message: str = ""):
    """Renderiza barra de progresso"""
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{message} ({current}/{total})")

def render_alert(message: str, alert_type: str = "info"):
    """Renderiza alerta colorido"""
    alert_configs = {
        'success': {'color': '#d4edda', 'border': '#c3e6cb', 'icon': '✅'},
        'info': {'color': '#d1ecf1', 'border': '#bee5eb', 'icon': 'ℹ️'},
        'warning': {'color': '#fff3cd', 'border': '#ffeaa7', 'icon': '⚠️'},
        'error': {'color': '#f8d7da', 'border': '#f5c6cb', 'icon': '❌'}
    }
    
    config = alert_configs.get(alert_type, alert_configs['info'])
    
    st.markdown(f"""
    <div style="background-color: {config['color']}; 
                border: 1px solid {config['border']}; 
                border-radius: 4px; 
                padding: 12px; 
                margin: 10px 0;">
        {config['icon']} {message}
    </div>
    """, unsafe_allow_html=True)

def create_value_distribution_chart(df: pd.DataFrame, value_column: str) -> go.Figure:
    """Cria gráfico de distribuição de valores"""
    fig = px.histogram(
        df[df[value_column] > 0],
        x=value_column,
        nbins=30,
        title=f"Distribuição de {value_column}",
        labels={value_column: "Valor (R$)", "count": "Frequência"}
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Valor (R$)",
        yaxis_title="Número de Funcionários"
    )
    
    return fig

def create_department_summary_chart(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de resumo por departamento"""
    if 'DEPARTAMENTO' not in df.columns:
        return None
    
    summary = df.groupby('DEPARTAMENTO').agg({
        'VALOR_TOTAL_VR': 'sum',
        'MATRICULA': 'count'
    }).reset_index()
    
    summary.columns = ['Departamento', 'Total VR', 'Funcionários']
    summary = summary.sort_values('Total VR', ascending=True)
    
    fig = px.bar(
        summary,
        x='Total VR',
        y='Departamento',
        orientation='h',
        title="Vale Refeição por Departamento",
        text='Total VR'
    )
    
    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
    fig.update_layout(height=max(400, len(summary) * 30))
    
    return fig

def create_monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência mensal"""
    if 'DATA_ADMISSAO' not in df.columns:
        return None
    
    # Simular dados mensais (em produção, usar dados reais)
    import datetime
    months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    monthly_data = []
    
    for month in months:
        # Simular valores (substituir por lógica real)
        total_employees = len(df)
        monthly_value = total_employees * 25.50  # Valor médio por funcionário
        
        monthly_data.append({
            'Mês': month.strftime('%Y-%m'),
            'Total VR': monthly_value,
            'Funcionários': total_employees
        })
    
    monthly_df = pd.DataFrame(monthly_data)
    
    fig = px.line(
        monthly_df,
        x='Mês',
        y='Total VR',
        title="Evolução Mensal do Vale Refeição",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Valor Total (R$)",
        height=400
    )
    
    return fig



def render_agent_status(agent_name: str, status: str):
    """Renderiza status de um agente"""
    status_colors = {
        'idle': '⚪',
        'running': '🟡',
        'success': '🟢',
        'error': '🔴'
    }
    
    status_texts = {
        'idle': 'Inativo',
        'running': 'Processando...',
        'success': 'Concluído',
        'error': 'Erro'
    }
    
    icon = status_colors.get(status, '⚪')
    text = status_texts.get(status, 'Desconhecido')
    
    st.markdown(f"{icon} **{agent_name}**: {text}")

def render_metrics_row(metrics: List[Dict[str, Any]]):
    """Renderiza uma linha de métricas"""
    # Tentar layout horizontal usando função segura
    cols = safe_columns(len(metrics))
    
    if cols:
        # Layout horizontal (funciona fora de colunas)
        for col, metric in zip(cols, metrics):
            with col:
                st.metric(
                    label=metric['label'],
                    value=metric['value'],
                    delta=metric.get('delta'),
                    delta_color=metric.get('delta_color', 'normal')
                )
    else:
        # Fallback: layout vertical (funciona dentro de colunas)
        st.markdown("### 📊 Métricas")
        for metric in metrics:
            st.metric(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta'),
                delta_color=metric.get('delta_color', 'normal')
            )

def render_data_preview(df: pd.DataFrame, title: str = "Preview dos Dados"):
    """Renderiza preview de um DataFrame"""
    st.subheader(title)
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["📊 Dados", "📈 Estatísticas", "🔍 Informações"])
    
    with tab1:
        # Configurações de display
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Buscar:", placeholder="Digite para filtrar...")
        with col2:
            n_rows = st.selectbox("Linhas:", [10, 25, 50, 100], index=0)
        
        # Filtrar dados se houver busca
        if search:
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # Mostrar dados
        st.dataframe(
            filtered_df.head(n_rows),
            use_container_width=True,
            height=400
        )
        
        # Info sobre filtro
        if search:
            st.caption(f"Mostrando {len(filtered_df)} de {len(df)} registros")
    
    with tab2:
        # Estatísticas descritivas
        st.write("**Resumo Estatístico:**")
        st.dataframe(df.describe(), use_container_width=True)
        
        # Tipos de dados
        st.write("**Tipos de Dados:**")
        dtype_df = pd.DataFrame({
            'Coluna': df.columns,
            'Tipo': df.dtypes.astype(str),
            'Não Nulos': df.count(),
            'Nulos': df.isnull().sum(),
            '% Nulos': (df.isnull().sum() / len(df) * 100).round(2)
        })
        st.dataframe(dtype_df, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Registros", f"{len(df):,}")
            st.metric("Total de Colunas", len(df.columns))
        
        with col2:
            st.metric("Memória Utilizada", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            st.metric("Células Vazias", f"{df.isnull().sum().sum():,}")

def render_upload_widget(
    label: str,
    key: str,
    accepted_types: List[str] = ['.csv', '.xlsx', '.xls'],
    help_text: Optional[str] = None
) -> Optional[Any]:
    """Widget customizado para upload de arquivos"""
    
    # Container para o upload
    with st.container():
        uploaded_file = st.file_uploader(
            label,
            type=[t.replace('.', '') for t in accepted_types],
            key=key,
            help=help_text
        )
        
        if uploaded_file:
            # Mostrar informações do arquivo
            file_details = {
                "Nome": uploaded_file.name,
                "Tipo": uploaded_file.type,
                "Tamanho": f"{uploaded_file.size / 1024:.2f} KB"
            }
            
            with st.expander("📄 Detalhes do Arquivo", expanded=False):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")
        
        return uploaded_file

def render_progress_bar(current: int, total: int, text: str = "Processando..."):
    """Renderiza barra de progresso"""
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{text} ({current}/{total})")

def render_alert(message: str, alert_type: str = "info"):
    """Renderiza alerta customizado"""
    alert_types = {
        'info': {'icon': 'ℹ️', 'color': '#d1ecf1', 'border': '#bee5eb'},
        'success': {'icon': '✅', 'color': '#d4edda', 'border': '#c3e6cb'},
        'warning': {'icon': '⚠️', 'color': '#fff3cd', 'border': '#ffeeba'},
        'error': {'icon': '❌', 'color': '#f8d7da', 'border': '#f5c6cb'}
    }
    
    config = alert_types.get(alert_type, alert_types['info'])
    
    st.markdown(f"""
    <div style="background-color: {config['color']}; 
                border: 1px solid {config['border']}; 
                border-radius: 4px; 
                padding: 12px; 
                margin: 10px 0;">
        {config['icon']} {message}
    </div>
    """, unsafe_allow_html=True)

def create_value_distribution_chart(df: pd.DataFrame, value_column: str) -> go.Figure:
    """Cria gráfico de distribuição de valores"""
    fig = px.histogram(
        df[df[value_column] > 0],
        x=value_column,
        nbins=30,
        title=f"Distribuição de {value_column}",
        labels={value_column: "Valor (R$)", "count": "Frequência"}
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Valor (R$)",
        yaxis_title="Número de Funcionários"
    )
    
    return fig

def create_department_summary_chart(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de resumo por departamento"""
    if 'DEPARTAMENTO' not in df.columns:
        return None
    
    summary = df.groupby('DEPARTAMENTO').agg({
        'VALOR_TOTAL_VR': 'sum',
        'MATRICULA': 'count'
    }).reset_index()
    
    summary.columns = ['Departamento', 'Total VR', 'Funcionários']
    summary = summary.sort_values('Total VR', ascending=True)
    
    fig = px.bar(
        summary,
        x='Total VR',
        y='Departamento',
        orientation='h',
        title="Vale Refeição por Departamento",
        text='Total VR'
    )
    
    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
    fig.update_layout(height=max(400, len(summary) * 30))
    
    return fig

def render_chat_interface(
    messages: List[Dict[str, str]], 
    key: str = "chat"
) -> Optional[str]:
    """Renderiza interface de chat"""
    # Histórico de mensagens
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input do usuário
    prompt = st.chat_input("Digite sua pergunta...", key=f"{key}_input")
    
    return prompt
