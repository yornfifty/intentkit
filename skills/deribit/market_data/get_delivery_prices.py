import logging
from typing import Any, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_delivery_prices_response import (
    GetDeliveryPricesResponse,
)

# Import the CSV utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetDeliveryPrices tool
class DeribitGetDeliveryPricesInput(BaseModel):
    """Input for DeribitGetDeliveryPrices tool."""

    index_name: str = Field(  # Using str due to long enum list
        ..., description="Index identifier (e.g., btc_usd, eth_usd)."
    )
    offset: Optional[int] = Field(
        0, description="The offset for pagination, default - 0."
    )
    count: Optional[int] = Field(
        10, description="Number of requested items, default - 10."
    )


# DeribitGetDeliveryPrices tool to fetch delivery prices from Deribit API
class DeribitGetDeliveryPrices(DeribitBaseTool):
    """Tool to retrieve delivery prices for a given index from Deribit API."""

    name: str = "get_delivery_prices"
    description: str = "Retrieves delivery prices for the given index."
    args_schema: Type[BaseModel] = DeribitGetDeliveryPricesInput

    async def _arun(
        self,
        index_name: str,
        offset: Optional[int] = 0,
        count: Optional[int] = 10,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (CSV)
        """
        Fetch delivery prices for a specific index with pagination, return as CSV.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "index_name": index_name,
                "offset": offset,
                "count": count,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_delivery_prices with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_delivery_prices", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to CSV string using the utility
            formatted_result = format_json_result(raw_json, GetDeliveryPricesResponse)
            logger.info(
                f"Successfully fetched delivery prices for {index_name} and format the result"
            )
            return formatted_result

        except Exception as e:
            logger.error(f"Error getting delivery prices for {index_name}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get delivery prices for {index_name}. Reason: {e}"
            ) from e
