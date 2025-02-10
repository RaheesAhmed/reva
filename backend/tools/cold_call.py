from typing import Dict, Any, Optional, ClassVar
from langchain.tools import Tool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun
import json
from pathlib import Path

class ColdCallTemplate(BaseModel):
    """Template structure for cold call scripts"""
    name: str
    template: str
    variables: Dict[str, str] = Field(default_factory=dict)
    industry_type: Optional[str] = None
    property_type: Optional[str] = None

class ProspectInfo(BaseModel):
    """Schema for prospect information"""
    script_text: Optional[str] = Field(
        None,
        description="Direct script text to use instead of template-based generation"
    )
    template_name: Optional[str] = Field(
        None,
        description="Name of the template to use"
    )
    company_name: Optional[str] = Field(
        None,
        description="Name of the prospect's company"
    )
    contact_name: Optional[str] = Field(
        None,
        description="Name of the contact person"
    )
    property_type: Optional[str] = Field(
        None,
        description="Type of property (office, retail, industrial, etc.)"
    )
    location: Optional[str] = Field(
        None,
        description="Property location"
    )
    pain_points: Optional[str] = Field(
        None,
        description="Known pain points or needs"
    )
    optimize_strategy: Optional[str] = Field(
        None,
        description="Strategy for optimization (e.g., consolidate, expand, modernize)"
    )

class ColdCallScriptTool(Tool):
    """Tool for generating customized cold call scripts for commercial real estate"""
    
    name: ClassVar[str] = "cold_call_script_generator"
    description: ClassVar[str] = """Use this tool to generate or customize cold call scripts for commercial real estate prospects.
    You can either provide a complete script text or prospect details for template-based generation."""
    
    templates_path: ClassVar[Path] = Path("data/templates/cold_call")
    templates: Dict[str, ColdCallTemplate] = {}
    
    def __init__(self):
        """Initialize the tool and load templates"""
        super().__init__(
            name=self.name,
            description=self.description,
            func=self._run,
            coroutine=self._arun,
            args_schema=ProspectInfo
        )
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, ColdCallTemplate]:
        """Load all available templates from the templates directory"""
        templates = {}
        if not self.templates_path.exists():
            return templates
            
        for template_file in self.templates_path.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    data = json.load(f)
                    template = ColdCallTemplate(**data)
                    templates[template.name] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
        return templates
    
    def _run(
        self,
        script_text: Optional[str] = None,
        template_name: Optional[str] = None,
        company_name: Optional[str] = None,
        contact_name: Optional[str] = None,
        property_type: Optional[str] = None,
        location: Optional[str] = None,
        pain_points: Optional[str] = None,
        optimize_strategy: Optional[str] = None,
        callback_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Generate a customized cold call script based on prospect information or direct script text
        """
        # If direct script text is provided, return it
        if script_text:
            return script_text
            
        # Build prospect info dictionary from provided parameters
        prospect_info = {
            "company_name": company_name,
            "contact_name": contact_name,
            "property_type": property_type,
            "location": location,
            "pain_points": pain_points,
            "optimize_strategy": optimize_strategy
        }
        # Remove None values
        prospect_info = {k: v for k, v in prospect_info.items() if v is not None}
            
        # Select appropriate template
        template = None
        if template_name and template_name in self.templates:
            template = self.templates[template_name]
        else:
            # Select based on property type or first available
            if property_type:
                property_type_lower = property_type.lower()
                for t in self.templates.values():
                    if t.property_type and t.property_type.lower() == property_type_lower:
                        template = t
                        break
            if not template and self.templates:
                template = next(iter(self.templates.values()))
                
        if not template:
            # Fallback template if no templates are loaded
            template = ColdCallTemplate(
                name="default",
                template=(
                    "Hello {contact_name}, this is [Your Name] from [Your Company]. "
                    "I noticed that {company_name} has commercial property interests in {location}. "
                    "I wanted to discuss how we could help address {pain_points} "
                    "and potentially improve your property portfolio's performance. "
                    "Would you have a few minutes to discuss this?"
                )
            )
        
        # Replace variables in template
        script = template.template
        for key, value in prospect_info.items():
            placeholder = "{" + key + "}"
            if placeholder in script:
                script = script.replace(placeholder, str(value))
                
        return script
    
    async def _arun(
        self,
        script_text: Optional[str] = None,
        template_name: Optional[str] = None,
        company_name: Optional[str] = None,
        contact_name: Optional[str] = None,
        property_type: Optional[str] = None,
        location: Optional[str] = None,
        pain_points: Optional[str] = None,
        optimize_strategy: Optional[str] = None,
        callback_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of _run"""
        return self._run(
            script_text=script_text,
            template_name=template_name,
            company_name=company_name,
            contact_name=contact_name,
            property_type=property_type,
            location=location,
            pain_points=pain_points,
            optimize_strategy=optimize_strategy,
            callback_manager=callback_manager
        )
        
    def add_template(self, template: ColdCallTemplate) -> None:
        """Add a new template to the collection"""
        template_path = self.templates_path / f"{template.name}.json"
        with open(template_path, "w") as f:
            json.dump(template.dict(), f, indent=2)
        self.templates[template.name] = template