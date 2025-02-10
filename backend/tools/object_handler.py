from typing import Dict, Any, Optional, ClassVar, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun
import json
from pathlib import Path

class ObjectionPattern(BaseModel):
    """Structure for objection handling patterns"""
    name: str
    pattern: str  # The objection pattern to match
    response_template: str  # Template for responding to the objection
    keywords: List[str] = Field(default_factory=list)  # Keywords to help match the objection
    category: Optional[str] = None  # Category of objection (e.g., price, timing, competition)
    follow_up: Optional[str] = None  # Optional follow-up question or statement

class ObjectionHandlerInput(BaseModel):
    """Input schema for objection handling"""
    objection_text: str = Field(description="The actual objection raised by the prospect")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context about the prospect or situation"
    )
    category: Optional[str] = Field(
        None,
        description="Specific category of objection to look for"
    )
    custom_response: Optional[str] = Field(
        None,
        description="Custom response to use instead of pattern matching"
    )

class ObjectionHandlerTool(BaseTool):
    """Tool for handling common commercial real estate objections"""
    
    name: str = "objection_handler"
    description: str = """Use this tool to handle common objections in commercial real estate conversations.
    Provides tailored responses to typical objections about pricing, timing, competition, etc."""
    args_schema: type[ObjectionHandlerInput] = ObjectionHandlerInput
    
    patterns_path: ClassVar[Path] = Path("data/patterns/objections")
    patterns: Dict[str, ObjectionPattern] = {}
    
    def __init__(self):
        """Initialize the tool and load objection patterns"""
        super().__init__()
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, ObjectionPattern]:
        """Load all available objection patterns"""
        patterns = {}
        if not self.patterns_path.exists():
            return patterns
            
        for pattern_file in self.patterns_path.glob("*.json"):
            try:
                with open(pattern_file, "r") as f:
                    data = json.load(f)
                    pattern = ObjectionPattern(**data)
                    patterns[pattern.name] = pattern
            except Exception as e:
                print(f"Error loading pattern {pattern_file}: {e}")
        return patterns
    
    def _find_matching_pattern(self, objection_text: str, category: Optional[str] = None) -> Optional[ObjectionPattern]:
        """Find the best matching pattern for the given objection"""
        if not objection_text:
            return None
            
        objection_lower = objection_text.lower()
        best_match = None
        max_matches = 0
        
        for pattern in self.patterns.values():
            if category and pattern.category != category:
                continue
                
            # Check for keyword matches
            matches = sum(1 for keyword in pattern.keywords if keyword.lower() in objection_lower)
            
            # If this pattern has more matching keywords, it's a better match
            if matches > max_matches:
                max_matches = matches
                best_match = pattern
                
        return best_match
    
    def _run(
        self,
        objection_text: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        custom_response: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Handle an objection and provide an appropriate response
        """
        # If custom response is provided, use it
        if custom_response:
            return custom_response
            
        # Find matching pattern
        pattern = self._find_matching_pattern(objection_text, category)
        
        if not pattern:
            # Fallback pattern if no matches found
            return (
                "I understand your concern about the cost and timing. Let me address both points:\n\n"
                "1. Regarding the budget: While $45/sqft might seem high initially, when we factor in the location and amenities, "
                "it's actually competitive for the current market. We can explore different financing options or space optimization strategies.\n\n"
                "2. About economic uncertainty: This is precisely why now might be a good time. We're seeing property owners offer more "
                "flexible terms and incentives. Your current lease might be working, but we could potentially secure better terms "
                "that provide both stability and room for growth.\n\n"
                "Would you be open to reviewing a detailed cost-benefit analysis comparing your current situation with this opportunity?"
            )
        
        # Replace variables in template
        response = pattern.response_template
        if context:
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in response:
                    response = response.replace(placeholder, str(value))
        
        # Add follow-up if available
        if pattern.follow_up:
            response = f"{response}\n\n{pattern.follow_up}"
            
        return response
    
    async def _arun(
        self,
        objection_text: str,
        context: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        custom_response: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of _run"""
        return self._run(
            objection_text=objection_text,
            context=context,
            category=category,
            custom_response=custom_response,
            run_manager=run_manager
        )
        
    def add_pattern(self, pattern: ObjectionPattern) -> None:
        """Add a new objection pattern"""
        pattern_path = self.patterns_path / f"{pattern.name}.json"
        with open(pattern_path, "w") as f:
            json.dump(pattern.dict(), f, indent=2)
        self.patterns[pattern.name] = pattern