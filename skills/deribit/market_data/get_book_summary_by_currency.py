import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_book_summary_by_currency_response import (
    GetBookSummaryByCurrencyResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetBookSummaryByCurrency tool
class DeribitGetBookSummaryByCurrencyInput(BaseModel):
    """Input for DeribitGetBookSummaryByCurrency tool."""

    currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"] = Field(
        ..., description="Currency symbol (e.g., BTC, ETH, USDC, USDT, EURR)"
    )
    kind: Optional[
        Literal["future", "option", "spot", "future_combo", "option_combo"]
    ] = Field(None, description="Instrument kind (optional)")


class DeribitGetBookSummaryByCurrencyTool(DeribitBaseTool):
    """Tool to fetch book summary for all instruments for a specific currency from Deribit API."""

    name: str = "get_book_summary_by_currency"
    description: str = (
        "Get the summary information such as open interest, 24h volume, etc. "
        "for all instruments of a specific currency, optionally filtered by kind."
    )
    args_schema: Type[BaseModel] = DeribitGetBookSummaryByCurrencyInput

    async def _arun(
        self,
        currency: Literal["BTC", "ETH", "USDC", "USDT", "EURR"],
        kind: Optional[
            Literal["future", "option", "spot", "future_combo", "option_combo"]
        ] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch book summary information for all instruments of a specific currency.
        Optionally, filter by instrument kind.
        """
        try:
            context = self.context_from_config(config)

            self.handle_tool_error

            # Check rate limit
            await self.apply_rate_limit(context)
            params = {"currency": currency}
            if kind is not None:
                params["kind"] = kind

            raw_json = await self.api.get(
                "/api/v2/public/get_book_summary_by_currency", params=params
            )

            # return raw_json
            return format_json_result(raw_json, GetBookSummaryByCurrencyResponse)

        except Exception as e:
            logger.error("Error getting book summary by currency: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
