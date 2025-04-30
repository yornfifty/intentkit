import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_last_trades_by_instrument_and_time_response import (
    GetLastTradesByInstrumentAndTimeResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetLastTradesByInstrumentAndTime tool
class DeribitGetLastTradesByInstrumentAndTimeInput(BaseModel):
    """Input for DeribitGetLastTradesByInstrumentAndTime tool."""

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
    count: Optional[int] = Field(
        10, description="Number of requested items, default - 10."
    )
    sorting: Optional[Literal["asc", "desc", "default"]] = Field(
        None,
        description="Direction of results sorting (default value means no sorting).",
    )


# DeribitGetLastTradesByInstrumentAndTime tool to fetch last trades by instrument and time from Deribit API
class DeribitGetLastTradesByInstrumentAndTime(DeribitBaseTool):
    """Tool to retrieve the latest trades for a specific instrument within a time range from Deribit API."""

    name: str = "get_last_trades_by_instrument_and_time"
    description: str = "Retrieve the latest trades that have occurred for a specific instrument and within a given time range."
    args_schema: Type[BaseModel] = DeribitGetLastTradesByInstrumentAndTimeInput

    async def _arun(
        self,
        instrument_name: str,
        start_timestamp: int,
        end_timestamp: int,
        count: Optional[int] = 10,
        sorting: Optional[Literal["asc", "desc", "default"]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch the latest trades for a specific instrument and time range, with optional filters,
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
            }
            if count is not None:
                params["count"] = count
            if sorting is not None:
                params["sorting"] = sorting

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_last_trades_by_instrument_and_time with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_last_trades_by_instrument_and_time", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetLastTradesByInstrumentAndTimeResponse
            )
            logger.info(
                f"Successfully fetched last trades for {instrument_name} in time range and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting last trades for {instrument_name} in time range: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get last trades for {instrument_name} in time range. Reason: {e}"
            ) from e
