"""
Agente de Extração e Limpeza de Dados
Responsável por processar planilhas e normalizar dados
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from llama_index import Document
import json
import re
from datetime import datetime

from .base_agent import BaseAgent
from ..config.settings import settings

class ExtractionAgent(BaseAgent):
    """Agente especializado em extração e limpeza de dados de planilhas"""
    
    def __init__(self):
        super().__init__(
            agent_name="extraction_agent",
            prompt_file="extraction_prompts.yaml",
            collection_name="extraction_rules"
        )
        self.column_mappings = {}
        self.validation_rules = {}
        
    def process(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """
        Processa um arquivo de planilha
        
        Args:
            file_path: Caminho do arquivo
            **kwargs: Argumentos adicionais
            
        Returns:
            DataFrame processado
        """
        self.log_action("Iniciando processamento", {"file": str(file_path)})
        
        # 1. Carregar arquivo
        df = self._load_file(file_path)
        
        # 2. Detectar e mapear colunas
        df = self._detect_and_map_columns(df)
        
        # 3. Limpar dados
        df = self._clean_data(df)
        
        # 4. Validar dados
        validation_results = self._validate_data(df)
        
        # 5. Adicionar metadados
        df = self._add_metadata(df, file_path)
        
        # 6. Armazenar regras aprendidas
        self._store_learning(df, validation_results)
        
        self.log_action("Processamento concluído", {
            "file": str(file_path),
            "rows": len(df),
            "columns": len(df.columns)
        })
        
        return df
    
    def _load_file(self, file_path: Path) -> pd.DataFrame:
        """Carrega arquivo Excel ou CSV"""
        try:
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                # Tentar ler todas as abas
                excel_file = pd.ExcelFile(file_path)
                if len(excel_file.sheet_names) > 1:
                    # Se houver múltiplas abas, usar IA para decidir qual usar
                    sheet_name = self._select_best_sheet(excel_file)
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.csv':
                # Detectar encoding
                encoding = self._detect_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
            else:
                raise ValueError(f"Formato não suportado: {file_path.suffix}")
                
            return df
        except Exception as e:
            self.log_action("Erro ao carregar arquivo", {"error": str(e)})
            raise
    
    def _detect_and_map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta e mapeia colunas usando IA"""
        # Obter amostra dos dados
        sample_data = df.head(5).to_dict()
        
        # Usar LLM para detectar mapeamento
        prompt = self.get_system_prompt('column_detection', 
                                      columns=list(df.columns),
                                      sample=json.dumps(sample_data, ensure_ascii=False))
        
        if self.llm:
            response = self.llm.complete(prompt)
            mappings = self._parse_column_mappings(response.text)
            
            # Aplicar mapeamentos
            rename_dict = {}
            for original, mapped in mappings.items():
                if original in df.columns:
                    rename_dict[original] = mapped
                    
            df = df.rename(columns=rename_dict)
            self.column_mappings.update(mappings)
        
        # Garantir que MATRICULA existe
        if 'MATRICULA' not in df.columns:
            # Tentar encontrar coluna similar
            matricula_candidates = [col for col in df.columns 
                                  if any(term in col.upper() 
                                        for term in ['MATRIC', 'REGISTRO', 'ID', 'CODIGO'])]
            if matricula_candidates:
                df = df.rename(columns={matricula_candidates[0]: 'MATRICULA'})
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e normaliza dados"""
        # Remover espaços extras
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Converter MATRICULA para string
        if 'MATRICULA' in df.columns:
            df['MATRICULA'] = df['MATRICULA'].astype(str).str.strip()
            # Remover caracteres especiais
            df['MATRICULA'] = df['MATRICULA'].str.replace(r'[^\w\s]', '', regex=True)
        
        # Detectar e converter tipos de dados
        for col in df.columns:
            # Datas
            if any(term in col.upper() for term in ['DATA', 'DATE', 'DT_']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Valores monetários
            elif any(term in col.upper() for term in ['VALOR', 'SALARIO', 'REMUNERACAO', 'VL_']):
                df[col] = self._clean_monetary_values(df[col])
            
            # CPF
            elif 'CPF' in col.upper():
                df[col] = self._clean_cpf(df[col])
        
        # Remover duplicatas baseadas em MATRICULA
        if 'MATRICULA' in df.columns:
            df = df.drop_duplicates(subset=['MATRICULA'], keep='last')
        
        return df
    
    def _clean_monetary_values(self, series: pd.Series) -> pd.Series:
        """Limpa valores monetários"""
        # Remover símbolos de moeda e espaços
        series = series.astype(str).str.replace(r'[R$\s]', '', regex=True)
        # Trocar vírgula por ponto
        series = series.str.replace(',', '.')
        # Converter para float
        return pd.to_numeric(series, errors='coerce')
    
    def _clean_cpf(self, series: pd.Series) -> pd.Series:
        """Limpa e formata CPF"""
        # Remover caracteres não numéricos
        series = series.astype(str).str.replace(r'\D', '', regex=True)
        # Adicionar zeros à esquerda se necessário
        series = series.str.zfill(11)
        # Formatar como XXX.XXX.XXX-XX
        series = series.apply(lambda x: f"{x[:3]}.{x[3:6]}.{x[6:9]}-{x[9:11]}" if len(x) == 11 else x)
        return series
    
    def _validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida dados e retorna relatório"""
        validation_results = {
            'total_rows': len(df),
            'valid_rows': 0,
            'issues': [],
            'warnings': []
        }
        
        # Validar MATRICULA
        if 'MATRICULA' in df.columns:
            missing_matricula = df['MATRICULA'].isna().sum()
            if missing_matricula > 0:
                validation_results['issues'].append(
                    f"{missing_matricula} registros sem MATRICULA"
                )
        else:
            validation_results['issues'].append("Coluna MATRICULA não encontrada")
        
        # Validar outras colunas importantes
        important_columns = ['NOME', 'CPF', 'CARGO', 'DEPARTAMENTO', 'SALARIO']
        for col in important_columns:
            if col in df.columns:
                missing = df[col].isna().sum()
                if missing > 0:
                    validation_results['warnings'].append(
                        f"{missing} registros sem {col}"
                    )
        
        # Contar linhas válidas (com MATRICULA)
        if 'MATRICULA' in df.columns:
            validation_results['valid_rows'] = df['MATRICULA'].notna().sum()
        
        return validation_results
    
    def _add_metadata(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """Adiciona metadados ao DataFrame"""
        df['_source_file'] = str(file_path.name)
        df['_import_date'] = datetime.now()
        df['_agent_version'] = '1.0.0'
        return df
    
    def _store_learning(self, df: pd.DataFrame, validation_results: Dict[str, Any]):
        """Armazena aprendizados para melhorar processamentos futuros"""
        if self.index:
            # Criar documento com aprendizados
            learning_doc = Document(
                text=json.dumps({
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'validation_results': validation_results,
                    'column_mappings': self.column_mappings
                }, default=str),
                metadata={
                    'type': 'learning',
                    'timestamp': datetime.now().isoformat()
                }
            )
            self.add_documents([learning_doc])
    
    def _select_best_sheet(self, excel_file: pd.ExcelFile) -> str:
        """Usa IA para selecionar a melhor aba de uma planilha"""
        sheet_info = []
        for sheet_name in excel_file.sheet_names:
            df_sample = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=5)
            sheet_info.append({
                'name': sheet_name,
                'columns': list(df_sample.columns),
                'rows': len(df_sample)
            })
        
        if self.llm:
            prompt = self.get_system_prompt('sheet_selection', 
                                          sheets=json.dumps(sheet_info, ensure_ascii=False))
            response = self.llm.complete(prompt)
            # Extrair nome da aba da resposta
            for sheet in excel_file.sheet_names:
                if sheet.lower() in response.text.lower():
                    return sheet
        
        # Fallback: usar primeira aba
        return excel_file.sheet_names[0]
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detecta encoding de arquivo CSV"""
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1000)  # Ler amostra
                return encoding
            except:
                continue
        
        return 'utf-8'  # Fallback
    
    def _parse_column_mappings(self, llm_response: str) -> Dict[str, str]:
        """Parse da resposta do LLM para mapeamento de colunas"""
        mappings = {}
        
        # Tentar extrair JSON da resposta
        try:
            # Procurar por JSON na resposta
            json_match = re.search(r'\{[^}]+\}', llm_response, re.DOTALL)
            if json_match:
                mappings = json.loads(json_match.group())
        except:
            # Fallback: extrair mapeamentos linha por linha
            lines = llm_response.split('\n')
            for line in lines:
                if '->' in line or '=>' in line:
                    parts = re.split(r'->|=>', line)
                    if len(parts) == 2:
                        original = parts[0].strip().strip('"\'')
                        mapped = parts[1].strip().strip('"\'')
                        mappings[original] = mapped
        
        return mappings
