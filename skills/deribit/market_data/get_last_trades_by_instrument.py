import logging
from typing import Any, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool
from skills.deribit.market_data.response.get_last_trades_by_instrument_response import (
    GetLastTradesByInstrumentResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetLastTradesByInstrument tool
class DeribitGetLastTradesByInstrumentInput(BaseModel):
    """Input for DeribitGetLastTradesByInstrument tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (e.g., BTC-PERPETUAL) (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first)",
    )
    start_seq: Optional[int] = Field(
        None, description="The sequence number of the first trade to be returned."
    )
    end_seq: Optional[int] = Field(
        None, description="The sequence number of the last trade to be returned."
    )
    start_timestamp: Optional[int] = Field(
        None,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: Optional[int] = Field(
        None,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    count: Optional[int] = Field(
        None, description="Number of requested items, default - 10."
    )
    sorting: Optional[Literal["asc", "desc", "default"]] = Field(
        None,
        description="Direction of results sorting (default value means no sorting).",
    )


# DeribitGetLastTradesByInstrument tool to fetch last trades by instrument from Deribit API
class DeribitGetLastTradesByInstrumentTool(DeribitBaseTool):
    """Tool to retrieve the latest trades that have occurred for a specific instrument from Deribit API."""

    name: str = "get_last_trades_by_instrument"
    description: str = (
        "Retrieve the latest trades that have occurred for a specific instrument."
    )
    args_schema: Type[BaseModel] = DeribitGetLastTradesByInstrumentInput

    async def _arun(
        self,
        instrument_name: str,
        start_seq: Optional[int] = None,
        end_seq: Optional[int] = None,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        count: Optional[int] = None,
        sorting: Optional[Literal["asc", "desc", "default"]] = None,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch the latest trades for a specific instrument.
        Allows filtering by sequence number, timestamp, count, and sorting.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare input data using the Pydantic model for validation
            params = {"instrument_name": instrument_name}

            # Add optional parameters if they are provided
            if start_seq is not None:
                params["start_seq"] = start_seq
            if end_seq is not None:
                params["end_seq"] = end_seq
            if start_timestamp is not None:
                params["start_timestamp"] = start_timestamp
            if end_timestamp is not None:
                params["end_timestamp"] = end_timestamp
            if count is not None:
                params["count"] = count
            if sorting is not None:
                params["sorting"] = sorting

            # Call the underlying generic API request method
            raw_json = await self.api.get(
                "/api/v2/public/get_last_trades_by_instrument", params=params
            )
            return format_json_result(raw_json, GetLastTradesByInstrumentResponse)

            # Parse the JSON response using the Pydantic model
            return GetLastTradesByInstrumentResponse(**raw_json)

        except Exception as e:
            logger.error("Error getting last trades by instrument: %s", str(e))
            raise type(e)(f"[agent:{context.agent.id}]: {e}") from e
