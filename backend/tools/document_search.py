from typing import Optional, Dict, Any, List
from langchain.tools import BaseTool # type: ignore
from pydantic import BaseModel, Field # type: ignore
from vectorstore.supabase_store import VectorStoreManager # type: ignore
import asyncio

class DocumentSearchInput(BaseModel):
    """Input schema for document search."""
    query: str = Field(description="The search query to find relevant documents")
    k: Optional[int] = Field(default=5, description="Number of documents to return")
    threshold: Optional[float] = Field(default=0.5, description="Minimum similarity threshold (0-1)")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata filter")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "query": "What are the key market trends in Manhattan office space?",
                "k": 3,
                "threshold": 0.7,
                "filter": {"property_type": "office", "location": "Manhattan"}
            }]
        }
    }

class DocumentSearchTool(BaseTool):
    name: str = "document_search"
    description: str = """Searches through internal documents and knowledge base for relevant information.
    Use this tool when you need to find specific information about properties, markets, or past analyses.
    The search is semantic, meaning it understands the meaning of your query, not just keywords.
    You can optionally filter results by metadata fields."""
    
    args_schema: type[BaseModel] = DocumentSearchInput
    vector_store: VectorStoreManager = Field(default_factory=VectorStoreManager)

    def _run(
        self,
        query: str,
        k: Optional[int] = 5,
        threshold: Optional[float] = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        This method is required by the BaseTool class but we'll raise NotImplementedError
        since we only want to use the async version.
        """
        raise NotImplementedError("DocumentSearchTool only supports async operations")

    async def _arun(
        self,
        query: str,
        k: Optional[int] = 5,
        threshold: Optional[float] = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Async implementation of document search.
        
        Args:
            query: Search query
            k: Number of documents to return
            threshold: Minimum similarity threshold
            filter: Optional metadata filter
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            # Perform the search with scores
            results = await self.vector_store.query(
                query=query,
                k=k,
                threshold=threshold,
                return_scores=True,
                filter=filter
            )
            
            # Format the results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            
            return {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "results": [],
                "total_results": 0
            } 