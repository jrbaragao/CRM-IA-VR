"""
Utilitário simplificado para uploads locais
Versão para trabalho acadêmico - sem complexidade de Cloud Storage
"""

import os
from pathlib import Path
from typing import Optional, Dict
import streamlit as st

# Verificar se estamos rodando no Cloud Run (para avisos)
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None


class CloudStorageManager:
    """Gerenciador simplificado de uploads - apenas local"""
    
    def __init__(self):
        # Sempre usar storage local (sem GCS)
        self.use_gcs = False
        self.bucket_name = None
        
        # Criar diretório de uploads se não existir
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Definir limites baseado no ambiente
        if IS_CLOUD_RUN:
            # Cloud Run tem limite de 32MB por request
            self.max_file_size_mb = 32
            self.environment = "Cloud Run"
        else:
            # Local permite arquivos maiores
            self.max_file_size_mb = 200
            self.environment = "Local"
    
    def get_storage_info(self) -> Dict:
        """Retorna informações sobre o storage"""
        return {
            'using_gcs': False,
            'bucket_name': None,
            'environment': self.environment,
            'max_file_size_mb': self.max_file_size_mb,
            'is_cloud_run': IS_CLOUD_RUN
        }
    
    def save_uploaded_file(self, uploaded_file, subfolder: str = "") -> Optional[Path]:
        """
        Salva arquivo enviado no diretório local
        
        Args:
            uploaded_file: Arquivo do st.file_uploader
            subfolder: Subpasta opcional dentro de uploads/
            
        Returns:
            Path do arquivo salvo ou None se falhar
        """
        try:
            # Criar subpasta se especificada
            if subfolder:
                target_dir = self.upload_dir / subfolder
                target_dir.mkdir(exist_ok=True, parents=True)
            else:
                target_dir = self.upload_dir
            
            # Caminho completo do arquivo
            file_path = target_dir / uploaded_file.name
            
            # Salvar arquivo
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return file_path
            
        except Exception as e:
            st.error(f"Erro ao salvar arquivo {uploaded_file.name}: {str(e)}")
            return None
    
    def get_upload_path(self, filename: str, subfolder: str = "") -> Path:
        """Retorna o caminho onde um arquivo seria salvo"""
        if subfolder:
            return self.upload_dir / subfolder / filename
        return self.upload_dir / filename
    
    def file_exists(self, filename: str, subfolder: str = "") -> bool:
        """Verifica se arquivo existe"""
        file_path = self.get_upload_path(filename, subfolder)
        return file_path.exists()
    
    def list_files(self, subfolder: str = "") -> list:
        """Lista arquivos no diretório de uploads"""
        if subfolder:
            target_dir = self.upload_dir / subfolder
        else:
            target_dir = self.upload_dir
        
        if not target_dir.exists():
            return []
        
        return [f.name for f in target_dir.iterdir() if f.is_file()]
    
    def delete_file(self, filename: str, subfolder: str = "") -> bool:
        """Deleta um arquivo"""
        try:
            file_path = self.get_upload_path(filename, subfolder)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            st.error(f"Erro ao deletar arquivo {filename}: {str(e)}")
            return False
    
    def get_file_size_limit_message(self) -> str:
        """Retorna mensagem sobre limite de tamanho"""
        if IS_CLOUD_RUN:
            return f"⚠️ **Ambiente Cloud Run**: Limite de **{self.max_file_size_mb}MB** por arquivo devido às limitações do Cloud Run."
        else:
            return f"✅ **Ambiente Local**: Limite de **{self.max_file_size_mb}MB** por arquivo."


# Instância global do gerenciador
storage_manager = CloudStorageManager()
