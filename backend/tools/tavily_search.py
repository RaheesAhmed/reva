from typing import Optional, List, ClassVar
from langchain.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()

class TavilySearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up")
    max_results: Optional[int] = Field(default=3, description="Maximum number of results to return")
    search_depth: Optional[str] = Field(
        default="advance",
        description="Search depth (basic or advanced)"
    )

class TavilySearchTool(StructuredTool):
    name: ClassVar[str] = "tavily_search"
    description: ClassVar[str] = "Search the web for real-time information using Tavily's AI-powered search engine"
    args_schema: ClassVar[type[BaseModel]] = TavilySearchInput
    
    def _run(self, query: str, max_results: int = 3, search_depth: str = "basic") -> List[dict]:
        try:
            search = TavilySearchResults(
                max_results=max_results,
                search_depth=search_depth,
                api_key=os.getenv("TAVILY_API_KEY")
            )
            results = search.invoke(query)
            return results
        except Exception as e:
            logger.error(f"Error in Tavily search: {str(e)}")
            raise Exception(f"Failed to perform Tavily search: {str(e)}")

    async def _arun(self, query: str, max_results: int = 3, search_depth: str = "basic") -> List[dict]:
        """
        Async implementation of Tavily search.
        """
        try:
            search = TavilySearchResults(
                max_results=max_results,
                search_depth=search_depth,
                api_key=os.getenv("TAVILY_API_KEY")
            )
            # Use ainvoke for async operation
            results = await search.ainvoke(query)
            return results
        except Exception as e:
            logger.error(f"Error in async Tavily search: {str(e)}")
            raise Exception(f"Failed to perform async Tavily search: {str(e)}")

# search = TavilySearchResults(max_results=2)
# search_results = search.invoke("what is the weather in SF")
# print(search_results)
