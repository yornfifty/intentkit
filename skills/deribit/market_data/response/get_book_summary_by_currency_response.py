from typing import List

from pydantic import BaseModel, Field


# --- Nested Model for items in the 'result' list ---
class BookSummaryInstrument(BaseModel):
    """Represents a summary of a trading instrument's current market state."""

    high: float = Field(description="The highest traded price within the 24h period.")
    low: float = Field(description="The lowest traded price within the 24h period.")
    last: float = Field(description="The most recent trade price.")
    instrument_name: str = Field(
        description="The identifier of the trading instrument, typically in 'BASE_QUOTE' format (e.g., BTC_USDT). (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    bid_price: float = Field(description="The current best bid price.")
    ask_price: float = Field(description="The current best ask price.")
    mark_price: float = Field(
        description="The fair price used for margin calculations."
    )
    creation_timestamp: int = Field(
        description="Timestamp when the market data snapshot was created (in milliseconds since Unix epoch)."
    )
    price_change: float = Field(
        description="Percentage change in price over the past 24h."
    )
    volume: float = Field(
        description="Total trading volume in base currency over the past 24h."
    )
    base_currency: str = Field(
        description="The base currency of the trading pair (e.g., BTC in BTC_USDT)."
    )
    estimated_delivery_price: float = Field(
        description="The estimated price at which the asset will be delivered or settled."
    )
    quote_currency: str = Field(
        description="The quote currency of the trading pair (e.g., USDT in BTC_USDT)."
    )
    volume_usd: float = Field(description="Total 24h traded volume in USD.")
    volume_notional: float = Field(
        description="Total 24h traded volume in quote currency."
    )
    mid_price: float = Field(
        description="The midpoint between the current best bid and best ask prices."
    )


# --- Main Response Model ---
class GetBookSummaryByCurrencyResponse(BaseModel):
    """Represents the full JSON-RPC standard response for a market data query."""

    result: List[BookSummaryInstrument] = Field(
        description="List of instruments with their current market summary."
    )
