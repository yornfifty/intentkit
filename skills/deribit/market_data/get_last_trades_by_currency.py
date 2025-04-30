import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_last_trades_by_currency_response import (
    GetLastTradesByCurrencyResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetLastTradesByCurrency tool
class DeribitGetLastTradesByCurrencyInput(BaseModel):
    """Input for DeribitGetLastTradesByCurrency tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol."
    )
    kind: Optional[
        Literal[
            "future", "option", "spot", "future_combo", "option_combo", "combo", "any"
        ]
    ] = Field(
        None,
        description='Instrument kind filter (optional). "combo" for any combo, "any" for all.',
    )
    start_id: Optional[str] = Field(
        None,
        description="The ID of the first trade to be returned (format depends on currency).",
    )
    end_id: Optional[str] = Field(
        None,
        description="The ID of the last trade to be returned (format depends on currency).",
    )
    start_timestamp: Optional[int] = Field(
        None,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: Optional[int] = Field(
        None,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    count: Optional[int] = Field(
        10, description="Number of requested items, default - 10."
    )
    sorting: Optional[Literal["asc", "desc", "default"]] = Field(
        None,
        description="Direction of results sorting (default value means no sorting).",
    )


# DeribitGetLastTradesByCurrency tool to fetch last trades by currency from Deribit API
class DeribitGetLastTradesByCurrency(DeribitBaseTool):
    """Tool to retrieve the latest trades for instruments of a specific currency from Deribit API."""

    name: str = "get_last_trades_by_currency"
    description: str = "Retrieve the latest trades that have occurred for instruments in a specific currency symbol."
    args_schema: Type[BaseModel] = DeribitGetLastTradesByCurrencyInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        kind: Optional[
            Literal[
                "future",
                "option",
                "spot",
                "future_combo",
                "option_combo",
                "combo",
                "any",
            ]
        ] = None,
        start_id: Optional[str] = None,
        end_id: Optional[str] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        count: Optional[int] = 10,
        sorting: Optional[Literal["asc", "desc", "default"]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch the latest trades for a specific currency, with optional filters,
        and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"currency": currency}
            if kind is not None:
                params["kind"] = kind
            if start_id is not None:
                params["start_id"] = start_id
            if end_id is not None:
                params["end_id"] = end_id
            if start_timestamp is not None:
                params["start_timestamp"] = start_timestamp
            if end_timestamp is not None:
                params["end_timestamp"] = end_timestamp
            if count is not None:
                params["count"] = count
            if sorting is not None:
                params["sorting"] = sorting

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_last_trades_by_currency with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_last_trades_by_currency", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = format_json_result(
                raw_json, GetLastTradesByCurrencyResponse
            )
            logger.info(
                f"Successfully fetched last trades for {currency} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting last trades for {currency}: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get last trades for {currency}. Reason: {e}"
            ) from e
