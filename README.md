# Commercial Real Estate AI Assistant

A powerful AI-powered chatbot for commercial real estate, leveraging LangChain, OpenAI, and Supabase for intelligent property analysis and document search.

## Features

- 🤖 AI-powered chat interface
- 🏢 Property analysis and market insights
- 📊 Economic data integration (FRED)
- 🔍 Intelligent document search with vector store
- 📄 Document management system
- 🌐 Real-time web search integration
- 💡 Value proposition generation
- 📈 Market analysis tools

## Tech Stack

### Backend

- FastAPI
- LangChain
- OpenAI GPT-4
- Supabase Vector Store
- Python 3.11+

### Frontend

- Next.js 14
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Markdown

## Project Structure

```
backend/
├───agents/
│   │   base_agent.py
│   │   real_estate_agent.py
├───config/
│   │   settings.py
├───data/
│   │   loaders.py
│   │   processors.py
├───prompts/
│   │   cold_call_prompt.py
│   │   system_prompt.py
│   │   user_prompts.py
├───tools/
│   │   document_search.py
│   │   market_analysis.py
│   │   property_analysis.py
│   │   search_tools.py
│   │   tavily_search.py
│   │   value_proposition.py
├───vectorstore/
│   │   setup.sql
│   │   supabase_store.py
├───tests/
├───requirements.txt
├───.env
├───logger.py
└───main.py

frontend/
├───app/
│   ├───admin/
│   │   └───upload/
│   │       └───page.tsx
│   ├───chat/
│   │   └───page.tsx
│   ├───layout.tsx
│   └───page.tsx
├───components/
│   ├───ui/
│   ├───Chat.tsx
│   └───ToolSelector.tsx
├───lib/
│   ├───api-client.ts
│   └───utils.ts
└───public/
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:

   ```bash
   cd backend
   python -m venv venv
   ```

2. Activate the virtual environment:

   - Windows:
     ```powershell
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the backend directory:

   ```env
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key

   # Supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_supabase_service_key

   # Vector Store
   VECTOR_STORE_TABLE=documents
   VECTOR_STORE_QUERY=match_documents

   # Tavily
   TAVILY_API_KEY=your_tavily_api_key

   # FRED
   FRED_API_KEY=your_fred_api_key
   ```

5. Set up Supabase:

   - Create a new Supabase project
   - Run the SQL setup script from `vectorstore/setup.sql`
   - Enable Vector extension in Supabase

6. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Create a .env.local file:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Available Tools

1. **Web Search**

   - Real-time web search using Tavily API
   - Intelligent result filtering and summarization

2. **Document Search**

   - Search through internal knowledge base
   - Vector similarity search with relevance scoring
   - Support for PDF, DOCX, and TXT files

3. **Economic Data**

   - FRED economic data integration
   - Market indicators and trends
   - Historical data analysis

4. **Market Analysis**

   - Location-based market insights
   - Trend analysis and forecasting
   - Competitive landscape assessment

5. **Property Analysis**

   - Detailed property evaluation
   - Investment potential assessment
   - Risk analysis

6. **Value Proposition**
   - Custom value proposition generation
   - Target audience customization
   - Competitive advantage highlighting

## Document Management

The system includes a document management interface at `/admin/upload` with features:

- File upload support (PDF, DOCX, TXT)
- Processing status tracking
- Vector store integration
- Document deletion
- Status indicators and error handling

## API Endpoints

### Chat Endpoints

- POST `/chat` - Main chat interface
- POST `/tools/search` - Web search
- POST `/tools/document-search` - Document search
- POST `/tools/economic-data` - FRED data
- POST `/tools/market-analysis` - Market analysis
- POST `/tools/property-analysis` - Property analysis
- POST `/tools/value-proposition` - Value propositions

### Admin Endpoints

- GET `/admin/documents` - List documents
- POST `/admin/documents/upload` - Upload document
- DELETE `/admin/documents/{document_id}` - Delete document

## Development Guidelines

1. **Code Style**

   - Follow PEP 8 for Python code
   - Use TypeScript for frontend
   - Maintain consistent naming conventions

2. **Error Handling**

   - Proper error logging
   - User-friendly error messages
   - Graceful fallbacks

3. **Testing**

   - Write unit tests for critical functions
   - Test edge cases
   - Maintain test coverage

4. **Security**
   - Secure API key handling
   - Input validation
   - Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For support, email `raheesahmed256@gmail.com`
