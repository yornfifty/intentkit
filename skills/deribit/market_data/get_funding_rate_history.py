import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_funding_rate_history_response import (
    GetFundingRateHistoryResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetFundingRateHistory tool
class DeribitGetFundingRateHistoryInput(BaseModel):
    """Input for DeribitGetFundingRateHistory tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (must be a PERPETUAL) (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )


# DeribitGetFundingRateHistory tool to fetch funding rate history from Deribit API
class DeribitGetFundingRateHistory(DeribitBaseTool):
    """Tool to retrieve hourly historical funding rates for a perpetual instrument from Deribit API."""

    name: str = "get_funding_rate_history"
    description: str = "Retrieves hourly historical interest rate (funding rate) for requested PERPETUAL instrument."
    args_schema: Type[BaseModel] = DeribitGetFundingRateHistoryInput

    async def _arun(
        self,
        instrument_name: str,
        start_timestamp: int,
        end_timestamp: int,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch hourly historical funding rates for a specific perpetual instrument and time range,
        and return the formatted result.
        """
        # Basic validation reminder
        if "PERPETUAL" not in instrument_name.upper():
            logger.warning(
                f"Instrument '{instrument_name}' might not be a perpetual. API call might fail or return unexpected results."
            )

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

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_funding_rate_history with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_funding_rate_history", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetFundingRateHistoryResponse
            )
            logger.info(
                f"Successfully fetched funding rate history for {instrument_name} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting funding rate history for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get funding rate history for {instrument_name}. Reason: {e}"
            ) from e
