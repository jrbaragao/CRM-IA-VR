"""
Página de monitoramento dos agentes em tempo real
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import json

from ..components import render_alert, render_metrics_row
from ...config.settings import settings

def render():
    """Renderiza página de monitoramento de agentes"""
    st.header("🤖 Monitor de Agentes IA")
    
    # Auto-refresh
    placeholder = st.empty()
    auto_refresh = st.checkbox("🔄 Auto-atualizar a cada 2 segundos", value=False)
    
    # Inicializar logs se não existir
    if 'agent_logs' not in st.session_state:
        st.session_state['agent_logs'] = []
    
    # Container principal
    with placeholder.container():
        render_monitor_content()
    
    # Auto-refresh se habilitado
    if auto_refresh:
        time.sleep(2)
        st.rerun()

def render_monitor_content():
    """Renderiza conteúdo do monitor"""
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs([
        "📜 Logs em Tempo Real", 
        "🔍 Ações dos Agentes",
        "📈 Métricas"
    ])
    
    with tab1:
        render_realtime_logs()
    
    with tab2:
        render_agent_actions()
    
    with tab3:
        render_metrics()


def render_realtime_logs():
    """Renderiza logs em tempo real"""
    st.subheader("Logs em Tempo Real")
    
    # Filtros
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        agent_filter = st.selectbox(
            "Filtrar por Agente",
            ["Todos", "extraction_agent", "calculation_agent", "report_agent"]
        )
    
    with col2:
        log_level = st.selectbox(
            "Nível de Log",
            ["Todos", "INFO", "WARNING", "ERROR", "DEBUG"]
        )
    
    with col3:
        if st.button("🗑️ Limpar Logs"):
            st.session_state['agent_logs'] = []
            st.rerun()
    
    # Container de logs com scroll
    log_container = st.container()
    
    with log_container:
        logs = st.session_state.get('agent_logs', [])
        
        # Filtrar logs
        if agent_filter != "Todos":
            logs = [log for log in logs if log.get('agent') == agent_filter]
        
        # Mostrar logs mais recentes primeiro
        logs = reversed(logs[-50:])  # Últimos 50 logs
        
        for log in logs:
            timestamp = log.get('timestamp', '')
            agent = log.get('agent', 'unknown')
            action = log.get('action', '')
            details = log.get('details', {})
            
            # Formatação do log
            log_message = f"**[{timestamp}]** `{agent}` - {action}"
            
            # Adicionar detalhes se existirem
            if details:
                details_str = json.dumps(details, ensure_ascii=False)
                log_message += f"\n```json\n{details_str}\n```"
            
            # Colorir baseado no tipo
            if "erro" in action.lower() or "error" in action.lower():
                st.error(log_message)
            elif "warning" in action.lower() or "aviso" in action.lower():
                st.warning(log_message)
            elif "success" in action.lower() or "concluído" in action.lower():
                st.success(log_message)
            else:
                st.info(log_message)

def render_agent_actions():
    """Renderiza ações específicas dos agentes"""
    st.subheader("Ações Detalhadas dos Agentes")
    
    # Simular algumas ações para demonstração
    if st.button("🎭 Simular Ações de Agentes"):
        simulate_agent_actions()
    
    # Mostrar ações por agente
    agents = ["extraction_agent", "calculation_agent", "report_agent"]
    
    for agent in agents:
        agent_logs = [log for log in st.session_state.get('agent_logs', []) if log.get('agent') == agent]
        
        if agent_logs:
            with st.expander(f"📋 {agent.replace('_', ' ').title()}", expanded=False):
                # Criar timeline de ações
                for log in agent_logs[-10:]:  # Últimas 10 ações
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.caption(get_time_ago(log['timestamp']))
                    
                    with col2:
                        st.markdown(f"**{log['action']}**")
                        if log.get('details'):
                            for key, value in log['details'].items():
                                st.caption(f"{key}: {value}")

def render_metrics():
    """Renderiza métricas dos agentes"""
    st.subheader("Métricas de Performance")
    
    # Calcular métricas dos logs
    logs = st.session_state.get('agent_logs', [])
    
    if not logs:
        st.info("Nenhuma métrica disponível ainda.")
        return
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Ações", len(logs))
    
    with col2:
        errors = len([log for log in logs if "erro" in log.get('action', '').lower()])
        st.metric("Erros", errors, delta_color="inverse")
    
    with col3:
        success = len([log for log in logs if "concluído" in log.get('action', '').lower()])
        st.metric("Sucessos", success)
    
    with col4:
        # Tempo médio de processamento (simulado)
        st.metric("Tempo Médio", "2.3s")
    
    st.divider()
    
    # Gráfico de atividade por agente
    if len(logs) > 0:
        df_logs = pd.DataFrame(logs)
        
        # Contar ações por agente
        agent_counts = df_logs['agent'].value_counts()
        
        st.subheader("Atividade por Agente")
        st.bar_chart(agent_counts)
        
        # Timeline de atividade
        st.subheader("Timeline de Atividade")
        
        # Preparar dados para timeline - com tratamento de erro
        try:
            # Tentar converter timestamps com diferentes formatos
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], errors='coerce', format='mixed')
            
            # Remover timestamps inválidos
            df_logs = df_logs.dropna(subset=['timestamp'])
            
            if not df_logs.empty:
                df_logs['hour'] = df_logs['timestamp'].dt.hour
                activity_by_hour = df_logs.groupby(['hour', 'agent']).size().unstack(fill_value=0)
                st.line_chart(activity_by_hour)
            else:
                st.info("Não foi possível processar os timestamps para o gráfico de timeline.")
        except Exception as e:
            st.warning(f"Erro ao processar timeline: {str(e)}")
            st.info("Alguns timestamps podem estar em formato incompatível.")

def get_last_agent_action(agent_name: str):
    """Obtém a última ação de um agente"""
    logs = st.session_state.get('agent_logs', [])
    agent_logs = [log for log in logs if log.get('agent') == agent_name]
    
    if agent_logs:
        return agent_logs[-1]
    return None

def get_time_ago(timestamp_str: str):
    """Calcula quanto tempo passou desde o timestamp"""
    try:
        # Tentar diferentes formatos de timestamp
        if 'T' in timestamp_str:
            # Formato ISO8601
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            # Formato apenas hora (HH:MM:SS) - assumir hoje
            from datetime import date
            today = date.today()
            time_part = datetime.strptime(timestamp_str, '%H:%M:%S').time()
            timestamp = datetime.combine(today, time_part)
        
        now = datetime.now()
        delta = now - timestamp
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m"
        else:
            return f"{int(delta.total_seconds() / 3600)}h"
    except Exception:
        return "?"

def simulate_agent_actions():
    """Simula algumas ações de agentes para demonstração"""
    simulated_actions = [
        {
            'timestamp': datetime.now().isoformat(),
            'agent': 'extraction_agent',
            'action': 'Iniciando análise de estrutura',
            'details': {'arquivo': 'funcionarios.csv', 'colunas': 7}
        },
        {
            'timestamp': (datetime.now() + timedelta(seconds=1)).isoformat(),
            'agent': 'extraction_agent',
            'action': 'Detectando tipos de dados',
            'details': {'matricula': 'string', 'salario': 'float', 'data_admissao': 'date'}
        },
        {
            'timestamp': (datetime.now() + timedelta(seconds=2)).isoformat(),
            'agent': 'extraction_agent',
            'action': 'Limpeza de dados concluída',
            'details': {'registros_limpos': 150, 'registros_removidos': 5}
        },
        {
            'timestamp': (datetime.now() + timedelta(seconds=3)).isoformat(),
            'agent': 'calculation_agent',
            'action': 'Iniciando cálculos de VR',
            'details': {'mes_referencia': '2024-08', 'funcionarios': 145}
        },
        {
            'timestamp': (datetime.now() + timedelta(seconds=4)).isoformat(),
            'agent': 'calculation_agent',
            'action': 'Aplicando regras de elegibilidade',
            'details': {'elegíveis': 140, 'não_elegíveis': 5}
        }
    ]
    
    # Adicionar aos logs
    if 'agent_logs' not in st.session_state:
        st.session_state['agent_logs'] = []
    
    st.session_state['agent_logs'].extend(simulated_actions)
    st.success("✅ Ações simuladas adicionadas aos logs!")
