from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from skills.deribit.base_response import DeribitBaseResponse


# --- Input Model ---
class DeribitGetInstrumentsInput(BaseModel):
    """Input model for the get_instruments endpoint."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR", "SOL", "any"] = Field(
        description='The currency symbol or "any" for all.'
    )
    kind: Optional[
        Literal["future", "option", "spot", "future_combo", "option_combo"]
    ] = Field(
        default=None,
        description="Instrument kind, if not provided instruments of all kinds are considered.",
    )
    expired: Optional[bool] = Field(
        default=None,
        description="Set to true to show recently expired instruments instead of active ones.",
    )


# --- Nested Models for the 'result' items ---
class TickSizeStep(BaseModel):
    """Defines a price step for instruments with varying tick sizes."""

    above_price: float = Field(
        description="The price threshold above which this tick size applies."
    )
    tick_size: float = Field(
        description="The tick size used above the specified price threshold. It must be multiple of the minimum tick size."
    )


class Instrument(BaseModel):
    """Represents a Deribit trading instrument within the response."""

    base_currency: str = Field(description="The underlying currency being traded.")
    block_trade_commission: float = Field(
        description="Block Trade commission for instrument."
    )
    block_trade_min_trade_amount: float = Field(
        description="Minimum amount for block trading."
    )
    block_trade_tick_size: float = Field(
        description="Specifies minimal price change for block trading."
    )
    contract_size: float = Field(description="Contract size for instrument.")
    counter_currency: str = Field(
        description="Counter currency for the instrument (e.g., USD)."
    )
    creation_timestamp: int = Field(
        description="The time when the instrument was first created (milliseconds since the UNIX epoch)."
    )
    expiration_timestamp: int = Field(
        description="The time when the instrument will expire (milliseconds since the UNIX epoch)."
    )
    future_type: Optional[str] = Field(
        default=None,
        description="DEPRECATED: Future type (only for futures). Use instrument_type instead.",
    )
    instrument_id: int = Field(description="Instrument ID.")
    instrument_name: str = Field(
        description="Unique instrument identifier (e.g., BTC-PERPETUAL). (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    instrument_type: str = Field(
        description="Type of the instrument, e.g., 'reversed' or 'linear'."
    )
    is_active: bool = Field(
        description="Indicates if the instrument can currently be traded."
    )
    kind: Literal["future", "option", "spot", "future_combo", "option_combo"] = Field(
        description="Instrument kind."
    )
    maker_commission: float = Field(description="Maker commission for instrument.")
    max_leverage: Optional[int] = Field(
        default=None,
        description="Maximal leverage for instrument (only applies to futures and perpetuals).",
    )
    max_liquidation_commission: Optional[float] = Field(
        default=None,
        description="Maximal liquidation trade commission for instrument (only applies to futures and perpetuals).",
    )
    min_trade_amount: float = Field(
        description="Minimum amount for trading. Units depend on instrument type."
    )
    option_type: Optional[Literal["call", "put"]] = Field(
        default=None, description="The option type (only applies to options)."
    )
    price_index: str = Field(
        description="Name of the price index used for settlement or mark price (e.g., 'btc_usd')."
    )
    quote_currency: str = Field(
        description="The currency in which the instrument prices are quoted."
    )
    rfq: bool = Field(
        description="Whether Request for Quote (RFQ) is active for this instrument."
    )
    settlement_currency: Optional[str] = Field(
        default=None,
        description="Settlement currency for the instrument (not present for spot).",
    )
    settlement_period: str = Field(
        description="The settlement period (e.g., 'perpetual', 'month', 'week')."
    )
    strike: Optional[float] = Field(
        default=None, description="The strike price (only applies to options)."
    )
    taker_commission: float = Field(description="Taker commission for instrument.")
    tick_size: float = Field(
        description="Specifies the minimum price change (tick) for the instrument."
    )
    tick_size_steps: List[TickSizeStep] = Field(
        description="Defines price steps for instruments with varying tick sizes. Empty list if uniform."
    )


# --- Main Response Model ---
class GetInstrumentsResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_instruments endpoint.
    Parsing and validation happen during instantiation of this model.
    """

    result: List[Instrument] = Field(
        description="The list of successfully retrieved instrument details."
    )
