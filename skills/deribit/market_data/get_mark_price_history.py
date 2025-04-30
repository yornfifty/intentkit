import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_mark_price_history_response import (
    GetMarkPriceHistoryResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetMarkPriceHistory tool
class DeribitGetMarkPriceHistoryInput(BaseModel):
    """Input for DeribitGetMarkPriceHistory tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (e.g., BTC-PERPETUAL). (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)",
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )


# DeribitGetMarkPriceHistory tool to fetch mark price history from Deribit API
class DeribitGetMarkPriceHistoryTool(DeribitBaseTool):
    """Tool to retrieve the mark price history for a given instrument and time range from Deribit API."""

    name: str = "get_mark_price_history"
    description: str = (
        "Public request for 5min history of markprice values for the instrument. "
        "Available only for a subset of options; other instruments return an empty list."
    )
    args_schema: Type[BaseModel] = DeribitGetMarkPriceHistoryInput

    async def _arun(
        self,
        instrument_name: str,
        start_timestamp: int,
        end_timestamp: int,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch mark price history for a specific instrument and time range.
        Note: Only works for specific options used in volatility index calculations.
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

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_mark_price_history with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_mark_price_history", params=params
            )
            return format_json_result(raw_json, GetMarkPriceHistoryResponse)

        except Exception as e:
            logger.error(
                f"Error getting mark price history for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get mark price history for {instrument_name}. Reason: {e}"
            ) from e
