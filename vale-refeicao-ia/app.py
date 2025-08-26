"""
Sistema de Cálculo de Vale Refeição com IA
Aplicação principal Streamlit
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent))

from src.config.settings import Settings
from src.ui.components import render_header, render_sidebar
from src.ui.pages import upload, processing, calculations, reports

# Configuração da página
st.set_page_config(
    page_title="💳 Sistema de Vale Refeição IA",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar configurações
settings = Settings()

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .agent-status {
        background: #e7f3ff;
        border: 1px solid #b8daff;
        color: #004085;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Renderizar header
    render_header()
    
    # Inicializar session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'calculations' not in st.session_state:
        st.session_state.calculations = None
    if 'agent_logs' not in st.session_state:
        st.session_state.agent_logs = []
    
    # Sidebar com navegação e configurações
    page = render_sidebar()
    
    # Renderizar página selecionada
    if page == 'upload':
        upload.render()
    elif page == 'processing':
        processing.render()
    elif page == 'calculations':
        calculations.render()
    elif page == 'reports':
        reports.render()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💳 Sistema de Vale Refeição IA | Desenvolvido com Streamlit e LlamaIndex</p>
        <p style='font-size: 0.8rem;'>Versão 1.0.0 | © 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
