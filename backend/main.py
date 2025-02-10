import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Request #type: ignore
from fastapi.responses import StreamingResponse 
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from pydantic import BaseModel #type: ignore
from typing import Optional, List, Dict, Any
from agents.real_estate_agent import RealEstateAgent
from logger import setup_logger
import uvicorn #type: ignore
from vectorstore.supabase_store import VectorStoreManager
import tempfile
import os
from pathlib import Path
from data.loaders import DocumentLoader
from data.processors import DocumentProcessor
from datetime import datetime
import uuid
from routes.auth import router as admin_router
from routes.user_auth import router as user_router
from routes.dashboard import router as dashboard_router
from routes.admin import router as admin_router
from tools.custom_web_search import TavilySearchWrapper, TavilySearchInput
from config.supabase import get_supabase

logger = setup_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CRE AI Assistant API",
    description="API for Commercial Real Estate AI Assistant tools and chat",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase admin client
supabase_admin = get_supabase(auth=False)

# Initialize agent and vector store
agent = RealEstateAgent(
    model_name="gpt-4-turbo-preview",
    temperature=0.7
)

@app.on_event("startup")
async def startup_event():
    """Initialize async components on startup."""
    try:
        await agent.initialize()
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}")
        raise

vector_store = VectorStoreManager()

# Initialize search wrapper
tavily_search = TavilySearchWrapper()

# Request Models
class ChatRequest(BaseModel):
    message: str
    tools: Optional[List[str]] = None

class TavilySearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    search_depth: Optional[str] = "advanced"
    include_answer: Optional[bool] = True
    include_raw_content: Optional[bool] = True
    include_images: Optional[bool] = True
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None

class FREDDataRequest(BaseModel):
    series_id: str
    observation_start: Optional[str] = None
    observation_end: Optional[str] = None
    units: Optional[str] = "lin"

class MarketAnalysisRequest(BaseModel):
    location: str
    property_type: str
    analysis_type: Optional[str] = "comprehensive"

class PropertyAnalysisRequest(BaseModel):
    property_id: str
    analysis_type: Optional[str] = "full"

class ValuePropositionRequest(BaseModel):
    property_details: Dict[str, Any]
    target_audience: Optional[str] = None

class DocumentSearchInput(BaseModel):
    query: str
    k: Optional[int] = 5
    threshold: Optional[float] = 0.5
    filter: Optional[Dict[str, Any]] = None

# System Message Models
class SystemMessageCreate(BaseModel):
    message: str

class SystemMessageResponse(BaseModel):
    id: str
    message: str
    is_active: bool
    created_at: str
    updated_at: str

@app.get("/")
async def root():
    """Root endpoint to verify API is running."""
    return {
        "status": "success",
        "message": "CRE AI Assistant API is running",
        "version": "1.0.0"
    }


# Include routers
try:
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(user_router, prefix="/api/users", tags=["users"])
    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
except Exception as e:
    logger.error(f"Error including routers: {str(e)}")
    raise

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with the AI assistant using all available tools with streaming support.
    """
    try:
        # If tools are specified, filter the agent's tools
        original_tools = agent.tools.copy()  # Save original tools
        if request.tools:
            available_tools = {
                'search': agent.tools[4],  # TavilySearchTool
                'economic-data': agent.tools[5],  # FREDEconomicTool
                'market-analysis': agent.tools[1],  # MarketAnalysisTool
                'property-analysis': agent.tools[0],  # PropertyAnalysisTool
                'value-proposition': agent.tools[2],  # ValuePropositionTool
                'document-search': agent.tools[3],  # DocumentSearchTool
            }
            filtered_tools = [available_tools[tool] for tool in request.tools if tool in available_tools]
            agent.tools = filtered_tools

        async def generate():
            try:
                # Run agent asynchronously
                response = await agent.arun(request.message)
                
                # Restore original tools
                if request.tools:
                    agent.tools = original_tools
                
                # Stream the response in smaller chunks
                words = response.split()
                for i in range(0, len(words), 3):  # Send 3 words at a time
                    chunk = " ".join(words[i:i+3])
                    yield f"data: {chunk}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for smoother streaming
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in chat: {str(e)}")
                yield f"data: ERROR: {str(e)}\n\n"
                # Restore original tools on error
                if request.tools:
                    agent.tools = original_tools

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        # Restore original tools on error
        if request.tools and 'original_tools' in locals():
            agent.tools = original_tools
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/search")
async def search_web(request: TavilySearchRequest) -> Dict[str, Any]:
    """
    Search the web using Tavily's AI-powered search engine.
    """
    try:
        tool = agent.tools[4]  # TavilySearchTool
        result = await tool._arun(query=request.query, max_results=request.max_results)
        return {"results": result}
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/economic-data")
async def get_economic_data(request: FREDDataRequest) -> Dict[str, Any]:
    """
    Fetch economic data from FRED (Federal Reserve Economic Data).
    """
    try:
        tool = agent.tools[5]  # FREDEconomicTool
        result = await tool._arun(
            series_id=request.series_id,
            observation_start=request.observation_start,
            observation_end=request.observation_end,
            units=request.units
        )
        return {"data": result}
    except Exception as e:
        logger.error(f"Error fetching economic data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/market-analysis")
async def analyze_market(request: MarketAnalysisRequest) -> Dict[str, Any]:
    """
    Perform market analysis for a specific location and property type.
    """
    try:
        tool = agent.tools[1]  # MarketAnalysisTool
        result = await tool._arun(
            market_area=request.location,
            property_type=request.property_type,
            timeframe="12 months"  # Default timeframe
        )
        return {"analysis": result}
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/property-analysis")
async def analyze_property(request: PropertyAnalysisRequest) -> Dict[str, Any]:
    """
    Analyze a specific property.
    """
    try:
        tool = agent.tools[0]  # PropertyAnalysisTool
        result = await tool._arun(property_id=request.property_id)
        return {"analysis": result}
    except Exception as e:
        logger.error(f"Error in property analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/value-proposition")
async def generate_value_proposition(request: ValuePropositionRequest) -> Dict[str, Any]:
    """
    Generate a value proposition for a property.
    """
    try:
        tool = agent.tools[2]  # ValuePropositionTool
        result = await tool._arun(
            property_type=request.property_details.get("type", ""),
            target_audience=request.target_audience or "investors",
            property_features=request.property_details.get("features", [])
        )
        return {"value_proposition": result}
    except Exception as e:
        logger.error(f"Error generating value proposition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/document-search")
async def search_documents(request: DocumentSearchInput) -> Dict[str, Any]:
    """
    Search through internal documents and knowledge base.
    """
    try:
        tool = agent.tools[3]  # DocumentSearchTool
        result = await tool._arun(
            query=request.query,
            k=request.k,
            threshold=request.threshold,
            filter=request.filter
        )
        return {"results": result}
    except Exception as e:
        logger.error(f"Error in document search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/custom-web-search")
async def custom_web_search(request: TavilySearchInput) -> Dict[str, Any]:
    """
    Advanced web search using Tavily's AI-powered search engine with all available features.
    
    Parameters:
    - query: Search query string
    - max_results: Maximum number of results (default: 5)
    - search_depth: Search depth - 'basic' or 'advanced' (default: 'advanced')
    - include_answer: Include AI-generated answer (default: True)
    - include_raw_content: Include raw content of search results (default: True)
    - include_images: Include images in search results (default: True)
    - include_domains: List of domains to include in search (optional)
    - exclude_domains: List of domains to exclude from search (optional)
    """
    try:
        # Process domain lists if provided as comma-separated strings
        if isinstance(request.include_domains, str):
            request.include_domains = [d.strip() for d in request.include_domains.split(',') if d.strip()]
        if isinstance(request.exclude_domains, str):
            request.exclude_domains = [d.strip() for d in request.exclude_domains.split(',') if d.strip()]
            
        # Convert string boolean values to actual booleans
        for field in ['include_answer', 'include_raw_content', 'include_images']:
            if hasattr(request, field) and isinstance(getattr(request, field), str):
                setattr(request, field, getattr(request, field).lower() == 'true')

        result = await tavily_search.search(request)
        return result
    except Exception as e:
        logger.error(f"Error in custom web search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/admin/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a new document."""
    try:
        # Save the uploaded file temporarily
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Load and process the document using DocumentLoader
            documents = DocumentLoader.load_file(temp_path)
        
            if not documents:
                raise ValueError("No content could be extracted from the file")
            
            # Prepare metadata
            metadata = {
                "id": str(uuid.uuid4()),  # Generate a unique ID
                "name": file.filename,
                "type": file.content_type,
                "size": len(content),
                "source": file.filename,  # Use filename as source
                "uploaded_at": datetime.now().isoformat()
            }
            
            # Create document in vector store with processed documents
            document_id = await vector_store.create_from_file(
                documents=documents,
                metadata=metadata
            )

            if document_id:
                return {"status": "success", "data": {"id": document_id, "metadata": metadata}}
            else:
                raise ValueError("Failed to create document in vector store")
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except ValueError as e:
        logger.error(f"Invalid file type: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/admin/system-message", response_model=SystemMessageResponse)
async def get_system_message():
    """Get the current active system message."""
    try:
        # First try to get active message from the table directly
        result = supabase_admin.table('system_messages').select('*').eq('is_active', True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            message_data = result.data[0]
            # Ensure all required fields are present
            return {
                "id": message_data.get("id", str(uuid.uuid4())),
                "message": message_data.get("message", ""),
                "is_active": message_data.get("is_active", True),
                "created_at": message_data.get("created_at", datetime.now().isoformat()),
                "updated_at": message_data.get("updated_at", datetime.now().isoformat())
            }
            
        # If no active message found, return default message
        default_message = {
            "id": str(uuid.uuid4()),
            "message": """You are an expert commercial real estate AI assistant. 
            You help analyze properties, market conditions, and create compelling value propositions.
            You have access to internal documents and can search through them for relevant information.
            You can perform real-time web searches for current market trends and news.
            You can access Federal Reserve economic data for deep market analysis.
            
            When analyzing comparable properties:
            1. Focus on the most relevant adjustments and their impact on value
            2. Explain market trends and their implications clearly
            3. Present value ranges with context and confidence levels
            4. Highlight key factors influencing the analysis
            
            You communicate professionally and focus on providing actionable insights backed by data.
            
            You have access to powerful calculation tools for:
            
            Financial Metrics (use financial_calculator):
            - ROI (Return on Investment)
            - Cap Rate (Capitalization Rate)
            - NOI (Net Operating Income)
            
            Market Metrics (use market_metrics_calculator):
            - Vacancy Rate
            - Absorption Rate
            - Rent Growth Rate
            
            Property Metrics (use property_metrics_calculator):
            - Price per Square Foot
            - Operating Expense Ratio
            - DSCR (Debt Service Coverage Ratio)
            
            Make sure to use the correct calculator for each metric.
            Always show your calculations and explain the results in a clear, professional manner.""",
            "is_active": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return default_message
    except Exception as e:
        logger.error(f"Error getting system message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/system-message", response_model=SystemMessageResponse)
async def create_system_message(message: SystemMessageCreate):
    """Create a new system message and set it as active."""
    try:
        # First, deactivate all existing messages with a proper WHERE clause
        supabase_admin.table('system_messages').update(
            {"is_active": False}
        ).neq('id', '00000000-0000-0000-0000-000000000000').execute()  # This ensures we update all records
        
        # Then create the new active message
        new_message = {
            "message": message.message,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase_admin.table('system_messages').insert(new_message).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create system message")
            
        return result.data[0]
        
    except Exception as e:
        logger.error(f"Error creating system message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/admin/system-message/{message_id}", response_model=SystemMessageResponse)
async def update_system_message(message_id: str, message: SystemMessageCreate):
    """Update an existing system message."""
    try:
        result = supabase_admin.table('system_messages').update({
            "message": message.message,
            "updated_at": datetime.now().isoformat()
        }).eq("id", message_id).execute()
        
        if result.data:
            return result.data[0]
        raise HTTPException(status_code=404, detail="System message not found")
    except Exception as e:
        logger.error(f"Error updating system message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/system-message/{message_id}")
async def delete_system_message(message_id: str):
    """Delete a system message."""
    try:
        result = supabase_admin.table('system_messages').delete().eq("id", message_id).execute()
        if result.data:
            return {"status": "success", "message": "System message deleted"}
        raise HTTPException(status_code=404, detail="System message not found")
    except Exception as e:
        logger.error(f"Error deleting system message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)