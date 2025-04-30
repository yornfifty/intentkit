import logging
from typing import Any, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from skills.deribit.base import DeribitBaseTool

# Updated import path for the response model
from skills.deribit.market_data.optimized_response.get_trade_volumes import (
    optimize_get_trade_volume_response,
)

# Import the formatting utility

logger = logging.getLogger(__name__)


# Input schema for DeribitGetTradeVolumes tool
class DeribitGetTradeVolumesInput(BaseModel):
    """Input for DeribitGetTradeVolumes tool."""

    extended: Optional[bool] = Field(
        False,
        description="Request extended statistics including 7 and 30 days volumes (default false).",
    )


# DeribitGetTradeVolumes tool to fetch aggregated trade volumes from Deribit API
class DeribitGetTradeVolumes(DeribitBaseTool):
    """Tool to retrieve aggregated 24h (and optionally 7d/30d) trade volumes for different instrument types and currencies."""

    name: str = "get_trade_volumes"
    description: str = (
        "Retrieves aggregated 24h trade volumes for different instrument types and currencies. "
        "Optionally retrieves 7d and 30d volumes."
    )
    args_schema: Type[BaseModel] = DeribitGetTradeVolumesInput

    async def _arun(
        self,
        extended: Optional[bool] = True,
        config: RunnableConfig = None,
        **kwargs,
    ) -> Any:  # Return type is str (formatted result)
        """
        Fetch aggregated trade volumes, optionally extended, and return the formatted result.
        """
        try:
            context = self.context_from_config(config)

            # Check rate limit
            await self.apply_rate_limit(context)

            # Prepare parameters for the API call
            params = {}
            # Only include 'extended' if it's explicitly True, as False is the default
            if extended:
                params["extended"] = True

            # --- API Call Logic Merged In using self.api.get ---
            logger.debug(f"Calling /public/get_trade_volumes with params: {params}")
            raw_json = await self.api.get(
                "/api/v2/public/get_trade_volumes", params=params
            )
            logger.debug(f"Received raw JSON response: {raw_json}")
            # --- End API Call Logic ---

            # Convert the JSON result to formatted result
            formatted_output = optimize_get_trade_volume_response(raw_json)
            # formatted_output = format_json_result(
            #     json_data=raw_json,
            #     model=GetTradeVolumesResponse,
            #     prompt_append="convert the result into a markdown table and sort it",
            #     csv=False,
            # )
            logger.info("Successfully fetched trade volumes and format the result")
            return formatted_output

        except Exception as e:
            logger.error(f"Error getting trade volumes: {str(e)}")
            raise type(e)(
                f"[agent:{context.agent.id}]: Failed to get trade volumes. Reason: {e}"
            ) from e
