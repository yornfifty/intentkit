from typing import List

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for items in the 'data' array ---
class FundingChartDataItem(BaseModel):
    """Represents a single data point in the funding chart history."""

    index_price: float = Field(description="Index price at the time of the data point.")
    interest_8h: float = Field(description="Historical 8-hour funding rate value.")
    timestamp: int = Field(
        description="The timestamp of the data point (milliseconds since the Unix epoch)."
    )


# --- Nested Model for the 'result' object ---
class GetFundingChartDataResult(BaseModel):
    """Result object containing funding chart data."""

    current_interest: float = Field(
        description="Current instantaneous interest rate (funding rate)."
    )
    data: List[FundingChartDataItem] = Field(
        description="List of historical funding data points."
    )
    interest_8h: float = Field(description="Current projected 8-hour funding rate.")


# --- Main Response Model ---
class GetFundingChartDataResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_funding_chart_data endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetFundingChartDataResult = Field(
        description="Contains the funding chart data points and current rates."
    )
