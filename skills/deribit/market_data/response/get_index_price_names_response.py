from typing import List

from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Main Response Model ---
class GetIndexPriceNamesResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_index_price_names endpoint.
    The result is a list of index name strings.
    Parsing and validation happen during instantiation.
    """

    result: List[str] = Field(
        description="List of all supported Price Index identifiers."
    )
