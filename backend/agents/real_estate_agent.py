from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.tools import Tool
from langchain.schema import SystemMessage, HumanMessage
from pydantic import Field

from .base_agent import BaseAgent
from config.settings import settings
from logger import setup_logger
from tools.property_analysis import PropertyAnalysisTool, PropertyMetricsCalculator
from tools.market_analysis import MarketAnalysisTool, MarketMetricsCalculator
from tools.value_proposition import ValuePropositionTool, FinancialCalculatorTool
from tools.document_search import DocumentSearchTool
from tools.tavily_search import TavilySearchTool
from tools.fred_economic import FREDEconomicTool
from tools.cold_call import ColdCallScriptTool
from tools.object_handler import ObjectionHandlerTool
from tools.sales_strategy_advisor import SalesStrategyAdvisorTool
from tools.comparable_analysis import ComparableAnalysisTool
from config.supabase import get_supabase

logger = setup_logger(__name__)

class RealEstateAgent(BaseAgent):
    """
    Specialized agent for commercial real estate interactions.
    Handles property analysis, market research, and value propositions.
    """
    
    llm: ChatOpenAI = Field(default_factory=lambda: ChatOpenAI(
        model_name=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
        streaming=True  # Enable streaming for better UX
    ))
    
    def _get_system_message(self) -> str:
        """Fetch the active system message from Supabase."""
        try:
            supabase = get_supabase(auth=False)  # Use admin client
            result = supabase.table('system_messages').select('*').eq('is_active', True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['message']
            
            # Return default message if no active message found
            return """You are an expert commercial real estate AI assistant. 
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
            Always show your calculations and explain the results in a clear, professional manner."""
            
        except Exception as e:
            logger.error(f"Error fetching system message: {str(e)}")
            return self.system_message

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None
    ):
        """
        Initialize the real estate agent with specific tools and configuration.
        
        Args:
            model_name: Optional override for the OpenAI model
            temperature: Optional override for model temperature
            system_message: Optional custom system message
        """
        # Initialize with default system message first
        super().__init__(
            tools=[],  # Will be initialized in setup_tools
            system_message=system_message or """You are an expert commercial real estate AI assistant."""
        )
        
        if model_name or temperature:
            self.llm = ChatOpenAI(
                model_name=model_name or settings.MODEL_NAME,
                temperature=temperature or settings.TEMPERATURE,
                api_key=settings.OPENAI_API_KEY,
                streaming=True
            )
        
        self.setup_tools()
        self.agent_executor = self.initialize_agent()

    async def initialize(self):
        """Async initialization method to be called after construction."""
        try:
            system_message = self._get_system_message()  # Now calling sync method
            self.system_message = system_message
            self.agent_executor = self.initialize_agent()
        except Exception as e:
            logger.error(f"Error in async initialization: {str(e)}")

    def setup_tools(self) -> List[Tool]:
        """Initialize and return the list of tools available to the agent"""
        self.tools = [
            PropertyAnalysisTool(),
            MarketAnalysisTool(),
            ValuePropositionTool(),
            DocumentSearchTool(),
            TavilySearchTool(),
            FREDEconomicTool(),
            ColdCallScriptTool(),
            ObjectionHandlerTool(),
            SalesStrategyAdvisorTool(),
            ComparableAnalysisTool(),
            PropertyMetricsCalculator(),
            MarketMetricsCalculator(),
            FinancialCalculatorTool()
        ]
        return self.tools

    def initialize_agent(self) -> AgentExecutor:
        """Initialize or reinitialize the agent executor with current tools."""
        try:
            # Create the prompt template with enhanced system message
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.system_message + """
                You now have access to powerful calculation tools for:
                
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
                Always show your calculations and explain the results in a clear, professional manner.
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            # Create the agent with OpenAI functions
            agent = create_openai_functions_agent(
                self.llm,
                self.tools,
                prompt
            )

            # Create the executor with optimized settings
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                max_iterations=10,
                max_execution_time=30,
                early_stopping_method="force",
                handle_parsing_errors=True,
                verbose=False
            )

        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise

    async def arun(self, input_text: str) -> str:
        """Run the agent asynchronously with streaming support."""
        try:
            if not self.agent_executor:
                self.agent_executor = self.initialize_agent()

            # Create an async LLM instance for parameter extraction
            async_llm = ChatOpenAI(
                model_name=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
                api_key=settings.OPENAI_API_KEY,
                streaming=True
            )

            # Get selected tools from input context
            selected_tools = []
            for tool in self.tools:
                if (tool.name.lower() in input_text.lower() or 
                    any(keyword in input_text.lower() for keyword in tool.name.split('-'))):
                    selected_tools.append(tool)

            if not selected_tools:
                selected_tools = self.tools

            # Create tasks for each selected tool
            tasks = []
            for tool in selected_tools:
                if hasattr(tool, '_arun'):
                    tool_params = await self._extract_tool_params(tool, input_text, async_llm)
                    if tool_params:
                        tasks.append(self._execute_tool(tool, tool_params))

            # Execute tools concurrently
            if tasks:
                import asyncio
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                processed_results = []
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Tool execution error: {str(result)}")
                        continue
                    if result is not None:
                        processed_results.append(result)

                if processed_results:
                    return await self._generate_combined_response(processed_results, input_text, async_llm)

            # Fall back to regular agent if no async tools were executed
            response = await self.agent_executor.ainvoke(
                {
                    "input": input_text,
                    "chat_history": self.memory.chat_memory.messages if self.memory else []
                }
            )
            return response["output"]

        except Exception as e:
            logger.error(f"Error in async execution: {str(e)}")
            raise

    async def _execute_tool(self, tool: Tool, params: Dict[str, Any]) -> Any:
        """Execute a single tool with error handling."""
        try:
            if hasattr(tool, '_arun'):
                return await tool._arun(**params)
            else:
                import asyncio
                return await asyncio.to_thread(tool._run, **params)
        except Exception as e:
            logger.error(f"Error executing tool {tool.name}: {str(e)}")
            return None

    async def _extract_tool_params(self, tool: Tool, input_text: str, async_llm: ChatOpenAI) -> Optional[Dict[str, Any]]:
        """Extract tool-specific parameters from input text using the LLM."""
        try:
            schema = tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {}
            required_params = schema.get('required', []) if schema else []
            properties = schema.get('properties', {}) if schema else {}

            prompt = f"""
            Based on the user input: "{input_text}"
            Extract parameters for the tool: {tool.name}
            Tool description: {tool.description}
            
            Required parameters: {required_params}
            Parameter descriptions:
            {chr(10).join([f'- {param}: {properties.get(param, {}).get("description", "No description")}' for param in required_params])}
            
            Return only the parameter values in valid JSON format.
            If a required parameter cannot be extracted from the input, use a reasonable default value.
            """
            
            response = await async_llm.ainvoke([HumanMessage(content=prompt)])
            
            import json
            try:
                params = json.loads(response.content)
                if isinstance(params, dict):
                    for param in required_params:
                        if param not in params:
                            params[param] = self._get_default_param_value(param, properties.get(param, {}))
                    return params
                return None
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting tool parameters: {str(e)}")
            return None

    def _get_default_param_value(self, param: str, param_info: Dict[str, Any]) -> Any:
        """Get a default value for a parameter based on its type."""
        param_type = param_info.get('type', 'string')
        if param_type == 'string':
            return ''
        elif param_type == 'number' or param_type == 'integer':
            return 0
        elif param_type == 'array':
            return []
        elif param_type == 'boolean':
            return False
        else:
            return None

    async def _generate_combined_response(self, results: List[Any], input_text: str, async_llm: ChatOpenAI) -> str:
        """Generate a combined response from multiple tool results."""
        try:
            formatted_results = []
            for result in results:
                if isinstance(result, dict):
                    formatted_results.extend([f"- {k}: {v}" for k, v in result.items()])
                else:
                    formatted_results.append(f"- {str(result)}")

            results_str = "\n".join(formatted_results)
            
            prompt = f"""
            Based on the user input: "{input_text}"
            And the following tool results:
            {results_str}
            
            Generate a comprehensive response that:
            1. Synthesizes all the relevant information
            2. Presents it in a clear, organized format using markdown
            3. Highlights key insights and recommendations
            4. Maintains a professional tone suitable for commercial real estate
            """
            
            response = await async_llm.ainvoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating combined response: {str(e)}")
            return "I apologize, but I encountered an error while processing the results. Please try again or contact support."

    def run(self, input_text: str) -> str:
        """Run the agent synchronously."""
        import asyncio
        try:
            return asyncio.run(self.arun(input_text))
        except Exception as e:
            logger.error(f"Error in sync execution: {str(e)}")
            raise

    model_config = {
        "arbitrary_types_allowed": True
    }