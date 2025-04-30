import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_funding_rate_value_response import (
    GetFundingRateValueResponse,
)
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetFundingRateValue tool
class DeribitGetFundingRateValueInput(BaseModel):
    """Input for DeribitGetFundingRateValue tool."""

    instrument_name: str = Field(
        ...,
        description="Instrument name (must be a PERPETUAL) (IMPORTANT : if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )
    start_timestamp: int = Field(
        ...,
        description="The earliest timestamp to return result from (milliseconds since the UNIX epoch).",
    )
    end_timestamp: int = Field(
        ...,
        description="The most recent timestamp to return result from (milliseconds since the UNIX epoch).",
    )


# DeribitGetFundingRateValue tool to fetch funding rate value from Deribit API
class DeribitGetFundingRateValueTool(DeribitBaseTool):
    """Tool to retrieve the funding rate value for a perpetual instrument over a requested period from Deribit API."""

    name: str = "get_funding_rate_value"
    description: str = "Retrieves interest rate value (funding rate) for requested period. Applicable only for PERPETUAL instruments."
    args_schema: Type[BaseModel] = DeribitGetFundingRateValueInput

    async def _arun(
        self,
        instrument_name: str,
        start_timestamp: int,
        end_timestamp: int,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:
        """
        Fetch funding rate value for a specific perpetual instrument and time range.
        """
        # Basic validation: Although the API handles it, reminding the user/LLM might be useful.
        if "PERPETUAL" not in instrument_name.upper():
            logger.warning(
                f"Instrument '{instrument_name}' might not be a perpetual. API call might fail or return unexpected results."
            )
            # Depending on desired strictness, could raise ValueError here.

        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(
                f"Calling /public/get_funding_rate_value with params: {params}"
            )
            raw_json = await self.api.get(
                "/api/v2/public/get_funding_rate_value", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            return format_json_result(raw_json, GetFundingRateValueResponse)

        except Exception as e:
            logger.error(
                f"Error getting funding rate value for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get funding rate value for {instrument_name}. Reason: {e}"
            ) from e
