import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_instruments_response import (
    GetInstrumentsResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetInstruments tool
class DeribitGetInstrumentsInput(BaseModel):
    """Input for DeribitGetInstruments tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR", "any"] = Field(
        ..., description="Currency symbol (BTC, ETH, USDC, USDT, EURR, or 'any')"
    )
    kind: Optional[
        Literal["future", "option", "spot", "future_combo", "option_combo"]
    ] = Field(
        None,
        description="Instrument kind: future, option, spot, future_combo, option_combo (optional)",
    )
    expired: Optional[bool] = Field(
        False,
        description="Set true to show expired instruments instead of active ones (optional)",
    )


# DeribitGetInstruments tool to fetch instruments from Deribit API
class DeribitGetInstrumentsTool(DeribitBaseTool):
    """Tool to fetch available instruments from Deribit API."""

    name: str = "get_instruments"
    description: str = "Get available trading instruments from Deribit."
    args_schema: Type[BaseModel] = DeribitGetInstrumentsInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR", "any"],
        kind: Optional[
            Literal["future", "option", "spot", "future_combo", "option_combo"]
        ] = None,
        expired: Optional[bool] = False,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch available instruments from Deribit based on the provided parameters.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Call the API to get instruments
            params = {"currency": currency}
            if kind is not None:
                params["kind"] = kind
            if expired is not None:
                params["expired"] = expired

            raw_json = await self.api.get(
                "/api/v2/public/get_instruments", params=params
            )
            return format_json_result(raw_json, GetInstrumentsResponse)

        except Exception as e:
            logger.error("Error getting instruments: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
