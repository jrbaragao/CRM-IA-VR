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
    st.header("📤 Upload de Arquivos")
    st.markdown("""
    Faça o upload das planilhas de RH que contêm as informações dos colaboradores.
    O sistema identificará automaticamente as colunas e utilizará a **MATRICULA** como chave para unificar os dados.
    """)
    
    # Container para uploads
    st.subheader("🗂️ Selecione os Arquivos")
    
    # Tabs para diferentes tipos de arquivos
    tab1, tab2, tab3 = st.tabs([
        "📋 Dados Principais", 
        "📊 Dados Complementares", 
        "📁 Upload em Lote"
    ])
    
    with tab1:
        st.markdown("""
        Upload do arquivo principal com dados dos funcionários (cadastro, matrícula, nome, cargo, etc.)
        """)
        
        main_file = render_upload_widget(
            label="Arquivo principal de funcionários",
            key="main_file_upload",
            help_text="Arquivo deve conter no mínimo: MATRICULA, NOME, CARGO"
        )
        
        if main_file:
            # Processar arquivo principal
            process_main_file(main_file)
    
    with tab2:
        st.markdown("""
        Upload de arquivos complementares (férias, faltas, benefícios, etc.)
        """)
        
        # Permitir múltiplos arquivos complementares
        comp_files = st.file_uploader(
            "Arquivos complementares",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            key="comp_files_upload",
            help="Selecione um ou mais arquivos complementares"
        )
        
        if comp_files:
            process_complementary_files(comp_files)
    
    with tab3:
        st.markdown("""
        Upload de múltiplos arquivos de uma vez. Útil quando há muitas planilhas para processar.
        """)
        
        batch_files = st.file_uploader(
            "Selecione todos os arquivos",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            key="batch_files_upload"
        )
        
        if batch_files:
            process_batch_files(batch_files)
    
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
    total_size = 0
    
    for key, file_info in st.session_state['uploaded_files'].items():
        files_data.append({
            'Nome': file_info['name'],
            'Tipo': 'Principal' if file_info['type'] == 'main' else 'Complementar',
            'Linhas': f"{file_info['rows']:,}",
            'Colunas': file_info['columns'],
            'Upload': file_info['upload_time'].strftime('%H:%M:%S')
        })
        total_rows += file_info['rows']
    
    # Tabela de arquivos
    df_files = pd.DataFrame(files_data)
    st.dataframe(df_files, use_container_width=True, hide_index=True)
    
    # Métricas resumidas
    metrics = [
        {'label': 'Total de Arquivos', 'value': len(files_data)},
        {'label': 'Total de Registros', 'value': f"{total_rows:,}"},
        {'label': 'Arquivo Principal', 'value': '✅' if any(f['Tipo'] == 'Principal' for f in files_data) else '❌'}
    ]
    
    render_metrics_row(metrics)
    
    # Opção para remover arquivos
    with st.expander("🗑️ Gerenciar Arquivos"):
        files_to_remove = st.multiselect(
            "Selecione arquivos para remover:",
            options=[f['name'] for f in st.session_state['uploaded_files'].values()]
        )
        
        if files_to_remove and st.button("Remover Selecionados", type="secondary"):
            for key, file_info in list(st.session_state['uploaded_files'].items()):
                if file_info['name'] in files_to_remove:
                    del st.session_state['uploaded_files'][key]
            st.rerun()
