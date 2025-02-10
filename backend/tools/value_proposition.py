from typing import Optional, Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio
import logging

class ValuePropositionInput(BaseModel):
    """Input schema for value proposition generation."""
    property_type: str = Field(description="Type of commercial property")
    target_audience: str = Field(description="Target audience (e.g., investors, tenants)")
    property_features: List[str] = Field(description="Key features and amenities of the property")
    location_benefits: Optional[List[str]] = Field(default=None, description="Location-specific benefits")
    market_position: Optional[str] = Field(default=None, description="Property's market positioning")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "property_type": "office",
                "target_audience": "investors",
                "property_features": ["Modern amenities", "Prime location", "Energy efficient"],
                "location_benefits": ["Close to transit", "Growing business district"],
                "market_position": "Premium"
            }]
        }
    }

class ValuePropositionTool(BaseTool):
    name: str = "value_proposition"
    description: str = """Generates compelling value propositions for commercial properties.
    Creates targeted messaging highlighting property benefits, features, and competitive advantages.
    Use this when you need to create persuasive property marketing messages or investment pitches."""
    
    args_schema: type[BaseModel] = ValuePropositionInput

    def _run(
        self,
        property_type: str,
        target_audience: str,
        property_features: List[str],
        location_benefits: Optional[List[str]] = None,
        market_position: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous fallback that raises NotImplementedError.
        Use _arun for async operations.
        """
        raise NotImplementedError("ValuePropositionTool only supports async operations")

    async def _arun(
        self,
        property_type: str,
        target_audience: str,
        property_features: List[str],
        location_benefits: Optional[List[str]] = None,
        market_position: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate value proposition asynchronously.
        
        Args:
            property_type: Type of commercial property
            target_audience: Target audience
            property_features: Key property features
            location_benefits: Location benefits
            market_position: Market positioning
            
        Returns:
            Dict containing value proposition components
        """
        try:
            # Create tasks for each value proposition component
            tasks = [
                asyncio.to_thread(lambda: self._generate_core_proposition(property_type, target_audience, property_features)),
                asyncio.to_thread(lambda: self._identify_key_benefits(property_features, location_benefits)),
                asyncio.to_thread(lambda: self._analyze_competitive_advantages(property_type, property_features, market_position)),
                asyncio.to_thread(lambda: self._create_targeted_messaging(target_audience, property_type)),
                asyncio.to_thread(lambda: self._calculate_roi_potential(property_type, market_position))
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger = logging.getLogger(__name__)
                    logger.error(f"Value proposition component error: {str(result)}")
                    continue
                processed_results.append(result)
            
            # Combine all results into final value proposition
            if len(processed_results) == 5:
                value_prop = {
                    "core_value_proposition": processed_results[0],
                    "key_benefits": processed_results[1],
                    "competitive_advantages": processed_results[2],
                    "target_messaging": processed_results[3],
                    "roi_potential": processed_results[4]
                }
                return value_prop
            else:
                raise Exception("One or more value proposition components failed")
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating value proposition: {str(e)}")
            return {
                "error": str(e),
                "property_type": property_type,
                "target_audience": target_audience
            }

    def _generate_core_proposition(
        self,
        property_type: str,
        target_audience: str,
        property_features: List[str]
    ) -> str:
        """Generate core value proposition statement."""
        audience_benefits = {
            "investors": "strong ROI potential and stable cash flow",
            "tenants": "prime location and modern amenities",
            "developers": "development potential and market opportunity"
        }
        
        benefit = audience_benefits.get(target_audience.lower(), "exceptional value")
        features_highlight = ", ".join(property_features[:2])
        
        return f"A premium {property_type} property offering {benefit}, featuring {features_highlight} in a strategic location."

    def _identify_key_benefits(
        self,
        property_features: List[str],
        location_benefits: Optional[List[str]]
    ) -> Dict[str, List[str]]:
        """Identify and categorize key benefits."""
        benefits = {
            "property_benefits": [
                self._convert_feature_to_benefit(feature)
                for feature in property_features
            ],
            "location_advantages": location_benefits or [
                "Excellent accessibility",
                "Strong market presence",
                "Growing neighborhood"
            ]
        }
        
        return benefits

    def _convert_feature_to_benefit(self, feature: str) -> str:
        """Convert property feature to benefit statement."""
        benefit_mapping = {
            "parking": "Convenient parking for employees and visitors",
            "security": "Enhanced safety and peace of mind",
            "amenities": "Improved tenant satisfaction and retention",
            "location": "Reduced commute times and better accessibility",
            "modern": "Lower operating costs and improved efficiency"
        }
        
        for key, value in benefit_mapping.items():
            if key in feature.lower():
                return value
                
        return f"Enhanced value through {feature}"

    def _analyze_competitive_advantages(
        self,
        property_type: str,
        property_features: List[str],
        market_position: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze and present competitive advantages."""
        return {
            "market_position": market_position or "Premium",
            "unique_features": property_features,
            "differentiators": [
                "Strategic location",
                "Modern amenities",
                "Flexible terms",
                "Professional management"
            ]
        }

    def _create_targeted_messaging(
        self,
        target_audience: str,
        property_type: str
    ) -> Dict[str, List[str]]:
        """Create audience-specific messaging."""
        messaging = {
            "value_statements": [
                f"Ideal {property_type} solution for {target_audience}",
                "Proven track record of tenant satisfaction",
                "Strategic location in growing market"
            ],
            "call_to_action": [
                "Schedule a viewing today",
                "Request detailed financial analysis",
                "Explore investment opportunity"
            ]
        }
        
        return messaging

    def _calculate_roi_potential(
        self,
        property_type: str,
        market_position: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate and present ROI potential."""
        return {
            "potential_returns": {
                "cap_rate_range": "5.5% - 7.5%",
                "cash_on_cash": "8% - 12%",
                "irr_projection": "15% - 18%"
            },
            "value_add_opportunities": [
                "Operational efficiency improvements",
                "Amenity upgrades",
                "Lease optimization"
            ]
        }

    async def _acalculate_roi_potential(
        self,
        property_type: str,
        market_position: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate ROI potential asynchronously."""
        return self._calculate_roi_potential(property_type, market_position)


class FinancialCalculatorInput(BaseModel):
    """Input schema for financial calculations."""
    operation: str = Field(
        description="Type of calculation to perform (roi, cap_rate, noi)",
        enum=["roi", "cap_rate", "noi"]
    )
    values: Dict[str, float] = Field(
        description="""Dictionary of values needed for calculation.
        For ROI: initial_investment, net_profit
        For Cap Rate: noi, property_value
        For NOI: gross_income, operating_expenses"""
    )

class FinancialCalculatorTool(BaseTool):
    """Tool for performing financial calculations related to commercial real estate."""
    name: str = "financial_calculator"
    description: str = """Performs financial calculations for commercial real estate analysis.
        Calculates metrics like ROI, Cap Rate, NOI, and other financial indicators.
        
        Example inputs:
        - ROI calculation: {"operation": "roi", "values": {"initial_investment": 1000000, "net_profit": 120000}}
        - Cap Rate calculation: {"operation": "cap_rate", "values": {"noi": 500000, "property_value": 5000000}}
        - NOI calculation: {"operation": "noi", "values": {"gross_income": 800000, "operating_expenses": 300000}}
        """
    args_schema: type[BaseModel] = FinancialCalculatorInput

    def _run(self, operation: str, values: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform financial calculations based on the operation type.
        
        Args:
            operation: Type of calculation (roi, cap_rate, noi)
            values: Dictionary containing required values for calculation
            
        Returns:
            Dictionary containing calculation results
        """
        if operation == "roi":
            return self._calculate_roi(values)
        elif operation == "cap_rate":
            return self._calculate_cap_rate(values)
        elif operation == "noi":
            return self._calculate_noi(values)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _calculate_roi(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate Return on Investment."""
        try:
            initial_investment = values.get("initial_investment", 0)
            net_profit = values.get("net_profit", 0)
            
            if initial_investment == 0:
                return {"error": "Initial investment cannot be zero"}
                
            roi = (net_profit / initial_investment) * 100
            return {
                "roi": round(roi, 2),
                "initial_investment": initial_investment,
                "net_profit": net_profit
            }
        except Exception as e:
            return {"error": f"ROI calculation failed: {str(e)}"}

    def _calculate_cap_rate(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate Capitalization Rate."""
        try:
            noi = values.get("noi", 0)
            property_value = values.get("property_value", 0)
            
            if property_value == 0:
                return {"error": "Property value cannot be zero"}
                
            cap_rate = (noi / property_value) * 100
            return {
                "cap_rate": round(cap_rate, 2),
                "noi": noi,
                "property_value": property_value
            }
        except Exception as e:
            return {"error": f"Cap Rate calculation failed: {str(e)}"}

    def _calculate_noi(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate Net Operating Income."""
        try:
            gross_income = values.get("gross_income", 0)
            operating_expenses = values.get("operating_expenses", 0)
            
            noi = gross_income - operating_expenses
            return {
                "noi": round(noi, 2),
                "gross_income": gross_income,
                "operating_expenses": operating_expenses
            }
        except Exception as e:
            return {"error": f"NOI calculation failed: {str(e)}"}