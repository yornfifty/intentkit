from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for stats ---
class Stats(BaseModel):
    """Statistics for the instrument over the last 24 hours."""

    high: Optional[float] = Field(None, description="Highest price during 24h.")
    low: Optional[float] = Field(None, description="Lowest price during 24h.")
    price_change: Optional[float] = Field(
        None,
        description="24-hour price change expressed as a percentage, null if no trades.",
    )
    volume: Optional[float] = Field(
        None, description="Volume during last 24h in base currency."
    )
    volume_usd: Optional[float] = Field(
        None, description="Volume in USD (futures only)."
    )


# --- Nested Model for greeks ---
class Greeks(BaseModel):
    """Option Greeks."""

    delta: float = Field(description="The delta value for the option.")
    gamma: float = Field(description="The gamma value for the option.")
    rho: float = Field(description="The rho value for the option.")
    theta: float = Field(description="The theta value for the option.")
    vega: float = Field(description="The vega value for the option.")


# --- Nested Model for the 'result' object ---
class GetOrderBookResult(BaseModel):
    """Detailed order book and market data for an instrument."""

    ask_iv: Optional[float] = Field(
        default=None, description="(Only for option) implied volatility for best ask."
    )
    asks: List[Tuple[float, float]] = Field(description="List of asks [price, amount].")
    best_ask_amount: float = Field(
        description="It represents the requested order size of all best asks."
    )
    best_ask_price: Optional[float] = Field(  # Doc says null is possible
        default=None,
        description="The current best ask price, null if there aren't any asks.",
    )
    best_bid_amount: float = Field(
        description="It represents the requested order size of all best bids."
    )
    best_bid_price: Optional[float] = Field(  # Doc says null is possible
        default=None,
        description="The current best bid price, null if there aren't any bids.",
    )
    bid_iv: Optional[float] = Field(
        default=None, description="(Only for option) implied volatility for best bid."
    )
    bids: List[Tuple[float, float]] = Field(description="List of bids [price, amount].")
    change_id: Optional[int] = Field(
        default=None,
        description="The ID of the last change to the order book.",  # Added based on example
    )
    current_funding: Optional[float] = Field(
        default=None, description="Current funding (perpetual only)."
    )
    delivery_price: Optional[float] = Field(
        default=None,
        description="The settlement price for the instrument. Only when state = closed.",
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
    open_interest: Optional[float] = (
        Field(  # Marked optional as it might not apply to all instrument types (e.g., spot)
            default=None,
            description="The total amount of outstanding contracts in the corresponding amount units. For perpetual and inverse futures the amount is in USD units. For options and linear futures and it is the underlying base currency coin.",
        )
    )
    settlement_price: Optional[float] = Field(
        default=None,
        description="Optional (not added for spot). The settlement price for the instrument. Only when state = open.",
    )
    state: Literal["open", "closed"] = Field(
        description="The state of the order book. Possible values are open and closed."
    )
    stats: Stats = Field(description="Instrument statistics for the last 24 hours.")
    timestamp: int = Field(
        description="The timestamp (milliseconds since the Unix epoch)."
    )
    underlying_index: Optional[str] = (
        Field(  # Changed type to str based on usual patterns, doc says 'number' which seems odd
            default=None,
            description="Name of the underlying future, or index_price (options only).",
        )
    )
    underlying_price: Optional[float] = Field(
        default=None,
        description="Underlying price for implied volatility calculations (options only).",
    )


# --- Main Response Model ---
class GetOrderBookResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_order_book endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetOrderBookResult = Field(
        description="Contains the detailed order book and market data."
    )
