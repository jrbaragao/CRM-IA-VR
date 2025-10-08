"""
Página de upload de arquivos
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import io
import json
import streamlit.components.v1 as components

from ..components import (
    render_upload_widget,
    render_alert,
    render_data_preview,
    render_metrics_row
)
from ...config.settings import settings
from ...utils.cloud_storage import storage_manager

def render():
    """Renderiza página de upload"""
    st.header("📤 Upload de Dados")
    
    # Mostrar informações sobre storage
    storage_info = storage_manager.get_storage_info()
    if storage_info['using_gcs']:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.warning(f"""
            ☁️ **Cloud Storage Configurado** - Bucket: `{storage_info['bucket_name']}`
            
            ✅ **Upload Direto ao GCS habilitado**
            """)
        
        # col2 intencionalmente sem conteúdo: botão "Arquivos Grandes?" removido
        
        # Debug - vamos descobrir de onde vem o limite
        if st.button("🔍 Debug Upload Limits", help="Investigar de onde vem o limite real"):
            from ...utils.debug_upload import debug_upload_limits, create_test_file
            
            debug_upload_limits()
            create_test_file()

        # Garantir CORS do bucket para upload direto via navegador (executa uma vez)
        if not st.session_state.get('gcs_cors_configured'):
            if storage_manager.configure_bucket_cors():
                st.session_state['gcs_cors_configured'] = True
                st.info("CORS do bucket verificado/atualizado para upload direto.")

        st.divider()
        render_gcs_direct_upload_section(storage_info['bucket_name'])
        
    else:
        st.info("💾 **Modo Local** - Limite de upload: **200MB** por arquivo")
    
    # Mostrar o fluxo completo com destaque visual
    st.markdown("""
    ### 📋 Fluxo do Sistema:
    <div style='background-color: #e6f3ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <b>1. 📤 Upload</b> <span style='color: #667eea;'>(VOCÊ ESTÁ AQUI)</span> → 
        2. 🔄 Preparação de Dados → 
        3. 🗃️ Banco de Dados → 
        4. 🤖 Agentes de IA
    </div>
    """, unsafe_allow_html=True)
    
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
        
        # Informações sobre próximos passos
        st.divider()
        
        # Criar um alerta visual mais claro
        st.success("✅ **Arquivos carregados com sucesso!**")
        
        # Instruções claras com destaque visual
        with st.container():
            st.markdown("""
            ### 🎯 **Próximo Passo Obrigatório:**
            
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea; position: relative;'>
                <div style='position: absolute; left: -40px; top: 50%; transform: translateY(-50%); font-size: 30px; animation: bounce 2s infinite;'>
                    ⬅️
                </div>
                <h4>👉 Clique em <b>"🔄 Preparação de Dados"</b> no menu lateral</h4>
                <p style='color: #666; margin: 5px 0;'>O menu está à esquerda da tela</p>
                <p style='color: #d73502; font-weight: bold; margin: 10px 0 0 0;'>
                    ⚠️ Não use os botões do navegador! Use o menu lateral do Streamlit.
                </p>
            </div>
            
            <style>
                @keyframes bounce {
                    0%, 100% { transform: translateY(-50%) translateX(0); }
                    50% { transform: translateY(-50%) translateX(-10px); }
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            #### O que acontecerá na próxima página:
            - 🤖 O agente de IA processará e limpará os dados
            - 🏗️ Criará tabelas dinâmicas no banco de dados
            - 📊 Salvará permanentemente os dados
            - 📈 Você verá logs em tempo real
            
            > **⚠️ Importante**: Os dados ainda NÃO foram salvos no banco. Você DEVE ir para "Preparação de Dados" para completar o processo.
            """)

def process_uploaded_files(files):
    """Processa todos os arquivos enviados com logs detalhados"""
    
    # Container de logs visuais
    log_container = st.empty()
    progress_bar = st.progress(0)
    
    logs = []
    
    def add_log(icon, message, type="info"):
        """Adiciona log visual"""
        logs.append(f"{icon} {message}")
        log_text = "\n".join(logs)
        
        if type == "error":
            log_container.error(log_text)
        elif type == "warning":
            log_container.warning(log_text)
        elif type == "success":
            log_container.success(log_text)
        else:
            log_container.info(log_text)
    
    try:
        if 'uploaded_files' not in st.session_state:
            st.session_state['uploaded_files'] = {}
        
        total_files = len(files)
        add_log("📋", f"Iniciando processamento de {total_files} arquivo(s)...")
        
        for i, file in enumerate(files):
            try:
                add_log("📁", f"**Arquivo {i+1}/{total_files}**: {file.name}")
                progress_bar.progress((i) / total_files)
                
                # Obter tamanho do arquivo
                add_log("📏", f"Verificando tamanho do arquivo...")
                file.seek(0, 2)  # Ir para o final do arquivo
                file_size_bytes = file.tell()
                file_size_mb = file_size_bytes / (1024 * 1024)
                file.seek(0)  # Voltar ao início
                
                add_log("✅", f"Tamanho: **{file_size_mb:.2f} MB** ({file_size_bytes:,} bytes)")
                
                # Verificar limite
                if file_size_mb > 30:
                    add_log("⚠️", f"**ALERTA**: Arquivo > 30MB! Cloud Run pode rejeitar.", "warning")
                    add_log("💡", "Solução: Use a versão local ou divida o arquivo", "warning")
                    
                # Tentar salvar arquivo
                add_log("💾", f"Salvando arquivo no storage...")
                try:
                    file_content = file.read()
                    file.seek(0)  # Resetar para leitura do pandas
                    
                    add_log("☁️", f"Fazendo upload para Cloud Storage...")
                    
                    saved_path = storage_manager.upload_file(
                        file_content,
                        file.name,
                        folder="uploads"
                    )
                    
                    if not saved_path:
                        add_log("❌", f"Erro ao salvar arquivo '{file.name}'", "error")
                        continue
                        
                    add_log("✅", f"Arquivo salvo: {saved_path}", "success")
                    
                except Exception as e:
                    add_log("❌", f"**ERRO ao salvar**: {str(e)}", "error")
                    add_log("🔍", f"Tipo de erro: {type(e).__name__}", "error")
                    
                    if "413" in str(e) or "Payload" in str(e) or "too large" in str(e).lower():
                        add_log("🚨", f"**ERRO 413 (Payload Too Large)**", "error")
                        add_log("📊", f"Arquivo {file.name}: {file_size_mb:.2f}MB", "error")
                        add_log("⚠️", f"Limite do Cloud Run: ~32MB via HTTP", "error")
                        add_log("💡", f"**SOLUÇÃO**: Use a versão local:", "warning")
                        add_log("💻", "```bash\ngit clone https://github.com/jrbaragao/CRM-IA-VR.git\ncd CRM-IA-VR/vale-refeicao-ia\nstreamlit run app.py\n```", "warning")
                    continue
                
                # Ler arquivo para obter metadados
                add_log("📊", f"Lendo dados para análise...")
                
                try:
                    if file.name.endswith('.csv'):
                        # Ler CSV com tratamento especial para aspas
                        df = pd.read_csv(file, quotechar='"', skipinitialspace=True)
                        # Remover aspas dos nomes das colunas se houver
                        df.columns = df.columns.str.strip('"').str.strip()
                    else:
                        df = pd.read_excel(file)
                    
                    add_log("✅", f"Dados lidos: {len(df)} linhas x {len(df.columns)} colunas")
                    
                except Exception as e:
                    add_log("❌", f"Erro ao ler dados: {str(e)}", "error")
                    continue
                
                # Validações básicas
                if df.empty:
                    add_log("⚠️", f"Arquivo '{file.name}' está vazio", "warning")
                    continue
                
                # Armazenar no session state
                file_key = f"file_{i}_{file.name}"
                st.session_state['uploaded_files'][file_key] = {
                    'name': file.name,
                    'data': df,  # Mantém em memória para preview
                    'file_path': saved_path,  # Caminho no storage
                    'file_size_mb': round(file_size_mb, 2),
                    'type': 'data',  # Todos são dados agora
                    'uploaded_at': datetime.now(),
                    'rows': len(df),
                    'columns': len(df.columns),
                    'index_column': None  # Coluna de indexação
                }
                
                add_log("🎉", f"**Arquivo processado com sucesso!**", "success")
                
            except Exception as e:
                add_log("❌", f"**ERRO não tratado**: {str(e)}", "error")
                add_log("🔍", f"Tipo de erro: {type(e).__name__}", "error")
                import traceback
                add_log("📝", f"```\n{traceback.format_exc()}\n```", "error")
        
        progress_bar.progress(1.0)
        add_log("🏁", f"**Processamento concluído!**", "success")
        
        # Resumo final
        successful = len(st.session_state.get('uploaded_files', {}))
        add_log("📊", f"**Total processado**: {successful}/{total_files} arquivo(s)", "success" if successful == total_files else "warning")
        
        # Preview e configuração dos arquivos
        for file_key, file_info in st.session_state['uploaded_files'].items():
            if file_key.startswith('file_'):
                storage_icon = "☁️" if file_info.get('file_path', '').startswith('gs://') else "💾"
                with st.expander(f"📊 {file_info['name']} - {file_info.get('file_size_mb', 0)}MB {storage_icon} ({file_info['rows']} linhas, {file_info['columns']} colunas)", expanded=False):
                    # Preview dos dados
                    st.dataframe(file_info['data'].head(), use_container_width=True)
                    
                    # Seleção de coluna de indexação
                    st.divider()
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("**🔑 Configuração de Indexação**")
                        use_index = st.checkbox(
                            "Definir coluna de indexação",
                            key=f"use_index_{file_key}",
                            help="Marque se deseja definir uma coluna como chave primária/índice para correlação entre tabelas"
                        )
                    
                    with col2:
                        if use_index:
                            columns = list(file_info['data'].columns)
                            index_col = st.selectbox(
                                "Selecione a coluna de indexação:",
                                options=[''] + columns,
                                key=f"index_{file_key}",
                                help="Esta coluna será usada como chave primária para relacionar com outras tabelas"
                            )
                            
                            # Atualizar no session state
                            if index_col:
                                st.session_state['uploaded_files'][file_key]['index_column'] = index_col
                                st.info(f"✅ Coluna '{index_col}' definida como índice")
        
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivos: {str(e)}")

def render_gcs_direct_upload_section(bucket_name: str):
    """Seção para upload direto ao GCS via Signed URL (PUT)."""
    st.subheader("☁️ Upload Direto ao Google Cloud Storage (Recomendado para >30MB)")

    # Selecionar arquivo (apenas para pegar metadados e acionar JS)
    uploaded_file = st.file_uploader(
        "Selecione um arquivo grande para enviar direto ao GCS",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=False,
        key="gcs_direct_upload_picker",
        help="O arquivo será enviado diretamente ao Google Cloud Storage, sem passar pelo Cloud Run."
    )

    if uploaded_file is None:
        return

    filename = uploaded_file.name
    content_type = uploaded_file.type or "application/octet-stream"
    object_name = f"uploads/{filename}"

    # Gerar Signed URL (será usada pelo JS para PUT)
    signed_url = storage_manager.generate_signed_upload_url(object_name, expiration_minutes=30, content_type=content_type)

    if not signed_url:
        st.error("Não foi possível gerar URL assinada para upload.")
        return

    st.info(f"Arquivo: {filename} | Tipo: {content_type}")

    # Enviar o conteúdo em memória via JS fetch PUT
    # Estratégia: lemos o arquivo no frontend via input invisível controlado pelo Streamlit
    # e fazemos PUT com o mesmo content-type.
    upload_button = st.button("🚀 Enviar direto ao GCS")

    if upload_button:
        # Obter bytes do arquivo e expor como base64 para o JS reconstruir um Blob
        file_bytes = uploaded_file.getvalue()
        b64_data = file_bytes.hex()

        components.html(
            f"""
<script>
(async () => {{
  try {{
    const hex = "{b64_data}";
    function hexToBytes(hex) {{
      const bytes = new Uint8Array(hex.length / 2);
      for (let i = 0; i < bytes.length; i++) {{
        bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
      }}
      return bytes;
    }}
    const bytes = hexToBytes(hex);
    const blob = new Blob([bytes], {{ type: "{content_type}" }});

    const resp = await fetch("{signed_url}", {{
      method: 'PUT',
      headers: {{
        'Content-Type': '{content_type}'
      }},
      body: blob
    }});

    if (!resp.ok) {{
      const text = await resp.text();
      document.body.innerHTML = `<pre>Falha no upload: ${{resp.status}}\n${{text}}</pre>`;
      return;
    }}

    document.body.innerHTML = `<div style="font-family: sans-serif;">✅ Upload concluído no GCS: gs://{bucket_name}/{object_name}</div>`;
    window.parent.postMessage({{ type: 'gcs-upload-done', path: 'gs://{bucket_name}/{object_name}' }}, '*');
  }} catch (e) {{
    document.body.innerHTML = `<pre>Erro: ${{e?.message || e}}</pre>`;
  }}
}})();
</script>
            """,
            height=120
        )

        # Registrar no session state caminho no GCS (será confirmado pelo postMessage)
        st.session_state['last_gcs_object'] = f"gs://{bucket_name}/{object_name}"

    # Botão para processar arquivo que já está no GCS
    if st.session_state.get('last_gcs_object'):
        st.success(f"Arquivo no GCS: {st.session_state['last_gcs_object']}")
        if st.button("🔄 Ler e processar arquivo do GCS"):
            process_gcs_uploaded_file(st.session_state['last_gcs_object'])

def process_gcs_uploaded_file(gcs_path: str):
    """Lê arquivo do GCS e integra ao fluxo de arquivos carregados."""
    try:
        content = storage_manager.download_file(gcs_path)
        if content is None:
            st.error("Não foi possível baixar arquivo do GCS.")
            return

        name = Path(gcs_path).name

        # Detecta tipo pelo sufixo
        if name.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        if 'uploaded_files' not in st.session_state:
            st.session_state['uploaded_files'] = {}

        file_key = f"gcs_{name}_{int(datetime.now().timestamp())}"
        st.session_state['uploaded_files'][file_key] = {
            'name': name,
            'data': df,
            'file_path': gcs_path,
            'file_size_mb': round(len(content) / (1024 * 1024), 2),
            'type': 'data',
            'uploaded_at': datetime.now(),
            'rows': len(df),
            'columns': len(df.columns),
            'index_column': None
        }

        st.success(f"✅ Arquivo processado do GCS: {name}")
    except Exception as e:
        st.error(f"Erro ao processar arquivo do GCS: {e}")

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
                # Ler CSV com tratamento especial para aspas
                df = pd.read_csv(file, quotechar='"', skipinitialspace=True)
                # Remover aspas dos nomes das colunas se houver
                df.columns = df.columns.str.strip('"').str.strip()
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
                # Ler CSV com tratamento especial para aspas
                df = pd.read_csv(file, quotechar='"', skipinitialspace=True)
                # Remover aspas dos nomes das colunas se houver
                df.columns = df.columns.str.strip('"').str.strip()
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
