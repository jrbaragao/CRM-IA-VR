"""
Página de relatórios e exportação
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
import json

from ..components import (
    render_alert,
    render_metrics_row,
    render_chat_interface
)
from ...config.settings import settings

def render():
    """Renderiza página de relatórios"""
    st.header("📊 Relatórios e Exportação")
    
    # Verificar se há cálculos realizados
    if not st.session_state.get('calculations'):
        render_alert(
            "⚠️ Nenhum cálculo foi realizado. Por favor, execute os cálculos primeiro.",
            "warning"
        )
        if st.button("↩️ Voltar para Cálculos"):
            st.session_state['current_page'] = 'calculations'
            st.rerun()
        return
    
    # Tabs para diferentes tipos de relatórios
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Relatório Executivo",
        "💾 Exportação de Dados",
        "🤖 Análise com IA",
        "📜 Histórico de Logs"
    ])
    
    with tab1:
        render_executive_report()
    
    with tab2:
        render_export_options()
    
    with tab3:
        render_ai_analysis()
    
    with tab4:
        render_agent_logs()

def render_executive_report():
    """Renderiza relatório executivo"""
    st.subheader("Relatório Executivo - Vale Refeição")
    
    # Dados do cálculo
    calc_data = st.session_state['calculations']
    df_calc = calc_data['data']
    mes_ref = calc_data['mes_referencia']
    regras = calc_data['regras']
    
    # Informações gerais
    st.markdown(f"""
    ### 📅 Período de Referência: {mes_ref}
    **Data de Geração:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """)
    
    # Resumo executivo
    st.markdown("### 📊 Resumo Executivo")
    
    total_funcionarios = len(df_calc)
    funcionarios_elegiveis = len(df_calc[df_calc['ELEGIVEL_VR'] == True])
    percentual_elegibilidade = (funcionarios_elegiveis / total_funcionarios * 100) if total_funcionarios > 0 else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Análise de Elegibilidade:**
        - Total de Funcionários: **{total_funcionarios:,}**
        - Funcionários Elegíveis: **{funcionarios_elegiveis:,}**
        - Taxa de Elegibilidade: **{percentual_elegibilidade:.1f}%**
        
        **Parâmetros Utilizados:**
        - Valor por Dia Útil: **R$ {regras['valor_dia_util']:.2f}**
        - Desconto Funcionário: **{regras['desconto_funcionario_pct']*100:.0f}%**
        - Dias Úteis no Mês: **{calc_data['dias_uteis']}**
        """)
    
    with col2:
        valor_total = df_calc['VALOR_TOTAL_VR'].sum()
        desconto_total = df_calc['DESCONTO_FUNCIONARIO'].sum()
        liquido_empresa = df_calc['VALOR_LIQUIDO_EMPRESA'].sum()
        
        st.markdown(f"""
        **Resumo Financeiro:**
        - Valor Total VR: **R$ {valor_total:,.2f}**
        - Desconto Funcionários: **R$ {desconto_total:,.2f}**
        - Custo Líquido Empresa: **R$ {liquido_empresa:,.2f}**
        
        **Médias:**
        - Valor Médio por Funcionário: **R$ {valor_total/funcionarios_elegiveis:,.2f}**
        - Custo Médio Empresa: **R$ {liquido_empresa/funcionarios_elegiveis:,.2f}**
        """)
    
    # Análise por departamento
    if 'DEPARTAMENTO' in df_calc.columns:
        st.markdown("### 🏢 Análise por Departamento")
        
        dept_analysis = df_calc.groupby('DEPARTAMENTO').agg({
            'MATRICULA': 'count',
            'VALOR_LIQUIDO_EMPRESA': 'sum'
        }).round(2)
        
        dept_analysis['Custo Médio'] = (
            dept_analysis['VALOR_LIQUIDO_EMPRESA'] / dept_analysis['MATRICULA']
        ).round(2)
        
        dept_analysis.columns = ['Funcionários', 'Custo Total', 'Custo Médio']
        dept_analysis = dept_analysis.sort_values('Custo Total', ascending=False)
        
        st.dataframe(dept_analysis, use_container_width=True)
    
    # Observações e recomendações
    st.markdown("### 💡 Observações e Recomendações")
    
    # Análise automática
    obs_list = []
    
    if percentual_elegibilidade < 80:
        obs_list.append(f"- A taxa de elegibilidade está em {percentual_elegibilidade:.1f}%, abaixo de 80%. Verificar critérios de elegibilidade.")
    
    funcionarios_sem_vr = df_calc[df_calc['ELEGIVEL_VR'] == False]
    if len(funcionarios_sem_vr) > 0:
        principais_motivos = funcionarios_sem_vr['OBSERVACOES'].value_counts().head(3)
        obs_list.append(f"- {len(funcionarios_sem_vr)} funcionários não são elegíveis. Principais motivos: {', '.join(principais_motivos.index[:3])}")
    
    custo_por_funcionario = liquido_empresa / funcionarios_elegiveis if funcionarios_elegiveis > 0 else 0
    if custo_por_funcionario > 600:
        obs_list.append(f"- Custo médio por funcionário (R$ {custo_por_funcionario:.2f}) está elevado. Considerar revisão dos valores.")
    
    if obs_list:
        for obs in obs_list:
            st.write(obs)
    else:
        st.write("- Todos os parâmetros estão dentro dos padrões esperados.")

def render_export_options():
    """Renderiza opções de exportação"""
    st.subheader("Exportação de Dados")
    
    calc_data = st.session_state['calculations']
    df_calc = calc_data['data']
    
    # Formatos de exportação
    st.markdown("### 📁 Formatos Disponíveis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📄 Excel")
        if st.button("Gerar Excel", key="export-excel", use_container_width=True):
            excel_data = export_to_excel(df_calc, calc_data)
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name=f"vale_refeicao_{calc_data['mes_referencia']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.markdown("#### 📊 CSV")
        csv_data = df_calc.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv_data,
            file_name=f"vale_refeicao_{calc_data['mes_referencia']}.csv",
            mime="text/csv"
        )
    
    with col3:
        st.markdown("#### 📋 JSON")
        json_data = df_calc.to_json(orient='records', date_format='iso')
        st.download_button(
            label="📥 Baixar JSON",
            data=json_data,
            file_name=f"vale_refeicao_{calc_data['mes_referencia']}.json",
            mime="application/json"
        )
    
    # Opções avançadas de exportação
    with st.expander("⚙️ Opções Avançadas de Exportação"):
        st.markdown("### Personalizar Exportação")
        
        # Seleção de colunas
        all_columns = list(df_calc.columns)
        selected_columns = st.multiselect(
            "Selecione as colunas para exportar:",
            options=all_columns,
            default=all_columns
        )
        
        # Filtros
        st.markdown("#### Filtros")
        col1, col2 = st.columns(2)
        
        with col1:
            export_only_eligible = st.checkbox("Exportar apenas funcionários elegíveis")
        
        with col2:
            if 'DEPARTAMENTO' in df_calc.columns:
                selected_depts = st.multiselect(
                    "Filtrar por departamentos:",
                    options=df_calc['DEPARTAMENTO'].unique()
                )
        
        # Aplicar filtros
        df_export = df_calc[selected_columns].copy()
        
        if export_only_eligible and 'ELEGIVEL_VR' in df_calc.columns:
            df_export = df_export[df_calc['ELEGIVEL_VR'] == True]
        
        if 'selected_depts' in locals() and selected_depts:
            df_export = df_export[df_calc['DEPARTAMENTO'].isin(selected_depts)]
        
        # Botão de exportação personalizada
        if st.button("Gerar Exportação Personalizada"):
            csv_custom = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV Personalizado",
                data=csv_custom,
                file_name=f"vale_refeicao_custom_{calc_data['mes_referencia']}.csv",
                mime="text/csv"
            )

def render_ai_analysis():
    """Renderiza análise com IA"""
    st.subheader("Análise Inteligente com IA")
    
    if not settings.openai_ready:
        render_alert(
            "⚠️ Configure a API Key da OpenAI na sidebar para usar este recurso.",
            "warning"
        )
        return
    
    st.markdown("""
    Use a IA para analisar os dados de vale refeição e obter insights personalizados.
    Você pode fazer perguntas como:
    - Quais departamentos têm o maior custo de VR?
    - Existe alguma anomalia nos valores calculados?
    - Como reduzir os custos mantendo os benefícios?
    """)
    
    # Interface de chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Adicionar contexto inicial se vazio
    if not st.session_state.chat_messages:
        calc_data = st.session_state['calculations']
        df_calc = calc_data['data']
        
        context = f"""
        Contexto dos dados de vale refeição:
        - Mês de referência: {calc_data['mes_referencia']}
        - Total de funcionários: {len(df_calc)}
        - Funcionários elegíveis: {len(df_calc[df_calc['ELEGIVEL_VR'] == True])}
        - Valor total: R$ {df_calc['VALOR_TOTAL_VR'].sum():,.2f}
        - Custo empresa: R$ {df_calc['VALOR_LIQUIDO_EMPRESA'].sum():,.2f}
        """
        
        st.session_state.chat_messages.append({
            "role": "system",
            "content": context
        })
    
    # Renderizar chat
    user_input = render_chat_interface(
        st.session_state.chat_messages[1:],  # Pular mensagem do sistema
        key="ai_analysis"
    )
    
    if user_input:
        # Adicionar pergunta do usuário
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Simular resposta da IA (substituir por chamada real)
        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                # Aqui você faria a chamada real para a IA
                response = "Baseado nos dados analisados, identifiquei que o departamento de Vendas tem o maior custo total de VR, representando 35% do total. Sugiro revisar a política de elegibilidade para otimizar custos."
                
                st.markdown(response)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response
                })

def render_agent_logs():
    """Renderiza logs dos agentes"""
    st.subheader("Histórico de Atividades dos Agentes")
    
    if not st.session_state.get('agent_logs'):
        st.info("Nenhuma atividade registrada ainda.")
        return
    
    # Converter logs para DataFrame
    logs_data = []
    for log in st.session_state['agent_logs']:
        logs_data.append({
            'Timestamp': log['timestamp'],
            'Agente': log['agent'],
            'Ação': log['action'],
            'Detalhes': json.dumps(log['details'], ensure_ascii=False)
        })
    
    df_logs = pd.DataFrame(logs_data)
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        agent_filter = st.selectbox(
            "Filtrar por agente:",
            options=['Todos'] + df_logs['Agente'].unique().tolist()
        )
    
    # Aplicar filtros
    if agent_filter != 'Todos':
        df_logs = df_logs[df_logs['Agente'] == agent_filter]
    
    # Mostrar logs
    st.dataframe(df_logs, use_container_width=True, height=400)
    
    # Estatísticas
    st.markdown("### 📊 Estatísticas de Processamento")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Ações", len(df_logs))
    with col2:
        st.metric("Agentes Ativos", df_logs['Agente'].nunique())
    with col3:
        if len(df_logs) > 0:
            tempo_total = pd.to_datetime(df_logs['Timestamp'].max()) - pd.to_datetime(df_logs['Timestamp'].min())
            st.metric("Tempo Total", f"{tempo_total.total_seconds():.1f}s")

def export_to_excel(df_calc, calc_data):
    """Exporta dados para Excel com múltiplas abas"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Aba principal com cálculos
        df_calc.to_excel(writer, sheet_name='Cálculos VR', index=False)
        
        # Aba de resumo
        summary_data = {
            'Métrica': [
                'Mês de Referência',
                'Total de Funcionários',
                'Funcionários Elegíveis',
                'Valor Total VR',
                'Desconto Funcionários',
                'Custo Líquido Empresa',
                'Valor por Dia',
                'Percentual Desconto',
                'Dias Úteis'
            ],
            'Valor': [
                calc_data['mes_referencia'],
                len(df_calc),
                len(df_calc[df_calc['ELEGIVEL_VR'] == True]),
                f"R$ {df_calc['VALOR_TOTAL_VR'].sum():,.2f}",
                f"R$ {df_calc['DESCONTO_FUNCIONARIO'].sum():,.2f}",
                f"R$ {df_calc['VALOR_LIQUIDO_EMPRESA'].sum():,.2f}",
                f"R$ {calc_data['regras']['valor_dia_util']:.2f}",
                f"{calc_data['regras']['desconto_funcionario_pct']*100:.0f}%",
                calc_data['dias_uteis']
            ]
        }
        
        pd.DataFrame(summary_data).to_excel(
            writer, 
            sheet_name='Resumo', 
            index=False
        )
        
        # Aba por departamento se disponível
        if 'DEPARTAMENTO' in df_calc.columns:
            dept_summary = df_calc.groupby('DEPARTAMENTO').agg({
                'MATRICULA': 'count',
                'VALOR_TOTAL_VR': 'sum',
                'VALOR_LIQUIDO_EMPRESA': 'sum'
            }).round(2)
            
            dept_summary.to_excel(writer, sheet_name='Por Departamento')
    
    output.seek(0)
    return output.getvalue()
