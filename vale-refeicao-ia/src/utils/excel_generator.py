"""
Utilitário para geração de planilhas Excel pelos agentes autônomos
"""

import pandas as pd
from io import BytesIO
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import streamlit as st
import json
import numpy as np

class ExcelGenerator:
    """Classe para geração de planilhas Excel pelos agentes"""
    
    def __init__(self):
        self.output_buffer = BytesIO()
        
    def create_excel_from_data(self, 
                              data: Union[pd.DataFrame, Dict[str, pd.DataFrame]], 
                              filename: str = None,
                              metadata: Dict[str, Any] = None) -> BytesIO:
        """
        Cria planilha Excel a partir de dados
        
        Args:
            data: DataFrame único ou dicionário de DataFrames (uma aba cada)
            filename: Nome do arquivo (opcional)
            metadata: Metadados para incluir na planilha
            
        Returns:
            BytesIO: Buffer com o arquivo Excel
        """
        
        if filename is None:
            filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
        output = BytesIO()
        
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                
                # Se é um DataFrame único
                if isinstance(data, pd.DataFrame):
                    self._write_single_dataframe(writer, data, metadata)
                
                # Se é um dicionário de DataFrames
                elif isinstance(data, dict):
                    self._write_multiple_dataframes(writer, data, metadata)
                
                else:
                    raise ValueError("Dados devem ser DataFrame ou dicionário de DataFrames")
                
                # Adicionar aba de metadados se fornecidos
                if metadata:
                    self._add_metadata_sheet(writer, metadata, filename)
                    
        except Exception as e:
            st.error(f"❌ Erro ao gerar Excel: {str(e)}")
            return None
            
        output.seek(0)
        return output
    
    def _write_single_dataframe(self, writer, df: pd.DataFrame, metadata: Dict[str, Any] = None):
        """Escreve um único DataFrame"""
        sheet_name = metadata.get('sheet_name', 'Dados') if metadata else 'Dados'
        
        # Limpar nome da aba
        sheet_name = self._clean_sheet_name(sheet_name)
        
        # Escrever dados
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Formatar planilha
        self._format_worksheet(writer, sheet_name, df)
    
    def _write_multiple_dataframes(self, writer, data_dict: Dict[str, pd.DataFrame], metadata: Dict[str, Any] = None):
        """Escreve múltiplos DataFrames em abas separadas"""
        
        for sheet_name, df in data_dict.items():
            # Limpar nome da aba
            clean_name = self._clean_sheet_name(sheet_name)
            
            # Tratamento especial para FORMATO_PADRAO_VR
            if sheet_name == 'FORMATO_PADRAO_VR' and 'TOTAL' in df.columns:
                # Calcular soma total da coluna TOTAL
                soma_total = df['TOTAL'].sum()
                
                # Escrever dados originais sem cabeçalhos (a formatação vai adicionar tudo)
                df.to_excel(writer, sheet_name=clean_name, index=False, header=False, startrow=3)
                
                # Formatar planilha com formatação especial (adiciona total e cabeçalhos)
                self._format_worksheet_with_total(writer, clean_name, df, soma_total)
            else:
                # Escrever dados normalmente
                df.to_excel(writer, sheet_name=clean_name, index=False)
                
                # Formatar planilha
                self._format_worksheet(writer, clean_name, df)
    
    def _add_metadata_sheet(self, writer, metadata: Dict[str, Any], filename: str):
        """Adiciona aba com metadados"""
        
        metadata_data = {
            'Propriedade': [],
            'Valor': []
        }
        
        # Informações básicas
        metadata_data['Propriedade'].extend([
            'Nome do Arquivo',
            'Data de Geração',
            'Gerado por',
            'Sistema'
        ])
        
        metadata_data['Valor'].extend([
            filename,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Agente Autônomo IA',
            'Sistema de Análise de Dados'
        ])
        
        # Adicionar metadados customizados
        for key, value in metadata.items():
            if key not in ['sheet_name']:
                metadata_data['Propriedade'].append(str(key))
                metadata_data['Valor'].append(str(value))
        
        # Criar DataFrame de metadados
        df_metadata = pd.DataFrame(metadata_data)
        
        # Escrever na aba
        df_metadata.to_excel(writer, sheet_name='Informações', index=False)
        
        # Formatar aba de metadados
        self._format_worksheet(writer, 'Informações', df_metadata)
    
    def _format_worksheet(self, writer, sheet_name: str, df: pd.DataFrame):
        """Aplica formatação básica à planilha"""
        
        try:
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Formato para valores monetários (padrão brasileiro)
            money_format = workbook.add_format({
                'num_format': '#.##0,00'  # Formato brasileiro: ponto para milhares, vírgula para decimais
            })
            
            # Formatar cabeçalhos
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Formatar dados com formato monetário quando aplicável
            for row_idx in range(len(df)):
                for col_idx, col in enumerate(df.columns):
                    value = df.iloc[row_idx, col_idx]
                    # Aplicar formato monetário para colunas de valores
                    if col in ['TOTAL', 'Custo empresa', 'Desconto profissional', 'VALOR DIÁRIO VR', 'VALOR_TOTAL_VR', 'VALOR_DIARIO', 'DESCONTO_FUNCIONARIO', 'VALOR_LIQUIDO_EMPRESA']:
                        if pd.notna(value) and isinstance(value, (int, float)):
                            worksheet.write(row_idx + 1, col_idx, value, money_format)
                        else:
                            worksheet.write(row_idx + 1, col_idx, value)
                    else:
                        worksheet.write(row_idx + 1, col_idx, value)
            
            # Auto-ajustar largura das colunas
            for i, col in enumerate(df.columns):
                # Calcular largura baseada no conteúdo
                max_length = max(
                    df[col].astype(str).map(len).max(),  # Maior valor na coluna
                    len(str(col))  # Nome da coluna
                )
                
                # Limitar largura máxima
                max_length = min(max_length + 2, 50)
                worksheet.set_column(i, i, max_length)
                
        except Exception as e:
            # Se formatação falhar, continua sem formatação
            pass
    
    def _format_worksheet_with_total(self, writer, sheet_name: str, df: pd.DataFrame, soma_total: float):
        """Aplica formatação especial para planilha com linha de totalização"""
        
        try:
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Formato para linha de total (padrão brasileiro)
            total_format = workbook.add_format({
                'bold': True,
                'num_format': '#.##0,00',  # Formato brasileiro: ponto para milhares, vírgula para decimais
                'fg_color': '#FFE699',
                'border': 2,
                'font_size': 12
            })
            
            # Formato para valores monetários (padrão brasileiro)
            money_format = workbook.add_format({
                'num_format': '#.##0,00'  # Formato brasileiro: ponto para milhares, vírgula para decimais
            })
            
            # Formatar primeira linha (total) - linha 0
            for col_idx, col in enumerate(df.columns):
                if col == 'TOTAL':
                    worksheet.write(0, col_idx, soma_total, total_format)
                else:
                    worksheet.write_string(0, col_idx, '', workbook.add_format({'border': 0}))
            
            # Linha vazia (linha 1) - já está vazia
            
            # Formatar cabeçalhos (linha 2)
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(2, col_num, value, header_format)
            
            # Formatar dados (a partir da linha 3) - os dados já foram escritos a partir da linha 3
            for row_idx in range(len(df)):
                for col_idx, col in enumerate(df.columns):
                    value = df.iloc[row_idx, col_idx]
                    if col in ['TOTAL', 'Custo empresa', 'Desconto profissional', 'VALOR DIÁRIO VR']:
                        if pd.notna(value) and isinstance(value, (int, float)):
                            worksheet.write(row_idx + 3, col_idx, value, money_format)
                        else:
                            worksheet.write(row_idx + 3, col_idx, value)
                    else:
                        worksheet.write(row_idx + 3, col_idx, value)
            
            # Auto-ajustar largura das colunas
            for i, col in enumerate(df.columns):
                if col == 'OBS GERAL':
                    worksheet.set_column(i, i, 60)  # Coluna OBS GERAL mais larga
                elif col == 'Sindicato do Colaborador':
                    worksheet.set_column(i, i, 30)  # Coluna Sindicato média
                else:
                    # Calcular largura baseada no conteúdo
                    max_length = max(
                        df[col].astype(str).map(len).max(),  # Maior valor na coluna
                        len(str(col))  # Nome da coluna
                    )
                    max_length = min(max_length + 2, 20)
                    worksheet.set_column(i, i, max_length)
                    
        except Exception as e:
            # Se formatação falhar, continua sem formatação
            pass
    
    def _clean_sheet_name(self, name: str) -> str:
        """Limpa nome da aba para Excel"""
        
        # Caracteres não permitidos no Excel
        invalid_chars = ['[', ']', '*', '?', ':', '/', '\\']
        
        clean_name = str(name)
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        
        # Limitar tamanho (Excel permite até 31 caracteres)
        clean_name = clean_name[:31]
        
        return clean_name
    
    @staticmethod
    def dataframe_to_excel_download(df: pd.DataFrame, 
                                   filename: str = None,
                                   metadata: Dict[str, Any] = None) -> BytesIO:
        """
        Método estático para conversão rápida DataFrame -> Excel
        
        Args:
            df: DataFrame para converter
            filename: Nome do arquivo
            metadata: Metadados opcionais
            
        Returns:
            BytesIO: Buffer com arquivo Excel
        """
        
        generator = ExcelGenerator()
        return generator.create_excel_from_data(df, filename, metadata)
    
    @staticmethod
    def query_result_to_excel(query_result: Dict[str, Any], 
                             question: str = "Consulta") -> BytesIO:
        """
        Converte resultado de consulta SQL em Excel
        
        Args:
            query_result: Resultado da consulta (deve ter 'data' com DataFrame)
            question: Pergunta original da consulta
            
        Returns:
            BytesIO: Buffer com arquivo Excel
        """
        
        if not query_result or 'data' not in query_result:
            return None
            
        df = query_result['data']
        
        metadata = {
            'Consulta Original': question,
            'Total de Registros': len(df),
            'Colunas': ', '.join(df.columns.tolist()),
            'Tipo': 'Resultado de Consulta SQL'
        }
        
        filename = f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        generator = ExcelGenerator()
        return generator.create_excel_from_data(df, filename, metadata)


def create_excel_tool_for_agent():
    """
    Cria uma ferramenta que agentes autônomos podem usar para gerar Excel
    
    Returns:
        Dict: Definição da ferramenta para uso pelos agentes
    """
    
    return {
        'name': 'excel_export',
        'description': 'Gera planilha Excel a partir de dados ou resultados de consultas',
        'parameters': {
            'data_source': 'DataFrame ou resultado de consulta SQL',
            'filename': 'Nome do arquivo (opcional)',
            'metadata': 'Informações adicionais para incluir (opcional)'
        },
        'usage_example': 'excel_export(data=df_resultado, filename="relatorio_vendas.xlsx", metadata={"periodo": "2024-01"})'
    }


def execute_excel_export_tool(data: Any, 
                             filename: str = None, 
                             metadata: Dict[str, Any] = None,
                             container = None) -> bool:
    """
    Executa a ferramenta de exportação Excel para agentes
    
    Args:
        data: Dados para exportar (DataFrame, dict de DataFrames, ou resultado de query)
        filename: Nome do arquivo
        metadata: Metadados adicionais
        container: Container Streamlit para exibir resultado
        
    Returns:
        bool: True se sucesso, False se erro
    """
    
    try:
        # Se container não fornecido, usar st diretamente
        if container is None:
            display = st
        else:
            display = container
            
        # Determinar tipo de dados
        if isinstance(data, dict) and 'data' in data:
            # Resultado de consulta SQL
            df = data['data']
            if metadata is None:
                metadata = {}
            metadata.update({
                'Tipo': 'Resultado de Consulta',
                'Registros': len(df)
            })
        elif isinstance(data, pd.DataFrame):
            # DataFrame direto
            df = data
        elif isinstance(data, dict):
            # Múltiplos DataFrames
            df = data
        else:
            display.error("❌ Tipo de dados não suportado para exportação Excel")
            return False
        
        # Gerar Excel
        generator = ExcelGenerator()
        excel_buffer = generator.create_excel_from_data(df, filename, metadata)
        
        if excel_buffer is None:
            return False
            
        # Determinar nome do arquivo
        if filename is None:
            filename = f"relatorio_agente_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        elif not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Exibir botão de download
        display.success("✅ Planilha Excel gerada com sucesso!")
        
        display.download_button(
            label="📥 Baixar Planilha Excel",
            data=excel_buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"excel_download_{datetime.now().timestamp()}"
        )
        
        # Log da ação
        if 'agent_logs' not in st.session_state:
            st.session_state['agent_logs'] = []
            
        st.session_state['agent_logs'].append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'agent': 'excel_generator',
            'action': '📊 Planilha Excel gerada',
            'details': {'filename': filename, 'status': 'Sucesso'}
        })
        
        return True
        
    except Exception as e:
        if container:
            container.error(f"❌ Erro ao gerar Excel: {str(e)}")
        else:
            st.error(f"❌ Erro ao gerar Excel: {str(e)}")
        return False

# Atualiza��o for�ada 09/18/2025 20:55:06
