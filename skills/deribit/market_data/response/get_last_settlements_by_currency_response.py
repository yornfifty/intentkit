from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for items in the 'settlements' list ---
class SettlementItem(BaseModel):
    """Represents a single settlement, delivery, or bankruptcy event."""

    type: Literal["settlement", "delivery", "bankruptcy"] = Field(
        description="The type of settlement event."
    )
    timestamp: int = Field(
        description="The timestamp (milliseconds since the Unix epoch)."
    )

    # Fields primarily for settlement/delivery
    instrument_name: Optional[str] = Field(
        None, description="Instrument name (settlement and delivery only)."
    )
    index_price: Optional[float] = Field(
        None,
        description="Underlying index price at time of event (settlement and delivery only).",
    )
    mark_price: Optional[float] = Field(
        None,
        description="Mark price at the settlement time (settlement and delivery only).",
    )
    position: Optional[float] = Field(
        None, description="Position size (settlement and delivery only)."
    )
    profit_loss: Optional[float] = Field(
        None,
        description="Profit and loss (in base currency; settlement and delivery only).",
    )
    session_profit_loss: float = Field(
        description="Total value of session profit and losses (in base currency)."
    )

    # Fields primarily for settlement (perpetual)
    funding: Optional[float] = Field(
        None,
        description="Funding (in base currency; settlement for perpetual product only).",
    )

    # Fields primarily for bankruptcy
    funded: Optional[float] = Field(
        None, description="Funded amount (bankruptcy only)."
    )
    socialized: Optional[float] = Field(
        None,
        description="The amount of the socialized losses (in base currency; bankruptcy only).",
    )
    session_bankruptcy: Optional[float] = Field(
        None,
        description="Value of session bankruptcy (in base currency; bankruptcy only).",
    )
    session_tax: Optional[float] = Field(
        None,
        description="Total amount of paid taxes/fees (in base currency; bankruptcy only).",
    )
    session_tax_rate: Optional[float] = Field(
        None, description="Rate of paid taxes/fees (in base currency; bankruptcy only)."
    )


# --- Nested Model for the 'result' object ---
class GetLastSettlementsByCurrencyResult(BaseModel):
    """Result object containing settlement data and pagination token."""

    settlements: List[SettlementItem] = Field(description="List of settlement events.")
    continuation: Optional[str] = Field(
        None, description="Continuation token for pagination."
    )


# --- Main Response Model ---
class GetLastSettlementsByCurrencyResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_last_settlements_by_currency endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetLastSettlementsByCurrencyResult = Field(
        description="Contains the list of settlements and pagination information."
    )
