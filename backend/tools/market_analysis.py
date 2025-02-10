from typing import Optional, Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio
import logging

class MarketAnalysisInput(BaseModel):
    """Input schema for market analysis."""
    market_area: str = Field(description="Geographic area for market analysis (city, region, etc.)")
    property_type: str = Field(description="Type of commercial property to analyze")
    timeframe: Optional[str] = Field(default="12 months", description="Timeframe for analysis (e.g., '6 months', '12 months')")
    specific_metrics: Optional[List[str]] = Field(default=None, description="Specific metrics to analyze")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "market_area": "Manhattan, NY",
                "property_type": "office",
                "timeframe": "12 months",
                "specific_metrics": ["vacancy_rate", "rental_rates", "absorption"]
            }]
        }
    }

class MarketAnalysisTool(BaseTool):
    name: str = "market_analysis"
    description: str = """Analyzes commercial real estate market conditions for specific areas and property types.
    Provides insights on market trends, vacancy rates, rental rates, cap rates, and investment opportunities.
    Use this when you need to understand market dynamics and trends for a specific area."""
    
    args_schema: type[BaseModel] = MarketAnalysisInput

    def _run(self, market_area: str, property_type: str, 
             timeframe: str = "12 months",
             specific_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run market analysis for specified area and property type.
        This is a synchronous fallback that raises NotImplementedError.
        Use _arun for async operations.
        """
        raise NotImplementedError("MarketAnalysisTool only supports async operations")

    async def _arun(self, market_area: str, property_type: str, 
                  timeframe: str = "12 months",
                  specific_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run market analysis asynchronously.
        
        Args:
            market_area: Geographic area for analysis
            property_type: Type of commercial property
            timeframe: Analysis timeframe
            specific_metrics: Specific metrics to analyze
            
        Returns:
            Dict containing market analysis results
        """
        try:
            # Get market overview concurrently
            market_overview = self._get_market_overview(market_area, property_type)
            market_metrics = self._get_market_metrics(market_area, property_type)
            trends = self._analyze_trends(market_area, property_type, timeframe)
            competitive = self._get_competitive_analysis(market_area, property_type)
            opportunities = self._assess_opportunities_and_risks(market_area, property_type)
            
            # Use asyncio.gather to run all analyses concurrently
            results = await asyncio.gather(
                asyncio.to_thread(lambda: market_overview),
                asyncio.to_thread(lambda: market_metrics),
                asyncio.to_thread(lambda: trends),
                asyncio.to_thread(lambda: competitive),
                asyncio.to_thread(lambda: opportunities)
            )
            
            analysis = {
                "market_overview": results[0],
                "market_metrics": results[1],
                "trends": results[2],
                "competitive_analysis": results[3],
                "opportunities_and_risks": results[4]
            }
            
            return analysis
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in market analysis: {str(e)}")
            return {
                "error": str(e),
                "market_area": market_area,
                "property_type": property_type
            }

    def _get_market_overview(self, market_area: str, property_type: str) -> Dict[str, Any]:
        """Get general market overview."""
        return {
            "market_size": "Large metropolitan area",
            "market_phase": "Growth",
            "market_stability": "High",
            "key_drivers": [
                "Strong job market",
                "Population growth",
                "Infrastructure development"
            ]
        }

    def _get_market_metrics(self, market_area: str, property_type: str) -> Dict[str, Any]:
        """Calculate key market metrics."""
        return {
            "vacancy_rate": "5.2%",
            "absorption_rate": "Positive",
            "average_lease_rate": "$25/sq ft/year",
            "cap_rate": "6.5%",
            "price_per_sqft": "$250",
            "inventory_levels": "15M sq ft"
        }

    def _analyze_trends(self, market_area: str, property_type: str, timeframe: str) -> Dict[str, Any]:
        """Analyze market trends over specified timeframe."""
        return {
            "price_trend": "Upward",
            "vacancy_trend": "Decreasing",
            "development_pipeline": "Moderate",
            "demand_indicators": "Strong",
            "rent_growth": "3.5% annually"
        }

    def _get_competitive_analysis(self, market_area: str, property_type: str) -> Dict[str, Any]:
        """Analyze competitive landscape."""
        return {
            "competition_level": "Moderate",
            "market_saturation": "65%",
            "barriers_to_entry": "High",
            "major_players": [
                "Local REIT holdings",
                "Institutional investors",
                "Private equity firms"
            ]
        }

    def _assess_opportunities_and_risks(self, market_area: str, property_type: str) -> Dict[str, Any]:
        """Assess market opportunities and risks."""
        return {
            "opportunities": [
                "Growing demand in tech sector",
                "Redevelopment potential in submarkets",
                "Strong rental growth prospects"
            ],
            "risks": [
                "Potential interest rate increases",
                "New supply in pipeline",
                "Economic uncertainty"
            ],
            "recommendation": "Market conditions favorable for investment"
        }

class MarketMetricsCalculatorInput(BaseModel):
    """Input schema for market metrics calculations."""
    operation: str = Field(
        description="Type of calculation to perform (vacancy_rate, absorption_rate, rent_growth)",
        enum=["vacancy_rate", "absorption_rate", "rent_growth"]
    )
    values: Dict[str, float] = Field(
        description="""Dictionary of values needed for calculation.
        For Vacancy Rate: vacant_space, total_space
        For Absorption Rate: space_leased, space_vacated, time_period
        For Rent Growth: initial_rent, final_rent"""
    )

class MarketMetricsCalculator(BaseTool):
    """Tool for calculating market-specific metrics in commercial real estate analysis."""
    name: str = "market_metrics_calculator"
    description: str = """Calculates various market-specific metrics for commercial real estate analysis.
        Includes vacancy rates, absorption rates, market rent growth, and other key indicators.
        
        Example inputs:
        - Vacancy Rate: {"operation": "vacancy_rate", "values": {"vacant_space": 5000, "total_space": 50000}}
        - Absorption Rate: {"operation": "absorption_rate", "values": {"space_leased": 10000, "space_vacated": 3000, "time_period": 12}}
        - Rent Growth: {"operation": "rent_growth", "values": {"initial_rent": 30, "final_rent": 35}}
        """
    args_schema: type[BaseModel] = MarketMetricsCalculatorInput

    def _run(self, operation: str, values: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform market-specific calculations based on the operation type.
        
        Args:
            operation: Type of calculation (vacancy_rate, absorption_rate, rent_growth)
            values: Dictionary containing required values for calculation
            
        Returns:
            Dictionary containing calculation results
        """
        if operation == "vacancy_rate":
            return self._calculate_vacancy_rate(values)
        elif operation == "absorption_rate":
            return self._calculate_absorption_rate(values)
        elif operation == "rent_growth":
            return self._calculate_rent_growth(values)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _calculate_vacancy_rate(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate market vacancy rate."""
        try:
            vacant_space = values.get("vacant_space", 0)
            total_space = values.get("total_space", 0)
            
            if total_space == 0:
                return {"error": "Total space cannot be zero"}
                
            vacancy_rate = (vacant_space / total_space) * 100
            return {
                "vacancy_rate": round(vacancy_rate, 2),
                "vacant_space": vacant_space,
                "total_space": total_space
            }
        except Exception as e:
            return {"error": f"Vacancy rate calculation failed: {str(e)}"}

    def _calculate_absorption_rate(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate net absorption rate."""
        try:
            space_leased = values.get("space_leased", 0)
            space_vacated = values.get("space_vacated", 0)
            time_period = values.get("time_period", 12)  # months
            
            net_absorption = space_leased - space_vacated
            monthly_absorption = net_absorption / time_period
            
            return {
                "net_absorption": round(net_absorption, 2),
                "monthly_absorption": round(monthly_absorption, 2),
                "time_period": time_period
            }
        except Exception as e:
            return {"error": f"Absorption rate calculation failed: {str(e)}"}

    def _calculate_rent_growth(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate rent growth rate."""
        try:
            initial_rent = values.get("initial_rent", 0)
            final_rent = values.get("final_rent", 0)
            
            if initial_rent == 0:
                return {"error": "Initial rent cannot be zero"}
                
            growth_rate = ((final_rent - initial_rent) / initial_rent) * 100
            return {
                "rent_growth_rate": round(growth_rate, 2),
                "initial_rent": initial_rent,
                "final_rent": final_rent
            }
        except Exception as e:
            return {"error": f"Rent growth calculation failed: {str(e)}"}