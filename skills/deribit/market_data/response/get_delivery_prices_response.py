from typing import List

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for individual delivery price items ---
class DeliveryPriceItem(BaseModel):
    """Represents a single delivery price entry."""

    date: str = Field(
        description="The event date with year, month and day (e.g., '2020-01-02')."
    )
    delivery_price: float = Field(
        description="The settlement price for the instrument on that date."
    )


# --- Nested Model for the 'result' object ---
class GetDeliveryPricesResult(BaseModel):
    """Result object containing delivery price data and total count."""

    data: List[DeliveryPriceItem] = Field(description="List of delivery price entries.")
    records_total: int = Field(
        description="Total number of available delivery prices for the index."
    )  # Doc says number, using int


# --- Main Response Model ---
class GetDeliveryPricesResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_delivery_prices endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetDeliveryPricesResult = Field(
        description="Contains the list of delivery prices and the total record count."
    )
