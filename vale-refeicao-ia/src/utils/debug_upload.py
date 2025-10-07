"""
Debug utilitário para investigar limitações de upload
"""

import streamlit as st
import os

def debug_upload_limits():
    """Mostra informações de debug sobre limitações de upload"""
    
    st.subheader("🔍 Debug - Limitações de Upload")
    
    # Informações do ambiente
    env_info = {
        "K_SERVICE": os.getenv("K_SERVICE", "Local"),
        "PORT": os.getenv("PORT", "8501"),
        "GCS_BUCKET_NAME": os.getenv("GCS_BUCKET_NAME", "Não configurado"),
        "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID", "Não configurado"),
    }
    
    st.json(env_info)
    
    # Informações do Streamlit
    st.subheader("⚙️ Configurações Streamlit")
    
    try:
        from streamlit.config import get_option
        
        config_info = {
            "server.maxUploadSize": get_option("server.maxUploadSize"),
            "server.maxMessageSize": get_option("server.maxMessageSize"),
            "server.enableCORS": get_option("server.enableCORS"),
            "server.headless": get_option("server.headless"),
        }
        
        st.json(config_info)
        
    except Exception as e:
        st.error(f"Erro ao obter configurações: {e}")
    
    # Teste de upload pequeno
    st.subheader("🧪 Teste de Upload")
    
    uploaded_file = st.file_uploader(
        "Teste com arquivo pequeno primeiro",
        type=['txt', 'csv'],
        help="Tente um arquivo < 10MB primeiro para testar"
    )
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        
        st.success(f"""
        ✅ **Upload Funcionou!**
        
        **Arquivo**: {uploaded_file.name}
        **Tamanho**: {file_size_mb:.2f} MB ({file_size:,} bytes)
        **Tipo**: {uploaded_file.type}
        """)
        
        if file_size_mb > 30:
            st.balloons()
            st.success("🎉 **PROVA**: Upload > 30MB funcionou! O limite de 32MB não existe!")
        
        # Informações técnicas
        st.subheader("🔬 Informações Técnicas")
        st.code(f"""
Cabeçalhos do arquivo:
- Nome: {uploaded_file.name}
- Tamanho: {file_size:,} bytes ({file_size_mb:.2f} MB)
- Tipo MIME: {uploaded_file.type}
- ID da sessão: {st.session_state.get('session_id', 'N/A')}
        """)

def create_test_file():
    """Cria arquivo de teste para upload"""
    
    st.subheader("📝 Criar Arquivo de Teste")
    
    test_size = st.selectbox(
        "Tamanho do arquivo de teste:",
        options=[10, 25, 40, 50, 100],
        format_func=lambda x: f"{x}MB"
    )
    
    if st.button(f"Gerar arquivo de {test_size}MB"):
        # Criar conteúdo CSV de teste
        import io
        import pandas as pd
        
        # Calcular número de linhas para atingir o tamanho desejado
        rows_needed = (test_size * 1024 * 1024) // 100  # ~100 bytes por linha
        
        # Gerar dados
        test_data = []
        for i in range(rows_needed):
            test_data.append({
                'id': i,
                'name': f'Test_User_{i:06d}',
                'email': f'user{i}@test.com',
                'value': i * 1.5,
                'category': f'Category_{i % 10}',
                'description': f'Test description for row {i} with some additional text to increase size'
            })
        
        df = pd.DataFrame(test_data)
        
        # Converter para CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        actual_size_mb = len(csv_content.encode()) / (1024 * 1024)
        
        st.download_button(
            label=f"📥 Download arquivo de teste ({actual_size_mb:.1f}MB)",
            data=csv_content,
            file_name=f"test_file_{test_size}mb.csv",
            mime="text/csv"
        )
        
        st.info(f"✅ Arquivo gerado: {actual_size_mb:.1f}MB ({len(test_data):,} linhas)")
