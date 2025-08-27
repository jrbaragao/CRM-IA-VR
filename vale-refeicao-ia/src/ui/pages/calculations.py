"""
Página de cálculos de vale refeição
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

from ..components import (
    render_alert,
    render_metrics_row,
    render_data_preview,
    create_value_distribution_chart,
    create_department_summary_chart
)
from ...agents.calculation_agent import CalculationAgent
from ...config.settings import settings

def render():
    """Renderiza página de cálculos"""
    st.header("🧮 Cálculos de Vale Refeição")
    
    # Verificar se há dados processados
    if not st.session_state.get('processed_data'):
        render_alert(
            "⚠️ Nenhum dado foi processado. Por favor, processe os arquivos primeiro.",
            "warning"
        )
        if st.button("↩️ Voltar para Processamento"):
            st.session_state['current_page'] = 'processing'
            st.rerun()
        return
    
    # Configurações de cálculo
    st.subheader("⚙️ Configurações de Cálculo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Mês de referência
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        mes_ref = st.selectbox(
            "Mês de Referência",
            options=[(f"{i:02d}/{current_year}", f"{current_year}-{i:02d}") 
                    for i in range(1, 13)],
            index=current_month - 1,
            format_func=lambda x: x[0]
        )
        mes_referencia = mes_ref[1]
    
    with col2:
        # Valor por dia
        valor_dia = st.number_input(
            "Valor por Dia Útil (R$)",
            min_value=0.0,
            value=st.session_state.get('calc_params', {}).get('valor_dia_util', 35.0),
            step=0.50,
            format="%.2f"
        )
    
    with col3:
        # Desconto funcionário
        desconto_pct = st.slider(
            "Desconto Funcionário (%)",
            min_value=0,
            max_value=50,
            value=int(st.session_state.get('calc_params', {}).get('desconto_funcionario_pct', 0.20) * 100)
        )
    
    # Mostrar dias úteis do mês
    year, month = map(int, mes_referencia.split('-'))
    dias_uteis = calculate_working_days(year, month)
    
    st.info(f"📅 O mês {mes_ref[0]} possui **{dias_uteis} dias úteis**")
    
    # Regras customizadas
    with st.expander("🔧 Regras Customizadas", expanded=False):
        st.markdown("Configure regras específicas para o cálculo:")
        
        col1, col2 = st.columns(2)
        with col1:
            incluir_estagiarios = st.checkbox("Incluir Estagiários", value=True)
            descontar_faltas = st.checkbox("Descontar Faltas", value=True)
        
        with col2:
            valor_minimo = st.number_input("Valor Mínimo VR (R$)", min_value=0.0, value=100.0)
            valor_maximo = st.number_input("Valor Máximo VR (R$)", min_value=0.0, value=1500.0)
    
    # Preparar regras customizadas
    regras_customizadas = {
        'valor_dia_util': valor_dia,
        'desconto_funcionario_pct': desconto_pct / 100,
        'incluir_estagiarios': incluir_estagiarios,
        'descontar_faltas': descontar_faltas,
        'valor_minimo': valor_minimo,
        'valor_maximo': valor_maximo
    }
    
    # Botão para calcular
    if st.button("🧮 Calcular Vale Refeição", type="primary"):
        calculate_vr(mes_referencia, dias_uteis, regras_customizadas)

def calculate_working_days(year, month):
    """Calcula dias úteis do mês"""
    # Obter primeiro e último dia do mês
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    
    # Contar dias úteis (segunda a sexta)
    working_days = 0
    current_day = first_day
    
    while current_day <= last_day:
        if current_day.weekday() < 5:  # 0-4 são segunda a sexta
            working_days += 1
        current_day = current_day.replace(day=current_day.day + 1)
    
    return working_days

def calculate_vr(mes_referencia, dias_uteis, regras_customizadas):
    """Executa cálculo de vale refeição"""
    st.session_state['calculation_status'] = 'running'
    
    # Inicializar agente de cálculo
    calculation_agent = CalculationAgent()
    
    # Container para progresso
    progress_container = st.container()
    
    with st.spinner("🧮 Calculando vale refeição..."):
        try:
            # Obter dados unificados
            if 'unified_data' in st.session_state:
                df_funcionarios = st.session_state['unified_data']
            else:
                # Usar primeiro arquivo processado
                first_data = list(st.session_state['processed_data'].values())[0]
                df_funcionarios = first_data['data']
            
            # Executar cálculo
            df_calculado = calculation_agent.process(
                funcionarios_df=df_funcionarios,
                mes_referencia=mes_referencia,
                regras_customizadas=regras_customizadas
            )
            
            # Salvar resultados
            st.session_state['calculations'] = {
                'data': df_calculado,
                'mes_referencia': mes_referencia,
                'dias_uteis': dias_uteis,
                'regras': regras_customizadas,
                'timestamp': datetime.now()
            }
            
            st.session_state['calculation_status'] = 'success'
            
            # Mostrar resultados
            show_calculation_results(df_calculado)
            
        except Exception as e:
            st.error(f"❌ Erro no cálculo: {str(e)}")
            st.session_state['calculation_status'] = 'error'

def show_calculation_results(df_calculado):
    """Mostra resultados dos cálculos"""
    st.success("✅ Cálculos concluídos com sucesso!")
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumo Geral", 
        "👥 Por Funcionário", 
        "🏢 Por Departamento",
        "📈 Análises"
    ])
    
    with tab1:
        # Métricas gerais
        total_funcionarios = len(df_calculado)
        funcionarios_elegiveis = len(df_calculado[df_calculado['ELEGIVEL_VR'] == True])
        valor_total = df_calculado['VALOR_TOTAL_VR'].sum()
        desconto_total = df_calculado['DESCONTO_FUNCIONARIO'].sum()
        liquido_empresa = df_calculado['VALOR_LIQUIDO_EMPRESA'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Funcionários", f"{total_funcionarios:,}")
            st.metric("Funcionários Elegíveis", f"{funcionarios_elegiveis:,}")
        
        with col2:
            st.metric("Valor Total VR", f"R$ {valor_total:,.2f}")
            st.metric("Desconto Funcionários", f"R$ {desconto_total:,.2f}")
        
        with col3:
            st.metric("Custo Líquido Empresa", f"R$ {liquido_empresa:,.2f}")
            st.metric("Custo Médio/Funcionário", f"R$ {liquido_empresa/funcionarios_elegiveis:,.2f}" if funcionarios_elegiveis > 0 else "R$ 0,00")
    
    with tab2:
        # Dados por funcionário
        st.subheader("Detalhamento por Funcionário")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_elegivel = st.selectbox(
                "Filtrar por Elegibilidade",
                ["Todos", "Elegíveis", "Não Elegíveis"]
            )
        
        # Aplicar filtros
        df_filtrado = df_calculado.copy()
        if filtro_elegivel == "Elegíveis":
            df_filtrado = df_filtrado[df_filtrado['ELEGIVEL_VR'] == True]
        elif filtro_elegivel == "Não Elegíveis":
            df_filtrado = df_filtrado[df_filtrado['ELEGIVEL_VR'] == False]
        
        # Mostrar dados
        colunas_exibir = [
            'MATRICULA', 'NOME', 'CARGO', 'DEPARTAMENTO',
            'ELEGIVEL_VR', 'DIAS_TRABALHADOS', 'VALOR_TOTAL_VR',
            'DESCONTO_FUNCIONARIO', 'VALOR_LIQUIDO_EMPRESA', 'OBSERVACOES'
        ]
        
        colunas_disponiveis = [col for col in colunas_exibir if col in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[colunas_disponiveis],
            use_container_width=True,
            height=400
        )
        
        # Opção de download
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Baixar CSV",
            csv,
            "calculo_vr_funcionarios.csv",
            "text/csv",
            key='download-csv'
        )
    
    with tab3:
        # Análise por departamento
        st.subheader("Resumo por Departamento")
        
        if 'DEPARTAMENTO' in df_calculado.columns:
            dept_summary = df_calculado.groupby('DEPARTAMENTO').agg({
                'MATRICULA': 'count',
                'ELEGIVEL_VR': 'sum',
                'VALOR_TOTAL_VR': 'sum',
                'DESCONTO_FUNCIONARIO': 'sum',
                'VALOR_LIQUIDO_EMPRESA': 'sum'
            }).round(2)
            
            dept_summary.columns = [
                'Total Funcionários',
                'Funcionários Elegíveis',
                'Valor Total VR',
                'Total Descontos',
                'Custo Líquido'
            ]
            
            st.dataframe(dept_summary, use_container_width=True)
            
            # Gráfico
            fig = create_department_summary_chart(df_calculado)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de departamento não disponíveis")
    
    with tab4:
        # Análises e gráficos
        st.subheader("Análises e Distribuições")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de valores
            fig = create_value_distribution_chart(df_calculado, 'VALOR_TOTAL_VR')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pizza de elegibilidade
            elegibility_data = df_calculado['ELEGIVEL_VR'].value_counts()
            fig = pd.DataFrame({
                'Status': ['Elegíveis', 'Não Elegíveis'],
                'Quantidade': [
                    elegibility_data.get(True, 0),
                    elegibility_data.get(False, 0)
                ]
            })
            
            import plotly.express as px
            fig_pie = px.pie(
                fig, 
                values='Quantidade', 
                names='Status',
                title="Distribuição de Elegibilidade"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Botão para próxima etapa
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📊 Gerar Relatórios", type="primary", use_container_width=True):
            st.session_state['current_page'] = 'reports'
            st.rerun()
