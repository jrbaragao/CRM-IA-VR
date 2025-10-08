"""
Utilitário para gerenciar uploads no Google Cloud Storage
Para arquivos grandes e persistência de dados na nuvem
"""

import os
import datetime
from pathlib import Path
from typing import Optional
import streamlit as st
import requests

# Verificar se estamos rodando no Cloud Run
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None

if IS_CLOUD_RUN:
    try:
        from google.cloud import storage
        from google.auth.transport.requests import Request as GoogleAuthRequest
        GCS_AVAILABLE = True
    except ImportError:
        GCS_AVAILABLE = False
else:
    GCS_AVAILABLE = False


class CloudStorageManager:
    """Gerenciador de uploads para Google Cloud Storage"""
    
    def __init__(self):
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'crmia-uploads')
        self.project_id = os.getenv('GCP_PROJECT_ID', 'awesome-carver-463213-r0')
        self.use_gcs = IS_CLOUD_RUN and GCS_AVAILABLE
        
        if self.use_gcs:
            try:
                self.client = storage.Client(project=self.project_id)
                self.bucket = self._get_or_create_bucket()
            except Exception as e:
                st.warning(f"Não foi possível conectar ao Cloud Storage: {e}")
                self.use_gcs = False
    
    def _get_or_create_bucket(self):
        """Obtém ou cria o bucket se não existir"""
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            return bucket
        except Exception:
            # Bucket não existe, vamos tentar criar
            try:
                bucket = self.client.create_bucket(
                    self.bucket_name,
                    location='southamerica-east1'
                )
                st.info(f"Bucket {self.bucket_name} criado com sucesso!")
                return bucket
            except Exception as e:
                st.error(f"Erro ao criar bucket: {e}")
                return None

    def _get_service_account_email(self) -> Optional[str]:
        """Obtém o e-mail da conta de serviço padrão via metadata server (Cloud Run)."""
        if not IS_CLOUD_RUN:
            return None
        try:
            resp = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
                headers={"Metadata-Flavor": "Google"},
                timeout=2,
            )
            if resp.status_code == 200:
                return resp.text.strip()
        except Exception:
            pass
        return None
    
    def upload_file(self, file_content: bytes, filename: str, folder: str = "uploads") -> Optional[str]:
        """
        Faz upload de arquivo para GCS ou salva localmente
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo
            folder: Pasta de destino
            
        Returns:
            Caminho do arquivo (local ou GCS)
        """
        if self.use_gcs and self.bucket:
            # Upload para Cloud Storage
            blob_name = f"{folder}/{filename}"
            blob = self.bucket.blob(blob_name)
            
            try:
                blob.upload_from_string(file_content)
                gcs_path = f"gs://{self.bucket_name}/{blob_name}"
                return gcs_path
            except Exception as e:
                st.error(f"Erro ao fazer upload para GCS: {e}")
                return None

    def generate_signed_upload_url(self, object_name: str, expiration_minutes: int = 30, content_type: Optional[str] = None) -> Optional[str]:
        """
        Gera uma Signed URL (V4) para upload direto via HTTP PUT para o objeto informado.
        
        Usa IAM Service Account Credentials API quando não há chave privada disponível.
        Requer:
        - API 'IAM Service Account Credentials' habilitada
        - Papel 'Service Account Token Creator' na service account do Cloud Run
        """
        if not (self.use_gcs and self.bucket):
            st.error("Cloud Storage não está disponível para gerar Signed URL")
            return None

        try:
            blob = self.bucket.blob(object_name)
            expiration = datetime.timedelta(minutes=expiration_minutes)

            # 1) Tentativa: assinatura com chave privada (local/ADC com JSON key)
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=expiration,
                    method="PUT",
                    content_type=content_type,
                )
                return url
            except AttributeError:
                # Credenciais sem chave privada (ComputeEngineCredentials)
                pass
            except Exception as e:
                # Outros erros, continua para fallback IAM
                st.warning(f"Tentativa de assinatura local falhou: {e}")

            # 2) Fallback: assinatura via IAM (sem chave privada)
            sa_email = self._get_service_account_email()
            if not sa_email:
                raise RuntimeError(
                    "Não foi possível obter o email da service account. "
                    "Verifique se está rodando no Cloud Run."
                )

            # Obtém as credenciais atuais
            credentials = getattr(self.client, "_credentials", None)
            if credentials is None:
                raise RuntimeError("Credenciais não disponíveis no cliente GCS")

            # Cria um signing request que usa IAM Credentials API
            from google.auth import iam
            from google.auth.transport import requests as auth_requests
            
            signing_request = auth_requests.Request()
            
            # Tenta usar google.auth.iam.Signer para assinar via IAM
            try:
                from google.auth.iam import Signer
                
                signer = Signer(
                    request=signing_request,
                    credentials=credentials,
                    service_account_email=sa_email
                )
                
                # Gera URL assinada usando o signer IAM
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=expiration,
                    method="PUT",
                    content_type=content_type,
                    service_account_email=sa_email,
                    access_token=None,  # Força uso do signer
                    credentials=signer,
                )
                return url
                
            except Exception as iam_error:
                st.error(f"Erro ao usar IAM Signer: {iam_error}")
                raise RuntimeError(
                    f"Falha na assinatura via IAM: {iam_error}\n\n"
                    "Verifique:\n"
                    "1. API 'IAM Service Account Credentials' está habilitada\n"
                    "2. Service Account tem papel 'Service Account Token Creator' sobre ela mesma\n"
                    "3. Aguarde 1-2 minutos após configurar para propagação\n\n"
                    "Veja: CONFIGURAR_IAM_SIGNED_URL.md"
                )

        except Exception as e:
            st.error(
                f"❌ Erro ao gerar Signed URL: {e}\n\n"
                "📚 Consulte o guia: CONFIGURAR_IAM_SIGNED_URL.md"
            )
            return None

    def create_resumable_upload_session(self, object_name: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Cria uma sessão de upload recomeçável (resumable) e retorna a URL da sessão.
        Essa abordagem não requer Signed URL e permite upload direto do navegador.
        """
        if not (self.use_gcs and self.bucket):
            st.error("Cloud Storage não está disponível para criar sessão de upload")
            return None
        try:
            blob = self.bucket.blob(object_name)
            session_url = blob.create_resumable_upload_session(content_type=content_type)
            return session_url
        except Exception as e:
            st.error(f"Erro ao criar sessão de upload: {e}")
            return None

    def configure_bucket_cors(self) -> bool:
        """
        Configura CORS do bucket para permitir uploads diretos do navegador.
        Permite métodos: PUT, GET, POST, HEAD, OPTIONS de qualquer origem.
        """
        if not (self.use_gcs and self.bucket):
            return False

        try:
            desired_cors = [{
                "origin": ["*"],
                "responseHeader": [
                    "Content-Type",
                    "Content-Range",
                    "x-goog-resumable",
                    "x-goog-meta-*"] ,
                "method": ["PUT", "GET", "POST", "HEAD", "OPTIONS"],
                "maxAgeSeconds": 3600
            }]

            # Evitar updates desnecessários
            if self.bucket.cors != desired_cors:
                self.bucket.cors = desired_cors
                self.bucket.patch()

            return True
        except Exception as e:
            st.error(f"Erro ao configurar CORS do bucket: {e}")
            return False
        else:
            # Salvar localmente
            local_path = Path(folder) / filename
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                local_path.write_bytes(file_content)
                return str(local_path)
            except Exception as e:
                st.error(f"Erro ao salvar arquivo localmente: {e}")
                return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Baixa arquivo do GCS ou lê localmente
        
        Args:
            file_path: Caminho do arquivo (gs://... ou local)
            
        Returns:
            Conteúdo do arquivo em bytes
        """
        if file_path.startswith('gs://'):
            # Download do Cloud Storage
            if not self.use_gcs:
                st.error("Cloud Storage não está disponível")
                return None
            
            try:
                # Extrair bucket e blob do path
                path_parts = file_path.replace('gs://', '').split('/', 1)
                bucket_name = path_parts[0]
                blob_name = path_parts[1] if len(path_parts) > 1 else ''
                
                bucket = self.client.get_bucket(bucket_name)
                blob = bucket.blob(blob_name)
                
                return blob.download_as_bytes()
            except Exception as e:
                st.error(f"Erro ao baixar arquivo do GCS: {e}")
                return None
        else:
            # Ler localmente
            try:
                return Path(file_path).read_bytes()
            except Exception as e:
                st.error(f"Erro ao ler arquivo local: {e}")
                return None
    
    def list_files(self, folder: str = "uploads") -> list:
        """Lista arquivos no GCS ou localmente"""
        if self.use_gcs and self.bucket:
            try:
                blobs = self.bucket.list_blobs(prefix=f"{folder}/")
                return [f"gs://{self.bucket_name}/{blob.name}" for blob in blobs]
            except Exception as e:
                st.error(f"Erro ao listar arquivos do GCS: {e}")
                return []
        else:
            local_path = Path(folder)
            if local_path.exists():
                return [str(f) for f in local_path.glob("*") if f.is_file()]
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """Deleta arquivo do GCS ou localmente"""
        if file_path.startswith('gs://'):
            if not self.use_gcs:
                return False
            
            try:
                path_parts = file_path.replace('gs://', '').split('/', 1)
                bucket_name = path_parts[0]
                blob_name = path_parts[1] if len(path_parts) > 1 else ''
                
                bucket = self.client.get_bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.delete()
                
                return True
            except Exception as e:
                st.error(f"Erro ao deletar arquivo do GCS: {e}")
                return False
        else:
            try:
                Path(file_path).unlink()
                return True
            except Exception as e:
                st.error(f"Erro ao deletar arquivo local: {e}")
                return False
    
    def get_storage_info(self) -> dict:
        """Retorna informações sobre o storage em uso"""
        return {
            'using_gcs': self.use_gcs,
            'is_cloud_run': IS_CLOUD_RUN,
            'bucket_name': self.bucket_name if self.use_gcs else 'N/A',
            'gcs_available': GCS_AVAILABLE
        }


# Instância global
storage_manager = CloudStorageManager()
