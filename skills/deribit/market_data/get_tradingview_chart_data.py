import logging
from typing import Any, Literal, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_tradingview_chart_data_response import (
    GetTradingviewChartDataResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetTradingviewChartData tool
class DeribitGetTradingviewChartDataInput(BaseModel):
    """Input for DeribitGetTradingviewChartData tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name. (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)",
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    resolution: Literal[
        "1", "3", "5", "10", "15", "30", "60", "120", "180", "360", "720", "1D"
    ] = Field(
        ...,
        description="Chart bars resolution in minutes (e.g., '60') or '1D'.",
    )


# DeribitGetTradingviewChartData tool to fetch TradingView chart data from Deribit API
class DeribitGetTradingviewChartData(DeribitBaseTool):
    """Tool to retrieve TradingView candle chart data for a specific instrument and resolution from Deribit API."""

    name: str = "get_tradingview_chart_data"
    description: str = (
        "Publicly available market data used to generate a TradingView candle chart."
    )
    args_schema: Type[BaseModel] = DeribitGetTradingviewChartDataInput

    async def _arun(
        self,
        instrument_name: str,
        start_timestamp: int,
        end_timestamp: int,
        resolution: Literal[
            "1", "3", "5", "10", "15", "30", "60", "120", "180", "360", "720", "1D"
        ],
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch TradingView chart data for a specific instrument, time range, and resolution,
        and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "resolution": resolution,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_tradingview_chart_data with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_tradingview_chart_data", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetTradingviewChartDataResponse
            )
            logger.info(
                f"Successfully fetched TradingView chart data for {instrument_name} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting TradingView chart data for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get TradingView chart data for {instrument_name}. Reason: {e}"
            ) from e
