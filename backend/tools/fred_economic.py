from typing import Optional, List, Dict, Any, ClassVar
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, PrivateAttr
import os
from dotenv import load_dotenv
from fredapi import Fred
from logger import setup_logger
import pandas as pd
from datetime import datetime, timedelta

logger = setup_logger(__name__)
load_dotenv()

class FREDSearchInput(BaseModel):
    series_id: str = Field(..., description="FRED series ID to look up (e.g., 'GDP' for Gross Domestic Product)")
    observation_start: Optional[str] = Field(
        default=None,
        description="Start date for data (YYYY-MM-DD format)"
    )
    observation_end: Optional[str] = Field(
        default=None,
        description="End date for data (YYYY-MM-DD format)"
    )
    units: Optional[str] = Field(
        default="lin",
        description="Data transformation (e.g., 'lin' for linear, 'chg' for change)"
    )

class FREDEconomicTool(StructuredTool):
    name: ClassVar[str] = "fred_economic_data"
    description: ClassVar[str] = "Fetch economic data from FRED (Federal Reserve Economic Data)"
    args_schema: ClassVar[type[BaseModel]] = FREDSearchInput
    _fred: Fred = PrivateAttr()
    
    def __init__(self, **data):
        super().__init__(**data)
        self._fred = Fred(api_key=os.getenv("FRED_API_KEY"))
        
    def _process_dates(self, observation_start: Optional[str], observation_end: Optional[str]) -> tuple:
        if not observation_end:
            observation_end = datetime.now().strftime("%Y-%m-%d")
        if not observation_start:
            # Default to 1 year of data if no start date provided
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            observation_start = start_date
        return observation_start, observation_end
    
    def _run(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        units: str = "lin"
    ) -> Dict[str, Any]:
        """
        Synchronous fallback that raises NotImplementedError.
        Use _arun for async operations.
        """
        raise NotImplementedError("FREDEconomicTool only supports async operations")

    async def _arun(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        units: str = "lin"
    ) -> Dict[str, Any]:
        """
        Fetch economic data from FRED asynchronously.
        
        Args:
            series_id: FRED series ID
            observation_start: Start date (YYYY-MM-DD)
            observation_end: End date (YYYY-MM-DD)
            units: Data transformation type
            
        Returns:
            Dict containing the economic data
        """
        try:
            import asyncio
            
            # Process dates
            start_date, end_date = self._process_dates(observation_start, observation_end)
            
            # Fetch data using asyncio.to_thread to make the sync FRED API call non-blocking
            data = await asyncio.to_thread(
                self._fred.get_series,
                series_id,
                observation_start=start_date,
                observation_end=end_date,
                units=units
            )
            
            # Convert data to a format that can be JSON serialized
            if isinstance(data, pd.Series):
                data_dict = {
                    str(date): float(value) if pd.notna(value) else None
                    for date, value in data.items()
                }
            else:
                data_dict = {}
            
            # Get series information
            series_info = await asyncio.to_thread(self._fred.get_series_info, series_id)
            
            return {
                "series_id": series_id,
                "title": series_info.get("title", ""),
                "units": series_info.get("units", ""),
                "frequency": series_info.get("frequency", ""),
                "observation_start": start_date,
                "observation_end": end_date,
                "data": data_dict
            }
            
        except Exception as e:
            logger.error(f"Error fetching FRED data: {str(e)}")
            return {
                "error": str(e),
                "series_id": series_id,
                "observation_start": observation_start,
                "observation_end": observation_end
            }