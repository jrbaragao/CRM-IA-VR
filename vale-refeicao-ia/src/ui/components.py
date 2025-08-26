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

def render_sidebar() -> str:
    """Renderiza sidebar com navegação e retorna página selecionada"""
    with st.sidebar:
        st.header("🧭 Navegação")
        
        # Menu de navegação
        pages = {
            'upload': '📤 Upload de Arquivos',
            'processing': '🔄 Processamento',
            'calculations': '🧮 Cálculos VR',
            'reports': '📊 Relatórios'
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
            st.success("✅ API Key configurada")
        
        # Configurações de cálculo
        with st.expander("💰 Parâmetros de Cálculo"):
            valor_dia = st.number_input(
                "Valor por dia útil (R$):",
                min_value=0.0,
                value=35.0,
                step=0.50
            )
            
            desconto_pct = st.slider(
                "Desconto funcionário (%):",
                min_value=0,
                max_value=50,
                value=20
            )
            
            st.session_state['calc_params'] = {
                'valor_dia_util': valor_dia,
                'desconto_funcionario_pct': desconto_pct / 100
            }
        
        st.divider()
        
        # Informações do sistema
        st.caption("Sistema v1.0.0")
        st.caption(f"© {datetime.now().year} - Desenvolvido com ❤️")
        
    return selected_page

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
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
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
