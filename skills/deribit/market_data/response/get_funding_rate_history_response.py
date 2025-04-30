from typing import List

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for items in the 'result' list ---
class FundingRateHistoryItem(BaseModel):
    """Represents a single historical funding rate data point."""

    timestamp: int = Field(
        description="The timestamp (milliseconds since the Unix epoch)."
    )
    index_price: float = Field(description="Index price at the time.")
    prev_index_price: float = Field(description="Index price at the previous interval.")
    interest_8h: float = Field(
        description="8-hour funding rate calculated at this time."
    )
    interest_1h: float = Field(
        description="1-hour funding rate calculated at this time."
    )


# --- Main Response Model ---
class GetFundingRateHistoryResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_funding_rate_history endpoint.
    The result is a list of funding rate history data points.
    Parsing and validation happen during instantiation.
    """

    result: List[FundingRateHistoryItem] = Field(
        description="List of historical funding rate data points."
    )
