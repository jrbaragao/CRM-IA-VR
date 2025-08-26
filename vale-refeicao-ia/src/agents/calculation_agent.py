"""
Agente de Cálculo de Vale Refeição
Responsável por calcular valores baseado em regras de negócio
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from llama_index import Document
import json
import calendar

from .base_agent import BaseAgent
from ..config.settings import settings
from ..data.models import CalculoValeRefeicao, FuncionarioVR

class CalculationAgent(BaseAgent):
    """Agente especializado em cálculos de vale refeição"""
    
    def __init__(self):
        super().__init__(
            agent_name="calculation_agent",
            prompt_file="calculation_prompts.yaml",
            collection_name="calculation_rules"
        )
        self.calculation_rules = self._load_calculation_rules()
        
    def process(self, 
                funcionarios_df: pd.DataFrame,
                mes_referencia: str,
                regras_customizadas: Dict[str, Any] = None,
                **kwargs) -> pd.DataFrame:
        """
        Calcula vale refeição para funcionários
        
        Args:
            funcionarios_df: DataFrame com dados dos funcionários
            mes_referencia: Mês de referência (YYYY-MM)
            regras_customizadas: Regras específicas do cliente
            
        Returns:
            DataFrame com cálculos
        """
        self.log_action("Iniciando cálculos", {
            "funcionarios": len(funcionarios_df),
            "mes_referencia": mes_referencia
        })
        
        # 1. Preparar dados
        df = self._prepare_data(funcionarios_df)
        
        # 2. Calcular dias úteis
        dias_uteis = self._calculate_working_days(mes_referencia)
        
        # 3. Aplicar regras de elegibilidade
        df = self._apply_eligibility_rules(df, regras_customizadas)
        
        # 4. Calcular valores
        df = self._calculate_values(df, dias_uteis, regras_customizadas)
        
        # 5. Aplicar descontos e ajustes
        df = self._apply_discounts_and_adjustments(df)
        
        # 6. Validar cálculos
        validation_results = self._validate_calculations(df)
        
        # 7. Gerar resumo
        summary = self._generate_summary(df, validation_results)
        
        # 8. Armazenar aprendizados
        self._store_calculation_learning(df, summary)
        
        self.log_action("Cálculos concluídos", summary)
        
        return df
    
    def _load_calculation_rules(self) -> Dict[str, Any]:
        """Carrega regras de cálculo padrão e customizadas"""
        default_rules = {
            'valor_dia_util': settings.valor_dia_util,
            'desconto_funcionario_pct': settings.desconto_funcionario_pct,
            'dias_uteis_padrao': settings.dias_uteis_mes_padrao,
            'categorias_elegiveis': ['CLT', 'EFETIVO', 'CONTRATADO'],
            'categorias_nao_elegiveis': ['ESTAGIARIO', 'TERCEIRIZADO', 'AFASTADO'],
            'desconto_maximo': 500.00,
            'valor_minimo': 100.00,
            'valor_maximo': 1500.00
        }
        
        # Carregar regras customizadas do índice se disponível
        if self.query_engine:
            try:
                response = self.query("Quais são as regras de cálculo customizadas mais recentes?")
                # Parse e merge com regras padrão
                # ... implementação específica
            except:
                pass
        
        return default_rules
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara dados para cálculo"""
        df = df.copy()
        
        # Garantir colunas necessárias
        required_columns = ['MATRICULA', 'NOME', 'CARGO', 'DEPARTAMENTO']
        for col in required_columns:
            if col not in df.columns:
                df[col] = np.nan
        
        # Adicionar colunas de cálculo
        calc_columns = [
            'ELEGIVEL_VR',
            'DIAS_TRABALHADOS',
            'DIAS_DESCONTO',
            'VALOR_TOTAL_VR',
            'DESCONTO_FUNCIONARIO',
            'VALOR_LIQUIDO_EMPRESA',
            'OBSERVACOES'
        ]
        
        for col in calc_columns:
            df[col] = np.nan
            
        return df
    
    def _calculate_working_days(self, mes_referencia: str) -> int:
        """Calcula dias úteis do mês"""
        try:
            # Parse mês referência
            year, month = map(int, mes_referencia.split('-'))
            
            # Obter primeiro e último dia do mês
            first_day = date(year, month, 1)
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            # Contar dias úteis (segunda a sexta)
            working_days = 0
            current_day = first_day
            
            while current_day <= last_day:
                if current_day.weekday() < 5:  # 0-4 são segunda a sexta
                    working_days += 1
                current_day += relativedelta(days=1)
            
            # Considerar feriados se disponível
            # TODO: Integrar com API de feriados
            
            return working_days
            
        except Exception as e:
            self.log_action("Erro ao calcular dias úteis", {"error": str(e)})
            return self.calculation_rules['dias_uteis_padrao']
    
    def _apply_eligibility_rules(self, 
                                df: pd.DataFrame, 
                                regras_customizadas: Dict[str, Any] = None) -> pd.DataFrame:
        """Aplica regras de elegibilidade"""
        # Inicializar todos como elegíveis
        df['ELEGIVEL_VR'] = True
        df['OBSERVACOES'] = ''
        
        # Regras baseadas em categoria/tipo de contrato
        if 'TIPO_CONTRATO' in df.columns:
            categorias_nao_elegiveis = (regras_customizadas or {}).get(
                'categorias_nao_elegiveis',
                self.calculation_rules['categorias_nao_elegiveis']
            )
            
            mask_nao_elegivel = df['TIPO_CONTRATO'].str.upper().isin(
                [cat.upper() for cat in categorias_nao_elegiveis]
            )
            df.loc[mask_nao_elegivel, 'ELEGIVEL_VR'] = False
            df.loc[mask_nao_elegivel, 'OBSERVACOES'] = 'Tipo de contrato não elegível'
        
        # Regras baseadas em afastamento
        if 'STATUS' in df.columns:
            mask_afastado = df['STATUS'].str.upper().isin(['AFASTADO', 'LICENCA', 'FERIAS'])
            df.loc[mask_afastado, 'ELEGIVEL_VR'] = False
            df.loc[mask_afastado, 'OBSERVACOES'] = df.loc[mask_afastado, 'OBSERVACOES'] + '; Funcionário afastado'
        
        # Regras baseadas em admissão/demissão
        if 'DATA_ADMISSAO' in df.columns:
            # TODO: Implementar cálculo proporcional para admitidos no mês
            pass
            
        # Usar IA para casos complexos
        if self.llm:
            casos_complexos = df[df['OBSERVACOES'].str.contains('revisar', na=False)]
            if len(casos_complexos) > 0:
                for idx, row in casos_complexos.iterrows():
                    elegibilidade = self._check_eligibility_with_ai(row)
                    df.loc[idx, 'ELEGIVEL_VR'] = elegibilidade['elegivel']
                    df.loc[idx, 'OBSERVACOES'] = elegibilidade['motivo']
        
        return df
    
    def _calculate_values(self, 
                         df: pd.DataFrame, 
                         dias_uteis: int,
                         regras_customizadas: Dict[str, Any] = None) -> pd.DataFrame:
        """Calcula valores de vale refeição"""
        # Obter valores das regras
        valor_dia = (regras_customizadas or {}).get(
            'valor_dia_util',
            self.calculation_rules['valor_dia_util']
        )
        
        desconto_pct = (regras_customizadas or {}).get(
            'desconto_funcionario_pct',
            self.calculation_rules['desconto_funcionario_pct']
        )
        
        # Calcular para funcionários elegíveis
        mask_elegivel = df['ELEGIVEL_VR'] == True
        
        # Dias trabalhados (por padrão, todos os dias úteis)
        df.loc[mask_elegivel, 'DIAS_TRABALHADOS'] = dias_uteis
        
        # Ajustar dias para admitidos/demitidos no mês
        if 'DATA_ADMISSAO' in df.columns:
            # TODO: Calcular dias proporcionais
            pass
        
        # Valor total
        df.loc[mask_elegivel, 'VALOR_TOTAL_VR'] = (
            df.loc[mask_elegivel, 'DIAS_TRABALHADOS'] * valor_dia
        )
        
        # Desconto do funcionário
        df.loc[mask_elegivel, 'DESCONTO_FUNCIONARIO'] = (
            df.loc[mask_elegivel, 'VALOR_TOTAL_VR'] * desconto_pct
        )
        
        # Aplicar limite de desconto
        desconto_maximo = self.calculation_rules['desconto_maximo']
        mask_desconto_alto = df['DESCONTO_FUNCIONARIO'] > desconto_maximo
        df.loc[mask_desconto_alto, 'DESCONTO_FUNCIONARIO'] = desconto_maximo
        
        # Valor líquido empresa
        df.loc[mask_elegivel, 'VALOR_LIQUIDO_EMPRESA'] = (
            df.loc[mask_elegivel, 'VALOR_TOTAL_VR'] - 
            df.loc[mask_elegivel, 'DESCONTO_FUNCIONARIO']
        )
        
        # Zerar valores para não elegíveis
        mask_nao_elegivel = df['ELEGIVEL_VR'] == False
        df.loc[mask_nao_elegivel, ['DIAS_TRABALHADOS', 'VALOR_TOTAL_VR', 
                                   'DESCONTO_FUNCIONARIO', 'VALOR_LIQUIDO_EMPRESA']] = 0
        
        return df
    
    def _apply_discounts_and_adjustments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica descontos e ajustes especiais"""
        # Verificar faltas se disponível
        if 'FALTAS' in df.columns:
            mask_com_faltas = (df['FALTAS'] > 0) & (df['ELEGIVEL_VR'] == True)
            
            # Descontar dias de falta
            df.loc[mask_com_faltas, 'DIAS_DESCONTO'] = df.loc[mask_com_faltas, 'FALTAS']
            
            # Recalcular valores
            valor_dia = self.calculation_rules['valor_dia_util']
            df.loc[mask_com_faltas, 'VALOR_TOTAL_VR'] = (
                df.loc[mask_com_faltas, 'VALOR_TOTAL_VR'] - 
                (df.loc[mask_com_faltas, 'DIAS_DESCONTO'] * valor_dia)
            )
            
            # Recalcular desconto
            desconto_pct = self.calculation_rules['desconto_funcionario_pct']
            df.loc[mask_com_faltas, 'DESCONTO_FUNCIONARIO'] = (
                df.loc[mask_com_faltas, 'VALOR_TOTAL_VR'] * desconto_pct
            )
            
            # Recalcular líquido
            df.loc[mask_com_faltas, 'VALOR_LIQUIDO_EMPRESA'] = (
                df.loc[mask_com_faltas, 'VALOR_TOTAL_VR'] - 
                df.loc[mask_com_faltas, 'DESCONTO_FUNCIONARIO']
            )
            
            # Adicionar observação
            df.loc[mask_com_faltas, 'OBSERVACOES'] = (
                df.loc[mask_com_faltas, 'OBSERVACOES'] + 
                '; Descontado ' + df.loc[mask_com_faltas, 'DIAS_DESCONTO'].astype(str) + ' dia(s) de falta'
            )
        
        # Aplicar limites mínimos e máximos
        valor_minimo = self.calculation_rules['valor_minimo']
        valor_maximo = self.calculation_rules['valor_maximo']
        
        mask_abaixo_minimo = (df['VALOR_TOTAL_VR'] < valor_minimo) & (df['VALOR_TOTAL_VR'] > 0)
        mask_acima_maximo = df['VALOR_TOTAL_VR'] > valor_maximo
        
        df.loc[mask_abaixo_minimo, 'VALOR_TOTAL_VR'] = valor_minimo
        df.loc[mask_acima_maximo, 'VALOR_TOTAL_VR'] = valor_maximo
        
        return df
    
    def _validate_calculations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida os cálculos realizados"""
        validation = {
            'total_funcionarios': len(df),
            'funcionarios_elegiveis': len(df[df['ELEGIVEL_VR'] == True]),
            'valor_total_vr': df['VALOR_TOTAL_VR'].sum(),
            'total_desconto_funcionario': df['DESCONTO_FUNCIONARIO'].sum(),
            'total_liquido_empresa': df['VALOR_LIQUIDO_EMPRESA'].sum(),
            'alertas': []
        }
        
        # Verificar valores negativos
        if (df['VALOR_TOTAL_VR'] < 0).any():
            validation['alertas'].append('Valores negativos encontrados')
        
        # Verificar valores muito altos
        media_vr = df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR'].mean()
        outliers = df[df['VALOR_TOTAL_VR'] > media_vr * 3]
        if len(outliers) > 0:
            validation['alertas'].append(f'{len(outliers)} funcionários com valores muito acima da média')
        
        # Verificar consistência
        calc_total = (df['VALOR_TOTAL_VR'] - df['DESCONTO_FUNCIONARIO']).sum()
        diff = abs(calc_total - validation['total_liquido_empresa'])
        if diff > 0.01:
            validation['alertas'].append('Inconsistência nos cálculos detectada')
        
        return validation
    
    def _generate_summary(self, 
                         df: pd.DataFrame, 
                         validation: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo dos cálculos"""
        summary = {
            'mes_referencia': datetime.now().strftime('%Y-%m'),
            'total_funcionarios': validation['total_funcionarios'],
            'funcionarios_elegiveis': validation['funcionarios_elegiveis'],
            'funcionarios_nao_elegiveis': validation['total_funcionarios'] - validation['funcionarios_elegiveis'],
            'valor_total_vr': round(validation['valor_total_vr'], 2),
            'total_desconto_funcionario': round(validation['total_desconto_funcionario'], 2),
            'total_liquido_empresa': round(validation['total_liquido_empresa'], 2),
            'custo_medio_por_funcionario': round(
                validation['total_liquido_empresa'] / validation['funcionarios_elegiveis']
                if validation['funcionarios_elegiveis'] > 0 else 0, 2
            ),
            'alertas': validation['alertas']
        }
        
        # Estatísticas por departamento se disponível
        if 'DEPARTAMENTO' in df.columns:
            summary['por_departamento'] = df.groupby('DEPARTAMENTO').agg({
                'ELEGIVEL_VR': 'sum',
                'VALOR_TOTAL_VR': 'sum',
                'VALOR_LIQUIDO_EMPRESA': 'sum'
            }).to_dict()
        
        return summary
    
    def _check_eligibility_with_ai(self, funcionario: pd.Series) -> Dict[str, Any]:
        """Usa IA para verificar elegibilidade em casos complexos"""
        prompt = self.get_system_prompt('eligibility_check',
                                      funcionario=funcionario.to_dict())
        
        if self.llm:
            response = self.llm.complete(prompt)
            # Parse da resposta
            try:
                result = json.loads(response.text)
                return result
            except:
                return {
                    'elegivel': True,
                    'motivo': 'Análise automática não conclusiva'
                }
        
        return {'elegivel': True, 'motivo': 'IA não disponível'}
    
    def _store_calculation_learning(self, 
                                   df: pd.DataFrame, 
                                   summary: Dict[str, Any]):
        """Armazena aprendizados dos cálculos"""
        if self.index:
            # Criar documento com resultados
            learning_doc = Document(
                text=json.dumps({
                    'summary': summary,
                    'calculation_date': datetime.now().isoformat(),
                    'rules_applied': self.calculation_rules,
                    'statistics': {
                        'avg_vr_value': float(df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR'].mean()),
                        'std_vr_value': float(df[df['VALOR_TOTAL_VR'] > 0]['VALOR_TOTAL_VR'].std()),
                        'eligibility_rate': summary['funcionarios_elegiveis'] / summary['total_funcionarios']
                    }
                }, default=str),
                metadata={
                    'type': 'calculation_result',
                    'timestamp': datetime.now().isoformat()
                }
            )
            self.add_documents([learning_doc])
    
    def get_calculation_report(self, df: pd.DataFrame) -> str:
        """Gera relatório textual dos cálculos"""
        if self.llm:
            prompt = self.get_system_prompt('generate_report',
                                          data=df.to_dict(),
                                          summary=self._generate_summary(df, {}))
            response = self.llm.complete(prompt)
            return response.text
        
        return "Relatório de cálculo não disponível"
