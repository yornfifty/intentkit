from typing import List, Tuple

from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Main Response Model ---
class GetMarkPriceHistoryResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_mark_price_history endpoint.
    The result is a list of timestamp-markprice pairs.
    Parsing and validation happen during instantiation.
    """

    # Result format: List of [timestamp_ms, markprice_value]
    result: List[Tuple[int, float]] = Field(
        description="List of timestamp-markprice pairs."
    )
