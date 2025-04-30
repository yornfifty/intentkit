from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class GetVolatilityIndexDataResult(BaseModel):
    """Result object containing volatility index candle data."""

    # Data format: [timestamp_ms, open, high, low, close]
    data: List[Tuple[int, float, float, float, float]] = Field(
        description="Candles as an array of arrays with 5 values each: timestamp (ms), open, high, low, close."
    )
    continuation: Optional[int] = Field(
        default=None,
        description="Continuation token to be used as 'end_timestamp' for the next request. NULL when no more data.",
    )


# --- Main Response Model ---
class GetVolatilityIndexDataResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_volatility_index_data endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetVolatilityIndexDataResult = Field(
        description="Contains the volatility index candle data and continuation token."
    )
