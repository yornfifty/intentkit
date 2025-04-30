import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_last_settlements_by_currency_response import (
    GetLastSettlementsByCurrencyResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetLastSettlementsByCurrency tool
class DeribitGetLastSettlementsByCurrencyInput(BaseModel):
    """Input for DeribitGetLastSettlementsByCurrency tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol."
    )
    type: Optional[Literal["settlement", "delivery", "bankruptcy"]] = Field(
        None, description="Settlement type filter (optional)."
    )
    count: Optional[int] = Field(
        20, description="Number of requested items, default - 20."
    )
    continuation: Optional[str] = Field(
        None,
        description="Continuation token for pagination (obtained from previous response).",
    )
    search_start_timestamp: Optional[int] = Field(
        None,
        description="The latest timestamp to return result from (milliseconds since the UNIX epoch).",
    )


# DeribitGetLastSettlementsByCurrency tool to fetch settlement history from Deribit API
class DeribitGetLastSettlementsByCurrency(DeribitBaseTool):
    """Tool to retrieve historical settlement, delivery, and bankruptcy events for a currency from Deribit API."""

    name: str = "get_last_settlements_by_currency"
    description: str = (
        "Retrieves historical settlement, delivery and bankruptcy events "
        "coming from all instruments within a given currency."
    )
    args_schema: Type[BaseModel] = DeribitGetLastSettlementsByCurrencyInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        type: Optional[Literal["settlement", "delivery", "bankruptcy"]] = None,
        count: Optional[int] = 20,
        continuation: Optional[str] = None,
        search_start_timestamp: Optional[int] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch historical settlement events for a currency, with optional filters and pagination,
        and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"currency": currency}
            if type is not None:
                params["type"] = type
            if count is not None:
                params["count"] = count
            if continuation is not None:
                params["continuation"] = continuation
            if search_start_timestamp is not None:
                params["search_start_timestamp"] = search_start_timestamp

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_last_settlements_by_currency with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_last_settlements_by_currency", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetLastSettlementsByCurrencyResponse
            )
            logger.info(
                f"Successfully fetched last settlements for {currency} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting last settlements for {currency}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get last settlements for {currency}. Reason: {e}"
            ) from e
