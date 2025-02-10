# Commercial Real Estate AI Assistant

A FastAPI-based backend service for a Commercial Real Estate AI assistant specializing in multi-tenant retail properties in the Metro Atlanta area.

## Core Features

### 1. AI Chat Interface

```python
POST /chat
{
    "message": str,
    "tools": Optional[List[str]]  # Specific tools to use
}
```

- Streaming responses enabled
- Dynamic tool selection based on context
- Configurable model parameters (temperature, etc.)

### 2. Document Management

```python
GET /admin/documents
POST /admin/documents/upload
DELETE /admin/documents/{document_id}
```

- Vector store integration with Supabase
- Semantic search capabilities
- Metadata tracking (upload time, file info)
- Automatic text chunking and embedding

### 3. Authentication

```python
# Admin Auth
POST /api/auth/admin/login
{
    "email": str,
    "password": str
}

# User Auth
POST /api/users/register
POST /api/users/login
POST /api/users/logout
```

- JWT-based admin authentication
- Supabase user authentication
- Role-based access control

### 4. Analysis Tools

#### Property Analysis

```python
POST /tools/property-analysis
{
    "property_id": str,
    "analysis_type": str = "full"  # Optional
}
```

- Property metrics calculation
- Investment potential assessment
- Detailed property evaluation
- Tenant mix analysis
- Location analysis

#### Market Analysis

```python
POST /tools/market-analysis
{
    "location": str,
    "property_type": str,
    "analysis_type": str = "comprehensive"  # Optional
}
```

- Market trends analysis
- Vacancy rates tracking
- Absorption rate calculation
- Rent growth analysis
- Sub-market reports
- Traffic count data

#### Comparable Analysis

```python
POST /tools/comparable-analysis
{
    "property_type": str,
    "location": str,
    "building_size": float,
    "year_built": int,
    "quality_rating": int,  # 1-5 scale
    "max_comps": int = 5
}
```

- Recent sales data analysis
- Market-based adjustments
- Value range estimation
- Confidence scoring
- Supporting market data

#### Sales Strategy

```python
POST /tools/sales-strategy
{
    "property_type": str,
    "property_value": float,
    "location": str,
    "market_conditions": Dict[str, Any],
    "timeline_constraints": Optional[str],
    "special_conditions": Optional[Dict[str, Any]]
}
```

- Sale method recommendations (public/private/auction)
- Timing optimization
- Market condition analysis
- Timeline estimation
- Key considerations

#### Document Search

```python
POST /tools/document-search
{
    "query": str,
    "k": int = 5,
    "threshold": float = 0.5,
    "filter": Dict[str, Any]
}
```

- Semantic search through documents
- Configurable similarity threshold
- Metadata-based filtering

#### Economic Data (FRED)

```python
POST /tools/economic-data
{
    "series_id": str,
    "observation_start": str,
    "observation_end": str,
    "units": str = "lin"
}
```

- Federal Reserve economic data integration
- Time series analysis
- Custom date range queries

## Project Structure

### Backend

```
backend/
├── agents/
│   ├── base_agent.py         # Base agent functionality
│   └── real_estate_agent.py  # CRE-specific agent
├── config/
│   └── settings.py           # Environment and app settings
├── data/
│   ├── loaders.py           # Document loading utilities
│   └── processors.py        # Text processing utilities
├── prompts/
│   └── system_prompt.py     # System prompts for AI
├── tools/
│   ├── cold_call.py        # Cold calling scripts
│   ├── comparable_analysis.py # Property comparables
│   ├── document_search.py  # Vector search
│   ├── fred_economic.py    # FRED integration
│   ├── market_analysis.py  # Market analytics
│   ├── object_handler.py   # Objection handling
│   ├── property_analysis.py # Property evaluation
│   ├── sales_strategy_advisor.py # Sales strategy
│   ├── search_tools.py     # Search utilities
│   ├── tavily_search.py    # Web search
│   └── value_proposition.py # Value prop generation
├── vectorstore/
│   ├── setup.sql          # Vector store setup
│   └── supabase_store.py  # Vector store management
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── logger.py             # Logging configuration
├── main.py              # FastAPI application
└── requirements.txt     # Python dependencies
```

### Frontend

```
frontend/
├── app/                   # Next.js 15 app directory
│   ├── admin/            # Admin dashboard pages
│   ├── chat/             # Chat interface pages
│   ├── favicon.ico       # Site favicon
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout component
│   └── page.tsx          # Home page component
├── components/           # Reusable React components
│   ├── ui/              # shadcn/ui components
│   ├── Chat.tsx         # Chat interface component
│   ├── Navbar.tsx       # Navigation component
│   └── ToolSelector.tsx # Tool selection component
├── hooks/               # Custom React hooks
├── lib/                 # Utility functions and configs
├── public/             # Static assets
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── components.json    # shadcn/ui configuration
├── eslint.config.mjs  # ESLint configuration
├── next.config.ts    # Next.js configuration
├── package.json      # Node dependencies
├── postcss.config.mjs # PostCSS configuration
├── tailwind.config.ts # Tailwind CSS configuration
└── tsconfig.json     # TypeScript configuration
```

## Setup

1. Environment Variables

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
VECTOR_STORE_TABLE=documents
VECTOR_STORE_QUERY=match_documents

FRED_API_KEY=...
JWT_SECRET_KEY=...
TAVILY_API_KEY=...

LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

3. Start Server

```bash
uvicorn main:app --reload
```

## Error Handling

The application implements comprehensive error handling:

- Input validation via Pydantic models
- Async operation timeouts
- Graceful error responses
- Detailed logging via custom logger

## Key Features

1. **Specialized Focus**

   - Multi-tenant retail properties
   - Property size: 5,000-50,000 sq ft
   - Non-anchored strip centers
   - Metro Atlanta area (45 markets)

2. **Data Sources**

   - QPublic Website integration
   - CoStar Data (when available)
   - GDOT traffic counts
   - FRED economic indicators

3. **Analysis Capabilities**
   - Tenant credit ratings
   - Business evaluation
   - Property stabilization potential
   - Leasing strategy optimization
   - Market-based valuations

## API Endpoints

### Root Endpoint

```http
GET /
```

Response:

```json
{
  "status": "success",
  "message": "CRE AI Assistant API is running",
  "version": "1.0.0"
}
```

### 1. Chat Interface

```http
POST /chat
```

Request:

```json
{
  "message": "string",
  "tools": [
    "search",
    "economic-data",
    "market-analysis",
    "property-analysis",
    "value-proposition",
    "document-search"
  ] // Optional
}
```

Response: Server-Sent Events (SSE) stream

- Content-Type: text/event-stream
- Streaming response with chunks of text
- Final message: "data: [DONE]"

### 2. Tools

#### Web Search

```http
POST /tools/search
```

Request:

```json
{
  "query": "string",
  "max_results": 5, // Optional
  "search_depth": "advanced", // Optional
  "include_answer": true, // Optional
  "include_raw_content": true, // Optional
  "include_images": true, // Optional
  "include_domains": ["string"], // Optional
  "exclude_domains": ["string"] // Optional
}
```

#### Economic Data (FRED)

```http
POST /tools/economic-data
```

Request:

```json
{
  "series_id": "string",
  "observation_start": "string", // Optional
  "observation_end": "string", // Optional
  "units": "lin" // Optional
}
```

#### Market Analysis

```http
POST /tools/market-analysis
```

Request:

```json
{
  "location": "string",
  "property_type": "string",
  "analysis_type": "comprehensive" // Optional
}
```

#### Property Analysis

```http
POST /tools/property-analysis
```

Request:

```json
{
  "property_id": "string",
  "analysis_type": "full" // Optional
}
```

#### Value Proposition

```http
POST /tools/value-proposition
```

Request:

```json
{
  "property_details": {
    "type": "string",
    "features": []
  },
  "target_audience": "string" // Optional
}
```

#### Document Search

```http
POST /tools/document-search
```

Request:

```json
{
  "query": "string",
  "k": 5, // Optional
  "threshold": 0.5, // Optional
  "filter": {} // Optional
}
```

#### Custom Web Search

```http
POST /tools/custom-web-search
```

Request:

```json
{
  "query": "string",
  "max_results": 5, // Optional
  "search_depth": "advanced", // Optional
  "include_answer": true, // Optional
  "include_raw_content": true, // Optional
  "include_images": true, // Optional
  "include_domains": ["string"], // Optional
  "exclude_domains": ["string"] // Optional
}
```

### 3. Document Management

```http
POST /admin/documents/upload
```

Request:

- Content-Type: multipart/form-data
- Body: file (File upload)

Response:

```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "metadata": {
      "id": "string",
      "name": "string",
      "type": "string",
      "size": 0,
      "source": "string",
      "uploaded_at": "string"
    }
  }
}
```

### 4. Authentication Routes

All authentication routes are handled by separate routers:

- Admin Authentication: `/api/auth/*`
- User Authentication: `/api/users/*`
- Dashboard: `/api/dashboard/*`
