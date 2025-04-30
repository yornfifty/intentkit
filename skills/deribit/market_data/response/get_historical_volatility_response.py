from typing import List, Tuple

from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Main Response Model ---
class GetHistoricalVolatilityResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_historical_volatility endpoint.
    The result is a list of timestamp-value pairs.
    Parsing and validation happen during instantiation.
    """

    # Result format: List of [timestamp_ms, volatility_value]
    result: List[Tuple[int, float]] = Field(
        description="List of timestamp-value pairs representing historical volatility."
    )
