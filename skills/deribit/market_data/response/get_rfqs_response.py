from typing import List, Literal

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for items in the 'result' list ---
class RFQItem(BaseModel):
    """Represents a single active Request For Quote (RFQ)."""

    amount: float = Field(
        description="Requested order size. Units depend on instrument type."
    )
    instrument_name: str = Field(
        description="Unique instrument identifier. (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    last_rfq_timestamp: int = Field(
        alias="last_rfq_tstamp",  # Use alias to match example if needed, but docs prefer underscore
        description="The timestamp of the last RFQ (milliseconds since the Unix epoch).",
    )
    side: Literal["buy", "sell"] = Field(description="Side of the RFQ.")
    traded_volume: float = Field(
        description="Volume traded since the last RFQ for this instrument/side."
    )


# --- Main Response Model ---
class GetRFQsResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_rfqs endpoint.
    The result is a list of active RFQs.
    Parsing and validation happen during instantiation.
    """

    result: List[RFQItem] = Field(description="List of active RFQs matching the query.")

    # If using alias 'last_rfq_tstamp', ensure Pydantic config allows population by alias
    model_config = {"populate_by_name": True}
