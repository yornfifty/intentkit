from typing import Optional

from pydantic import BaseModel, Field

from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class GetIndexPriceResult(BaseModel):
    """Result object containing the index price and estimated delivery price."""

    index_price: float = Field(description="Value of requested index.")
    estimated_delivery_price: Optional[float] = (
        Field(  # Marked optional as it might not always be present or relevant
            default=None,
            description="Estimated delivery price for the market. For more details, see Documentation > General > Expiration Price.",
        )
    )


# --- Main Response Model ---
class GetIndexPriceResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_index_price endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetIndexPriceResult = Field(
        description="Contains the index price and estimated delivery price."
    )
