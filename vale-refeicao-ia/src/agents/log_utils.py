"""
Utilidades para logging dos agentes
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional

def log_agent_action(agent_name: str, action: str, details: Optional[Dict[str, Any]] = None):
    """
    Registra uma ação do agente nos logs da sessão
    
    Args:
        agent_name: Nome do agente (ex: 'extraction_agent')
        action: Descrição da ação
        details: Detalhes adicionais (opcional)
    """
    if 'agent_logs' not in st.session_state:
        st.session_state['agent_logs'] = []
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'agent': agent_name,
        'action': action,
        'details': details or {}
    }
    
    st.session_state['agent_logs'].append(log_entry)
    
    # Manter apenas os últimos 100 logs para não sobrecarregar
    if len(st.session_state['agent_logs']) > 100:
        st.session_state['agent_logs'] = st.session_state['agent_logs'][-100:]
    
    # Forçar atualização da interface (opcional, pode causar muitas atualizações)
    # st.rerun()

def log_extraction_step(step: str, **kwargs):
    """Log específico para o agente de extração"""
    log_agent_action('extraction_agent', step, kwargs)

def log_calculation_step(step: str, **kwargs):
    """Log específico para o agente de cálculo"""
    log_agent_action('calculation_agent', step, kwargs)

def log_report_step(step: str, **kwargs):
    """Log específico para o agente de relatórios"""
    log_agent_action('report_agent', step, kwargs)
