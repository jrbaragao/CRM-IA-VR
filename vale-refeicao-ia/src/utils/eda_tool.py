"""
Tool de Análise Exploratória de Dados (EDA)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Union
import io
import base64
from datetime import datetime
import json
import streamlit as st

class EDAAnalyzer:
    """Analisador para Análise Exploratória de Dados"""
    
    def __init__(self):
        # Configurar matplotlib para não mostrar plots
        plt.ioff()
        # Configurar estilo do seaborn
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def analyze_dataset(self, df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
        """Realiza análise completa do dataset"""
        try:
            results = {
                "dataset_name": dataset_name,
                "basic_info": self._get_basic_info(df),
                "data_types": self._analyze_data_types(df),
                "missing_values": self._analyze_missing_values(df),
                "numeric_stats": self._analyze_numeric_columns(df),
                "categorical_stats": self._analyze_categorical_columns(df),
                "correlations": self._analyze_correlations(df),
                "outliers": self._detect_outliers(df),
                "distributions": self._analyze_distributions(df),
                "patterns": self._identify_patterns(df),
                "recommendations": self._generate_recommendations(df)
            }
            
            return results
            
        except Exception as e:
            return {
                "error": f"Erro na análise: {str(e)}",
                "dataset_name": dataset_name
            }
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informações básicas do dataset"""
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "duplicate_rows": df.duplicated().sum(),
            "duplicate_percentage": (df.duplicated().sum() / len(df) * 100) if len(df) > 0 else 0
        }
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa tipos de dados"""
        type_counts = df.dtypes.value_counts()
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        return {
            "type_summary": {str(k): int(v) for k, v in type_counts.items()},
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    def _analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa valores ausentes"""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df) * 100).round(2)
        
        return {
            "total_missing": int(missing_counts.sum()),
            "columns_with_missing": missing_counts[missing_counts > 0].to_dict(),
            "missing_percentages": missing_percentages[missing_percentages > 0].to_dict(),
            "complete_columns": missing_counts[missing_counts == 0].index.tolist()
        }
    
    def _analyze_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa colunas numéricas"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "Nenhuma coluna numérica encontrada"}
        
        stats = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            
            if len(col_data) > 0:
                stats[col] = {
                    "count": int(col_data.count()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q1": float(col_data.quantile(0.25)),
                    "q3": float(col_data.quantile(0.75)),
                    "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis()),
                    "unique_values": int(col_data.nunique()),
                    "mode": float(col_data.mode().iloc[0]) if not col_data.mode().empty else None
                }
        
        return stats
    
    def _analyze_categorical_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa colunas categóricas"""
        categorical_df = df.select_dtypes(include=['object', 'category'])
        
        if categorical_df.empty:
            return {"message": "Nenhuma coluna categórica encontrada"}
        
        stats = {}
        for col in categorical_df.columns:
            col_data = categorical_df[col].dropna()
            
            if len(col_data) > 0:
                value_counts = col_data.value_counts()
                stats[col] = {
                    "unique_values": int(col_data.nunique()),
                    "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "least_frequent": str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                    "least_frequent_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                    "top_10_values": {str(k): int(v) for k, v in value_counts.head(10).items()}
                }
        
        return stats
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa correlações entre variáveis numéricas"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {"message": "Menos de 2 colunas numéricas para calcular correlação"}
        
        # Calcular matriz de correlação
        corr_matrix = numeric_df.corr()
        
        # Encontrar correlações fortes (> 0.7 ou < -0.7)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(corr_value)
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "highly_correlated_pairs": len(strong_correlations)
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta outliers usando método IQR"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "Nenhuma coluna numérica para detectar outliers"}
        
        outliers_info = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                
                outliers_info[col] = {
                    "outlier_count": len(outliers),
                    "outlier_percentage": (len(outliers) / len(col_data) * 100),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "outlier_values": outliers.tolist()[:10]  # Primeiros 10 outliers
                }
        
        return outliers_info
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa distribuições das variáveis"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "Nenhuma coluna numérica para analisar distribuição"}
        
        distributions = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            
            if len(col_data) > 0:
                # Teste de normalidade simplificado (baseado em skewness)
                skewness = col_data.skew()
                is_normal = abs(skewness) < 0.5
                
                distributions[col] = {
                    "skewness": float(skewness),
                    "distribution_type": "aproximadamente normal" if is_normal else "assimétrica",
                    "histogram_bins": 20,
                    "recommended_transformation": self._recommend_transformation(skewness)
                }
        
        return distributions
    
    def _recommend_transformation(self, skewness: float) -> str:
        """Recomenda transformação baseada na assimetria"""
        if abs(skewness) < 0.5:
            return "Nenhuma transformação necessária"
        elif skewness > 0.5:
            return "Considere transformação log ou sqrt"
        else:
            return "Considere transformação quadrática ou cúbica"
    
    def _identify_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identifica padrões nos dados"""
        patterns = {
            "temporal_patterns": [],
            "value_patterns": [],
            "missing_patterns": []
        }
        
        # Padrões temporais
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_cols:
            if len(df[col].dropna()) > 0:
                patterns["temporal_patterns"].append({
                    "column": col,
                    "min_date": str(df[col].min()),
                    "max_date": str(df[col].max()),
                    "date_range_days": (df[col].max() - df[col].min()).days
                })
        
        # Padrões de valores constantes
        for col in df.columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.01:  # Menos de 1% de valores únicos
                patterns["value_patterns"].append({
                    "column": col,
                    "pattern": "Baixa variabilidade",
                    "unique_ratio": unique_ratio
                })
        
        # Padrões de valores ausentes
        missing_cols = df.columns[df.isnull().any()].tolist()
        if len(missing_cols) > 1:
            # Verificar se há colunas com padrão similar de ausência
            missing_patterns = df[missing_cols].isnull()
            correlation = missing_patterns.corr()
            
            for i in range(len(missing_cols)):
                for j in range(i+1, len(missing_cols)):
                    if correlation.iloc[i, j] > 0.8:
                        patterns["missing_patterns"].append({
                            "columns": [missing_cols[i], missing_cols[j]],
                            "correlation": float(correlation.iloc[i, j])
                        })
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Verificar valores ausentes
        missing_info = self._analyze_missing_values(df)
        if missing_info["total_missing"] > 0:
            recommendations.append(
                f"🔍 Tratar {missing_info['total_missing']} valores ausentes em {len(missing_info['columns_with_missing'])} colunas"
            )
        
        # Verificar duplicatas
        basic_info = self._get_basic_info(df)
        if basic_info["duplicate_rows"] > 0:
            recommendations.append(
                f"🔄 Remover {basic_info['duplicate_rows']} linhas duplicadas ({basic_info['duplicate_percentage']:.1f}%)"
            )
        
        # Verificar outliers
        outliers = self._detect_outliers(df)
        cols_with_outliers = [col for col, info in outliers.items() 
                             if isinstance(info, dict) and info.get("outlier_count", 0) > 0]
        if cols_with_outliers:
            recommendations.append(
                f"⚠️ Investigar outliers em {len(cols_with_outliers)} colunas numéricas"
            )
        
        # Verificar correlações
        correlations = self._analyze_correlations(df)
        if correlations.get("highly_correlated_pairs", 0) > 0:
            recommendations.append(
                f"🔗 Avaliar {correlations['highly_correlated_pairs']} pares de variáveis altamente correlacionadas"
            )
        
        # Verificar distribuições
        distributions = self._analyze_distributions(df)
        skewed_cols = [col for col, info in distributions.items() 
                      if isinstance(info, dict) and abs(info.get("skewness", 0)) > 1]
        if skewed_cols:
            recommendations.append(
                f"📊 Considerar transformação em {len(skewed_cols)} colunas com distribuição assimétrica"
            )
        
        return recommendations


def execute_eda_analysis(db, data_tables: list, query: str = None) -> dict:
    """
    Executa análise exploratória de dados em tabelas específicas
    
    Args:
        db: Instância do DatabaseManager
        data_tables: Lista de tabelas disponíveis
        query: Pergunta do usuário sobre os dados
    
    Returns:
        dict: Resultados da análise
    """
    try:
        analyzer = EDAAnalyzer()
        results = {
            "action_type": "eda_analysis",
            "query": query,
            "analyses": {},
            "visualizations": [],
            "insights": [],
            "success": True
        }
        
        # Se não especificou tabelas, analisar todas
        if not query or "todas" in query.lower():
            tables_to_analyze = data_tables
        else:
            # Tentar identificar tabelas mencionadas na query
            tables_to_analyze = [t for t in data_tables if t.lower() in query.lower()]
            if not tables_to_analyze:
                tables_to_analyze = data_tables[:3]  # Primeiras 3 tabelas se não encontrar
        
        # Analisar cada tabela
        for table in tables_to_analyze:
            if table in data_tables:
                try:
                    # Carregar dados da tabela
                    df = db.get_table_data(table)
                    
                    if df is not None and not df.empty:
                        # Executar análise
                        analysis = analyzer.analyze_dataset(df, table)
                        results["analyses"][table] = analysis
                        
                        # Gerar insights específicos
                        insights = _generate_insights_from_analysis(analysis, table)
                        results["insights"].extend(insights)
                        
                except Exception as e:
                    results["analyses"][table] = {"error": str(e)}
        
        # Gerar visualizações se solicitado
        if query and any(term in query.lower() for term in ["gráfico", "grafico", "plot", "visualiz"]):
            results["visualizations"] = _generate_visualizations(db, tables_to_analyze, results["analyses"])
        
        # Resumo final
        results["summary"] = _generate_eda_summary(results)
        
        return results
        
    except Exception as e:
        return {
            "action_type": "eda_analysis",
            "success": False,
            "error": str(e)
        }


def _generate_insights_from_analysis(analysis: Dict[str, Any], table_name: str) -> List[str]:
    """Gera insights a partir da análise"""
    insights = []
    
    # Insights sobre dados básicos
    if "basic_info" in analysis:
        info = analysis["basic_info"]
        insights.append(
            f"📊 Tabela '{table_name}': {info['total_rows']:,} registros, "
            f"{info['total_columns']} colunas, {info['memory_usage_mb']:.1f}MB"
        )
        
        if info["duplicate_rows"] > 0:
            insights.append(
                f"⚠️ '{table_name}': {info['duplicate_rows']} linhas duplicadas "
                f"({info['duplicate_percentage']:.1f}%)"
            )
    
    # Insights sobre valores ausentes
    if "missing_values" in analysis:
        missing = analysis["missing_values"]
        if missing["total_missing"] > 0:
            worst_cols = sorted(
                missing["missing_percentages"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            insights.append(
                f"❓ '{table_name}': Valores ausentes em {len(missing['columns_with_missing'])} colunas. "
                f"Piores: {', '.join([f'{col} ({pct:.1f}%)' for col, pct in worst_cols])}"
            )
    
    # Insights sobre outliers
    if "outliers" in analysis:
        outliers = analysis["outliers"]
        cols_with_many_outliers = [
            col for col, info in outliers.items() 
            if isinstance(info, dict) and info.get("outlier_percentage", 0) > 5
        ]
        if cols_with_many_outliers:
            insights.append(
                f"📍 '{table_name}': Muitos outliers (>5%) em: {', '.join(cols_with_many_outliers)}"
            )
    
    # Insights sobre correlações
    if "correlations" in analysis and "strong_correlations" in analysis["correlations"]:
        correlations = analysis["correlations"]["strong_correlations"]
        if correlations:
            insights.append(
                f"🔗 '{table_name}': {len(correlations)} pares de variáveis fortemente correlacionadas"
            )
    
    return insights


def _generate_visualizations(db, tables: List[str], analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera visualizações básicas"""
    visualizations = []
    
    for table in tables[:2]:  # Limitar a 2 tabelas para não sobrecarregar
        if table in analyses and "numeric_stats" in analyses[table]:
            # Criar descrição das visualizações possíveis
            numeric_cols = list(analyses[table]["numeric_stats"].keys())
            if numeric_cols:
                visualizations.append({
                    "table": table,
                    "type": "histograms",
                    "columns": numeric_cols[:5],  # Primeiras 5 colunas numéricas
                    "description": f"Histogramas das distribuições em '{table}'"
                })
                
                if len(numeric_cols) > 1:
                    visualizations.append({
                        "table": table,
                        "type": "correlation_matrix",
                        "description": f"Matriz de correlação para '{table}'"
                    })
    
    return visualizations


def _generate_eda_summary(results: Dict[str, Any]) -> str:
    """Gera resumo da análise exploratória"""
    summary_parts = []
    
    # Resumo das tabelas analisadas
    tables_analyzed = len(results.get("analyses", {}))
    summary_parts.append(f"✅ Analisadas {tables_analyzed} tabelas")
    
    # Total de insights
    total_insights = len(results.get("insights", []))
    if total_insights > 0:
        summary_parts.append(f"💡 {total_insights} insights identificados")
    
    # Visualizações sugeridas
    viz_count = len(results.get("visualizations", []))
    if viz_count > 0:
        summary_parts.append(f"📊 {viz_count} visualizações disponíveis")
    
    # Problemas encontrados
    errors = sum(1 for analysis in results.get("analyses", {}).values() 
                if "error" in analysis)
    if errors > 0:
        summary_parts.append(f"⚠️ {errors} erros durante análise")
    
    return " | ".join(summary_parts)


# Função para criar gráficos específicos
def create_distribution_plot(df: pd.DataFrame, column: str) -> str:
    """Cria histograma de distribuição e retorna como base64"""
    try:
        plt.figure(figsize=(10, 6))
        plt.hist(df[column].dropna(), bins=30, edgecolor='black', alpha=0.7)
        plt.title(f'Distribuição de {column}')
        plt.xlabel(column)
        plt.ylabel('Frequência')
        plt.grid(True, alpha=0.3)
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        plt.close()
        return None


def create_correlation_heatmap(df: pd.DataFrame) -> str:
    """Cria heatmap de correlação e retorna como base64"""
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return None
        
        plt.figure(figsize=(12, 10))
        correlation_matrix = numeric_df.corr()
        
        # Criar heatmap
        sns.heatmap(
            correlation_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8}
        )
        
        plt.title('Matriz de Correlação')
        plt.tight_layout()
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        plt.close()
        return None


def create_boxplot(df: pd.DataFrame, columns: List[str]) -> str:
    """Cria boxplot para detectar outliers e retorna como base64"""
    try:
        plt.figure(figsize=(12, 6))
        df[columns].boxplot(figsize=(12, 6))
        plt.title('Boxplot - Detecção de Outliers')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return plot_base64
        
    except Exception as e:
        plt.close()
        return None
