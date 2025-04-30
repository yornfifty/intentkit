from typing import List

from pydantic import Field

from skills.deribit.base_response import DeribitBaseResponse
from skills.deribit.market_data.response.get_book_summary_by_currency_response import (
    BookSummaryInstrument,
)

# Reuse the item model from the other endpoint as the structure is the same!


# --- Main Response Model (Inherits from Base) ---
class GetBookSummaryByInstrumentResponse(DeribitBaseResponse):  # Inherit from base
    """
    Represents the full successful JSON response from the /public/get_book_summary_by_instrument endpoint.
    Inherits common fields from DeribitBaseResponse.
    NOTE: The result is a list containing exactly one summary item for the requested instrument.
    """

    # Define the specific 'result' field, reusing the item model
    # The API returns a list even for a single instrument lookup.
    result: List[BookSummaryInstrument] = Field(
        description="List containing the book summary for the specified instrument."
    )
