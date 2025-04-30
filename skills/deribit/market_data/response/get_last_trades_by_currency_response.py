from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse

# Reusing models from the instrument-based trades response as the structure is identical
from skills.deribit.market_data.response.get_last_trades_by_instrument_response import (
    GetLastTradesResult,  # Reusing the result structure model
)


# --- Main Response Model ---
# Although the structure is reused, defining a specific class name improves clarity.
class GetLastTradesByCurrencyResult(GetLastTradesResult):
    """Result object containing trade data and pagination info for trades filtered by currency."""

    pass


class GetLastTradesByCurrencyResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_last_trades_by_currency endpoint.
    Parsing and validation happen during instantiation. Uses reused models for trade items and result structure.
    """

    result: GetLastTradesByCurrencyResult = Field(
        description="Contains the list of trades for the currency and pagination information."
    )
