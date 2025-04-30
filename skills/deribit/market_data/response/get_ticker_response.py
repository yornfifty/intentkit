from typing import Literal, Optional

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse

# Reusing nested models from get_order_book response
from skills.deribit.market_data.response.get_order_book_response import Greeks, Stats


# --- Nested Model for the 'result' object ---
# Similar to GetOrderBookResult but without bids/asks arrays and specific ticker fields
class TickerResult(BaseModel):
    """Detailed ticker information for an instrument."""

    ask_iv: Optional[float] = Field(
        default=None, description="(Only for option) implied volatility for best ask."
    )
    best_ask_amount: float = Field(
        description="It represents the requested order size of all best asks."
    )
    best_ask_price: Optional[float] = Field(
        default=None,
        description="The current best ask price, null if there aren't any asks.",
    )
    best_bid_amount: float = Field(
        description="It represents the requested order size of all best bids."
    )
    best_bid_price: Optional[float] = Field(
        default=None,
        description="The current best bid price, null if there aren't any bids.",
    )
    bid_iv: Optional[float] = Field(
        default=None, description="(Only for option) implied volatility for best bid."
    )
    current_funding: Optional[float] = Field(
        default=None, description="Current funding (perpetual only)."
    )
    delivery_price: Optional[float] = Field(
        default=None,
        description="The settlement price for the instrument. Only when state = closed.",
    )
    estimated_delivery_price: Optional[float] = Field(  # In example, marked Optional
        default=None, description="Estimated delivery price for the market."
    )
    funding_8h: Optional[float] = Field(
        default=None, description="Funding 8h (perpetual only)."
    )
    greeks: Optional[Greeks] = Field(
        default=None, description="Option Greeks (options only)."
    )
    index_price: float = Field(description="Current index price.")
    instrument_name: str = Field(
        description="Unique instrument identifier. (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    interest_rate: Optional[float] = Field(
        default=None,
        description="Interest rate used in implied volatility calculations (options only).",
    )
    interest_value: Optional[float] = Field(  # Added based on docs/example
        default=None,
        description="Value used to calculate realized_funding in positions (perpetual only).",
    )
    last_price: Optional[float] = Field(
        default=None, description="The price for the last trade."
    )
    mark_iv: Optional[float] = Field(
        default=None, description="(Only for option) implied volatility for mark price."
    )
    mark_price: float = Field(description="The mark price for the instrument.")
    max_price: float = Field(
        description="The maximum price for the future. Any buy orders you submit higher than this price, will be clamped to this maximum."
    )
    min_price: float = Field(
        description="The minimum price for the future. Any sell orders you submit lower than this price will be clamped to this minimum."
    )
    open_interest: float = Field(  # Example showed value for perpetual, keep non-optional for now
        description="The total amount of outstanding contracts in the corresponding amount units."
    )
    settlement_price: Optional[float] = Field(  # Optional based on docs and example
        default=None,
        description="The settlement price for the instrument. Only when state = open (spot excluded).",
    )
    state: Literal["open", "closed"] = Field(
        description="The state of the order book. Possible values are open and closed."
    )
    stats: Stats = Field(description="Instrument statistics for the last 24 hours.")
    timestamp: int = Field(
        description="The timestamp (milliseconds since the Unix epoch)."
    )
    underlying_index: Optional[str] = (
        Field(  # Changed type to str based on usual patterns
            default=None,
            description="Name of the underlying future, or index_price (options only).",
        )
    )
    underlying_price: Optional[float] = Field(
        default=None,
        description="Underlying price for implied volatility calculations (options only).",
    )


# --- Main Response Model ---
class GetTickerResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/ticker endpoint.
    Parsing and validation happen during instantiation.
    """

    result: TickerResult = Field(
        description="Contains the detailed ticker information."
    )
