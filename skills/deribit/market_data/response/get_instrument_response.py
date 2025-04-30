# --- Nested Model for tick size steps ---
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from skills.deribit.base_response import DeribitBaseResponse


class TickSizeStep(BaseModel):
    """Defines a tick size applicable above a certain price."""

    above_price: float = Field(
        description="The price from which the increased tick size applies."
    )
    tick_size: float = Field(description="Tick size to be used above the price.")


# --- Nested Model for the 'result' object ---
class GetInstrumentResult(BaseModel):
    """Detailed information about a specific instrument."""

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
    contract_size: int = Field(description="Contract size for instrument.")
    counter_currency: str = Field(description="Counter currency for the instrument.")
    creation_timestamp: int = Field(
        description="The time when the instrument was first created (milliseconds since the UNIX epoch)."
    )
    expiration_timestamp: int = Field(
        description="The time when the instrument will expire (milliseconds since the UNIX epoch)."
    )
    future_type: Optional[str] = Field(
        None,
        description="(DEPRECATED) Future type (only for futures). Use instrument_type.",
    )
    instrument_id: int = Field(description="Instrument ID.")
    instrument_name: str = Field(
        description="Unique instrument identifier. (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)"
    )
    instrument_type: Optional[Literal["linear", "reversed"]] = Field(
        None, description="Type of the instrument (linear or reversed)."
    )
    is_active: bool = Field(
        description="Indicates if the instrument can currently be traded."
    )
    kind: Literal["future", "option", "spot", "future_combo", "option_combo"] = Field(
        description="Instrument kind."
    )
    maker_commission: float = Field(description="Maker commission for instrument.")
    max_leverage: Optional[int] = Field(
        None, description="Maximal leverage for instrument (only for futures)."
    )
    max_liquidation_commission: Optional[float] = Field(
        None,
        description="Maximal liquidation trade commission for instrument (only for futures).",
    )
    min_trade_amount: float = Field(
        description="Minimum amount for trading. Units depend on instrument type."
    )
    option_type: Optional[Literal["call", "put"]] = Field(
        None, description="The option type (only for options)."
    )
    price_index: str = Field(
        description="Name of price index that is used for this instrument."
    )
    quote_currency: str = Field(
        description="The currency in which the instrument prices are quoted."
    )
    rfq: bool = Field(description="Whether or not RFQ is active on the instrument.")
    settlement_currency: Optional[str] = Field(
        None, description="Settlement currency for the instrument (not for spot)."
    )
    settlement_period: Optional[Literal["month", "week", "day", "perpetual"]] = Field(
        None, description="The settlement period (not for spot)."
    )
    strike: Optional[float] = Field(
        None, description="The strike value (only for options)."
    )
    taker_commission: float = Field(description="Taker commission for instrument.")
    tick_size: float = Field(
        description="Specifies minimal price change for the instrument."
    )
    tick_size_steps: Optional[List[TickSizeStep]] = Field(
        None, description="Optional list defining tick size steps above certain prices."
    )


# --- Main Response Model ---
class GetInstrumentResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_instrument endpoint.
    Parsing and validation happen during instantiation.
    """

    result: GetInstrumentResult = Field(
        description="Contains the detailed instrument information."
    )
