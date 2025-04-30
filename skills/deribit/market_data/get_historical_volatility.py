import logging
from typing import Any, Literal, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_historical_volatility_response import (
    GetHistoricalVolatilityResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetHistoricalVolatility tool
class DeribitGetHistoricalVolatilityInput(BaseModel):
    """Input for DeribitGetHistoricalVolatility tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol (e.g., BTC, ETH)."
    )


# DeribitGetHistoricalVolatility tool to fetch historical volatility from Deribit API
class DeribitGetHistoricalVolatilityTool(DeribitBaseTool):
    """Tool to retrieve historical volatility data for a specific currency from Deribit API."""

    name: str = "get_historical_volatility"
    description: str = (
        "Provides information about historical volatility for a given cryptocurrency."
    )
    args_schema: Type[BaseModel] = DeribitGetHistoricalVolatilityInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch historical volatility data for a specific currency.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "currency": currency,
            }

            logger.debug(
                f"Calling /public/get_historical_volatility with params: {params}"
            )
            # Using self.api.get as requested
            raw_json = await self.api.get(
                "/api/v2/public/get_historical_volatility", params=params
            )

            return format_json_result(raw_json, GetHistoricalVolatilityResponse)

        except Exception as e:
            logger.error(
                f"Error getting historical volatility for {currency}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get historical volatility for {currency}. Reason: {e}"
            ) from e
