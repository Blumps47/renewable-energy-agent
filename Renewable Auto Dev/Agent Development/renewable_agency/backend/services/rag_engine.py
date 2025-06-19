"""
RAG Query Engine for Renewable Energy RAG System

Handles vector similarity search, result ranking, and context preparation
for the AI agent with proper multi-tenant security.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio

import openai
import numpy as np
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class RAGQueryEngine:
    """Engine for querying documents using vector similarity search."""
    
    def __init__(self, supabase_url: str, supabase_key: str, openai_api_key: str):
        """Initialize the RAG query engine."""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        openai.api_key = openai_api_key
        
    async def query_documents(
        self,
        user_id: str,
        query: str,
        project_ids: Optional[List[str]] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Query documents using vector similarity search.
        
        Args:
            user_id: User UUID for RLS filtering
            query: Search query string
            project_ids: Optional list of project UUIDs to filter by
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score for results
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)
            
            # Build the search query with RLS filtering
            search_results = await self._vector_search(
                user_id=user_id,
                query_embedding=query_embedding,
                project_ids=project_ids,
                limit=limit * 2  # Get more results to filter by threshold
            )
            
            # Calculate similarities and filter by threshold
            ranked_results = []
            for result in search_results:
                similarity_score = self._calculate_cosine_similarity(
                    query_embedding, result["embedding"]
                )
                
                if similarity_score >= similarity_threshold:
                    result["similarity_score"] = similarity_score
                    ranked_results.append(result)
            
            # Sort by similarity score and limit results
            ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            final_results = ranked_results[:limit]
            
            # Prepare context string for agent
            context_string = self._prepare_context_string(final_results)
            
            # Get source attribution information
            sources = self._extract_source_info(final_results)
            
            return {
                "query": query,
                "results_count": len(final_results),
                "context": context_string,
                "sources": sources,
                "chunks": final_results,
                "search_metadata": {
                    "user_id": user_id,
                    "project_ids": project_ids,
                    "similarity_threshold": similarity_threshold,
                    "total_candidates": len(search_results),
                    "filtered_results": len(final_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise Exception(f"Failed to query documents: {str(e)}")
    
    async def _generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for the search query.
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-3-small",
                input=[query]
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    async def _vector_search(
        self,
        user_id: str,
        query_embedding: List[float],
        project_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search with RLS filtering.
        
        Args:
            user_id: User UUID for RLS
            query_embedding: Query embedding vector
            project_ids: Optional project UUIDs to filter by
            limit: Maximum results to return
            
        Returns:
            List of matching document chunks
        """
        try:
            # Build SQL query for vector search with RLS
            # Note: This uses Supabase's vector similarity search
            
            # Base query with RLS filtering
            query_builder = self.supabase.table("document_chunks").select(
                """
                id,
                content,
                embedding,
                metadata,
                document_id,
                project_id,
                chunk_index,
                token_count,
                documents!inner(file_name, file_type, source_type),
                projects!inner(name, market, location, owner)
                """
            ).eq("user_id", user_id)
            
            # Add project filtering if specified
            if project_ids:
                query_builder = query_builder.in_("project_id", project_ids)
            
            # Execute the query to get all chunks (we'll do similarity calculation in Python)
            # In production, you'd want to use Supabase's vector similarity functions
            result = query_builder.limit(1000).execute()  # Get a reasonable subset
            
            chunks = result.data
            
            # Calculate similarities and get top results
            # In production, this would be done in the database for efficiency
            chunk_similarities = []
            for chunk in chunks:
                similarity = self._calculate_cosine_similarity(
                    query_embedding, chunk["embedding"]
                )
                chunk["similarity_score"] = similarity
                chunk_similarities.append(chunk)
            
            # Sort by similarity and return top results
            chunk_similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            return chunk_similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            raise
    
    def _calculate_cosine_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
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
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def _prepare_context_string(self, results: List[Dict[str, Any]]) -> str:
        """
        Prepare context string for the AI agent from search results.
        
        Args:
            results: List of search result chunks
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        context_parts.append("RELEVANT RENEWABLE ENERGY PROJECT DOCUMENTS:")
        context_parts.append("=" * 60)
        
        for i, result in enumerate(results, 1):
            # Extract metadata
            metadata = result.get("metadata", {})
            document_info = result.get("documents", {})
            project_info = result.get("projects", {})
            
            # Create source header
            source_header = f"\n[SOURCE {i}] "
            if project_info.get("name"):
                source_header += f"Project: {project_info['name']} | "
            if document_info.get("file_name"):
                source_header += f"Document: {document_info['file_name']} | "
            source_header += f"Relevance: {result['similarity_score']:.2f}"
            
            context_parts.append(source_header)
            context_parts.append("-" * 40)
            
            # Add project context if available
            project_context = []
            if project_info.get("market"):
                project_context.append(f"Type: {project_info['market']}")
            if project_info.get("location"):
                project_context.append(f"Location: {project_info['location']}")
            if project_info.get("owner"):
                project_context.append(f"Owner: {project_info['owner']}")
            
            if project_context:
                context_parts.append("Project Context: " + " | ".join(project_context))
            
            # Add the chunk content
            content = result["content"]
            # Remove the context prefix we added during processing
            if "RENEWABLE ENERGY PROJECT DOCUMENT" in content:
                content_lines = content.split("\n")
                # Find where the actual content starts (after the context prefix)
                content_start = 0
                for j, line in enumerate(content_lines):
                    if line.strip() and not line.startswith("RENEWABLE ENERGY PROJECT DOCUMENT") and "|" not in line:
                        content_start = j
                        break
                content = "\n".join(content_lines[content_start:])
            
            context_parts.append(f"Content: {content.strip()}")
            context_parts.append("")  # Empty line between sources
        
        context_parts.append("=" * 60)
        context_parts.append("END OF DOCUMENT CONTEXT")
        
        return "\n".join(context_parts)
    
    def _extract_source_info(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source attribution information from search results.
        
        Args:
            results: List of search result chunks
            
        Returns:
            List of source information dictionaries
        """
        sources = []
        
        for result in results:
            document_info = result.get("documents", {})
            project_info = result.get("projects", {})
            metadata = result.get("metadata", {})
            
            source = {
                "document_id": result["document_id"],
                "project_id": result["project_id"],
                "chunk_id": result["id"],
                "file_name": document_info.get("file_name", "Unknown"),
                "project_name": project_info.get("name", "Unknown"),
                "project_market": project_info.get("market", "Unknown"),
                "similarity_score": result["similarity_score"],
                "chunk_index": result["chunk_index"],
                "source_type": document_info.get("source_type", "unknown"),
                "file_type": document_info.get("file_type", "unknown")
            }
            
            sources.append(source)
        
        return sources
    
    async def query_by_project(
        self,
        user_id: str,
        project_id: str,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Query documents within a specific project.
        
        Args:
            user_id: User UUID
            project_id: Project UUID to search within
            query: Search query
            limit: Maximum results
            
        Returns:
            Search results for the specific project
        """
        return await self.query_documents(
            user_id=user_id,
            query=query,
            project_ids=[project_id],
            limit=limit
        )
    
    async def get_similar_chunks(
        self,
        user_id: str,
        chunk_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find chunks similar to a given chunk.
        
        Args:
            user_id: User UUID
            chunk_id: Reference chunk UUID
            limit: Maximum results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar chunks
        """
        try:
            # Get the reference chunk
            ref_result = self.supabase.table("document_chunks").select(
                "embedding"
            ).eq("id", chunk_id).eq("user_id", user_id).execute()
            
            if not ref_result.data:
                raise ValueError(f"Chunk {chunk_id} not found")
            
            ref_embedding = ref_result.data[0]["embedding"]
            
            # Find similar chunks
            return await self._vector_search(
                user_id=user_id,
                query_embedding=ref_embedding,
                limit=limit + 1  # +1 to exclude the reference chunk itself
            )
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            raise
    
    async def get_project_summary(
        self,
        user_id: str,
        project_id: str,
        query: str = "project overview and key information"
    ) -> Dict[str, Any]:
        """
        Get a summary of project documents using RAG.
        
        Args:
            user_id: User UUID
            project_id: Project UUID
            query: Query to guide summary generation
            
        Returns:
            Project summary with source attribution
        """
        try:
            # Query for project overview information
            results = await self.query_by_project(
                user_id=user_id,
                project_id=project_id,
                query=query,
                limit=10
            )
            
            # Get project details
            project_result = self.supabase.table("projects").select("*").eq(
                "id", project_id
            ).eq("user_id", user_id).execute()
            
            project_info = project_result.data[0] if project_result.data else {}
            
            return {
                "project_info": project_info,
                "document_context": results["context"],
                "sources": results["sources"],
                "summary_query": query,
                "documents_found": results["results_count"]
            }
            
        except Exception as e:
            logger.error(f"Error generating project summary: {str(e)}")
            raise
    
    async def search_across_projects(
        self,
        user_id: str,
        query: str,
        market_filter: Optional[str] = None,
        location_filter: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search across all user projects with optional filters.
        
        Args:
            user_id: User UUID
            query: Search query
            market_filter: Optional market type filter (e.g., "Solar", "Wind")
            location_filter: Optional location filter
            limit: Maximum results
            
        Returns:
            Cross-project search results
        """
        try:
            # Get project IDs that match filters
            project_query = self.supabase.table("projects").select("id").eq("user_id", user_id)
            
            if market_filter:
                project_query = project_query.ilike("market", f"%{market_filter}%")
            
            if location_filter:
                project_query = project_query.ilike("location", f"%{location_filter}%")
            
            project_result = project_query.execute()
            project_ids = [p["id"] for p in project_result.data]
            
            if not project_ids:
                return {
                    "query": query,
                    "results_count": 0,
                    "context": "No projects found matching the specified filters.",
                    "sources": [],
                    "chunks": [],
                    "search_metadata": {
                        "market_filter": market_filter,
                        "location_filter": location_filter,
                        "projects_searched": 0
                    }
                }
            
            # Search within filtered projects
            results = await self.query_documents(
                user_id=user_id,
                query=query,
                project_ids=project_ids,
                limit=limit
            )
            
            results["search_metadata"]["market_filter"] = market_filter
            results["search_metadata"]["location_filter"] = location_filter
            results["search_metadata"]["projects_searched"] = len(project_ids)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in cross-project search: {str(e)}")
            raise 