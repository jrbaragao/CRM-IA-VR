"""
Conexão e operações com banco de dados SQLite
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, Optional
import streamlit as st
from datetime import datetime
import pandas as pd

from .models import Base, ImportacaoArquivo, AgentLog
from ..config.settings import settings

class DatabaseManager:
    """Gerenciador de conexão com banco de dados"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa conexão com banco de dados"""
        try:
            # Usar SQLite por padrão se não configurado
            database_url = settings.database_url
            if not database_url or "postgresql" in database_url:
                database_url = "sqlite:///./vale_refeicao.db"
                st.info("🔄 Usando SQLite local: vale_refeicao.db")
            
            # Criar engine
            self.engine = create_engine(
                database_url,
                echo=settings.debug,
                connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
            )
            
            # Criar tabelas
            Base.metadata.create_all(bind=self.engine)
            
            # Criar tabela de configurações de cálculo
            self._create_calculation_configs_table()
            
            # Não criar mais configuração padrão automaticamente
            # self._create_default_calculation_config()
            
            # Remover tabelas antigas se existirem
            self._cleanup_old_tables()
            
            # Recriar tabela de importações se necessário (para remover empresa_id)
            self._update_importacoes_table()
            
            # Criar session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            st.success("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            st.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager para sessões do banco"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Testa conexão com banco de dados"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            st.error(f"❌ Erro na conexão: {str(e)}")
            return False
    
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str, 
                                   primary_key: str = None) -> bool:
        """
        Cria uma tabela dinamicamente baseada no DataFrame
        
        Args:
            df: DataFrame com os dados
            table_name: Nome da tabela a ser criada
            primary_key: Nome da coluna que será chave primária
            
        Returns:
            True se criou com sucesso
        """
        try:
            # Limpar nome da tabela (remover caracteres especiais)
            table_name = self._clean_table_name(table_name)
            
            # Mapear tipos do pandas para SQLite
            type_mapping = {
                'object': 'TEXT',
                'int64': 'INTEGER',
                'float64': 'REAL',
                'bool': 'INTEGER',
                'datetime64[ns]': 'DATETIME',
                'category': 'TEXT'
            }
            
            # Construir SQL CREATE TABLE
            columns = []
            for col in df.columns:
                col_name = self._clean_column_name(col)
                pandas_type = str(df[col].dtype)
                sql_type = type_mapping.get(pandas_type, 'TEXT')
                
                # Adicionar PRIMARY KEY se especificado
                if primary_key and col_name.upper() == primary_key.upper():
                    columns.append(f'"{col_name}" {sql_type} PRIMARY KEY')
                else:
                    columns.append(f'"{col_name}" {sql_type}')
            
            # Adicionar colunas de metadados
            columns.extend([
                '"created_at" DATETIME DEFAULT CURRENT_TIMESTAMP',
                '"updated_at" DATETIME DEFAULT CURRENT_TIMESTAMP'
            ])
            
            create_sql = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                {', '.join(columns)}
            )
            '''
            
            # Executar criação da tabela
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            
            st.success(f"✅ Tabela '{table_name}' criada com sucesso!")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao criar tabela '{table_name}': {str(e)}")
            return False
    
    def save_dataframe_to_table(self, df: pd.DataFrame, table_name: str, 
                               if_exists: str = 'replace') -> int:
        """
        Salva DataFrame diretamente em uma tabela
        
        Args:
            df: DataFrame com os dados
            table_name: Nome da tabela
            if_exists: 'replace', 'append', 'fail'
            
        Returns:
            Número de registros salvos
        """
        try:
            # Limpar nome da tabela
            table_name = self._clean_table_name(table_name)
            
            # Limpar nomes das colunas
            df_clean = df.copy()
            df_clean.columns = [self._clean_column_name(col) for col in df_clean.columns]
            
            # Adicionar metadados
            df_clean['created_at'] = datetime.utcnow()
            df_clean['updated_at'] = datetime.utcnow()
            
            # Salvar no banco usando pandas to_sql
            # Para SQLite, precisamos considerar o limite de variáveis (999)
            # Com 33 colunas, podemos processar no máximo ~30 linhas por vez
            num_columns = len(df_clean.columns)
            max_params = 999
            rows_per_chunk = max(1, min(max_params // num_columns - 1, 100))
            
            # Se temos muitas linhas, usar chunks menores
            if len(df_clean) > rows_per_chunk:
                chunksize = rows_per_chunk
            else:
                chunksize = None
            
            st.info(f"📊 Salvando {len(df_clean)} registros na tabela '{table_name}'...")
            if chunksize:
                st.info(f"📦 Processando em lotes de {chunksize} registros por vez...")
                
                # Salvar com progresso manual para grandes datasets
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                # Dividir o dataframe em chunks e salvar
                total_saved = 0
                for i in range(0, len(df_clean), chunksize):
                    chunk = df_clean.iloc[i:i + chunksize]
                    chunk.to_sql(
                        name=table_name,
                        con=self.engine,
                        if_exists='append' if i > 0 else if_exists,
                        index=False,
                        method='multi'
                    )
                    total_saved += len(chunk)
                    progress = total_saved / len(df_clean)
                    progress_bar.progress(progress)
                    progress_text.text(f"Salvando... {total_saved}/{len(df_clean)} registros")
                
                progress_bar.empty()
                progress_text.empty()
                rows_saved = total_saved
            else:
                # Dataset pequeno, salvar de uma vez
                rows_saved = df_clean.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists=if_exists,
                    index=False,
                    method='multi'
                )
            
            # Verificar se os dados foram realmente salvos
            try:
                with self.engine.connect() as conn:
                    # Usar text() do SQLAlchemy para executar SQL bruto
                    from sqlalchemy import text
                    query = text(f'SELECT COUNT(*) FROM "{table_name}"')
                    result = conn.execute(query)
                    actual_count = result.scalar()
            except Exception as count_error:
                st.warning(f"⚠️ Não foi possível verificar contagem: {str(count_error)}")
                actual_count = len(df_clean)
            
            st.success(f"✅ {actual_count} registros salvos na tabela '{table_name}'!")
            return actual_count
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar dados na tabela '{table_name}': {str(e)}")
            raise
    
    def _clean_table_name(self, name: str) -> str:
        """Limpa nome da tabela para ser válido no SQL"""
        import re
        # Remover extensão se houver
        name = name.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
        # Substituir caracteres especiais por underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Garantir que não comece com número
        if name[0].isdigit():
            name = f'table_{name}'
        return name.lower()
    
    def _clean_column_name(self, name: str) -> str:
        """Limpa nome da coluna para ser válido no SQL"""
        import re
        # Substituir caracteres especiais por underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remover underscores duplos
        name = re.sub(r'_+', '_', name)
        # Remover underscore no início e fim
        name = name.strip('_')
        # Garantir que não comece com número
        if name and name[0].isdigit():
            name = f'col_{name}'
        return name.upper() if name else 'UNNAMED_COLUMN'
    
    def list_tables(self) -> list:
        """Lista todas as tabelas do banco de dados"""
        try:
            with self.engine.connect() as conn:
                # SQLite - buscar tabelas na sqlite_master
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """))
                tables = [row[0] for row in result.fetchall()]
                return tables
        except Exception as e:
            st.error(f"❌ Erro ao listar tabelas: {str(e)}")
            return []
    
    def get_table_data(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """Busca dados de uma tabela específica"""
        try:
            table_name = self._clean_table_name(table_name)
            
            # Construir query
            query = f'SELECT * FROM "{table_name}"'
            if limit:
                query += f' LIMIT {limit}'
            
            # Executar query
            df = pd.read_sql(query, self.engine)
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados da tabela '{table_name}': {str(e)}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> dict:
        """Retorna informações sobre uma tabela"""
        try:
            table_name = self._clean_table_name(table_name)
            
            with self.engine.connect() as conn:
                # Informações das colunas
                result = conn.execute(text(f'PRAGMA table_info("{table_name}")'))
                columns = []
                for row in result.fetchall():
                    columns.append({
                        'name': row[1],
                        'type': row[2],
                        'not_null': bool(row[3]),
                        'primary_key': bool(row[5])
                    })
                
                # Contar registros
                count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                total_rows = count_result.fetchone()[0]
                
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'total_rows': total_rows
                }
                
        except Exception as e:
            st.error(f"❌ Erro ao obter informações da tabela '{table_name}': {str(e)}")
            return {}
    
    def drop_table(self, table_name: str) -> bool:
        """Remove uma tabela do banco de dados"""
        try:
            table_name = self._clean_table_name(table_name)
            
            with self.engine.connect() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.commit()
            
            st.success(f"✅ Tabela '{table_name}' removida com sucesso!")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao remover tabela '{table_name}': {str(e)}")
            return False
    
    def update_primary_key(self, table_name: str, old_pk: str, new_pk: str) -> bool:
        """
        Atualiza a chave primária de uma tabela
        No SQLite, isso requer recriar a tabela
        """
        try:
            table_name = self._clean_table_name(table_name)
            old_pk = self._clean_column_name(old_pk) if old_pk else None
            new_pk = self._clean_column_name(new_pk) if new_pk else None
            
            with self.engine.connect() as conn:
                # 1. Obter estrutura atual da tabela
                table_info = self.get_table_info(table_name)
                if not table_info:
                    raise Exception(f"Tabela '{table_name}' não encontrada")
                
                # 2. Criar nova estrutura com nova PK
                columns = []
                for col in table_info['columns']:
                    col_name = col['name']
                    col_type = col['type']
                    
                    # Definir se é chave primária
                    if new_pk and col_name.upper() == new_pk.upper():
                        columns.append(f'"{col_name}" {col_type} PRIMARY KEY')
                    elif old_pk and col_name.upper() == old_pk.upper():
                        # Remover PRIMARY KEY da coluna antiga
                        columns.append(f'"{col_name}" {col_type}')
                    else:
                        # Manter como está (sem PK)
                        columns.append(f'"{col_name}" {col_type}')
                
                # 3. Criar tabela temporária
                temp_table = f"{table_name}_temp"
                create_temp_sql = f'''
                CREATE TABLE "{temp_table}" (
                    {', '.join(columns)}
                )
                '''
                
                conn.execute(text(create_temp_sql))
                
                # 4. Copiar dados para tabela temporária
                column_names = [col['name'] for col in table_info['columns']]
                columns_str = ', '.join([f'"{col}"' for col in column_names])
                
                copy_sql = f'''
                INSERT INTO "{temp_table}" ({columns_str})
                SELECT {columns_str} FROM "{table_name}"
                '''
                
                conn.execute(text(copy_sql))
                
                # 5. Remover tabela original
                conn.execute(text(f'DROP TABLE "{table_name}"'))
                
                # 6. Renomear tabela temporária
                conn.execute(text(f'ALTER TABLE "{temp_table}" RENAME TO "{table_name}"'))
                
                conn.commit()
            
            pk_text = f"'{new_pk}'" if new_pk else "removida"
            st.success(f"✅ Chave primária da tabela '{table_name}' alterada para {pk_text}!")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao alterar chave primária: {str(e)}")
            return False
    
    def get_column_sample_data(self, table_name: str, column_name: str, limit: int = 5) -> list:
        """Retorna dados de exemplo de uma coluna para ajudar na escolha da PK"""
        try:
            table_name = self._clean_table_name(table_name)
            column_name = self._clean_column_name(column_name)
            
            query = f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT {limit}'
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [str(row[0]) for row in result.fetchall()]
                
        except Exception as e:
            return []
    
    # Funções removidas: _create_funcionario e _update_funcionario
    # Os dados agora são salvos diretamente nas tabelas dinâmicas via DataFrame
    
    def log_importacao(self, nome_arquivo: str, status: str, total_linhas: int, 
                      linhas_processadas: int, erros: dict = None) -> int:
        """
        Registra importação de arquivo
        
        Returns:
            ID da importação criada
        """
        try:
            with self.get_session() as session:
                importacao = ImportacaoArquivo(
                    # empresa_id removido - agora usamos tabelas dinâmicas
                    nome_arquivo=nome_arquivo,
                    tipo_arquivo="dados_dinamicos",
                    formato=nome_arquivo.split('.')[-1].lower(),
                    status=status,
                    total_linhas=total_linhas,
                    linhas_processadas=linhas_processadas,
                    linhas_erro=total_linhas - linhas_processadas,
                    erros=erros or {},
                    agente_processamento="extraction_agent",
                    processed_at=datetime.utcnow() if status == "concluido" else None
                )
                
                session.add(importacao)
                session.flush()  # Para obter o ID
                
                return importacao.id
                
        except Exception as e:
            st.error(f"❌ Erro ao registrar importação: {str(e)}")
            raise
    
    def log_to_session(self, agent_name: str, action: str, input_data: dict = None, 
                        output_data: dict = None, status: str = "success", 
                        error_message: str = None) -> int:
        """
        Registra ação de agente
        
        Returns:
            ID do log criado
        """
        try:
            with self.get_session() as session:
                log_entry = AgentLog(
                    agent_name=agent_name,
                    action=action,
                    # empresa_id removido - não existe mais na tabela
                    input_data=input_data or {},
                    output_data=output_data or {},
                    status=status,
                    error_message=error_message
                )
                
                session.add(log_entry)
                session.flush()
                
                return log_entry.id
                
        except Exception as e:
            st.error(f"❌ Erro ao registrar log do agente: {str(e)}")
            raise
    
    # Função removida: get_funcionarios
    # Os dados de funcionários agora vêm das tabelas dinâmicas criadas pelos uploads
    
    # Função removida: ensure_empresa_exists
    # As configurações da empresa agora são gerenciadas via settings ou tabelas dinâmicas
    
    def _create_calculation_configs_table(self):
        """Cria tabela para configurações de cálculo"""
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS calculation_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                prompt TEXT NOT NULL,
                available_tools TEXT NOT NULL,  -- JSON array das ferramentas disponíveis
                max_iterations INTEGER DEFAULT 5,
                exploration_depth TEXT DEFAULT 'Intermediária',
                include_insights BOOLEAN DEFAULT TRUE,
                show_reasoning BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            """
            
            with self.engine.begin() as conn:
                conn.execute(text(create_table_sql))
                # Commit automático com begin()
                
        except Exception as e:
            st.error(f"Erro ao criar tabela de configurações de cálculo: {str(e)}")
    
    def save_calculation_config(self, name: str, description: str, prompt: str, 
                              available_tools: list, config: dict) -> bool:
        """Salva configuração de cálculo"""
        try:
            import json
            
            # Função local de log para evitar import circular
            def log_to_session(agent: str, action: str, details: dict = None):
                """Log local para session state"""
                if 'agent_logs' not in st.session_state:
                    st.session_state.agent_logs = []
                
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'agent': agent,
                    'action': action,
                    'details': details or {}
                }
                st.session_state.agent_logs.append(log_entry)
            
            # Log inicial
            log_to_session(
                "config_manager",
                f"🔧 Iniciando salvamento de configuração: {name}",
                {
                    "nome": name,
                    "ferramentas": len(available_tools),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            # Verificar se a tabela existe
            with self.engine.connect() as conn:
                check_table_sql = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='calculation_configs'
                """
                result = conn.execute(text(check_table_sql))
                table_exists = result.fetchone()
                
                if not table_exists:
                    st.warning("⚠️ Tabela calculation_configs não existe. Criando...")
                    log_to_session(
                        "config_manager",
                        "📋 Criando tabela calculation_configs",
                        {"status": "criando"}
                    )
                    conn.close()  # Fechar conexão antes de criar tabela
                    self._create_calculation_configs_table()
                    st.success("✅ Tabela calculation_configs criada com sucesso!")
                    log_to_session(
                        "config_manager",
                        "✅ Tabela calculation_configs criada",
                        {"status": "criada"}
                    )
                else:
                    st.caption("✅ Tabela calculation_configs já existe.")
                    log_to_session(
                        "config_manager",
                        "✅ Tabela calculation_configs encontrada",
                        {"status": "existe"}
                    )
            
            # Preparar dados
            tools_json = json.dumps(available_tools)
            
            # Verificar se já existe
            check_sql = "SELECT id FROM calculation_configs WHERE name = :name"
            
            # Usar begin() para transação explícita
            with self.engine.begin() as conn:
                result = conn.execute(text(check_sql), {"name": name}).fetchone()
                
                if result:
                    # Atualizar existente
                    log_to_session(
                        "config_manager",
                        f"📝 Atualizando configuração existente: {name}",
                        {"id": result[0], "acao": "update"}
                    )
                    
                    update_sql = """
                    UPDATE calculation_configs 
                    SET description = :description, prompt = :prompt, 
                        available_tools = :tools, max_iterations = :max_iter,
                        exploration_depth = :depth, include_insights = :insights,
                        show_reasoning = :reasoning, updated_at = CURRENT_TIMESTAMP
                    WHERE name = :name
                    """
                    
                    conn.execute(text(update_sql), {
                        "name": name,
                        "description": description,
                        "prompt": prompt,
                        "tools": tools_json,
                        "max_iter": config.get('max_iterations', 5),
                        "depth": config.get('exploration_depth', 'Intermediária'),
                        "insights": config.get('include_insights', True),
                        "reasoning": config.get('show_reasoning', True)
                    })
                    
                    log_to_session(
                        "config_manager",
                        "✅ Configuração atualizada com sucesso",
                        {"nome": name, "acao": "update_complete"}
                    )
                else:
                    # Inserir novo
                    log_to_session(
                        "config_manager",
                        f"➕ Criando nova configuração: {name}",
                        {"acao": "insert"}
                    )
                    
                    insert_sql = """
                    INSERT INTO calculation_configs 
                    (name, description, prompt, available_tools, max_iterations,
                     exploration_depth, include_insights, show_reasoning, is_active)
                    VALUES (:name, :description, :prompt, :tools, :max_iter,
                            :depth, :insights, :reasoning, 1)
                    """
                    
                    params = {
                        "name": name,
                        "description": description,
                        "prompt": prompt,
                        "tools": tools_json,
                        "max_iter": config.get('max_iterations', 5),
                        "depth": config.get('exploration_depth', 'Intermediária'),
                        "insights": config.get('include_insights', True),
                        "reasoning": config.get('show_reasoning', True)
                    }
                    
                    log_to_session(
                        "config_manager",
                        "🔍 Parâmetros da inserção",
                        {"params": str(params)[:200] + "..."}
                    )
                    
                    conn.execute(text(insert_sql), params)
                    
                    log_to_session(
                        "config_manager",
                        "✅ Inserção executada",
                        {"nome": name, "acao": "insert_complete"}
                    )
                
                # Commit automático com begin()
                log_to_session(
                    "config_manager",
                    "💾 Commit automático da transação",
                    {"status": "commit_auto"}
                )
                
            # Verificar se foi salvo em nova conexão
            log_to_session(
                "config_manager",
                "🔍 Verificando se a configuração foi salva",
                {"nome": name}
            )
            
            with self.engine.connect() as conn:
                verify_sql = "SELECT COUNT(*) FROM calculation_configs WHERE name = :name"
                result = conn.execute(text(verify_sql), {"name": name})
                count = result.scalar()
                
                log_to_session(
                    "config_manager",
                    f"📊 Resultado da verificação: {count} registro(s)",
                    {"nome": name, "count": count}
                )
                
                if count > 0:
                    st.info(f"✅ Configuração '{name}' verificada no banco de dados.")
                    log_to_session(
                        "config_manager",
                        f"✅ SUCESSO: Configuração '{name}' salva com sucesso!",
                        {"nome": name, "status": "success"}
                    )
                    return True
                else:
                    st.error(f"❌ Configuração '{name}' não foi encontrada após salvar.")
                    log_to_session(
                        "config_manager",
                        f"❌ ERRO: Configuração '{name}' não foi encontrada!",
                        {"nome": name, "status": "error"}
                    )
                    return False
                
        except Exception as e:
            st.error(f"❌ Erro ao salvar configuração de cálculo: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            st.error(f"Detalhes: {error_details}")
            
            log_to_session(
                "config_manager",
                f"❌ ERRO CRÍTICO ao salvar configuração",
                {
                    "nome": name,
                    "erro": str(e),
                    "traceback": error_details[:500]
                }
            )
            return False
    
    def get_calculation_configs(self) -> list:
        """Obtém todas as configurações de cálculo"""
        try:
            sql = """
            SELECT id, name, description, prompt, available_tools, 
                   max_iterations, exploration_depth, include_insights, 
                   show_reasoning, created_at, updated_at, is_active
            FROM calculation_configs 
            WHERE is_active = TRUE OR is_active IS NULL
            ORDER BY name
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                configs = []
                
                for row in result:
                    import json
                    config = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'prompt': row[3],
                        'available_tools': json.loads(row[4]) if row[4] else [],
                        'max_iterations': row[5],
                        'exploration_depth': row[6],
                        'include_insights': bool(row[7]),
                        'show_reasoning': bool(row[8]),
                        'created_at': row[9],
                        'updated_at': row[10],
                        'is_active': bool(row[11])
                    }
                    configs.append(config)
                
                return configs
                
        except Exception as e:
            st.error(f"Erro ao obter configurações de cálculo: {str(e)}")
            return []
    
    def get_calculation_config(self, name: str) -> dict:
        """Obtém configuração específica de cálculo"""
        try:
            sql = """
            SELECT id, name, description, prompt, available_tools, 
                   max_iterations, exploration_depth, include_insights, 
                   show_reasoning, created_at, updated_at, is_active
            FROM calculation_configs 
            WHERE name = :name AND is_active = TRUE
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {"name": name}).fetchone()
                
                if result:
                    import json
                    return {
                        'id': result[0],
                        'name': result[1],
                        'description': result[2],
                        'prompt': result[3],
                        'available_tools': json.loads(result[4]) if result[4] else [],
                        'max_iterations': result[5],
                        'exploration_depth': result[6],
                        'include_insights': bool(result[7]),
                        'show_reasoning': bool(result[8]),
                        'created_at': result[9],
                        'updated_at': result[10],
                        'is_active': bool(result[11])
                    }
                
                return None
                
        except Exception as e:
            st.error(f"Erro ao obter configuração de cálculo: {str(e)}")
            return None
    
    def delete_calculation_config(self, name: str) -> bool:
        """Remove configuração de cálculo (soft delete)"""
        try:
            sql = """
            UPDATE calculation_configs 
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE name = :name
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(sql), {"name": name})
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Erro ao remover configuração de cálculo: {str(e)}")
            return False
    
    def _create_default_calculation_config(self):
        """Cria configuração padrão de cálculo se não existir"""
        try:
            # Verificar se já existe configuração padrão
            existing = self.get_calculation_config("Vale Refeição Padrão")
            if existing:
                return
            
            # Configuração padrão
            default_prompt = """Analise os dados de funcionários e calcule o vale refeição baseado nas seguintes regras:

1. REGRAS DE ELEGIBILIDADE:
   - Considerar apenas funcionários ativos
   - Incluir todos os tipos de contrato (CLT, estagiários, etc.)

2. REGRAS DE CÁLCULO:
   - Funcionários com salário até R$ 3.000: vale de R$ 500/mês
   - Funcionários com salário entre R$ 3.001 e R$ 6.000: vale de R$ 400/mês  
   - Funcionários com salário acima de R$ 6.000: vale de R$ 300/mês

3. AJUSTES PROPORCIONAIS:
   - Calcular valor proporcional aos dias trabalhados no mês
   - Descontar faltas não justificadas
   - Considerar férias e licenças

4. RELATÓRIO FINAL:
   - Gerar resumo por departamento
   - Calcular totais gerais
   - Identificar funcionários não elegíveis e motivos
   - Apresentar estatísticas e insights

Execute o cálculo de forma detalhada e organize os resultados de forma clara."""

            default_tools = [
                'sql_query',
                'data_exploration', 
                'mathematical_operations',
                'conditional_logic',
                'aggregations',
                'report_generation'
            ]
            
            default_config = {
                'max_iterations': 8,
                'exploration_depth': 'Avançada',
                'include_insights': True,
                'show_reasoning': True
            }
            
            # Salvar configuração padrão
            self.save_calculation_config(
                "Vale Refeição Padrão",
                "Configuração padrão para cálculo de vale refeição baseado em faixas salariais",
                default_prompt,
                default_tools,
                default_config
            )
            
        except Exception as e:
            # Não mostrar erro para não interromper inicialização
            pass
    
    def _cleanup_old_tables(self):
        """Remove tabelas antigas que não são mais utilizadas"""
        try:
            old_tables = ['empresas', 'funcionarios', 'funcionarios_vr', 'regras_calculo_vr', 'calculos_vr']
            
            with self.engine.connect() as conn:
                for table in old_tables:
                    try:
                        # Verificar se a tabela existe
                        check_sql = f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='{table}'
                        """
                        result = conn.execute(text(check_sql)).fetchone()
                        
                        if result:
                            # Tabela existe, remover
                            drop_sql = f"DROP TABLE IF EXISTS {table}"
                            conn.execute(text(drop_sql))
                            print(f"✅ Tabela antiga '{table}' removida")
                        
                    except Exception as e:
                        # Continuar mesmo se houver erro em uma tabela específica
                        print(f"⚠️ Erro ao remover tabela '{table}': {str(e)}")
                        continue
                
                conn.commit()
                
        except Exception as e:
            # Não mostrar erro para não interromper inicialização
            print(f"⚠️ Erro na limpeza de tabelas antigas: {str(e)}")
            pass
    
    def _update_importacoes_table(self):
        """Atualiza tabela de importações removendo empresa_id se existir"""
        try:
            with self.engine.connect() as conn:
                # Verificar se a tabela importacoes existe e tem empresa_id
                check_column_sql = """
                PRAGMA table_info(importacoes)
                """
                
                result = conn.execute(text(check_column_sql)).fetchall()
                columns = [row[1] for row in result]  # row[1] é o nome da coluna
                
                if 'empresa_id' in columns:
                    print("🔄 Atualizando tabela importacoes para remover empresa_id...")
                    
                    # Fazer backup dos dados
                    backup_sql = """
                    CREATE TABLE importacoes_backup AS 
                    SELECT nome_arquivo, tipo_arquivo, formato, tamanho_bytes, 
                           status, total_linhas, linhas_processadas, linhas_erro,
                           mapeamento_colunas, log_processamento, erros, 
                           agente_processamento, created_at, processed_at
                    FROM importacoes
                    """
                    
                    try:
                        conn.execute(text(backup_sql))
                    except:
                        pass  # Tabela backup pode já existir
                    
                    # Remover tabela antiga
                    conn.execute(text("DROP TABLE IF EXISTS importacoes"))
                    
                    # Recriar tabela sem empresa_id (SQLAlchemy fará isso automaticamente)
                    Base.metadata.create_all(bind=self.engine)
                    
                    # Restaurar dados
                    restore_sql = """
                    INSERT INTO importacoes 
                    (nome_arquivo, tipo_arquivo, formato, tamanho_bytes, 
                     status, total_linhas, linhas_processadas, linhas_erro,
                     mapeamento_colunas, log_processamento, erros, 
                     agente_processamento, created_at, processed_at)
                    SELECT nome_arquivo, tipo_arquivo, formato, tamanho_bytes, 
                           status, total_linhas, linhas_processadas, linhas_erro,
                           mapeamento_colunas, log_processamento, erros, 
                           agente_processamento, created_at, processed_at
                    FROM importacoes_backup
                    """
                    
                    try:
                        conn.execute(text(restore_sql))
                        print("✅ Tabela importacoes atualizada com sucesso!")
                    except:
                        pass  # Pode não haver dados para restaurar
                    
                    # Remover backup
                    try:
                        conn.execute(text("DROP TABLE importacoes_backup"))
                    except:
                        pass
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Erro ao atualizar tabela importacoes: {str(e)}")
            pass

# Instância global do gerenciador
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Retorna instância do gerenciador de banco de dados"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
