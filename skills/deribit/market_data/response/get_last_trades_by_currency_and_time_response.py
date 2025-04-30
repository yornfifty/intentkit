from pydantic import Field

from skills.deribit.base_response import DeribitBaseResponse
from skills.deribit.market_data.response.get_last_trades_by_instrument_response import (
    GetLastTradesResult,  # Reusing the result structure model
)


# --- Main Response Model ---
class GetLastTradesByCurrencyAndTimeResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the
    /public/get_last_trades_by_currency_and_time endpoint.
    Parsing and validation happen during instantiation.
    Uses reused models for trade items and result structure.
    """

    result: GetLastTradesResult = Field(
        description="Contains the list of trades and pagination information."
    )


# Optional: If you prefer explicit definition even if identical
# You could copy the definitions of TradeItem and GetLastTradesResult here
# but reusing is generally better practice.
