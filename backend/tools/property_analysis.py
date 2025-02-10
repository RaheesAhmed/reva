from typing import Optional, Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging

class PropertyAnalysisInput(BaseModel):
    """Input schema for property analysis."""
    property_type: str = Field(description="Type of commercial property (e.g., office, retail, industrial)")
    location: str = Field(description="Property location (address or area)")
    size: Optional[float] = Field(default=None, description="Property size in square feet")
    price: Optional[float] = Field(default=None, description="Property price or asking price")
    year_built: Optional[int] = Field(default=None, description="Year the property was built")
    additional_details: Optional[str] = Field(default=None, description="Any additional property details")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "property_type": "office",
                "location": "123 Business Ave, New York, NY",
                "size": 50000,
                "price": 15000000,
                "year_built": 2010
            }]
        }
    }

class PropertyAnalysisTool(BaseTool):
    name: str = "property_analysis"
    description: str = """Analyzes commercial properties based on provided details.
    Evaluates key metrics like location quality, price per square foot, potential ROI,
    and market positioning. Use this when you need to assess a specific property's
    characteristics and investment potential."""
    
    args_schema: type[BaseModel] = PropertyAnalysisInput

    def _run(self, property_type: str, location: str, size: Optional[float] = None,
             price: Optional[float] = None, year_built: Optional[int] = None,
             additional_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronous fallback that raises NotImplementedError.
        Use _arun for async operations.
        """
        raise NotImplementedError("PropertyAnalysisTool only supports async operations")

    async def _arun(self, property_type: str, location: str, size: Optional[float] = None,
                  price: Optional[float] = None, year_built: Optional[int] = None,
                  additional_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Run property analysis asynchronously.
        
        Args:
            property_type: Type of commercial property
            location: Property location
            size: Property size in square feet
            price: Property price
            year_built: Year built
            additional_details: Additional property information
            
        Returns:
            Dict containing analysis results
        """
        try:
            import asyncio
            
            # Create tasks for each analysis component
            tasks = [
                asyncio.to_thread(lambda: {
                    "type": property_type,
                    "location": location,
                    "size": size,
                    "price": price,
                    "year_built": year_built
                }),
                asyncio.to_thread(lambda: self._analyze_location(location)),
                asyncio.to_thread(lambda: self._calculate_market_metrics(property_type, size, price)),
                asyncio.to_thread(lambda: self._assess_condition(year_built)),
                asyncio.to_thread(lambda: self._generate_recommendations(property_type, location))
            ]
            
            # Execute all analysis tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger = logging.getLogger(__name__)
                    logger.error(f"Analysis component error: {str(result)}")
                    continue
                processed_results.append(result)
            
            # Combine all results into final analysis
            if len(processed_results) == 5:
                analysis = {
                    "property_overview": processed_results[0],
                    "location_analysis": processed_results[1],
                    "market_metrics": processed_results[2],
                    "condition_assessment": processed_results[3],
                    "recommendations": processed_results[4]
                }
                return analysis
            else:
                raise Exception("One or more analysis components failed")
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in property analysis: {str(e)}")
            return {
                "error": str(e),
                "property_type": property_type,
                "location": location
            }

    def _analyze_location(self, location: str) -> Dict[str, Any]:
        """Analyze the property location."""
        # Placeholder for location analysis logic
        return {
            "accessibility": "High",
            "market_demand": "Strong",
            "development_potential": "Moderate"
        }

    def _calculate_market_metrics(self, property_type: str, 
                                size: Optional[float], 
                                price: Optional[float]) -> Dict[str, Any]:
        """Calculate key market metrics."""
        metrics = {
            "market_segment": property_type.capitalize(),
            "estimated_occupancy_rate": "95%"
        }
        
        if size and price:
            metrics["price_per_sqft"] = price / size
            
        return metrics

    def _assess_condition(self, year_built: Optional[int]) -> Dict[str, Any]:
        """Assess property condition based on age and other factors."""
        if not year_built:
            return {"condition": "Unknown"}
            
        import datetime
        current_year = datetime.datetime.now().year
        age = current_year - year_built
        
        if age < 5:
            condition = "Excellent"
        elif age < 15:
            condition = "Good"
        elif age < 30:
            condition = "Fair"
        else:
            condition = "May need renovation"
            
        return {
            "condition": condition,
            "age": age,
            "renovation_needed": age > 30
        }

    def _generate_recommendations(self, property_type: str, location: str) -> List[str]:
        """Generate property-specific recommendations."""
        return [
            f"Consider market trends for {property_type} properties in {location}",
            "Conduct detailed property inspection",
            "Review tenant history and occupancy rates",
            "Analyze potential for value-add improvements"
        ]

    async def _agenerate_recommendations(self, property_type: str, location: str) -> List[str]:
        """Generate recommendations asynchronously."""
        return self._generate_recommendations(property_type, location)


class PropertyMetricsCalculatorInput(BaseModel):
    """Input schema for property metrics calculations."""
    operation: str = Field(
        description="Type of calculation to perform (price_per_sqft, operating_expense_ratio, dscr)",
        enum=["price_per_sqft", "operating_expense_ratio", "dscr"]
    )
    values: Dict[str, float] = Field(
        description="""Dictionary of values needed for calculation.
        For Price per Sqft: price, square_feet
        For Operating Expense Ratio: operating_expenses, gross_operating_income
        For DSCR: noi, debt_service"""
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "operation": "dscr",
                "values": {
                    "noi": 500000,
                    "debt_service": 350000
                }
            }]
        }
    }

class PropertyMetricsCalculator(BaseTool):
    """Tool for calculating property-specific metrics in commercial real estate analysis."""
    name: str = "property_metrics_calculator"
    description: str = """Calculates various property-specific metrics for commercial real estate analysis.
        Includes price per square foot, operating expense ratio, debt service coverage ratio, and other key indicators.
        
        Example inputs:
        - Price per Sqft: {"operation": "price_per_sqft", "values": {"price": 2000000, "square_feet": 10000}}
        - Operating Expense Ratio: {"operation": "operating_expense_ratio", "values": {"operating_expenses": 300000, "gross_operating_income": 800000}}
        - DSCR: {"operation": "dscr", "values": {"noi": 500000, "debt_service": 400000}}
        """
    args_schema: type[BaseModel] = PropertyMetricsCalculatorInput

    def _run(self, operation: str, values: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform property-specific calculations based on the operation type.
        
        Args:
            operation: Type of calculation (price_per_sqft, operating_expense_ratio, dscr)
            values: Dictionary containing required values for calculation
            
        Returns:
            Dictionary containing calculation results
        """
        if operation == "price_per_sqft":
            return self._calculate_price_per_sqft(values)
        elif operation == "operating_expense_ratio":
            return self._calculate_operating_expense_ratio(values)
        elif operation == "dscr":
            return self._calculate_dscr(values)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _calculate_price_per_sqft(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate price per square foot."""
        try:
            price = values.get("price", 0)
            square_feet = values.get("square_feet", 0)
            
            if square_feet == 0:
                return {"error": "Square footage cannot be zero"}
                
            price_per_sqft = price / square_feet
            return {
                "price_per_sqft": round(price_per_sqft, 2),
                "price": price,
                "square_feet": square_feet
            }
        except Exception as e:
            return {"error": f"Price per square foot calculation failed: {str(e)}"}

    def _calculate_operating_expense_ratio(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate operating expense ratio."""
        try:
            operating_expenses = values.get("operating_expenses", 0)
            gross_operating_income = values.get("gross_operating_income", 0)
            
            if gross_operating_income == 0:
                return {"error": "Gross operating income cannot be zero"}
                
            expense_ratio = (operating_expenses / gross_operating_income) * 100
            return {
                "operating_expense_ratio": round(expense_ratio, 2),
                "operating_expenses": operating_expenses,
                "gross_operating_income": gross_operating_income
            }
        except Exception as e:
            return {"error": f"Operating expense ratio calculation failed: {str(e)}"}

    def _calculate_dscr(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Calculate Debt Service Coverage Ratio."""
        try:
            noi = values.get("noi", 0)
            debt_service = values.get("debt_service", 0)
            
            if debt_service == 0:
                return {"error": "Debt service cannot be zero"}
                
            dscr = noi / debt_service
            return {
                "dscr": round(dscr, 2),
                "noi": noi,
                "debt_service": debt_service,
                "interpretation": self._interpret_dscr(dscr)
            }
        except Exception as e:
            return {"error": f"DSCR calculation failed: {str(e)}"}
            
    def _interpret_dscr(self, dscr: float) -> str:
        """Interpret DSCR value."""
        if dscr >= 1.5:
            return "Strong debt service coverage"
        elif dscr >= 1.25:
            return "Good debt service coverage"
        elif dscr >= 1.0:
            return "Adequate debt service coverage"
        else:
            return "Poor debt service coverage - potential risk"