import logging
from typing import Any, Literal, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_index_response import (
    GetIndexResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetIndex tool
class DeribitGetIndexInput(BaseModel):
    """Input for DeribitGetIndex tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol (e.g., BTC, ETH)."
    )


# DeribitGetIndex tool to fetch index price by currency from Deribit API (DEPRECATED)
class DeribitGetIndex(DeribitBaseTool):
    """
    (DEPRECATED) Tool to retrieve the current index price for instruments of a selected currency from Deribit API.
    Note: This endpoint is deprecated by Deribit and may be removed in the future.
    Consider using /public/get_index_price instead.
    """

    name: str = "get_index"
    description: str = (
        "(DEPRECATED) Retrieves the current index price for the instruments, for the selected currency. "
        "Prefer /public/get_index_price."
    )
    args_schema: Type[BaseModel] = DeribitGetIndexInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch the current index price for a specific currency and return the formatted result.
        WARNING: Uses a deprecated Deribit endpoint.
        """
        logger.warning(
            "Using deprecated Deribit endpoint /public/get_index. Consider migrating to /public/get_index_price."
        )
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "currency": currency,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_index with params: {params}")
            raw_json = await self.api.get("/api/v2/public/get_index", params=params)
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(raw_json, GetIndexResponse)
            logger.info(
                f"Successfully fetched index price for {currency} (using deprecated endpoint) and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting index price for {currency} (using deprecated endpoint): {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get index price for {currency} (deprecated endpoint). Reason: {e}"
            ) from e
