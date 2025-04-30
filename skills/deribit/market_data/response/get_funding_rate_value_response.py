from pydantic import Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Main Response Model ---
class GetFundingRateValueResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_funding_rate_value endpoint.
    The result is a single float value representing the funding rate.
    Parsing and validation happen during instantiation.
    """

    result: float = Field(
        description="The funding rate value for the requested period."
    )
