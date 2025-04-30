import logging
from typing import Any, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.response.get_instrument_response import (
    GetInstrumentResponse,
)

# Import the formatting utility
from skills.deribit.utils.format_json_result import format_json_result

logger = logging.getLogger(__name__)


# Input schema for DeribitGetInstrument tool
class DeribitGetInstrumentInput(BaseModel):
    """Input for DeribitGetInstrument tool. depends on DeribitGetInstrumentsTool"""

    instrument_name: str = Field(
        ...,
        description="Instrument name (if you dont know what to input, you have to call DeribitGetInstrumentsTool first).",
    )


# DeribitGetInstrument tool to fetch instrument details from Deribit API
class DeribitGetInstrument(DeribitBaseTool):
    """Tool to retrieve detailed information about a specific instrument from Deribit API."""

    name: str = "get_instrument"
    description: str = "Retrieves information about a specific instrument."
    args_schema: Type[BaseModel] = DeribitGetInstrumentInput

    async def _arun(
        self,
        instrument_name: str,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch detailed information for a specific instrument and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {
                "instrument_name": instrument_name,
            }

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_instrument with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_instrument", params=params
            )

            formatted_output = format_json_result(raw_json, GetInstrumentResponse)
            logger.info(
                f"Successfully fetched instrument details for {instrument_name} and format the result"
            )
            return formatted_output

        except Exception as e:
            logger.error(
                f"Error getting instrument details for {instrument_name}: {str(e)}"
            )
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get instrument details for {instrument_name}. Reason: {e}"
            ) from e
