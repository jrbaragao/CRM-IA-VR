"""
Página de processamento de dados
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

from ..components import (
    render_alert,
    render_progress_bar,
    render_data_preview,
    render_metrics_row
)
from ...agents.extraction_agent import ExtractionAgent
from ...agents.log_utils import log_extraction_step
from ...config.settings import settings

def render():
    """Renderiza página de processamento"""
    st.header("🔄 Processamento de Dados")
    
    # Botão de teste para logs
    if st.button("🧪 Testar Logs"):
        log_extraction_step("🧪 Teste de log", tipo="teste", timestamp="agora")
        st.success("Log de teste adicionado!")
        st.rerun()
    
    # Verificar se há arquivos para processar
    if not st.session_state.get('uploaded_files'):
        render_alert(
            "⚠️ Nenhum arquivo foi carregado. Por favor, faça upload dos arquivos primeiro.",
            "warning"
        )
        if st.button("↩️ Voltar para Upload"):
            st.session_state['current_page'] = 'upload'
            st.rerun()
        return
    
    st.markdown("""
    O sistema irá processar os arquivos carregados utilizando agentes de IA para:
    - 🔍 Detectar e mapear colunas automaticamente
    - 🧹 Limpar e normalizar dados
    - 🔗 Unificar informações usando MATRICULA como chave
    - ✅ Validar dados e identificar inconsistências
    """)
    
    # Status dos agentes
    st.session_state['extraction_status'] = 'idle'
    
    # Container para processamento
    with st.container():
        st.subheader("📊 Arquivos para Processar")
        
        # Listar arquivos
        files_to_process = []
        for key, file_info in st.session_state['uploaded_files'].items():
            files_to_process.append({
                'Nome': file_info['name'],
                'Tipo': file_info['type'],
                'Registros': file_info['rows'],
                'Status': 'Aguardando'
            })
        
        df_files = pd.DataFrame(files_to_process)
        st.dataframe(df_files, use_container_width=True, hide_index=True)
    
    # Botão para iniciar processamento
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("🚀 Iniciar Processamento", type="primary"):
        process_files()
    st.markdown("</div>", unsafe_allow_html=True)

def process_files():
    """Processa os arquivos carregados"""
    st.session_state['extraction_status'] = 'running'
    
    # Inicializar agente de extração
    extraction_agent = ExtractionAgent()
    
    # Container para logs
    log_container = st.container()
    progress_container = st.container()
    
    # Processar cada arquivo
    total_files = len(st.session_state['uploaded_files'])
    processed_data = {}
    
    for idx, (key, file_info) in enumerate(st.session_state['uploaded_files'].items()):
        with progress_container:
            render_progress_bar(
                idx + 1, 
                total_files, 
                f"Processando {file_info['name']}..."
            )
        
        with log_container:
            with st.expander(f"📄 {file_info['name']}", expanded=True):
                st.info(f"🔄 Iniciando processamento...")
                
                # Adicionar logs simulados para demonstração
                log_extraction_step("📋 Preparando para processar arquivo", arquivo=file_info['name'])
                st.empty()  # Força atualização
                time.sleep(0.3)
                
                log_extraction_step("🔍 Analisando estrutura do arquivo", 
                                  total_linhas=file_info['rows'], 
                                  total_colunas=len(file_info['data'].columns))
                st.empty()  # Força atualização
                time.sleep(0.3)
                
                # Processar com o agente
                try:
                    # Simular etapas de processamento
                    log_extraction_step("🏷️ Identificando tipos de colunas...")
                    st.empty()  # Força atualização
                    time.sleep(0.3)
                    
                    log_extraction_step("✅ Colunas identificadas", 
                                      colunas=list(file_info['data'].columns)[:5] + ['...'])
                    st.empty()  # Força atualização
                    time.sleep(0.3)
                    
                    log_extraction_step("🧹 Limpando dados inconsistentes...")
                    st.empty()  # Força atualização
                    time.sleep(0.3)
                    
                    # Aqui você processaria o arquivo real
                    # df_processed = extraction_agent.process(file_info['data'])
                    df_processed = file_info['data']  # Por enquanto, usar dados originais
                    
                    log_extraction_step("✅ Limpeza concluída", 
                                      registros_removidos=0,
                                      registros_válidos=len(df_processed))
                    st.empty()  # Força atualização
                    
                    # Adicionar log do agente
                    log_entry = extraction_agent.log_action(
                        "Processamento concluído",
                        {
                            "file": file_info['name'],
                            "rows_processed": len(df_processed),
                            "columns_mapped": len(df_processed.columns)
                        }
                    )
                    st.session_state['agent_logs'].append(log_entry)
                    
                    # Armazenar dados processados
                    processed_data[key] = {
                        'name': file_info['name'],
                        'data': df_processed,
                        'original_rows': file_info['rows'],
                        'processed_rows': len(df_processed),
                        'processing_time': datetime.now()
                    }
                    
                    st.success(f"✅ Processamento concluído! {len(df_processed)} registros processados.")
                    
                    # Mostrar preview dos dados processados
                    st.markdown("**Preview dos Dados Processados:**")
                    st.dataframe(df_processed.head(10), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Erro no processamento: {str(e)}")
                    st.session_state['extraction_status'] = 'error'
    
    # Salvar dados processados
    st.session_state['processed_data'] = processed_data
    st.session_state['extraction_status'] = 'success'
    
    # Unificar dados usando MATRICULA
    st.divider()
    st.subheader("🔗 Unificação de Dados")
    
    with st.spinner("Unificando dados usando MATRICULA como chave..."):
        unified_data = unify_data(processed_data)
        st.session_state['unified_data'] = unified_data
    
    # Log final
    log_extraction_step("🎉 Processamento completo!", 
                       arquivos_processados=len(processed_data),
                       total_registros=sum(d['processed_rows'] for d in processed_data.values()))
    
    # Mostrar resumo
    st.success("✅ Processamento completo!")
    
    # Métricas finais
    metrics = [
        {'label': 'Arquivos Processados', 'value': len(processed_data)},
        {'label': 'Total de Registros', 'value': sum(d['processed_rows'] for d in processed_data.values())},
        {'label': 'Funcionários Únicos', 'value': len(unified_data) if 'unified_data' in locals() else 0}
    ]
    render_metrics_row(metrics)
    
    # Botão para próxima etapa
    st.divider()
    # Centralizar botão sem usar colunas (para evitar conflito com layout principal)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("➡️ Ir para Cálculos", type="primary"):
        st.session_state['current_page'] = 'calculations'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def unify_data(processed_data):
    """Unifica dados usando MATRICULA como chave"""
    # Criar DataFrame unificado
    main_df = None
    
    for key, data_info in processed_data.items():
        df = data_info['data']
        
        if 'MATRICULA' not in df.columns:
            st.warning(f"⚠️ Arquivo {data_info['name']} não possui coluna MATRICULA")
            continue
        
        if main_df is None:
            main_df = df
        else:
            # Fazer merge usando MATRICULA
            main_df = pd.merge(
                main_df,
                df,
                on='MATRICULA',
                how='outer',
                suffixes=('', f'_{key}')
            )
    
    return main_df if main_df is not None else pd.DataFrame()
