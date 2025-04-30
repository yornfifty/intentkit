import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import (
    DeribitBaseTool,
)

# Updated import path for the response model
from skills.deribit.market_data.response.get_order_book_by_instrument_id_response import (
    GetOrderBookByInstrumentIdResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetOrderBookByInstrumentId tool
class DeribitGetOrderBookByInstrumentIdInput(BaseModel):
    """Input for DeribitGetOrderBookByInstrumentId tool."""

    instrument_id: int = Field(
        ...,
        description="The instrument ID for which to retrieve the order book.",
    )
    depth: Optional[Literal[1, 5, 10, 20, 50, 100, 1000, 10000]] = Field(
        None, description="The number of entries to return for bids and asks."
    )


# DeribitGetOrderBookByInstrumentId tool to fetch order book by ID from Deribit API
class DeribitGetOrderBookByInstrumentIdTool(DeribitBaseTool):
    """Tool to retrieve the order book, along with other market values for a given instrument ID from Deribit API."""

    name: str = "get_order_book_by_instrument_id"
    description: str = "Retrieves the order book, along with other market values for a given instrument ID."
    args_schema: Type[BaseModel] = DeribitGetOrderBookByInstrumentIdInput

    async def _arun(
        self,
        instrument_id: int,
        depth: Optional[Literal[1, 5, 10, 20, 50, 100, 1000, 10000]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch the order book for a specific instrument ID.
        Allows specifying the depth of the book.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {"instrument_id": instrument_id}
            if depth is not None:
                params["depth"] = depth

            # --- API Call Logic Merged In ---

            logger.debug(
                f"Calling /public/get_order_book_by_instrument_id with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_order_book_by_instrument_id", params=params
            )
            return format_json_result(raw_json, GetOrderBookByInstrumentIdResponse)

        except Exception as e:
            logger.error(
                f"Error getting order book for instrument ID {instrument_id}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get order book for instrument ID {instrument_id}. Reason: {e}"
            ) from e
