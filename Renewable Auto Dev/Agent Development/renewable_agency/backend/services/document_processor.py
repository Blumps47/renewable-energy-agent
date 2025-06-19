"""
Document Processing Service for Renewable Energy RAG System

Handles text extraction from various file formats, intelligent chunking with context,
and embedding generation using OpenAI's API.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import tiktoken

import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from supabase import create_client, Client
import numpy as np

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents into searchable chunks with embeddings."""
    
    def __init__(self, supabase_url: str, supabase_key: str, openai_api_key: str):
        """Initialize the document processor."""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        openai.api_key = openai_api_key
        
        # Initialize text splitter with renewable energy optimized settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """
        Process a document by extracting text, chunking, and generating embeddings.
        
        Args:
            document_id: UUID of the document to process
            
        Returns:
            Dictionary with processing results and statistics
        """
        try:
            # Update status to processing
            self.supabase.table("documents").update({
                "processing_status": "processing"
            }).eq("id", document_id).execute()
            
            # Get document record
            doc_result = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            
            if not doc_result.data:
                raise ValueError(f"Document {document_id} not found")
            
            document = doc_result.data[0]
            
            # Get project information for context
            project_result = self.supabase.table("projects").select("*").eq(
                "id", document["project_id"]
            ).execute()
            
            project = project_result.data[0] if project_result.data else {}
            
            # Extract text from document
            text_content = await self._extract_text(document)
            
            if not text_content.strip():
                raise ValueError("No text content extracted from document")
            
            # Create chunks with context
            chunks = await self._create_contextual_chunks(text_content, document, project)
            
            # Generate embeddings for chunks
            embeddings = await self._generate_embeddings([chunk["content"] for chunk in chunks])
            
            # Store chunks with embeddings
            chunk_records = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_record = {
                    "user_id": document["user_id"],
                    "document_id": document_id,
                    "project_id": document["project_id"],
                    "chunk_index": i,
                    "content": chunk["content"],
                    "embedding": embedding,
                    "token_count": chunk["token_count"],
                    "metadata": chunk["metadata"]
                }
                chunk_records.append(chunk_record)
            
            # Batch insert chunks
            self.supabase.table("document_chunks").insert(chunk_records).execute()
            
            # Update document status
            self.supabase.table("documents").update({
                "processing_status": "completed",
                "processed_at": datetime.utcnow().isoformat(),
                "chunk_count": len(chunk_records),
                "error_message": None
            }).eq("id", document_id).execute()
            
            processing_stats = {
                "document_id": document_id,
                "chunks_created": len(chunk_records),
                "total_tokens": sum(chunk["token_count"] for chunk in chunks),
                "processing_time": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            logger.info(f"Successfully processed document {document_id}: {processing_stats}")
            return processing_stats
            
        except Exception as e:
            error_msg = f"Error processing document {document_id}: {str(e)}"
            logger.error(error_msg)
            
            # Update document with error status
            self.supabase.table("documents").update({
                "processing_status": "failed",
                "error_message": error_msg
            }).eq("id", document_id).execute()
            
            raise Exception(error_msg)
    
    async def _extract_text(self, document: Dict[str, Any]) -> str:
        """
        Extract text content from document based on file type.
        
        Args:
            document: Document record from database
            
        Returns:
            Extracted text content
        """
        try:
            # Download file from Supabase Storage
            file_content = self.supabase.storage.from_("documents").download(
                document["file_path"]
            )
            
            # Create temporary file for processing
            temp_file_path = f"/tmp/{document['id']}{document['file_type']}"
            
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            # Extract text based on file type
            file_type = document["file_type"].lower()
            
            if file_type == '.pdf':
                loader = PyPDFLoader(temp_file_path)
                pages = loader.load()
                text_content = "\n\n".join([page.page_content for page in pages])
                
            elif file_type in ['.docx', '.doc']:
                loader = Docx2txtLoader(temp_file_path)
                doc = loader.load()
                text_content = doc[0].page_content
                
            elif file_type in ['.txt', '.md']:
                loader = TextLoader(temp_file_path, encoding='utf-8')
                doc = loader.load()
                text_content = doc[0].page_content
                
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Clean up temporary file
            os.remove(temp_file_path)
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from {document['file_name']}: {str(e)}")
            raise
    
    async def _create_contextual_chunks(
        self, 
        text_content: str, 
        document: Dict[str, Any], 
        project: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create contextual chunks with renewable energy project metadata.
        
        Args:
            text_content: Raw text content from document
            document: Document record
            project: Project record
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text_content)
        
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Count tokens
            token_count = len(self.tokenizer.encode(chunk_text))
            
            # Create contextual prefix for better retrieval
            context_prefix = self._create_context_prefix(document, project)
            
            # Combine context with chunk content
            contextual_content = f"{context_prefix}\n\n{chunk_text}"
            
            # Create metadata for the chunk
            chunk_metadata = {
                "chunk_index": i,
                "file_name": document["file_name"],
                "project_name": project.get("name", "Unknown"),
                "project_market": project.get("market", "Unknown"),
                "project_location": project.get("location", "Unknown"),
                "project_owner": project.get("owner", "Unknown"),
                "source_type": document["source_type"],
                "file_type": document["file_type"],
                "original_token_count": token_count,
                "context_added": True,
                "chunk_start_char": i * 800,  # Approximate character position
                "renewable_energy_context": True
            }
            
            chunks.append({
                "content": contextual_content,
                "token_count": len(self.tokenizer.encode(contextual_content)),
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def _create_context_prefix(self, document: Dict[str, Any], project: Dict[str, Any]) -> str:
        """
        Create a context prefix for chunks to improve retrieval relevance.
        
        Args:
            document: Document record
            project: Project record
            
        Returns:
            Context prefix string
        """
        context_parts = []
        
        # Project context
        if project.get("name"):
            context_parts.append(f"Project: {project['name']}")
        
        if project.get("market"):
            context_parts.append(f"Renewable Energy Type: {project['market']}")
        
        if project.get("location"):
            context_parts.append(f"Location: {project['location']}")
        
        if project.get("owner"):
            context_parts.append(f"Project Owner: {project['owner']}")
        
        # Document context
        context_parts.append(f"Document: {document['file_name']}")
        
        # Create context string
        context_prefix = "RENEWABLE ENERGY PROJECT DOCUMENT\n" + " | ".join(context_parts)
        
        return context_prefix
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI's API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Process in batches to avoid API limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                response = await openai.Embedding.acreate(
                    model="text-embedding-3-small",
                    input=batch_texts
                )
                
                # Extract embeddings
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    async def reprocess_document(self, document_id: str) -> Dict[str, Any]:
        """
        Reprocess an existing document (useful for updates or errors).
        
        Args:
            document_id: UUID of document to reprocess
            
        Returns:
            Processing results
        """
        try:
            # Delete existing chunks
            self.supabase.table("document_chunks").delete().eq(
                "document_id", document_id
            ).execute()
            
            # Reset document status
            self.supabase.table("documents").update({
                "processing_status": "pending",
                "chunk_count": 0,
                "processed_at": None,
                "error_message": None
            }).eq("id", document_id).execute()
            
            # Process document
            return await self.process_document(document_id)
            
        except Exception as e:
            logger.error(f"Error reprocessing document {document_id}: {str(e)}")
            raise
    
    async def get_processing_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get the processing status of a document.
        
        Args:
            document_id: UUID of document
            
        Returns:
            Status information
        """
        try:
            result = self.supabase.table("documents").select(
                "processing_status, chunk_count, processed_at, error_message"
            ).eq("id", document_id).execute()
            
            if not result.data:
                raise ValueError(f"Document {document_id} not found")
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error getting processing status: {str(e)}")
            raise
    
    async def batch_process_documents(
        self, 
        user_id: str, 
        project_id: Optional[str] = None,
        status_filter: str = "pending"
    ) -> Dict[str, Any]:
        """
        Process multiple documents in batch.
        
        Args:
            user_id: User UUID
            project_id: Optional project UUID to filter by
            status_filter: Processing status to filter by
            
        Returns:
            Batch processing results
        """
        try:
            # Get documents to process
            query = self.supabase.table("documents").select("id").eq(
                "user_id", user_id
            ).eq("processing_status", status_filter)
            
            if project_id:
                query = query.eq("project_id", project_id)
            
            result = query.execute()
            document_ids = [doc["id"] for doc in result.data]
            
            batch_results = {
                "total_documents": len(document_ids),
                "processed": 0,
                "failed": 0,
                "results": []
            }
            
            # Process each document
            for doc_id in document_ids:
                try:
                    processing_result = await self.process_document(doc_id)
                    batch_results["processed"] += 1
                    batch_results["results"].append({
                        "document_id": doc_id,
                        "status": "success",
                        "result": processing_result
                    })
                except Exception as e:
                    batch_results["failed"] += 1
                    batch_results["results"].append({
                        "document_id": doc_id,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0 