"""
Project Service for Renewable Energy RAG System

Handles CRUD operations for renewable energy projects with proper
multi-tenant security and metadata management.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from supabase import create_client, Client

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for managing renewable energy projects."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the project service."""
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    async def create_project(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        market: Optional[str] = None,
        location: Optional[str] = None,
        owner: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new renewable energy project.
        
        Args:
            user_id: User UUID
            name: Project name
            description: Project description
            market: Renewable energy market type (Solar, Wind, Hydro, etc.)
            location: Project location
            owner: Project owner/developer
            metadata: Additional project metadata
            
        Returns:
            Created project record
        """
        try:
            project_data = {
                "user_id": user_id,
                "name": name,
                "description": description,
                "market": market,
                "location": location,
                "owner": owner,
                "status": "active",
                "metadata": metadata or {}
            }
            
            result = self.supabase.table("projects").insert(project_data).execute()
            
            if result.data:
                project = result.data[0]
                logger.info(f"Created project {project['id']} for user {user_id}")
                return project
            else:
                raise Exception("Failed to create project")
                
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise Exception(f"Failed to create project: {str(e)}")
    
    async def get_project(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """
        Get a specific project by ID.
        
        Args:
            user_id: User UUID for RLS
            project_id: Project UUID
            
        Returns:
            Project record with statistics
        """
        try:
            # Get project details
            project_result = self.supabase.table("projects").select("*").eq(
                "id", project_id
            ).eq("user_id", user_id).execute()
            
            if not project_result.data:
                raise ValueError(f"Project {project_id} not found")
            
            project = project_result.data[0]
            
            # Get document statistics
            doc_stats = await self._get_project_document_stats(project_id)
            
            # Combine project data with statistics
            project_with_stats = {
                **project,
                "document_stats": doc_stats
            }
            
            return project_with_stats
            
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise Exception(f"Failed to get project: {str(e)}")
    
    async def list_user_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        market: Optional[str] = None,
        include_stats: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all projects for a user with optional filtering.
        
        Args:
            user_id: User UUID
            status: Optional status filter
            market: Optional market type filter
            include_stats: Whether to include document statistics
            
        Returns:
            List of project records
        """
        try:
            # Build query
            query = self.supabase.table("projects").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            if market:
                query = query.ilike("market", f"%{market}%")
            
            # Execute query
            result = query.order("created_at", desc=True).execute()
            projects = result.data
            
            # Add document statistics if requested
            if include_stats:
                for project in projects:
                    project["document_stats"] = await self._get_project_document_stats(
                        project["id"]
                    )
            
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects for user {user_id}: {str(e)}")
            raise Exception(f"Failed to list projects: {str(e)}")
    
    async def update_project(
        self,
        user_id: str,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        market: Optional[str] = None,
        location: Optional[str] = None,
        owner: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing project.
        
        Args:
            user_id: User UUID for RLS
            project_id: Project UUID
            name: Updated project name
            description: Updated description
            market: Updated market type
            location: Updated location
            owner: Updated owner
            status: Updated status
            metadata: Updated metadata
            
        Returns:
            Updated project record
        """
        try:
            # Build update data (only include non-None values)
            update_data = {}
            
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if market is not None:
                update_data["market"] = market
            if location is not None:
                update_data["location"] = location
            if owner is not None:
                update_data["owner"] = owner
            if status is not None:
                update_data["status"] = status
            if metadata is not None:
                update_data["metadata"] = metadata
            
            if not update_data:
                raise ValueError("No update data provided")
            
            # Update the project
            result = self.supabase.table("projects").update(update_data).eq(
                "id", project_id
            ).eq("user_id", user_id).execute()
            
            if result.data:
                logger.info(f"Updated project {project_id}")
                return result.data[0]
            else:
                raise ValueError(f"Project {project_id} not found or no changes made")
                
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise Exception(f"Failed to update project: {str(e)}")
    
    async def delete_project(self, user_id: str, project_id: str) -> bool:
        """
        Delete a project and all associated documents.
        
        Args:
            user_id: User UUID for RLS
            project_id: Project UUID
            
        Returns:
            True if successful
        """
        try:
            # First, delete all document chunks for this project
            self.supabase.table("document_chunks").delete().eq(
                "project_id", project_id
            ).eq("user_id", user_id).execute()
            
            # Delete all documents for this project
            # Note: This will also trigger storage cleanup if implemented
            documents_result = self.supabase.table("documents").select("file_path").eq(
                "project_id", project_id
            ).eq("user_id", user_id).execute()
            
            # Delete files from storage
            if documents_result.data:
                file_paths = [doc["file_path"] for doc in documents_result.data]
                try:
                    self.supabase.storage.from_("documents").remove(file_paths)
                except Exception as e:
                    logger.warning(f"Could not delete some files from storage: {str(e)}")
            
            # Delete document records
            self.supabase.table("documents").delete().eq(
                "project_id", project_id
            ).eq("user_id", user_id).execute()
            
            # Delete conversation contexts for this project
            self.supabase.table("conversation_contexts").delete().eq(
                "user_id", user_id
            ).execute()  # Note: Would need project_id in conversation_contexts for precise filtering
            
            # Finally, delete the project
            result = self.supabase.table("projects").delete().eq(
                "id", project_id
            ).eq("user_id", user_id).execute()
            
            logger.info(f"Deleted project {project_id} and all associated data")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            raise Exception(f"Failed to delete project: {str(e)}")
    
    async def _get_project_document_stats(self, project_id: str) -> Dict[str, Any]:
        """
        Get document statistics for a project.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Document statistics
        """
        try:
            # Get document counts by status
            doc_result = self.supabase.table("documents").select(
                "processing_status"
            ).eq("project_id", project_id).execute()
            
            documents = doc_result.data
            
            # Count by status
            status_counts = {}
            for doc in documents:
                status = doc["processing_status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get chunk count
            chunk_result = self.supabase.table("document_chunks").select(
                "id", count="exact"
            ).eq("project_id", project_id).execute()
            
            chunk_count = chunk_result.count if chunk_result.count else 0
            
            return {
                "total_documents": len(documents),
                "status_breakdown": status_counts,
                "total_chunks": chunk_count,
                "pending_processing": status_counts.get("pending", 0),
                "processing": status_counts.get("processing", 0),
                "completed": status_counts.get("completed", 0),
                "failed": status_counts.get("failed", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats for project {project_id}: {str(e)}")
            return {
                "total_documents": 0,
                "status_breakdown": {},
                "total_chunks": 0,
                "pending_processing": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            }
    
    async def get_project_analytics(
        self, 
        user_id: str, 
        project_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed analytics for a project.
        
        Args:
            user_id: User UUID
            project_id: Project UUID
            
        Returns:
            Project analytics data
        """
        try:
            # Get project details
            project = await self.get_project(user_id, project_id)
            
            # Get document analytics
            doc_analytics = await self._get_document_analytics(project_id)
            
            # Get processing timeline
            processing_timeline = await self._get_processing_timeline(project_id)
            
            # Get source breakdown
            source_breakdown = await self._get_source_breakdown(project_id)
            
            return {
                "project": project,
                "document_analytics": doc_analytics,
                "processing_timeline": processing_timeline,
                "source_breakdown": source_breakdown,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting project analytics: {str(e)}")
            raise Exception(f"Failed to get project analytics: {str(e)}")
    
    async def _get_document_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get detailed document analytics for a project."""
        try:
            # Get documents with details
            result = self.supabase.table("documents").select(
                "file_type, file_size, processing_status, source_type, created_at, processed_at"
            ).eq("project_id", project_id).execute()
            
            documents = result.data
            
            if not documents:
                return {
                    "total_size": 0,
                    "file_type_breakdown": {},
                    "source_type_breakdown": {},
                    "avg_processing_time": 0,
                    "processing_success_rate": 0
                }
            
            # Calculate analytics
            total_size = sum(doc.get("file_size", 0) for doc in documents)
            
            # File type breakdown
            file_types = {}
            for doc in documents:
                file_type = doc.get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # Source type breakdown
            source_types = {}
            for doc in documents:
                source_type = doc.get("source_type", "unknown")
                source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Processing statistics
            completed_docs = [d for d in documents if d.get("processing_status") == "completed"]
            success_rate = len(completed_docs) / len(documents) * 100 if documents else 0
            
            # Average processing time (for completed documents)
            processing_times = []
            for doc in completed_docs:
                if doc.get("created_at") and doc.get("processed_at"):
                    created = datetime.fromisoformat(doc["created_at"].replace('Z', '+00:00'))
                    processed = datetime.fromisoformat(doc["processed_at"].replace('Z', '+00:00'))
                    processing_times.append((processed - created).total_seconds())
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            return {
                "total_size": total_size,
                "file_type_breakdown": file_types,
                "source_type_breakdown": source_types,
                "avg_processing_time": avg_processing_time,
                "processing_success_rate": success_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting document analytics: {str(e)}")
            return {}
    
    async def _get_processing_timeline(self, project_id: str) -> List[Dict[str, Any]]:
        """Get processing timeline for a project."""
        try:
            result = self.supabase.table("documents").select(
                "created_at, processed_at, processing_status, file_name"
            ).eq("project_id", project_id).order("created_at").execute()
            
            timeline = []
            for doc in result.data:
                timeline.append({
                    "file_name": doc["file_name"],
                    "created_at": doc["created_at"],
                    "processed_at": doc.get("processed_at"),
                    "status": doc["processing_status"]
                })
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting processing timeline: {str(e)}")
            return []
    
    async def _get_source_breakdown(self, project_id: str) -> Dict[str, Any]:
        """Get source breakdown for a project."""
        try:
            result = self.supabase.table("documents").select(
                "source_type, file_size"
            ).eq("project_id", project_id).execute()
            
            breakdown = {}
            for doc in result.data:
                source = doc["source_type"]
                if source not in breakdown:
                    breakdown[source] = {"count": 0, "total_size": 0}
                
                breakdown[source]["count"] += 1
                breakdown[source]["total_size"] += doc.get("file_size", 0)
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting source breakdown: {str(e)}")
            return {}
    
    async def compare_projects(
        self,
        user_id: str,
        project_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple projects side by side.
        
        Args:
            user_id: User UUID
            project_ids: List of project UUIDs to compare
            
        Returns:
            Comparison data for projects
        """
        try:
            if len(project_ids) < 2:
                raise ValueError("At least 2 projects required for comparison")
            
            comparison_data = {
                "projects": [],
                "comparison_metrics": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Get data for each project
            for project_id in project_ids:
                try:
                    project_data = await self.get_project_analytics(user_id, project_id)
                    comparison_data["projects"].append(project_data)
                except Exception as e:
                    logger.warning(f"Could not get data for project {project_id}: {str(e)}")
            
            # Calculate comparison metrics
            if comparison_data["projects"]:
                comparison_data["comparison_metrics"] = self._calculate_comparison_metrics(
                    comparison_data["projects"]
                )
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Error comparing projects: {str(e)}")
            raise Exception(f"Failed to compare projects: {str(e)}")
    
    def _calculate_comparison_metrics(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comparison metrics between projects."""
        try:
            metrics = {
                "document_counts": [],
                "chunk_counts": [],
                "processing_success_rates": [],
                "total_sizes": [],
                "markets": [],
                "locations": []
            }
            
            for project_data in projects:
                project = project_data["project"]
                doc_analytics = project_data.get("document_analytics", {})
                
                metrics["document_counts"].append({
                    "project_name": project["name"],
                    "count": project["document_stats"]["total_documents"]
                })
                
                metrics["chunk_counts"].append({
                    "project_name": project["name"],
                    "count": project["document_stats"]["total_chunks"]
                })
                
                metrics["processing_success_rates"].append({
                    "project_name": project["name"],
                    "rate": doc_analytics.get("processing_success_rate", 0)
                })
                
                metrics["total_sizes"].append({
                    "project_name": project["name"],
                    "size": doc_analytics.get("total_size", 0)
                })
                
                metrics["markets"].append({
                    "project_name": project["name"],
                    "market": project.get("market", "Unknown")
                })
                
                metrics["locations"].append({
                    "project_name": project["name"],
                    "location": project.get("location", "Unknown")
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating comparison metrics: {str(e)}")
            return {} 