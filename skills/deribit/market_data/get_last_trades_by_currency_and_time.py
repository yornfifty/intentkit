import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_last_trades_by_currency_and_time_response import (
    GetLastTradesByCurrencyAndTimeResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetLastTradesByCurrencyAndTime tool
class DeribitGetLastTradesByCurrencyAndTimeInput(BaseModel):
    """Input for DeribitGetLastTradesByCurrencyAndTime tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="The currency symbol."
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    kind: Optional[
        Literal[
            "future", "option", "spot", "future_combo", "option_combo", "combo", "any"
        ]
    ] = Field(
        None,
        description='Instrument kind, "combo" for any combo or "any" for all. If not provided instruments of all kinds are considered.',
    )
    count: Optional[int] = Field(
        None, description="Number of requested items, default - 10."
    )
    sorting: Optional[Literal["asc", "desc", "default"]] = Field(
        None,
        description="Direction of results sorting (default value means no sorting).",
    )


# DeribitGetLastTradesByCurrencyAndTime tool to fetch last trades by currency and time from Deribit API
class DeribitGetLastTradesByCurrencyAndTimeTool(DeribitBaseTool):
    """Tool to retrieve the latest trades for a specific currency within a time range from Deribit API."""

    name: str = "get_last_trades_by_currency_and_time"
    description: str = (
        "Retrieve the latest trades that have occurred for instruments "
        "in a specific currency symbol and within a given time range."
    )
    args_schema: Type[BaseModel] = DeribitGetLastTradesByCurrencyAndTimeInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        start_timestamp: int,
        end_timestamp: int,
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
        count: Optional[int] = None,
        sorting: Optional[Literal["asc", "desc", "default"]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch the latest trades for a specific currency within a given time range.
        Optionally filter by instrument kind, count, and sorting.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare input data using the Pydantic model for validation
            params = {
                "currency": currency,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
            }

            # Add optional parameters if they are provided
            if kind is not None:
                params["kind"] = kind
            if count is not None:
                params["count"] = count
            if sorting is not None:
                params["sorting"] = sorting

            # Call the underlying generic API request method
            raw_json = await self.get(
                "/api/v2/public/get_last_trades_by_currency_and_time", params=params
            )
            return format_json_result(raw_json, GetLastTradesByCurrencyAndTimeResponse)

            # Parse the JSON response using the Pydantic model
            return GetLastTradesByCurrencyAndTimeResponse(**raw_json)

        except Exception as e:
            logger.error("Error getting last trades by currency and time: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
