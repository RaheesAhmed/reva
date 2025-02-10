from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from enum import Enum

class AdjustmentType(str, Enum):
    """Types of adjustments that can be made to comparable properties"""
    MARKET_CONDITIONS = "market_conditions"
    LOCATION = "location"
    SIZE = "size"
    AGE = "age"
    QUALITY = "quality"
    AMENITIES = "amenities"
    PARKING = "parking"
    LEASE_TERMS = "lease_terms"

class ComparableProperty(BaseModel):
    """Structure for comparable property data"""
    property_id: str
    address: str
    sale_date: datetime
    sale_price: float
    price_per_sf: float
    property_type: str
    building_size: float
    year_built: int
    occupancy_rate: float
    quality_rating: int  # 1-5 scale
    amenities: List[str]
    parking_ratio: float
    lease_type: str
    cap_rate: Optional[float] = None
    noi: Optional[float] = None

class MarketAdjustment(BaseModel):
    """Structure for market adjustment calculations"""
    adjustment_type: AdjustmentType
    percentage: float
    rationale: str
    impact_value: float

class ComparableAnalysisInput(BaseModel):
    """Input schema for comparable analysis"""
    property_type: str = Field(description="Type of property (e.g., office, retail, industrial)")
    location: str = Field(description="Property location")
    building_size: float = Field(description="Building size in square feet")
    year_built: int = Field(description="Year the property was built")
    quality_rating: int = Field(description="Quality rating on a scale of 1-5")
    max_comps: int = Field(default=5, description="Maximum number of comparables to return")
    max_age_years: int = Field(default=2, description="Maximum age of comparable sales in years")
    radius_miles: float = Field(default=5.0, description="Search radius in miles")
    specific_adjustments: Optional[Dict[str, float]] = Field(
        default=None,
        description="Specific adjustment overrides for certain factors"
    )

class ComparableAnalysisOutput(BaseModel):
    """Output schema for comparable analysis"""
    subject_property: Dict[str, Any]
    comparable_properties: List[ComparableProperty]
    adjustments: List[MarketAdjustment]
    adjusted_values: Dict[str, float]
    final_value_range: Dict[str, float]
    market_trends: Dict[str, Any]
    confidence_score: float
    supporting_data: Dict[str, Any]

class ComparableAnalysisTool(BaseTool):
    """Tool for generating and analyzing comparable properties"""
    
    name: str = "comparable_analysis"
    description: str = """Analyzes comparable properties and generates market-adjusted valuations.
    Provides recent sales data, market adjustments, and value ranges."""
    
    args_schema: type[ComparableAnalysisInput] = ComparableAnalysisInput
    return_type: type[ComparableAnalysisOutput] = ComparableAnalysisOutput

    def _fetch_recent_sales(
        self,
        property_type: str,
        location: str,
        max_comps: int,
        max_age_years: int,
        radius_miles: float
    ) -> List[ComparableProperty]:
        """Fetch recent comparable sales from the database"""
        # This would typically integrate with a real estate database
        # For demonstration, returning mock data
        current_date = datetime.now()
        mock_comps = [
            ComparableProperty(
                property_id=f"PROP{i}",
                address=f"{i*100} Main St, {location}",
                sale_date=current_date - timedelta(days=i*90),
                sale_price=10000000 + (i * 500000),
                price_per_sf=350 + (i * 10),
                property_type=property_type,
                building_size=25000 + (i * 1000),
                year_built=2010 - i,
                occupancy_rate=0.95 - (i * 0.02),
                quality_rating=4,
                amenities=["Lobby", "Parking", "Security"],
                parking_ratio=3.0,
                lease_type="NNN",
                cap_rate=0.065 + (i * 0.002),
                noi=650000 + (i * 25000)
            )
            for i in range(max_comps)
        ]
        return mock_comps

    def _calculate_market_adjustment(
        self,
        comp: ComparableProperty,
        subject: Dict[str, Any],
        adjustment_type: AdjustmentType,
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> MarketAdjustment:
        """Calculate specific market adjustments"""
        
        if adjustment_type == AdjustmentType.MARKET_CONDITIONS:
            # Time-based market adjustment (e.g., 3% per year appreciation)
            months_diff = (datetime.now() - comp.sale_date).days / 30.44
            adjustment_pct = (months_diff * 0.0025)  # 3% annual appreciation
            
            return MarketAdjustment(
                adjustment_type=adjustment_type,
                percentage=adjustment_pct,
                rationale=f"Market appreciation over {months_diff:.1f} months",
                impact_value=comp.sale_price * adjustment_pct
            )
            
        elif adjustment_type == AdjustmentType.LOCATION:
            # Location quality adjustment
            location_factor = 0.05  # 5% per quality point difference
            return MarketAdjustment(
                adjustment_type=adjustment_type,
                percentage=location_factor,
                rationale="Location quality adjustment",
                impact_value=comp.sale_price * location_factor
            )
            
        elif adjustment_type == AdjustmentType.SIZE:
            # Size adjustment (economies of scale)
            size_diff_pct = (subject["building_size"] - comp.building_size) / comp.building_size
            size_factor = size_diff_pct * -0.1  # -10% adjustment per 100% size difference
            
            return MarketAdjustment(
                adjustment_type=adjustment_type,
                percentage=size_factor,
                rationale=f"Size difference adjustment: {size_diff_pct:.1%}",
                impact_value=comp.sale_price * size_factor
            )
            
        else:
            # Default minimal adjustment
            return MarketAdjustment(
                adjustment_type=adjustment_type,
                percentage=0.0,
                rationale="No adjustment needed",
                impact_value=0.0
            )

    def _apply_adjustments(
        self,
        comps: List[ComparableProperty],
        subject: Dict[str, Any],
        specific_adjustments: Optional[Dict[str, float]] = None
    ) -> tuple[List[MarketAdjustment], Dict[str, float]]:
        """Apply all relevant adjustments to comparable properties"""
        all_adjustments = []
        adjusted_values = {}
        
        for comp in comps:
            comp_adjustments = []
            
            # Calculate standard adjustments
            for adj_type in AdjustmentType:
                if specific_adjustments and adj_type.value in specific_adjustments:
                    # Use provided specific adjustment
                    adjustment = MarketAdjustment(
                        adjustment_type=adj_type,
                        percentage=specific_adjustments[adj_type.value],
                        rationale=f"User-specified {adj_type.value} adjustment",
                        impact_value=comp.sale_price * specific_adjustments[adj_type.value]
                    )
                else:
                    # Calculate standard adjustment
                    adjustment = self._calculate_market_adjustment(
                        comp,
                        subject,
                        adj_type
                    )
                
                comp_adjustments.append(adjustment)
            
            # Calculate total adjustment for this comp
            total_adjustment = sum(adj.impact_value for adj in comp_adjustments)
            adjusted_value = comp.sale_price + total_adjustment
            
            adjusted_values[comp.property_id] = adjusted_value
            all_adjustments.extend(comp_adjustments)
        
        return all_adjustments, adjusted_values

    def _analyze_market_trends(
        self,
        comps: List[ComparableProperty]
    ) -> Dict[str, Any]:
        """Analyze market trends from comparable data"""
        # Calculate various market metrics
        avg_price_per_sf = sum(c.price_per_sf for c in comps) / len(comps)
        avg_cap_rate = sum(c.cap_rate for c in comps if c.cap_rate) / len([c for c in comps if c.cap_rate])
        
        # Sort by date to analyze trends
        sorted_comps = sorted(comps, key=lambda x: x.sale_date)
        price_trend = [
            {
                "date": c.sale_date.strftime("%Y-%m-%d"),
                "price_per_sf": c.price_per_sf,
                "cap_rate": c.cap_rate
            }
            for c in sorted_comps
        ]
        
        return {
            "average_metrics": {
                "price_per_sf": avg_price_per_sf,
                "cap_rate": avg_cap_rate
            },
            "price_trends": price_trend,
            "market_conditions": "stable",  # This could be more sophisticated
            "absorption_rate": "positive",  # This could be calculated from actual data
            "inventory_levels": "moderate"  # This could be from market database
        }

    def _run(
        self,
        property_type: str,
        location: str,
        building_size: float,
        year_built: int,
        quality_rating: int,
        max_comps: int = 5,
        max_age_years: int = 2,
        radius_miles: float = 5.0,
        specific_adjustments: Optional[Dict[str, float]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> ComparableAnalysisOutput:
        """
        Execute comparable analysis
        """
        # Create subject property profile
        subject_property = {
            "property_type": property_type,
            "location": location,
            "building_size": building_size,
            "year_built": year_built,
            "quality_rating": quality_rating
        }
        
        # Fetch comparable sales
        comps = self._fetch_recent_sales(
            property_type,
            location,
            max_comps,
            max_age_years,
            radius_miles
        )
        
        # Calculate adjustments
        adjustments, adjusted_values = self._apply_adjustments(
            comps,
            subject_property,
            specific_adjustments
        )
        
        # Analyze market trends
        market_trends = self._analyze_market_trends(comps)
        
        # Calculate final value range
        adjusted_values_list = list(adjusted_values.values())
        final_value_range = {
            "min": min(adjusted_values_list),
            "max": max(adjusted_values_list),
            "mean": sum(adjusted_values_list) / len(adjusted_values_list),
            "median": sorted(adjusted_values_list)[len(adjusted_values_list)//2]
        }
        
        # Summarize key adjustments for better readability
        summarized_adjustments = []
        for comp in comps:
            comp_adjustments = [adj for adj in adjustments if abs(adj.impact_value) > 0]
            if comp_adjustments:
                summarized_adjustments.extend(comp_adjustments[:3])  # Keep only significant adjustments
        
        # Format market trends more concisely
        concise_market_trends = {
            "average_price_psf": market_trends["average_metrics"]["price_per_sf"],
            "average_cap_rate": market_trends["average_metrics"]["cap_rate"],
            "market_condition": market_trends["market_conditions"],
            "recent_trend": "Increasing" if market_trends["price_trends"][-1]["price_per_sf"] > market_trends["price_trends"][0]["price_per_sf"] else "Decreasing"
        }
        
        return ComparableAnalysisOutput(
            subject_property=subject_property,
            comparable_properties=comps[:3],  # Limit to top 3 comps for conciseness
            adjustments=summarized_adjustments,
            adjusted_values=adjusted_values,
            final_value_range=final_value_range,
            market_trends=concise_market_trends,
            confidence_score=0.85,
            supporting_data={
                "comp_count": len(comps),
                "data_quality": "high",
                "primary_adjustments": list(set(adj.adjustment_type for adj in summarized_adjustments))
            }
        )

    async def _arun(
        self,
        property_type: str,
        location: str,
        building_size: float,
        year_built: int,
        quality_rating: int,
        max_comps: int = 5,
        max_age_years: int = 2,
        radius_miles: float = 5.0,
        specific_adjustments: Optional[Dict[str, float]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> ComparableAnalysisOutput:
        """Async version of _run"""
        return self._run(
            property_type=property_type,
            location=location,
            building_size=building_size,
            year_built=year_built,
            quality_rating=quality_rating,
            max_comps=max_comps,
            max_age_years=max_age_years,
            radius_miles=radius_miles,
            specific_adjustments=specific_adjustments,
            run_manager=run_manager
        )
