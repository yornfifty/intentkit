from typing import List, Literal

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for the 'result' object ---
class GetTradingviewChartDataResult(BaseModel):
    """Result object containing TradingView chart candle data."""

    close: List[float] = Field(description="List of prices at close (one per candle).")
    cost: List[float] = Field(
        description="List of cost bars (volume in quote currency, one per candle)."
    )
    high: List[float] = Field(
        description="List of highest price levels (one per candle)."
    )
    low: List[float] = Field(
        description="List of lowest price levels (one per candle)."
    )
    open: List[float] = Field(description="List of prices at open (one per candle).")
    status: Literal["ok", "no_data"] = Field(
        description="Status of the query: ok or no_data."
    )
    ticks: List[int] = Field(
        description="Values of the time axis given in milliseconds since UNIX epoch."
    )
    volume: List[float] = Field(
        description="List of volume bars (in base currency, one per candle)."
    )


# --- Main Response Model ---
class GetTradingviewChartDataResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_tradingview_chart_data endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetTradingviewChartDataResult = Field(
        description="Contains the TradingView chart candle data."
    )
