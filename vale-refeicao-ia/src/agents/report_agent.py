"""
Agente de Relatórios e Insights
Responsável por gerar relatórios executivos e análises
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from llama_index.core import Document
import json
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

from .base_agent import BaseAgent
from ..config.settings import settings

class ReportAgent(BaseAgent):
    """Agente especializado em geração de relatórios e insights"""
    
    def __init__(self):
        super().__init__(
            agent_name="report_agent",
            prompt_file="report_prompts.yaml",
            collection_name="report_insights"
        )
        
    def process(self, 
                calculation_data: Dict[str, Any],
                report_type: str = "executive",
                **kwargs) -> Dict[str, Any]:
        """
        Gera relatórios baseados nos dados de cálculo
        
        Args:
            calculation_data: Dados dos cálculos de VR
            report_type: Tipo de relatório (executive, detailed, anomaly)
            
        Returns:
            Dicionário com relatório gerado
        """
        self.log_action("Iniciando geração de relatório", {
            "report_type": report_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extrair dados
        df_calc = calculation_data['data']
        mes_ref = calculation_data['mes_referencia']
        regras = calculation_data.get('regras', {})
        
        # Gerar relatório baseado no tipo
        if report_type == "executive":
            report = self._generate_executive_report(df_calc, mes_ref, regras)
        elif report_type == "detailed":
            report = self._generate_detailed_report(df_calc, mes_ref, regras)
        elif report_type == "anomaly":
            report = self._generate_anomaly_report(df_calc, mes_ref, regras)
        else:
            report = self._generate_custom_report(df_calc, mes_ref, regras, kwargs)
        
        # Armazenar insights para aprendizado
        self._store_insights(report)
        
        self.log_action("Relatório gerado", {
            "report_type": report_type,
            "sections": len(report.get('sections', []))
        })
        
        return report
    
    def _generate_executive_report(self, 
                                  df: pd.DataFrame, 
                                  mes_ref: str, 
                                  regras: Dict) -> Dict[str, Any]:
        """Gera relatório executivo"""
        report = {
            'type': 'executive',
            'generated_at': datetime.now().isoformat(),
            'month_reference': mes_ref,
            'sections': []
        }
        
        # 1. Resumo Geral
        total_func = len(df)
        func_elegiveis = len(df[df['ELEGIVEL_VR'] == True])
        taxa_elegibilidade = (func_elegiveis / total_func * 100) if total_func > 0 else 0
        
        valor_total = df['VALOR_TOTAL_VR'].sum()
        desconto_total = df['DESCONTO_FUNCIONARIO'].sum()
        liquido_empresa = df['VALOR_LIQUIDO_EMPRESA'].sum()
        
        summary_section = {
            'title': 'Resumo Executivo',
            'metrics': {
                'total_funcionarios': total_func,
                'funcionarios_elegiveis': func_elegiveis,
                'taxa_elegibilidade': f"{taxa_elegibilidade:.1f}%",
                'valor_total_vr': f"R$ {valor_total:,.2f}",
                'desconto_funcionarios': f"R$ {desconto_total:,.2f}",
                'custo_liquido_empresa': f"R$ {liquido_empresa:,.2f}",
                'custo_medio_funcionario': f"R$ {liquido_empresa/func_elegiveis:,.2f}" if func_elegiveis > 0 else "R$ 0,00"
            }
        }
        
        # Adicionar insights com IA se disponível
        if self.llm:
            insights = self._generate_insights_with_ai(df, summary_section['metrics'])
            summary_section['insights'] = insights
        
        report['sections'].append(summary_section)
        
        # 2. Análise por Departamento
        if 'DEPARTAMENTO' in df.columns:
            dept_analysis = self._analyze_by_department(df)
            report['sections'].append(dept_analysis)
        
        # 3. Análise de Tendências
        trend_analysis = self._analyze_trends(df)
        report['sections'].append(trend_analysis)
        
        # 4. Recomendações
        recommendations = self._generate_recommendations(df, taxa_elegibilidade, liquido_empresa)
        report['sections'].append(recommendations)
        
        return report
    
    def _generate_detailed_report(self, 
                                 df: pd.DataFrame, 
                                 mes_ref: str, 
                                 regras: Dict) -> Dict[str, Any]:
        """Gera relatório detalhado"""
        report = {
            'type': 'detailed',
            'generated_at': datetime.now().isoformat(),
            'month_reference': mes_ref,
            'sections': []
        }
        
        # 1. Análise completa por funcionário
        employee_details = {
            'title': 'Detalhamento por Funcionário',
            'data': []
        }
        
        for _, row in df.iterrows():
            employee_details['data'].append({
                'matricula': row.get('MATRICULA', ''),
                'nome': row.get('NOME', ''),
                'departamento': row.get('DEPARTAMENTO', ''),
                'cargo': row.get('CARGO', ''),
                'elegivel': row.get('ELEGIVEL_VR', False),
                'valor_vr': row.get('VALOR_TOTAL_VR', 0),
                'desconto': row.get('DESCONTO_FUNCIONARIO', 0),
                'liquido_empresa': row.get('VALOR_LIQUIDO_EMPRESA', 0),
                'observacoes': row.get('OBSERVACOES', '')
            })
        
        report['sections'].append(employee_details)
        
        # 2. Estatísticas detalhadas
        stats = self._calculate_detailed_statistics(df)
        report['sections'].append(stats)
        
        return report
    
    def _generate_anomaly_report(self, 
                                df: pd.DataFrame, 
                                mes_ref: str, 
                                regras: Dict) -> Dict[str, Any]:
        """Gera relatório de anomalias"""
        report = {
            'type': 'anomaly',
            'generated_at': datetime.now().isoformat(),
            'month_reference': mes_ref,
            'sections': []
        }
        
        anomalies = {
            'title': 'Anomalias Detectadas',
            'items': []
        }
        
        # 1. Valores atípicos
        if 'VALOR_TOTAL_VR' in df.columns:
            q1 = df['VALOR_TOTAL_VR'].quantile(0.25)
            q3 = df['VALOR_TOTAL_VR'].quantile(0.75)
            iqr = q3 - q1
            
            outliers_high = df[df['VALOR_TOTAL_VR'] > (q3 + 1.5 * iqr)]
            outliers_low = df[df['VALOR_TOTAL_VR'] < (q1 - 1.5 * iqr)]
            
            if len(outliers_high) > 0:
                anomalies['items'].append({
                    'type': 'valor_alto',
                    'description': f'{len(outliers_high)} funcionários com valores muito acima da média',
                    'details': outliers_high[['MATRICULA', 'NOME', 'VALOR_TOTAL_VR']].to_dict('records')
                })
            
            if len(outliers_low) > 0:
                anomalies['items'].append({
                    'type': 'valor_baixo',
                    'description': f'{len(outliers_low)} funcionários com valores muito abaixo da média',
                    'details': outliers_low[['MATRICULA', 'NOME', 'VALOR_TOTAL_VR']].to_dict('records')
                })
        
        # 2. Inconsistências
        inconsistencies = self._detect_inconsistencies(df)
        if inconsistencies:
            anomalies['items'].extend(inconsistencies)
        
        report['sections'].append(anomalies)
        
        return report
    
    def _analyze_by_department(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análise por departamento"""
        dept_summary = df.groupby('DEPARTAMENTO').agg({
            'MATRICULA': 'count',
            'ELEGIVEL_VR': lambda x: (x == True).sum(),
            'VALOR_TOTAL_VR': 'sum',
            'DESCONTO_FUNCIONARIO': 'sum',
            'VALOR_LIQUIDO_EMPRESA': 'sum'
        }).round(2)
        
        dept_summary['taxa_elegibilidade'] = (
            dept_summary['ELEGIVEL_VR'] / dept_summary['MATRICULA'] * 100
        ).round(1)
        
        dept_summary['custo_medio'] = (
            dept_summary['VALOR_LIQUIDO_EMPRESA'] / dept_summary['ELEGIVEL_VR']
        ).round(2)
        
        return {
            'title': 'Análise por Departamento',
            'data': dept_summary.to_dict('index'),
            'top_cost_departments': dept_summary.nlargest(3, 'VALOR_LIQUIDO_EMPRESA').index.tolist(),
            'lowest_eligibility_rate': dept_summary.nsmallest(3, 'taxa_elegibilidade').index.tolist()
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análise de tendências"""
        trends = {
            'title': 'Análise de Tendências',
            'observations': []
        }
        
        # Buscar dados históricos se disponível
        if self.query_engine:
            try:
                historical_data = self.query("Quais foram os valores de VR dos últimos 3 meses?")
                # Processar dados históricos
                # ... implementação específica
            except:
                pass
        
        # Análises básicas
        avg_value = df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR'].mean()
        trends['observations'].append(f"Valor médio de VR: R$ {avg_value:.2f}")
        
        if 'DEPARTAMENTO' in df.columns:
            dept_variation = df.groupby('DEPARTAMENTO')['VALOR_TOTAL_VR'].std().mean()
            trends['observations'].append(
                f"Variação média entre departamentos: R$ {dept_variation:.2f}"
            )
        
        return trends
    
    def _generate_recommendations(self, 
                                 df: pd.DataFrame, 
                                 taxa_elegibilidade: float,
                                 custo_total: float) -> Dict[str, Any]:
        """Gera recomendações baseadas na análise"""
        recommendations = {
            'title': 'Recomendações',
            'items': []
        }
        
        # Recomendações baseadas em regras
        if taxa_elegibilidade < 80:
            recommendations['items'].append({
                'priority': 'alta',
                'category': 'elegibilidade',
                'recommendation': 'Revisar critérios de elegibilidade',
                'reason': f'Taxa de elegibilidade está em {taxa_elegibilidade:.1f}%, abaixo do ideal de 80%',
                'impact': 'Pode aumentar satisfação dos funcionários'
            })
        
        custo_por_func = custo_total / len(df[df['ELEGIVEL_VR'] == True]) if len(df[df['ELEGIVEL_VR'] == True]) > 0 else 0
        if custo_por_func > 700:
            recommendations['items'].append({
                'priority': 'média',
                'category': 'custo',
                'recommendation': 'Avaliar possibilidade de negociar valores com fornecedores',
                'reason': f'Custo médio por funcionário (R$ {custo_por_func:.2f}) está elevado',
                'impact': 'Redução de até 15% nos custos'
            })
        
        # Recomendações com IA se disponível
        if self.llm:
            ai_recommendations = self._get_ai_recommendations(df)
            recommendations['items'].extend(ai_recommendations)
        
        return recommendations
    
    def _generate_insights_with_ai(self, 
                                  df: pd.DataFrame, 
                                  metrics: Dict[str, Any]) -> List[str]:
        """Gera insights usando IA"""
        prompt = self.get_system_prompt('generate_insights',
                                      metrics=json.dumps(metrics, ensure_ascii=False),
                                      data_summary=self._get_data_summary(df))
        
        try:
            response = self.llm.complete(prompt)
            # Parse insights da resposta
            insights = response.text.split('\n')
            return [insight.strip() for insight in insights if insight.strip()]
        except:
            return ["Análise de IA não disponível"]
    
    def _get_data_summary(self, df: pd.DataFrame) -> str:
        """Gera resumo dos dados para contexto da IA"""
        summary = f"""
        Total de registros: {len(df)}
        Colunas disponíveis: {', '.join(df.columns)}
        Funcionários elegíveis: {len(df[df.get('ELEGIVEL_VR', False) == True])}
        Valor total: R$ {df.get('VALOR_TOTAL_VR', pd.Series()).sum():,.2f}
        """
        return summary
    
    def _calculate_detailed_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula estatísticas detalhadas"""
        stats = {
            'title': 'Estatísticas Detalhadas',
            'metrics': {}
        }
        
        if 'VALOR_TOTAL_VR' in df.columns:
            valores = df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR']
            stats['metrics']['valor_vr'] = {
                'media': valores.mean(),
                'mediana': valores.median(),
                'desvio_padrao': valores.std(),
                'minimo': valores.min(),
                'maximo': valores.max(),
                'quartil_25': valores.quantile(0.25),
                'quartil_75': valores.quantile(0.75)
            }
        
        return stats
    
    def _detect_inconsistencies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta inconsistências nos dados"""
        inconsistencies = []
        
        # Verificar valores negativos
        if 'VALOR_TOTAL_VR' in df.columns:
            negative_values = df[df['VALOR_TOTAL_VR'] < 0]
            if len(negative_values) > 0:
                inconsistencies.append({
                    'type': 'valores_negativos',
                    'description': f'{len(negative_values)} registros com valores negativos',
                    'severity': 'alta'
                })
        
        # Verificar dados faltantes em campos críticos
        critical_fields = ['MATRICULA', 'NOME']
        for field in critical_fields:
            if field in df.columns:
                missing = df[field].isna().sum()
                if missing > 0:
                    inconsistencies.append({
                        'type': 'dados_faltantes',
                        'description': f'{missing} registros sem {field}',
                        'severity': 'alta'
                    })
        
        return inconsistencies
    
    def _get_ai_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Obtém recomendações usando IA"""
        prompt = self.get_system_prompt('generate_recommendations',
                                      data_summary=self._get_data_summary(df))
        
        try:
            response = self.llm.complete(prompt)
            # Parse recomendações
            recommendations = []
            # ... implementação de parsing
            return recommendations
        except:
            return []
    
    def _store_insights(self, report: Dict[str, Any]):
        """Armazena insights para aprendizado futuro"""
        if self.index:
            insight_doc = Document(
                text=json.dumps(report, ensure_ascii=False, default=str),
                metadata={
                    'type': 'report',
                    'report_type': report.get('type'),
                    'month': report.get('month_reference'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            self.add_documents([insight_doc])
    
    def export_to_pdf(self, report: Dict[str, Any]) -> BytesIO:
        """Exporta relatório para PDF"""
        # Implementação simplificada - você pode usar reportlab ou weasyprint
        pdf_buffer = BytesIO()
        
        # TODO: Implementar geração de PDF real
        # Por enquanto, retorna buffer vazio
        
        pdf_buffer.seek(0)
        return pdf_buffer
    
    def generate_visualizations(self, df: pd.DataFrame) -> Dict[str, BytesIO]:
        """Gera visualizações para o relatório"""
        visualizations = {}
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Distribuição de valores
        if 'VALOR_TOTAL_VR' in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR'].hist(bins=30, ax=ax)
            ax.set_title('Distribuição de Valores de Vale Refeição')
            ax.set_xlabel('Valor (R$)')
            ax.set_ylabel('Frequência')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations['distribuicao_valores'] = buffer
            plt.close()
        
        # 2. Por departamento
        if 'DEPARTAMENTO' in df.columns and 'VALOR_LIQUIDO_EMPRESA' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 8))
            dept_summary = df.groupby('DEPARTAMENTO')['VALOR_LIQUIDO_EMPRESA'].sum().sort_values(ascending=True)
            dept_summary.plot(kind='barh', ax=ax)
            ax.set_title('Custo de Vale Refeição por Departamento')
            ax.set_xlabel('Custo Total (R$)')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations['custo_departamento'] = buffer
            plt.close()
        
        return visualizations
