import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_instruments_response import (
    GetInstrumentsResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetBookSummaryByInstrument tool
class DeribitGetBookSummaryByInstrumentInput(BaseModel):
    """Input for DeribitGetBookSummaryByInstrument tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (e.g., ETH-22FEB19-140-P), (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )


# DeribitGetBookSummaryByInstrument tool to fetch book summary from Deribit API
class DeribitGetBookSummaryByInstrumentTool(DeribitBaseTool):
    """Tool to fetch book summary for a specific instrument from Deribit API."""

    name: str = "get_book_summary_by_instrument"
    description: str = (
        "Get the summary information such as open interest, 24h volume, etc. "
        "for a specific instrument on Deribit."
    )
    args_schema: Type[BaseModel] = DeribitGetBookSummaryByInstrumentInput

    async def _arun(
        self,
        instrument_name: str,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch book summary information for a specific instrument from Deribit.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            params = {"instrument_name": instrument_name}

            raw_json = await self.api.get(
                "/api/v2/public/get_book_summary_by_instrument", params=params
            )
            return format_json_result(raw_json, GetInstrumentsResponse)

        except Exception as e:
            logger.error("Error getting book summary: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
