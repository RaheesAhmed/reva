from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.tools import ToolException

from vectorstore.supabase_store import VectorStoreManager
from logger import setup_logger

logger = setup_logger(__name__)

class SearchQuery(BaseModel):
    query: str = Field(description="The search query to execute")
    k: Optional[int] = Field(default=5, description="Number of results to return")
    threshold: Optional[float] = Field(
        default=0.5,
        description="Minimum relevance score threshold"
    )

@tool(args_schema=SearchQuery)
def search_documents(
    query: str,
    k: int = 5,
    threshold: float = 0.5
) -> str:
    """
    Search through internal documents using vector similarity search.
    Returns the most relevant document passages.
    """
    try:
        vector_store = VectorStoreManager()
        results = vector_store.query(query, k=k, threshold=threshold)
        
        if not results:
            return "No relevant documents found for the given query."
            
        formatted_results = []
        for doc, score in results:
            formatted_results.append(
                f"Relevance Score: {score:.2f}\n"
                f"Content: {doc.page_content}\n"
                f"Source: {doc.metadata.get('source', 'Unknown')}\n"
            )
            
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error in document search: {str(e)}")
        raise ToolException(f"Search failed: {str(e)}")