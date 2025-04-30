from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class GetContractSizeResult(BaseModel):
    """Result object containing the contract size."""

    contract_size: int = Field(
        description="Contract size, for futures in USD, for options in base currency."
    )


# --- Main Response Model ---
class GetContractSizeResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_contract_size endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetContractSizeResult = Field(description="Contains the contract size.")
