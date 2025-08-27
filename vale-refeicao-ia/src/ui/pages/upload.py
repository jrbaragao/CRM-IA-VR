"""
Página de upload de arquivos
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

from ..components import (
    render_upload_widget,
    render_alert,
    render_data_preview,
    render_metrics_row
)
from ...config.settings import settings

def render():
    """Renderiza página de upload"""
    st.header("📤 Upload de Dados")
    st.markdown("""
    Faça o upload das suas planilhas de dados. O sistema criará **tabelas dinâmicas** 
    automaticamente e os **agentes autônomos** identificarão as correlações através 
    dos prompts configurados.
    """)
    
    # Informações sobre o novo sistema
    with st.expander("ℹ️ Como funciona o novo sistema", expanded=False):
        st.markdown("""
        **🚀 Sistema Inteligente e Flexível:**
        
        **📊 Tabelas Dinâmicas:**
        - Cada arquivo cria sua própria tabela no banco
        - Estrutura adaptada automaticamente aos dados
        - Sem necessidade de esquema pré-definido
        
        **🤖 Correlações Inteligentes:**
        - Agentes autônomos identificam relações entre tabelas
        - Prompts definem como correlacionar os dados
        - Chaves de correlação definidas dinamicamente
        
        **🔄 Processo Simplificado:**
        - Upload → Tabela Dinâmica → Configuração de Prompts → Análise Autônoma
        """)
    
    # Container para uploads
    st.subheader("📁 Selecione seus Arquivos de Dados")
    
    uploaded_files = st.file_uploader(
        "Faça upload dos seus arquivos de dados",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        key="data_files_upload",
        help="Cada arquivo será processado e criará uma tabela dinâmica no banco de dados"
    )
    
    if uploaded_files:
        # Processar todos os arquivos
        process_uploaded_files(uploaded_files)
    
    # Seção de arquivos carregados
    if st.session_state.get('uploaded_files'):
        st.divider()
        display_uploaded_files()
        
        # Botão para prosseguir
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Processar Arquivos", type="primary", use_container_width=True):
                st.session_state['current_page'] = 'processing'
                st.rerun()

def process_uploaded_files(files):
    """Processa todos os arquivos enviados"""
    try:
        if 'uploaded_files' not in st.session_state:
            st.session_state['uploaded_files'] = {}
        
        for i, file in enumerate(files):
            # Ler arquivo
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validações básicas
            if df.empty:
                st.warning(f"⚠️ Arquivo '{file.name}' está vazio")
                continue
            
            # Armazenar no session state
            file_key = f"file_{i}_{file.name}"
            st.session_state['uploaded_files'][file_key] = {
                'name': file.name,
                'data': df,
                'type': 'data',  # Todos são dados agora
                'uploaded_at': datetime.now(),
                'rows': len(df),
                'columns': len(df.columns)
            }
        
        st.success(f"✅ {len(files)} arquivo(s) carregado(s) com sucesso!")
        
        # Preview dos arquivos
        for file_key, file_info in st.session_state['uploaded_files'].items():
            if file_key.startswith('file_'):
                with st.expander(f"📊 {file_info['name']} ({file_info['rows']} linhas, {file_info['columns']} colunas)", expanded=False):
                    st.dataframe(file_info['data'].head(), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivos: {str(e)}")

def process_main_file(file):
    """Processa arquivo principal"""
    try:
        # Ler arquivo
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Validações básicas
        if 'MATRICULA' not in df.columns and 'matricula' not in df.columns and 'Matricula' not in df.columns:
            # Tentar identificar coluna de matrícula
            possible_matricula_cols = [col for col in df.columns 
                                     if any(term in col.lower() 
                                           for term in ['matric', 'registro', 'cod', 'id'])]
            
            if possible_matricula_cols:
                render_alert(
                    f"Coluna MATRICULA não encontrada. Possíveis candidatas: {', '.join(possible_matricula_cols)}",
                    "warning"
                )
            else:
                render_alert(
                    "⚠️ Atenção: Coluna MATRICULA não encontrada. O sistema tentará identificá-la automaticamente.",
                    "warning"
                )
        
        # Armazenar no session state
        if 'uploaded_files' not in st.session_state:
            st.session_state['uploaded_files'] = {}
        
        st.session_state['uploaded_files']['main'] = {
            'name': file.name,
            'data': df,
            'type': 'main',
            'upload_time': datetime.now(),
            'rows': len(df),
            'columns': len(df.columns)
        }
        
        # Mostrar preview
        render_data_preview(df, f"Preview: {file.name}")
        
        render_alert(f"✅ Arquivo '{file.name}' carregado com sucesso!", "success")
        
    except Exception as e:
        render_alert(f"Erro ao processar arquivo: {str(e)}", "error")

def process_complementary_files(files):
    """Processa arquivos complementares"""
    if 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = {}
    
    success_count = 0
    error_count = 0
    
    for file in files:
        try:
            # Ler arquivo
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Armazenar
            file_key = f"comp_{file.name}"
            st.session_state['uploaded_files'][file_key] = {
                'name': file.name,
                'data': df,
                'type': 'complementary',
                'upload_time': datetime.now(),
                'rows': len(df),
                'columns': len(df.columns)
            }
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            st.error(f"Erro em '{file.name}': {str(e)}")
    
    if success_count > 0:
        render_alert(
            f"✅ {success_count} arquivo(s) complementar(es) carregado(s) com sucesso!",
            "success"
        )
    
    if error_count > 0:
        render_alert(
            f"❌ {error_count} arquivo(s) com erro no processamento.",
            "error"
        )

def process_batch_files(files):
    """Processa múltiplos arquivos em lote"""
    if 'uploaded_files' not in st.session_state:
        st.session_state['uploaded_files'] = {}
    
    progress_bar = st.progress(0, text="Processando arquivos...")
    success_count = 0
    error_count = 0
    
    for idx, file in enumerate(files):
        try:
            # Atualizar progresso
            progress = (idx + 1) / len(files)
            progress_bar.progress(progress, text=f"Processando {file.name}...")
            
            # Ler arquivo
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Determinar tipo (principal ou complementar)
            file_type = 'main' if idx == 0 else 'complementary'
            file_key = 'main' if file_type == 'main' else f"batch_{file.name}"
            
            # Armazenar
            st.session_state['uploaded_files'][file_key] = {
                'name': file.name,
                'data': df,
                'type': file_type,
                'upload_time': datetime.now(),
                'rows': len(df),
                'columns': len(df.columns)
            }
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            st.error(f"Erro em '{file.name}': {str(e)}")
    
    progress_bar.empty()
    
    # Mostrar resumo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Arquivos", len(files))
    with col2:
        st.metric("Sucesso", success_count, delta=None, delta_color="normal")
    with col3:
        st.metric("Erros", error_count, delta=None, delta_color="inverse" if error_count > 0 else "normal")

def display_uploaded_files():
    """Exibe resumo dos arquivos carregados"""
    st.subheader("📁 Arquivos Carregados")
    
    files_data = []
    total_rows = 0
    
    for key, file_info in st.session_state['uploaded_files'].items():
        files_data.append({
            'Nome': file_info['name'],
            'Tipo': 'Dados',  # Todos são dados agora
            'Linhas': f"{file_info['rows']:,}",
            'Colunas': file_info['columns'],
            'Upload': file_info.get('uploaded_at', file_info.get('upload_time', datetime.now())).strftime('%H:%M:%S')
        })
        total_rows += file_info['rows']
    
    # Tabela de arquivos
    df_files = pd.DataFrame(files_data)
    st.dataframe(df_files, use_container_width=True, hide_index=True)
    
    # Métricas resumidas
    metrics = [
        {'label': 'Total de Arquivos', 'value': len(files_data)},
        {'label': 'Total de Registros', 'value': f"{total_rows:,}"},
        {'label': 'Tabelas a Criar', 'value': len(files_data)}
    ]
    
    render_metrics_row(metrics)
    
    # Opção para remover arquivos
    with st.expander("🗑️ Gerenciar Arquivos"):
        files_to_remove = st.multiselect(
            "Selecione arquivos para remover:",
            options=[file_info['name'] for file_info in st.session_state['uploaded_files'].values()]
        )
        
        if files_to_remove and st.button("Remover Selecionados", type="secondary"):
            for key, file_info in list(st.session_state['uploaded_files'].items()):
                if file_info['name'] in files_to_remove:
                    del st.session_state['uploaded_files'][key]
            st.rerun()
