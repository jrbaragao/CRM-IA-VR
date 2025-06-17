import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import io
import base64
from openai import OpenAI
import plotly.express as px
import plotly.graph_objects as go
import os
import sqlite3
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI as LlamaOpenAI

# Configuração da página
st.set_page_config(
    page_title="📊 Análise de Notas Fiscais",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def criar_banco_sqlite(df_cabecalho, df_itens):
    """Cria e configura o banco SQLite com os dados dos DataFrames"""
    conn = sqlite3.connect('notas_fiscais.db')
    
    # Ajustar nomes das colunas (remover espaços e caracteres especiais)
    df_cabecalho.columns = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df_cabecalho.columns]
    df_itens.columns = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df_itens.columns]
    
    # Converter DataFrames para SQLite
    df_cabecalho.to_sql('cabecalho', conn, if_exists='replace', index=False)
    df_itens.to_sql('itens', conn, if_exists='replace', index=False)
    
    # Mostrar estrutura das tabelas
    st.info("📊 Estrutura das tabelas no banco SQLite:")
    
    # Estrutura da tabela cabecalho
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(cabecalho)")
    colunas_cabecalho = cursor.fetchall()
    st.write("Tabela 'cabecalho':")
    for col in colunas_cabecalho:
        st.write(f"- {col[1]} ({col[2]})")
    
    # Estrutura da tabela itens
    cursor.execute("PRAGMA table_info(itens)")
    colunas_itens = cursor.fetchall()
    st.write("Tabela 'itens':")
    for col in colunas_itens:
        st.write(f"- {col[1]} ({col[2]})")
    
    return conn

def executar_query_sqlite(query, conn):
    """Executa uma query SQL no banco SQLite"""
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"❌ Erro na query SQL: {str(e)}")
        return None

def processar_pergunta(pergunta, conn, client, df_cabecalho, df_itens):
    """Processa a pergunta do usuário e retorna a resposta"""
    try:
        # Preparar informações sobre as colunas
        colunas_cabecalho = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df_cabecalho.columns]
        colunas_itens = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df_itens.columns]
        
        # Exemplos de dados
        exemplo_cabecalho = df_cabecalho.head(1).to_dict('records')[0]
        exemplo_itens = df_itens.head(1).to_dict('records')[0]
        
        # Primeiro, verificar se a pergunta precisa de SQL
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""Você é um assistente especializado em análise de dados.
                Sua tarefa é determinar se a pergunta do usuário precisa de uma consulta SQL ou não.
                Responda APENAS com 'SQL' se precisar de consulta SQL, ou 'CHAT' se for uma pergunta geral.
                
                Contexto dos dados:
                Tabela 'cabecalho':
                - Colunas: {', '.join(colunas_cabecalho)}
                - Exemplo: {exemplo_cabecalho}
                
                Tabela 'itens':
                - Colunas: {', '.join(colunas_itens)}
                - Exemplo: {exemplo_itens}
                
                Exemplos:
                - "Olá" -> CHAT
                - "Como vai?" -> CHAT
                - "Qual o valor total?" -> SQL
                - "Mostre as notas" -> SQL"""},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=10
        )
        
        tipo_resposta = response.choices[0].message.content.strip()
        
        if tipo_resposta == "CHAT":
            # Se for uma pergunta geral, responder diretamente
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"""Você é um assistente especializado em análise de notas fiscais.
                    Você tem acesso aos seguintes dados:
                    
                    Tabela 'cabecalho':
                    - Colunas: {', '.join(colunas_cabecalho)}
                    - Exemplo: {exemplo_cabecalho}
                    
                    Tabela 'itens':
                    - Colunas: {', '.join(colunas_itens)}
                    - Exemplo: {exemplo_itens}
                    
                    Responda de forma amigável e profissional."""},
                    {"role": "user", "content": pergunta}
                ],
                max_tokens=500
            )
            
            return {
                "sql": None,
                "resultado": None,
                "resposta_formatada": response.choices[0].message.content
            }
        
        # Se precisar de SQL, continuar com o processamento normal
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""Você é um especialista em SQL e análise de dados.
                Sua tarefa é converter perguntas em português para comandos SQL.
                Use SQLite como banco de dados.
                
                Tabelas disponíveis:
                
                1. Tabela 'cabecalho':
                - Colunas: {', '.join(colunas_cabecalho)}
                - Exemplo: {exemplo_cabecalho}
                
                2. Tabela 'itens':
                - Colunas: {', '.join(colunas_itens)}
                - Exemplo: {exemplo_itens}
                
                IMPORTANTE:
                1. Retorne APENAS o comando SQL, sem ```sql ou outras marcações
                2. Use os nomes das colunas EXATAMENTE como mostrado acima (com underscores)
                3. Use aspas simples para strings
                4. Exemplo correto: SELECT VALOR_NOTA_FISCAL FROM cabecalho WHERE CHAVE_DE_ACESSO = '123'
                5. NÃO inclua ```sql no início ou fim da query"""},
                {"role": "user", "content": pergunta}
            ],
            max_tokens=500
        )
        
        # Extrair SQL gerado e limpar
        sql_query = response.choices[0].message.content.strip()
        # Remover ```sql se existir
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Executar query
        resultado = executar_query_sqlite(sql_query, conn)
        
        if resultado is not None:
            # Formatar resposta
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de dados. Formate a resposta de forma clara e profissional."},
                    {"role": "user", "content": f"Formate esta resposta para o usuário: {resultado.to_string()}"}
                ],
                max_tokens=500
            )
            
            return {
                "sql": sql_query,
                "resultado": resultado,
                "resposta_formatada": response.choices[0].message.content
            }
        
    except Exception as e:
        st.error(f"❌ Erro ao processar pergunta: {str(e)}")
        return None

# Função principal
def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 Análise Inteligente de Notas Fiscais</h1>
        <p>Upload, análise e chat inteligente com IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Campo para API da OpenAI
        st.subheader("🤖 Integração OpenAI")
        openai_api_key = st.text_input(
            "API Key da OpenAI:",
            type="password",
            help="Cole sua API key da OpenAI para análises inteligentes e chat"
        )
        
        if openai_api_key:
            # Criar cliente OpenAI
            client = OpenAI(api_key=openai_api_key)
            os.environ["OPENAI_API_KEY"] = openai_api_key
            
            # Configurar LlamaIndex para usar GPT-4o globalmente
            Settings.llm = LlamaOpenAI(model="gpt-4o", temperature=0.1)
            
            st.success("✅ API OpenAI configurada! (GPT-4o)")
        
        st.divider()
        
        # Configurações do Chat
        st.subheader("💬 Configurações do Chat")
        chat_ativado = st.checkbox("Ativar Chat Inteligente", value=True)
        
        if chat_ativado:
            max_memory_tokens = st.slider("Memória do Chat (tokens):", 1000, 5000, 3000)
            st.info("📊 O chat analisará os dados CSV que você carregar")
        else:
            max_memory_tokens = 3000  # Valor padrão quando desativado
        
        st.divider()
        
    # Upload de arquivos
    st.header("📁 Upload dos Arquivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Cabeçalhos das Notas Fiscais")
        arquivo_cabecalho = st.file_uploader(
            "Selecione o arquivo de cabeçalhos (.csv)",
            type=['csv'],
            key="cabecalho"
        )
        
    with col2:
        st.subheader("📦 Itens das Notas Fiscais") 
        arquivo_itens = st.file_uploader(
            "Selecione o arquivo de itens (.csv)",
            type=['csv'],
            key="itens"
        )
    
    # Processamento dos arquivos
    if arquivo_cabecalho and arquivo_itens:
        
        # Carregando os dados
        with st.spinner("🔄 Carregando arquivos..."):
            try:
                df_cabecalho = pd.read_csv(arquivo_cabecalho)
                df_itens = pd.read_csv(arquivo_itens)
                
                # Criar banco SQLite
                conn = criar_banco_sqlite(df_cabecalho, df_itens)
                
                st.success("✅ Arquivos carregados e banco SQLite criado com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivos: {str(e)}")
                return
        
        # Informações básicas
        st.header("📊 Informações dos Datasets")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Registros Cabeçalho", df_cabecalho.shape[0])
        with col2:
            st.metric("📋 Colunas Cabeçalho", df_cabecalho.shape[1])
        with col3:
            st.metric("📦 Registros Itens", df_itens.shape[0])
        with col4:
            st.metric("📦 Colunas Itens", df_itens.shape[1])
        
        # Preview dos dados
        st.header("👀 Preview dos Dados")
        
        tab1, tab2 = st.tabs(["📋 Cabeçalhos", "📦 Itens"])
        
        with tab1:
            st.dataframe(df_cabecalho.head(), use_container_width=True)
            
        with tab2:
            st.dataframe(df_itens.head(), use_container_width=True)

    # Chat Inteligente com dados carregados
    if openai_api_key and chat_ativado and 'conn' in locals():
        st.header("💬 Chat Inteligente com Dados das Notas Fiscais")
        
        # Inicializar histórico do chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Mostrar histórico do chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input do usuário
        if prompt := st.chat_input("Faça sua pergunta sobre os dados das notas fiscais..."):
            # Adicionar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Processar pergunta
            with st.chat_message("assistant"):
                with st.spinner("🤖 Processando..."):
                    resultado = processar_pergunta(prompt, conn, client, df_cabecalho, df_itens)
                    
                    if resultado:
                        if resultado["sql"]:
                            # Se tiver SQL, mostrar o comando
                            st.code(resultado["sql"], language="sql")
                        
                        # Mostrar resultado formatado
                        st.markdown(resultado["resposta_formatada"])
                        
                        # Adicionar resposta ao histórico
                        mensagem = resultado["resposta_formatada"]
                        if resultado["sql"]:
                            mensagem = f"SQL gerado:\n```sql\n{resultado['sql']}\n```\n\nResposta:\n{resultado['resposta_formatada']}"
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": mensagem
                        })
                    else:
                        st.error("❌ Não foi possível processar sua pergunta.")

# Função removida - geração de PDF não é mais necessária

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Análise de Notas Fiscais | Desenvolvido com Streamlit e GPT-4o</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 