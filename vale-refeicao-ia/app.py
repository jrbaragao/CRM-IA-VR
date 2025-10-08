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
from src.ui.components import render_header, render_sidebar, render_realtime_logs
from src.ui.pages import upload, processing, calculations, reports, prompts_manager, agent_monitor, database_viewer

# Configuração da página
st.set_page_config(
    page_title="Sistema de Agente de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Mudado para collapsed já que temos navegação customizada
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
    
    # Adicionar logs de exemplo se não houver nenhum (apenas para teste)
    if len(st.session_state.agent_logs) == 0:
        from datetime import datetime
        st.session_state.agent_logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'agent': 'extraction_agent',
                'action': '🚀 Sistema iniciado',
                'details': {'status': 'Aguardando arquivos'}
            }
        ]
    
    # Verificar se deve usar sidebar padrão ou layout customizado
    use_custom_layout = st.session_state.get('use_custom_layout', True)
    
    if use_custom_layout:
        # Layout customizado com 3 colunas
        col_nav, col_main, col_logs = st.columns([1, 2.5, 1])
        
        # Coluna da esquerda - Navegação
        with col_nav:
            page = render_sidebar()
    else:
        # Layout com sidebar padrão (mais espaço para conteúdo)
        col_main, col_logs = st.columns([3, 1])
        page = render_sidebar()
    
    # Coluna do meio - Conteúdo principal
    with col_main:
        # Renderizar página selecionada
        if page == 'upload':
            upload.render()
        elif page == 'processing':
            processing.render()
        elif page == 'calculations':
            calculations.render()
        elif page == 'reports':
            reports.render()
        elif page == 'prompts':
            prompts_manager.render()
        elif page == 'monitor':
            agent_monitor.render()
        elif page == 'database':
            database_viewer.render()
    
    # Coluna da direita - Logs em tempo real
    with col_logs:
        render_realtime_logs()
    
    # Footer
    st.markdown("---")
    import os as _os
    import subprocess
    
    k_service = _os.getenv("K_SERVICE", "Local")
    k_revision = _os.getenv("K_REVISION", "Dev")
    
    # Tentar obter hash do Git commit
    git_hash = "unknown"
    try:
        git_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=Path(__file__).parent,
            stderr=subprocess.DEVNULL,
            timeout=2
        ).decode('utf-8').strip()
    except:
        pass
    
    # Timestamp do arquivo app.py (última modificação)
    try:
        app_mtime = _os.path.getmtime(__file__)
        from datetime import datetime
        app_date = datetime.fromtimestamp(app_mtime).strftime('%Y-%m-%d %H:%M')
    except:
        app_date = "unknown"
    
    st.markdown(f"""
    <div style='text-align: center; color: #666;'>
        <p>💳 Sistema de Vale Refeição IA | Desenvolvido com Streamlit e LlamaIndex</p>
        <p style='font-size: 0.8rem;'>Versão 1.0.0 | © 2024</p>
        <p style='font-size: 0.75rem; color:#999;'>
            K_SERVICE: <code>{k_service}</code> | 
            K_REVISION: <code>{k_revision}</code> | 
            Git: <code>{git_hash}</code> | 
            Build: <code>{app_date}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
