import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_ticker_response import (
    GetTickerResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetTicker tool
class DeribitGetTickerInput(BaseModel):
    """Input for DeribitGetTicker tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (e.g., BTC-PERPETUAL). (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)",
    )


# DeribitGetTicker tool to fetch ticker information from Deribit API
class DeribitGetTicker(DeribitBaseTool):
    """Tool to retrieve ticker information for a specific instrument from Deribit API."""

    name: str = "get_ticker"
    description: str = "Get ticker information for an instrument."
    args_schema: Type[BaseModel] = DeribitGetTickerInput

    async def _arun(
        self,
        instrument_name: str,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch ticker information for a specific instrument and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/ticker with params: {params}")
            raw_json = await self.api.get("/api/v2/public/ticker", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetTickerResponse)
            logger.info(
                f"Successfully fetched ticker for {instrument_name} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting ticker for {instrument_name}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get ticker for {instrument_name}. Reason: {e}"
            ) from e
