import logging
from typing import Any, Literal, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_volatility_index_data_response import (
    GetVolatilityIndexDataResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetVolatilityIndexData tool
class DeribitGetVolatilityIndexDataInput(BaseModel):
    """Input for DeribitGetVolatilityIndexData tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol (e.g., BTC, ETH)."
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    resolution: Literal["1", "60", "3600", "43200", "1D"] = Field(
        ...,
        description="Time resolution in seconds (e.g., '60' for 1 minute) or '1D' for daily.",
    )


# DeribitGetVolatilityIndexData tool to fetch volatility index data from Deribit API
class DeribitGetVolatilityIndexDataTool(DeribitBaseTool):
    """Tool to retrieve volatility index candle data for a specific currency and time range from Deribit API."""

    name: str = "get_volatility_index_data"
    description: str = "Public market data request for volatility index candles."
    args_schema: Type[BaseModel] = DeribitGetVolatilityIndexDataInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        start_timestamp: int,
        end_timestamp: int,
        resolution: Literal["1", "60", "3600", "43200", "1D"],
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch volatility index candle data for a specific currency, time range, and resolution.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "currency": currency,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "resolution": resolution,
            }

            logger.debug(
                f"Calling /public/get_volatility_index_data with params: {params}"
            )
            # Using self.api.get as requested
            raw_json = await self.api.get(
                "/api/v2/public/get_volatility_index_data", params=params
            )

            return format_json_result(raw_json, GetVolatilityIndexDataResponse)

        except Exception as e:
            logger.error(
                f"Error getting volatility index data for {currency}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get volatility index data for {currency}. Reason: {e}"
            ) from e
