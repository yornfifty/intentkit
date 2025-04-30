from typing import List, Optional

from pydantic import BaseModel, Field

# Updated import path for base response
from skills.deribit.base_response import DeribitBaseResponse


# --- Nested Model for withdrawal priorities ---
class WithdrawalPriority(BaseModel):
    """Details of a specific withdrawal priority level."""

    name: str = Field(
        description="Name of the priority level (e.g., 'very_low', 'very_high')."
    )
    value: float = Field(
        description="Associated fee multiplier or value for the priority."
    )


# --- Nested Model for items in the 'result' list ---
class CurrencyItem(BaseModel):
    """Represents details for a single supported currency."""

    coin_type: str = Field(
        description="The type of the currency (e.g., 'BITCOIN', 'ETHER')."
    )
    currency: str = Field(
        description="The abbreviation of the currency used in the API (e.g., 'BTC', 'ETH')."
    )
    currency_long: str = Field(
        description="The full name for the currency (e.g., 'Bitcoin', 'Ethereum')."
    )
    fee_precision: int = Field(description="Precision used for fee calculations.")
    in_cross_collateral_pool: Optional[bool] = (
        Field(  # Added based on doc, not in example
            default=None,
            description="True if the currency is part of the cross collateral pool.",
        )
    )
    min_confirmations: int = Field(
        description="Minimum number of block chain confirmations before deposit is accepted."
    )
    min_withdrawal_fee: float = Field(
        description="The minimum transaction fee paid for withdrawals."
    )
    withdrawal_fee: float = Field(
        description="The standard transaction fee paid for withdrawals."
    )
    withdrawal_priorities: List[WithdrawalPriority] = Field(
        description="List of available withdrawal priority levels and their associated values."
    )


# --- Main Response Model ---
class GetCurrenciesResponse(DeribitBaseResponse):
    """
    Represents the full successful JSON response from the /public/get_currencies endpoint.
    The result is a list of currency details.
    Parsing and validation happen during instantiation.
    """

    result: List[CurrencyItem] = Field(
        description="List of details for all supported currencies."
    )
