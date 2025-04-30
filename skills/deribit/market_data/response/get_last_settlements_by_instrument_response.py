from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse

# Reusing models from the currency-based settlement response as the structure is identical
from skills.deribit.market_data.response.get_last_settlements_by_currency_response import (
    GetLastSettlementsByCurrencyResult,  # Reusing the result structure
)


# --- Main Response Model ---
# Renaming the result class for clarity, although it reuses the structure
class GetLastSettlementsByInstrumentResult(GetLastSettlementsByCurrencyResult):
    """Result object containing settlement data and pagination token for a specific instrument."""

    pass


class GetLastSettlementsByInstrumentResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_last_settlements_by_instrument endpoint.
    Parsing and validation happen during instantiation. Uses reused models for settlement items and result structure.
    """

    result: GetLastSettlementsByInstrumentResult = Field(
        description="Contains the list of settlements for the instrument and pagination information."
    )
