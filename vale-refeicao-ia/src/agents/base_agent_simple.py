"""
Classe base simplificada para todos os agentes LlamaIndex
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from llama_index.core import (
    VectorStoreIndex,
    Document,
    Settings
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from pathlib import Path
import yaml
import logging
from datetime import datetime

from ..config.settings import settings

# Configurar logger
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Classe base para agentes de processamento"""
    
    def __init__(self, 
                 agent_name: str,
                 prompt_file: str,
                 collection_name: str = None):
        """
        Inicializa o agente base
        
        Args:
            agent_name: Nome do agente
            prompt_file: Arquivo YAML com prompts
            collection_name: Nome da coleção (não usado nesta versão simplificada)
        """
        self.agent_name = agent_name
        self.prompt_file = prompt_file
        self.collection_name = collection_name or f"{agent_name}_collection"
        self.prompts = self._load_prompts()
        self.llm = None
        self.embed_model = None
        self.index = None
        self.query_engine = None
        self._setup_llm()
        self._setup_simple_index()
        
    def _load_prompts(self) -> Dict[str, str]:
        """Carrega prompts do arquivo YAML"""
        prompt_path = settings.prompts_dir / self.prompt_file
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Arquivo de prompts não encontrado: {prompt_path}")
            return {}
    
    def _setup_llm(self):
        """Configura o modelo LLM"""
        if not settings.openai_ready:
            logger.warning("OpenAI API key não configurada")
            return
            
        self.llm = OpenAI(
            model=settings.openai_model,
            temperature=settings.agent_temperature,
            api_key=settings.openai_api_key
        )
        
        self.embed_model = OpenAIEmbedding(
            api_key=settings.openai_api_key
        )
        
        # Configurar Settings globais
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
    
    def _setup_simple_index(self):
        """Configura índice simples em memória"""
        if self.llm and self.embed_model:
            # Criar índice vazio em memória
            self.index = VectorStoreIndex.from_documents(
                [],
                embed_model=self.embed_model
            )
            
            # Criar query engine
            self.query_engine = self.index.as_query_engine(
                llm=self.llm
            )
    
    def add_knowledge(self, text: str, metadata: Dict[str, Any] = None):
        """Adiciona conhecimento ao índice"""
        if not self.index:
            return
            
        doc = Document(
            text=text,
            metadata=metadata or {}
        )
        
        self.index.insert(doc)
    
    def query(self, question: str) -> str:
        """Consulta o índice"""
        if not self.query_engine:
            return "Query engine não configurado"
            
        response = self.query_engine.query(question)
        return str(response)
    
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """
        Processa dados específicos do agente
        Deve ser implementado por cada agente
        """
        pass
    
    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        """Retorna um prompt formatado"""
        prompt_template = self.prompts.get(prompt_key, "")
        if prompt_template:
            return prompt_template.format(**kwargs)
        return ""
    
    def log_processing(self, message: str, level: str = "info"):
        """Registra log do processamento"""
        log_message = f"[{self.agent_name}] {message}"
        
        if level == "debug":
            logger.debug(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "error":
            logger.error(log_message)
        else:
            logger.info(log_message)
