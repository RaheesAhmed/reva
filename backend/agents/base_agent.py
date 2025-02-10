from typing import List, Optional, Dict, Any
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class BaseAgent(BaseModel):
    """Base agent class with common functionality for all CRE agents."""
    
    tools: List[BaseTool] = Field(default_factory=list)
    memory: Optional[ConversationBufferMemory] = Field(default=None)
    system_message: str = Field(default="You are a helpful AI assistant for commercial real estate.")
    agent_executor: Optional[AgentExecutor] = Field(default=None)
    
    def setup_memory(self) -> None:
        """Initialize conversation memory with system message."""
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output",
            input_key="input"
        )
    
    def get_agent_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for agent initialization."""
        return {
            "memory": self.memory,
            "system_message": self.system_message,
            "handle_parsing_errors": True,
            "max_iterations": 10,  # Increased from 3
            "max_execution_time": 30,  # 30 seconds timeout
            "early_stopping_method": "force",
            "verbose": True
        }
    
    def initialize_agent(self) -> AgentExecutor:
        """Initialize the agent with tools and memory."""
        if not self.memory:
            self.setup_memory()
            
        # Agent initialization logic to be implemented by subclasses
        raise NotImplementedError("Subclasses must implement initialize_agent()")
    
    async def arun(self, input_text: str) -> str:
        """Run the agent asynchronously."""
        try:
            if not self.agent_executor:
                self.agent_executor = self.initialize_agent()

            response = await self.agent_executor.ainvoke(
                {
                    "input": input_text,
                    "chat_history": self.memory.chat_memory.messages if self.memory else []
                }
            )
            return response["output"]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in async execution: {str(e)}")
            raise
    
    def run(self, input_text: str) -> str:
        """Run the agent synchronously."""
        raise NotImplementedError("Subclasses must implement run()")
        
    model_config = {
        "arbitrary_types_allowed": True
    } 