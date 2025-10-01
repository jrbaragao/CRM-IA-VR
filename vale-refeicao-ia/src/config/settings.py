"""
Configurações do sistema de Vale Refeição
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações gerais
    app_name: str = "Sistema de Agente de IA"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Configurações de servidor (cloud-friendly)
    port: int = Field(default=8501, env="PORT")  # Para Google Cloud Run
    host: str = Field(default="0.0.0.0", env="HOST")
    
    # Banco de dados
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/vale_refeicao",
        env="DATABASE_URL"
    )
    
    # OpenAI/LlamaIndex
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # ChromaDB (Vector Store)
    chroma_persist_dir: Path = Field(
        default=Path("./chroma_db"),
        env="CHROMA_PERSIST_DIR"
    )
    
    # Configurações de upload
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_extensions: str = Field(
        default="csv,xlsx,xls",
        env="ALLOWED_EXTENSIONS"
    )
    
    # Configurações dos agentes
    agent_temperature: float = Field(default=0.1, env="AGENT_TEMPERATURE")
    agent_max_retries: int = Field(default=3, env="AGENT_MAX_RETRIES")
    
    # Configurações de cálculo de vale refeição
    valor_dia_util: float = Field(default=35.00, env="VALOR_DIA_UTIL")
    desconto_funcionario_pct: float = Field(default=0.20, env="DESCONTO_FUNCIONARIO_PCT")
    dias_uteis_mes_padrao: int = Field(default=22, env="DIAS_UTEIS_MES_PADRAO")
    
    # Diretórios
    upload_dir: Path = Field(default=Path("./uploads"), env="UPLOAD_DIR")
    export_dir: Path = Field(default=Path("./exports"), env="EXPORT_DIR")
    prompts_dir: Path = Field(default=Path("./prompts"), env="PROMPTS_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Criar diretórios se não existirem
        self.upload_dir.mkdir(exist_ok=True)
        self.export_dir.mkdir(exist_ok=True)
        self.chroma_persist_dir.mkdir(exist_ok=True)
        
    @property
    def max_file_size_bytes(self) -> int:
        """Retorna o tamanho máximo do arquivo em bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Retorna lista de extensões permitidas"""
        # Adiciona ponto se não tiver
        exts = self.allowed_extensions.split(',')
        return [f".{ext.strip()}" if not ext.strip().startswith('.') else ext.strip() for ext in exts]
    
    @property
    def database_ready(self) -> bool:
        """Verifica se o banco de dados está configurado"""
        return self.database_url and self.database_url != "postgresql://user:password@localhost:5432/vale_refeicao"
    
    @property
    def openai_ready(self) -> bool:
        """Verifica se a OpenAI está configurada"""
        return bool(self.openai_api_key)

# Instância global das configurações
settings = Settings()
