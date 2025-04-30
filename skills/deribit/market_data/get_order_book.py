import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_order_book_response import (
    GetOrderBookResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetOrderBook tool
class DeribitGetOrderBookInput(BaseModel):
    """Input for DeribitGetOrderBook tool."""

    instrument_name: str = Field(
        ...,
        description="The instrument name for which to retrieve the order book (e.g., BTC-PERPETUAL). (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)",
    )
    depth: Optional[Literal[1, 5, 10, 20, 50, 100, 1000, 10000]] = Field(
        None, description="The number of entries to return for bids and asks."
    )


# DeribitGetOrderBook tool to fetch order book from Deribit API
class DeribitGetOrderBookTool(DeribitBaseTool):
    """Tool to retrieve the order book, along with other market values for a given instrument from Deribit API."""

    name: str = "get_order_book"
    description: str = "Retrieves the order book, along with other market values for a given instrument."
    args_schema: Type[BaseModel] = DeribitGetOrderBookInput

    async def _arun(
        self,
        instrument_name: str,
        depth: Optional[Literal[1, 5, 10, 20, 50, 100, 1000, 10000]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch the order book for a specific instrument.
        Allows specifying the depth of the book.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"instrument_name": instrument_name}
            if depth is not None:
                params["depth"] = depth

            # --- API Call Logic Merged In ---

            logger.debug(f"Calling /public/get_order_book with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_order_book", params=params
            )
            return format_json_result(raw_json, GetOrderBookResponse)

        except Exception as e:
            logger.error(f"Error getting order book for {instrument_name}: {str(e)}")
            # Reraise exception, potentially wrapping it or adding context
            # Ensure sensitive details aren't leaked if this bubbles up to the user.
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get order book for {instrument_name}. Reason: {e}"
            ) from e
