from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse

# Reusing models from the other last_trades responses as the structure is identical
from skills.deribit.market_data.response.get_last_trades_by_instrument_response import (
    GetLastTradesResult,  # Reusing the result structure model
)


# --- Main Response Model ---
# Renaming the result class for clarity, although it reuses the structure.
class GetLastTradesByInstrumentAndTimeResult(GetLastTradesResult):
    """Result object containing trade data and pagination info for trades filtered by instrument and time."""

    pass


class GetLastTradesByInstrumentAndTimeResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_last_trades_by_instrument_and_time endpoint.
    Parsing and validation happen during instantiation. Uses reused models for trade items and result structure.
    """

    result: GetLastTradesByInstrumentAndTimeResult = Field(
        description="Contains the list of trades for the instrument within the time range and pagination information."
    )
