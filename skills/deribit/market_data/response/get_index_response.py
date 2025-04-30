from typing import Optional

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
# Using a flexible approach as keys depend on input currency
class GetIndexResult(BaseModel):
    """
    Result object containing the index price for the requested currency and EDP.
    Note: The specific currency key (e.g., 'BTC', 'ETH') depends on the request.
    """

    # Define known possible keys as optional
    BTC: Optional[float] = Field(
        None, description="The current index price for BTC-USD (if currency=BTC)."
    )
    ETH: Optional[float] = Field(
        None, description="The current index price for ETH-USD (if currency=ETH)."
    )
    # Add other potential currencies if needed (USDC, USDT, EURR maps aren't explicitly defined in doc)
    # Example for USDC:
    USDC: Optional[float] = Field(
        None, description="The current index price for USDC-USD (if currency=USDC)."
    )
    USDT: Optional[float] = Field(
        None, description="The current index price for USDT-USD (if currency=USDT)."
    )
    EURR: Optional[float] = Field(
        None, description="The current index price for EURR-USD (if currency=EURR)."
    )

    edp: Optional[float] = (
        Field(  # Optional as it might be missing in rare cases or future changes
            None, description="Estimated delivery price for the currency."
        )
    )

    # Allow extra fields to handle potential future currencies without breaking
    # class Config:
    #     extra = "allow"
    # Pydantic v2 way:
    model_config = {"extra": "allow"}

    # Add a validator to ensure at least one currency price + edp is present? Optional.


# --- Main Response Model ---
class GetIndexResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the deprecated /public/get_index endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetIndexResult = Field(
        description="Contains the index price for the requested currency and the estimated delivery price."
    )
