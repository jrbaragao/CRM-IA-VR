"""
Classe base para todos os agentes LlamaIndex
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    Document,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
from llama_index.vector_stores import ChromaVectorStore
import chromadb
from pathlib import Path
import yaml
import logging
from datetime import datetime

from ..config.settings import settings

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
            collection_name: Nome da coleção no ChromaDB
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
        if collection_name:
            self._setup_vector_store()
        
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
    
    def _setup_vector_store(self):
        """Configura o vector store com ChromaDB"""
        # Cliente ChromaDB
        chroma_client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir)
        )
        
        # Coleção
        collection = chroma_client.get_or_create_collection(
            name=self.collection_name
        )
        
        # Vector store
        vector_store = ChromaVectorStore(
            chroma_collection=collection
        )
        
        # Storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )
        
        # Service context
        service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embed_model
        )
        
        # Criar ou carregar índice
        try:
            self.index = load_index_from_storage(
                storage_context,
                service_context=service_context
            )
            logger.info(f"Índice carregado para {self.agent_name}")
        except:
            self.index = VectorStoreIndex(
                [],
                storage_context=storage_context,
                service_context=service_context
            )
            logger.info(f"Novo índice criado para {self.agent_name}")
        
        # Query engine
        self.query_engine = self.index.as_query_engine()
    
    def add_documents(self, documents: List[Document]):
        """Adiciona documentos ao índice"""
        if self.index:
            for doc in documents:
                self.index.insert(doc)
            logger.info(f"{len(documents)} documentos adicionados ao {self.agent_name}")
    
    def query(self, query_str: str, **kwargs) -> Any:
        """Executa uma query no índice"""
        if not self.query_engine:
            raise ValueError("Query engine não configurado")
        
        return self.query_engine.query(query_str, **kwargs)
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Registra ação do agente"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_name,
            'action': action,
            'details': details or {}
        }
        logger.info(f"[{self.agent_name}] {action}")
        return log_entry
    
    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any:
        """
        Processa dados específicos do agente
        Deve ser implementado por cada agente
        """
        pass
    
    def get_system_prompt(self, prompt_key: str, **kwargs) -> str:
        """Obtém e formata um prompt do sistema"""
        prompt_template = self.prompts.get(prompt_key, "")
        if kwargs:
            return prompt_template.format(**kwargs)
        return prompt_template
