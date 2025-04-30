# -------- unused we use the existing optimized_response\get_trade_volumes.py -------- 

# from typing import List, Optional

# from pydantic import BaseModel, Field

# # Updated import path for base response
# from skills.deribit.base_response import DeribitBaseResponse


# # --- Nested Model for items in the 'result' list ---
# class TradeVolumeItem(BaseModel):
#     """Represents aggregated trade volumes for a specific currency."""

#     currency: str = Field(description='Currency symbol (e.g., "BTC", "ETH").')
#     # 24h volumes (always present)
#     puts_volume: float = Field(description="Total 24h trade volume for put options.")
#     futures_volume: float = Field(description="Total 24h trade volume for futures.")
#     calls_volume: float = Field(description="Total 24h trade volume for call options.")
#     spot_volume: float = Field(description="Total 24h trade volume for spot.")
#     # Extended volumes (present if extended=true)
#     calls_volume_7d: Optional[float] = Field(
#         None, description="Total 7d trade volume for call options."
#     )
#     calls_volume_30d: Optional[float] = Field(
#         None, description="Total 30d trade volume for call options."
#     )
#     futures_volume_7d: Optional[float] = Field(
#         None, description="Total 7d trade volume for futures."
#     )
#     futures_volume_30d: Optional[float] = Field(
#         None, description="Total 30d trade volume for futures."
#     )
#     puts_volume_7d: Optional[float] = Field(
#         None, description="Total 7d trade volume for put options."
#     )
#     puts_volume_30d: Optional[float] = Field(
#         None, description="Total 30d trade volume for put options."
#     )
#     spot_volume_7d: Optional[float] = Field(
#         None, description="Total 7d trade for spot."
#     )
#     spot_volume_30d: Optional[float] = Field(
#         None, description="Total 30d trade for spot."
#     )


# # --- Main Response Model ---
# class GetTradeVolumesResponse(DeribitBaseResponse):
#     """
#     Represents the full successful JSON response from the /public/get_trade_volumes endpoint.
#     The result is a list of aggregated trade volumes per currency.
#     Parsing and validation happen during instantiation.
#     """

#     result: List[TradeVolumeItem] = Field(
#         description="List of aggregated trade volumes per currency."
#     )
