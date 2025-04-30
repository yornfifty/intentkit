from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for individual trade items in the 'trades' list ---
class TradeItem(BaseModel):
    """Represents a single trade event for an instrument."""

    amount: float = Field(
        description="Trade amount. For perpetual and inverse futures the amount is in USD units. For options and linear futures and it is the underlying base currency coin."
    )
    block_rfq_id: Optional[int] = Field(
        default=None,
        description="ID of the Block RFQ - when trade was part of the Block RFQ",
    )
    block_trade_id: Optional[str] = Field(
        default=None,
        description="Block trade id - when trade was part of a block trade",
    )
    block_trade_leg_count: Optional[int] = Field(
        default=None,
        description="Block trade leg count - when trade was part of a block trade",
    )
    combo_id: Optional[str] = Field(
        default=None,
        description="Optional field containing combo instrument name if the trade is a combo trade",
    )
    combo_trade_id: Optional[float] = (
        Field(  # API doc says 'number', using float for flexibility
            default=None,
            description="Optional field containing combo trade identifier if the trade is a combo trade",
        )
    )
    contracts: Optional[float] = Field(  # API doc says 'number', using float
        default=None,
        description="Trade size in contract units (optional, may be absent in historical trades)",
    )
    direction: Literal["buy", "sell"] = Field(description="Direction: buy, or sell")
    index_price: float = Field(description="Index Price at the moment of trade")
    instrument_name: str = Field(
        description="Unique instrument identifier, (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    iv: Optional[float] = Field(
        default=None,
        description="Option implied volatility for the price (Option only)",
    )
    liquidation: Optional[Literal["M", "T", "MT"]] = Field(
        default=None,
        description='Optional field (only for trades caused by liquidation): "M" when maker side of trade was under liquidation, "T" when taker side was under liquidation, "MT" when both sides of trade were under liquidation',
    )
    mark_price: float = Field(description="Mark Price at the moment of trade")
    price: float = Field(description="Price in base currency")
    tick_direction: Literal[0, 1, 2, 3] = Field(
        description='Direction of the "tick" (0 = Plus Tick, 1 = Zero-Plus Tick, 2 = Minus Tick, 3 = Zero-Minus Tick).'
    )
    timestamp: int = Field(
        description="The timestamp of the trade (milliseconds since the UNIX epoch)"
    )
    trade_id: str = Field(description="Unique (per currency) trade identifier")
    trade_seq: int = Field(
        description="The sequence number of the trade within instrument"
    )


# --- Nested Model for the 'result' object ---
class GetLastTradesResult(BaseModel):
    """The result field containing the list of trades and pagination info."""

    has_more: bool = Field(
        description="Indicates if there are more trades available beyond the current response."
    )
    trades: List[TradeItem] = Field(description="List of trade details.")


# --- Main Response Model ---
class GetLastTradesByInstrumentResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_last_trades_by_instrument endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetLastTradesResult = Field(
        description="Contains the list of trades and pagination information."
    )
