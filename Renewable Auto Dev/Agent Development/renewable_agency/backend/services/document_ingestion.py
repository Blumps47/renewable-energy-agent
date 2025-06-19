"""
Document Ingestion Service for Renewable Energy RAG System

Handles document synchronization from external sources (Dropbox, Google Drive)
and local file uploads with proper metadata and security.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pathlib import Path

import dropbox
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from supabase import create_client, Client
import aiofiles

from ..models import Document, DocumentCreate

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    """Service for ingesting documents from various sources into the RAG system."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the document ingestion service."""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
        
    async def sync_dropbox_folder(
        self, 
        user_id: str, 
        project_id: str, 
        access_token: str, 
        folder_path: str = ""
    ) -> Dict[str, Any]:
        """
        Synchronize documents from a Dropbox folder.
        
        Args:
            user_id: The user's UUID
            project_id: The project UUID to associate documents with
            access_token: Dropbox access token
            folder_path: Path to the Dropbox folder (empty for root)
            
        Returns:
            Dictionary with sync results and statistics
        """
        try:
            dbx = dropbox.Dropbox(access_token)
            
            # List files in the folder
            if folder_path:
                result = dbx.files_list_folder(folder_path)
            else:
                result = dbx.files_list_folder("")
                
            sync_stats = {
                "total_files": 0,
                "processed_files": 0,
                "skipped_files": 0,
                "errors": []
            }
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    sync_stats["total_files"] += 1
                    
                    # Check if file extension is supported
                    file_ext = Path(entry.name).suffix.lower()
                    if file_ext not in self.supported_extensions:
                        sync_stats["skipped_files"] += 1
                        logger.info(f"Skipping unsupported file: {entry.name}")
                        continue
                    
                    try:
                        # Check if document already exists
                        existing_doc = self.supabase.table("documents").select("*").eq(
                            "source_id", entry.id
                        ).eq("user_id", user_id).execute()
                        
                        if existing_doc.data:
                            # Update existing document if modified
                            existing = existing_doc.data[0]
                            if existing["metadata"].get("rev") != entry.rev:
                                await self._update_dropbox_document(
                                    dbx, entry, existing["id"], user_id, project_id
                                )
                                sync_stats["processed_files"] += 1
                        else:
                            # Create new document
                            await self._create_dropbox_document(
                                dbx, entry, user_id, project_id
                            )
                            sync_stats["processed_files"] += 1
                            
                    except Exception as e:
                        error_msg = f"Error processing {entry.name}: {str(e)}"
                        sync_stats["errors"].append(error_msg)
                        logger.error(error_msg)
                        
            return sync_stats
            
        except Exception as e:
            logger.error(f"Dropbox sync error: {str(e)}")
            raise Exception(f"Failed to sync Dropbox folder: {str(e)}")
    
    async def sync_google_drive_folder(
        self,
        user_id: str,
        project_id: str,
        credentials: Dict[str, Any],
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronize documents from a Google Drive folder.
        
        Args:
            user_id: The user's UUID
            project_id: The project UUID to associate documents with
            credentials: Google OAuth2 credentials dict
            folder_id: Google Drive folder ID (None for root)
            
        Returns:
            Dictionary with sync results and statistics
        """
        try:
            creds = Credentials.from_authorized_user_info(credentials)
            service = build('drive', 'v3', credentials=creds)
            
            # Build query for files
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
                
            # List files
            results = service.files().list(
                q=query,
                fields="files(id,name,size,mimeType,modifiedTime,parents)"
            ).execute()
            
            files = results.get('files', [])
            
            sync_stats = {
                "total_files": 0,
                "processed_files": 0,
                "skipped_files": 0,
                "errors": []
            }
            
            for file_item in files:
                sync_stats["total_files"] += 1
                
                # Check if file type is supported
                mime_type = file_item.get('mimeType', '')
                if not self._is_supported_mime_type(mime_type):
                    sync_stats["skipped_files"] += 1
                    continue
                
                try:
                    # Check if document already exists
                    existing_doc = self.supabase.table("documents").select("*").eq(
                        "source_id", file_item['id']
                    ).eq("user_id", user_id).execute()
                    
                    if existing_doc.data:
                        # Update existing document if modified
                        existing = existing_doc.data[0]
                        if existing["metadata"].get("modifiedTime") != file_item.get("modifiedTime"):
                            await self._update_google_drive_document(
                                service, file_item, existing["id"], user_id, project_id
                            )
                            sync_stats["processed_files"] += 1
                    else:
                        # Create new document
                        await self._create_google_drive_document(
                            service, file_item, user_id, project_id
                        )
                        sync_stats["processed_files"] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing {file_item['name']}: {str(e)}"
                    sync_stats["errors"].append(error_msg)
                    logger.error(error_msg)
                    
            return sync_stats
            
        except Exception as e:
            logger.error(f"Google Drive sync error: {str(e)}")
            raise Exception(f"Failed to sync Google Drive folder: {str(e)}")
    
    async def upload_local_document(
        self,
        user_id: str,
        project_id: str,
        file_path: str,
        file_name: str,
        file_content: bytes
    ) -> str:
        """
        Upload a local document to the system.
        
        Args:
            user_id: The user's UUID
            project_id: The project UUID
            file_path: Local file path for storage
            file_name: Original file name
            file_content: File content as bytes
            
        Returns:
            Document ID of the created document
        """
        try:
            # Check file extension
            file_ext = Path(file_name).suffix.lower()
            if file_ext not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Store file in Supabase Storage
            storage_path = f"{user_id}/{project_id}/{file_name}"
            
            # Upload to storage bucket
            self.supabase.storage.from_("documents").upload(
                storage_path, file_content
            )
            
            # Create document record
            document_data = {
                "user_id": user_id,
                "project_id": project_id,
                "file_name": file_name,
                "file_path": storage_path,
                "file_size": len(file_content),
                "file_type": file_ext,
                "source_type": "upload",
                "processing_status": "pending",
                "metadata": {
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "original_path": file_path
                }
            }
            
            result = self.supabase.table("documents").insert(document_data).execute()
            
            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to create document record")
                
        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            raise Exception(f"Failed to upload document: {str(e)}")
    
    async def _create_dropbox_document(
        self, 
        dbx: dropbox.Dropbox, 
        entry: dropbox.files.FileMetadata,
        user_id: str,
        project_id: str
    ) -> str:
        """Create a new document from Dropbox file."""
        try:
            # Download file content
            _, response = dbx.files_download(entry.path_lower)
            file_content = response.content
            
            # Store in Supabase Storage
            storage_path = f"{user_id}/{project_id}/dropbox/{entry.name}"
            
            self.supabase.storage.from_("documents").upload(
                storage_path, file_content
            )
            
            # Create document record
            document_data = {
                "user_id": user_id,
                "project_id": project_id,
                "file_name": entry.name,
                "file_path": storage_path,
                "file_size": entry.size,
                "file_type": Path(entry.name).suffix.lower(),
                "source_type": "dropbox",
                "source_id": entry.id,
                "processing_status": "pending",
                "metadata": {
                    "rev": entry.rev,
                    "client_modified": entry.client_modified.isoformat() if entry.client_modified else None,
                    "server_modified": entry.server_modified.isoformat() if entry.server_modified else None,
                    "path_lower": entry.path_lower
                }
            }
            
            result = self.supabase.table("documents").insert(document_data).execute()
            return result.data[0]["id"]
            
        except Exception as e:
            logger.error(f"Error creating Dropbox document: {str(e)}")
            raise
    
    async def _update_dropbox_document(
        self,
        dbx: dropbox.Dropbox,
        entry: dropbox.files.FileMetadata,
        document_id: str,
        user_id: str,
        project_id: str
    ):
        """Update an existing Dropbox document."""
        try:
            # Download updated file content
            _, response = dbx.files_download(entry.path_lower)
            file_content = response.content
            
            # Update storage
            storage_path = f"{user_id}/{project_id}/dropbox/{entry.name}"
            
            # Remove old file and upload new one
            try:
                self.supabase.storage.from_("documents").remove([storage_path])
            except:
                pass  # File might not exist
                
            self.supabase.storage.from_("documents").upload(
                storage_path, file_content
            )
            
            # Update document record
            update_data = {
                "file_size": entry.size,
                "processing_status": "pending",
                "processed_at": None,
                "metadata": {
                    "rev": entry.rev,
                    "client_modified": entry.client_modified.isoformat() if entry.client_modified else None,
                    "server_modified": entry.server_modified.isoformat() if entry.server_modified else None,
                    "path_lower": entry.path_lower,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
            
            self.supabase.table("documents").update(update_data).eq("id", document_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating Dropbox document: {str(e)}")
            raise
    
    async def _create_google_drive_document(
        self,
        service,
        file_item: Dict[str, Any],
        user_id: str,
        project_id: str
    ) -> str:
        """Create a new document from Google Drive file."""
        try:
            # Download file content
            file_content = service.files().get_media(fileId=file_item['id']).execute()
            
            # Store in Supabase Storage
            storage_path = f"{user_id}/{project_id}/google_drive/{file_item['name']}"
            
            self.supabase.storage.from_("documents").upload(
                storage_path, file_content
            )
            
            # Create document record
            document_data = {
                "user_id": user_id,
                "project_id": project_id,
                "file_name": file_item['name'],
                "file_path": storage_path,
                "file_size": int(file_item.get('size', 0)),
                "file_type": self._get_file_extension_from_mime(file_item.get('mimeType', '')),
                "source_type": "google_drive",
                "source_id": file_item['id'],
                "processing_status": "pending",
                "metadata": {
                    "mimeType": file_item.get('mimeType'),
                    "modifiedTime": file_item.get('modifiedTime'),
                    "parents": file_item.get('parents', [])
                }
            }
            
            result = self.supabase.table("documents").insert(document_data).execute()
            return result.data[0]["id"]
            
        except Exception as e:
            logger.error(f"Error creating Google Drive document: {str(e)}")
            raise
    
    async def _update_google_drive_document(
        self,
        service,
        file_item: Dict[str, Any],
        document_id: str,
        user_id: str,
        project_id: str
    ):
        """Update an existing Google Drive document."""
        try:
            # Download updated file content
            file_content = service.files().get_media(fileId=file_item['id']).execute()
            
            # Update storage
            storage_path = f"{user_id}/{project_id}/google_drive/{file_item['name']}"
            
            # Remove old file and upload new one
            try:
                self.supabase.storage.from_("documents").remove([storage_path])
            except:
                pass  # File might not exist
                
            self.supabase.storage.from_("documents").upload(
                storage_path, file_content
            )
            
            # Update document record
            update_data = {
                "file_size": int(file_item.get('size', 0)),
                "processing_status": "pending",
                "processed_at": None,
                "metadata": {
                    "mimeType": file_item.get('mimeType'),
                    "modifiedTime": file_item.get('modifiedTime'),
                    "parents": file_item.get('parents', []),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
            
            self.supabase.table("documents").update(update_data).eq("id", document_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating Google Drive document: {str(e)}")
            raise
    
    def _is_supported_mime_type(self, mime_type: str) -> bool:
        """Check if the MIME type is supported."""
        supported_mimes = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain',
            'text/markdown'
        }
        return mime_type in supported_mimes
    
    def _get_file_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_to_ext = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/msword': '.doc',
            'text/plain': '.txt',
            'text/markdown': '.md'
        }
        return mime_to_ext.get(mime_type, '.txt')
    
    async def get_user_documents(
        self, 
        user_id: str, 
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get documents for a user, optionally filtered by project and status.
        
        Args:
            user_id: The user's UUID
            project_id: Optional project ID to filter by
            status: Optional processing status to filter by
            
        Returns:
            List of document records
        """
        try:
            query = self.supabase.table("documents").select("*").eq("user_id", user_id)
            
            if project_id:
                query = query.eq("project_id", project_id)
            
            if status:
                query = query.eq("processing_status", status)
                
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Error fetching user documents: {str(e)}")
            raise Exception(f"Failed to fetch documents: {str(e)}")
    
    async def delete_document(self, user_id: str, document_id: str) -> bool:
        """
        Delete a document and its associated chunks.
        
        Args:
            user_id: The user's UUID
            document_id: The document UUID to delete
            
        Returns:
            True if successful
        """
        try:
            # Get document info
            doc_result = self.supabase.table("documents").select("*").eq(
                "id", document_id
            ).eq("user_id", user_id).execute()
            
            if not doc_result.data:
                raise ValueError("Document not found")
            
            document = doc_result.data[0]
            
            # Delete from storage
            try:
                self.supabase.storage.from_("documents").remove([document["file_path"]])
            except:
                logger.warning(f"Could not delete file from storage: {document['file_path']}")
            
            # Delete document chunks
            self.supabase.table("document_chunks").delete().eq(
                "document_id", document_id
            ).execute()
            
            # Delete document record
            self.supabase.table("documents").delete().eq("id", document_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise Exception(f"Failed to delete document: {str(e)}") 