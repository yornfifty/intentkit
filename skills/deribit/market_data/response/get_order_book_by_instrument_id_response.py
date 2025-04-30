from pydantic import Field

# Reusing models from the previous get_order_book response
from skills.deribit.base_response import DeribitBaseResponse
from skills.deribit.market_data.response.get_order_book_response import (
    GetOrderBookResult,
)


# --- Main Response Model ---
class GetOrderBookByInstrumentIdResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the
    /public/get_order_book_by_instrument_id endpoint.
    Parsing and validation happen during instantiation.
    Uses reused models for the result structure.
    """

    result: GetOrderBookResult = Field(
        description="Contains the detailed order book and market data."
    )
