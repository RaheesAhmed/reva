from typing import Optional, List, Dict, Any
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()

class TavilySearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up")
    max_results: Optional[int] = Field(default=5, description="Maximum number of results to return")
    search_depth: Optional[str] = Field(default="advanced", description="Search depth (basic or advanced)")
    include_answer: Optional[bool] = Field(default=True, description="Include AI-generated answer")
    include_raw_content: Optional[bool] = Field(default=True, description="Include raw content")
    include_images: Optional[bool] = Field(default=True, description="Include images in results")
    include_domains: Optional[List[str]] = Field(default=None, description="List of domains to include")
    exclude_domains: Optional[List[str]] = Field(default=None, description="List of domains to exclude")

class TavilySearchWrapper:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")

    def create_search_tool(self, params: Dict[str, Any]) -> TavilySearchResults:
        return TavilySearchResults(
            api_key=self.api_key,
            **params
        )

    async def search(self, params: TavilySearchInput) -> Dict[str, Any]:
        try:
            # Convert params to dict and filter out None values
            search_params = params.dict(exclude_none=True)
            query = search_params.pop('query')  # Remove query from params as it's passed separately

            # Create search tool with remaining parameters
            search_tool = self.create_search_tool(search_params)
            
            # Perform the search
            results = await search_tool.ainvoke(query)
            
            return {
                "status": "success",
                "results": results,
                "metadata": {
                    "query": query,
                    **search_params
                }
            }
        except Exception as e:
            logger.error(f"Error in Tavily search: {str(e)}")
            raise Exception(f"Failed to perform Tavily search: {str(e)}")

# search = TavilySearchResults(max_results=2)
# search_results = search.invoke("what is the weather in SF")
# print(search_results)
